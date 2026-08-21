<?php

declare(strict_types=1);

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketFingerprintService;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketReviewReceiptService;

function i10ReceiptAssert(bool $condition,string $message): void
{
    if(!$condition){throw new RuntimeException($message);}
}

$packet=[
    'SchemaVersion'=>'1.0',
    'Mode'=>'decision-packet-only',
    'ComparisonSlug'=>'om-foreningen-editor-test',
    'Stages'=>[['Stage'=>1,'Slug'=>'om-foreningen-editor-test','EligibleForOperatorReview'=>true,'Blockers'=>[]]],
    'Executable'=>false,
    'PublicMutationAvailable'=>false,
];
$fingerprints=new ConversionDecisionPacketFingerprintService();
$fingerprint=$fingerprints->fingerprint($packet);
$service=new ConversionDecisionPacketReviewReceiptService($fingerprints);
$receipt=$service->capture($packet,$fingerprint,'Allan','test2 · Chrome','QA-I10-REVIEW-001','Reviewed decision packet only.');

i10ReceiptAssert(($receipt['Mode']??'')==='decision-packet-review-receipt-only','Receipt must remain review-only.');
i10ReceiptAssert(($receipt['HumanReviewRecorded']??false)===true,'Human review flag missing.');
i10ReceiptAssert(($receipt['AuthorizesCutover']??true)===false,'Review receipt must not authorize cutover.');
i10ReceiptAssert(($receipt['Executable']??true)===false && ($receipt['PublicMutationAvailable']??true)===false,'Review receipt must remain non-executable/non-mutating.');
i10ReceiptAssert($service->verify($packet,$receipt),'Exact reviewed packet must verify against receipt.');

$tampered=$packet;$tampered['Stages'][0]['Blockers']=['legacy-source-drift'];
i10ReceiptAssert(!$service->verify($tampered,$receipt),'Packet changes after review must invalidate receipt.');

$unsafe=$receipt;$unsafe['AuthorizesCutover']=true;
i10ReceiptAssert(!$service->verify($packet,$unsafe),'Receipt claiming cutover authorization must never verify.');
$unsafe=$receipt;$unsafe['Executable']=true;
i10ReceiptAssert(!$service->verify($packet,$unsafe),'Receipt claiming execution must never verify.');

$failed=false;try{$service->capture($packet,['Hash'=>str_repeat('0',64)],'Allan','test2','evidence');}catch(RuntimeException $e){$failed=true;}
i10ReceiptAssert($failed,'Stale/invalid packet fingerprint must block receipt capture.');
$failed=false;try{$service->capture($packet,$fingerprint,'','test2','evidence');}catch(RuntimeException $e){$failed=true;}
i10ReceiptAssert($failed,'Reviewer identity is mandatory.');
$failed=false;try{$service->capture($packet,$fingerprint,'Allan','','evidence');}catch(RuntimeException $e){$failed=true;}
i10ReceiptAssert($failed,'Environment reference is mandatory.');
$failed=false;try{$service->capture($packet,$fingerprint,'Allan','test2','');}catch(RuntimeException $e){$failed=true;}
i10ReceiptAssert($failed,'Evidence reference is mandatory.');

fwrite(STDOUT,"I10 decision packet review receipt: PASS\n");
