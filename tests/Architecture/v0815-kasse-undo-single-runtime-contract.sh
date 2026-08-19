#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/EditorLayoutToolsAdminController.php'
LAYOUT='assets/ultimate-designer-layout-tools.js'
NEST='assets/ultimate-designer-nesting-tools.js'

for file in "$CTRL" "$LAYOUT" "$NEST"; do
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
require_contains "$NEST" "data-h18-v0815-kasse-runtime" 'v0.8.15 runtime marker is missing'

# Hidden source rows may not become visually orphaned if the base editor rebuilds a canvas preview.
require_contains "$NEST" 'function compositionMissing()' 'composition loss detector is missing'
require_contains "$NEST" 'observer.observe($sections.get(0), { childList: true, subtree: true });' 'composition observer does not watch preview rebuilds'
require_contains "$NEST" "!$preview.children('.h18-ud-auto-box-grid').length" 'Auto-kasser missing-composition detection is absent'
require_contains "$NEST" "!$preview.children('.h18-ud-box-contents-preview').length" 'Kasse missing-composition detection is absent'

# Restore-derived history callbacks are discarded. They must never be delayed until suppression expires.
require_contains "$CTRL" "callback.name === 'editorHistoryRecordNow'" 'history capture callback guard is missing'
require_contains "$CTRL" 'return NativeSetTimeout(function () {}, 0);' 'suppressed history capture is not discarded'
if grep -F 'guard.remaining() + 30' "$CTRL" >/dev/null; then
  echo 'FAIL: restore-derived history capture is still delayed and replayed later'
  exit 1
fi
require_contains "$CTRL" "meta.target.id === 'h18-page-editor-form'" 'MutationObserver history suppression is not scoped to the page editor'
require_contains "$CTRL" '#h18-editor-undo,#h18-editor-redo' 'Undo/Redo does not start the restore transaction'

# No public persistence/cutover primitives are introduced by this editor hotfix.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$NEST" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.15 introduced a public persistence/cutover primitive'
  exit 1
fi

node --check "$LAYOUT"
node --check "$NEST"
php -l "$CTRL" >/dev/null

echo 'v0.8.15 Kasse/Undo single-runtime contract: PASS'
