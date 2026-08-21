#!/usr/bin/env bash
set -euo pipefail

NEST='assets/ultimate-designer-nesting-tools.js'
DROP='assets/ultimate-designer-lego-drop-zones-v0838.js'
SPEC='tests/Architecture/browser/lego-drop-zones-v0838.spec.cjs'

for file in "$NEST" "$DROP" "$SPEC"; do
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

# Browser regression must prove ordinary-to-ordinary placement and preserve the
# earlier Kasse side-drop behavior.
require_contains "$SPEC" 'LEGO-031 dropping ordinary element beside ordinary element creates authoritative Auto-kasser' 'generic side-drop browser regression missing'
require_contains "$SPEC" "toHaveValue('auto-1'" 'generic authoritative parent assertion missing'
require_contains "$SPEC" 'dropping existing Kasse on v0.8.38 Left zone is executed by existing nesting motor' 'Kasse side-drop regression missing'

# No duplicate persistence/history/public-rendering owner in the LEGO adapter.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_|wp_ajax_|undoStack|redoStack|historyEntries|editorHistoryEntries' "$NEST" "$DROP" >/dev/null; then
  echo 'FAIL: LEGO-031 introduced a second persistence/history/public-cutover owner'
  exit 1
fi

node --check "$NEST"
node --check "$DROP"
node --check "$SPEC"

echo 'v0.8.40 LEGO ordinary side-by-side contract: PASS'
