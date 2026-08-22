#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$root"

tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT
mkdir -p "$tmp/dist"
cp dist/hangar18-manager.zip "$tmp/dist/hangar18-manager.zip"
cp update.json "$tmp/update.json"

sha="1111111111111111111111111111111111111111"
node tools/lego-release-acceptance-init.cjs "$tmp/update.json" --commit-sha="$sha" > "$tmp/record.json"
node tools/lego-acceptance-validate.cjs "$tmp/record.json" --expected-sha="$sha" --expected-version="$(php -r '$j=json_decode(file_get_contents("update.json"),true); echo $j["version"];')" > /dev/null

node - "$tmp/record.json" <<'NODE'
const fs=require('fs');
const record=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
if(record.overallStatus!=='PENDING') throw new Error('bootstrap must start PENDING');
if(Object.keys(record.scenarios||{}).join('')!=='ABCDEFGHIJKL') throw new Error('A-L scenarios required');
for(const [id,s] of Object.entries(record.scenarios)) {
  if(s.status!=='PENDING' || !Array.isArray(s.evidence) || s.evidence.length!==0) throw new Error(`${id} must start PENDING without evidence`);
}
if(record.criticalFlags.consoleError || record.criticalFlags.dataLossOrDuplicate || record.criticalFlags.protectedDomainRegression) throw new Error('critical flags must start false');
if(record.environment.stagingUrl!=='https://test2.hangar18.dk') throw new Error('default staging target mismatch');
if(!/public cutover is not authorized/i.test(record.notes||'')) throw new Error('cutover safety note required');
NODE

release_version="$(php -r '$j=json_decode(file_get_contents("update.json"),true); echo $j["version"] ?? "";')"
release_package_sha="$(php -r '$j=json_decode(file_get_contents("update.json"),true); echo $j["package_sha256"] ?? "";')"
version_slug="$(printf '%s' "$release_version" | tr -d '.')"
canonical="docs/lego-v${version_slug}-manual-acceptance.json"
test -f "$canonical" || { echo "FAIL: missing canonical release acceptance $canonical" >&2; exit 1; }
release_sha="$(php -r '$j=json_decode(file_get_contents($argv[1]),true); echo $j["build"]["commitSha"] ?? "";' "$canonical")"
node tools/lego-acceptance-validate.cjs "$canonical" --expected-sha="$release_sha" --expected-version="$release_version" >/dev/null
node - "$canonical" "$release_package_sha" <<'NODE'
const fs=require('fs');
const record=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
const expectedPackageSha=process.argv[3];
if(record.build.packageSha256!==expectedPackageSha) throw new Error('canonical record package hash must match update.json');
if(!['PENDING','PASS','FAIL'].includes(record.overallStatus)) throw new Error('canonical release record has invalid overall status');
if(Object.keys(record.scenarios||{}).join('')!=='ABCDEFGHIJKL') throw new Error('canonical A-L scenarios required');
for(const [id,s] of Object.entries(record.scenarios||{})) {
  if(!['PENDING','PASS','FAIL','BLOCKED'].includes(s.status)) throw new Error(`${id} canonical scenario status invalid`);
  if(!Array.isArray(s.evidence)) throw new Error(`${id} canonical evidence must be an array`);
  if(s.status==='PASS' && s.evidence.length===0) throw new Error(`${id} canonical PASS requires evidence`);
}
if(record.environment.stagingUrl!=='https://test2.hangar18.dk') throw new Error('canonical staging target mismatch');
if(!/public cutover is not authorized/i.test(record.notes||'')) throw new Error('canonical cutover safety note required');
NODE

python3 - "$tmp/update.json" <<'PY'
import json,sys
p=sys.argv[1]
j=json.load(open(p))
j['package_sha256']='0'*64
open(p,'w').write(json.dumps(j))
PY
if node tools/lego-release-acceptance-init.cjs "$tmp/update.json" --commit-sha="$sha" >/dev/null 2>&1; then
  echo "Expected bad package SHA to fail" >&2
  exit 1
fi

cp update.json "$tmp/update.json"
python3 - "$tmp/update.json" <<'PY'
import json,sys
p=sys.argv[1]
j=json.load(open(p))
j['package_path']='../outside.zip'
open(p,'w').write(json.dumps(j))
PY
if node tools/lego-release-acceptance-init.cjs "$tmp/update.json" --commit-sha="$sha" >/dev/null 2>&1; then
  echo "Expected unsafe package path to fail" >&2
  exit 1
fi

if node tools/lego-release-acceptance-init.cjs update.json --commit-sha=short >/dev/null 2>&1; then
  echo "Expected short commit SHA to fail" >&2
  exit 1
fi

echo "LEGO release acceptance init contract: PASS"
