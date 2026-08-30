<?php

declare(strict_types=1);

// In-memory WordPress stubs for deterministic TemplateLayoutModel QA.
$GLOBALS['v0161_options'] = [];
$GLOBALS['v0161_post_meta'] = [];
$GLOBALS['v0161_uuid_counter'] = 0;

function sanitize_key($value): string
{
    $value = strtolower(trim((string) $value));
    $value = preg_replace('/[^a-z0-9_\-]/', '', $value);
    return is_string($value) ? $value : '';
}

function sanitize_text_field($value): string { return trim(strip_tags((string) $value)); }
function sanitize_hex_color($value) { $value = strtolower((string) $value); return preg_match('/^#[0-9a-f]{6}$/', $value) ? $value : null; }
function esc_url_raw($value): string { return (string) $value; }
function wp_kses_post($value): string { return (string) $value; }
function absint($value): int { return abs((int) $value); }
function wp_json_encode($value, $flags = 0) { return json_encode($value, $flags); }
function get_option($key, $default = false) { return array_key_exists((string) $key, $GLOBALS['v0161_options']) ? $GLOBALS['v0161_options'][(string) $key] : $default; }
function update_option($key, $value, $autoload = null): bool { $GLOBALS['v0161_options'][(string) $key] = $value; return true; }
function get_post_meta($postId, $key, $single = false) { return $GLOBALS['v0161_post_meta'][(int) $postId][(string) $key] ?? ($single ? '' : []); }
function update_post_meta($postId, $key, $value): bool { $GLOBALS['v0161_post_meta'][(int) $postId][(string) $key] = $value; return true; }
function wp_generate_uuid4(): string
{
    $GLOBALS['v0161_uuid_counter']++;
    return sprintf('%08x-0000-4000-8000-%012d', $GLOBALS['v0161_uuid_counter'], $GLOBALS['v0161_uuid_counter']);
}

require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/HierarchyNormalizer.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/LayoutModel.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/GlobalLayoutModel.php';
require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/TemplateLayoutModel.php';

use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;

function qa_assert(bool $condition, string $message): void
{
    if (!$condition) {
        fwrite(STDERR, "FAIL: {$message}\n");
        exit(1);
    }
    echo "PASS: {$message}\n";
}

/** @return array<string,array<string,mixed>> */
function nodes_by_id(array $model): array
{
    $result = [];
    foreach (($model['nodes'] ?? []) as $node) {
        if (is_array($node) && isset($node['id'])) {
            $result[(string) $node['id']] = $node;
        }
    }
    return $result;
}

$legacyHeader = LayoutModel::empty();
$legacyHeader['nodes'][] = [
    'id' => 'legacy-header-text',
    'type' => 'text',
    'parentId' => '',
    'order' => 10,
    'geometry' => ['desktop' => ['x' => 0, 'y' => 0, 'w' => 120, 'h' => 8]],
    'props' => ['text' => 'Legacy header'],
];
$legacyFooter = LayoutModel::empty();
$legacyFooter['nodes'][] = [
    'id' => 'legacy-footer-text',
    'type' => 'text',
    'parentId' => '',
    'order' => 10,
    'geometry' => ['desktop' => ['x' => 0, 'y' => 0, 'w' => 120, 'h' => 8]],
    'props' => ['text' => 'Legacy footer'],
];
$GLOBALS['v0161_options']['h18_clean_global_header_layout_v1'] = $legacyHeader;
$GLOBALS['v0161_options']['h18_clean_global_footer_layout_v1'] = $legacyFooter;
$GLOBALS['v0161_options']['h18_clean_global_header_version_v1'] = 3;
$GLOBALS['v0161_options']['h18_clean_global_footer_version_v1'] = 4;

TemplateLayoutModel::ensureMigrated();
$headerNodes = nodes_by_id(TemplateLayoutModel::model('header-standard-v1'));
$footerNodes = nodes_by_id(TemplateLayoutModel::model('footer-standard-v1'));
qa_assert(isset($headerNodes['legacy-header-text']), 'legacy Header-indhold bevares ved migration');
qa_assert(isset($footerNodes['legacy-footer-text']), 'legacy Footer-indhold bevares ved migration');
qa_assert(($headerNodes['legacy-header-text']['props']['text'] ?? '') === 'Legacy header', 'legacy Header-tekst bevares byte-logisk');
qa_assert(($footerNodes['legacy-footer-text']['props']['text'] ?? '') === 'Legacy footer', 'legacy Footer-tekst bevares byte-logisk');
$headerParent = (string) ($headerNodes['legacy-header-text']['parentId'] ?? '');
$footerParent = (string) ($footerNodes['legacy-footer-text']['parentId'] ?? '');
qa_assert($headerParent !== '' && isset($headerNodes[$headerParent]) && ($headerNodes[$headerParent]['type'] ?? '') === 'section', 'legacy Header canonicaliseres sikkert under Section-wrapper');
qa_assert($footerParent !== '' && isset($footerNodes[$footerParent]) && ($footerNodes[$footerParent]['type'] ?? '') === 'section', 'legacy Footer canonicaliseres sikkert under Section-wrapper');
qa_assert(TemplateLayoutModel::version('header-standard-v1') === 3, 'Header-version bevares ved migration');
qa_assert(TemplateLayoutModel::version('footer-standard-v1') === 4, 'Footer-version bevares ved migration');

$header2 = TemplateLayoutModel::create('header', 'Header – QA 2');
$footer2 = TemplateLayoutModel::create('footer', 'Footer – QA 2');
qa_assert(count(TemplateLayoutModel::all('header')) >= 2, 'mindst to Header-templates kan eksistere samtidigt');
qa_assert(count(TemplateLayoutModel::all('footer')) >= 2, 'mindst to Footer-templates kan eksistere samtidigt');

$hVersion = TemplateLayoutModel::saveVersion($header2, LayoutModel::empty(), ['sticky' => true], 1, 'Header QA');
$fVersion = TemplateLayoutModel::saveVersion($footer2, LayoutModel::empty(), [], 1, 'Footer QA');
qa_assert($hVersion === 1 && $fVersion === 1, 'hver template har uafhængig versionshistorik');

TemplateLayoutModel::setDefault('header', $header2);
TemplateLayoutModel::setDefault('footer', $footer2);
qa_assert(TemplateLayoutModel::defaultId('header') === $header2, 'website-standard Header kan vælges');
qa_assert(TemplateLayoutModel::defaultId('footer') === $footer2, 'website-standard Footer kan vælges');

$pageId = 42;
TemplateLayoutModel::setPageChoice($pageId, 'header', 'header-standard-v1');
TemplateLayoutModel::setPageChoice($pageId, 'footer', 'none');
qa_assert(TemplateLayoutModel::resolveId($pageId, 'header') === 'header-standard-v1', 'side kan override Header uafhængigt');
qa_assert(TemplateLayoutModel::resolveId($pageId, 'footer') === '', 'Ingen Footer stopper resolveren eksplicit');

TemplateLayoutModel::setPageChoice($pageId, 'header', 'none');
qa_assert(TemplateLayoutModel::resolveId($pageId, 'header') === '', 'Ingen Header stopper resolveren eksplicit');
TemplateLayoutModel::setPageChoice($pageId, 'header', 'auto');
qa_assert(TemplateLayoutModel::resolveId($pageId, 'header') === $header2, 'Auto resolver til aktiv website-standard');

TemplateLayoutModel::setActive($header2, false);
qa_assert(TemplateLayoutModel::defaultId('header') === 'header-standard-v1', 'inaktiv standard vælges ikke automatisk');
qa_assert(TemplateLayoutModel::resolveChoiceId('header', 'auto') === 'header-standard-v1', 'shared preview/frontend resolver falder deterministisk tilbage til aktiv Header');
qa_assert(TemplateLayoutModel::resolveChoiceId('header', $header2) === 'header-standard-v1', 'inaktiv eksplicit Header falder sikkert tilbage til aktiv standard');
qa_assert(TemplateLayoutModel::resolveChoiceId('footer', 'none') === '', 'shared resolver respekterer Ingen Footer');

$copy = TemplateLayoutModel::duplicate('header-standard-v1', 'Header – QA kopi');
$beforeId = $copy;
TemplateLayoutModel::rename($copy, 'Header – QA omdøbt');
qa_assert($beforeId === $copy && (TemplateLayoutModel::meta($copy)['name'] ?? '') === 'Header – QA omdøbt', 'omdøbning bevarer stabilt template-ID');

$first = TemplateLayoutModel::resolveChoiceId('header', 'auto');
$second = TemplateLayoutModel::resolveChoiceId('header', 'auto');
qa_assert($first === $second, 'resolveren er deterministisk');

echo "v0.1.61 Header/Footer Definition of Done QA PASS\n";
