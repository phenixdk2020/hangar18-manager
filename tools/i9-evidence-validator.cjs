#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

const STATUS_VALUES = ['PASS', 'FAIL', 'BLOCKED', 'PENDING'];
const PLACEHOLDER_RE = /(^|\b)(replace-with|todo|tbd|unknown)(\b|$)/i;

function usage() {
  return [
    'Usage:',
    '  node tools/i9-evidence-validator.cjs <manifest.json> [options]',
    '',
    'Options:',
    '  --expected-sha <40-hex>       Require exact build commit SHA',
    '  --expected-version <version>   Require exact plugin version',
    '  --require-pass                 Exit non-zero unless every gate is PASS',
    '  --json                         Emit machine-readable JSON result',
    '  --markdown                     Emit a compact Markdown evidence report',
    '  --schema <path>                Override schema path',
    '  --help                         Show this help',
  ].join('\n');
}

function parseArgs(argv) {
  const out = {
    manifestPath: '',
    schemaPath: path.resolve(__dirname, '..', 'docs', 'i9-evidence-manifest.schema.json'),
    expectedSha: '',
    expectedVersion: '',
    requirePass: false,
    json: false,
    markdown: false,
    help: false,
  };

  const positional = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') out.help = true;
    else if (arg === '--require-pass') out.requirePass = true;
    else if (arg === '--json') out.json = true;
    else if (arg === '--markdown') out.markdown = true;
    else if (arg === '--expected-sha') out.expectedSha = String(argv[++i] || '').trim().toLowerCase();
    else if (arg === '--expected-version') out.expectedVersion = String(argv[++i] || '').trim();
    else if (arg === '--schema') out.schemaPath = path.resolve(String(argv[++i] || ''));
    else if (arg.startsWith('-')) throw new Error(`Unknown option: ${arg}`);
    else positional.push(arg);
  }
  if (positional.length > 1) throw new Error('Only one manifest path may be supplied.');
  out.manifestPath = positional[0] ? path.resolve(positional[0]) : '';
  if (out.json && out.markdown) throw new Error('--json and --markdown are mutually exclusive.');
  return out;
}

function readJson(filePath, label) {
  let raw;
  try {
    raw = fs.readFileSync(filePath, 'utf8');
  } catch (error) {
    throw new Error(`${label} cannot be read: ${error.message}`);
  }
  try {
    return JSON.parse(raw);
  } catch (error) {
    throw new Error(`${label} is not valid JSON: ${error.message}`);
  }
}

function isObject(value) {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

function nonEmptyString(value) {
  return typeof value === 'string' && value.trim() !== '';
}

function uniqueStrings(values) {
  if (!Array.isArray(values)) return false;
  if (values.some((value) => !nonEmptyString(value))) return false;
  return new Set(values).size === values.length;
}

function addUnknownKeyErrors(errors, value, allowed, prefix) {
  if (!isObject(value)) return;
  for (const key of Object.keys(value)) {
    if (!allowed.includes(key)) errors.push(`${prefix}.${key}: unknown property`);
  }
}

function deriveOverallStatus(gates, requiredGates) {
  const statuses = requiredGates.map((gate) => gates[gate]?.status);
  if (statuses.includes('FAIL')) return 'FAIL';
  if (statuses.includes('BLOCKED')) return 'BLOCKED';
  if (statuses.every((status) => status === 'PASS')) return 'PASS';
  return 'PENDING';
}

function validateManifest(manifest, schema, options = {}) {
  const errors = [];
  const warnings = [];
  const requiredGates = Array.isArray(schema?.properties?.gates?.required)
    ? schema.properties.gates.required.slice()
    : [];

  if (!isObject(manifest)) {
    return { ok: false, errors: ['root: expected object'], warnings, requiredGates, derivedStatus: 'PENDING', gateCounts: {} };
  }

  const rootAllowed = Object.keys(schema?.properties || {});
  addUnknownKeyErrors(errors, manifest, rootAllowed, 'root');
  for (const key of schema?.required || []) {
    if (!(key in manifest)) errors.push(`root.${key}: required property missing`);
  }

  if (manifest.schemaVersion !== 1) errors.push('root.schemaVersion: must equal 1');

  const build = manifest.build;
  if (!isObject(build)) errors.push('root.build: expected object');
  else {
    addUnknownKeyErrors(errors, build, ['commitSha', 'pluginVersion', 'testedAt', 'tester'], 'root.build');
    if (!/^[0-9a-fA-F]{40}$/.test(String(build.commitSha || ''))) errors.push('root.build.commitSha: expected 40 hexadecimal characters');
    if (!nonEmptyString(build.pluginVersion)) errors.push('root.build.pluginVersion: non-empty value required');
    if (!nonEmptyString(build.testedAt) || Number.isNaN(Date.parse(build.testedAt))) errors.push('root.build.testedAt: valid ISO date-time required');
    if ('tester' in build && typeof build.tester !== 'string') errors.push('root.build.tester: expected string');

    if (options.expectedSha) {
      if (!/^[0-9a-f]{40}$/.test(options.expectedSha)) errors.push('option --expected-sha: expected 40 hexadecimal characters');
      else if (String(build.commitSha || '').toLowerCase() !== options.expectedSha) errors.push(`root.build.commitSha: expected ${options.expectedSha}`);
    }
    if (options.expectedVersion && String(build.pluginVersion || '') !== options.expectedVersion) {
      errors.push(`root.build.pluginVersion: expected ${options.expectedVersion}`);
    }
  }

  const environment = manifest.environment;
  if (!isObject(environment)) errors.push('root.environment: expected object');
  else {
    addUnknownKeyErrors(errors, environment, ['target', 'wordpressVersion', 'phpVersion', 'backupRestorePointId'], 'root.environment');
    if (!nonEmptyString(environment.target)) errors.push('root.environment.target: non-empty URL required');
    else {
      try {
        const target = new URL(environment.target);
        if (!['http:', 'https:'].includes(target.protocol)) errors.push('root.environment.target: only http/https URLs are allowed');
      } catch (_error) {
        errors.push('root.environment.target: valid URL required');
      }
    }
    if (!nonEmptyString(environment.wordpressVersion)) errors.push('root.environment.wordpressVersion: non-empty value required');
    if (!nonEmptyString(environment.phpVersion)) errors.push('root.environment.phpVersion: non-empty value required');
    if ('backupRestorePointId' in environment && environment.backupRestorePointId !== null && typeof environment.backupRestorePointId !== 'string') {
      errors.push('root.environment.backupRestorePointId: expected string or null');
    }
  }

  const gates = manifest.gates;
  if (!isObject(gates)) errors.push('root.gates: expected object');
  else {
    addUnknownKeyErrors(errors, gates, requiredGates, 'root.gates');
    for (const gate of requiredGates) {
      const result = gates[gate];
      if (!isObject(result)) {
        errors.push(`root.gates.${gate}: required gate object missing`);
        continue;
      }
      addUnknownKeyErrors(errors, result, ['status', 'evidence', 'browserOrTool', 'notes'], `root.gates.${gate}`);
      if (!STATUS_VALUES.includes(result.status)) errors.push(`root.gates.${gate}.status: expected ${STATUS_VALUES.join('|')}`);
      if (!uniqueStrings(result.evidence)) errors.push(`root.gates.${gate}.evidence: expected unique non-empty string array`);
      if (result.status === 'PASS' && (!Array.isArray(result.evidence) || result.evidence.length === 0)) {
        errors.push(`root.gates.${gate}.evidence: PASS requires at least one evidence reference`);
      }
      if ('browserOrTool' in result && typeof result.browserOrTool !== 'string') errors.push(`root.gates.${gate}.browserOrTool: expected string`);
      if ('notes' in result && typeof result.notes !== 'string') errors.push(`root.gates.${gate}.notes: expected string`);
    }
  }

  if (!STATUS_VALUES.includes(manifest.overallStatus)) errors.push(`root.overallStatus: expected ${STATUS_VALUES.join('|')}`);
  if ('notes' in manifest && typeof manifest.notes !== 'string') errors.push('root.notes: expected string');

  const derivedStatus = isObject(gates) ? deriveOverallStatus(gates, requiredGates) : 'PENDING';
  if (STATUS_VALUES.includes(manifest.overallStatus) && manifest.overallStatus !== derivedStatus) {
    errors.push(`root.overallStatus: declared ${manifest.overallStatus}, but gate states derive ${derivedStatus}`);
  }

  if (derivedStatus === 'PASS') {
    const placeholderValues = [
      build?.pluginVersion,
      build?.tester,
      environment?.wordpressVersion,
      environment?.phpVersion,
    ].filter((value) => typeof value === 'string');
    if (/^0{40}$/.test(String(build?.commitSha || ''))) errors.push('root.build.commitSha: all-zero template SHA is not allowed for PASS');
    if (placeholderValues.some((value) => PLACEHOLDER_RE.test(value))) errors.push('PASS manifest still contains template/placeholder values');
  }

  if (options.requirePass && derivedStatus !== 'PASS') errors.push(`--require-pass: manifest derives ${derivedStatus}`);
  if (!nonEmptyString(build?.tester)) warnings.push('root.build.tester: tester identity is recommended for auditability');
  if (!nonEmptyString(environment?.backupRestorePointId)) warnings.push('root.environment.backupRestorePointId: no restore-point reference recorded');

  const gateCounts = STATUS_VALUES.reduce((acc, status) => {
    acc[status] = requiredGates.filter((gate) => gates?.[gate]?.status === status).length;
    return acc;
  }, {});

  return {
    ok: errors.length === 0,
    errors,
    warnings,
    requiredGates,
    derivedStatus,
    declaredStatus: manifest.overallStatus,
    gateCounts,
    build: {
      commitSha: build?.commitSha || '',
      pluginVersion: build?.pluginVersion || '',
      testedAt: build?.testedAt || '',
    },
    environment: {
      target: environment?.target || '',
      wordpressVersion: environment?.wordpressVersion || '',
      phpVersion: environment?.phpVersion || '',
    },
  };
}

function markdownReport(result, manifestPath) {
  const lines = [
    '# I9 Evidence Validation',
    '',
    `- Manifest: \`${manifestPath}\``,
    `- Validation: **${result.ok ? 'PASS' : 'FAIL'}**`,
    `- Derived I9 status: **${result.derivedStatus}**`,
    `- Build SHA: \`${result.build.commitSha || '-'}\``,
    `- Plugin version: \`${result.build.pluginVersion || '-'}\``,
    `- Target: ${result.environment.target || '-'}`,
    '',
    '## Gate summary',
    '',
    '| Status | Count |',
    '|---|---:|',
    ...STATUS_VALUES.map((status) => `| ${status} | ${result.gateCounts[status] || 0} |`),
  ];
  if (result.errors.length) lines.push('', '## Errors', '', ...result.errors.map((error) => `- ${error}`));
  if (result.warnings.length) lines.push('', '## Warnings', '', ...result.warnings.map((warning) => `- ${warning}`));
  return `${lines.join('\n')}\n`;
}

function textReport(result, manifestPath) {
  const lines = [
    `I9 evidence manifest validation: ${result.ok ? 'PASS' : 'FAIL'}`,
    `Manifest: ${manifestPath}`,
    `Derived status: ${result.derivedStatus}`,
    `Gates: PASS=${result.gateCounts.PASS || 0} FAIL=${result.gateCounts.FAIL || 0} BLOCKED=${result.gateCounts.BLOCKED || 0} PENDING=${result.gateCounts.PENDING || 0}`,
  ];
  if (result.errors.length) lines.push('Errors:', ...result.errors.map((error) => `  - ${error}`));
  if (result.warnings.length) lines.push('Warnings:', ...result.warnings.map((warning) => `  - ${warning}`));
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

  let manifest;
  let schema;
  try {
    manifest = readJson(options.manifestPath, 'Manifest');
    schema = readJson(options.schemaPath, 'Schema');
  } catch (error) {
    const result = { ok: false, errors: [error.message], warnings: [], derivedStatus: 'PENDING', declaredStatus: '', gateCounts: {}, build: {}, environment: {} };
    process.stdout.write(options.json ? `${JSON.stringify(result, null, 2)}\n` : textReport(result, options.manifestPath));
    return 1;
  }

  const result = validateManifest(manifest, schema, options);
  if (options.json) process.stdout.write(`${JSON.stringify(result, null, 2)}\n`);
  else if (options.markdown) process.stdout.write(markdownReport(result, options.manifestPath));
  else process.stdout.write(textReport(result, options.manifestPath));
  return result.ok ? 0 : 1;
}

if (require.main === module) process.exitCode = main();

module.exports = {
  STATUS_VALUES,
  deriveOverallStatus,
  markdownReport,
  parseArgs,
  validateManifest,
};
