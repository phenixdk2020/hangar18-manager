<?php

declare(strict_types=1);

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Assets\AssetUsageScanner;
use RuntimeException;

$usage=(new AssetUsageScanner())->scan([
    'data:event:12'=>['MainMediaId'=>['321'],'Other'=>['x']],
    'page:test'=>['Sections'=>[['Key'=>'photo','MediaId'=>321]]],
]);
if(count($usage[321]??[])!==2){throw new RuntimeException('WordPress single-value meta array MediaId was not indexed.');}
$resources=array_column($usage[321],'Resource');
sort($resources,SORT_STRING);
if($resources!==['data:event:12','page:test']){throw new RuntimeException('Usage resources mismatch.');}
fwrite(STDOUT,"I5 WordPress media meta usage: PASS\n");
