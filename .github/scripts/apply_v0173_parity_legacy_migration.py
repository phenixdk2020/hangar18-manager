from __future__ import annotations

from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[2]


def read(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f'Missing required file: {path}')
    return p.read_text(encoding='utf-8')


def write(path: str, value: str) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(value, encoding='utf-8')


def replace_once(path: str, old: str, new: str) -> None:
    value = read(path)
    if new in value:
        return
    if old not in value:
        raise SystemExit(f'{path}: replacement anchor missing: {old[:140]}')
    write(path, value.replace(old, new, 1))


def append_once(path: str, marker: str, addition: str) -> None:
    value = read(path)
    if marker in value:
        return
    write(path, value.rstrip() + '\n\n' + addition.strip() + '\n')


PLUGIN = 'clean/hangar18-manager/hangar18-manager.php'
CONVERSION = 'clean/hangar18-manager/src/Admin/ConversionController.php'
RESPONSIVE = 'clean/hangar18-manager/src/Frontend/ResponsiveRenderer.php'
RENDERER = 'clean/hangar18-manager/src/Frontend/Renderer.php'
CORE = 'clean/hangar18-manager/assets/editor-v018-core.js'
VIEWPORT = 'clean/hangar18-manager/assets/editor-v0144-viewport.js'

# ---------------------------------------------------------------------------
# Version and bootstrap
# ---------------------------------------------------------------------------
replace_once(PLUGIN, ' * Version: 0.1.72', ' * Version: 0.1.73')
replace_once(PLUGIN, "define('H18_CLEAN_VERSION', '0.1.72');", "define('H18_CLEAN_VERSION', '0.1.73');")
replace_once(PLUGIN,
    "require_once H18_CLEAN_DIR . 'src/Migration/PageConversionService.php';",
    "require_once H18_CLEAN_DIR . 'src/Migration/PageConversionService.php';\n"
    "require_once H18_CLEAN_DIR . 'src/Migration/LegacyMediaImporter.php';\n"
    "require_once H18_CLEAN_DIR . 'src/Migration/LegacyModuleSourceService.php';\n"
    "require_once H18_CLEAN_DIR . 'src/Migration/LegacyModuleMigrationService.php';")
replace_once(PLUGIN,
    "require_once H18_CLEAN_DIR . 'src/Admin/ConversionController.php';",
    "require_once H18_CLEAN_DIR . 'src/Admin/ConversionController.php';\n"
    "require_once H18_CLEAN_DIR . 'src/Admin/LegacyMigrationController.php';")
replace_once(PLUGIN,
    "    \\VisualDesignerManager\\Admin\\ConversionController::register();",
    "    \\VisualDesignerManager\\Admin\\ConversionController::register();\n"
    "    \\VisualDesignerManager\\Admin\\LegacyMigrationController::register();")
replace_once(PLUGIN,
    "    wp_enqueue_style(\n        'h18-clean-editor-v0166-foundation',\n        H18_CLEAN_URL . 'assets/editor-v0166-foundation.css',\n        ['h18-clean-editor-v0165-elements'],\n        H18_CLEAN_VERSION\n    );",
    "    wp_enqueue_style(\n        'h18-clean-editor-v0166-foundation',\n        H18_CLEAN_URL . 'assets/editor-v0166-foundation.css',\n        ['h18-clean-editor-v0165-elements'],\n        H18_CLEAN_VERSION\n    );\n"
    "    wp_enqueue_style(\n        'h18-clean-editor-v0173-parity',\n        H18_CLEAN_URL . 'assets/editor-v0173-parity.css',\n        ['h18-clean-editor-v0166-foundation'],\n        H18_CLEAN_VERSION\n    );")

# ---------------------------------------------------------------------------
# VD-RENDER-PARITY-001: editor chrome is zero-layout-impact.
# ---------------------------------------------------------------------------
write('clean/hangar18-manager/assets/editor-v0173-parity.css', r'''/* Visual Designer Manager 0.1.73
 * VD-RENDER-PARITY-001
 * Designer chrome must never change the canonical content box.
 */
.h18-clean-workspace .h18-clean-node--section>.h18-clean-inner-surface,
.h18-clean-workspace .h18-clean-node--container>.h18-clean-inner-surface{
    margin:0!important;
    min-height:0!important;
    border:0!important;
    outline:1px dashed #a7aaad;
    outline-offset:-1px;
    box-sizing:border-box;
}
.h18-clean-workspace .h18-clean-node--section>.h18-clean-inner-surface.is-drop-target,
.h18-clean-workspace .h18-clean-node--container>.h18-clean-inner-surface.is-drop-target{
    outline:3px solid #2271b1;
    outline-offset:-3px;
    box-shadow:none!important;
}
/* Text padding is applied inline from canonical props by editor-v018-core.js. */
.h18-clean-workspace .h18-clean-node-preview--text{padding:0}
''')

# Text preview used a hard-coded editor padding from editor.css; frontend uses props.padding.
replace_once(CORE,
    "            wrap.style.boxSizing = 'border-box';\n            wrap.style.fontFamily = fontCss(node.props.fontFamily || 'system');",
    "            wrap.style.boxSizing = 'border-box';\n            wrap.style.padding = String(Math.max(0, parseInt(node.props.padding || 0, 10) || 0)) + 'px';\n            wrap.style.fontFamily = fontCss(node.props.fontFamily || 'system');")

# Exact visual comparison should start at 100%; Fit remains an explicit work zoom.
replace_once(VIEWPORT, "    var mode = 'fit';", "    var mode = 'manual';")
replace_once(VIEWPORT,
    "        window.addEventListener('pageshow', function () { mode = 'fit'; window.requestAnimationFrame(setFit); }, { passive: true });",
    "        window.addEventListener('pageshow', function () { mode = 'manual'; window.requestAnimationFrame(function(){ setManual(1, null); }); }, { passive: true });")
replace_once(VIEWPORT,
    "            if (event.target.closest('.h18-clean-device-button')) {\n                mode = 'fit';\n                window.requestAnimationFrame(schedule);\n                return;\n            }",
    "            if (event.target.closest('.h18-clean-device-button')) {\n                window.requestAnimationFrame(schedule);\n                return;\n            }")
replace_once(VIEWPORT,
    "        mode = 'fit';\n        currentScale = 1;\n        setFit();",
    "        mode = 'manual';\n        currentScale = 1;\n        setManual(1, null);")
replace_once(VIEWPORT,
    "            status.title = mode === 'fit'\n                ? 'Virtuel frontendbredde. Fit følger automatisk den ledige editorbredde.'\n                : 'Manuel canvas-zoom. Layoutets virtuelle geometri er uændret.';",
    "            status.title = mode === 'fit'\n                ? 'Fit er arbejdszoom og skalerer canvas visuelt. Brug 100% til 1:1 visuel sammenligning.'\n                : (Math.abs(currentScale - 1) < 0.001 ? '1:1-visning: CSS-pixelstørrelser vises uden editor-skalering.' : 'Manuel canvas-zoom. Layoutets canonical geometri er uændret.');")

# ---------------------------------------------------------------------------
# Responsive Page/Header/Footer parity. The existing renderer only emitted page
# breakpoint rules. Replace ResponsiveRenderer with a scoped multi-model layer.
# ---------------------------------------------------------------------------
write(RESPONSIVE, r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Frontend;

use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;

/**
 * VD-RENDER-PARITY-001 responsive geometry layer.
 * Page, resolved Header and resolved Footer are rendered from the same canonical
 * geometry and receive the same breakpoint algorithm.
 */
final class ResponsiveRenderer
{
    public const LAPTOP_MAX = 1180;
    public const MOBILE_MAX = 782;

    public static function register(): void
    {
        add_action('wp_head', [self::class, 'css'], 1001);
    }

    public static function css(): void
    {
        if (!is_singular('page')) { return; }
        $postId = get_queried_object_id();
        if ($postId <= 0) { return; }
        $page = self::model($postId);
        if ($page === null) { return; }

        $models = [['scope' => '.h18-vd-live-shell-page', 'model' => $page]];
        foreach (['header', 'footer'] as $type) {
            $id = ThemeShell::resolvedTemplateId($postId, $type);
            if ($id === '' || !TemplateLayoutModel::exists($id, $type)) { continue; }
            $models[] = [
                'scope' => $type === 'header' ? '.h18-vd-live-shell-header' : '.h18-vd-live-shell-footer',
                'model' => TemplateLayoutModel::model($id),
            ];
        }
        echo self::styleTag($models, 'h18-clean-responsive-css');
    }

    /**
     * Responsive CSS used by Renderer::standaloneDocument so its Header/Page/
     * Footer preview follows exactly the same breakpoint rules as frontend.
     * @param array<string,mixed> $page
     * @param array<string,mixed>|null $header
     * @param array<string,mixed>|null $footer
     */
    public static function standaloneStyle(array $page, ?array $header, ?array $footer): string
    {
        $models = [['scope' => '.h18-vd-composite-main', 'model' => LayoutModel::normalize($page)]];
        if ($header !== null) { $models[] = ['scope' => '.h18-vd-composite-header', 'model' => LayoutModel::normalize($header)]; }
        if ($footer !== null) { $models[] = ['scope' => '.h18-vd-composite-footer', 'model' => LayoutModel::normalize($footer)]; }
        return self::styleTag($models, 'h18-clean-responsive-preview-css');
    }

    /** @param array<int,array{scope:string,model:array<string,mixed>}> $models */
    private static function styleTag(array $models, string $id): string
    {
        $laptop = '';
        $mobile = '';
        foreach ($models as $entry) {
            $scope = trim((string) ($entry['scope'] ?? ''));
            $model = isset($entry['model']) && is_array($entry['model']) ? $entry['model'] : [];
            if ($scope === '' || empty($model['nodes']) || !is_array($model['nodes'])) { continue; }
            [$byId, $byParent] = self::index($model);
            foreach ($byId as $nodeId => $node) {
                $lg = self::effectiveGeometry($node, 'laptop');
                $mg = self::effectiveGeometry($node, 'mobile');
                $laptopRows = self::effectiveRows($nodeId, 'laptop', $byId, $byParent, []);
                $mobileRows = self::effectiveRows($nodeId, 'mobile', $byId, $byParent, []);
                $selector = $scope . ' #h18-clean-' . self::cssId($nodeId);
                $props = is_array($node['props'] ?? null) ? $node['props'] : [];
                $floating = (string) ($node['type'] ?? '') === 'button' && (string) ($props['placementMode'] ?? 'normal') === 'overlay';
                $zIndex = max(1, min(200, (int) ($props['zIndex'] ?? 20)));
                $laptop .= self::geometryCss($selector, $lg, $laptopRows, $floating, $zIndex);
                $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);
            }
        }
        return '<style id="' . esc_attr($id) . '">.h18-clean-page{max-width:100%;overflow-x:clip}'
            . '@media(max-width:' . self::LAPTOP_MAX . 'px){' . $laptop . '}'
            . '@media(max-width:' . self::MOBILE_MAX . 'px){' . $mobile . '}</style>';
    }

    /** @param array<string,mixed> $model @return array{0:array<string,array<string,mixed>>,1:array<string,array<int,array<string,mixed>>>} */
    private static function index(array $model): array
    {
        $byId = []; $byParent = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $id = (string) $node['id'];
            $byId[$id] = $node;
            $byParent[(string) ($node['parentId'] ?? '')][] = $node;
        }
        return [$byId, $byParent];
    }

    /** @return array<string,mixed>|null */
    private static function model(int $postId): ?array
    {
        $preview = self::previewModel($postId);
        if ($preview !== null) { return $preview; }
        if (!metadata_exists('post', $postId, LayoutModel::META)) { return null; }
        return LayoutModel::get($postId);
    }

    /** @return array<string,mixed>|null */
    private static function previewModel(int $postId): ?array
    {
        if (!is_user_logged_in() || !current_user_can('edit_pages')) { return null; }
        $token = isset($_GET['h18_clean_preview']) ? sanitize_key((string) wp_unslash($_GET['h18_clean_preview'])) : '';
        if ($token === '' || !preg_match('/^[a-z0-9]{12,64}$/', $token)) { return null; }
        $raw = get_transient(Renderer::previewKey(get_current_user_id(), $postId, $token));
        if (!is_array($raw)) { return null; }
        try { return LayoutModel::normalize($raw); } catch (\Throwable $error) { return null; }
    }

    /** @param array<string,mixed> $node @return array{x:int,y:int,w:int,h:int} */
    private static function effectiveGeometry(array $node, string $device): array
    {
        $geometry = is_array($node['geometry'] ?? null) ? $node['geometry'] : [];
        $desktop = self::geometry($geometry['desktop'] ?? null);
        if ($device === 'desktop') { return $desktop; }
        $laptopRaw = is_array($geometry['laptop'] ?? null) ? $geometry['laptop'] : [];
        $laptop = !empty($laptopRaw['inheritDesktop']) ? $desktop : self::geometry($laptopRaw, $desktop);
        if ($device === 'laptop') { return $laptop; }
        $mobileRaw = is_array($geometry['mobile'] ?? null) ? $geometry['mobile'] : [];
        return !empty($mobileRaw['inheritDesktop']) ? $laptop : self::geometry($mobileRaw, $laptop);
    }

    /** @param mixed $raw @param array{x:int,y:int,w:int,h:int}|null $fallback @return array{x:int,y:int,w:int,h:int} */
    private static function geometry(mixed $raw, ?array $fallback = null): array
    {
        $fallback ??= ['x' => 0, 'y' => 0, 'w' => LayoutModel::UNITS, 'h' => 0];
        if (!is_array($raw)) { return $fallback; }
        $x = max(0, min(LayoutModel::UNITS - 1, (int) ($raw['x'] ?? $fallback['x'])));
        $w = max(1, min(LayoutModel::UNITS - $x, (int) ($raw['w'] ?? $fallback['w'])));
        return ['x' => $x, 'y' => max(0, min(10000, (int) ($raw['y'] ?? $fallback['y']))), 'w' => $w, 'h' => max(0, min(4000, (int) ($raw['h'] ?? $fallback['h'])))];
    }

    /** @param array<string,array<string,mixed>> $byId @param array<string,array<int,array<string,mixed>>> $byParent @param array<string,bool> $seen */
    private static function effectiveRows(string $id, string $device, array $byId, array $byParent, array $seen): int
    {
        if (!isset($byId[$id]) || isset($seen[$id])) { return 1; }
        $seen[$id] = true;
        $node = $byId[$id];
        $g = self::effectiveGeometry($node, $device);
        $type = (string) ($node['type'] ?? '');
        $base = $g['h'] > 0 ? $g['h'] : (in_array($type, ['text', 'image'], true) ? 10 : 8);
        if (!in_array($type, ['section', 'container'], true)) { return max(1, $base); }
        $required = 0;
        foreach ($byParent[$id] ?? [] as $child) {
            $childProps = is_array($child['props'] ?? null) ? $child['props'] : [];
            if ((string) ($child['type'] ?? '') === 'button' && (string) ($child['parentId'] ?? '') !== '' && (string) ($childProps['placementMode'] ?? 'normal') === 'overlay') { continue; }
            $childId = (string) ($child['id'] ?? '');
            if ($childId === '') { continue; }
            $cg = self::effectiveGeometry($child, $device);
            $required = max($required, $cg['y'] + self::effectiveRows($childId, $device, $byId, $byParent, $seen));
        }
        $props = is_array($node['props'] ?? null) ? $node['props'] : [];
        $extraPx = (max(0, (int) ($props['padding'] ?? 0)) * 2) + (max(0, (int) ($props['borderWidth'] ?? 0)) * 2);
        $required += (int) ceil($extraPx / LayoutModel::ROW_PX);
        return max(1, $base, $required);
    }

    /** @param array{x:int,y:int,w:int,h:int} $g */
    private static function geometryCss(string $selector, array $g, int $rows, bool $floating = false, int $zIndex = 20): string
    {
        $rows = max(1, $rows);
        if ($floating) {
            $left = ($g['x'] / LayoutModel::UNITS) * 100; $width = ($g['w'] / LayoutModel::UNITS) * 100;
            return $selector . '{position:absolute!important;left:' . $left . '%!important;top:' . (max(0, $g['y']) * LayoutModel::ROW_PX) . 'px!important;width:' . $width . '%!important;height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;min-height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;z-index:' . max(1, min(200, $zIndex)) . '!important;grid-column:auto!important;grid-row:auto!important;margin-top:0!important;}';
        }
        return $selector . '{grid-column:' . ($g['x'] + 1) . '/span ' . $g['w'] . '!important;grid-row:' . (max(0, $g['y']) + 1) . '/span ' . $rows . '!important;min-height:' . ($rows * LayoutModel::ROW_PX) . 'px!important;margin-top:0!important;}';
    }

    private static function cssId(string $id): string
    {
        return str_replace(['.', ':'], ['\\.', '\\:'], $id);
    }

    private function __construct() {}
}
''')

# Standalone preview must include the same responsive geometry layer.
replace_once(RENDERER,
    "        $style = (string) ob_get_clean();\n        self::$forceStandaloneCss = $previous;\n\n        $header = $headerModel !== null ? self::renderModel(LayoutModel::normalize($headerModel)) : '';",
    "        $style = (string) ob_get_clean();\n        self::$forceStandaloneCss = $previous;\n        $style .= ResponsiveRenderer::standaloneStyle($pageModel, $headerModel, $footerModel);\n\n        $header = $headerModel !== null ? self::renderModel(LayoutModel::normalize($headerModel)) : '';")

# ---------------------------------------------------------------------------
# VD-LEGACY-MIGRATION-001 services
# ---------------------------------------------------------------------------
write('clean/hangar18-manager/src/Migration/LegacyMediaImporter.php', r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

final class LegacyMediaImporter
{
    public const SOURCE_META = '_h18_legacy_media_source_url_v0173';
    public const HASH_META = '_h18_legacy_media_source_hash_v0173';

    /** @return int|\WP_Error */
    public static function import(string $url, string $title = '')
    {
        $url = esc_url_raw(trim($url), ['https']);
        if ($url === '' || strtolower((string) wp_parse_url($url, PHP_URL_SCHEME)) !== 'https') {
            return new \WP_Error('h18_legacy_media_url', 'Billed-URL skal være offentlig HTTPS.');
        }
        $existing = get_posts(['post_type' => 'attachment', 'post_status' => 'inherit', 'fields' => 'ids', 'posts_per_page' => 1, 'meta_key' => self::SOURCE_META, 'meta_value' => $url, 'suppress_filters' => true]);
        if ($existing) { return (int) $existing[0]; }

        require_once ABSPATH . 'wp-admin/includes/file.php';
        require_once ABSPATH . 'wp-admin/includes/media.php';
        require_once ABSPATH . 'wp-admin/includes/image.php';
        $tmp = download_url($url, 20);
        if (is_wp_error($tmp)) { return $tmp; }
        $path = (string) wp_parse_url($url, PHP_URL_PATH);
        $name = sanitize_file_name(basename($path));
        if ($name === '' || strpos($name, '.') === false) { $name = 'legacy-image.jpg'; }
        $file = ['name' => $name, 'tmp_name' => $tmp];
        $id = media_handle_sideload($file, 0, sanitize_text_field($title));
        if (is_wp_error($id)) { @unlink($tmp); return $id; }
        $mime = (string) get_post_mime_type((int) $id);
        if (strpos($mime, 'image/') !== 0) { wp_delete_attachment((int) $id, true); return new \WP_Error('h18_legacy_media_type', 'Kilden var ikke et billede.'); }
        update_post_meta((int) $id, self::SOURCE_META, $url);
        $filePath = get_attached_file((int) $id);
        if (is_string($filePath) && is_file($filePath)) { update_post_meta((int) $id, self::HASH_META, hash_file('sha256', $filePath)); }
        return (int) $id;
    }

    private function __construct() {}
}
''')

write('clean/hangar18-manager/src/Migration/LegacyModuleSourceService.php', r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Modules\ModuleRegistry;

final class LegacyModuleSourceService
{
    /** @return array<int,array<string,string>> */
    public static function scan(string $module, string $indexUrl): array
    {
        $module = ModuleRegistry::key($module);
        if (!ModuleRegistry::supports($module)) { throw new \InvalidArgumentException('Ukendt modul.'); }
        $source = ExternalPageSourceService::fetch($indexUrl);
        $html = (string) ($source['html'] ?? '');
        $base = (string) ($source['url'] ?? $indexUrl);
        $host = strtolower((string) wp_parse_url($base, PHP_URL_HOST));
        $out = [];
        if (!class_exists('DOMDocument')) { return $out; }
        $dom = new \DOMDocument('1.0', 'UTF-8');
        $old = libxml_use_internal_errors(true); $dom->loadHTML('<?xml encoding="utf-8" ?>' . $html, LIBXML_NONET | LIBXML_NOERROR | LIBXML_NOWARNING); libxml_clear_errors(); libxml_use_internal_errors($old);
        foreach ($dom->getElementsByTagName('a') as $a) {
            if (!$a instanceof \DOMElement) { continue; }
            $url = esc_url_raw(trim($a->getAttribute('href')));
            if ($url === '' || strtolower((string) wp_parse_url($url, PHP_URL_SCHEME)) !== 'https' || strtolower((string) wp_parse_url($url, PHP_URL_HOST)) !== $host) { continue; }
            $url = strtok($url, '#') ?: $url;
            if (rtrim($url, '/') === rtrim($base, '/')) { continue; }
            $title = sanitize_text_field(trim((string) $a->textContent));
            if ($title === '') { continue; }
            $out[$url] = ['url' => $url, 'title' => $title];
            if (count($out) >= 100) { break; }
        }
        return array_values($out);
    }

    /** @return array<string,mixed> */
    public static function detail(string $module, string $url): array
    {
        $module = ModuleRegistry::key($module);
        if (!ModuleRegistry::supports($module)) { throw new \InvalidArgumentException('Ukendt modul.'); }
        $source = ExternalPageSourceService::fetch($url);
        $html = (string) ($source['html'] ?? '');
        $title = sanitize_text_field((string) ($source['title'] ?? ''));
        $summary = ''; $description = ''; $images = []; $attributes = []; $fields = [];
        if (class_exists('DOMDocument')) {
            $dom = new \DOMDocument('1.0', 'UTF-8'); $old = libxml_use_internal_errors(true); $dom->loadHTML('<?xml encoding="utf-8" ?>' . $html, LIBXML_NONET | LIBXML_NOERROR | LIBXML_NOWARNING); libxml_clear_errors(); libxml_use_internal_errors($old); $xp = new \DOMXPath($dom);
            if ($title === '') { $h = $xp->query('//h1[1]'); if ($h && $h->length) { $title = sanitize_text_field((string) $h->item(0)->textContent); } }
            $ps = $xp->query('//p[normalize-space()][1]'); if ($ps && $ps->length) { $summary = sanitize_textarea_field(trim((string) $ps->item(0)->textContent)); }
            $body = $xp->query('//body[1]'); if ($body && $body->length) { foreach ($body->item(0)->childNodes as $child) { $part = $dom->saveHTML($child); if (is_string($part)) { $description .= $part; } } }
            foreach ($xp->query('//img[@src]') ?: [] as $img) { if ($img instanceof \DOMElement) { $src = esc_url_raw($img->getAttribute('src')); if ($src !== '' && strtolower((string) wp_parse_url($src, PHP_URL_SCHEME)) === 'https') { $images[$src] = $src; } } }
            if ($module === 'vehicles') { $attributes = self::vehicleAttributes($xp); }
            if ($module === 'events') { $fields = self::eventFields($xp, $html); }
        }
        $images = array_values($images);
        if ($module === 'vehicles') { $fields['description'] = wp_kses_post($description); $fields['category'] = ''; $fields['imageIds'] = []; }
        if ($module === 'events') { $fields['description'] = wp_kses_post($description); }
        if ($module === 'galleries') { $fields = ['description' => wp_kses_post($description), 'imageIds' => []]; }
        $warnings = [];
        if ($title === '') { $warnings[] = 'missing-title'; }
        if ($module === 'events' && empty($fields['start'])) { $warnings[] = 'event-date-needs-qa'; }
        if (!$images) { $warnings[] = 'no-images-found'; }
        return [
            'module' => $module, 'sourceUrl' => (string) ($source['url'] ?? $url), 'sourceHash' => (string) ($source['hash'] ?? hash('sha256', $html)),
            'title' => $title, 'slug' => sanitize_title($title), 'summary' => $summary, 'description' => wp_kses_post($description),
            'imageUrls' => $images, 'fields' => $fields, 'attributes' => $attributes, 'warnings' => $warnings,
        ];
    }

    /** @return array<int,array<string,mixed>> */
    private static function vehicleAttributes(\DOMXPath $xp): array
    {
        $pairs = []; $order = 10;
        foreach ($xp->query('//tr') ?: [] as $tr) {
            if (!$tr instanceof \DOMElement) { continue; }
            $cells = $xp->query('./th|./td', $tr); if (!$cells || $cells->length < 2) { continue; }
            $label = sanitize_text_field(trim((string) $cells->item(0)->textContent)); $value = sanitize_text_field(trim((string) $cells->item(1)->textContent));
            if ($label !== '' && $value !== '') { $pairs[sanitize_key($label)] = ['key' => sanitize_key($label), 'label' => $label, 'type' => 'text', 'value' => $value, 'enabled' => true, 'order' => $order]; $order += 10; }
        }
        foreach ($xp->query('//dt') ?: [] as $dt) {
            if (!$dt instanceof \DOMElement) { continue; } $dd = $dt->nextSibling; while ($dd && !($dd instanceof \DOMElement)) { $dd = $dd->nextSibling; }
            if (!$dd || strtolower($dd->nodeName) !== 'dd') { continue; }
            $label = sanitize_text_field(trim((string) $dt->textContent)); $value = sanitize_text_field(trim((string) $dd->textContent));
            if ($label !== '' && $value !== '') { $pairs[sanitize_key($label)] = ['key' => sanitize_key($label), 'label' => $label, 'type' => 'text', 'value' => $value, 'enabled' => true, 'order' => $order]; $order += 10; }
        }
        return array_values($pairs);
    }

    /** @return array<string,mixed> */
    private static function eventFields(\DOMXPath $xp, string $html): array
    {
        $start = ''; $end = ''; $location = '';
        foreach ($xp->query('//time[@datetime]') ?: [] as $time) {
            if (!$time instanceof \DOMElement) { continue; } $dt = trim($time->getAttribute('datetime'));
            if (preg_match('/^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}/', $dt)) { if ($start === '') { $start = substr($dt, 0, 16); } elseif ($end === '') { $end = substr($dt, 0, 16); break; } }
        }
        if ($start === '' && preg_match('/\\b(20\\d{2})[-\\/.](0?[1-9]|1[0-2])[-\\/.](0?[1-9]|[12]\\d|3[01])(?:\\D{0,8}([01]?\\d|2[0-3])[:.]([0-5]\\d))?/', wp_strip_all_tags($html), $m)) {
            $start = sprintf('%04d-%02d-%02dT%02d:%02d', (int) $m[1], (int) $m[2], (int) $m[3], isset($m[4]) ? (int) $m[4] : 0, isset($m[5]) ? (int) $m[5] : 0);
        }
        foreach (['//*[contains(@class,"location")][1]', '//*[@itemprop="location"][1]'] as $q) { $nodes = $xp->query($q); if ($nodes && $nodes->length) { $location = sanitize_text_field(trim((string) $nodes->item(0)->textContent)); if ($location !== '') { break; } } }
        return ['start' => $start, 'end' => $end, 'location' => $location, 'description' => ''];
    }

    private function __construct() {}
}
''')

write('clean/hangar18-manager/src/Migration/LegacyModuleMigrationService.php', r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Modules\ModuleRegistry;
use VisualDesignerManager\Modules\ModuleStore;

final class LegacyModuleMigrationService
{
    public const OPTION = 'h18_vd_legacy_migration_v0173';
    public const SOURCE_URL_META = '_h18_legacy_source_url_v0173';
    public const SOURCE_HASH_META = '_h18_legacy_source_hash_v0173';
    public const IMPORTED_META = '_h18_legacy_imported_utc_v0173';

    /** @return array<string,mixed> */
    public static function state(): array
    {
        $raw = get_option(self::OPTION, []); return is_array($raw) ? $raw : [];
    }

    /** @return array<string,mixed> */
    public static function scan(string $module, string $indexUrl): array
    {
        $module = ModuleRegistry::key($module); $items = LegacyModuleSourceService::scan($module, $indexUrl);
        $state = self::state(); $state[$module] = ['indexUrl' => esc_url_raw($indexUrl), 'scannedUtc' => gmdate('c'), 'items' => []];
        foreach ($items as $item) { $url = (string) ($item['url'] ?? ''); if ($url === '') { continue; } $state[$module]['items'][hash('sha256', $url)] = ['sourceUrl' => $url, 'title' => (string) ($item['title'] ?? ''), 'status' => 'discovered', 'warnings' => []]; }
        update_option(self::OPTION, $state, false); return $state[$module];
    }

    /** @return array<string,mixed> */
    public static function prepareBatch(string $module, int $limit = 5): array
    {
        $module = ModuleRegistry::key($module); $state = self::state(); if (!isset($state[$module]['items']) || !is_array($state[$module]['items'])) { throw new \RuntimeException('Scan modulet først.'); }
        $done = 0;
        foreach ($state[$module]['items'] as $key => $item) {
            if ($done >= max(1, min(10, $limit))) { break; }
            if ((string) ($item['status'] ?? '') !== 'discovered') { continue; }
            try { $detail = LegacyModuleSourceService::detail($module, (string) $item['sourceUrl']); $detail['status'] = empty($detail['warnings']) ? 'ready' : 'review'; $state[$module]['items'][$key] = array_merge($item, $detail); }
            catch (\Throwable $e) { $item['status'] = 'error'; $item['warnings'] = [$e->getMessage()]; $state[$module]['items'][$key] = $item; }
            $done++;
        }
        update_option(self::OPTION, $state, false); return $state[$module];
    }

    /** @return array{status:string,postId:int,message:string} */
    public static function approve(string $module, string $key): array
    {
        $module = ModuleRegistry::key($module); $state = self::state(); $item = $state[$module]['items'][$key] ?? null;
        if (!is_array($item) || !in_array((string) ($item['status'] ?? ''), ['ready', 'review', 'changed'], true)) { throw new \RuntimeException('Kandidaten er ikke klar til godkendelse.'); }
        $url = esc_url_raw((string) ($item['sourceUrl'] ?? '')); $hash = sanitize_text_field((string) ($item['sourceHash'] ?? ''));
        if ($url === '' || !preg_match('/^[a-f0-9]{64}$/', $hash)) { throw new \RuntimeException('Kildens URL/hash mangler.'); }
        $existing = self::findBySource($module, $url);
        if ($existing > 0 && hash_equals((string) get_post_meta($existing, self::SOURCE_HASH_META, true), $hash)) {
            $state[$module]['items'][$key]['status'] = 'unchanged'; $state[$module]['items'][$key]['targetPostId'] = $existing; update_option(self::OPTION, $state, false);
            return ['status' => 'unchanged', 'postId' => $existing, 'message' => 'Allerede importeret og uændret.'];
        }

        $media = [];
        foreach (array_slice((array) ($item['imageUrls'] ?? []), 0, 500) as $imageUrl) {
            $id = LegacyMediaImporter::import((string) $imageUrl, (string) ($item['title'] ?? ''));
            if (!is_wp_error($id) && (int) $id > 0) { $media[] = (int) $id; }
        }
        $fields = isset($item['fields']) && is_array($item['fields']) ? $item['fields'] : [];
        if ($module === 'vehicles' || $module === 'galleries') { $fields['imageIds'] = $media; }
        $recordId = $existing > 0 && ($old = ModuleStore::get($existing)) !== null ? (string) ($old['id'] ?? '') : 'legacy-' . substr(hash('sha256', $url), 0, 24);
        $raw = [
            'id' => $recordId, 'title' => (string) ($item['title'] ?? ''), 'slug' => (string) ($item['slug'] ?? ''), 'status' => 'draft',
            'sortOrder' => 0, 'featuredMediaId' => $media ? (int) $media[0] : 0, 'summary' => (string) ($item['summary'] ?? ''),
            'fields' => $fields, 'attributes' => isset($item['attributes']) && is_array($item['attributes']) ? $item['attributes'] : [],
        ];
        $saved = ModuleStore::save($module, $raw, $existing);
        if (is_wp_error($saved)) { throw new \RuntimeException($saved->get_error_message()); }
        $postId = (int) $saved; update_post_meta($postId, self::SOURCE_URL_META, $url); update_post_meta($postId, self::SOURCE_HASH_META, $hash); update_post_meta($postId, self::IMPORTED_META, gmdate('c'));
        $state[$module]['items'][$key]['status'] = 'imported'; $state[$module]['items'][$key]['targetPostId'] = $postId; update_option(self::OPTION, $state, false);
        return ['status' => 'imported', 'postId' => $postId, 'message' => 'Importeret som kladde til modul-QA.'];
    }

    public static function clear(string $module): void
    {
        $module = ModuleRegistry::key($module); $state = self::state(); unset($state[$module]); update_option(self::OPTION, $state, false);
    }

    private static function findBySource(string $module, string $url): int
    {
        $ids = get_posts(['post_type' => ModuleStore::POST_TYPE, 'post_status' => 'publish', 'fields' => 'ids', 'posts_per_page' => 1, 'suppress_filters' => true,
            'meta_query' => [['key' => ModuleStore::META_MODULE, 'value' => $module], ['key' => self::SOURCE_URL_META, 'value' => $url]]]);
        return $ids ? (int) $ids[0] : 0;
    }

    private function __construct() {}
}
''')

write('clean/hangar18-manager/src/Admin/LegacyMigrationController.php', r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Migration\LegacyModuleMigrationService;
use VisualDesignerManager\Modules\ModuleRegistry;

final class LegacyMigrationController
{
    private const SCAN = 'h18_vd_legacy_scan_v0173';
    private const PREPARE = 'h18_vd_legacy_prepare_v0173';
    private const APPROVE = 'h18_vd_legacy_approve_v0173';
    private const CLEAR = 'h18_vd_legacy_clear_v0173';
    private const NONCE = 'h18_vd_legacy_v0173';

    public static function register(): void
    {
        add_action('admin_post_' . self::SCAN, [self::class, 'scan']); add_action('admin_post_' . self::PREPARE, [self::class, 'prepare']);
        add_action('admin_post_' . self::APPROVE, [self::class, 'approve']); add_action('admin_post_' . self::CLEAR, [self::class, 'clear']);
    }

    public static function render(): void
    {
        self::guard(); $state = LegacyModuleMigrationService::state(); $active = ModuleRegistry::key((string) ($_GET['module'] ?? 'vehicles')); if (!ModuleRegistry::supports($active)) { $active = 'vehicles'; }
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? '')); $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        echo '<div class="wrap h18-manager-admin"><h1>Konvertering · Legacy migrering</h1>';
        self::tabs('legacy');
        echo '<p class="h18-manager-description">Læs det gamle website read-only og konvertér Køretøjer, Events og Billedgalleri til canonical ModuleStore-records. Intet aktiveres offentligt automatisk; godkendte records oprettes som kladder.</p>';
        if ($message !== '') { echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>'; }
        echo '<nav class="nav-tab-wrapper">'; foreach (['vehicles' => 'Køretøjer', 'events' => 'Events', 'galleries' => 'Billedgalleri'] as $key => $label) { $url = admin_url('admin.php?page=h18-clean-conversion&vd_tab=legacy&module=' . $key); echo '<a class="nav-tab ' . ($active === $key ? 'nav-tab-active' : '') . '" href="' . esc_url($url) . '">' . esc_html($label) . '</a>'; } echo '</nav>';
        $bucket = isset($state[$active]) && is_array($state[$active]) ? $state[$active] : [];
        self::scanForm($active, (string) ($bucket['indexUrl'] ?? self::defaultUrl($active)));
        self::summary($bucket);
        self::items($active, $bucket);
        echo '</div>';
    }

    public static function tabs(string $active): void
    {
        echo '<nav class="nav-tab-wrapper" style="margin-bottom:16px"><a class="nav-tab ' . ($active === 'pages' ? 'nav-tab-active' : '') . '" href="' . esc_url(admin_url('admin.php?page=h18-clean-conversion&vd_tab=pages')) . '">Sider</a><a class="nav-tab ' . ($active === 'legacy' ? 'nav-tab-active' : '') . '" href="' . esc_url(admin_url('admin.php?page=h18-clean-conversion&vd_tab=legacy')) . '">Legacy migrering</a></nav>';
    }

    private static function scanForm(string $module, string $url): void
    {
        echo '<section class="h18-manager-card"><h2>Kilde</h2><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-manager-page-create-form">'; wp_nonce_field(self::NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::SCAN) . '"><input type="hidden" name="module" value="' . esc_attr($module) . '"><label style="min-width:420px;flex:1"><strong>Oversigts-URL på gammelt website</strong><input type="url" class="widefat" name="index_url" required value="' . esc_attr($url) . '"></label><button class="button button-primary" type="submit">Scan read-only</button></form><p class="description">Scan opretter kun kandidater. Kildesitet ændres aldrig.</p></section>';
    }

    /** @param array<string,mixed> $bucket */
    private static function summary(array $bucket): void
    {
        $items = isset($bucket['items']) && is_array($bucket['items']) ? $bucket['items'] : []; $counts = [];
        foreach ($items as $item) { $key = is_array($item) ? (string) ($item['status'] ?? 'discovered') : 'error'; $counts[$key] = ($counts[$key] ?? 0) + 1; }
        echo '<div class="h18-manager-stats"><div class="h18-manager-stat"><strong>' . count($items) . '</strong><span>Fundet</span></div><div class="h18-manager-stat"><strong>' . (($counts['ready'] ?? 0) + ($counts['review'] ?? 0)) . '</strong><span>Klar til QA</span></div><div class="h18-manager-stat"><strong>' . ($counts['imported'] ?? 0) . '</strong><span>Importeret</span></div><div class="h18-manager-stat"><strong>' . ($counts['error'] ?? 0) . '</strong><span>Fejl</span></div></div>';
    }

    /** @param array<string,mixed> $bucket */
    private static function items(string $module, array $bucket): void
    {
        $items = isset($bucket['items']) && is_array($bucket['items']) ? $bucket['items'] : [];
        if (!$items) { echo '<p>Ingen kandidater endnu.</p>'; return; }
        echo '<div class="h18-manager-toolbar">'; self::button(self::PREPARE, $module, '', 'Forbered næste 5', true); self::button(self::CLEAR, $module, '', 'Ryd scan', false); echo '</div>';
        echo '<table class="widefat striped"><thead><tr><th>Titel</th><th>Kilde</th><th>Status</th><th>Billeder</th><th>QA</th><th>Handling</th></tr></thead><tbody>';
        foreach ($items as $key => $item) { if (!is_array($item)) { continue; } $warnings = isset($item['warnings']) && is_array($item['warnings']) ? $item['warnings'] : [];
            echo '<tr><td><strong>' . esc_html((string) ($item['title'] ?? '')) . '</strong></td><td><a target="_blank" rel="noopener" href="' . esc_url((string) ($item['sourceUrl'] ?? '')) . '">Åbn kilde</a></td><td><code>' . esc_html((string) ($item['status'] ?? '')) . '</code></td><td>' . esc_html((string) count((array) ($item['imageUrls'] ?? []))) . '</td><td>' . ($warnings ? esc_html(implode(' · ', array_map('strval', $warnings))) : '—') . '</td><td>';
            if (in_array((string) ($item['status'] ?? ''), ['ready', 'review', 'changed'], true)) { self::button(self::APPROVE, $module, (string) $key, 'Godkend/importér', true); } elseif (!empty($item['targetPostId'])) { echo '<code>ID ' . esc_html((string) $item['targetPostId']) . '</code>'; } echo '</td></tr>';
        }
        echo '</tbody></table>';
    }

    private static function button(string $action, string $module, string $key, string $label, bool $primary): void
    {
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">'; wp_nonce_field(self::NONCE); echo '<input type="hidden" name="action" value="' . esc_attr($action) . '"><input type="hidden" name="module" value="' . esc_attr($module) . '">'; if ($key !== '') { echo '<input type="hidden" name="candidate" value="' . esc_attr($key) . '">'; } echo '<button class="button ' . ($primary ? 'button-primary' : '') . '" type="submit">' . esc_html($label) . '</button></form>';
    }

    public static function scan(): void { self::guard(); check_admin_referer(self::NONCE); $m = ModuleRegistry::key((string) ($_POST['module'] ?? '')); try { LegacyModuleMigrationService::scan($m, esc_url_raw((string) wp_unslash($_POST['index_url'] ?? ''))); self::redirect($m, 'success', 'Scan gennemført. Forbered kandidaterne i små batches.'); } catch (\Throwable $e) { self::redirect($m, 'error', $e->getMessage()); } }
    public static function prepare(): void { self::guard(); check_admin_referer(self::NONCE); $m = ModuleRegistry::key((string) ($_POST['module'] ?? '')); try { LegacyModuleMigrationService::prepareBatch($m, 5); self::redirect($m, 'success', 'Næste batch er forberedt til QA.'); } catch (\Throwable $e) { self::redirect($m, 'error', $e->getMessage()); } }
    public static function approve(): void { self::guard(); check_admin_referer(self::NONCE); $m = ModuleRegistry::key((string) ($_POST['module'] ?? '')); try { $r = LegacyModuleMigrationService::approve($m, sanitize_text_field((string) ($_POST['candidate'] ?? ''))); self::redirect($m, 'success', (string) $r['message']); } catch (\Throwable $e) { self::redirect($m, 'error', $e->getMessage()); } }
    public static function clear(): void { self::guard(); check_admin_referer(self::NONCE); $m = ModuleRegistry::key((string) ($_POST['module'] ?? '')); LegacyModuleMigrationService::clear($m); self::redirect($m, 'success', 'Scan/kandidater er ryddet. Importerede modulrecords er ikke slettet.'); }

    private static function redirect(string $module, string $status, string $message): void { wp_safe_redirect(add_query_arg(['page' => 'h18-clean-conversion', 'vd_tab' => 'legacy', 'module' => $module, 'vd_status' => $status, 'vd_message' => rawurlencode($message)], admin_url('admin.php'))); exit; }
    private static function guard(): void { if (!current_user_can('edit_pages')) { wp_die('Du har ikke adgang til Legacy migrering.'); } }
    private static function defaultUrl(string $module): string { $base = 'https://test2.hangar18.dk/'; return $base . ($module === 'vehicles' ? 'koeretoejer-og-materiel/' : ($module === 'events' ? 'events/' : 'billedgalleri/')); }
    private function __construct() {}
}
''')

# Conversion remains one Admin menu entry with Sider + Legacy tabs.
replace_once(CONVERSION,
    "    public static function render(): void\n    {\n        self::guard();\n        $pages = self::pages();",
    "    public static function render(): void\n    {\n        self::guard();\n        $tab = sanitize_key((string) ($_GET['vd_tab'] ?? 'pages'));\n        if ($tab === 'legacy') { LegacyMigrationController::render(); return; }\n        $pages = self::pages();")
replace_once(CONVERSION,
    "        echo '<h1>Konvertering af sider</h1>';",
    "        echo '<h1>Konvertering af sider</h1>';\n        LegacyMigrationController::tabs('pages');")

# ---------------------------------------------------------------------------
# Documentation and release metadata
# ---------------------------------------------------------------------------
notes = '''<h2>0.1.73 – Render Parity + Legacy Migration &amp; Cutover</h2>\n<ul>\n<li><strong>VD-RENDER-PARITY-001:</strong> Side, Header og Footer bruger samme canonical content-box og responsive breakpoint-geometri i Designer, Preview og frontend.</li>\n<li>Editor-rammer er nu zero-layout-impact; tekstpadding kommer fra samme canonical props som frontend. 100% er standard 1:1-visning, mens Fit er en eksplicit arbejdszoom.</li>\n<li><strong>VD-LEGACY-MIGRATION-001:</strong> Konvertering har fanen Legacy migrering for Køretøjer, Events og Billedgalleri.</li>\n<li>Legacy-scan er read-only, opretter QA-kandidater i små batches og importerer først efter eksplicit godkendelse.</li>\n<li>Billeder sideloades til WordPress Media Library med source-URL/hash og dubletkontrol; modulrecords får source-URL/hash og oprettes som kladder.</li>\n<li>Manglende eller ændrede kilder sletter aldrig eksisterende records automatisk.</li>\n</ul>'''
write('clean-release-notes.html', notes)

history = json.loads(read('clean/hangar18-manager/release-history.json'))
versions = history.get('versions', [])
if not any(str(v.get('version')) == '0.1.73' for v in versions):
    versions.insert(0, {'version': '0.1.73', 'date': '2026-09-01', 'items': [
        'VD-RENDER-PARITY-001: Side, Header og Footer deler canonical content-box og breakpoint-regler mellem Designer, Preview og frontend.',
        'Editor-chrome påvirker ikke længere layoutbredde; 100% er standard 1:1-visning og Fit er eksplicit arbejdszoom.',
        'VD-LEGACY-MIGRATION-001: Konvertering har read-only Legacy migrering for Køretøjer, Events og Billedgalleri.',
        'Legacy kandidater forberedes i små QA-batches og godkendte records oprettes som kladder i ModuleStore.',
        'Legacy billeder importeres til Media Library med source URL/hash og idempotent dubletkontrol.'
    ]})
    history['versions'] = versions
    write('clean/hangar18-manager/release-history.json', json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write('docs/v0173-status.md', '''# Visual Designer Manager v0.1.73 status\n\nRelease candidate: **Render Parity + Legacy Migration & Cutover**.\n\n- VD-RENDER-PARITY-001: Designer/Preview/frontend parity for Side, Header og Footer.\n- VD-LEGACY-MIGRATION-001: staged read-only legacy scan/import for vehicles, events and galleries.\n- Source URL/hash, Media Library sideload, duplicate protection and draft-first cutover.\n- Manuals, release history and backlog synchronized.\n''')

append_once('CLEAN-DESIGN-MANUAL.md', 'VD-RENDER-PARITY-001', '''## v0.1.73 · VD-RENDER-PARITY-001\nDesignerens rammer/håndtag er kun chrome og må ikke optage canonical layoutplads. Sektion/Kasse, tekstpadding og responsive geometrier skal derfor beregnes identisk i Designer, standalone Preview og frontend. Header og Footer følger samme breakpoint-resolver som siden. **100%** er 1:1 visuel CSS-pixelvisning; **Fit** er arbejdszoom og kan derfor se fysisk mindre ud uden at ændre layoutdata.\n''')
append_once('CLEAN-TECHNICAL-MANUAL.md', 'VD-LEGACY-MIGRATION-001', '''## v0.1.73 · VD-LEGACY-MIGRATION-001\nLegacy migrering ligger under Konvertering og arbejder staged: scan → prepare → QA → approve. Kilden læses read-only via den eksisterende sikre HTTPS-importer. Module records gemmer source URL/hash og oprettes som draft. Media sideloades til WordPress Media Library og deduplikeres via `_h18_legacy_media_source_url_v0173`. Manglende kilder udløser aldrig automatisk delete. VD-RENDER-PARITY-001 udvider ResponsiveRenderer til scoped Page/Header/Footer models og standalone Preview.\n''')
append_once('CLEAN-USER-MANUAL.md', 'Legacy migrering (v0.1.73)', '''## Legacy migrering (v0.1.73)\nGå til **Visual Designer Manager → Konvertering → Legacy migrering**. Vælg Køretøjer, Events eller Billedgalleri, angiv oversigts-URL, vælg **Scan read-only**, og brug **Forbered næste 5**. Gennemgå kilde, advarsler og antal billeder før **Godkend/importér**. Godkendte poster oprettes som kladder, så de kan QA-kontrolleres i moduladministrationen før publicering. Brug Designerens **100%**-knap når du vil sammenligne visuelt 1:1; Fit er arbejdszoom.\n''')

backlog = read('docs/clean-backlog-v0100.md')
backlog = backlog.replace('**Aktuel release:** v0.1.72', '**Aktuel release:** v0.1.73')
backlog = backlog.replace('5. **v0.1.73 – Modul-cutover/migrering — NÆSTE:** samlet legacy data-/module-migrering med side-by-side QA før cutover.', '5. **v0.1.73 – Render Parity + Legacy migrering — FÆRDIG:** Designer/Preview/frontend parity for Side/Header/Footer samt staged legacy import af Køretøjer, Events, Billedgalleri og Media Library.\\n6. **NÆSTE:** live-site cutover QA, pæne modul-URLer og resterende responsive/Tablet-afslutning.')
if 'VD-RENDER-PARITY-001 — IMPLEMENTERET I v0.1.73' not in backlog:
    backlog = backlog.replace('## Åben backlog', '## Åben backlog\\n\\n### VD-RENDER-PARITY-001 — IMPLEMENTERET I v0.1.73\\n- Side, Header og Footer bruger samme breakpoint-geometri i Designer, Preview og frontend.\\n- Editor chrome er zero-layout-impact. 100% er 1:1-visning; Fit er arbejdszoom.\\n\\n### VD-LEGACY-MIGRATION-001 — IMPLEMENTERET I v0.1.73\\n- Read-only scan under Konvertering → Legacy migrering.\\n- Køretøjer, Events og Billedgalleri staged som QA-kandidater og importeres som kladder.\\n- Media Library sideload + source URL/hash + dubletkontrol; ingen automatisk delete.\\n')
backlog = backlog.replace('\\n', '\n')
write('docs/clean-backlog-v0100.md', backlog)

print('Applied v0.1.73 Render Parity + Legacy Migration candidate.')
