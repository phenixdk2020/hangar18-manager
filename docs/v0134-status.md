# Visual Designer Manager 0.1.34 – status

Dato: 28. august 2026

## Scope

Ren bugfix-release før videre backlogarbejde.

1. VD-TEXT-SEL-001: Fed/Kursiv/Understregning skal bevare samme selection stabilt.
2. VD-FLOAT-STACK-001: Flydende Knap må ikke skjules, når et normalt element markeres.

## Implementering

- `editor-v0125.js` er eneste autoritative rich-text selection-owner.
- Selection gemmes som logiske tekst-offsets ved pointerdown og anvendes i én formatteringstransaktion.
- Legacy restore-loops i `editor-v0131.js` og `editor-v0132.js` deaktiveres, når v0125 owner er aktiv.
- `editor-v0134.css` fjerner normale node-stacking-contexts i editoren og placerer floating i et særskilt top-lag.
- Canonical Lag/z-index bevares til floating-rækkefølge og frontend.

## QA-gate

- PHP syntax PASS.
- JavaScript syntax PASS.
- Hierarchy/model regression PASS.
- Kildekontrakter for single selection owner og floating top-layer PASS.
- Endelig Firefox interaction-QA udføres af bruger efter release.
