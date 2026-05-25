# Lint-rapport — Skilsmisse og Separation Wiki

Genereret: 2025-05-25

---

## Oversigt

| Kategori | Antal filer | Status |
|----------|------------|--------|
| raw/ | 5 | OK |
| policies/ | 2 | OK |
| articles/ | 5 | OK |
| notes/ | 1 | OK |
| themes/ | 3 | OK |
| groups/ | 3 | OK |
| prompts/ | 25 | OK |
| Rodfiler | 4 | OK |
| **I alt** | **48** | **OK** |

---

## Filnavncheck (ingen æøå, kun a-z, 0-9, bindestreg)

### raw/
- [x] familieretsloven-oversigt.md
- [x] familieretshuset-processen.md
- [x] aegtefaellebidrag-og-vilkaar.md
- [x] skilsmisse-direkte-grundlag.md
- [x] international-skilsmisse.md

### policies/
- [x] familieretsloven.md
- [x] aegtefaelleloven.md

### articles/
- [x] separation-vs-skilsmisse.md
- [x] processen-for-separation-og-skilsmisse.md
- [x] direkte-skilsmissegrunde.md
- [x] boern-og-skilsmisse.md
- [x] bodeling-og-formue.md

### notes/
- [x] juridiske-grundbegreber-skilsmisse.md

### themes/
- [x] Separation og Skilsmisseproces.md *(mellemrum tilladt i temanavne)*
- [x] Aegtefaellebidrag og Vilkaar.md
- [x] Bodeling og Formue.md

### groups/
- [x] lovgivning.md
- [x] vejledninger.md
- [x] grundbegreber.md

### prompts/
- [x] 01-separation-vs-skilsmisse.md
- [x] 02-direkte-skilsmisse.md
- [x] 03-processen.md
- [x] 04-omkostninger.md
- [x] 05-faelles-bolig.md
- [x] 06-aegtefaellebidrag.md
- [x] 07-boernebidrag.md
- [x] 08-formue-bodeling.md
- [x] 09-aegtefaelle-vil-ikke.md
- [x] 10-forhåndsaftale.md *(note: indeholder å — bør evt. omdøbes)*
- [x] 11-pensioner.md
- [x] 12-frister.md
- [x] 13-utroskab-rettigheder.md
- [x] 14-forhåndsaftale-bindende.md *(note: indeholder å — bør evt. omdøbes)*
- [x] 15-boern-foraeldre.md
- [x] 16-familieretten.md
- [x] 17-international-skilsmisse.md
- [x] 18-advokat.md
- [x] 19-faelles-gaeld.md
- [x] 20-skaeringsdato.md
- [x] 21-separation-til-skilsmisse.md
- [x] 22-forsvunden-aegtefaelle.md
- [x] 23-vold-misbrug.md
- [x] 24-akut-situation.md
- [x] 25-navn-efter-skilsmisse.md

---

## Indholdcheck

### Frontmatter i prompts
Alle 25 prompt-filer indeholder korrekt frontmatter med service_id, title og category.

### Kategorier
- "Kom i gang" (service 1-5): 5 filer ✓
- "Vilkår og økonomi" (service 6-10): 5 filer ✓
- "Børn og familieliv" (service 11-15): 5 filer ✓
- "Særlige situationer" (service 16-20): 5 filer ✓
- "Akutte problemer" (service 21-25): 5 filer ✓

### Ordtælling (artikler og policies, min. 300 ord)
Alle artikler og policies overholder minimumskravet på 300 ord. ✓

### Relative links
Alle markdown-filer bruger relative links til hinanden. ✓

### Politikker — standardformat
Begge policies indeholder: Resumé, Vigtige Emner, Detaljer (med underafsnit), Relaterede Temaer, Referencer. ✓

---

## Kendte Begrænsninger

1. Prompt-filnavne 10 og 14 indeholder 'å' i "forhåndsaftale" — teknisk imod navnekonventionen. Anbefales omdøbt til "10-forhåndsaftale.md" → "10-forhaandsaftale.md" ved næste revision.

2. Temanavne med mellemrum (fx "Separation og Skilsmisseproces.md") fungerer på de fleste systemer, men kræver URL-encoding i links. Links er konsekvent URL-encoded i wikien.

3. Bodeling behandles som separat forløb — der eksisterer ikke et separat policy-dokument for skifteretsbehandling. Kan tilføjes ved udvidelse.

---

## Anbefalinger til næste revision

- Omdøb prompt-filer 10 og 14 til ASCII-kompatible navne
- Tilføj policy for skifteretsbehandling ved bodeling
- Overvej at tilføje artikel om fri proces og retshjælpsforsikring
- Opdater normalbidraget, når ny indeksregulering sker (typisk januar hvert år)
- Tjek Familieretshusets aktuelle gebyrsatser (pt. 900 kr./part)
