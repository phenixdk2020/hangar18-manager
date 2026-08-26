<?php

declare(strict_types=1);

require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/HierarchyNormalizer.php';

use Hangar18\Clean\Model\HierarchyNormalizer;
use Hangar18\Clean\Model\LayoutModel;

/* Minimal WordPress function stubs required by LayoutModel::normalize(). */
if (!function_exists('sanitize_key')) {
    function sanitize_key($value): string
    {
        return strtolower((string) preg_replace('/[^a-z0-9_\-]/i', '', (string) $value));
    }
}
if (!function_exists('sanitize_text_field')) {
    function sanitize_text_field($value): string
    {
        return trim(strip_tags((string) $value));
    }
}
if (!function_exists('wp_kses_post')) {
    function wp_kses_post($value): string
    {
        return (string) $value;
    }
}
if (!function_exists('sanitize_hex_color')) {
    function sanitize_hex_color($value)
    {
        $value = (string) $value;
        return preg_match('/^#[0-9a-f]{6}$/i', $value) ? strtolower($value) : null;
    }
}
if (!function_exists('absint')) {
    function absint($value): int
    {
        return abs((int) $value);
    }
}
if (!function_exists('esc_url_raw')) {
    function esc_url_raw($value): string
    {
        return (string) $value;
    }
}
if (!function_exists('wp_json_encode')) {
    function wp_json_encode($value, int $flags = 0, int $depth = 512)
    {
        return json_encode($value, $flags, $depth);
    }
}

require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/LayoutModel.php';

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

/* Verify the real canonical LayoutModel pipeline, not only the helper class. */
$rawModel = [
    'schemaVersion' => 1,
    'units' => 120,
    'rowPx' => 8,
    'nodes' => [
        [
            'id' => 'legacy-leaf',
            'type' => 'text',
            'parentId' => '',
            'order' => 10,
            'geometry' => geometry(23, 14, 71, 9),
            'props' => [
                'heading' => 'Test',
                'text' => 'Legacy root text',
                'gapX' => 5,
                'gapY' => 13,
            ],
        ],
        [
            'id' => 'root-sec',
            'type' => 'section',
            'parentId' => '',
            'order' => 20,
            'geometry' => geometry(0, 30, 120, 20),
            'props' => props(),
        ],
        [
            'id' => 'nested-sec',
            'type' => 'section',
            'parentId' => 'root-sec',
            'order' => 10,
            'geometry' => geometry(0, 0, 120, 12),
            'props' => props(),
        ],
    ],
];

$canonical = LayoutModel::normalize($rawModel);
$canonicalMap = [];
foreach ($canonical['nodes'] as $node) {
    $canonicalMap[$node['id']] = $node;
    if (($node['parentId'] ?? '') === '') {
        assertQa($node['type'] === 'section', 'LayoutModel pipeline left a non-Section at root.');
    }
    if ($node['type'] === 'section') {
        assertQa(($node['parentId'] ?? '') === '', 'LayoutModel pipeline left a nested Section.');
    }
}
assertQa(isset($canonicalMap['legacy-leaf']), 'LayoutModel pipeline lost legacy leaf content.');
assertQa($canonicalMap['nested-sec']['type'] === 'container', 'LayoutModel pipeline did not convert nested Section to Kasse.');
$wrapperId = (string) $canonicalMap['legacy-leaf']['parentId'];
assertQa($wrapperId !== '' && isset($canonicalMap[$wrapperId]), 'LayoutModel pipeline did not create legacy wrapper Section.');
assertQa($canonicalMap[$wrapperId]['geometry']['desktop']['x'] === 23, 'LayoutModel wrapper lost desktop X geometry.');
assertQa($canonicalMap['legacy-leaf']['geometry']['desktop']['x'] === 0, 'LayoutModel legacy leaf was not localized.');
assertQa($canonicalMap[$wrapperId]['props']['gapY'] === 13, 'LayoutModel wrapper did not inherit root gapY.');

$canonicalAgain = LayoutModel::normalize($canonical);
assertQa(
    wp_json_encode($canonical, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) === wp_json_encode($canonicalAgain, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES),
    'LayoutModel canonical normalization is not idempotent.'
);
assertQa(
    LayoutModel::structuralDigest($canonical) === LayoutModel::structuralDigest($canonicalAgain),
    'LayoutModel structural digest changes after idempotent normalization.'
);

echo "HierarchyNormalizer + LayoutModel QA PASS\n";
