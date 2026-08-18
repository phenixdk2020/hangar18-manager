#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-layout-tools.js'
CSS='assets/ultimate-designer-layout-tools.css'
CTRL='src/Admin/LayoutToolsAdminController.php'
BOOT='src/Admin/IntegrationAdminBootstrap.php'
MAIN='hangar18-manager.php'

for file in "$JS" "$CSS" "$CTRL" "$BOOT" "$MAIN"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Auto-kasser: uses existing generic Grid/Container data and derives equal-width
# desktop columns from child count. Gap remains the existing LayoutGapPx setting.
grep -F "AUTO_LABEL = 'Auto-kasser'" "$JS" >/dev/null
grep -F "BOX_LABEL = 'Kasse'" "$JS" >/dev/null
grep -F "paletteButton('Auto-kasser', 'grid'" "$JS" >/dev/null
grep -F "paletteButton('Kasse', 'container'" "$JS" >/dev/null
grep -F "LayoutColumns" "$JS" >/dev/null
grep -F "LayoutGapPx" "$JS" >/dev/null
grep -F "MobileLayoutColumns" "$JS" >/dev/null
grep -F "setParent" "$JS" >/dev/null

# Every Kasse is still a normal Container, so its own existing Inspector design
# and typography properties remain available independently.
grep -F "'CustomBackgroundColor'" "$MAIN" >/dev/null
grep -F "'CustomTextColor'" "$MAIN" >/dev/null
grep -F "'CustomHeadingColor'" "$MAIN" >/dev/null
grep -F "'SectionBodyFontFamily'" "$MAIN" >/dev/null
grep -F "'SectionHeadingFontFamily'" "$MAIN" >/dev/null
grep -F "'BodyFontSizePx'" "$MAIN" >/dev/null
grep -F "h18-element-typography-box" "$MAIN" >/dev/null

# Table is a visual UI over the existing safe HTML section. It supports rows,
# columns, header, zebra, colors, font size, padding and mobile overflow.
grep -F "paletteButton('Tabel', 'html'" "$JS" >/dev/null
grep -F 'data-h18-table="1"' "$JS" >/dev/null
grep -F 'headerBg' "$JS" >/dev/null
grep -F 'headerColor' "$JS" >/dev/null
grep -F 'cellBg' "$JS" >/dev/null
grep -F 'textColor' "$JS" >/dev/null
grep -F 'fontSize' "$JS" >/dev/null
grep -F 'padding' "$JS" >/dev/null
grep -F "mobile: 'scroll'" "$JS" >/dev/null

# HTML content is still normalized by wp_kses_post server-side.
grep -F "wp_kses_post((string) (\$raw['Content'] ?? ''))" "$MAIN" >/dev/null

# Dedicated UI is admin-only and only enqueued on the existing Sider screen.
grep -F "PAGE_SLUG = 'hangar18-pages'" "$CTRL" >/dev/null
grep -F "add_action('admin_enqueue_scripts'" "$CTRL" >/dev/null
grep -F 'hangar18-ultimate-designer-layout-tools' "$CTRL" >/dev/null
grep -F 'LayoutToolsAdminController::register();' "$BOOT" >/dev/null
if grep -E "add_action\('(wp|init|template_redirect|wp_head|wp_footer)'" "$CTRL" >/dev/null; then
  echo 'FAIL: LayoutToolsAdminController registers frontend hook'
  exit 1
fi

# No cutover/public activation is introduced by this editor slice.
if grep -Ei '(activate|cutover|publish).*(page|frontend)|wp_update_post|update_post_meta' "$CTRL" "$JS" >/dev/null; then
  echo 'FAIL: v0.8.5 layout tools contain page cutover/write primitive outside existing page form'
  exit 1
fi

echo 'v0.8.5 Auto-kasser/Table admin contract: PASS'
