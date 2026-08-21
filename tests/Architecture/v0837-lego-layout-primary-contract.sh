#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-lego-layout-primary-v0837.js'
CSS='assets/ultimate-designer-lego-layout-primary-v0837.css'
CTRL='src/Admin/EditorLegoLayoutPrimaryAdminController.php'
PRIMARY_CTRL='src/Admin/EditorLegoPrimaryViewAdminController.php'
SPEC='tests/Architecture/browser/lego-layout-primary-v0837.spec.cjs'

for file in "$JS" "$CSS" "$CTRL" "$PRIMARY_CTRL" "$SPEC"; do
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

require_contains "$JS" "const STATE_CLASS = 'h18-lego-layout-primary-state-json';" 'canonical layout row state is missing'
require_contains "$JS" 'Tablet|Mobile' 'responsive legacy layout prefixes are not covered'
require_contains "$JS" 'PaddingPx|HorizontalPaddingPx|TopSpacingPx|BottomSpacingPx|WidthPercent|MinHeightPx' 'core layout field family is incomplete'
require_contains "$JS" 'Columns|MobileColumns|ColumnGapPx|MobileColumnGapPx' 'specialized grid layout fields are incomplete'
require_contains "$JS" "document.addEventListener('input', captureLayoutValue, true);" 'layout mirror must run before delegated history handlers'
require_contains "$JS" "document.addEventListener('change', captureLayoutValue, true);" 'change/select layout mirror is missing'
require_contains "$JS" "data-h18-v0837-layout-proxy" 'Direct Design/Inspector canonical marker is missing'
require_contains "$JS" 'this hidden canonical state deliberately emits no second input event' 'single-history ownership comment/contract is missing'
require_contains "$CTRL" "\$page !== 'hangar18-pages'" 'layout bridge must remain admin page scoped'
require_contains "$CTRL" "current_user_can('edit_pages')" 'layout bridge capability gate is missing'
require_contains "$CTRL" 'hangar18-ultimate-designer-lego-primary-view-v0836' 'layout bridge must load after primary design view'
require_contains "$PRIMARY_CTRL" 'EditorLegoLayoutPrimaryAdminController::register();' 'layout bridge is not registered after primary design view'
require_contains "$SPEC" 'Direct Design layout mirrors into canonical row state before one existing checkpoint' 'Direct Design single-checkpoint regression is missing'
require_contains "$SPEC" 'Inspector layout input updates the same canonical row state without a second state event' 'Inspector canonical regression is missing'
require_contains "$SPEC" 'history-style DOM restore brings legacy layout and canonical state back together' 'history DOM restore regression is missing'
require_contains "$SPEC" 'specialized Columns and MobileColumnGap keep exact legacy semantics inside canonical state' 'grid layout compatibility regression is missing'

# v0.8.37 is a view/history mirror only. Persistence, public renderer,
# placement and history engines remain the existing owners.
if grep -Ei 'update_option|add_option|delete_option|wp_update_post|wp_insert_post|admin_post_|wp_ajax_|localStorage|sessionStorage|undoStack|redoStack|historyEntries|editorHistoryEntries|sortable\(' "$JS" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.37 introduced a persistence, placement or parallel history primitive'
  exit 1
fi

node --check "$JS"
node --check "$SPEC"
php -l "$CTRL" >/dev/null
php -l "$PRIMARY_CTRL" >/dev/null

echo 'v0.8.37 LEGO primary layout canonicalization contract: PASS'
