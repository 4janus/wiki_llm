"""NiceGUI responsive chat interface for the Danish legal advisory system (JurAklar).

Provides a multi-advisor, multi-service web UI.  Each advisor has its own set
of services (grouped by category).  The UI is responsive:

- Desktop (>599 px): advisor tabs across the top + service chips below them.
- Mobile (≤599 px): advisor select dropdown + service select dropdown.

Conversation history is kept per (advisor, service) pair and is stored inside
the shared AdvisorEngine instance (single-user local use).
"""
from __future__ import annotations

import os
from pathlib import Path

from ..models.config import LLMConfig


def start_advisor_ui(
    root: Path,
    llm_config: LLMConfig,
    *,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> None:
    """Start the NiceGUI HTTP server with the JurAklar advisor chat interface.

    Discovers advisors from *root*, builds the chat UI, and calls ``ui.run``.
    This function blocks until the server is stopped.  Host and port can be
    overridden via the WIKI_UI_HOST and WIKI_UI_PORT environment variables.

    Args:
        root: Root directory containing advisor sub-directories.
        llm_config: LLM backend configuration used to create the LLM client.
        host: Network interface to bind to.
        port: TCP port for the NiceGUI HTTP server.

    Raises:
        RuntimeError: If nicegui is not installed.
        RuntimeError: If no advisors are found inside *root*.
    """
    try:
        from nicegui import ui  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("nicegui not installed. Run: pip install nicegui") from exc

    from ..llm.factory import create_client  # noqa: PLC0415
    from .advisor_engine import AdvisorEngine  # noqa: PLC0415

    llm = create_client(llm_config)
    engine = AdvisorEngine(root, llm)
    # NOTE: engine is shared across all browser connections (by design — single-user local tool).
    # Opening multiple tabs will share conversation history.
    advisors = engine.discover()

    if not advisors:
        raise RuntimeError(f"No advisors found in {root}. Check that sub-directories contain a prompts/ directory.")

    effective_host = os.environ.get("WIKI_UI_HOST", host)
    effective_port = int(os.environ.get("WIKI_UI_PORT", port))
    storage_secret = os.environ.get("WIKI_UI_STORAGE_SECRET", "juraklar-secret")

    @ui.page("/")
    async def index_page() -> None:  # noqa: C901  (complexity acceptable for a page handler)
        ui.dark_mode()

        # ------------------------------------------------------------------ #
        # Per-connection state (fresh closure per page load)
        # ------------------------------------------------------------------ #
        first_advisor_id = next(iter(advisors))
        first_advisor = advisors[first_advisor_id]
        first_service_id = first_advisor.services[0].id if first_advisor.services else 0

        state: dict = {
            "advisor": first_advisor_id,
            "service": first_service_id,
        }

        # ------------------------------------------------------------------ #
        # Helpers
        # ------------------------------------------------------------------ #

        def current_advisor():
            return advisors[state["advisor"]]

        def services_by_category() -> dict[str, list]:
            result: dict[str, list] = {}
            for svc in current_advisor().services:
                result.setdefault(svc.category or "Generelt", []).append(svc)
            return result

        def refresh_chat() -> None:
            chat_container.clear()
            history = engine.get_history(state["advisor"], state["service"])
            with chat_container:
                if not history:
                    svc = next(
                        (s for s in current_advisor().services if s.id == state["service"]),
                        None,
                    )
                    if svc:
                        ui.label(f"📋 {svc.title}").classes("text-caption text-grey-5 q-mb-sm")
                        ui.label("Start samtalen ved at skrive dit spørgsmål nedenfor.").classes(
                            "text-grey-6 text-body2"
                        )
                for msg in history:
                    if msg["role"] == "user":
                        with ui.row().classes("w-full justify-end"):
                            with ui.card().classes("bg-primary text-white q-pa-sm").style("max-width: 70%"):
                                ui.label(msg["content"]).classes("text-body2")
                    elif msg["role"] == "assistant":
                        with ui.card().classes("w-full bg-grey-9 q-pa-sm"):
                            ui.markdown(msg["content"]).classes("text-body2")

        # ------------------------------------------------------------------ #
        # Change handlers
        # ------------------------------------------------------------------ #

        def on_advisor_change(advisor_id: str) -> None:
            state["advisor"] = advisor_id
            adv = advisors.get(advisor_id)
            if adv and adv.services:
                state["service"] = adv.services[0].id
            desktop_chips.refresh()
            mobile_service_select.refresh()
            refresh_chat()

        def on_service_change(service_id: int) -> None:
            state["service"] = service_id
            desktop_chips.refresh()
            mobile_service_select.refresh()
            refresh_chat()

        # ------------------------------------------------------------------ #
        # App header
        # ------------------------------------------------------------------ #
        with ui.header().classes("bg-grey-10 text-white q-pa-sm"):
            ui.label("⚖️ JurAklar").classes("text-h6 text-bold")
            ui.label("Juridisk rådgivning").classes("text-caption text-grey-5 q-ml-sm")

        # ------------------------------------------------------------------ #
        # Main layout wrapper
        # ------------------------------------------------------------------ #
        with ui.column().classes("w-full max-w-4xl mx-auto q-pa-md").style("height: calc(100vh - 120px); display: flex; flex-direction: column"):

            # -------------------------------------------------------------- #
            # DESKTOP layout (visible on >599px)
            # -------------------------------------------------------------- #
            with ui.element("div").classes("gt-xs w-full"):

                # Advisor tabs
                with ui.tabs(value=state["advisor"]).classes("w-full bg-grey-10") as tabs:
                    for adv_id, adv in advisors.items():
                        ui.tab(adv_id, label=adv.title)
                tabs.on("update:model-value", lambda e: on_advisor_change(
                    e.args["value"] if isinstance(e.args, dict)
                    else (e.args[0] if isinstance(e.args, list) else e.args)
                ))

                # Service chips — refreshable so they update when advisor/service changes
                @ui.refreshable
                def desktop_chips() -> None:
                    with ui.column().classes("w-full q-pa-xs"):
                        for cat, svcs in services_by_category().items():
                            ui.label(cat).classes("text-caption text-grey-5 q-mt-xs")
                            with ui.row().classes("w-full flex-wrap gap-1"):
                                for svc in svcs:
                                    active = svc.id == state["service"]
                                    ui.chip(
                                        svc.title,
                                        on_click=lambda s=svc: on_service_change(s.id),
                                    ).props("color=primary dense" if active else "outline color=grey-6 dense")

                desktop_chips()

            # -------------------------------------------------------------- #
            # MOBILE layout (visible on ≤599px)
            # -------------------------------------------------------------- #
            with ui.element("div").classes("lt-sm w-full"):

                # Advisor dropdown
                ui.select(
                    {k: v.title for k, v in advisors.items()},
                    value=state["advisor"],
                    on_change=lambda e: on_advisor_change(e.value),
                ).classes("w-full").props("dense outlined dark label='Rådgiver'")

                # Service dropdown — refreshable so it updates when advisor changes
                @ui.refreshable
                def mobile_service_select() -> None:
                    svc_options = {svc.id: svc.title for svc in current_advisor().services}
                    ui.select(
                        svc_options,
                        value=state["service"],
                        on_change=lambda e: on_service_change(e.value),
                    ).classes("w-full q-mt-xs").props("dense outlined dark label='Ydelse'")

                mobile_service_select()

            ui.separator().classes("q-my-xs")

            # -------------------------------------------------------------- #
            # Chat area
            # -------------------------------------------------------------- #
            with ui.scroll_area().classes("w-full flex-1"):
                chat_container = ui.column().classes("w-full gap-2 q-pa-sm")
            refresh_chat()  # populate immediately

            # -------------------------------------------------------------- #
            # Input row
            # -------------------------------------------------------------- #
            with ui.row().classes("w-full q-mt-sm items-center gap-2"):
                input_box = (
                    ui.input(placeholder="Skriv dit spørgsmål…")
                    .classes("flex-1")
                    .props("dense outlined dark")
                )

                async def send() -> None:
                    question = input_box.value.strip()
                    if not question:
                        return
                    input_box.value = ""
                    # Capture current context before await
                    cur_advisor = state["advisor"]
                    cur_service = state["service"]
                    with chat_container:
                        with ui.row().classes("w-full justify-end"):
                            with ui.card().classes("bg-primary text-white q-pa-sm").style("max-width: 70%"):
                                ui.label(question).classes("text-body2")
                        thinking = ui.label("…").classes("text-grey-5 text-body2 q-ml-sm")
                    try:
                        answer = await engine.ask(cur_advisor, cur_service, question)
                    except Exception as exc:  # noqa: BLE001
                        answer = f"**Fejl:** {exc}"
                    thinking.delete()
                    # Only append if user is still on the same advisor/service
                    if state["advisor"] == cur_advisor and state["service"] == cur_service:
                        with chat_container:
                            with ui.card().classes("w-full bg-grey-9 q-pa-sm"):
                                ui.markdown(answer).classes("text-body2")

                input_box.on("keydown.enter", send)
                ui.button("Send", on_click=send).props("color=primary dense")
                ui.button(
                    "Ryd",
                    on_click=lambda: (
                        engine.clear(state["advisor"], state["service"]),
                        refresh_chat(),
                    ),
                ).props("flat color=grey-6 dense size=sm")

    ui.run(
        host=effective_host,
        port=effective_port,
        title="JurAklar — Juridisk Rådgivning",
        storage_secret=storage_secret,
        reload=False,
    )
