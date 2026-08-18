#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/PortabilityAdminController.php'
repo='src/Infrastructure/WordPress/WordPressOptionArtifactRepository.php'
tokens='src/Portability/ImportPlanTokenService.php'

for required in \
  "admin_post_h18_ud_export_page_package" \
  "admin_post_h18_ud_export_artifact_package" \
  "wp_ajax_h18_ud_preview_page_import" \
  "wp_ajax_h18_ud_plan_artifact_import" \
  "admin_post_h18_ud_confirm_artifact_import" \
  "admin_post_h18_ud_restore_portability_backup" \
  "check_admin_referer(self::NONCE_ACTION)" \
  "check_ajax_referer(self::PLAN_NONCE,'nonce')" \
  "current_user_can('edit_pages')" \
  "MAX_JSON=1048576" \
  "ImportPlanTokenService" \
  "tokens()->verify" \
  "confirm_import" \
  "WordPressOptionArtifactRepository" \
  "WriteAllowed'=>false"; do
  grep -F "$required" "$controller" >/dev/null || { echo "FAIL: missing I6 safety marker: $required"; exit 1; }
done

# I6 must not write imported pages or perform frontend cutover.
for forbidden in '->save($key' 'wp_update_post' 'wp_insert_post' 'update_post_meta' 'delete_post_meta' 'template_redirect' 'wp_head' 'wp_footer'; do
  if grep -F -- "$forbidden" "$controller" >/dev/null; then echo "FAIL: I6 controller contains forbidden page/frontend write primitive: $forbidden"; exit 1; fi
done

grep -F "OPTION='hangar18_ud_portable_artifacts_v1'" "$repo" >/dev/null
grep -F 'restoreSnapshot' "$repo" >/dev/null
grep -F 'transaction(callable' "$repo" >/dev/null
grep -F "hash_hmac('sha256'" "$tokens" >/dev/null
grep -F 'hash_equals' "$tokens" >/dev/null
grep -F 'expires' "$tokens" >/dev/null

grep -F 'Sidepakker er preview-only indtil I10' "$controller" >/dev/null
grep -F 'Portability Workspace' "$controller" >/dev/null

echo 'I6 Portability admin safety contract: PASS'
