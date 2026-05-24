# Testamente-wiki Implementationsplan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bygge en komplet, borgervenlig dansk wiki om testamente — fra deep research via retsinformation.dk til færdige wiki-sider — ved at følge AGENTS.md-pipelinen.

**Architecture:** To faser: (1) Deep research henter lovgivning og vejledninger fra nettet og gemmer dem som strukturerede Markdown-filer i `raw/`. (2) AGENTS.md-pipelinen (Read → Generate → Topics → Groups → Index → Consolidate → Lint → Repair) transformerer raw-filerne til færdige wiki-sider i `juraklar/testamente/`. Alle operationer sker via fil-værktøjer (Read, Write, Edit, WebFetch) — aldrig Bash til projektkode.

**Tech Stack:** WebFetch (kildeindsamling), Read/Write/Edit (filoperationer), AGENTS.md pipeline (8 stadier), Markdown med YAML frontmatter, Dansk sprog

---

## Filstruktur der oprettes

```
juraklar/testamente/
  raw/
    arveloven.md                         ← Arveloven fra retsinformation.dk
    centralregistret-for-testamenter.md  ← Tinglysningsrettens regler
    bekendtgoerelse-notarer.md           ← BEK om notarbekræftelse
    advokatraad-testamente.md            ← Advokatsamfundets vejledning
    domstolsstyrelsen-vejledning.md      ← Domstolsstyrelsens vejledning
    juridisk-laerebogsudtog.md           ← Uddrag fra juridiske lærebøger
  love/
    arvelovens-rammer.md
    formkrav.md
  vejledninger/
    hvad-er-et-testamente.md
    typer-af-testamenter.md
    hvem-kan-arve.md
    oprettelse-trin-for-trin.md
    typiske-fejl.md
    saerlige-situationer.md
  index.md
  topics.md
  lint_report.md
```

**Frontmatter-standard for alle raw-filer:**
```markdown
---
kilde: <kildens fulde navn>
url: <https://...>
hentet: 2026-05-24
type: lovgivning | vejledning | laerebog | praksis
status: gaeldende
---
```

---

## Task 1: Opsætning — mapper + AGENTS.md CONFIG

**Files:**
- Create: `juraklar/testamente/raw/` (mappe)
- Modify: `AGENTS.md` (CONFIG-blokken)

- [ ] **Step 1.1: Opret mappestruktur**

  Brug Write-værktøjet til at oprette en placeholder-fil der sikrer mappen eksisterer:

  Skriv filen `juraklar/testamente/raw/.gitkeep` med tomt indhold.

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
  entity_types: love, vejledninger, praksis
  language: Dansk
  CONFIG_END
  -->
  ```

- [ ] **Step 1.3: Verificer**

  Læs AGENTS.md og bekræft at CONFIG-blokken indeholder alle 5 felter korrekt udfyldt.

- [ ] **Step 1.4: Commit**

  ```
  git add juraklar/testamente/raw/.gitkeep AGENTS.md
  git commit -m "chore: opsæt testamente-mappestruktur og AGENTS.md config"
  ```

---

## Task 2: Hent Arveloven (primær lovkilde)

**Files:**
- Create: `juraklar/testamente/raw/arveloven.md`

- [ ] **Step 2.1: Find gældende Arvelov på retsinformation.dk**

  Søg på `https://www.retsinformation.dk/eli/lta/2007/515` (Arveloven LBK nr. 515 af 06/06/2007 — men verificer at dette er den nyeste gældende version ved at tjekke om siden er markeret "historisk").

  Tjek alternativt via søgning: `https://www.retsinformation.dk/Search?search=arveloven&document_type=LBK`

  **Krav:** Siden MÅ IKKE være mærket "Historisk" — vælg den nyeste gældende LBK.

- [ ] **Step 2.2: Udtræk lovtekst**

  Hent indholdet af den gældende Arvelov. Fokuser på:
  - Kapitel 1: Slægtninges arveret (§ 1–§ 6)
  - Kapitel 2: Ægtefælles arveret (§ 7–§ 14)
  - Kapitel 3: Testamente (§ 63–§ 97) — **dette kapitel prioriteres**
  - Kapitel 4: Tvangsarv (§ 5, stk. 1–2)

- [ ] **Step 2.3: Skriv filen**

  Gem som `juraklar/testamente/raw/arveloven.md` med denne struktur:

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

  [lovtekst]

  ## Kapitel 2: Ægtefælles arveret (§ 7–§ 14)

  [lovtekst]

  ## Kapitel 3: Om testamenter (§ 63–§ 97)

  ### § 63 — Testatorfrihed og begrænsninger
  [lovtekst]

  ### § 64 — Testamentarisk habilitet
  [lovtekst]

  [fortsæt for alle §§ i kapitel 3]

  ## Kapitel 4: Tvangsarv

  ### § 5 — Tvangsarv og frikvote
  [lovtekst]
  ```

- [ ] **Step 2.4: Verificer**

  Læs `juraklar/testamente/raw/arveloven.md` og bekræft:
  - Frontmatter er komplet (alle 5 felter)
  - `status: gaeldende` (ikke "historisk")
  - Indeholder § 63–§ 97 (testamentkapitlet)
  - Fil er ikke tom

- [ ] **Step 2.5: Commit**

  ```
  git add juraklar/testamente/raw/arveloven.md
  git commit -m "research: hent gældende Arvelov fra retsinformation.dk"
  ```

---

## Task 3: Hent regler om Centralregisteret for Testamenter

**Files:**
- Create: `juraklar/testamente/raw/centralregistret-for-testamenter.md`

- [ ] **Step 3.1: Find regler om registrering**

  Søg på retsinformation.dk og Tinglysningsrettens hjemmeside (`https://tinglysningsretten.dk`) efter:
  - Regler om anmeldelse til Centralregisteret for Testamenter
  - Bekendtgørelse om Centralregisteret for Testamenter

  Tjek URL: `https://www.retsinformation.dk/Search?search=centralregistret+testamenter`

  Find den gældende bekendtgørelse (mærket "Gældende", ikke "Historisk").

- [ ] **Step 3.2: Hent Tinglysningsrettens borgerinformation**

  Hent også fra: `https://tinglysningsretten.dk/testamente/`
  (Domstolsstyrelsens vejledning om oprettelse og registrering)

- [ ] **Step 3.3: Skriv filen**

  Gem som `juraklar/testamente/raw/centralregistret-for-testamenter.md`:

  ```markdown
  ---
  kilde: Centralregisteret for Testamenter — Tinglysningsretten og retsinformation.dk
  url: https://tinglysningsretten.dk/testamente/
  hentet: 2026-05-24
  type: lovgivning
  status: gaeldende
  ---
  # Centralregisteret for Testamenter

  > Regler om anmeldelse og registrering af testamenter i det statslige centrale register.
  > Forvaltes af Tinglysningsretten under Domstolsstyrelsen.

  ## Hvad er Centralregisteret for Testamenter?

  [indhold]

  ## Bekendtgørelsesgrundlag

  [lovhenvisning og regler]

  ## Hvem kan anmelde?

  [indhold]

  ## Sådan anmelder du et testamente

  [trin-for-trin fra Tinglysningsretten]

  ## Gebyrer

  [aktuelle gebyrer]

  ## Hvad registreres?

  [indhold — selve testamentet eller blot oplysning om det]
  ```

- [ ] **Step 3.4: Verificer**

  Læs filen og bekræft: frontmatter komplet, indeholder afsnit om anmeldelsesprocedure, `status: gaeldende`.

- [ ] **Step 3.5: Commit**

  ```
  git add juraklar/testamente/raw/centralregistret-for-testamenter.md
  git commit -m "research: hent regler om Centralregisteret for Testamenter"
  ```

---

## Task 4: Hent bekendtgørelse om notarbekræftelse

**Files:**
- Create: `juraklar/testamente/raw/bekendtgoerelse-notarer.md`

- [ ] **Step 4.1: Find bekendtgørelse om notarer**

  Søg på: `https://www.retsinformation.dk/Search?search=notarbekr%C3%A6ftelse+testamente&document_type=BEK`

  Alternativt søg efter "bekendtgørelse om notarforretninger" eller "retsplejelovens § 16" der regulerer notarvirksomhed.

  **Krav:** Kun gældende bekendtgørelse (ikke historisk).

- [ ] **Step 4.2: Hent Retsplejelovens §§ om notarer**

  Find relevante §§ i Retsplejeloven (LBK) om notarbekræftelse. Tjek:
  `https://www.retsinformation.dk/eli/lta/2021/1835` (Retsplejeloven) eller nyere gældende version.
  Relevante §§ om notarvirksomhed er typisk § 16–§ 16 k.

- [ ] **Step 4.3: Skriv filen**

  Gem som `juraklar/testamente/raw/bekendtgoerelse-notarer.md`:

  ```markdown
  ---
  kilde: Bekendtgørelse om notarbekræftelse + Retsplejeloven §§ om notarer
  url: https://www.retsinformation.dk/[bekendtgørelse-url]
  hentet: 2026-05-24
  type: lovgivning
  status: gaeldende
  ---
  # Notarbekræftelse af testamenter — lovgrundlag

  > Notarbekræftelse reguleres af Retsplejeloven og tilhørende bekendtgørelser.

  ## Retsplejeloven — §§ om notarvirksomhed

  ### § 16 — Notarens opgaver
  [lovtekst]

  [øvrige relevante §§]

  ## Bekendtgørelse om notarforretninger

  ### Krav til notartestamente

  [indhold: hvad skal fremgå, fremmøde, identifikation]

  ### Gebyr for notarbekræftelse

  [aktuelle satser]

  ## Krav til testator ved notarbekræftelse

  [habilitet, fremmøde, regler]
  ```

- [ ] **Step 4.4: Verificer**

  Læs filen: frontmatter komplet, indeholder lovtekst om notarvirksomhed, `status: gaeldende`.

- [ ] **Step 4.5: Commit**

  ```
  git add juraklar/testamente/raw/bekendtgoerelse-notarer.md
  git commit -m "research: hent bekendtgørelse og retsplejelov om notarbekræftelse"
  ```

---

## Task 5: Hent Advokatsamfundets vejledning

**Files:**
- Create: `juraklar/testamente/raw/advokatraad-testamente.md`

- [ ] **Step 5.1: Find vejledning på advokatsamfundet.dk**

  Hent fra: `https://www.advokatsamfundet.dk/for-borgere/find-en-advokat/hvad-kan-en-advokat-hjaelpe-dig-med/arv-og-testamente/`

  Alternativt: `https://www.advokatsamfundet.dk` — søg efter "testamente".

- [ ] **Step 5.2: Find supplerende borgerinformation**

  Hent også fra borger.dk om testamente:
  `https://www.borger.dk/familie-og-boern/doed-og-begravelse/testamente`

- [ ] **Step 5.3: Skriv filen**

  Gem som `juraklar/testamente/raw/advokatraad-testamente.md`:

  ```markdown
  ---
  kilde: Advokatsamfundet + borger.dk
  url: https://www.advokatsamfundet.dk/for-borgere/find-en-advokat/hvad-kan-en-advokat-hjaelpe-dig-med/arv-og-testamente/
  hentet: 2026-05-24
  type: vejledning
  status: gaeldende
  ---
  # Advokatsamfundets vejledning: Testamente

  > Borgerrettet vejledning om oprettelse og brug af testamente.
  > Kilde: Advokatsamfundet og borger.dk

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

  ## Råd fra borger.dk

  [indhold fra borger.dk-siden]
  ```

- [ ] **Step 5.4: Verificer**

  Læs filen: type er `vejledning`, frontmatter komplet, indhold er borgernivå-sprog.

- [ ] **Step 5.5: Commit**

  ```
  git add juraklar/testamente/raw/advokatraad-testamente.md
  git commit -m "research: hent Advokatsamfundet og borger.dk vejledning om testamente"
  ```

---

## Task 6: Hent Domstolsstyrelsens vejledning om notarer

**Files:**
- Create: `juraklar/testamente/raw/domstolsstyrelsen-vejledning.md`

- [ ] **Step 6.1: Hent fra domstol.dk**

  Hent fra: `https://www.domstol.dk/notar/`
  Og: `https://www.domstol.dk/notar/testamente/`

  Kig efter:
  - Hvad en notar gør
  - Sådan bookes en notartime
  - Hvad medbringer man
  - Gebyrer

- [ ] **Step 6.2: Find gebyrbekendtgørelse**

  Søg på retsinformation.dk efter den gældende retsafgiftslov eller gebyrbekendtgørelse for notarforretninger:
  `https://www.retsinformation.dk/Search?search=retsafgift+notar`

- [ ] **Step 6.3: Skriv filen**

  Gem som `juraklar/testamente/raw/domstolsstyrelsen-vejledning.md`:

  ```markdown
  ---
  kilde: Domstolsstyrelsen — domstol.dk
  url: https://www.domstol.dk/notar/testamente/
  hentet: 2026-05-24
  type: vejledning
  status: gaeldende
  ---
  # Domstolsstyrelsens vejledning om notartestamente

  > Officiel vejledning fra Danmarks domstole om brug af notar ved testamenteoprettelse.

  ## Hvad laver en notar?

  [indhold]

  ## Sådan opretter du et notartestamente — trin for trin

  [indhold]

  ## Book en notartime

  [indhold — hvilken ret, hvad koster det, hvad medbringer man]

  ## Gebyrer (gældende takster)

  [indhold fra retsafgiftsloven/bekendtgørelse]

  ## Hvad sker der med testamentet efter notarbekræftelse?

  [registrering, originalopbevaring]
  ```

- [ ] **Step 6.4: Verificer**

  Læs filen: indeholder konkrete trin, `status: gaeldende`, frontmatter komplet.

- [ ] **Step 6.5: Commit**

  ```
  git add juraklar/testamente/raw/domstolsstyrelsen-vejledning.md
  git commit -m "research: hent Domstolsstyrelsens vejledning om notartestamente"
  ```

---

## Task 7: Saml juridisk lærebogsmateriale

**Files:**
- Create: `juraklar/testamente/raw/juridisk-laerebogsudtog.md`

- [ ] **Step 7.1: Find frit tilgængeligt lærebogsmateriale**

  Søg efter frit tilgængeligt materiale om dansk arveret fra:
  - Juridiske fakultetshjemmesider (jura.ku.dk, law.au.dk)
  - Åbne undervisningssider om arveret
  - Retsdogmatiske artikler tilgængeligt online

  Søg f.eks.: `https://jura.ku.dk` → "arveret" eller "testamente"
  Eller Google Scholar-søgning: `arveret testamente Danmark lærebog open access`

  **Fallback hvis intet open-access materiale findes:** Udled de juridiske grundbegreber direkte fra den hentede `arveloven.md` og `juridisk-laerebogsudtog.md` ved at sammenfatte og forklare §§ med juridisk-faglig præcision. Filens `type` sættes da til `praksis` og `kilde` til `Udledt af Arveloven`.

- [ ] **Step 7.2: Hent supplerende retspraksis-oversigt**

  Søg på `https://domsdatabasen.dk` eller `https://www.ugeskriftforretsvæsen.dk` efter:
  - Centrale domme om testamentarisk habilitet
  - Domme om formkrav (hvad ugyldiggør et testamente)
  - Kan nævnes som praksis-reference uden at gengive fulde domme

- [ ] **Step 7.3: Skriv filen**

  Gem som `juraklar/testamente/raw/juridisk-laerebogsudtog.md`:

  ```markdown
  ---
  kilde: Juridisk lærebogsmateriale og retspraksis-oversigt
  url: [primær kilde-URL]
  hentet: 2026-05-24
  type: laerebog
  status: gaeldende
  ---
  # Juridisk lærebogsmateriale: Arveret og testamente

  > Uddrag og sammenfatninger fra frit tilgængeligt juridisk undervisningsmateriale
  > om dansk arveret med fokus på testamente. Suppleret med centrale retspraksis-referencer.

  ## Grundbegreber i dansk arveret

  ### Legal arvefølge
  [indhold — slægt i første, anden og tredje klasse]

  ### Tvangsarv og frikvote
  [indhold — de 1/4 og 3/4 regler, hvem har tvangsarvekrav]

  ### Testators dispositionsret
  [indhold — hvad kan man lovligt bestemme]

  ## Testamentarisk habilitet

  [indhold — krav til testators mentale tilstand, alder (18 år)]

  ## Formkrav — konsekvenser af manglende opfyldelse

  [indhold — hvad gør et testamente ugyldigt]

  ## Centrale retspraksis-referencer

  | Sag | Problemstilling | Udfald |
  |-----|----------------|--------|
  | [Dom] | [hvad handlede sagen om] | [resultat] |

  ## Særlige konstruktioner

  ### Gensidigt testamente
  [indhold]

  ### Kombinationstestamente
  [indhold]

  ### Særeje ved testamente
  [indhold]
  ```

- [ ] **Step 7.4: Verificer**

  Læs filen: indeholder mindst afsnit om tvangsarv, habilitet og formkrav. Frontmatter komplet.

- [ ] **Step 7.5: Commit**

  ```
  git add juraklar/testamente/raw/juridisk-laerebogsudtog.md
  git commit -m "research: saml juridisk lærebogsmateriale og retspraksis om testamente"
  ```

---

## Task 8: Stage 1 — Read (verificer alle raw-filer)

**Files:**
- Read: alle 6 filer i `juraklar/testamente/raw/`

- [ ] **Step 8.1: Læs alle raw-filer og byg dokumentliste**

  Læs alle 6 filer og opret en intern liste:

  ```
  [
    { filename: "arveloven.md", type: "lovgivning", status: "gaeldende", har_frontmatter: ja },
    { filename: "centralregistret-for-testamenter.md", type: "lovgivning", status: "gaeldende", har_frontmatter: ja },
    { filename: "bekendtgoerelse-notarer.md", type: "lovgivning", status: "gaeldende", har_frontmatter: ja },
    { filename: "advokatraad-testamente.md", type: "vejledning", status: "gaeldende", har_frontmatter: ja },
    { filename: "domstolsstyrelsen-vejledning.md", type: "vejledning", status: "gaeldende", har_frontmatter: ja },
    { filename: "juridisk-laerebogsudtog.md", type: "laerebog", status: "gaeldende", har_frontmatter: ja },
  ]
  ```

- [ ] **Step 8.2: Verificer at ingen fil mangler**

  Bekræft at alle 6 filer eksisterer og har:
  - Komplet frontmatter (kilde, url, hentet, type, status)
  - `status: gaeldende` (aldrig "historisk")
  - Ikke-tomt indhold under frontmatter

- [ ] **Step 8.3: Rapporter**

  Print status: `✓ Stage 1 complete — 6 raw-filer læst, alle gældende`

---

## Task 9: Stage 2 — Generate (opret de 8 wiki-sider)

**Files:**
- Create: `juraklar/testamente/love/arvelovens-rammer.md`
- Create: `juraklar/testamente/love/formkrav.md`
- Create: `juraklar/testamente/vejledninger/hvad-er-et-testamente.md`
- Create: `juraklar/testamente/vejledninger/typer-af-testamenter.md`
- Create: `juraklar/testamente/vejledninger/hvem-kan-arve.md`
- Create: `juraklar/testamente/vejledninger/oprettelse-trin-for-trin.md`
- Create: `juraklar/testamente/vejledninger/typiske-fejl.md`
- Create: `juraklar/testamente/vejledninger/saerlige-situationer.md`

Hver wiki-side gennemgår **3-pas-processen** (Writer → Evaluator → Editor) som beskrevet i AGENTS.md Stage 2.

**Wiki-side-skabelon:**
```markdown
# {Titel}

## Resumé
{Et afsnit om hvad siden handler om.}

## Nøglepunkter
- {Bullet-liste med centrale fakta}

## Detaljer
{Uddybet indhold. Brug H3-underoverskrifter. Lovhenvisninger i parentes: (Arveloven § X).}

## Relateret
- [[{Tilknyttet side}]]

## Referencer
- Kilde: {raw-filnavn}
```

- [ ] **Step 9.1: Opret `juraklar/testamente/love/` mappe**

  Skriv `juraklar/testamente/love/.gitkeep` for at oprette mappen.

- [ ] **Step 9.2: Generer `arvelovens-rammer.md` (3 pas)**

  **Pass 1 — Writer:** Skriv et udkast med indhold fra `arveloven.md` om:
  - Legal arvefølge (§ 1–§ 6)
  - Tvangsarv og frikvote (§ 5, stk. 1–2)
  - Ægtefælles arveret (§ 7–§ 14)
  - Hvad en testator kan disponere over inden for arvelovens rammer

  **Pass 2 — Evaluator:** Score 1–5 på Coverage, Clarity, Structure. Hvis score < 4, noter forbedringer.

  **Pass 3 — Editor:** Anvend forbedringer og gem det endelige udkast.

  Gem som `juraklar/testamente/love/arvelovens-rammer.md`.

- [ ] **Step 9.3: Generer `formkrav.md` (3 pas)**

  Indhold fra `arveloven.md` § 63–§ 74 og `bekendtgoerelse-notarer.md`:
  - Krav til vidnetestamente (§ 63–§ 66)
  - Krav til notartestamente (§ 67–§ 70)
  - Nødtestamente (§ 71–§ 73)
  - Hvad ugyldiggør et testamente (§ 74)

  Gem som `juraklar/testamente/love/formkrav.md`.

- [ ] **Step 9.4: Opret `juraklar/testamente/vejledninger/` mappe**

  Skriv `juraklar/testamente/vejledninger/.gitkeep`.

- [ ] **Step 9.5: Generer `hvad-er-et-testamente.md` (3 pas)**

  Indhold fra `advokatraad-testamente.md` og `juridisk-laerebogsudtog.md`:
  - Hvad er et testamente og hvad kan det bestemme?
  - Hvornår er et testamente nødvendigt (fx samlevere, blandede familier)?
  - Hvad kan IKKE bestemmes i et testamente?

  Gem som `juraklar/testamente/vejledninger/hvad-er-et-testamente.md`.

- [ ] **Step 9.6: Generer `typer-af-testamenter.md` (3 pas)**

  Indhold fra `arveloven.md` § 63–§ 73 og `domstolsstyrelsen-vejledning.md`:
  - Notartestamente: procedure, fordele, omkostninger
  - Vidnetestamente: krav til vidner, hvad kan gå galt
  - Nødtestamente: hvornår kan det bruges, tidsbegrænsning

  Gem som `juraklar/testamente/vejledninger/typer-af-testamenter.md`.

- [ ] **Step 9.7: Generer `hvem-kan-arve.md` (3 pas)**

  Indhold fra `arveloven.md` § 1–§ 14 og `juridisk-laerebogsudtog.md`:
  - Arveklasser (1., 2., 3. klasse)
  - Samlevers arveret (ingen legal arveret — kræver testamente)
  - Børn fra flere forhold
  - Adopterede og biologiske børn
  - Hvornår arver staten?

  Gem som `juraklar/testamente/vejledninger/hvem-kan-arve.md`.

- [ ] **Step 9.8: Generer `oprettelse-trin-for-trin.md` (3 pas)**

  Indhold fra `domstolsstyrelsen-vejledning.md`, `centralregistret-for-testamenter.md` og `advokatraad-testamente.md`:
  - Trin 1: Beslut type (notartestamente anbefales)
  - Trin 2: Book notartime (hvilken ret, pris)
  - Trin 3: Hvad medbringer man
  - Trin 4: Notarbekræftelse og registrering i Centralregisteret
  - Trin 5: Opbevaring af originalen
  - Trin 6: Hvornår bør man opdatere testamentet?

  Gem som `juraklar/testamente/vejledninger/oprettelse-trin-for-trin.md`.

- [ ] **Step 9.9: Generer `typiske-fejl.md` (3 pas)**

  Indhold fra `arveloven.md` § 74–§ 80, `juridisk-laerebogsudtog.md` og `advokatraad-testamente.md`:
  - Manglende vidner eller forkerte vidner (inhabile)
  - Testator mangler testamentarisk habilitet
  - Bestemmelser der strider mod tvangsarv
  - Tvetydige formuleringer
  - Forældet testamente efter nyt ægteskab/skilsmisse

  Gem som `juraklar/testamente/vejledninger/typiske-fejl.md`.

- [ ] **Step 9.10: Generer `saerlige-situationer.md` (3 pas)**

  Indhold fra `juridisk-laerebogsudtog.md`, `advokatraad-testamente.md`:
  - Samlevende uden vielse
  - Blandede familier (børn fra tidligere forhold)
  - Arv til velgørenhed
  - Ejendom i udlandet (kort omtale — EU-forordning 650/2012)
  - Gensidigt testamente med ægtefælle
  - Særeje via testamente

  Gem som `juraklar/testamente/vejledninger/saerlige-situationer.md`.

- [ ] **Step 9.11: Verificer alle 8 sider**

  Læs alle 8 wiki-sider og bekræft at hver har: Resumé, Nøglepunkter, Detaljer, Relateret, Referencer.

- [ ] **Step 9.12: Commit**

  ```
  git add juraklar/testamente/love/ juraklar/testamente/vejledninger/
  git commit -m "feat: generer 8 testamente wiki-sider via AGENTS.md Stage 2"
  ```

  Print: `✓ Stage 2 complete — 8 wiki-sider genereret`

---

## Task 10: Stage 3 — Topics (taxonomy)

**Files:**
- Create: `juraklar/testamente/topics.md`

- [ ] **Step 10.1: Udtræk nøglebegreber fra alle 8 wiki-sider**

  Læs alle sider og identificer nøgletermer, f.eks.:
  - Notartestamente, Vidnetestamente, Nødtestamente
  - Tvangsarv, Frikvote, Legal arvefølge
  - Testamentarisk habilitet, Testator
  - Centralregisteret for Testamenter, Tinglysningsretten
  - Arveafkald, Arvelader, Legatar
  - Gensidigt testamente, Særeje

- [ ] **Step 10.2: Normaliser og skriv topics.md**

  ```markdown
  # Emneindeks — Testamente

  ## Notartestamente
  Aliaser: notarbekræftet testamente
  Sider: [[typer-af-testamenter]], [[oprettelse-trin-for-trin]], [[formkrav]]

  ## Vidnetestamente
  Aliaser: —
  Sider: [[typer-af-testamenter]], [[formkrav]], [[typiske-fejl]]

  ## Nødtestamente
  Aliaser: —
  Sider: [[typer-af-testamenter]], [[formkrav]]

  ## Tvangsarv
  Aliaser: tvangsarvekrav, tvangsarving
  Sider: [[arvelovens-rammer]], [[hvem-kan-arve]], [[typiske-fejl]]

  ## Frikvote
  Aliaser: den frie tredjedel
  Sider: [[arvelovens-rammer]]

  ## Legal arvefølge
  Aliaser: lovbestemt arvefølge
  Sider: [[arvelovens-rammer]], [[hvem-kan-arve]]

  ## Testamentarisk habilitet
  Aliaser: testationsevne
  Sider: [[formkrav]], [[typiske-fejl]]

  ## Centralregisteret for Testamenter
  Aliaser: testamentsregisteret
  Sider: [[oprettelse-trin-for-trin]]

  ## Gensidigt testamente
  Aliaser: indbyrdes testamente
  Sider: [[saerlige-situationer]]
  ```

  Gem som `juraklar/testamente/topics.md`.

- [ ] **Step 10.3: Commit**

  ```
  git add juraklar/testamente/topics.md
  git commit -m "feat: opret topics.md taxonomi for testamente-wiki"
  ```

  Print: `✓ Stage 3 complete — topics.md oprettet med nøglebegreber`

---

## Task 11: Stage 4 — Groups (kategori-sider)

**Files:**
- Create: `juraklar/testamente/groups/lovgivning.md`
- Create: `juraklar/testamente/groups/borgervejledning.md`

- [ ] **Step 11.1: Opret groups-mappe og lovgivning.md**

  ```markdown
  # Lovgivning om testamente

  Samling af wiki-sider der beskriver det lovmæssige grundlag for testamente i Danmark.
  Primær kilde: Arveloven og tilhørende bekendtgørelser.

  ## Sider
  - [[arvelovens-rammer]]
  - [[formkrav]]
  ```

  Gem som `juraklar/testamente/groups/lovgivning.md`.

- [ ] **Step 11.2: Opret borgervejledning.md**

  ```markdown
  # Borgervejledning om testamente

  Praktisk orienterede sider for borgere der vil oprette eller forstå et testamente.

  ## Sider
  - [[hvad-er-et-testamente]]
  - [[typer-af-testamenter]]
  - [[hvem-kan-arve]]
  - [[oprettelse-trin-for-trin]]
  - [[typiske-fejl]]
  - [[saerlige-situationer]]
  ```

  Gem som `juraklar/testamente/groups/borgervejledning.md`.

- [ ] **Step 11.3: Commit**

  ```
  git add juraklar/testamente/groups/
  git commit -m "feat: opret gruppe-sider for testamente-wiki"
  ```

  Print: `✓ Stage 4 complete — 2 gruppe-sider oprettet`

---

## Task 12: Stage 5 — Index

**Files:**
- Create: `juraklar/testamente/index.md`

- [ ] **Step 12.1: Scan alle .md-filer i output-mappen**

  Scan rekursivt i `juraklar/testamente/` (ekskluder `raw/`, `index.md`, `topics.md`, `lint_report.md`).

- [ ] **Step 12.2: Skriv index.md**

  ```markdown
  # Testamente — Indeks

  ## Lovgivning
  - [[arvelovens-rammer]]
  - [[formkrav]]

  ## Borgervejledning
  - [[hvad-er-et-testamente]]
  - [[typer-af-testamenter]]
  - [[hvem-kan-arve]]
  - [[oprettelse-trin-for-trin]]
  - [[typiske-fejl]]
  - [[saerlige-situationer]]

  ## Grupper
  - [[lovgivning]]
  - [[borgervejledning]]
  ```

  Gem som `juraklar/testamente/index.md`.

- [ ] **Step 12.3: Commit**

  ```
  git add juraklar/testamente/index.md
  git commit -m "feat: opret index.md for testamente-wiki"
  ```

  Print: `✓ Stage 5 complete — index.md bygget med 8 wiki-sider + 2 grupper`

---

## Task 13: Stage 6 — Consolidate (duplikatkontrol)

**Files:**
- Modify: evt. wiki-sider hvis dubletter opdages

- [ ] **Step 13.1: Tjek for indholdsmæssig overlap**

  Sammenlign parvis:
  - `formkrav.md` vs `typiske-fejl.md` (begge om gyldighed — overlap > 70%?)
  - `arvelovens-rammer.md` vs `hvem-kan-arve.md` (begge om arveklasser — overlap?)
  - `typer-af-testamenter.md` vs `oprettelse-trin-for-trin.md` (begge nævner notartestamente)

- [ ] **Step 13.2: Flet ved behov**

  Hvis overlap > 70% på to sider:
  1. Behold den mest komplette version som primær
  2. Flyt unikt indhold fra den anden til primær-siden under et nyt H3-afsnit
  3. Erstat den redundante side med en redirect-note: `> Se [[primær-side]]`
  4. Opdater alle wikilinks i andre sider

  Bed bruger om bekræftelse inden sletning.

- [ ] **Step 13.3: Rapporter**

  Print resultatet: `✓ Stage 6 complete — [N] overlap fundet, [M] flettet`

---

## Task 14: Stage 7 — Lint

**Files:**
- Create: `juraklar/testamente/lint_report.md`

- [ ] **Step 14.1: Kontroller brudte wikilinks**

  Tjek alle `[[...]]`-links i alle sider: er der en matchende fil?

- [ ] **Step 14.2: Kontroller orphan-sider**

  Tjek om alle 8 wiki-sider linkes fra mindst én anden side.

- [ ] **Step 14.3: Kontroller manglende sektioner**

  Verificer at alle sider har: `## Resumé`, `## Nøglepunkter`, `## Detaljer`, `## Relateret`, `## Referencer`.

- [ ] **Step 14.4: Skriv lint_report.md**

  ```markdown
  # Lint-rapport — Testamente-wiki

  Dato: 2026-05-24

  ## Brudte wikilinks
  [ingen | liste af brudte links]

  ## Orphan-sider
  [ingen | liste af sider uden indgående links]

  ## Manglende sektioner
  [ingen | liste af sider med manglende afsnit]

  ## Opsummering
  N brudte links, N orphan-sider, N advarsler.
  ```

  Gem som `juraklar/testamente/lint_report.md`.

- [ ] **Step 14.5: Commit**

  ```
  git add juraklar/testamente/lint_report.md
  git commit -m "chore: lint-rapport for testamente-wiki"
  ```

  Print: `✓ Stage 7 complete — N brudte links, N orphan-sider, N advarsler`

---

## Task 15: Stage 8 — Repair (ret lint-fund)

**Files:**
- Modify: wiki-sider med fund fra lint-rapporten

- [ ] **Step 15.1: Ret brudte wikilinks**

  For hvert brudt `[[Link]]`:
  - Hvis tydelig match (> 80% sandsynlighed): erstat med korrekt `[[Korrekt Titel]]`
  - Hvis usikkert: erstat med klartekst og tilføj `<!-- TODO: verificer link -->`

- [ ] **Step 15.2: Ret orphan-sider**

  For hver orphan-side:
  - Find den mest tematisk beslægtede eksisterende side
  - Tilføj link til orphan-siden i den sides `## Relateret`-sektion

- [ ] **Step 15.3: Kør lint igen**

  Genlæs alle sider og verificer at alle fund er rettet.

- [ ] **Step 15.4: Opdater lint_report.md**

  Tilføj nederst i filen:

  ```markdown
  ## Repair-kørselslog

  Dato: 2026-05-24
  - [Beskrivelse af rettelser]

  Resterende problemer: [ingen | liste]
  ```

- [ ] **Step 15.5: Final commit**

  ```
  git add juraklar/testamente/
  git commit -m "fix: repair-kørsels rettelser af lint-fund i testamente-wiki"
  ```

  Print: `✓ Stage 8 complete — alle fund rettet. Testamente-wiki er klar.`

---

## Succeskriterier (fra spec)

- [ ] Alle 6 raw-filer eksisterer med komplet frontmatter og `status: gaeldende`
- [ ] Alle 8 planlagte wiki-sider er genereret med alle påkrævede sektioner
- [ ] `lint_report.md` viser 0 brudte wikilinks og 0 manglende sektioner
- [ ] Alt indhold er på dansk med borgertilgængeligt sprog
- [ ] Lovhenvisninger er i format: *(Arveloven § X, stk. Y)*
