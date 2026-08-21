#!/usr/bin/env bash
set -euo pipefail

NESTING='assets/ultimate-designer-nesting-tools.js'
SPACING='assets/ultimate-designer-lego-spacing-v0831.js'
RESPONSIVE='assets/ultimate-designer-lego-design-responsive-v0833.js'
INTERACTION='assets/ultimate-designer-lego-interaction-states-v0834.js'
SPEC='tests/Architecture/browser/lego-consolidation-v0835.spec.cjs'
ADMIN='assets/admin.js'

for file in "$NESTING" "$SPACING" "$RESPONSIVE" "$INTERACTION" "$SPEC" "$ADMIN"; do
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

# Existing placement model remains authoritative.
require_contains "$NESTING" 'const MAX_NESTING_DEPTH = 2;' 'nesting depth contract changed'
require_contains "$NESTING" 'function setParent($row, key)' 'existing parent setter is missing'
require_contains "$NESTING" '.h18-layout-parent-key' 'LayoutParentKey is no longer the shared hierarchy field'
require_contains "$NESTING" 'function moveRowIntoBox($row, $box)' 'existing element-to-Kasse placement motor is missing'
require_contains "$NESTING" 'function moveBoxIntoAuto($row, $auto)' 'existing Kasse-to-Auto placement motor is missing'
require_contains "$ADMIN" 'layoutParentCapableV0519' 'legacy/canonical parent capability bridge is missing'

# Existing three LEGO state layers must remain independent views over the same row/history owner.
require_contains "$SPACING" '.h18-lego-spacing-state-json' 'spacing canonical row state is missing'
require_contains "$RESPONSIVE" '.h18-lego-responsive-design-state-json' 'responsive design canonical row state is missing'
require_contains "$INTERACTION" '.h18-lego-interaction-states-state-json' 'interaction canonical row state is missing'

# v0.8.35 consolidation must exercise all critical combinations in one browser DOM.
require_contains "$SPEC" "Auto-kasser -> Kasse -> Kasse + element" 'nested consolidation case is missing'
require_contains "$SPEC" "spacing responsive design and interaction state stay independent" 'combined state isolation case is missing'
require_contains "$SPEC" "one combined history-style DOM restore" 'combined history restore case is missing'
require_contains "$SPEC" "data-h18-lego-path=\"Tablet.Gap.X\"" 'Tablet spacing edit is not covered'
require_contains "$SPEC" "data-h18-rd-path=\"Radius.All\"" 'Tablet responsive design edit is not covered'
require_contains "$SPEC" "data-h18-i-path=\"Active.Effect\"" 'Tablet Active state edit is not covered'
require_contains "$SPEC" "data-h18-i-path=\"Focus.Color\"" 'Tablet Focus state edit is not covered'
require_contains "$SPEC" "data-h18-v0811-child=\"box-b\"" 'Kasse-i-Kasse composition is not covered'
require_contains "$SPEC" "data-h18-v0811-child=\"text-1\"" 'element-i-Kasse composition is not covered'
require_contains "$SPEC" "data-h18-v0811-box=\"box-a\"" 'Kasse-i-Auto-kasser composition is not covered'

# The v0.8.35 test-only slice must not introduce a second motor/store/history implementation.
if grep -Ei 'update_option|add_option|delete_option|admin_post_|wp_ajax_|localStorage|sessionStorage|undoStack|redoStack|historyEntries|editorHistoryEntries' "$SPEC" >/dev/null; then
  echo 'FAIL: consolidation test introduced or assumes a parallel persistence/history store'
  exit 1
fi

node --check "$SPEC"
echo 'v0.8.35 LEGO consolidation / primary-editor readiness contract: PASS'
