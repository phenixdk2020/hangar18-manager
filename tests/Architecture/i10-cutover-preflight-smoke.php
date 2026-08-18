<?php

declare(strict_types=1);

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceChecklist;
use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceValidator;
use Hangar18\UltimateDesigner\Migration\ConversionCutoverPreflightService;
use Hangar18\UltimateDesigner\Migration\ConversionCutoverPreflightTokenService;
use Hangar18\UltimateDesigner\Portability\CanonicalJson;
use Hangar18\UltimateDesigner\QA\ReleaseReadiness;

function i10PreflightAssert(bool $condition,string $message): void
{
    if(!$condition){throw new RuntimeException($message);}
}

$legacy=[
    'Version'=>'1.22',
    'PageSlug'=>'om-foreningen-editor-test',
    'PageTitle'=>'Om editor test',
    'Sections'=>[['Key'=>'intro','Type'=>'text','Content'=>'Original state']],
];
$hash=(new CanonicalJson())->hash($legacy);
$shadow=['Slug'=>'om-foreningen-editor-test','SourceHash'=>$hash,'State'=>$legacy,'PublicActivation'=>false];
$checks=[];foreach(array_keys((new ConversionAcceptanceChecklist())->required()) as $key){$checks[$key]=true;}
$acceptance=(new ConversionAcceptanceValidator())->normalize('om-foreningen-editor-test',$hash,[
    'Checks'=>$checks,'Environment'=>'test2 · Firefox','EvidenceRef'=>'QA-I10-PREFLIGHT-001','ConfirmedManual'=>true,
],7);
$manual=[];foreach(array_keys((new ReleaseReadiness())->requiredManualEvidence()) as $gate){$manual[$gate]=true;}

$service=new ConversionCutoverPreflightService();
$preflight=$service->build(
    'om-foreningen-editor-test',123,'https://test2.example/om-foreningen-editor-test/',
    $legacy,$shadow,$acceptance,$manual,[],'om-foreningen-editor-test'
);
i10PreflightAssert($preflight['EligibleForFutureCutover']===true,'Accepted comparison shadow with complete manual evidence and no source drift must be preflight-eligible.');
i10PreflightAssert($preflight['SourceDriftFree']===true && $preflight['AcceptanceValid']===true,'Eligible preflight must prove source/acceptance validity.');
i10PreflightAssert($preflight['Executable']===false && $preflight['PublicMutationAvailable']===false,'I10 preflight must remain non-executable and non-mutating.');

$tokens=new ConversionCutoverPreflightTokenService(str_repeat('i10-v086-secret-',3));
$signed=$tokens->issue($preflight,300);
i10PreflightAssert($tokens->verify($signed['token'],$preflight),'Signed preflight token must verify against exact immutable snapshot.');
$tampered=$preflight;$tampered['PageId']=124;
i10PreflightAssert(!$tokens->verify($signed['token'],$tampered),'Preflight token must fail after target identity is changed.');

$changed=$legacy;$changed['Sections'][0]['Content']='Changed after acceptance';
$drifted=$service->build(
    'om-foreningen-editor-test',123,'https://test2.example/om-foreningen-editor-test/',
    $changed,$shadow,$acceptance,$manual,[],'om-foreningen-editor-test'
);
i10PreflightAssert($drifted['EligibleForFutureCutover']===false,'Legacy source drift after shadow/acceptance must block preflight.');
i10PreflightAssert(in_array('legacy-source-drift',$drifted['Blockers'],true),'Source drift blocker must be explicit.');
$blockedSigning=false;try{$tokens->issue($drifted);}catch(RuntimeException $e){$blockedSigning=true;}
i10PreflightAssert($blockedSigning,'Blocked preflight must never receive a signed token.');

$missingPage=$service->build('om-foreningen-editor-test',0,'',$legacy,$shadow,$acceptance,$manual,[],'om-foreningen-editor-test');
i10PreflightAssert(in_array('wordpress-page-id-missing',$missingPage['Blockers'],true)&&in_array('wordpress-permalink-missing',$missingPage['Blockers'],true),'WordPress identity/permalink are mandatory preflight evidence.');

$protected=$service->build('events',12,'https://test2.example/events/',$legacy,['SourceHash'=>$hash],null,$manual,['om-foreningen-editor-test','hjem','om-foreningen','kontakt','bliv-medlem'],'om-foreningen-editor-test');
i10PreflightAssert($protected['EligibleForFutureCutover']===false,'Protected Event domain must remain blocked while CompatibilityPolicy requires legacy runtime.');
i10PreflightAssert(in_array('protected-legacy-runtime-policy:event',$protected['Blockers'],true),'Protected runtime-policy blocker must remain explicit.');

fwrite(STDOUT,"I10 cutover preflight v0.8.6: PASS\n");
