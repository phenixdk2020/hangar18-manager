# Ultimate Designer — integration backlog after UD-120

**Statusdato:** 19. august 2026  
**Aktuel pluginbaseline:** Hangar18 Manager **v0.8.6**

The UD-001..120 design backlog now has architecture/core coverage and the wp-admin integration backlog is largely implemented. The remaining work is deliberately concentrated in manual QA evidence and the final controlled conversion. **Existing Hangar18 pages are still not converted.**

## Non-negotiable migration rule

Existing page conversion is the last phase. Vehicle/Event/Gallery remain protected legacy domains until side-by-side visual/function regression, compatibility proof and rollback rehearsal have passed.

No automated QA result may replace a required manual/live acceptance gate.

## Status overview

| Phase | Status | Delivered |
|---|---|---|
| I1 — Admin integration / shadow dashboard | ✅ Complete | Admin-only Ultimate Designer dashboard; no frontend hooks or renderer replacement. |
| I2 — Visual Header/Footer Builder | ✅ Complete in shadow/admin | Shared Sections tree, visual editing, typography/design controls and admin preview. Public assignment remains inactive. |
| I3 — Menu Builder v2 | ✅ Complete in shadow/admin | Nested drag/drop, presets, keyboard preview, mega component binding and explicit page include/exclude. |
| I4 — Side Health editor panel | ✅ Complete | Live/read-only Design/Mobile/Accessibility/Performance/SEO analysis with element links; collapsed by default. |
| I5 — Asset Manager UI | ✅ Complete | Collections/tags/usage/focal point/derivatives/duplicate reporting over native WordPress Media IDs. |
| I6 — Portability UI | ✅ Complete | Dry-run-first import, signed plans, conflict/remap report, isolated workspace, backup/restore. |
| I7 — Permissions / Design Lock UI | ✅ Complete | Additive capabilities/roles and design-lock policy; legacy `edit_pages` preserved. |
| I8 — AI UI/provider configuration | ✅ Complete | Provider-neutral registry/settings, no credentials in options, pending suggestions and reversible Apply/Undo plans. |
| I9 — Manual QA evidence dashboard | 🟡 Framework complete | Evidence ledger and copy-only rollback preflight exist; required live/manual evidence is still pending. |
| I10 — Final controlled conversion | 🟡 Preflight complete / cutover locked | Planner, shadow workspace, acceptance ledger, source-drift checks and signed non-executable preflight are implemented. |

## I1 — Admin integration / shadow dashboard — COMPLETE

Delivered in v0.7.4:

- namespaced architecture autoloader wired safely into wp-admin;
- Ultimate Designer submenu;
- status cards for Site Builder, menus, assets, portability, permissions, AI, QA and conversion;
- manual release gates shown separately from automated QA;
- no frontend hooks, renderer replacement or page writes from the integration dashboard.

## I2 — Visual Header/Footer Builder — COMPLETE IN SHADOW/ADMIN

Delivered in v0.7.5:

- shared `Sections` tree and Inspector conventions;
- Header/Footer template list and visual editor;
- drag/reorder and keyboard movement;
- typography/design/layout fields with server-side roundtrip validation;
- live admin preview;
- global assignment remains shadow-only.

Public Header/Footer replacement is not enabled.

## I3 — Menu Builder v2 — COMPLETE IN SHADOW/ADMIN

Delivered in v0.7.6 and extended in v0.7.8:

- one generic menu data source;
- nested drag/drop with validation;
- desktop/mobile presentation presets;
- keyboard preview;
- optional icon/badge/mega-panel `ComponentId`;
- **available pages are explicitly selected into the menu**; pages may exist without being menu items;
- removing a menu item does not delete or change the WordPress page.

Public menu replacement is not enabled.

## I4 — Side Health editor panel — COMPLETE

Delivered in v0.7.7 and UX-adjusted in v0.8.5:

- deterministic Design/Mobile/Accessibility/Performance/SEO analysis on the currently edited state;
- issue links to concrete editor elements;
- hard failures kept separate from the numeric score;
- read-only analysis — never auto-rewrites content;
- Side Health starts **collapsed** in Inspector so normal element settings remain visible.

## I5 — Asset Manager UI — COMPLETE

Delivered in v0.7.8:

- collections/folders/tags over native WordPress Media IDs;
- usage inspector;
- WordPress post-meta aware MediaId detection;
- focal point UI;
- WebP/AVIF derivatives named `*.h18.webp` / `*.h18.avif`;
- existing originals and existing derivatives are never overwritten;
- SHA-256 duplicate reporting;
- no automatic deletion.

## I6 — Portability UI — COMPLETE

Delivered in v0.7.9:

- page/global-style export and validation;
- artifact export/import for components/templates/menus/forms;
- import always begins as dry-run;
- conflict/remap/broken-asset report;
- signed plan token bound to exact package/strategy/plan;
- explicit confirmation before mutation;
- automatic pre-import backup;
- imports write only to an isolated Portability Workspace in this phase;
- page cutover remains reserved for I10.

## I7 — Permissions / Design Lock UI — COMPLETE

Delivered in v0.8.0:

- preview capability/role changes before installation;
- named role/capability recipes;
- design/structure lock controls;
- component editable inputs;
- additive-only installation — no automatic `remove_role`, `remove_cap` or user-role reassignment;
- current legacy `edit_pages` access remains available during migration.

## I8 — AI UI/provider configuration — COMPLETE

Delivered in v0.8.1:

- provider-neutral registry;
- settings store enabled/provider-id only — not provider credentials;
- text/layout/design/accessibility suggestion sandbox;
- suggestions remain pending until explicit acceptance;
- signed acceptance is bound to exact proposal state;
- accepted proposal yields reversible Apply/Undo data;
- no direct page-write path.

## I9 — Manual QA evidence dashboard — FRAMEWORK COMPLETE / EVIDENCE PENDING

Delivered in v0.8.2.

Required manual evidence:

1. latest Chrome brand test;
2. latest Edge brand test;
3. latest Firefox brand test;
4. latest Safari brand test;
5. screen-reader core flow;
6. `test2` live-site E2E;
7. Vehicle/Event/Gallery visual/function regression;
8. migration/rollback on a live copy.

The automated rollback simulation/preflight does **not** satisfy the live-copy gate.

Release readiness remains false while any required manual evidence is missing.

## I10 — Final controlled conversion — ACTIVE, PUBLIC CUTOVER STILL LOCKED

Fixed conversion order:

1. comparison page;
2. Hjem;
3. Om foreningen;
4. Kontakt;
5. Bliv medlem;
6. Vehicle/Event/Gallery only after protected compatibility gates;
7. legacy removal last.

### I10 implementation slices

- **I10-A — Planner/shadow workspace (v0.8.3, complete):**
  - fixed conversion order;
  - global I9 gate evaluation;
  - copy-only shadow records;
  - no activate/cutover/publish handler.

- **I10-B — Shadow acceptance ledger (v0.8.4, complete):**
  - manual page-specific evidence for desktop/tablet/mobile plus save/preview/revision/rollback;
  - acceptance derived server-side;
  - acceptance bound to exact shadow `SourceHash`;
  - rebuilding a shadow invalidates stale acceptance.

- **UX-1 — Auto-kasser + Table + Side Health collapse (v0.8.5, complete):**
  - Auto-kasser reuse Grid/Container schema and distribute children evenly;
  - 1 child = 100%, 2 = 50/50, 3 ≈ 33.3% each, up to 6 columns;
  - each box retains individual typography/design/spacing/border/shadow/responsive settings;
  - visual Table tool over sanitized HTML;
  - Side Health collapsed by default.

- **I10-C — Signed cutover preflight (v0.8.6, complete):**
  - compares current legacy-state hash with accepted shadow `SourceHash`;
  - checks current WordPress Page ID and permalink;
  - checks I9 manual QA, conversion sequence and shadow acceptance;
  - HMAC-signs the immutable preflight snapshot;
  - token expires and becomes invalid if state drifts;
  - `Executable=false`;
  - `PublicMutationAvailable=false`;
  - still no activate/cutover/publish handler.

- **I10-D — Public comparison-page cutover (BLOCKED):**
  - may only be designed/exposed after all eight I9 manual gates are actually PASS;
  - must retain explicit backup and rollback;
  - starts with a non-critical comparison page only.

- **I10-E — Core page cutover (BLOCKED):**
  - Hjem → Om → Kontakt → Bliv medlem;
  - one at a time;
  - previous stage must remain accepted and non-stale.

- **I10-F — Protected domain cutover (BLOCKED):**
  - Vehicle/Event/Gallery remain on protected legacy runtime;
  - separate compatibility proof and policy change are required.

- **I10-G — Legacy removal (BLOCKED):**
  - remove legacy code only after final acceptance of every converted page/domain and after rollback retention is no longer required.

## Current next actions

1. Run and record all I9 manual QA evidence on `test2`.
2. Fix any live QA / Side Health issues without converting existing pages.
3. Create or refresh the comparison-page shadow copy.
4. Record page-specific acceptance against the current `SourceHash`.
5. Run and persist the v0.8.6 signed preflight.
6. Only then design/approve a separate public activation + rollback mechanism for the comparison page.
