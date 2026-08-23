# Hangar18 Manager — aktiv backlog v0.8.74

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.74**  
**Package SHA-256:** `0078534a22418238794232f3e1a32ee56a4d53af55dacd17fe1024fc5ad5d625`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md` er historiske snapshots.

## Verificeret diagnose fra v0.8.73

Brugerens kopierede diagnose viste:

- `selection-runtime=` tom.
- `selection key/mode` tomme.
- native `.is-selected` række fandtes stadig.
- ingen markerede nested selection-noder.
- `inside-runtime=0.8.72` var indlæst.
- drag-data kunne ikke bruges, fordi v0.8.73 diagnostic havde bundet Sortable-events før editor-DOM kunne eksistere, og mutation-loggen skubbede action-events ud.

### Konklusion selection

`ultimate-designer-lego-inspector-only-v0847.js` installerede event handlers før den nederste `MutationObserver.observe(document.body, ...)`. Hvis scriptet kørte før `document.body` fandtes, kunne observer-installationen kaste før runtime API/version blev registreret. Det forklarer samtidig splitsekundsmarkering: click-handleren kunne nå at markere child, men der fandtes ingen efterfølgende selection-runtime/observer til at genmarkere efter render.

v0.8.74 registrerer API/runtime før body-afhængig initialisering og starter observer via sikker DOMContentLoaded/init.

### Diagnose Kasse-drop

v0.8.74 ændrer ikke placement semantics. Diagnosen er ændret til delegerede Sortable-events og gemmer `last-drag` peaks separat fra mutationer. Næste brugerdiagnose skal derfor afgøre om `IND I KASSEN`:

1. aldrig oprettes,
2. oprettes men ikke er synlig,
3. er synlig men aldrig bliver aktiv,
4. bliver aktiv men placement-resultatet fejler.

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-SELECTION-074 | Kritisk | 🟡 FIX-KANDIDAT | Selection-runtime fejlede init før `document.body`, så child-marker ikke kunne overleve render. | Diagnose viser `selection-runtime=0.8.74`, `api=0.8.74`, `observer=active`; child-click giver nested key, `selectedMatching>=1`, og rød kant bliver stående. |
| LEGO-INSIDE-DIAG-074 | Kritisk | 🔎 DIAGNOSE | Tidligere diagnose kunne ikke fastholde Sortable/overlay-data. | En komplet `last-drag` rapport viser peakOverlays/peakBox/peakInside/visibleInside/activeSeen/result, så næste placement-fix kan målrettes én konkret fejl. |
| LEGO-INSIDE-072 | Kritisk | 🔴 ÅBEN | `IND I KASSEN` bliver fortsat ikke synlig/brugbar i live-editor. | Kasse viser eksplicit `IND I KASSEN`; slip dér sætter LayoutParentKey og bliver ikke ren reorder. |
| LEGO-REPAINT-062 | Høj | 🔴 BACKLOG | Klik/resize kan stadig give unødige repaint-opdateringer. | Ingen flerblink efter selection/placement er stabile. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede/latest kan vise `JA`. | Korrekt version_compare-state. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Automatisk check kan sætte `JA` uden at opdatere vist latest-version. | Availability og vist versionsnummer kommer fra samme manifest-state. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## Manuel test v0.8.74

1. Klik child-element i Kassen og vent 5 sekunder.
2. Kopiér diagnose.
3. Nulstil diagnose-loggen.
4. Træk et top-level element over Kassen, prøv midten, og slip.
5. Kopiér diagnose igen.

Placement ændres ikke yderligere før `last-drag`-data er modtaget.
