#!/usr/bin/env bash
set -euo pipefail

fail=0
for pattern in 'eval[[:space:]]*\(' 'shell_exec[[:space:]]*\(' 'passthru[[:space:]]*\(' 'system[[:space:]]*\(' 'unserialize[[:space:]]*\('; do
  if grep -RInE "$pattern" src --include='*.php'; then echo "SECURITY HIGH: forbidden primitive matched: $pattern"; fail=1; fi
done

service_request_hits="$(find src -type f -name '*.php' ! -path 'src/Admin/*' ! -path 'src/Rest/*' -print0 | xargs -0 grep -nHE '\$_(GET|POST|REQUEST|FILES|COOKIE)\b' || true)"
if [[ -n "$service_request_hits" ]]; then printf '%s\n' "$service_request_hits"; echo 'SECURITY HIGH: domain/service layer reads raw request globals directly.'; fail=1; fi

check_admin_controller(){
  local controller="$1" label="$2"
  [[ -f "$controller" ]] || return 0
  grep -F "current_user_can('edit_pages')" "$controller" >/dev/null || { echo "SECURITY HIGH: $label capability guard missing."; fail=1; }
}
check_admin_controller src/Admin/SiteTemplateAdminController.php I2
check_admin_controller src/Admin/MenuAdminController.php I3
check_admin_controller src/Admin/SideHealthAdminController.php I4

grep -F 'check_admin_referer(self::NONCE_ACTION)' src/Admin/SiteTemplateAdminController.php >/dev/null || { echo 'SECURITY HIGH: I2 nonce guard missing.'; fail=1; }
grep -F 'check_admin_referer(self::NONCE_ACTION)' src/Admin/MenuAdminController.php >/dev/null || { echo 'SECURITY HIGH: I3 nonce guard missing.'; fail=1; }
grep -F 'check_ajax_referer(self::NONCE_ACTION' src/Admin/SideHealthAdminController.php >/dev/null || { echo 'SECURITY HIGH: I4 AJAX nonce guard missing.'; fail=1; }

grep -F 'sanitize_key' src/Admin/SiteTemplateAdminController.php >/dev/null || fail=1
grep -F 'sanitize_text_field' src/Admin/SiteTemplateAdminController.php >/dev/null || fail=1
grep -F 'wp_kses_post' src/Admin/SiteTemplateAdminController.php >/dev/null || fail=1
grep -F 'sanitize_hex_color' src/Admin/SiteTemplateAdminController.php >/dev/null || fail=1

grep -F 'sanitize_key' src/Admin/MenuAdminController.php >/dev/null || fail=1
grep -F 'sanitize_text_field' src/Admin/MenuAdminController.php >/dev/null || fail=1
grep -F 'esc_url_raw' src/Admin/MenuAdminController.php >/dev/null || fail=1
grep -F 'javascript|data|vbscript' src/Admin/MenuAdminController.php >/dev/null || fail=1

# I4 accepts a transient DOM snapshot only. It must be bounded and read-only.
grep -F 'MAX_JSON_BYTES' src/Admin/SideHealthAdminController.php >/dev/null || { echo 'SECURITY HIGH: I4 request-size limit missing.'; fail=1; }
grep -F 'count($sections) > 100' src/Admin/SideHealthAdminController.php >/dev/null || { echo 'SECURITY HIGH: I4 section-count limit missing.'; fail=1; }
if grep -E '(update_option|wp_update_post|->save\(|delete_option|wp_delete_post)' src/Admin/SideHealthAdminController.php >/dev/null; then
  echo 'SECURITY HIGH: I4 Side Health controller contains a write primitive.'
  fail=1
fi

grep -F "hangar18_use_custom_code" src/Permissions/CapabilityCatalog.php >/dev/null
grep -F "hangar18_use_ai" src/Permissions/CapabilityCatalog.php >/dev/null
grep -F "Import requires explicit confirmation" src/Portability/ImportExecutor.php >/dev/null
grep -F "hash_hmac('sha256'" src/Workflow/PreviewTokenService.php >/dev/null
grep -F "hash_equals" src/Workflow/PreviewTokenService.php >/dev/null
grep -F "https" src/Interaction/RedirectActionHandler.php >/dev/null
grep -F "https" src/Infrastructure/WordPress/WordPressWebhookActionHandler.php >/dev/null

if [[ "$fail" -ne 0 ]]; then exit 1; fi
echo 'E14 security audit (services + HTTP controller boundaries incl. I4 read-only bridge): PASS'
