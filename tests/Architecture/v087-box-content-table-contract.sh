#!/usr/bin/env bash
set -euo pipefail

BOX_JS='assets/ultimate-designer-box-content-layout.js'
BOX_CSS='assets/ultimate-designer-box-content-layout.css'
TABLE_JS='assets/ultimate-designer-table-appearance.js'
TABLE_CSS='assets/ultimate-designer-table-appearance.css'
NEST_JS='assets/ultimate-designer-nesting-tools.js'
CTRL='src/Admin/EditorLayoutToolsAdminController.php'
MAIN='hangar18-manager.php'

for file in "$BOX_JS" "$BOX_CSS" "$TABLE_JS" "$TABLE_CSS" "$NEST_JS" "$CTRL" "$MAIN"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# A Box can contain multiple normal elements through LayoutParentKey.
grep -F 'function directChildCount($row)' "$BOX_JS" >/dev/null
grep -F 'Kassen kan indeholde flere elementer' "$BOX_JS" >/dev/null
grep -F "'LayoutDirection'" "$BOX_JS" >/dev/null
grep -F "'LayoutGapPx'" "$BOX_JS" >/dev/null
grep -F "'MobileLayoutGapPx'" "$BOX_JS" >/dev/null
grep -F "'MobileLayoutStack'" "$BOX_JS" >/dev/null
grep -F 'function directChildren($box)' "$NEST_JS" >/dev/null
grep -F 'h18-ud-box-child-chip' "$NEST_JS" >/dev/null

# Existing recursive renderer is still the source of truth for nested children.
grep -F 'render_page_editor_layout_tree' "$MAIN" >/dev/null
grep -F "['container','flex','grid']" "$MAIN" >/dev/null
grep -F 'LayoutParentKey' "$MAIN" >/dev/null

# Table borders can be hidden with width 0 while keeping table semantics/data.
grep -F 'data-h18-table-border-width' "$TABLE_JS" >/dev/null
grep -F 'data-h18-table-border-hidden' "$TABLE_JS" >/dev/null
grep -F "width === 0 ? '0 solid transparent'" "$TABLE_JS" >/dev/null
grep -F '0 px gør alle celle- og tabelkanter helt usynlige' "$TABLE_JS" >/dev/null
grep -F 'h18-ud-table-border-appearance' "$TABLE_CSS" >/dev/null

# All additions stay admin-only and reuse the existing editor fields.
grep -F 'hangar18-ultimate-designer-box-content-layout' "$CTRL" >/dev/null
grep -F 'hangar18-ultimate-designer-table-appearance' "$CTRL" >/dev/null
grep -F "\$page !== 'hangar18-pages'" "$CTRL" >/dev/null
grep -F "current_user_can('edit_pages')" "$CTRL" >/dev/null
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$BOX_JS" "$TABLE_JS" "$CTRL" >/dev/null; then
  echo 'FAIL: box/table UX introduced a persistence/public-cutover primitive'
  exit 1
fi

node --check "$BOX_JS"
node --check "$TABLE_JS"
echo 'v0.8.7 multi-element box content + borderless table contract: PASS'
