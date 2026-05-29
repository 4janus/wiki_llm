"""FastAPI advisor chat interface — JuraKlar juridisk rådgivning."""
from __future__ import annotations

import asyncio
import io
import json
import os
import re
from pathlib import Path
from typing import Any

from fastapi import FastAPI, File, Form, UploadFile
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
            answer = await engine.ask(req.advisor_id, req.service_id, full_question)
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
        return {"name": file.filename, "text": text}

    @app.get("/api/download/{advisor_id}/{service_id}")
    async def download_chat(
        advisor_id: str,
        service_id: int,
        fmt: str = "md",
    ) -> Response:
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
