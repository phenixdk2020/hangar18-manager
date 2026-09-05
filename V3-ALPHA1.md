# Visual Designer Manager V3 — 3.0.0-alpha.1

## Purpose

This is the first V3 baseline and is deliberately derived from the released/tested V1 `0.1.93` runtime at commit `dc3bad403c764f4ec123a526333a781d05dde491`.

V3 Alpha.1 is not a Designer reimplementation.

## Preservation rule

Before packaging, the release workflow requires `clean/hangar18-manager/` to be byte-identical to the V1 `0.1.93` release baseline. The existing V1 syntax/current regression gates are then executed.

The build copies that runtime into the new WordPress plugin package and changes only the package/bootstrap/update identity required for the new plugin basename:

- folder: `visual-designer-manager`
- main file: `visual-designer-manager.php`
- version: `3.0.0-alpha.1`
- updater slug/plugin basename and V3 manifest channel

Every other Designer/renderer/admin runtime file is SHA-256 compared with the V1 source and must remain byte-identical for this release.

## Explicitly preserved V1 behavior

The release gate verifies the existing V1 palette drag/drop chain, canvas drop handling, V1 cell placement model, resize, Undo/Redo and the existing V1 release regression gates.

## Compatibility identifiers

Alpha.1 intentionally retains the V1 runtime/storage compatibility identifiers internally. They are not mechanically renamed in this release because doing so would increase functional risk before the V1-behavior baseline is established. Internal identifier/storage migration will be a later V3 refactor stage and must preserve this baseline behavior.

## Package

`dist/visual-designer-manager-v3.0.0-alpha.1.zip`

SHA-256: `9b95ef4989f233a6b6c0d0fd0fbf35c0a0c03e9ca5d4bec9189d0add04434164`

Updater manifest: `v3-update.json`

## Acceptance

- `test3.hangar18.dk` remains the V1 golden reference.
- `test4.hangar18.dk` is the V3 acceptance target.
- V3 is not promoted to `3.0.0` until the V1 behavior and visual output are accepted.
