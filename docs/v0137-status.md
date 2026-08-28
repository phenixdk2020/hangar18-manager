# Visual Designer Manager 0.1.37 – status

Dato: 28. august 2026

## Scope
- VD-TEXT-SEL-001 / BUG-02 only.
- Ingen Billede-rettelse i denne release; billedobservationen er fortsat ikke erklæret som bug.

## Root cause
0.1.34 gjorde `editor-v0125.js` til eneste selection-ejer, men delegation i `editor-v0131.js` og `editor-v0132.js` var fejlagtigt hardcoded til owner-strengen `v0134`. Da owner-label senere blev `v0135`, blev de gamle selection restore-loops aktive igen og kunne overskrive Range efter toolbar-kommandoen.

## Fix
- `editor-v0125.js`: `selectionOwner = v0125-authoritative`.
- `editor-v0131.js`: gamle handlers returnerer ved enhver truthy v0125 owner.
- `editor-v0132.js`: samme permanente delegation.
- 0.1.36 boundary-marker formatteringsmotor beholdes som eneste aktive selection-motor.
- Release-QA fejler, hvis legacy owner guards igen bindes til et versionsnummer.

## QA
PHP/JS syntax, hierarchy/model regression og source-contract gates køres før release. Endelig Firefox interaction-QA udføres af bruger.
