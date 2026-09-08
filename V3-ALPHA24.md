# Visual Designer Manager V3 – 3.0.0-alpha.24

## Formål

Alpha.24 er en strukturel mobil-paritetsrettelse baseret på den read-only V1/V3-overdragelse fra 8. september 2026. V1/test2 er facit. Denne release ændrer ikke V1-kilden.

## Verificerede problemer som rettes

1. Header/Footer havde responsive node-ID-regler med minimumshøjder, mens senere mobilnulstilling kun brugte klasse-selectors. ID-reglerne vandt derfor på specificitet.
2. Headeren beholdt 8 px grid-rækker og Alpha.23's interim-mål i stedet for V1-referenceværdierne.
3. Mobilflowet blandede geometry-baserede margins, Section/Container padding, sectionGap og nested 100vw-breakouts. Samme afstand kunne derfor blive lagt på flere niveauer.
4. Major-sektionernes 30/15 px V1-padding blev nulstillet igen af Alpha.20 ancestor-cleanup, fordi selve bandet også blev behandlet som wrapper.
5. Bevaring/Formidling/Fællesskab fik en ekstra indrammet tekstflade inde i et allerede farvet kort.
6. Footerens generelle `min-height:0` kunne ikke slå de genererede ID-minimumshøjder; nested containere fik samtidig footer-padding gentaget.
7. Text-body kunne begynde med et redundant linjeskift/`<br>` umiddelbart efter en separat heading.

## V1 mobilreference

- Header padding: 7 px 11 px
- Logo: 70 px bredde, auto højde
- Headertitel: 17 px, weight 750, line-height 1.15
- Hamburger: 44×44 px, 1 px kant, 6 px radius
- Header → sideindhold: 24 px som mobil standard
- Hero: 155 px referencehøjde
- Tagline: 16 px / 650 / line-height 1.35, padding 12 px 15 px
- Indholdssektion: 30 px top/bund, 15 px sider
- H2: 25 px / 1.18
- Featurekort: 18 px padding / 8 px radius, én samlet kortflade
- Event/Galleri mobilgap: 16 px
- Før Footer: 24 px standard
- Footer: 32 px 15 px 20 px på den ydre footer-surface, ikke på nested containere

## Implementering

### Responsive cascade ownership

For konverterede V1-sider bliver mobile Section/Container-noder natural-flow flex-containere. Gamle geometry-afledte child margins nulstilles; intern elementafstand kommer fra `elementGap`, mens semantic page bands ejer `sectionGap`.

Nested `100vw` + negative side-margin-breakouts fjernes fra parity-passene. Full-width bruger 100% af en parent, som eksplicit er gjort full-width.

### Header

Headerens surface/section/container får `grid-auto-rows:auto`. Hver node får desuden et ID-specifikt mobile reset efter de genererede geometry-regler. Logo/titel/menu får derefter de målte V1-mål.

Alpha.22's normale DOM-menu og `is-open` hamburgercontroller bevares.

### Footer

Footerens ydre surface ejer `32px 15px 20px`. Section/Container padding er 0. Alle Footer-noder resettes med ID-specificitet til natural height, så en genereret desktop/min-height ikke kan overleve på mobil.

### Sider → Sideindstillinger → Afstande

Alpha.23-felterne bevares og suppleres med:

- Afstand efter Header
- Afstand mellem sektioner
- Standard afstand mellem elementer
- Afstand til Footer

Alle fire er responsive pr. Desktop/Laptop/Tablet/Mobil og gemmes i sidens canonical `pageSettings`/versionshistorik.

## Ikke ændret i Alpha.24

- V1 runtime 0.1.93
- Website-menu persistence fra Alpha.21
- Desktop menu render fra Alpha.22
- Page title-problemet på Om/Kontakt ændres ikke i denne release, fordi overdragelsen markerer det som noget der skal verificeres før en konkret rettelse fastlægges.

## Acceptance efter installation

Den endelige visuelle godkendelse skal fortsat udføres på faktiske viewports 390×844 og 430×932. Kontroller Header, hero, tagline, alle hovedsektioner, featurekort, Events/Galleri, sidste element → Footer og Footerens samlede natural height. Desktop 1440×900 og de seks undersider kontrolleres derefter for regression.
