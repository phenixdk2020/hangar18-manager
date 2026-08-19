#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/EditorLayoutToolsAdminController.php'
NEST='assets/ultimate-designer-nesting-tools.js'

for file in "$CTRL" "$NEST"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# v0.8.13: exactly one live Kasse placement runtime.
grep -F 'enqueueEditorHistoryGuardV0813' "$CTRL" >/dev/null
grep -F 'enqueueKasseDragAuthorityV0813' "$CTRL" >/dev/null
if grep -F 'self::enqueueV0810KasseRuntime();' "$CTRL" >/dev/null; then
  echo 'FAIL: obsolete v0.8.10 Kasse runtime is still enqueued'
  exit 1
fi
if grep -F "'hangar18-ultimate-designer-visual-composition'" "$CTRL" >/dev/null; then
  echo 'FAIL: obsolete visual-composition runtime is live'
  exit 1
fi

grep -F 'data-h18-v0813-kasse-authority' "$CTRL" >/dev/null
grep -F "removeAttribute('data-h18-layout-tool')" "$CTRL" >/dev/null
grep -F "setTimeout(function () { item.setAttribute('data-h18-layout-tool', 'box'); }, 0);" "$CTRL" >/dev/null

# Undo/redo guard suppresses only the editor-history observer during restore settling.
grep -F '__h18HistoryObserverGuardV0813' "$CTRL" >/dev/null
grep -F "meta.target.id === 'h18-page-editor-form'" "$CTRL" >/dev/null
grep -F '#h18-editor-undo,#h18-editor-redo' "$CTRL" >/dev/null
grep -F 'suppress(180)' "$CTRL" >/dev/null

# Kasse in Kasse is allowed subject to cycle/depth guard; side placement alone creates Auto-kasser.
grep -F 'function canMoveIntoBox($row, $box)' "$NEST" >/dev/null
if grep -F '!isBox($box) || isBox($row)' "$NEST" >/dev/null; then
  echo 'FAIL: Kasse source is still categorically rejected as a child'
  exit 1
fi
grep -F 'function subtreeDepth($row)' "$NEST" >/dev/null
grep -F 'function parentDepth($row)' "$NEST" >/dev/null
grep -F 'function finishNewBoxInside(beforeKeys, targetKey)' "$NEST" >/dev/null
grep -F "mode: 'inside'" "$NEST" >/dev/null
grep -F "mode: 'side'" "$NEST" >/dev/null
grep -F 'createAutoForBoxes($source, $target, side)' "$NEST" >/dev/null
grep -F 'placeBoxBeside($source, $target, side)' "$NEST" >/dev/null

# One palette drop is consumed once. A dragend after a handled drop may not create another element.
grep -F 'dropHandled: false' "$NEST" >/dev/null
grep -F 'state.dropHandled = true' "$NEST" >/dev/null
grep -F 'if (!state.dropHandled)' "$NEST" >/dev/null

# Nested Kasse previews retain their own visible contents/dropzone.
grep -F 'clonePreview($child, isBox($child))' "$NEST" >/dev/null

# No public persistence/cutover primitives.
if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option|admin_post_.*(activate|cutover|publish)' "$NEST" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.13 introduced public persistence/cutover primitive'
  exit 1
fi

node --check "$NEST"
php -l "$CTRL" >/dev/null

echo 'v0.8.13 Kasse authority/history contract: PASS'
