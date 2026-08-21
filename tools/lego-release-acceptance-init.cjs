#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function fail(message) {
  process.stderr.write(`LEGO release acceptance init: FAIL — ${message}\n`);
  process.exit(1);
}

const updatePath = process.argv[2] || 'update.json';
const commitArg = process.argv.find((v) => v.startsWith('--commit-sha='));
const stagingArg = process.argv.find((v) => v.startsWith('--staging-url='));
if (!commitArg) fail('usage: lego-release-acceptance-init.cjs <update.json> --commit-sha=<40-char-sha> [--staging-url=https://test2.hangar18.dk]');

const commitSha = commitArg.split('=')[1].toLowerCase();
if (!/^[0-9a-f]{40}$/.test(commitSha)) fail('commit SHA must be a full 40-character git SHA');
if (!fs.existsSync(updatePath)) fail(`missing ${updatePath}`);

let update;
try { update = JSON.parse(fs.readFileSync(updatePath, 'utf8')); }
catch (error) { fail(`invalid update JSON: ${error.message}`); }

if (update.plugin !== 'hangar18-manager') fail('update manifest plugin must be hangar18-manager');
const version = String(update.version || '');
if (!/^\d+\.\d+\.\d+$/.test(version)) fail('update manifest version must be x.y.z');

const packageRel = String(update.package_path || '');
if (!packageRel || path.isAbsolute(packageRel) || packageRel.split(/[\\/]+/).includes('..')) fail('unsafe or missing package_path');
const packagePath = path.resolve(path.dirname(path.resolve(updatePath)), packageRel);
if (!fs.existsSync(packagePath)) fail(`missing release package ${packageRel}`);

const expectedPackageSha = String(update.package_sha256 || '').toLowerCase();
if (!/^[0-9a-f]{64}$/.test(expectedPackageSha)) fail('update manifest package_sha256 must be SHA-256');
const actualPackageSha = crypto.createHash('sha256').update(fs.readFileSync(packagePath)).digest('hex');
if (actualPackageSha !== expectedPackageSha) fail('release package SHA-256 does not match update manifest');

const stagingUrl = stagingArg ? stagingArg.split('=').slice(1).join('=') : 'https://test2.hangar18.dk';
if (!/^https:\/\//i.test(stagingUrl)) fail('staging URL must use https');

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
  L: 'Vehicle/Event/Gallery regression'
};
const scenarios = {};
for (const id of Object.keys(notes)) scenarios[id] = {status:'PENDING', evidence:[], note:notes[id]};

const record = {
  schemaVersion: '1.0',
  build: {
    commitSha,
    pluginVersion: version,
    packageSha256: actualPackageSha
  },
  environment: {
    stagingUrl,
    browser: 'PENDING',
    os: 'PENDING',
    desktopViewport: 'PENDING',
    tabletViewport: 'PENDING',
    mobileViewport: 'PENDING'
  },
  scenarios,
  criticalFlags: {
    consoleError: false,
    dataLossOrDuplicate: false,
    protectedDomainRegression: false
  },
  overallStatus: 'PENDING',
  notes: `Official release acceptance bootstrap for Hangar18 Manager ${version}; public cutover is not authorized.`
};

process.stdout.write(JSON.stringify(record, null, 2) + '\n');
