# JuraKlar UI Redesign — Spec

**Dato:** 2026-05-27  
**Fil:** `src/ui/advisor_app.py`  
**Status:** Godkendt af bruger

---

## Oversigt

Komplet redesign af JuraKlar advisor-appen (`start_advisor_ui`). Nuværende layout erstattes med:

- **Sammenklappelig venstre sidebar** (desktop: altid synlig · mobil: hamburger-drawer)
- **Forside med velkomst + consent** — vises ved hvert besøg, låser input indtil godkendt
- **Emerald Legal farveskema** — dyb grøn i mørk tilstand, mintgrøn i lys tilstand
- **Dark/light-toggle** i header
- **Mobil-first** responsive layout

Eksisterende upload (📎) og download (💾) funktionalitet bevares uændret.

---

## Farveskema: Emerald Legal

### Mørk tilstand (standard)

| Token | Hex | Brug |
|---|---|---|
| `--bg-deep` | `#080f0c` | Chat-baggrund |
| `--bg-base` | `#0c1510` | Applikationsrod |
| `--bg-surface` | `#0d1f16` | Header, input-række, consent-boks |
| `--bg-sidebar` | `#0a1a12` | Sidebar |
| `--bg-bubble-user` | `#0d4a30` | Bruger-boble |
| `--bg-bubble-bot` | `#0d1f16` | Bot-boble |
| `--border` | `#1a3028` | Alle kanter |
| `--accent` | `#4ade99` | Primær accent (knapper, active-state, links) |
| `--accent-btn` | `#0d4a30` | Knap-baggrund |
| `--text-primary` | `#e0e0e0` | Primær tekst |
| `--text-secondary` | `#8ab898` | Brødtekst, placeholder |
| `--text-dim` | `#3a6a50` | Dimmet tekst (inaktive jurister) |
| `--text-muted` | `#2a4a32` | Meget dimmet |

### Lys tilstand

| Token | Hex | Brug |
|---|---|---|
| `--bg-deep` | `#ffffff` | Chat-baggrund |
| `--bg-base` | `#f8fdf9` | Applikationsrod |
| `--bg-surface` | `#f0faf5` | Header, input-række |
| `--bg-sidebar` | `#e0f5ea` | Sidebar |
| `--bg-bubble-user` | `#0a6e40` | Bruger-boble |
| `--bg-bubble-bot` | `#f0faf5` | Bot-boble |
| `--border` | `#c8e8d8` | Alle kanter |
| `--accent` | `#0a6e40` | Primær accent |
| `--accent-btn` | `#0a6e40` | Knap-baggrund |
| `--text-primary` | `#1a3a28` | Primær tekst |
| `--text-secondary` | `#3a6a50` | Brødtekst |
| `--text-dim` | `#7aaa88` | Dimmet |

CSS-variabler defineres på `:root` og overskrives via `.light-mode` på `<body>`-elementet. NiceGUI's `ui.dark_mode` bruges til at toggle klassen.

---

## Layout

### Desktop (≥ 768px)

```
┌─────────────────────────────────────────────────┐
│  HEADER: ⚖️ JuraKlar  [breadcrumb]        🌙/☀️  │
├──────────────┬──────────────────────────────────┤
│  SIDEBAR     │  CHAT AREA                        │
│  160px fast  │  flex: 1                          │
│              │                                   │
│  [VÆLG       │  (forside / chat-bobler)          │
│   JURIST]    │                                   │
│              │                                   │
│  1. Testam.  │                                   │
│  2. Ægte▾   │                                   │
│    › Opret  │                                   │
│    › Særeje │                                   │
│  3. Fremtid  │                                   │
│  (dimmed)    │                                   │
├──────────────┴──────────────────────────────────┤
│  INPUT: 📎  [tekstfelt____________]  Send  💾   │
└─────────────────────────────────────────────────┘
```

### Mobil (< 768px)

Sidebar skjult som standard. Hamburger-ikon (☰) i header åbner en **slide-in drawer** (overlay, 80% bredde, maks 300px) med alle 20 jurister. Tap uden for drawer lukker den.

Når en jurist er valgt og drawer er lukket, vises et **pill-strip** direkte under headeren med:
- Valgt jurist som titel (klikbar → åbner drawer igen)
- Undermenuer som pills (scrollbar vandret)

```
┌─────────────────────────┐
│ ☰  ⚖️ JuraKlar      🌙 │  ← header
├─────────────────────────┤
│ ⚖️ Ægtepagt ▾           │  ← pill-strip (kun efter jurist valgt)
│ [Opret] [Særeje] [Tingl]│
├─────────────────────────┤
│                         │
│   (chat-bobler)         │  ← chat area (scroll)
│                         │
├─────────────────────────┤
│ 📎 [spørgsmål…] Send 💾 │  ← input
└─────────────────────────┘
```

---

## Tilstandsmaskine (per browser-session)

```
START
  │
  ▼
FORSIDE (consent_accepted = false)
  - Viser velkomst + consent-boks
  - Input-række er deaktiveret (opacity 0.35, pointer-events none)
  - Sidebar er synlig men klik på jurister er blokeret
  │
  ├─ Bruger krydser ☑ af
  │    → [FORTSÆT]-knap dukker op
  │
  └─ Bruger trykker [FORTSÆT]
       → consent_accepted = true
       ▼
     JURIST-VALG
       - Input-række aktiveres
       - Sidebar klikbar
       - Chat viser placeholder: "Vælg en jurist i menuen til venstre"
       │
       └─ Bruger klikker jurist i sidebar/drawer
            → selected_advisor = jurist_id
            → Sidebar: valgt jurist foldes ud med undermenuer
            → Øvrige jurister dimmes (vises stadig men gråtonede)
            → Chat viser advisor-placeholder
            ▼
          UNDERMENU-VALG (valgfrit)
            - Bruger klikker undermenu-item
            → selected_service = service_id
            → Input-felt forudfyldes med service-titel
            → Chat skifter til service-historik
            │
            └─ CHAT AKTIV
                 - Send/Enter sender besked
                 - Bobler renderes løbende
                 - Upload 📎 aktiveret
                 - Download 💾 aktiveret

  Fra enhver tilstand:
    - Klik på "⚖️ JuraKlar" i header → FORSIDE (consent_accepted = false, nulstil)
    - Toggle 🌙/☀️ → skifter dark/light mode (ingen state-reset)
    - ☰ (mobil) → åbner/lukker drawer (ingen state-reset)
```

---

## Komponenter

### 1. Header

**Indhold:**
- Venstre: `☰` hamburger-knap (kun synlig på mobil, `display:none` på desktop)
- Venstre: `⚖️ JuraKlar` — klikbar, nulstiller til forside
- Midten: breadcrumb `[jurist] · [undermenu]` — vises når advisor er valgt (skjult på mobil)
- Højre: `🌙`/`☀️` toggle-knap

**NiceGUI:** `ui.element('header')` med `ui.button` til logo-klik og toggle.

---

### 2. Sidebar

**Desktop:**
- Fast bredde 160px, `position: relative`, scrollbar ved overflow
- Altid synlig

**Mobil:**
- Skjult som standard (`display: none`)
- Drawer-overlay ved ☰-klik: `position: fixed; inset: 0; z-index: 100`
- Drawer-panel: `width: min(80vw, 300px)`
- Tap på overlay-baggrund lukker drawer

**Indhold:**
- `[VÆLG JURIST]`-knap øverst. Adfærd:
  - Hvis ingen advisor er valgt: ingen effekt (listen er allerede fuld)
  - Hvis advisor er valgt: nulstiller `state["advisor"] = None`, viser alle 20 igen uden undermenuer
- 20 advisors i fast defineret rækkefølge svarende til `20_rådgivere.txt` (se nedenfor)
- Valgt advisor: foldet ud med undermenuer (fra `advisor.services` grupperet på `category`)
- Øvrige advisors: dimmet (grå tekst), stadig synlige og klikbare
- Ingen advisor valgt: alle 20 vises med fuld farve

**Advisorrækkefølge:** `AdvisorEngine.discover()` sorterer alfabetisk efter mappenavn, ikke efter `20_rådgivere.txt`. `advisor_app.py` re-sorterer ved at anvende følgende hardkodede rækkefølge efter `discover()`-kaldet:

```python
_ADVISOR_ORDER = [
    "testamente", "aegtepagt", "fremtidsfuldmagt", "boligkob", "doedsbo",
    "skilsmisse", "bodeling", "foraeldre", "samliv", "gavebrev",
    "lejeret", "ansaettelsesret", "erstatning", "patientskade", "gaeldssanering",
    "socialret", "forsikring", "naboret", "forbrugerret", "vaergemaal",
]
# Advisors ikke i listen tilføjes bagerst i alfabetisk orden
```

**State-effekter ved advisor-klik:**
1. `state["advisor"] = advisor_id`
2. `state["category"] = None`
3. `state["service"] = advisor.services[0].id if advisor.services else None`
4. Sidebar refresh
5. Chat refresh

---

### 3. Forside / consent

Vises i chat-området når `state["consent_accepted"] == False`.

**Velkomst-tekst (præcis ordlyd):**
```
Hvad kan JuraKlar?
JuraKlar rummer 20 AI-jurister med hver deres speciale.
De kan rådgive dig om juridiske spørgsmål,
Lave juridiske dokumenter som testamente, ægtepagt,
slutseddel, skøde, lejekontrakt og meget mere.
De kan læse dine dokumenter og foreslå rettelser,
finde mangler, opdatere til nyeste lov mm.

Det hele foregår i en Chat med AI-juristen.

Hvad koster det?
Anonym bruger kr 200. MobilePay eller Kort.
Betaling først ved upload eller download.
Bruger der tester og giver feedback kører Gratis,
men skal angive e-mail og udfylde et lille spørgeskema efterfølgende.
```

**Consent-boks:**
```
JuraKlar er
  · Lavet af AI
  · Valideret af AI
  · Testet af AI

Det er på dit eget ansvar at benytte denne rådgivning.

[ ] Ja, jeg har forstået det er AI og at det er mit eget ansvar

[FORTSÆT]  ← kun synlig når checkbox er afkrydset
```

**Input-lås:** Mens `consent_accepted == False` er input-feltet, Send-knap, 📎 og 💾 deaktiverede (visual + funktionel lås via `pointer-events: none` og `opacity: 0.35`).

---

### 4. Chat-område

Uændret logik fra nuværende implementation. Visuelle ændringer:

- Bruger-boble: `--bg-bubble-user`, højrejusteret, `border-radius: 12px 12px 3px 12px`
- Bot-boble: `--bg-bubble-bot` med border, venstrejusteret, `border-radius: 3px 12px 12px 12px`
- Markdown-rendering bevares (`ui.markdown`)
- Scroll-area fylder resterende plads

---

### 5. Input-række

Rækkefølge (venstre → højre): `📎 Upload` · `[tekstfelt]` · `Send` · `Ryd` · `💾 Download`

Upload og download er identiske med nuværende implementation. Kun visuelt restylet.

---

### 6. Pill-strip (kun mobil)

Vises under header på mobil når `state["advisor"]` er sat og `state["consent_accepted"] == True`.

- Advisor-navn som klikbar titel (klik → åbner drawer)
- Undermenuer som vandrette pills (scrollable)
- Aktiv undermenu highlightet med accent-farve

Implementeres som `@ui.refreshable` komponent.

---

## State-struktur

```python
state: dict = {
    "consent_accepted": False,   # NY — låser UI indtil FORTSÆT
    "advisor":          None,    # str | None — valgt advisor_id
    "category":         None,    # str | None — åben kategori i sidebar
    "service":          None,    # int | None — aktiv service
    "uploaded_docs":    [],      # [{"name": str, "text": str}]
    "dark_mode":        True,    # bool — mørk/lys tilstand
}
```

---

## CSS-strategi

CSS defineres som én samlet streng (`_PAGE_CSS`) med CSS-variabler:

```css
:root {
  --bg-deep: #080f0c;
  /* ... alle tokens ... */
}
body.light-mode {
  --bg-deep: #ffffff;
  /* ... lys-overrides ... */
}
```

`ui.dark_mode()` og `ui.add_css()` bruges som i dag. Dark/light toggle kalder `ui.run_javascript("document.body.classList.toggle('light-mode')")` og opdaterer `state["dark_mode"]`.

Responsive breakpoint på 768px via CSS media queries. NiceGUI's Quasar-klasser bruges minimalt — primært til `ui.scroll_area` og `ui.upload`.

---

## Filer der ændres

| Fil | Ændring |
|---|---|
| `src/ui/advisor_app.py` | Komplet rewrite af `start_advisor_ui` og `_PAGE_CSS` |

Ingen ændringer i `advisor_engine.py`, `chat_engine.py`, `cli.py` eller andre filer.

---

## Afgrænsning (ikke i scope)

- Betaling (MobilePay/Kort) — vises kun som tekst på forsiden, ingen implementation
- Feedback-flow (e-mail + spørgeskema) — vises kun som tekst, ingen implementation
- Session-isolation (flere samtidige brugere) — eksisterende begrænsning bevares
- PWA/app-installation
