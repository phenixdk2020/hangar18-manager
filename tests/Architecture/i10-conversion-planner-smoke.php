<?php

declare(strict_types=1);

$h18ConversionOptions=[];
function get_option(string $key,$default=false){global $h18ConversionOptions;return $h18ConversionOptions[$key]??$default;}
function update_option(string $key,$value,$autoload=null): bool{global $h18ConversionOptions;$h18ConversionOptions[$key]=$value;return true;}

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionWorkspaceRepository;
use Hangar18\UltimateDesigner\Migration\ConversionPlanService;
use Hangar18\UltimateDesigner\Migration\ConversionReadinessGate;
use Hangar18\UltimateDesigner\QA\ReleaseReadiness;
use RuntimeException;

function i10Assert(bool $condition,string $message): void{if(!$condition){throw new RuntimeException($message);}}

$pages=[
 ['Slug'=>'om-foreningen-editor-test','Title'=>'Om editor test'],
 ['Slug'=>'hjem','Title'=>'Hjem'],['Slug'=>'om-foreningen','Title'=>'Om'],['Slug'=>'kontakt','Title'=>'Kontakt'],['Slug'=>'bliv-medlem','Title'=>'Bliv medlem'],
 ['Slug'=>'koeretoejer-og-materiel','Title'=>'Køretøjer'],['Slug'=>'events','Title'=>'Events'],['Slug'=>'billedgalleri','Title'=>'Billedgalleri'],
];
$manual=(new ReleaseReadiness())->requiredManualEvidence();
$plan=(new ConversionPlanService())->plan($pages,$manual,[]);
i10Assert(($plan['Mode']??'')==='plan-only'&&($plan['PublicMutationAvailable']??true)===false,'I10 planner must explicitly expose no public mutation.');
i10Assert(($plan['ComparisonSlug']??'')==='om-foreningen-editor-test','Planner must choose a non-critical editor/test comparison page.');
$first=$plan['Stages'][0]??[];i10Assert(($first['EligibleForFutureCutover']??true)===false,'Comparison page must remain blocked while manual gates are incomplete.');
i10Assert(in_array('manual-gate:latest-chrome-brand',(array)($first['Blockers']??[]),true),'Missing manual evidence must appear as explicit blocker.');

$allPass=array_fill_keys(array_keys($manual),true);$gate=new ConversionReadinessGate();
$comparison=$gate->evaluate('om-foreningen-editor-test',$allPass,[],'om-foreningen-editor-test');
i10Assert(($comparison['EligibleForFutureCutover']??false)===true,'Comparison target may become future-eligible only after all manual gates pass.');
$home=$gate->evaluate('hjem',$allPass,['om-foreningen-editor-test'],'om-foreningen-editor-test');
i10Assert(($home['EligibleForFutureCutover']??false)===true,'Hjem must require accepted comparison page but no prior core page.');
$omBlocked=$gate->evaluate('om-foreningen',$allPass,['om-foreningen-editor-test'],'om-foreningen-editor-test');
i10Assert(($omBlocked['EligibleForFutureCutover']??true)===false&&in_array('prior-core-not-accepted:hjem',(array)$omBlocked['Blockers'],true),'Om must remain blocked until Hjem is accepted.');
$om=$gate->evaluate('om-foreningen',$allPass,['om-foreningen-editor-test','hjem'],'om-foreningen-editor-test');
i10Assert(($om['EligibleForFutureCutover']??false)===true,'Om may become future-eligible after accepted comparison + Hjem.');
$protected=$gate->evaluate('events',$allPass,['om-foreningen-editor-test','hjem','om-foreningen','kontakt','bliv-medlem'],'om-foreningen-editor-test');
i10Assert(($protected['EligibleForFutureCutover']??true)===false&&in_array('protected-legacy-runtime-policy:event',(array)$protected['Blockers'],true),'Protected Event domain must remain blocked by CompatibilityPolicy even after core sequence.');

$source=['Version'=>'1.22','Sections'=>[['Key'=>'hero','Type'=>'text','Content'=>'Original']]];$before=$source;$repo=new WordPressOptionConversionWorkspaceRepository();$shadow=$repo->createShadow('om-foreningen-editor-test',$source,77);
i10Assert(($shadow['Mode']??'')==='shadow-copy-only'&&($shadow['PublicActivation']??true)===false&&($shadow['Accepted']??true)===false,'Shadow workspace must never imply activation or acceptance.');
i10Assert($source===$before,'Creating a shadow copy must not mutate source state.');
i10Assert(($repo->all()['om-foreningen-editor-test']['SourceHash']??'')===($shadow['SourceHash']??''),'Shadow workspace must persist deterministic source hash.');
i10Assert(!array_key_exists('hangar18_manager_pages_v1',$h18ConversionOptions),'I10 workspace test must never write legacy page-store option.');

fwrite(STDOUT,"I10 conversion planner + shadow-only workspace: PASS\n");
