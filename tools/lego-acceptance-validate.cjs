#!/usr/bin/env node
'use strict';

const fs = require('fs');

function fail(message) {
  process.stderr.write(`LEGO acceptance validate: FAIL — ${message}\n`);
  process.exit(1);
}

const file = process.argv[2];
const requirePass = process.argv.includes('--require-pass');
const expectedShaArg = process.argv.find((v) => v.startsWith('--expected-sha='));
const expectedVersionArg = process.argv.find((v) => v.startsWith('--expected-version='));
if (!file) fail('usage: lego-acceptance-validate.cjs <record.json> [--require-pass] [--expected-sha=...] [--expected-version=...]');
if (!fs.existsSync(file)) fail(`missing ${file}`);

let record;
try { record = JSON.parse(fs.readFileSync(file, 'utf8')); }
catch (error) { fail(`invalid JSON: ${error.message}`); }

if (record.schemaVersion !== '1.0') fail('schemaVersion must be 1.0');
const build = record.build || {};
const sha = String(build.commitSha || '').toLowerCase();
const version = String(build.pluginVersion || '');
const packageSha = String(build.packageSha256 || '').toLowerCase();
if (!/^[0-9a-f]{40}$/.test(sha)) fail('build.commitSha must be full git SHA');
if (!/^\d+\.\d+\.\d+$/.test(version)) fail('build.pluginVersion must be x.y.z');
if (!/^[0-9a-f]{64}$/.test(packageSha)) fail('build.packageSha256 must be SHA-256');
if (expectedShaArg && sha !== expectedShaArg.split('=')[1].toLowerCase()) fail('build commit does not match expected SHA');
if (expectedVersionArg && version !== expectedVersionArg.split('=')[1]) fail('plugin version does not match expected version');

const environment = record.environment || {};
for (const key of ['stagingUrl','browser','os']) if (!String(environment[key] || '').trim()) fail(`environment.${key} is required`);

const allowed = new Set(['PASS','FAIL','BLOCKED','PENDING']);
const scenarios = record.scenarios || {};
const ids = 'ABCDEFGHIJKL'.split('');
const statuses = [];
for (const id of ids) {
  const scenario = scenarios[id];
  if (!scenario || typeof scenario !== 'object') fail(`scenario ${id} is missing`);
  const status = String(scenario.status || '');
  if (!allowed.has(status)) fail(`scenario ${id} has invalid status`);
  if (!Array.isArray(scenario.evidence)) fail(`scenario ${id} evidence must be an array`);
  if (status === 'PASS' && scenario.evidence.filter((v) => String(v).trim()).length === 0) fail(`scenario ${id} PASS requires evidence`);
  statuses.push(status);
}

const flags = record.criticalFlags || {};
for (const key of ['consoleError','dataLossOrDuplicate','protectedDomainRegression']) {
  if (typeof flags[key] !== 'boolean') fail(`criticalFlags.${key} must be boolean`);
}

let computed = 'PENDING';
if (statuses.includes('FAIL') || flags.consoleError || flags.dataLossOrDuplicate || flags.protectedDomainRegression) computed = 'FAIL';
else if (statuses.includes('BLOCKED')) computed = 'BLOCKED';
else if (statuses.every((s) => s === 'PASS')) computed = 'PASS';

if (!allowed.has(String(record.overallStatus || ''))) fail('overallStatus is invalid');
if (record.overallStatus !== computed) fail(`overallStatus=${record.overallStatus} but computed=${computed}`);
if (requirePass && computed !== 'PASS') fail(`--require-pass requested but overall status is ${computed}`);

process.stdout.write(JSON.stringify({
  ok: true,
  overallStatus: computed,
  commitSha: sha,
  pluginVersion: version,
  passedScenarios: statuses.filter((s) => s === 'PASS').length,
  totalScenarios: ids.length,
  readyForI9EvidenceHandoff: computed === 'PASS'
}, null, 2) + '\n');
