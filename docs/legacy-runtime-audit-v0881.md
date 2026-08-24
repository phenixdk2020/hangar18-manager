# Hangar18 Manager v0.8.81 — legacy runtime audit

## Princip

Gamle versionsnumre i funktionsnavne er ikke i sig selv bevis på død kode. Oprydning må kun ske, når den konkrete funktion er klassificeret og dens nuværende ansvar er erstattet eller dokumenteret unødvendigt.

## Klassifikation

### Behold som aktiv runtime

- `disable_astra_banner_for_managed_pages()` og de tilhørende Astra-filtre: dette er fortsat en render-time guard mod Astra Banner Area på managed pages. Den er ikke en one-time migration.
- Vehicle/Event/Gallery data stores, markers og public render paths: autoritative produktdomæner og uden for cleanup-scope.
- Page Editor canonical section state, history og backup hooks: aktive systemdele.
- Updater code backup/SHA/rollback: aktive sikkerhedsmekanismer.

### One-time repair/migration — kandidat til senere fjernelse efter live QA

Registreret i constructor som `admin_init`:

- `maybe_run_frontend_repair_046`
- `maybe_repair_astra_banner_047`
- `maybe_repair_vehicle_layout_049`
- `maybe_repair_legacy_page_templates_0411`
- `maybe_repair_mobile_content_layout_0414`
- `maybe_cleanup_legacy_startup_and_vehicle_mobile_0415`
- `maybe_restore_home_editor_design_0423`

De har tilhørende repair/options-flags. De må ikke slettes blindt i v0.8.81, fordi en installation der aldrig har kørt et bestemt trin ellers kan miste migrationsadfærden. Næste cleanup skal bevise, at test2 og den forventede upgrade-path allerede har passeret hvert trin, tage backup af relevante options/data og først derefter fjerne hook + metode + flag.

### Manuel vedligeholdelse — ikke automatisk dead code

- Menu repair-handleren `handle_repair_menu()` er en eksplicit administratorhandling. Den er ikke det samme som de one-time `admin_init` repair hooks og beholdes indtil Menu UI v2 har en verificeret fuld erstatning og rollback-plan.
- Rebuild-handlers for Vehicle/Event/Gallery er aktive reparationsværktøjer og beholdes; kun deres WhatIf simulation branches fjernes.

### Editor migration/import

Legacy Page Editor/import/shadow/conversion-kode skal vurderes efter funktion, ikke versionsnavn. Aktive conversion-test, restore, backup og compatibility paths beholdes. En senere batch skal identificere konkrete importers/shims med nul references før removal.

## WordPress options

### Aktiv data — behold

- `hangar18_manager_vehicle_register_v12`
- øvrige aktuelle Vehicle/Event/Gallery/Page Editor stores
- updater state/settings/locks
- backup/version stores

### Migration/baseline — behold indtil afsluttende migration

- `hangar18_manager_config_import_meta`
- `hangar18_manager_config_bootstrap_v032`
- `hangar18_manager_authoritative_baseline_20260813`

### One-time repair flags — cleanup-kandidater, ikke slettet i v0.8.81

- `hangar18_manager_frontend_repair_046`
- `hangar18_manager_astra_banner_repair_047`
- `hangar18_manager_vehicle_layout_repair_049`
- `hangar18_manager_legacy_page_template_repair_0411`
- `hangar18_manager_mobile_content_layout_repair_0414`
- `hangar18_manager_legacy_startup_cleanup_0415`
- `hangar18_manager_home_editor_design_repair_0423`

## Release/installationspolitik

Release ZIP må ikke indeholde:

- `.ps1`
- `tools/`, `tests/`, `docs/` eller andre dev-only trees
- log/tmp/bak-filer
- gamle VehicleRegister/bootstrap JSON-filer
- WhatIf shim-filer fra v0.8.58

`tools/release-integrity.py` og `tools/legacy-cleanup-audit.py` er de automatiske guards; den installerede Cleanup-audit på Opdateringer supplerer med WordPress options og filer i den faktiske installation/uploads.

## WordPress-native målarkitektur

Efter cleanup skal systemet have disse tydelige ejere:

- WordPress posts/meta/media: public content og medier.
- Hangar18 options: kun aktuelle, dokumenterede stores/settings/state.
- Page Editor canonical rows + eksisterende section fields: layout/content persistence.
- `LayoutParentKey`: canonical parent relation for Kasse/Grid/Flex.
- Page versions + managed/site backups: restore/rollback.
- GitHub release manifest + updater state: code delivery og versionsstatus.
- Ultimate Designer admin-lag: UX over eksisterende canonical state, ikke konkurrerende databaser.

Gamle repair flags og migration hooks må først fjernes, når upgrade-pathen ikke længere behøver dem og backup/live QA dokumenterer det.
