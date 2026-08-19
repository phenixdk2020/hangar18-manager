#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/EditorLayoutToolsAdminController.php'
NEST='assets/ultimate-designer-nesting-tools.js'
LAYOUT='assets/ultimate-designer-layout-tools.js'
CSS='assets/ultimate-designer-nesting-tools.css'

for file in "$CTRL" "$NEST" "$LAYOUT" "$CSS"; do
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

# Exactly one live Kasse placement authority; obsolete composers remain disabled.
require_contains "$CTRL" 'enqueueEditorHistoryGuardV0813' 'history guard is not registered'
require_contains "$CTRL" 'enqueueKasseDragAuthorityV0813' 'Kasse drag authority shim is not registered'
if grep -F 'self::enqueueV0810KasseRuntime();' "$CTRL" >/dev/null; then
  echo 'FAIL: obsolete v0.8.10 Kasse runtime is still enqueued'
  exit 1
fi
if grep -F "'hangar18-ultimate-designer-visual-composition'" "$CTRL" >/dev/null; then
  echo 'FAIL: obsolete visual-composition runtime is live'
  exit 1
fi
require_contains "$CTRL" 'data-h18-v0813-kasse-authority' 'v0.8.13 authority marker is missing'
require_contains "$CTRL" 'data-h18-v0814-kasse-authority' 'v0.8.14 authority marker is missing'
require_contains "$CTRL" "removeAttribute('data-h18-layout-tool')" 'layout-tools Kasse claim is not neutralized during dragstart'
require_contains "$CTRL" "setTimeout(function () { item.setAttribute('data-h18-layout-tool', 'box'); }, 0);" 'Kasse palette metadata is not restored after dragstart'

# Undo/redo restore transaction must outlive MutationObserver/derived Kasse settling.
require_contains "$CTRL" '__h18HistoryObserverGuardV0813' 'Undo/Redo observer guard is missing'
require_contains "$CTRL" '__h18HistoryTransactionV0814' 'v0.8.14 history transaction guard is missing'
require_contains "$CTRL" "meta.target.id === 'h18-page-editor-form'" 'Undo/Redo guard is not scoped to the page-editor history observer'
require_contains "$CTRL" '#h18-editor-undo,#h18-editor-redo' 'Undo/Redo controls do not activate the settle guard'
require_contains "$CTRL" 'api.suppress(520)' 'Undo/Redo settle transaction is too short/missing'
require_contains "$CTRL" "callback.name === 'editorHistoryRecordNow'" 'derived history capture is not guarded during restore'

# Kasse in Kasse is allowed subject to cycle/depth guard; side placement alone creates Auto-kasser.
require_contains "$NEST" 'function canMoveIntoBox($row, $box)' 'inside-Kasse acceptance guard is missing'
if grep -F '!isBox($box) || isBox($row)' "$NEST" >/dev/null; then
  echo 'FAIL: Kasse source is still categorically rejected as a child'
  exit 1
fi
require_contains "$NEST" 'function subtreeDepth($row)' 'subtree depth guard is missing'
require_contains "$NEST" 'function parentDepth($row)' 'parent depth guard is missing'
require_contains "$NEST" 'function wouldCreateCycle($row, $box)' 'cycle guard is missing'
require_contains "$NEST" 'function finishNewBoxInside(beforeKeys, targetKey)' 'new Kasse cannot finish as a child of another Kasse'
require_contains "$NEST" "state.mode = 'inside';" 'palette Kasse does not resolve an inside-drop mode'
require_contains "$NEST" "state.mode = 'side';" 'palette Kasse does not resolve a side-drop mode'
require_contains "$NEST" 'createAutoForBoxes($source, $target, side)' 'side-drop cannot create/reuse Auto-kasser composition'
require_contains "$NEST" 'placeBoxBeside($source, $target, side)' 'side placement path is missing'

# v0.8.14+: Auto-kasser is Grid-only at creation and explicitly accepts Kasse children.
if awk '/function configurePendingTool\(/,/^    }/' "$LAYOUT" | grep -F 'createInitialBox($row)' >/dev/null; then
  echo 'FAIL: Auto-kasser still creates an implicit Container together with Grid'
  exit 1
fi
require_contains "$NEST" 'function targetAutoForElement(element)' 'Auto-kasser target resolver is missing'
require_contains "$NEST" 'function canMoveBoxIntoAuto($row, $auto)' 'Auto-kasser acceptance guard is missing'
require_contains "$NEST" 'function moveBoxIntoAuto($row, $auto)' 'existing Kasse cannot move into Auto-kasser'
require_contains "$NEST" 'function finishNewBoxInAuto(beforeKeys, targetKey)' 'new Kasse cannot finish inside Auto-kasser'
require_contains "$NEST" "state.mode = 'auto';" 'palette Kasse does not resolve Auto-kasser drop mode'
require_contains "$NEST" 'data-h18-v0814-auto-drop' 'explicit Auto-kasser drop zone is missing'
require_contains "$NEST" 'data-h18-v0814-auto-key' 'Auto-kasser visible grid is not mapped to source Grid'
require_contains "$CSS" '.h18-v0814-auto-drop-zone' 'Auto-kasser drop zone has no visible styling'
require_contains "$CSS" '.h18-ud-auto-box-grid.h18-v0814-auto-drop-active' 'Auto-kasser active target feedback is missing'

# One palette drop is consumed once. A dragend after a handled drop may not create another element.
require_contains "$NEST" 'dropHandled: false' 'palette drag state lacks idempotent dropHandled flag'
require_contains "$NEST" 'state.dropHandled = true' 'drop handler does not mark the drop consumed'
require_contains "$NEST" 'if (!state.dropHandled)' 'dragend does not guard against duplicate completion'
require_contains "$NEST" 'suppressPaletteClickUntil' 'post-drag palette click suppression is missing'
require_contains "$NEST" 'stopImmediatePropagation' 'post-drag click is not fully consumed'

# Nested source rows stay storage-authoritative while the visible preview keeps child content.
require_contains "$NEST" 'clonePreview($child, isBox($child))' 'nested Kasse preview strips its own contents/dropzone'
require_contains "$NEST" 'h18-v0813-nested-box' 'nested Kasse visible proxy is missing'
require_contains "$NEST" 'data-h18-v0813-box-drop' 'explicit inside-Kasse drop target is missing'
if ! grep -E "text: 'v0\.8\.(14|15)'" "$NEST" >/dev/null; then
  echo 'FAIL: visible Kasse runtime badge is older than v0.8.14'
  exit 1
fi

# No public persistence/cutover primitives.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$NEST" "$CTRL" "$LAYOUT" >/dev/null; then
  echo 'FAIL: Kasse hotfix introduced public persistence/cutover primitive'
  exit 1
fi

node --check "$NEST"
node --check "$LAYOUT"
php -l "$CTRL" >/dev/null

echo 'v0.8.13-v0.8.15 Kasse authority/history contract: PASS'
