<?php

declare(strict_types=1);

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketFingerprintService;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketReviewChainFormatter;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketReviewChainService;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketReviewReceiptService;

function i10ReviewChainAssert(bool $condition,string $message): void
{
    if(!$condition){throw new RuntimeException($message);}
}

$packet=[
    'SchemaVersion'=>'1.0',
    'Mode'=>'decision-packet-only',
    'ComparisonSlug'=>'om-foreningen-editor-test',
    'ReviewableTargets'=>['Hjem','om-foreningen-editor-test','hjem',''],
    'Stages'=>[
        ['Stage'=>1,'Slug'=>'om-foreningen-editor-test','EligibleForOperatorReview'=>true,'Blockers'=>[]],
        ['Stage'=>2,'Slug'=>'hjem','EligibleForOperatorReview'=>true,'Blockers'=>[]],
    ],
    'Executable'=>false,
    'PublicMutationAvailable'=>false,
];

$fingerprints=new ConversionDecisionPacketFingerprintService();
$receipts=new ConversionDecisionPacketReviewReceiptService($fingerprints);
$chain=new ConversionDecisionPacketReviewChainService($fingerprints,$receipts);
$formatter=new ConversionDecisionPacketReviewChainFormatter();
$fingerprint=$fingerprints->fingerprint($packet);
$receipt=$receipts->capture($packet,$fingerprint,'Allan','test2 · Chrome','QA-I10-CHAIN-001','Human review only.');

$valid=$chain->inspect($packet,$fingerprint,$receipt);
i10ReviewChainAssert(($valid['Mode']??'')==='decision-packet-review-chain-only','Review chain must remain report-only.');
i10ReviewChainAssert(($valid['ReviewChainValid']??false)===true,'Exact packet/fingerprint/receipt chain should validate.');
i10ReviewChainAssert(($valid['FreshHumanReviewRequired']??true)===false,'Exact reviewed packet should not require another review.');
i10ReviewChainAssert(($valid['FingerprintValid']??false)===true && ($valid['HumanReviewReceiptValid']??false)===true,'Fingerprint and receipt should both validate.');
i10ReviewChainAssert(($valid['FingerprintReceiptHashesMatch']??false)===true,'Fingerprint/receipt hash binding must match.');
i10ReviewChainAssert(($valid['Blockers']??['x'])===[],'Valid chain must have no blockers.');
i10ReviewChainAssert(($valid['ReviewableTargets']??[])===['hjem','om-foreningen-editor-test'],'Reviewable target output must be canonical/deterministic.');
i10ReviewChainAssert(($valid['AuthorizesCutover']??true)===false,'Review chain must never authorize cutover.');
i10ReviewChainAssert(($valid['Executable']??true)===false && ($valid['PublicMutationAvailable']??true)===false,'Review chain must remain non-executable/non-mutating.');

$json=$formatter->json($valid);
$decoded=json_decode($json,true,512,JSON_THROW_ON_ERROR);
i10ReviewChainAssert(($decoded['ReviewChainValid']??false)===true,'JSON formatter must preserve chain validity.');
i10ReviewChainAssert(($decoded['AuthorizesCutover']??true)===false,'JSON formatter must preserve non-authorizing state.');
$markdown=$formatter->markdown($valid);
i10ReviewChainAssert(str_contains($markdown,'# I10 Review Chain'),'Review-chain Markdown heading missing.');
i10ReviewChainAssert(str_contains($markdown,'Review chain valid: **YES**'),'Markdown must expose valid-chain status.');
i10ReviewChainAssert(str_contains($markdown,'Authorizes cutover: **NO**'),'Markdown must expose non-authorizing state.');
i10ReviewChainAssert(str_contains($markdown,'Executable: **NO**'),'Markdown must expose non-executable state.');
i10ReviewChainAssert(str_contains($markdown,'does not authorize cutover'),'Markdown must state evidence-only semantics.');

$missingFingerprint=$chain->inspect($packet,null,$receipt);
i10ReviewChainAssert($missingFingerprint['ReviewChainValid']===false && $missingFingerprint['FreshHumanReviewRequired']===true,'Missing fingerprint must invalidate chain.');
i10ReviewChainAssert(in_array('review-chain:fingerprint-missing',$missingFingerprint['Blockers'],true),'Missing fingerprint blocker absent.');
$missingMarkdown=$formatter->markdown($missingFingerprint);
i10ReviewChainAssert(str_contains($missingMarkdown,'Fresh human review required: **YES**'),'Formatter must surface fresh-review requirement.');
i10ReviewChainAssert(str_contains($missingMarkdown,'review-chain:fingerprint-missing'),'Formatter must surface blockers.');

$missingReceipt=$chain->inspect($packet,$fingerprint,null);
i10ReviewChainAssert($missingReceipt['ReviewChainValid']===false && $missingReceipt['FreshHumanReviewRequired']===true,'Missing human receipt must invalidate chain.');
i10ReviewChainAssert(in_array('review-chain:human-review-receipt-missing',$missingReceipt['Blockers'],true),'Missing receipt blocker absent.');

$changed=$packet;
$changed['Stages'][1]['Blockers']=['legacy-source-drift'];
$stale=$chain->inspect($changed,$fingerprint,$receipt);
i10ReviewChainAssert($stale['ReviewChainValid']===false && $stale['FreshHumanReviewRequired']===true,'Changed packet must make prior review stale.');
i10ReviewChainAssert(in_array('review-chain:fingerprint-invalid-or-stale',$stale['Blockers'],true),'Stale fingerprint blocker missing.');
i10ReviewChainAssert(in_array('review-chain:human-review-receipt-invalid-or-stale',$stale['Blockers'],true),'Stale receipt blocker missing.');

$unsafe=$packet;
$unsafe['Executable']=true;
$unsafeResult=$chain->inspect($unsafe,$fingerprint,$receipt);
i10ReviewChainAssert($unsafeResult['PacketSafetyInvariantValid']===false,'Unsafe packet execution state must be detected.');
i10ReviewChainAssert(in_array('review-chain:packet-execution-invariant-violated',$unsafeResult['Blockers'],true),'Execution invariant blocker missing.');
i10ReviewChainAssert(($unsafeResult['AuthorizesCutover']??true)===false,'Even unsafe input must not yield authorization.');

$wrongMode=$packet;
$wrongMode['Mode']='cutover';
$modeResult=$chain->inspect($wrongMode,$fingerprint,$receipt);
i10ReviewChainAssert($modeResult['PacketModeValid']===false,'Unexpected packet mode must be detected.');
i10ReviewChainAssert(in_array('review-chain:packet-mode-invalid',$modeResult['Blockers'],true),'Packet mode blocker missing.');

fwrite(STDOUT,"I10 decision packet review chain + formatter: PASS\n");
