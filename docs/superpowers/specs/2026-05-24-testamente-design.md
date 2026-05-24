# Design: Testamente-wiki

**Dato:** 2026-05-24  
**Projekt:** wiki_llm / juraklar  
**Emne:** Testamente (rådgiver nr. 1 af 20)  
**Sprog:** Dansk  
**Status:** Godkendt

---

## Formål

Bygge en borgervenlig wiki om testamente som fundament for en juridisk rådgivningsagent. Wikien skal dække dansk arveret med udgangspunkt i gældende lovgivning fra retsinformation.dk, suppleret med vejledninger og praksis. Indholdet organiseres som svar på de spørgsmål borgere typisk stiller.

---

## Mappestruktur

```
juraklar/
  testamente/
    raw/                        ← Deep research output (én .md-fil pr. kilde)
      arveloven.md
      centralregistret-for-testamenter.md
      bekendtgoerelse-notarer.md
      advokatraad-testamente.md
      domstolsstyrelsen-vejledning.md
      juridisk-laerebogsudtog.md
    love/                       ← Wiki-output fra AGENTS.md-pipelinen
    vejledninger/
    index.md
    topics.md
    lint_report.md
```

---

## Fase 1: Deep Research (raw/)

### Krav til kildeindsamling

Alle lovkilder hentes fra **retsinformation.dk**. Kun gældende love accepteres — ingen historiske versioner (markeret "historisk" på retsinformation.dk).

Hvert raw-dokument gemmes som struktureret Markdown med følgende format:

```markdown
---
kilde: <navn>
url: <https://...>
hentet: 2026-05-24
type: lovgivning | vejledning | laerebog | praksis
status: gaeldende
---
# <Lovens/vejledningens titel>

<Fuldt indhold — lovtekst, afsnit eller uddrag>
```

### Primære kilder (lovgivning — retsinformation.dk)

| Fil | Indhold |
|-----|---------|
| `arveloven.md` | Arveloven (LBK) — komplet lovtekst, særligt kapitel om testamenter |
| `centralregistret-for-testamenter.md` | Regler om registrering i Centralregisteret for Testamenter (Tinglysningsretten) |
| `bekendtgoerelse-notarer.md` | Bekendtgørelse om notarbekræftelse af testamenter |

### Sekundære kilder (vejledninger og praksis)

| Fil | Indhold |
|-----|---------|
| `advokatraad-testamente.md` | Advokatsamfundets vejledning til borgere om testamente |
| `domstolsstyrelsen-vejledning.md` | Domstolsstyrelsens vejledning om notarforretninger |
| `juridisk-laerebogsudtog.md` | Uddrag fra anerkendte juridiske lærebøger om arve- og skifteret |

---

## Fase 2: Wiki-generering (AGENTS.md-pipeline)

Pipeline køres på raw/-materialet:  
**Read → Generate → Topics → Groups → Index → Consolidate → Lint → Repair**

### AGENTS.md-konfiguration

```
wiki_name: Testamente
input_folder: juraklar/testamente/raw/
output_folder: juraklar/testamente/
entity_types: love, vejledninger, praksis
language: Dansk
```

### Planlagte wiki-sider

Wiki-siderne er organiseret som borgerspørgsmål med juridiske svar:

| Side | Spørgsmål / formål |
|------|--------------------|
| `hvad-er-et-testamente.md` | Hvad er et testamente, og hvornår er det nødvendigt? |
| `typer-af-testamenter.md` | Hvad er forskellen på et notartestamente, vidnetestamente og nødtestamente? |
| `formkrav.md` | Hvad kræves for at et testamente er gyldigt? |
| `arvelovens-rammer.md` | Hvad bestemmer loven — tvangsarv, frikvote, legal arvefølge? |
| `hvem-kan-arve.md` | Hvem kan arve? Samlevere, børn fra flere forhold, fjernere slægt? |
| `oprettelse-trin-for-trin.md` | Hvordan opretter jeg et testamente i praksis — pris, sted, forløb? |
| `typiske-fejl.md` | Hvad gør et testamente ugyldigt? |
| `saerlige-situationer.md` | Særlige situationer: blandede familier, ejendom i udlandet, velgørenhed |

### Tone og sprog

- Borgervenligt dansk — ikke juristsproget
- Juridiske fagtermer forklares ved første brug
- Lovhenvisninger i parentes: *(Arveloven § 5, stk. 2)*
- Neutralt, encyclopædisk — ingen anbefalinger om specifikke advokater

---

## Succeskriterier

1. Alle raw/-filer er hentet fra gældende kilder (ingen historiske love)
2. Hver raw/-fil har komplet frontmatter (kilde, url, dato, type, status)
3. AGENTS.md-pipelinen producerer mindst de 8 planlagte wiki-sider
4. Lint-rapport viser 0 brudte wikilinks og 0 manglende sektioner
5. Alle wiki-sider er skrevet på dansk med borgertilgængeligt sprog

---

## Afgrænsninger (scope)

- **Inkluderet:** Dansk arveret, testamentsoprettelse, formkrav, arvelovens begrænsninger
- **Ikke inkluderet:** International arveret (EU-forordning 650/2012 behandles kun overfladisk), skattemæssige konsekvenser af arv, skifte-processen efter dødsfald
- **Ikke inkluderet:** De øvrige 19 juridiske rådgivningsemner (behandles i separate wikier)
