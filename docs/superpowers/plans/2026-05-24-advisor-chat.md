# Advisor Chat Interface — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a NiceGUI multi-advisor chat interface with per-service RAG prompts, reusable for all JurAklar legal advisors.

**Architecture:** New `AdvisorEngine` wraps multiple `ChatEngine` instances (one per advisor×service combination), each with its own BM25 index and conversation history. New `advisor_app.py` provides a responsive NiceGUI UI with tabs (desktop) / dropdowns (mobile). 25 Danish service prompts stored as `.md` files co-located with the testamente wiki.

**Tech Stack:** Python, NiceGUI (Quasar), BM25 (rank-bm25), existing ChatEngine, Typer CLI, types.SimpleNamespace for duck-typed config.

---

## File Structure

```
juraklar/testamente/prompts/         ← CREATE: 25 service prompt files
  01-hvad-er-et-testamente.md
  02-legal-arvefølge.md
  ... (03–24)
  25-notaren-kan-ikke.md

src/ui/advisor_engine.py             ← CREATE: multi-advisor RAG wrapper
src/ui/advisor_app.py                ← CREATE: NiceGUI standalone UI
src/cli.py                           ← MODIFY: add `advisor` command
```

---

## Task 1: 25 service prompts

**Files:**
- Create: `juraklar/testamente/prompts/01-hvad-er-et-testamente.md` through `25-notaren-kan-ikke.md`

- [ ] **Step 1: Create prompts directory and write all 25 prompt files**

`juraklar/testamente/prompts/01-hvad-er-et-testamente.md`:
```markdown
---
service_id: 1
title: Hvad er et testamente — og har jeg brug for et?
category: Kom i gang
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Hjælp brugeren med at forstå hvad et testamente er og om de har brug for et.

Fremgangsmåde:
- Forklar kort hvad et testamente gør (og hvad det IKKE kan)
- Spørg ind til brugerens situation: er du gift, samlevende, har du børn?
- Vurder konkret om de har brug for et testamente baseret på situationen

Brug wiki-konteksten som faktuel baggrund. Svar på dansk. Vær borgervenlig — undgå juridisk jargon.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/02-legal-arvefølge.md`:
```markdown
---
service_id: 2
title: Hvad sker der med min arv, hvis jeg dør uden testamente?
category: Kom i gang
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar brugeren den legale arvefølge — hvad loven bestemmer uden testamente.

Fremgangsmåde:
- Gennemgå de tre arveklasser (børn, forældre/søskende, bedsteforældre)
- Fremhæv at samlevende IKKE arver uden testamente
- Beregn konkret fordeling hvis brugeren oplyser sin situation

Brug wiki-konteksten som faktuel baggrund. Svar på dansk. Vær konkret og præcis om paragraf-referencer.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/03-hvad-maa-jeg-bestemme.md`:
```markdown
---
service_id: 3
title: Hvad må jeg bestemme i et testamente — og hvad må jeg ikke?
category: Kom i gang
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar reglerne om tvangsarv, frikvote og gyldige testamentsbestemmelser.

Fremgangsmåde:
- Forklar tvangsarvens størrelse (25% af boet til livsarvinger, maks 1.580.000 kr. pr. barn)
- Forklar frikvoten (de resterende 75% kan testamenteres frit)
- Gennemgå hvad man kan og ikke kan bestemme

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/04-skriv-testamente.md`:
```markdown
---
service_id: 4
title: Hjælp mig med at skrive et testamente
category: Opret testamente
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Hjælp brugeren med at formulere de vigtigste bestemmelser i et testamente.

Fremgangsmåde:
- Afdæk brugerens ønsker: hvem skal arve hvad? Er der særlige betingelser?
- Forklar hvilken form testamentet skal have (notar vs. vidner)
- Formuler konkrete bestemmelser i klart dansk — én ad gangen
- Gør opmærksom på at det endelige dokument skal oprettes korrekt (notar anbefales)

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/05-type-testamente.md`:
```markdown
---
service_id: 5
title: Hvilken type testamente passer til mig?
category: Opret testamente
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Hjælp brugeren med at vælge mellem notartestamente, vidnetestamente og nødtestamente.

Fremgangsmåde:
- Spørg ind til brugerens situation (haster det? er notaren tilgængelig? er der vidner?)
- Sammenlign de tre typer: pris, krav, fordele, ulemper
- Giv en klar anbefaling baseret på situationen

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/06-klar-til-notaren.md`:
```markdown
---
service_id: 6
title: Klar til notaren — hvad skal jeg forberede?
category: Opret testamente
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Guides brugeren trin for trin til notarmødet.

Fremgangsmåde:
- Gennemgå hvad der skal medbringes (ID, oversigt over ønsker, navne på arvinger)
- Forklar hvad det koster (ca. 900–1.500 kr. hos notar)
- Beskriv hvad der sker ved mødet og bagefter (CRT-registrering)
- Hjælp brugeren med at forberede sine ønsker

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/07-gensidigt-testamente.md`:
```markdown
---
service_id: 7
title: Opret et gensidigt testamente med min ægtefælle
category: Opret testamente
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar reglerne for indbyrdes testamente og hjælp brugeren med at forstå bindende karakter.

Fremgangsmåde:
- Forklar hvad et gensidigt testamente er og hvornår det er hensigtsmæssigt
- Gennemgå bindende karakter: hvornår kan det ændres?
- Forklar tvangsarvsproblematikken ved gensidigt testamente med børn

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/08-gennemgaa-testamente.md`:
```markdown
---
service_id: 8
title: Gennemgå mit testamente — er det stadig gyldigt?
category: Gennemgang af eksisterende testamente
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Hjælp brugeren med at vurdere om et eksisterende testamente er gyldigt.

Fremgangsmåde:
- Spørg om testamentets type (notar/vidner), dato og underskrifter
- Tjek formkrav: to vidner der var til stede, ikke inhabile, testators habilitet
- Vurder om livsomstændigheder (nyt ægteskab, skilsmisse, børn) kan have ændret gyldigheden
- Anbefal eventuel opdatering

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/09-typiske-fejl.md`:
```markdown
---
service_id: 9
title: Tjek mit testamente for typiske fejl
category: Gennemgang af eksisterende testamente
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Gennemgå de hyppigste fejl der ugyldiggør et testamente.

Fremgangsmåde:
- Gennemgå de 5 hyppigste fejl: inhabile vidner, manglende datering, uklar formulering, overskredet frikvote, ikke registreret i CRT
- Spørg brugeren om testamentets konkrete indhold for at tjekke for fejl
- Giv konkrete forbedringsforslag

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/10-gift-testamente.md`:
```markdown
---
service_id: 10
title: Jeg er blevet gift — hvad sker der med mit gamle testamente?
category: Gennemgang af eksisterende testamente
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar konsekvenserne af nyt ægteskab for et eksisterende testamente.

Fremgangsmåde:
- Forklar at nyt ægteskab som udgangspunkt medfører bortfald af tidligere testamente (AL §74)
- Gennemgå undtagelserne (testamentet er oprettet med tanke på det kommende ægteskab)
- Anbefal hvad brugeren bør gøre nu

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/11-skilt-testamente.md`:
```markdown
---
service_id: 11
title: Jeg er blevet skilt — gælder mine testamentsbestemmelser stadig?
category: Gennemgang af eksisterende testamente
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar hvad skilsmisse betyder for et eksisterende testamente.

Fremgangsmåde:
- Forklar at skilsmisse automatisk tilbagekalder begunstigelser til tidligere ægtefælle (AL §75)
- Gennemgå hvad der sker med øvrige bestemmelser i testamentet
- Anbefal opdatering af testamentet efter skilsmisse

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/12-samlevende.md`:
```markdown
---
service_id: 12
title: Jeg er samlevende — er min partner sikret uden testamente?
category: Familiesituationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar samlevendes retsstilling og hvad der kræves for at sikre partneren.

Fremgangsmåde:
- Forklar klart at samlevende INGEN legal arveret har i Danmark
- Beregn konkret hvad der sker ved dødsfald uden testamente (boet til slægtninge)
- Forklar hvad et testamente skal indeholde for at sikre partner
- Nævn eventuelt samlivskontrakt og begunstigelse på livsforsikring/pension

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/13-boern-flere-forhold.md`:
```markdown
---
service_id: 13
title: Jeg har børn fra flere forhold — hvad gælder?
category: Familiesituationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Gennemgå reglerne om arv til børn fra forskellige forhold.

Fremgangsmåde:
- Forklar at alle livsarvinger (fællesbørn og særbørn) er ligestillede ved arv
- Beregn tvangsarv og frikvote konkret for brugerens situation
- Forklar risikoen for at arven "blandes" med en ny partners midler
- Gennemgå muligheder: testamentarisk særeje, betinget arv

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/14-mindreaarige-boern.md`:
```markdown
---
service_id: 14
title: Jeg vil sikre mine mindreårige børn
category: Familiesituationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Hjælp brugeren med at sikre mindreårige børn via testamente.

Fremgangsmåde:
- Forklar hvem der automatisk får forældremyndighed (den anden forælder)
- Forklar hvornår og hvordan brugeren kan udpege en forældremyndighedsindehaver i testamentet
- Gennemgå aldersgrænser for udbetaling af arv (normalt 18 år, kan hæves til 25)
- Forklar rollen som testamentseksekutor for børnenes arv

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/15-blandede-familier.md`:
```markdown
---
service_id: 15
title: Min ægtefælle har børn fra et tidligere forhold
category: Familiesituationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Hjælp brugeren med at navigere i blandede familiers arveforhold.

Fremgangsmåde:
- Forklar risikoen: ved uskiftet bo kan boet ende hos ægtefælles særbørn
- Gennemgå muligheder: skifte ved dødsfald, begrænsninger i uskiftet bo
- Forklar testamentariske løsninger der beskytter fællesbørn

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/16-tvangsarv.md`:
```markdown
---
service_id: 16
title: Hvad er tvangsarv — og hvad kan jeg frit bestemme?
category: Arv og regler
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar tvangsarvens regler præcist og hjælp brugeren med at forstå sin råderet.

Fremgangsmåde:
- Forklar tvangsarvens størrelse: 25% af boet til livsarvinger (AL §5), maks 1.580.000 kr. pr. barn (2024)
- Beregn frikvoten for brugerens konkrete situation
- Forklar hvad der sker med tvangsarv til umyndige børn
- Gennemgå muligheder for at begrænse arv inden for lovens rammer

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/17-hvem-arver-mig.md`:
```markdown
---
service_id: 17
title: Hvem arver mig — og i hvilken rækkefølge?
category: Arv og regler
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Gennemgå de tre arveklasser og forklar arverækkefølgen.

Fremgangsmåde:
- Beskriv 1. klasse: livsarvinger (børn og deres efterkommere) — arver alt
- Beskriv 2. klasse: forældre og søskende — arver kun hvis ingen 1. klasse arvinger
- Beskriv 3. klasse: bedsteforældre og deres direkte efterkommere
- Forklar ægtefælles særstilling (AL §§9–11)
- Beregn konkret hvem der arver baseret på brugerens oplysninger

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/18-betingelser-arv.md`:
```markdown
---
service_id: 18
title: Kan jeg sætte betingelser for arven?
category: Arv og regler
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar mulighederne for betingede og begrænsede legater.

Fremgangsmåde:
- Forklar testamentarisk særeje: beskytter arv mod modtagerens fremtidige skilsmisse
- Gennemgå aldersgrænser for udbetaling (kan sættes op til 25 år)
- Forklar betingede legater (f.eks. "kun hvis X uddanner sig")
- Gør opmærksom på hvad der IKKE er gyldige betingelser (stridende mod lov/sædelighed)

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/19-arv-vs-forsikring.md`:
```markdown
---
service_id: 19
title: Hvad er forskellen på arv og livsforsikring/pension?
category: Arv og regler
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar hvordan livsforsikringer og pensioner fordeles uden om testamentet.

Fremgangsmåde:
- Forklar at livsforsikringer og pensioner har egne begunstigelsesregler — testamentet gælder IKKE
- Gennemgå hvad der sker uden en navngivet begunstiget (boet arver)
- Forklar sammenhængen: testamente + begunstigelse på forsikring/pension = komplet sikring
- Anbefal brugeren at tjekke sine begunstigelser

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/20-velgoerenhed.md`:
```markdown
---
service_id: 20
title: Jeg vil give arv til velgørenhed
category: Særlige situationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Hjælp brugeren med at testamentere til en velgørende organisation.

Fremgangsmåde:
- Forklar at legater til godkendte organisationer er skattefradragsberettigede for boet
- Gennemgå hvilke organisationer der er godkendt (SKAT's liste)
- Forklar teknisk formulering i testamentet (legat vs. arveret)
- Nævn mulighed for at kombinere med familiens tvangsarv

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/21-udenlandsk-ejendom.md`:
```markdown
---
service_id: 21
title: Jeg ejer fast ejendom i udlandet
category: Særlige situationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Informer brugeren om de særlige regler for fast ejendom i udlandet.

Fremgangsmåde:
- Forklar EU-forordning 650/2012: borgere kan vælge hjemlandets lovgivning
- Gør opmærksom på at fast ejendom i visse lande er underlagt det pågældende lands lov
- Forklar risikoen for dobbelt beskatning og modstridende regler
- Anbefal specialistrådgivning — dette er et komplekst område

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Dette emne kræver specialistrådgivning hos en advokat med erfaring i internationalt arveret.
```

`juraklar/testamente/prompts/22-saereje.md`:
```markdown
---
service_id: 22
title: Jeg vil gøre arven til særeje for modtageren
category: Særlige situationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar testamentarisk særeje og hvordan det beskytter arven.

Fremgangsmåde:
- Forklar hvad testamentarisk særeje betyder: arven indgår ikke i modtagerens bodeling ved skilsmisse
- Gennemgå formulering i testamentet: "arven tilfalder X som særeje"
- Forklar begrænsninger: særeje beskytter ikke mod modtagerens kreditorer
- Gennemgå kombinationsmuligheder (særeje + aldersgrænse)

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/23-arve-fra-afdoed.md`:
```markdown
---
service_id: 23
title: Jeg vil arve fra en afdød — hvad er mine rettigheder?
category: Særlige situationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Hjælp brugeren med at forstå sine rettigheder som arving.

Fremgangsmåde:
- Forklar tvangsarv og hvornår man kan gøre krav på den
- Gennemgå boets behandling: privat skifte vs. skifterettens behandling
- Forklar arveafkald (kan gøres på vegne af egne livsarvinger)
- Gennemgå klagemulighederne ved uenighed om boets behandling

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

`juraklar/testamente/prompts/24-alvorligt-syg.md`:
```markdown
---
service_id: 24
title: Jeg er alvorligt syg og har ikke tid — hvad gør jeg NU?
category: Akutte situationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Guides brugeren hurtigt og klart til at oprette et nødtestamente.

Fremgangsmåde:
- Forklar nødtestamente STRAKS: ingen formkrav, kan oprettes mundtligt eller skriftligt for vidner
- Nødtestamente er gyldigt i 3 måneder efter oprettelsen (AL §74)
- Beskriv trin: 2 vidner til stede, læs ønsker op, vidnerne underskriver
- Anbefal at følge op med et notartestamente når situationen tillader det

Brug wiki-konteksten som faktuel baggrund. Svar på dansk. Vær kortfattet og handlingsorienteret.
```

`juraklar/testamente/prompts/25-notaren-kan-ikke.md`:
```markdown
---
service_id: 25
title: Notaren kan ikke komme til mig — hvad er alternativerne?
category: Akutte situationer
---

Du er en dansk juridisk rådgiver specialiseret i testamente og arveret.
Forklar alternativerne når notaren ikke er tilgængelig.

Fremgangsmåde:
- Forklar vidnetestamente som akut løsning: 2 habile vidner, underskrift, datering
- Gennemgå habilitetskrav til vidner (ikke arvinger, ikke ægtefælle/samlever til arving)
- Nævn at mange notarer tilbyder hjemmebesøg — anbefal at ringe og spørge
- Anbefal CRT-registrering efterfølgende

Brug wiki-konteksten som faktuel baggrund. Svar på dansk.
Komplekse sager anbefales håndteret af en advokat med speciale i arveret.
```

- [ ] **Step 2: Verify all 25 files exist**

Run: `ls juraklar/testamente/prompts/ | wc -l`
Expected: `25`

- [ ] **Step 3: Commit**

```bash
git add juraklar/testamente/prompts/
git commit -m "feat: add 25 testamente service prompts"
```

---

## Task 2: AdvisorEngine

**Files:**
- Create: `src/ui/advisor_engine.py`
- Test: `tests/ui/test_advisor_engine.py`

- [ ] **Step 1: Write the failing test**

Create `tests/ui/test_advisor_engine.py`:
```python
"""Tests for AdvisorEngine discovery and config parsing."""
from __future__ import annotations
import tempfile
from pathlib import Path

import pytest

from src.ui.advisor_engine import (
    AdvisorEngine,
    AdvisorConfig,
    ServiceConfig,
    _parse_frontmatter,
    _make_chat_cfg,
)


# --- _parse_frontmatter ---

def test_parse_frontmatter_valid():
    content = "---\nservice_id: 1\ntitle: Test\ncategory: Kom i gang\n---\n\nBody text here."
    fm, body = _parse_frontmatter(content)
    assert fm["service_id"] == "1"
    assert fm["title"] == "Test"
    assert fm["category"] == "Kom i gang"
    assert "Body text here." in body


def test_parse_frontmatter_no_frontmatter():
    content = "Just body text."
    fm, body = _parse_frontmatter(content)
    assert fm == {}
    assert body == "Just body text."


# --- _make_chat_cfg ---

def test_make_chat_cfg_readable():
    cfg = _make_chat_cfg("TestWiki", Path("/tmp"), "System prompt text")
    assert cfg.wiki_name == "TestWiki"
    assert cfg.wiki_dir == Path("/tmp")
    assert cfg.prompt_chat.read_text() == "System prompt text"
    assert cfg.prompt_chat.read_text(encoding="utf-8") == "System prompt text"


# --- AdvisorEngine.discover ---

def _make_advisor_dir(tmp: Path, advisor_id: str, title: str, n_services: int = 2) -> None:
    d = tmp / advisor_id
    d.mkdir()
    # index.md
    (d / "index.md").write_text(f"# {title}\n\nBeskrivelse.", encoding="utf-8")
    # prompts/
    p = d / "prompts"
    p.mkdir()
    for i in range(1, n_services + 1):
        (p / f"{i:02d}-service-{i}.md").write_text(
            f"---\nservice_id: {i}\ntitle: Service {i}\ncategory: Kategori\n---\n\nPrompt {i}.",
            encoding="utf-8",
        )


def test_discover_single_advisor():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_advisor_dir(root, "testamente", "Testamente")
        engine = AdvisorEngine(root=root, llm=None)
        advisors = engine.discover()
        assert "testamente" in advisors
        adv = advisors["testamente"]
        assert adv.title == "Testamente"
        assert len(adv.services) == 2
        assert adv.services[0].id == 1
        assert adv.services[0].title == "Service 1"
        assert adv.services[0].category == "Kategori"
        assert "Prompt 1." in adv.services[0].prompt


def test_discover_ignores_dirs_without_prompts():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_advisor_dir(root, "testamente", "Testamente")
        (root / "empty-dir").mkdir()  # no prompts/ subdir
        engine = AdvisorEngine(root=root, llm=None)
        advisors = engine.discover()
        assert "testamente" in advisors
        assert "empty-dir" not in advisors


def test_discover_title_fallback():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        d = root / "boligkob"
        d.mkdir()
        p = d / "prompts"
        p.mkdir()
        (p / "01-x.md").write_text(
            "---\nservice_id: 1\ntitle: X\ncategory: A\n---\nPrompt.",
            encoding="utf-8",
        )
        # No index.md — fallback to capitalized dir name
        engine = AdvisorEngine(root=root, llm=None)
        advisors = engine.discover()
        assert advisors["boligkob"].title == "Boligkob"


def test_discover_caches_result():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _make_advisor_dir(root, "testamente", "Testamente")
        engine = AdvisorEngine(root=root, llm=None)
        r1 = engine.discover()
        r2 = engine.discover()
        assert r1 is r2  # same object, not re-computed


def test_get_history_empty_for_unknown_key():
    engine = AdvisorEngine(root=Path("."), llm=None)
    assert engine.get_history("testamente", 1) == []
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ui/test_advisor_engine.py -v 2>&1 | head -30`
Expected: ImportError or ModuleNotFoundError (file doesn't exist yet)

- [ ] **Step 3: Implement advisor_engine.py**

Create `src/ui/advisor_engine.py`:
```python
"""Multi-advisor RAG engine with per-(advisor, service) ChatEngine instances.

Each (advisor_id, service_id) combination gets its own ChatEngine instance
with its own BM25 index and conversation history. ChatEngine instances are
lazy-loaded on first use.

Note: AdvisorEngine is a single shared server instance. History is not
isolated per browser session — designed for single-user local use.
"""
from __future__ import annotations

import re
import types
from dataclasses import dataclass, field
from pathlib import Path

from ..llm.base import BaseLLMClient
from .chat_engine import ChatEngine


@dataclass
class ServiceConfig:
    """Configuration for a single advisory service."""
    id: int
    title: str
    category: str
    prompt: str  # System prompt body (frontmatter stripped)


@dataclass
class AdvisorConfig:
    """Configuration for a single legal advisor (e.g. testamente)."""
    id: str          # directory name, e.g. "testamente"
    title: str       # from index.md heading, e.g. "Testamente"
    services: list[ServiceConfig] = field(default_factory=list)
    wiki_dir: Path = field(default_factory=Path)


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Split YAML frontmatter from body using regex.

    Args:
        content: Full file content including optional frontmatter block.

    Returns:
        Tuple of (frontmatter_dict, body_text). If no frontmatter, returns
        empty dict and original content.
    """
    parts = re.split(r"^---\s*$", content, maxsplit=2, flags=re.MULTILINE)
    if len(parts) == 3:
        fm: dict[str, str] = {}
        for line in parts[1].strip().splitlines():
            if ":" in line:
                k, _, v = line.partition(":")
                fm[k.strip()] = v.strip()
        return fm, parts[2]
    return {}, content


def _make_chat_cfg(wiki_name: str, wiki_dir: Path, prompt_text: str) -> object:
    """Create a duck-typed config object compatible with ChatEngine.

    ChatEngine uses only three attributes of WikiConfig:
      - cfg.wiki_name  (str)
      - cfg.wiki_dir   (Path)
      - cfg.prompt_chat.read_text(encoding=...)  (str)

    Returns a SimpleNamespace that satisfies these without requiring a full
    WikiConfig (which would need many unused fields).
    """
    prompt_ns = types.SimpleNamespace(
        read_text=lambda encoding="utf-8": prompt_text
    )
    return types.SimpleNamespace(
        wiki_name=wiki_name,
        wiki_dir=wiki_dir,
        prompt_chat=prompt_ns,
    )


class AdvisorEngine:
    """Multi-advisor wrapper over ChatEngine.

    Discovers advisors from the filesystem, lazily creates and caches one
    ChatEngine per (advisor_id, service_id) combination.
    """

    def __init__(self, root: Path, llm: BaseLLMClient | None) -> None:
        """
        Args:
            root: Directory containing advisor subdirectories (e.g. juraklar/).
            llm: LLM client for chat responses. May be None for testing discovery only.
        """
        self._root = root
        self._llm = llm
        self._advisors: dict[str, AdvisorConfig] | None = None
        self._engines: dict[tuple[str, int], ChatEngine] = {}

    def discover(self) -> dict[str, AdvisorConfig]:
        """Scan root/ and return all valid advisors.

        A directory is a valid advisor if it contains a prompts/ subdirectory
        with at least one .md file. Result is cached after the first call.

        Returns:
            Dict mapping advisor_id to AdvisorConfig, sorted by directory name.
        """
        if self._advisors is not None:
            return self._advisors

        advisors: dict[str, AdvisorConfig] = {}
        for d in sorted(self._root.iterdir()):
            if not d.is_dir():
                continue
            prompts_dir = d / "prompts"
            if not prompts_dir.exists():
                continue
            prompt_files = sorted(prompts_dir.glob("*.md"), key=lambda p: p.name)
            if not prompt_files:
                continue

            # Parse advisor title from index.md first heading
            title = d.name.capitalize()
            index_file = d / "index.md"
            if index_file.exists():
                m = re.search(
                    r"^#\s+(.+)$",
                    index_file.read_text(encoding="utf-8"),
                    re.MULTILINE,
                )
                if m:
                    title = m.group(1).strip()

            # Parse services
            services: list[ServiceConfig] = []
            for f in prompt_files:
                fm, body = _parse_frontmatter(f.read_text(encoding="utf-8"))
                services.append(ServiceConfig(
                    id=int(fm.get("service_id", 0)),
                    title=fm.get("title", f.stem),
                    category=fm.get("category", ""),
                    prompt=body.strip(),
                ))

            advisors[d.name] = AdvisorConfig(
                id=d.name,
                title=title,
                services=services,
                wiki_dir=d,
            )

        self._advisors = advisors
        return advisors

    def get_engine(self, advisor_id: str, service_id: int) -> ChatEngine:
        """Lazy-load and cache a ChatEngine for (advisor_id, service_id).

        On first call, builds the BM25 index from the advisor's wiki pages.
        Subsequent calls return the cached instance.

        Args:
            advisor_id: Advisor directory name (e.g. "testamente").
            service_id: Service number (1–25).

        Returns:
            ChatEngine instance with BM25 index built.
        """
        key = (advisor_id, service_id)
        if key not in self._engines:
            advisors = self.discover()
            advisor = advisors[advisor_id]
            service = next(s for s in advisor.services if s.id == service_id)
            cfg = _make_chat_cfg(advisor.title, advisor.wiki_dir, service.prompt)
            engine = ChatEngine(cfg)  # type: ignore[arg-type]
            engine.build_index()
            self._engines[key] = engine
        return self._engines[key]

    async def ask(self, advisor_id: str, service_id: int, question: str) -> str:
        """Answer a question using the appropriate ChatEngine.

        Args:
            advisor_id: Advisor directory name.
            service_id: Service number.
            question: User's natural-language question.

        Returns:
            LLM answer as a Markdown-formatted string.
        """
        engine = self.get_engine(advisor_id, service_id)
        return await engine.ask(question, self._llm)

    def get_history(self, advisor_id: str, service_id: int) -> list[dict]:
        """Return conversation history for (advisor_id, service_id).

        Returns empty list if the combination has never been used.
        """
        key = (advisor_id, service_id)
        if key not in self._engines:
            return []
        return list(self._engines[key]._history)

    def clear(self, advisor_id: str, service_id: int) -> None:
        """Clear conversation history for (advisor_id, service_id).

        No-op if the combination has never been used.
        """
        key = (advisor_id, service_id)
        if key in self._engines:
            self._engines[key].clear_history()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/ui/test_advisor_engine.py -v`
Expected: All 7 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/ui/advisor_engine.py tests/ui/test_advisor_engine.py
git commit -m "feat: add AdvisorEngine multi-advisor RAG wrapper"
```

---

## Task 3: advisor_app.py

**Files:**
- Create: `src/ui/advisor_app.py`

- [ ] **Step 1: Write the failing test**

Create `tests/ui/test_advisor_app.py`:
```python
"""Smoke tests for advisor_app imports and start_advisor_ui signature."""
from __future__ import annotations
import inspect
from src.ui.advisor_app import start_advisor_ui


def test_start_advisor_ui_is_callable():
    assert callable(start_advisor_ui)


def test_start_advisor_ui_signature():
    sig = inspect.signature(start_advisor_ui)
    params = list(sig.parameters.keys())
    assert "root" in params
    assert "llm_config" in params
    assert "port" in params
    assert "host" in params
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/ui/test_advisor_app.py -v 2>&1 | head -20`
Expected: ImportError (file doesn't exist)

- [ ] **Step 3: Implement advisor_app.py**

Create `src/ui/advisor_app.py`:
```python
"""NiceGUI advisor chat interface for multi-domain legal advisory.

Responsive layout:
- Desktop (> 599px): advisor tabs + service chips grouped by category
- Mobile (≤ 599px): advisor dropdown + service dropdown

Each (advisor, service) combination has its own conversation history,
maintained in the AdvisorEngine for the duration of the server session.
"""
from __future__ import annotations

import os
from pathlib import Path

from ..llm.factory import create_client
from ..models.config import LLMConfig
from .advisor_engine import AdvisorEngine, AdvisorConfig


def start_advisor_ui(
    root: Path,
    llm_config: LLMConfig,
    *,
    host: str = "0.0.0.0",
    port: int = 8080,
) -> None:
    """Start the NiceGUI advisor chat server.

    Discovers all advisors under root/, creates a shared AdvisorEngine,
    and starts the NiceGUI HTTP server. Blocks until the server is stopped.

    Args:
        root: Directory containing advisor subdirectories (e.g. juraklar/).
        llm_config: LLM backend configuration.
        host: Network interface to bind to.
        port: TCP port for the HTTP server.

    Raises:
        RuntimeError: If nicegui is not installed or no advisors found.
    """
    try:
        from nicegui import ui, app as ng_app  # noqa: PLC0415
    except ImportError as exc:
        raise RuntimeError("nicegui not installed. Run: pip install nicegui") from exc

    llm = create_client(llm_config)
    engine = AdvisorEngine(root=root, llm=llm)
    advisors = engine.discover()

    if not advisors:
        raise RuntimeError(f"No advisors found in {root}. Add a prompts/ subdirectory.")

    storage_secret = os.environ.get("WIKI_UI_STORAGE_SECRET", "juraklar-secret")

    @ui.page("/")
    async def index_page() -> None:  # noqa: RUF029
        ui.dark_mode()

        advisor_ids = list(advisors.keys())
        # Per-connection state (NiceGUI creates a new closure per browser connection)
        state: dict = {
            "advisor": advisor_ids[0],
            "service": advisors[advisor_ids[0]].services[0].id,
        }

        def current_advisor() -> AdvisorConfig:
            return advisors[state["advisor"]]

        def services_by_category() -> dict[str, list]:
            cats: dict[str, list] = {}
            for svc in current_advisor().services:
                cats.setdefault(svc.category, []).append(svc)
            return cats

        # ── Chat container ──────────────────────────────────────────────────
        chat_scroll = ui.scroll_area().classes("w-full flex-1 min-h-0")
        chat_container = chat_scroll.default_slot.parent_id  # placeholder

        with chat_scroll:
            chat_container = ui.column().classes("w-full gap-2 q-pa-sm")

        def refresh_chat() -> None:
            chat_container.clear()
            history = engine.get_history(state["advisor"], state["service"])
            with chat_container:
                if not history:
                    adv = current_advisor()
                    svc = next(
                        (s for s in adv.services if s.id == state["service"]), None
                    )
                    if svc:
                        ui.label(f"📋 {svc.title}").classes(
                            "text-caption text-grey-5 q-mb-sm"
                        )
                        ui.label(
                            "Start samtalen ved at skrive dit spørgsmål nedenfor."
                        ).classes("text-grey-6 text-body2")
                for msg in history:
                    if msg["role"] == "user":
                        with ui.row().classes("w-full justify-end"):
                            with ui.card().classes(
                                "bg-primary text-white q-pa-sm"
                            ).style("max-width: 70%"):
                                ui.label(msg["content"]).classes("text-body2")
                    elif msg["role"] == "assistant":
                        with ui.card().classes("w-full bg-grey-9 q-pa-sm"):
                            ui.markdown(msg["content"]).classes("text-body2")

        def on_advisor_change(new_advisor_id: str) -> None:
            if new_advisor_id not in advisors:
                return
            state["advisor"] = new_advisor_id
            state["service"] = advisors[new_advisor_id].services[0].id
            desktop_chips.refresh()
            mobile_service_select.refresh()
            refresh_chat()

        def on_service_change(new_service_id: int) -> None:
            state["service"] = new_service_id
            desktop_chips.refresh()
            refresh_chat()

        # ── Layout ──────────────────────────────────────────────────────────
        with ui.column().classes("w-full h-screen max-w-4xl mx-auto"):

            # App header
            with ui.row().classes(
                "w-full items-center q-px-md q-py-sm bg-grey-10"
            ):
                ui.label("⚖️ JurAklar").classes("text-h6 text-bold")
                ui.label("Juridisk rådgivning").classes(
                    "text-caption text-grey-5 q-ml-sm"
                )

            # ── DESKTOP: tabs + chips (hidden on mobile, Quasar lt-sm) ──────
            with ui.element("div").classes("gt-xs w-full"):
                # Advisor tabs
                with ui.tabs(value=state["advisor"]).classes(
                    "w-full bg-grey-10"
                ) as desktop_tabs:
                    for adv_id, adv in advisors.items():
                        ui.tab(adv_id, label=adv.title)

                desktop_tabs.on(
                    "update:model-value",
                    lambda e: on_advisor_change(e.args),
                )

                # Service chips by category
                @ui.refreshable
                def desktop_chips() -> None:
                    with ui.column().classes(
                        "w-full q-px-md q-py-sm bg-grey-10 gap-1"
                    ):
                        for cat, svcs in services_by_category().items():
                            ui.label(cat).classes(
                                "text-caption text-grey-5 q-mt-xs"
                            )
                            with ui.row().classes("w-full flex-wrap gap-1"):
                                for svc in svcs:
                                    active = svc.id == state["service"]
                                    ui.chip(
                                        svc.title,
                                        on_click=lambda s=svc: on_service_change(s.id),
                                    ).props(
                                        "color=primary dense"
                                        if active
                                        else "outline color=grey-6 dense"
                                    )

                desktop_chips()

            # ── MOBILE: dropdowns (hidden on desktop, Quasar gt-xs) ─────────
            with ui.element("div").classes("lt-sm w-full q-pa-sm bg-grey-10"):
                ui.label("RÅDGIVER").classes("text-caption text-grey-5")
                ui.select(
                    {k: v.title for k, v in advisors.items()},
                    value=state["advisor"],
                    on_change=lambda e: on_advisor_change(e.value),
                ).classes("w-full q-mb-sm").props("dense dark")

                ui.label("SERVICE").classes("text-caption text-grey-5")

                @ui.refreshable
                def mobile_service_select() -> None:
                    svc_options = {
                        s.id: s.title for s in current_advisor().services
                    }
                    ui.select(
                        svc_options,
                        value=state["service"],
                        on_change=lambda e: on_service_change(e.value),
                    ).classes("w-full").props("dense dark")

                mobile_service_select()

            ui.separator().classes("q-my-none")

            # ── Chat area ────────────────────────────────────────────────────
            refresh_chat()

            # ── Input row ────────────────────────────────────────────────────
            with ui.row().classes(
                "w-full items-center gap-2 q-px-md q-py-sm bg-grey-10"
            ):
                input_box = ui.input(
                    placeholder="Skriv dit spørgsmål..."
                ).classes("flex-1").props("dark dense")

                async def send() -> None:
                    question = input_box.value.strip()
                    if not question:
                        return
                    input_box.value = ""

                    with chat_container:
                        with ui.row().classes("w-full justify-end"):
                            with ui.card().classes(
                                "bg-primary text-white q-pa-sm"
                            ).style("max-width: 70%"):
                                ui.label(question).classes("text-body2")
                        thinking = ui.label("…").classes(
                            "text-grey-5 text-body2 q-ml-sm"
                        )

                    try:
                        answer = await engine.ask(
                            state["advisor"], state["service"], question
                        )
                    except Exception as exc:  # noqa: BLE001
                        answer = f"**Fejl:** {exc}"

                    thinking.delete()
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

    effective_host = os.environ.get("WIKI_UI_HOST", host)
    effective_port = int(os.environ.get("WIKI_UI_PORT", port))

    ui.run(
        host=effective_host,
        port=effective_port,
        title="JurAklar — Juridisk Rådgivning",
        storage_secret=storage_secret,
        reload=False,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest tests/ui/test_advisor_app.py -v`
Expected: 2 tests PASS

- [ ] **Step 5: Commit**

```bash
git add src/ui/advisor_app.py tests/ui/test_advisor_app.py
git commit -m "feat: add advisor_app NiceGUI responsive chat UI"
```

---

## Task 4: CLI command

**Files:**
- Modify: `src/cli.py` (add `advisor` command after the `chat` command)

- [ ] **Step 1: Write the failing test**

Add to `tests/test_cli.py` (or create if it doesn't exist):
```python
def test_advisor_command_is_registered():
    """Verify 'advisor' command is registered in the CLI."""
    from typer.testing import CliRunner
    from src.cli import app
    runner = CliRunner()
    result = runner.invoke(app, ["advisor", "--help"])
    assert result.exit_code == 0
    assert "advisor" in result.output.lower() or "root" in result.output.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli.py::test_advisor_command_is_registered -v 2>&1 | head -20`
Expected: FAIL — "advisor" command not found

- [ ] **Step 3: Add advisor command to src/cli.py**

Add after the `chat` command (after line 214, before `setup`):
```python
@app.command()
def advisor(
    root: str = typer.Option("juraklar", "--root", help="Mappe med rådgivere"),
    host: str = typer.Option("0.0.0.0", "--host", help="Chat server host"),
    port: int = typer.Option(8080, "--port", help="Chat server port"),
) -> None:
    """Start JurAklar multi-advisor chat interface."""
    import os  # noqa: PLC0415
    load_dotenv(Path(__file__).parent.parent / ".env", override=True)

    try:
        from .ui.advisor_app import start_advisor_ui  # noqa: PLC0415
        from .models.config import LLMConfig  # noqa: PLC0415
    except ImportError as exc:
        typer.echo(f"[ERROR] Advisor UI not available: {exc}", err=True)
        raise typer.Exit(1) from exc

    llm_config = LLMConfig(
        backend=os.environ.get("WIKI_BACKEND", "openrouter"),  # type: ignore[arg-type]
        model_id=os.environ.get("WIKI_MODEL_ID", "anthropic/claude-sonnet-4-5"),
    )
    start_advisor_ui(root=Path(root), llm_config=llm_config, host=host, port=port)
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cli.py::test_advisor_command_is_registered -v`
Expected: PASS

- [ ] **Step 5: Manual smoke test (optional)**

Run: `python -m src.cli advisor --help`
Expected: Shows help text with `--root`, `--host`, `--port` options

- [ ] **Step 6: Commit**

```bash
git add src/cli.py
git commit -m "feat: add advisor CLI command for multi-advisor chat UI"
```

---

## Self-review checklist

After all tasks complete, verify:
- [ ] `ls juraklar/testamente/prompts/ | wc -l` → 25
- [ ] `python -m pytest tests/ui/ -v` → all pass
- [ ] `python -m src.cli advisor --help` → shows usage
- [ ] Import smoke test: `python -c "from src.ui.advisor_engine import AdvisorEngine; print('OK')"`
