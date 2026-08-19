#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-nesting-tools.js'
CSS='assets/ultimate-designer-nesting-tools.css'
ADMIN_JS='assets/admin.js'

for file in "$JS" "$CSS" "$ADMIN_JS"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Palette-created elements still use the existing LayoutParentKey nesting path.
# v0.8.11 renamed the implementation from finishNest() to finishNewNested(),
# but the behavioral invariant is unchanged.
grep -F 'function finishNewNested(beforeKeys, type, boxKey)' "$JS" >/dev/null
grep -F 'moveRowIntoBox($newRow, $box)' "$JS" >/dev/null
grep -F '.h18-layout-parent-key' "$JS" >/dev/null
grep -F '.h18-layout-parent-select' "$JS" >/dev/null

# Existing rows are dragged by jQuery UI Sortable. v0.8.11 owns this flow
# directly in the active Kasse runtime under the h18V0811Kasse namespace.
grep -F "sortstart.h18V0811Kasse" "$JS" >/dev/null
grep -F "sort.h18V0811Kasse" "$JS" >/dev/null
grep -F "sortstop.h18V0811Kasse" "$JS" >/dev/null
grep -F 'function boxAtPoint(pageX, pageY, $draggedRow)' "$JS" >/dev/null
grep -F 'function canMoveIntoBox($row, $box)' "$JS" >/dev/null
grep -F 'function moveRowIntoBox($row, $box)' "$JS" >/dev/null
grep -F 'syncFlatOrder()' "$JS" >/dev/null

# Kasse exposes an explicit inside drop target instead of only before/after
# positioning in the flat legacy sortable.
grep -F 'h18-ud-box-drop-zone' "$JS" >/dev/null
grep -F 'Træk et element hertil for at lægge det IND I kassen' "$JS" >/dev/null
grep -F '.h18-ud-box-drop-zone' "$CSS" >/dev/null
grep -F '.h18-ud-existing-row-drag .h18-ud-box-drop-zone' "$CSS" >/dev/null

# v0.8.11 additionally owns explicit side placement for Kasser.
grep -F 'function sideZoneAtPoint(pageX, pageY, sourceKey)' "$JS" >/dev/null
grep -F 'function placeBoxBeside($source, $target, side)' "$JS" >/dev/null
grep -F 'h18-v0811-side-zone' "$JS" >/dev/null

# The flat form structure remains intact; hierarchy is still persisted through
# the existing parent/order controls used by the public recursive renderer.
grep -F 'function syncPageSectionOrder' "$ADMIN_JS" >/dev/null
grep -F '.h18-page-section-order' "$ADMIN_JS" >/dev/null
grep -F 'function layoutWouldCycleV0519' "$ADMIN_JS" >/dev/null

# This UX addon must not introduce direct WordPress writes or a cutover path.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" >/dev/null; then
  echo 'FAIL: box drop UX introduced persistence/public-cutover primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.8 existing element -> Kasse drop contract (v0.8.11-compatible): PASS'
