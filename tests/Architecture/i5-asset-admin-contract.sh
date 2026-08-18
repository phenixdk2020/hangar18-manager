#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/AssetManagerAdminController.php'
service='src/Assets/ImageOptimizationService.php'
planner='src/Assets/ImageOptimizationPlanner.php'

for required in \
  "add_action('admin_post_h18_ud_save_asset_metadata'" \
  "add_action('admin_post_h18_ud_generate_asset_derivatives'" \
  "add_action('wp_ajax_h18_ud_asset_duplicates'" \
  "check_admin_referer(self::NONCE_ACTION)" \
  "check_ajax_referer('h18_ud_asset_duplicates_v1','nonce')" \
  "current_user_can('edit_pages')" \
  "new DuplicateAssetDetector()" \
  "new ImageOptimizationService(new WordPressImageOptimizer())" \
  "Originalen bevares altid"; do
  grep -F "$required" "$controller" >/dev/null || { echo "FAIL: missing I5 safety marker: $required"; exit 1; }
done

for forbidden in 'wp_delete_attachment' 'wp_delete_post' 'update_attached_file' 'wp_handle_sideload' 'media_handle_sideload' 'unlink(' 'rename(' 'copy('; do
  if grep -F "$forbidden" "$controller" >/dev/null; then echo "FAIL: destructive/native asset primitive present in I5 controller: $forbidden"; exit 1; fi
done

grep -F "file_exists(\$targetPath)" "$service" >/dev/null
grep -F "target-exists" "$service" >/dev/null
grep -F "'.h18.webp'" "$planner" >/dev/null
grep -F "'.h18.avif'" "$planner" >/dev/null

grep -F 'MediaId' src/Assets/AssetMetadataValidator.php >/dev/null
grep -F "OPTION = 'hangar18_ud_asset_metadata_v1'" src/Infrastructure/WordPress/WordPressOptionAssetMetadataRepository.php >/dev/null

echo 'I5 Asset Manager safety contract: PASS'
