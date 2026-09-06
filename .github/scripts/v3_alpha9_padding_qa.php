<?php
declare(strict_types=1);

// Exercise the real model with in-memory WordPress metadata storage.
$metadata = [];
function get_post_meta($id, $key, $single = true) { global $metadata; return $metadata[$id][$key] ?? ''; }
function update_post_meta($id, $key, $value) { global $metadata; $metadata[$id][$key] = $value; return true; }
function sanitize_key($value) { return preg_replace('/[^a-z0-9_-]/', '', strtolower($value)); }
function sanitize_text_field($value) { return strip_tags($value); }
function sanitize_hex_color($value) { return preg_match('/^#(?:[a-f0-9]{3}|[a-f0-9]{6})$/i', $value) ? $value : ''; }
function wp_json_encode($value, $flags = 0) { return json_encode($value, $flags); }

$root = $argv[1] ?? 'build/visual-designer-manager';
require $root . '/src/Model/HierarchyNormalizer.php';
require $root . '/src/Model/LayoutModel.php';
use VisualDesignerManager\Model\LayoutModel;

function check($condition, $label): void {
    if (!$condition) { throw new RuntimeException($label); }
}
function modelWith(array $props): array {
    return ['nodes' => [
        ['id'=>'section', 'type'=>'section', 'parentId'=>'', 'props'=>$props],
        ['id'=>'box', 'type'=>'container', 'parentId'=>'section', 'props'=>$props],
    ]];
}

$sides = ['paddingTop'=>0, 'paddingRight'=>17, 'paddingBottom'=>48, 'paddingLeft'=>240];
$model = modelWith(['padding'=>12] + $sides);
check(LayoutModel::saveVersion(1, $model, 7, 'Padding QA') === 1, 'First save creates version');
$loaded = LayoutModel::get(1);
foreach ($loaded['nodes'] as $node) {
    foreach ($sides as $key=>$value) {
        check(($node['props'][$key] ?? null) === $value, $node['type'] . ': lost ' . $key);
    }
}
check(LayoutModel::saveVersion(1, $loaded, 7, 'Reload QA') === 2, 'Second save creates version');
check(LayoutModel::get(1) === $loaded, 'Save/read cycle must be idempotent');
$history = LayoutModel::history(1);
check(count($history) === 2 && $history[0]['model'] === $loaded, 'History preserves side padding');

$legacy = LayoutModel::normalize(modelWith(['padding'=>23]));
foreach ($legacy['nodes'] as $node) {
    check($node['props']['padding'] === 23, 'Legacy shared padding retained');
    foreach ($sides as $key=>$value) {
        check(!array_key_exists($key, $node['props']), 'Absent side must retain legacy fallback and repair default');
    }
}
$bounded = LayoutModel::normalize(modelWith(['paddingTop'=>-2, 'paddingRight'=>999, 'paddingBottom'=>'34', 'paddingLeft'=>'invalid']));
foreach ($bounded['nodes'] as $node) {
    foreach (['paddingTop'=>0, 'paddingRight'=>240, 'paddingBottom'=>34, 'paddingLeft'=>0] as $key=>$value) {
        check($node['props'][$key] === $value, 'Bounds validation: ' . $key);
    }
}
echo "Alpha.9 section/container padding save/read/history, legacy fallback and bounds: PASS\n";
