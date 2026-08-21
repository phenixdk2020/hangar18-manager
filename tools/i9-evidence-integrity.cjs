#!/usr/bin/env node
'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const { validateManifest } = require('./i9-evidence-validator.cjs');

function usage() {
  return [
    'Usage:',
    '  node tools/i9-evidence-integrity.cjs <manifest.json> [options]',
    '',
    'Options:',
    '  --root <path>                  Repository/evidence root for local references; default cwd',
    '  --expected-sha <40-hex>        Bind manifest to expected build SHA',
    '  --expected-version <version>   Bind manifest to expected plugin version',
    '  --expected-target <url>        Bind manifest to expected staging target',
    '  --require-pass                 Require manifest to derive I9 PASS',
    '  --require-all-local            Reject external/non-local evidence refs',
    '  --markdown                     Emit Markdown instead of JSON',
    '  --schema <path>                Override schema path',
    '  --help                         Show this help',
  ].join('\n');
}

function parseArgs(argv) {
  const out = {
    manifestPath: '',
    root: process.cwd(),
    schemaPath: path.resolve(__dirname, '..', 'docs', 'i9-evidence-manifest.schema.json'),
    expectedSha: '', expectedVersion: '', expectedTarget: '', requirePass: false,
    requireAllLocal: false, markdown: false, help: false,
  };
  const positional = [];
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') out.help = true;
    else if (arg === '--require-pass') out.requirePass = true;
    else if (arg === '--require-all-local') out.requireAllLocal = true;
    else if (arg === '--markdown') out.markdown = true;
    else if (arg === '--root') out.root = path.resolve(String(argv[++i] || ''));
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

function sha256File(filePath) {
  const hash = crypto.createHash('sha256');
  hash.update(fs.readFileSync(filePath));
  return hash.digest('hex');
}

function isExternalReference(ref) {
  return /^[a-z][a-z0-9+.-]*:/i.test(ref);
}

function resolveContained(root, ref) {
  if (path.isAbsolute(ref)) return null;
  const normalized = ref.replace(/\\/g, '/');
  if (normalized.split('/').includes('..')) return null;
  const rootResolved = path.resolve(root);
  const candidate = path.resolve(rootResolved, ref);
  const rel = path.relative(rootResolved, candidate);
  if (rel === '' || (!rel.startsWith(`..${path.sep}`) && rel !== '..' && !path.isAbsolute(rel))) return candidate;
  return null;
}

function buildIntegrityIndex(manifest, manifestPath, schema, options) {
  const validation = validateManifest(manifest, schema, {
    expectedSha: options.expectedSha,
    expectedVersion: options.expectedVersion,
    expectedTarget: options.expectedTarget,
    requirePass: options.requirePass,
  });
  const errors = validation.errors.slice();
  const entries = [];

  for (const gateName of validation.requiredGates || []) {
    const gate = manifest?.gates?.[gateName];
    for (const ref of Array.isArray(gate?.evidence) ? gate.evidence : []) {
      if (isExternalReference(ref)) {
        entries.push({ gate: gateName, reference: ref, kind: 'external', verified: false, sha256: null, bytes: null });
        if (options.requireAllLocal) errors.push(`gate ${gateName}: external evidence is not allowed in --require-all-local mode: ${ref}`);
        continue;
      }

      const localPath = resolveContained(options.root, ref);
      if (!localPath) {
        entries.push({ gate: gateName, reference: ref, kind: 'invalid-local-path', verified: false, sha256: null, bytes: null });
        errors.push(`gate ${gateName}: local evidence path escapes root or is absolute: ${ref}`);
        continue;
      }

      let stat;
      try {
        stat = fs.statSync(localPath);
      } catch (_error) {
        entries.push({ gate: gateName, reference: ref, kind: 'local', verified: false, sha256: null, bytes: null });
        errors.push(`gate ${gateName}: local evidence file is missing: ${ref}`);
        continue;
      }
      if (!stat.isFile()) {
        entries.push({ gate: gateName, reference: ref, kind: 'local', verified: false, sha256: null, bytes: null });
        errors.push(`gate ${gateName}: local evidence reference is not a file: ${ref}`);
        continue;
      }

      entries.push({
        gate: gateName,
        reference: ref,
        kind: 'local',
        verified: true,
        sha256: sha256File(localPath),
        bytes: stat.size,
      });
    }
  }

  const localVerified = entries.filter((entry) => entry.kind === 'local' && entry.verified).length;
  const external = entries.filter((entry) => entry.kind === 'external').length;
  const unresolved = entries.length - localVerified - external;
  const manifestStat = fs.statSync(manifestPath);

  return {
    schemaVersion: 1,
    ok: errors.length === 0,
    generatedAt: new Date().toISOString(),
    root: path.resolve(options.root),
    manifest: {
      path: manifestPath,
      sha256: sha256File(manifestPath),
      bytes: manifestStat.size,
      buildSha: manifest?.build?.commitSha || '',
      pluginVersion: manifest?.build?.pluginVersion || '',
      target: manifest?.environment?.target || '',
      derivedStatus: validation.derivedStatus,
    },
    summary: { references: entries.length, localVerified, external, unresolved },
    entries,
    errors,
    warnings: validation.warnings || [],
  };
}

function markdown(index) {
  const lines = [
    '# I9 Evidence Integrity', '',
    `- Result: **${index.ok ? 'PASS' : 'FAIL'}**`,
    `- Manifest SHA-256: \`${index.manifest.sha256}\``,
    `- Build SHA: \`${index.manifest.buildSha || '-'}\``,
    `- Plugin version: \`${index.manifest.pluginVersion || '-'}\``,
    `- Target: ${index.manifest.target || '-'}`,
    `- Derived I9 status: **${index.manifest.derivedStatus}**`,
    `- References: ${index.summary.references} (${index.summary.localVerified} local verified, ${index.summary.external} external, ${index.summary.unresolved} unresolved)`,
    '', '## Evidence', '',
    '| Gate | Reference | Kind | Verified | SHA-256 | Bytes |',
    '|---|---|---|---:|---|---:|',
  ];
  for (const entry of index.entries) {
    const safeRef = String(entry.reference).replace(/\|/g, '\\|');
    lines.push(`| ${entry.gate} | ${safeRef} | ${entry.kind} | ${entry.verified ? 'yes' : 'no'} | ${entry.sha256 || '-'} | ${entry.bytes ?? '-'} |`);
  }
  if (index.errors.length) lines.push('', '## Errors', '', ...index.errors.map((error) => `- ${error}`));
  if (index.warnings.length) lines.push('', '## Warnings', '', ...index.warnings.map((warning) => `- ${warning}`));
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
    const index = buildIntegrityIndex(manifest, options.manifestPath, schema, options);
    process.stdout.write(options.markdown ? markdown(index) : `${JSON.stringify(index, null, 2)}\n`);
    return index.ok ? 0 : 1;
  } catch (error) {
    process.stderr.write(`${error.message}\n`);
    return 1;
  }
}

if (require.main === module) process.exitCode = main();
module.exports = { buildIntegrityIndex, isExternalReference, markdown, parseArgs, resolveContained, sha256File };
