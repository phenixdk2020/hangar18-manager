<?php

declare(strict_types=1);

$GLOBALS['vd_options'] = [];
$GLOBALS['vd_post_meta'] = [];
$GLOBALS['vd_uuid_counter'] = 0;

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
if (!function_exists('get_option')) {
    function get_option($name, $default = false) { return array_key_exists((string) $name, $GLOBALS['vd_options']) ? $GLOBALS['vd_options'][(string) $name] : $default; }
}
if (!function_exists('update_option')) {
    function update_option($name, $value, $autoload = null): bool { $GLOBALS['vd_options'][(string) $name] = $value; return true; }
}
if (!function_exists('get_post_meta')) {
    function get_post_meta($postId, $key = '', $single = false) {
        $postId = (int) $postId;
        $key = (string) $key;
        if (!isset($GLOBALS['vd_post_meta'][$postId]) || !array_key_exists($key, $GLOBALS['vd_post_meta'][$postId])) { return $single ? '' : []; }
        $value = $GLOBALS['vd_post_meta'][$postId][$key];
        return $single ? $value : [$value];
    }
}
if (!function_exists('update_post_meta')) {
    function update_post_meta($postId, $key, $value): bool { $GLOBALS['vd_post_meta'][(int) $postId][(string) $key] = $value; return true; }
}
if (!function_exists('wp_generate_uuid4')) {
    function wp_generate_uuid4(): string {
        $GLOBALS['vd_uuid_counter']++;
        $counter = (int) $GLOBALS['vd_uuid_counter'];
        return sprintf('%08x-%04x-4000-8000-%012x', $counter, $counter & 0xffff, $counter);
    }
}

require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/HierarchyNormalizer.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/LayoutModel.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/GlobalLayoutModel.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/TemplateLayoutModel.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Migration/LegacyHeaderConverter.php';

use Hangar18\Clean\Model\LayoutModel;
use Hangar18\Clean\Model\TemplateLayoutModel;
use Hangar18\Clean\Migration\LegacyHeaderConverter;

function vdFail(string $message): void { fwrite(STDERR, "V0125 MODEL QA FAIL: {$message}\n"); exit(1); }
function vdAssert(bool $condition, string $message): void { if (!$condition) { vdFail($message); } }

function vdGeometry(int $x, int $y, int $w, int $h): array
{
    return [
        'desktop' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h],
        'laptop' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h, 'inheritDesktop' => true],
        'tablet' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h, 'inheritDesktop' => true],
        'mobile' => ['x' => $x, 'y' => $y, 'w' => $w, 'h' => $h, 'inheritDesktop' => true],
    ];
}

/* Button is a canonical leaf and its public properties are normalized. */
$buttonModel = LayoutModel::normalize([
    'nodes' => [
        [
            'id' => 'section-a', 'type' => 'section', 'parentId' => '', 'order' => 10,
            'geometry' => vdGeometry(0, 0, 120, 20),
            'props' => ['background' => '#ffffff', 'padding' => 0, 'minHeightRows' => 20],
        ],
        [
            'id' => 'button-a', 'type' => 'button', 'parentId' => 'section-a', 'order' => 10,
            'geometry' => vdGeometry(10, 2, 30, 8),
            'props' => [
                'text' => 'Læs mere', 'linkType' => 'page', 'pageId' => 42,
                'targetBlank' => true, 'background' => '#30382A', 'textColor' => '#FFFFFF',
                'hoverBackground' => '#525A5F', 'hoverTextColor' => '#FFFFFF', 'focusColor' => '#C3AE83',
                'paddingX' => 24, 'paddingY' => 12, 'radius' => 9,
            ],
        ],
    ],
]);
$button = null;
foreach ($buttonModel['nodes'] as $node) { if (($node['id'] ?? '') === 'button-a') { $button = $node; break; } }
vdAssert(is_array($button), 'Button disappeared during canonical normalization.');
vdAssert(($button['type'] ?? '') === 'button', 'Button type was not retained.');
vdAssert(($button['props']['linkType'] ?? '') === 'page', 'Button link type was not retained.');
vdAssert((int) ($button['props']['pageId'] ?? 0) === 42, 'Button internal page ID was not retained.');
vdAssert(($button['props']['background'] ?? '') === '#30382a', 'Button background was not normalized.');
vdAssert((int) ($button['props']['radius'] ?? -1) === 9, 'Button radius was not retained.');


/* Menu is a canonical leaf whose content comes from a WordPress menu reference. */
$menuModel = LayoutModel::normalize([
    'nodes' => [
        [
            'id' => 'section-menu', 'type' => 'section', 'parentId' => '', 'order' => 10,
            'geometry' => vdGeometry(0, 0, 120, 12),
            'props' => ['background' => '#30382a', 'padding' => 0, 'minHeightRows' => 12],
        ],
        [
            'id' => 'menu-a', 'type' => 'menu', 'parentId' => 'section-menu', 'order' => 10,
            'geometry' => vdGeometry(40, 1, 80, 10),
            'props' => ['menuId' => 6, 'orientation' => 'horizontal', 'align' => 'right', 'mobileMode' => 'hamburger', 'textColor' => '#FFFFFF', 'menuGap' => 28],
        ],
    ],
]);
$menuNode = null;
foreach ($menuModel['nodes'] as $node) { if (($node['id'] ?? '') === 'menu-a') { $menuNode = $node; break; } }
vdAssert(is_array($menuNode), 'Menu disappeared during canonical normalization.');
vdAssert(($menuNode['type'] ?? '') === 'menu', 'Menu canonical type was not retained.');
vdAssert((int) ($menuNode['props']['menuId'] ?? 0) === 6, 'Menu WordPress source ID was not retained.');
vdAssert(($menuNode['props']['mobileMode'] ?? '') === 'hamburger', 'Menu mobile mode was not retained.');
vdAssert(($menuNode['props']['textColor'] ?? '') === '#ffffff', 'Menu text color was not normalized.');

/* Seed phase-1 single Header/Footer storage exactly as an existing 0.1.23 site could have it. */
$legacyHeader = LayoutModel::normalize([
    'nodes' => [[
        'id' => 'legacy-header-section', 'type' => 'section', 'parentId' => '', 'order' => 10,
        'geometry' => vdGeometry(0, 0, 120, 12),
        'props' => ['background' => '#30382a', 'padding' => 0, 'minHeightRows' => 12],
    ]],
]);
$legacyFooter = LayoutModel::normalize([
    'nodes' => [[
        'id' => 'legacy-footer-section', 'type' => 'section', 'parentId' => '', 'order' => 10,
        'geometry' => vdGeometry(0, 0, 120, 14),
        'props' => ['background' => '#525a5f', 'padding' => 0, 'minHeightRows' => 14],
    ]],
]);
$GLOBALS['vd_options']['h18_clean_global_header_layout_v1'] = $legacyHeader;
$GLOBALS['vd_options']['h18_clean_global_footer_layout_v1'] = $legacyFooter;
$GLOBALS['vd_options']['h18_clean_global_header_settings_v1'] = ['enabled' => true, 'sticky' => true, 'overlay' => false, 'contentWidth' => 1280];
$GLOBALS['vd_options']['h18_clean_global_footer_settings_v1'] = ['enabled' => true, 'contentWidth' => 1280];
$GLOBALS['vd_options']['h18_clean_global_header_history_v1'] = [[
    'version' => 1, 'savedUtc' => '2026-08-26T10:00:00+00:00', 'userId' => 1,
    'note' => 'Eksisterende Header', 'digest' => 'legacy', 'model' => $legacyHeader,
    'settings' => ['enabled' => true, 'sticky' => true, 'overlay' => false, 'contentWidth' => 1280],
]];
$GLOBALS['vd_options']['h18_clean_global_footer_history_v1'] = [];
$GLOBALS['vd_options']['h18_clean_global_header_version_v1'] = 1;
$GLOBALS['vd_options']['h18_clean_global_footer_version_v1'] = 0;

TemplateLayoutModel::ensureMigrated();
$headers = TemplateLayoutModel::all('header');
$footers = TemplateLayoutModel::all('footer');
vdAssert(count($headers) === 1, 'Migration did not create exactly one standard Header.');
vdAssert(count($footers) === 1, 'Migration did not create exactly one standard Footer.');
vdAssert(TemplateLayoutModel::defaultId('header') === 'header-standard-v1', 'Migrated Header is not the website default.');
vdAssert(TemplateLayoutModel::defaultId('footer') === 'footer-standard-v1', 'Migrated Footer is not the website default.');
vdAssert(TemplateLayoutModel::version('header-standard-v1') === 1, 'Migrated Header version was not preserved.');
vdAssert(count(TemplateLayoutModel::history('header-standard-v1')) === 1, 'Migrated Header history was not preserved.');
vdAssert(LayoutModel::structuralDigest(TemplateLayoutModel::model('header-standard-v1')) === LayoutModel::structuralDigest($legacyHeader), 'Migrated Header model changed.');
vdAssert(!empty(TemplateLayoutModel::settings('header-standard-v1')['sticky']), 'Migrated Header sticky setting was lost.');

/* Named templates can be created, renamed, duplicated and independently defaulted. */
$secondHeader = TemplateLayoutModel::create('header', 'Header – Forside');
vdAssert(TemplateLayoutModel::exists($secondHeader, 'header'), 'New Header template was not created.');
TemplateLayoutModel::rename($secondHeader, 'Header – Hjem');
vdAssert((TemplateLayoutModel::meta($secondHeader)['name'] ?? '') === 'Header – Hjem', 'Header rename failed.');
$copyHeader = TemplateLayoutModel::duplicate($secondHeader, 'Header – Hjem kopi');
vdAssert($copyHeader !== $secondHeader && TemplateLayoutModel::exists($copyHeader, 'header'), 'Header duplicate failed.');
TemplateLayoutModel::setDefault('header', $secondHeader);
vdAssert(TemplateLayoutModel::defaultId('header') === $secondHeader, 'Changing website-default Header failed.');
vdAssert(TemplateLayoutModel::defaultId('footer') === 'footer-standard-v1', 'Changing Header default changed Footer default.');

/* Each template owns its own version history. */
$version1 = TemplateLayoutModel::saveVersion($secondHeader, $buttonModel, ['sticky' => false, 'overlay' => false, 'contentWidth' => 1440], 7, 'Tilføjet Knap');
$version2 = TemplateLayoutModel::saveVersion($secondHeader, $buttonModel, ['sticky' => true, 'overlay' => false, 'contentWidth' => 1440], 7, 'Ændret Sticky Header');
vdAssert($version1 === 1 && $version2 === 2, 'Per-template version counter is wrong.');
vdAssert(count(TemplateLayoutModel::history($secondHeader)) === 2, 'Per-template history count is wrong.');
vdAssert(TemplateLayoutModel::version('header-standard-v1') === 1, 'Saving a second Header changed the migrated Header version.');

/* Page-level Header/Footer choice is independent and deterministic. */
$postId = 99;
TemplateLayoutModel::setPageChoice($postId, 'header', 'auto');
TemplateLayoutModel::setPageChoice($postId, 'footer', 'auto');
vdAssert(TemplateLayoutModel::resolveId($postId, 'header') === $secondHeader, 'Auto Header did not resolve to current default.');
vdAssert(TemplateLayoutModel::resolveId($postId, 'footer') === 'footer-standard-v1', 'Auto Footer did not resolve to Footer default.');
TemplateLayoutModel::setPageChoice($postId, 'header', 'header-standard-v1');
vdAssert(TemplateLayoutModel::resolveId($postId, 'header') === 'header-standard-v1', 'Explicit Header override failed.');
TemplateLayoutModel::setPageChoice($postId, 'footer', 'none');
vdAssert(TemplateLayoutModel::resolveId($postId, 'footer') === '', 'Explicit no-Footer choice did not stop resolution.');

/* An inactive explicit template cannot be selected at runtime; resolver falls back to active default. */
TemplateLayoutModel::setActive('header-standard-v1', false);
TemplateLayoutModel::setPageChoice($postId, 'header', 'header-standard-v1');
vdAssert(TemplateLayoutModel::resolveId($postId, 'header') === $secondHeader, 'Inactive explicit Header did not fall back to active default.');

/* Idempotent migration: rerunning must never duplicate templates or history. */
$beforeHeaders = TemplateLayoutModel::all('header');
$beforeHistory = TemplateLayoutModel::history('header-standard-v1');
TemplateLayoutModel::ensureMigrated();
vdAssert(count(TemplateLayoutModel::all('header')) === count($beforeHeaders), 'Migration is not idempotent.');
vdAssert(count(TemplateLayoutModel::history('header-standard-v1')) === count($beforeHistory), 'Migration duplicated historical versions.');

/* Legacy HeaderDesign is converted into a canonical editable Header model. */
$convertedHeader = LegacyHeaderConverter::buildModelFromLegacyDesign([
    'DesktopContentWidthPercent' => 90,
    'LaptopContentWidthPercent' => 95,
    'ShowBrand' => true,
    'BrandText' => 'Aalborg Kaserners Veteran Panser- og Køretøjsforening',
    'ShowLogo' => true,
    'LogoMediaId' => 55,
    'LogoUrl' => 'https://example.test/logo.png',
    'MenuAlignment' => 'Right',
    'BackgroundMode' => 'None',
    'TextColor' => '#30382a',
    'AccentColor' => '#c3ae83',
    'MenuFontWeight' => 'Semibold',
], 77);
$convertedByType = [];
foreach ($convertedHeader['nodes'] as $node) { $convertedByType[(string) ($node['type'] ?? '')][] = $node; }
vdAssert(count($convertedByType['section'] ?? []) === 1, 'Legacy Header conversion must create one root Section.');
vdAssert(count($convertedByType['container'] ?? []) === 1, 'Legacy Header conversion must create one inner Container.');
vdAssert(count($convertedByType['image'] ?? []) === 1, 'Legacy Header logo was not converted to Image.');
vdAssert(count($convertedByType['text'] ?? []) === 1, 'Legacy Header brand was not converted to Text.');
vdAssert(count($convertedByType['menu'] ?? []) === 1, 'Legacy Header menu was not converted to Menu.');
$convertedSection = ($convertedByType['section'] ?? [])[0] ?? [];
$convertedMenu = ($convertedByType['menu'] ?? [])[0] ?? [];
vdAssert((int) ($convertedSection['geometry']['desktop']['x'] ?? -1) === 6, '90 percent legacy Header width did not center at X=6.');
vdAssert((int) ($convertedSection['geometry']['desktop']['w'] ?? -1) === 108, '90 percent legacy Header width did not become 108/120 units.');
vdAssert((int) ($convertedMenu['props']['menuId'] ?? 0) === 77, 'Legacy active WordPress menu ID was not retained.');
vdAssert(($convertedMenu['props']['textColor'] ?? '') === '#30382a', 'Transparent legacy Header did not retain dark menu text.');
vdAssert((int) ($convertedMenu['props']['fontWeight'] ?? 0) === 600, 'Legacy Semibold menu weight was not converted.');
vdAssert((int) ($convertedMenu['geometry']['mobile']['w'] ?? 0) === 30, 'Converted mobile Menu must reserve the right-side hamburger area.');
vdAssert(empty($convertedMenu['geometry']['mobile']['inheritDesktop']), 'Converted mobile Menu geometry must be explicit.');

echo "Visual Designer Manager 0.1.41 model QA PASS\n";
