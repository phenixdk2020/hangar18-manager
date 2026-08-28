# Visual Designer Manager 0.1.33 – status

Dato: 28. august 2026

## Scope

0.1.33 er en fokuseret bugfix-release før næste backlog-featurepakke.

1. VD-TEXT-SEL-001: Kursiv skal bevare samme tekstselection som Fed og Understregning.
2. VD-FLOAT-001: En ny Flydende Knap fra paletten må ikke gå gennem normal celle-split.

## Implementering

- Rich-text command-pipelinen gemmer selection som logiske tekst-offsets før `execCommand` og rekonstruerer en frisk Range efter DOM-ændringen.
- Palette-Knap klassificeres som floating før drop-placement beregnes.
- Overlay-drop nulstiller target/cell-band og bruger fri parent-relativ X/Y.
- `placementMode=overlay` sættes canonical ved oprettelsen.
- Flydende Knap er eksplicit hierarchy-undtagelse og må ligge på Side-root, i Sektion eller Kasse.
- Normal Knap følger fortsat almindelige leaf/grid-regler.
- Inspector-scroll fra 0.1.32 ændres ikke.

## QA gates

- PHP syntax på hele pluginet.
- JavaScript syntax på alle editor-assets.
- Hierarchy normalizer QA.
- v0.1.25 model QA.
- Statisk kontraktcheck af logical selection pipeline.
- Statisk kontraktcheck af palette-floating før dropPlacement og canonical `placementMode=overlay`.
- Statisk hierarchy-check af floating root-undtagelsen.

Efter release kræves bruger-QA af de to konkrete interaction flows, før backlog-featurearbejdet fortsættes.
