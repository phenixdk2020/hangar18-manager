#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

function die(message) {
  process.stderr.write(`LEGO acceptance report: FAIL — ${message}\n`);
  process.exit(1);
}

function argValue(name) {
  const prefix = `--${name}=`;
  const found = process.argv.find((value) => value.startsWith(prefix));
  return found ? found.slice(prefix.length) : '';
}

function clean(value) {
  return String(value == null ? '' : value).trim();
}

function pending(value) {
  const normalized = clean(value).toUpperCase();
  return !normalized || normalized === 'PENDING' || normalized === 'TODO' || normalized === 'TBD';
}

const recordPath = process.argv[2];
if (!recordPath || recordPath.startsWith('--')) {
  die('usage: lego-acceptance-report.cjs <record.json> [--markdown] [--require-handoff-ready] [--expected-sha=...] [--expected-version=...] [--expected-package-sha=...] [--expected-target=...]');
}
if (!fs.existsSync(recordPath)) die(`missing ${recordPath}`);

let record;
try {
  record = JSON.parse(fs.readFileSync(recordPath, 'utf8'));
} catch (error) {
  die(`invalid JSON: ${error.message}`);
}

if (record.schemaVersion !== '1.0') die('schemaVersion must be 1.0');

const build = record.build || {};
const commitSha = clean(build.commitSha).toLowerCase();
const pluginVersion = clean(build.pluginVersion);
const packageSha256 = clean(build.packageSha256).toLowerCase();
if (!/^[0-9a-f]{40}$/.test(commitSha)) die('build.commitSha must be full git SHA');
if (!/^\d+\.\d+\.\d+$/.test(pluginVersion)) die('build.pluginVersion must be x.y.z');
if (!/^[0-9a-f]{64}$/.test(packageSha256)) die('build.packageSha256 must be SHA-256');

const expectedSha = clean(argValue('expected-sha')).toLowerCase();
const expectedVersion = clean(argValue('expected-version'));
const expectedPackageSha = clean(argValue('expected-package-sha')).toLowerCase();
const expectedTarget = clean(argValue('expected-target')).replace(/\/$/, '');
if (expectedSha && commitSha !== expectedSha) die('build commit does not match expected SHA');
if (expectedVersion && pluginVersion !== expectedVersion) die('plugin version does not match expected version');
if (expectedPackageSha && packageSha256 !== expectedPackageSha) die('package SHA-256 does not match expected value');

const environment = record.environment || {};
const stagingUrl = clean(environment.stagingUrl).replace(/\/$/, '');
if (!/^https?:\/\//i.test(stagingUrl)) die('environment.stagingUrl must be HTTP/HTTPS URL');
if (expectedTarget && stagingUrl !== expectedTarget) die('staging target does not match expected target');
if (!clean(environment.browser)) die('environment.browser is required');
if (!clean(environment.os)) die('environment.os is required');

const scenarioIds = 'ABCDEFGHIJKL'.split('');
const allowed = new Set(['PASS', 'FAIL', 'BLOCKED', 'PENDING']);
const rows = [];
const evidence = [];
for (const id of scenarioIds) {
  const scenario = (record.scenarios || {})[id];
  if (!scenario || typeof scenario !== 'object') die(`scenario ${id} is missing`);
  const status = clean(scenario.status).toUpperCase();
  if (!allowed.has(status)) die(`scenario ${id} has invalid status`);
  if (!Array.isArray(scenario.evidence)) die(`scenario ${id} evidence must be an array`);
  const refs = scenario.evidence.map(clean).filter(Boolean);
  if (status === 'PASS' && refs.length === 0) die(`scenario ${id} PASS requires evidence`);
  refs.forEach((ref) => evidence.push({ scenario: id, ref }));
  rows.push({
    id,
    status,
    note: clean(scenario.note),
    evidenceCount: refs.length,
    evidence: refs,
  });
}

const flags = record.criticalFlags || {};
for (const key of ['consoleError', 'dataLossOrDuplicate', 'protectedDomainRegression']) {
  if (typeof flags[key] !== 'boolean') die(`criticalFlags.${key} must be boolean`);
}

const statuses = rows.map((row) => row.status);
let computedStatus = 'PENDING';
if (statuses.includes('FAIL') || flags.consoleError || flags.dataLossOrDuplicate || flags.protectedDomainRegression) computedStatus = 'FAIL';
else if (statuses.includes('BLOCKED')) computedStatus = 'BLOCKED';
else if (statuses.every((status) => status === 'PASS')) computedStatus = 'PASS';

if (!allowed.has(clean(record.overallStatus).toUpperCase())) die('overallStatus is invalid');
if (clean(record.overallStatus).toUpperCase() !== computedStatus) {
  die(`overallStatus=${record.overallStatus} but computed=${computedStatus}`);
}

const envChecks = {
  browser: !pending(environment.browser),
  os: !pending(environment.os),
  desktopViewport: !pending(environment.desktopViewport),
  tabletViewport: !pending(environment.tabletViewport),
  mobileViewport: !pending(environment.mobileViewport),
};
const environmentComplete = Object.values(envChecks).every(Boolean);
const acceptancePass = computedStatus === 'PASS';
const readyForI9Test2EvidenceHandoff = acceptancePass && environmentComplete;

const blockers = [];
for (const row of rows) {
  if (row.status !== 'PASS') blockers.push(`Scenario ${row.id} is ${row.status}`);
}
for (const [key, complete] of Object.entries(envChecks)) {
  if (!complete) blockers.push(`Environment ${key} is pending`);
}
if (flags.consoleError) blockers.push('Critical console/PHP error flag is set');
if (flags.dataLossOrDuplicate) blockers.push('Critical data loss/duplicate flag is set');
if (flags.protectedDomainRegression) blockers.push('Protected-domain regression flag is set');

const report = {
  schemaVersion: '1.0',
  sourceRecord: path.basename(recordPath),
  validationOk: true,
  build: { commitSha, pluginVersion, packageSha256 },
  environment: {
    stagingUrl,
    browser: clean(environment.browser),
    os: clean(environment.os),
    desktopViewport: clean(environment.desktopViewport),
    tabletViewport: clean(environment.tabletViewport),
    mobileViewport: clean(environment.mobileViewport),
    complete: environmentComplete,
  },
  summary: {
    overallStatus: computedStatus,
    passed: statuses.filter((s) => s === 'PASS').length,
    failed: statuses.filter((s) => s === 'FAIL').length,
    blocked: statuses.filter((s) => s === 'BLOCKED').length,
    pending: statuses.filter((s) => s === 'PENDING').length,
    total: scenarioIds.length,
    evidenceReferences: evidence.length,
  },
  scenarios: rows,
  criticalFlags: {
    consoleError: flags.consoleError,
    dataLossOrDuplicate: flags.dataLossOrDuplicate,
    protectedDomainRegression: flags.protectedDomainRegression,
  },
  blockers,
  readyForI9Test2EvidenceHandoff,
  authorizesI9Pass: false,
  authorizesCutover: false,
  executable: false,
  publicMutationAvailable: false,
  nextAction: readyForI9Test2EvidenceHandoff
    ? 'Attach this evidenced A–L result to the I9 test2LiveE2E gate; complete all remaining I9 gates separately.'
    : 'Complete the listed A–L/environment blockers on test2 and attach concrete evidence before I9 handoff.',
};

function markdown(r) {
  const yesNo = (value) => value ? 'YES' : 'NO';
  const lines = [];
  lines.push('# LEGO manual acceptance report');
  lines.push('');
  lines.push(`- Build: \`${r.build.pluginVersion}\` / \`${r.build.commitSha}\``);
  lines.push(`- Package SHA-256: \`${r.build.packageSha256}\``);
  lines.push(`- Target: \`${r.environment.stagingUrl}\``);
  lines.push(`- Overall A–L status: **${r.summary.overallStatus}**`);
  lines.push(`- Scenarios: ${r.summary.passed}/${r.summary.total} PASS`);
  lines.push(`- Environment complete: **${yesNo(r.environment.complete)}**`);
  lines.push(`- Ready for I9 test2 evidence handoff: **${yesNo(r.readyForI9Test2EvidenceHandoff)}**`);
  lines.push(`- Authorizes I9 PASS: **NO**`);
  lines.push(`- Authorizes cutover: **NO**`);
  lines.push('');
  lines.push('| Scenario | Status | Evidence | Note |');
  lines.push('|---|---|---:|---|');
  for (const row of r.scenarios) {
    lines.push(`| ${row.id} | ${row.status} | ${row.evidenceCount} | ${row.note.replace(/\|/g, '\\|')} |`);
  }
  lines.push('');
  lines.push('## Blockers');
  lines.push('');
  if (r.blockers.length === 0) lines.push('- None for A–L handoff. Remaining I9 gates still apply.');
  else r.blockers.forEach((blocker) => lines.push(`- ${blocker}`));
  lines.push('');
  lines.push('## Next action');
  lines.push('');
  lines.push(r.nextAction);
  return lines.join('\n') + '\n';
}

if (process.argv.includes('--markdown')) process.stdout.write(markdown(report));
else process.stdout.write(JSON.stringify(report, null, 2) + '\n');

if (process.argv.includes('--require-handoff-ready') && !readyForI9Test2EvidenceHandoff) {
  process.exitCode = 2;
}
