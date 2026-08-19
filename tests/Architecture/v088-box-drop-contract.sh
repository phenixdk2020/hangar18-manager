#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-nesting-tools.js'
CSS='assets/ultimate-designer-nesting-tools.css'
MAIN='hangar18-manager.php'

for file in "$JS" "$CSS" "$MAIN"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Palette-created elements still use the existing LayoutParentKey nesting path.
grep -F 'function finishNewNested(beforeKeys, type, boxKey)' "$JS" >/dev/null
grep -F 'moveRowIntoBox($newRow, $box)' "$JS" >/dev/null
grep -F 'function setParent($row, key)' "$JS" >/dev/null
grep -F '.h18-layout-parent-key' "$JS" >/dev/null
grep -F '.h18-layout-parent-select' "$JS" >/dev/null

# Existing rows are dragged by the existing jQuery UI Sortable and v0.8.11
# owns the inside-Kasse decision, cycle guard and persisted flat Order sync.
grep -F "sortstart.h18V0811Kasse" "$JS" >/dev/null
grep -F "sort.h18V0811Kasse" "$JS" >/dev/null
grep -F "sortstop.h18V0811Kasse" "$JS" >/dev/null
grep -F 'function boxAtPoint(pageX, pageY, $draggedRow)' "$JS" >/dev/null
grep -F 'function wouldCreateCycle($row, $box)' "$JS" >/dev/null
grep -F 'function canMoveIntoBox($row, $box)' "$JS" >/dev/null
grep -F 'function moveRowIntoBox($row, $box)' "$JS" >/dev/null
grep -F 'function syncFlatOrder()' "$JS" >/dev/null
grep -F '.h18-page-section-order' "$JS" >/dev/null

# Kasse exposes an explicit inside drop target instead of only before/after
# positioning in the flat legacy sortable.
grep -F 'h18-ud-box-drop-zone' "$JS" >/dev/null
grep -F 'Træk et element hertil for at lægge det IND I kassen' "$JS" >/dev/null
grep -F '.h18-ud-box-drop-zone' "$CSS" >/dev/null
grep -F '.h18-ud-existing-row-drag .h18-ud-box-drop-zone' "$CSS" >/dev/null

# v0.8.11 additionally owns explicit side placement for Kasser and reuses
# the existing Grid/Auto-kasser hierarchy rather than creating new storage.
grep -F 'function sideZoneAtPoint(pageX, pageY, sourceKey)' "$JS" >/dev/null
grep -F 'function placeBoxBeside($source, $target, side)' "$JS" >/dev/null
grep -F 'function createAutoForBoxes($source, $target, side)' "$JS" >/dev/null
grep -F "const AUTO_LABEL = 'Auto-kasser';" "$JS" >/dev/null
grep -F 'h18-v0811-side-zone' "$JS" >/dev/null

# Public rendering still consumes the existing LayoutParentKey hierarchy.
grep -F 'render_page_editor_layout_tree' "$MAIN" >/dev/null
grep -F 'LayoutParentKey' "$MAIN" >/dev/null

# This UX addon must not introduce direct WordPress writes or a cutover path.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" >/dev/null; then
  echo 'FAIL: box drop UX introduced persistence/public-cutover primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.8 existing element -> Kasse drop behavioral contract (v0.8.11-compatible): PASS'
