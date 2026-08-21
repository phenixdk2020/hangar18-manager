#!/usr/bin/env node
'use strict';

const fs = require('fs');

function fail(message) {
  process.stderr.write(`LEGO acceptance record: ${message}\n`);
  process.exit(1);
}

const args = process.argv.slice(2);
if (!args[0]) {
  fail('usage: node tools/lego-acceptance-record.cjs <record.json> (--scenario A --status PASS [--evidence ref ...] [--note text] | --critical-flag consoleError --critical-value true)');
}

const file = args[0];
const getOne = (name) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : undefined;
};
const getMany = (name) => {
  const values = [];
  for (let i = 1; i < args.length; i += 1) {
    if (args[i] === name) {
      if (!args[i + 1]) fail(`${name} requires a value`);
      values.push(args[i + 1]);
      i += 1;
    }
  }
  return values;
};

let record;
try {
  record = JSON.parse(fs.readFileSync(file, 'utf8'));
} catch (error) {
  fail(`cannot read record: ${error.message}`);
}

record = JSON.parse(JSON.stringify(record));
const allowedStatuses = new Set(['PASS', 'FAIL', 'BLOCKED', 'PENDING']);
const scenarioId = getOne('--scenario');
const status = getOne('--status');
const criticalFlag = getOne('--critical-flag');
const criticalValue = getOne('--critical-value');

if (scenarioId && criticalFlag) fail('update exactly one scenario or one critical flag per invocation');
if (!scenarioId && !criticalFlag) fail('either --scenario or --critical-flag is required');

if (scenarioId) {
  if (!/^[A-L]$/.test(scenarioId)) fail('--scenario must be A through L');
  if (!allowedStatuses.has(String(status || ''))) fail('--status must be PASS, FAIL, BLOCKED or PENDING');
  if (!record.scenarios || !record.scenarios[scenarioId]) fail(`scenario ${scenarioId} is missing from record`);

  const evidence = getMany('--evidence').map((value) => String(value).trim()).filter(Boolean);
  const note = getOne('--note');
  if (status === 'PASS' && evidence.length === 0) fail('PASS requires at least one --evidence value');

  record.scenarios[scenarioId].status = status;
  record.scenarios[scenarioId].evidence = evidence;
  if (note !== undefined) record.scenarios[scenarioId].note = note;
} else {
  const allowedFlags = new Set(['consoleError', 'dataLossOrDuplicate', 'protectedDomainRegression']);
  if (!allowedFlags.has(String(criticalFlag || ''))) fail('invalid --critical-flag');
  if (!['true', 'false'].includes(String(criticalValue))) fail('--critical-value must be true or false');
  if (!record.criticalFlags || typeof record.criticalFlags !== 'object') fail('criticalFlags is missing from record');
  record.criticalFlags[criticalFlag] = criticalValue === 'true';
}

const ids = 'ABCDEFGHIJKL'.split('');
const statuses = ids.map((id) => String(record.scenarios?.[id]?.status || 'PENDING'));
const flags = record.criticalFlags || {};
let overall = 'PENDING';
if (statuses.includes('FAIL') || flags.consoleError || flags.dataLossOrDuplicate || flags.protectedDomainRegression) overall = 'FAIL';
else if (statuses.includes('BLOCKED')) overall = 'BLOCKED';
else if (statuses.every((item) => item === 'PASS')) overall = 'PASS';
record.overallStatus = overall;

process.stdout.write(`${JSON.stringify(record, null, 2)}\n`);
