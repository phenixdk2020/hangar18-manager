#!/usr/bin/env bash
set -euo pipefail

MODEL='src/Editor/LegoDesignModel.php'
STATE_MODEL='src/Editor/LegoInteractionStateModel.php'
RESP_MODEL='src/Editor/LegoResponsiveDesignModel.php'
CTRL='src/Admin/EditorLegoInteractionStatesAdminController.php'
RESP_CTRL='src/Admin/EditorLegoResponsiveDesignAdminController.php'
JS='assets/ultimate-designer-lego-interaction-states-v0834.js'
GUARD='assets/ultimate-designer-lego-interaction-states-event-guard-v0834.js'
SNAPSHOT='assets/ultimate-designer-lego-interaction-snapshot-v0834.js'
CSS='assets/ultimate-designer-lego-interaction-states-v0834.css'

for file in "$MODEL" "$STATE_MODEL" "$RESP_MODEL" "$CTRL" "$RESP_CTRL" "$JS" "$GUARD" "$SNAPSHOT" "$CSS"; do
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

require_contains "$MODEL" 'public const SCHEMA_VERSION = 2;' 'common design schema was not extended'
require_contains "$MODEL" "'Motion.Transition' => 'TransitionPreset'" 'transition is not mapped to legacy field'
require_contains "$MODEL" "'States.Focus.Style' => 'FocusRingStyle'" 'focus style is not mapped'
require_contains "$MODEL" "'States.Active.Effect' => 'ActiveEffect'" 'active effect is not mapped'
require_contains "$MODEL" "'States.Disabled.Opacity' => 'DisabledOpacityPercent'" 'disabled opacity is not mapped'
require_contains "$MODEL" 'public static function transitionPresets()' 'transition vocabulary missing'
require_contains "$MODEL" 'public static function focusStyles()' 'focus vocabulary missing'
require_contains "$MODEL" 'public static function activeEffects()' 'active vocabulary missing'

require_contains "$STATE_MODEL" 'final class LegoInteractionStateModel' 'interaction subset model missing'
require_contains "$STATE_MODEL" 'public static function fromDesign' 'interaction read view missing'
require_contains "$STATE_MODEL" 'public static function mergeIntoDesign' 'interaction merge helper missing'
require_contains "$RESP_MODEL" 'LegoDesignModel::normalizeState' 'responsive model no longer normalizes through common design model'

require_contains "$RESP_CTRL" 'EditorLegoInteractionStatesAdminController::register();' 'interaction layer is not registered after responsive design'
require_contains "$CTRL" 'EditorLegoResponsiveDesignAdminController::OPTION' 'interaction layer introduced or missed shared responsive option'
require_contains "$CTRL" "add_action('admin_post_h18_save_page_editor', [self::class, 'preserveBeforeSave'], 4);" 'pre-save snapshot hook missing'
require_contains "$CTRL" "add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 6);" 'post-responsive merge hook missing'
require_contains "$CTRL" "'InteractionHasOverride'" 'interaction override marker missing'
require_contains "$CTRL" "'InteractionHasSnapshot'" 'interaction snapshot marker missing'
require_contains "$CTRL" 'Preserve the snapshot even while inheritance is active' 'inactive override preservation is not explicit'
require_contains "$CTRL" 'LegoInteractionStateModel::mergeIntoDesign' 'interaction state is not merged into existing device Design'
require_contains "$CTRL" 'assets/ultimate-designer-lego-interaction-states-v0834.js' 'interaction runtime is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-lego-interaction-states-event-guard-v0834.js' 'interaction select guard is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-lego-interaction-snapshot-v0834.js' 'interaction snapshot runtime is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-lego-interaction-states-v0834.css' 'interaction CSS is not enqueued'
require_contains "$CTRL" "'hangar18-ultimate-designer-history-content-v0823'" 'existing history owner is not explicit dependency'
require_contains "$CTRL" "'hangar18-ultimate-designer-lego-design-responsive-v0833'" 'interaction layer does not load after responsive design'

require_contains "$JS" "const STATE_CLASS = 'h18-lego-interaction-states-state-json';" 'canonical interaction row field missing'
require_contains "$JS" "HasOverride" 'responsive interaction override ownership missing'
require_contains "$JS" "state[device].Interaction = desktopInteraction(\$row);" 'first interaction override is not seeded from current Desktop'
require_contains "$JS" "if (captureHistory) { \$field.trigger('input'); }" 'responsive interaction edits are not routed through existing history event'
require_contains "$JS" "data-h18-lego-interaction-states-runtime','0.8.34'" 'interaction runtime marker missing'
require_contains "$JS" "text:'LEGO-design · States'" 'Inspector state panel missing'
require_contains "$JS" "text:'Arv interaktions-states fra Desktop'" 'interaction inheritance UI missing'
require_contains "$JS" "data-h18-i-role" 'Kasse/element shared panel role missing'
require_contains "$JS" "Focus.Style" 'Focus controls missing'
require_contains "$JS" "Active.Effect" 'Active controls missing'
require_contains "$JS" "Disabled.Opacity" 'Disabled controls missing'
require_contains "$JS" "h18_lego_interaction_states[" 'interaction save payload missing'
require_contains "$GUARD" 'select[data-h18-i-path]' 'interaction select duplicate-event guard missing'
require_contains "$GUARD" 'event.stopPropagation();' 'interaction select duplicate-event guard inactive'
require_contains "$SNAPSHOT" 'HasSnapshot' 'reversible snapshot metadata is not submitted'
require_contains "$SNAPSHOT" 'InteractionHasSnapshot' 'stored snapshot ownership is not rehydrated'
require_contains "$SNAPSHOT" "data-h18-lego-interaction-snapshot-runtime', '0.8.34'" 'snapshot runtime marker missing'
require_contains "$CSS" '.h18-i-panel' 'interaction Inspector CSS missing'
require_contains "$CSS" 'data-h18-interaction-states="1"' 'interaction preview CSS marker missing'

# This slice may persist only through the already existing responsive option and
# existing legacy page-section save. It must not add frontend hooks, post writes,
# another drag/drop engine or another history stack.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|template_redirect|wp_head|wp_footer|wp_nav_menu' "$STATE_MODEL" "$CTRL" "$JS" "$GUARD" "$SNAPSHOT" >/dev/null; then
  echo 'FAIL: interaction states introduced public/post mutation primitives'
  exit 1
fi
if grep -Ei 'editorHistoryEntries|historyEntries|undoStack|redoStack|sortable\(|draggable\(|droppable\(' "$JS" "$GUARD" "$SNAPSHOT" >/dev/null; then
  echo 'FAIL: interaction states introduced parallel history or drag/drop state'
  exit 1
fi
if grep -Ei 'localStorage|sessionStorage' "$JS" "$GUARD" "$SNAPSHOT" >/dev/null; then
  echo 'FAIL: interaction states introduced browser-only persistence'
  exit 1
fi

php tests/Architecture/v0834-lego-interaction-states-smoke.php
php -l "$MODEL" >/dev/null
php -l "$STATE_MODEL" >/dev/null
php -l "$RESP_MODEL" >/dev/null
php -l "$CTRL" >/dev/null
node --check "$JS"
node --check "$GUARD"
node --check "$SNAPSHOT"

echo 'v0.8.34 LEGO interaction states contract: PASS'
