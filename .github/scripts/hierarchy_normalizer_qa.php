<?php

declare(strict_types=1);

require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/HierarchyNormalizer.php';

use Hangar18\Clean\Model\HierarchyNormalizer;

function failQa(string $message): void
{
    fwrite(STDERR, "HIERARCHY QA FAIL: {$message}\n");
    exit(1);
}

function assertQa(bool $condition, string $message): void
{
    if (!$condition) {
        failQa($message);
    }
}

function device(int $x, int $y, int $w, int $h, ?bool $inherit = null): array
{
    $value = ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h];
    if ($inherit !== null) {
        $value['inheritDesktop'] = $inherit;
    }
    return $value;
}

function geometry(int $x, int $y, int $w, int $h): array
{
    return [
        'desktop' => device($x, $y, $w, $h),
        'laptop' => device($x + 1, $y + 1, max(1, $w - 2), $h + 1, false),
        'tablet' => device(0, 0, 120, 0, true),
        'mobile' => device(0, 0, 120, $h + 2, false),
    ];
}

function props(int $gapX = 0, int $gapY = 0): array
{
    return [
        'background' => '',
        'radius' => 0,
        'padding' => 0,
        'minHeightRows' => 0,
        'borderWidth' => 0,
        'borderColor' => '#000000',
        'gapX' => $gapX,
        'gapY' => $gapY,
    ];
}

$nodes = [
    'root-section' => [
        'id' => 'root-section',
        'type' => 'section',
        'parentId' => '',
        'order' => 10,
        'geometry' => geometry(0, 0, 120, 20),
        'props' => props(),
    ],
    'nested-section' => [
        'id' => 'nested-section',
        'type' => 'section',
        'parentId' => 'root-section',
        'order' => 10,
        'geometry' => geometry(0, 0, 120, 10),
        'props' => props(),
    ],
    'nested-text' => [
        'id' => 'nested-text',
        'type' => 'text',
        'parentId' => 'nested-section',
        'order' => 10,
        'geometry' => geometry(0, 0, 120, 8),
        'props' => ['gapX' => 0, 'gapY' => 0],
    ],
    'legacy-root-text' => [
        'id' => 'legacy-root-text',
        'type' => 'text',
        'parentId' => '',
        'order' => 20,
        'geometry' => geometry(17, 31, 43, 11),
        'props' => ['gapX' => 9, 'gapY' => 17],
    ],
    'legacy-root-container' => [
        'id' => 'legacy-root-container',
        'type' => 'container',
        'parentId' => '',
        'order' => 30,
        'geometry' => geometry(64, 31, 56, 18),
        'props' => props(4, 12),
    ],
    'container-child' => [
        'id' => 'container-child',
        'type' => 'image',
        'parentId' => 'legacy-root-container',
        'order' => 10,
        'geometry' => geometry(5, 2, 80, 10),
        'props' => ['gapX' => 0, 'gapY' => 0],
    ],
];

$oldTextGeometry = $nodes['legacy-root-text']['geometry'];
$oldContainerGeometry = $nodes['legacy-root-container']['geometry'];

HierarchyNormalizer::normalize($nodes);

assertQa($nodes['nested-section']['type'] === 'container', 'Nested Section was not converted to Kasse/container.');
assertQa($nodes['nested-section']['parentId'] === 'root-section', 'Nested Section parent changed unexpectedly.');
assertQa($nodes['nested-text']['parentId'] === 'nested-section', 'Child of converted nested Section was detached.');

foreach ($nodes as $node) {
    if (($node['parentId'] ?? '') === '') {
        assertQa(($node['type'] ?? '') === 'section', 'A non-Section remains at root after normalization.');
    }
    if (($node['type'] ?? '') === 'section') {
        assertQa(($node['parentId'] ?? '') === '', 'A Section remains nested after normalization.');
    }
}

$text = $nodes['legacy-root-text'];
$textWrapper = $nodes[$text['parentId']] ?? null;
assertQa(is_array($textWrapper), 'Legacy root Text has no wrapper.');
assertQa($textWrapper['type'] === 'section', 'Legacy root Text wrapper is not a Section.');
assertQa($textWrapper['geometry'] === $oldTextGeometry, 'Legacy root Text wrapper did not preserve root geometry.');
assertQa($text['geometry']['desktop']['x'] === 0 && $text['geometry']['desktop']['y'] === 0, 'Legacy Text was not localized inside wrapper.');
assertQa($text['geometry']['desktop']['w'] === 120 && $text['geometry']['desktop']['h'] === 11, 'Legacy Text local desktop geometry is wrong.');
assertQa($text['geometry']['laptop']['inheritDesktop'] === false && $text['geometry']['laptop']['w'] === 120, 'Legacy Text laptop override was not preserved locally.');
assertQa($textWrapper['props']['gapX'] === 9 && $textWrapper['props']['gapY'] === 17, 'Root spacing was not moved to wrapper.');
assertQa($text['props']['gapX'] === 0 && $text['props']['gapY'] === 0, 'Root spacing remained on wrapped child.');

$container = $nodes['legacy-root-container'];
$containerWrapper = $nodes[$container['parentId']] ?? null;
assertQa(is_array($containerWrapper), 'Legacy root Kasse has no wrapper.');
assertQa($containerWrapper['geometry'] === $oldContainerGeometry, 'Legacy root Kasse wrapper did not preserve root geometry.');
assertQa($nodes['container-child']['parentId'] === 'legacy-root-container', 'Descendant of wrapped Kasse was detached.');

$once = serialize($nodes);
HierarchyNormalizer::normalize($nodes);
$twice = serialize($nodes);
assertQa($once === $twice, 'Hierarchy normalization is not idempotent.');

echo "HierarchyNormalizer QA PASS\n";
