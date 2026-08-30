# Visual Designer Manager 0.1.62 status

## Kopiér side
- Placering: `Visual Designer Manager → Sider`.
- `Kopiér` åbner et lille navnefelt direkte ved den valgte side.
- Nyt sidenavn er obligatorisk.
- Ny side oprettes altid som kladde med nyt WordPress-ID og unik slug.
- WordPress-indhold, parent, menu-order, side-template og featured image kopieres.
- Visual Designer-layout kopieres som kopiens egen v1; kildens historik kopieres ikke.
- Header/Footer-sidevalg kopieres.
- Hjemmeside-status kopieres aldrig.
- Strukturel Designer-digest verificeres; fejl ruller kopien tilbage.

## Header/Footer
- Synlig Admin-status: `Klar`.
- `Klar` er ikke en frysning. Relevante fælles Designer-fejlrettelser og forbedringer skal fortsat ramme Header/Footer og regressionstestes dér.
