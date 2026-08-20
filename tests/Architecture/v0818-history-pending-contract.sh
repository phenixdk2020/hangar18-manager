#!/usr/bin/env bash
set -euo pipefail

RUNTIME_0818='assets/ultimate-designer-history-v0818.js'
RUNTIME_0820='assets/ultimate-designer-history-preload-v0820.js'
CTRL='src/Admin/EditorElementLibraryAdminController.php'
MAIN='hangar18-manager.php'

for file in "$RUNTIME_0818" "$RUNTIME_0820" "$CTRL" "$MAIN"; do
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
require_contains "$RUNTIME_0818" 'data-h18-v0818-history-runtime' 'v0.8.18 rollback runtime marker is missing'
require_contains "$RUNTIME_0818" "callback.name === 'editorHistoryRecordNow'" 'v0.8.18 rollback scheduler is incomplete'
require_contains "$RUNTIME_0818" 'runPendingHistory();' 'v0.8.18 rollback pending flush is missing'

if grep -F "hangar18-ultimate-designer-history-v0818" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.18 is still enqueued beside the active history owner'
  exit 1
fi

# Regression behind v0.8.20: IntegrationAdminBootstrap is registered before the
# legacy Hangar18_Manager instance, while hangar18-manager-admin is enqueued by
# the latter. An inline script attached to that handle from the earlier hook can
# therefore be discarded by WordPress. The successor must NOT rely on that handle.
require_contains "$MAIN" 'IntegrationAdminBootstrap::register();' 'Ultimate Designer bootstrap registration is missing'
require_contains "$MAIN" 'Hangar18_Manager::instance();' 'legacy manager bootstrap is missing'
if grep -F "wp_add_inline_script('hangar18-manager-admin'" "$CTRL" >/dev/null; then
  echo 'FAIL: history runtime is again attached inline to a handle that may not yet be queued'
  exit 1
fi

# v0.8.20 is a real header asset. assets/admin.js is explicitly a footer asset in
# the legacy manager, so the history owner necessarily executes first regardless
# of admin_enqueue_scripts callback registration order.
require_contains "$CTRL" "'hangar18-ultimate-designer-history-preload-v0820'" 'v0.8.20 history preloader is not enqueued'
require_contains "$CTRL" "assets/ultimate-designer-history-preload-v0820.js" 'v0.8.20 history preloader path is missing'
require_contains "$CTRL" "['jquery']," 'v0.8.20 preloader does not declare jQuery dependency'
require_contains "$CTRL" "false" 'v0.8.20 preloader is not configured as a header asset'
require_contains "$CTRL" "'hangar18-manager-admin', 'hangar18-ultimate-designer-history-preload-v0820'" 'element library does not depend on both base admin and history preloader'
require_contains "$MAIN" "'hangar18-manager-admin'" 'legacy base admin handle is missing'
require_contains "$MAIN" "plugin_dir_url(__FILE__) . 'assets/admin.js'" 'legacy assets/admin.js enqueue is missing'

require_contains "$RUNTIME_0820" 'data-h18-v0820-history-runtime' 'v0.8.20 runtime marker is missing'
require_contains "$RUNTIME_0820" "callback.name === 'editorHistoryRecordNow'" 'v0.8.20 does not own core history scheduling'
require_contains "$RUNTIME_0820" 'milliseconds <= 120' 'structural checkpoints still share typing debounce'
require_contains "$RUNTIME_0820" 'runPendingHistory();' 'pending input edit is not flushed before structural/Undo checkpoints'
require_contains "$RUNTIME_0820" 'callback.apply(window, args);' 'structural checkpoint is not committed immediately'
require_contains "$RUNTIME_0820" 'return 0;' 'legacy editorHistoryTimer can still receive a stale native timer id'
require_contains "$RUNTIME_0820" 'scheduleSelectionClear' 'Undo/Redo does not clear historical Inspector selection'
require_contains "$RUNTIME_0820" "data-h18-history-runtime', '0.8.20'" 'runtime identity marker is missing'
require_contains "$RUNTIME_0820" "badge.textContent = 'H0.8.20'" 'visible live-runtime diagnostic badge is missing'

if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option' "$CTRL" "$RUNTIME_0820" >/dev/null; then
  echo 'FAIL: history bridge introduced persistence primitives'
  exit 1
fi

node --check "$RUNTIME_0820"
php -l "$CTRL" >/dev/null

echo 'v0.8.18 rollback / v0.8.20 header-preloader successor contract: PASS'
