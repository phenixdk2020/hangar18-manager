# Hangar18 Manager — aktiv backlog v0.8.71

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.71**  
**Release commit:** `d176f7c3f0b0df807223a1f2678b046cac7fd813`  
**Package SHA-256:** `7eaed0a152c1d6672b9067c85b1e4e5cd5dc598a68a2984833a2781c63582e9e`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Manuel FAIL fra v0.8.70

- `IND I KASSEN` blev fortsat ikke vist under drag over en Kasse.
- Rød child-markering blev kun vist et splitsekund og forsvandt derefter.
- v0.8.70 er derfor FAIL på både inside-zone rendering og persistent child-selection.

## Ny teknisk afgrænsning

- Overlayet kunne kun tilføje `IND I KASSEN`, hvis Kasse-rækken blev genkendt gennem runtime label/state. Inspector-handoff gør dette ustabilt.
- v0.8.71 genkender Kasse strukturelt som `container`, `data-h18-box=1` eller en række med Kasse-preview.
- v0.8.48 click-pathen satte child-marker korrekt, men dens body MutationObserver fjernede alle marker-klasser ved hver DOM-mutation og udledte derefter selection igen fra transient `.is-selected`/Inspector-state.
- v0.8.71 gemmer den key brugeren faktisk valgte. DOM-renders må kun genanvende denne key og må ikke skifte selection.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO child-selection | 🟡 FIX-KANDIDAT v0.8.71 | Test stabil key-ejet child-markering gennem Kasse/Grid rerender. |
| LEGO IND I KASSEN | 🟡 FIX-KANDIDAT v0.8.71 | Test at strukturel Kasse altid får den synlige femte inside-zone. |
| LEGO Over/Under stack | 🟡 BEVARET v0.8.51 | Regressionstest; må ikke ændres. |
| LEGO repaint/resize | 🔴 BACKLOG | Optimeres først efter placement/selection semantics er stabile. |
| GitHub updater status | 🔴 REGRESSION | UPDATER-STATUS-001 forbliver åben. |
| GitHub updater versionsvisning | 🔴 REGRESSION | UPDATER-VERSION-002 forbliver åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres. |
| Public cutover | 🔒 LÅST | Ingen cutover før samlet manuel QA. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-SELECTION-071 | Kritisk | 🟡 FIX-KANDIDAT | Child-marker bliver sat ved klik, men nyere DOM-renders får den gamle observer til at miste selection. | Klik child → child-key gemmes som aktiv bruger-selection. DOM-rerender → samme child genmarkeres uden først at nulstille selection. Kun ét visuelt element er rødt. Klik andet child/top-level → key/mode skifter kun pga. dette brugerklik. |
| LEGO-INSIDE-071 | Kritisk | 🟡 FIX-KANDIDAT | `IND I KASSEN` blev ikke renderet, fordi overlayets Kasse-genkendelse var afhængig af label/state. | Ethvert gyldigt Kasse/container-target viser central `IND I KASSEN` ved drag af almindeligt element. Overlay har `data-h18-v0871-target-box=1` og `data-h18-v0871-has-inside=1`. Slip på inside → LayoutParentKey bliver Kasse-key. |
| LEGO-REPAINT-062 | Høj | 🔴 BACKLOG | Klik/resize kan stadig give unødige repaint-opdateringer. | Ingen flerblink efter kritiske semantics er stabile. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede og seneste GitHub-version kan vise `Opdatering tilgængelig: JA`. | `installed < latest` → JA; `installed == latest` → NEJ; `installed > latest` → NEJ. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Automatisk GitHub-check kan sætte JA uden at opdatere vist latest-version. | Availability og versionsnummer kommer fra samme manifest-state. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## Manuel test v0.8.71

- [ ] Træk almindeligt top-level Tekst/Billede over en Kasse → `IND I KASSEN` vises tydeligt i midten sammen med de øvrige relevante zoner.
- [ ] Slip på `IND I KASSEN` → elementet bliver child i Kassen og bytter ikke blot plads.
- [ ] Klik child-element i Kassen → rød markering kommer frem og forbliver mindst 5 sekunder.
- [ ] Klik andet child-element → rød markering flytter kun til dette child.
- [ ] Når child er valgt, vises parent-Kassen ikke samtidig med rød native selection.
- [ ] Klik top-level Kasse/element → nested-mode ophører og top-level selection vises normalt.
- [ ] Regressionstest Over/Under og fri reorder.

## Arbejdsregel

Selection-key må kun ændres af en bruger-selection-gesture. MutationObservers og layout-renders må kun genanvende aktiv key. Kasse-dropsemantik skal være synlig i LEGO-overlayet; ingen skjulte inside-hitområder.
