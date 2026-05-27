# JuraKlar FastAPI UI — Spec

**Dato:** 2026-05-27
**Erstatter:** `2026-05-27-juraklar-ui-redesign.md` (NiceGUI-version, afbrudt pga. framework-problemer)
**Status:** Godkendt af bruger

---

## Oversigt

Erstat NiceGUI-implementationen i `src/ui/advisor_app.py` med en **FastAPI-server** der serverer én statisk HTML-side. Alt UI-logik lever i `src/ui/static/index.html` som ren HTML + inline CSS + vanilla JS.

`advisor_engine.py`, `chat_engine.py` og `cli.py` røres **ikke**. `start_advisor_ui(root, llm_config, host, port)` bevarer præcis samme signatur.

---

## Filer

| Fil | Handling |
|---|---|
| `src/ui/advisor_app.py` | Komplet rewrite: NiceGUI → FastAPI + uvicorn |
| `src/ui/static/index.html` | Ny fil: single-page klient |

---

## Server — `advisor_app.py`

FastAPI-app startet med `uvicorn.run()` (erstatter `ui.run()`).

### Endpoints

| Method | Path | Beskrivelse |
|---|---|---|
| `GET` | `/` | Serverer `src/ui/static/index.html` |
| `GET` | `/api/advisors` | JSON-liste over alle advisors med services |
| `POST` | `/api/chat` | SSE-stream: modtager spørgsmål, streamer svar |
| `DELETE` | `/api/history/{advisor_id}/{service_id}` | Rydder chat-historik for advisor+service |
| `POST` | `/api/upload` | MarkItDown-parse af fil, returnerer `{name, text}` |
| `GET` | `/api/download/{advisor_id}/{service_id}` | Returnerer chat-historik som `.md`-fil |

### `/api/advisors` — respons

```json
[
  {
    "id": "testamente",
    "title": "Testamente",
    "services": [
      {"id": 1, "title": "Opret testamente", "category": "Oprettelse"},
      {"id": 2, "title": "Ændre testamente", "category": "Ændring"}
    ]
  }
]
```

Rækkefølge følger `_ADVISOR_ORDER` (samme liste som i den gamle `advisor_app.py`).

### `/api/chat` — SSE-streaming

**Request:**
```json
{
  "advisor_id": "testamente",
  "service_id": 1,
  "question": "Hvad koster det?",
  "docs": [{"name": "kontrakt.pdf", "text": "..."}],
  "session_id": "uuid-v4"
}
```

**Response:** `Content-Type: text/event-stream`
```
data: {"t": "Et"}\n\n
data: {"t": " testamente"}\n\n
...
data: [DONE]\n\n
```

Implementering: tjek om `ChatEngine` / LLM-klienten understøtter token-streaming. Hvis ja, yield tokens direkte. Hvis nej, kald den eksisterende `engine.ask()` og chunk svaret i ord med 20ms delay (visuelt identisk for brugeren).

Hvis `docs` er ikke-tom, præfikses `question` med dokumentindholdet (samme logik som nuværende `advisor_app.py`).

### `/api/upload` — fil-upload

Modtager `multipart/form-data` med fil + `session_id`. Bruger `MarkItDown` til at parse PDF/DOCX/TXT/MD. Returnerer `{"name": "...", "text": "..."}`. Fejl returneres som `{"name": "...", "text": "(Kunne ikke parse: ...)"}`.

Uploadede dokumenter gemmes **ikke** server-side — klienten holder dem i `state.uploadedDocs` og sender dem med i hvert `/api/chat`-kald.

### `/api/download`

Bygger Markdown-streng fra `engine.get_history(advisor_id, service_id)`. Returnerer som `Content-Disposition: attachment; filename="juraklar-rådgivning.md"`.

### Sessions

Klienten genererer en UUID v4 ved første besøg og gemmer den i `localStorage` som `jk_session_id`. Den sendes som felt i chat- og upload-requests. Serveren bruger den som nøgle i en in-memory dict til at holde session-specifik state (pt. kun til fremtidig brug — uploadede docs holdes klient-side).

---

## Klient — `src/ui/static/index.html`

Én fil med inline `<style>` og inline `<script>`. Ingen npm, ingen bundler, ingen eksterne afhængigheder.

### State-objekt

```js
const state = {
  consentAccepted: false,   // bool
  advisor: null,            // str | null — valgt advisor_id
  service: null,            // int | null — valgt service_id
  uploadedDocs: [],         // [{name, text}]
  sessionId: getSessionId() // UUID fra localStorage
};
```

### Tilstandsmaskine

```
START
  └─ Siden loader → fetch /api/advisors → byg sidebar
  └─ Vis: CONSENT

CONSENT (consentAccepted = false)
  └─ Sidebar synlig men pointer-events: none
  └─ Input-række: opacity 0.35, pointer-events: none
  └─ Checkbox ☑ → vis [FORTSÆT]-knap
  └─ [FORTSÆT] → consentAccepted = true → vis JURIST-VALG

JURIST-VALG (consentAccepted = true, advisor = null)
  └─ Chat viser: "Vælg en jurist i menuen til venstre"
  └─ Sidebar fuldt klikbar
  └─ Klik advisor → CHAT

CHAT (advisor ≠ null)
  └─ Sidebar: valgt advisor foldet ud med services
  └─ Øvrige advisors dimmet (synlige, klikbare)
  └─ Klik service → skift service, hent historik, vis pills
  └─ Klik pill → fyld input-felt med pill-tekst
  └─ Send / Enter → POST /api/chat → stream → vis bobler
  └─ Klik ⚖️ logo → reset til CONSENT (al state nulstilles)
  └─ Toggle 🌙/☀️ → skift dark/light (ingen state-reset)
```

### Layout (desktop ≥ 768px)

```
┌──────────────────────────────────────────────────┐
│  HEADER: ⚖️ JuraKlar  [breadcrumb]          🌙/☀️ │
├────────────┬─────────────────────────────────────┤
│  SIDEBAR   │  CHAT AREA                           │
│  160px     │                                      │
│            │  (consent / jurist-valg / bobler)    │
│  [VÆLG     │                                      │
│   JURIST]  ├─────────────────────────────────────┤
│            │  PILLS (spørgsmål-knapper)           │
│  Jurist 1  ├─────────────────────────────────────┤
│  › Service │  INPUT: 📎  [felt_________]  Send  💾│
│  › Service │                                      │
│  Jurist 2  │                                      │
│  (dimmet)  │                                      │
└────────────┴─────────────────────────────────────┘
```

### Layout (mobil < 768px)

Sidebar skjult. Hamburger-ikon (☰) i header åbner slide-in drawer (overlay, `min(80vw, 300px)`). Pill-strip vises vandret under header når advisor er valgt.

### Streaming — fetch + ReadableStream

```js
const resp = await fetch('/api/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({advisor_id, service_id, question, docs, session_id})
});
const reader = resp.body.getReader();
const decoder = new TextDecoder();
let buf = '';
while (true) {
  const {done, value} = await reader.read();
  if (done) break;
  buf += decoder.decode(value, {stream: true});
  const lines = buf.split('\n');
  buf = lines.pop();
  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const payload = line.slice(6);
      if (payload === '[DONE]') { finaliseBoble(); break; }
      const {t} = JSON.parse(payload);
      appendToken(t);  // tilføj token til aktiv bot-boble
    }
  }
}
```

### Upload

`<input type="file" accept=".pdf,.docx,.txt,.md" multiple>` trigges fra 📎-knap. `FormData` POSTes til `/api/upload`. Svar tilføjes til `state.uploadedDocs`. Chips renderes under chat med × til at fjerne dem.

### Download

Klik på 💾 åbner en lille menu (Markdown / Ren tekst). Kald `GET /api/download/{advisor}/{service}?fmt=md` — browseren modtager filen direkte via `Content-Disposition: attachment`.

---

## Farveskema: Emerald Legal (uændret)

### Mørk tilstand (standard)

| Token | Hex |
|---|---|
| `--bg-deep` | `#080f0c` |
| `--bg-base` | `#0c1510` |
| `--bg-surface` | `#0d1f16` |
| `--bg-sidebar` | `#0a1a12` |
| `--bg-bubble-user` | `#0d4a30` |
| `--bg-bubble-bot` | `#0d1f16` |
| `--border` | `#1a3028` |
| `--accent` | `#4ade99` |
| `--accent-btn` | `#0d4a30` |
| `--text-primary` | `#e0e0e0` |
| `--text-secondary` | `#8ab898` |
| `--text-dim` | `#3a6a50` |
| `--text-muted` | `#2a4a32` |

### Lys tilstand

| Token | Hex |
|---|---|
| `--bg-deep` | `#ffffff` |
| `--bg-base` | `#f8fdf9` |
| `--bg-surface` | `#f0faf5` |
| `--bg-sidebar` | `#e0f5ea` |
| `--bg-bubble-user` | `#0a6e40` |
| `--bg-bubble-bot` | `#f0faf5` |
| `--border` | `#c8e8d8` |
| `--accent` | `#0a6e40` |
| `--text-primary` | `#1a3a28` |
| `--text-secondary` | `#3a6a50` |
| `--text-dim` | `#7aaa88` |

Toggle: klik 🌙/☀️ → `document.body.classList.toggle('light-mode')`.

---

## Advisor-rækkefølge

```python
_ADVISOR_ORDER = [
    "testamente", "aegtepagt", "fremtidsfuldmagt", "boligkob", "doedsbo",
    "skilsmisse", "bodeling", "foraeldre", "samliv", "gavebrev",
    "lejeret", "ansaettelsesret", "erstatning", "patientskade", "gaeldssanering",
    "socialret", "forsikring", "naboret", "forbrugerret", "vaergemaal",
]
```

Advisors ikke i listen tilføjes bagerst alfabetisk.

---

## Afgrænsning (ikke i scope)

- Betaling — kun tekst på forsiden
- Feedback-flow — kun tekst på forsiden
- Multi-user session-isolering (historie per session) — bevares som eksisterende begrænsning; `ChatEngine` holder historik globalt per `(advisor_id, service_id)`
- PWA / app-installation
- Markdown-rendering af bot-svar — simpel tekst er tilstrækkeligt; `<pre>`-wrap til kodeblokke
