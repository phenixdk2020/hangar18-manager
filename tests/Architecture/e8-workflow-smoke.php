<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();
require_once __DIR__ . '/InMemoryRevisionRepository.php';
require_once __DIR__ . '/InMemoryStagingRepository.php';

use Hangar18\UltimateDesigner\Workflow\PreviewService;
use Hangar18\UltimateDesigner\Workflow\PreviewTokenService;
use Hangar18\UltimateDesigner\Workflow\RevisionService;
use Hangar18\UltimateDesigner\Workflow\StagingService;
use Hangar18\UltimateDesigner\Workflow\StructuredRevisionDiff;
use RuntimeException;

function e8Assert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$revisions = new InMemoryRevisionRepository();
$service = new RevisionService($revisions);
$resource = 'page:hjem';
$state1 = ['Sections'=>[['Key'=>'a','Type'=>'text','Title'=>'Hej']], 'PageTitle'=>'Hjem'];
$state2 = ['Sections'=>[['Key'=>'a','Type'=>'text','Title'=>'Hej verden'],['Key'=>'b','Type'=>'image']], 'PageTitle'=>'Hjem'];

$auto = $service->autosave($resource, $state1, 7);
e8Assert(($auto['State']['PageTitle'] ?? '') === 'Hjem', 'Autosave must retain working state.');
e8Assert(count($service->history($resource)) === 0, 'Autosave must not create permanent revision spam.');
$rev1 = $service->save($resource, $state1, 7, 'Første gem');
e8Assert(count($service->history($resource)) === 1, 'Manual save must create permanent revision.');
e8Assert($service->recoverAutosave($resource) === null, 'Manual save must clear autosave snapshot.');
$rev2 = $service->save($resource, $state2, 7, 'Anden gem');
e8Assert((int) $rev2['Sequence'] === 2, 'Revision sequence must increase.');
$restored = $service->restore($resource, (string) $rev1['Id'], 8, 'Gendan første');
e8Assert((string) $restored['RestoreOf'] === (string) $rev1['Id'], 'Restore must append a new revision referencing its source.');
e8Assert(count($service->history($resource)) === 3, 'Restore must preserve history rather than overwrite it.');

$diff = (new StructuredRevisionDiff())->diff($state1, $state2);
e8Assert(count($diff['added']) === 1, 'Structured diff must report added sections.');
e8Assert(count($diff['changed']) === 1, 'Structured diff must report changed section properties.');
e8Assert(($diff['added'][0]['Key'] ?? '') === 'b', 'Structured diff must retain added element key.');
e8Assert(($diff['changed'][0]['Properties'][0]['Property'] ?? '') === 'Title', 'Structured diff must name changed property.');

$stagingRepo = new InMemoryStagingRepository();
$staging = new StagingService($stagingRepo, $revisions);
$staging->saveWorking($resource, $state1);
e8Assert(($staging->working($resource)['PageTitle'] ?? '') === 'Hjem', 'Working state must be independently readable.');
$firstPublish = $staging->publish($resource, 7, 'Publicér første');
e8Assert(($firstPublish['State']['PageTitle'] ?? '') === 'Hjem', 'Publish must promote working state.');
e8Assert($staging->published($resource) === $state1, 'Published state must equal promoted working state.');
$beforeSecond = count($revisions->history($resource));
$staging->saveWorking($resource, $state2);
$staging->publish($resource, 7, 'Publicér anden');
e8Assert($staging->published($resource) === $state2, 'Second publish must atomically replace public state.');
e8Assert(count($revisions->history($resource)) === $beforeSecond + 1, 'Publishing over existing public state must create pre-publish backup revision.');

$tokens = new PreviewTokenService(str_repeat('x', 48));
$issued = $tokens->issue($resource, 'mobile', 600);
$claims = $tokens->validate($issued['token']);
e8Assert(is_array($claims) && $claims['device'] === 'mobile' && $claims['resource'] === $resource, 'Preview token must validate resource/device claims.');
$preview = new PreviewService($tokens, $stagingRepo);
$resolved = $preview->resolve($issued['token']);
e8Assert(is_array($resolved) && ($resolved['state']['PageTitle'] ?? '') === 'Hjem', 'Preview must resolve unpublished working state read-only.');
$tokens->revoke($issued['token']);
e8Assert($tokens->validate($issued['token']) === null, 'Revoked preview token must be rejected.');
e8Assert($tokens->validate('not-a-token') === null, 'Malformed preview token must fail closed.');

fwrite(STDOUT, "E8 Workflow core UD-081..088: PASS\n");
