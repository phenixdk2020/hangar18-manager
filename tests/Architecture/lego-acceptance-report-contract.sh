#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$root"

TOOL='tools/lego-acceptance-report.cjs'
RECORD='docs/lego-v0840-manual-acceptance.json'

test -f "$TOOL" || { echo "FAIL: missing $TOOL"; exit 1; }
test -f "$RECORD" || { echo "FAIL: missing $RECORD"; exit 1; }
node --check "$TOOL"

node "$TOOL" "$RECORD" \
  --expected-sha=b35b3809500f7de90ab7a3df0249fd84194edb51 \
  --expected-version=0.8.40 \
  --expected-package-sha=1497d3f0bd784aa10dcb8b14ee91a74b21fda99c78071ddedb2dcf0f2b988a66 \
  --expected-target=https://test2.hangar18.dk > /tmp/lego-v0840-report-pending.json

grep -F '"overallStatus": "PENDING"' /tmp/lego-v0840-report-pending.json >/dev/null || { echo 'FAIL: canonical record must report PENDING'; exit 1; }
grep -F '"passed": 0' /tmp/lego-v0840-report-pending.json >/dev/null || { echo 'FAIL: canonical record must start 0/12 PASS'; exit 1; }
grep -F '"readyForI9Test2EvidenceHandoff": false' /tmp/lego-v0840-report-pending.json >/dev/null || { echo 'FAIL: PENDING record must not be handoff-ready'; exit 1; }

if node "$TOOL" "$RECORD" --require-handoff-ready >/dev/null 2>&1; then
  echo 'FAIL: PENDING record must fail --require-handoff-ready'
  exit 1
fi

python3 <<'PY'
import json
src='docs/lego-v0840-manual-acceptance.json'
d=json.load(open(src,encoding='utf-8'))
d['environment'].update({
    'browser':'Chrome 140',
    'os':'Windows 11',
    'desktopViewport':'1920x1080',
    'tabletViewport':'768x1024',
    'mobileViewport':'390x844',
})
for key in d['scenarios']:
    d['scenarios'][key]['status']='PASS'
    d['scenarios'][key]['evidence']=[f'evidence/lego-v0840-{key}.png']
d['overallStatus']='PASS'
json.dump(d,open('/tmp/lego-v0840-pass.json','w',encoding='utf-8'),indent=2)

incomplete=json.loads(json.dumps(d))
incomplete['environment']['mobileViewport']='PENDING'
json.dump(incomplete,open('/tmp/lego-v0840-pass-env-pending.json','w',encoding='utf-8'),indent=2)

critical=json.loads(json.dumps(d))
critical['criticalFlags']['protectedDomainRegression']=True
critical['overallStatus']='FAIL'
json.dump(critical,open('/tmp/lego-v0840-critical.json','w',encoding='utf-8'),indent=2)
PY

node "$TOOL" /tmp/lego-v0840-pass.json --require-handoff-ready > /tmp/lego-v0840-report-pass.json
grep -F '"overallStatus": "PASS"' /tmp/lego-v0840-report-pass.json >/dev/null || { echo 'FAIL: evidenced A-L must report PASS'; exit 1; }
grep -F '"passed": 12' /tmp/lego-v0840-report-pass.json >/dev/null || { echo 'FAIL: evidenced A-L must report 12/12'; exit 1; }
grep -F '"readyForI9Test2EvidenceHandoff": true' /tmp/lego-v0840-report-pass.json >/dev/null || { echo 'FAIL: evidenced A-L with complete environment must be handoff-ready'; exit 1; }
grep -F '"authorizesI9Pass": false' /tmp/lego-v0840-report-pass.json >/dev/null || { echo 'FAIL: report must never authorize I9 PASS'; exit 1; }
grep -F '"authorizesCutover": false' /tmp/lego-v0840-report-pass.json >/dev/null || { echo 'FAIL: report must never authorize cutover'; exit 1; }
grep -F '"executable": false' /tmp/lego-v0840-report-pass.json >/dev/null || { echo 'FAIL: report must remain non-executable'; exit 1; }
grep -F '"publicMutationAvailable": false' /tmp/lego-v0840-report-pass.json >/dev/null || { echo 'FAIL: report must not expose public mutation'; exit 1; }

if node "$TOOL" /tmp/lego-v0840-pass-env-pending.json --require-handoff-ready >/dev/null 2>&1; then
  echo 'FAIL: incomplete environment must block I9 test2 handoff readiness'
  exit 1
fi

node "$TOOL" /tmp/lego-v0840-critical.json > /tmp/lego-v0840-report-critical.json
grep -F '"overallStatus": "FAIL"' /tmp/lego-v0840-report-critical.json >/dev/null || { echo 'FAIL: protected-domain regression must force FAIL'; exit 1; }
grep -F '"readyForI9Test2EvidenceHandoff": false' /tmp/lego-v0840-report-critical.json >/dev/null || { echo 'FAIL: critical FAIL must block handoff'; exit 1; }

for bad in \
  '--expected-sha=1111111111111111111111111111111111111111' \
  '--expected-version=9.9.9' \
  '--expected-package-sha=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' \
  '--expected-target=https://wrong.example.test'; do
  if node "$TOOL" "$RECORD" "$bad" >/dev/null 2>&1; then
    echo "FAIL: mismatch $bad must be rejected"
    exit 1
  fi
done

node "$TOOL" /tmp/lego-v0840-pass.json --markdown > /tmp/lego-v0840-report.md
grep -F 'Ready for I9 test2 evidence handoff: **YES**' /tmp/lego-v0840-report.md >/dev/null || { echo 'FAIL: markdown must show handoff readiness'; exit 1; }
grep -F 'Authorizes I9 PASS: **NO**' /tmp/lego-v0840-report.md >/dev/null || { echo 'FAIL: markdown must keep I9 PASS locked'; exit 1; }
grep -F 'Authorizes cutover: **NO**' /tmp/lego-v0840-report.md >/dev/null || { echo 'FAIL: markdown must keep cutover locked'; exit 1; }

if grep -Ei 'writeFile|appendFile|unlink|rmSync|renameSync|copyFile|child_process|execSync|spawnSync' "$TOOL" >/dev/null; then
  echo 'FAIL: LEGO acceptance report must remain read-only'
  exit 1
fi

echo 'LEGO-043 acceptance report contract: PASS'
