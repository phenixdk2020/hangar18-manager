#!/usr/bin/env bash
set -euo pipefail

INIT='tools/i9-evidence-init.cjs'
VALIDATOR='tools/i9-evidence-validator.cjs'
RECORD='tools/i9-evidence-record.cjs'
PLUGIN='hangar18-manager.php'
TARGET='https://test2.hangar18.dk/'

for file in "$INIT" "$VALIDATOR" "$RECORD" "$PLUGIN"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

node --check "$RECORD"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
SHA='3333333333333333333333333333333333333333'
VERSION="$(sed -n "s/^[[:space:]]*const VERSION = '\([^']*\)';.*/\1/p" "$PLUGIN" | head -n 1)"
SOURCE="$TMP/source.json"
NEXT="$TMP/next.json"

node "$INIT" \
  --sha "$SHA" \
  --version "$VERSION" \
  --wordpress-version '6.8.2' \
  --php-version '8.2' \
  --tester 'CI record contract' \
  --backup-restore-point 'H18-BACKUP-RECORD' \
  --target "$TARGET" \
  --output "$SOURCE"

SOURCE_HASH="$(sha256sum "$SOURCE" | awk '{print $1}')"

# PASS without evidence is impossible.
if node "$RECORD" "$SOURCE" --gate chrome --status PASS > "$NEXT" 2>/dev/null; then
  echo 'FAIL: recorder accepted PASS without evidence'
  exit 1
fi

# Unknown gates and statuses are rejected.
if node "$RECORD" "$SOURCE" --gate inventedGate --status PASS --evidence 'evidence/x.md' > "$NEXT" 2>/dev/null; then
  echo 'FAIL: recorder accepted unknown gate'
  exit 1
fi
if node "$RECORD" "$SOURCE" --gate chrome --status DONE --evidence 'evidence/x.md' > "$NEXT" 2>/dev/null; then
  echo 'FAIL: recorder accepted unknown status'
  exit 1
fi

# One evidenced PASS is recorded without mutating the source and overall remains PENDING.
node "$RECORD" "$SOURCE" \
  --gate chrome \
  --status PASS \
  --evidence 'evidence/chrome-desktop.md' \
  --browser-or-tool 'Google Chrome' \
  --notes 'Brand test recorded by operator.' > "$NEXT"

test "$(sha256sum "$SOURCE" | awk '{print $1}')" = "$SOURCE_HASH" || { echo 'FAIL: recorder mutated source manifest'; exit 1; }
node - "$NEXT" <<'NODE'
const m=require(process.argv[2]);
if(m.gates.chrome.status!=='PASS') process.exit(1);
if(m.gates.chrome.evidence.length!==1) process.exit(1);
if(m.gates.chrome.browserOrTool!=='Google Chrome') process.exit(1);
if(m.overallStatus!=='PENDING') process.exit(1);
NODE
node "$VALIDATOR" "$NEXT" --expected-sha "$SHA" --expected-version "$VERSION" --expected-target "$TARGET"

# Evidence is deduplicated and can be extended while source remains unchanged.
node "$RECORD" "$NEXT" --gate chrome --status PASS \
  --evidence 'evidence/chrome-desktop.md' \
  --evidence 'evidence/chrome-mobile.md' > "$TMP/chrome2.json"
node -e "const m=require(process.argv[1]); if(m.gates.chrome.evidence.length!==2) process.exit(1)" "$TMP/chrome2.json"

# FAIL takes precedence in derived overall status.
node "$RECORD" "$TMP/chrome2.json" --gate edge --status FAIL --evidence 'evidence/edge-failure.md' > "$TMP/fail.json"
node -e "const m=require(process.argv[1]); if(m.overallStatus!=='FAIL'||m.gates.edge.status!=='FAIL') process.exit(1)" "$TMP/fail.json"

# BLOCKED is derived when no FAIL remains.
node "$RECORD" "$TMP/fail.json" --gate edge --status BLOCKED --clear-evidence --evidence 'evidence/edge-blocked.md' > "$TMP/blocked.json"
node -e "const m=require(process.argv[1]); if(m.overallStatus!=='BLOCKED'||m.gates.edge.status!=='BLOCKED') process.exit(1)" "$TMP/blocked.json"

# Build a fully evidenced PASS only through eight explicit gate transformations.
cp "$SOURCE" "$TMP/all.json"
for gate in chrome edge firefox safari screenReader test2LiveE2E protectedDomains rollback; do
  node "$RECORD" "$TMP/all.json" --gate "$gate" --status PASS --evidence "evidence/${gate}.md" > "$TMP/all.next.json"
  mv "$TMP/all.next.json" "$TMP/all.json"
done
node -e "const m=require(process.argv[1]); if(m.overallStatus!=='PASS') process.exit(1)" "$TMP/all.json"
node "$VALIDATOR" "$TMP/all.json" --expected-sha "$SHA" --expected-version "$VERSION" --expected-target "$TARGET" --require-pass

# The recorder implementation itself must not contain write/rename/delete primitives.
if grep -E 'writeFileSync|renameSync|unlinkSync|rmSync|appendFileSync|createWriteStream' "$RECORD" >/dev/null; then
  echo 'FAIL: recorder contains a direct file-write primitive'
  exit 1
fi

# Evidence integrity is the next read-only layer and is executed transitively from this contract.
bash tests/Architecture/i9-evidence-integrity-contract.sh

echo "I9 read-only gate recorder contract: PASS ($VERSION)"
