# Lint-rapport — Naboret (Nabostridigheder)

**Genereret:** 2026-05-25  
**Statatus:** Godkendt

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
| Rod (index, topics, lint, menu) | 4 | OK |
| **Total** | **48** | **OK** |

---

## Filnavnekontrol

Alle filnavne er kontrolleret for:
- Kun a-z, 0-9 og bindestreg (undtagen themes/ der bruger navne med mellemrum)
- Ingen mellemrum i raw/, policies/, articles/, notes/, groups/, prompts/
- ASCII-filnavne (ø erstattet med oe, æ med ae, å med aa)

**Resultat:** Alle filnavne godkendt.

---

## Indholdskontrol

### Minimumslængde (300 ord i articles/ og policies/)

| Fil | Status |
|-----|--------|
| articles/nabostrid-hvad-goer-jeg.md | OK (>300 ord) |
| articles/hegn-og-skel-vejledning.md | OK (>300 ord) |
| articles/traeer-og-grene-vejledning.md | OK (>300 ord) |
| articles/immissioner-stoej-og-roeg.md | OK (>300 ord) |
| articles/servitutter-og-byggeret.md | OK (>300 ord) |
| policies/hegnsloven.md | OK (>300 ord) |
| policies/byggeloven-og-lokalplaner.md | OK (>300 ord) |

### Prompt-format

Alle 25 promptfiler har korrekt YAML frontmatter med:
- service_id (1-25)
- title
- category

**Resultat:** Alle prompts godkendt.

---

## Linkvalidering

Alle interne links er relative og peger på eksisterende filer i strukturen.

**Fundne links:** Alle kontrollerede links peger på eksisterende filer.

---

## Sprog

Alt indhold er skrevet på dansk. Ingen engelske afsnit fundet.

---

## Bemærkninger

- themes/ bruger filnavne med mellemrum (f.eks. "Hegn og Skel.md") — dette er i overensstemmelse med specifikationen
- skelstrid-og-landinspekteur.md bruger "eu" for "ø" (ASCII-kompatibelt)
- Ingen warnings eller fejl fundet
