#!/usr/bin/env bash
set -euo pipefail

RUNTIME_0818='assets/ultimate-designer-history-v0818.js'
RUNTIME_0820='assets/ultimate-designer-history-preload-v0820.js'
RUNTIME_0821='assets/ultimate-designer-history-preload-v0821.js'
RUNTIME_0822='assets/ultimate-designer-history-post-restore-v0822.js'
CTRL='src/Admin/EditorElementLibraryAdminController.php'
MAIN='hangar18-manager.php'

for file in "$RUNTIME_0818" "$RUNTIME_0820" "$RUNTIME_0821" "$RUNTIME_0822" "$CTRL" "$MAIN"; do
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

# v0.8.18/v0.8.20 stay available for rollback archaeology, but are no longer active.
require_contains "$RUNTIME_0818" 'data-h18-v0818-history-runtime' 'v0.8.18 rollback runtime marker is missing'
require_contains "$RUNTIME_0820" 'data-h18-v0820-history-runtime' 'v0.8.20 rollback runtime marker is missing'
if grep -F "hangar18-ultimate-designer-history-v0818" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.18 is still enqueued beside the active history owner'
  exit 1
fi
if grep -F "hangar18-ultimate-designer-history-preload-v0820" "$CTRL" >/dev/null; then
  echo 'FAIL: v0.8.20 is still enqueued beside the active history owner'
  exit 1
fi

# IntegrationAdminBootstrap is registered before the legacy manager. The active
# history owner therefore remains a real header asset and never relies on inline
# code being attached to hangar18-manager-admin before that handle is queued.
require_contains "$MAIN" 'IntegrationAdminBootstrap::register();' 'Ultimate Designer bootstrap registration is missing'
require_contains "$MAIN" 'Hangar18_Manager::instance();' 'legacy manager bootstrap is missing'
if grep -F "wp_add_inline_script('hangar18-manager-admin'" "$CTRL" >/dev/null; then
  echo 'FAIL: history runtime is again attached inline to a handle that may not yet be queued'
  exit 1
fi

require_contains "$CTRL" "'hangar18-ultimate-designer-history-preload-v0821'" 'v0.8.21 history preloader is not enqueued'
require_contains "$CTRL" 'assets/ultimate-designer-history-preload-v0821.js' 'v0.8.21 history preloader path is missing'
require_contains "$CTRL" "['jquery']," 'v0.8.21 preloader does not declare jQuery dependency'
require_contains "$CTRL" 'assets/ultimate-designer-history-post-restore-v0822.js' 'v0.8.22 post-restore bridge path is missing'
require_contains "$CTRL" "'hangar18-ultimate-designer-history-post-restore-v0822'" 'v0.8.22 post-restore bridge is not enqueued/dependency-linked'
require_contains "$CTRL" "'hangar18-manager-admin'" 'element library no longer depends on base admin'
require_contains "$CTRL" "'hangar18-ultimate-designer-history-preload-v0821'" 'element library no longer depends on v0.8.21 owner'
require_contains "$CTRL" "'hangar18-ultimate-designer-history-post-restore-v0822'" 'element library no longer depends on v0.8.22 intent bridge'
require_contains "$MAIN" "'hangar18-manager-admin'" 'legacy base admin handle is missing'
require_contains "$MAIN" "plugin_dir_url(__FILE__) . 'assets/admin.js'" 'legacy assets/admin.js enqueue is missing'

require_contains "$RUNTIME_0821" 'data-h18-v0821-history-runtime' 'v0.8.21 runtime marker is missing'
require_contains "$RUNTIME_0821" "callback.name === 'editorHistoryRecordNow'" 'v0.8.21 does not own core history scheduling'
require_contains "$RUNTIME_0821" 'milliseconds <= 120' 'structural checkpoints still share typing debounce'
require_contains "$RUNTIME_0821" 'runPendingHistory();' 'pending input edit is not flushed before structural/Undo checkpoints'
require_contains "$RUNTIME_0821" 'scheduleSelectionClear' 'Undo/Redo does not clear historical Inspector selection'

# v0.8.21 regression: live form state must survive snapshot cloning.
require_contains "$RUNTIME_0821" 'function copyFormControlState(sourceRoot, cloneRoot)' 'form-state clone copier is missing'
require_contains "$RUNTIME_0821" "node.id === 'h18-page-sections-sortable'" 'section collection clone source is not scoped'
require_contains "$RUNTIME_0821" "node.classList.contains('h18-page-section-body')" 'Inspector body clone source is not scoped'
require_contains "$RUNTIME_0821" "source.tagName === 'SELECT'" 'select live state is not copied'
require_contains "$RUNTIME_0821" "source.tagName === 'TEXTAREA'" 'textarea live state is not copied'
require_contains "$RUNTIME_0821" "option.setAttribute('selected', 'selected')" 'selected option attributes are not materialized in snapshot clone'
require_contains "$RUNTIME_0821" 'jq.fn.clone = bridgedClone;' 'snapshot jQuery clone bridge is not active'

# v0.8.22 regression: after a complete Undo/Redo cycle, the first new structural
# user action must reopen history and become its own checkpoint immediately.
require_contains "$RUNTIME_0822" 'data-h18-v0822-post-restore-history' 'v0.8.22 runtime marker is missing'
require_contains "$RUNTIME_0822" 'function armStructuralCapture(event)' 'post-restore structural intent arm is missing'
require_contains "$RUNTIME_0822" ".h18-builder-palette-item" 'palette insertion is not recognized as structural intent'
require_contains "$RUNTIME_0822" 'forceNextStructuralCapture' 'post-restore structural checkpoint flag is missing'
require_contains "$RUNTIME_0822" "callback.name === 'editorHistoryRecordNow'" 'v0.8.22 does not identify core history capture'
require_contains "$RUNTIME_0822" 'milliseconds <= 120' 'v0.8.22 does not restrict bypass to structural capture timing'
require_contains "$RUNTIME_0822" "data-h18-history-runtime', '0.8.22'" 'v0.8.22 runtime identity marker is missing'
require_contains "$RUNTIME_0822" "badge.textContent = 'H0.8.22'" 'v0.8.22 visible diagnostic badge is missing'

if grep -Ei 'wp_update_post|wp_insert_post|update_post_meta|delete_post_meta|update_option|delete_option' "$CTRL" "$RUNTIME_0821" "$RUNTIME_0822" >/dev/null; then
  echo 'FAIL: history bridge introduced persistence primitives'
  exit 1
fi

node --check "$RUNTIME_0821"
node --check "$RUNTIME_0822"
php -l "$CTRL" >/dev/null

echo 'v0.8.21 owner + v0.8.22 post-Redo structural history bridge contract: PASS'
