# Ultimate Designer — integration backlog after UD-120

The UD-001..120 design backlog has architecture/core coverage, but several cores are intentionally passive. This backlog closes the gap between implemented services and usable wp-admin UI **without converting the existing Hangar18 pages yet**.

## Non-negotiable migration rule

Existing page conversion is the last phase. Vehicle/Event/Gallery remain protected legacy domains until side-by-side visual/function regression and rollback rehearsal have passed.

## I1 — Admin integration / shadow dashboard

- Load the namespaced architecture autoloader from the plugin runtime.
- Register an admin-only Ultimate Designer submenu.
- Show Site Builder/template/menu/asset/permission status from the extracted repositories.
- Show manual release gates separately from automated QA.
- No frontend hooks, renderer replacement or page writes.

## I2 — Visual Header/Footer Builder

- Reuse the same Sections tree and Inspector conventions as the page editor.
- Create/duplicate/rename/delete Header and Footer templates.
- Device previews and typography/design/layout controls.
- Global assignment remains shadow-only until cutover.
- Add explicit preview URL/token before any frontend activation.

## I3 — Menu Builder v2

- One menu data source for classic, transparent, sticky, floating, mega, off-canvas, fullscreen, side-rail and bottom-mobile presets.
- Drag/drop nested items with depth/cycle validation.
- Accessible keyboard preview.
- Visual mega-panel/component binding.
- No replacement of the current public menu until acceptance.

## I4 — Side Health editor panel

- Run deterministic Design/Mobile/Accessibility/Performance/SEO analyzers on the currently edited state.
- Link each issue to its concrete element in Navigator/Inspector.
- Show HardFailures separately from score.
- Never auto-rewrite the page.

## I5 — Asset Manager UI

- Collections/folders/tags over native WordPress Media IDs.
- Usage inspector before delete.
- Focal point UI.
- WebP/AVIF derivative planning/generation with original preserved.
- SHA-256 duplicate report; no automatic deletion.

## I6 — Portability UI

- Export page/global styles and selected components/templates/menus/forms.
- Import starts in dry-run.
- Conflict/remap/broken asset report before confirmation.
- Automatic pre-import backup and visible restore action.

## I7 — Permissions / Design Lock UI

- Preview capability/role changes before install.
- Designer/Editor/domain role recipes.
- Component editable inputs and design/structure lock controls.
- Preserve current legacy `edit_pages` behavior until migration is approved.

## I8 — AI UI/provider configuration

- Provider-neutral settings boundary.
- Text/layout/design/accessibility suggestion panels.
- Every suggestion remains pending until explicit accept.
- Accepted changes integrate with undo/revision; no provider gets repository write access.

## I9 — Manual QA evidence dashboard

- Record Chrome/Edge/Firefox/Safari brand checks.
- Record screen-reader core flow.
- Record test2 live E2E and Vehicle/Event/Gallery visual/function regression.
- Record live-copy migration/rollback rehearsal.
- Release readiness remains false while required evidence is missing.

## I10 — Final controlled conversion (LAST)

1. Back up current state.
2. Convert one non-critical comparison page.
3. Compare legacy/new desktop/tablet/mobile output.
4. Verify save/preview/revision/rollback.
5. Convert Hjem, Om, Kontakt and Bliv medlem one at a time.
6. Convert Vehicle/Event/Gallery only after their protected compatibility gates pass.
7. Keep rollback until final acceptance.
8. Remove legacy code only after every converted domain is accepted.

### I10 implementation slices

- **I10-A — Planner/shadow workspace (v0.8.3, complete):** fixed conversion order, I9 gate evaluation and copy-only shadow records. No activate/cutover/publish handler exists.
- **I10-B — Shadow acceptance ledger (v0.8.4):** manual page-specific evidence for desktop/tablet/mobile plus save/preview/revision/rollback. Acceptance is derived by the server and bound to the exact shadow `SourceHash`; rebuilding a shadow invalidates stale acceptance. This does not activate a public page.
- **I10-C — Public comparison-page cutover (blocked):** may only be implemented/exposed after all eight I9 manual gates are actually PASS. It must start with the non-critical comparison page and retain an explicit rollback path.
- **I10-D — Core page cutover (blocked):** Hjem → Om → Kontakt → Bliv medlem, one at a time, only after acceptance of the previous stage.
- **I10-E — Protected domain cutover (blocked):** Vehicle/Event/Gallery remain on the protected legacy runtime until their separate compatibility policy/gates are explicitly accepted.
- **I10-F — Legacy removal (blocked):** legacy code is removed only after every converted page/domain has final acceptance and rollback retention requirements are satisfied.
