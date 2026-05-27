# JuraKlar UI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite `src/ui/advisor_app.py` with Emerald Legal color scheme, collapsible sidebar, mobile drawer, consent gate, dark/light toggle, and advisor ordering from `20_rådgivere.txt`.

**Architecture:** Single-file rewrite of `advisor_app.py`. Pure logic (`_sort_advisors`) is extracted to a module-level function for testability. CSS uses CSS custom properties (variables) with a `body.light-mode` override class toggled via `ui.run_javascript`. Mobile responsiveness via CSS media queries + a fixed-position drawer overlay toggled by adding/removing an `.open` CSS class via JavaScript.

**Tech Stack:** NiceGUI ≥1.4, Python 3.11+, CSS custom properties, `ui.run_javascript` for class toggling, existing `AdvisorEngine` / `ChatEngine` unchanged.

**Spec:** `docs/superpowers/specs/2026-05-27-juraklar-ui-redesign.md`

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/ui/advisor_app.py` | Rewrite | All UI: layout, CSS, state, interactions |
| `tests/ui/test_advisor_app.py` | Extend | Tests for `_sort_advisors` pure function |

No other files are touched.

---

## Task 1: Advisor ordering — pure function + test

Extract advisor ordering logic before touching any UI. This is the only pure function in the module and the only thing that needs a unit test.

**Files:**
- Modify: `src/ui/advisor_app.py` (top-of-file additions only)
- Modify: `tests/ui/test_advisor_app.py`

- [ ] **Step 1.1 — Write the failing test**

Replace `tests/ui/test_advisor_app.py` with:

```python
"""Tests for advisor_app: imports, signature, and _sort_advisors."""
from __future__ import annotations
import inspect
from src.ui.advisor_app import _ADVISOR_ORDER, _sort_advisors, start_advisor_ui


def test_start_advisor_ui_is_callable():
    assert callable(start_advisor_ui)


def test_start_advisor_ui_signature():
    sig = inspect.signature(start_advisor_ui)
    params = list(sig.parameters.keys())
    assert "root" in params
    assert "llm_config" in params
    assert "port" in params
    assert "host" in params


def test_advisor_order_has_20_entries():
    assert len(_ADVISOR_ORDER) == 20


def test_sort_advisors_preserves_known_order():
    """Advisors in _ADVISOR_ORDER come out in that order."""
    # Build a mock advisors dict in reverse order
    mock = {slug: object() for slug in reversed(_ADVISOR_ORDER)}
    result = _sort_advisors(mock)
    assert list(result.keys()) == _ADVISOR_ORDER


def test_sort_advisors_unknown_slugs_appended_alphabetically():
    """Advisors not in _ADVISOR_ORDER are appended after known ones."""
    mock = {"zebra": object(), "apple": object(), "testamente": object()}
    result = _sort_advisors(mock)
    keys = list(result.keys())
    assert keys[0] == "testamente"          # known: first in order
    assert keys[1:] == ["apple", "zebra"]   # unknown: alphabetical


def test_sort_advisors_empty_input():
    assert _sort_advisors({}) == {}


def test_sort_advisors_returns_new_dict():
    """Does not mutate the input dict."""
    original = {"testamente": object()}
    result = _sort_advisors(original)
    assert result is not original
```

- [ ] **Step 1.2 — Run test to verify it fails**

```bash
cd /Users/christianliisberg/projects/wiki_llm
uv run pytest tests/ui/test_advisor_app.py -v 2>&1 | tail -20
```

Expected: `ImportError` — `_ADVISOR_ORDER` and `_sort_advisors` not yet defined.

- [ ] **Step 1.3 — Add `_ADVISOR_ORDER` and `_sort_advisors` to `advisor_app.py`**

Insert immediately after the module docstring and imports (before `_PAGE_CSS`):

```python
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
```

- [ ] **Step 1.4 — Run tests to verify they pass**

```bash
uv run pytest tests/ui/test_advisor_app.py -v 2>&1 | tail -20
```

Expected: all 8 tests `PASSED`.

- [ ] **Step 1.5 — Commit**

```bash
git add src/ui/advisor_app.py tests/ui/test_advisor_app.py
git commit -m "feat: add _sort_advisors + _ADVISOR_ORDER for 20_rådgivere.txt order"
```

---

## Task 2: CSS variable system

Replace `_PAGE_CSS` with the full Emerald Legal design system. The existing `start_advisor_ui` function is untouched — it still runs, just looks different.

**Files:**
- Modify: `src/ui/advisor_app.py` (replace `_PAGE_CSS` only)

- [ ] **Step 2.1 — Replace `_PAGE_CSS`**

Find the existing `_PAGE_CSS = """..."""` block and replace it entirely with:

```python
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
```

- [ ] **Step 2.2 — Smoke test: verify the app still imports**

```bash
uv run python -c "from src.ui.advisor_app import start_advisor_ui; print('OK')"
```

Expected: `OK`

- [ ] **Step 2.3 — Run existing tests**

```bash
uv run pytest tests/ui/test_advisor_app.py -v 2>&1 | tail -10
```

Expected: all tests pass.

- [ ] **Step 2.4 — Commit**

```bash
git add src/ui/advisor_app.py
git commit -m "feat: replace _PAGE_CSS with Emerald Legal CSS variable system"
```

---

## Task 3: Base layout skeleton + dark/light toggle

Rewrite `start_advisor_ui` with the new state dict, header, body structure, and dark/light toggle. The consent flow, sidebar interactions, and chat are stubs — the app loads and the toggle works.

**Files:**
- Modify: `src/ui/advisor_app.py` (rewrite `start_advisor_ui` body)

- [ ] **Step 3.1 — Replace the `@ui.page("/")` function body with the new skeleton**

Locate `async def index_page() -> None:` inside `start_advisor_ui` and replace its entire body with:

```python
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
                with ui.element("div").classes("jk-sidebar"):
                    ui.label("(sidebar stub)").classes("text-xs")

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
                    with ui.element("div").classes("jk-uploads"):
                        upload_chips_el = ui.element("div").classes("flex flex-wrap gap-2")

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

        def _refresh_sidebar():
            pass  # implemented in Task 5

        def _refresh_chat():
            pass  # implemented in Task 4

        def _refresh_breadcrumb():
            adv = advisors.get(state["advisor"]) if state["advisor"] else None
            if adv:
                svc = next((s for s in adv.services if s.id == state["service"]), None)
                breadcrumb_label.set_text(
                    f"{adv.title} · {svc.title}" if svc else adv.title
                )
            else:
                breadcrumb_label.set_text("")
```

- [ ] **Step 3.2 — Smoke test: app starts without error**

```bash
# Start in background, then stop
uv run python -c "
import threading, time
from pathlib import Path
from src.models.config import LLMConfig
from src.ui.advisor_app import start_advisor_ui
# Just verify it imports and the function exists
print('start_advisor_ui:', callable(start_advisor_ui))
"
```

Expected: `start_advisor_ui: True`

- [ ] **Step 3.3 — Run tests**

```bash
uv run pytest tests/ui/test_advisor_app.py -v 2>&1 | tail -10
```

Expected: all pass.

- [ ] **Step 3.4 — Commit**

```bash
git add src/ui/advisor_app.py
git commit -m "feat: new state structure, header, body skeleton with dark/light toggle"
```

---

## Task 4: Forside + consent flow

Replace the chat stub with the welcome text and consent box. Wire the checkbox so `[FORTSÆT]` appears on tick, and unlock the input row when clicked.

**Files:**
- Modify: `src/ui/advisor_app.py`

- [ ] **Step 4.1 — Add helper functions and replace `_refresh_chat` stub**

Insert the following functions inside `index_page`, replacing the `_refresh_chat` stub and filling in `_refresh_sidebar` stub temporarily:

```python
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
                        # Show/hide [FORTSÆT] based on checkbox state
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
            # Unlock input row
            input_row_el.classes(remove="jk-input-locked")
            input_box.props("placeholder='Skriv dit spørgsmål…'")
            _refresh_chat()
            _refresh_breadcrumb()
```

- [ ] **Step 4.2 — Call `_refresh_chat()` at the bottom of `index_page`**

After the drawer definition, ensure the page initialises with the forside:

```python
        # Initialise page
        _refresh_chat()
```

- [ ] **Step 4.3 — Verify imports still work**

```bash
uv run python -c "from src.ui.advisor_app import start_advisor_ui; print('OK')"
```

Expected: `OK`

- [ ] **Step 4.4 — Run tests**

```bash
uv run pytest tests/ui/test_advisor_app.py -v 2>&1 | tail -10
```

Expected: all pass.

- [ ] **Step 4.5 — Commit**

```bash
git add src/ui/advisor_app.py
git commit -m "feat: forside welcome text + consent checkbox + FORTSÆT unlock flow"
```

---

## Task 5: Desktop sidebar

Replace the sidebar stub with the real sorted advisor list. Clicking an advisor folds others, shows sub-menus. VÆLG JURIST resets selection.

**Files:**
- Modify: `src/ui/advisor_app.py`

- [ ] **Step 5.1 — Add advisor click handlers and replace `_refresh_sidebar` stub**

Insert the following inside `index_page`, replacing `def _refresh_sidebar(): pass`:

```python
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
            _close_drawer()   # closes mobile drawer if open

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
```

- [ ] **Step 5.2 — Replace the sidebar stub element in the layout**

Find:
```python
                with ui.element("div").classes("jk-sidebar"):
                    ui.label("(sidebar stub)").classes("text-xs")
```

Replace with:
```python
                with ui.element("div").classes("jk-sidebar") as sidebar_container:
                    _sidebar_content()
```

- [ ] **Step 5.3 — Smoke test**

```bash
uv run python -c "from src.ui.advisor_app import start_advisor_ui; print('OK')"
```

Expected: `OK`

- [ ] **Step 5.4 — Run tests**

```bash
uv run pytest tests/ui/test_advisor_app.py -v 2>&1 | tail -10
```

Expected: all pass.

- [ ] **Step 5.5 — Commit**

```bash
git add src/ui/advisor_app.py
git commit -m "feat: desktop sidebar with sorted advisor list, fold/dim, submenus"
```

---

## Task 6: Mobile drawer

Replace the drawer stub with the same sorted advisor list. The `_open_drawer` / `_close_drawer` helpers already exist; this task fills the drawer with real content and mirrors the sidebar interaction.

**Files:**
- Modify: `src/ui/advisor_app.py`

- [ ] **Step 6.1 — Replace the drawer stub with refreshable content**

Find the drawer stub:
```python
            with drawer_overlay_el:
                with ui.element("div").classes("jk-drawer"):
                    ui.label("✕ luk").classes("jk-drawer-close").on(
                        "click", lambda: _close_drawer()
                    )
                    ui.label("(drawer stub)").classes("text-xs")
                # Tap on backdrop closes drawer
                drawer_overlay_el.on(
```

Replace with:
```python
            with drawer_overlay_el:
                with ui.element("div").classes("jk-drawer") as drawer_inner:

                    ui.label("✕ luk").classes("jk-drawer-close").on(
                        "click", lambda: _close_drawer()
                    )

                    @ui.refreshable
                    def _drawer_content() -> None:
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
                                    is_active = svc.id == state["service"]
                                    svc_css = "jk-submenu active" if is_active else "jk-submenu"
                                    (
                                        ui.label(f"› {svc.title}")
                                        .classes(svc_css)
                                        .on("click", lambda _s=svc: _on_service_click(_s))
                                    )

                    _drawer_content()

                # Tap on backdrop closes drawer
                drawer_overlay_el.on(
```

- [ ] **Step 6.2 — Update `_refresh_sidebar` to also refresh the drawer**

Find the line `sidebar_container.clear()` inside `_refresh_sidebar` and add a drawer refresh:

```python
        def _refresh_sidebar() -> None:
            sidebar_container.clear()
            with sidebar_container:
                _sidebar_content()
            _drawer_content.refresh()
```

- [ ] **Step 6.3 — Smoke test**

```bash
uv run python -c "from src.ui.advisor_app import start_advisor_ui; print('OK')"
```

Expected: `OK`

- [ ] **Step 6.4 — Run tests**

```bash
uv run pytest tests/ui/test_advisor_app.py -v 2>&1 | tail -10
```

Expected: all pass.

- [ ] **Step 6.5 — Commit**

```bash
git add src/ui/advisor_app.py
git commit -m "feat: mobile drawer with advisor list mirroring desktop sidebar"
```

---

## Task 7: Mobile pill-strip

After an advisor is selected on mobile, show a compact strip under the header with the advisor name and service pills. On desktop it stays hidden via CSS.

**Files:**
- Modify: `src/ui/advisor_app.py`

- [ ] **Step 7.1 — Add `_refresh_pill_strip` function**

Insert inside `index_page` after the `_refresh_sidebar` function:

```python
        def _refresh_pill_strip() -> None:
            pill_strip_el.clear()
            if not state["consent_accepted"] or state["advisor"] is None:
                pill_strip_el.style("display: none;")
                return
            # On desktop the CSS hides this; on mobile we show it
            pill_strip_el.style("display: block;")
            adv = advisors[state["advisor"]]
            with pill_strip_el:
                (
                    ui.label(f"⚖️ {adv.title} ▾")
                    .classes("jk-pill-advisor")
                    .on("click", lambda: _open_drawer())
                )
                with ui.element("div").classes("jk-pills"):
                    for svc in adv.services:
                        is_active = svc.id == state["service"]
                        pill_css = "jk-pill active" if is_active else "jk-pill inactive"
                        (
                            ui.label(svc.title)
                            .classes(pill_css)
                            .on("click", lambda _s=svc: _on_service_click(_s))
                        )
```

- [ ] **Step 7.2 — Wire `_refresh_pill_strip` into `_on_consent_continue` and `_reset_to_forside`**

In `_on_consent_continue`, add after `_refresh_chat()`:
```python
            _refresh_pill_strip()
```

In `_reset_to_forside`, add after `_refresh_sidebar()`:
```python
            _refresh_pill_strip()
```

- [ ] **Step 7.3 — Smoke test**

```bash
uv run python -c "from src.ui.advisor_app import start_advisor_ui; print('OK')"
```

Expected: `OK`

- [ ] **Step 7.4 — Run tests**

```bash
uv run pytest tests/ui/test_advisor_app.py -v 2>&1 | tail -10
```

Expected: all pass.

- [ ] **Step 7.5 — Commit**

```bash
git add src/ui/advisor_app.py
git commit -m "feat: mobile pill-strip after advisor selected"
```

---

## Task 8: Chat area, input row, and send/upload/download

Wire up the full send flow, upload handling, download, and clear — reusing existing logic from the old file but with new CSS classes and corrected input row order.

**Files:**
- Modify: `src/ui/advisor_app.py`

- [ ] **Step 8.1 — Add send, clear, upload, and download handlers**

Insert inside `index_page`, before the layout block:

```python
        # ── Chat handlers ──────────────────────────────────────────────────

        async def _send() -> None:
            raw = input_box.value.strip()
            if not raw or not state["consent_accepted"]:
                return
            input_box.value = ""

            if state["uploaded_docs"]:
                doc_block = "\n\n".join(
                    f"### Uploadet: {d['name']}\n{d['text'][:4000]}"
                    for d in state["uploaded_docs"]
                )
                full_question = (
                    f"Brugeren har uploadet følgende dokument(er):\n\n"
                    f"{doc_block}\n\n---\n\n{raw}"
                )
            else:
                full_question = raw

            cur_a = state["advisor"]
            cur_s = state["service"]
            with chat_container:
                _render_msg("user", raw)
                thinking = ui.label("…").classes("text-grey-5 text-sm q-ml-sm")
            try:
                answer = await engine.ask(cur_a, cur_s, full_question)
            except Exception as exc:  # noqa: BLE001
                answer = f"**Fejl:** {exc}"
            thinking.delete()
            if state["advisor"] == cur_a and state["service"] == cur_s:
                with chat_container:
                    _render_msg("assistant", answer)

        def _clear_chat() -> None:
            engine.clear(state["advisor"], state["service"])
            _refresh_chat()

        async def _handle_upload(e) -> None:
            try:
                from markitdown import MarkItDown  # noqa: PLC0415
                raw_bytes = await e.file.read()
                ext = Path(e.file.name).suffix.lower() or ".txt"
                result = MarkItDown().convert_stream(io.BytesIO(raw_bytes), file_extension=ext)
                text = result.text_content or ""
                state["uploaded_docs"].append({"name": e.file.name, "text": text})
            except Exception as exc:  # noqa: BLE001
                state["uploaded_docs"].append({
                    "name": e.file.name,
                    "text": f"(Kunne ikke parse: {exc})",
                })
            _refresh_upload_chips()

        def _remove_doc(idx: int) -> None:
            if 0 <= idx < len(state["uploaded_docs"]):
                state["uploaded_docs"].pop(idx)
            _refresh_upload_chips()

        def _refresh_upload_chips() -> None:
            upload_chips_el.clear()
            if not state["uploaded_docs"]:
                return
            with upload_chips_el:
                ui.label("📎 Dokumenter:").classes("text-xs text-grey-5")
                for i, doc in enumerate(state["uploaded_docs"]):
                    ui.chip(
                        doc["name"],
                        on_click=lambda idx=i: _remove_doc(idx),
                    ).props("dense outline color=grey-5 removable").classes("text-xs")

        def _download_chat(fmt: str = "md") -> None:
            import re as _re  # noqa: PLC0415
            history = engine.get_history(state["advisor"], state["service"])
            if not history:
                return
            adv = advisors[state["advisor"]]
            svc = next((s for s in adv.services if s.id == state["service"]), None)
            title = adv.title
            svc_title = svc.title if svc else ""
            if fmt == "md":
                lines = [f"# JuraKlar — {title}", f"## {svc_title}", "", "---", ""]
                for msg in history:
                    if msg["role"] == "user":
                        lines += [f"**Dig:** {msg['content']}", ""]
                    else:
                        lines += [f"**JuraKlar:**\n\n{msg['content']}", ""]
                content = "\n".join(lines)
                filename, media_type = "juraklar-rådgivning.md", "text/markdown"
            else:
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
                filename, media_type = "juraklar-rådgivning.txt", "text/plain"
            ui.download(content.encode("utf-8"), filename=filename, media_type=media_type)
```

- [ ] **Step 8.2 — Replace the input row stub with the wired version**

Find:
```python
                    with ui.element("div").classes("jk-input jk-input-locked") as input_row_el:
                        uploader = (
                            ui.upload(on_upload=lambda e: None, auto_upload=True, multiple=True)
```

Replace with:
```python
                    with ui.element("div").classes("jk-input jk-input-locked") as input_row_el:
                        uploader = (
                            ui.upload(on_upload=_handle_upload, auto_upload=True, multiple=True)
```

Then replace the stub Send and Ryd buttons and download menu items:

```python
                        ui.button("Send", on_click=_send).props("color=primary dense")
                        ui.button("Ryd", on_click=_clear_chat).props("flat color=grey-6 dense size=sm")
                        with ui.button(icon="download").props("flat dense color=grey-5").tooltip("Download samtale"):
                            with ui.menu():
                                ui.menu_item("Markdown (.md)", on_click=lambda: _download_chat("md"))
                                ui.menu_item("Ren tekst (.txt)", on_click=lambda: _download_chat("txt"))
```

Also wire `Enter` key:
```python
                        input_box.on("keydown.enter", _send)
```

- [ ] **Step 8.3 — Update upload chips container reference**

The `upload_chips_el` is currently a bare `ui.element("div")`. In the uploads section replace:
```python
                    with ui.element("div").classes("jk-uploads"):
                        upload_chips_el = ui.element("div").classes("flex flex-wrap gap-2")
```
with:
```python
                    with ui.element("div").classes("jk-uploads") as upload_chips_el:
                        pass
```

- [ ] **Step 8.4 — Run tests**

```bash
uv run pytest tests/ui/test_advisor_app.py -v 2>&1 | tail -10
```

Expected: all pass.

- [ ] **Step 8.5 — Commit**

```bash
git add src/ui/advisor_app.py
git commit -m "feat: wire send, clear, upload, download handlers with new CSS classes"
```

---

## Task 9: Verification + cleanup

Run the full app manually, verify every flow, remove any remaining stubs, run the full test suite.

**Files:**
- Modify: `src/ui/advisor_app.py` (cleanup only)

- [ ] **Step 9.1 — Run the full test suite**

```bash
uv run pytest --ignore=tests/ui/test_advisor_app.py -x -q 2>&1 | tail -20
uv run pytest tests/ui/ -v 2>&1 | tail -20
```

Expected: all pass, no errors.

- [ ] **Step 9.2 — Start the app and verify manually**

```bash
uv run wiki-llm.py advisor --config config/my_wiki.py
```

Open `http://localhost:8080` and verify the following checklist:

**Forside (desktop + mobil):**
- [ ] Velkomst-tekst og consent-boks vises ved første load
- [ ] Checkbox afkrydset → `[FORTSÆT]` dukker op
- [ ] Uden afkrydsning er `[FORTSÆT]` skjult
- [ ] `[FORTSÆT]` → input-rækken aktiveres, forside erstattes af "Vælg en jurist"

**Sidebar (desktop ≥768px):**
- [ ] 20 jurister vises i korrekt rækkefølge (Testamente, Ægtepagt, Fremtidsfuldmagt …)
- [ ] Klik på jurist → markeres grønt, øvrige dimmes, undermenuer folder ud
- [ ] Klik på undermenu → input-felt forudfyldes, undermenu highlightes
- [ ] `[VÆLG JURIST]` → alle 20 vises igen, ingen markeret
- [ ] Sidebar er **ikke** synlig på mobil (< 768px)

**Mobil (< 768px):**
- [ ] Hamburger ☰ synlig i header
- [ ] ☰ → drawer glider ind med alle 20 jurister
- [ ] Klik uden for drawer → lukker
- [ ] ✕ luk → drawer lukker
- [ ] Efter jurist valgt: drawer lukker, pill-strip vises under header
- [ ] Pill-strip: advisor-navn klikbar (åbner drawer), undermenuer som vandret scroll-liste

**Mørk/lys toggle:**
- [ ] 🌙/☀️ knap skifter hele appens farvepalette inkl. sidebar, chat og bobler
- [ ] Toggle-knap skifter tekst til ☀️ / 🌙

**Chat:**
- [ ] Bruger-bobler er højrejusterede, grønne
- [ ] Bot-svar er venstrejusterede, mørkere baggrund, markdown renderes korrekt
- [ ] Ryd → samtalen nulstilles

**Upload/Download:**
- [ ] 📎 åbner fil-picker
- [ ] Uploadet fil vises som chip i upload-rækken
- [ ] Klik på chip → fjerner filen
- [ ] 💾 → dropdown: Markdown / Ren tekst → download starter

**Logo-klik:**
- [ ] Klik `⚖️ JuraKlar` i header → consent-flow vises igen (consent_accepted = False)
- [ ] Input-rækken låses igen

- [ ] **Step 9.3 — Remove any remaining stubs from the code**

Search for any `"(stub)"` strings or pass-only functions and fix them:

```bash
grep -n "stub\|pass  # implemented" src/ui/advisor_app.py
```

Expected: no matches.

- [ ] **Step 9.4 — Final commit**

```bash
git add src/ui/advisor_app.py
git commit -m "feat: complete JuraKlar UI redesign — Emerald Legal, mobile-first, consent gate

- Emerald Legal colour scheme (dark/light via CSS variables)
- Collapsible sidebar (desktop: always visible; mobile: drawer overlay)
- Consent gate on every session — input locked until accepted
- 20 advisors in 20_rådgivere.txt order with fold/dim interaction
- Mobile pill-strip showing selected advisor + service pills
- Dark/light toggle (🌙/☀️) in header
- Logo click resets to forside
- Upload, download, send, clear all wired"
```
