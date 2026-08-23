# Hangar18 Manager — aktiv backlog v0.8.63

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.63**  
**Package SHA-256:** `49387856070b576f6a700c419a1aba111f5e301ed282389f0729944c4c715cbb`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO existing-element placement | 🟡 MANUEL TEST | Bekræft at forbedringen fra v0.8.62 fortsat virker. |
| LEGO selection | 🟡 FIX-KANDIDAT v0.8.63 | Klik mellem almindelige Grid-elementer og lodrette stack-segmenter; den røde ramme skal blive stående på valgt element. |
| LEGO repaint/resize | 🟡 MANUEL TEST | Bekræft at v0.8.62 fortsat har fjernet flerblink ved klik og resize. |
| GitHub updater | 🔴 REGRESSION | UPDATER-STATUS-001 forbliver separat og åben. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres af editor/updater-fixes. |
| Public cutover | 🔒 LÅST | Ingen public mutation/cutover før manuel QA er stabil. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-SELECTION-063 | Høj | 🟡 FIX-KANDIDAT | Den røde selection-ramme kunne vises kort og derefter forsvinde, fordi stack-rendereren erstattede den wrapper som havde selection-klassen. | Selection følger canonical element-key gennem normale Grid-tiles, child-cards og stack-segmenter; rød ramme bliver stående efter klik, Inspector-handoff, stack-render og resize; skift mellem elementer flytter rammen direkte til nyt valg. |
| LEGO-DROP-062 | Høj | 🟡 MANUEL TEST | Existing-element LEGO placement er forbedret i v0.8.62. | Venstre/Højre samler elementer deterministisk i samme Auto-kasse; Over/Under bruger stack; fri reorder virker uden LEGO-zone. |
| LEGO-REPAINT-062 | Høj | 🟡 MANUEL TEST | Gentagne komplette canvas-renders blev reduceret i v0.8.62. | Ingen flerblink ved selection eller resize; højst nødvendig afsluttende synkronisering. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede og seneste GitHub-version kan stadig vise `Opdatering tilgængelig: JA`. | `installed == latest` giver altid NEJ; backup/SHA/rollback uændret. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## v0.8.63 — teknisk selection-fix

- Selection-ejeren gemmer fortsat den valgte canonical element-key gennem Inspector-handoff.
- Selection-klassen sættes nu på normale `.h18-v0811-auto-box`, `.h18-v0811-child-card` og `.h18-v0851-stack-segment` efter deres element-key.
- Den canonical række får en persistent fallback-klasse, så WordPress' midlertidige fjernelse af `.is-selected` ikke kan fjerne selection visuelt.
- Klik direkte på et stack-segment vælger segmentets egen key.
- Drag/drop, resize, page schema og stack-persistence er ikke ændret i v0.8.63.

## Manuel test v0.8.63

- [ ] Klik Tekst → rød ramme bliver stående.
- [ ] Klik Billede → rammen flytter direkte og bliver stående.
- [ ] Test samme valg efter at Tekst/Billede er samlet i samme Auto-kasse.
- [ ] Test root-element og nederste element i en lodret Over/Under-stack.
- [ ] Vent mindst 3 sekunder efter klik → rammen må ikke forsvinde.
- [ ] Resize bredde og højde → rammen skal stadig være på det valgte element efter slip.
- [ ] Bekræft at v0.8.62 placement stadig fungerer.
