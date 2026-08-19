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

# Generic content elements can be nested in a Kasse via the existing LayoutParentKey model.
grep -F "const BOX_LABEL = 'Kasse';" "$JS" >/dev/null
grep -F 'function targetBoxForElement(element)' "$JS" >/dev/null
grep -F 'function setParent($row, key)' "$JS" >/dev/null
grep -F '.h18-layout-parent-key' "$JS" >/dev/null
grep -F '.h18-layout-parent-select' "$JS" >/dev/null
grep -F 'finishNest(beforeKeys, type, boxKey)' "$JS" >/dev/null
grep -F "item.hasAttribute('data-h18-layout-tool')" "$JS" >/dev/null
grep -F 'selectedBox()' "$JS" >/dev/null
grep -F 'h18-ud-box-contents-preview' "$JS" >/dev/null
grep -F 'h18-ud-box-child-chip' "$JS" >/dev/null
grep -F 'h18-ud-nesting-drop-target' "$CSS" >/dev/null
grep -F 'Slip her for at lægge elementet i kassen' "$CSS" >/dev/null

# Existing editor/runtime already owns the persisted hierarchy and public recursive renderer.
grep -F "function layoutParentCapableV0519" "$ADMIN_JS" >/dev/null
grep -F "['container','flex','grid']" "$ADMIN_JS" >/dev/null
grep -F 'render_page_editor_layout_tree' "$MAIN" >/dev/null
grep -F "['container','flex','grid']" "$MAIN" >/dev/null
grep -F "LayoutParentKey" "$MAIN" >/dev/null

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
echo 'v0.8.7 generic box nesting contract: PASS'
