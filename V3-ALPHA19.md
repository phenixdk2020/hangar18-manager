# Visual Designer Manager V3 — 3.0.0-alpha.19

## Scope

Alpha.19 retter to konkrete fejl efter Alpha.18:

1. Alpha.18's edge-to-edge-regler ramte kun root-noder (`parentId === ''`), mens den faktiske V3-forside har hero, tagline og flere visuelle bands inde i Section/Container-hierarkiet.
2. Den ønskede alfabetiske sortering gjaldt Visual Designer Managers WordPress-adminmenu — ikke element-paletten inde i Designeren.

## Nested Mobile Edge Parity

- Hele den canonical V3-node-model traverseres; mobilreglerne er ikke længere begrænset til root-noder.
- Hero identificeres semantisk som det første brede mobile billede og bliver 100vw/full-bleed.
- Heroens Section/Container-ancestor-chain nulstilles for ekstra mobil-gutter/margin, så wrapperne ikke genindfører luft.
- Tagline med teksten "Bevaring, restaurering og levende formidling ... militærhistorie" bliver et 100vw sandfarvet V1-band med 18 px intern padding.
- Alle Spacer-noder under den konverterede V1-side skjules på mobil; spacing bæres i stedet af de deterministiske V1-gaps.
- Store semantiske sektioner som "Om foreningen", "Køretøjer og materiel", "Events", "Billedgalleri", "Bliv en del af foreningen" og "Kontakt os" får nærmeste Section/Container-band gjort full-width med 18 px intern tekstpadding.
- Bevaring / Formidling / Fællesskab bevares som V1-inset cards med 10 px sidemargin og 14 px mellemrum.
- Header, Alpha.14-menuadfærd og Alpha.17 Eventlist-størrelsesstyring ændres ikke.

## VDM-adminmenu

Efter alle V3-controllere har registreret deres submenuer køres en sortering ved `admin_menu` priority 999.

- Alle synlige punkter under **Visual Designer Manager** sorteres alfabetisk efter deres viste navn.
- Links, capabilities, callbacks og slugs ændres ikke.
- Det betyder også, at punkter fra separate controllere (Visual Designer, Eksport, Tema, Siteindstillinger osv.) kommer med, hvis de er registreret under samme VDM-parent.
- Alpha.18's utilsigtede alfabetiske sortering af element-paletten fjernes igen.

## Acceptance

Automatisk QA validerer build-kontrakten, V1-baseline, PHP/JS-syntaks, retained Alpha.17/18-funktioner, nested semantic selectors og admin-menu sorteringshook. Den visuelle acceptance-gate er stadig test4 på rigtig iPhone: hero til kant, mindre stablet luft, full-width tagline/major bands og uændret fungerende mobilmenu.
