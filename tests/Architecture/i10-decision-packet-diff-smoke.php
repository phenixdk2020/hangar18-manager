<?php

declare(strict_types=1);

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketDiffService;

function i10DiffAssert(bool $condition,string $message): void
{
    if(!$condition){throw new RuntimeException($message);}
}

$before=[
    'ComparisonSlug'=>'om-foreningen-editor-test',
    'ManualEvidenceComplete'=>false,
    'AcceptedSlugs'=>[],
    'Stages'=>[
        ['Stage'=>1,'Kind'=>'comparison','Slug'=>'om-foreningen-editor-test','Exists'=>true,'PlanEligible'=>false,'PreflightAvailable'=>true,'EligibleForOperatorReview'=>false,'Blockers'=>['manual-gate:safari']],
        ['Stage'=>2,'Kind'=>'core','Slug'=>'hjem','Exists'=>true,'PlanEligible'=>false,'PreflightAvailable'=>false,'EligibleForOperatorReview'=>false,'Blockers'=>['comparison-page-not-accepted','decision-input-missing']],
    ],
    'Executable'=>false,
    'PublicMutationAvailable'=>false,
];
$after=$before;

$service=new ConversionDecisionPacketDiffService();
$same=$service->compare($before,$after);
i10DiffAssert(($same['Mode']??'')==='decision-packet-diff-only','Diff must remain decision-only.');
i10DiffAssert(($same['Changed']??true)===false && ($same['ChangedStageCount']??-1)===0,'Identical packets must produce no changes.');
i10DiffAssert(($same['Executable']??true)===false && ($same['PublicMutationAvailable']??true)===false,'Diff must remain non-executable/non-mutating.');

$after['ManualEvidenceComplete']=true;
$after['AcceptedSlugs']=['om-foreningen-editor-test'];
$after['Stages'][0]['PlanEligible']=true;
$after['Stages'][0]['EligibleForOperatorReview']=true;
$after['Stages'][0]['Blockers']=[];
$after['Stages'][1]['Blockers']=['decision-input-missing'];
$changed=$service->compare($before,$after);
i10DiffAssert($changed['Changed']===true,'Meaningful packet changes must be detected.');
i10DiffAssert($changed['ManualEvidenceChanged']===true,'Manual evidence transition must be explicit.');
i10DiffAssert($changed['AcceptedSlugsChanged']===true,'Acceptance sequence transition must be explicit.');
i10DiffAssert($changed['ChangedStageCount']===2,'Both changed stages must be reported.');
$comparison=array_values(array_filter($changed['StageChanges'],static fn(array $row): bool=>($row['Slug']??'')==='om-foreningen-editor-test'))[0]??null;
i10DiffAssert(is_array($comparison)&&($comparison['Change']??'')==='stage-changed','Comparison stage change missing.');
i10DiffAssert(($comparison['Before']['EligibleForOperatorReview']??true)===false && ($comparison['After']['EligibleForOperatorReview']??false)===true,'Reviewability transition must be preserved.');

$removed=$after;array_pop($removed['Stages']);
$removedDiff=$service->compare($after,$removed);
i10DiffAssert($removedDiff['ChangedStageCount']===1,'Removed stage must be reported once.');
i10DiffAssert(($removedDiff['StageChanges'][0]['Change']??'')==='stage-removed','Removed stage classification missing.');

$added=$after;$added['Stages'][]=['Stage'=>3,'Kind'=>'core','Slug'=>'om-foreningen','Exists'=>true,'PlanEligible'=>false,'PreflightAvailable'=>false,'EligibleForOperatorReview'=>false,'Blockers'=>['decision-input-missing']];
$addedDiff=$service->compare($after,$added);
i10DiffAssert($addedDiff['ChangedStageCount']===1 && ($addedDiff['StageChanges'][0]['Change']??'')==='stage-added','Added stage classification missing.');

fwrite(STDOUT,"I10 decision packet diff: PASS\n");
