# Visual Designer Manager 0.1.53 status

## BUG-18 – gennemsigtig elementbaggrund

- Designer leaf-card må ikke have hvid paint når canonical transparent-flag er aktivt.
- Tekst/Menu bruger `backgroundTransparent`; Billede bruger `boxTransparent`.
- Nærmeste forælder (Kasse/Sektion) skal kunne ses igennem.
- Selection/hover/resize-chrome bevares.
- Samme v018-core bruges af side-Designer og Global Header/Footer Designer.
- Preview/frontend skal fortsat bruge canonical Rendererens `transparent` paint.
