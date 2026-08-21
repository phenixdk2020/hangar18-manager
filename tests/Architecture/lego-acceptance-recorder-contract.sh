#!/usr/bin/env bash
set -euo pipefail

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cp docs/lego-manual-acceptance.example.json "$TMP/record.json"

node tools/lego-acceptance-record.cjs "$TMP/record.json" \
  --scenario A --status PASS --evidence evidence/A.png --note "A ok" > "$TMP/a.json"
node tools/lego-acceptance-validate.cjs "$TMP/a.json" >/dev/null

node - "$TMP/a.json" <<'NODE'
const fs=require('fs');
const r=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
if(r.scenarios.A.status !== 'PASS') throw new Error('scenario A not PASS');
if(r.scenarios.A.evidence[0] !== 'evidence/A.png') throw new Error('scenario A evidence missing');
if(r.scenarios.A.note !== 'A ok') throw new Error('scenario A note missing');
if(r.overallStatus !== 'PENDING') throw new Error('overall must remain PENDING until all A-L pass');
NODE

if node tools/lego-acceptance-record.cjs "$TMP/record.json" --scenario B --status PASS >/dev/null 2>&1; then
  echo "PASS without evidence must fail" >&2
  exit 1
fi

node tools/lego-acceptance-record.cjs "$TMP/a.json" \
  --critical-flag consoleError --critical-value true > "$TMP/critical.json"
node tools/lego-acceptance-validate.cjs "$TMP/critical.json" >/dev/null
node - "$TMP/critical.json" <<'NODE'
const fs=require('fs');
const r=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
if(r.criticalFlags.consoleError !== true) throw new Error('critical flag not set');
if(r.overallStatus !== 'FAIL') throw new Error('critical flag must force FAIL');
NODE

node tools/lego-acceptance-record.cjs "$TMP/critical.json" \
  --critical-flag consoleError --critical-value false > "$TMP/cleared.json"
node tools/lego-acceptance-validate.cjs "$TMP/cleared.json" >/dev/null
node - "$TMP/cleared.json" <<'NODE'
const fs=require('fs');
const r=JSON.parse(fs.readFileSync(process.argv[2],'utf8'));
if(r.criticalFlags.consoleError !== false) throw new Error('critical flag not cleared');
if(r.overallStatus !== 'PENDING') throw new Error('overall must recompute after flag clear');
NODE

if node tools/lego-acceptance-record.cjs "$TMP/record.json" --scenario Z --status FAIL >/dev/null 2>&1; then
  echo "Invalid scenario must fail" >&2
  exit 1
fi
if node tools/lego-acceptance-record.cjs "$TMP/record.json" --critical-flag nope --critical-value true >/dev/null 2>&1; then
  echo "Invalid critical flag must fail" >&2
  exit 1
fi

grep -F 'process.stdout.write' tools/lego-acceptance-record.cjs >/dev/null
! grep -Eq 'writeFile|appendFile|renameSync|unlinkSync|rmSync' tools/lego-acceptance-record.cjs

echo "LEGO acceptance recorder contract: PASS"
