#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const { STATUS_VALUES, deriveOverallStatus, validateManifest } = require('./i9-evidence-validator.cjs');

function usage() {
  return [
    'Usage:',
    '  node tools/i9-evidence-record.cjs <manifest.json> --gate <name> --status <status> [options]',
    '',
    'The tool never edits the source manifest. The updated manifest is written to stdout.',
    '',
    'Options:',
    '  --evidence <ref>               Append evidence reference; repeatable',
    '  --clear-evidence                Clear existing evidence before appending',
    '  --browser-or-tool <value>       Record browser/tool used for this gate',
    '  --notes <text>                  Replace gate notes',
    '  --schema <path>                 Override schema path',
    '  --help                          Show this help',
  ].join('\n');
}

function parseArgs(argv) {
  const out = {
    manifestPath: '', gate: '', status: '', evidence: [], clearEvidence: false,
    browserOrTool: null, notes: null, help: false,
    schemaPath: path.resolve(__dirname, '..', 'docs', 'i9-evidence-manifest.schema.json'),
  };
  const positional = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') out.help = true;
    else if (arg === '--clear-evidence') out.clearEvidence = true;
    else if (arg === '--gate') out.gate = String(argv[++i] || '').trim();
    else if (arg === '--status') out.status = String(argv[++i] || '').trim().toUpperCase();
    else if (arg === '--evidence') out.evidence.push(String(argv[++i] || '').trim());
    else if (arg === '--browser-or-tool') out.browserOrTool = String(argv[++i] || '').trim();
    else if (arg === '--notes') out.notes = String(argv[++i] || '');
    else if (arg === '--schema') out.schemaPath = path.resolve(String(argv[++i] || ''));
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

function recordGate(manifest, schema, options) {
  const before = validateManifest(manifest, schema, {});
  if (!before.ok) throw new Error(`Manifest is invalid before update:\n${before.errors.map((e) => `- ${e}`).join('\n')}`);

  const requiredGates = Array.isArray(schema?.properties?.gates?.required) ? schema.properties.gates.required.slice() : [];
  if (!requiredGates.includes(options.gate)) throw new Error(`Unknown I9 gate: ${options.gate}`);
  if (!STATUS_VALUES.includes(options.status)) throw new Error(`Invalid status: ${options.status}. Expected ${STATUS_VALUES.join('|')}`);
  if (options.evidence.some((ref) => !ref)) throw new Error('Evidence references must not be empty.');

  const next = JSON.parse(JSON.stringify(manifest));
  const gate = next.gates[options.gate];
  const existing = options.clearEvidence ? [] : Array.isArray(gate.evidence) ? gate.evidence.slice() : [];
  gate.evidence = Array.from(new Set([...existing, ...options.evidence]));
  gate.status = options.status;

  if (options.browserOrTool !== null) {
    if (options.browserOrTool) gate.browserOrTool = options.browserOrTool;
    else delete gate.browserOrTool;
  }
  if (options.notes !== null) {
    if (options.notes) gate.notes = options.notes;
    else delete gate.notes;
  }
  if (gate.status === 'PASS' && gate.evidence.length === 0) throw new Error(`Gate ${options.gate}: PASS requires at least one evidence reference.`);

  next.overallStatus = deriveOverallStatus(next.gates, requiredGates);
  const after = validateManifest(next, schema, {});
  if (!after.ok) throw new Error(`Updated manifest would be invalid:\n${after.errors.map((e) => `- ${e}`).join('\n')}`);
  return next;
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
  if (!options.manifestPath || !options.gate || !options.status) {
    process.stderr.write(`${usage()}\n`);
    return 2;
  }

  try {
    const manifest = readJson(options.manifestPath, 'Manifest');
    const schema = readJson(options.schemaPath, 'Schema');
    const next = recordGate(manifest, schema, options);
    process.stdout.write(`${JSON.stringify(next, null, 2)}\n`);
    return 0;
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    return 1;
  }
}

if (require.main === module) process.exitCode = main();
module.exports = { parseArgs, recordGate };
