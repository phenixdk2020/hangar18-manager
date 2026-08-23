# Hangar18 Manager — aktiv backlog v0.8.76

**Statusdato:** 23. august 2026  
**Aktuel pluginbaseline:** **v0.8.76**  
**Release commit:** `dfb7903350d83676e85905753e01c64d91ad6b2a`  
**Package SHA-256:** `148ceec83e3c756f11741c8e7f53f2c94535e8434379d919fa68c63d2264a0d6`  
**Testtarget:** `https://test2.hangar18.dk`

Denne fil er den aktuelle canonical aktive backlog. Tidligere `active-backlog-v08xx.md` er historiske snapshots.

## Arbejdsstrategi efter v0.8.76

v0.8.76 introducerer opt-in persistent trace/debug. De langvarige LEGO selection/drop/repaint-fejl fryses som kendte åbne fejl, indtil de kan reproduceres med fuld trace. Arbejdet fortsætter på de øvrige backlogspor imens.

Trace master findes på **Opdateringer** og er FRA som standard. Når master er TIL, kan en test startes/stoppes i Designeren og eksporteres som TXT/JSON. Trace-data er browser-lokale og password/token/nonce-lignende værdier maskeres.

## Prioriteret aktiv backlog

| ID | Prioritet | Status | Problem | Definition of done |
|---|---|---|---|---|
| TRACE-076 | Kritisk | 🟡 MANUEL TEST | Langvarig editorfejlfinding har manglet et komplet reproducerbart eventspor. | Master TIL/FRA på Opdateringer; trace indlæses kun når master=TIL; tung log er FRA indtil Start test/Fortsæt; Stop bevarer log; Markér/Kopiér/TXT/JSON/Nulstil virker; log overlever refresh; JS errors registreres når trace-værktøjet er indlæst; sensitive værdier maskeres. |
| UPDATER-VERSION-002 | Kritisk | 🔴 ÅBEN | Automatisk update-check kan sætte `Opdatering tilgængelig: JA`, mens feltet `Seneste GitHub-version` stadig viser en gammel version. Manuel check opdaterer begge. | Auto-check, manuel check og render af Opdateringer bruger samme atomiske manifest/state. Hvis JA kommer fra version X, skal `Seneste GitHub-version` samtidig vise X. Ingen blanding af gammel manifestvisning og ny availability. |
| UPDATER-STATUS-001 | Kritisk | 🔴 ÅBEN | Efter en vellykket opdatering kan siden fortsat vise `Opdatering tilgængelig: JA`, selv om installeret version er lig latest. | `installed < latest` → JA. `installed == latest` → NEJ. `installed > latest` → NEJ. Efter installation genlæses/normaliseres aktiv pluginversion og state invalides/reberegnes, så stale JA ikke overlever update eller refresh. |
| PAGE-VERSION-RESTORE-001 | Høj | 🔴 ÅBEN | Page Editor har versionshistorik/backup ved gem, men restore af en konkret tidligere webpage-version skal være komplet og sikkert tilgængelig fra UI. | Versioner kan listes med tidspunkt/ændringsnote/pluginversion; Preview/sammenligning uden write; Restore kræver eksplicit valg mellem **Erstat original** og **Restore som kopi**. Erstat original tager safety-version før write og kan undo'es. Restore som kopi må ikke ændre originalen og opretter en ny WordPress-side/kladde med collision-safe titel/slug. Vehicle/Event/Gallery påvirkes ikke. |
| WHATIF-CLEANUP-001 | Høj | 🔴 ÅBEN | v0.8.58 fjernede synlig WhatIf UI, men kompatibilitets-/backendgrene og særskilte `no-whatif` assets findes fortsat. | Audit alle WhatIf-referencer i PHP/JS/CSS/schema/tests/docs. Fjern døde WhatIf branches, hidden inputs, query/post parsing og kompatibilitetskode der ikke længere har en funktion. Fjern `hangar18-no-whatif-v0858.*` når de ikke længere er nødvendige. Bevar backup/rollback og normale save-flows. Ingen synlig eller skjult WhatIf-state tilbage i aktiv runtime. |
| LEGACY-POWERSHELL-CLEANUP-001 | Høj | 🔴 ÅBEN | Projektet startede med PowerShell/JSON-bootstrap og legacy management-artifacts. Der skal ryddes op systematisk, så WordPress-plugin/runtime er den eneste aktive administrationsvej. | Audit repository, release ZIP, plugin directory og relevante legacy data/artifacts for PowerShell/bootstrap/VehicleRegister-generation. Ingen `.ps1` eller kendt `Hangar18-VehicleRegister.json` ligger i aktuelt repository tree; runtime/site skal stadig auditeres før punktet kan lukkes. Fjern kun dokumenteret døde artifacts efter backup. Bevar nødvendige migrerede WordPress-data. |
| LEGO-SELECTION-075 | Kritisk | ⏸ FROSSET / TRACE | Nested selection blev stabil i v0.8.74, men skift mellem nested og top-level har fortsat vist dobbelt/fejlmarkering i senere tests. | Reproducer med TRACE-076. Trace skal vise click/pointer/focus, active key/mode, native row, red keys og runtime calls. Fix først derefter. Præcis én rød markering efter hver selection. |
| LEGO-INSIDE-075 | Kritisk | ⏸ FROSSET / TRACE | Element → `IND I KASSEN` på layoutkasser er fortsat ustabil/ikke synlig i live-test. | Reproducer med TRACE-076. Trace skal vise source key/type, Sortable lifecycle, overlays, inside zones, active zone, target key og ParentKey før/efter. Fix først derefter. |
| LEGO-REPAINT-062 | Høj | ⏸ FROSSET / TRACE | Klik/resize kan stadig give blink/unødige renders. | Reproducer med TRACE-076 og identificer konkrete refresh/render-calls; ingen generiske timers/observer-lag. |
| I9-EVIDENCE | Normal | 🟡 PENDING | Samlet manuel/live QA mangler. | Canonical test2/protected-domain/rollback evidence gennemført efter kritiske editor/updater-fejl. |
| I10-CUTOVER | Normal | 🔒 LÅST | Public conversion må ikke fortsætte endnu. | Først efter fuldt I9 PASS og særskilt cutover-godkendelse. |

## WhatIf — konkret cleanup-scope

Repository tree indeholder fortsat:

- `assets/hangar18-no-whatif-v0858.js`
- `assets/hangar18-no-whatif-v0858.css`
- `src/Admin/NoWhatIfAdminController.php`

Disse blev oprindeligt indført som en sikker UI-only fjernelse af WhatIf. `WHATIF-CLEANUP-001` er den efterfølgende source-cleanup: fjern den gamle funktionalitet ved kilden, og fjern derefter shim/controller/assets i stedet for at skjule UI-elementer runtime.

## PowerShell/legacy cleanup — kendt status

Det aktuelle GitHub repository tree viser ingen `.ps1` filer og ingen filsti med `VehicleRegister` i navnet. Det er **ikke** nok til at lukke opgaven, fordi den også omfatter installeret plugin/site, eventuelle uploads/legacy JSON-data og historiske bootstrap-artifacts. Oprydning skal udføres med read-only audit først og backup før deletion.

## Page version restore — sikkerhedskrav

Den eksisterende legacy plugin-kode har `PAGE_VERSION_HISTORY_OPTION = hangar18_manager_page_versions_v1`, og versionshistorikken indgår i full managed backup. Restore-backloggen skal bygge videre på dette dataformat i stedet for at introducere en parallel versionsdatabase.

Minimum flow:

1. Vælg side.
2. Se versionsliste med timestamp + reason/ændringsnote.
3. Preview/sammenlign valgte version mod aktuel uden write.
4. Vælg **Restore**.
5. Vælg eksplicit restore-mode:
   - **Erstat original** — den eksisterende side erstattes med den valgte version.
   - **Restore som kopi** — originalen røres ikke; den valgte version oprettes som en ny WordPress-side/kladde med collision-safe titel og slug.
6. Ved **Erstat original** oprettes automatisk en safety-version af den aktuelle side før første write.
7. Ved **Restore som kopi** må der ikke foretages write mod original side, original page-editor state eller original slug.
8. Verificer canonical store + WordPress page output for den valgte restore-mode.
9. **Erstat original** skal kunne undo'es tilbage til safety-versionen.
10. Kopien skal efter oprettelse kunne redigeres og gemmes som en normal selvstændig side.

UI'et må ikke vælge restore-mode automatisk. Brugeren skal aktivt vælge **Erstat original** eller **Restore som kopi** før restore kan gennemføres.

## Updater — atomisk state-kontrakt

Updater UI må aldrig vise state fra forskellige checks i samme render.

Canonical state for et check skal mindst indeholde:

- `checked_at_utc`
- `current_version`
- `manifest.version`
- `update_available`
- `compatible_wp`
- `compatible_php`
- `error`

`update_available` skal altid beregnes fra **præcis de samme** `current_version` og `manifest.version`, som renderes på siden. Efter installation skal gammel state invalides eller erstattes med et nyt state-snapshot.

## Næste arbejdsrækkefølge

1. Manuel smoke-test af TRACE-076 UI/master uden at genåbne LEGO-fejl.
2. `UPDATER-VERSION-002` + `UPDATER-STATUS-001` som ét isoleret updater-fixspor.
3. `PAGE-VERSION-RESTORE-001` med eksplicit **Erstat original / Restore som kopi**.
4. `WHATIF-CLEANUP-001`.
5. `LEGACY-POWERSHELL-CLEANUP-001` read-only audit → godkendt cleanup.
6. Fortsæt øvrig backlog/I9 prep.
7. LEGO-fejl genoptages kun med konkret TRACE-076 reproduktion.

## Beskyttede områder

- Vehicle/Event/Gallery må ikke ændres af updater/trace/WhatIf/restore-cleanup.
- Backup, package SHA-verifikation, code backup og automatisk updater rollback skal bevares.
- Public cutover er fortsat ikke autoriseret.
