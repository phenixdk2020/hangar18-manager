# Hangar18 Manager — canonical backlog delta v0.8.81

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.81 testkandidat under build  
**Extends:** `docs/active-backlog-v0880.md`

Denne fil er den aktuelle canonical backlog. Den arver hele master-roadmapet via v0.8.80 og overskriver kun punkter ændret i denne batch.

## Batchstatus

Denne arbejdsbatch omfatter nu **42 backlog-ID’er**. `release-config.json` holdes bevidst urørt mens v0.8.81 release-pipelinen er blokeret, så yderligere source-arbejde ikke starter flere konkurrerende release-runs. Hovedmålet er permanent WhatIf source-removal, fail-closed release-QA, updater/release-hardening, backup-integritet/health, dokumenteret legacy-klassifikation/rollback og sikre Navigator-produktivitetsfunktioner. De frosne `LEGO-SELECTION-075`, `LEGO-INSIDE-075` og `LEGO-REPAINT-062` ændres ikke.

# A. Release / sporbarhed

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| RELEASE-006 | Normal | 🟡 AUTOMATISK QA + MANUEL ROLLBACK-TEST | Updater-hardening verificerer efter succesfuld rollback den faktisk gendannede `hangar18-manager.php`: plugin-header og `Hangar18_Manager::VERSION` skal være den tidligere version. `hangar18_manager_update_rollback_verification_v1` gemmer `from_version`, `to_version`, `restored_main_sha256`, code-backup SHA og UTC; loggen skriver `UPDATE_ROLLBACK_VERIFIED`. `tools/updater-rollback-qa.py` kræver kontrakten. Rigtig Plugin_Upgrader rollback-test mangler. |
| RELEASE-007 | Høj | ✅ FÆRDIG v0.8.81 | Fail-closed release-cleanup skriver ved stop en isoleret `docs/release-build-failure.md` med version/source commit/step/stderr/stdout, ruller delvise source-writes tilbage og committer kun diagnosen. Diagnosen er udvidet til hele pre-package QA-kæden. |
| RELEASE-008 | Høj | ✅ FÆRDIG v0.8.81 | Release-workflow bruger én concurrency-gruppe med `cancel-in-progress: true`, så nyeste release-config-trigger vinder og ældre køede/in-progress builds ikke senere kan publicere stale packages. |
| RELEASE-009 | Normal | ✅ FÆRDIG v0.8.81 | Release-metadata normaliserer readme pr. versionsnummer: alle eksisterende sektioner for samme version fjernes og præcis én aktuel sektion indsættes, så retries ikke skaber dublerede release-noter. |

# C. GitHub updater

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| UPDATER-SCHEMA-003 | Kritisk | ✅ USER PASS / PIPELINE FIX v0.8.81 | Installeret v0.8.80 accepterer kun `schema_version=1.0`. Aktiv `update.json` er hotfixet til 1.0 og brugerens update-check er bekræftet fungerende. Release-generatoren er låst til 1.0 og package verification fejler ved andet schema, indtil alle installerbare legacy-updatere er migreret. |
| UPDATER-006 | Høj | 🟡 FIX-KANDIDAT / MANUEL UPDATE-TEST | `UpdaterPostInstallVerificationAdminController` verificerer på første request fra ny kode aktiv `Hangar18_Manager::VERSION`, plugin-header og VERSION-kilde mod pending expected-version. Release-hardening skriver pending-transition først efter installeret source er verificeret. Success-audit gemmer from/to/runtime og SHA af installeret hovedfil. |
| UPDATER-007 | Høj | 🟡 FIX-KANDIDAT / MANUEL UPDATE-TEST | Efter installation invalidates `hangar18_manager_update_state_v1`, `update_plugins` site-transient og WordPress plugin-cache samlet; næste request verificerer runtime før atomisk updater-state genopbygges. Samme cache cleanup udføres efter succesfuld rollback. |
| UPDATER-008 | Høj | 🟡 AUTOMATISK QA + MANUEL UPDATE-TEST | Eksisterende SHA-kontrol af GitHub-bytes bevares. `tools/updater-install-hardening.py` tilføjer anden SHA-256-kontrol af den faktisk gemte ZIP-fil før udpakning; mismatch sletter ZIP og stopper transactionen. |
| UPDATER-009 | Høj | 🟡 AUTOMATISK QA + MANUEL UPDATE-TEST | Code-backup oprettes fortsat før mutation. Hardening genåbner backup-ZIP, kræver hovedfil med både korrekt plugin-header og VERSION-konstant og beregner backup-SHA før update-pakken installeres. |
| UPDATER-010 | Høj | 🟡 AUTOMATISK KONTRAKT-QA | `tools/updater-rollback-qa.py` tester simuleret success, fejl før backup, fejl efter verificeret backup og rollback-fejl. Succesfuld rollback skal nu også verificere restored version + SHA og persistere rollback-audit før pending/cache ryddes. Fuld WordPress integrationstest med rigtig Plugin_Upgrader mangler fortsat. |
| UPDATER-015 | Normal | ✅ AUTOMATISK QA v0.8.81 | `tools/updater-contract-qa.py` tester behind/equal/ahead, schema 1.0 vs ukendt schema, plugin-id, versionformat, SHA-format og at atomisk state fortsat beregner JA/NEJ ud fra `latest` mod aktiv `current`. Kører i governance og release-QA. |

# D. Backup, restore og retention

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| BACKUP-002 | Høj | 🟡 FIX-KANDIDAT / MANUEL UI-TEST | `BackupHealthAdminController` viser read-only retention-overblik for B1/B2 med antal backups, samlet diskforbrug, ældste/nyeste tidspunkt og ældste alder i dage. Ingen automatisk sletning introduceres. |
| BACKUP-003 | Høj | 🟡 AUTOMATISK QA + MANUEL RESTORE-TEST | B2 validerede allerede manifest/payload/media SHA ved plan og igen før execute. Ny `ManagedPageBackupIntegrityService` validerer legacy B1 JSON path/størrelse/struktur og SHA-256. B1 restore/copy forms bindes til den viste SHA og afviser mutation hvis filen ændres. `backup-safety-qa.yml` beskytter kontrakten. Versionshistorik-flow skal stadig manuelt verificeres. |
| BACKUP-004 | Normal | 🟡 FIX-KANDIDAT / MANUEL DOWNLOAD-TEST | Backup support kan eksportere samlet B1+B2 restore-audit som UTF-8 JSON eller semikolon-separeret CSV med source/tid/mode/backup/side/safety backup/user/error. Maks 500 nyeste records. |
| BACKUP-006 | Normal | 🟡 FIX-KANDIDAT / MANUEL UI-TEST | Read-only health-check køres højst hver 6. time på Opdateringer/Designer eller manuelt. Seneste 10 B1 JSON-filer SHA/struktur-valideres og seneste 5 B2-pakker gennem `SiteBackupPackageService::validate`; fejl vises uden at ændre backupdata. |

# E. WhatIf cleanup

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| WHATIF-CLEANUP-001 | Høj | 🟡 RELEASE-MIGRATION v0.8.81 | `tools/whatif-source-cleanup.py` er idempotent/fail-closed og release-workflowet anvender den før pakning. Release må kun fortsætte når primær runtime er uden WhatIf og shim-filer er slettet. |
| WHATIF-002 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Vehicle WhatIf markup/backend branches fjernes ved source-cleanup; normal save/layout/register/fields skal smoke-testes på test2. |
| WHATIF-003 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Event WhatIf markup/backend branches fjernes; normal save/layout/rebuild skal smoke-testes. |
| WHATIF-004 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Gallery WhatIf markup/backend branches fjernes; normal save/layout/rebuild skal smoke-testes. |
| WHATIF-005 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Page Editor WhatIf request/state fjernes; save-status er altid `Gemmer…`; draft-save er ikke længere simulation-gated; normal save/history smoke-test mangler. |
| WHATIF-006 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Static/legacy content WhatIf markup/backend paths fjernes af samme guarded source-cleanup; normal save smoke-test mangler. |
| WHATIF-007 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Menu create/add/repair/save simulation controls og branches fjernes; normale menu-handlinger smoke-testes efter release. |
| WHATIF-008 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Design/Header/Footer/shell relaterede WhatIf runtime-referencer må ikke overleve primary-runtime assertion. |
| WHATIF-009 | Normal | 🟡 AUTOMATISK QA v0.8.81 | Primære runtime-filer må ikke længere indeholde gamle WhatIf help/log/runtime-tekster. Fail-closed diagnose fandt fem resterende UI/help-tekster; cleaner v1.5 omskriver dem deterministisk. Historisk cleanup-dokumentation er tilladt. |
| WHATIF-010 | Normal | 🟡 AUTOMATISK QA v0.8.81 | `.h18-whatif-help` omdøbes/fjernes. Blandede wrappers med reelle kontroller bevares som neutral `.h18-action-options`; den generiske `.h18-safe-switch` beholdes, fordi den også bruges af aktive indstillinger som Pin menu/header. |
| WHATIF-011 | Normal | 🟡 AUTOMATISK QA v0.8.81 | Page Editor WhatIf selectors/state fjernes fra `assets/admin.js`; fail-closed diagnose fandt de sidste change/draft-save-referencer og cleaner v1.5 fjerner/omskriver dem; JS syntax kontrolleres efter mutation. |
| WHATIF-012 | Høj | 🟡 RELEASE-MIGRATION v0.8.81 | `NoWhatIfAdminController::register()` og controllerfilen fjernes efter source-cleanup i samme release transaction. |
| WHATIF-013 | Høj | 🟡 RELEASE-MIGRATION v0.8.81 | `hangar18-no-whatif-v0858.js/.css` slettes i samme release transaction og må ikke findes i ZIP. |
| WHATIF-014 | Høj | 🟡 AUTOMATISK QA v0.8.81 | Cleaner kræver 0 case-insensitive `whatif` hits i `hangar18-manager.php`, `assets/admin.js`, `assets/admin.css`, `IntegrationAdminBootstrap.php` samt ingen shim-filer; PHP/JS lint er obligatorisk. |
| WHATIF-015 | Normal | ✅ FÆRDIG v0.8.81 | `docs/whatif-removal-v0881.md` dokumenterer ny kontrakt, domæner, guardrails, konsekvens og testmatrix. |

# F. PowerShell / legacy bootstrap / gammel runtime cleanup

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| LEGACY-006 | Høj | 🟡 MANUEL TEST v0.8.81 | `LegacyStateBackupAdminController` på Opdateringer opretter før cleanup et SHA-mærket snapshot af kendte migration/repair-options i `hangar18_manager_legacy_cleanup_backups_v1`, inkl. exists/value, pluginversion, UTC og user ID. Maks 10 snapshots; handlingen sletter/ændrer ingen kilde-options. |
| LEGACY-007 | Normal | ⛔ BLOKERET AF LEGACY-006 + LIVE MIGRATIONSBEVIS | Startup-repair hooks må først fjernes når test2 har et verificeret rollback-snapshot og hvert relevant repair-flag/migrationsresultat er dokumenteret. Audit viser at hooks stadig kan udføre reelle page/data writes og derfor ikke er sikre nul-reference-sletninger endnu. |
| LEGACY-008 | Normal | ⛔ BLOKERET AF LEGACY-006 + LEGACY-007 | One-time repair flags slettes først efter hook-retirement og dokumenteret upgrade-path. Ingen automatisk flag-sletning er implementeret. |
| LEGACY-009 | Normal | ✅ AUDIT FÆRDIG v0.8.81 | Astra runtime guard er klassificeret som aktiv; `maybe_repair_astra_banner_047` er særskilt one-time migration-kandidat og slettes ikke blindt. |
| LEGACY-010 | Normal | ✅ AUDIT FÆRDIG v0.8.81 | `handle_repair_menu()` klassificeres som manuel vedligeholdelse, ikke automatisk dead code; beholdes indtil Menu UI v2 har verificeret fuld erstatning. |
| LEGACY-011 | Normal | 🟡 AUTOMATISK REFERENCEGRAPH QA | `tools/legacy-reference-graph.py` scanner `hangar18-manager.php` + `src/**/*.php`, inventerer legacy/migration/import/conversion/shadow-klasser, one-time `admin_init` repair-hooks og migration/repair option-konstanter. `legacy-reference-graph-qa.yml` kræver fortsatte eksterne referencer for kendte aktive `LegacyShellShadowAdminController`, `LegacyShellSnapshotService` og `ConversionAdminController`; definition-only resultater er kun review-kandidater og slettes ikke automatisk. |
| LEGACY-012 | Normal | ✅ AUTOMATISK QA v0.8.81 | Release ZIP-policy + legacy audit blokerer PowerShell, bootstrap/VehicleRegister JSON og dev-only leftovers; v0.8.81 tilføjer desuden blokering af WhatIf shim-filer. |
| LEGACY-013 | Normal | ✅ FÆRDIG v0.8.81 | `docs/legacy-runtime-audit-v0881.md` dokumenterer ønsket WordPress-native ejerarkitektur og cleanup-grænser. |

# H. LEGO Navigator, selection og produktivitets-UX

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| LEGO-NAV-003 | Høj | 🟡 MANUEL TEST v0.8.81 | Selection-sync fra v0.8.80 suppleres med autoscroll til den valgte synlige Navigator-node. Ingen selection-owner ændres. |
| LEGO-NAV-006 | Høj | 🟡 MANUEL TEST v0.8.81 | Højreklik i Navigator giver Redigér, Duplikér, Kopiér design, Indsæt design, Flyt til…, Vis/skjul og Fjern ved at kalde eksisterende editor-handlers. Wrap forbliver åben. |
| LEGO-NAV-009 | Normal | 🟡 MANUEL TEST v0.8.81 | Typefilter viser `Alle typer` eller én section-type og bevarer ancestors for matchende children. |

# W. Testing og QA automation

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| QA-020 | Normal | 🟡 DELVIST v0.8.81 | Governance QA dry-runs WhatIf-cleaner + updater-hardening på kopi, linter muteret PHP/JS, kører updater contract/rollback matrix, linter post-install/legacy rollback controllers og syntax-checker Navigator productivity-laget. Separate legacy-referencegraph og backup-safety workflows beskytter aktive migration/shadow references samt backup-integritetskontrakter; fuld historisk asset-lint er fortsat åben. |

# Næste sikre arbejde mens v0.8.81 build er blokeret

1. Review definition-only resultater fra LEGACY-011 workflow; slet kun kandidater hvor dynamisk autoload/handler-reference også er udelukket.
2. Fortsæt ikke LEGACY-007/008 destruktivt før `LEGACY-006` rollback-punkt er live-verificeret på test2.
3. Manuel updater acceptance skal verificere from/to/runtime, package SHA, code-backup SHA, restored rollback SHA og cache-invalidation.
4. Manuel backup acceptance skal verificere B1 SHA-change rejection, B2 validate-before-execute, audit-download og retention/health UI.
5. Når v0.8.81 kan pakkes: smoke-test Vehicle/Event/Gallery/Menu/Page Editor saves efter WhatIf removal.
6. Smoke-test Navigator typefilter, autoscroll og context menu.
7. De tre frosne canvas-runtimebugs genåbnes kun med TRACE evidence.
