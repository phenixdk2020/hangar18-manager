<?php

declare(strict_types=1);

$h18Options=[];
function get_option(string $key,$default=false){global $h18Options;return $h18Options[$key]??$default;}
function update_option(string $key,$value,$autoload=null): bool{global $h18Options;$changed=!array_key_exists($key,$h18Options)||$h18Options[$key]!==$value;$h18Options[$key]=$value;return $changed;}

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionArtifactRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionRevisionRepository;
use Hangar18\UltimateDesigner\Portability\ArtifactPackageService;
use Hangar18\UltimateDesigner\Portability\BackupService;
use Hangar18\UltimateDesigner\Portability\ImportExecutor;
use Hangar18\UltimateDesigner\Portability\ImportPlanTokenService;
use Hangar18\UltimateDesigner\Portability\ImportPlanner;
use Hangar18\UltimateDesigner\Portability\PortableReferenceInspector;
use RuntimeException;

function i6Assert(bool $condition,string $message): void{if(!$condition){throw new RuntimeException($message);}}

$repo=new WordPressOptionArtifactRepository();
$repo->save('component','card',['Name'=>'Eksisterende kort','Value'=>1]);
$before=$repo->snapshot();
$service=new ArtifactPackageService();
$json=$service->export([
    ['Type'=>'component','Id'=>'card','Name'=>'Nyt kort','Data'=>['Name'=>'Nyt kort','Value'=>2]],
    ['Type'=>'template','Id'=>'archive','Name'=>'Arkiv','Data'=>['Component'=>'artifact://component:card']],
]);
$package=$service->import($json);
$planner=new ImportPlanner($repo);
$dry=$planner->plan($package['Artifacts'],'remap',true);
i6Assert($dry['DryRun']===true&&$dry['MutationAllowed']===false,'Dry-run must not authorize mutation.');
i6Assert(($dry['Mappings']['component:card']??'')==='card-import-2','Collision must be remapped before confirmation.');
i6Assert($repo->snapshot()===$before,'Planning must not mutate workspace.');

$refs=(new PortableReferenceInspector())->inspect($package['Artifacts']);
i6Assert($refs['Artifacts']===['component:card']&&$refs['Assets']===[],'Portable artifact reference must be discovered.');
$tokenService=new ImportPlanTokenService(str_repeat('i6-secret-',5));
$issued=$tokenService->issue($package['Checksum'],'remap',$dry,900);
i6Assert($tokenService->verify($issued['token'],$package['Checksum'],'remap',$dry),'Signed dry-run token must verify for exact package/plan.');
i6Assert(!$tokenService->verify($issued['token'],$package['Checksum'],'skip',$dry),'Token must not verify for another strategy.');
$changed=$dry;$changed['Mappings']['component:card']='tampered';
i6Assert(!$tokenService->verify($issued['token'],$package['Checksum'],'remap',$changed),'Token must not verify for a changed plan.');

$blocked=false;
try{(new ImportExecutor($repo,new BackupService(new WordPressOptionRevisionRepository())))->execute($dry,[],7,true);}catch(RuntimeException $e){$blocked=true;}
i6Assert($blocked&&$repo->snapshot()===$before,'Dry-run must remain non-mutating even if execute is called.');

$write=$planner->plan($package['Artifacts'],'remap',false);
$result=(new ImportExecutor($repo,new BackupService(new WordPressOptionRevisionRepository())))->execute($write,[],7,true);
$after=$repo->snapshot();
i6Assert(isset($after['component']['card-import-2'],$after['template']['archive']),'Confirmed workspace import must write remapped artifacts.');
i6Assert(($after['template']['archive']['Component']??'')==='card-import-2','Cross-artifact reference must follow remap.');
i6Assert((string)($result['BackupId']??'')!=='','Confirmed import must return automatic backup ID.');
$restored=(new BackupService(new WordPressOptionRevisionRepository()))->restoreState('portability:artifact-import',(string)$result['BackupId']);
i6Assert($restored===$before,'Pre-import backup must contain exact workspace state.');
$repo->restoreSnapshot($restored);i6Assert($repo->snapshot()===$before,'Workspace restore must recover exact state.');

$assetJson=$service->export([['Type'=>'component','Id'=>'photo','Name'=>'Photo','Data'=>['Media'=>'asset://asset:77']]]);
$assetPackage=$service->import($assetJson);$assetRefs=(new PortableReferenceInspector())->inspect($assetPackage['Artifacts']);
i6Assert($assetRefs['Assets']===['asset:77'],'Asset reference must be exposed as unresolved before write.');

fwrite(STDOUT,"I6 Portability workspace + signed dry-run: PASS\n");
