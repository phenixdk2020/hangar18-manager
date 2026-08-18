#!/usr/bin/env bash
set -euo pipefail

js='assets/ultimate-designer-layout-tools.js'
css='assets/ultimate-designer-layout-tools.css'
health_js='assets/ultimate-designer-side-health.js'
health_css='assets/ultimate-designer-side-health.css'
controller='src/Admin/SideHealthAdminController.php'

for file in "$js" "$css" "$health_js" "$health_css" "$controller"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Auto-kasser reuse existing grid/container schema and derive equal columns from child count.
grep -F "const AUTO_LABEL = 'Auto-kasser';" "$js" >/dev/null
grep -F "const BOX_LABEL = 'Kasse';" "$js" >/dev/null
grep -F "const columns = Math.max(1, Math.min(6, count || 1));" "$js" >/dev/null
grep -F "[LayoutColumns]" "$js" >/dev/null
grep -F "[MobileLayoutColumns]" "$js" >/dev/null
grep -F "[LayoutGapPx]" "$js" >/dev/null
grep -F "[MobileLayoutGapPx]" "$js" >/dev/null
grep -F "rowType($row) === 'container'" "$js" >/dev/null
grep -F "rowType($row) === 'grid'" "$js" >/dev/null

# Inspector integration must follow the legacy editor's selected-row body move.
grep -F "if ($row.hasClass('is-selected'))" "$js" >/dev/null
grep -F "$('#h18-page-inspector-target').find(selector)" "$js" >/dev/null

# Table is a visual editor over the existing sanitized HTML element.
grep -F "paletteButton('Tabel', 'html', 'table'" "$js" >/dev/null
grep -F 'data-h18-table="1"' "$js" >/dev/null
grep -F "data-table-setting': 'rows'" "$js" >/dev/null
grep -F "data-table-setting': 'cols'" "$js" >/dev/null
grep -F "data-table-setting': 'fontSize'" "$js" >/dev/null
grep -F "data-table-setting': 'padding'" "$js" >/dev/null
grep -F "Vandret scroll" "$js" >/dev/null
grep -F "Første række er overskrift" "$js" >/dev/null
grep -F "Zebra-striber" "$js" >/dev/null

# Side Health must default collapsed so Inspector content remains usable.
grep -F 'class="h18-ud-side-health-panel is-collapsed"' "$health_js" >/dev/null
grep -F 'class="h18-ud-health-toggle" aria-expanded="false"' "$health_js" >/dev/null
grep -F "setCollapsed(true);" "$health_js" >/dev/null
grep -F '.h18-ud-side-health-panel.is-collapsed .h18-ud-health-body{display:none}' "$health_css" >/dev/null

# Assets are admin-page-only and loaded after the existing page editor script.
grep -F "'hangar18-ultimate-designer-layout-tools'" "$controller" >/dev/null
grep -F "['jquery', 'hangar18-manager-admin']" "$controller" >/dev/null
if grep -E "add_action\('(wp|init|template_redirect|wp_head|wp_footer)'" "$controller" >/dev/null; then
  echo 'FAIL: v0.8.5 page editor enhancements register a frontend hook'
  exit 1
fi

# No destructive WordPress/page operations belong in the client-only layout tool.
if grep -E "wp_delete|delete_post|remove_role|activate|cutover|publish" "$js" >/dev/null; then
  echo 'FAIL: v0.8.5 layout tool contains a destructive/cutover primitive'
  exit 1
fi

echo 'v0.8.5 Auto-kasser/Table/Collapsed Side Health contract: PASS'
