# Visual Designer Manager V3 3.0.0-alpha.5

## True Site Shell & Designer/Live Parity

Alpha.5 addresses the acceptance defects observed on test4 after importing the V1 0.1.93 site package.

### Scope

- VDM layout pages take ownership of the WordPress frontend template through `template_include`.
- The active WordPress theme no longer renders its own header, footer or page title around a VDM page.
- The standalone VDM template retains normal WordPress lifecycle hooks: `wp_head()`, `wp_body_open()` and `wp_footer()`.
- Non-VDM WordPress pages remain handled by the active theme.
- The imported V1 Designer/runtime/layout/storage remains unchanged.
- The existing V1 virtual Designer viewport remains fixed at 1920/1180/980/390 px for Desktop/Laptop/Tablet/Mobile.
- Fit remains a visual CSS transform only; it does not rewrite the layout model or imported coordinates.

### Safety contract

Alpha.5 is layered deterministically on Alpha.4. It does not modify:

- `editor-v018-core.js`
- `editor-v0144-viewport.js`
- `editor-v0169-canvas-height.js`
- `Renderer.php`
- `ResponsiveRenderer.php`
- `LayoutModel.php`
- `V3StorageMigration.php`

The build verifies these files by SHA-256 before and after the Alpha.5 transform.

### Acceptance on test4

After updating from Alpha.4, compare the same imported page against test3 at the same browser width. On VDM pages there must be only one VDM header, one VDM content surface and one VDM footer. The theme's site header, theme page title and theme footer must be absent.

Use `Bliv medlem` and `Hjem – Visual Designer` as initial reference pages. No page data should be manually corrected before this shell-level comparison is complete.
