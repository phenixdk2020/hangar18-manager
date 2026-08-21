#!/usr/bin/env bash
set -euo pipefail

WF='.github/workflows/lego-staging-build.yml'
RUNBOOK='docs/lego-staging-install-runbook.md'
test -f "$WF" || { echo "FAIL: missing $WF"; exit 1; }
test -f "$RUNBOOK" || { echo "FAIL: missing $RUNBOOK"; exit 1; }

require_contains() {
  local file="$1" needle="$2" label="$3"
  grep -F -- "$needle" "$file" >/dev/null || { echo "FAIL: $label"; echo "  missing: $needle"; exit 1; }
}

require_contains "$WF" 'workflow_dispatch:' 'staging build must be manual-dispatch only'
require_contains "$WF" 'contents: read' 'staging build must have read-only repository permission'
require_contains "$WF" 'lego-manual-acceptance-contract.sh' 'manual acceptance contract must gate staging build'
require_contains "$WF" 'protected-domain-contract.sh' 'protected-domain contract must gate staging build'
require_contains "$WF" 'v0840-lego-side-by-side-contract.sh' 'side-by-side contract missing'
require_contains "$WF" 'v0841-lego-resize-contract.sh' 'resize contract missing'
require_contains "$WF" 'v0842-lego-responsive-layout-contract.sh' 'responsive layout contract missing'
require_contains "$WF" 'commitSha' 'build manifest must bind commit SHA'
require_contains "$WF" 'pluginVersion' 'build manifest must bind plugin version'
require_contains "$WF" "'officialRelease':False" 'staging manifest must mark non-release build'
require_contains "$WF" "'publicCutoverAuthorized':False" 'staging manifest must deny cutover authorization'
require_contains "$WF" 'cp hangar18-manager.php readme.txt TEST-BUILD.txt build/hangar18-manager/' 'build identity must be embedded in plugin ZIP'
require_contains "$WF" 'hangar18-manager/TEST-BUILD.txt' 'embedded build identity verification missing'
require_contains "$WF" 'actions/upload-artifact@v4' 'staging artifact upload missing'
require_contains "$WF" 'retention-days: 14' 'staging artifact retention missing'

require_contains "$RUNBOOK" 'SHA256SUMS.txt' 'install runbook must verify package hash'
require_contains "$RUNBOOK" 'TEST-BUILD.txt' 'install runbook must verify build identity'
require_contains "$RUNBOOK" 'Vehicle/Event/Gallery' 'install runbook protected-domain smoke missing'
require_contains "$RUNBOOK" 'Plugin rollback' 'plugin rollback instructions missing'
require_contains "$RUNBOOK" 'Data rollback' 'data rollback instructions missing'
require_contains "$RUNBOOK" 'B1/B2 restore' 'data restore owner missing'
require_contains "$RUNBOOK" 'ikke en officiel release' 'staging/non-release boundary missing'

if grep -Eq '^[[:space:]]*(push:|pull_request:)' "$WF"; then
  echo 'FAIL: staging build must not run automatically on push/PR'
  exit 1
fi
if grep -Ei 'contents:[[:space:]]*write|git push|git commit|release-config\.json|gh release|wp_update_post|wp_insert_post' "$WF" >/dev/null; then
  echo 'FAIL: staging build introduced release/write/public mutation primitive'
  exit 1
fi

echo 'LEGO-035/036 staging build + install/rollback contract: PASS'
