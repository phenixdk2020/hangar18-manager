#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/EditorLegoSpacingAdminController.php'
LIB='src/Admin/EditorElementLibraryAdminController.php'
JS='assets/ultimate-designer-lego-spacing.js'
CSS='assets/ultimate-designer-lego-spacing.css'

for file in "$CTRL" "$LIB" "$JS" "$CSS"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

require_contains() {
  local file="$1"
  local needle="$2"
  local label="$3"
  if ! grep -F -- "$needle" "$file" >/dev/null; then
    echo "FAIL: $label"
    echo "  missing: $needle"
    exit 1
  fi
}

require_contains "$LIB" 'EditorLegoSpacingAdminController::register();' 'LEGO spacing controller is not registered before editor enqueue'
require_contains "$CTRL" "hangar18_ultimate_designer_lego_spacing_v1" 'separate LEGO spacing option is missing'
require_contains "$CTRL" "add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 5);" 'LEGO spacing is not captured before the legacy redirecting save handler'
require_contains "$CTRL" 'assets/ultimate-designer-lego-spacing.js' 'LEGO spacing JS is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-lego-spacing.css' 'LEGO spacing CSS is not enqueued'
require_contains "$CTRL" "'MarginXPx'" 'desktop element X spacing is not persisted'
require_contains "$CTRL" "'MarginYPx'" 'desktop element Y spacing is not persisted'
require_contains "$CTRL" "'MobileMarginXPx'" 'mobile element X spacing is not persisted'
require_contains "$CTRL" "'MobileMarginYPx'" 'mobile element Y spacing is not persisted'
require_contains "$CTRL" "'GapXPx'" 'desktop layout X gap is not persisted'
require_contains "$CTRL" "'GapYPx'" 'desktop layout Y gap is not persisted'
require_contains "$CTRL" "'MobileGapXPx'" 'mobile layout X gap is not persisted'
require_contains "$CTRL" "'MobileGapYPx'" 'mobile layout Y gap is not persisted'

require_contains "$JS" "legacyNumber(\$row, 'LayoutGapPx', 16)" 'legacy desktop gap fallback is missing'
require_contains "$JS" "legacyNumber(\$row, 'MobileLayoutGapPx', 12)" 'legacy mobile gap fallback is missing'
require_contains "$JS" "class: 'h18-section-module-box h18-canvas-direct-controls h18-ud-lego-spacing-panel'" 'LEGO Inspector is not recognized by content-history runtime'
require_contains "$JS" "data-h18-lego-margin-x" 'LEGO X state is not embedded in history DOM snapshots'
require_contains "$JS" "data-h18-lego-gap-y" 'LEGO Y gap state is not embedded in history DOM snapshots'
require_contains "$JS" "h18_lego_spacing[" 'LEGO save payload is not generated'
require_contains "$JS" "data-h18-lego-spacing-runtime', '0.8.24'" 'LEGO runtime identity is missing'
require_contains "$CSS" 'column-gap:var(--h18-lego-gap-x' 'separate X gap is not applied in editor preview'
require_contains "$CSS" 'row-gap:var(--h18-lego-gap-y' 'separate Y gap is not applied in editor preview'

if grep -Ei 'wp_update_post|wp_insert_post|set_post_thumbnail|update_post_meta|delete_post_meta' "$CTRL" "$JS" >/dev/null; then
  echo 'FAIL: LEGO spacing foundation introduced public/post mutation primitives'
  exit 1
fi

node --check "$JS"
php -l "$CTRL" >/dev/null
php -l "$LIB" >/dev/null

echo 'v0.8.24 LEGO X/Y spacing foundation contract: PASS'
