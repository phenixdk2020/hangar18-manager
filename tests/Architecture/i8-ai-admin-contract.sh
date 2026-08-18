#!/usr/bin/env bash
set -euo pipefail

controller='src/Admin/AiAdminController.php'
settings='src/Infrastructure/WordPress/WordPressOptionAiSettingsRepository.php'
proposals='src/Infrastructure/WordPress/WordPressOptionAiProposalRepository.php'
factory='src/Infrastructure/WordPress/WordPressAiProviderRegistryFactory.php'

grep -F "current_user_can('manage_options')" "$controller" >/dev/null
grep -F 'CapabilityCatalog::USE_AI' "$controller" >/dev/null
grep -F 'check_admin_referer(self::NONCE_ACTION)' "$controller" >/dev/null
grep -F 'hangar18_ud_ai_providers' "$factory" >/dev/null
grep -F 'Credentials are deliberately not part' src/AI/AiSettings.php >/dev/null
grep -F 'AI proposal token secret must be at least 32 characters.' src/AI/AiProposalTokenService.php >/dev/null
grep -F "hash_hmac('sha256'" src/AI/AiProposalTokenService.php >/dev/null
grep -F 'hash_equals' src/AI/AiProposalTokenService.php >/dev/null
grep -F 'Apply/Undo' "$controller" >/dev/null

# I8 may store only provider id/enabled settings and isolated proposal state. No page mutation primitive is allowed.
if grep -E '(wp_update_post|wp_insert_post|wp_delete_post|update_post_meta|delete_post_meta|LegacyOptionPageRepository|PageRepository|->save\([^)]*Page)' "$controller" "$settings" "$proposals" >/dev/null; then
  echo 'FAIL: I8 contains a page mutation primitive.'; exit 1
fi

# Credentials/secrets must not become a settings field or form input.
if grep -Ei 'name="(api[_-]?key|secret|token|password|credential)' "$controller" >/dev/null; then
  echo 'FAIL: I8 admin exposes a credential input.'; exit 1
fi
if grep -Ei "\['(api[_-]?key|secret|password|credential)'\]" src/AI/AiSettings.php "$settings" >/dev/null; then
  echo 'FAIL: I8 settings model persists credential-like fields.'; exit 1
fi

# No automatic accept path.
grep -F 'AI suggestion requires explicit user acceptance.' src/AI/SuggestionGuard.php >/dev/null
if grep -E 'accept\([^,]+,[[:space:]]*true\)' src/Infrastructure src/Core --include='*.php' >/dev/null; then
  echo 'FAIL: non-admin infrastructure auto-accepts AI suggestions.'; exit 1
fi

echo 'I8 AI admin safety contract (no credentials, no page-write, explicit acceptance): PASS'
