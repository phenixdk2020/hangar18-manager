#!/usr/bin/env bash
set -euo pipefail

MODEL='src/Editor/LegoDesignModel.php'
CTRL='src/Admin/EditorLegoDesignAdminController.php'
SPACING_CTRL='src/Admin/EditorLegoSpacingAdminController.php'
JS='assets/ultimate-designer-lego-design-v0832.js'
GUARD='assets/ultimate-designer-lego-design-event-guard-v0832.js'
CSS='assets/ultimate-designer-lego-design-v0832.css'

for file in "$MODEL" "$CTRL" "$SPACING_CTRL" "$JS" "$GUARD" "$CSS"; do
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

require_contains "$MODEL" 'public const SCHEMA_VERSION = 1;' 'common design schema is missing'
require_contains "$MODEL" 'public static function legacyFieldMap' 'canonical-to-legacy mapping is missing'
require_contains "$MODEL" "'Colors.Background' => 'CustomBackgroundColor'" 'background mapping is missing'
require_contains "$MODEL" "'Border.Width' => 'BorderWidthPx'" 'border mapping is missing'
require_contains "$MODEL" "'Radius.TopLeft' => 'RadiusTopLeftPx'" 'per-corner radius mapping is missing'
require_contains "$MODEL" "'Typography.BodyFont' => 'SectionBodyFontFamily'" 'typography mapping is missing'
require_contains "$MODEL" "'Effects.Shadow' => 'ShadowStyle'" 'effects mapping is missing'
require_contains "$MODEL" "'States.Hover.Mode' => 'HoverStyleMode'" 'hover state mapping is missing'
require_contains "$MODEL" 'public static function fromLegacy' 'legacy-derived canonical model is missing'
require_contains "$MODEL" 'public static function toLegacy' 'canonical roundtrip support is missing'

require_contains "$SPACING_CTRL" 'EditorLegoDesignAdminController::register();' 'v0.8.32 design layer is not registered after spacing'
require_contains "$CTRL" 'assets/ultimate-designer-lego-design-v0832.js' 'v0.8.32 design runtime is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-lego-design-event-guard-v0832.js' 'v0.8.32 select event guard is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-lego-design-v0832.css' 'v0.8.32 design CSS is not enqueued'
require_contains "$CTRL" "'hangar18-ultimate-designer-history-content-v0823'" 'existing history owner is not an explicit dependency'
require_contains "$CTRL" "'hangar18-ultimate-designer-lego-spacing-v0831'" 'common design does not layer after responsive spacing'
require_contains "$CTRL" "'fieldMap' => LegoDesignModel::legacyFieldMap()" 'runtime field map is not sourced from canonical PHP model'

require_contains "$JS" "const PANEL_ID = 'h18-ud-lego-design-panel';" 'common design inspector panel is missing'
require_contains "$JS" "return ['container', 'grid', 'flex'].indexOf(rowType(\$row)) !== -1;" 'Kasse/Grid/Flex does not use the shared design runtime'
require_contains "$JS" "data-h18-lego-design-path" 'canonical path controls are missing'
require_contains "$JS" "setFieldSilently(\$row, 'DesignMode', 'Custom');" 'normal-state companion mode transaction is missing'
require_contains "$JS" "setFieldSilently(\$row, 'HoverStyleMode', 'Custom');" 'hover companion mode transaction is missing'
require_contains "$JS" "\$actual.trigger(eventType === 'change' ? 'change' : 'input');" 'LEGO design is not routed through existing form/history events'
require_contains "$JS" "data-h18-lego-design-state" 'derived canonical row-state marker is missing'
require_contains "$JS" "version: '0.8.32'" 'runtime identity is missing'
require_contains "$GUARD" "select[data-h18-lego-design-path]" 'select duplicate-event guard is not scoped to LEGO design controls'
require_contains "$GUARD" "event.stopPropagation();" 'select duplicate-event guard is not active'
require_contains "$GUARD" "data-h18-lego-design-select-guard" 'select guard runtime marker is missing'

# v0.8.32 must not introduce another persistence store or save endpoint.
if grep -Ei 'update_option|add_option|delete_option|admin_post_|wp_ajax_|localStorage|sessionStorage' "$CTRL" "$JS" "$GUARD" >/dev/null; then
  echo 'FAIL: common design introduced parallel persistence/save state'
  exit 1
fi

# v0.8.32 must still use the existing history motor, never a second stack or command handler.
if grep -Ei 'editorHistoryEntries|historyEntries|undoStack|redoStack|addEventListener\([^,]*(undo|redo)|\.on\([^,]*(undo|redo)' "$JS" "$GUARD" >/dev/null; then
  echo 'FAIL: common design introduced a second history/Undo runtime'
  exit 1
fi

# Admin-only design layer must not add public/post mutation primitives.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|template_redirect|wp_head|wp_footer|wp_nav_menu' "$MODEL" "$CTRL" "$JS" "$GUARD" >/dev/null; then
  echo 'FAIL: common design introduced public/post mutation primitives'
  exit 1
fi

php tests/Architecture/v0832-lego-common-design-smoke.php
php -l "$MODEL" >/dev/null
php -l "$CTRL" >/dev/null
php -l "$SPACING_CTRL" >/dev/null
node --check "$JS"
node --check "$GUARD"

echo 'v0.8.32 LEGO common element/Kasse design contract: PASS'
