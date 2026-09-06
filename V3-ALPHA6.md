# Visual Designer Manager V3 3.0.0-alpha.6

## V1 Updates UI parity + V3 release history

Alpha.6 repairs two regressions on **Opdateringer** after the V3 route cutover.

The V1 0.1.93 Updates page markup and Manager CSS were already present in V3, but `AdminController::enqueue()` still gated the shared Manager styles on the old `h18-clean-*` hook prefix. WordPress therefore rendered the V3 Updates page without the imported V1 Manager CSS.

The release-history reader also accepted only stable `x.y.z` version strings. V3 prereleases such as `3.0.0-alpha.5` were therefore filtered out, while the packaged `release-history.json` still contained only V1 entries.

Alpha.6 changes only the V3 build output needed to restore parity:

- canonical `vdm-*` admin hooks load the existing V1 Manager CSS again;
- the Updates page keeps the V1 cards, large version number, status badges, toolbar, checkpoint table and spacing;
- `releaseHistory()` accepts semantic prerelease labels such as `3.0.0-alpha.6`;
- `3.0.0-alpha.1` through `3.0.0-alpha.6` are prepended to the packaged release history;
- the complete V1 history beginning with `0.1.93` is retained below the V3 entries;
- the installed V3 row can therefore receive the existing `Installeret` badge;
- the visible updater notice now says `Visual Designer Manager → Opdateringer`;
- the V1 CSS files themselves are unchanged;
- Designer, viewport, frontend renderer, Alpha.5 site shell, layout model and storage migration are unchanged.

## Acceptance target

On `test4.hangar18.dk`, **Visual Designer Manager → Opdateringer** should visually match the V1 0.1.93 reference on `test3.hangar18.dk`, while showing the V3 updater state, V3 update-checkpoints and V3 Alpha.1–Alpha.6 versions above the retained V1 history.
