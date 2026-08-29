# Visual Designer Manager 0.1.46 – status

Dato: 2026-08-29

## Implementeret

- BUG-15: lokal Header/Footer preview er intern overlay og bruger ikke `window.open`.
- BUG-16: manglende Footer-kilde bruger Desktop-reference fra 29-08-2026.
- Canvas starter altid i Fit ved editor-entry/pageshow og breakpointskift.
- Rich-text paragraph/list/link spacing nulstilles deterministisk i både Designer og frontend.
- Theme Shell cutover er fortsat OFF.

## QA-status

Kode-/modelkontrakter dækkes af release-gates. Bruger-QA af Footer Desktop parity afventer. Menu er næste hovedopgave efter Footer PASS.
