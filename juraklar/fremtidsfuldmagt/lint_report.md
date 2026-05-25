# Lint-rapport — Fremtidsfuldmagt Wiki

Dato: 2026-05-25
Gennemgået af: Automatisk wikigenerering

---

## Oversigt

| Kategori | Antal filer | Status |
|---|---|---|
| raw/ | 5 | OK |
| policies/ | 2 | OK |
| articles/ | 5 | OK |
| notes/ | 1 | OK |
| themes/ | 3 | OK |
| groups/ | 3 | OK |
| prompts/ | 25 | OK |
| Rodmapper (index, topics, lint, menu) | 4 | OK |
| **Total** | **48** | **OK** |

---

## Strukturtjek

### Alle sider har korrekt format
- [x] Alle wiki-sider (policies, articles, notes, themes, groups) følger det obligatoriske format:
  - `# Titel`
  - `## Resumé`
  - `## Vigtige Emner`
  - `## Detaljer` (med underafsnit)
  - `## Relaterede Temaer` / `## Relaterede Sider`
  - `## Referencer`

### Alle prompt-filer har korrekt format
- [x] Alle 25 prompt-filer (01-25) har YAML-frontmatter med `service_id`, `title` og `category`
- [x] Alle prompt-filer indeholder rolledefinition, opgavebeskrivelse, struktur, tone og anbefaling om advokat

### Interne links
- [x] index.md linker til alle sider med korrekte relative stier
- [x] URL-encoding anvendt for filnavne med æøå og mellemrum (f.eks. `Ikrafttr%C3%A6delse`, `V%C3%A6rgem%C3%A5l`)
- [x] Temaer krydshenviser til hinanden og til artikler

---

## Indholdsvalidering

### Juridisk korrekthed
- [x] Lovhenvisninger stemmer overens med kildefilerne (lov nr. 618/2016, bkg. nr. 1018/2017)
- [x] Gebyrer er korrekte: notarvedståelse 300 kr., aktivering 1.475 kr.
- [x] Frister er korrekte: notarvedståelse inden 6 måneder fra digital oprettelse
- [x] Aldersgrænser er korrekte: min. 18 år for fuldmagtsgiver og fuldmagtshaver
- [x] Rolledefinitioner er korrekte: Familieretshuset (aktivering + tilsyn), Tinglysningsretten (register)

### Dækning
- [x] Alle centrale emner fra researchen er dækket:
  - Hvad er en fremtidsfuldmagt
  - Oprettelsesproces (digital + notar)
  - Fuldmagtens rækkevidde (økonomi + personlige anliggender)
  - Krav til fuldmagtshaver
  - Aktiveringsproces (lægeerklæring + Familieretshuset)
  - Tilbagekaldelse
  - Begrænsninger (medicin, testamente)
  - Sammenligning med værgemål
  - Tilsyn (Familieretshuset)

### Sprog
- [x] Alt indhold er på dansk
- [x] Juridiske termer er brugt korrekt
- [x] Teksten er tilgængelig for borgere uden juridisk baggrund

---

## Anbefalede forbedringer (fremtidig opdatering)

1. **Lovændringer**: Følg med i eventuelle ændringer til loven efter 2026 — senest opdatering var bkg. 322/2019
2. **Gebyrjustering**: Gebyrer kan ændres af Domstolsstyrelsen — verificer altid aktuelle satser på domstol.dk
3. **Familieretshusets sagsbehandlingstid**: Verificer om 4-8 uger fortsat er repræsentativt
4. **Online-tjenester**: Verificer at legaldesk.dk og minadvokat.dk stadig er aktive og relevante

---

## Bekræftelse

Alle filer er oprettet og følger wikiens retningslinjer. Wikien er klar til brug som kildemateriale for rådgivningssystemet.
