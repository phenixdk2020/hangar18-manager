#!/usr/bin/env bash
set -euo pipefail

INIT='tools/i9-evidence-init.cjs'
VALIDATOR='tools/i9-evidence-validator.cjs'
RECORD='tools/i9-evidence-record.cjs'
READINESS='tools/i9-evidence-readiness.cjs'
WORKFLOW='.github/workflows/i9-evidence-validate.yml'
PLUGIN='hangar18-manager.php'
TARGET='https://test2.hangar18.dk/'

for file in "$INIT" "$VALIDATOR" "$RECORD" "$READINESS" "$WORKFLOW" "$PLUGIN"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done
node --check "$READINESS"

grep -F 'tools/i9-evidence-readiness.cjs' "$WORKFLOW" >/dev/null || { echo 'FAIL: Actions evidence gate must run readiness reporter'; exit 1; }
grep -F 'i9-evidence-readiness.json' "$WORKFLOW" >/dev/null || { echo 'FAIL: readiness report must be included in Actions artifact'; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
SHA='6666666666666666666666666666666666666666'
VERSION="$(sed -n "s/^[[:space:]]*const VERSION = '\([^']*\)';.*/\1/p" "$PLUGIN" | head -n 1)"
MANIFEST="$TMP/manifest.json"

node "$INIT" --sha "$SHA" --version "$VERSION" --wordpress-version '6.8.2' --php-version '8.2' \
  --tester 'CI readiness contract' --backup-restore-point 'H18-BACKUP-READINESS' --target "$TARGET" --output "$MANIFEST"

# Fresh evidence set must be valid but not ready for I10.
node "$READINESS" "$MANIFEST" --expected-sha "$SHA" --expected-version "$VERSION" --expected-target "$TARGET" > "$TMP/pending.json"
node - "$TMP/pending.json" <<'NODE'
const r=require(process.argv[2]);
if(!r.validationOk||r.derivedStatus!=='PENDING'||r.readyForI10) process.exit(1);
if(r.summary.required!==8||r.summary.complete!==0||r.summary.incomplete!==8||r.summary.pending!==8) process.exit(1);
if(!r.gates.every(g=>g.blocker==='gate-pending'&&!g.complete&&g.nextAction)) process.exit(1);
NODE
node "$READINESS" "$MANIFEST" --markdown | grep -F 'Ready for I10: **NO**' >/dev/null

# One evidenced PASS reduces blockers but must not unlock I10.
node "$RECORD" "$MANIFEST" --gate chrome --status PASS --evidence 'evidence/chrome.md' > "$TMP/one.json"
node "$READINESS" "$TMP/one.json" > "$TMP/one-readiness.json"
node - "$TMP/one-readiness.json" <<'NODE'
const r=require(process.argv[2]); const chrome=r.gates.find(g=>g.gate==='chrome');
if(r.readyForI10||r.summary.complete!==1||r.summary.incomplete!==7) process.exit(1);
if(!chrome||!chrome.complete||chrome.blocker!==''||chrome.evidenceCount!==1) process.exit(1);
NODE

# FAIL has explicit blocker semantics and can never be ready.
node "$RECORD" "$TMP/one.json" --gate edge --status FAIL --evidence 'evidence/edge-fail.md' > "$TMP/fail.json"
node "$READINESS" "$TMP/fail.json" > "$TMP/fail-readiness.json"
node - "$TMP/fail-readiness.json" <<'NODE'
const r=require(process.argv[2]); const edge=r.gates.find(g=>g.gate==='edge');
if(r.derivedStatus!=='FAIL'||r.readyForI10||r.summary.failed!==1) process.exit(1);
if(!edge||edge.blocker!=='gate-failed'||!edge.nextAction) process.exit(1);
NODE

# BLOCKED has distinct blocker semantics when no FAIL remains.
node "$RECORD" "$TMP/one.json" --gate edge --status BLOCKED --evidence 'evidence/edge-blocked.md' > "$TMP/blocked.json"
node "$READINESS" "$TMP/blocked.json" > "$TMP/blocked-readiness.json"
node - "$TMP/blocked-readiness.json" <<'NODE'
const r=require(process.argv[2]); const edge=r.gates.find(g=>g.gate==='edge');
if(r.derivedStatus!=='BLOCKED'||r.readyForI10||r.summary.blocked!==1) process.exit(1);
if(!edge||edge.blocker!=='gate-blocked') process.exit(1);
NODE

# Build a full evidenced PASS through eight explicit human-gate records.
cp "$MANIFEST" "$TMP/all.json"
for gate in chrome edge firefox safari screenReader test2LiveE2E protectedDomains rollback; do
  node "$RECORD" "$TMP/all.json" --gate "$gate" --status PASS --evidence "evidence/${gate}.md" > "$TMP/all.next.json"
  mv "$TMP/all.next.json" "$TMP/all.json"
done
node "$VALIDATOR" "$TMP/all.json" --expected-sha "$SHA" --expected-version "$VERSION" --expected-target "$TARGET" --require-pass
node "$READINESS" "$TMP/all.json" --expected-sha "$SHA" --expected-version "$VERSION" --expected-target "$TARGET" > "$TMP/pass-readiness.json"
node - "$TMP/pass-readiness.json" <<'NODE'
const r=require(process.argv[2]);
if(!r.validationOk||r.derivedStatus!=='PASS'||!r.readyForI10) process.exit(1);
if(r.summary.complete!==8||r.summary.incomplete!==0||r.gates.some(g=>!g.complete||g.blocker)) process.exit(1);
NODE
node "$READINESS" "$TMP/all.json" --markdown | grep -F 'Ready for I10: **YES**' >/dev/null

# Stale build/environment identity must force readiness false through validator failure.
node "$READINESS" "$TMP/all.json" --expected-sha '7777777777777777777777777777777777777777' > "$TMP/stale.json" || true
node - "$TMP/stale.json" <<'NODE'
const r=require(process.argv[2]);
if(r.validationOk||r.readyForI10||!Array.isArray(r.validationErrors)||r.validationErrors.length===0) process.exit(1);
NODE

# Readiness reporting itself is read-only.
if grep -E 'writeFileSync|renameSync|unlinkSync|rmSync|appendFileSync|createWriteStream' "$READINESS" >/dev/null; then
  echo 'FAIL: readiness tool contains a direct file-write primitive'
  exit 1
fi

echo "I9 evidence readiness/blocker contract: PASS ($VERSION)"
