# Hangar18 Manager — aktiv backlog v0.8.68

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.68**  
**Package SHA-256:** `0fb7b298f3034f6506a13e4a967d689ee008f766aeea6e82190012fe51f22ca5`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Manuel FAIL fra v0.8.66

- Kasse og top-level elementer kunne få rød markering.
- Valgte child-elementer inde i Kassen fik fortsat ikke rød markering.
- Eksisterende element kunne stadig ikke trækkes IND I Kassen; element og Kasse endte som almindelig reorder/ombytning.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO child-selection | 🟡 FIX-KANDIDAT v0.8.68 | Selection er rullet tilbage til den kendte v0.8.51/LEGO-048-model. Test Kasse, child og top-level element. |
| LEGO element → Kasse | 🟡 FIX-KANDIDAT v0.8.68 | Pointer-position bruges kun til inside-Kasse placement; test blå inside-target og faktisk parent/child-resultat. |
| LEGO repaint/resize | 🟡 BACKLOG | Må ikke blandes ind i selection/inside-fix før de to kritiske funktioner er stabile. |
| GitHub updater status | 🔴 REGRESSION | UPDATER-STATUS-001 forbliver åben. |
| GitHub updater versionsvisning | 🔴 REGRESSION | UPDATER-VERSION-002 forbliver åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres af editor/updater-fixes. |
| Public cutover | 🔒 LÅST | Ingen public mutation/cutover før manuel QA er stabil. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-SELECTION-068 | Kritisk | 🟡 FIX-KANDIDAT | Senere selection-lag efter v0.8.51 gav manglende/dobbelt selection. Brugeren bekræfter, at rød markering inde i Kassen har virket tidligere. v0.8.68 gendanner v0.8.51/LEGO-048 selection på `.h18-v0811-child-card` og `.h18-v0811-auto-box`. | Klik Kasse → Kasse rød. Klik child i Kassen → child rød. Klik top-level element → top-level rød. Ingen senere data-h18-v0865/v0867 selection-layer må konkurrere. |
| LEGO-INSIDE-068 | Kritisk | 🟡 FIX-KANDIDAT | Sortable-reorder vinder stadig når et eksisterende element forsøges lagt IND I Kassen. | Under drag viser midten af Kassen blå stiplet inside-target. Ved slip sættes LayoutParentKey til Kassen, elementet bliver child og Kasse/element bytter ikke blot plads. |
| LEGO-REPAINT-062 | Høj | 🔴 BACKLOG | Klik/resize kan stadig give unødige repaint-opdateringer. | Løses først efter selection og inside-Kasse er stabile; ingen flerblink uden at ændre placement/selection semantics. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede og seneste GitHub-version kan vise `Opdatering tilgængelig: JA`. | `installed < latest` → JA; `installed == latest` → NEJ; `installed > latest` → NEJ. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Automatisk GitHub-check kan sætte `JA`, men `Seneste GitHub-version` følger ikke nødvendigvis med. | Availability og versionsnummer skal komme fra samme atomiske manifest-state. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## Manuel test v0.8.68

- [ ] Klik Kasse → rød markering.
- [ ] Klik Tekst/Billede inde i Kassen → child-elementet får rød markering som i den tidligere fungerende version.
- [ ] Klik top-level element → rød markering flytter dertil.
- [ ] Træk top-level element over midten af Kassen → blå stiplet inside-target bliver synlig.
- [ ] Slip mens blå target er synlig → elementet bliver child i Kassen og bytter ikke blot plads.
- [ ] Regressionstest Venstre/Højre/Over/Under efter ovenstående.

## Arbejdsregel

Selection baseres nu på den tidligere fungerende v0.8.51/LEGO-048-model. Nye selection-modeller må ikke introduceres uden dokumenteret behov. Repaint og updater behandles som separate backlogspor.
