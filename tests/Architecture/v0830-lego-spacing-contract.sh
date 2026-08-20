#!/usr/bin/env bash
set -euo pipefail

MODEL='src/Editor/LegoSpacingModel.php'
CTRL='src/Admin/EditorLegoSpacingAdminController.php'
BOOT='src/Admin/IntegrationAdminBootstrap.php'
JS='assets/ultimate-designer-lego-spacing-v0830.js'
CSS='assets/ultimate-designer-lego-spacing-v0830.css'

for file in "$MODEL" "$CTRL" "$BOOT" "$JS" "$CSS"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

require_contains() {
  local file="$1" needle="$2" label="$3"
  if ! grep -F -- "$needle" "$file" >/dev/null; then
    echo "FAIL: $label"
    echo "  missing: $needle"
    exit 1
  fi
}

require_contains "$MODEL" 'final class LegoSpacingModel' 'canonical LEGO spacing model is missing'
require_contains "$MODEL" "'Margin' => self::axisPair" 'shared per-element margin axis pair is missing'
require_contains "$MODEL" "'Gap' => self::axisPair" 'shared Kasse/layout gap axis pair is missing'
require_contains "$MODEL" "'LayoutGapPx'" 'legacy desktop gap compatibility is missing'
require_contains "$MODEL" "'MobileLayoutGapPx'" 'legacy mobile gap compatibility is missing'

require_contains "$BOOT" 'EditorLegoSpacingAdminController::register();' 'LEGO spacing controller is not registered in the admin bridge'
require_contains "$CTRL" "hangar18_ultimate_designer_lego_spacing_v2" 'versioned LEGO spacing option is missing'
require_contains "$CTRL" "add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 5);" 'LEGO state must persist before legacy page-save redirect'
require_contains "$CTRL" "hangar18-ultimate-designer-history-content-v0823" 'LEGO runtime is not explicitly attached to the existing history owner'
require_contains "$CTRL" 'LegoSpacingModel::normalize' 'server persistence does not use the shared canonical model'

require_contains "$JS" "const STATE_CLASS = 'h18-lego-spacing-state-json';" 'canonical hidden row field is missing'
require_contains "$JS" "legacyNumber(\$row, 'LayoutGapPx', 16)" 'legacy desktop gap fallback is missing in editor hydration'
require_contains "$JS" "legacyNumber(\$row, 'MobileLayoutGapPx', 12)" 'legacy mobile gap fallback is missing in editor hydration'
require_contains "$JS" "Desktop.Margin.X" 'desktop element X control is missing'
require_contains "$JS" "Desktop.Margin.Y" 'desktop element Y control is missing'
require_contains "$JS" "Desktop.Gap.X" 'desktop Kasse/layout X gap is missing'
require_contains "$JS" "Desktop.Gap.Y" 'desktop Kasse/layout Y gap is missing'
require_contains "$JS" "Mobile.Margin.X" 'mobile element X control is missing'
require_contains "$JS" "Mobile.Gap.Y" 'mobile Kasse/layout Y gap is missing'
require_contains "$JS" "class: 'h18-section-module-box h18-canvas-direct-controls h18-ud-lego-spacing-panel'" 'Inspector controls are not inside the existing content-history boundary'
require_contains "$JS" "\$field.trigger('input');" 'one Inspector edit does not feed the existing page-history checkpoint'
require_contains "$JS" "data-h18-lego-spacing-runtime', '0.8.30'" 'runtime identity is missing'
require_contains "$JS" "h18_lego_spacing[" 'save payload is missing'

require_contains "$CSS" 'column-gap:var(--h18-lego-gap-x' 'separate desktop X gap is not applied'
require_contains "$CSS" 'row-gap:var(--h18-lego-gap-y' 'separate desktop Y gap is not applied'
require_contains "$CSS" 'var(--h18-lego-mobile-gap-x' 'mobile X gap is not applied'
require_contains "$CSS" 'var(--h18-lego-mobile-margin-y' 'mobile Y margin is not applied'

# LEGO-001/021: no second history stack, no own Undo/Redo command path.
if grep -Ei 'editorHistoryEntries|historyEntries|undoStack|redoStack|addEventListener\([^,]*(undo|redo)|\.on\([^,]*(undo|redo)' "$JS" >/dev/null; then
  echo 'FAIL: LEGO spacing introduced a second history/Undo runtime'
  exit 1
fi

# Foundation is admin/editor state only. Public/post renderer mutations stay locked.
if grep -Ei 'wp_update_post|wp_insert_post|set_post_thumbnail|update_post_meta|delete_post_meta|template_redirect|wp_head|wp_footer|wp_nav_menu' "$MODEL" "$CTRL" "$JS" >/dev/null; then
  echo 'FAIL: LEGO spacing foundation introduced public/post mutation primitives'
  exit 1
fi

php tests/Architecture/v0830-lego-spacing-smoke.php
php -l "$MODEL" >/dev/null
php -l "$CTRL" >/dev/null
php -l "$BOOT" >/dev/null
node --check "$JS"

echo 'v0.8.30 LEGO shared X/Y spacing/history contract: PASS'
