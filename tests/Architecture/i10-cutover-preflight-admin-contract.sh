#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/CutoverPreflightAdminController.php'
repo='src/Infrastructure/WordPress/WordPressOptionCutoverPreflightRepository.php'
service='src/Migration/ConversionCutoverPreflightService.php'
token='src/Migration/ConversionCutoverPreflightTokenService.php'
bootstrap='src/Admin/IntegrationAdminBootstrap.php'

for file in "$controller" "$repo" "$service" "$token" "$bootstrap"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

grep -F "admin_post_h18_ud_create_cutover_preflight" "$controller" >/dev/null
grep -F "CutoverPreflightAdminController::register();" "$bootstrap" >/dev/null
grep -F "CutoverPreflightAdminController::renderPanel();" "$bootstrap" >/dev/null
grep -F "'Executable' => false" "$service" >/dev/null
grep -F "'PublicMutationAvailable' => false" "$service" >/dev/null
grep -F "'Executable' => false" "$repo" >/dev/null
grep -F "legacy-source-drift" src/Migration/ConversionSourceDriftService.php >/dev/null
grep -F "hash_hmac('sha256'" "$token" >/dev/null
grep -F 'hash_equals' "$token" >/dev/null
grep -F 'Cutover preflight token secret must be at least 32 characters.' "$token" >/dev/null

# Only a preflight creation handler may be registered in this controller.
if grep -E "admin_post_h18_ud_(activate|cutover|publish|switch|promote)" "$controller" >/dev/null; then
  echo 'FAIL: preflight controller exposes a public mutation handler'
  exit 1
fi
if grep -E 'wp_update_post|wp_insert_post|wp_delete_post|update_post_meta|delete_post_meta|wp_trash_post' "$controller" "$repo" "$service" "$token" >/dev/null; then
  echo 'FAIL: preflight slice contains WordPress post mutation primitive'
  exit 1
fi
if grep -F "update_option('hangar18_manager_pages_v1'" "$controller" "$repo" "$service" "$token" >/dev/null; then
  echo 'FAIL: preflight slice writes legacy page-store'
  exit 1
fi
if grep -E "add_action\('(wp|init|template_redirect|wp_head|wp_footer)'" "$controller" >/dev/null; then
  echo 'FAIL: preflight controller registers frontend/runtime hook'
  exit 1
fi

echo 'I10 cutover preflight admin safety contract v0.8.6: PASS'
