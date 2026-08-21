<?php

declare(strict_types=1);

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketFingerprintService;

function i10FingerprintAssert(bool $condition,string $message): void
{
    if(!$condition){throw new RuntimeException($message);}
}

$packet=[
    'SchemaVersion'=>'1.0',
    'Mode'=>'decision-packet-only',
    'ComparisonSlug'=>'om-foreningen-editor-test',
    'Stages'=>[
        ['Stage'=>1,'Slug'=>'om-foreningen-editor-test','EligibleForOperatorReview'=>true,'Blockers'=>[]],
        ['Stage'=>2,'Slug'=>'hjem','EligibleForOperatorReview'=>false,'Blockers'=>['decision-input-missing']],
    ],
    'Executable'=>false,
    'PublicMutationAvailable'=>false,
];

$service=new ConversionDecisionPacketFingerprintService();
$fingerprint=$service->fingerprint($packet);
i10FingerprintAssert(($fingerprint['Algorithm']??'')==='sha256','Fingerprint algorithm must be sha256.');
i10FingerprintAssert(preg_match('/^[a-f0-9]{64}$/',(string)($fingerprint['Hash']??''))===1,'Fingerprint hash must be canonical 64-character SHA-256.');
i10FingerprintAssert(($fingerprint['Purpose']??'')==='evidence-integrity-only','Fingerprint purpose must remain evidence-only.');
i10FingerprintAssert(($fingerprint['AuthorizesCutover']??true)===false,'Fingerprint must never authorize cutover.');
i10FingerprintAssert(($fingerprint['Executable']??true)===false && ($fingerprint['PublicMutationAvailable']??true)===false,'Fingerprint metadata must remain non-executable/non-mutating.');
i10FingerprintAssert($service->verify($packet,$fingerprint),'Exact packet must verify against its fingerprint.');

$tampered=$packet;
$tampered['Stages'][1]['Blockers']=[];
i10FingerprintAssert(!$service->verify($tampered,$fingerprint),'Changing blockers must invalidate packet fingerprint.');
$tampered2=$packet;
$tampered2['Executable']=true;
i10FingerprintAssert(!$service->verify($tampered2,$fingerprint),'Changing execution state must invalidate packet fingerprint.');

$unsafe=$fingerprint;$unsafe['AuthorizesCutover']=true;
i10FingerprintAssert(!$service->verify($packet,$unsafe),'Fingerprint claiming cutover authorization must never verify.');
$unsafe=$fingerprint;$unsafe['PublicMutationAvailable']=true;
i10FingerprintAssert(!$service->verify($packet,$unsafe),'Fingerprint claiming public mutation must never verify.');

fwrite(STDOUT,"I10 decision packet fingerprint: PASS\n");
