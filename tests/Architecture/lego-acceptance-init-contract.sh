#!/usr/bin/env bash
set -euo pipefail

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

cat > "$TMP/manifest.json" <<'JSON'
{
  "schemaVersion": "1.0",
  "purpose": "lego-staging-manual-acceptance",
  "commitSha": "1111111111111111111111111111111111111111",
  "pluginVersion": "0.8.39",
  "note": "contract",
  "package": "hangar18-manager-lego-staging.zip",
  "packageSha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "officialRelease": false,
  "publicCutoverAuthorized": false
}
JSON

node tools/lego-acceptance-init.cjs "$TMP/manifest.json" > "$TMP/record.json"
node tools/lego-acceptance-validate.cjs "$TMP/record.json" \
  --expected-sha 1111111111111111111111111111111111111111 \
  --expected-version 0.8.39 >/dev/null

node - "$TMP/record.json" <<'NODE'
const fs=require('fs');
const record=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const ids='ABCDEFGHIJKL'.split('');
if(record.overallStatus !== 'PENDING') throw new Error('bootstrap must remain PENDING');
if(record.build.commitSha !== '1111111111111111111111111111111111111111') throw new Error('SHA binding missing');
if(record.build.pluginVersion !== '0.8.39') throw new Error('version binding missing');
if(record.build.packageSha256 !== 'a'.repeat(64)) throw new Error('package SHA binding missing');
for(const id of ids){
  if(!record.scenarios[id] || record.scenarios[id].status !== 'PENDING') throw new Error(`scenario ${id} must be PENDING`);
  if(record.scenarios[id].evidence.length !== 0) throw new Error(`scenario ${id} must have no evidence`);
}
if(Object.values(record.criticalFlags).some(Boolean)) throw new Error('critical flags must start false');
NODE

if node tools/lego-acceptance-init.cjs "$TMP/manifest.json" --unknown >/dev/null 2>&1; then
  echo "Expected unknown argument failure" >&2
  exit 1
fi

node - "$TMP/manifest.json" "$TMP/bad.json" <<'NODE'
const fs=require('fs');
const src=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
src.publicCutoverAuthorized=true;
fs.writeFileSync(process.argv[3],JSON.stringify(src));
NODE
if node tools/lego-acceptance-init.cjs "$TMP/bad.json" >/dev/null 2>&1; then
  echo "Expected cutover-authorized manifest rejection" >&2
  exit 1
fi

grep -F "process.stdout.write" tools/lego-acceptance-init.cjs >/dev/null
! grep -Eq "writeFile|appendFile|renameSync|unlinkSync|rmSync" tools/lego-acceptance-init.cjs

echo "LEGO acceptance init contract: PASS"
