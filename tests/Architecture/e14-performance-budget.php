<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();
require_once __DIR__ . '/InMemoryArtifactRepository.php';

use Hangar18\UltimateDesigner\Portability\ArtifactPackageService;
use Hangar18\UltimateDesigner\Portability\ImportPlanner;
use Hangar18\UltimateDesigner\Quality\SideHealthService;
use RuntimeException;

function e14PerfAssert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$root = dirname(__DIR__, 2);
$siteRuntime = filesize($root . '/assets/site-builder-runtime.js');
$interactionRuntime = filesize($root . '/assets/interaction-runtime.js');
e14PerfAssert(is_int($siteRuntime) && $siteRuntime <= 50 * 1024, 'Site Builder public runtime exceeds 50 KiB budget.');
e14PerfAssert(is_int($interactionRuntime) && $interactionRuntime <= 50 * 1024, 'Interaction public runtime exceeds 50 KiB budget.');

$startMemory = memory_get_usage(true);
$start = microtime(true);
$artifacts = [];
for ($i=1;$i<=1000;$i++) {
    $artifacts[] = [
        'Type'=>$i % 4 === 0 ? 'form' : ($i % 3 === 0 ? 'menu' : ($i % 2 === 0 ? 'template' : 'component')),
        'Id'=>'item-'.$i,
        'Name'=>'Item '.$i,
        'Data'=>['Title'=>'Item '.$i,'Settings'=>['Spacing'=>16,'Enabled'=>true]],
    ];
}
$packages = new ArtifactPackageService();
$json = $packages->export($artifacts);
$imported = $packages->import($json);
$planner = new ImportPlanner(new InMemoryArtifactRepository());
$plan = $planner->plan($imported['Artifacts'],'remap',true);
$elapsed = microtime(true) - $start;
$memoryDelta = max(0,memory_get_peak_usage(true)-$startMemory);
e14PerfAssert(count($plan['Actions']) === 1000, 'Performance fixture did not plan every artifact.');
e14PerfAssert($elapsed < 5.0, '1000-artifact export/import/plan exceeds 5 second CI budget: '.round($elapsed,3).'s');
e14PerfAssert($memoryDelta < 128 * 1024 * 1024, '1000-artifact portability flow exceeds 128 MiB memory budget.');

$sections = [];
$parent = '';
for ($i=1;$i<=120;$i++) {
    $key='section-'.$i;
    $sections[]=['Key'=>$key,'Type'=>$i===1?'heading':'text','HeadingTag'=>$i===1?'h1':'','LayoutParentKey'=>$i<=7?$parent:'','Content'=>str_repeat('x',120)];
    if ($i<=7) { $parent=$key; }
}
$healthStart = microtime(true);
$report = (new SideHealthService())->analyze(['Sections'=>$sections],['Title'=>'Performance fixture','MetaDescription'=>'Performance fixture for CI checks.','Index'=>false],[]);
$healthElapsed = microtime(true)-$healthStart;
e14PerfAssert(isset($report['Score']), 'Side Health performance fixture did not produce report.');
e14PerfAssert($healthElapsed < 2.0, 'Side Health 120-element analysis exceeds 2 second CI budget: '.round($healthElapsed,3).'s');

fwrite(STDOUT, sprintf("E14 performance budget: PASS (runtimes %d/%d bytes, portability %.3fs, health %.3fs)\n",$siteRuntime,$interactionRuntime,$elapsed,$healthElapsed));
