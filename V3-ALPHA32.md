# Visual Designer Manager V3 — Alpha.32

Version: `3.0.0-alpha.32`

## Problem

The WordPress **Opdateringer** page could report `3.0.0-alpha.29` as the newest GitHub version even after Alpha.30 and Alpha.31 had been built.

The installed updater was working as designed: it reads the stable manifest at:

`v3-clean-refactor/v3-update.json`

That stable release manifest had simply not been advanced after Alpha.29. Its package URL and checksum therefore also still referenced Alpha.29.

## Fix

Alpha.32 fixes the **release channel**, not only the text shown in the admin UI.

After Alpha.32 QA succeeds, the release workflow publishes these two files together to the stable `v3-clean-refactor` branch:

- `dist/visual-designer-manager-v3.0.0-alpha.32.zip`
- `v3-update.json`

The manifest contains the exact SHA-256 of the installer ZIP and points to the ZIP on the same stable branch.

Publishing both files in the same Git commit prevents the update manifest from pointing to a package that has not yet been published.

## Existing installations

The updater URL inside V3 remains unchanged. Existing V3 installations therefore require no local updater configuration change.

After Alpha.32 is published, **Tjek GitHub-opdatering** should resolve the stable manifest as `3.0.0-alpha.32`.

## Regression scope

Alpha.32 deliberately leaves Alpha.31 frontend behavior intact, including:

- Moduldesign → Afstand til Footer (0–200 px)
- Event, Gallery and Vehicle detail Footer spacing
- Alpha.30 Footer parity
- Event Program line-break repair
- linked Event-gallery CTA
- Website-menu binding in Header/Footer

## Release-channel acceptance

1. Alpha.32 build and PHP/JavaScript validation must pass.
2. The generated plugin must still point to `v3-clean-refactor/v3-update.json`.
3. The installer ZIP must pass archive validation.
4. The release manifest must contain version `3.0.0-alpha.32`.
5. The manifest package URL must point to `dist/visual-designer-manager-v3.0.0-alpha.32.zip` on `v3-clean-refactor`.
6. The manifest SHA-256 must exactly match the published ZIP.
7. ZIP and manifest must be committed to the stable release branch together.
