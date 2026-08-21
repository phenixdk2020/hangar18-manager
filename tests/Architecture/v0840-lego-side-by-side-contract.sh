#!/usr/bin/env bash
set -euo pipefail

NEST='assets/ultimate-designer-nesting-tools.js'
DROP='assets/ultimate-designer-lego-drop-zones-v0838.js'
ATOMIC='assets/ultimate-designer-history-atomic-v0840.js'
CTRL='src/Admin/EditorLegoDropZonesAdminController.php'
SPEC='tests/Architecture/browser/lego-drop-zones-v0838.spec.cjs'
HISTORY_SPEC='tests/Architecture/browser/lego-side-by-side-history-v0840.spec.cjs'

for file in "$NEST" "$DROP" "$ATOMIC" "$CTRL" "$SPEC" "$HISTORY_SPEC"; do
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

# LEGO-031 extends the existing Auto-kasser hierarchy instead of introducing a
# second placement/parent store.
require_contains "$NEST" 'function canPlaceRowBeside($source, $target)' 'generic side compatibility guard missing'
require_contains "$NEST" 'function createAutoForRows($source, $target, side)' 'generic Auto-kasser adapter missing'
require_contains "$NEST" 'function placeRowBeside($source, $target, side)' 'generic side placement missing'
require_contains "$NEST" 'function finishNewElementBeside(beforeKeys, type, targetKey, side)' 'palette generic side completion missing'
require_contains "$NEST" 'const $children = directChildren($auto);' 'Auto-kasser still filters out ordinary children'
require_contains "$NEST" "'data-h18-v0840-auto-child': childKey" 'ordinary Auto-kasser visible tile marker missing'
require_contains "$NEST" '.h18-layout-parent-key' 'LayoutParentKey authority missing'
require_contains "$NEST" 'data-h18-v0840-side-by-side-runtime' 'v0.8.40 placement runtime marker missing'

# Visual Left/Right targets remain a thin adapter to the established v0.8.11
# side-zone contract and now also activate for ordinary elements.
require_contains "$DROP" "classes.push('h18-v0811-side-zone');" 'visual side zones no longer reuse placement contract'
require_contains "$DROP" "attrs['data-side'] = position;" 'side data-side contract missing'
require_contains "$DROP" "attrs['data-box'] = targetKey;" 'side data-box contract missing'
require_contains "$DROP" "dragMode = boxSource ? 'palette-box' : 'palette-element';" 'ordinary palette drag mode missing'
require_contains "$DROP" "data-h18-lego-side-by-side-runtime', '0.8.40'" 'v0.8.40 visual runtime marker missing'
require_contains "$DROP" "attrs['data-h18-v0840-generic-side-contract'] = '1';" 'generic side-zone marker missing'

# One drag/drop action is batched in front of the existing history owner. The
# adapter never owns snapshots, Undo/Redo entries or persistence itself.
require_contains "$ATOMIC" "callback.name === 'editorHistoryRecordNow'" 'atomic adapter does not target existing core history callback'
require_contains "$ATOMIC" 'window.__h18HistoryCoreBridgeV0821' 'existing v0.8.21 history bridge is not reused'
require_contains "$ATOMIC" "begin('palette-drag-drop')" 'palette drag atomic transaction missing'
require_contains "$ATOMIC" "begin('existing-row-drag-drop')" 'sortable drag atomic transaction missing'
require_contains "$ATOMIC" 'window.__h18HistoryAtomicV0840' 'atomic transaction API marker missing'
require_contains "$CTRL" 'hangar18-ultimate-designer-history-atomic-v0840' 'atomic adapter is not loaded by LEGO editor controller'
require_contains "$CTRL" "'hangar18-ultimate-designer-nesting-tools'" 'atomic adapter does not load after authoritative placement owner'

# Browser regressions prove ordinary-to-ordinary placement, old Kasse placement,
# and the one-checkpoint Undo/Redo requirement including wrapper/order/parents.
require_contains "$SPEC" 'LEGO-031 dropping ordinary element beside ordinary element creates authoritative Auto-kasser' 'generic side-drop browser regression missing'
require_contains "$SPEC" "toHaveValue('auto-1'" 'generic authoritative parent assertion missing'
require_contains "$SPEC" 'dropping existing Kasse on v0.8.38 Left zone is executed by existing nesting motor' 'Kasse side-drop regression missing'
require_contains "$HISTORY_SPEC" 'LEGO-031 side-drop is one history checkpoint and Undo Redo restores wrapper order and parents' 'atomic history browser regression missing'
require_contains "$HISTORY_SPEC" 'expect(current.entries).toBe(2)' 'one-checkpoint assertion missing'
require_contains "$HISTORY_SPEC" "expect(current.keys).toEqual(['auto-1','text-1','text-2'])" 'wrapper/order restore assertion missing'
require_contains "$HISTORY_SPEC" "expect(current.parents['text-1']).toBe('auto-1')" 'parent restore assertion missing'

# No duplicate persistence/history/public-rendering owner in the LEGO adapters.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_|wp_ajax_|undoStack|redoStack|historyEntries|editorHistoryEntries' "$NEST" "$DROP" "$ATOMIC" >/dev/null; then
  echo 'FAIL: LEGO-031 introduced a second persistence/history/public-cutover owner'
  exit 1
fi

node --check "$NEST"
node --check "$DROP"
node --check "$ATOMIC"
node --check "$SPEC"
node --check "$HISTORY_SPEC"
php -l "$CTRL" >/dev/null

echo 'v0.8.40 LEGO ordinary side-by-side + atomic history contract: PASS'
