#!/usr/bin/env bash
set -euo pipefail

CTRL='src/Admin/DecisionPacketAdminController.php'
BOOT='src/Admin/IntegrationAdminBootstrap.php'

for file in "$CTRL" "$BOOT"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

php -l "$CTRL" >/dev/null

grep -F 'DecisionPacketAdminController::renderPanel();' "$BOOT" >/dev/null || { echo 'FAIL: read-only decision panel is not rendered by Ultimate Designer bootstrap'; exit 1; }
grep -F 'I10 · Decision packet · read-only' "$CTRL" >/dev/null || { echo 'FAIL: read-only operator heading missing'; exit 1; }
grep -F 'READ ONLY · CUTOVER LOCKED' "$CTRL" >/dev/null || { echo 'FAIL: cutover-lock badge missing'; exit 1; }
grep -F 'Executable: NO' "$CTRL" >/dev/null || { echo 'FAIL: executable lock missing from UI'; exit 1; }
grep -F 'PublicMutationAvailable: NO' "$CTRL" >/dev/null || { echo 'FAIL: public mutation lock missing from UI'; exit 1; }
grep -F 'AuthorizesCutover=false' "$CTRL" >/dev/null || { echo 'FAIL: explicit non-authorizing invariant missing from UI'; exit 1; }
grep -F 'ConversionDecisionPacketService' "$CTRL" >/dev/null || { echo 'FAIL: admin panel must reuse canonical decision packet service'; exit 1; }
grep -F 'ConversionDecisionPacketFingerprintService' "$CTRL" >/dev/null || { echo 'FAIL: admin panel must reuse canonical packet fingerprint'; exit 1; }

# This panel is display-only: no forms, action handlers, nonces, POST reads or write primitives.
if grep -Ei '<form|admin_post_|wp_nonce_field|\$_POST|wp_update_post|wp_insert_post|wp_delete_post|update_post_meta|delete_post_meta|update_option|delete_option|->save\(|->createShadow\(' "$CTRL" >/dev/null; then
  echo 'FAIL: decision packet panel contains a form/action/write primitive'
  exit 1
fi

# It must not register hooks of its own; render is invoked directly by the existing admin composition.
if grep -E 'add_action\(|add_filter\(|function register\(' "$CTRL" >/dev/null; then
  echo 'FAIL: decision packet panel introduced a parallel hook/registration path'
  exit 1
fi

echo 'I10 read-only decision packet admin contract: PASS'
