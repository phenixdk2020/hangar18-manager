# Visual Designer Manager V3 3.0.0-alpha.7

## V1 Style Recovery & Shared Main Menu

Alpha.7 fixes two acceptance findings from the direct V1/test3 versus V3/test4 export comparison.

### 1. Duplicate historical style harmonization

The V1 `SiteDesignHarmonizer` is a historical v0.1.72 one-time migration. Portable site import carries the layout/history but not its historical DONE marker. On test4 the retained V1 runtime therefore executed the harmonizer a second time on these six pages:

- Om foreningen
- Køretøjer og materiel
- Events
- Billedgalleri
- Bliv medlem
- Kontakt

The V3 export contains a second history entry named `Design harmoniseret med Hjem (v0.1.72)` on all six pages after import. Hjem is not a harmonizer target, which explains why its colours remained correct.

Alpha.7 no longer registers the historical `SiteDesignHarmonizer` in V3. `V3StyleRecovery` detects the duplicated history entry and compares the model immediately before and after the bad second pass. It restores only props changed by that pass and only when the current prop still equals the bad value. Geometry, hierarchy, order and later user edits are preserved. A normal Designer version and a backup meta are written for rollback.

### 2. Footer Genveje follows Header main menu

The imported Footer uses a static HTML text block for Genveje. Alpha.7 converts that block to a normal vertical VDM Menu element. Its menu ID is synchronized from the resolved Header's primary Menu, and a `wp_nav_menu_args` filter resolves the Header menu dynamically on the frontend. Menu items, labels, order and URLs are therefore maintained in one WordPress menu only.

## Protected behavior

Alpha.7 does not rewrite the V1 Designer, viewport, frontend Renderer, responsive Renderer, site shell, LayoutModel, TemplateLayoutModel, Alpha.3 storage migration or Manager CSS. Those files are protected byte-for-byte by the build gate.
