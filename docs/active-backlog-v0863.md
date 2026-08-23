# Hangar18 Manager — aktiv backlog v0.8.63

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.63**  
**Package SHA-256:** `49387856070b576f6a700c419a1aba111f5e301ed282389f0729944c4c715cbb`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md`-filer er historiske snapshots.

## Status lige nu

| Område | Status | Næste handling |
|---|---|---|
| LEGO existing-element placement | 🔴 REGRESSION | Tekst + Billede kan fortsat ikke samles deterministisk i samme Kasse/Grid; drag/drop ender som almindelig reorder og elementerne bytter plads. |
| LEGO selection | 🔴 REGRESSION | Den røde markering vises kortvarigt eller forsvinder efter selection/render. |
| LEGO repaint/resize | 🟡 FORBEDRET | Repaint er forbedret siden v0.8.61, men må fortsat regressionstestes sammen med selection/placement. |
| GitHub updater status | 🔴 REGRESSION | UPDATER-STATUS-001: samme installerede og seneste version kan stadig give `Opdatering tilgængelig: JA`. |
| GitHub updater versionsvisning | 🔴 REGRESSION | UPDATER-VERSION-002: automatisk check på Opdateringer opdager update og viser `JA`, men feltet med seneste GitHub-version opdateres ikke til den fundne nye version. |
| Vehicle/Event/Gallery | 🔒 BESKYT | Må ikke ændres af editor/updater-fixes. |
| Public cutover | 🔒 LÅST | Ingen public mutation/cutover før manuel QA er stabil. |

## Aktive backlogpunkter

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| LEGO-DROP-062 | Kritisk | 🔴 ÅBEN / MANUEL FAIL v0.8.63 | Med Tekst og derefter Billede som separate elementer kan et eksisterende element fortsat ikke flyttes ind i samme Kasse/Grid som det andet. Ved drag/drop skifter elementerne blot plads som almindelig Sortable-reorder. | En eksplicit LEGO-placement-zone skal være autoritativ ved drop. Venstre/Højre samler de to eksisterende elementer i samme Auto-kasse/Grid; Over/Under opretter/genbruger korrekt stack; almindelig fri reorder må kun ske når ingen LEGO-placement-zone vælges. |
| LEGO-SELECTION-063 | Kritisk | 🔴 ÅBEN / MANUEL FAIL v0.8.63 | Den røde selection-ramme vises kortvarigt eller forsvinder igen efter klik/render. | Selection følger canonical element-key på top-level preview, Grid-tile, child-card og stack-segment. Rød ramme bliver stående efter klik, Inspector-handoff, layout-render, drag/drop og resize, indtil et andet element vælges. |
| LEGO-REPAINT-062 | Høj | 🟡 FORBEDRET | Gentagne komplette canvas-renders er reduceret, men selection/placement kan fortsat fremkalde render-handoff. | Ingen flerblink ved selection eller resize; højst nødvendig afsluttende synkronisering og ingen selection-tab. |
| UPDATER-STATUS-001 | Høj | 🔴 ÅBEN | Samme installerede og seneste GitHub-version kan stadig vise `Opdatering tilgængelig: JA`. | `installed < latest` → JA; `installed == latest` → NEJ; `installed > latest` → NEJ. Resultatet skal være ens efter automatisk check, manuel kontrol, update og refresh. Backup/SHA/rollback uændret. |
| UPDATER-VERSION-002 | Høj | 🔴 ÅBEN | Når man åbner Opdateringer, foretager updateren automatisk et GitHub-check. Den kan opdage, at en opdatering findes og vise `Opdatering tilgængelig: JA`, men `Seneste GitHub-version` bliver stående på den tidligere/stale version i stedet for versionsnummeret fra det manifest/check som udløste JA-status. | Ét atomisk updater-state skal drive både availability og latest-version. Efter automatisk check skal manifestversionen opdateres i samme state/transaktion før UI renderes. `JA` må aldrig vises sammen med et stale `Seneste GitHub-version`. Manuel `Kontrollér GitHub nu`, automatisk page-load check og refresh skal vise identiske data. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## Manuel evidence — v0.8.63 — 2026-08-23

### Editor

1. Opret Tekst som almindeligt element.
2. Opret Billede under Tekst som almindeligt element.
3. Forsøg at trække det ene element ind i samme Kasse/Grid som det andet.
4. **Observeret FAIL:** elementerne skifter blot plads; placement bliver behandlet som almindelig reorder.
5. Klik på elementerne.
6. **Observeret FAIL:** den røde selection-ramme forsvinder igen.
7. Repaint/opdatering er forbedret i forhold til tidligere versioner, men selection er fortsat ustabil.

### Updater

1. Åbn Hangar18-siden **Opdateringer**.
2. Siden foretager automatisk check mod GitHub.
3. Updateren kan vise `Opdatering tilgængelig: JA`.
4. **Observeret FAIL:** feltet `Seneste GitHub-version` bliver ikke samtidig opdateret til versionsnummeret fra den nye fundne release.
5. Det betyder, at availability-state og displayed latest-version kommer fra forskellige/stale state-kilder.

## Arbejdsregel

- LEGO placement, LEGO selection/repaint og GitHub updater behandles som tre separate fejlspor.
- Der må ikke bygges endnu et bredt editor-hotfix oven på v0.8.63 uden først at identificere den konkrete event-/state-ejer, der vinder i runtime.
- Updater-fixes må ikke ændre editor-runtime.
- Editor-fixes må ikke ændre updaterens backup, SHA-verifikation eller rollback-flow.
- Vehicle/Event/Gallery er protected domains og må ikke ændres af disse fixes.
