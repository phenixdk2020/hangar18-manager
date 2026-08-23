# Hangar18 Manager — aktiv backlog v0.8.65

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.65**  
**Release commit:** `a4d5d5e1296abebd718d720cfcbdc978026ba5ff`  
**Package SHA-256:** `823f6ab315eddb5b891d2bb0e0d097ba1049cba8d72ef6efbd9d7f104cbf0cbe`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO selection | 🟡 FIX-KANDIDAT v0.8.65 | Test at præcis ét synligt element har rød ramme ad gangen: Kasse, child-element og top-level element. |
| LEGO element → Kasse | 🟡 FIX-KANDIDAT v0.8.65 | Test at et almindeligt Tekst/Billede kan slippes over hele Kasse-indholdsområdet og faktisk bliver child i Kassen. |
| LEGO side/vertical placement | 🟡 BASELINE | Venstre/Højre/Over/Under er ikke ændret af v0.8.65; regressionstest efter Kasse-inside ændringen. |
| LEGO repaint/resize | 🟡 FORBEDRET | Regressionstest ved klik og bredde/højde-resize. |
| GitHub updater status | 🔴 REGRESSION | UPDATER-STATUS-001 forbliver åben. |
| GitHub updater versionsvisning | 🔴 REGRESSION | UPDATER-VERSION-002 forbliver åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres af editor/updater-fixes. |
| Public cutover | 🔒 LÅST | Ingen public mutation/cutover før manuel QA er stabil. |

## Manuel FAIL fra v0.8.64

- Kassen kunne beholde rød ramme efter klik på et element inde i Kassen.
- Et nyt top-level element kunne få rød ramme samtidig med den tidligere Kasse, så to elementer så aktive ud samtidig.
- Selection fungerede tydeligere på elementer uden for en Kasse end på child-elementer inde i en Kasse.
- Et element under en Kasse kunne stadig ikke trækkes IND I Kassen; gestussen endte som almindelig Sortable-reorder/ombytning.

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-SELECTION-065 | Kritisk | 🟡 FIX-KANDIDAT | To visuelle selection-systemer kunne tegne samtidigt: native `.is-selected`/kompatibilitetsklasser og den canonical key-baserede selection. Det gav både dobbelt rød ramme og tab af markering på child-elementer. | Præcis én synlig DOM-node får `data-h18-v0865-selected="1"`. Gamle selection-klasser tegner ingen rød ramme. Klik Kasse → kun Kasse rød; klik child → kun child rød; klik top-level element → kun det element rød. Markeringen overlever Inspector-handoff, refresh og resize. |
| LEGO-INSIDE-065 | Kritisk | 🟡 FIX-KANDIDAT | Eksisterende almindelige elementer kunne kun ramme en lille legacy inside-dropzone; ved drag over selve Kasse-indholdet vandt Sortable-reorder og element/Kasse skiftede blot placering. | Hele `.h18-ud-box-contents-preview` fungerer som autoritativt IND I KASSEN-mål for almindelige elementer. Ved sortstop sættes LayoutParentKey til Kassen, canonical row placeres blandt Kassens children, stack-state ryddes ved behov, og der køres én nesting-refresh. Uden inside-target bevares normal baseline-reorder. |
| LEGO-REPAINT-062 | Høj | 🟡 FORBEDRET | Gentagne komplette canvas-renders er reduceret. | Ingen flerblink ved selection eller resize; højst nødvendig afsluttende synkronisering og ingen selection-tab. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede og seneste GitHub-version kan stadig vise `Opdatering tilgængelig: JA`. | `installed < latest` → JA; `installed == latest` → NEJ; `installed > latest` → NEJ; ens resultat efter automatisk check, manuel kontrol, update og refresh. Backup/SHA/rollback uændret. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Når siden Opdateringer åbnes, kan det automatiske GitHub-check opdage en update og sætte `Opdatering tilgængelig: JA`, men `Seneste GitHub-version` opdateres ikke samtidig til den fundne nye version. | Availability og displayed latest-version kommer fra samme atomiske manifest-state. `JA` må aldrig vises sammen med et stale versionsnummer. Automatisk check, manuel `Kontrollér GitHub nu` og refresh skal vise identiske data. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## v0.8.65 — teknisk ændring

### Selection

- `ultimate-designer-lego-inspector-only-v0847.js` vælger én synlig repræsentation af den aktive canonical key i prioriteten stack-segment → child-card → Auto-box → top-level preview.
- Kun denne node får `data-h18-v0865-selected="1"`.
- Gamle `.is-selected`, `is-h18-v0863-selected-row` og `is-h18-v0848-selected-element` bevares af kompatibilitetshensyn, men deres røde outline neutraliseres i `ultimate-designer-lego-fixes-v0851.css`.

### IND I KASSEN

- `ultimate-designer-lego-placement-stability-v0862.js` ejer kun én ny gestus: eksisterende almindeligt element → Kasse-indhold.
- Under drag hit-testes hele det synlige `.h18-ud-box-contents-preview`.
- Ved sortstop korrigeres en eventuel midlertidig Sortable-reorder til den eksplicit valgte inside-placement.
- Venstre/Højre/Over/Under ændres ikke af denne kode.

## Manuel test v0.8.65

- [ ] Klik Kasse → kun Kassen har rød ramme.
- [ ] Klik et element inde i Kassen → Kasse-rammen forsvinder, kun elementet har rød ramme.
- [ ] Klik et top-level element under Kassen → kun dette element har rød ramme.
- [ ] Vent mindst 5 sekunder mellem hvert valg → rammen må ikke forsvinde eller duplikeres.
- [ ] Træk top-level Tekst/Billede over selve Kasse-indholdet → dropzonen aktiveres og elementet ender IND I Kassen.
- [ ] Bekræft at element og Kasse ikke blot bytter plads.
- [ ] Test fri reorder uden inside-target → skal stadig fungere.
- [ ] Regressionstest Venstre/Højre/Over/Under.
- [ ] Test bredde/højde-resize → ingen flerblink og selection bevares.
- [ ] Bekræft at Vehicle/Event/Gallery ikke er påvirket.

## Arbejdsregel

Updateren og LEGO-editoren behandles fortsat som separate fejlspor. UPDATER-STATUS-001 og UPDATER-VERSION-002 løses ikke ved at ændre editor-runtime. Editor-fixes må ikke ændre updaterens backup, SHA-verifikation eller rollback-flow.
