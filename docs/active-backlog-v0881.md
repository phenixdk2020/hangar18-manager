# Hangar18 Manager — canonical backlog delta v0.8.81

**Statusdato:** 24. august 2026  
**Baseline:** v0.8.81 testkandidat under build  
**Extends:** `docs/active-backlog-v0880.md`

Denne fil er den aktuelle canonical backlog. Den arver hele master-roadmapet via v0.8.80 og overskriver kun punkter ændret i denne batch.

## Batchstatus

Denne batch arbejder på **24 backlog-ID’er**. Hovedmålet er permanent WhatIf source-removal med fail-closed release-QA, dokumenteret legacy-klassifikation og sikre Navigator-produktivitetsfunktioner. De frosne `LEGO-SELECTION-075`, `LEGO-INSIDE-075` og `LEGO-REPAINT-062` ændres ikke.

# E. WhatIf cleanup

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| WHATIF-CLEANUP-001 | Høj | 🟡 RELEASE-MIGRATION v0.8.81 | `tools/whatif-source-cleanup.py` er idempotent/fail-closed og release-workflowet anvender den før pakning. Release må kun fortsætte når primær runtime er uden WhatIf og shim-filer er slettet. |
| WHATIF-002 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Vehicle WhatIf markup/backend branches fjernes ved source-cleanup; normal save/layout/register/fields skal smoke-testes på test2. |
| WHATIF-003 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Event WhatIf markup/backend branches fjernes; normal save/layout/rebuild skal smoke-testes. |
| WHATIF-004 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Gallery WhatIf markup/backend branches fjernes; normal save/layout/rebuild skal smoke-testes. |
| WHATIF-005 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Page Editor WhatIf request/state fjernes; save-status er altid `Gemmer…`; normal save/history smoke-test mangler. |
| WHATIF-006 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Static/legacy content WhatIf markup/backend paths fjernes af samme guarded source-cleanup; normal save smoke-test mangler. |
| WHATIF-007 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Menu create/add/repair/save simulation controls og branches fjernes; normale menu-handlinger smoke-testes efter release. |
| WHATIF-008 | Høj | 🟡 AUTOMATISK QA + MANUEL TEST v0.8.81 | Design/Header/Footer/shell relaterede WhatIf runtime-referencer må ikke overleve primary-runtime assertion. |
| WHATIF-009 | Normal | 🟡 AUTOMATISK QA v0.8.81 | Primære runtime-filer må ikke længere indeholde gamle WhatIf help/log/runtime-tekster. Historisk cleanup-dokumentation er tilladt. |
| WHATIF-010 | Normal | 🟡 AUTOMATISK QA v0.8.81 | `.h18-whatif-help` og WhatIf-only styling fjernes; `.h18-safe-switch` fjernes fra fælles badge-regel når shim migreres væk. |
| WHATIF-011 | Normal | 🟡 AUTOMATISK QA v0.8.81 | Page Editor WhatIf selectors/state fjernes fra `assets/admin.js`; JS syntax kontrolleres efter mutation. |
| WHATIF-012 | Høj | 🟡 RELEASE-MIGRATION v0.8.81 | `NoWhatIfAdminController::register()` og controllerfilen fjernes efter source-cleanup i samme release transaction. |
| WHATIF-013 | Høj | 🟡 RELEASE-MIGRATION v0.8.81 | `hangar18-no-whatif-v0858.js/.css` slettes i samme release transaction og må ikke findes i ZIP. |
| WHATIF-014 | Høj | 🟡 AUTOMATISK QA v0.8.81 | Cleaner kræver 0 case-insensitive `whatif` hits i `hangar18-manager.php`, `assets/admin.js`, `assets/admin.css`, `IntegrationAdminBootstrap.php` samt ingen shim-filer; PHP/JS lint er obligatorisk. |
| WHATIF-015 | Normal | ✅ FÆRDIG v0.8.81 | `docs/whatif-removal-v0881.md` dokumenterer ny kontrakt, domæner, guardrails, konsekvens og testmatrix. |

# F. PowerShell / legacy bootstrap / gammel runtime cleanup

| ID | Pri | Status | Leverance / Definition of done |
|---|---|---|---|
| LEGACY-009 | Normal | ✅ AUDIT FÆRDIG v0.8.81 | Astra runtime guard er klassificeret som aktiv; `maybe_repair_astra_banner_047` er særskilt one-time migration-kandidat og slettes ikke blindt. |
| LEGACY-010 | Normal | ✅ AUDIT FÆRDIG v0.8.81 | `handle_repair_menu()` klassificeres som manuel vedligeholdelse, ikke automatisk dead code; beholdes indtil Menu UI v2 har verificeret fuld erstatning. |
| LEGACY-011 | Normal | 🟡 AUDIT DELVIST v0.8.81 | Editor migration/import/shadow/conversion paths er klassificeret efter ansvar; konkrete nul-reference shims skal stadig identificeres før removal. |
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
| QA-020 | Normal | 🟡 DELVIST v0.8.81 | Governance QA dry-runs WhatIf source-cleaner på kopi, linter muteret PHP/JS og syntax-checker Navigator productivity-laget; fuld historisk asset-lint er fortsat åben. |

# Næste batch efter v0.8.81

1. Smoke-test v0.8.81 på test2: normale Vehicle/Event/Gallery/Menu/Page Editor saves efter WhatIf removal.
2. Smoke-test Navigator typefilter, autoscroll og context menu.
3. Brug installed Cleanup-audit til at afgøre LEGACY-006..008: backup af døde options → fjern dokumenterede one-time repair hooks/flags i små batches.
4. Fortsæt LEGACY-011 med konkret referencegraph over gamle editor importers/shims.
5. De tre frosne canvas-runtimebugs genåbnes kun med TRACE evidence.
