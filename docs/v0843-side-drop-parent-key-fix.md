# v0.8.43 kandidat — side-drop ParentKey-handoff

## Fundet i manuel v0.8.42 acceptance

Den reelle test2-session viste fortsat fejl i Scenario C:

1. Opret/brug **Tekst og billede**.
2. Træk nyt **Tekst** fra venstre palette til den synlige **Venstre**-zone.
3. En Auto-kasse/Grid-række oprettes, men står med **0 børn**.
4. Tekst og Tekst og billede forbliver lodrette top-level elementer.

Det betyder, at v0.8.42 ikke er manuelt accepteret.

## Root cause

Den eksisterende nesting-motor er fortsat korrekt placement-authority. Fejlen ligger i kontrollernes handoff efter oprettelse af en ny Auto-kasse:

- nesting-motoren skriver den nye parent-key til hidden `LayoutParentKey`;
- derefter spejles samme key til `.h18-layout-parent-select`;
- den fulde WordPress-editor har en normal select→hidden change-handler;
- hvis den nyoprettede Auto-kasse endnu ikke findes som option i selecten, bliver `.val(parentKey)` til en tom værdi;
- select change-handleren skriver derefter tom værdi tilbage til `LayoutParentKey`.

Resultatet er en gyldig Auto-kasse med 0 børn, præcis som den manuelle observation.

## Fix

`ultimate-designer-lego-parent-key-guard-v0845.js` beskytter kun denne kontrolsynkronisering:

- reagerer kun når den eksisterende motor allerede har valgt en ikke-tom `LayoutParentKey`;
- accepterer kun en parent-key, som matcher en eksisterende aktiv `container`, `flex` eller `grid`-række;
- sikrer, at samme key findes som option i rækkens parent-select og Inspector-select, hvis rækken er valgt;
- flytter ingen DOM-rækker;
- vælger ingen placement;
- opretter ingen Auto-kasse;
- ejer ingen history, persistence eller public renderer.

`LayoutParentKey` og den eksisterende nesting/Auto-kasse-motor er fortsat canonical authority.

## Regression

Den eksisterende `lego-palette-side-drop-v0843.spec.cjs` er udvidet med den WordPress select→hidden handler, der manglede i den tidligere isolerede test.

PASS kræver nu:

- palette → Venstre virker, selv når native HTML5 target er previewet;
- ny Grid-række konfigureres som Auto-kasser;
- både Tekst og Tekst og billede har samme Auto-kasse `LayoutParentKey`;
- begge parent-selects viser samme parent-key;
- Auto-kasse-preview har 2 tiles;
- antal orphan Grid/Auto-kasser med 0 børn er 0.

## Acceptance

Automatiseret PASS er ikke manuel PASS. Efter en QA-grøn release skal den samme handling gentages på `test2` før Scenario C kan ændres fra FAIL til PASS.

I9 forbliver PENDING og I10/public cutover forbliver låst.
