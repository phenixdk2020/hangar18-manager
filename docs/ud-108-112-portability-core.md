# E13 Portability core — UD-108 to UD-112

## UD-108 Page + global styles JSON

`PagePackageService` exports the normalized page state together with global styles, package schema version, page schema version and SHA-256 checksums. Import validates JSON, package/page schema, page state and checksums before returning any data. A successful roundtrip returns byte-semantically identical page/global-style values.

## UD-109 Components/templates/menus/forms

`ArtifactPackageService` packages selected artifacts with stable `ExportId` values. `ImportPlanner` detects target-ID collisions before writes. `remap` creates deterministic collision-free IDs, while `skip` and `reject` remain explicit strategies. Portable cross-artifact references use `artifact://<ExportId>` and are resolved through the final mapping table.

## UD-110 Asset manifest/package mapping

`AssetManifestService` validates an asset manifest with SHA-256 checksums and maps package assets to target native Media IDs by content hash. Missing assets are returned in `Broken`; they are never silently dropped. Portable asset references use `asset://asset:<SourceMediaId>` and must have a target mapping before execution.

## UD-111 Dry-run / conflicts

Planning is dry-run by default and has no repository write method. A plan exposes `Conflicts`, `Mappings`, `Actions`, `Valid` and `MutationAllowed`. `ImportExecutor` refuses dry-run, invalid, unconfirmed or blocked plans. Reference errors abort the target transaction.

## UD-112 Automatic backup

Before any confirmed import write, `ImportExecutor` snapshots the target repository and persists a checksum-protected backup revision. A failed import leaves the backup intact while rolling the target repository back. The existing E8 `StagingService` already takes a pre-publish backup before replacing an existing public state; E13 regression tests verify this behavior remains active.

## Compatibility boundary

This slice does not import or convert existing Hangar18 pages automatically. It establishes the package/plan/backup engine required for the final migration phase. Vehicle/Event/Gallery and legacy URLs/rendering remain unchanged.
