<?php

declare(strict_types=1);

$GLOBALS['v0167_actions'] = [];
$GLOBALS['v0167_post_types'] = [];

if (!function_exists('sanitize_key')) {
    function sanitize_key($value): string { return strtolower((string) preg_replace('/[^a-z0-9_\-]/i', '', (string) $value)); }
}
if (!function_exists('sanitize_text_field')) {
    function sanitize_text_field($value): string { return trim(strip_tags((string) $value)); }
}
if (!function_exists('sanitize_textarea_field')) {
    function sanitize_textarea_field($value): string { return trim(strip_tags((string) $value)); }
}
if (!function_exists('sanitize_title')) {
    function sanitize_title($value): string {
        $value = strtolower(trim(strip_tags((string) $value)));
        $value = preg_replace('/[^a-z0-9]+/i', '-', $value);
        return trim((string) $value, '-');
    }
}
if (!function_exists('wp_kses_post')) {
    function wp_kses_post($value): string { return strip_tags((string) $value, '<b><strong><em><i><p><br><ul><ol><li>'); }
}
if (!function_exists('absint')) {
    function absint($value): int { return abs((int) $value); }
}
if (!function_exists('esc_url_raw')) {
    function esc_url_raw($value): string { return trim((string) $value); }
}
if (!function_exists('wp_json_encode')) {
    function wp_json_encode($value, int $flags = 0, int $depth = 512) { return json_encode($value, $flags, $depth); }
}
if (!function_exists('add_action')) {
    function add_action($hook, $callback): void { $GLOBALS['v0167_actions'][(string) $hook][] = $callback; }
}
if (!function_exists('post_type_exists')) {
    function post_type_exists($postType): bool { return isset($GLOBALS['v0167_post_types'][(string) $postType]); }
}
if (!function_exists('register_post_type')) {
    function register_post_type($postType, $args) { $GLOBALS['v0167_post_types'][(string) $postType] = $args; return (object) ['name' => $postType]; }
}

require_once __DIR__ . '/../../clean/hangar18-manager/src/Modules/ModuleRegistry.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Modules/ModuleRecord.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Modules/ModuleBinding.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Modules/ModuleStore.php';

use VisualDesignerManager\Modules\ModuleBinding;
use VisualDesignerManager\Modules\ModuleRecord;
use VisualDesignerManager\Modules\ModuleRegistry;
use VisualDesignerManager\Modules\ModuleStore;

function fail167(string $message): void { fwrite(STDERR, "V0167 MODULE FOUNDATION QA FAIL: {$message}\n"); exit(1); }
function assert167(bool $condition, string $message): void { if (!$condition) { fail167($message); } }

$all = ModuleRegistry::all();
assert167(array_keys($all) === ['vehicles', 'events', 'galleries'], 'Registry module keys changed');
assert167(ModuleRegistry::key('vehicle') === 'vehicles', 'Vehicle alias not normalized');
assert167(ModuleRegistry::key('album') === 'galleries', 'Album alias not normalized');
assert167(ModuleRegistry::supports('events'), 'Events missing from registry');
assert167(!ModuleRegistry::supports('unknown'), 'Unknown module incorrectly supported');
assert167(isset(ModuleRegistry::fieldDefinitions('vehicles')['description']), 'Vehicle description field missing');
assert167(isset(ModuleRegistry::fieldDefinitions('events')['start']), 'Event start field missing');
assert167(isset(ModuleRegistry::fieldDefinitions('galleries')['imageIds']), 'Gallery image list field missing');

$catalog = ModuleRegistry::editorCatalog();
assert167(($catalog['schema'] ?? 0) === 1, 'Editor catalog schema mismatch');
assert167(count($catalog['modules'] ?? []) === 3, 'Editor catalog module count mismatch');

$vehicle = ModuleRecord::normalize('vehicle', [
    'id' => 'VEHICLE:001',
    'title' => '<b>M113</b>',
    'status' => 'PUBLISH',
    'sortOrder' => 20,
    'featuredMediaId' => -45,
    'summary' => '<b>Bæltekøretøj</b>',
    'fields' => [
        'description' => '<p><strong>Historisk</strong> køretøj</p>',
        'category' => '<i>Bæltekøretøj</i>',
        'ignored' => 'må ikke med',
    ],
    'attributes' => [
        ['key' => 'weight', 'label' => 'Vægt', 'type' => 'text', 'value' => '<b>12.300 kg</b>', 'enabled' => true, 'order' => 20],
        ['key' => 'year', 'label' => 'Årgang', 'type' => 'integer', 'value' => '1968', 'enabled' => false, 'order' => 10],
    ],
]);
assert167(($vehicle['module'] ?? '') === 'vehicles', 'Record module alias not canonical');
assert167(($vehicle['id'] ?? '') === 'vehicle:001', 'Record ID not normalized');
assert167(($vehicle['title'] ?? '') === 'M113', 'Record title not sanitized');
assert167(($vehicle['status'] ?? '') === 'publish', 'Record status not normalized');
assert167(($vehicle['featuredMediaId'] ?? 0) === 45, 'Featured media ID not normalized');
assert167(!isset(($vehicle['fields'] ?? [])['ignored']), 'Unknown standard field leaked into record');
assert167(($vehicle['fields']['category'] ?? '') === 'Bæltekøretøj', 'Vehicle category not sanitized');
assert167(count($vehicle['attributes'] ?? []) === 2, 'Dynamic attributes lost');
assert167(($vehicle['attributes'][0]['key'] ?? '') === 'year', 'Attributes not sorted canonically');
assert167(($vehicle['attributes'][0]['value'] ?? 0) === 1968, 'Integer attribute not normalized');
assert167(($vehicle['attributes'][1]['value'] ?? '') === '12.300 kg', 'Text attribute not sanitized');

$gallery = ModuleRecord::normalize('galleries', [
    'title' => 'Sommertræf',
    'fields' => ['imageIds' => [5, '5', 8, 0, -12]],
]);
assert167(($gallery['fields']['imageIds'] ?? []) === [5, 8, 12], 'Gallery media list not normalized/unique');

$invalid = ModuleRecord::normalize('vehicles', ['id' => 'spaces are invalid']);
assert167(($invalid['id'] ?? 'x') === '', 'Invalid record ID was retained');
$unknown = ModuleRecord::normalize('unknown', ['title' => 'X']);
assert167($unknown === [], 'Unknown module record was not rejected');

$again = ModuleRecord::normalize('vehicles', $vehicle);
assert167(ModuleRecord::canonicalJson($again) === ModuleRecord::canonicalJson($vehicle), 'Record normalization is not idempotent');
assert167(ModuleRecord::digest($again) === ModuleRecord::digest($vehicle), 'Record digest is not stable');

$binding = ModuleBinding::normalize([
    'mode' => 'module',
    'module' => 'vehicle',
    'view' => 'detail',
    'recordId' => 'vehicle:001',
    'query' => ['status' => 'all', 'orderBy' => 'title', 'order' => 'desc', 'limit' => 999],
    'fieldMap' => ['Heading' => 'title', 'Spec Weight' => 'weight'],
]);
assert167(ModuleBinding::isDynamic($binding), 'Valid module binding not dynamic');
assert167(($binding['module'] ?? '') === 'vehicles', 'Binding module not canonical');
assert167(($binding['recordId'] ?? '') === 'vehicle:001', 'Detail record ID lost');
assert167(($binding['query']['limit'] ?? 0) === 100, 'Binding limit not clamped');
assert167(($binding['query']['order'] ?? '') === 'DESC', 'Binding order not normalized');
assert167(($binding['fieldMap']['heading'] ?? '') === 'title', 'Binding field map not sanitized');

$fallback = ModuleBinding::normalize(['mode' => 'module', 'module' => 'unknown']);
assert167(($fallback['mode'] ?? '') === 'static' && ($fallback['module'] ?? 'x') === '', 'Unknown module binding did not fall back to static');

ModuleStore::register();
assert167(isset($GLOBALS['v0167_actions']['init'][0]), 'ModuleStore did not register init hook');
ModuleStore::registerPostType();
assert167(isset($GLOBALS['v0167_post_types'][ModuleStore::POST_TYPE]), 'ModuleStore post type not registered');
$args = $GLOBALS['v0167_post_types'][ModuleStore::POST_TYPE];
assert167(($args['public'] ?? true) === false, 'Module storage post type must remain private');
assert167(($args['show_ui'] ?? true) === false, 'Module storage post type must not leak into native WP admin');
assert167(($args['show_in_rest'] ?? true) === false, 'Module storage post type must not be exposed through REST by default');

fwrite(STDOUT, "V0167 MODULE FOUNDATION QA OK\n");
