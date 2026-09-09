# Visual Designer Manager V3 — 3.0.0-alpha.26

## Formål
Alpha.26 er en målrettet Header/Footer mobilrettelse efter Alpha.25 natural-flow reset. Sideindholdets mobile flow ændres ikke i denne version.

## Header
- Alpha.25 fladede nested Header wrappers ud med `display:contents` for at fjerne gamle grid/min-height problemer.
- Alpha.26 flytter den effektive Header-templatebaggrund til den yderste mobile Header surface, så baggrundsfarven igen males korrekt uden at genindføre faste højder.
- Logo, titel og hamburger beholder Alpha.25 natural flex-row geometri.

## Footer
- Footerens yderste mobile surface maler nu templatebaggrunden helt ud til viewportens kanter.
- `32px 15px 20px` er fortsat indvendig Footer content-padding og ikke en hvid yderramme.
- V1-reference typografi gendannes for brand, beskrivelse, sektionoverskrifter og copyright.
- Copyright bruger 11px på mobil og holdes på én linje, hvor viewporten tillader det.

## Genveje
Footerens `Genveje` er ikke en separat hardcoded linkliste. Den følger altid Visual Designer Managers kanoniske **Website-menu** (`vdm_website_menu_id`).

Det betyder:
- Footer viser de aktuelle punkter fra den valgte Website-menu.
- Rækkefølgen kommer fra WordPress-menuens rækkefølge.
- Hvis Website-menuen ændres, følger Header og Footer med uden at Footer skal redigeres særskilt.
- Footerens særskilte `Bliv medlem` og `Kontakt` knapper er fortsat egne Footer-elementer; de påvirker ikke, hvilke punkter menuen indeholder.

## Regression guards
- V1 0.1.93 er fortsat låst byte-for-byte ved `dc3bad403c764f4ec123a526333a781d05dde491`.
- Alpha.25 natural mobile flow bevares.
- Alpha.24 side spacing/hero/card parity bevares.
- Alpha.22 normal-DOM hamburger-controller og Alpha.21 Website-menu binding bevares.
