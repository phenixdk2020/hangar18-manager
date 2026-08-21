#!/usr/bin/env bash
set -euo pipefail

MODEL='src/Editor/LegoResponsiveDesignModel.php'
BASE_MODEL='src/Editor/LegoDesignModel.php'
CTRL='src/Admin/EditorLegoResponsiveDesignAdminController.php'
BASE_CTRL='src/Admin/EditorLegoDesignAdminController.php'
RESTORE='src/Backup/SiteBackupRestoreCoordinator.php'
JS='assets/ultimate-designer-lego-design-responsive-v0833.js'
GUARD='assets/ultimate-designer-lego-design-responsive-event-guard-v0833.js'
CSS='assets/ultimate-designer-lego-design-responsive-v0833.css'

for file in "$MODEL" "$BASE_MODEL" "$CTRL" "$BASE_CTRL" "$RESTORE" "$JS" "$GUARD" "$CSS"; do
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

require_contains "$MODEL" 'public const SCHEMA_VERSION = 1;' 'responsive design schema missing'
require_contains "$MODEL" "'Tablet' => self::normalizeDevice" 'Tablet responsive model missing'
require_contains "$MODEL" "'Mobile' => self::normalizeDevice" 'Mobile responsive model missing'
require_contains "$MODEL" "'HasOverride' =>" 'override-presence marker missing'
require_contains "$MODEL" 'public static function setInheritance' 'inheritance transition helper missing'
require_contains "$MODEL" "if (!\$inherit && empty(\$responsive[\$device]['HasOverride']))" 'first override is not seeded from current Desktop'
require_contains "$MODEL" "'Design'=>\$desktop" 'inherited device is not a live Desktop view'

require_contains "$BASE_CTRL" 'EditorLegoResponsiveDesignAdminController::register();' 'responsive design layer is not registered after v0.8.32'
require_contains "$CTRL" "public const OPTION = 'hangar18_ultimate_designer_lego_design_responsive_v1';" 'responsive design option missing'
require_contains "$CTRL" 'assets/ultimate-designer-lego-design-responsive-event-guard-v0833.js' 'responsive select guard is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-lego-design-responsive-v0833.js' 'responsive design runtime is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-lego-design-responsive-v0833.css' 'responsive design CSS is not enqueued'
require_contains "$CTRL" "'hangar18-ultimate-designer-history-content-v0823'" 'existing history owner is not explicit dependency'
require_contains "$CTRL" "'hangar18-ultimate-designer-lego-design-v0832'" 'responsive design does not layer after common design'
require_contains "$CTRL" "add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 5);" 'responsive additive save bridge missing'

require_contains "$JS" "const STATE_CLASS = 'h18-lego-responsive-design-state-json';" 'canonical responsive row field missing'
require_contains "$JS" 'HasOverride' 'runtime does not preserve override ownership'
require_contains "$JS" "state[device].Design = desktopState(\$row);" 'first override is not seeded from current Desktop in browser runtime'
require_contains "$JS" "state[panelDevice].HasOverride = true;" 'responsive edits do not mark explicit override'
require_contains "$JS" "if (captureHistory) { \$field.trigger('input'); }" 'responsive changes are not routed through existing history event'
require_contains "$JS" "data-h18-lego-responsive-design-runtime','0.8.33'" 'responsive runtime marker missing'
require_contains "$JS" "data-h18-responsive-hover-shadow" 'hover effect is not independent from hover color mode'
require_contains "$GUARD" 'select[data-h18-rd-path]' 'responsive select duplicate-event guard missing'
require_contains "$GUARD" 'event.stopPropagation();' 'responsive select duplicate-event guard inactive'
require_contains "$CSS" 'data-h18-responsive-design-active="1"' 'responsive preview overlay CSS missing'
require_contains "$CSS" 'data-h18-responsive-hover-shadow="1"' 'responsive hover shadow CSS missing'

require_contains "$RESTORE" "LEGO_RESPONSIVE_DESIGN_OPTION = 'hangar18_ultimate_designer_lego_design_responsive_v1'" 'B2 responsive design option integration missing'
require_contains "$RESTORE" "'LegoResponsiveDesignRestored'" 'selective B2 responsive design result missing'
require_contains "$RESTORE" 'restoreSelectivePageOption' 'shared selective page option restore helper missing'

# The responsive layer may persist only its additive option. It must not mutate posts,
# public rendering, menus, or create another drag/drop/history implementation.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|template_redirect|wp_head|wp_footer|wp_nav_menu' "$MODEL" "$CTRL" "$JS" "$GUARD" >/dev/null; then
  echo 'FAIL: responsive design introduced public/post mutation primitives'
  exit 1
fi
if grep -Ei 'editorHistoryEntries|historyEntries|undoStack|redoStack|sortable\(|draggable\(|droppable\(' "$JS" "$GUARD" >/dev/null; then
  echo 'FAIL: responsive design introduced parallel history or drag/drop state'
  exit 1
fi
if grep -Ei 'localStorage|sessionStorage' "$JS" "$GUARD" >/dev/null; then
  echo 'FAIL: responsive design introduced browser-only persistence'
  exit 1
fi

php tests/Architecture/v0833-lego-responsive-design-smoke.php
php -l "$MODEL" >/dev/null
php -l "$CTRL" >/dev/null
php -l "$RESTORE" >/dev/null
node --check "$JS"
node --check "$GUARD"

echo 'v0.8.33 LEGO responsive common design contract: PASS'
