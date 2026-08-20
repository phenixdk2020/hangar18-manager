<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Editor/LegoSpacingModel.php';

use Hangar18\UltimateDesigner\Editor\LegoSpacingModel;

function legoResponsiveAssert(bool $condition, string $message): void
{
    if (!$condition) {
        throw new RuntimeException($message);
    }
}

$defaults = LegoSpacingModel::defaults([
    'LayoutGapPx' => 22,
    'MobileLayoutGapPx' => 14,
]);
legoResponsiveAssert($defaults['SchemaVersion'] === 2, 'Responsive LEGO schema must be version 2.');
legoResponsiveAssert($defaults['Desktop']['Gap'] === ['X'=>22,'Y'=>22], 'Legacy desktop gap must seed both Desktop axes.');
legoResponsiveAssert($defaults['Tablet']['InheritDesktop'] === true, 'New Tablet state must inherit Desktop by default.');
legoResponsiveAssert(LegoSpacingModel::effective($defaults, 'tablet')['Gap'] === ['X'=>22,'Y'=>22], 'Inherited Tablet must resolve to Desktop gap.');
legoResponsiveAssert($defaults['Mobile']['InheritDesktop'] === false, 'Mobile must remain an explicit override by default for backwards compatibility.');
legoResponsiveAssert($defaults['Mobile']['Gap'] === ['X'=>14,'Y'=>14], 'Legacy mobile gap must remain the Mobile override.');

// Simulate a stored v0.8.30/schema-1 state. Mobile values must remain explicit.
$v0830 = LegoSpacingModel::normalize([
    'SchemaVersion' => 1,
    'Desktop' => [
        'Margin' => ['X'=>11,'Y'=>19],
        'Gap' => ['X'=>32,'Y'=>7],
    ],
    'Mobile' => [
        'Margin' => ['X'=>5,'Y'=>9],
        'Gap' => ['X'=>44,'Y'=>17],
    ],
], ['LayoutGapPx'=>16,'MobileLayoutGapPx'=>12]);
legoResponsiveAssert($v0830['Tablet']['InheritDesktop'] === true, 'Schema-1 migration must add inherited Tablet state.');
legoResponsiveAssert(LegoSpacingModel::effective($v0830, 'Tablet')['Margin'] === ['X'=>11,'Y'=>19], 'Migrated Tablet effective margin must follow Desktop.');
legoResponsiveAssert($v0830['Mobile']['InheritDesktop'] === false, 'Schema-1 Mobile must not silently start inheriting Desktop.');
legoResponsiveAssert($v0830['Mobile']['Margin'] === ['X'=>5,'Y'=>9], 'Schema-1 Mobile margin must survive migration.');
legoResponsiveAssert($v0830['Mobile']['Gap'] === ['X'=>44,'Y'=>17], 'Schema-1 Mobile gap must survive migration.');

$overrides = LegoSpacingModel::normalize([
    'SchemaVersion' => 2,
    'Desktop' => [
        'Margin' => ['X'=>10,'Y'=>20],
        'Gap' => ['X'=>30,'Y'=>40],
    ],
    'Tablet' => [
        'InheritDesktop' => false,
        'Margin' => ['X'=>3,'Y'=>4],
        'Gap' => ['X'=>5,'Y'=>6],
    ],
    'Mobile' => [
        'InheritDesktop' => true,
        'Margin' => ['X'=>91,'Y'=>92],
        'Gap' => ['X'=>93,'Y'=>94],
    ],
]);
legoResponsiveAssert(LegoSpacingModel::effective($overrides, 'Tablet')['Margin'] === ['X'=>3,'Y'=>4], 'Tablet override margin must remain independent.');
legoResponsiveAssert(LegoSpacingModel::effective($overrides, 'Tablet')['Gap'] === ['X'=>5,'Y'=>6], 'Tablet override gap must remain independent.');
$effectiveMobile = LegoSpacingModel::effective($overrides, 'Mobile');
legoResponsiveAssert($effectiveMobile['Inherited'] === true, 'Mobile inheritance flag must be reflected in effective state.');
legoResponsiveAssert($effectiveMobile['Margin'] === ['X'=>10,'Y'=>20], 'Inherited Mobile margin must resolve to Desktop.');
legoResponsiveAssert($effectiveMobile['Gap'] === ['X'=>30,'Y'=>40], 'Inherited Mobile gap must resolve to Desktop.');
legoResponsiveAssert($overrides['Mobile']['Margin'] === ['X'=>91,'Y'=>92], 'Enabling inheritance must not delete stored Mobile override margin.');
legoResponsiveAssert($overrides['Mobile']['Gap'] === ['X'=>93,'Y'=>94], 'Enabling inheritance must not delete stored Mobile override gap.');

$clamped = LegoSpacingModel::normalize([
    'Desktop' => ['Margin'=>['X'=>999,'Y'=>-7], 'Gap'=>['X'=>'bad','Y'=>200]],
    'Tablet' => ['InheritDesktop'=>false, 'Margin'=>['X'=>999,'Y'=>-2], 'Gap'=>['X'=>'bad','Y'=>999]],
    'Mobile' => ['InheritDesktop'=>false, 'Margin'=>['X'=>999,'Y'=>-2], 'Gap'=>['X'=>'bad','Y'=>999]],
], ['LayoutGapPx'=>18,'MobileLayoutGapPx'=>13]);
legoResponsiveAssert($clamped['Desktop']['Margin'] === ['X'=>160,'Y'=>0], 'Desktop margin must clamp to safe limits.');
legoResponsiveAssert($clamped['Desktop']['Gap'] === ['X'=>18,'Y'=>160], 'Desktop invalid X must fall back while Y clamps.');
legoResponsiveAssert($clamped['Tablet']['Margin'] === ['X'=>160,'Y'=>0], 'Tablet margin must clamp to safe limits.');
legoResponsiveAssert($clamped['Tablet']['Gap'] === ['X'=>18,'Y'=>160], 'Tablet invalid X must use Desktop fallback while Y clamps.');
legoResponsiveAssert($clamped['Mobile']['Margin'] === ['X'=>120,'Y'=>0], 'Mobile margin must clamp to mobile limits.');
legoResponsiveAssert($clamped['Mobile']['Gap'] === ['X'=>13,'Y'=>120], 'Mobile invalid X must use mobile legacy fallback while Y clamps.');

fwrite(STDOUT, "v0.8.31 LEGO responsive spacing/inheritance model: PASS\n");
