#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-nesting-tools.js'
CSS='assets/ultimate-designer-nesting-tools.css'
CTRL='src/Admin/EditorLayoutToolsAdminController.php'
MAIN='hangar18-manager.php'
ADMIN_JS='assets/admin.js'

for file in "$JS" "$CSS" "$CTRL" "$MAIN" "$ADMIN_JS"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Generic content elements remain nestable in a Kasse through the existing LayoutParentKey model.
grep -F "const BOX_LABEL = 'Kasse';" "$JS" >/dev/null
grep -F 'function targetBoxForElement(element)' "$JS" >/dev/null
grep -F 'function setParent($row, key)' "$JS" >/dev/null
grep -F '.h18-layout-parent-key' "$JS" >/dev/null
grep -F '.h18-layout-parent-select' "$JS" >/dev/null
grep -F 'data-h18-layout-tool' "$JS" >/dev/null
grep -F 'h18-ud-box-contents-preview' "$JS" >/dev/null
grep -Eq 'finishNest\(|finishNewNested\(' "$JS"
grep -Eq 'h18-ud-box-child-chip|h18-v0811-child-card' "$JS"
grep -F 'h18-ud-nesting-drop-target' "$CSS" >/dev/null
grep -F 'Slip her for at lægge elementet i kassen' "$CSS" >/dev/null

# Existing editor/runtime still owns persisted hierarchy and the public recursive renderer.
grep -F "function layoutParentCapableV0519" "$ADMIN_JS" >/dev/null
grep -F "['container','flex','grid']" "$ADMIN_JS" >/dev/null
grep -F 'render_page_editor_layout_tree' "$MAIN" >/dev/null
grep -F "['container','flex','grid']" "$MAIN" >/dev/null
grep -F 'LayoutParentKey' "$MAIN" >/dev/null

# Admin-only enqueue; no persistence or public cutover path in this UX enhancer.
grep -F 'hangar18-ultimate-designer-nesting-tools' "$CTRL" >/dev/null
grep -F 'ultimate-designer-nesting-tools.js' "$CTRL" >/dev/null
grep -F 'ultimate-designer-nesting-tools.css' "$CTRL" >/dev/null
grep -F "\$page !== 'hangar18-pages'" "$CTRL" >/dev/null
grep -F "current_user_can('edit_pages')" "$CTRL" >/dev/null
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$JS" "$CTRL" >/dev/null; then
  echo 'FAIL: nesting UX introduced a persistence/public-cutover primitive'
  exit 1
fi

node --check "$JS"
echo 'v0.8.7 generic box nesting behavioral contract: PASS'
