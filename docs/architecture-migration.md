# Ultimate Designer architecture migration

**Status:** 19. august 2026  
**Current plugin:** Hangar18 Manager **v0.8.6**  
**Legacy compatibility baseline:** **v0.5.30**  
**Page-editor schema reference:** **1.22**

## Baseline and migration model

Ultimate Designer is being introduced with a **strangler/incremental migration**, not a rewrite from scratch.

The current plugin contains a modular namespaced architecture, wp-admin integration layers and conversion preflight tooling, while the existing legacy rendering/data path remains authoritative for existing public pages until a target has passed the defined compatibility and rollback gates.

The protected v0.5.30 baseline remains the behavioural reference for Vehicle/Event/Gallery.

## Protected domain contract

Vehicle, Event and Gallery are protected compatibility domains.

Until a replacement path has passed regression QA and separate compatibility acceptance, the following remain invariant:

1. Stored WordPress data and existing IDs.
2. Public URLs and existing shortcodes/routes.
3. Frontend HTML/CSS/JavaScript hooks required by current presentation.
4. Image selection, placement and responsive behaviour.
5. Alignment, field visibility and presentation settings.
6. Existing create/edit/delete admin workflows.
7. Optional/custom field preservation.
8. Rollback to the protected legacy runtime during transition.

The concrete baseline is characterized in `architecture-legacy-domain-contract-v0530.md`.

## Architecture target

The target architecture follows the Ultimate Designer design specification:

- namespaced modular PHP services;
- versioned schemas and migrations;
- element/property registries;
- repository/storage abstractions;
- centralized security/validation;
- deterministic render/style/data services;
- reusable components/templates;
- Site Builder for Header/Footer/Menu;
- generic Dynamic CMS;
- workflow/revisions/staging;
- Side Health;
- permissions/design lock;
- AI suggestions;
- portability/import/export;
- domain features such as Vehicle/Event/Gallery represented as schemas/presets/components on the generic engine rather than separate engines.

## Current implementation state

The architecture is no longer only a foundation slice. Through v0.8.6 the repository includes:

- Architecture Foundation + runtime bridge.
- UD-060 Vehicle/Event/Gallery starter schemas.
- E6 Site Builder.
- E7 Interaction.
- E8 Workflow/revisions/staging.
- E9 Assets.
- E10 Permissions.
- E11 Quality / Side Health.
- E12 AI suggestion layer.
- E13 Portability.
- E14 automated QA baseline.
- I1 Ultimate Designer wp-admin integration.
- I2 visual Header/Footer Builder in shadow/admin mode.
- I3 Menu UI v2 in shadow/admin mode.
- I4 Side Health live panel in the legacy page editor.
- I5 Asset Manager UI.
- I6 Import/Export UI with isolated workspace.
- I7 Permissions/Design Lock UI.
- I8 AI UI/provider boundary.
- I9 Manual QA evidence dashboard.
- I10 planner, shadow-copy, acceptance ledger and signed cutover preflight.
- v0.8.5 Auto-kasser, visual Table tool and collapsed Side Health Inspector behaviour.
- v0.8.6 source-drift detection and signed non-executable preflight.

## Legacy data compatibility

The existing page-editor state remains in WordPress option:

`hangar18_manager_pages_v1`

It remains keyed by page slug and uses schema 1.22 fields including:

- `Version`
- `PageSlug`
- `PageTitle`
- `ContentVersion`
- `DataContextType`
- `DataContextEntryId`
- `Sections`

This option is still treated as authoritative legacy source data during the conversion-preparation phase.

The architecture adapters preserve the existing slug-keyed model and do not silently replace IDs or URLs.

## Current I9 manual gates

The following must be manually evidenced before public I10 cutover can be exposed:

1. latest Chrome brand test;
2. latest Edge brand test;
3. latest Firefox brand test;
4. latest Safari brand test;
5. screen-reader core flow;
6. `test2` live-site end-to-end test;
7. Vehicle/Event/Gallery visual/function regression;
8. migration/rollback on a live copy.

Automated CI/preflight cannot mark these manual gates as passed.

## I10 conversion sequence

The order is fixed:

1. non-critical comparison page;
2. Hjem;
3. Om foreningen;
4. Kontakt;
5. Bliv medlem;
6. Vehicle/Event/Gallery last;
7. legacy removal only after final acceptance.

A later stage cannot become eligible until the required prior stage is accepted.

## I10 safety layers implemented through v0.8.6

### Planner / shadow workspace — v0.8.3

- computes ordered eligibility and blockers;
- creates copy-only shadow state;
- does not modify public WordPress posts, URLs or the legacy option.

### Shadow acceptance — v0.8.4

- requires manual page-specific desktop/tablet/mobile/save/preview/revision/rollback checks;
- binds acceptance to the exact shadow `SourceHash`;
- a regenerated shadow makes old acceptance stale.

### Source-drift + signed cutover preflight — v0.8.6

Before a future cutover can even be considered, the preflight verifies:

- all required I9 manual evidence;
- correct conversion sequence;
- current shadow acceptance;
- current legacy-state hash equals the shadow source hash;
- WordPress page ID is stable;
- permalink is present and current;
- target is not blocked by the protected-domain policy.

An eligible preflight is HMAC-signed and time-limited.

Critically:

- `Executable=false`
- `PublicMutationAvailable=false`
- no activate/cutover/publish handler exists in this phase.

The signed preflight is proof that the state is eligible for a **future separately approved** activation mechanism; it is not an activation token.

## Protected Vehicle/Event/Gallery rule

Vehicle/Event/Gallery stay on the v0.5.30-compatible legacy renderer until:

- all core pages have passed the controlled sequence;
- protected visual/function regression is documented;
- schema/data/URL/media compatibility is proven;
- a separate compatibility policy decision allows the domain to leave legacy runtime;
- rollback remains available.

## QA state

Architecture QA runs the relevant matrix on PHP **8.0, 8.2 and 8.3**, including:

- protected-domain contract;
- schema/runtime bridge/compatibility tests;
- E6–E14 smoke tests;
- I1–I10 integration/safety tests;
- security audit;
- performance budget;
- migration/rollback test;
- end-to-end tests;
- JavaScript syntax;
- browser-engine regression on Chromium/Firefox/WebKit.

This automated QA complements but does not replace the manual I9 evidence.

## Next migration step

The next legitimate migration activity is **manual QA/evidence on `test2`**, not public conversion.

After manual gates are PASS:

1. refresh the comparison-page shadow;
2. record acceptance against its current source hash;
3. run signed preflight;
4. design and approve an explicit comparison-page activation/rollback mechanism;
5. cut over the comparison page only;
6. compare old/new output and prove rollback;
7. continue one page at a time;
8. handle Vehicle/Event/Gallery last.
