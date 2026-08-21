#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { validateManifest } = require('./i9-evidence-validator.cjs');

const ACTIONS = {
  chrome: 'Run the Chrome brand/manual flow and attach concrete evidence.',
  edge: 'Run the Edge brand/manual flow and attach concrete evidence.',
  firefox: 'Run the Firefox brand/manual flow and attach concrete evidence.',
  safari: 'Run the Safari brand/manual flow and attach concrete evidence.',
  screenReader: 'Run the required screen-reader core flow and attach notes/evidence.',
  test2LiveE2E: 'Run the authenticated test2 editor/live E2E checklist and attach evidence.',
  protectedDomains: 'Verify Vehicle/Event/Gallery visual and functional parity and attach evidence.',
  rollback: 'Run the staging/live-copy rollback rehearsal and attach restore evidence.',
};

function usage() {
  return [
    'Usage:',
    '  node tools/i9-evidence-readiness.cjs <manifest.json> [options]',
    '',
    'Options:',
    '  --expected-sha <40-hex>        Bind manifest to expected build SHA',
    '  --expected-version <version>   Bind manifest to expected plugin version',
    '  --expected-target <url>        Bind manifest to expected staging target',
    '  --markdown                     Emit Markdown instead of JSON',
    '  --schema <path>                Override schema path',
    '  --help                         Show this help',
  ].join('\n');
}

function parseArgs(argv) {
  const out = {
    manifestPath: '',
    schemaPath: path.resolve(__dirname, '..', 'docs', 'i9-evidence-manifest.schema.json'),
    expectedSha: '', expectedVersion: '', expectedTarget: '', markdown: false, help: false,
  };
  const positional = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') out.help = true;
    else if (arg === '--markdown') out.markdown = true;
    else if (arg === '--schema') out.schemaPath = path.resolve(String(argv[++i] || ''));
    else if (arg === '--expected-sha') out.expectedSha = String(argv[++i] || '').trim().toLowerCase();
    else if (arg === '--expected-version') out.expectedVersion = String(argv[++i] || '').trim();
    else if (arg === '--expected-target') out.expectedTarget = String(argv[++i] || '').trim();
    else if (arg.startsWith('-')) throw new Error(`Unknown option: ${arg}`);
    else positional.push(arg);
  }
  if (positional.length > 1) throw new Error('Only one manifest path may be supplied.');
  out.manifestPath = positional[0] ? path.resolve(positional[0]) : '';
  return out;
}

function readJson(filePath, label) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf8'));
  } catch (error) {
    throw new Error(`${label} cannot be read as JSON: ${error.message}`);
  }
}

function readiness(manifest, schema, options) {
  const validation = validateManifest(manifest, schema, {
    expectedSha: options.expectedSha,
    expectedVersion: options.expectedVersion,
    expectedTarget: options.expectedTarget,
  });
  const gates = [];
  for (const name of validation.requiredGates || []) {
    const gate = manifest?.gates?.[name] || {};
    const evidenceCount = Array.isArray(gate.evidence) ? gate.evidence.length : 0;
    const status = String(gate.status || 'PENDING');
    const complete = status === 'PASS' && evidenceCount > 0;
    let blocker = '';
    if (status === 'FAIL') blocker = 'gate-failed';
    else if (status === 'BLOCKED') blocker = 'gate-blocked';
    else if (status !== 'PASS') blocker = 'gate-pending';
    else if (evidenceCount === 0) blocker = 'pass-evidence-missing';

    gates.push({
      gate: name,
      status,
      evidenceCount,
      complete,
      blocker,
      nextAction: complete ? 'No action required for this gate.' : (ACTIONS[name] || 'Complete this manual/live gate and attach evidence.'),
    });
  }

  const incomplete = gates.filter((gate) => !gate.complete);
  return {
    schemaVersion: 1,
    validationOk: validation.ok,
    derivedStatus: validation.derivedStatus,
    readyForI10: validation.ok && validation.derivedStatus === 'PASS' && incomplete.length === 0,
    build: validation.build,
    environment: validation.environment,
    summary: {
      required: gates.length,
      complete: gates.length - incomplete.length,
      incomplete: incomplete.length,
      failed: gates.filter((gate) => gate.status === 'FAIL').length,
      blocked: gates.filter((gate) => gate.status === 'BLOCKED').length,
      pending: gates.filter((gate) => gate.status === 'PENDING').length,
    },
    gates,
    validationErrors: validation.errors,
    warnings: validation.warnings,
  };
}

function markdown(report) {
  const lines = [
    '# I9 Evidence Readiness', '',
    `- Manifest validation: **${report.validationOk ? 'PASS' : 'FAIL'}**`,
    `- Derived I9 status: **${report.derivedStatus}**`,
    `- Ready for I10: **${report.readyForI10 ? 'YES' : 'NO'}**`,
    `- Complete gates: ${report.summary.complete}/${report.summary.required}`,
    '',
    '| Gate | Status | Evidence | Blocker | Next action |',
    '|---|---|---:|---|---|',
  ];
  for (const gate of report.gates) {
    const action = gate.nextAction.replace(/\|/g, '\\|');
    lines.push(`| ${gate.gate} | ${gate.status} | ${gate.evidenceCount} | ${gate.blocker || '-'} | ${action} |`);
  }
  if (report.validationErrors.length) lines.push('', '## Validation errors', '', ...report.validationErrors.map((error) => `- ${error}`));
  if (report.warnings.length) lines.push('', '## Warnings', '', ...report.warnings.map((warning) => `- ${warning}`));
  return `${lines.join('\n')}\n`;
}

function main(argv = process.argv.slice(2)) {
  let options;
  try {
    options = parseArgs(argv);
  } catch (error) {
    process.stderr.write(`${error.message}\n\n${usage()}\n`);
    return 2;
  }
  if (options.help) {
    process.stdout.write(`${usage()}\n`);
    return 0;
  }
  if (!options.manifestPath) {
    process.stderr.write(`${usage()}\n`);
    return 2;
  }

  try {
    const manifest = readJson(options.manifestPath, 'Manifest');
    const schema = readJson(options.schemaPath, 'Schema');
    const report = readiness(manifest, schema, options);
    process.stdout.write(options.markdown ? markdown(report) : `${JSON.stringify(report, null, 2)}\n`);
    return report.validationOk ? 0 : 1;
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    return 1;
  }
}

if (require.main === module) process.exitCode = main();
module.exports = { ACTIONS, markdown, parseArgs, readiness };
