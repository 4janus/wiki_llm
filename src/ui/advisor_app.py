"""NiceGUI 3.x advisor chat interface — JuraKlar juridisk rådgivning.

Layout (position:fixed flex-kolonne, fylder præcis viewport):
  1. Header            – logo + undertitel
  2. Domæne-tabs       – scrollbar ved mange domæner (≥20)
  3. Nav-panel         – kategori-pills; klik → spørgsmåls-pills (progressiv disclosure)
  4. Chat-område       – scrollbart boble-layout, vokser til at fylde resten
  5. Upload-chips      – vises kun når dokumenter er uploadet
  6. Input-række       – tekstfelt + Send + Ryd + 📎 Upload + 💾 Download

Interaktion:
  - Klik domæne-tab      → skifter domæne, kollaps kategori
  - Klik kategori-pill   → fold ud / ind spørgsmål (toggle)
  - Klik spørgsmål-pill  → forudfylder inputfelt + sætter aktiv service
  - 📎 Upload            → parser PDF/DOCX/TXT med MarkItDown, vises som chip
  - 💾 Download          → downloader hele samtalen som .md
  - Send / Enter         → sender spørgsmål med uploadet dokumentkontekst hvis relevant
"""
from __future__ import annotations

import io
import os
from pathlib import Path

from ..models.config import LLMConfig

# ── Advisor display order (matches 20_rådgivere.txt top-to-bottom) ─────────
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


# ── CSS injiceret én gang per side ────────────────────────────────────────────
_PAGE_CSS = """
body, html { margin: 0; padding: 0; overflow: hidden; height: 100%; }
/* Fyld præcis viewport — position:fixed er mere robust end 100dvh */
.jk-root {
    position: fixed; inset: 0;
    display: flex; flex-direction: column;
    background: #121212;
}
.jk-header {
    flex: 0 0 auto;
    display: flex; align-items: center; gap: 10px;
    padding: 8px 16px;
    background: #1c1c1c; border-bottom: 1px solid #2e2e2e;
}
.jk-tabs   { flex: 0 0 auto; background: #1c1c1c; border-bottom: 1px solid #242424; }
.jk-nav    { flex: 0 0 auto; background: #1a1a1a; border-bottom: 1px solid #242424;
             padding: 10px 16px; min-height: 42px; }
.jk-chat   { flex: 1 1 0; min-height: 0; width: 100%; }
.jk-uploads {
    flex: 0 0 auto;
    display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
    padding: 6px 16px; background: #191919; border-top: 1px solid #2a2a2a;
}
.jk-input  {
    flex: 0 0 auto;
    display: flex; gap: 8px; align-items: center;
    padding: 10px 16px;
    background: #1c1c1c; border-top: 1px solid #2e2e2e;
}
/* Chat-bobler */
.jk-user { background:#1565c0; color:#fff; border-radius:12px 12px 4px 12px;
           padding:8px 12px; max-width:75%; word-wrap:break-word; }
.jk-bot  { background:#1e1e1e; border:1px solid #333;
           border-radius:4px 12px 12px 12px; padding:10px 14px; width:100%; }
"""


def start_advisor_ui(
    root: Path,
    llm_config: LLMConfig,
    *,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> None:
    """Start NiceGUI-serveren med JuraKlar advisor chat-interface.

    Args:
        root: Rodmappe med rådgiver-undermapper (fx ``juraklar/``).
        llm_config: LLM-konfiguration.
        host: Netværksinterface (standard ``0.0.0.0``).
        port: TCP-port (standard ``8080``).
    """
    try:
        from nicegui import ui  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("nicegui ikke installeret — kør: pip install nicegui") from exc

    from ..llm.factory import create_client  # noqa: PLC0415
    from .advisor_engine import AdvisorEngine  # noqa: PLC0415

    llm = create_client(llm_config)
    engine = AdvisorEngine(root, llm)
    advisors = engine.discover()

    if not advisors:
        raise RuntimeError(
            f"Ingen rådgivere fundet i {root}. "
            "Opret undermapper med en prompts/-mappe."
        )

    effective_host = os.environ.get("WIKI_UI_HOST", host)
    effective_port = int(os.environ.get("WIKI_UI_PORT", port))
    storage_secret = os.environ.get("WIKI_UI_STORAGE_SECRET", "juraklar-secret")

    @ui.page("/")
    async def index_page() -> None:  # noqa: C901
        ui.dark_mode(True)
        ui.add_css(_PAGE_CSS)

        # ── per-side state ────────────────────────────────────────────────────
        first_id = next(iter(advisors))
        first_adv = advisors[first_id]
        first_svc_id = first_adv.services[0].id if first_adv.services else 0

        state: dict = {
            "advisor":        first_id,
            "category":       None,   # None = alle kategorier kollapsede
            "service":        first_svc_id,
            "uploaded_docs":  [],     # [{"name": str, "text": str}, ...]
        }

        # ── hjælpefunktioner ──────────────────────────────────────────────────

        def cur_adv():
            return advisors[state["advisor"]]

        def cats_for_cur() -> dict[str, list]:
            result: dict[str, list] = {}
            for svc in cur_adv().services:
                result.setdefault(svc.category or "Generelt", []).append(svc)
            return result

        # ── chat-rendering ────────────────────────────────────────────────────

        def _render_msg(role: str, content: str) -> None:
            if role == "user":
                with ui.row().classes("w-full justify-end q-mb-xs"):
                    ui.label(content).classes("jk-user text-sm")
            else:
                with ui.element("div").classes("jk-bot q-mb-xs"):
                    ui.markdown(content).classes("text-sm text-grey-2")

        def refresh_chat() -> None:
            chat_container.clear()
            history = engine.get_history(state["advisor"], state["service"])
            with chat_container:
                if not history:
                    svc = next(
                        (s for s in cur_adv().services if s.id == state["service"]),
                        None,
                    )
                    placeholder = (
                        f"📋 **{svc.title}**\n\nKlik Send, eller skriv dit spørgsmål nedenfor."
                        if svc else "Vælg et emne ovenfor og stil dit spørgsmål."
                    )
                    with ui.element("div").classes("jk-bot q-mt-sm"):
                        ui.markdown(placeholder).classes("text-sm text-grey-3")
                    return
                for msg in history:
                    _render_msg(msg["role"], msg["content"])

        # ── event-handlers ────────────────────────────────────────────────────

        def on_advisor_change(advisor_id: str) -> None:
            state["advisor"] = advisor_id
            state["category"] = None
            adv = advisors.get(advisor_id)
            if adv and adv.services:
                state["service"] = adv.services[0].id
            nav_panel.refresh()
            refresh_chat()

        def on_category_toggle(cat_name: str) -> None:
            state["category"] = None if state["category"] == cat_name else cat_name
            nav_panel.refresh()

        def on_question_click(svc) -> None:
            state["service"] = svc.id
            nav_panel.refresh()
            input_box.value = svc.title
            input_box.run_method("focus")
            refresh_chat()

        async def send() -> None:
            raw = input_box.value.strip()
            if not raw:
                return
            input_box.value = ""

            # Byg fuld kontekst inkl. uploadede dokumenter
            if state["uploaded_docs"]:
                doc_block = "\n\n".join(
                    f"### Uploadet: {d['name']}\n{d['text'][:4000]}"
                    for d in state["uploaded_docs"]
                )
                full_question = (
                    f"Brugeren har uploadet følgende dokument(er) til gennemsyn:\n\n"
                    f"{doc_block}\n\n---\n\n{raw}"
                )
            else:
                full_question = raw

            cur_a = state["advisor"]
            cur_s = state["service"]
            with chat_container:
                _render_msg("user", raw)          # vis kun brugerens tekst i chat
                thinking = ui.label("…").classes("text-grey-5 text-sm q-ml-sm q-mb-xs")
            try:
                answer = await engine.ask(cur_a, cur_s, full_question)
            except Exception as exc:  # noqa: BLE001
                answer = f"**Fejl:** {exc}"
            thinking.delete()
            if state["advisor"] == cur_a and state["service"] == cur_s:
                with chat_container:
                    _render_msg("assistant", answer)

        def clear_chat() -> None:
            engine.clear(state["advisor"], state["service"])
            refresh_chat()

        async def handle_upload(e) -> None:
            """Parser uploadet fil med MarkItDown og gemmer tekst i state."""
            try:
                from markitdown import MarkItDown  # noqa: PLC0415
                raw_bytes = await e.file.read()
                ext = Path(e.file.name).suffix.lower() or ".txt"
                md_conv = MarkItDown()
                result = md_conv.convert_stream(io.BytesIO(raw_bytes), file_extension=ext)
                text = result.text_content or ""
                state["uploaded_docs"].append({"name": e.file.name, "text": text})
            except Exception as exc:  # noqa: BLE001
                state["uploaded_docs"].append({
                    "name": e.file.name,
                    "text": f"(Kunne ikke parse: {exc})",
                })
            upload_chips.refresh()

        def remove_doc(idx: int) -> None:
            if 0 <= idx < len(state["uploaded_docs"]):
                state["uploaded_docs"].pop(idx)
            upload_chips.refresh()

        def download_chat(fmt: str = "md") -> None:
            """Download hele samtalen som Markdown eller ren tekst."""
            import re as _re  # noqa: PLC0415
            history = engine.get_history(state["advisor"], state["service"])
            if not history:
                return
            adv = cur_adv()
            svc = next((s for s in adv.services if s.id == state["service"]), None)
            title = adv.title
            svc_title = svc.title if svc else ""

            if fmt == "md":
                lines = [
                    f"# JuraKlar — {title}",
                    f"## {svc_title}",
                    "",
                    "---",
                    "",
                ]
                for msg in history:
                    if msg["role"] == "user":
                        lines += [f"**Dig:** {msg['content']}", ""]
                    else:
                        lines += [f"**JuraKlar:**\n\n{msg['content']}", ""]
                content = "\n".join(lines)
                filename = "juraklar-rådgivning.md"
                media_type = "text/markdown"
            else:  # txt
                sep = "=" * 50
                lines = [f"JuraKlar — {title}", svc_title, "", sep, ""]
                for msg in history:
                    if msg["role"] == "user":
                        lines += [f"Dig: {msg['content']}", ""]
                    else:
                        plain = _re.sub(r"\*{1,2}(.+?)\*{1,2}", r"\1", msg["content"])
                        plain = _re.sub(r"#{1,6}\s+", "", plain)
                        lines += [f"JuraKlar: {plain}", ""]
                content = "\n".join(lines)
                filename = "juraklar-rådgivning.txt"
                media_type = "text/plain"

            ui.download(content.encode("utf-8"), filename=filename, media_type=media_type)

        # ── navigations-panel (refreshable) ───────────────────────────────────
        @ui.refreshable
        def nav_panel() -> None:
            cats = cats_for_cur()
            sel_cat = state["category"]

            # Række 1: kategori-pills
            with ui.row().classes("flex-wrap gap-2 items-center"):
                for cat_name, svcs in cats.items():
                    is_active = cat_name == sel_cat
                    (
                        ui.chip(
                            f"{cat_name} ({len(svcs)})",
                            on_click=lambda c=cat_name: on_category_toggle(c),
                        )
                        .props("dense color=primary" if is_active else "dense outline color=grey-6")
                        .classes("cursor-pointer font-medium")
                    )

            # Række 2: spørgsmåls-pills — kun når kategori er valgt
            if sel_cat and sel_cat in cats:
                with ui.element("div").style("margin-top: 10px;"):
                    ui.label(sel_cat).classes("text-grey-5").style(
                        "font-size: 10px; text-transform: uppercase; letter-spacing: 0.6px;"
                    )
                    with ui.row().classes("flex-wrap gap-2").style("margin-top: 4px;"):
                        for svc in cats[sel_cat]:
                            is_active_svc = svc.id == state["service"]
                            (
                                ui.chip(
                                    svc.title,
                                    on_click=lambda s=svc: on_question_click(s),
                                )
                                .props("dense color=primary" if is_active_svc else "dense outline color=grey-5")
                                .classes("cursor-pointer")
                                .style("font-size: 12px;")
                            )

        # ── uploadede filer (refreshable) ─────────────────────────────────────
        @ui.refreshable
        def upload_chips() -> None:
            if not state["uploaded_docs"]:
                return
            ui.label("📎 Dokumenter:").classes("text-xs text-grey-5")
            for i, doc in enumerate(state["uploaded_docs"]):
                ui.chip(
                    doc["name"],
                    on_click=lambda idx=i: remove_doc(idx),
                ).props("dense outline color=grey-5 removable").classes("text-xs")

        # ── side-layout ───────────────────────────────────────────────────────
        with ui.element("div").classes("jk-root"):

            # 1. Header
            with ui.element("div").classes("jk-header"):
                ui.label("⚖️ JuraKlar").classes("text-h6 text-bold text-white")
                ui.label("Juridisk rådgivning").classes("text-caption text-grey-5")

            # 2. Domæne-tabs
            with ui.element("div").classes("jk-tabs"):
                with ui.tabs(
                    value=state["advisor"],
                    on_change=lambda e: on_advisor_change(e.value),
                ).classes("w-full").props("align=left dense"):
                    for adv_id, adv in advisors.items():
                        ui.tab(adv_id, label=adv.title)

            # 3. Kategori + spørgsmål
            with ui.element("div").classes("jk-nav"):
                nav_panel()

            # 4. Chat-scrollområde
            with ui.scroll_area().classes("jk-chat"):
                chat_container = ui.column().classes("w-full gap-1").style("padding: 16px;")

            # 5. Upload-chips (skjult når tom)
            with ui.element("div").classes("jk-uploads"):
                upload_chips()

            # 6. Input-række
            with ui.element("div").classes("jk-input"):
                # Skjult upload-komponent — trigges af knappen nedenfor
                # Uploaderen er usynlig men monteret (position:absolute, opacity:0).
                # display:none forhindrer browseren i at åbne file-pickeren — opacity:0 gør det ikke.
                uploader = (
                    ui.upload(on_upload=handle_upload, auto_upload=True, multiple=True)
                    .props('accept=".pdf,.docx,.txt,.md" flat dense')
                    .style(
                        "position: absolute; opacity: 0; width: 1px; height: 1px; "
                        "overflow: hidden; pointer-events: none;"
                    )
                )
                ui.button(
                    icon="attach_file",
                    on_click=lambda: uploader.run_method("pickFiles"),
                ).props("flat dense color=grey-5").tooltip("Upload dokument (PDF, DOCX, TXT)")

                input_box = (
                    ui.input(placeholder="Skriv dit spørgsmål…")
                    .classes("flex-1")
                    .props("dense outlined dark")
                )
                input_box.on("keydown.enter", send)
                ui.button("Send", on_click=send).props("color=primary dense")
                ui.button("Ryd", on_click=clear_chat).props("flat color=grey-6 dense size=sm")
                with ui.button(icon="download").props("flat dense color=grey-5").tooltip("Download samtale"):
                    with ui.menu():
                        ui.menu_item("Markdown (.md)", on_click=lambda: download_chat("md"))
                        ui.menu_item("Ren tekst (.txt)", on_click=lambda: download_chat("txt"))

        refresh_chat()

    ui.run(
        host=effective_host,
        port=effective_port,
        title="JuraKlar — Juridisk Rådgivning",
        storage_secret=storage_secret,
        reload=False,
    )
