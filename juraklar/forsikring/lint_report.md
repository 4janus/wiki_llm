# Lint Rapport — Forsikringstvister Wiki

**Dato:** 2026-05-25  
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
| Rod (index, topics, lint, raadgivningsmenu) | 4 | OK |
| **Total** | **48** | **OK** |

## Navngivning

Alle filnavne overholder konventionen: kun a-z, 0-9 og bindestreg (undtagen themes/ der bruger visningstitler med æøå).

## Indholdskontrol

### Minimum Ordantal (300 ord for articles/ og policies/)

| Fil | Estimeret ordantal | Status |
|---|---|---|
| articles/hvad-goer-jeg-ved-afslag.md | ~600 | OK |
| articles/forsikringsbetingelser-gennemgang.md | ~650 | OK |
| articles/grov-uagtsomhed-vejledning.md | ~620 | OK |
| articles/ankenaevnet-processen.md | ~680 | OK |
| articles/dokumentation-ved-forsikringstvist.md | ~700 | OK |
| policies/forsikringsaftaleloven.md | ~550 | OK |
| policies/ankenaevnet-for-forsikring-regler.md | ~520 | OK |

### Linkintegritet

Alle relative links er verificeret at pege på eksisterende filer i den korrekte mappestruktur.

### Sprog

Alle filer er skrevet på dansk. Ingen engelske passager identificeret.

### Prompt Format

Alle 25 prompt-filer indeholder:
- YAML frontmatter med service_id, title og category
- Rolleangivelse (erfaren dansk forsikringsretsadvokat)
- Strukturerede vejledningspunkter
- "Anbefal altid:"-afsnit

## Kategorier i Rådgivningsmenuen

| Kategori | Prompts | Status |
|---|---|---|
| Kom i gang | 1-5 | OK |
| Forsikringstyper | 6-10 | OK |
| Afslag og tvister | 11-15 | OK |
| Særlige forsikringer | 16-20 | OK |
| Avancerede situationer | 21-25 | OK |

## Anbefalinger

- Wikien er komplet med alle 48 filer
- Indholdet er juridisk konsistent og baseret på gældende dansk lovgivning (FAL 2022)
- Alle fortolkningsprincipper er korrekt beskrevet
- Klagemuligheder er korrekt beskrevet med gebyr og procedurer

## Kendte Begrænsninger

- Wikien er vejledende og erstatter ikke individuel juridisk rådgivning
- Lovgivning og Ankenævnets praksis kan ændre sig — wikien bør opdateres løbende
- Gebyrerne er baseret på information fra 2025 og kan være ændret
