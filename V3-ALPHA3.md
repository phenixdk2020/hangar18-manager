# Visual Designer Manager V3 — 3.0.0-alpha.3

## Purpose

Alpha.3 is the **V1 Storage Migration & Import Baseline**. It remains a deterministic build from the released/tested V1 `0.1.93` runtime at commit `dc3bad403c764f4ec123a526333a781d05dde491`.

This release does not reimplement the Designer, renderer or user workflows.

## Canonicalized active storage

Alpha.3 changes only active content/design persistence to VDM identifiers:

- page layout, version and history post meta
- Header/Footer registry, defaults, per-template model/settings/history/version and per-page assignment
- collection/module design post meta
- Vehicle and Event field registries
- VDM menu snapshot history
- module record post type and module record metadata

Site identity fields already use `vdm_*` and are unchanged.

## Deliberately not renamed in Alpha.3

Operational action/nonces, admin slugs, CSS/JS selectors, diagnostics storage, updater cache/backup keys and historical migration markers stay unchanged. They are not imported site content and renaming them here would add risk without improving the import baseline.

## Migration safety contract

`V3StorageMigration` runs automatically after updating from Alpha.2.

- Legacy V1 values are never deleted or overwritten.
- Canonical values are copied only when missing.
- An existing canonical value is reused only when its serialized digest matches the legacy value.
- Conflicting values are reported, not overwritten.
- Historical template option families are copied by prefix.
- Old `h18_module_item` records are duplicated to `vdm_module_item`; the original posts remain in place.
- A pre-migration digest/count manifest is saved as `vdm_v3_storage_backup_manifest_v1`.
- Migration result and verification are saved as `vdm_v3_storage_migration_v1`.
- Re-running after a successful migration is a no-op.

## Import boundary

After Alpha.3 is installed and its migration has completed, `test3.hangar18.dk` may be exported using the tested V1 `Eksporter alt` workflow and imported into `test4.hangar18.dk` using the VDM portable-package preflight/import flow.

The semantic V1 portable package is imported through the current V3 models, so newly imported page/layout, Header/Footer, field and module data is written directly to the canonical VDM storage identifiers.

## Acceptance

- `test3.hangar18.dk` remains the V1 golden reference.
- `test4.hangar18.dk` becomes the persistent V3 imported acceptance site after this release.
- Legacy storage is retained until the imported site is accepted.
- No promotion to V3 final before Desktop/Laptop/Tablet/Mobile visual and functional acceptance.
