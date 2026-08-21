#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

function usage() {
  return [
    'Usage:',
    '  node tools/i9-evidence-init.cjs --sha <40-hex> --version <plugin> --wordpress-version <wp> --php-version <php> --tester <name> [options]',
    '',
    'Options:',
    "  --target <url>                 Default: https://test2.hangar18.dk/",
    '  --backup-restore-point <id>    Optional restore-point reference',
    '  --output <path>                Write JSON to file instead of stdout',
    '  --force                        Allow replacing an existing output file',
    '  --template <path>              Override manifest template path',
    '  --help                         Show this help',
  ].join('\n');
}

function parseArgs(argv) {
  const out = {
    sha: '', version: '', wordpressVersion: '', phpVersion: '', tester: '',
    target: 'https://test2.hangar18.dk/', backupRestorePointId: null,
    output: '', force: false, help: false,
    template: path.resolve(__dirname, '..', 'docs', 'i9-evidence-manifest.example.json'),
  };
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') out.help = true;
    else if (arg === '--force') out.force = true;
    else if (arg === '--sha') out.sha = String(argv[++i] || '').trim().toLowerCase();
    else if (arg === '--version') out.version = String(argv[++i] || '').trim();
    else if (arg === '--wordpress-version') out.wordpressVersion = String(argv[++i] || '').trim();
    else if (arg === '--php-version') out.phpVersion = String(argv[++i] || '').trim();
    else if (arg === '--tester') out.tester = String(argv[++i] || '').trim();
    else if (arg === '--target') out.target = String(argv[++i] || '').trim();
    else if (arg === '--backup-restore-point') out.backupRestorePointId = String(argv[++i] || '').trim() || null;
    else if (arg === '--output') out.output = path.resolve(String(argv[++i] || ''));
    else if (arg === '--template') out.template = path.resolve(String(argv[++i] || ''));
    else throw new Error(`Unknown option: ${arg}`);
  }
  return out;
}

function validateOptions(options) {
  const errors = [];
  if (!/^[0-9a-f]{40}$/.test(options.sha)) errors.push('--sha must be exactly 40 hexadecimal characters');
  if (/^0{40}$/.test(options.sha)) errors.push('--sha must not use the all-zero template SHA');
  for (const [name, value] of [
    ['--version', options.version],
    ['--wordpress-version', options.wordpressVersion],
    ['--php-version', options.phpVersion],
    ['--tester', options.tester],
  ]) {
    if (!value) errors.push(`${name} is required`);
  }
  try {
    const target = new URL(options.target);
    if (!['http:', 'https:'].includes(target.protocol)) errors.push('--target must use http or https');
  } catch (_error) {
    errors.push('--target must be a valid URL');
  }
  return errors;
}

function createManifest(template, options) {
  const manifest = JSON.parse(JSON.stringify(template));
  manifest.schemaVersion = 1;
  manifest.build = {
    commitSha: options.sha,
    pluginVersion: options.version,
    testedAt: new Date().toISOString(),
    tester: options.tester,
  };
  manifest.environment = {
    target: options.target,
    wordpressVersion: options.wordpressVersion,
    phpVersion: options.phpVersion,
    backupRestorePointId: options.backupRestorePointId,
  };
  for (const gate of Object.keys(manifest.gates || {})) {
    manifest.gates[gate] = { status: 'PENDING', evidence: [] };
  }
  manifest.overallStatus = 'PENDING';
  manifest.notes = 'Initialized for I9 evidence collection. Every mandatory gate must be evidenced before PASS.';
  return manifest;
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

  const errors = validateOptions(options);
  if (errors.length) {
    process.stderr.write(`${errors.join('\n')}\n\n${usage()}\n`);
    return 2;
  }

  let template;
  try {
    template = JSON.parse(fs.readFileSync(options.template, 'utf8'));
  } catch (error) {
    process.stderr.write(`Template cannot be read: ${error.message}\n`);
    return 1;
  }

  const manifest = createManifest(template, options);
  const json = `${JSON.stringify(manifest, null, 2)}\n`;
  if (!options.output) {
    process.stdout.write(json);
    return 0;
  }
  if (fs.existsSync(options.output) && !options.force) {
    process.stderr.write(`Output already exists: ${options.output}. Use --force to replace it.\n`);
    return 1;
  }
  fs.mkdirSync(path.dirname(options.output), { recursive: true });
  fs.writeFileSync(options.output, json, 'utf8');
  process.stdout.write(`Created pending I9 evidence manifest: ${options.output}\n`);
  return 0;
}

if (require.main === module) process.exitCode = main();

module.exports = { createManifest, parseArgs, validateOptions };
