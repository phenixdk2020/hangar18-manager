#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');

function fail(message) {
  process.stderr.write(`LEGO acceptance init: ${message}\n`);
  process.exit(1);
}

const args = process.argv.slice(2);
if (args.length < 1) {
  fail('usage: node tools/lego-acceptance-init.cjs <staging-manifest.json> [--staging-url <url>]');
}

const manifestPath = path.resolve(args[0]);
let stagingUrl = 'https://test2.hangar18.dk';
for (let i = 1; i < args.length; i += 1) {
  if (args[i] === '--staging-url') {
    if (!args[i + 1]) fail('--staging-url requires a value');
    stagingUrl = args[i + 1];
    i += 1;
  } else {
    fail(`unknown argument: ${args[i]}`);
  }
}

let manifest;
try {
  manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
} catch (error) {
  fail(`cannot read manifest: ${error.message}`);
}

const sha = String(manifest.commitSha || '');
const version = String(manifest.pluginVersion || '');
const packageSha256 = String(manifest.packageSha256 || '');
if (!/^[0-9a-f]{40}$/i.test(sha)) fail('manifest commitSha must be a 40-character hex SHA');
if (!version) fail('manifest pluginVersion is required');
if (!/^[0-9a-f]{64}$/i.test(packageSha256)) fail('manifest packageSha256 must be a 64-character hex SHA-256');
if (manifest.officialRelease !== false) fail('manifest must explicitly declare officialRelease=false');
if (manifest.publicCutoverAuthorized !== false) fail('manifest must explicitly declare publicCutoverAuthorized=false');

const notes = {
  A: 'Elementbibliotek og drop',
  B: 'Kasse og nesting',
  C: 'Side-by-side',
  D: 'Desktop resize',
  E: 'Tablet/Mobil overrides',
  F: 'Design og spacing',
  G: 'Foldbare paneler',
  H: 'Undo/Redo',
  I: 'Save/reload persistence',
  J: 'Preview',
  K: 'Backup/restore',
  L: 'Vehicle/Event/Gallery regression',
};

const scenarios = {};
for (const [id, note] of Object.entries(notes)) {
  scenarios[id] = { status: 'PENDING', evidence: [], note };
}

const record = {
  schemaVersion: '1.0',
  build: {
    commitSha: sha.toLowerCase(),
    pluginVersion: version,
    packageSha256: packageSha256.toLowerCase(),
  },
  environment: {
    stagingUrl,
    browser: 'PENDING',
    os: 'PENDING',
    desktopViewport: 'PENDING',
    tabletViewport: 'PENDING',
    mobileViewport: 'PENDING',
  },
  scenarios,
  criticalFlags: {
    consoleError: false,
    dataLossOrDuplicate: false,
    protectedDomainRegression: false,
  },
  overallStatus: 'PENDING',
  notes: `Bootstrap fra ${path.basename(manifestPath)}. Manuel evidence kræves; denne fil må ikke betragtes som PASS.`,
};

process.stdout.write(`${JSON.stringify(record, null, 2)}\n`);
