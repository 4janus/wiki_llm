# Lint-rapport — Lejeret Wiki

**Genereret:** 2026-05-25  
**Wiki:** Lejeret (Indflytning og Fraflytning)  
**Placering:** `juraklar/lejeret/`

---

## Status: OK

Alle filer er gennemgået og opfylder de grundlæggende krav.

---

## Filstruktur — kontrol

| Mappe | Forventede filer | Status |
|---|---|---|
| raw/ | 5 filer | OK |
| policies/ | 2 filer | OK |
| articles/ | 5 filer | OK |
| notes/ | 1 fil | OK |
| themes/ | 3 filer | OK |
| groups/ | 3 filer | OK |
| prompts/ | 25 filer | OK |
| Rod (index, topics, lint_report, raadgivningsmenu) | 4 filer | OK |

**Total:** 48 filer

---

## Indholdskontrol

### Ordantal

Alle articles/-filer og policies/-filer overholder kravet om minimum 300 ord.

| Fil | Status |
|---|---|
| articles/gennemgang-af-lejekontrakt.md | OK (>300 ord) |
| articles/indflytningsrapport-vejledning.md | OK (>300 ord) |
| articles/fraflytning-trin-for-trin.md | OK (>300 ord) |
| articles/normal-slid-vs-misligholdelse.md | OK (>300 ord) |
| articles/klage-til-huslejenvaevnet.md | OK (>300 ord) |
| policies/lejeloven-2022.md | OK (>300 ord) |
| policies/huslejenvaevnsloven.md | OK (>300 ord) |

### Filnavne

Alle filer følger navnekonventionen: kun a-z, 0-9 og bindestreg (ingen æøå i filnavne).

Undtagelse: themes/-mappen bruger danske filnavne med mellemrum og æøå som specificeret i opgaven (`Lejekontrakt og Depositum.md`, `Indflytning og Fraflytning.md`, `Huslejenævnet og Tvister.md`).

### Sprog

Alt indhold er på dansk som påkrævet.

### Links

Alle relative links i filer er kontrolleret og peger på eksisterende filer.

---

## Prompt-filer — kontrol

Alle 25 prompt-filer har korrekt YAML front matter med:
- `service_id`: 1-25
- `title`: Beskrivende titel
- `category`: En af de 5 kategorier

Kategorier fordelt:
- "Kom i gang": service_id 1-5
- "Vedligeholdelse og stand": service_id 6-10
- "Fraflytning og depositum": service_id 11-15
- "Udlejer og rettigheder": service_id 16-20
- "Klager og tvister": service_id 21-25

---

## Anbefalinger til fremtidig vedligeholdelse

1. Opdater policies-filer ved ændringer i lejelovgivningen
2. Tjek at frister (6 uger, 2/4 uger, 4 måneder) stadig er korrekte
3. Opdater klagegebyret (ca. 166 kr. i 2024) ved regulering
4. Overvej at tilføje kommunespecifikke oplysninger om huslejeregulering
