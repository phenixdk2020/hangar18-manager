#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/ConversionAdminController.php'
plan='src/Migration/ConversionPlanService.php'
gate='src/Migration/ConversionReadinessGate.php'
workspace='src/Infrastructure/WordPress/WordPressOptionConversionWorkspaceRepository.php'

grep -F "add_action('admin_post_h18_ud_create_conversion_shadow'" "$controller" >/dev/null
grep -F "current_user_can('manage_options')" "$controller" >/dev/null
grep -F 'check_admin_referer(self::NONCE_ACTION)' "$controller" >/dev/null
grep -F "get_option('hangar18_manager_pages_v1',[])" "$controller" >/dev/null
grep -F "'PublicMutationAvailable'=>false" "$plan" >/dev/null
grep -F "'PublicActivation'=>false" "$workspace" >/dev/null
grep -F 'CompatibilityPolicy::mustUseLegacyRuntime' "$gate" >/dev/null
grep -F "'protected-legacy-runtime-policy:'" "$gate" >/dev/null
grep -F 'Public cutover findes ikke i denne version.' "$controller" >/dev/null

# I10 v0.8.3 is planner-only. No activation/cutover handler or action value may exist.
if grep -Ei "add_action\('admin_post_[^']*(activate|cutover|publish|switch)|name=\\?\"action\\?\" value=\\?\"[^\"]*(activate|cutover|publish|switch)" "$controller" >/dev/null; then
  echo 'FAIL: I10 planner exposes an activation/cutover handler.'; exit 1
fi

# Legacy page-store and WordPress posts are read-only in planner phase.
if grep -E "update_option\(['\"]hangar18_manager_pages_v1|delete_option\(['\"]hangar18_manager_pages_v1|wp_update_post|wp_insert_post|wp_delete_post|update_post_meta|delete_post_meta" "$controller" "$workspace" "$plan" "$gate" >/dev/null; then
  echo 'FAIL: I10 planner contains a public/legacy page mutation primitive.'; exit 1
fi

# Protected domain policy must not be weakened in this slice.
grep -F "public const PROTECTED_DOMAINS = ['vehicle', 'event', 'gallery'];" src/Compatibility/CompatibilityPolicy.php >/dev/null
grep -F 'return self::isProtectedDomain($domain);' src/Compatibility/CompatibilityPolicy.php >/dev/null

echo 'I10 conversion planner safety contract (shadow only, no cutover, protected legacy): PASS'
