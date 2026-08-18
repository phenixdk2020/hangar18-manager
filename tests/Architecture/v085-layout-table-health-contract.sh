#!/usr/bin/env bash
set -euo pipefail

js='assets/ultimate-designer-layout-tools.js'
css='assets/ultimate-designer-layout-tools.css'
health_js='assets/ultimate-designer-side-health.js'
health_css='assets/ultimate-designer-side-health.css'
controller='src/Admin/EditorLayoutToolsAdminController.php'

require_literal() {
  local needle="$1"
  local file="$2"
  local label="$3"
  if ! grep -F -- "$needle" "$file" >/dev/null; then
    echo "FAIL: $label"
    echo "  expected literal: $needle"
    echo "  file: $file"
    exit 1
  fi
}

for file in "$js" "$css" "$health_js" "$health_css" "$controller"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Auto-kasser reuse existing grid/container schema and derive equal columns from child count.
require_literal "const AUTO_LABEL = 'Auto-kasser';" "$js" 'Auto-kasser label missing'
require_literal "const BOX_LABEL = 'Kasse';" "$js" 'Kasse label missing'
require_literal "const columns = Math.max(1, Math.min(6, count || 1));" "$js" 'automatic equal-column calculation missing'
require_literal '[LayoutColumns]' "$js" 'desktop LayoutColumns binding missing'
require_literal '[MobileLayoutColumns]' "$js" 'mobile LayoutColumns binding missing'
require_literal 'LayoutGapPx' "$js" 'desktop gap setting missing'
require_literal 'MobileLayoutGapPx' "$js" 'mobile gap setting missing'
require_literal "rowType(\$row) === 'container'" "$js" 'Kasse must remain a normal container'
require_literal "rowType(\$row) === 'grid'" "$js" 'Auto-kasser must remain a normal grid'

# Inspector integration must follow the legacy editor's selected-row body move.
require_literal "if (\$row.hasClass('is-selected'))" "$js" 'selected-row Inspector bridge missing'
require_literal "\$('#h18-page-inspector-target').find(selector)" "$js" 'Inspector control lookup missing'

# Table is a visual editor over the existing sanitized HTML element.
require_literal "paletteButton('Tabel', 'html', 'table'" "$js" 'Tabel palette item missing'
require_literal 'data-h18-table="1"' "$js" 'Tabel storage marker missing'
require_literal "data-table-setting': 'rows'" "$js" 'Tabel rows setting missing'
require_literal "data-table-setting': 'cols'" "$js" 'Tabel columns setting missing'
require_literal "data-table-setting': 'fontSize'" "$js" 'Tabel font-size setting missing'
require_literal "data-table-setting': 'padding'" "$js" 'Tabel cell-padding setting missing'
require_literal 'Vandret scroll' "$js" 'Tabel mobile horizontal-scroll option missing'
require_literal 'Første række er overskrift' "$js" 'Tabel header-row option missing'
require_literal 'Zebra-striber' "$js" 'Tabel zebra option missing'

# Side Health must default collapsed so Inspector content remains usable.
require_literal 'class="h18-ud-side-health-panel is-collapsed"' "$health_js" 'Side Health must start collapsed'
require_literal 'class="h18-ud-health-toggle" aria-expanded="false"' "$health_js" 'Side Health toggle accessibility state missing'
require_literal 'setCollapsed(true);' "$health_js" 'Side Health initial collapse call missing'
require_literal '.h18-ud-side-health-panel.is-collapsed .h18-ud-health-body{display:none}' "$health_css" 'collapsed Side Health body CSS missing'

# Assets are admin-page-only and loaded after the existing page editor script.
require_literal "'hangar18-ultimate-designer-layout-tools'" "$controller" 'layout tools enqueue handle missing'
require_literal "['jquery', 'jquery-ui-sortable', 'hangar18-manager-admin']" "$controller" 'layout tools must load after existing page editor'
require_literal "\$page !== 'hangar18-pages'" "$controller" 'layout tools page restriction missing'
if grep -E "add_action\('(wp|init|template_redirect|wp_head|wp_footer)'" "$controller" >/dev/null; then
  echo 'FAIL: v0.8.5 page editor enhancements register a frontend hook'
  exit 1
fi

# No destructive WordPress/page operations belong in the client-only layout tool.
if grep -E 'wp_delete|delete_post|remove_role|activate|cutover|publish' "$js" >/dev/null; then
  echo 'FAIL: v0.8.5 layout tool contains a destructive/cutover primitive'
  exit 1
fi

echo 'v0.8.5 Auto-kasser/Table/Collapsed Side Health contract: PASS'
