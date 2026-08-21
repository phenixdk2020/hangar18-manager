#!/usr/bin/env bash
set -euo pipefail

WF='.github/workflows/lego-staging-build.yml'
test -f "$WF" || { echo "FAIL: missing $WF"; exit 1; }

require_contains() {
  local needle="$1" label="$2"
  grep -F -- "$needle" "$WF" >/dev/null || { echo "FAIL: $label"; echo "  missing: $needle"; exit 1; }
}

require_contains 'workflow_dispatch:' 'staging build must be manual-dispatch only'
require_contains 'contents: read' 'staging build must have read-only repository permission'
require_contains 'lego-manual-acceptance-contract.sh' 'manual acceptance contract must gate staging build'
require_contains 'protected-domain-contract.sh' 'protected-domain contract must gate staging build'
require_contains 'v0840-lego-side-by-side-contract.sh' 'side-by-side contract missing'
require_contains 'v0841-lego-resize-contract.sh' 'resize contract missing'
require_contains 'v0842-lego-responsive-layout-contract.sh' 'responsive layout contract missing'
require_contains 'commitSha' 'build manifest must bind commit SHA'
require_contains 'pluginVersion' 'build manifest must bind plugin version'
require_contains "'officialRelease':False" 'staging manifest must mark non-release build'
require_contains "'publicCutoverAuthorized':False" 'staging manifest must deny cutover authorization'
require_contains 'actions/upload-artifact@v4' 'staging artifact upload missing'
require_contains 'retention-days: 14' 'staging artifact retention missing'

if grep -Eq '^[[:space:]]*(push:|pull_request:)' "$WF"; then
  echo 'FAIL: staging build must not run automatically on push/PR'
  exit 1
fi
if grep -Ei 'contents:[[:space:]]*write|git push|git commit|release-config\.json|gh release|wp_update_post|wp_insert_post' "$WF" >/dev/null; then
  echo 'FAIL: staging build introduced release/write/public mutation primitive'
  exit 1
fi

echo 'LEGO-035 staging test build contract: PASS'
