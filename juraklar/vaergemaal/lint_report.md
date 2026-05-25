# Lint Report — Værgemål Wiki

**Genereret:** 2026-05-25  
**Status:** Bestået

---

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
| Rodmappe | 4 (index, topics, lint, raadgivning) | OK |
| **Total** | **48** | **OK** |

---

## Filnavne

Alle filnavne er kontrolleret mod kravspecifikationen:
- Kun a-z, 0-9, bindestreg (ingen æøå i filnavne)
- Undtagelse: `themes/` mapper tillader unicode i filnavnet iht. specifikationen

| Fil | Tegn OK | Sprog OK |
|---|---|---|
| raw/vaergemaalsloven-oversigt.md | Ja | Ja |
| raw/betingelser-og-grader.md | Ja | Ja |
| raw/processen-hos-familieretshuset.md | Ja | Ja |
| raw/vaergens-opgaver-og-tilsyn.md | Ja | Ja |
| raw/ophoer-og-aendring.md | Ja | Ja |
| policies/vaergemaalsloven.md | Ja | Ja |
| policies/familieretshuset-og-vaergemaal.md | Ja | Ja |
| articles/hvad-er-et-vaergemaal.md | Ja | Ja |
| articles/processen-trin-for-trin.md | Ja | Ja |
| articles/vaergens-rolle-og-pligter.md | Ja | Ja |
| articles/personens-rettigheder.md | Ja | Ja |
| articles/alternativer-til-vaergemaal.md | Ja | Ja |
| notes/juridiske-grundbegreber-vaergemaal.md | Ja | Ja |
| themes/Betingelser og Processen.md | N/A (unicode tilladt her) | Ja |
| themes/Værgemalets Grader og Omfang.md | N/A (unicode tilladt her) | Ja |
| themes/Tilsyn og Rettigheder.md | N/A (unicode tilladt her) | Ja |
| groups/lovgivning.md | Ja | Ja |
| groups/vejledninger.md | Ja | Ja |
| groups/grundbegreber.md | Ja | Ja |
| prompts/01–25 (25 filer) | Ja | Ja |

---

## Indholdscheck

| Krav | Status |
|---|---|
| Alle filer skrevet på dansk | Bestået |
| Articles min. 300 ord | Bestået |
| Policies min. 300 ord | Bestået |
| Relative links (ikke absolutte) | Bestået |
| Prompts har korrekt frontmatter (service_id, title, category) | Bestået |
| Alle 25 prompts oprettet | Bestået |
| Promptkategorier matcher specifikationen | Bestået |

---

## Links

Alle interne links er relative og peger på eksisterende filer. Ingen brudte links identificeret.

---

## Bemærkninger

- Alle filer er oprettet i henhold til specifikationen
- Indhold baseret udelukkende på den medfølgende research — ingen WebFetch eller WebSearch anvendt
- `raw/` mappe indeholder kun kildedokumenter, ikke prompts (korrekt)
