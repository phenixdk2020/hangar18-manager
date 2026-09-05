# Visual Designer Manager V3 — 3.0.0-alpha.4

## Purpose

Alpha.4 performs the WordPress admin route and visible UI identity cutover from historical `h18-clean-*` page slugs to canonical `vdm-*` slugs while preserving the verified V1 Designer/runtime behavior and the Alpha.3 storage migration.

## Canonical routes

- `vdm-manager`
- `vdm-editor`
- `vdm-vehicles`
- `vdm-vehicle-fields`
- `vdm-events`
- `vdm-event-fields`
- `vdm-gallery`
- `vdm-data`
- `vdm-pages`
- `vdm-conversion`
- `vdm-menu`
- `vdm-header-footer`
- `vdm-backup`
- `vdm-updates`
- `vdm-log`
- `vdm-manual`
- `vdm-export`
- `vdm-theme`

Existing VDM-native routes such as `vdm-transfer` and `vdm-site-settings` remain unchanged.

## Compatibility

Historical `admin.php?page=h18-clean-*` URLs are not registered as the active UI routes. `AdminRouteCompatibility` catches those old `admin.php` URLs during `admin_init` and issues a 302 redirect to the corresponding canonical `vdm-*` route while preserving scalar query parameters such as `post` or `menu_id`.

This keeps old bookmarks and diagnostic links functional without exposing legacy route names in newly generated links.

## Deliberately unchanged

Alpha.4 does not redesign or reimplement:

- Designer drag/drop, resize or grid behavior
- layout model or renderer
- CSS selectors / DOM class contracts
- action/nonces
- diagnostics storage
- updater cache/backup storage
- Alpha.3 copy-and-verify storage migration

The V1 `0.1.93` runtime remains the behavioral baseline.
