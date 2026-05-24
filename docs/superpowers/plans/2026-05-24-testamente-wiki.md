# Testamente-wiki Implementationsplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bygge en komplet, borgervenlig dansk wiki om testamente — fra deep research via retsinformation.dk til færdige wiki-sider — ved at følge AGENTS.md-pipelinen og bruge de færdige prompts i `config/prompts/`.

**Architecture:** To faser: (1) Deep research henter lovgivning og vejledninger fra nettet og gemmer dem som strukturerede Markdown-filer i `raw/`. (2) AGENTS.md-pipelinen (Read → Generate → Topics → Groups → Index → Consolidate → Lint → Repair) transformerer raw-filerne til færdige wiki-sider via de prompt-templates der ligger i `config/prompts/`. Alle operationer sker via fil-værktøjer (Read, Write, Edit, WebFetch) — aldrig Bash til projektkode.

**Tech Stack:** WebFetch (kildeindsamling), Read/Write/Edit (filoperationer), Jinja2-style prompt-templates i `config/prompts/`, AGENTS.md pipeline (8 stadier), Markdown, Dansk sprog

---

## Prompt-mapping for testamente-wiki

| Entity type | Wiki-prompt (Writer) | Evaluerings-prompt | Output-mappe |
|---|---|---|---|
| `policies` | `config/prompts/wiki_summary_policies.md` | `config/prompts/wiki_evaluate_policies.md` | `policies/` |
| `articles` | `config/prompts/wiki_summary_articles.md` | `config/prompts/wiki_evaluate_articles.md` | `articles/` |
| `notes` | `config/prompts/wiki_summary_notes.md` | `config/prompts/wiki_evaluate_notes.md` | `notes/` |
| Tema-sider | `config/prompts/wiki_agent_create_theme.md` | — | `themes/` |

**Rå kilder → entity type:**
- Arveloven, bekendtgørelser, lovtekst → `policies`
- Advokatsamfundet, Domstolsstyrelsen, borger.dk → `articles`
- Juridisk lærebogsmateriale, praksis → `notes`

**Tre-pas processen (Stage 2 — Generate):**
```
Pass 1 — Writer:   Anvend wiki_summary_{type}.md → draft Markdown
Pass 2 — Evaluator: Anvend wiki_evaluate_{type}.md → JSON {approved, problems, suggestions}
Pass 3 — Editor:   Hvis approved=false: anvend wiki_editor.md med {problems} og {suggestions} → endelig Markdown
```

**Wiki-sektioner (dansk oversættelse af prompt-skabelonen):**
```markdown
# {Titel}

## Resumé
{2–4 sætninger om sidens formål og hovedpointer.}

## Vigtige Emner
- {Bullet-liste over centrale emner dækket af kilden}

## Detaljer
{Uddybet indhold med H3-underoverskrifter efter behov.}

## Relaterede Temaer
- [Tvangsarv](../themes/Tvangsarv.md)
- [Notartestamente](../themes/Notartestamente.md)
```

> ⚠️ Links til temaer bruger standard Markdown `[Tema](../themes/Tema.md)` — IKKE `[[wikilink]]` format.

---

## Filstruktur der oprettes

```
juraklar/testamente/
  raw/
    arveloven.md                         ← type: lovgivning (→ policies)
    centralregistret-for-testamenter.md  ← type: lovgivning (→ policies)
    bekendtgoerelse-notarer.md           ← type: lovgivning (→ policies)
    advokatraad-testamente.md            ← type: vejledning (→ articles)
    domstolsstyrelsen-vejledning.md      ← type: vejledning (→ articles)
    juridisk-laerebogsudtog.md           ← type: laerebog   (→ notes)
  policies/
    arvelovens-rammer.md
    formkrav.md
  articles/
    hvad-er-et-testamente.md
    typer-af-testamenter.md
    hvem-kan-arve.md
    oprettelse-trin-for-trin.md
    typiske-fejl.md
    saerlige-situationer.md
  notes/
    juridisk-grundbegreber.md
  themes/
    Tvangsarv.md
    Notartestamente.md
    Vidnetestamente.md
    Testamentarisk Habilitet.md
    Legal Arvefølge.md
    Centralregisteret For Testamenter.md
  index.md
  topics.md
  lint_report.md
```

**Frontmatter-standard for raw-filer:**
```markdown
---
kilde: <kildens fulde navn>
url: <https://...>
hentet: 2026-05-24
type: lovgivning | vejledning | laerebog
status: gaeldende
---
```

---

## Task 1: Opsætning — mapper + AGENTS.md CONFIG

**Files:**
- Create: `juraklar/testamente/raw/.gitkeep`
- Modify: `AGENTS.md` (CONFIG-blokken)

- [ ] **Step 1.1: Opret mappestruktur**

  Skriv en placeholder-fil for at oprette mappen:
  Opret `juraklar/testamente/raw/.gitkeep` med tomt indhold.

- [ ] **Step 1.2: Opdater CONFIG-blokken i AGENTS.md**

  Find denne blok i AGENTS.md:
  ```
  <!--
  CONFIG_START
  wiki_name:
  input_folder:
  output_folder:
  entity_types:
  language: English
  CONFIG_END
  -->
  ```

  Erstat den med:
  ```
  <!--
  CONFIG_START
  wiki_name: Testamente
  input_folder: juraklar/testamente/raw/
  output_folder: juraklar/testamente/
  entity_types: policies, articles, notes
  language: Dansk
  CONFIG_END
  -->
  ```

- [ ] **Step 1.3: Verificer**

  Læs AGENTS.md og bekræft at alle 5 CONFIG-felter er udfyldt korrekt.

- [ ] **Step 1.4: Commit**

  ```
  git add juraklar/testamente/raw/.gitkeep AGENTS.md
  git commit -m "chore: opsæt testamente-mappestruktur og AGENTS.md config"
  ```

---

## Task 2: Hent Arveloven (primær lovkilde → policies)

**Files:**
- Create: `juraklar/testamente/raw/arveloven.md`

- [ ] **Step 2.1: Find gældende Arvelov på retsinformation.dk**

  Hent søgeresultater fra:
  `https://www.retsinformation.dk/Search?search=arveloven&document_type=LBK`

  Vælg det resultat der er markeret "Gældende" (ikke "Historisk"). Det er typisk den nyeste LBK. Hent den fulde lovtekst.

  Direkte URL at forsøge: `https://www.retsinformation.dk/eli/lta/2007/515`
  (Arveloven — men verificer at det er gældende; find nyere LBK-version hvis nødvendigt.)

  **Krav:** Siden MÅ IKKE være mærket "Historisk".

- [ ] **Step 2.2: Udtræk og skriv arveloven.md**

  Gem som `juraklar/testamente/raw/arveloven.md`:

  ```markdown
  ---
  kilde: Arveloven
  url: https://www.retsinformation.dk/eli/lta/[årstal]/[nummer]
  hentet: 2026-05-24
  type: lovgivning
  status: gaeldende
  ---
  # Arveloven

  > LBK nr. [nummer] af [dato]. Gældende. Hentet fra retsinformation.dk.

  ## Kapitel 1: Slægtninges arveret (§ 1–§ 6)

  ### § 1
  [lovtekst]

  [...]

  ## Kapitel 2: Ægtefælles arveret (§ 7–§ 14)

  [lovtekst]

  ## Kapitel 3: Om testamenter (§ 63–§ 97)

  ### § 63 — Testators rådighed
  [lovtekst]

  ### § 64 — Testamentarisk habilitet
  [lovtekst]

  [alle §§ 63–97]

  ## § 5 — Tvangsarv og frikvote

  [lovtekst for § 5, stk. 1–2]
  ```

- [ ] **Step 2.3: Verificer**

  Læs filen. Bekræft:
  - Frontmatter: alle 5 felter til stede
  - `status: gaeldende`
  - Indeholder §§ 63–97 (testamentkapitlet)
  - Indeholder § 5 om tvangsarv

- [ ] **Step 2.4: Commit**

  ```
  git add juraklar/testamente/raw/arveloven.md
  git commit -m "research: hent gældende Arvelov fra retsinformation.dk"
  ```

---

## Task 3: Hent regler om Centralregisteret for Testamenter (→ policies)

**Files:**
- Create: `juraklar/testamente/raw/centralregistret-for-testamenter.md`

- [ ] **Step 3.1: Find regler på retsinformation.dk og tinglysningsretten.dk**

  Hent fra:
  - `https://tinglysningsretten.dk/testamente/` (Tinglysningsrettens borgerinformation)
  - Søg bekendtgørelse: `https://www.retsinformation.dk/Search?search=centralregistret+testamenter`

  Find den gældende bekendtgørelse (ikke historisk).

- [ ] **Step 3.2: Skriv centralregistret-for-testamenter.md**

  ```markdown
  ---
  kilde: Centralregisteret for Testamenter — Tinglysningsretten
  url: https://tinglysningsretten.dk/testamente/
  hentet: 2026-05-24
  type: lovgivning
  status: gaeldende
  ---
  # Centralregisteret for Testamenter

  > Statsligt register for anmeldelse af testamenter.
  > Forvaltes af Tinglysningsretten under Domstolsstyrelsen.

  ## Hvad er registret?

  [indhold]

  ## Bekendtgørelsesgrundlag

  [lovhenvisning]

  ## Hvem kan anmelde?

  [indhold]

  ## Sådan anmelder du

  [trin-for-trin]

  ## Gebyrer

  [aktuelle takster]

  ## Hvad registreres?

  [selve testamentet eller blot oplysning om eksistens]
  ```

- [ ] **Step 3.3: Verificer**

  Frontmatter komplet, `status: gaeldende`, indeholder anmeldelsesprocedure.

- [ ] **Step 3.4: Commit**

  ```
  git add juraklar/testamente/raw/centralregistret-for-testamenter.md
  git commit -m "research: hent regler om Centralregisteret for Testamenter"
  ```

---

## Task 4: Hent bekendtgørelse om notarbekræftelse (→ policies)

**Files:**
- Create: `juraklar/testamente/raw/bekendtgoerelse-notarer.md`

- [ ] **Step 4.1: Find bekendtgørelse og Retsplejelovens §§ om notarer**

  Hent fra retsinformation.dk:
  - Søg: `https://www.retsinformation.dk/Search?search=notarbekr%C3%A6ftelse&document_type=BEK`
  - Find gældende BEK om notarforretninger.
  - Find også Retsplejelovens §§ om notarvirksomhed (typisk § 16–§ 16 k) via:
    `https://www.retsinformation.dk/Search?search=retsplejeloven&document_type=LBK`
    (vælg nyeste gældende LBK)

- [ ] **Step 4.2: Skriv bekendtgoerelse-notarer.md**

  ```markdown
  ---
  kilde: Bekendtgørelse om notarbekræftelse + Retsplejeloven §§ om notarer
  url: https://www.retsinformation.dk/[bekendtgørelse-url]
  hentet: 2026-05-24
  type: lovgivning
  status: gaeldende
  ---
  # Notarbekræftelse af testamenter — lovgrundlag

  ## Retsplejeloven — §§ om notarvirksomhed

  ### § 16 — Notarens opgaver
  [lovtekst]

  [øvrige relevante §§]

  ## Bekendtgørelse om notarforretninger

  ### Krav til notartestamente
  [fremmøde, identifikation, hvad skal fremgå]

  ### Gebyr for notarbekræftelse
  [aktuelle satser fra retsafgiftsloven]

  ## Krav til testator
  [habilitet, personligt fremmøde]
  ```

- [ ] **Step 4.3: Verificer**

  Frontmatter komplet, `status: gaeldende`, indeholder notarlovgivning og gebyrer.

- [ ] **Step 4.4: Commit**

  ```
  git add juraklar/testamente/raw/bekendtgoerelse-notarer.md
  git commit -m "research: hent bekendtgørelse og retsplejelov om notarbekræftelse"
  ```

---

## Task 5: Hent Advokatsamfundets og borger.dk vejledning (→ articles)

**Files:**
- Create: `juraklar/testamente/raw/advokatraad-testamente.md`

- [ ] **Step 5.1: Hent fra advokatsamfundet.dk og borger.dk**

  Hent fra:
  - `https://www.advokatsamfundet.dk/for-borgere/find-en-advokat/hvad-kan-en-advokat-hjaelpe-dig-med/arv-og-testamente/`
  - `https://www.borger.dk/familie-og-boern/doed-og-begravelse/testamente`

- [ ] **Step 5.2: Skriv advokatraad-testamente.md**

  ```markdown
  ---
  kilde: Advokatsamfundet + borger.dk
  url: https://www.advokatsamfundet.dk/for-borgere/...
  hentet: 2026-05-24
  type: vejledning
  status: gaeldende
  ---
  # Advokatsamfundets vejledning: Testamente

  ## Hvorfor oprette et testamente?
  [indhold]

  ## Hvad kan et testamente bestemme?
  [indhold]

  ## Typer af testamenter
  [indhold]

  ## Hvad koster det?
  [indhold]

  ## Hvornår er et testamente ugyldigt?
  [indhold]

  ## Fra borger.dk
  [indhold fra borger.dk-siden]
  ```

- [ ] **Step 5.3: Verificer**

  `type: vejledning`, frontmatter komplet, borgervenligt sprog.

- [ ] **Step 5.4: Commit**

  ```
  git add juraklar/testamente/raw/advokatraad-testamente.md
  git commit -m "research: hent Advokatsamfundet og borger.dk vejledning om testamente"
  ```

---

## Task 6: Hent Domstolsstyrelsens vejledning om notarer (→ articles)

**Files:**
- Create: `juraklar/testamente/raw/domstolsstyrelsen-vejledning.md`

- [ ] **Step 6.1: Hent fra domstol.dk**

  Hent fra:
  - `https://www.domstol.dk/notar/`
  - `https://www.domstol.dk/notar/testamente/`

- [ ] **Step 6.2: Skriv domstolsstyrelsen-vejledning.md**

  ```markdown
  ---
  kilde: Domstolsstyrelsen — domstol.dk
  url: https://www.domstol.dk/notar/testamente/
  hentet: 2026-05-24
  type: vejledning
  status: gaeldende
  ---
  # Domstolsstyrelsens vejledning om notartestamente

  ## Hvad laver en notar?
  [indhold]

  ## Sådan opretter du et notartestamente — trin for trin
  [indhold]

  ## Book en notartime
  [hvilken ret, pris, hvad medbringer man]

  ## Gebyrer (gældende takster)
  [indhold]

  ## Hvad sker der med testamentet efter notarbekræftelse?
  [registrering, opbevaring]
  ```

- [ ] **Step 6.3: Verificer**

  Frontmatter komplet, `status: gaeldende`, indeholder konkrete trin.

- [ ] **Step 6.4: Commit**

  ```
  git add juraklar/testamente/raw/domstolsstyrelsen-vejledning.md
  git commit -m "research: hent Domstolsstyrelsens vejledning om notartestamente"
  ```

---

## Task 7: Saml juridisk grundmateriale (→ notes)

**Files:**
- Create: `juraklar/testamente/raw/juridisk-laerebogsudtog.md`

- [ ] **Step 7.1: Find frit tilgængeligt juridisk materiale**

  Forsøg at hente fra:
  - `https://jura.ku.dk` → søg "arveret" eller "testamente"
  - `https://www.domsdatabasen.dk` → centrale domme om testamentarisk habilitet og formkrav

  **Fallback hvis intet open-access materiale findes:** Udled de juridiske grundbegreber direkte fra den allerede hentede `arveloven.md` ved at sammenfatte og forklare §§ med juridisk-faglig præcision. Sæt da `type: praksis` og `kilde: Udledt af Arveloven`.

- [ ] **Step 7.2: Skriv juridisk-laerebogsudtog.md**

  ```markdown
  ---
  kilde: Juridisk grundmateriale — arveret og testamente
  url: [primær kilde-URL eller "Udledt af Arveloven"]
  hentet: 2026-05-24
  type: laerebog
  status: gaeldende
  ---
  # Juridisk grundmateriale: Arveret og testamente

  ## Grundbegreber i dansk arveret

  ### Legal arvefølge
  [arveklasser 1, 2, 3 — hvem arver hvad uden testamente]

  ### Tvangsarv og frikvote
  [1/4 tvangsarv til livsarvinger, 3/4 fri disposition — Arveloven § 5]

  ### Testators dispositionsret
  [hvad kan man lovligt bestemme i et testamente]

  ## Testamentarisk habilitet

  [krav: 18 år, ikke under værgemål der afskærer testationsret — Arveloven § 64]

  ## Formkrav — konsekvenser af manglende opfyldelse

  [vidnekrav, notarkrav, hvad ugyldiggør]

  ## Centrale retspraksis-referencer

  | Problem | Retlig konsekvens |
  |---------|------------------|
  | Inhabile vidner | Testamentet ugyldigt (Arveloven § 66) |
  | Testator uden habilitet | Testamentet anfægteligt (§ 64) |
  | Manglende notarbekræftelse | Vidnetestamente — andre formkrav gælder |

  ## Særlige konstruktioner

  ### Gensidigt testamente (indbyrdes testamente)
  [ægtefæller testamenterer til hinanden — betingelser og ophør]

  ### Kombinationstestamente
  [blanding af notarbekræftelse og egenhændigt brev]

  ### Særeje ved testamente
  [testamentarisk særeje — hvad det indebærer]
  ```

- [ ] **Step 7.3: Verificer**

  Frontmatter komplet, indeholder tvangsarv, habilitet og formkrav.

- [ ] **Step 7.4: Commit**

  ```
  git add juraklar/testamente/raw/juridisk-laerebogsudtog.md
  git commit -m "research: saml juridisk grundmateriale om arveret og testamente"
  ```

---

## Task 8: Stage 1 — Read (verificer alle raw-filer)

**Files:**
- Read: alle 6 filer i `juraklar/testamente/raw/`

- [ ] **Step 8.1: Læs alle 6 raw-filer**

  Læs hver fil og byg en intern dokumentliste:

  ```
  [
    { filename: "arveloven.md",                        entity_type: "policies", prompt_writer: "wiki_summary_policies.md",  prompt_eval: "wiki_evaluate_policies.md" },
    { filename: "centralregistret-for-testamenter.md", entity_type: "policies", prompt_writer: "wiki_summary_policies.md",  prompt_eval: "wiki_evaluate_policies.md" },
    { filename: "bekendtgoerelse-notarer.md",           entity_type: "policies", prompt_writer: "wiki_summary_policies.md",  prompt_eval: "wiki_evaluate_policies.md" },
    { filename: "advokatraad-testamente.md",            entity_type: "articles", prompt_writer: "wiki_summary_articles.md",  prompt_eval: "wiki_evaluate_articles.md" },
    { filename: "domstolsstyrelsen-vejledning.md",      entity_type: "articles", prompt_writer: "wiki_summary_articles.md",  prompt_eval: "wiki_evaluate_articles.md" },
    { filename: "juridisk-laerebogsudtog.md",           entity_type: "notes",    prompt_writer: "wiki_summary_notes.md",     prompt_eval: "wiki_evaluate_notes.md"    },
  ]
  ```

- [ ] **Step 8.2: Verificer krav**

  Bekræft for hver fil:
  - Frontmatter komplet (alle 5 felter)
  - `status: gaeldende` (aldrig "historisk")
  - Indhold ikke tomt

- [ ] **Step 8.3: Rapporter**

  Print: `✓ Stage 1 complete — 6 raw-filer læst, alle gældende, entity types tildelt`

---

## Task 9: Stage 2 — Generate (opret wiki-sider med 3-pas processen)

**Files:**
- Create: `juraklar/testamente/policies/arvelovens-rammer.md`
- Create: `juraklar/testamente/policies/formkrav.md`
- Create: `juraklar/testamente/articles/hvad-er-et-testamente.md`
- Create: `juraklar/testamente/articles/typer-af-testamenter.md`
- Create: `juraklar/testamente/articles/hvem-kan-arve.md`
- Create: `juraklar/testamente/articles/oprettelse-trin-for-trin.md`
- Create: `juraklar/testamente/articles/typiske-fejl.md`
- Create: `juraklar/testamente/articles/saerlige-situationer.md`
- Create: `juraklar/testamente/notes/juridisk-grundbegreber.md`

**3-pas proces — gælder for ALLE sider:**

```
Pass 1 — Writer:
  Læs prompt: config/prompts/wiki_summary_{entity_type}.md
  Udfyld: object_type = {entity_type}, language = Dansk
  Skriv wiki-side ud fra kildeindholdet.
  Sektioner (på dansk): Resumé, Vigtige Emner, Detaljer, Relaterede Temaer
  Links til temaer: [Tema](../themes/Tema.md)  ← IKKE [[wikilink]]

Pass 2 — Evaluator:
  Læs prompt: config/prompts/wiki_evaluate_{entity_type}.md
  Udfyld: object_type = {entity_type}, language = Dansk
  Evaluer udkastet → returner JSON:
  { "approved": true/false, "problems": [...], "suggestions": [...] }

Pass 3 — Editor (kun hvis approved=false):
  Læs prompt: config/prompts/wiki_editor.md
  Udfyld: language = Dansk, problems = [...], suggestions = [...]
  Reskriv udkastet → gem som endelig version.
  Hvis approved=true i Pass 2: gem udkastet direkte.
```

- [ ] **Step 9.1: Opret policies/-mappe**

  Skriv `juraklar/testamente/policies/.gitkeep`.

- [ ] **Step 9.2: Generer `policies/arvelovens-rammer.md` (3 pas)**

  **Kilde:** `raw/arveloven.md` — fokus på § 1–§ 14 (arveklasser, ægtefælle) og § 5 (tvangsarv).
  **Prompt:** `wiki_summary_policies.md` med `object_type=policies, language=Dansk`

  Pass 1 — Writer: Skriv udkast med sektioner:
  - **Resumé:** Hvad loven bestemmer om arv og testamentarisk frikvote
  - **Vigtige Emner:** Legal arvefølge, tvangsarv (§ 5 stk. 1–2), frikvote, arveklasser 1-3
  - **Detaljer:**
    - `### Arveklasser` — 1. klasse (livsarvinger), 2. klasse (forældre/søskende), 3. klasse (bedsteforældre/onkler/tanter)
    - `### Tvangsarv` — 1/4 af arven til livsarvinger kan ikke fratages dem
    - `### Frikvote` — de resterende 3/4 kan testamenteres frit
    - `### Ægtefælles arveret` — uskiftet bo, legale arveandele
  - **Relaterede Temaer:** `[Tvangsarv](../themes/Tvangsarv.md)`, `[Legal Arvefølge](../themes/Legal Arvefølge.md)`

  Pass 2 — Evaluator: Anvend `wiki_evaluate_policies.md`. Returnerer JSON.

  Pass 3 — Editor: Anvend `wiki_editor.md` hvis `approved=false`.

  Gem færdigt resultat som `juraklar/testamente/policies/arvelovens-rammer.md`.

- [ ] **Step 9.3: Generer `policies/formkrav.md` (3 pas)**

  **Kilde:** `raw/arveloven.md` §§ 63–74 + `raw/bekendtgoerelse-notarer.md`
  **Prompt:** `wiki_summary_policies.md` med `object_type=policies, language=Dansk`

  Pass 1 — Writer:
  - **Resumé:** Formelle krav til et gyldigt testamente i Danmark
  - **Vigtige Emner:** Notartestamente, vidnetestamente, nødtestamente, ugyldighedsgrunde
  - **Detaljer:**
    - `### Notartestamente (§ 67–§ 70)` — procedure, fordele, krav
    - `### Vidnetestamente (§ 63–§ 66)` — to vidner, inhabilitetsregler for vidner
    - `### Nødtestamente (§ 71–§ 73)` — mundtligt eller egenhændigt, tidsbegrænsning 3 måneder
    - `### Ugyldighedsgrunde (§ 74)` — hvad ugyldiggør et testamente
  - **Relaterede Temaer:** `[Notartestamente](../themes/Notartestamente.md)`, `[Vidnetestamente](../themes/Vidnetestamente.md)`, `[Testamentarisk Habilitet](../themes/Testamentarisk Habilitet.md)`

  Pass 2 og 3 som beskrevet ovenfor.

  Gem som `juraklar/testamente/policies/formkrav.md`.

- [ ] **Step 9.4: Opret articles/-mappe**

  Skriv `juraklar/testamente/articles/.gitkeep`.

- [ ] **Step 9.5: Generer `articles/hvad-er-et-testamente.md` (3 pas)**

  **Kilde:** `raw/advokatraad-testamente.md` + `raw/juridisk-laerebogsudtog.md`
  **Prompt:** `wiki_summary_articles.md` med `object_type=articles, language=Dansk`

  Pass 1 — Writer:
  - **Resumé:** Hvad et testamente er, og hvornår det er nødvendigt for borgere
  - **Vigtige Emner:** Definition, hvornår er det nødvendigt, hvad kan bestemmes, hvad KAN IKKE bestemmes
  - **Detaljer:**
    - `### Hvad er et testamente?` — juridisk definition
    - `### Hvornår er et testamente nødvendigt?` — samlevere (ingen legal arveret), blandede familier, velgørenhed
    - `### Hvad KAN bestemmes` — pengegaver, ejendom, særeje, velgørenhed
    - `### Hvad KAN IKKE bestemmes` — tvangsarv fratages, ulovlige bestemmelser
  - **Relaterede Temaer:** `[Legal Arvefølge](../themes/Legal Arvefølge.md)`, `[Tvangsarv](../themes/Tvangsarv.md)`

  Pass 2 og 3 som beskrevet ovenfor.

  Gem som `juraklar/testamente/articles/hvad-er-et-testamente.md`.

- [ ] **Step 9.6: Generer `articles/typer-af-testamenter.md` (3 pas)**

  **Kilde:** `raw/arveloven.md` §§ 63–73 + `raw/domstolsstyrelsen-vejledning.md`
  **Prompt:** `wiki_summary_articles.md` med `object_type=articles, language=Dansk`

  Pass 1 — Writer:
  - **Resumé:** De tre typer testamenter i dansk ret og deres forskelle
  - **Vigtige Emner:** Notartestamente, vidnetestamente, nødtestamente
  - **Detaljer:**
    - `### Notartestamente` — procedure hos notar, stærkest retssikkerhed, pris ca. 300–500 kr.
    - `### Vidnetestamente` — to voksne inhabile vidner, skriftligt og underskrevet i vidnernes nærvær
    - `### Nødtestamente` — kan oprettes mundtligt ved livsnød, bortfalder automatisk efter 3 måneder
  - **Relaterede Temaer:** `[Notartestamente](../themes/Notartestamente.md)`, `[Vidnetestamente](../themes/Vidnetestamente.md)`, `[Centralregisteret For Testamenter](../themes/Centralregisteret For Testamenter.md)`

  Gem som `juraklar/testamente/articles/typer-af-testamenter.md`.

- [ ] **Step 9.7: Generer `articles/hvem-kan-arve.md` (3 pas)**

  **Kilde:** `raw/arveloven.md` §§ 1–14 + `raw/juridisk-laerebogsudtog.md`
  **Prompt:** `wiki_summary_articles.md` med `object_type=articles, language=Dansk`

  Pass 1 — Writer:
  - **Resumé:** Hvem der arver uden testamente, og hvem der kræver testamente for at arve
  - **Vigtige Emner:** Arveklasser, samlevers manglende arveret, adopterede børn, statens arveret
  - **Detaljer:**
    - `### 1. arveklasse` — børn og børnebørn (livsarvinger)
    - `### 2. arveklasse` — forældre og søskende
    - `### 3. arveklasse` — bedsteforældre, onkler og tanter
    - `### Samlevere` — ingen legal arveret — kræver testamente
    - `### Børn fra flere forhold` — ligestillet med øvrige børn (§ 1)
    - `### Adopterede børn` — ligestillet med biologiske børn
    - `### Staten arver` — hvis ingen arvinger i de tre klasser
  - **Relaterede Temaer:** `[Legal Arvefølge](../themes/Legal Arvefølge.md)`, `[Tvangsarv](../themes/Tvangsarv.md)`

  Gem som `juraklar/testamente/articles/hvem-kan-arve.md`.

- [ ] **Step 9.8: Generer `articles/oprettelse-trin-for-trin.md` (3 pas)**

  **Kilde:** `raw/domstolsstyrelsen-vejledning.md` + `raw/centralregistret-for-testamenter.md` + `raw/bekendtgoerelse-notarer.md`
  **Prompt:** `wiki_summary_articles.md` med `object_type=articles, language=Dansk`

  Pass 1 — Writer:
  - **Resumé:** Praktisk guide til at oprette et notartestamente i Danmark
  - **Vigtige Emner:** Book notartime, medbring, bekræftelse, registrering, opbevaring, opdatering
  - **Detaljer:**
    - `### Trin 1: Vælg type` — notartestamente anbefales (stærkeste retssikkerhed)
    - `### Trin 2: Book notartime` — hvilken byret, online booking eller telefon
    - `### Trin 3: Medbring til notaren` — gyldig legitimation, evt. udkast til testamente
    - `### Trin 4: Notarbekræftelse` — notaren bekræfter identitet og habilitet
    - `### Trin 5: Registrering i Centralregisteret` — automatisk eller på eget initiativ, gebyr
    - `### Trin 6: Opbevaring` — originalen hos dig eller din advokat
    - `### Trin 7: Opdater ved livsændringer` — nyt ægteskab, skilsmisse, børn, nye ejendomme
  - **Relaterede Temaer:** `[Notartestamente](../themes/Notartestamente.md)`, `[Centralregisteret For Testamenter](../themes/Centralregisteret For Testamenter.md)`

  Gem som `juraklar/testamente/articles/oprettelse-trin-for-trin.md`.

- [ ] **Step 9.9: Generer `articles/typiske-fejl.md` (3 pas)**

  **Kilde:** `raw/arveloven.md` §§ 74–80 + `raw/juridisk-laerebogsudtog.md` + `raw/advokatraad-testamente.md`
  **Prompt:** `wiki_summary_articles.md` med `object_type=articles, language=Dansk`

  Pass 1 — Writer:
  - **Resumé:** Fejl der gør et testamente ugyldigt eller anfægteligt
  - **Vigtige Emner:** Inhabile vidner, manglende habilitet, tvangsarvsovertrædelse, tvetydighed, forældet testamente
  - **Detaljer:**
    - `### Inhabile vidner` — ægtefælle, livsarvinger eller kreditorer må ikke være vidner (§ 65)
    - `### Testator mangler habilitet` — under 18 år, eller ikke i stand til fornuftig viljestilkendegivelse (§ 64)
    - `### Tvangsarv fratages` — bestemmelser der fratager livsarvinger tvangsarven er ugyldige (§ 5)
    - `### Tvetydige formuleringer` — uklare betingelser kan ugyldiggøre bestemmelsen
    - `### Forældet testamente` — nyt ægteskab medfører som udgangspunkt at gammelt testamente bortfalder (§ 77)
    - `### Vidnetestamente uden vidner` — begge vidner skal være til stede ved underskrift
  - **Relaterede Temaer:** `[Testamentarisk Habilitet](../themes/Testamentarisk Habilitet.md)`, `[Vidnetestamente](../themes/Vidnetestamente.md)`, `[Tvangsarv](../themes/Tvangsarv.md)`

  Gem som `juraklar/testamente/articles/typiske-fejl.md`.

- [ ] **Step 9.10: Generer `articles/saerlige-situationer.md` (3 pas)**

  **Kilde:** `raw/juridisk-laerebogsudtog.md` + `raw/advokatraad-testamente.md`
  **Prompt:** `wiki_summary_articles.md` med `object_type=articles, language=Dansk`

  Pass 1 — Writer:
  - **Resumé:** Særlige situationer hvor et testamente er særligt vigtigt eller komplekst
  - **Vigtige Emner:** Samlevende, blandede familier, velgørenhed, udlandsejendom, gensidigt testamente
  - **Detaljer:**
    - `### Samlevende uden vielse` — ingen legal arveret → testamente er afgørende
    - `### Blandede familier` — børn fra flere forhold, halvsøskende, stedforældre
    - `### Arv til velgørenhed` — legater til organisationer, fradragsregler
    - `### Ejendom i udlandet` — EU-forordning 650/2012 om international arveret (nævn kort, anbefal advokat)
    - `### Gensidigt testamente` — ægtefæller testamenterer til hinanden, bindende karakter
    - `### Testamentarisk særeje` — arv modtaget som særeje er beskyttet mod bodeling
  - **Relaterede Temaer:** `[Legal Arvefølge](../themes/Legal Arvefølge.md)`, `[Notartestamente](../themes/Notartestamente.md)`

  Gem som `juraklar/testamente/articles/saerlige-situationer.md`.

- [ ] **Step 9.11: Opret notes/-mappe og generer `notes/juridisk-grundbegreber.md` (3 pas)**

  **Kilde:** `raw/juridisk-laerebogsudtog.md`
  **Prompt:** `wiki_summary_notes.md` med `object_type=notes, language=Dansk`

  Pass 1 — Writer:
  - **Resumé:** Juridiske grundbegreber i dansk arveret og testamenteret, til faglig reference
  - **Vigtige Emner:** Testator, legatar, arvelader, arveafkald, gensidigt testamente, særeje
  - **Detaljer:** (faglig præcis tone)
    - `### Centrale begreber` — definitioner af: testator, legatar, arvelader, arveafkald, proklama
    - `### Særlige konstruktioner` — gensidigt testamente, kombinationstestamente, testamentarisk særeje
    - `### Centrale retspraksis-temaer` — habilitetsvurdering, anfægtelse, fortolkning
  - **Relaterede Temaer:** `[Testamentarisk Habilitet](../themes/Testamentarisk Habilitet.md)`, `[Legal Arvefølge](../themes/Legal Arvefølge.md)`

  Gem som `juraklar/testamente/notes/juridisk-grundbegreber.md`.

- [ ] **Step 9.12: Verificer alle 9 sider**

  Læs alle 9 wiki-sider og bekræft at hver har:
  - `# Titel`, `## Resumé`, `## Vigtige Emner`, `## Detaljer`, `## Relaterede Temaer`
  - Mindst ét link i format `[Tema](../themes/Tema.md)`
  - Sprog: dansk

- [ ] **Step 9.13: Commit**

  ```
  git add juraklar/testamente/policies/ juraklar/testamente/articles/ juraklar/testamente/notes/
  git commit -m "feat: generer 9 testamente wiki-sider via AGENTS.md Stage 2"
  ```

  Print: `✓ Stage 2 complete — 9 wiki-sider genereret (2 policies, 6 articles, 1 notes)`

---

## Task 10: Stage 3 — Topics (normalisér nøglebegreber)

**Files:**
- Create: `juraklar/testamente/topics.md`

- [ ] **Step 10.1: Udtræk råtermer fra alle 9 wiki-sider**

  Læs alle sider og saml alle nævnte juridiske termer, fx:
  `notartestamente, vidnetestamente, nødtestamente, tvangsarv, frikvote, legal arvefølge, testamentarisk habilitet, testator, arvelader, legatar, arveafkald, gensidigt testamente, centralregisteret for testamenter, særeje, livsarving`

- [ ] **Step 10.2: Anvend wiki_topics_normalize.md logik**

  Læs `config/prompts/wiki_topics_normalize.md`.
  Normaliser råtermerne til kanoniske former (Title Case, merge synonymer):

  ```json
  {
    "notartestamente": "Notartestamente",
    "vidnetestamente": "Vidnetestamente",
    "nødtestamente": "Nødtestamente",
    "tvangsarv": "Tvangsarv",
    "frikvote": "Frikvote",
    "legal arvefølge": "Legal Arvefølge",
    "lovbestemt arvefølge": "Legal Arvefølge",
    "testamentarisk habilitet": "Testamentarisk Habilitet",
    "testationsevne": "Testamentarisk Habilitet",
    "testator": "Testator",
    "arvelader": "Testator",
    "legatar": "Legatar",
    "arveafkald": "Arveafkald",
    "gensidigt testamente": "Gensidigt Testamente",
    "indbyrdes testamente": "Gensidigt Testamente",
    "centralregisteret": "Centralregisteret For Testamenter",
    "testamentsregisteret": "Centralregisteret For Testamenter",
    "særeje": "Testamentarisk Særeje"
  }
  ```

- [ ] **Step 10.3: Skriv topics.md**

  ```markdown
  # Emneindeks — Testamente

  ## Notartestamente
  Aliaser: notarbekræftet testamente
  Sider: [typer-af-testamenter](articles/typer-af-testamenter.md), [oprettelse-trin-for-trin](articles/oprettelse-trin-for-trin.md), [formkrav](policies/formkrav.md)

  ## Vidnetestamente
  Aliaser: —
  Sider: [typer-af-testamenter](articles/typer-af-testamenter.md), [formkrav](policies/formkrav.md), [typiske-fejl](articles/typiske-fejl.md)

  ## Nødtestamente
  Aliaser: —
  Sider: [typer-af-testamenter](articles/typer-af-testamenter.md), [formkrav](policies/formkrav.md)

  ## Tvangsarv
  Aliaser: tvangsarvekrav
  Sider: [arvelovens-rammer](policies/arvelovens-rammer.md), [hvem-kan-arve](articles/hvem-kan-arve.md), [typiske-fejl](articles/typiske-fejl.md)

  ## Legal Arvefølge
  Aliaser: lovbestemt arvefølge
  Sider: [arvelovens-rammer](policies/arvelovens-rammer.md), [hvem-kan-arve](articles/hvem-kan-arve.md)

  ## Testamentarisk Habilitet
  Aliaser: testationsevne
  Sider: [formkrav](policies/formkrav.md), [typiske-fejl](articles/typiske-fejl.md), [juridisk-grundbegreber](notes/juridisk-grundbegreber.md)

  ## Centralregisteret For Testamenter
  Aliaser: testamentsregisteret
  Sider: [oprettelse-trin-for-trin](articles/oprettelse-trin-for-trin.md)

  ## Gensidigt Testamente
  Aliaser: indbyrdes testamente
  Sider: [saerlige-situationer](articles/saerlige-situationer.md), [juridisk-grundbegreber](notes/juridisk-grundbegreber.md)

  ## Frikvote
  Aliaser: den frie del
  Sider: [arvelovens-rammer](policies/arvelovens-rammer.md)
  ```

  Gem som `juraklar/testamente/topics.md`.

- [ ] **Step 10.4: Commit**

  ```
  git add juraklar/testamente/topics.md
  git commit -m "feat: opret topics.md taxonomi for testamente-wiki"
  ```

  Print: `✓ Stage 3 complete — topics.md med 9 normaliserede nøglebegreber`

---

## Task 11: Stage 4 — Groups / Themes (tematiske oversigts-sider)

**Files:**
- Create: `juraklar/testamente/themes/Tvangsarv.md`
- Create: `juraklar/testamente/themes/Notartestamente.md`
- Create: `juraklar/testamente/themes/Vidnetestamente.md`
- Create: `juraklar/testamente/themes/Testamentarisk Habilitet.md`
- Create: `juraklar/testamente/themes/Legal Arvefølge.md`
- Create: `juraklar/testamente/themes/Centralregisteret For Testamenter.md`

**Prompt der bruges:** `config/prompts/wiki_agent_create_theme.md`
  - Udfyld: `language=Dansk`, `term={temaets navn}`, `links={liste af relaterede sider}`
  - Sektioner: `# {term}`, `## Overblik` (2–3 sætninger), `## Relaterede Sider` (bullet-liste)

- [ ] **Step 11.1: Opret themes/-mappe**

  Skriv `juraklar/testamente/themes/.gitkeep`.

- [ ] **Step 11.2: Generer `themes/Tvangsarv.md`**

  Anvend `wiki_agent_create_theme.md` med:
  - `term = Tvangsarv`
  - `links = arvelovens-rammer, hvem-kan-arve, typiske-fejl`

  ```markdown
  # Tvangsarv

  ## Overblik
  Tvangsarv er den del af arven som livsarvinger (børn og børnebørn) altid har krav på,
  uanset hvad testamentet bestemmer. Tvangsarven udgør 1/4 af den legale arvelod
  og kan ikke fratages ved testamente (Arveloven § 5, stk. 1). Den resterende del
  — frikvoten — kan testamenteres frit.

  ## Relaterede Sider
  - [Arvelovens rammer](../policies/arvelovens-rammer.md)
  - [Hvem kan arve](../articles/hvem-kan-arve.md)
  - [Typiske fejl](../articles/typiske-fejl.md)
  ```

  Gem som `juraklar/testamente/themes/Tvangsarv.md`.

- [ ] **Step 11.3: Generer `themes/Notartestamente.md`**

  ```markdown
  # Notartestamente

  ## Overblik
  Et notartestamente er oprettet for og bekræftet af en notar ved en dansk byret.
  Det er den mest retssikre form for testamente, da notaren verificerer testators
  identitet og habilitet. Notartestamenter registreres automatisk i Centralregisteret
  for Testamenter.

  ## Relaterede Sider
  - [Typer af testamenter](../articles/typer-af-testamenter.md)
  - [Oprettelse trin for trin](../articles/oprettelse-trin-for-trin.md)
  - [Formkrav](../policies/formkrav.md)
  ```

  Gem som `juraklar/testamente/themes/Notartestamente.md`.

- [ ] **Step 11.4: Generer `themes/Vidnetestamente.md`**

  ```markdown
  # Vidnetestamente

  ## Overblik
  Et vidnetestamente kræver to habile, voksne vidner som er til stede når testator
  underskriver. Vidnerne må ikke selv arve efter testamentet og ikke være i nær familie
  med testator (Arveloven § 65). Vidnetestamenter registreres ikke automatisk og er
  mere sårbare over for anfægtelse end notartestamenter.

  ## Relaterede Sider
  - [Typer af testamenter](../articles/typer-af-testamenter.md)
  - [Formkrav](../policies/formkrav.md)
  - [Typiske fejl](../articles/typiske-fejl.md)
  ```

  Gem som `juraklar/testamente/themes/Vidnetestamente.md`.

- [ ] **Step 11.5: Generer `themes/Testamentarisk Habilitet.md`**

  ```markdown
  # Testamentarisk Habilitet

  ## Overblik
  Testamentarisk habilitet er betingelsen om at testator skal være myndig (mindst 18 år)
  og i stand til fornuftsmæssig viljestilkendegivelse på tidspunktet for testamentets
  oprettelse (Arveloven § 64). Manglende habilitet — fx på grund af demens eller
  alvorlig psykisk sygdom — gør testamentet anfægteligt.

  ## Relaterede Sider
  - [Formkrav](../policies/formkrav.md)
  - [Typiske fejl](../articles/typiske-fejl.md)
  - [Juridisk grundbegreber](../notes/juridisk-grundbegreber.md)
  ```

  Gem som `juraklar/testamente/themes/Testamentarisk Habilitet.md`.

- [ ] **Step 11.6: Generer `themes/Legal Arvefølge.md`**

  ```markdown
  # Legal Arvefølge

  ## Overblik
  Den legale arvefølge er den lovbestemte fordeling af arv når der ikke er oprettet et
  testamente. Arven fordeles efter tre arveklasser: 1. klasse (livsarvinger), 2. klasse
  (forældre og søskende), 3. klasse (bedsteforældre og disses efterkommere).
  Samlevere er ikke omfattet og arver intet uden testamente.

  ## Relaterede Sider
  - [Arvelovens rammer](../policies/arvelovens-rammer.md)
  - [Hvem kan arve](../articles/hvem-kan-arve.md)
  - [Hvad er et testamente](../articles/hvad-er-et-testamente.md)
  ```

  Gem som `juraklar/testamente/themes/Legal Arvefølge.md`.

- [ ] **Step 11.7: Generer `themes/Centralregisteret For Testamenter.md`**

  ```markdown
  # Centralregisteret For Testamenter

  ## Overblik
  Centralregisteret for Testamenter er et statsligt register under Tinglysningsretten
  hvor testamenter kan anmeldes. Registrering sikrer at testamentet kan findes ved
  dødsfald. Notartestamenter registreres automatisk; vidnetestamenter kan anmeldes
  frivilligt mod et gebyr.

  ## Relaterede Sider
  - [Oprettelse trin for trin](../articles/oprettelse-trin-for-trin.md)
  - [Typer af testamenter](../articles/typer-af-testamenter.md)
  ```

  Gem som `juraklar/testamente/themes/Centralregisteret For Testamenter.md`.

- [ ] **Step 11.8: Commit**

  ```
  git add juraklar/testamente/themes/
  git commit -m "feat: opret 6 tema-sider for testamente-wiki"
  ```

  Print: `✓ Stage 4 complete — 6 tema-sider oprettet i themes/`

---

## Task 12: Stage 5 — Index

**Files:**
- Create: `juraklar/testamente/index.md`

- [ ] **Step 12.1: Scan alle .md-filer i output-mappen**

  Scan rekursivt i `juraklar/testamente/` — ekskluder `raw/`, `index.md`, `topics.md`, `lint_report.md`.

- [ ] **Step 12.2: Skriv index.md**

  ```markdown
  # Testamente — Indeks

  ## Lovgivning (policies)
  - [Arvelovens rammer](policies/arvelovens-rammer.md)
  - [Formkrav](policies/formkrav.md)

  ## Vejledninger (articles)
  - [Hvad er et testamente?](articles/hvad-er-et-testamente.md)
  - [Typer af testamenter](articles/typer-af-testamenter.md)
  - [Hvem kan arve?](articles/hvem-kan-arve.md)
  - [Oprettelse trin for trin](articles/oprettelse-trin-for-trin.md)
  - [Typiske fejl](articles/typiske-fejl.md)
  - [Særlige situationer](articles/saerlige-situationer.md)

  ## Faglige noter (notes)
  - [Juridisk grundbegreber](notes/juridisk-grundbegreber.md)

  ## Temaer (themes)
  - [Tvangsarv](themes/Tvangsarv.md)
  - [Notartestamente](themes/Notartestamente.md)
  - [Vidnetestamente](themes/Vidnetestamente.md)
  - [Testamentarisk Habilitet](themes/Testamentarisk%20Habilitet.md)
  - [Legal Arvefølge](themes/Legal%20Arvefølge.md)
  - [Centralregisteret For Testamenter](themes/Centralregisteret%20For%20Testamenter.md)
  ```

  Gem som `juraklar/testamente/index.md`.

- [ ] **Step 12.3: Commit**

  ```
  git add juraklar/testamente/index.md
  git commit -m "feat: opret index.md for testamente-wiki"
  ```

  Print: `✓ Stage 5 complete — index.md med 9 wiki-sider + 6 temaer`

---

## Task 13: Stage 6 — Consolidate

**Files:**
- Modify: wiki-sider ved fund

- [ ] **Step 13.1: Anvend wiki_consolidate_themes.md logik**

  Læs `config/prompts/wiki_consolidate_themes.md`.
  Analyser alle sidetitler og sammenlign semantisk:

  ```
  Titler at sammenligne:
  - "Arvelovens rammer" vs "Hvem kan arve" (begge om arveret?)
  - "Formkrav" vs "Typiske fejl" (begge om gyldighed?)
  - "Typer af testamenter" vs "Oprettelse trin for trin" (begge om notartestamente?)
  ```

  Returner JSON-array for eventuelle semantiske dubletter:
  `[{"canonical": "<bedste titel>", "duplicates": ["<dup1>"]}]`
  Returner `[]` hvis ingen.

- [ ] **Step 13.2: Flet ved behov**

  Hvis overlap > 70% på to sider:
  1. Behold den mere komplette side som primær
  2. Flyt unikt indhold til primær-siden under nyt H3-afsnit
  3. Erstat redundant side med redirect-note: `> Se [Primær Side](../sti/til/primær.md)`
  4. Bed bruger om bekræftelse inden sletning

- [ ] **Step 13.3: Rapporter**

  Print: `✓ Stage 6 complete — [N] semantiske overlap fundet, [M] flettet`

---

## Task 14: Stage 7 — Lint

**Files:**
- Create: `juraklar/testamente/lint_report.md`

- [ ] **Step 14.1: Anvend wiki_lint.md logik**

  Læs `config/prompts/wiki_lint.md`.
  Analyser alle wiki-sider for:
  - Manglende eller ufuldstændige sektioner (Resumé, Vigtige Emner, Detaljer, Relaterede Temaer)
  - Brudte links: `[Tema](../themes/Tema.md)` — eksisterer filen?
  - Orphan-sider: sider der ikke linkes fra nogen anden side
  - Sider der mangler `## Relaterede Temaer` med mindst ét tema-link

- [ ] **Step 14.2: Skriv lint_report.md**

  ```markdown
  # Lint-rapport — Testamente-wiki

  Dato: 2026-05-24

  ## Brudte links
  [ingen | liste af brudte tema-links med sideangivelse]

  ## Orphan-sider
  [ingen | sider uden indgående links]

  ## Manglende sektioner
  [ingen | liste: "side.md — mangler ## Resumé"]

  ## Sider uden tema-links
  [ingen | liste af sider uden Relaterede Temaer]

  ## Opsummering
  N brudte links · N orphan-sider · N advarsler
  ```

  Gem som `juraklar/testamente/lint_report.md`.

- [ ] **Step 14.3: Commit**

  ```
  git add juraklar/testamente/lint_report.md
  git commit -m "chore: lint-rapport for testamente-wiki"
  ```

  Print: `✓ Stage 7 complete — N brudte links, N orphans, N advarsler`

---

## Task 15: Stage 8 — Repair

**Files:**
- Modify: wiki-sider med fund fra lint-rapporten

- [ ] **Step 15.1: Ret brudte tema-links**

  For hvert brudt `[Tema](../themes/Tema.md)`:
  - Tjek om temaet eksisterer med anderledes filnavn (store/små bogstaver, mellemrum)
  - Hvis match > 80%: ret link til korrekt filnavn
  - Hvis usikkert: behold linket og tilføj `<!-- TODO: verificer tema-link -->`

- [ ] **Step 15.2: Ret orphan-sider**

  For hver orphan-side:
  - Find den mest tematisk beslægtede wiki-side
  - Tilføj link i dennes `## Relaterede Temaer`-sektion

- [ ] **Step 15.3: Ret manglende sektioner**

  For sider med manglende sektioner:
  - Tilføj den manglende sektion med minimalt indhold
  - Fx manglende `## Relaterede Temaer`: tilføj mindst ét relevant tema-link

- [ ] **Step 15.4: Kør lint igen**

  Genlæs alle sider og verificer at alle fund er rettet.

- [ ] **Step 15.5: Opdater lint_report.md**

  Tilføj:
  ```markdown
  ## Repair-log

  Dato: 2026-05-24
  - [Beskrivelse af hver rettelse]

  Resterende problemer: ingen
  ```

- [ ] **Step 15.6: Final commit**

  ```
  git add juraklar/testamente/
  git commit -m "fix: repair-rettelser af lint-fund i testamente-wiki

  Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"
  ```

  Print: `✓ Stage 8 complete — alle fund rettet. Testamente-wiki er klar.`

---

## Succeskriterier (fra spec)

- [ ] Alle 6 raw-filer eksisterer med komplet frontmatter og `status: gaeldende`
- [ ] Alle 9 wiki-sider er genereret med sektionerne: Resumé, Vigtige Emner, Detaljer, Relaterede Temaer
- [ ] Alle tema-links bruger formatet `[Tema](../themes/Tema.md)` — ikke `[[wikilink]]`
- [ ] 6 tema-sider i `themes/` er oprettet via `wiki_agent_create_theme.md`-logik
- [ ] `lint_report.md` viser 0 brudte links og 0 manglende sektioner
- [ ] Alt indhold er på dansk med borgertilgængeligt sprog
- [ ] Lovhenvisninger er i format: *(Arveloven § X, stk. Y)*
