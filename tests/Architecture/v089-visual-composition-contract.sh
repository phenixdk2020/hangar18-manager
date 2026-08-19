#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-visual-composition.js'
CSS='assets/ultimate-designer-visual-composition.css'
CTRL='src/Admin/EditorLayoutToolsAdminController.php'

for file in "$JS" "$CSS" "$CTRL"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# The visual canvas must compose the existing flat LayoutParentKey model rather
# than introducing a second persistence structure.
grep -F "const AUTO_LABEL = 'Auto-kasser';" "$JS" >/dev/null
grep -F "const BOX_LABEL = 'Kasse';" "$JS" >/dev/null
grep -F 'function parentKey($row)' "$JS" >/dev/null
grep -F 'function setParent($row, key)' "$JS" >/dev/null
grep -F '.h18-layout-parent-key' "$JS" >/dev/null
grep -F '.h18-layout-parent-select' "$JS" >/dev/null

# Nested source rows are hidden only in the desktop editor; their real form
# controls stay in the DOM so normal save/serialization remains authoritative.
grep -F 'h18-ud-vc-source-hidden' "$JS" >/dev/null
grep -F '.h18-page-section-row.h18-ud-vc-source-hidden{display:none!important}' "$CSS" >/dev/null
grep -F '@media(max-width:1180px)' "$CSS" >/dev/null
grep -F 'display:block!important' "$CSS" >/dev/null

# A Kasse renders real child previews inside the existing Kasse contents area.
grep -F 'function renderBoxComposition($box)' "$JS" >/dev/null
grep -F 'h18-ud-vc-child-card' "$JS" >/dev/null
grep -F 'cleanPreviewClone($child)' "$JS" >/dev/null
grep -F 'data-h18-vc-box-key' "$JS" >/dev/null

# Auto-kasser renders child Kasser as a real visual grid and keeps columns in
# sync with the number of box children.
grep -F 'function renderAutoComposition($autoRow)' "$JS" >/dev/null
grep -F 'h18-ud-vc-auto-grid' "$JS" >/dev/null
grep -F 'h18-ud-vc-box-tile' "$JS" >/dev/null
grep -F 'syncAutoColumns($autoRow)' "$JS" >/dev/null

# Explicit side drop-zones guide a newly dragged Kasse onto an existing Kasse,
# allowing the existing Layout+ tool to create/reuse Auto-kasser.
grep -F 'h18-ud-vc-side-drop-zone' "$JS" >/dev/null
grep -F 'Sæt Kasse ved siden af' "$JS" >/dev/null
grep -F 'h18-ud-vc-new-box-dragging' "$JS" >/dev/null

# Hidden children remain editable and can be moved between Kasser from their
# visual proxy without exposing a new storage API.
grep -F 'h18-ud-vc-edit' "$JS" >/dev/null
grep -F 'moveChildToBox(childKey, boxKey)' "$JS" >/dev/null
grep -F 'reorderBoxWithinAuto(boxKey, targetKey, side)' "$JS" >/dev/null

# The addon is admin-only and depends on the existing box-content layer.
grep -F 'hangar18-ultimate-designer-visual-composition' "$CTRL" >/dev/null
grep -F 'ultimate-designer-visual-composition.js' "$CTRL" >/dev/null
grep -F 'ultimate-designer-visual-composition.css' "$CTRL" >/dev/null
grep -F "'hangar18-ultimate-designer-box-content-layout'" "$CTRL" >/dev/null

if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" "$CTRL" >/dev/null; then
  echo 'FAIL: visual composition introduced persistence/public-cutover primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.9 visual box composition contract: PASS'
