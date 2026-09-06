# Visual Designer Manager V3 3.0.0-alpha.6

## V1 Updates UI parity

Alpha.6 repairs the admin-style regression introduced by the canonical `vdm-*` admin route cutover.

The V1 0.1.93 Updates page markup and Manager CSS were already present in V3, but `AdminController::enqueue()` still gated the shared Manager styles on the old `h18-clean-*` hook prefix. WordPress therefore rendered the V3 Updates page without the imported V1 Manager CSS.

Alpha.6 changes only the V3 build output needed to restore that styling:

- canonical `vdm-*` admin hooks load the existing V1 Manager CSS again;
- the Updates page keeps the V1 cards, large version number, status badges, toolbar, checkpoint table and spacing;
- the visible updater notice now says `Visual Designer Manager → Opdateringer`;
- the V1 CSS files themselves are unchanged;
- Designer, viewport, frontend renderer, Alpha.5 site shell, layout model and storage migration are unchanged.

## Acceptance target

On `test4.hangar18.dk`, **Visual Designer Manager → Opdateringer** should visually match the V1 0.1.93 reference on `test3.hangar18.dk`, while continuing to use the V3 updater manifest, Alpha.6 version and V3 update/checkpoint data.
