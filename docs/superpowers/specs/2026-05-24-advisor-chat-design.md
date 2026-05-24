# Advisor Chat Interface — Design Spec

**Dato:** 2026-05-24  
**Status:** Godkendt

---

## Formål

Byg et NiceGUI-baseret chat-interface der giver brugeren adgang til juridisk rådgivning via en advisor-vælger og en service-menu. Interfacet er designet til genbrug på tværs af alle JurAklar-rådgivere (Testamente, Skilsmisse, Boligkøb m.fl.).

---

## Arkitektur

### Nye filer

```
juraklar/
  testamente/
    prompts/                         ← 25 service-prompts (ny mappe)
      01-hvad-er-et-testamente.md
      02-legal-arvefølge.md
      ...
      25-noedtestamente.md

src/ui/
  advisor_app.py                     ← NY: NiceGUI standalone app
  advisor_engine.py                  ← NY: multi-advisor wrapper

src/cli.py                           ← MODIFICERES: tilføj `advisor`-kommando
```

### Uændrede filer

```
src/ui/chat_engine.py                ← UÆNDRET
src/ui/app.py                        ← UÆNDRET
src/models/config.py                 ← UÆNDRET
```

---

## Prompt-filformat

Hver service-prompt er en Markdown-fil med YAML frontmatter:

```markdown
---
service_id: 1
title: Hvad er et testamente — og har jeg brug for et?
category: Kom i gang
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.

Brugeren vil forstå hvad et testamente er, og om de har brug for et.

Hjælp dem ved at:
- Forklare kort hvad et testamente gør (og hvad det ikke gør)
- Spørge ind til deres situation (gift? børn? samlever? fast ejendom?)
- Vurdere om de konkret har brug for et testamente

Brug altid det relevante indhold fra wiki'en som faktuel baggrund.
Svar på dansk. Vær konkret og borgervenlig — undgå juridisk jargon.
```

**Navngivning:** `{NN}-{slug}.md` hvor `NN` er nummeret fra rådgivningsmenuen (01–25).  
**Placering:** `juraklar/{advisor_id}/prompts/`

---

## Discovery-logik

`AdvisorEngine.discover(root: Path)` scanner `root/` (dvs. `juraklar/`) og bygger en advisor-katalog:

1. Iterer over alle undermapper i `root/`
2. En mappe er en gyldig rådgiver hvis den indeholder `prompts/` (mindst én `.md`-fil)
3. **Titel** hentes fra første `# Overskrift` i `index.md` (fallback: mappe-navn capitalized)
4. **Services** loades fra `prompts/*.md`, sorteret numerisk på filnavn-prefix
5. Frontmatter parses med simpel regex (`re.split(r'^---\s*$', content, 2, re.MULTILINE)`) — ingen ekstern afhængighed

```python
@dataclass
class ServiceConfig:
    id: int
    title: str
    category: str
    prompt: str          # rå body-tekst fra .md-filen

@dataclass
class AdvisorConfig:
    id: str              # mappe-navn, fx "testamente"
    title: str           # fra index.md
    services: list[ServiceConfig]
    wiki_dir: Path       # juraklar/testamente/ (til ChatEngine)
```

---

## AdvisorEngine API

```python
class AdvisorEngine:
    def __init__(self, root: Path, llm: str): ...

    def discover(self) -> dict[str, AdvisorConfig]:
        """Scanner root/ og returnerer alle gyldige rådgivere."""

    def get_engine(self, advisor_id: str, service_id: int) -> ChatEngine:
        """
        Lazy-loader og cacher én ChatEngine per (advisor_id, service_id).
        Hver instans har sin egen wiki_dir og sin egen interne historik.
        BM25-indekset bygges ved første kald (build_index()).
        """

    def ask(self, advisor_id: str, service_id: int, question: str) -> str:
        """
        Sender spørgsmål til ChatEngine for kombinationen.
        System-prompten sendes som første bruger-besked ved ny session.
        Returnerer svaret som streng.
        """

    def get_history(self, advisor_id: str, service_id: int) -> list[dict]:
        """Returnerer chat-historik fra ChatEngine-instansen for kombinationen."""

    def clear(self, advisor_id: str, service_id: int) -> None:
        """Kalder engine.clear_history() for kombinationen."""
```

**Historik-nøgle:** `(advisor_id, service_id)` → dedikeret `ChatEngine`-instans  
Lazy-loaded: instansen oprettes og indekset bygges første gang kombinationen aktiveres.  
Historik holdes in-memory for sessionens varighed. Ingen persistens til disk.

**Enkeltbruger-forudsætning:** `AdvisorEngine` er en delt server-instans. Historik er ikke isoleret per browser-session. Dette er acceptabelt for lokal brug af én bruger.

**System-prompt-injektion:** Første gang `ask()` kaldes for en ny `(advisor, service)`-kombination, sendes service-promptens body som en indledende besked til `ChatEngine.ask()`, så den indgår i konteksten.

---

## UI — advisor_app.py

### Layout

**Desktop (≥768px) — tabs + chips:**
```
┌─────────────────────────────────────────────────┐
│  [📜 Testamente] [👨‍👩‍👧 Skilsmisse] [🏠 Boligkøb]  │  ← q-tabs
├─────────────────────────────────────────────────┤
│  KOM I GANG                                     │
│  [1. Hvad er et testamente?●] [2. Arvefølge]... │  ← q-chip per service
│  OPRET TESTAMENTE                               │
│  [4. Hjælp mig med at skrive] [5. Typer]...    │
├─────────────────────────────────────────────────┤
│                                                 │
│  [bot] Hej! Du har valgt »...«                  │  ← chat-bobler
│                              [bruger] ...  [  ] │
│                                                 │
├─────────────────────────────────────────────────┤
│  [Skriv dit spørgsmål...              ] [Send]  │  ← input
└─────────────────────────────────────────────────┘
```

**Mobil (<768px) — dropdowns:**
```
┌───────────────────────────┐
│  RÅDGIVER                 │
│  [📜 Testamente        ▾] │  ← q-select
│  SERVICE                  │
│  [1. Hvad er et test.. ▾] │  ← q-select
├───────────────────────────┤
│  [bot] Hej!...            │
│           [bruger] ...    │
├───────────────────────────┤
│  [Skriv her...    ] [→]   │
└───────────────────────────┘
```

Responsivt skift via Quasars built-in breakpoint-klasser. NiceGUI eksponerer disse via `ui.add_css()` og betingede `classes('lt-sm')` / `classes('gt-xs')` på elementer.

### State (per browser-session)

```python
# NiceGUI app.storage.user (per browser-tab)
{
  "active_advisor": "testamente",
  "active_service": 1
}
# Historik holdes i AdvisorEngine-instansen (shared, keyed på (advisor, service))
```

### Interaktioner

| Handling | Effekt |
|---|---|
| Klik på advisor-tab | Skifter `active_advisor`, viser services for ny rådgiver, genindlæser historik |
| Klik på service-chip | Skifter `active_service`, genindlæser historik for kombinationen |
| Send besked | `engine.ask(advisor, service, text)` → appender til chat |
| Skift service | Historik gemmes — genindlæses næste gang service aktiveres |

---

## CLI-integration

Ny kommando i `src/cli.py`:

```python
@app.command()
def advisor(
    root: str = typer.Option("juraklar", help="Mappe med rådgivere"),
    port: int = typer.Option(8080, help="Port"),
    host: str = typer.Option("0.0.0.0", help="Host"),
):
    """Start advisor chat-interface."""
    from src.ui.advisor_app import start_advisor_ui
    start_advisor_ui(root=Path(root), port=port, host=host)
```

---

## 25 Service-prompts — Testamente

Alle 25 prompts oprettes i `juraklar/testamente/prompts/`. De mapper direkte til `raadgivningsmenu.md`:

| Fil | Title | Kategori |
|---|---|---|
| `01-hvad-er-et-testamente.md` | Hvad er et testamente — og har jeg brug for et? | Kom i gang |
| `02-legal-arvefølge.md` | Hvad sker der med min arv, hvis jeg dør uden testamente? | Kom i gang |
| `03-hvad-maa-jeg-bestemme.md` | Hvad må jeg bestemme i et testamente — og hvad må jeg ikke? | Kom i gang |
| `04-skriv-testamente.md` | Hjælp mig med at skrive et testamente | Opret testamente |
| `05-type-testamente.md` | Hvilken type testamente passer til mig? | Opret testamente |
| `06-klar-til-notaren.md` | Klar til notaren — hvad skal jeg forberede? | Opret testamente |
| `07-gensidigt-testamente.md` | Opret et gensidigt testamente med min ægtefælle | Opret testamente |
| `08-gennemgaa-testamente.md` | Gennemgå mit testamente — er det stadig gyldigt? | Gennemgang |
| `09-typiske-fejl.md` | Tjek mit testamente for typiske fejl | Gennemgang |
| `10-gift-testamente.md` | Jeg er blevet gift — hvad sker der med mit gamle testamente? | Gennemgang |
| `11-skilt-testamente.md` | Jeg er blevet skilt — gælder mine testamentsbestemmelser stadig? | Gennemgang |
| `12-samlevende.md` | Jeg er samlevende — er min partner sikret uden testamente? | Familiesituationer |
| `13-boern-flere-forhold.md` | Jeg har børn fra flere forhold — hvad gælder? | Familiesituationer |
| `14-mindreaarige-boern.md` | Jeg vil sikre mine mindreårige børn | Familiesituationer |
| `15-blandede-familier.md` | Min ægtefælle har børn fra et tidligere forhold | Familiesituationer |
| `16-tvangsarv.md` | Hvad er tvangsarv — og hvad kan jeg frit bestemme? | Arv og regler |
| `17-hvem-arver-mig.md` | Hvem arver mig — og i hvilken rækkefølge? | Arv og regler |
| `18-betingelser-arv.md` | Kan jeg sætte betingelser for arven? | Arv og regler |
| `19-arv-vs-forsikring.md` | Hvad er forskellen på arv og livsforsikring/pension? | Arv og regler |
| `20-velgoerenhed.md` | Jeg vil give arv til velgørenhed | Særlige situationer |
| `21-udenlandsk-ejendom.md` | Jeg ejer fast ejendom i udlandet | Særlige situationer |
| `22-saereje.md` | Jeg vil gøre arven til særeje for modtageren | Særlige situationer |
| `23-arve-fra-afdoed.md` | Jeg vil arve fra en afdød — hvad er mine rettigheder? | Særlige situationer |
| `24-alvorligt-syg.md` | Jeg er alvorligt syg og har ikke tid — hvad gør jeg NU? | Akutte situationer |
| `25-notaren-kan-ikke.md` | Notaren kan ikke komme til mig — hvad er alternativerne? | Akutte situationer |

---

## Out of scope

- Persistens af historik på tværs af browser-sessioner (ingen database)
- Autentificering
- Redigering af prompts i UI
- Integration med eksisterende `app.py`

---

## Lovgivning og ansvarsfraskrivelse

Alle prompts skal afsluttes med vejledning om at komplekse sager anbefales håndteret af en advokat. Rådgivningen er baseret på gældende dansk ret (Arveloven LBK nr. 1347 af 15/06/2021).
