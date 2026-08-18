#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/PermissionsAdminController.php'
installer='src/Infrastructure/WordPress/WordPressRoleInstaller.php'
planner='src/Permissions/RoleInstallationPlanner.php'

for required in \
  "admin_post_h18_ud_install_roles" \
  "admin_post_h18_ud_save_design_lock" \
  "current_user_can('manage_options')" \
  "check_admin_referer(self::NONCE_ACTION)" \
  "confirm_install" \
  "RoleInstallationPlanner" \
  "WordPressRoleInstaller" \
  "additive-only" \
  "edit_pages" \
  "Design Lock policy"; do
  grep -F "$required" "$controller" >/dev/null || { echo "FAIL: missing I7 marker: $required"; exit 1; }
done

for forbidden in 'remove_role' 'remove_cap' 'set_role(' 'add_role(' 'wp_delete_user' 'delete_option('; do
  if grep -F "$forbidden" "$controller" >/dev/null; then echo "FAIL: I7 controller contains lockout/destructive primitive: $forbidden"; exit 1; fi
done

if grep -E 'remove_role|remove_cap' "$installer" >/dev/null; then echo 'FAIL: role installer must remain additive-only'; exit 1; fi
grep -F "'Remove'=>[]" "$planner" >/dev/null
grep -F "'Removals'=>0" "$planner" >/dev/null
grep -F "OPTION='hangar18_ud_design_lock_v1'" src/Infrastructure/WordPress/WordPressOptionDesignLockRepository.php >/dev/null

echo 'I7 permissions/admin no-lockout contract: PASS'
