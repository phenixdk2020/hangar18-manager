#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-visual-composition.js'
CSS='assets/ultimate-designer-visual-composition.css'
CTRL='src/Admin/EditorLayoutToolsAdminController.php'

for file in "$JS" "$CSS" "$CTRL"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Keep the historical v0.8.9 addon syntactically valid and verify that it still
# represents the same non-persistent LayoutParentKey composition model. v0.8.10
# is allowed to supersede this addon at enqueue/runtime level.
grep -F "const AUTO_LABEL = 'Auto-kasser';" "$JS" >/dev/null
grep -F "const BOX_LABEL = 'Kasse';" "$JS" >/dev/null
grep -F 'function parentKey($row)' "$JS" >/dev/null
grep -F 'function setParent($row, key)' "$JS" >/dev/null
grep -F '.h18-layout-parent-key' "$JS" >/dev/null
grep -F '.h18-layout-parent-select' "$JS" >/dev/null

grep -F 'h18-ud-vc-source-hidden' "$JS" >/dev/null
grep -F '.h18-page-section-row.h18-ud-vc-source-hidden{display:none!important}' "$CSS" >/dev/null
grep -F '@media(max-width:1180px)' "$CSS" >/dev/null
grep -F '.h18-ud-vc-auto-grid{grid-template-columns:1fr!important}' "$CSS" >/dev/null
if grep -F '.h18-page-section-row.h18-ud-vc-source-hidden{display:block!important}' "$CSS" >/dev/null; then
  echo 'FAIL: responsive CSS exposes duplicate flat child rows'
  exit 1
fi

grep -F 'function renderBoxComposition($box)' "$JS" >/dev/null
grep -F 'h18-ud-vc-child-card' "$JS" >/dev/null
grep -F 'cleanPreviewClone($child)' "$JS" >/dev/null
grep -F 'data-h18-vc-box-key' "$JS" >/dev/null

grep -F 'function renderAutoComposition($autoRow)' "$JS" >/dev/null
grep -F 'h18-ud-vc-auto-grid' "$JS" >/dev/null
grep -F 'h18-ud-vc-box-tile' "$JS" >/dev/null
grep -F 'syncAutoColumns($autoRow)' "$JS" >/dev/null

grep -F 'h18-ud-vc-side-drop-zone' "$JS" >/dev/null
grep -F 'Sæt Kasse ved siden af' "$JS" >/dev/null
grep -F 'h18-ud-vc-new-box-dragging' "$JS" >/dev/null

grep -F 'h18-ud-vc-edit' "$JS" >/dev/null
grep -F 'moveChildToBox(childKey, boxKey)' "$JS" >/dev/null
grep -F 'reorderBoxWithinAuto(boxKey, targetKey, side)' "$JS" >/dev/null

# Before v0.8.10 the controller enqueued the addon directly. Starting in
# v0.8.10 the live correction is deliberately attached inline to already-active
# nesting/box-content handles. Accept either architecture, but require exactly a
# recognised admin-only composition path.
if grep -F 'enqueueV0810KasseRuntime' "$CTRL" >/dev/null; then
  grep -F "wp_add_inline_script('hangar18-ultimate-designer-box-content-layout'" "$CTRL" >/dev/null
  grep -F "wp_add_inline_style('hangar18-ultimate-designer-nesting-tools'" "$CTRL" >/dev/null
else
  grep -F 'hangar18-ultimate-designer-visual-composition' "$CTRL" >/dev/null
  grep -F 'ultimate-designer-visual-composition.js' "$CTRL" >/dev/null
  grep -F 'ultimate-designer-visual-composition.css' "$CTRL" >/dev/null
  grep -F "'hangar18-ultimate-designer-box-content-layout'" "$CTRL" >/dev/null
fi

if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" "$CTRL" >/dev/null; then
  echo 'FAIL: visual composition introduced persistence/public-cutover primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.9 visual box composition historical contract: PASS'
