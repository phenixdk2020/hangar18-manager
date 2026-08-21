#!/usr/bin/env bash
set -euo pipefail

JS='assets/ultimate-designer-lego-drop-zones-v0838.js'
CSS='assets/ultimate-designer-lego-drop-zones-v0838.css'
CTRL='src/Admin/EditorLegoDropZonesAdminController.php'
PARENT_CTRL='src/Admin/EditorLegoLayoutPrimaryAdminController.php'
NESTING='assets/ultimate-designer-nesting-tools.js'
SPEC='tests/Architecture/browser/lego-drop-zones-v0838.spec.cjs'

for file in "$JS" "$CSS" "$CTRL" "$PARENT_CTRL" "$NESTING" "$SPEC"; do
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

# Four visual directions are present.
require_contains "$JS" "zone('over'" 'Over drop-zone missing'
require_contains "$JS" "zone('under'" 'Under drop-zone missing'
require_contains "$JS" "zone('left'" 'Venstre drop-zone missing'
require_contains "$JS" "zone('right'" 'Højre drop-zone missing'
require_contains "$CSS" '.h18-v0838-drop-zone.is-over' 'Over visual CSS missing'
require_contains "$CSS" '.h18-v0838-drop-zone.is-under' 'Under visual CSS missing'
require_contains "$CSS" '.h18-v0838-drop-zone.is-left' 'Venstre visual CSS missing'
require_contains "$CSS" '.h18-v0838-drop-zone.is-right' 'Højre visual CSS missing'

# Over/Under are passive over the existing sortable; side placement explicitly
# reuses the authoritative v0.8.11 Kasse motor contract.
require_contains "$CSS" '.h18-v0838-drop-zone.is-over,.h18-v0838-drop-zone.is-under{pointer-events:none}' 'Over/Under must not replace sortable hit-testing'
require_contains "$JS" "classes.push('h18-v0811-side-zone');" 'side zones do not reuse existing placement contract'
require_contains "$JS" "attrs['data-side'] = position;" 'existing side data-side contract missing'
require_contains "$JS" "attrs['data-box'] = targetKey;" 'existing side data-box contract missing'
require_contains "$NESTING" 'function sideZoneAtPoint(pageX, pageY, sourceKey)' 'authoritative side hit-test missing'
require_contains "$NESTING" 'function placeBoxBeside($source, $target, side)' 'authoritative side placement missing'
require_contains "$NESTING" 'function createAutoForBoxes($source, $target, side)' 'authoritative Auto-kasser creation missing'

# Existing element drags keep vertical placement only until LEGO-031 adds the
# existing-motor adapter for arbitrary side-by-side elements.
require_contains "$JS" "dragSourceType !== 'container'" 'generic element side compatibility guard missing'
require_contains "$JS" "classes.push('is-disabled');" 'unsupported side zones must be visually disabled'

# Admin-only, loaded after nesting + canonical layout stack.
require_contains "$CTRL" "\$page !== 'hangar18-pages'" 'drop zones not scoped to page editor'
require_contains "$CTRL" "current_user_can('edit_pages')" 'drop zones capability gate missing'
require_contains "$CTRL" 'hangar18-ultimate-designer-nesting-tools' 'nesting dependency missing'
require_contains "$CTRL" 'hangar18-ultimate-designer-lego-layout-primary-v0837' 'canonical layout dependency missing'
require_contains "$PARENT_CTRL" 'EditorLegoDropZonesAdminController::register();' 'drop-zone controller not registered after layout view'

# Browser regression proves the side zone is not just decorative: the existing
# nesting runtime consumes it and creates Auto-kasser/parent relations.
require_contains "$SPEC" 'dropping existing Kasse on v0.8.38 Left zone is executed by existing nesting motor' 'existing-motor integration test missing'
require_contains "$SPEC" "toHaveValue('auto-1'" 'parent relation integration assertion missing'
require_contains "$SPEC" 'generic element drag keeps Over Under but disables unsupported side-by-side targets' 'generic compatibility test missing'
require_contains "$SPEC" 'Kasse already inside Auto-kasser gets visual left/right proxy targets without new placement data' 'Auto-kasser proxy test missing'

# This slice is visual targeting only. It must not implement a second placement,
# persistence or history engine.
if grep -Ei 'setParent|insertBefore|insertAfter|appendTo|prependTo|sortable\(|update_option|add_option|delete_option|wp_update_post|wp_insert_post|admin_post_|wp_ajax_|undoStack|redoStack|historyEntries|editorHistoryEntries' "$JS" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.38 introduced placement/persistence/history primitives outside nesting-tools'
  exit 1
fi

node --check "$JS"
node --check "$SPEC"
php -l "$CTRL" >/dev/null

echo 'v0.8.38 LEGO visual four-way drop-zone contract: PASS'
