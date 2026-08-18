<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();
require_once __DIR__ . '/InMemoryArtifactRepository.php';
require_once __DIR__ . '/InMemoryRevisionRepository.php';
require_once __DIR__ . '/InMemoryStagingRepository.php';

use Hangar18\UltimateDesigner\Core\Version;
use Hangar18\UltimateDesigner\Portability\ArtifactPackageService;
use Hangar18\UltimateDesigner\Portability\AssetManifestService;
use Hangar18\UltimateDesigner\Portability\BackupService;
use Hangar18\UltimateDesigner\Portability\ImportExecutor;
use Hangar18\UltimateDesigner\Portability\ImportPlanner;
use Hangar18\UltimateDesigner\Portability\PagePackageService;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use Hangar18\UltimateDesigner\Workflow\StagingService;
use RuntimeException;

function e13Assert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

// UD-108: page + global styles roundtrip must be exact and schema/checksum protected.
$page = [
    'Version'=>Version::PAGE_SCHEMA,
    'PageSlug'=>'portability-test',
    'PageTitle'=>'Portability test',
    'ContentVersion'=>3,
    'DataContextType'=>'',
    'DataContextEntryId'=>0,
    'Sections'=>[
        ['Key'=>'hero','Type'=>'text','LayoutParentKey'=>'','Title'=>'Velkommen','Content'=>'Test'],
    ],
];
$styles = ['Colors'=>['Primary'=>'#30382a'],'Typography'=>['Body'=>'Segoe UI'],'Spacing'=>['M'=>16]];
$pagePackages = new PagePackageService(new PageSchemaValidator());
$pageJson = $pagePackages->export($page,$styles);
$pageImported = $pagePackages->import($pageJson);
e13Assert($pageImported['Page'] === $page, 'Page JSON package must import to the identical page state.');
e13Assert($pageImported['GlobalStyles'] === $styles, 'Global styles must roundtrip identically.');
$tampered = str_replace('Velkommen','Manipuleret',$pageJson);
$tamperBlocked = false;
try { $pagePackages->import($tampered); } catch (RuntimeException $e) { $tamperBlocked = true; }
e13Assert($tamperBlocked, 'Checksum must reject tampered page packages.');

// UD-109/111: artifacts plan collision-free IDs before any write.
$artifactPackages = new ArtifactPackageService();
$artifactJson = $artifactPackages->export([
    ['Type'=>'component','Id'=>'card','Name'=>'Kort','Data'=>['Title'=>'Kort','MediaId'=>'asset://asset:5']],
    ['Type'=>'template','Id'=>'archive','Name'=>'Arkiv','Data'=>['CardComponent'=>'artifact://component:card']],
    ['Type'=>'menu','Id'=>'main','Name'=>'Hovedmenu','Data'=>['Items'=>[['Label'=>'Hjem','Url'=>'/']]]],
    ['Type'=>'form','Id'=>'contact','Name'=>'Kontakt','Data'=>['Fields'=>[['Name'=>'email','Type'=>'email']]]],
]);
$artifactPackage = $artifactPackages->import($artifactJson);
$seed = ['component'=>['card'=>['Title'=>'Eksisterende kort']]];
$target = new InMemoryArtifactRepository($seed);
$planner = new ImportPlanner($target);
$dryPlan = $planner->plan($artifactPackage['Artifacts'],'remap',true);
e13Assert($dryPlan['DryRun'] === true && $dryPlan['MutationAllowed'] === false, 'Dry-run must never authorize mutation.');
e13Assert($target->snapshot() === $seed, 'Dry-run planning must not mutate target repository.');
e13Assert(($dryPlan['Mappings']['component:card'] ?? '') === 'card-import-2', 'ID collision must receive deterministic collision-free remap.');
e13Assert(count($dryPlan['Conflicts']) === 1, 'ID collision must be visible before import.');
$rejectPlan = $planner->plan($artifactPackage['Artifacts'],'reject',false);
e13Assert($rejectPlan['Valid'] === false && $rejectPlan['MutationAllowed'] === false, 'Reject strategy must block colliding import before mutation.');

// UD-110: asset matching is SHA-256 based and reports broken package references.
$assetManifests = new AssetManifestService();
$hash5 = hash('sha256','asset-five');
$hash6 = hash('sha256','asset-six');
$manifest = $assetManifests->manifest([
    ['MediaId'=>5,'Hash'=>$hash5,'Filename'=>'five.jpg','Mime'=>'image/jpeg','Bytes'=>1000],
    ['MediaId'=>6,'Hash'=>$hash6,'Filename'=>'six.jpg','Mime'=>'image/jpeg','Bytes'=>2000],
]);
$assetMatch = $assetManifests->match($manifest,[
    ['MediaId'=>501,'Hash'=>$hash5,'Filename'=>'renamed-five.jpg'],
]);
e13Assert(($assetMatch['Mappings']['asset:5'] ?? 0) === 501, 'Asset import must map matching bytes/hash even when filename/ID differs.');
e13Assert(count($assetMatch['Broken']) === 1 && ($assetMatch['Broken'][0]['PackageAssetId'] ?? '') === 'asset:6', 'Unmatched assets must be reported as broken instead of silently dropped.');

// UD-111/112: confirmed import backs up first, remaps refs and writes atomically.
$revisions = new InMemoryRevisionRepository();
$backups = new BackupService($revisions);
$executor = new ImportExecutor($target,$backups);
$executeBlocked = false;
try { $executor->execute($dryPlan,['asset:5'=>501],7,true); } catch (RuntimeException $e) { $executeBlocked = true; }
e13Assert($executeBlocked && $target->snapshot() === $seed, 'Dry-run plan must remain non-mutating even when execute is called.');

$writePlan = $planner->plan($artifactPackage['Artifacts'],'remap',false);
$result = $executor->execute($writePlan,['asset:5'=>501],7,true);
e13Assert(count($result['Written']) === 4, 'Confirmed import must move all selected artifacts.');
$after = $target->snapshot();
e13Assert(isset($after['component']['card-import-2']), 'Colliding component must be imported under remapped ID.');
e13Assert(($after['component']['card-import-2']['MediaId'] ?? 0) === 501, 'Portable asset reference must map to target native MediaId.');
e13Assert(($after['template']['archive']['CardComponent'] ?? '') === 'card-import-2', 'Artifact reference must follow component ID remap.');
$restoredBackup = $backups->restoreState('portability:artifact-import',(string) $result['BackupId']);
e13Assert($restoredBackup === $seed, 'Automatic pre-import backup must restore exact pre-import state.');

// Broken asset refs abort atomically while the pre-import backup remains available.
$rollbackTarget = new InMemoryArtifactRepository($seed);
$rollbackPlanner = new ImportPlanner($rollbackTarget);
$rollbackPlan = $rollbackPlanner->plan($artifactPackage['Artifacts'],'remap',false);
$rollbackRevisions = new InMemoryRevisionRepository();
$rollbackExecutor = new ImportExecutor($rollbackTarget,new BackupService($rollbackRevisions));
$brokenBlocked = false;
try { $rollbackExecutor->execute($rollbackPlan,[],7,true); } catch (RuntimeException $e) { $brokenBlocked = true; }
e13Assert($brokenBlocked && $rollbackTarget->snapshot() === $seed, 'Broken reference must rollback the entire import mutation.');
e13Assert(count($rollbackRevisions->history('portability:artifact-import')) === 1, 'Failed import still keeps its pre-import recovery backup.');

// UD-112 pre-publish behavior remains guaranteed by the E8 staging model.
$stagingRepo = new InMemoryStagingRepository();
$publishRevisions = new InMemoryRevisionRepository();
$staging = new StagingService($stagingRepo,$publishRevisions);
$staging->saveWorking('page:publish-test',['Version'=>1]);
$staging->publish('page:publish-test',7,'First publish');
$staging->saveWorking('page:publish-test',['Version'=>2]);
$staging->publish('page:publish-test',7,'Second publish');
e13Assert(count($publishRevisions->history('page:publish-test')) === 1, 'Replacing an existing public state must create an automatic pre-publish backup.');
e13Assert(($publishRevisions->history('page:publish-test')[0]['State']['Version'] ?? 0) === 1, 'Pre-publish backup must contain exact previous public state.');

fwrite(STDOUT, "E13 Portability core UD-108..112: PASS\n");
