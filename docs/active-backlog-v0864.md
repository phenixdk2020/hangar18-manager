# Hangar18 Manager — aktiv backlog v0.8.64

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.64**  
**Release commit:** `e0de713a46258a417c13472e17be09a849e9b392`  
**Package SHA-256:** `3407cdab2a61db688148526ffbd07cebd6c5edb92a8c1fe5ba06eb451f3b9e14`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO existing-element placement | 🟡 FIX-KANDIDAT v0.8.64 | Test Tekst + Billede: eksisterende drag skal igen bruge v0.8.58/v0.8.51 placement-runtime uden v0.8.62-koordinatoren. |
| LEGO selection | 🟡 FIX-KANDIDAT v0.8.64 | Test top-level Tekst/Billede: rød ramme skal blive stående efter Inspector-handoff. |
| LEGO repaint/resize | 🟡 FORBEDRET | Repaint-forbedringer bevares; regressionstest ved klik og resize. |
| GitHub updater status | 🔴 REGRESSION | UPDATER-STATUS-001 forbliver åben. |
| GitHub updater versionsvisning | 🔴 REGRESSION | UPDATER-VERSION-002 forbliver åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres af editor/updater-fixes. |
| Public cutover | 🔒 LÅST | Ingen public mutation/cutover før manuel QA er stabil. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-DROP-064 | Kritisk | 🟡 FIX-KANDIDAT | v0.8.62 introducerede en ekstra placement-koordinator oven på den kendte v0.8.58/v0.8.51 nesting/drop-zone-runtime. Manuel v0.8.63 viste fortsat rå Sortable-reorder. v0.8.64 deaktiverer koordinatoren helt. | Tekst + Billede kan samles i samme Kasse/Grid via de etablerede placement-zoner uden blot at bytte plads; almindelig reorder virker fortsat uden placement-zone. |
| LEGO-SELECTION-064 | Kritisk | 🟡 FIX-KANDIDAT | Ved top-level selection kunne WordPress flytte `.h18-page-section-key` ind i Inspector før rækkens `data-key` var gemt. Den røde native markering blev derfor synlig kort, hvorefter persistent selection ikke længere kunne genfinde rækken. | På pointerdown gemmes canonical key på rækken før Inspector-handoff. Rød ramme bliver stående på Tekst/Billede efter klik, Inspector-handoff, render og resize indtil et andet element vælges. |
| LEGO-REPAINT-062 | Høj | 🟡 FORBEDRET | Gentagne komplette canvas-renders er reduceret. | Ingen flerblink ved selection eller resize; højst nødvendig afsluttende synkronisering og ingen selection-tab. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede og seneste GitHub-version kan stadig vise `Opdatering tilgængelig: JA`. | `installed < latest` → JA; `installed == latest` → NEJ; `installed > latest` → NEJ; ens resultat efter automatisk check, manuel kontrol, update og refresh. Backup/SHA/rollback uændret. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Når siden Opdateringer åbnes, kan det automatiske GitHub-check opdage en update og sætte `Opdatering tilgængelig: JA`, men `Seneste GitHub-version` opdateres ikke samtidig til den fundne nye version. | Availability og displayed latest-version kommer fra samme atomiske manifest-state. `JA` må aldrig vises sammen med et stale versionsnummer. Automatisk check, manuel `Kontrollér GitHub nu` og refresh skal vise identiske data. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## v0.8.64 — teknisk ændring

### Placement

- `ultimate-designer-lego-placement-stability-v0862.js` registrerer ikke længere drag/sort/drop/parent/refresh-handlers.
- Eksisterende element-placement ejes igen kun af den kendte v0.8.58/v0.8.51 nesting- og drop-zone-runtime.
- Ingen page-schema- eller persistence-ændringer.

### Selection

- Ved pointerdown på et canonical top-level preview kopieres `.h18-page-section-key` til rækkens `data-key` før click åbner Inspector.
- Den eksisterende v0.8.63 selection-ejer kan derefter genfinde rækken, selv efter at WordPress har flyttet nøglefeltet ind i Inspector.
- Ingen ny MutationObserver, timeout, refresh eller render tilføjes af dette fix.

## Manuel test v0.8.64

- [ ] Opret Tekst og Billede som separate top-level elementer.
- [ ] Klik Tekst → rød ramme bliver stående i mindst 5 sekunder.
- [ ] Klik Billede → rammen flytter og bliver stående.
- [ ] Træk Billede mod Tekst og brug eksisterende placement-zone → de samles i samme Kasse/Grid og bytter ikke blot plads.
- [ ] Gentag modsat vej.
- [ ] Test bredde/højde-resize → ingen flerblink og selection bevares efter slip.
- [ ] Bekræft at Vehicle/Event/Gallery ikke er påvirket.

## Arbejdsregel

Updateren og LEGO-editoren behandles fortsat som separate fejlspor. UPDATER-STATUS-001 og UPDATER-VERSION-002 løses ikke ved at ændre editor-runtime. Editor-fixes må ikke ændre updaterens backup, SHA-verifikation eller rollback-flow.
