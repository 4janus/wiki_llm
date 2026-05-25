# Lint-rapport — Boligkøb Wiki

**Dato:** 2024-01-01  
**Wiki:** juraklar/boligkob  
**Status:** Ingen fejl fundet

## Filstruktur

| Mappe | Filer | Status |
|---|---|---|
| raw/ | 5 filer | OK |
| policies/ | 2 filer | OK |
| articles/ | 5 filer | OK |
| notes/ | 1 fil | OK |
| themes/ | 3 filer | OK |
| groups/ | 3 filer | OK |
| prompts/ | 25 filer | OK |
| Rodmappe | 4 filer (index, topics, lint_report, raadgivningsmenu) | OK |

**Total:** 48 filer

## Linkkontrol

Alle interne markdown-links er kontrolleret. Relative stier er korrekt angivet fra hvert dokuments placering.

| Dokumenttype | Links kontrolleret | Ugyldige links |
|---|---|---|
| policies/ | 4 | 0 |
| articles/ | 12 | 0 |
| notes/ | 6 | 0 |
| themes/ | 15 | 0 |
| groups/ | 9 | 0 |
| index.md | 18 | 0 |

## Indholdskontrol

| Kontrol | Resultat |
|---|---|
| Minimumslængde articles (300 ord) | Alle 5 artikler overstiger 300 ord |
| Minimumslængde policies (300 ord) | Begge policies overstiger 300 ord |
| Prompts service_id 1-25 | Alle 25 service_id'er til stede, ingen dubletter |
| Kategorimarkering i prompts | Alle 25 prompts har korrekt category-felt |
| Frontmatter format i prompts | Alle 25 prompts har korrekt YAML frontmatter |
| Dansk indhold | Alt indhold er på dansk |
| Filnavne (kun a-z, 0-9, bindestreg) | Alle filnavne i raw/, policies/, articles/, notes/, groups/, prompts/ er conforme |
| Temanavne med danske tegn | Tilladt i themes/ og index.md |

## Kategoridækning (prompts)

| Kategori | Service-IDs | Antal |
|---|---|---|
| Kom i gang | 1-5 | 5 |
| Dokumenter og rapporter | 6-10 | 5 |
| Økonomi og gebyrer | 11-15 | 5 |
| Særlige boligtyper | 16-20 | 5 |
| Problemer og konflikter | 21-25 | 5 |

## Konklusioner

Ingen fejl fundet. Wikien er komplet og klar til brug.
