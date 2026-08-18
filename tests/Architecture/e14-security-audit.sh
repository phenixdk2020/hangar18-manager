#!/usr/bin/env bash
set -euo pipefail

fail=0

for pattern in 'eval[[:space:]]*\(' 'shell_exec[[:space:]]*\(' 'passthru[[:space:]]*\(' 'system[[:space:]]*\(' 'unserialize[[:space:]]*\('; do
  if grep -RInE "$pattern" src --include='*.php'; then
    echo "SECURITY HIGH: forbidden primitive matched: $pattern"
    fail=1
  fi
done

# New architecture services must not read request globals directly. HTTP adapters/controllers
# should own request parsing and pass validated values into services.
if grep -RInE '\$_(GET|POST|REQUEST|FILES|COOKIE)\b' src --include='*.php'; then
  echo 'SECURITY HIGH: service layer reads raw request globals directly.'
  fail=1
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

echo 'E14 security audit (new architecture scope): PASS'
