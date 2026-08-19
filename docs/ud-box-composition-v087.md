# Ultimate Designer — Kassekomposition v0.8.7

## Mål

Kasse er et generelt Container-element, ikke et specialelement til én bestemt type indhold. En Kasse kan indeholde flere almindelige elementer som Tekst, Billede, Knap, Ikon, Liste og andre understøttede elementer.

Foretrukken struktur for almindeligt responsivt sidelayout:

```text
Auto-kasser / Grid
├── Kasse 1 / Container
│   ├── Billede
│   ├── Tekst
│   └── Knap
└── Kasse 2 / Container
    ├── Tekst
    └── Billede
```

Dette genbruger den eksisterende `LayoutParentKey`-model og den eksisterende rekursive Container/Flex/Grid-renderer.

## Indsæt elementer i en Kasse

- Træk et almindeligt element fra Elementbiblioteket og slip det på en Kasse.
- Alternativt: vælg Kassen og klik derefter på Tekst/Billede/Knap/etc. i Elementbiblioteket.
- Handlingen opretter fortsat elementet gennem den eksisterende editor og sætter derefter den nye rows `LayoutParentKey` til den valgte Kasse.
- Der er ingen grænse på præcis ét child-element; flere direkte children i samme Kasse understøttes.
- Kassen viser editor-only en indholdsoversigt med direkte children og genvej til redigering.

## Indholdslayout pr. Kasse

Kassen bruger sine eksisterende Container-layoutfelter til at placere child-elementerne:

- `LayoutDirection`: lodret eller vandret på desktop.
- `LayoutJustify`: start, center, end eller space-between.
- `LayoutAlign`: start, center, end eller stretch.
- `LayoutWrap`: tillad ombrydning.
- `LayoutGapPx`: intern afstand på desktop.
- `MobileLayoutGapPx`: intern afstand på mobil.
- `MobileLayoutStack`: stak child-elementer lodret på mobil.

Nye Kasser fra v0.8.7-værktøjet får et praktisk indholdsdefault: lodret flow, stretch, start-justering og mobil stacking. Brugeren kan ændre dette pr. Kasse.

Kassens **ydre** placering i en Auto-kasser-række styres fortsat af parent Grid. Kassens **indre** placering af Tekst/Billede/Knap styres af Kassen selv. De to niveauer er derfor adskilt.

## Hvorfor ikke bruge Tabel til layout?

Tabel er for semantiske tabeldata: rækker/kolonner, overskrifter og sammenhørende celler. Tabel bør ikke bruges som erstatning for Kasse/Flex/Grid ved almindeligt sidelayout, fordi responsive ombrydning og elementkomposition håndteres bedre af Container/Grid/Flex.

Tabelværktøjet må stadig kunne være visuelt uden linjer. v0.8.7 tilføjer derfor:

- `data-h18-table-border-width` på det sanitiserede tabelmarkup,
- kantbredde fra 0 til 8 px i editoren,
- `0 px` = helt usynlige celle-/tabelkanter,
- hurtigknap Skjul/Vis kanter,
- eksisterende tabelindhold og semantik bevares.

Hvis WordPress skulle fjerne det ekstra data-attribut under sanitization, kan 0 px stadig genkendes fra den gemte inline border-style ved næste editor-load.

## Arkitektur og sikkerhed

Implementeringen er additiv wp-admin UX:

- `assets/ultimate-designer-nesting-tools.js/css`
- `assets/ultimate-designer-box-content-layout.js/css`
- `assets/ultimate-designer-table-appearance.js/css`

De enqueues kun på `page=hangar18-pages` for brugere med `edit_pages` gennem `EditorLayoutToolsAdminController`.

Der indføres ingen:

- ny page schema-version,
- ny WordPress option/post meta persistence-model,
- frontend hook,
- renderer switch,
- public cutover-handler.

Vehicle/Event/Gallery forbliver på den beskyttede legacy runtime.

## QA

- `v087-nesting-contract.sh` karakteriserer element-til-Kasse nesting via `LayoutParentKey`.
- `v087-box-content-table-contract.sh` karakteriserer flere children, child-layout-kontroller og 0 px tabelkanter.
- Architecture QA kører Node syntax check på alle nye JavaScript-assets.
