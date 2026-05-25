# Lint-rapport — Forbrugerret (Mangler ved store køb)

**Genereret:** 2026-05-25
**Status:** Godkendt

## Filstruktur

| Mappe | Antal filer | Status |
|---|---|---|
| raw/ | 5 | OK |
| policies/ | 2 | OK |
| articles/ | 5 | OK |
| notes/ | 1 | OK |
| themes/ | 3 | OK |
| groups/ | 3 | OK |
| prompts/ | 25 | OK |
| Rod (index, topics, lint, raadgivning) | 4 | OK |
| **Total** | **48** | **OK** |

## Filnavne

Alle filnavne overholder kravene:
- Kun a–z, 0–9, bindestreg (undtagen themes/ der bruger danske filnavne med mellemrum)
- Ingen store bogstaver (undtagen themes/ filnavne der matcher kravsspecifikationen)
- Ingen specialtegn

## Indhold

### Ordtælling (artikler og policies — min. 300 ord)

| Fil | Estimeret ordantal | Status |
|---|---|---|
| articles/hvad-er-en-mangel.md | ~500 | OK |
| articles/reklamationsprocessen-trin-for-trin.md | ~600 | OK |
| articles/fortrydelsesret-vejledning.md | ~550 | OK |
| articles/forbrugerklagenaevnet-vejledning.md | ~550 | OK |
| articles/haandvaerker-og-tjenesteydelser.md | ~500 | OK |
| policies/koebeloven.md | ~500 | OK |
| policies/lov-om-forbrugeraftaler.md | ~500 | OK |

### Links

Relative links er anvendt konsekvent (ikke absolutte stier). Links er verificeret internt.

### Sprog

Alt indhold er på dansk. Ingen engelske termer uden forklaring.

## Promptfiler (25 stk.)

Alle 25 promptfiler er oprettet med korrekt frontmatter:
- `service_id`: 1–25
- `title`: Dansk titel
- `category`: En af de 5 kategorier

Kategorier anvendt:
- "Kom i gang" (services 1–5)
- "Reklamation og rettigheder" (services 6–10)
- "Specifikke køb" (services 11–15)
- "Processen" (services 16–20)
- "Særlige situationer" (services 21–25)

## Mangler / noter

- Ingen kritiske mangler fundet
- Themes-filer bruger danske navne med mellemrum som specificeret i kravene
- Alle raw-filer dækker deres angivne emner fyldestgørende
