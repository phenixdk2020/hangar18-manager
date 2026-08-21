#!/usr/bin/env bash
set -euo pipefail

service="src/Backup/ManagedPageTrashService.php"
controller="src/Admin/BackupRestoreAdminController.php"
asset="assets/ultimate-designer-page-delete-v0844.js"

for file in "$service" "$controller" "$asset"; do
  [[ -f "$file" ]] || { echo "Missing $file"; exit 1; }
done

# Mutation semantics: WordPress Trash only, no permanent delete in PAGE-DELETE implementation.
grep -q "wp_trash_post" "$service"
if grep -Eq "wp_delete_post|DELETE FROM|\$wpdb->delete" "$service" "$controller" "$asset"; then
  echo "PAGE-DELETE-001 contract FAILED: permanent/raw delete primitive found."
  exit 1
fi

# Safety backup and audit binding.
grep -q "PAGE-DELETE-001 sikkerhedsbackup" "$service"
grep -q "PAGE_EDITOR_OPTION" "$service"
grep -q "SafetyBackup" "$service"
grep -q "PageId" "$service"
grep -q "Title" "$service"
grep -q "UserId" "$service"
grep -q "Utc" "$service"

# Protected domain guard is both UI and server side.
for slug in hjem koeretoejer-og-materiel events billedgalleri; do
  grep -q "'$slug'" "$service"
  grep -q "'$slug'" "$asset"
done

# Server authorization: coarse page delete + object-specific delete + nonce.
grep -q "current_user_can('delete_pages')" "$controller"
grep -q "current_user_can('delete_post'" "$controller"
grep -q "check_admin_referer('h18_ud_trash_page')" "$controller"

# Exact-title confirmation and explicit cancellation paths in UI.
grep -q "window.prompt" "$asset"
grep -q "confirmed === null" "$asset"
grep -q "confirmed.trim() !== title" "$asset"
grep -q "window.confirm" "$asset"
grep -q "Slet side" "$asset"

# Restore promise must remain B1, not a new competing restore stack.
grep -q "ManagedPageBackupRestoreService" "$controller"
if grep -Eq "restorePage|untrash|wp_untrash_post" "$service"; then
  echo "PAGE-DELETE-001 contract FAILED: competing restore path introduced."
  exit 1
fi

echo "PAGE-DELETE-001 safety contract: PASS"
