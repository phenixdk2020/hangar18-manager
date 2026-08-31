<?php

declare(strict_types=1);

if (!function_exists('sanitize_key')) {
    function sanitize_key($value): string { return strtolower((string) preg_replace('/[^a-z0-9_\-]/i', '', (string) $value)); }
}
if (!function_exists('sanitize_text_field')) {
    function sanitize_text_field($value): string { return trim(strip_tags((string) $value)); }
}
if (!function_exists('wp_kses_post')) {
    function wp_kses_post($value): string { return (string) $value; }
}
if (!function_exists('sanitize_hex_color')) {
    function sanitize_hex_color($value) { $value = (string) $value; return preg_match('/^#[0-9a-f]{6}$/i', $value) ? strtolower($value) : null; }
}
if (!function_exists('absint')) {
    function absint($value): int { return abs((int) $value); }
}
if (!function_exists('esc_url_raw')) {
    function esc_url_raw($value): string { return (string) $value; }
}
if (!function_exists('wp_json_encode')) {
    function wp_json_encode($value, int $flags = 0, int $depth = 512) { return json_encode($value, $flags, $depth); }
}
if (!function_exists('apply_filters')) {
    function apply_filters($hook, $value) { return $value; }
}

require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/HierarchyNormalizer.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/LayoutModel.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Migration/CanvasSectionMigration.php';

use VisualDesignerManager\Migration\CanvasSectionMigration;
use VisualDesignerManager\Model\HierarchyNormalizer;
use VisualDesignerManager\Model\LayoutModel;

function qaFail(string $message): void
{
    fwrite(STDERR, "V0168 CANVAS SECTION QA FAIL: {$message}\n");
    exit(1);
}

function qaAssert(bool $condition, string $message): void
{
    if (!$condition) { qaFail($message); }
}

function dev(int $x, int $y, int $w, int $h, ?bool $inherit = null): array
{
    $row = ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h];
    if ($inherit !== null) { $row['inheritDesktop'] = $inherit; }
    return $row;
}

function geom(int $x, int $y, int $w, int $h): array
{
    return [
        'desktop' => dev($x, $y, $w, $h),
        'laptop' => dev($x, $y, $w, $h, true),
        'tablet' => dev($x, $y, $w, $h, true),
        'mobile' => dev(0, 0, 120, $h, true),
    ];
}

$legacy = [
    'schemaVersion' => 1,
    'units' => 120,
    'rowPx' => 8,
    'nodes' => [
        [
            'id' => 'legacy-root-text',
            'type' => 'text',
            'parentId' => '',
            'order' => 10,
            'geometry' => geom(18, 7, 70, 9),
            'props' => ['heading' => '', 'text' => 'Bevar mig', 'gapX' => 5, 'gapY' => 11],
        ],
        [
            'id' => 'root-section',
            'type' => 'section',
            'parentId' => '',
            'order' => 20,
            'geometry' => geom(0, 20, 120, 20),
            'props' => ['background' => '', 'gapX' => 0, 'gapY' => 0],
        ],
        [
            'id' => 'nested-section',
            'type' => 'section',
            'parentId' => 'root-section',
            'order' => 10,
            'geometry' => geom(0, 0, 120, 10),
            'props' => ['background' => '', 'gapX' => 0, 'gapY' => 0],
        ],
        [
            'id' => 'nested-text',
            'type' => 'text',
            'parentId' => 'nested-section',
            'order' => 10,
            'geometry' => geom(0, 0, 120, 8),
            'props' => ['heading' => '', 'text' => 'Barn'],
        ],
    ],
];

qaAssert(CanvasSectionMigration::TARGET_VERSION === '0.1.68', 'Wrong target version.');
qaAssert(CanvasSectionMigration::BACKUP_META === '_h18_clean_layout_pre_section_v0168', 'Backup meta contract changed.');
qaAssert(str_contains(CanvasSectionMigration::NOTE, 'Section-struktur'), 'Migration version note is missing.');
qaAssert(CanvasSectionMigration::needsMigration($legacy), 'Legacy root/nested Section model was not detected.');

$normalized = LayoutModel::normalize($legacy);
qaAssert(HierarchyNormalizer::isCanonical($normalized['nodes']), 'Normalized model is not canonical.');

$map = [];
foreach ($normalized['nodes'] as $node) { $map[$node['id']] = $node; }
foreach (['legacy-root-text', 'root-section', 'nested-section', 'nested-text'] as $id) {
    qaAssert(isset($map[$id]), 'Original node ID was lost: ' . $id);
}
qaAssert($map['nested-section']['type'] === 'container', 'Nested Section was not converted to Kasse/container.');
qaAssert($map['nested-section']['parentId'] === 'root-section', 'Nested Section parent changed.');
qaAssert($map['legacy-root-text']['parentId'] !== '', 'Legacy root Text was not wrapped.');
$wrapperId = $map['legacy-root-text']['parentId'];
qaAssert(isset($map[$wrapperId]) && $map[$wrapperId]['type'] === 'section', 'Legacy root wrapper is not a Section.');
qaAssert($map[$wrapperId]['parentId'] === '', 'Wrapper Section is not root.');
qaAssert($map[$wrapperId]['geometry']['desktop']['x'] === 18, 'Wrapper did not preserve root X geometry.');
qaAssert($map['legacy-root-text']['geometry']['desktop']['x'] === 0, 'Wrapped child was not localized.');
qaAssert($map['legacy-root-text']['geometry']['desktop']['w'] === 120, 'Wrapped child was not localized to full Section width.');
qaAssert($map[$wrapperId]['props']['gapY'] === 11, 'Root gapY was not moved to wrapper.');
qaAssert($map['legacy-root-text']['props']['gapY'] === 0, 'Root gapY remained on wrapped child.');
qaAssert(!CanvasSectionMigration::needsMigration($normalized), 'Canonical normalized model still reports migration needed.');

$canonicalAgain = LayoutModel::normalize($normalized);
qaAssert(
    wp_json_encode($normalized, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) === wp_json_encode($canonicalAgain, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES),
    'v0.1.68 hierarchy normalization is not idempotent.'
);

$rootContainer = $normalized;
$rootContainer['nodes'][] = [
    'id' => 'bad-root-container',
    'type' => 'container',
    'parentId' => '',
    'order' => 999,
    'geometry' => geom(0, 50, 120, 8),
    'props' => ['background' => ''],
];
qaAssert(CanvasSectionMigration::needsMigration($rootContainer), 'Root Kasse was not detected as non-canonical.');

$cycle = [
    'nodes' => [
        ['id' => 'a', 'type' => 'container', 'parentId' => 'b'],
        ['id' => 'b', 'type' => 'container', 'parentId' => 'a'],
    ],
];
qaAssert(CanvasSectionMigration::needsMigration($cycle), 'Hierarchy cycle was not detected.');
qaAssert(!HierarchyNormalizer::isCanonical($cycle['nodes']), 'Canonical validator accepted a cycle.');

print("V0168 CANVAS SECTION QA OK\n");
