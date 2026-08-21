#!/usr/bin/env bash
set -euo pipefail

SPEC='tests/Live/i9-public-readonly.spec.cjs'
CONFIG='tests/Live/playwright.i9-public.config.cjs'
WORKFLOW='.github/workflows/i9-test2-live-readonly.yml'
RUNBOOK='docs/i9-manual-qa-evidence-runbook.md'
TEST2='docs/i9-test2-live-e2e-checklist.md'
ROLLBACK='docs/i9-rollback-rehearsal.md'
MANUAL='docs/ultimate-designer-user-manual.md'
MANIFEST_SCHEMA='docs/i9-evidence-manifest.schema.json'
MANIFEST_EXAMPLE='docs/i9-evidence-manifest.example.json'

for file in "$SPEC" "$CONFIG" "$WORKFLOW" "$RUNBOOK" "$TEST2" "$ROLLBACK" "$MANUAL" "$MANIFEST_SCHEMA" "$MANIFEST_EXAMPLE"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

require_contains() {
  local file="$1" needle="$2" label="$3"
  grep -F -- "$needle" "$file" >/dev/null || { echo "FAIL: $label"; echo "  missing: $needle"; exit 1; }
}

# Read-only public smoke scope and evidence. It must be explicit-dispatch only.
require_contains "$WORKFLOW" 'workflow_dispatch:' 'live smoke must remain explicitly dispatched'
if grep -Eq '^  (push|pull_request):' "$WORKFLOW"; then
  echo 'FAIL: I9 live smoke must not run automatically on push/pull_request'
  exit 1
fi
require_contains "$WORKFLOW" "default: 'https://test2.hangar18.dk'" 'test2 default target missing'
require_contains "$WORKFLOW" 'actions/upload-artifact@v4' 'live evidence artifact upload missing'
require_contains "$SPEC" "'/koeretoejer-og-materiel/'" 'Vehicle route missing'
require_contains "$SPEC" "'/events/'" 'Event route missing'
require_contains "$SPEC" "'/billedgalleri/'" 'Gallery route missing'
require_contains "$SPEC" 'horizontal page overflow' 'responsive overflow assertion missing'
require_contains "$SPEC" 'page.screenshot' 'screenshot evidence missing'
require_contains "$SPEC" 'critical error on this website' 'WordPress critical-error guard missing'
require_contains "$SPEC" 'unexpectedly redirected to login' 'login-redirect rejection guard missing'

# The public smoke may inspect URLs containing wp-login/wp-admin as negative assertions,
# but it must not interact with controls, authenticate, submit, upload or call write methods.
if grep -Ei '\b(POST|PUT|PATCH|DELETE)\b|request\.(post|put|patch|delete)\s*\(|\.fill\s*\(|\.type\s*\(|\.pressSequentially\s*\(|\.check\s*\(|\.uncheck\s*\(|\.selectOption\s*\(|\.setInputFiles\s*\(|\.click\s*\(|\.dblclick\s*\(|\.tap\s*\(' "$SPEC" >/dev/null; then
  echo 'FAIL: I9 public smoke contains an interactive/mutating primitive'
  exit 1
fi

# Documentation must keep the manual/live gate distinction explicit.
require_contains "$RUNBOOK" 'Automatiseret CI er støttebevis, ikke erstatning.' 'manual evidence distinction missing'
require_contains "$TEST2" 'staging/kopi og ikke produktion' 'test2 staging preflight missing'
require_contains "$ROLLBACK" 'Et FAIL blokerer I10.' 'rollback blocking rule missing'
require_contains "$MANUAL" 'Vehicle, Event og Gallery er fortsat beskyttede legacy-domæner' 'protected-domain warning missing from manual'

# Evidence manifests must be valid JSON and preserve every mandatory I9 gate.
node -e "JSON.parse(require('fs').readFileSync(process.argv[1], 'utf8'))" "$MANIFEST_SCHEMA"
node -e "const m=JSON.parse(require('fs').readFileSync(process.argv[1],'utf8')); const required=['chrome','edge','firefox','safari','screenReader','test2LiveE2E','protectedDomains','rollback']; if(m.schemaVersion!==1||m.overallStatus!=='PENDING'||required.some(k=>!m.gates||!m.gates[k])) process.exit(1);" "$MANIFEST_EXAMPLE"
require_contains "$MANIFEST_SCHEMA" '"overallStatus"' 'manifest overall status missing'
require_contains "$MANIFEST_SCHEMA" '"rollback"' 'manifest rollback gate missing'
require_contains "$MANIFEST_SCHEMA" '"minItems": 1' 'PASS gate must require evidence'

node --check "$SPEC"
node --check "$CONFIG"

echo 'I9 live read-only preparation contract: PASS'
