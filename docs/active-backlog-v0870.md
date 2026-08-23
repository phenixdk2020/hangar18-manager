# Hangar18 Manager — aktiv backlog v0.8.70

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.70**  
**Release commit:** `17948b2690f0640bdf6f78b9df0e5fc42fc6c0cd`  
**Package SHA-256:** `0a0e6d65c28803506f20cba1440c2493c99c00102d8ee65d955e15547de2d566`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Manuel FAIL fra v0.8.69

- Child-elementer inde i Kassen fik fortsat ikke korrekt rød markering.
- Ved drag fra over/oven ind over Kassen blev der kun tilbudt Over/Under; `IND I KASSEN` var ikke en rigtig synlig LEGO-dropzone.
- v0.8.69 er derfor FAIL på både selection og inside-Kasse.

## Vigtig historisk korrektion

- Den selection-fil vi tidligere beskrev som v0.8.48 var faktisk v0.8.51-varianten af `ultimate-designer-lego-inspector-only-v0847.js`.
- Den præcise v0.8.48 release bruger child-cardens egen `.h18-v0811-edit-child` direkte ved nested click.
- v0.8.70 gendanner denne eksakte nested-click-path.
- v0.8.49 er fortsat pensioneret som selvstændig selection-ejer; v0.8.50 funktioner og v0.8.51 Over/Under stacking bevares.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO child-selection | 🟡 FIX-KANDIDAT v0.8.70 | Test den ægte v0.8.48 nested click/selection-path. |
| LEGO IND I KASSEN | 🟡 FIX-KANDIDAT v0.8.70 | Test den nye synlige femte LEGO-zone i midten af Kassen. |
| LEGO Over/Under stack | 🟡 BEVARET v0.8.51 | Regressionstest; skal fortsat fungere. |
| LEGO repaint/resize | 🔴 BACKLOG | Må først optimeres videre når selection og inside semantics er stabile. |
| GitHub updater status | 🔴 REGRESSION | UPDATER-STATUS-001 forbliver åben. |
| GitHub updater versionsvisning | 🔴 REGRESSION | UPDATER-VERSION-002 forbliver åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres. |
| Public cutover | 🔒 LÅST | Ingen cutover før samlet manuel QA. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-SELECTION-070 | Kritisk | 🟡 FIX-KANDIDAT | Nested selection brugte efterfølgende v0.8.51 canonical-row handoff i stedet for den præcise v0.8.48 child-card Rediger-path. | Klik child i Kassen → kun child bliver rødt markeret og forbliver markeret efter Inspector-handoff. Top-level Kasse/element fortsætter korrekt. |
| LEGO-INSIDE-070 | Kritisk | 🟡 FIX-KANDIDAT | Kasse havde kun Over/Under/Venstre/Højre LEGO-zoner; hidden center-hit var ikke en bruger-valgbar placement-semantik. | Under almindeligt element-drag viser Kassen en femte central `IND I KASSEN`-zone. Slip dér → LayoutParentKey bliver Kasse-key og elementet bliver child. Slip på Over/Under → vertical placement, ikke inside. |
| LEGO-REPAINT-062 | Høj | 🔴 BACKLOG | Klik/resize kan stadig give unødige repaint-opdateringer. | Ingen flerblink efter kritiske placement/selection semantics er stabile. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede og seneste GitHub-version kan vise `Opdatering tilgængelig: JA`. | `installed < latest` → JA; `installed == latest` → NEJ; `installed > latest` → NEJ. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Automatisk GitHub-check kan sætte JA uden at opdatere vist latest-version. | Availability og versionsnummer kommer fra samme manifest-state. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## Manuel test v0.8.70

- [ ] Klik Kasse → rød markering.
- [ ] Klik child-element i Kassen → kun child rød.
- [ ] Klik et andet child-element → markeringen flytter til dette element.
- [ ] Træk top-level Tekst/Billede over en Kasse → fem zoner er synlige: Over, Under, Venstre, Højre, IND I KASSEN.
- [ ] Slip på IND I KASSEN → elementet bliver child og bytter ikke blot plads.
- [ ] Slip på Over/Under → v0.8.51 vertical placement fungerer fortsat.
- [ ] Fri reorder udenfor dropzoner fungerer fortsat.

## Arbejdsregel

Ingen flere skjulte inside-hitområder. Placement-semantik skal være synlig og entydig i LEGO-zonerne. Selection-reference er den faktiske v0.8.48 nested click-path; Over/Under-reference er v0.8.51.
