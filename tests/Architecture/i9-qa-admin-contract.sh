#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/QaDashboardAdminController.php'
validator='src/QA/ManualEvidenceValidator.php'
preflight='src/QA/RollbackPreflightService.php'

grep -F "current_user_can('manage_options')" "$controller" >/dev/null
grep -F 'check_admin_referer(self::NONCE_ACTION)' "$controller" >/dev/null
grep -F "get_option('hangar18_manager_pages_v1',[])" "$controller" >/dev/null
grep -F "SatisfiesManualLiveCopyGate'=>false" "$preflight" >/dev/null
grep -F "!\$confirmed||\$environment===''||\$evidenceRef===''" "$validator" >/dev/null
grep -F "'migration-rollback-live-copy'=>false" src/QA/ReleaseReadiness.php >/dev/null
grep -F 'Automated preflight never marks a manual gate as passed.' "$controller" >/dev/null

# The QA layer may read the legacy page option for a copy-only preflight, but must never write it.
if grep -E "update_option\(['\"]hangar18_manager_pages_v1|delete_option\(['\"]hangar18_manager_pages_v1" "$controller" "$preflight" "$validator" >/dev/null; then
  echo 'FAIL: I9 writes the legacy page store.'; exit 1
fi

# No WordPress page/post mutation or page repository is allowed in I9.
if grep -E '(wp_update_post|wp_insert_post|wp_delete_post|update_post_meta|delete_post_meta|LegacyOptionPageRepository|PageRepository)' "$controller" "$preflight" "$validator" src/Infrastructure/WordPress/WordPressOptionManualQaEvidenceRepository.php >/dev/null; then
  echo 'FAIL: I9 contains a page mutation/repository primitive.'; exit 1
fi

# An automated result must never be promoted into manual evidence by the service layer.
if grep -E 'save\([^;]*migration-rollback-live-copy|ConfirmedManual[^;]*true' "$preflight" >/dev/null; then
  echo 'FAIL: automated preflight can impersonate manual evidence.'; exit 1
fi

echo 'I9 QA dashboard safety contract (manual evidence only, copy preflight, no page-write): PASS'
