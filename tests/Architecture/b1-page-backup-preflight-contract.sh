#!/usr/bin/env bash
set -euo pipefail

PREFLIGHT='src/Backup/ManagedPageBackupRestorePreflightService.php'
CTRL='src/Admin/BackupRestoreAdminController.php'

test -f "$PREFLIGHT" || { echo "FAIL: missing $PREFLIGHT"; exit 1; }
test -f "$CTRL" || { echo "FAIL: missing $CTRL"; exit 1; }

grep -F "HANGAR18-PAGE-EDITOR-DATA" "$PREFLIGHT" >/dev/null
grep -F "[hangar18_page_editor" "$PREFLIGHT" >/dev/null
grep -F "'embedded-marker-only'" "$PREFLIGHT" >/dev/null
grep -F "'HasPageEditorStoreEntry'" "$PREFLIGHT" >/dev/null
grep -F "analyzeReplace(\$filename, \$sourceKey)" "$CTRL" >/dev/null
grep -F "if (empty(\$check['Allowed']))" "$CTRL" >/dev/null
grep -F "Erstat original · låst" "$CTRL" >/dev/null

# analyzeReplace must execute before replacement service mutation in the handler.
preflight_line="$(grep -n 'analyzeReplace(\$filename, \$sourceKey)' "$CTRL" | tail -1 | cut -d: -f1)"
restore_line="$(grep -n 'restoreOriginal(\$filename, \$sourceKey)' "$CTRL" | head -1 | cut -d: -f1)"
test -n "$preflight_line" && test -n "$restore_line" && test "$preflight_line" -lt "$restore_line" || { echo 'FAIL: replace mutation is not gated by preflight'; exit 1; }

if grep -Ei 'wp_update_post|wp_insert_post|update_option|update_post_meta|delete_post_meta|admin_post_|wp_ajax_|template_redirect|wp_head|wp_footer' "$PREFLIGHT" >/dev/null; then
  echo 'FAIL: B1 preflight must remain read-only'
  exit 1
fi

echo 'B1 legacy editor restore preflight contract: PASS'
