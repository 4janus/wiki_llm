# Lint-rapport — Bodelingsaftale (Skilsmisse)

**Genereret:** 2026-05-25  
**Wiki:** juraklar/bodeling/

---

## Oversigt

| Kategori | Antal filer | Status |
|----------|-------------|--------|
| raw/ | 5 | OK |
| policies/ | 2 | OK |
| articles/ | 5 | OK |
| notes/ | 1 | OK |
| themes/ | 3 | OK |
| groups/ | 3 | OK |
| prompts/ | 25 | OK |
| Top-niveau | 4 | OK |
| **Total** | **48** | **OK** |

---

## Filkontrol

### raw/
- [x] `aegtefaelleloven-bodeling.md` — ingen frontmatter, dansk indhold
- [x] `skaeringsdato-og-nettoformue.md` — ingen frontmatter, dansk indhold
- [x] `pensioner-ved-bodeling.md` — ingen frontmatter, dansk indhold
- [x] `vurdering-af-aktiver.md` — ingen frontmatter, dansk indhold
- [x] `skifteretten-ved-uenighed.md` — ingen frontmatter, dansk indhold

### policies/
- [x] `aegtefaelleloven-formueforhold.md` — frontmatter OK, min. 300 ord
- [x] `pensionsregler-ved-bodeling.md` — frontmatter OK, min. 300 ord

### articles/
- [x] `hvad-er-en-bodeling.md` — frontmatter OK, min. 300 ord
- [x] `bodelingsprocessen-trin-for-trin.md` — frontmatter OK, min. 300 ord
- [x] `saereje-og-delingsformue.md` — frontmatter OK, min. 300 ord
- [x] `vurdering-af-aktiver-vejledning.md` — frontmatter OK, min. 300 ord
- [x] `bodeling-ved-doedsfall.md` — frontmatter OK, min. 300 ord

### notes/
- [x] `juridiske-grundbegreber-bodeling.md` — tabelformat, frontmatter OK

### themes/
- [x] `Delingsformue og Skæringsdato.md` — frontmatter OK
- [x] `Pensioner og Kompensation.md` — frontmatter OK
- [x] `Aktivvurdering og Skifteretten.md` — frontmatter OK

### groups/
- [x] `lovgivning.md` — frontmatter OK
- [x] `vejledninger.md` — frontmatter OK
- [x] `grundbegreber.md` — frontmatter OK

### prompts/
- [x] 01–25 alle filer oprettet med korrekt frontmatter (service_id, title, category)
- [x] Kategorier: "Kom i gang" (1-5), "Aktiver og gæld" (6-10), "Særlige aktiver" (11-15), "Processen" (16-20), "Konflikter og tvister" (21-25)

### Top-niveau
- [x] `index.md` — oversigt over alle filer
- [x] `topics.md` — emneoversigt
- [x] `lint_report.md` — denne rapport
- [x] `raadgivningsmenu.md` — menu over alle 25 rådgivningstjenester

---

## Navnekonventioner

- [x] Alle filnavne kun a-z, 0-9 og bindestreg (undtagen themes/ der bruger danske bogstaver med mellemrum jf. specifikation)
- [x] Alle filer er på dansk

## Linkvalidering

- [x] Relative links bruges konsekvent
- [x] Krydsreferencer er korrekte (relative stier fra fil til fil)

## Indholdskontrol

- [x] Alle artikler og politikker er min. 300 ord
- [x] Alle prompts har "Anbefal altid:" sektion
- [x] Alle prompts beskriver en dansk familieretadvokat som persona
- [x] Korrekte lovhenvisninger (Ægtefælleloven lov nr. 548/2017)

---

## Kendte begrænsninger

- Temafilnavne indeholder mellemrum og danske bogstaver — dette er intentionelt jf. specifikationen og fungerer med URL-encoding i links
- Skifteretssagens præcise gebyrer varierer og kan ikke angives præcist

---

*Ingen fejl fundet.*
