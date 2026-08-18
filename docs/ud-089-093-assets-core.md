# E9 Assets core — UD-089 to UD-093

## Compatibility rule

The Asset Manager is an overlay on WordPress Media Library. Native attachment IDs remain authoritative and are never renumbered or replaced.

## UD-089 Asset manager

- Folder path, collections and tags are stored separately from native attachment records.
- Metadata is keyed by the immutable WordPress MediaId.
- Copyright/source and responsive focal point metadata can be attached without altering the media object.
- WordPress adapter stores the overlay in `hangar18_ud_asset_metadata_v1`.

## UD-090 Usage inspector

`AssetUsageScanner` recursively indexes MediaId/ImageMediaId/BackgroundMediaId and related native-ID fields across arbitrary resource states. Resource keys can identify pages, components and data entries. The result is suitable for a pre-delete usage inspector.

## UD-091 Focal point

Desktop/tablet/mobile focal points use 0–100 coordinates. Missing breakpoints inherit the previous value. The resolver outputs CSS object-position values and variables.

## UD-092 Image optimization

- The original source is always preserved.
- WebP/AVIF derivatives are planned only where the image backend reports support.
- `WordPressImageOptimizer` uses the native WP image editor and writes derivatives beside the source; it never deletes or overwrites the source.
- Quality/max-dimension options are bounded by the adapter/service.

## UD-093 Duplicate detection

Duplicate groups use SHA-256 of local file bytes. Detection is non-destructive: it reports matching MediaIds/paths and never deletes, merges or rewrites attachments automatically.

## Activation boundary

This slice is additive. Existing Vehicle/Event/Gallery media behavior and existing pages continue to use the current runtime until final migration/activation QA.
