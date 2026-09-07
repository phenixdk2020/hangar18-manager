# Visual Designer Manager V3 — 3.0.0-alpha.16

## Scope

Alpha.16 er en målrettet **V1 Mobile Visual Parity**-version.

Alpha.15 løste den strukturelle mobilfejl ved at skifte konverterede V1-sider fra V3's 120-kolonne telefongrid til naturligt vertikalt flow. Mobilvisningen er derfor funktionel igen, men screenshot-sammenligningen mellem V3 og den fungerende V1 viser stadig tydelige visuelle afvigelser.

Alpha.16 ændrer ikke den nye Alpha.15-flowmodel. Den gendanner i stedet den mobile præsentationskontrakt fra V1.

## Visuelle referencepunkter

- Header-identiteten skal være kompakt som V1: mindre logo/brand, normalt cirka to tekstlinjer og uændret fungerende hamburger-menu.
- Forsidens hero skal have V1's mobile højdeprincip på 220 px og må ikke efterfølges af et stort kunstigt grid-tomrum.
- Tagline-blokken skal være sandfarvet (`#c3ae83`) med mørk tekst (`#30382a`) som V1.
- Mobiltypografi følger V1's faktiske clamp-niveauer: body 16 px, H1 32 px, H2 24.8 px og H3 19.2 px.
- Standardknapper følger V1's importerede mobilprincip: 52 px minimumshøjde, 13/24 px padding og afrundet pill-form.
- Bevaring / Formidling / Fællesskab skal være inset-kort med 20 px indholdspadding og 7 px radius, ikke full-bleed sektioner.
- Fællesskab bruger V1's stålgrå baggrund og hvid tekst.
- Køretøjer og materiel, Events, Billedgalleri, medlems- og kontaktsektioner skal bruge den mindre V1-mobile typografiskala.
- Footer skal gå i naturligt vertikalt flow, så Genveje-links vises direkte under Genveje uden stort tomrum, efterfulgt af Foreningen, knapper, divider og copyright.

## Data- og kompatibilitetsregel

Den bevarede V1-layoutmodel bruges read-only som paint-reference for matchende node-id/type. Gemte V3-data omskrives ikke. V3-native sider uden bevaret V1-kilde beholder den normale V3 responsive model.

Header/Footer får samme V1-mobile flowprincip, men Alpha.14's native `details/summary` hamburger-menu bevares uændret.

## Acceptance på test4

Automatiseret QA er release-gate. Den endelige visuelle acceptance-gate er stadig mobilvisningen på test4 sammenlignet med de godkendte V1 screenshots. Alpha.16 må derfor ikke kaldes visuelt færdig alene på baggrund af grøn CI.
