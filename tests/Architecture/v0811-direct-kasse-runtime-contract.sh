#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-nesting-tools.js'
CSS='assets/ultimate-designer-nesting-tools.css'

for file in "$JS" "$CSS"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Nested child source rows are hidden unconditionally from flat canvas while staying in DOM/storage.
grep -F 'data-h18-v0811-child-source' "$JS" >/dev/null
grep -F 'data-h18-v0811-child-source="1"]{display:none!important}' "$CSS" >/dev/null
if grep -F 'data-h18-v0811-child-source="1"]:not(.is-selected)' "$CSS" >/dev/null; then
  echo 'FAIL: selected nested source rows would still remain visible'
  exit 1
fi

# Real child previews are composed inside the Kasse and edit remains routed through the source row/Inspector.
grep -F 'function clonePreview($row)' "$JS" >/dev/null
grep -F 'h18-v0811-child-card' "$JS" >/dev/null
grep -F 'h18-v0811-edit-child' "$JS" >/dev/null
grep -F "text: 'v0.8.11'" "$JS" >/dev/null

# Top-level Kasser expose explicit left/right targets and both new/existing Kasse drag paths use them.
grep -F 'h18-v0811-side-zones' "$JS" >/dev/null
grep -F "'data-side': 'left'" "$JS" >/dev/null
grep -F "'data-side': 'right'" "$JS" >/dev/null
grep -F 'let paletteBoxDrag = null;' "$JS" >/dev/null
grep -F 'let existingBoxDrag = null;' "$JS" >/dev/null
grep -F 'function sideZoneAtPoint(pageX, pageY, sourceKey)' "$JS" >/dev/null
grep -F 'function placeBoxBeside($source, $target, side)' "$JS" >/dev/null

# Side-by-side composition reuses existing Grid/Auto-kasser + LayoutParentKey, not new storage.
grep -F "const AUTO_LABEL = 'Auto-kasser';" "$JS" >/dev/null
grep -F 'function createAutoForBoxes($source, $target, side)' "$JS" >/dev/null
grep -F '.h18-layout-parent-key' "$JS" >/dev/null
grep -F '.h18-layout-parent-select' "$JS" >/dev/null
grep -F 'h18-v0811-auto-grid' "$JS" >/dev/null
grep -F 'grid-template-columns:repeat(var(--h18-v0811-cols,1)' "$CSS" >/dev/null

# Runtime remains admin UX only; no WordPress persistence/cutover primitives may appear here.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" >/dev/null; then
  echo 'FAIL: v0.8.11 Kasse runtime introduced persistence/public-cutover primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.11 direct Kasse composition contract: PASS'
