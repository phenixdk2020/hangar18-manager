#!/usr/bin/env bash
set -euo pipefail

INDEX='docs/i9-evidence-gate-index.md'
SESSION='docs/i9-evidence-session-runbook.md'

declare -A FILES=(
  [chrome]='docs/i9-evidence-gate-chrome.md'
  [edge]='docs/i9-evidence-gate-edge.md'
  [firefox]='docs/i9-evidence-gate-firefox.md'
  [safari]='docs/i9-evidence-gate-safari.md'
  [screenReader]='docs/i9-evidence-gate-screen-reader.md'
  [test2LiveE2E]='docs/i9-evidence-gate-test2-live-e2e.md'
  [protectedDomains]='docs/i9-evidence-gate-protected-domains.md'
  [rollback]='docs/i9-evidence-gate-rollback.md'
)

required=(chrome edge firefox safari screenReader test2LiveE2E protectedDomains rollback)

for required_file in "$INDEX" "$SESSION"; do
  test -f "$required_file" || { echo "FAIL: missing $required_file"; exit 1; }
done

for gate in "${required[@]}"; do
  file="${FILES[$gate]}"
  test -f "$file" || { echo "FAIL: missing template $file"; exit 1; }
  grep -F "**Gate key:** \`$gate\`" "$file" >/dev/null || { echo "FAIL: canonical gate key missing in $file"; exit 1; }
  grep -F '**Initial status:** `PENDING`' "$file" >/dev/null || { echo "FAIL: template must start PENDING: $file"; exit 1; }
  grep -F 'Commit SHA:' "$file" >/dev/null || { echo "FAIL: build SHA field missing: $file"; exit 1; }
  grep -F 'Plugin version:' "$file" >/dev/null || { echo "FAIL: plugin version field missing: $file"; exit 1; }
  grep -F 'Target URL' "$file" >/dev/null || { echo "FAIL: target field missing: $file"; exit 1; }
  grep -F 'Evidence 1:' "$file" >/dev/null || { echo "FAIL: evidence field missing: $file"; exit 1; }
  grep -F -- '- [ ] `PASS`' "$file" >/dev/null || { echo "FAIL: unselected PASS decision missing: $file"; exit 1; }
  if grep -F -- '- [x] `PASS`' "$file" >/dev/null || grep -F -- '- [X] `PASS`' "$file" >/dev/null; then
    echo "FAIL: template pre-accepts PASS: $file"
    exit 1
  fi
  grep -F "\`$gate\`" "$INDEX" >/dev/null || { echo "FAIL: $gate missing from operator index"; exit 1; }
  grep -F "\`$gate\`" "$SESSION" >/dev/null || { echo "FAIL: $gate missing from session runbook"; exit 1; }
done

# Index must map exactly the eight canonical gate rows, not invent a ninth gate.
rows="$(grep -E '^\| `(chrome|edge|firefox|safari|screenReader|test2LiveE2E|protectedDomains|rollback)` \|' "$INDEX" | wc -l | tr -d ' ')"
test "$rows" = '8' || { echo "FAIL: expected 8 canonical gate rows in index, got $rows"; exit 1; }

grep -F 'Automated Playwright/PHP QA kan støtte' "$INDEX" >/dev/null || { echo 'FAIL: manual-vs-automated boundary missing'; exit 1; }
grep -F 'I10-mutations/cutover-koden forbliver separat låst' "$INDEX" >/dev/null || { echo 'FAIL: I10 lock statement missing'; exit 1; }

grep -F 'Backup/restore-point ID:' "$SESSION" >/dev/null || { echo 'FAIL: session restore-point binding missing'; exit 1; }
grep -F 'Start en **ny build-bound evidence session**' "$SESSION" >/dev/null || { echo 'FAIL: stale-build retest policy missing'; exit 1; }
grep -F '`readyForI10=true` er stadig kun et dokumenteret readiness-resultat' "$SESSION" >/dev/null || { echo 'FAIL: readiness/cutover boundary missing'; exit 1; }
grep -F 'ikke at starte page conversion' "$SESSION" >/dev/null || { echo 'FAIL: non-PASS handoff stop rule missing'; exit 1; }

echo 'I9 manual evidence gate templates/session contract: PASS'
