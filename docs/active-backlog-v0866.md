# Hangar18 Manager — aktiv backlog v0.8.66

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.66**  
**Release commit:** `bdb969d0a7924acb672da7ce6fcdadb7014b7faf`  
**Package SHA-256:** `751bb886c25223d476dbc480834ad2a55a52720a4ae9f9f9e492b4e9e3160d91`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Manuel FAIL fra v0.8.65

- Ingen synlig rød selection-ramme på elementer eller Kasser.
- Eksisterende element kunne stadig ikke trækkes IND I en Kasse; element og Kasse endte fortsat som almindelig reorder/ombytning.
- v0.8.65 må derfor ikke betragtes som PASS på LEGO-SELECTION eller LEGO-INSIDE.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO selection | 🟡 FIX-KANDIDAT v0.8.66 | Test at præcis én rød canonical selection-ramme er synlig og bliver stående. |
| LEGO element → Kasse | 🟡 FIX-KANDIDAT v0.8.66 | Test at hele Kasse-indholdet fungerer som hitområde for baseline `moveRowIntoBox()`. |
| LEGO side/vertical placement | 🟡 BASELINE | Venstre/Højre/Over/Under er ikke ændret i v0.8.66; regressionstest. |
| LEGO repaint/resize | 🟡 FORBEDRET | Regressionstest ved klik og bredde/højde-resize. |
| GitHub updater status | 🔴 REGRESSION | UPDATER-STATUS-001 forbliver åben. |
| GitHub updater versionsvisning | 🔴 REGRESSION | UPDATER-VERSION-002 forbliver åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres af editor/updater-fixes. |
| Public cutover | 🔒 LÅST | Ingen public mutation/cutover før manuel QA er stabil. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-SELECTION-066 | Kritisk | 🟡 FIX-KANDIDAT | v0.8.65 satte den dedikerede selection-attribut korrekt, men den røde regel tabte CSS-specificitet til en senere kompatibilitets-neutralisering med `!important`. | Den dedikerede canonical markør vinder CSS-kaskaden. Præcis én synlig node er rød. Klik Kasse → kun Kasse. Klik child → kun child. Klik top-level element → kun dette element. Markeringen bliver stående efter Inspector-handoff, refresh og resize. |
| LEGO-INSIDE-066 | Kritisk | 🟡 FIX-KANDIDAT | Baseline `nesting-tools` har korrekt `sortstop -> moveRowIntoBox()`, men `boxAtPoint()` målte kun den lille `.h18-ud-box-drop-zone`. Drag over selve Kasse-indholdet blev derfor ikke klassificeret som `inside`. | Under eksisterende element-drag strækkes den eksisterende dropzones geometri over hele `.h18-ud-box-contents-preview`, så baseline `boxAtPoint()` registrerer Kassen og baseline `moveRowIntoBox()` sætter `LayoutParentKey` og flytter rækken. Ingen sekundær sort/drop-ejer. |
| LEGO-REPAINT-062 | Høj | 🟡 FORBEDRET | Gentagne komplette canvas-renders er reduceret. | Ingen flerblink ved selection eller resize; højst nødvendig afsluttende synkronisering og ingen selection-tab. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede og seneste GitHub-version kan stadig vise `Opdatering tilgængelig: JA`. | `installed < latest` → JA; `installed == latest` → NEJ; `installed > latest` → NEJ; ens resultat efter automatisk check, manuel kontrol, update og refresh. Backup/SHA/rollback uændret. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Når siden Opdateringer åbnes, kan automatisk GitHub-check opdage en update og sætte `Opdatering tilgængelig: JA`, men `Seneste GitHub-version` følger ikke nødvendigvis med. | Availability og displayed latest-version kommer fra samme atomiske manifest-state. `JA` må aldrig vises sammen med stale versionsnummer. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## v0.8.66 — teknisk ændring

### Selection

- `data-h18-v0865-selected="1"` er fortsat den eneste tilsigtede røde visuelle selection-ejer.
- Dens CSS-selector har nu højere specificitet end de senere kompatibilitetsregler, som neutraliserer gamle `.is-selected`/`is-h18-v0848-selected-element` frames.
- Der tilføjes ingen ny selection-observer eller repaint-loop.

### IND I KASSEN

- v0.8.65's sekundære Sortable/inside-handler er fjernet igen.
- Den kanoniske `nesting-tools` runtime er eneste placement-ejer.
- Under `.h18-ud-existing-row-drag` udvides den allerede eksisterende `.h18-ud-box-drop-zone` absolut over hele `.h18-ud-box-contents-preview`.
- Baseline `boxAtPoint()` ser dermed det fulde Kasse-indhold som sit eksisterende hitmål og afslutter via eksisterende `moveRowIntoBox()` ved sortstop.

## Manuel test v0.8.66

- [ ] Klik Kasse → præcis én rød ramme.
- [ ] Klik child-element i Kassen → Kasse-rammen væk, kun child rød.
- [ ] Klik top-level element → kun dette element rød.
- [ ] Vent mindst 5 sekunder → markeringen bliver stående.
- [ ] Træk top-level Tekst/Billede over midten af Kasse-indholdet → Kassen skal fremstå som aktivt dropmål og elementet ende IND I Kassen.
- [ ] Bekræft at element og Kasse ikke blot bytter plads.
- [ ] Test fri reorder uden Kasse-hit → skal stadig fungere.
- [ ] Regressionstest Venstre/Højre/Over/Under.
- [ ] Test bredde/højde-resize og selection efter slip.
- [ ] Bekræft at Vehicle/Event/Gallery ikke er påvirket.

## Arbejdsregel

Updateren og LEGO-editoren behandles fortsat som separate fejlspor. UPDATER-STATUS-001 og UPDATER-VERSION-002 løses ikke ved at ændre editor-runtime. Editor-fixes må ikke ændre updaterens backup, SHA-verifikation eller rollback-flow.
