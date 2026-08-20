#!/usr/bin/env bash
set -euo pipefail

MANIFEST='src/Backup/SiteBackupManifestService.php'
VALIDATOR='src/Backup/SiteBackupManifestValidator.php'
COLLECT='src/Backup/SiteBackupSnapshotCollector.php'
PACKAGE='src/Backup/SiteBackupPackageService.php'
RESTORE='src/Backup/SiteBackupRestoreService.php'
COORD='src/Backup/SiteBackupRestoreCoordinator.php'
SECURITY='src/Backup/SiteBackupSecurityPolicy.php'
ADMIN='src/Admin/SiteBackupAdminController.php'
BOOT='src/Admin/IntegrationAdminBootstrap.php'

for file in "$MANIFEST" "$VALIDATOR" "$COLLECT" "$PACKAGE" "$RESTORE" "$COORD" "$SECURITY" "$ADMIN" "$BOOT"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

# Immutable versioned package + checksums + application-aware payloads.
grep -F "H18-BACKUP-(\\d{6})" "$MANIFEST" >/dev/null
grep -F "ManifestSha256" "$MANIFEST" >/dev/null
grep -F "'managed-site'" "$COLLECT" >/dev/null
grep -F "'page-versions'" "$COLLECT" >/dev/null
grep -F "'site-builder'" "$COLLECT" >/dev/null
grep -F "'forms-polls-data'" "$COLLECT" >/dev/null
grep -F "'plugin-metadata'" "$COLLECT" >/dev/null
grep -F "hash_file('sha256'" "$COLLECT" >/dev/null

# Package is staged, self-validated, then atomically installed.
grep -F ".building-" "$PACKAGE" >/dev/null
grep -F "validateDirectory(\$building)" "$PACKAGE" >/dev/null
grep -F "rename(\$building, \$final)" "$PACKAGE" >/dev/null
grep -F "ZipArchive" "$PACKAGE" >/dev/null
grep -F "safeRelativePath" "$PACKAGE" >/dev/null

# Restore plan is signed/state-bound and core safety backup precedes mutation.
grep -F "CurrentStateHash" "$RESTORE" >/dev/null
grep -F "hash_hmac('sha256'" "$RESTORE" >/dev/null
grep -F "B2 sikkerhedsbackup før" "$RESTORE" >/dev/null
safety_line="$(grep -n "B2 sikkerhedsbackup før" "$RESTORE" | head -1 | cut -d: -f1)"
media_line="$(grep -n '\$this->restoreMedia' "$RESTORE" | head -1 | cut -d: -f1)"
test -n "$safety_line" && test -n "$media_line" && test "$safety_line" -lt "$media_line" || { echo 'FAIL: B2 safety backup is not before first restore mutation'; exit 1; }
grep -F "restoreSelectivePageEditor" "$RESTORE" >/dev/null
grep -F "restoreSelectivePageVersions" "$RESTORE" >/dev/null

# Coordinator adds security preflight, stale lock recovery and failure audit.
grep -F "SiteBackupSecurityPolicy::assertManifestSafe" "$COORD" >/dev/null
grep -F "STALE_LOCK_SECONDS" "$COORD" >/dev/null
grep -F "SafetyBackupId" "$COORD" >/dev/null
grep -F -- "-failed" "$COORD" >/dev/null

# Imported packages are bounded before extraction/restore.
grep -F "MAX_ZIP_BYTES" "$SECURITY" >/dev/null
grep -F "MAX_UNPACKED_BYTES" "$SECURITY" >/dev/null
grep -F "MAX_ZIP_ENTRIES" "$SECURITY" >/dev/null
grep -F "BLOCKED_EXTENSIONS" "$SECURITY" >/dev/null
grep -F ".htaccess" "$SECURITY" >/dev/null
grep -F "web.config" "$SECURITY" >/dev/null
inspect_line="$(grep -n 'SiteBackupSecurityPolicy::inspectZip' "$ADMIN" | head -1 | cut -d: -f1)"
import_line="$(grep -n 'importZip(\$tmp' "$ADMIN" | head -1 | cut -d: -f1)"
test -n "$inspect_line" && test -n "$import_line" && test "$inspect_line" -lt "$import_line" || { echo 'FAIL: ZIP security preflight is not before extraction/import'; exit 1; }

# Destructive B2 operations are admin-only, nonce gated and explicit.
grep -F "current_user_can('manage_options')" "$ADMIN" >/dev/null
grep -F "check_admin_referer(self::NONCE)" "$ADMIN" >/dev/null
grep -F "GENDAN HANGAR18" "$ADMIN" >/dev/null
grep -F "admin_post_h18_ud_b2_execute_restore" "$ADMIN" >/dev/null
grep -F "SiteBackupAdminController::register();" "$BOOT" >/dev/null
grep -F "SiteBackupAdminController::renderPanel();" "$BOOT" >/dev/null

# Standard B2 must remain application-aware, never raw whole-WordPress DR.
if grep -Ei 'mysqldump|mysql .*<|DROP TABLE|TRUNCATE TABLE|switch_theme\s*\(|activate_plugin\s*\(|deactivate_plugins\s*\(|wp-admin/includes/plugin\.php' "$MANIFEST" "$VALIDATOR" "$COLLECT" "$PACKAGE" "$RESTORE" "$COORD" "$ADMIN" >/dev/null; then
  echo 'FAIL: standard B2 introduced raw DB/plugin/theme disaster-recovery behavior'
  exit 1
fi

# No public mutation hooks from B2 admin/backup services.
if grep -Ei 'wp_ajax_nopriv_|template_redirect|wp_head|wp_footer|wp_nav_menu|wp_update_nav_menu|wp_create_nav_menu' "$PACKAGE" "$RESTORE" "$COORD" "$ADMIN" >/dev/null; then
  echo 'FAIL: B2 introduced public mutation path'
  exit 1
fi

echo 'B2 versioned package/full+selective restore security contract: PASS'
