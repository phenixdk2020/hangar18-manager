<?php

declare(strict_types=1);

$h18QaOptions=[];
function get_option(string $key,$default=false){global $h18QaOptions;return $h18QaOptions[$key]??$default;}
function update_option(string $key,$value,$autoload=null): bool{global $h18QaOptions;$h18QaOptions[$key]=$value;return true;}

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionManualQaEvidenceRepository;
use Hangar18\UltimateDesigner\QA\ManualEvidenceValidator;
use Hangar18\UltimateDesigner\QA\ReleaseReadiness;
use Hangar18\UltimateDesigner\QA\RollbackPreflightService;
use RuntimeException;

function i9Assert(bool $condition,string $message): void{if(!$condition){throw new RuntimeException($message);}}

$validator=new ManualEvidenceValidator();
$blocked=false;
try{$validator->normalize('latest-chrome-brand',['Status'=>'pass','Environment'=>'Chrome','EvidenceRef'=>'','ConfirmedManual'=>true],42);}catch(RuntimeException $e){$blocked=true;}
i9Assert($blocked,'Manual PASS must require evidence reference.');
$blocked=false;
try{$validator->normalize('latest-chrome-brand',['Status'=>'pass','Environment'=>'Chrome','EvidenceRef'=>'shot-1','ConfirmedManual'=>false],42);}catch(RuntimeException $e){$blocked=true;}
i9Assert($blocked,'Manual PASS must require explicit human confirmation.');
$blocked=false;
try{$validator->normalize('not-a-real-gate',['Status'=>'pass','Environment'=>'x','EvidenceRef'=>'y','ConfirmedManual'=>true],42);}catch(RuntimeException $e){$blocked=true;}
i9Assert($blocked,'Unknown manual QA gates must be rejected.');

$repo=new WordPressOptionManualQaEvidenceRepository($validator);
$record=$repo->save('latest-chrome-brand',['Status'=>'pass','Environment'=>'test2 · Chrome 140 · desktop','EvidenceRef'=>'qa://chrome/001','Notes'=>'Header/menu visually checked','ConfirmedManual'=>true],42);
i9Assert(($record['Status']??'')==='pass'&&!empty($record['ConfirmedManual'])&&($record['UserId']??0)===42,'Confirmed manual evidence must persist with user/environment/reference.');
$pending=$repo->save('latest-edge-brand',['Status'=>'pending','Environment'=>'','EvidenceRef'=>'','Notes'=>'','ConfirmedManual'=>false],42);
i9Assert(($pending['Status']??'')==='pending','Pending evidence may be saved without pretending to pass.');
$records=$repo->all();$map=$validator->statusMap($records);
i9Assert(($map['latest-chrome-brand']??false)===true,'Confirmed manual PASS must close its exact gate.');
i9Assert(($map['latest-edge-brand']??true)===false,'Pending evidence must not close a gate.');
i9Assert(($map['migration-rollback-live-copy']??true)===false,'Missing live-copy evidence must remain pending.');
$readiness=(new ReleaseReadiness())->evaluate([],$map);
i9Assert(($readiness['Ready']??true)===false&&($readiness['ManualPassed']??0)===1&&($readiness['ManualTotal']??0)===8,'I10 readiness must remain blocked until all eight manual gates pass.');

$snapshot=['hjem'=>['Version'=>'1.22','Sections'=>[['Key'=>'hero','Type'=>'text','Content'=>'Original']]],'om'=>['Version'=>'1.22','Sections'=>[]]];
$before=$snapshot;$preflight=(new RollbackPreflightService())->rehearse($snapshot);
i9Assert(($preflight['Pass']??false)===true,'Rollback preflight must prove exact restoration on copy.');
i9Assert(($preflight['Mode']??'')==='in-memory-copy-only','Rollback preflight must explicitly identify copy-only mode.');
i9Assert(($preflight['SatisfiesManualLiveCopyGate']??true)===false,'Automated rollback preflight must never satisfy manual live-copy gate.');
i9Assert($snapshot===$before,'Rollback preflight must not mutate source snapshot.');
i9Assert(($preflight['BeforeHash']??'')===($preflight['RestoredHash']??''),'Restored preflight hash must equal original hash.');
i9Assert(($preflight['MutatedHash']??'')!==($preflight['BeforeHash']??''),'Preflight must actually exercise a temporary changed copy.');

fwrite(STDOUT,"I9 manual QA evidence + rollback copy preflight: PASS\n");
