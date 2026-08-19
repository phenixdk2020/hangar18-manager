#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/EditorLayoutToolsAdminController.php'
js='assets/ultimate-designer-box-tools.js'
css='assets/ultimate-designer-box-tools.css'

test -f "$js"
test -f "$css"

grep -F "hangar18-ultimate-designer-box-tools" "$controller" >/dev/null
grep -F "ultimate-designer-box-tools.js" "$controller" >/dev/null
grep -F "ultimate-designer-box-tools.css" "$controller" >/dev/null

grep -F "LayoutGapPx" "$js" >/dev/null
grep -F "MobileLayoutGapPx" "$js" >/dev/null
grep -F "RadiusPx" "$js" >/dev/null
grep -F "RadiusTopLeftPx" "$js" >/dev/null
grep -F "RadiusTopRightPx" "$js" >/dev/null
grep -F "RadiusBottomRightPx" "$js" >/dev/null
grep -F "RadiusBottomLeftPx" "$js" >/dev/null
grep -F "CustomBackgroundColor" "$js" >/dev/null
grep -F "CustomTextColor" "$js" >/dev/null
grep -F "CustomHeadingColor" "$js" >/dev/null
grep -F "CustomBorderColor" "$js" >/dev/null
grep -F "SectionBodyFontFamily" "$js" >/dev/null
grep -F "SectionHeadingFontFamily" "$js" >/dev/null
grep -F "BodyFontSizePx" "$js" >/dev/null
grep -F "H2FontSizePx" "$js" >/dev/null
grep -F "HorizontalPaddingPx" "$js" >/dev/null
grep -F "BorderWidthPx" "$js" >/dev/null
grep -F "DesignMode" "$js" >/dev/null

grep -F "Kasse · eget design" "$js" >/dev/null
grep -F "Firkantet" "$js" >/dev/null
grep -F "Styr hvert hjørne separat" "$js" >/dev/null
grep -F "Afstand mellem kasser" "$js" >/dev/null
grep -F "h18-ud-auto-box-tile" "$js" >/dev/null
grep -F "grid-template-columns: repeat(var(--h18-ud-box-columns" "$css" >/dev/null

if grep -RInE "add_action\('(wp|init|template_redirect|wp_head|wp_footer)'" "$controller" "$js" >/dev/null; then
  echo 'FAIL: box tools must stay admin-only'; exit 1
fi

node --check "$js"

echo 'Ultimate Designer v0.8.7 box tools contract: PASS'
