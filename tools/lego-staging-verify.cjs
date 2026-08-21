#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

function fail(message) {
  process.stderr.write(`LEGO staging verify: FAIL — ${message}\n`);
  process.exit(1);
}

const root = path.resolve(process.argv[2] || 'staging-dist');
const manifestPath = path.join(root, 'lego-staging-manifest.json');
const buildPath = path.join(root, 'TEST-BUILD.txt');

if (!fs.existsSync(manifestPath)) fail('missing lego-staging-manifest.json');
if (!fs.existsSync(buildPath)) fail('missing TEST-BUILD.txt');

let manifest;
try {
  manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
} catch (error) {
  fail(`invalid manifest JSON: ${error.message}`);
}

if (manifest.schemaVersion !== '1.0') fail('unexpected manifest schemaVersion');
if (manifest.purpose !== 'lego-staging-manual-acceptance') fail('unexpected manifest purpose');
if (manifest.officialRelease !== false) fail('artifact must not be marked as official release');
if (manifest.publicCutoverAuthorized !== false) fail('artifact must not authorize public cutover');

const sha = String(manifest.commitSha || '').trim().toLowerCase();
const version = String(manifest.pluginVersion || '').trim();
const packageName = String(manifest.package || '').trim();
const expectedPackageSha = String(manifest.packageSha256 || '').trim().toLowerCase();

if (!/^[0-9a-f]{40}$/.test(sha)) fail('commitSha must be a full 40-char git SHA');
if (!/^\d+\.\d+\.\d+$/.test(version)) fail('pluginVersion must be semantic x.y.z');
if (!/^hangar18-manager-lego-staging\.zip$/.test(packageName)) fail('unexpected package filename');
if (!/^[0-9a-f]{64}$/.test(expectedPackageSha)) fail('packageSha256 must be SHA-256 hex');

const packagePath = path.join(root, packageName);
if (!fs.existsSync(packagePath)) fail(`missing ${packageName}`);
const actualPackageSha = crypto.createHash('sha256').update(fs.readFileSync(packagePath)).digest('hex');
if (actualPackageSha !== expectedPackageSha) fail('package SHA-256 does not match manifest');

const buildText = fs.readFileSync(buildPath, 'utf8');
if (!buildText.includes(`Build commit: ${sha}`)) fail('TEST-BUILD.txt commit does not match manifest');
if (!buildText.includes(`Plugin version: ${version}`)) fail('TEST-BUILD.txt version does not match manifest');
if (!buildText.includes('Official release: NO')) fail('TEST-BUILD.txt must identify non-release build');
if (!buildText.includes('Public cutover authorized: NO')) fail('TEST-BUILD.txt must deny cutover authorization');

const sumsPath = path.join(root, 'SHA256SUMS.txt');
if (!fs.existsSync(sumsPath)) fail('missing SHA256SUMS.txt');
const sums = fs.readFileSync(sumsPath, 'utf8');
if (!sums.includes(actualPackageSha) || !sums.includes(packageName)) fail('SHA256SUMS.txt does not bind package hash/name');

process.stdout.write(JSON.stringify({
  ok: true,
  commitSha: sha,
  pluginVersion: version,
  package: packageName,
  packageSha256: actualPackageSha,
  officialRelease: false,
  publicCutoverAuthorized: false
}, null, 2) + '\n');
