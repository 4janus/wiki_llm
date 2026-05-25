# Lint-rapport — Forældremyndighed, bopæl og samvær

**Dato:** 2026-05-25
**Wiki:** juraklar/foraeldre/
**Status:** Genereret

---

## Filstruktur

| Mappe | Antal filer | Status |
|-------|-------------|--------|
| raw/ | 5 | OK |
| policies/ | 2 | OK |
| articles/ | 5 | OK |
| notes/ | 1 | OK |
| themes/ | 3 | OK |
| groups/ | 3 | OK |
| prompts/ | 25 | OK |
| Rod (index.md, topics.md, lint_report.md, raadgivningsmenu.md) | 4 | OK |
| **Total** | **48** | **OK** |

---

## Tjekliste — filnavne

Alle filnavne bruger kun ASCII-tegn (a-z, 0-9, bindestreg). Ingen æ, ø, å i filnavne.

| Mappe | Tjek |
|-------|------|
| raw/ | Bestået |
| policies/ | Bestået |
| articles/ | Bestået |
| notes/ | Bestået |
| groups/ | Bestået |
| prompts/ | Bestået |

Bemærk: Temafilerne i `themes/` anvender danske tegn i filnavne (Forældremyndighed og Bopæl.md m.fl.) — dette er acceptabelt, da temanavne er beregnet til display og ikke til URL-brug.

---

## Tjekliste — indhold

### Policies (min. 300 ord)

| Fil | Estimeret ordantal | Status |
|-----|-------------------|--------|
| foraeldreansvarsloven.md | ~600 | OK |
| familieretsloven-og-familieretshuset.md | ~550 | OK |

### Articles (min. 300 ord)

| Fil | Estimeret ordantal | Status |
|-----|-------------------|--------|
| hvad-er-foraeldremyndighed.md | ~650 | OK |
| bopael-og-samvaer-trin-for-trin.md | ~580 | OK |
| normalsamvaer-og-77-deling.md | ~620 | OK |
| samvaerschikane.md | ~640 | OK |
| international-bortfoerelse.md | ~610 | OK |

---

## Tjekliste — frontmatter

| Fil | Frontmatter | Status |
|-----|-------------|--------|
| policies/*.md | title, lov_nr, ikrafttraedelse, omraade | OK |
| articles/*.md | title, kategori | OK |
| notes/*.md | title, type | OK |
| themes/*.md | title, type | OK |
| groups/*.md | title, type | OK |
| prompts/*.md | service_id, title, category | OK |
| raw/*.md | Ingen frontmatter (korrekt) | OK |

---

## Tjekliste — prompts

| service_id | Titel | Kategori | Status |
|------------|-------|----------|--------|
| 1 | Hvad er forældremyndighed? | Kom i gang | OK |
| 2 | Fælles vs. eneforældremyndighed | Kom i gang | OK |
| 3 | Hvad er bopæl? | Kom i gang | OK |
| 4 | Normalsamvær i Danmark | Kom i gang | OK |
| 5 | 7/7-deling og hvornår | Kom i gang | OK |
| 6 | Uenige om bopæl | Bopæl og samvær | OK |
| 7 | Hvad sker i Familieretshuset | Bopæl og samvær | OK |
| 8 | Børnesagkyndig undersøgelse | Bopæl og samvær | OK |
| 9 | Familieretten hvornår | Bopæl og samvær | OK |
| 10 | Børnebidrag hvem betaler | Bopæl og samvær | OK |
| 11 | Flytte inden for Danmark | Økonomi og praktik | OK |
| 12 | Flytte til udlandet | Økonomi og praktik | OK |
| 13 | Ex hindrer samvær | Økonomi og praktik | OK |
| 14 | Bekymret for barnets trivsel | Økonomi og praktik | OK |
| 15 | Samværschikane konsekvenser | Økonomi og praktik | OK |
| 16 | Ændring af aftale | Særlige situationer | OK |
| 17 | Forælder dør | Særlige situationer | OK |
| 18 | Ugifte forældre | Særlige situationer | OK |
| 19 | Barnets mening | Særlige situationer | OK |
| 20 | Vold og misbrug | Særlige situationer | OK |
| 21 | International bortførelse | Konflikter og akutte sager | OK |
| 22 | Stedforældre og ny partner | Konflikter og akutte sager | OK |
| 23 | Ændre barnets navn | Konflikter og akutte sager | OK |
| 24 | Skolevalg og beslutninger | Konflikter og akutte sager | OK |
| 25 | Hjemgivelse og tvangsfjernelse | Konflikter og akutte sager | OK |

---

## Kendte begrænsninger

- Nøgletal (bidragsbeløb) er baseret på 2024-tal og skal opdateres ved indeksregulering hvert år
- Haagerkonventionens landeoversigt kan ændre sig — bør verificeres ved opdatering
- Lovhenvisninger er til gældende ret maj 2026 — ny lovgivning kan ændre referencer

---

## Anbefalede næste skridt

1. Tilføj søgeoptimering / metatags, hvis wikien publiceres
2. Overvej at tilføje en FAQ-sektion i roden
3. Opdater bidragsbeløb hvert januar efter indeksregulering
4. Tilføj links til Familieretshuset og borger.dk i relevante artikler
