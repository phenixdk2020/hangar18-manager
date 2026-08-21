<?php

declare(strict_types=1);

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Migration\ConversionDecisionEvidenceBundleService;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketFingerprintService;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketReviewChainService;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketReviewReceiptService;

function i10BundleAssert(bool $condition,string $message): void
{
    if(!$condition){throw new RuntimeException($message);}
}

$packet=[
    'SchemaVersion'=>'1.0',
    'Mode'=>'decision-packet-only',
    'ComparisonSlug'=>'om-foreningen-editor-test',
    'ReviewableTargets'=>['om-foreningen-editor-test'],
    'Stages'=>[['Stage'=>1,'Slug'=>'om-foreningen-editor-test','EligibleForOperatorReview'=>true,'Blockers'=>[]]],
    'Executable'=>false,
    'PublicMutationAvailable'=>false,
];
$fingerprints=new ConversionDecisionPacketFingerprintService();
$receipts=new ConversionDecisionPacketReviewReceiptService($fingerprints);
$chain=new ConversionDecisionPacketReviewChainService($fingerprints,$receipts);
$bundleService=new ConversionDecisionEvidenceBundleService($chain);
$fingerprint=$fingerprints->fingerprint($packet);
$receipt=$receipts->capture($packet,$fingerprint,'Allan','test2 · Chrome','QA-I10-BUNDLE-001');

$bundle=$bundleService->build($packet,$fingerprint,$receipt);
i10BundleAssert(($bundle['Mode']??'')==='decision-evidence-bundle-only','Bundle must remain evidence-only.');
i10BundleAssert(($bundle['PacketHash']??'')===($fingerprint['Hash']??''),'Bundle must expose exact packet hash.');
i10BundleAssert(($bundle['EvidenceChainComplete']??false)===true,'Valid packet/fingerprint/receipt must yield complete evidence chain.');
i10BundleAssert(($bundle['FreshHumanReviewRequired']??true)===false,'Valid evidence bundle must not require fresh review.');
i10BundleAssert(($bundle['ReviewChain']['ReviewChainValid']??false)===true,'Embedded review chain must remain valid.');
i10BundleAssert(($bundle['Packet']??[])===$packet,'Bundle must preserve packet snapshot.');
i10BundleAssert(($bundle['Fingerprint']??[])===$fingerprint,'Bundle must preserve fingerprint snapshot.');
i10BundleAssert(($bundle['ReviewReceipt']??[])===$receipt,'Bundle must preserve review receipt snapshot.');
i10BundleAssert(($bundle['AuthorizesCutover']??true)===false,'Evidence bundle must never authorize cutover.');
i10BundleAssert(($bundle['Executable']??true)===false && ($bundle['PublicMutationAvailable']??true)===false,'Evidence bundle must remain non-executable/non-mutating.');

$missingReceipt=$bundleService->build($packet,$fingerprint,null);
i10BundleAssert($missingReceipt['EvidenceChainComplete']===false && $missingReceipt['FreshHumanReviewRequired']===true,'Missing receipt must produce incomplete evidence bundle.');
i10BundleAssert(in_array('review-chain:human-review-receipt-missing',$missingReceipt['ReviewChain']['Blockers'],true),'Missing receipt blocker must propagate into bundle.');

$tampered=$packet;$tampered['Stages'][0]['Blockers']=['legacy-source-drift'];
$stale=$bundleService->build($tampered,$fingerprint,$receipt);
i10BundleAssert($stale['EvidenceChainComplete']===false && $stale['FreshHumanReviewRequired']===true,'Changed packet must produce stale/incomplete evidence bundle.');
i10BundleAssert(($stale['AuthorizesCutover']??true)===false,'Stale evidence bundle must still remain non-authorizing.');

fwrite(STDOUT,"I10 decision evidence bundle: PASS\n");
