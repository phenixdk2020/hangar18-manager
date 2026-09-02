<?php

declare(strict_types=1);

require_once __DIR__ . '/../../clean/hangar18-manager/src/Migration/ConvertedButtonOverlayMigration.php';

use VisualDesignerManager\Migration\ConvertedButtonOverlayMigration;

function pass(bool $condition, string $message): void
{
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
    fwrite(STDOUT, "PASS: {$message}\n");
}

$suffix = 'deadbeef';
$model = [
    'schemaVersion' => 1,
    'units' => 120,
    'rowPx' => 8,
    'nodes' => [
        [
            'id' => 'button-deadbeef-10-20',
            'type' => 'button',
            'parentId' => 'section-deadbeef-10',
            'order' => 20,
            'geometry' => ['desktop' => ['x' => 40, 'y' => 10, 'w' => 20, 'h' => 7]],
            'props' => ['text' => 'Konverteret', 'placementMode' => 'normal', 'zIndex' => 20],
        ],
        [
            'id' => 'button-deadbeef-10-30',
            'type' => 'button',
            'parentId' => 'section-deadbeef-10',
            'order' => 30,
            'geometry' => ['desktop' => ['x' => 50, 'y' => 20, 'w' => 20, 'h' => 7]],
            'props' => ['text' => 'Allerede flydende', 'placementMode' => 'overlay', 'zIndex' => 40],
        ],
        [
            'id' => 'button-native-123456',
            'type' => 'button',
            'parentId' => 'section-deadbeef-10',
            'order' => 40,
            'geometry' => ['desktop' => ['x' => 0, 'y' => 0, 'w' => 20, 'h' => 7]],
            'props' => ['text' => 'Normal Designer-knap', 'placementMode' => 'normal', 'zIndex' => 20],
        ],
        [
            'id' => 'button-deadbeef-10-fake',
            'type' => 'text',
            'parentId' => 'section-deadbeef-10',
            'order' => 50,
            'geometry' => ['desktop' => ['x' => 0, 'y' => 0, 'w' => 20, 'h' => 7]],
            'props' => ['text' => 'Ikke en knap', 'placementMode' => 'normal'],
        ],
    ],
];

[$next, $changed] = ConvertedButtonOverlayMigration::upgradeModelForConverter($model, $suffix);
pass($changed === 1, 'only one matching converter-owned normal button is migrated');
pass(($next['nodes'][0]['props']['placementMode'] ?? '') === 'overlay', 'matching converted button becomes overlay');
pass(($next['nodes'][0]['geometry'] ?? null) === ($model['nodes'][0]['geometry'] ?? null), 'converted button geometry is preserved');
pass(($next['nodes'][0]['props']['zIndex'] ?? null) === 20, 'converted button z-index is preserved');
pass(($next['nodes'][1]['props']['placementMode'] ?? '') === 'overlay', 'already floating converted button stays overlay');
pass(($next['nodes'][1]['props']['zIndex'] ?? null) === 40, 'already floating converted button remains otherwise untouched');
pass(($next['nodes'][2]['props']['placementMode'] ?? '') === 'normal', 'ordinary Designer button remains normal');
pass(($next['nodes'][3]['props']['placementMode'] ?? '') === 'normal', 'non-button node with converter-like ID is untouched');

[$again, $changedAgain] = ConvertedButtonOverlayMigration::upgradeModelForConverter($next, $suffix);
pass($changedAgain === 0, 'migration kernel is idempotent');
pass($again === $next, 'second migration pass does not mutate the model');

[$invalid, $invalidCount] = ConvertedButtonOverlayMigration::upgradeModelForConverter($model, 'not-safe');
pass($invalidCount === 0 && $invalid === $model, 'invalid source suffix cannot migrate anything');

fwrite(STDOUT, "Visual Designer Manager v0.1.82 converted button behavior QA: PASS\n");
