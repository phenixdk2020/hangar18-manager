<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Editor/LegoSpacingModel.php';

use Hangar18\UltimateDesigner\Editor\LegoSpacingModel;

function legoAssert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$legacy = LegoSpacingModel::defaults([
    'LayoutGapPx' => 22,
    'MobileLayoutGapPx' => 14,
]);
legoAssert($legacy['SchemaVersion'] === 1, 'LEGO spacing schema must be explicit.');
legoAssert($legacy['Desktop']['Gap']['X'] === 22 && $legacy['Desktop']['Gap']['Y'] === 22, 'Legacy desktop gap must seed both X and Y.');
legoAssert($legacy['Mobile']['Gap']['X'] === 14 && $legacy['Mobile']['Gap']['Y'] === 14, 'Legacy mobile gap must seed both X and Y.');
legoAssert($legacy['Desktop']['Margin'] === ['X'=>0,'Y'=>0], 'Element margin must start neutral.');

$custom = LegoSpacingModel::normalize([
    'Desktop' => [
        'Margin' => ['X'=>11,'Y'=>19],
        'Gap' => ['X'=>32,'Y'=>7],
    ],
    'Mobile' => [
        'Margin' => ['X'=>5,'Y'=>9],
        'Gap' => ['X'=>120,'Y'=>17],
    ],
], ['LayoutGapPx'=>16,'MobileLayoutGapPx'=>12]);
legoAssert($custom['Desktop']['Margin'] === ['X'=>11,'Y'=>19], 'Desktop X/Y margin must remain independent.');
legoAssert($custom['Desktop']['Gap'] === ['X'=>32,'Y'=>7], 'Desktop X/Y gap must remain independent.');
legoAssert($custom['Mobile']['Margin'] === ['X'=>5,'Y'=>9], 'Mobile X/Y margin must remain independent.');
legoAssert($custom['Mobile']['Gap'] === ['X'=>120,'Y'=>17], 'Mobile X/Y gap must remain independent.');

$clamped = LegoSpacingModel::normalize([
    'Desktop' => ['Margin'=>['X'=>999,'Y'=>-7], 'Gap'=>['X'=>'bad','Y'=>200]],
    'Mobile' => ['Margin'=>['X'=>999,'Y'=>-2], 'Gap'=>['X'=>'bad','Y'=>999]],
], ['LayoutGapPx'=>18,'MobileLayoutGapPx'=>13]);
legoAssert($clamped['Desktop']['Margin'] === ['X'=>160,'Y'=>0], 'Desktop margin must clamp to safe limits.');
legoAssert($clamped['Desktop']['Gap'] === ['X'=>18,'Y'=>160], 'Desktop invalid X must fall back while Y clamps independently.');
legoAssert($clamped['Mobile']['Margin'] === ['X'=>120,'Y'=>0], 'Mobile margin must clamp to mobile limits.');
legoAssert($clamped['Mobile']['Gap'] === ['X'=>13,'Y'=>120], 'Mobile invalid X must fall back while Y clamps independently.');

fwrite(STDOUT, "v0.8.30 LEGO canonical X/Y spacing model: PASS\n");
