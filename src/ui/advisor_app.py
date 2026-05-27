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
/* ── Reset ───────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; }
body, html { margin: 0; padding: 0; height: 100%; overflow: hidden; }

/* ── CSS Variables: Dark (default) ──────────────────────────── */
:root {
  --bg-deep:            #080f0c;
  --bg-base:            #0c1510;
  --bg-surface:         #0d1f16;
  --bg-sidebar:         #0a1a12;
  --bg-bubble-user:     #0d4a30;
  --bg-bubble-bot:      #0d1f16;
  --border:             #1a3028;
  --accent:             #4ade99;
  --accent-btn:         #0d4a30;
  --accent-btn-border:  #1a6040;
  --text-primary:       #e0e0e0;
  --text-secondary:     #8ab898;
  --text-dim:           #3a6a50;
  --text-muted:         #2a4a32;
  --bubble-user-text:   #a0ffc8;
  --bubble-bot-text:    #a0c8b4;
}

/* ── CSS Variables: Light ────────────────────────────────────── */
body.light-mode {
  --bg-deep:            #ffffff;
  --bg-base:            #f8fdf9;
  --bg-surface:         #f0faf5;
  --bg-sidebar:         #e0f5ea;
  --bg-bubble-user:     #0a6e40;
  --bg-bubble-bot:      #f0faf5;
  --border:             #c8e8d8;
  --accent:             #0a6e40;
  --accent-btn:         #0a6e40;
  --accent-btn-border:  #087840;
  --text-primary:       #1a3a28;
  --text-secondary:     #3a6a50;
  --text-dim:           #7aaa88;
  --text-muted:         #aaccbb;
  --bubble-user-text:   #ffffff;
  --bubble-bot-text:    #1a3a28;
}

/* ── Root ────────────────────────────────────────────────────── */
.jk-root {
  position: fixed; inset: 0;
  display: flex; flex-direction: column;
  background: var(--bg-base); color: var(--text-primary);
}

/* ── Header ──────────────────────────────────────────────────── */
.jk-header {
  flex: 0 0 auto; display: flex; align-items: center; gap: 10px;
  padding: 8px 16px;
  background: var(--bg-surface); border-bottom: 1px solid var(--border);
}
.jk-logo {
  font-size: 16px; font-weight: 800; color: var(--text-primary);
  cursor: pointer; user-select: none;
}
.jk-breadcrumb { font-size: 11px; color: var(--text-dim); }
.jk-spacer { flex: 1; }
.jk-hamburger {
  display: none;
  font-size: 22px; color: var(--text-secondary);
  cursor: pointer; background: none; border: none; padding: 2px 6px;
  line-height: 1;
}
.jk-toggle {
  font-size: 18px; cursor: pointer; color: var(--text-dim);
  background: none; border: none; padding: 2px 6px; line-height: 1;
}

/* ── Body ────────────────────────────────────────────────────── */
.jk-body { flex: 1 1 0; min-height: 0; display: flex; }

/* ── Sidebar ─────────────────────────────────────────────────── */
.jk-sidebar {
  width: 160px; flex-shrink: 0;
  background: var(--bg-sidebar); border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  padding: 8px; gap: 2px; overflow-y: auto;
}
.jk-vælg-btn {
  background: var(--accent-btn); color: var(--accent);
  border: 1px solid var(--accent-btn-border); border-radius: 7px;
  padding: 7px 8px; font-size: 11px; font-weight: 800;
  text-align: center; cursor: pointer; letter-spacing: 0.3px;
  margin-bottom: 4px; user-select: none;
}
.jk-advisor {
  padding: 5px 8px; border-radius: 5px; font-size: 11px;
  color: var(--text-secondary); cursor: pointer;
}
.jk-advisor:hover { background: rgba(13,74,48,0.2); }
.jk-advisor.active { background: rgba(13,74,48,0.35); color: var(--accent); font-weight: 700; }
.jk-advisor.dimmed { color: var(--text-muted); }
.jk-submenu {
  padding: 3px 16px; font-size: 10px; color: var(--text-dim); cursor: pointer;
}
.jk-submenu:hover { color: var(--accent); }
.jk-submenu.active { color: var(--accent); font-weight: 700; }

/* ── Main column ─────────────────────────────────────────────── */
.jk-main { flex: 1 1 0; min-width: 0; display: flex; flex-direction: column; }

/* ── Pill strip (mobile) ─────────────────────────────────────── */
.jk-pill-strip {
  display: none;
  flex-shrink: 0;
  background: var(--bg-sidebar); border-bottom: 1px solid var(--border);
  padding: 6px 12px;
}
.jk-pill-advisor {
  font-size: 11px; color: var(--accent); font-weight: 700;
  margin-bottom: 5px; cursor: pointer;
}
.jk-pills { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 2px; }
.jk-pill {
  font-size: 10px; border-radius: 12px; padding: 3px 10px;
  cursor: pointer; white-space: nowrap; flex-shrink: 0;
}
.jk-pill.active { background: var(--accent-btn); color: var(--accent); }
.jk-pill.inactive { border: 1px solid var(--border); color: var(--text-dim); }

/* ── Chat ────────────────────────────────────────────────────── */
.jk-chat { flex: 1 1 0; min-height: 0; background: var(--bg-deep); }

/* ── Forside ─────────────────────────────────────────────────── */
.jk-forside { padding: 24px; max-width: 620px; }
.jk-forside-title {
  font-size: 18px; font-weight: 800; color: var(--accent); margin-bottom: 10px;
}
.jk-forside-text {
  font-size: 13px; color: var(--text-secondary); line-height: 1.8; margin-bottom: 16px;
}
.jk-forside-section {
  font-size: 13px; font-weight: 700; color: var(--text-primary); margin-bottom: 4px;
}
.jk-consent-box {
  background: var(--bg-surface); border: 1px solid var(--border); border-radius: 10px;
  padding: 16px; margin-top: 8px;
}
.jk-consent-title {
  font-size: 13px; font-weight: 700; color: var(--text-primary); margin-bottom: 8px;
}
.jk-consent-body {
  font-size: 12px; color: var(--text-secondary); line-height: 1.8; margin-bottom: 12px;
}

/* ── Chat bubbles ────────────────────────────────────────────── */
.jk-user {
  background: var(--bg-bubble-user); color: var(--bubble-user-text);
  border-radius: 14px 14px 4px 14px; padding: 10px 14px;
  max-width: 75%; word-wrap: break-word; font-size: 14px;
}
.jk-bot {
  background: var(--bg-bubble-bot); border: 1px solid var(--border);
  border-radius: 4px 14px 14px 14px; padding: 12px 16px;
  max-width: 88%; font-size: 14px;
  color: var(--text-primary); line-height: 1.65;
}

/* ── Upload chips ────────────────────────────────────────────── */
.jk-uploads {
  flex: 0 0 auto; display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
  padding: 6px 16px; background: var(--bg-surface); border-top: 1px solid var(--border);
}

/* ── Input row ───────────────────────────────────────────────── */
.jk-input {
  flex: 0 0 auto; display: flex; gap: 8px; align-items: center;
  padding: 10px 16px; background: var(--bg-surface); border-top: 1px solid var(--border);
}
.jk-input-locked { opacity: 0.38; pointer-events: none; }

/* ── Mobile drawer overlay ───────────────────────────────────── */
.jk-drawer-overlay {
  position: fixed; inset: 0; z-index: 500;
  display: none; background: rgba(0,0,0,0.62);
}
.jk-drawer-overlay.open { display: flex; }
.jk-drawer {
  width: min(80vw, 300px); height: 100%;
  background: var(--bg-sidebar); border-right: 1px solid var(--border);
  display: flex; flex-direction: column;
  padding: 10px; gap: 2px; overflow-y: auto;
}
.jk-drawer-close {
  font-size: 12px; color: var(--text-dim); text-align: right;
  cursor: pointer; margin-bottom: 6px; user-select: none;
}

/* ── Responsive ──────────────────────────────────────────────── */
@media (max-width: 767px) {
  .jk-sidebar   { display: none !important; }
  .jk-hamburger { display: block !important; }
  .jk-breadcrumb { display: none; }
}
@media (min-width: 768px) {
  .jk-hamburger  { display: none !important; }
  .jk-drawer-overlay { display: none !important; }
}
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

        # ── State ─────────────────────────────────────────────────────────
        state: dict = {
            "consent_accepted": False,
            "advisor":          None,   # str | None
            "category":         None,   # str | None
            "service":          None,   # int | None
            "uploaded_docs":    [],
            "dark_mode":        True,
        }

        # ── Dark/light toggle ──────────────────────────────────────────────
        dark_ref = ui.dark_mode(True)

        def _toggle_dark() -> None:
            state["dark_mode"] = not state["dark_mode"]
            if state["dark_mode"]:
                dark_ref.enable()
                ui.run_javascript("document.body.classList.remove('light-mode')")
                toggle_btn.set_text("🌙")
            else:
                dark_ref.disable()
                ui.run_javascript("document.body.classList.add('light-mode')")
                toggle_btn.set_text("☀️")

        # ── Root container ─────────────────────────────────────────────────
        with ui.element("div").classes("jk-root"):

            # 1. Header
            with ui.element("div").classes("jk-header"):
                hamburger_btn = (
                    ui.button("☰", on_click=lambda: _open_drawer())
                    .classes("jk-hamburger")
                    .props("flat dense")
                )
                logo_btn = (
                    ui.label("⚖️ JuraKlar")
                    .classes("jk-logo")
                    .on("click", lambda: _reset_to_forside())
                )
                breadcrumb_label = ui.label("").classes("jk-breadcrumb")
                ui.element("div").classes("jk-spacer")
                toggle_btn = (
                    ui.button("🌙", on_click=_toggle_dark)
                    .classes("jk-toggle")
                    .props("flat dense")
                )

            # 2. Body (sidebar + main)
            with ui.element("div").classes("jk-body"):

                # ── Sidebar (desktop) ──────────────────────────────────────
                with ui.element("div").classes("jk-sidebar") as sidebar_container:
                    _sidebar_content()

                # ── Main column ────────────────────────────────────────────
                with ui.element("div").classes("jk-main"):

                    # 2a. Pill strip (mobile only — shown after advisor selected)
                    pill_strip_el = ui.element("div").classes("jk-pill-strip")

                    # 2b. Chat scroll area
                    with ui.scroll_area().classes("jk-chat"):
                        chat_container = (
                            ui.column()
                            .classes("w-full gap-2")
                            .style("padding: 16px;")
                        )

                    # 2c. Upload chips (hidden when empty)
                    with ui.element("div").classes("jk-uploads") as upload_chips_el:
                        pass

                    # 2d. Input row
                    with ui.element("div").classes("jk-input jk-input-locked") as input_row_el:
                        uploader = (
                            ui.upload(on_upload=lambda e: None, auto_upload=True, multiple=True)
                            .props('accept=".pdf,.docx,.txt,.md" flat dense')
                            .style(
                                "position:absolute;opacity:0;width:1px;height:1px;"
                                "overflow:hidden;pointer-events:none;"
                            )
                        )
                        ui.button(
                            icon="attach_file",
                            on_click=lambda: uploader.run_method("pickFiles"),
                        ).props("flat dense color=grey-5").tooltip("Upload dokument")

                        input_box = (
                            ui.input(placeholder="Acceptér consent for at starte…")
                            .classes("flex-1")
                            .props("dense outlined dark")
                        )
                        ui.button("Send").props("color=primary dense")
                        ui.button("Ryd").props("flat color=grey-6 dense size=sm")
                        with ui.button(icon="download").props("flat dense color=grey-5"):
                            with ui.menu():
                                ui.menu_item("Markdown (.md)")
                                ui.menu_item("Ren tekst (.txt)")

            # 3. Mobile drawer overlay (always mounted, hidden by CSS)
            drawer_overlay_el = ui.element("div").classes("jk-drawer-overlay")
            with drawer_overlay_el:
                with ui.element("div").classes("jk-drawer"):
                    ui.label("✕ luk").classes("jk-drawer-close").on(
                        "click", lambda: _close_drawer()
                    )
                    ui.label("(drawer stub)").classes("text-xs")
                # Tap on backdrop closes drawer
                drawer_overlay_el.on(
                    "click",
                    js_handler="""(e) => {
                        if (e.target === e.currentTarget)
                            e.currentTarget.classList.remove('open');
                    }""",
                )

        # Initialise page
        _refresh_chat()

        # ── Helper stubs (filled in later tasks) ──────────────────────────
        def _open_drawer():
            ui.run_javascript(
                "document.querySelector('.jk-drawer-overlay').classList.add('open')"
            )

        def _close_drawer():
            ui.run_javascript(
                "document.querySelector('.jk-drawer-overlay').classList.remove('open')"
            )

        def _reset_to_forside():
            state["consent_accepted"] = False
            state["advisor"] = None
            state["category"] = None
            state["service"] = None
            _refresh_sidebar()
            _refresh_pill_strip()
            _refresh_chat()
            _refresh_breadcrumb()
            input_row_el.classes(add="jk-input-locked")
            input_box.props("placeholder='Acceptér consent for at starte…'")

        # ── Sidebar state helpers ──────────────────────────────────────────

        sorted_advisors = _sort_advisors(advisors)

        def _on_advisor_click(advisor_id: str) -> None:
            state["advisor"] = advisor_id
            state["category"] = None
            adv = advisors[advisor_id]
            state["service"] = adv.services[0].id if adv.services else None
            _refresh_sidebar()
            _refresh_pill_strip()
            _refresh_chat()
            _refresh_breadcrumb()
            _close_drawer()

        def _on_service_click(svc) -> None:
            state["service"] = svc.id
            input_box.value = svc.title
            input_box.run_method("focus")
            _refresh_sidebar()
            _refresh_pill_strip()
            _refresh_chat()
            _refresh_breadcrumb()

        def _on_vælg_jurist() -> None:
            """Reset advisor selection → show all 20 again."""
            state["advisor"] = None
            state["category"] = None
            state["service"] = None
            _refresh_sidebar()
            _refresh_pill_strip()
            _refresh_chat()
            _refresh_breadcrumb()

        # ── Sidebar render ─────────────────────────────────────────────────

        def _sidebar_content() -> None:
            (
                ui.label("[ VÆLG JURIST ]")
                .classes("jk-vælg-btn")
                .on("click", _on_vælg_jurist)
            )
            for adv_id, adv in sorted_advisors.items():
                is_selected = adv_id == state["advisor"]
                any_selected = state["advisor"] is not None
                css = "jk-advisor"
                if is_selected:
                    css += " active"
                elif any_selected:
                    css += " dimmed"
                (
                    ui.label(adv.title)
                    .classes(css)
                    .on("click", lambda _a=adv_id: _on_advisor_click(_a))
                )
                if is_selected:
                    for svc in adv.services:
                        is_active_svc = svc.id == state["service"]
                        svc_css = "jk-submenu active" if is_active_svc else "jk-submenu"
                        (
                            ui.label(f"› {svc.title}")
                            .classes(svc_css)
                            .on("click", lambda _s=svc: _on_service_click(_s))
                        )

        def _refresh_sidebar() -> None:
            sidebar_container.clear()
            with sidebar_container:
                _sidebar_content()

        def _refresh_pill_strip():
            pass  # implemented in Task 7

        # ── Chat rendering ─────────────────────────────────────────────────

        def _render_msg(role: str, content: str) -> None:
            if role == "user":
                with ui.row().classes("w-full justify-end"):
                    ui.label(content).classes("jk-user text-sm")
            else:
                with ui.element("div").classes("jk-bot"):
                    ui.markdown(content).classes("text-sm")

        def _refresh_chat() -> None:
            chat_container.clear()
            with chat_container:
                if not state["consent_accepted"]:
                    _render_forside()
                    return
                if state["advisor"] is None:
                    with ui.element("div").classes("jk-bot"):
                        ui.markdown(
                            "**Vælg en jurist** i menuen til venstre for at starte."
                        ).classes("text-sm")
                    return
                history = engine.get_history(state["advisor"], state["service"])
                if not history:
                    adv = advisors[state["advisor"]]
                    svc = next(
                        (s for s in adv.services if s.id == state["service"]), None
                    )
                    placeholder = (
                        f"📋 **{svc.title}**\n\nKlik Send, eller skriv dit spørgsmål."
                        if svc
                        else "Vælg et emne i menuen og stil dit spørgsmål."
                    )
                    with ui.element("div").classes("jk-bot"):
                        ui.markdown(placeholder).classes("text-sm")
                    return
                for msg in history:
                    _render_msg(msg["role"], msg["content"])

        def _render_forside() -> None:
            """Render welcome text + consent box inside chat_container."""
            with ui.element("div").classes("jk-forside"):
                ui.label("Hvad kan JuraKlar?").classes("jk-forside-title")
                ui.label(
                    "JuraKlar rummer 20 AI-jurister med hver deres speciale.\n"
                    "De kan rådgive dig om juridiske spørgsmål,\n"
                    "lave juridiske dokumenter som testamente, ægtepagt,\n"
                    "slutseddel, skøde, lejekontrakt og meget mere.\n"
                    "De kan læse dine dokumenter og foreslå rettelser,\n"
                    "finde mangler, opdatere til nyeste lov mm.\n\n"
                    "Det hele foregår i en Chat med AI-juristen."
                ).classes("jk-forside-text").style("white-space: pre-line;")

                ui.label("Hvad koster det?").classes("jk-forside-section")
                ui.label(
                    "Anonym bruger kr 200. MobilePay eller Kort.\n"
                    "Betaling først ved upload eller download.\n"
                    "Bruger der tester og giver feedback kører Gratis,\n"
                    "men skal angive e-mail og udfylde et lille spørgeskema efterfølgende."
                ).classes("jk-forside-text").style("white-space: pre-line;")

                with ui.element("div").classes("jk-consent-box"):
                    ui.label("Consent").classes("jk-consent-title")
                    ui.label(
                        "JuraKlar er\n"
                        "  · Lavet af AI\n"
                        "  · Valideret af AI\n"
                        "  · Testet af AI\n\n"
                        "Det er på dit eget ansvar at benytte denne rådgivning."
                    ).classes("jk-consent-body").style("white-space: pre-line;")

                    continue_btn = (
                        ui.button("[ FORTSÆT ]", on_click=_on_consent_continue)
                        .classes("jk-continue-btn")
                        .props("flat")
                        .style("display: none;")
                    )

                    def _on_consent_check(e) -> None:
                        if e.value:
                            continue_btn.style("display: inline-block;")
                        else:
                            continue_btn.style("display: none;")

                    ui.checkbox(
                        "Ja, jeg har forstået det er AI og at det er mit eget ansvar",
                        on_change=_on_consent_check,
                    ).props("color=positive")

        def _on_consent_continue() -> None:
            state["consent_accepted"] = True
            input_row_el.classes(remove="jk-input-locked")
            input_box.props("placeholder='Skriv dit spørgsmål…'")
            _refresh_chat()
            _refresh_pill_strip()
            _refresh_breadcrumb()

        def _refresh_breadcrumb():
            adv = advisors.get(state["advisor"]) if state["advisor"] else None
            if adv:
                svc = next((s for s in adv.services if s.id == state["service"]), None)
                breadcrumb_label.set_text(
                    f"{adv.title} · {svc.title}" if svc else adv.title
                )
            else:
                breadcrumb_label.set_text("")

    ui.run(
        host=effective_host,
        port=effective_port,
        title="JuraKlar — Juridisk Rådgivning",
        storage_secret=storage_secret,
        reload=False,
    )
