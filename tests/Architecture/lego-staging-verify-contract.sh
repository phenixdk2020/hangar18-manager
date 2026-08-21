#!/usr/bin/env bash
set -euo pipefail

TOOL='tools/lego-staging-verify.cjs'
WF='.github/workflows/lego-staging-build.yml'

test -f "$TOOL" || { echo "FAIL: missing $TOOL"; exit 1; }
test -f "$WF" || { echo "FAIL: missing $WF"; exit 1; }

require_contains() {
  local file="$1" needle="$2" label="$3"
  grep -F -- "$needle" "$file" >/dev/null || { echo "FAIL: $label"; echo "  missing: $needle"; exit 1; }
}

require_contains "$TOOL" 'packageSha256' 'package hash validation missing'
require_contains "$TOOL" 'Build commit:' 'build SHA binding missing'
require_contains "$TOOL" 'Plugin version:' 'version binding missing'
require_contains "$TOOL" 'officialRelease !== false' 'non-release invariant missing'
require_contains "$TOOL" 'publicCutoverAuthorized !== false' 'cutover deny invariant missing'
require_contains "$TOOL" 'SHA256SUMS.txt' 'checksum file validation missing'
require_contains "$WF" 'node tools/lego-staging-verify.cjs staging-dist' 'staging workflow must self-verify artifact before upload'

node --check "$TOOL"

if grep -Ei 'writeFile|appendFile|unlink|rmSync|renameSync|copyFile|execSync|spawnSync|child_process' "$TOOL" >/dev/null; then
  echo 'FAIL: artifact verifier must remain read-only'
  exit 1
fi

echo 'LEGO-037 staging artifact verifier contract: PASS'
