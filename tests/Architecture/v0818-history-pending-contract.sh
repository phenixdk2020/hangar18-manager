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

# v0.8.18 stays available for rollback archaeology, but it is no longer active.
require_contains "$RUNTIME" 'data-h18-v0818-history-runtime' 'v0.8.18 rollback runtime marker is missing'
require_contains "$RUNTIME" "callback.name === 'editorHistoryRecordNow'" 'v0.8.18 rollback scheduler is incomplete'
require_contains "$RUNTIME" 'runPendingHistory();' 'v0.8.18 rollback pending flush is missing'
require_contains "$CTRL" 'v0.8.18 remains in the package solely as rollback archaeology' 'v0.8.18 retirement is not documented'

if grep -F "hangar18-ultimate-designer-history-v0818" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.18 is still enqueued beside the v0.8.19 preloaded owner'
  exit 1
fi

# v0.8.19 is injected before the legacy admin runtime and owns all later core
# editorHistoryRecordNow scheduling.
require_contains "$CTRL" 'enqueueEditorHistoryCoreBridgeV0819' 'v0.8.19 preloaded history bridge is missing'
require_contains "$CTRL" "wp_add_inline_script('hangar18-manager-admin', \$js, 'before');" 'v0.8.19 does not execute before assets/admin.js'
require_contains "$CTRL" 'data-h18-v0819-history-runtime' 'v0.8.19 runtime marker is missing'
require_contains "$CTRL" "callback.name === 'editorHistoryRecordNow'" 'v0.8.19 does not own core history scheduling'
require_contains "$CTRL" 'milliseconds <= 120' 'structural history checkpoints are still left in the input debounce queue'
require_contains "$CTRL" 'runPendingHistory();' 'pending input edit is not flushed before structural/Undo checkpoints'
require_contains "$CTRL" 'callback.apply(window, args);' 'structural checkpoint is not committed immediately'
require_contains "$CTRL" 'return 0;' 'legacy editorHistoryTimer can still receive a stale native timer id'
require_contains "$CTRL" 'scheduleSelectionClear' 'Undo/Redo does not clear historical Inspector selection'
require_contains "$CTRL" "data-h18-history-runtime', '0.8.19'" 'runtime identity marker is missing'

if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option' "$CTRL" >/dev/null; then
  echo 'FAIL: history bridge introduced persistence primitives'
  exit 1
fi

python3 - <<'PY' > /tmp/h18-v0819-history.js
from pathlib import Path
import re
s=Path('src/Admin/EditorElementLibraryAdminController.php').read_text()
m=re.search(r"private static function enqueueEditorHistoryCoreBridgeV0819\(\): void[\s\S]*?\$js = <<<'JS'\n([\s\S]*?)\nJS;", s)
if not m: raise SystemExit(1)
print(m.group(1))
PY
node --check /tmp/h18-v0819-history.js
php -l "$CTRL" >/dev/null

echo 'v0.8.18 rollback / v0.8.19 preloaded-history successor contract: PASS'
