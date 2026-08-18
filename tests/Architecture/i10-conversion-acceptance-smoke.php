<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceChecklist;
use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceValidator;
use RuntimeException;

function i10AcceptanceAssert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$checklist = new ConversionAcceptanceChecklist();
$validator = new ConversionAcceptanceValidator($checklist);
$required = $checklist->required();
i10AcceptanceAssert(count($required) === 7, 'I10 acceptance must require seven page-specific checks.');

$hashA = str_repeat('a', 64);
$hashB = str_repeat('b', 64);
$allPass = array_fill_keys(array_keys($required), true);

$malicious = $validator->normalize('hjem-gammel', $hashA, [
    'Checks' => [],
    'Environment' => 'Chrome / desktop',
    'EvidenceRef' => 'evidence://attempt',
    'ConfirmedManual' => false,
    'AcceptedForSequence' => true,
], 7);
i10AcceptanceAssert(empty($malicious['AcceptedForSequence']), 'Caller-supplied AcceptedForSequence must never bypass derived manual acceptance.');
i10AcceptanceAssert(!$validator->isAccepted($malicious, $hashA), 'Incomplete evidence must not be accepted.');

$valid = $validator->normalize('hjem-gammel', $hashA, [
    'Checks' => $allPass,
    'Environment' => 'Chrome desktop + responsive device checks',
    'EvidenceRef' => 'qa://comparison/hjem-gammel/001',
    'Notes' => 'Manual comparison and rollback verified.',
    'ConfirmedManual' => true,
], 42);
i10AcceptanceAssert(!empty($valid['AcceptedForSequence']), 'Complete manually confirmed evidence must be accepted for sequence.');
i10AcceptanceAssert($validator->isAccepted($valid, $hashA), 'Acceptance must be valid for the exact shadow source hash.');
i10AcceptanceAssert(!$validator->isAccepted($valid, $hashB), 'Rebuilt/different shadow hash must invalidate prior acceptance.');
i10AcceptanceAssert(in_array('acceptance-source-hash-stale', $validator->blockers($valid, $hashB), true), 'Stale hash must be visible as a blocker.');

$oneMissing = $allPass;
$oneMissing['rollback-flow'] = false;
$incomplete = $validator->normalize('hjem-gammel', $hashA, [
    'Checks' => $oneMissing,
    'Environment' => 'Chrome desktop + responsive device checks',
    'EvidenceRef' => 'qa://comparison/hjem-gammel/002',
    'ConfirmedManual' => true,
], 42);
i10AcceptanceAssert(!$validator->isAccepted($incomplete, $hashA), 'Missing rollback evidence must block sequence acceptance.');
i10AcceptanceAssert(in_array('acceptance-check:rollback-flow', $validator->blockers($incomplete, $hashA), true), 'Missing rollback check must be named in blockers.');

fwrite(STDOUT, "I10 conversion acceptance ledger v0.8.4: PASS\n");
