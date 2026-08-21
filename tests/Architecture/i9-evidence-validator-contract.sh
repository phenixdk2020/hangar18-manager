#!/usr/bin/env bash
set -euo pipefail

VALIDATOR='tools/i9-evidence-validator.cjs'
INIT='tools/i9-evidence-init.cjs'
SCHEMA='docs/i9-evidence-manifest.schema.json'
EXAMPLE='docs/i9-evidence-manifest.example.json'

for file in "$VALIDATOR" "$INIT" "$SCHEMA" "$EXAMPLE"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

node --check "$VALIDATOR"
node --check "$INIT"

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
SHA='1111111111111111111111111111111111111111'
VERSION='0.8.42'
MANIFEST="$TMP/i9.json"

node "$INIT" \
  --sha "$SHA" \
  --version "$VERSION" \
  --wordpress-version '6.8.2' \
  --php-version '8.2' \
  --tester 'CI contract' \
  --backup-restore-point 'H18-BACKUP-TEST' \
  --output "$MANIFEST"

# Initializer must never manufacture acceptance.
node -e "const m=require(process.argv[1]); if(m.overallStatus!=='PENDING') process.exit(1); for(const g of Object.values(m.gates)){if(g.status!=='PENDING'||g.evidence.length!==0) process.exit(1)}" "$MANIFEST"
node "$VALIDATOR" "$MANIFEST" --expected-sha "$SHA" --expected-version "$VERSION"
if node "$VALIDATOR" "$MANIFEST" --require-pass >/dev/null 2>&1; then
  echo 'FAIL: pending manifest passed --require-pass'
  exit 1
fi

# Convert every required gate to evidenced PASS and require a clean release gate.
node - "$MANIFEST" <<'NODE'
const fs=require('fs');
const p=process.argv[2];
const m=JSON.parse(fs.readFileSync(p,'utf8'));
for(const [name,gate] of Object.entries(m.gates)){
  gate.status='PASS';
  gate.evidence=[`evidence/${name}.md`];
}
m.overallStatus='PASS';
fs.writeFileSync(p,JSON.stringify(m,null,2)+'\n');
NODE
node "$VALIDATOR" "$MANIFEST" --expected-sha "$SHA" --expected-version "$VERSION" --require-pass
node "$VALIDATOR" "$MANIFEST" --json --require-pass > "$TMP/result.json"
node -e "const r=require(process.argv[1]); if(!r.ok||r.derivedStatus!=='PASS'||r.gateCounts.PASS!==8) process.exit(1)" "$TMP/result.json"
node "$VALIDATOR" "$MANIFEST" --markdown --require-pass | grep -F 'Derived I9 status: **PASS**' >/dev/null

# Wrong build identity must block validation.
if node "$VALIDATOR" "$MANIFEST" --expected-sha '2222222222222222222222222222222222222222' >/dev/null 2>&1; then
  echo 'FAIL: wrong expected SHA was accepted'
  exit 1
fi
if node "$VALIDATOR" "$MANIFEST" --expected-version '9.9.9' >/dev/null 2>&1; then
  echo 'FAIL: wrong expected version was accepted'
  exit 1
fi

# A PASS gate without evidence must fail.
node - "$MANIFEST" <<'NODE'
const fs=require('fs'); const p=process.argv[2]; const m=JSON.parse(fs.readFileSync(p,'utf8'));
m.gates.safari.evidence=[]; fs.writeFileSync(p,JSON.stringify(m,null,2)+'\n');
NODE
if node "$VALIDATOR" "$MANIFEST" >/dev/null 2>&1; then
  echo 'FAIL: PASS gate without evidence was accepted'
  exit 1
fi

# Overall status must match gate-derived precedence.
node - "$MANIFEST" <<'NODE'
const fs=require('fs'); const p=process.argv[2]; const m=JSON.parse(fs.readFileSync(p,'utf8'));
m.gates.safari.evidence=['evidence/safari.md'];
m.gates.edge.status='FAIL';
m.overallStatus='PASS';
fs.writeFileSync(p,JSON.stringify(m,null,2)+'\n');
NODE
if node "$VALIDATOR" "$MANIFEST" >/dev/null 2>&1; then
  echo 'FAIL: inconsistent overallStatus was accepted'
  exit 1
fi

# FAIL is valid evidence state, but can never satisfy --require-pass.
node - "$MANIFEST" <<'NODE'
const fs=require('fs'); const p=process.argv[2]; const m=JSON.parse(fs.readFileSync(p,'utf8'));
m.overallStatus='FAIL'; fs.writeFileSync(p,JSON.stringify(m,null,2)+'\n');
NODE
node "$VALIDATOR" "$MANIFEST"
if node "$VALIDATOR" "$MANIFEST" --require-pass >/dev/null 2>&1; then
  echo 'FAIL: FAIL manifest passed release gate'
  exit 1
fi

echo 'I9 evidence validator/init contract: PASS'
