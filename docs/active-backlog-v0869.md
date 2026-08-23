# Hangar18 Manager — aktiv backlog v0.8.69

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.69**  
**Release commit:** `6e5b57f83d1f2f4f5e317cdf2f1778b572baa0ba`  
**Package SHA-256:** `77816b5b85788894f9a96e5763e1db6bf9e7ab4d4069eb12a3765f762bfb245b`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Manuel FAIL fra v0.8.68

- Rød markering virkede fortsat ikke korrekt på valgte child-elementer inde i Kassen.
- Eksisterende element kunne fortsat ikke flyttes IND I Kassen; element og Kasse skiftede blot placering via Sortable-reorder.
- Brugerens historiske observation er vigtig: child-selection virkede i en tidligere version før v0.8.51, mens v0.8.51 var versionen hvor lodret Over/Under stacking blev gjort funktionel.

## Historisk afgrænsning

- v0.8.48 / LEGO-048 indførte direkte nested selection på `.h18-v0811-child-card` og `.h18-v0811-auto-box` med `is-h18-v0848-selected-element`.
- v0.8.49 tilføjede en separat persistent selection-inspector med egen active-key state, document.body MutationObserver, nesting.refresh wrapper og gentagne settle-kørsler.
- v0.8.50 kaldte fortsat v0.8.49 selection API efter media/design/history-reconcile.
- v0.8.51 tilføjede den lodrette stack/Over-Under model.
- Arbejdshypotesen er derfor: behold v0.8.48 selection, v0.8.50 funktioner og v0.8.51 stack — men fjern v0.8.49 som selection-ejer.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO child-selection | 🟡 FIX-KANDIDAT v0.8.69 | Test v0.8.48 selection uden v0.8.49 som konkurrerende selection-ejer. |
| LEGO Over/Under stack | 🟡 BEVARET v0.8.51 | Regressionstest; må ikke ændres af selection-fix. |
| LEGO element → Kasse | 🟡 FIX-KANDIDAT v0.8.69 | Test Kasse-center som entydigt inside-target og faktisk ParentKey-resultat. |
| LEGO repaint/resize | 🔴 BACKLOG | Må først optimeres videre efter selection og inside-Kasse er stabile. |
| GitHub updater status | 🔴 REGRESSION | UPDATER-STATUS-001 forbliver åben. |
| GitHub updater versionsvisning | 🔴 REGRESSION | UPDATER-VERSION-002 forbliver åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres af editor/updater-fixes. |
| Public cutover | 🔒 LÅST | Ingen public mutation/cutover før manuel QA er stabil. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-SELECTION-069 | Kritisk | 🟡 FIX-KANDIDAT | v0.8.49 blev fortsat indlæst som en ekstra selection-ejer oven på den fungerende v0.8.48 nested selection. v0.8.50 genkaldte desuden v0.8.49 API'et under reconcile. | v0.8.49 ejer ikke selection, har ingen selection-body-observer eller nesting.refresh wrapper. v0.8.48 markerer child/top-level. v0.8.50 kompatibilitetskald ændrer kun marker hvis DOM faktisk mangler korrekt v0.8.48 marker. |
| LEGO-INSIDE-069 | Kritisk | 🟡 FIX-KANDIDAT | Inside-Kasse target blev tidligere nulstillet af global LEGO-zone detektion eller stale Sortable coordinates. | Midterområdet af en gyldig Kasse er entydigt `IND I KASSEN`; final target genberegnes på sidste faktiske pointerkoordinat ved sortstop; LayoutParentKey bliver Kasse-key og element/Kasse bytter ikke blot plads. |
| LEGO-REPAINT-062 | Høj | 🔴 BACKLOG | Klik/resize kan stadig give unødige repaint-opdateringer. | Ingen flerblink eller unødige fulde renders, men først efter de to kritiske semantics er stabile. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede og seneste GitHub-version kan vise `Opdatering tilgængelig: JA`. | `installed < latest` → JA; `installed == latest` → NEJ; `installed > latest` → NEJ. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Automatisk GitHub-check kan sætte `JA`, men `Seneste GitHub-version` følger ikke nødvendigvis med. | Availability og versionsnummer skal komme fra samme atomiske manifest-state. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## Manuel test v0.8.69

- [ ] Klik top-level Kasse → rød markering.
- [ ] Klik Tekst/Billede inde i Kassen → kun det valgte child-element får rød markering.
- [ ] Vent 5 sekunder → markeringen forbliver stabil uden v0.8.49 settle-blink.
- [ ] Klik et andet child-element → markeringen flytter præcist én gang.
- [ ] Regressionstest v0.8.51 Over/Under → lodret stacking fungerer fortsat.
- [ ] Træk et top-level element over **midten** af Kassen → blå inside-target bliver synlig.
- [ ] Slip i center-target → elementet bliver child i Kassen og skifter ikke blot plads.
- [ ] Test fri reorder udenfor Kasse-center → normal reorder virker fortsat.

## Arbejdsregel

Selection og placement behandles som separate semantics. v0.8.48 er selection-reference; v0.8.51 er Over/Under-reference. Der introduceres ikke nye selection-ejere. Repaint og updater forbliver separate backlogspor.
