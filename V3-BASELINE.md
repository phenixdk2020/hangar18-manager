# Visual Designer Manager V3 baseline

## Source baseline

V3 starts from the released and tested V1 `0.1.93` codebase at commit `dc3bad403c764f4ec123a526333a781d05dde491`.

## Non-negotiable migration rule

V3 is a clean technical refactor of the working V1 product. It is not a Designer reimplementation.

The following behavior must remain functionally identical unless an explicit defect fix is separately approved:

- Designer palette and drag/drop behavior
- canvas movement and resize behavior
- responsive breakpoints
- inspector controls
- Header/Footer workflows
- Menu workflows
- page/version workflows
- Events, Vehicles and Gallery workflows
- forms
- backup/export/update workflows
- frontend rendering

## Allowed V3 changes before parity acceptance

- plugin/folder/package identity
- namespaces/classes/constants
- options/meta/action/nonce/REST identifiers
- CSS/JS technical prefixes
- build/release identity
- one-time storage migration to the new VDM identifiers
- regression/identity gates required to prove the refactor

## Acceptance references

- `test3.hangar18.dk`: V1 golden visual/functional reference
- `test4.hangar18.dk`: V3 acceptance target

V3 must not be promoted to `3.0.0` until the migrated test4 site matches the working V1 reference across the established Desktop/Laptop/Tablet/Mobile workflows.

## Initial target

`3.0.0-alpha.1` — V1 Clean Identity Baseline.
