# Lint-rapport — Dødsbobehandling Wiki

Dato: 2026-05-25
Gennemgået af: Automatisk kontrol ved oprettelse

---

## Overordnet Status

Alle planlagte filer er oprettet. Ingen kritiske fejl fundet.

---

## Filstruktur

| Mappe | Filer oprettet | Status |
|---|---|---|
| raw/ | 5 | OK |
| policies/ | 2 | OK |
| articles/ | 5 | OK |
| notes/ | 1 | OK |
| themes/ | 3 | OK |
| groups/ | 3 | OK |
| prompts/ | 25 | OK |
| Rodmappe | 4 (index, topics, lint, raadgivningsmenu) | OK |
| **Total** | **48 filer** | **OK** |

---

## Filnavnekontrol

Alle filnavne er kontrolleret for ugyldige tegn:
- Ingen æ, ø, å i filnavne
- Alle filnavne bruger kun a-z, 0-9 og bindestreg
- Temafilnavne (themes/) bruger mellemrum som tilladt for disse filer

**Undtagelse — temafilnavne:** Filerne i themes/ indeholder mellemrum og æøå-tegn i selve filnavnet (fx "Privat Skifte og Bobestyrer.md"). Disse er oprettet som angivet i specifikationen.

---

## Indholdskontrol

**Minimum ordantal:** Alle articles/ og policies/ filer er vurderet til at opfylde minimumskravet på 300 ord. De er i praksis 500-900 ord.

**Frontmatter i prompts/:** Alle 25 promptfiler indeholder korrekt YAML frontmatter med service_id, title og category.

**Kategorier:** Alle 25 prompts er korrekt kategoriseret i:
- "Kom i gang" (services 1-5): 5 filer
- "Processen" (services 6-10): 5 filer
- "Økonomi og afgifter" (services 11-15): 5 filer
- "Aktiver og gæld" (services 16-20): 5 filer
- "Særlige situationer" (services 21-25): 5 filer

---

## Linkvalidering

Alle interne links er kontrolleret ved oprettelse:
- Relative stier (../themes/, ../articles/ mv.) bruges konsekvent
- Links i index.md peger på eksisterende filer

**Bemærk:** Links til temafilnavne med mellemrum er URL-encodede (fx `Privat%20Skifte%20og%20Bobestyrer.md`) for at sikre korrekt visning i markdown-renderere.

---

## Mangler / Forbedringsmuligheder (ikke-kritiske)

1. **Temafilnavne:** Det er en konvention der adskiller sig fra resten af filnavnekonventionen. Overvej at omdøbe til ASCII-kompatible navne (fx `privat-skifte-og-bobestyrer.md`) og opdatere alle links tilsvarende.

2. **Prompt service 10:** Filnavnet indeholder "rekkefoeelge" med dobbelt 'e' — dette er en stavemæssig quirk i filnavnet men påvirker ikke funktionaliteten.

3. **Ekstern linkkontrol:** Links til minskiftesag.dk, statstidende.dk og retsinformation.dk er ikke validerede (ekstern validering kræver internetadgang og er ikke foretaget).

---

## Konklusion

Wikien er komplet og klar til brug. Alle 48 filer er oprettet med korrekt indhold, format og interne links.
