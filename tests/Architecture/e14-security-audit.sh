#!/usr/bin/env bash
set -euo pipefail

fail=0

# Dangerous execution/deserialization primitives remain forbidden everywhere in the
# extracted architecture, including controllers/adapters.
for pattern in 'eval[[:space:]]*\(' 'shell_exec[[:space:]]*\(' 'passthru[[:space:]]*\(' 'system[[:space:]]*\(' 'unserialize[[:space:]]*\('; do
  if grep -RInE "$pattern" src --include='*.php'; then
    echo "SECURITY HIGH: forbidden primitive matched: $pattern"
    fail=1
  fi
done

# Domain/services must never parse raw request globals. Admin/Rest are explicit HTTP
# controller boundaries: they may parse requests, but must validate/sanitize before
# passing values to the extracted services.
service_request_hits="$(
  find src -type f -name '*.php' \
    ! -path 'src/Admin/*' \
    ! -path 'src/Rest/*' \
    -print0 | xargs -0 grep -nHE '\$_(GET|POST|REQUEST|FILES|COOKIE)\b' || true
)"
if [[ -n "$service_request_hits" ]]; then
  printf '%s\n' "$service_request_hits"
  echo 'SECURITY HIGH: domain/service layer reads raw request globals directly.'
  fail=1
fi

# I1/I2 admin HTTP boundary: every mutating Site Builder handler passes through the
# same capability + nonce guard, and request values are normalized before storage.
controller='src/Admin/SiteTemplateAdminController.php'
if [[ -f "$controller" ]]; then
  grep -F "current_user_can('edit_pages')" "$controller" >/dev/null || { echo 'SECURITY HIGH: I2 controller capability guard missing.'; fail=1; }
  grep -F 'check_admin_referer(self::NONCE_ACTION)' "$controller" >/dev/null || { echo 'SECURITY HIGH: I2 controller nonce guard missing.'; fail=1; }
  grep -F 'sanitize_key' "$controller" >/dev/null || { echo 'SECURITY HIGH: I2 identifier sanitization missing.'; fail=1; }
  grep -F 'sanitize_text_field' "$controller" >/dev/null || { echo 'SECURITY HIGH: I2 text sanitization missing.'; fail=1; }
  grep -F 'wp_kses_post' "$controller" >/dev/null || { echo 'SECURITY HIGH: I2 rich-content sanitization missing.'; fail=1; }
  grep -F 'sanitize_hex_color' "$controller" >/dev/null || { echo 'SECURITY HIGH: I2 color sanitization missing.'; fail=1; }
fi

# Capability and safety boundaries required by the design.
grep -F "hangar18_use_custom_code" src/Permissions/CapabilityCatalog.php >/dev/null
grep -F "hangar18_use_ai" src/Permissions/CapabilityCatalog.php >/dev/null
grep -F "requires explicit confirmation" src/Portability/ImportExecutor.php >/dev/null || grep -F "Import requires explicit confirmation" src/Portability/ImportExecutor.php >/dev/null
grep -F "Preview token secret must be at least 32 characters" src/Workflow/PreviewTokenService.php >/dev/null
grep -F "hash_hmac('sha256'" src/Workflow/PreviewTokenService.php >/dev/null
grep -F "hash_equals" src/Workflow/PreviewTokenService.php >/dev/null
grep -F "https" src/Interaction/RedirectActionHandler.php >/dev/null
grep -F "https" src/Infrastructure/WordPress/WordPressWebhookActionHandler.php >/dev/null

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi

echo 'E14 security audit (services + HTTP controller boundaries): PASS'
