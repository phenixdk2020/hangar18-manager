# Hangar18 Manager — aktiv backlog v0.8.73

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.73 Diagnostic**  
**Release commit:** `85c0a53b684798d36d9d70ec4c5f2127cdb2456d`  
**Package SHA-256:** `47395d8b5ca1ccb45601a2e3cac7116f0b566c1f7dfc0ef8c44eb025663213ad`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Manuel FAIL fra v0.8.72

- Child-selection inde i Kassen forsvinder fortsat efter splitsekund.
- `IND I KASSEN` bliver fortsat ikke vist i live drag-scenariet.
- v0.8.72 er derfor FAIL på begge kritiske acceptance-tests.

## Arbejdsbeslutning

Ingen yderligere funktionelle editorfixes før live runtime-state er observeret. v0.8.73 er diagnostic-only og må ikke ændre selection-, placement-, ParentKey- eller stack-semantik.

## Status

| Område | Status | Næste handling |
|---|---|---|
| LEGO child-selection | 🔴 DIAGNOSE | Kør click-test og kopier LEGO diagnose efter den røde ramme er forsvundet. |
| LEGO IND I KASSEN | 🔴 DIAGNOSE | Kør drag over Kasse og kopier LEGO diagnose efter zonerne har været vist. |
| LEGO Over/Under | 🔒 BESKYT | Må ikke ændres under diagnose. |
| LEGO repaint/resize | 🔴 BACKLOG | Behandles først efter semantics er stabile. |
| GitHub updater status | 🔴 REGRESSION | UPDATER-STATUS-001 åben. |
| GitHub updater versionsvisning | 🔴 REGRESSION | UPDATER-VERSION-002 åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres. |
| Public cutover | 🔒 LÅST | Ingen cutover før samlet manuel QA. |

## Diagnosefelter v0.8.73

Panelet viser selection-key/mode, matching/visible nested nodes, selectedMatching/selectedTotal, native selected-row key, computed outline, drag source key/type/mode, overlay count, Kasse-overlay count, inside-zone count/visible count, aktiv dropzone og sidste inside-resultat.

### Test A — selection
1. Klik et child-element inde i Kassen.
2. Vent til den røde ramme er forsvundet.
3. Tryk **Kopiér diagnose** og gem teksten.

### Test B — IND I KASSEN
1. Træk et top-level Tekst/Billede over Kassen og bevæg musen gennem midten.
2. Slip eller annuller efter at dropzonerne har været synlige.
3. Tryk **Kopiér diagnose** og gem teksten.

De to diagnosetekster bruges til at afgøre om fejlen ligger i state, DOM-target, CSS, overlay-rendering eller Sortable-handoff før næste funktionelle release.
