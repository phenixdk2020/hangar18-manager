# Ultimate Designer architecture migration

**Status updated:** 18 August 2026  
**Current public release:** Hangar18 Manager v0.8.6

## Baseline and compatibility anchor

- Legacy runtime reference: Hangar18 Manager v0.5.30.
- Legacy page-editor schema reference: 1.22.
- Current public plugin release: v0.8.6.
- v0.5.30 remains the protected behavioral reference for Vehicle/Event/Gallery until those domains explicitly pass replacement compatibility gates.
- The architecture migration follows a strangler model; extracted services and admin/shadow tooling may advance without forcing a public renderer switch.

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

## Non-negotiable final-phase conversion rule

Existing public pages are converted **last**, after the generic engine, admin tooling, QA evidence, acceptance and rollback mechanisms have been proven.

The sequence is fixed:

1. create/refresh backup and rollback reference;
2. use one deliberately non-critical comparison page;
3. compare legacy and new output on desktop, tablet and mobile;
4. verify save, preview, revision and rollback;
5. convert Hjem;
6. convert Om foreningen;
7. convert Kontakt;
8. convert Bliv medlem;
9. convert Vehicle/Event/Gallery only after separate protected-domain compatibility acceptance;
10. remove legacy paths only after final acceptance.

This rule prevents editor/architecture work from silently turning into a site migration.

## Migration method

The refactor uses a strangler approach:

1. Add contracts, registries and services beside the legacy runtime.
2. Characterize existing behaviour with tests/fixtures.
3. Extract one responsibility without changing its public behaviour.
4. Compare old and new output.
5. Integrate admin/shadow workflows without switching public rendering.
6. Collect manual QA and page-specific acceptance.
7. Build a non-executable cutover preflight.
8. Expose public cutover only as a later, separately approved slice.
9. Keep an explicit rollback path until the new responsibility is stable.
10. Remove legacy code only after final acceptance.

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
- Human compatibility acceptance is recorded from real test evidence.

## Architecture target

The target continues to follow the approved Ultimate Designer design specification:

- namespaced modular PHP layer;
- versioned schemas and migrations;
- element and property registries;
- repository/storage abstraction;
- centralized security/validation;
- deterministic render/style engines;
- admin/editor integration boundary;
- Site Builder, Dynamic CMS, workflow, assets, permissions, quality, AI and portability as generic services;
- domain features such as Vehicle/Event/Gallery represented as schemas/presets/components on the generic engine rather than separate permanent engines.

The long-term editor target remains schema-driven and compatible with a future React/TypeScript shell. The migration does not require rewriting stable legacy UI in one step.

## Legacy data compatibility characterized

The existing v0.5.30 page-editor state is stored in WordPress option `hangar18_manager_pages_v1`, keyed by page slug. The normalized page state uses schema 1.22 with:

- `Version`
- `PageSlug`
- `PageTitle`
- `ContentVersion`
- `DataContextType`
- `DataContextEntryId`
- `Sections`

The repository boundary therefore uses a string page key and the compatibility adapter preserves the exact existing option name and slug-keyed map. No forced ID conversion or alternate public storage is introduced during the protected migration phase.

The v0.5.30 admin log is stored in `hangar18_manager_log` with fields `time`, `level`, `checkpoint`, `message` and `user`, retaining the newest 750 entries. `LegacyOptionLogger` preserves that same option, record shape and retention policy for compatibility.

## Implemented architecture/core coverage

The original UD-001..120 backlog now has architecture/core coverage across the extracted namespaces and contract tests.

Major implemented areas include:

- Core/autoload/version/runtime bridge.
- Contracts and registries.
- Schema validation and migrations.
- Compatibility comparison and protected-domain policies.
- Dynamic data starter presets for Vehicle/Event/Gallery.
- Site Builder services.
- Interaction/form/action services.
- Workflow/revision/staging/preview services.
- Asset services.
- Permissions/Design Lock services.
- Quality/Side Health analyzers.
- AI suggestion services.
- Portability/import/export/backup services.
- QA/release/readiness/rollback services.

Several components intentionally remain passive, shadow-only or non-executable until the I9/I10 gates are satisfied.

## wp-admin integration progress

The post-UD-120 integration backlog has been implemented through the following slices:

| Slice | State |
|---|---|
| I1 Admin integration dashboard | Complete |
| I2 Header/Footer Builder | Complete in shadow mode |
| I3 Menu Builder v2 | Complete in shadow mode |
| I4 Side Health | Complete |
| I5 Asset Manager | Complete |
| I6 Portability workspace | Complete / isolated |
| I7 Permissions / Design Lock | Complete / shadow-compatible |
| I8 AI proposal UI | Complete / suggestion sandbox |
| I9 Manual QA evidence dashboard | Tooling complete; manual evidence pending |
| I10-A planner/shadow workspace | Complete in v0.8.3 |
| I10-B shadow acceptance ledger | Complete in v0.8.4 |
| UX v0.8.5 | Auto-kasser, Table tool, Inspector integration, compact Side Health |
| I10 signed preflight | Complete in v0.8.6 |
| I10-C public comparison cutover | Blocked |
| I10-D core pages | Blocked |
| I10-E Vehicle/Event/Gallery | Blocked / protected legacy |
| I10-F legacy removal | Blocked |

## v0.8.5 editor UX integration

v0.8.5 improves the existing editor without changing the public runtime:

- Auto-kasser derive equal desktop columns from child count using the existing Grid/Container schema.
- Each Kasse retains independent design/typography/spacing/border/shadow/responsive properties.
- Tabel is a visual editing layer over the existing sanitized HTML element.
- Inspector integration follows the selected row even when the legacy editor moves the settings body.
- Side Health starts collapsed and expands on demand.

These changes are admin/editor enhancements, not page conversion.

## v0.8.6 signed cutover preflight

v0.8.6 adds a locked technical preflight before any future public cutover can be considered.

The preflight checks:

- current legacy state versus the shadow `SourceHash`;
- WordPress Page ID;
- WordPress permalink;
- global I9 manual evidence status;
- fixed I10 conversion order;
- page-specific shadow acceptance;
- current source hash consistency.

If eligible, the exact preflight snapshot may be HMAC-signed with an expiry. The token is bound to the immutable snapshot; source/identity/blocker changes invalidate the prior state.

Hard safety properties for this phase:

- `Mode = cutover-preflight-only`
- `Executable = false`
- `PublicMutationAvailable = false`
- no activate handler;
- no cutover handler;
- no publish handler;
- no WordPress post/URL mutation;
- no mutation of `hangar18_manager_pages_v1` by the preflight.

The preflight answers only: **would this target be technically eligible for a future separately implemented cutover?**

## Current QA state

The automated architecture/contract matrix is green on PHP:

- 8.0
- 8.2
- 8.3

Automated QA includes architecture/schema/runtime bridge/compatibility/core/integration/security and the v0.8.5/v0.8.6 contracts.

Automated checks do **not** close the manual I9 gates.

The remaining manual/live evidence includes:

- Chrome;
- Edge;
- Firefox;
- Safari/WebKit;
- keyboard/screen-reader flow;
- test2 live E2E;
- Vehicle/Event/Gallery visual/function regression;
- migration/rollback rehearsal on a live copy.

## Current gate

The architecture is deliberately stopped before public mutation.

The next project gate is:

> Complete and record I9 manual/live QA on test2, then obtain current shadow acceptance and signed preflight for the non-critical comparison page.

Only after that evidence exists should a separate I10-C public comparison-page cutover slice be designed and reviewed.

Hjem, Om, Kontakt, Bliv medlem and especially Vehicle/Event/Gallery remain later stages.
