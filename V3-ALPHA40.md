# Visual Designer Manager V3 — Alpha.40

Version: `3.0.0-alpha.40`

## Scope

Alpha.40 fixes a regression in the collapsible **Elementer** side panel.

The Elementer/Lag feature wrapped every child of the palette into a tab panel. That included the permanent `Elementer` heading and its collapse/reopen toggle created by `editor-v0121-panels.js`.

When the palette was collapsed, the tab panels were hidden by CSS. The reopen toggle was therefore hidden together with the content, leaving only an empty narrow rail and no visible way to restore the Elementer palette.

## Fix

- The permanent Elementer heading/toggle remains a **direct child** of `.h18-clean-palette`.
- Only the actual Elementer/Lag tab content is wrapped.
- The panel controller has a defensive fallback: if the direct heading is missing, it creates one before installing the toggle.
- Inspector behavior is unchanged.
- Alpha.39 fixes are retained.

## Acceptance

1. Open Visual Designer with **Elementer** visible.
2. Click the Elementer collapse arrow.
3. The palette collapses to the narrow left rail.
4. A visible **›** reopen button remains in the rail.
5. Click it and verify Elementer/Lag and all + element buttons return.
6. Repeat using **⇔ Mere canvas** to collapse both panels.
7. Verify both left Elementer and right Inspector have visible reopen buttons.
8. Reload the editor while Elementer is collapsed and verify the reopen button is still visible.
