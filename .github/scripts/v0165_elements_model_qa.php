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

require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/HierarchyNormalizer.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/LayoutModel.php';

use VisualDesignerManager\Model\LayoutModel;

function fail165(string $message): void { fwrite(STDERR, "V0165 ELEMENT MODEL QA FAIL: {$message}\n"); exit(1); }
function assert165(bool $condition, string $message): void { if (!$condition) { fail165($message); } }

function geo165(int $x, int $y, int $w, int $h): array
{
    return [
        'desktop' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h],
        'laptop' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h, 'inheritDesktop' => true],
        'tablet' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h, 'inheritDesktop' => true],
        'mobile' => ['x' => 0, 'y' => $y, 'w' => 120, 'h' => $h, 'inheritDesktop' => true],
    ];
}

$headers = [];
for ($i = 1; $i <= 14; $i++) { $headers[] = 'Kolonne ' . $i; }

$raw = [
    'nodes' => [
        ['id' => 'section-elements', 'type' => 'section', 'parentId' => '', 'order' => 10, 'geometry' => geo165(0, 0, 120, 80), 'props' => ['background' => '#ffffff', 'minHeightRows' => 80]],
        ['id' => 'spacer-a', 'type' => 'spacer', 'parentId' => 'section-elements', 'order' => 10, 'geometry' => geo165(0, 0, 120, 4), 'props' => []],
        ['id' => 'divider-a', 'type' => 'divider', 'parentId' => 'section-elements', 'order' => 20, 'geometry' => geo165(0, 5, 120, 4), 'props' => ['orientation' => 'vertical', 'lineColor' => '#C3C4C7', 'lineWidth' => 3, 'lineStyle' => 'dashed']],
        ['id' => 'icon-a', 'type' => 'icon', 'parentId' => 'section-elements', 'order' => 30, 'geometry' => geo165(0, 10, 20, 8), 'props' => ['icon' => 'not-an-icon', 'iconSize' => 44, 'iconColor' => '#30382A', 'align' => 'right']],
        ['id' => 'badge-a', 'type' => 'badge', 'parentId' => 'section-elements', 'order' => 40, 'geometry' => geo165(22, 10, 30, 8), 'props' => ['text' => '<b>Operativ</b>', 'background' => '#C3AE83', 'textColor' => '#30382A', 'fontWeight' => 800]],
        ['id' => 'link-a', 'type' => 'link', 'parentId' => 'section-elements', 'order' => 50, 'geometry' => geo165(54, 10, 30, 8), 'props' => ['text' => 'Læs mere →', 'linkType' => 'page', 'pageId' => 42, 'targetBlank' => true, 'underline' => true]],
        ['id' => 'datalist-a', 'type' => 'datalist', 'parentId' => 'section-elements', 'order' => 60, 'geometry' => geo165(0, 20, 60, 20), 'props' => [
            'rows' => [
                ['label' => 'Motor', 'value' => 'Detroit Diesel'],
                ['label' => '', 'value' => ''],
                ['label' => '<b>Vægt</b>', 'value' => '12.300 kg'],
            ],
            'layout' => 'stacked', 'labelWidth' => 55, 'cellPadding' => 9, 'showDividers' => false, 'zebra' => true,
        ]],
        ['id' => 'table-a', 'type' => 'table', 'parentId' => 'section-elements', 'order' => 70, 'geometry' => geo165(0, 42, 120, 25), 'props' => [
            'headers' => $headers,
            'rows' => [
                ['M113', 'Bæltekøretøj', 'Operativ'],
                ['Unimog', 'Hjulkøretøj', 'Restaurering'],
            ],
            'cellBorderWidth' => 0,
            'mobileMode' => 'cards',
            'zebra' => false,
        ]],
    ],
];

$model = LayoutModel::normalize($raw);
$byId = [];
foreach ($model['nodes'] as $node) { $byId[(string) $node['id']] = $node; }

foreach (['spacer-a' => 'spacer', 'divider-a' => 'divider', 'icon-a' => 'icon', 'badge-a' => 'badge', 'link-a' => 'link', 'datalist-a' => 'datalist', 'table-a' => 'table'] as $id => $type) {
    assert165(isset($byId[$id]), "{$type} disappeared during normalization");
    assert165(($byId[$id]['type'] ?? '') === $type, "{$type} type changed during normalization");
}

assert165(($byId['divider-a']['props']['orientation'] ?? '') === 'vertical', 'Divider orientation was lost');
assert165(($byId['divider-a']['props']['lineColor'] ?? '') === '#c3c4c7', 'Divider color was not normalized');
assert165(($byId['icon-a']['props']['icon'] ?? '') === 'star', 'Invalid icon token did not fall back to star');
assert165((int) ($byId['icon-a']['props']['iconSize'] ?? 0) === 44, 'Icon size was lost');
assert165(($byId['badge-a']['props']['text'] ?? '') === 'Operativ', 'Badge text was not sanitized');
assert165(($byId['link-a']['props']['linkType'] ?? '') === 'page' && (int) ($byId['link-a']['props']['pageId'] ?? 0) === 42, 'Link page binding was lost');
assert165(!empty($byId['link-a']['props']['underline']), 'Link underline setting was lost');

$dataRows = $byId['datalist-a']['props']['rows'] ?? [];
assert165(is_array($dataRows) && count($dataRows) === 2, 'Data List did not remove the empty row');
assert165(($dataRows[1]['label'] ?? '') === 'Vægt', 'Data List label was not sanitized');
assert165(($byId['datalist-a']['props']['layout'] ?? '') === 'stacked', 'Data List layout was lost');
assert165(empty($byId['datalist-a']['props']['showDividers']), 'Data List divider toggle was lost');

$table = $byId['table-a']['props'];
assert165(is_array($table['headers'] ?? null) && count($table['headers']) === 12, 'Table headers were not capped at 12');
assert165(is_array($table['rows'] ?? null) && count($table['rows']) === 2, 'Table rows were lost');
assert165(count($table['rows'][0]) === 12, 'Table rows were not normalized to header column count');
assert165((int) ($table['cellBorderWidth'] ?? -1) === 0, 'Table 0px cell border was not retained');
assert165(($table['mobileMode'] ?? '') === 'cards', 'Table mobile card mode was lost');
assert165(empty($table['zebra']), 'Table zebra=false was not retained');

$again = LayoutModel::normalize($model);
assert165(json_encode($again, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES) === json_encode($model, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES), 'General element model normalization is not idempotent');

fwrite(STDOUT, "V0165 ELEMENT MODEL QA OK\n");
