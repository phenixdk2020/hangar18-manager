#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/EditorLayoutToolsAdminController.php'
ELEMENT_CTRL='src/Admin/EditorElementLibraryAdminController.php'
LAYOUT='assets/ultimate-designer-layout-tools.js'
NEST='assets/ultimate-designer-nesting-tools.js'
NEST_CSS='assets/ultimate-designer-nesting-tools.css'
BOX_CONTENT='assets/ultimate-designer-box-content-layout.js'
HISTORY_V0817='assets/ultimate-designer-history-v0817.js'
HISTORY_V0818='assets/ultimate-designer-history-v0818.js'
HISTORY_V0820='assets/ultimate-designer-history-preload-v0820.js'
HISTORY_V0821='assets/ultimate-designer-history-preload-v0821.js'

for file in "$CTRL" "$ELEMENT_CTRL" "$LAYOUT" "$NEST" "$NEST_CSS" "$BOX_CONTENT" "$HISTORY_V0817" "$HISTORY_V0818" "$HISTORY_V0820" "$HISTORY_V0821"; do
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

# Auto-kasser creation remains Grid-only in the normal layout tool.
require_contains "$LAYOUT" "if (tool === 'auto-row')" 'Auto-kasser tool path is missing'
require_contains "$LAYOUT" 'configureAutoRow($row);' 'Auto-kasser no longer configures the created Grid'
if awk '/function configurePendingTool\(/,/^    }/' "$LAYOUT" | grep -F 'createInitialBox($row)' >/dev/null; then
  echo 'FAIL: Auto-kasser creates an implicit Kasse again'
  exit 1
fi

# v0.8.14 inline Auto adapter may remain as dead rollback reference, but it must not be activated.
if grep -F 'self::enqueueAutoKasseAuthorityV0814();' "$CTRL" >/dev/null; then
  echo 'FAIL: duplicate v0.8.14 Auto-kasse placement runtime is still enqueued'
  exit 1
fi
require_contains "$CTRL" 'It is deliberately NOT enqueued' 'retired Auto-kasse adapter is not documented as inactive'

# The direct nesting runtime owns both new and existing Kasse -> Auto-kasser placement.
require_contains "$NEST" 'function targetAutoForElement(element)' 'palette Auto-kasser target resolution is missing'
require_contains "$NEST" 'function autoAtPoint(pageX, pageY, $draggedRow)' 'sortable Auto-kasser hit-test is missing'
require_contains "$NEST" 'function moveBoxIntoAuto($row, $auto)' 'existing Kasse cannot be parented into Auto-kasser'
require_contains "$NEST" 'function finishNewBoxInAuto(beforeKeys, targetKey)' 'new Kasse cannot be parented into Auto-kasser'
require_contains "$NEST" "state.mode = 'auto';" 'new Kasse Auto-kasser mode is missing'
require_contains "$NEST" "existingBoxDrag.mode = 'auto';" 'existing Kasse Auto-kasser mode is missing'
require_contains "$NEST" "text: 'v0.8.15'" 'v0.8.15 runtime badge is missing'
require_contains "$NEST" 'data-h18-v0815-kasse-runtime' 'v0.8.15 runtime marker is missing'

# v0.8.16 direct Auto-kasser drop safety.
if grep -F '#h18-page-sections-sortable>.h18-page-section-row[data-h18-nested-in-box]:not([data-h18-nested-in-box=""]){display:none!important}' "$NEST_CSS" >/dev/null; then
  echo 'FAIL: Kasse can still disappear solely because parent metadata was written'
  exit 1
fi
require_contains "$NEST_CSS" 'data-h18-v0811-child-source="1"]{display:none!important}' 'authoritative child-source hiding rule is missing'
require_contains "$NEST_CSS" 'h18-v0811-box-drag>.h18-page-section-row[data-section-type="grid"]>.h18-canvas-preview>.h18-v0814-auto-drop-zone' 'Auto-kasser drop zone does not expand over the full Grid canvas'
require_contains "$NEST_CSS" 'position:absolute;inset:0' 'full Auto-kasser direct-drop hit area is missing'
require_contains "$NEST_CSS" 'pointer-events:none' 'full Auto-kasser hit area blocks more specific Kasse-in-Kasse targeting'

# Hidden source rows may not become visually orphaned if the base editor rebuilds a canvas preview.
require_contains "$NEST" 'function compositionMissing()' 'composition loss detector is missing'
require_contains "$NEST" 'observer.observe($sections.get(0), { childList: true, subtree: true });' 'composition observer does not watch preview rebuilds'
require_contains "$NEST" '!$preview.children('"'"'.h18-ud-auto-box-grid'"'"').length' 'Auto-kasser missing-composition detection is absent'
require_contains "$NEST" '!$preview.children('"'"'.h18-ud-box-contents-preview'"'"').length' 'Kasse missing-composition detection is absent'

# The original restore observer guard remains scoped to the page editor.
require_contains "$CTRL" "callback.name === 'editorHistoryRecordNow'" 'history capture callback guard is missing'
require_contains "$CTRL" 'return 0;' 'suppressed history capture does not report that no timer exists'
if grep -F 'guard.remaining() + 30' "$CTRL" >/dev/null; then
  echo 'FAIL: restore-derived history capture is still delayed and replayed later'
  exit 1
fi
if grep -F 'return NativeSetTimeout(function () {}, 0);' "$CTRL" >/dev/null; then
  echo 'FAIL: suppressed history capture leaves a stale pending timer id'
  exit 1
fi
require_contains "$CTRL" "meta.target.id === 'h18-page-editor-form'" 'MutationObserver history suppression is not scoped to the page editor'
require_contains "$CTRL" '#h18-editor-undo,#h18-editor-redo' 'Undo/Redo does not start the restore transaction'

# v0.8.16 closes every legitimate restore entry point and preserves genuine user edits.
require_contains "$BOX_CONTENT" 'data-h18-v0816-history-guard' 'v0.8.16 history guard runtime marker is missing'
require_contains "$BOX_CONTENT" '#h18-editor-restore-draft' 'local draft restore is not guarded'
require_contains "$BOX_CONTENT" '#h18-command-palette-results .h18-command-result' 'command palette Undo/Redo is not guarded'
require_contains "$BOX_CONTENT" "label === 'Fortryd' || label === 'Gendan'" 'command palette history action detection is missing'
require_contains "$BOX_CONTENT" 'guard.markTrustedEdit = function' 'trusted post-Undo edit bridge is missing'
require_contains "$BOX_CONTENT" 'if (guard.hasTrustedEdit()) { return false; }' 'trusted post-Undo edits are still suppressed'
require_contains "$BOX_CONTENT" 'event.isTrusted !== true' 'programmatic restore events are not separated from real user input'
require_contains "$BOX_CONTENT" "document.addEventListener('input', markTrustedEditorEdit, true);" 'real input does not reopen history capture'
require_contains "$BOX_CONTENT" "document.addEventListener('change', markTrustedEditorEdit, true);" 'real change does not reopen history capture'
require_contains "$BOX_CONTENT" "document.addEventListener('pointerdown', markTrustedStructuralEdit, true);" 'real drag/sort actions do not reopen history capture'
require_contains "$BOX_CONTENT" '.h18-page-section-drag,' 'section drag is not treated as a genuine post-Undo edit'
require_contains "$BOX_CONTENT" '.h18-builder-palette-item,' 'palette add/drag is not treated as a genuine post-Undo edit'

# Older history assets remain rollback references only.
require_contains "$HISTORY_V0817" 'data-h18-v0817-history-latch' 'v0.8.17 rollback asset is missing'
require_contains "$HISTORY_V0818" 'data-h18-v0818-history-runtime' 'v0.8.18 rollback asset is missing'
require_contains "$HISTORY_V0820" 'data-h18-v0820-history-runtime' 'v0.8.20 rollback asset is missing'
if grep -F 'hangar18-ultimate-designer-history-v0817' "$ELEMENT_CTRL" >/dev/null; then
  echo 'FAIL: v0.8.17 is still enqueued'
  exit 1
fi
if grep -F 'hangar18-ultimate-designer-history-v0818' "$ELEMENT_CTRL" >/dev/null; then
  echo 'FAIL: v0.8.18 is still enqueued'
  exit 1
fi
if grep -F 'hangar18-ultimate-designer-history-preload-v0820' "$ELEMENT_CTRL" >/dev/null; then
  echo 'FAIL: v0.8.20 is still enqueued beside v0.8.21'
  exit 1
fi

# v0.8.21 is the single active history owner. It remains a real header asset and
# additionally preserves live form state across the exact clones made by the
# legacy history snapshot before refreshPageSectionType rehydrates each row.
require_contains "$ELEMENT_CTRL" 'hangar18-ultimate-designer-history-preload-v0821' 'v0.8.21 active history owner is missing'
require_contains "$ELEMENT_CTRL" 'ultimate-designer-history-preload-v0821.js' 'v0.8.21 history asset path is missing'
if grep -F "wp_add_inline_script('hangar18-manager-admin'" "$ELEMENT_CTRL" >/dev/null; then
  echo 'FAIL: active history owner is still coupled to the legacy admin handle'
  exit 1
fi
require_contains "$HISTORY_V0821" 'data-h18-v0821-history-runtime' 'v0.8.21 runtime marker is missing'
require_contains "$HISTORY_V0821" "callback.name === 'editorHistoryRecordNow'" 'v0.8.21 does not own core history scheduling'
require_contains "$HISTORY_V0821" 'milliseconds <= 120' 'v0.8.21 does not split structural checkpoints from input debounce'
require_contains "$HISTORY_V0821" 'runPendingHistory();' 'v0.8.21 does not flush pending input once before checkpoints/Undo'
require_contains "$HISTORY_V0821" 'scheduleSelectionClear' 'v0.8.21 does not clear stale historical Inspector selection'
require_contains "$HISTORY_V0821" 'copyFormControlState' 'v0.8.21 does not preserve live form values in snapshot clones'
require_contains "$HISTORY_V0821" 'jq.fn.clone = bridgedClone;' 'v0.8.21 clone bridge is not active'
require_contains "$HISTORY_V0821" "version: '0.8.21'" 'v0.8.21 runtime identity is missing'
require_contains "$HISTORY_V0821" "badge.textContent = 'H0.8.21'" 'v0.8.21 live runtime badge is missing'

# No second history stack or persistence/cutover path is introduced by extensions.
if grep -E 'editorHistoryEntries|editorHistoryIndex|const[[:space:]]+.*History.*\[|let[[:space:]]+.*History.*\[' "$BOX_CONTENT" "$HISTORY_V0817" "$HISTORY_V0818" "$HISTORY_V0820" "$HISTORY_V0821" "$ELEMENT_CTRL" >/dev/null; then
  echo 'FAIL: Undo extensions introduced a second editor history stack'
  exit 1
fi
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$NEST" "$CTRL" "$BOX_CONTENT" "$HISTORY_V0817" "$HISTORY_V0818" "$HISTORY_V0820" "$HISTORY_V0821" "$ELEMENT_CTRL" >/dev/null; then
  echo 'FAIL: Undo/Kasse hotfix introduced a public persistence/cutover primitive'
  exit 1
fi

node --check "$LAYOUT"
node --check "$NEST"
node --check "$BOX_CONTENT"
node --check "$HISTORY_V0817"
node --check "$HISTORY_V0818"
node --check "$HISTORY_V0820"
node --check "$HISTORY_V0821"
php -l "$CTRL" >/dev/null
php -l "$ELEMENT_CTRL" >/dev/null

echo 'v0.8.15-v0.8.21 Kasse/Undo single-active-history-owner contract: PASS'
