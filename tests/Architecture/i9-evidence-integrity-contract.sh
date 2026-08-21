#!/usr/bin/env bash
set -euo pipefail

INIT='tools/i9-evidence-init.cjs'
VALIDATOR='tools/i9-evidence-validator.cjs'
RECORD='tools/i9-evidence-record.cjs'
INTEGRITY='tools/i9-evidence-integrity.cjs'
WORKFLOW='.github/workflows/i9-evidence-validate.yml'
PLUGIN='hangar18-manager.php'
TARGET='https://test2.hangar18.dk/'

for file in "$INIT" "$VALIDATOR" "$RECORD" "$INTEGRITY" "$WORKFLOW" "$PLUGIN"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done
node --check "$INTEGRITY"

grep -F 'tools/i9-evidence-integrity.cjs' "$WORKFLOW" >/dev/null || { echo 'FAIL: Actions release gate does not run integrity index'; exit 1; }
grep -F 'i9-evidence-integrity.json' "$WORKFLOW" >/dev/null || { echo 'FAIL: integrity artifact report missing from workflow'; exit 1; }
grep -F 'evidence_root:' "$WORKFLOW" >/dev/null || { echo 'FAIL: evidence root input missing'; exit 1; }
grep -F 'require_all_local:' "$WORKFLOW" >/dev/null || { echo 'FAIL: all-local integrity input missing'; exit 1; }
grep -F 'contents: read' "$WORKFLOW" >/dev/null || { echo 'FAIL: integrity workflow must remain read-only'; exit 1; }

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
ROOT="$TMP/root"
mkdir -p "$ROOT/evidence"
SHA='4444444444444444444444444444444444444444'
VERSION="$(sed -n "s/^[[:space:]]*const VERSION = '\([^']*\)';.*/\1/p" "$PLUGIN" | head -n 1)"
MANIFEST="$ROOT/manifest.json"
printf 'chrome screenshot metadata\n' > "$ROOT/evidence/chrome.txt"
printf 'rollback notes\n' > "$ROOT/evidence/rollback.txt"

node "$INIT" --sha "$SHA" --version "$VERSION" --wordpress-version '6.8.2' --php-version '8.2' \
  --tester 'CI integrity contract' --backup-restore-point 'H18-BACKUP-INTEGRITY' --target "$TARGET" --output "$MANIFEST"

# Add local evidence, one external evidence reference and keep the manifest otherwise pending.
node "$RECORD" "$MANIFEST" --gate chrome --status PASS --evidence 'evidence/chrome.txt' > "$ROOT/next.json"
mv "$ROOT/next.json" "$MANIFEST"
node "$RECORD" "$MANIFEST" --gate rollback --status PENDING --evidence 'https://example.invalid/actions/123' > "$ROOT/next.json"
mv "$ROOT/next.json" "$MANIFEST"

node "$INTEGRITY" "$MANIFEST" --root "$ROOT" --expected-sha "$SHA" --expected-version "$VERSION" --expected-target "$TARGET" > "$TMP/index.json"
node - "$TMP/index.json" "$ROOT/evidence/chrome.txt" <<'NODE'
const fs=require('fs'); const crypto=require('crypto');
const i=require(process.argv[2]); const p=process.argv[3];
const expected=crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex');
if(!i.ok) process.exit(1);
if(i.summary.references!==2||i.summary.localVerified!==1||i.summary.external!==1||i.summary.unresolved!==0) process.exit(1);
const local=i.entries.find(e=>e.reference==='evidence/chrome.txt');
if(!local||!local.verified||local.sha256!==expected) process.exit(1);
const ext=i.entries.find(e=>e.kind==='external'); if(!ext||ext.verified) process.exit(1);
NODE

# Markdown must expose the hash/index summary.
node "$INTEGRITY" "$MANIFEST" --root "$ROOT" --markdown | grep -F '# I9 Evidence Integrity' >/dev/null
node "$INTEGRITY" "$MANIFEST" --root "$ROOT" --markdown | grep -F 'local verified' >/dev/null

# External refs are allowed normally but fail explicit all-local mode.
if node "$INTEGRITY" "$MANIFEST" --root "$ROOT" --require-all-local >/dev/null 2>&1; then
  echo 'FAIL: external reference passed --require-all-local'
  exit 1
fi

# Missing local files are always an integrity failure.
node "$RECORD" "$MANIFEST" --gate edge --status PENDING --evidence 'evidence/missing.txt' > "$ROOT/missing.json"
if node "$INTEGRITY" "$ROOT/missing.json" --root "$ROOT" >/dev/null 2>&1; then
  echo 'FAIL: missing local evidence was accepted'
  exit 1
fi

# Absolute/traversal local paths must be rejected as non-contained.
node - "$MANIFEST" "$ROOT/traversal.json" <<'NODE'
const fs=require('fs'); const m=require(process.argv[2]);
m.gates.edge.evidence=['../outside.txt']; fs.writeFileSync(process.argv[3],JSON.stringify(m,null,2)+'\n');
NODE
if node "$INTEGRITY" "$ROOT/traversal.json" --root "$ROOT" >/dev/null 2>&1; then
  echo 'FAIL: traversal evidence path was accepted'
  exit 1
fi

# Build/environment binding carries through the integrity command.
if node "$INTEGRITY" "$MANIFEST" --root "$ROOT" --expected-sha '5555555555555555555555555555555555555555' >/dev/null 2>&1; then
  echo 'FAIL: stale SHA passed integrity validation'
  exit 1
fi
if node "$INTEGRITY" "$MANIFEST" --root "$ROOT" --expected-target 'https://example.invalid/' >/dev/null 2>&1; then
  echo 'FAIL: wrong target passed integrity validation'
  exit 1
fi

# Integrity tool itself is read-only with respect to evidence/manifests.
if grep -E 'writeFileSync|renameSync|unlinkSync|rmSync|appendFileSync|createWriteStream' "$INTEGRITY" >/dev/null; then
  echo 'FAIL: integrity tool contains a direct file-write primitive'
  exit 1
fi

echo "I9 evidence integrity + workflow contract: PASS ($VERSION)"
