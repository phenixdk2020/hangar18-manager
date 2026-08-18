# Ultimate Designer — integration backlog after UD-120

**Status updated:** 18 August 2026  
**Current public release:** Hangar18 Manager v0.8.6

The UD-001..120 design backlog has architecture/core coverage. The integration backlog turns those services into usable wp-admin workflows **without converting the existing Hangar18 pages before the release gates are satisfied**.

## Non-negotiable migration rule

Existing page conversion is the last phase. Vehicle/Event/Gallery remain protected legacy domains until side-by-side visual/function regression and rollback rehearsal have passed.

The intended order is:

1. non-critical comparison page;
2. Hjem;
3. Om foreningen;
4. Kontakt;
5. Bliv medlem;
6. Vehicle/Event/Gallery only after separate compatibility acceptance;
7. legacy removal only after final acceptance.

## Current status summary

| Slice | Status | Current result |
|---|---|---|
| I1 Admin integration / shadow dashboard | ✅ Complete | Admin-only integration dashboard; no frontend replacement. |
| I2 Visual Header/Footer Builder | ✅ Complete · shadow | Visual templates and assignments exist without public cutover. |
| I3 Menu Builder v2 | ✅ Complete · shadow | Nested menu/presets/page chooser/accessibility preview. |
| I4 Side Health editor panel | ✅ Complete | Live read-only quality analysis; collapsed by default from v0.8.5. |
| I5 Asset Manager UI | ✅ Complete | Metadata/usage/focal point/duplicates/derivatives. |
| I6 Portability UI | ✅ Complete · isolated | Dry-run/import/export/backup/restore in isolated workspace. |
| I7 Permissions / Design Lock UI | ✅ Complete · shadow | Additive capabilities/roles and design-lock policy. |
| I8 AI UI/provider configuration | ✅ Complete · sandbox | Pending proposals only; no provider repository writes. |
| I9 Manual QA evidence dashboard | 🟡 Tooling complete | Manual browser/a11y/test2/V-E-G/rollback evidence still pending. |
| I10-A Planner/shadow workspace | ✅ Complete · v0.8.3 | Fixed order, blockers and copy-only shadow records. |
| I10-B Shadow acceptance ledger | ✅ Complete · v0.8.4 | Manual acceptance bound to exact shadow `SourceHash`. |
| UX-1 Auto-kasser/Tabel/Inspector | ✅ Complete · v0.8.5 | Equal-column boxes, visual Table tool and compact Side Health. |
| I10 preflight | ✅ Complete · v0.8.6 | Signed non-executable preflight with source-drift and identity checks. |
| I10-C Public comparison cutover | 🔒 Blocked | No activate/cutover/publish handler exists. |
| I10-D Core pages | 🔒 Blocked | Starts only after comparison acceptance. |
| I10-E Protected domains | 🔒 Blocked | Vehicle/Event/Gallery remain legacy. |
| I10-F Legacy removal | 🔒 Blocked | Last step after all final acceptances. |

## I1 — Admin integration / shadow dashboard — COMPLETE

- Load the namespaced architecture autoloader from the plugin runtime.
- Register an admin-only Ultimate Designer submenu.
- Show Site Builder/template/menu/asset/permission status from the extracted repositories.
- Show manual release gates separately from automated QA.
- No frontend renderer replacement or public page conversion.

## I2 — Visual Header/Footer Builder — COMPLETE IN SHADOW MODE

- Reuses the same page-state/template conventions as the extracted architecture.
- Header/Footer templates, assignments and previews are available in admin.
- Global/public assignment remains separated from the legacy frontend until controlled cutover.

## I3 — Menu Builder v2 — COMPLETE IN SHADOW MODE

- Shared menu data supports the planned presentation presets.
- Nested items have validation.
- Page chooser keeps page existence independent from menu membership.
- Accessibility/keyboard-oriented preview is represented.
- No public legacy menu replacement before acceptance.

## I4 — Side Health editor panel — COMPLETE

- Runs deterministic Design/Mobile/Accessibility/Performance/SEO analyzers.
- Links issues to concrete editor elements.
- Keeps analysis read-only.
- From v0.8.5 the panel starts collapsed so Inspector controls remain usable.

## I5 — Asset Manager UI — COMPLETE

- Collections/folders/tags over native WordPress Media IDs.
- Usage inspector.
- Responsive focal point support.
- WebP/AVIF derivative workflow preserves originals.
- SHA-256 duplicate reporting; no automatic destructive merge/delete.

## I6 — Portability UI — COMPLETE IN ISOLATED WORKSPACE

- Export page/global styles and selected artifacts.
- Import starts in dry-run.
- Conflict/remap/broken-reference reporting happens before confirmation.
- Automatic pre-import backup and restore path exist.
- Confirmed imports remain isolated from public page cutover.

## I7 — Permissions / Design Lock UI — COMPLETE IN SHADOW MODE

- Capability/role preview before additive installation.
- Named Ultimate Designer roles/capabilities.
- Design Lock policy and editable-input concepts.
- Existing legacy `edit_pages` behavior is preserved until runtime migration is approved.

## I8 — AI UI/provider configuration — COMPLETE AS SUGGESTION SANDBOX

- Provider-neutral settings boundary.
- Text/design/accessibility suggestions.
- Suggestions remain pending until explicit accept.
- Accepted proposals produce reversible apply/undo data rather than direct page mutation.
- Provider credentials are not stored as ordinary project content.

## I9 — Manual QA evidence dashboard — TOOLING COMPLETE, EVIDENCE PENDING

Tooling exists for recording the required manual gates, but the gates are not considered PASS until real evidence is entered.

Required evidence includes:

- Chrome;
- Edge;
- Firefox;
- Safari/WebKit;
- keyboard/screen-reader core flow;
- test2 live end-to-end;
- Vehicle/Event/Gallery visual/function regression;
- live-copy migration/rollback rehearsal.

Automated CI may support these gates but may not impersonate manual evidence.

## UX-1 — v0.8.5 Auto-kasser, Tabel and Inspector usability — COMPLETE

v0.8.5 added editor usability work outside the original I-number sequence:

- Auto-kasser derive equal desktop columns from child count on the existing Grid/Container schema.
- Each Kasse keeps individual typography/design/spacing/border/shadow/responsive controls.
- Tabel is a visual editing layer over the existing sanitized HTML element.
- Inspector integration follows the selected row after the legacy editor moves its settings body.
- Side Health starts collapsed and expands on demand.

This does not change the public runtime or migrate existing pages.

## I10 — Final controlled conversion (LAST)

1. Back up current state.
2. Convert one non-critical comparison page.
3. Compare legacy/new desktop/tablet/mobile output.
4. Verify save/preview/revision/rollback.
5. Convert Hjem, Om, Kontakt and Bliv medlem one at a time.
6. Convert Vehicle/Event/Gallery only after their protected compatibility gates pass.
7. Keep rollback until final acceptance.
8. Remove legacy code only after every converted domain is accepted.

### I10-A — Planner/shadow workspace — COMPLETE IN v0.8.3

- fixed conversion order;
- I9 gate evaluation;
- copy-only shadow records;
- no activate/cutover/publish handler.

### I10-B — Shadow acceptance ledger — COMPLETE IN v0.8.4

- manual page-specific evidence for desktop/tablet/mobile;
- save/preview/revision/rollback checks;
- acceptance is derived server-side;
- acceptance is bound to the exact shadow `SourceHash`;
- rebuilding/changing the shadow invalidates stale acceptance;
- this does not activate a public page.

### I10 preflight — COMPLETE IN v0.8.6

The preflight layer closes the technical gap before any future public cutover handler may be considered:

- compares current legacy state to shadow `SourceHash` to detect source drift;
- requires WordPress Page ID and permalink;
- evaluates I9 manual gates and fixed conversion sequence;
- validates shadow acceptance against the current source hash;
- signs an eligible immutable preflight snapshot with HMAC;
- time-limits the signed snapshot;
- makes old snapshots stale if state/identity/hash changes;
- persists only non-executable preflight records;
- hard-requires `Executable=false`;
- hard-requires `PublicMutationAvailable=false`.

There is still no activate/cutover/publish handler.

### I10-C — Public comparison-page cutover — BLOCKED

May only be implemented/exposed after all required I9 manual gates are actually PASS and the comparison page has current acceptance plus a valid preflight.

The first public cutover must:

- be limited to the non-critical comparison page;
- preserve WordPress identity/URL;
- take a pre-cutover backup;
- retain an explicit one-action rollback path;
- leave Vehicle/Event/Gallery untouched.

### I10-D — Core page cutover — BLOCKED

Order is fixed:

`Hjem → Om foreningen → Kontakt → Bliv medlem`

Each stage starts only after the prior page's visual/function/save/preview/revision/rollback acceptance is recorded.

### I10-E — Protected domain cutover — BLOCKED

Vehicle/Event/Gallery remain on the protected legacy runtime until:

- stored values/IDs remain compatible;
- public counts/order/filtering match;
- CSS/JS-relevant markup hooks match;
- desktop/tablet/mobile behavior matches;
- optional/custom fields are preserved;
- URLs/media references do not change;
- legacy data loads without manual repair;
- rollback remains available;
- separate human compatibility acceptance is recorded.

### I10-F — Legacy removal — BLOCKED

Legacy code is removed only after every converted page/domain has final acceptance and rollback retention requirements are satisfied.

## Release checkpoint

Current public release: **v0.8.6**.

The next project gate is **manual I9/test2 evidence**, not automatic conversion.
