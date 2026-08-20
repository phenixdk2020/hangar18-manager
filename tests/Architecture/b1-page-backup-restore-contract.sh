#!/usr/bin/env bash
set -euo pipefail

SERVICE='src/Backup/ManagedPageBackupRestoreService.php'
CTRL='src/Admin/BackupRestoreAdminController.php'
BOOT='src/Admin/IntegrationAdminBootstrap.php'

for file in "$SERVICE" "$CTRL" "$BOOT"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Existing managed backup format/directory only.
grep -F "Hangar18-Web-(?:Full-Backup|Backup)" "$SERVICE" >/dev/null
grep -F "hangar18-manager-backups" "$SERVICE" >/dev/null
grep -F "realpath(" "$SERVICE" >/dev/null
grep -F "strpos(\$realPath, \$prefix) !== 0" "$SERVICE" >/dev/null

# Replace-original must create safety backup before wp_update_post.
safety_line="$(grep -n 'createSafetyBackup(\$target' "$SERVICE" | head -1 | cut -d: -f1)"
write_line="$(grep -n 'wp_update_post(\[' "$SERVICE" | head -1 | cut -d: -f1)"
test -n "$safety_line" && test -n "$write_line" && test "$safety_line" -lt "$write_line" || { echo 'FAIL: safety backup is not before first replace write'; exit 1; }

grep -F "'Mode' => 'replace-original'" "$SERVICE" >/dev/null
grep -F "'SafetyBackup' => basename(\$safetyFile)" "$SERVICE" >/dev/null

# Copy is collision-safe, draft-only and uses a separate slug/store key.
grep -F "sanitize_title(\$sourceSlug . '-kopi')" "$SERVICE" >/dev/null
grep -F "'post_status' => 'draft'" "$SERVICE" >/dev/null
grep -F "writeEditorStoreEntry(\$copySlug" "$SERVICE" >/dev/null
grep -F "wp_delete_post(\$newId, true)" "$SERVICE" >/dev/null

# Restore preserves original URL identity by omitting post_name in wp_update payload.
replace_block="$(sed -n '/\$result = wp_update_post(\[/,/\], true);/p' "$SERVICE" | head -40)"
if printf '%s\n' "$replace_block" | grep -F "'post_name'" >/dev/null; then
  echo 'FAIL: replace-original attempts to rename original slug'
  exit 1
fi

# Explicit authenticated/capability-gated admin mutation only.
grep -F "current_user_can('edit_pages')" "$CTRL" >/dev/null
grep -F "check_admin_referer('h18_ud_backup_restore')" "$CTRL" >/dev/null
grep -F "admin_post_h18_ud_restore_backup_original" "$CTRL" >/dev/null
grep -F "admin_post_h18_ud_restore_backup_copy" "$CTRL" >/dev/null
grep -F "BackupRestoreAdminController::register();" "$BOOT" >/dev/null
grep -F "BackupRestoreAdminController::renderPanel();" "$BOOT" >/dev/null

# No automatic execution / public hook / menu mutation in B1 code.
if grep -Ei "wp_ajax_nopriv_|template_redirect|wp_head|wp_footer|wp_nav_menu|wp_update_nav_menu|wp_create_nav_menu|set_theme_mod|switch_theme" "$SERVICE" "$CTRL" >/dev/null; then
  echo 'FAIL: B1 introduced public or menu mutation path'
  exit 1
fi

echo 'B1 page backup restore security/behavior contract: PASS'
