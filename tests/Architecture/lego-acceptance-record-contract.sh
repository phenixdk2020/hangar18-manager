#!/usr/bin/env bash
set -euo pipefail

TOOL='tools/lego-acceptance-validate.cjs'
SCHEMA='docs/lego-manual-acceptance.schema.json'
EXAMPLE='docs/lego-manual-acceptance.example.json'

for file in "$TOOL" "$SCHEMA" "$EXAMPLE"; do
  test -f "$file" || { echo "FAIL: missing $file"; exit 1; }
done

node --check "$TOOL"
node "$TOOL" "$EXAMPLE" >/tmp/lego-acceptance-pending.json

grep -F '"overallStatus": "PENDING"' /tmp/lego-acceptance-pending.json >/dev/null || { echo 'FAIL: pending example did not validate as PENDING'; exit 1; }

if node "$TOOL" "$EXAMPLE" --require-pass >/dev/null 2>&1; then
  echo 'FAIL: PENDING example must not pass --require-pass'
  exit 1
fi

python3 <<'PY'
import json
p='docs/lego-manual-acceptance.example.json'
d=json.load(open(p,encoding='utf-8'))
d['build']['commitSha']='1'*40
d['build']['packageSha256']='2'*64
for key in d['scenarios']:
    d['scenarios'][key]['status']='PASS'
    d['scenarios'][key]['evidence']=[f'evidence/{key}.png']
d['overallStatus']='PASS'
json.dump(d,open('/tmp/lego-acceptance-pass.json','w',encoding='utf-8'),indent=2)

bad=json.loads(json.dumps(d))
bad['scenarios']['C']['evidence']=[]
json.dump(bad,open('/tmp/lego-acceptance-no-evidence.json','w',encoding='utf-8'),indent=2)

critical=json.loads(json.dumps(d))
critical['criticalFlags']['protectedDomainRegression']=True
critical['overallStatus']='FAIL'
json.dump(critical,open('/tmp/lego-acceptance-critical.json','w',encoding='utf-8'),indent=2)
PY

node "$TOOL" /tmp/lego-acceptance-pass.json --require-pass --expected-sha=$(printf '1%.0s' {1..40}) --expected-version=0.8.39 >/dev/null
node "$TOOL" /tmp/lego-acceptance-critical.json >/tmp/lego-critical-result.json
grep -F '"overallStatus": "FAIL"' /tmp/lego-critical-result.json >/dev/null || { echo 'FAIL: critical protected-domain regression must compute FAIL'; exit 1; }

if node "$TOOL" /tmp/lego-acceptance-no-evidence.json >/dev/null 2>&1; then
  echo 'FAIL: PASS scenario without evidence must be rejected'
  exit 1
fi
if node "$TOOL" /tmp/lego-acceptance-pass.json --expected-sha=$(printf '3%.0s' {1..40}) >/dev/null 2>&1; then
  echo 'FAIL: expected SHA mismatch must be rejected'
  exit 1
fi

if grep -Ei 'writeFile|appendFile|unlink|rmSync|renameSync|copyFile|child_process|execSync|spawnSync' "$TOOL" >/dev/null; then
  echo 'FAIL: LEGO acceptance validator must remain read-only'
  exit 1
fi

echo 'LEGO-038 manual acceptance record contract: PASS'
