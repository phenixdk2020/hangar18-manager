# Ultimate Designer — Elementbibliotek v0.8.7

## Formål

Gøre den eksisterende element-/funktionspalette hurtigere at bruge uden at ændre page schema, frontend-rendering eller den eksisterende drag-and-drop-motor.

## Leverance

- Fritekstsøgning på elementnavn og type.
- Kategorifiltre: Alle, Favoritter, Indhold, Layout, Interaktiv, Dynamisk og Avanceret.
- Browser-lokale favoritter via `localStorage`.
- Synlig tæller for aktuelle søgeresultater.
- Accessible filterknapper med `aria-pressed` og favoritknapper med `aria-pressed`.
- `/` fokuserer søgefeltet, når Elementer-panelet er aktivt og brugeren ikke skriver i et felt.
- Eksisterende `.h18-builder-palette-item`-knapper genbruges uændret til klik og drag/drop.

## Auto-kasser og individuelt kassedesign

v0.8.7 gør Auto-kasser tydeligere i editoren uden at ændre lagringsmodellen. Auto-kasser fortsætter med at bruge eksisterende Grid + Container-felter og `LayoutParentKey`.

- Auto-kasser får en visuel grid-preview i canvas, så kasserne vises ved siden af hinanden i stedet for kun som lodrette editorrækker.
- Antallet af desktop-kolonner følger automatisk antallet af kasser, mens mobil starter med én kolonne.
- `LayoutGapPx` og `MobileLayoutGapPx` styrer spacing mellem kasserne.
- Hver kasse får sit eget designpanel i Inspector.
- Radius kan sættes til 0 px for helt firkantede kasser eller til en valgfri værdi; hvert af de fire hjørner kan også styres separat.
- Baggrund, tekst, overskrift og kantfarve kan indstilles separat pr. kasse via de eksisterende custom design-felter.
- Brødtekstfont, overskriftsfont, brødtekststørrelse og H2-størrelse kan indstilles separat pr. kasse.
- Lodret/vandret padding og kantbredde kan indstilles separat pr. kasse.
- En kasse kan vælges direkte fra grid-previewet for at åbne dens individuelle designkontroller.

Implementeringen ligger i `assets/ultimate-designer-box-tools.js` og `assets/ultimate-designer-box-tools.css`, som enqueues admin-only fra `EditorLayoutToolsAdminController`.

## Arkitektur

`EditorElementLibraryAdminController` enqueuer kun de nye assets på `page=hangar18-pages` for brugere med `edit_pages`. JavaScript-laget filtrerer og grupperer den allerede renderede palette og kalder ingen repository-, AJAX- eller WordPress write-API'er.

`EditorLayoutToolsAdminController` enqueuer tilsvarende layout-, tabel- og kasseværktøjer admin-only. Kasseværktøjet genbruger eksisterende design- og layoutfelter og indfører derfor ingen parallel persistence-model.

Der indføres derfor ingen:

- ny option eller post meta,
- schema-version,
- frontend-hook,
- renderer-switch,
- public cutover-handler.

## UD-020 command palette

Ctrl/Cmd+K command palette er allerede implementeret i det eksisterende editor-runtime (`assets/admin.js`) med søgning på nuværende elementer, tilføj-element-kommandoer, responsive visninger, states, undo/redo, navigation og designhandlinger. v0.8.7-kontrakttesten karakteriserer denne eksisterende funktion, så den ikke utilsigtet mistes under den videre arkitekturopdeling.

## Protected domains

Vehicle, Event og Gallery forbliver på deres eksisterende legacy runtime. Denne slice ændrer kun wp-admin UX for Sider-editorens elementpalette og layoutværktøjer.

## QA

`tests/Architecture/v087-element-library-contract.sh` verificerer:

1. søgning, kategorier og favoritter,
2. admin-only enqueue,
3. fravær af persistence/cutover primitives,
4. bevarelse af Ctrl/Cmd+K command palette,
5. at ingen protected-domain-fil er ændret i branchen.

`tests/Architecture/v087-box-tools-contract.sh` verificerer:

1. admin-only enqueue af kasseværktøjerne,
2. spacing-felter for desktop og mobil,
3. fælles og individuelle hjørneradier,
4. separate farve-, font-, størrelse-, padding- og kantfelter,
5. side-by-side grid-preview i canvas,
6. JavaScript-syntaks via `node --check`.
