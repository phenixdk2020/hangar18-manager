# Ultimate Designer architecture migration

## Baseline

- Runtime reference: Hangar18 Manager v0.5.30.
- Page-editor schema reference: 1.22.
- Architecture work is performed on `agent/architecture-foundation` until compatibility gates pass.
- The existing v0.5.30 runtime remains authoritative during the extraction phase.

## Protected domain contract

Vehicle, Event and Gallery are protected compatibility domains during the migration.

Until a replacement path has passed regression QA, the following must remain unchanged for each protected domain:

1. Stored WordPress data and existing IDs.
2. Public URLs and existing shortcodes/routes.
3. Frontend HTML structure required by existing CSS and JavaScript.
4. CSS class names and layout hooks used by the current theme/plugin output.
5. Image selection, image placement and responsive behaviour.
6. Existing alignment, field visibility and presentation settings.
7. Create/edit/delete behaviour and existing admin workflows.

A refactor commit must not switch a protected domain to a new renderer merely because equivalent classes exist in `src/`.

The concrete v0.5.30 Vehicle/Event/Gallery hooks are characterized separately in `architecture-legacy-domain-contract-v0530.md`.

## Migration rule

The refactor uses a strangler approach:

1. Add contracts, registries and services beside the legacy runtime.
2. Characterize existing behaviour with tests/fixtures.
3. Extract one responsibility without changing its public behaviour.
4. Compare old and new output.
5. Switch only that responsibility when the comparison gate passes.
6. Keep an explicit rollback path until the new responsibility is stable.

## Required compatibility gates before Vehicle/Event/Gallery migration

A protected domain may leave the legacy runtime only when all applicable checks pass:

- Same persisted values when editing an existing entry.
- Same public item count/order/filtering for the same stored data.
- Same semantic markup and all CSS/JS-relevant hooks.
- Same desktop/tablet/mobile alignment and image behaviour.
- No lost optional/custom fields.
- No changed URLs, IDs or media references.
- Existing v0.5.30 data loads without manual migration.
- Rollback to the v0.5.30 path remains possible during the transition.

## Architecture target

The target follows the Ultimate Designer design specification:

- namespaced modular PHP layer;
- versioned schemas and migrations;
- element and property registries;
- repository/storage abstraction;
- centralized security/validation;
- deterministic render/style engines;
- REST boundary for the future React/TypeScript editor;
- domain features such as Vehicle/Event/Gallery represented as schemas/presets/components on the generic engine rather than separate engines.

## Legacy data compatibility already characterized

The existing v0.5.30 page-editor state is stored in WordPress option `hangar18_manager_pages_v1`, keyed by page slug. The normalized page state uses schema 1.22 with:

- `Version`
- `PageSlug`
- `PageTitle`
- `ContentVersion`
- `DataContextType`
- `DataContextEntryId`
- `Sections`

The new repository boundary therefore uses a string page key and the compatibility adapter preserves the exact existing option name and slug-keyed map. No ID conversion or alternate storage is introduced.

The current v0.5.30 admin log is stored in `hangar18_manager_log` with fields `time`, `level`, `checkpoint`, `message` and `user`, retaining the newest 750 entries. `LegacyOptionLogger` preserves that same option, record shape and retention policy for later integration.

## Current foundation slice

The current slice is intentionally non-invasive and contains:

- `src/Autoload.php`
- `src/Core/Version.php`
- `src/Core/Architecture.php`
- `src/Contracts/ElementDefinition.php`
- `src/Contracts/PropertyDefinition.php`
- `src/Contracts/PageRepository.php`
- `src/Contracts/SchemaMigration.php`
- `src/Contracts/SchemaValidator.php`
- `src/Contracts/RenderEngine.php`
- `src/Contracts/SecurityGate.php`
- `src/Contracts/Logger.php`
- `src/Registry/ElementRegistry.php`
- `src/Registry/PropertyRegistry.php`
- `src/Migration/MigrationRegistry.php`
- `src/Schema/PageSchemaValidator.php`
- `src/Compatibility/CompatibilityPolicy.php`
- `src/Infrastructure/WordPress/LegacyOptionPageRepository.php`
- `src/Infrastructure/WordPress/WordPressSecurityGate.php`
- `src/Infrastructure/WordPress/LegacyOptionLogger.php`
- `tests/Architecture/architecture-smoke.php`
- `tests/Architecture/page-schema-smoke.php`
- `tests/Architecture/assert-foundation-isolation.sh`
- `tests/Architecture/protected-domain-contract.sh`
- `.github/workflows/architecture-foundation-qa.yml`

These files are not wired into the WordPress runtime yet. Therefore the public v0.5.30 rendering path remains unchanged by this slice.

## QA gates for this slice

The Architecture Foundation workflow runs on PHP 8.0, 8.2 and 8.3 and must pass:

1. Foundation isolation guard against `origin/main`.
2. Protected Vehicle/Event/Gallery v0.5.30 contract test.
3. PHP syntax validation for all new architecture/test PHP files.
4. Registry and migration smoke tests.
5. Page schema 1.22 compatibility validation tests.
6. Explicit compatibility assertions that Vehicle, Event and Gallery remain on the legacy runtime during the foundation phase.
