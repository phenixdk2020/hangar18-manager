#!/usr/bin/env bash
set -euo pipefail

RUNTIME='assets/ultimate-designer-history-v0818.js'
CTRL='src/Admin/EditorElementLibraryAdminController.php'

for file in "$RUNTIME" "$CTRL"; do
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

require_contains "$RUNTIME" 'data-h18-v0818-history-runtime' 'v0.8.18 runtime marker is missing'
require_contains "$RUNTIME" "callback.name === 'editorHistoryRecordNow'" 'core history callback ownership is missing'
require_contains "$RUNTIME" 'state.pending = null;' 'owned pending history timer is not cleared after execution'
require_contains "$RUNTIME" 'return 0;' 'core editorHistoryTimer is not forced to a non-stale handle'
require_contains "$RUNTIME" 'runPendingHistory();' 'real pending edit is not flushed before Undo/Redo'
require_contains "$RUNTIME" 'if (state.restoreLatched)' 'restore-derived history capture is not suppressed'
require_contains "$RUNTIME" 'clearEditorSelection();' 'selection is not cleared when the selected element disappears'
require_contains "$RUNTIME" 'Selection is UI' 'selection/history separation is not documented in runtime'
require_contains "$CTRL" 'ultimate-designer-history-v0818.js' 'v0.8.18 history runtime is not enqueued'
require_contains "$CTRL" "'0.8.18'" 'v0.8.18 fallback asset version is missing'

if grep -F "assets/ultimate-designer-history-v0817.js'" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.17 history runtime is still enqueued alongside v0.8.18'
  exit 1
fi

if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option' "$RUNTIME" >/dev/null; then
  echo 'FAIL: history hotfix introduced persistence primitives'
  exit 1
fi

node --check "$RUNTIME"
php -l "$CTRL" >/dev/null

echo 'v0.8.18 pending-history/selection contract: PASS'
