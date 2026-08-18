<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();
require_once __DIR__ . '/InMemoryAssetMetadataRepository.php';
require_once __DIR__ . '/FakeImageOptimizer.php';

use Hangar18\UltimateDesigner\Assets\AssetManagerService;
use Hangar18\UltimateDesigner\Assets\AssetUsageScanner;
use Hangar18\UltimateDesigner\Assets\DuplicateAssetDetector;
use Hangar18\UltimateDesigner\Assets\FocalPointResolver;
use Hangar18\UltimateDesigner\Assets\ImageOptimizationPlanner;
use Hangar18\UltimateDesigner\Assets\ImageOptimizationService;
use RuntimeException;

function e9Assert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$repo = new InMemoryAssetMetadataRepository();
$manager = new AssetManagerService($repo);
$a = $manager->save(101, [
    'Folder'=>'Events/2026',
    'Collections'=>['Events','Forside'],
    'Tags'=>['Leopard','Aalborg'],
    'FocalPoint'=>['desktop'=>['X'=>25,'Y'=>40],'mobile'=>['X'=>110,'Y'=>-10]],
    'Copyright'=>'Hangar18',
    'SourceUrl'=>'https://example.test/source',
]);
$manager->save(102, ['Folder'=>'Events/2026','Collections'=>['Events'],'Tags'=>['Aalborg']]);
e9Assert((int) $a['MediaId'] === 101, 'Metadata overlay must preserve native WordPress media ID.');
e9Assert($repo->get(101)['Folder'] === 'Events/2026', 'Folder metadata must be stored without changing media ID.');
e9Assert($manager->filter('Events/2026','Events','Aalborg') === [101,102], 'Asset filters must combine folder/collection/tag.');
$taxonomy = $manager->taxonomy();
e9Assert(in_array('Forside',$taxonomy['collections'],true) && in_array('Leopard',$taxonomy['tags'],true), 'Collections/tags taxonomy must be discoverable.');
e9Assert(($a['FocalPoint']['mobile']['X'] ?? -1) === 100.0 && ($a['FocalPoint']['mobile']['Y'] ?? -1) === 0.0, 'Stored focal points must be clamped.');

$usage = (new AssetUsageScanner())->scan([
    'page:hjem'=>['Sections'=>[['Key'=>'hero','MediaId'=>101],['Key'=>'card','ImageMediaId'=>102]]],
    'component:vehicle-card'=>['Sections'=>[['BackgroundMediaId'=>101]]],
    'data:event:7'=>['MainMediaId'=>103],
]);
e9Assert(count($usage[101] ?? []) === 2, 'Usage inspector must find page/component references to same media ID.');
e9Assert(($usage[103][0]['Resource'] ?? '') === 'data:event:7', 'Usage inspector must include data entry references.');

$focal = (new FocalPointResolver())->resolve(['desktop'=>['X'=>20,'Y'=>30],'mobile'=>['X'=>80,'Y'=>70]]);
e9Assert($focal['desktop']['Css'] === '20% 30%', 'Desktop focal point must map to object-position.');
e9Assert($focal['tablet']['Css'] === '20% 30%', 'Tablet focal point must inherit desktop when no override exists.');
e9Assert($focal['mobile']['Css'] === '80% 70%', 'Mobile focal override must be independent.');

$optimizer = new FakeImageOptimizer(['webp','avif']);
$plan = (new ImageOptimizationPlanner($optimizer))->plan('image/jpeg');
e9Assert($plan['PreserveOriginal'] === true && count($plan['Targets']) === 2, 'Optimization plan must preserve original and select supported modern formats.');
$tmpDir = sys_get_temp_dir() . '/h18-e9-' . bin2hex(random_bytes(4));
mkdir($tmpDir, 0700, true);
$source = $tmpDir . '/photo.jpg';
file_put_contents($source, 'original-image-bytes');
$result = (new ImageOptimizationService($optimizer))->optimize($source, 'image/jpeg', ['Quality'=>82]);
e9Assert($result['preserved'] === true && file_get_contents($source) === 'original-image-bytes', 'Optimization must never replace the original.');
e9Assert(count($result['derivatives']) === 2 && is_file($tmpDir . '/photo.h18.webp') && is_file($tmpDir . '/photo.h18.avif'), 'Optimization pipeline must create namespaced supported derivatives.');
$second = (new ImageOptimizationService($optimizer))->optimize($source, 'image/jpeg', ['Quality'=>82]);
e9Assert(count($second['derivatives']) === 0 && in_array('webp:target-exists',$second['skipped'],true) && in_array('avif:target-exists',$second['skipped'],true), 'Optimization must never overwrite existing derivatives.');

$dup1 = $tmpDir . '/duplicate-a.jpg';
$dup2 = $tmpDir . '/duplicate-b.jpg';
$unique = $tmpDir . '/unique.jpg';
file_put_contents($dup1, 'same');
file_put_contents($dup2, 'same');
file_put_contents($unique, 'different');
$duplicates = (new DuplicateAssetDetector())->detect([201=>$dup1,202=>$dup2,203=>$unique]);
e9Assert(count($duplicates) === 1 && $duplicates[0]['MediaIds'] === [201,202], 'SHA-256 detector must find true duplicates without including unique assets.');
e9Assert(is_file($dup1) && is_file($dup2), 'Duplicate detection must be non-destructive.');

foreach (glob($tmpDir . '/*') ?: [] as $file) { @unlink($file); }
@rmdir($tmpDir);

fwrite(STDOUT, "E9 Assets core UD-089..093: PASS\n");