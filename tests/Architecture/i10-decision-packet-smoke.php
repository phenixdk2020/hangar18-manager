<?php

declare(strict_types=1);

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceChecklist;
use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceValidator;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketService;
use Hangar18\UltimateDesigner\Portability\CanonicalJson;
use Hangar18\UltimateDesigner\QA\ReleaseReadiness;

function i10PacketAssert(bool $condition,string $message): void
{
    if(!$condition){throw new RuntimeException($message);}
}

$serviceSource=(string)file_get_contents(dirname(__DIR__,2).'/src/Migration/ConversionDecisionPacketService.php');
foreach(['wp_update_post','wp_insert_post','update_post_meta','delete_post_meta','update_option','delete_option','wp_delete_post','wp_publish_post'] as $forbidden){
    i10PacketAssert(stripos($serviceSource,$forbidden)===false,'Decision packet service must not contain mutation primitive: '.$forbidden);
}
i10PacketAssert(str_contains($serviceSource,"'Executable' => false"),'Decision packet must hard-code Executable=false.');
i10PacketAssert(str_contains($serviceSource,"'PublicMutationAvailable' => false"),'Decision packet must hard-code PublicMutationAvailable=false.');

$comparison='om-foreningen-editor-test';
$legacy=[
    'Version'=>'1.22',
    'PageSlug'=>$comparison,
    'PageTitle'=>'Om editor test',
    'Sections'=>[['Key'=>'intro','Type'=>'text','Content'=>'Original state']],
];
$hash=(new CanonicalJson())->hash($legacy);
$shadow=['Slug'=>$comparison,'SourceHash'=>$hash,'State'=>$legacy,'PublicActivation'=>false];
$checks=[];foreach(array_keys((new ConversionAcceptanceChecklist())->required()) as $key){$checks[$key]=true;}
$acceptance=(new ConversionAcceptanceValidator())->normalize($comparison,$hash,[
    'Checks'=>$checks,
    'Environment'=>'test2 · Chrome',
    'EvidenceRef'=>'QA-I10-PACKET-COMPARISON',
    'ConfirmedManual'=>true,
],7);
$manual=[];foreach(array_keys((new ReleaseReadiness())->requiredManualEvidence()) as $gate){$manual[$gate]=true;}

$pages=[
    ['Slug'=>$comparison,'Title'=>'Comparison'],
    ['Slug'=>'hjem','Title'=>'Hjem'],
    ['Slug'=>'om-foreningen','Title'=>'Om foreningen'],
    ['Slug'=>'kontakt','Title'=>'Kontakt'],
    ['Slug'=>'bliv-medlem','Title'=>'Bliv medlem'],
    ['Slug'=>'koeretoejer-og-materiel','Title'=>'Køretøjer og materiel'],
    ['Slug'=>'events','Title'=>'Events'],
    ['Slug'=>'billedgalleri','Title'=>'Billedgalleri'],
];
$inputs=[
    $comparison=>[
        'PageId'=>123,
        'Permalink'=>'https://test2.example/'.$comparison.'/',
        'CurrentLegacyState'=>$legacy,
        'Shadow'=>$shadow,
        'AcceptanceRecord'=>$acceptance,
    ],
];

$service=new ConversionDecisionPacketService();
$packet=$service->build($pages,$manual,[],$inputs);
i10PacketAssert(($packet['Mode']??'')==='decision-packet-only','Packet must stay decision-only.');
i10PacketAssert(($packet['Executable']??true)===false && ($packet['PublicMutationAvailable']??true)===false,'Decision packet must never expose execution/public mutation.');
i10PacketAssert(($packet['ComparisonSlug']??'')===$comparison,'Comparison target must come from canonical plan service.');
i10PacketAssert(in_array($comparison,$packet['ReviewableTargets'],true),'Fully evidenced comparison target should be operator-reviewable.');
$comparisonRow=array_values(array_filter($packet['Stages'],static fn(array $row): bool=>($row['Slug']??'')===$comparison))[0]??null;
i10PacketAssert(is_array($comparisonRow)&&$comparisonRow['EligibleForOperatorReview']===true,'Comparison stage must be reviewable only when plan+preflight are both clean.');
i10PacketAssert(($comparisonRow['Preflight']['Executable']??true)===false,'Embedded preflight must remain non-executable.');
i10PacketAssert(($comparisonRow['Preflight']['PublicMutationAvailable']??true)===false,'Embedded preflight must remain non-mutating.');

$homeRow=array_values(array_filter($packet['Stages'],static fn(array $row): bool=>($row['Slug']??'')==='hjem'))[0]??null;
i10PacketAssert(is_array($homeRow)&&$homeRow['EligibleForOperatorReview']===false,'Missing per-target decision input must block Hjem.');
i10PacketAssert(in_array('decision-input-missing',$homeRow['Blockers'],true),'Decision packet must expose missing target input explicitly.');

i10PacketAssert(isset($packet['BlockedTargets']['events']),'Protected Event target must remain blocked.');

$acceptedComparison=$service->build($pages,$manual,[$comparison],$inputs);
$homeRow2=array_values(array_filter($acceptedComparison['Stages'],static fn(array $row): bool=>($row['Slug']??'')==='hjem'))[0]??null;
i10PacketAssert(is_array($homeRow2)&&!in_array('comparison-page-not-accepted',$homeRow2['Blockers'],true),'Accepting comparison may clear sequence blocker, but not missing decision input.');
i10PacketAssert(in_array('decision-input-missing',$homeRow2['Blockers'],true),'Missing Hjem decision input must remain blocking.');

$incomplete=$manual;array_shift($incomplete);
$blocked=$service->build($pages,$incomplete,[],$inputs);
i10PacketAssert(($blocked['ManualEvidenceComplete']??true)===false,'Incomplete manual evidence must be visible at packet level.');
$comparisonBlocked=array_values(array_filter($blocked['Stages'],static fn(array $row): bool=>($row['Slug']??'')===$comparison))[0]??null;
i10PacketAssert(is_array($comparisonBlocked)&&$comparisonBlocked['EligibleForOperatorReview']===false,'Missing manual evidence must block comparison reviewability.');
i10PacketAssert((bool)array_filter($comparisonBlocked['Blockers'],static fn(string $b): bool=>str_starts_with($b,'manual-gate:')),'Manual gate blocker must remain explicit.');

$driftedLegacy=$legacy;$driftedLegacy['Sections'][0]['Content']='Drifted';
$driftInputs=$inputs;$driftInputs[$comparison]['CurrentLegacyState']=$driftedLegacy;
$driftPacket=$service->build($pages,$manual,[],$driftInputs);
$driftRow=array_values(array_filter($driftPacket['Stages'],static fn(array $row): bool=>($row['Slug']??'')===$comparison))[0]??null;
i10PacketAssert(is_array($driftRow)&&in_array('legacy-source-drift',$driftRow['Blockers'],true),'Source drift must propagate into decision packet blockers.');
i10PacketAssert($driftRow['EligibleForOperatorReview']===false,'Source drift must block operator reviewability.');

fwrite(STDOUT,"I10 decision packet: PASS\n");
