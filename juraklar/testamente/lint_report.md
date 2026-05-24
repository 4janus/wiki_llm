# Lint-rapport — Testamente-wiki

Dato: 2026-05-24

## Brudte links
ingen

## Manglende sektioner
- `articles/hvem-kan-arve.md` — mangler `## Resumé`, `## Vigtige Emner`, `## Detaljer`, `## Relaterede Temaer` (siden er reduceret til redirect efter Stage 6 konsolidering med `policies/arvelovens-rammer.md`)

## Orphan-sider
ingen

## Sider uden tema-links
ingen

## Opsummering
0 brudte links · 4 manglende sektioner · 0 orphans · 0 uden tema-links

---

## Repair-log

Dato: 2026-05-24

### Stage 6 — Consolidate
- **Flettet:** `articles/hvem-kan-arve.md` → `policies/arvelovens-rammer.md` (overlap >70% på arveklasser §§1–3, adoption §4, tvangsarv §5, ægtefælles arveret §§9–11).
  - Kanonisk side opdateret med unikt indhold fra `hvem-kan-arve.md`: samlevende-afsnit, overlevelseskrav (§94), uddybet tvangsarvseksempel.
  - `hvem-kan-arve.md` erstattet med redirect til kanonisk side.
- Øvrige 7 sidepar analyseret — ingen øvrige par med overlap >70%. Beslutning: ingen yderligere fletning.

### Stage 7 — Lint
- 0 brudte links fundet.
- 1 side med manglende sektioner: `hvem-kan-arve.md` (følge af konsolidering).
- 0 orphan-sider.
- 0 sider uden tema-links.

### Stage 8 — Repair
- **Manglende sektioner i `hvem-kan-arve.md`:** Siden er intentionelt en redirect-side efter Stage 6-konsolideringen. For at overholde lint-kravet om de 4 obligatoriske sektioner (`## Resumé`, `## Vigtige Emner`, `## Detaljer`, `## Relaterede Temaer`) er siden udvidet med minimale men korrekte sektioner, der tydeligt peger videre til den kanoniske side `policies/arvelovens-rammer.md`. Tema-links tilføjet: `Legal Arvefølge` og `Tvangsarv`.
