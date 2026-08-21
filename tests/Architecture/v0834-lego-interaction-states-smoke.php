<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Editor\LegoDesignModel;
use Hangar18\UltimateDesigner\Editor\LegoInteractionStateModel;
use Hangar18\UltimateDesigner\Editor\LegoResponsiveDesignModel;

require_once dirname(__DIR__, 2) . '/src/Editor/LegoDesignModel.php';
require_once dirname(__DIR__, 2) . '/src/Editor/LegoInteractionStateModel.php';
require_once dirname(__DIR__, 2) . '/src/Editor/LegoResponsiveDesignModel.php';

function h18InteractionAssert(bool $ok, string $message): void
{
    if (!$ok) {
        throw new RuntimeException($message);
    }
}

$desktop = LegoDesignModel::fromLegacy([
    'DesignMode' => 'Custom',
    'CustomBackgroundColor' => '#112233',
    'RadiusPx' => 13,
    'TransitionPreset' => 'Slow',
    'FocusRingStyle' => 'Custom',
    'FocusRingColor' => '#123456',
    'FocusRingWidthPx' => 5,
    'FocusRingOffsetPx' => 4,
    'ActiveEffect' => 'ScaleDown',
    'DisabledOpacityPercent' => 42,
]);

h18InteractionAssert(LegoDesignModel::SCHEMA_VERSION === 2, 'Common design schema must be v2 for interaction states.');
h18InteractionAssert(($desktop['Motion']['Transition'] ?? '') === 'Slow', 'Transition must normalize into common design state.');
h18InteractionAssert(($desktop['States']['Focus']['Style'] ?? '') === 'Custom', 'Focus style missing from common design state.');
h18InteractionAssert(($desktop['States']['Focus']['Color'] ?? '') === '#123456', 'Focus color missing from common design state.');
h18InteractionAssert(($desktop['States']['Focus']['Width'] ?? 0) === 5, 'Focus width missing from common design state.');
h18InteractionAssert(($desktop['States']['Active']['Effect'] ?? '') === 'ScaleDown', 'Active effect missing from common design state.');
h18InteractionAssert(($desktop['States']['Disabled']['Opacity'] ?? 0) === 42, 'Disabled opacity missing from common design state.');

$interaction = LegoInteractionStateModel::fromDesign($desktop);
h18InteractionAssert(($interaction['Motion']['Transition'] ?? '') === 'Slow', 'Interaction subset must read transition.');
h18InteractionAssert(($interaction['Focus']['Offset'] ?? 0) === 4, 'Interaction subset must read focus offset.');
h18InteractionAssert(($interaction['Active']['Effect'] ?? '') === 'ScaleDown', 'Interaction subset must read active effect.');

$changed = $interaction;
$changed['Motion']['Transition'] = 'Fast';
$changed['Focus']['Style'] = 'None';
$changed['Focus']['Color'] = '#abcdef';
$changed['Focus']['Width'] = 8;
$changed['Focus']['Offset'] = 12;
$changed['Active']['Effect'] = 'Press';
$changed['Disabled']['Opacity'] = 31;
$merged = LegoInteractionStateModel::mergeIntoDesign($desktop, $changed);

h18InteractionAssert(($merged['Colors']['Background'] ?? '') === '#112233', 'Merging interaction state must not change base colors.');
h18InteractionAssert(($merged['Radius']['All'] ?? 0) === 13, 'Merging interaction state must not change radius.');
h18InteractionAssert(($merged['Motion']['Transition'] ?? '') === 'Fast', 'Merged transition missing.');
h18InteractionAssert(($merged['States']['Focus']['Style'] ?? '') === 'None', 'Merged focus style missing.');
h18InteractionAssert(($merged['States']['Active']['Effect'] ?? '') === 'Press', 'Merged active effect missing.');
h18InteractionAssert(($merged['States']['Disabled']['Opacity'] ?? 0) === 31, 'Merged disabled opacity missing.');

$invalid = LegoInteractionStateModel::normalize([
    'Motion' => ['Transition' => 'Turbo'],
    'Focus' => ['Style' => 'Laser', 'Color' => 'red', 'Width' => 99, 'Offset' => -5],
    'Active' => ['Effect' => 'Bounce'],
    'Disabled' => ['Opacity' => 2],
], $desktop);
h18InteractionAssert(($invalid['Motion']['Transition'] ?? '') === 'Slow', 'Invalid transition must fall back to current design.');
h18InteractionAssert(($invalid['Focus']['Style'] ?? '') === 'Custom', 'Invalid focus style must fall back to current design.');
h18InteractionAssert(($invalid['Focus']['Width'] ?? 0) === 8, 'Focus width must clamp at 8.');
h18InteractionAssert(($invalid['Focus']['Offset'] ?? -1) === 0, 'Focus offset must clamp at 0.');
h18InteractionAssert(($invalid['Active']['Effect'] ?? '') === 'ScaleDown', 'Invalid active effect must fall back.');
h18InteractionAssert(($invalid['Disabled']['Opacity'] ?? 0) === 10, 'Disabled opacity must clamp at 10.');

$responsive = LegoResponsiveDesignModel::defaults($desktop);
$responsive = LegoResponsiveDesignModel::setInheritance($responsive, $desktop, 'Tablet', false);
$responsive['Tablet']['Design'] = LegoInteractionStateModel::mergeIntoDesign(
    $responsive['Tablet']['Design'],
    [
        'Motion' => ['Transition' => 'Fast'],
        'Focus' => ['Style' => 'Custom', 'Color' => '#654321', 'Width' => 6, 'Offset' => 3],
        'Active' => ['Effect' => 'Press'],
        'Disabled' => ['Opacity' => 37],
    ]
);
$responsive = LegoResponsiveDesignModel::normalize($responsive, $desktop);
$effective = LegoResponsiveDesignModel::effective($responsive, $desktop, 'Tablet');
h18InteractionAssert(($effective['Design']['States']['Focus']['Color'] ?? '') === '#654321', 'Responsive model must preserve focus override inside Design.');
h18InteractionAssert(($effective['Design']['States']['Active']['Effect'] ?? '') === 'Press', 'Responsive model must preserve active override inside Design.');
h18InteractionAssert(($effective['Design']['States']['Disabled']['Opacity'] ?? 0) === 37, 'Responsive model must preserve disabled override inside Design.');

$responsive = LegoResponsiveDesignModel::setInheritance($responsive, $desktop, 'Tablet', true);
h18InteractionAssert(($responsive['Tablet']['Design']['States']['Focus']['Color'] ?? '') === '#654321', 'Turning design inheritance on must not erase interaction snapshot.');
$responsive = LegoResponsiveDesignModel::setInheritance($responsive, $desktop, 'Tablet', false);
$effective = LegoResponsiveDesignModel::effective($responsive, $desktop, 'Tablet');
h18InteractionAssert(($effective['Design']['States']['Focus']['Color'] ?? '') === '#654321', 'Interaction snapshot must return after inheritance cycle.');

echo "v0.8.34 LEGO interaction state model smoke: PASS\n";
