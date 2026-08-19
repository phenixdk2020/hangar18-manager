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

## Arkitektur

`EditorElementLibraryAdminController` enqueuer kun de nye assets på `page=hangar18-pages` for brugere med `edit_pages`. JavaScript-laget filtrerer og grupperer den allerede renderede palette og kalder ingen repository-, AJAX- eller WordPress write-API'er.

Der indføres derfor ingen:

- ny option eller post meta,
- schema-version,
- frontend-hook,
- renderer-switch,
- public cutover-handler.

## UD-020 command palette

Ctrl/Cmd+K command palette er allerede implementeret i det eksisterende editor-runtime (`assets/admin.js`) med søgning på nuværende elementer, tilføj-element-kommandoer, responsive visninger, states, undo/redo, navigation og designhandlinger. v0.8.7-kontrakttesten karakteriserer denne eksisterende funktion, så den ikke utilsigtet mistes under den videre arkitekturopdeling.

## Protected domains

Vehicle, Event og Gallery forbliver på deres eksisterende legacy runtime. Denne slice ændrer kun wp-admin UX for Sider-editorens elementpalette.

## QA

`tests/Architecture/v087-element-library-contract.sh` verificerer:

1. søgning, kategorier og favoritter,
2. admin-only enqueue,
3. fravær af persistence/cutover primitives,
4. bevarelse af Ctrl/Cmd+K command palette,
5. at ingen protected-domain-fil er ændret i branchen.
