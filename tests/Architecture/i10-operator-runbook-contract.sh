#!/usr/bin/env bash
set -euo pipefail

PLAN='src/Migration/ConversionPlanService.php'
GATE='src/Migration/ConversionReadinessGate.php'
PREFLIGHT='src/Migration/ConversionCutoverPreflightService.php'
ACCEPTANCE='src/Migration/ConversionAcceptanceValidator.php'
CHECKLIST='src/Migration/ConversionAcceptanceChecklist.php'
TARGETS='src/Migration/ConversionTargetCatalog.php'
RUNBOOK='docs/i10-operator-runbook.md'
BLOCKERS='docs/i10-blocker-reference.md'
TEMPLATE='docs/i10-acceptance-record-template.md'

for file in "$PLAN" "$GATE" "$PREFLIGHT" "$ACCEPTANCE" "$CHECKLIST" "$TARGETS" "$RUNBOOK" "$BLOCKERS" "$TEMPLATE"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

require_contains() {
  local file="$1" needle="$2" label="$3"
  grep -F -- "$needle" "$file" >/dev/null || { echo "FAIL: $label"; echo "  missing: $needle"; exit 1; }
}

# Existing runtime must remain plan/preflight-only.
require_contains "$PLAN" "'Mode'=>'plan-only'" 'plan-only mode missing'
require_contains "$PLAN" "'PublicMutationAvailable'=>false" 'conversion plan unexpectedly exposes mutation'
require_contains "$PREFLIGHT" "'Mode' => 'cutover-preflight-only'" 'preflight-only mode missing'
require_contains "$PREFLIGHT" "'Executable' => false" 'preflight unexpectedly executable'
require_contains "$PREFLIGHT" "'PublicMutationAvailable' => false" 'preflight unexpectedly exposes mutation'

# Fixed target order and protected-domain policy must be reflected in the operator docs.
require_contains "$TARGETS" "public const CORE_ORDER=['hjem','om-foreningen','kontakt','bliv-medlem'];" 'canonical core order changed'
require_contains "$RUNBOOK" '1. sikker comparison-/testside;' 'comparison must remain first'
require_contains "$RUNBOOK" '2. `hjem`;' 'Hjem order missing'
require_contains "$RUNBOOK" '3. `om-foreningen`;' 'Om order missing'
require_contains "$RUNBOOK" '4. `kontakt`;' 'Kontakt order missing'
require_contains "$RUNBOOK" '5. `bliv-medlem`;' 'Bliv medlem order missing'
require_contains "$RUNBOOK" 'legacy removal allersidst.' 'legacy removal last rule missing'
require_contains "$GATE" 'protected-legacy-runtime-policy:' 'protected legacy policy blocker missing from runtime'
require_contains "$BLOCKERS" '`protected-legacy-runtime-policy:<domain>`' 'protected legacy policy missing from blocker docs'

# Human acceptance checklist must stay aligned with documentation.
for key in desktop-compare tablet-compare mobile-compare save-flow preview-flow revision-flow rollback-flow; do
  require_contains "$CHECKLIST" "'$key'" "runtime acceptance check missing: $key"
  require_contains "$RUNBOOK" "\`$key\`" "runbook acceptance check missing: $key"
  require_contains "$TEMPLATE" "\`$key\`" "template acceptance check missing: $key"
done

require_contains "$ACCEPTANCE" "'ConfirmedManual'" 'manual confirmation state missing'
require_contains "$ACCEPTANCE" "'EvidenceRef'" 'evidence reference state missing'
require_contains "$ACCEPTANCE" "'SourceHash'" 'acceptance source hash missing'
require_contains "$RUNBOOK" '`ConfirmedManual=true`' 'manual confirmation requirement missing from runbook'
require_contains "$RUNBOOK" '`EvidenceRef`' 'evidence reference requirement missing from runbook'
require_contains "$RUNBOOK" '`SourceHash`' 'source hash requirement missing from runbook'

# Documentation must not imply that I10 is currently executable.
if grep -Ei 'cutover (nu|now)|public mutation (er|is) available|Executable=true|PublicMutationAvailable=true' "$RUNBOOK" "$BLOCKERS" "$TEMPLATE" >/dev/null; then
  echo 'FAIL: I10 prep documentation implies executable public cutover'
  exit 1
fi

echo 'I10 operator runbook contract: PASS'
