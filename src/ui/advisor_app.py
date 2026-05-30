"""FastAPI advisor chat interface — JuraKlar juridisk rådgivning."""
from __future__ import annotations

import asyncio
import io
import json
import os
import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, Response, StreamingResponse
from pydantic import BaseModel

from ..models.config import LLMConfig

# ── Advisor display order ──────────────────────────────────────
_ADVISOR_ORDER: list[str] = [
    "testamente", "aegtepagt", "fremtidsfuldmagt", "boligkob", "doedsbo",
    "skilsmisse", "bodeling", "foraeldre", "samliv", "gavebrev",
    "lejeret", "ansaettelsesret", "erstatning", "patientskade", "gaeldssanering",
    "socialret", "forsikring", "naboret", "forbrugerret", "vaergemaal",
]


def _sort_advisors(advisors: dict) -> dict:
    """Return a new dict sorted by _ADVISOR_ORDER; unknown keys appended alphabetically."""
    known = {k: advisors[k] for k in _ADVISOR_ORDER if k in advisors}
    unknown = {k: advisors[k] for k in sorted(advisors) if k not in known}
    return {**known, **unknown}


class _DocItem(BaseModel):
    name: str
    text: str


class _ChatRequest(BaseModel):
    advisor_id: str
    service_id: int
    question: str
    docs: list[_DocItem] = []
    session_id: str = ""


class _ReviewRequest(BaseModel):
    advisor_id: str
    rating: int
    comment: str = ""
    email: str


class _TokenValidateRequest(BaseModel):
    token: str
    advisor_id: str
    service_id: int
    fmt: str


class _StripeCheckoutRequest(BaseModel):
    advisor_id: str
    service_id: int
    fmt: str


class _StripeVerifyRequest(BaseModel):
    session_id: str
    advisor_id: str
    service_id: int
    fmt: str


def _create_app(
    root: Path,
    llm_config: LLMConfig,
    *,
    _engine: Any = None,
) -> FastAPI:
    """Create and return the FastAPI application.

    Args:
        root: Advisor root directory.
        llm_config: LLM backend config.
        _engine: Injected AdvisorEngine for testing; if None, one is created.
    """
    if _engine is None:
        from ..llm.factory import create_client  # noqa: PLC0415
        from .advisor_engine import AdvisorEngine  # noqa: PLC0415
        llm = create_client(llm_config)
        engine = AdvisorEngine(root, llm)
    else:
        engine = _engine

    advisors = engine.discover()
    if not advisors:
        raise RuntimeError(
            f"Ingen rådgivere fundet i {root}. "
            "Opret undermapper med en prompts/-mappe."
        )

    from .db import init_db  # noqa: PLC0415
    init_db()

    static_dir = Path(__file__).parent / "static"
    static_dir.mkdir(parents=True, exist_ok=True)

    app = FastAPI(title="JuraKlar")

    @app.get("/")
    async def index() -> FileResponse:
        return FileResponse(static_dir / "index.html", media_type="text/html")

    @app.get("/api/advisors")
    async def get_advisors() -> list[dict]:
        sorted_adv = _sort_advisors(engine.discover())
        return [
            {
                "id": adv.id,
                "title": adv.title,
                "services": [
                    {"id": s.id, "title": s.title, "category": s.category}
                    for s in adv.services
                ],
            }
            for adv in sorted_adv.values()
        ]

    @app.post("/api/chat")
    async def chat(req: _ChatRequest) -> StreamingResponse:
        if req.docs:
            doc_block = "\n\n".join(
                f"### Uploadet: {d.name}\n{d.text[:4000]}" for d in req.docs
            )
            full_question = (
                f"Brugeren har uploadet følgende dokument(er):\n\n"
                f"{doc_block}\n\n---\n\n{req.question}"
            )
        else:
            full_question = req.question

        async def _stream() -> Any:
            try:
                answer = await engine.ask(req.advisor_id, req.service_id, full_question)
            except Exception as exc:  # noqa: BLE001
                yield f"data: {json.dumps({'error': str(exc)})}\n\n"
                yield "data: [DONE]\n\n"
                return
            words = answer.split(" ")
            for i, word in enumerate(words):
                token = word if i == 0 else " " + word
                yield f"data: {json.dumps({'t': token})}\n\n"
                await asyncio.sleep(0.02)
            yield "data: [DONE]\n\n"

        return StreamingResponse(_stream(), media_type="text/event-stream")

    @app.delete("/api/history/{advisor_id}/{service_id}", status_code=204)
    async def clear_history(advisor_id: str, service_id: int) -> None:
        engine.clear(advisor_id, service_id)

    @app.post("/api/upload")
    async def upload_file(
        file: UploadFile = File(...),
        session_id: str = Form(""),
    ) -> dict:
        content = await file.read()
        ext = Path(file.filename or "file.txt").suffix.lower() or ".txt"
        try:
            from markitdown import MarkItDown  # noqa: PLC0415
            result = MarkItDown().convert_stream(io.BytesIO(content), file_extension=ext)
            text = result.text_content or ""
        except Exception as exc:  # noqa: BLE001
            text = f"(Kunne ikke parse: {exc})"
        return {"name": file.filename or "unknown", "text": text}

    @app.get("/api/download")
    async def download_chat(grant_id: str) -> Response:
        from .db import consume_grant  # noqa: PLC0415
        grant = consume_grant(grant_id)
        if not grant:
            raise HTTPException(403, "Ugyldig eller udløbet download-tilladelse")

        advisor_id = grant["advisor_id"]
        service_id = grant["service_id"]
        fmt = grant["fmt"]

        history = engine.get_history(advisor_id, service_id)
        all_advisors = engine.discover()
        adv = all_advisors.get(advisor_id)
        svc = next((s for s in adv.services if s.id == service_id), None) if adv else None
        title = adv.title if adv else advisor_id
        svc_title = svc.title if svc else str(service_id)

        if fmt == "md":
            lines = [f"# JuraKlar — {title}", f"## {svc_title}", "", "---", ""]
            for msg in history:
                if msg["role"] == "user":
                    lines += [f"**Dig:** {msg['content']}", ""]
                else:
                    lines += [f"**JuraKlar:**\n\n{msg['content']}", ""]
            body = "\n".join(lines)
            filename = "juraklar-raadgivning.md"
            media_type = "text/markdown"
        elif fmt == "html":
            rows = ""
            for msg in history:
                if msg["role"] == "user":
                    safe = msg["content"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    rows += f'<div class="msg user"><span class="label">Dig</span><p>{safe}</p></div>\n'
                else:
                    rows += f'<div class="msg bot"><span class="label">JuraKlar</span><div class="md-body">{msg["content"]}</div></div>\n'
            body = f"""<!DOCTYPE html>
<html lang="da"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>JuraKlar — {title}</title>
<script src="https://cdn.jsdelivr.net/npm/marked@13/marked.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dompurify@3/dist/purify.min.js"></script>
<style>
  body{{font-family:system-ui,sans-serif;max-width:800px;margin:40px auto;padding:0 20px;color:#1a3a28;background:#f8fdf9}}
  h1{{color:#0a6e40}}h2{{color:#3a6a50;margin-top:0}}
  .header{{border-bottom:2px solid #c8e8d8;padding-bottom:16px;margin-bottom:24px}}
  .msg{{margin-bottom:20px;padding:14px 18px;border-radius:10px}}
  .msg.user{{background:#e0f5ea;border-left:4px solid #0a6e40}}
  .msg.bot{{background:#fff;border:1px solid #c8e8d8}}
  .label{{display:inline-block;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:6px;color:#3a6a50}}
  .msg.user .label{{color:#0a6e40}}
  p{{margin:0 0 .6em}}p:last-child{{margin-bottom:0}}
  table{{border-collapse:collapse;width:100%;margin:.6em 0;font-size:.9em}}
  th,td{{border:1px solid #c8e8d8;padding:7px 12px;text-align:left;vertical-align:top}}
  th{{background:#e0f5ea;color:#0a6e40;font-weight:700}}
  tr:nth-child(even) td{{background:#f0faf5}}
  code{{background:#e0f5ea;border-radius:4px;padding:1px 5px;font-size:.88em}}
  pre{{background:#e0f5ea;border-radius:6px;padding:12px;overflow-x:auto}}
  footer{{margin-top:40px;font-size:12px;color:#7aaa88;border-top:1px solid #c8e8d8;padding-top:12px}}
</style></head><body>
<div class="header"><h1>JuraKlar</h1><h2>{title}{" — " + svc_title if svc_title else ""}</h2></div>
{rows}
<footer>Genereret af JuraKlar · Generel juridisk information, ikke personlig rådgivning</footer>
<script>marked.use({{breaks:true,gfm:true}});document.querySelectorAll('.md-body').forEach(el=>{{el.innerHTML=DOMPurify.sanitize(marked.parse(el.textContent));}});</script>
</body></html>"""
            filename = "juraklar-raadgivning.html"
            media_type = "text/html"
        else:
            sep = "=" * 50
            lines = [f"JuraKlar — {title}", svc_title, "", sep, ""]
            for msg in history:
                if msg["role"] == "user":
                    lines += [f"Dig: {msg['content']}", ""]
                else:
                    plain = re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", msg["content"])
                    plain = re.sub(r"#{1,6}\s+", "", plain)
                    lines += [f"JuraKlar: {plain}", ""]
            body = "\n".join(lines)
            filename = "juraklar-raadgivning.txt"
            media_type = "text/plain"

        return Response(
            content=body.encode("utf-8"),
            media_type=media_type,
            headers={"Content-Disposition": f'attachment; filename="{filename}"'},
        )

    @app.post("/api/review")
    async def submit_review(req: _ReviewRequest) -> dict:
        from .db import create_token  # noqa: PLC0415
        if not 1 <= req.rating <= 5:
            raise HTTPException(400, "Bedømmelse skal være 1–5")
        token = create_token(req.email, req.advisor_id, req.rating, req.comment or None)
        return {"token": f"{token[:4]}-{token[4:]}"}

    @app.post("/api/token/validate")
    async def validate_token(req: _TokenValidateRequest) -> dict:
        from .db import validate_and_consume_token, create_grant  # noqa: PLC0415
        if not validate_and_consume_token(req.token):
            raise HTTPException(400, "Ugyldig eller udløbet kode")
        grant_id = create_grant(req.advisor_id, req.service_id, req.fmt)
        return {"grant_id": grant_id}

    @app.post("/api/stripe/checkout")
    async def stripe_checkout(req: _StripeCheckoutRequest) -> dict:
        import stripe  # noqa: PLC0415
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
        if not stripe.api_key:
            raise HTTPException(503, "Stripe ikke konfigureret")
        base_url = os.getenv("BASE_URL", "http://localhost:8080")
        session = stripe.checkout.Session.create(
            payment_method_types=["card", "mobilepay"],
            line_items=[{
                "price_data": {
                    "currency": "dkk",
                    "product_data": {"name": "JuraKlar — Download samtale"},
                    "unit_amount": 19900,
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url=(
                f"{base_url}/?stripe_success=1"
                f"&session_id={{CHECKOUT_SESSION_ID}}"
                f"&advisor={req.advisor_id}&service={req.service_id}&fmt={req.fmt}"
            ),
            cancel_url=f"{base_url}/",
            metadata={"advisor_id": req.advisor_id, "service_id": str(req.service_id), "fmt": req.fmt},
        )
        return {"checkout_url": session.url}

    @app.post("/api/stripe/verify")
    async def stripe_verify(req: _StripeVerifyRequest) -> dict:
        import stripe  # noqa: PLC0415
        from .db import create_grant  # noqa: PLC0415
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "")
        session = stripe.checkout.Session.retrieve(req.session_id)
        if session.payment_status != "paid":
            raise HTTPException(402, "Betaling ikke gennemført")
        grant_id = create_grant(req.advisor_id, req.service_id, req.fmt)
        return {"grant_id": grant_id}

    return app


def start_advisor_ui(
    root: Path,
    llm_config: LLMConfig,
    *,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> None:
    """Start the FastAPI server with JuraKlar advisor chat interface."""
    try:
        import uvicorn  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("uvicorn ikke installeret — kør: pip install uvicorn[standard]") from exc

    effective_host = os.environ.get("WIKI_UI_HOST", host)
    effective_port = int(os.environ.get("WIKI_UI_PORT", port))

    app = _create_app(root, llm_config)
    uvicorn.run(app, host=effective_host, port=effective_port)
