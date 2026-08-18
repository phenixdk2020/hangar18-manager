#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/ConversionAdminController.php'
plan='src/Migration/ConversionPlanService.php'
gate='src/Migration/ConversionReadinessGate.php'
workspace='src/Infrastructure/WordPress/WordPressOptionConversionWorkspaceRepository.php'
acceptance_repo='src/Infrastructure/WordPress/WordPressOptionConversionAcceptanceRepository.php'
acceptance_validator='src/Migration/ConversionAcceptanceValidator.php'
checklist='src/Migration/ConversionAcceptanceChecklist.php'

grep -F "add_action('admin_post_h18_ud_create_conversion_shadow'" "$controller" >/dev/null
grep -F "add_action('admin_post_h18_ud_save_conversion_acceptance'" "$controller" >/dev/null
grep -F "current_user_can('manage_options')" "$controller" >/dev/null
grep -F 'check_admin_referer(self::NONCE_ACTION)' "$controller" >/dev/null
grep -F "get_option('hangar18_manager_pages_v1',[])" "$controller" >/dev/null
grep -F "'PublicMutationAvailable'=>false" "$plan" >/dev/null
grep -F "'PublicActivation'=>false" "$workspace" >/dev/null
grep -F "public const OPTION = 'hangar18_ud_conversion_acceptance_v1';" "$acceptance_repo" >/dev/null
grep -F "'AcceptedForSequence' => \$accepted" "$acceptance_validator" >/dev/null
grep -F 'hash_equals($currentHash,$postedHash)' "$controller" >/dev/null
grep -F "'rollback-flow' => 'Rollback flow verified'" "$checklist" >/dev/null
grep -F 'CompatibilityPolicy::mustUseLegacyRuntime' "$gate" >/dev/null
grep -F "'protected-legacy-runtime-policy:'" "$gate" >/dev/null
grep -F 'Public cutover findes ikke i denne version.' "$controller" >/dev/null

# Planner + acceptance ledger still expose no activation/cutover action.
if grep -Ei "add_action\('admin_post_[^']*(activate|cutover|publish|switch)|name=\\?\"action\\?\" value=\\?\"[^\"]*(activate|cutover|publish|switch)" "$controller" >/dev/null; then
  echo 'FAIL: I10 exposes an activation/cutover handler.'; exit 1
fi

# Legacy page-store and WordPress posts stay read-only. Acceptance may only write its dedicated option.
if grep -E "update_option\(['\"]hangar18_manager_pages_v1|delete_option\(['\"]hangar18_manager_pages_v1|wp_update_post|wp_insert_post|wp_delete_post|update_post_meta|delete_post_meta" "$controller" "$workspace" "$plan" "$gate" "$acceptance_repo" "$acceptance_validator" >/dev/null; then
  echo 'FAIL: I10 contains a public/legacy page mutation primitive.'; exit 1
fi

# A rebuilt shadow must invalidate evidence by exact SourceHash; accepted state is derived, not trusted from POST.
grep -F 'hash_equals((string) ($record['"'"'SourceHash'"'"'] ?? '"'"''"'"'), $currentSourceHash)' "$acceptance_validator" >/dev/null
if grep -F "\$_POST['AcceptedForSequence']" "$controller" "$acceptance_validator" >/dev/null; then
  echo 'FAIL: acceptance state can be supplied directly by the request.'; exit 1
fi

# Protected domain policy must not be weakened in this slice.
grep -F "public const PROTECTED_DOMAINS = ['vehicle', 'event', 'gallery'];" src/Compatibility/CompatibilityPolicy.php >/dev/null
grep -F 'return self::isProtectedDomain($domain);' src/Compatibility/CompatibilityPolicy.php >/dev/null

echo 'I10 acceptance ledger safety contract (manual/hash-bound, shadow only, no cutover): PASS'
