#!/usr/bin/env bash
set -euo pipefail

file="hangar18-manager.php"

required=(
  "const VEHICLE_PARENT_SLUG = 'koeretoejer-og-materiel'"
  "const EVENT_PARENT_SLUG   = 'events'"
  "const GALLERY_PARENT_SLUG = 'billedgalleri'"
  "const VEHICLE_MARKER = 'HANGAR18-VEHICLE-DATA'"
  "const EVENT_MARKER   = 'HANGAR18-EVENT-DATA'"
  "const GALLERY_MARKER = 'HANGAR18-GALLERY-ALBUM-DATA'"
  "admin_post_h18_save_vehicle"
  "admin_post_h18_save_vehicle_register_settings"
  "admin_post_h18_save_vehicle_fields"
  "admin_post_h18_rebuild_vehicle_register"
  "admin_post_h18_save_event"
  "admin_post_h18_save_event_layout"
  "admin_post_h18_rebuild_event_register"
  "admin_post_h18_save_gallery_album"
  "admin_post_h18_save_gallery_layout"
  "admin_post_h18_rebuild_gallery_index"
  ".h18-vehicle-register"
  ".h18-vehicle-hero"
  ".h18-vehicle-main-layout"
  ".h18-event-register"
  ".h18-event-hero"
  ".h18-event-image"
  ".h18-gallery-grid"
  ".h18-gallery-hero"
  ".h18-gallery-item"
)

for needle in "${required[@]}"; do
  if ! grep -Fq -- "$needle" "$file"; then
    echo "Protected domain contract FAILED: missing '$needle'"
    exit 1
  fi
done

echo "Protected Vehicle/Event/Gallery v0.5.30 contract: PASS"
