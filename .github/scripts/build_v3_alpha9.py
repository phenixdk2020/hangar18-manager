from pathlib import Path
import json
import re
import subprocess

VERSION = '3.0.0-alpha.9'
DEST = Path('build/visual-designer-manager')


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str, label: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor in {rel}, found {count}')
    write(rel, value.replace(old, new, 1))


subprocess.run(['python3', '.github/scripts/build_v3_alpha8.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.8', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.8');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.8');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.9 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Designer: section side paddings + WYSIWYG form width parity.
# ---------------------------------------------------------------------------
js_rel = 'assets/editor-v018-core.js'
replace_once(
    js_rel,
    "                padding: clamp(parseInt(raw.padding || 0, 10) || 0, 0, 120),\n                minHeightRows:",
    "                padding: clamp(parseInt(raw.padding || 0, 10) || 0, 0, 120),\n                paddingTop: clamp(parseInt(raw.paddingTop != null ? raw.paddingTop : (raw.padding || 0), 10) || 0, 0, 240),\n                paddingRight: clamp(parseInt(raw.paddingRight != null ? raw.paddingRight : (raw.padding || 0), 10) || 0, 0, 240),\n                paddingBottom: clamp(parseInt(raw.paddingBottom != null ? raw.paddingBottom : (raw.padding || 0), 10) || 0, 0, 240),\n                paddingLeft: clamp(parseInt(raw.paddingLeft != null ? raw.paddingLeft : (raw.padding || 0), 10) || 0, 0, 240),\n                minHeightRows:",
    'parent side-padding normalization'
)
replace_once(
    js_rel,
    "                inner.style.padding = (p.padding || 0) + 'px';",
    "                const legacyPadding = parseInt(p.padding || 0, 10) || 0;\n                inner.style.paddingTop = String(p.paddingTop == null ? legacyPadding : p.paddingTop) + 'px';\n                inner.style.paddingRight = String(p.paddingRight == null ? legacyPadding : p.paddingRight) + 'px';\n                inner.style.paddingBottom = String(p.paddingBottom == null ? legacyPadding : p.paddingBottom) + 'px';\n                inner.style.paddingLeft = String(p.paddingLeft == null ? legacyPadding : p.paddingLeft) + 'px';",
    'designer surface side-padding'
)
replace_once(
    js_rel,
    "            html += '<div class=\"h18-clean-field-grid\"><label>Hjørner px<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"100\" value=\"' + (node.props.radius || 0) + '\"></label><label>Padding px<input data-field=\"padding\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.padding || 0) + '\"></label></div>';",
    "            const legacySectionPadding = parseInt(node.props.padding || 0, 10) || 0;\n            html += '<div class=\"h18-clean-field-grid\"><label>Hjørner px<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"100\" value=\"' + (node.props.radius || 0) + '\"></label><label>Padding top px<input data-field=\"paddingTop\" type=\"number\" min=\"0\" max=\"240\" value=\"' + (node.props.paddingTop == null ? legacySectionPadding : node.props.paddingTop) + '\"></label><label>Padding højre px<input data-field=\"paddingRight\" type=\"number\" min=\"0\" max=\"240\" value=\"' + (node.props.paddingRight == null ? legacySectionPadding : node.props.paddingRight) + '\"></label><label>Padding bund px<input data-field=\"paddingBottom\" type=\"number\" min=\"0\" max=\"240\" value=\"' + (node.props.paddingBottom == null ? legacySectionPadding : node.props.paddingBottom) + '\"></label><label>Padding venstre px<input data-field=\"paddingLeft\" type=\"number\" min=\"0\" max=\"240\" value=\"' + (node.props.paddingLeft == null ? legacySectionPadding : node.props.paddingLeft) + '\"></label></div>';",
    'section padding inspector'
)
replace_once(
    js_rel,
    "                else if (field === 'padding') { current.props.padding = clamp(parseInt(control.value || 0, 10) || 0, 0, 120); }",
    "                else if (field === 'padding') { current.props.padding = clamp(parseInt(control.value || 0, 10) || 0, 0, 120); }\n                else if (field === 'paddingTop') { current.props.paddingTop = clamp(parseInt(control.value || 0, 10) || 0, 0, 240); }\n                else if (field === 'paddingRight') { current.props.paddingRight = clamp(parseInt(control.value || 0, 10) || 0, 0, 240); }\n                else if (field === 'paddingBottom') { current.props.paddingBottom = clamp(parseInt(control.value || 0, 10) || 0, 0, 240); }\n                else if (field === 'paddingLeft') { current.props.paddingLeft = clamp(parseInt(control.value || 0, 10) || 0, 0, 240); }",
    'section padding handlers'
)

css_rel = 'assets/admin-v0175.css'
css = read(css_rel)
css += """

/* V3 alpha.9 - Designer/live form width parity. Selection chrome must not alter form geometry. */
.h18-clean-node-preview--form{padding:0!important;box-sizing:border-box!important}
.h18-vd-form-preview,.h18-vd-form-preview-body,.h18-vd-form-preview-grid,.h18-vd-form-preview-field{min-width:0;box-sizing:border-box}
.h18-vd-form-preview-grid{gap:var(--vdm-form-field-gap,16px)!important}
.h18-vd-form-preview-field input,.h18-vd-form-preview-field textarea{display:block;width:100%;max-width:none;box-sizing:border-box}
@media(max-width:782px){.h18-vd-form-preview-grid{grid-template-columns:1fr!important}}
"""
write(css_rel, css)

# ---------------------------------------------------------------------------
# Frontend renderer: real side padding and dynamic detail height.
# ---------------------------------------------------------------------------
renderer_rel = 'src/Frontend/Renderer.php'
replace_once(
    renderer_rel,
    "        $h = max(0, (int) ($g['h'] ?? 0));\n        $style = 'grid-column:' . ($x + 1) . '/span ' . $w . ';';",
    "        $h = max(0, (int) ($g['h'] ?? 0));\n        $earlyType = (string) ($node['type'] ?? '');\n        $earlyProps = is_array($node['props'] ?? null) ? $node['props'] : [];\n        if ($earlyType === 'gallerydetail') {\n            $h = max($h, self::galleryDetailRows($node, 'desktop'));\n        }\n        if (in_array($earlyType, ['section', 'container'], true)) {\n            $requiredPx = self::requiredChildHeightPx((string) ($node['id'] ?? ''), $byParent) + self::verticalPaddingPx($earlyProps);\n            $h = max($h, (int) ceil($requiredPx / LayoutModel::ROW_PX));\n        }\n        $style = 'grid-column:' . ($x + 1) . '/span ' . $w . ';';",
    'dynamic row span before grid style'
)
replace_once(
    renderer_rel,
    "        $background = sanitize_hex_color((string) ($props['background'] ?? '')) ?: 'transparent';\n        $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));\n        $classes = $type === 'section' ? 'h18-clean-front-section' : 'h18-clean-front-container';\n        $requiredHeight = self::requiredChildHeightPx((string) $node['id'], $byParent);\n        $selectedHeight = $h * LayoutModel::ROW_PX;\n        $minimumHeight = max($selectedHeight, $requiredHeight);\n        if ($minimumHeight > 0) {\n            $style .= 'min-height:' . $minimumHeight . 'px;';\n        }\n        $boxStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';padding:' . $padding . 'px;';",
    "        $background = sanitize_hex_color((string) ($props['background'] ?? '')) ?: 'transparent';\n        $legacyPadding = max(0, min(120, (int) ($props['padding'] ?? 0)));\n        $paddingTop = max(0, min(240, (int) ($props['paddingTop'] ?? $legacyPadding)));\n        $paddingRight = max(0, min(240, (int) ($props['paddingRight'] ?? $legacyPadding)));\n        $paddingBottom = max(0, min(240, (int) ($props['paddingBottom'] ?? $legacyPadding)));\n        $paddingLeft = max(0, min(240, (int) ($props['paddingLeft'] ?? $legacyPadding)));\n        $classes = $type === 'section' ? 'h18-clean-front-section' : 'h18-clean-front-container';\n        $requiredHeight = self::requiredChildHeightPx((string) $node['id'], $byParent) + $paddingTop + $paddingBottom;\n        $selectedHeight = $h * LayoutModel::ROW_PX;\n        $minimumHeight = max($selectedHeight, $requiredHeight);\n        if ($minimumHeight > 0) {\n            $style .= 'min-height:' . $minimumHeight . 'px;';\n        }\n        $boxStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';padding:' . $paddingTop . 'px ' . $paddingRight . 'px ' . $paddingBottom . 'px ' . $paddingLeft . 'px;';",
    'frontend side-padding block'
)
replace_once(
    renderer_rel,
    "            if (in_array($type, ['section', 'container'], true)) {\n                $childHeight = max($childHeight, self::requiredChildHeightPx((string) ($child['id'] ?? ''), $byParent));\n            }",
    "            if ($type === 'gallerydetail') {\n                $childHeight = max($childHeight, self::galleryDetailRows($child, 'desktop') * LayoutModel::ROW_PX);\n            }\n            if (in_array($type, ['section', 'container'], true)) {\n                $childProps = is_array($child['props'] ?? null) ? $child['props'] : [];\n                $childHeight = max($childHeight, self::requiredChildHeightPx((string) ($child['id'] ?? ''), $byParent) + self::verticalPaddingPx($childProps));\n            }",
    'dynamic child height'
)

renderer = read(renderer_rel)
end_anchor = "        return $required;\n    }\n}"
if renderer.count(end_anchor) != 1:
    raise SystemExit('Renderer helper end anchor mismatch')
helpers = r'''        return $required;
    }

    /** @param array<string,mixed> $props */
    private static function verticalPaddingPx(array $props): int
    {
        $legacy = max(0, min(120, (int) ($props['padding'] ?? 0)));
        $top = max(0, min(240, (int) ($props['paddingTop'] ?? $legacy)));
        $bottom = max(0, min(240, (int) ($props['paddingBottom'] ?? $legacy)));
        return $top + $bottom;
    }

    /** @param array<string,mixed> $node */
    private static function galleryDetailRows(array $node, string $device): int
    {
        $props = is_array($node['props'] ?? null) ? $node['props'] : [];
        $recordId = strtolower(trim((string) ($props['recordId'] ?? '')));
        if ($recordId === '') { $recordId = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET['h18_gallery'] ?? '')))); }
        $count = 0; $hasDescription = false;
        if ($recordId !== '' && preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) {
            $found = ModuleStore::findByRecordId('galleries', $recordId);
            $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
            if (is_array($record)) {
                $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
                $ids = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
                $count = count($ids);
                $hasDescription = !empty($props['showDescription']) && trim((string) ($fields['description'] ?? '')) !== '';
            }
        }
        $columns = $device === 'mobile' ? 1 : ($device === 'tablet' ? min(2, max(1, (int) ($props['columns'] ?? 4))) : max(1, min(6, (int) ($props['columns'] ?? 4))));
        $imageHeight = max(80, min(700, (int) ($props['imageHeight'] ?? 220)));
        $gap = max(0, min(80, (int) ($props['gap'] ?? 12)));
        $padding = max(0, min(80, (int) ($props['padding'] ?? 16)));
        $imageRows = $count > 0 ? (int) ceil($count / $columns) : 0;
        $imagesPx = $imageRows > 0 ? ($imageRows * $imageHeight) + (max(0, $imageRows - 1) * $gap) : 0;
        $chromePx = 88 + ($hasDescription ? 144 : 0) + ($padding * 2);
        return max(8, (int) ceil(($chromePx + $imagesPx) / LayoutModel::ROW_PX));
    }
}'''
write(renderer_rel, renderer.replace(end_anchor, helpers, 1))

# Gallery collection page owns only controls/cards; the Designer page owns its heading.
collection_rel = 'src/Frontend/CollectionPageRenderer.php'
collection = read(collection_rel)
collection = collection.replace(" . '<section class=\"h18-module-section\"><h2>Køretøjer</h2>';", " . '<section class=\"h18-module-section\">';")
collection = collection.replace("<section class=\"h18-module-section\"><h2>Køretøjer</h2>", "<section class=\"h18-module-section\">")
write(collection_rel, collection)

# Standardise album-back wording wherever the retained V1 runtime emits it.
for php in DEST.rglob('*.php'):
    text = php.read_text(encoding='utf-8')
    if '← Tilbage til Billedgalleri' in text:
        php.write_text(text.replace('← Tilbage til Billedgalleri', '← Tilbage til album'), encoding='utf-8')

# ---------------------------------------------------------------------------
# Responsive runtime: side padding and dynamic gallery/event fact rows.
# ---------------------------------------------------------------------------
rr_rel = 'src/Frontend/ResponsiveRenderer.php'
rr = read(rr_rel)
anchor = 'use VisualDesignerManager\\Model\\TemplateLayoutModel;\n'
if anchor not in rr:
    raise SystemExit('ResponsiveRenderer TemplateLayoutModel import missing')
if 'use VisualDesignerManager\\Modules\\ModuleStore;' not in rr:
    rr = rr.replace(anchor, anchor + 'use VisualDesignerManager\\Modules\\ModuleStore;\n', 1)
write(rr_rel, rr)
replace_once(
    rr_rel,
    "        $base = $g['h'] > 0 ? $g['h'] : (in_array($type, ['text', 'image'], true) ? 10 : 8);",
    "        $base = $g['h'] > 0 ? $g['h'] : (in_array($type, ['text', 'image'], true) ? 10 : 8);\n        if ($type === 'gallerydetail') { $base = max($base, self::galleryDetailRows($node, $device)); }\n        if ($type === 'eventfacts' && $device === 'mobile') { $base = max($base, 42); }",
    'responsive dynamic detail rows'
)
replace_once(
    rr_rel,
    "        $props = is_array($node['props'] ?? null) ? $node['props'] : [];\n        $extraPx = (max(0, (int) ($props['padding'] ?? 0)) * 2) + (max(0, (int) ($props['borderWidth'] ?? 0)) * 2);",
    "        $props = is_array($node['props'] ?? null) ? $node['props'] : [];\n        $legacyPadding = max(0, (int) ($props['padding'] ?? 0));\n        $paddingTop = max(0, (int) ($props['paddingTop'] ?? $legacyPadding));\n        $paddingBottom = max(0, (int) ($props['paddingBottom'] ?? $legacyPadding));\n        $extraPx = $paddingTop + $paddingBottom + (max(0, (int) ($props['borderWidth'] ?? 0)) * 2);",
    'responsive side-padding rows'
)
rr = read(rr_rel)
marker = "    /** @param array{x:int,y:int,w:int,h:int} $g */\n    private static function geometryCss"
if marker not in rr:
    raise SystemExit('ResponsiveRenderer geometryCss marker missing')
responsive_helper = r'''    /** @param array<string,mixed> $node */
    private static function galleryDetailRows(array $node, string $device): int
    {
        $props = is_array($node['props'] ?? null) ? $node['props'] : [];
        $recordId = strtolower(trim((string) ($props['recordId'] ?? '')));
        if ($recordId === '') { $recordId = strtolower(trim(sanitize_text_field((string) wp_unslash($_GET['h18_gallery'] ?? '')))); }
        $count = 0; $hasDescription = false;
        if ($recordId !== '' && preg_match('/^[a-z0-9][a-z0-9._:-]{0,127}$/', $recordId)) {
            $found = ModuleStore::findByRecordId('galleries', $recordId);
            $record = is_array($found) && isset($found['record']) && is_array($found['record']) ? $found['record'] : null;
            if (is_array($record)) {
                $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
                $ids = isset($fields['imageIds']) && is_array($fields['imageIds']) ? array_values(array_filter(array_map('absint', $fields['imageIds']))) : [];
                $count = count($ids);
                $hasDescription = !empty($props['showDescription']) && trim((string) ($fields['description'] ?? '')) !== '';
            }
        }
        $columns = $device === 'mobile' ? 1 : ($device === 'tablet' ? min(2, max(1, (int) ($props['columns'] ?? 4))) : max(1, min(6, (int) ($props['columns'] ?? 4))));
        $imageHeight = max(80, min(700, (int) ($props['imageHeight'] ?? 220)));
        $gap = max(0, min(80, (int) ($props['gap'] ?? 12)));
        $padding = max(0, min(80, (int) ($props['padding'] ?? 16)));
        $imageRows = $count > 0 ? (int) ceil($count / $columns) : 0;
        $px = 88 + ($hasDescription ? 144 : 0) + ($padding * 2);
        if ($imageRows > 0) { $px += ($imageRows * $imageHeight) + (max(0, $imageRows - 1) * $gap); }
        return max(8, (int) ceil($px / LayoutModel::ROW_PX));
    }

'''
write(rr_rel, rr.replace(marker, responsive_helper + marker, 1))

# ---------------------------------------------------------------------------
# One-time V3 detail-layout repair. It recognises only the known V1 regression
# signatures and leaves custom layouts untouched.
# ---------------------------------------------------------------------------
repair = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class V3DetailLayoutRepair
{
    private const EVENT_META = '_vdm_v3_alpha9_event_detail_repaired';
    private const EVENT_BACKUP = '_vdm_v3_alpha9_event_detail_backup';
    private const ALBUM_META = '_vdm_v3_alpha9_album_detail_repaired';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'ensure'], 35);
    }

    public static function ensure(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        self::repairEvent();
        self::repairAlbum();
    }

    private static function repairEvent(): void
    {
        $page = get_page_by_path('event-detalje', OBJECT, 'page');
        if (!$page instanceof \WP_Post) { return; }
        $postId = (int) $page->ID;
        if (get_post_meta($postId, self::EVENT_META, true)) { return; }
        $model = LayoutModel::get($postId);
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        $ids = [];
        foreach ($nodes as $node) { if (is_array($node)) { $ids[(string) ($node['id'] ?? '')] = true; } }
        $known = ['detail-section','event-image','event-facts','eventfield-about','eventfield-program','eventfield-practical'];
        foreach ($known as $id) {
            if (empty($ids[$id])) {
                update_post_meta($postId, self::EVENT_META, ['status'=>'skipped-custom-layout','checkedUtc'=>gmdate('c')]);
                return;
            }
        }
        update_post_meta($postId, self::EVENT_BACKUP, $model);
        $drop = ['event-title'=>true,'event-date'=>true,'event-location'=>true,'event-summary'=>true,'event-description'=>true];
        $positions = [
            'detail-back'=>[3,2,30,7,10],
            'event-image'=>[3,10,114,44,20],
            'event-facts'=>[3,56,114,10,30],
            'eventfield-about'=>[3,68,114,12,40],
            'eventfield-program'=>[3,82,114,12,50],
            'eventfield-practical'=>[3,96,114,12,60],
        ];
        $next = [];
        foreach ($nodes as $node) {
            if (!is_array($node)) { continue; }
            $id = (string) ($node['id'] ?? '');
            if (isset($drop[$id])) { continue; }
            if ($id === 'detail-section') {
                $node['geometry'] = self::geometry(0,0,120,112);
                $node['props'] = is_array($node['props'] ?? null) ? $node['props'] : [];
                $node['props']['minHeightRows'] = 112;
                if (!array_key_exists('paddingBottom', $node['props'])) { $node['props']['paddingBottom'] = 32; }
            } elseif (isset($positions[$id])) {
                [$x,$y,$w,$h,$order] = $positions[$id];
                $node['geometry'] = self::geometry($x,$y,$w,$h);
                $node['order'] = $order;
                $node['parentId'] = 'detail-section';
            }
            $next[] = $node;
        }
        $model['nodes'] = $next;
        $version = LayoutModel::saveVersion($postId, $model, get_current_user_id(), 'V3 alpha.9: gendan oprindelig Eventdetalje-rækkefølge');
        update_post_meta($postId, self::EVENT_META, ['status'=>'repaired','version'=>$version,'repairedUtc'=>gmdate('c')]);
    }

    private static function repairAlbum(): void
    {
        $page = get_page_by_path('album-detalje', OBJECT, 'page');
        if (!$page instanceof \WP_Post) { return; }
        $postId = (int) $page->ID;
        if (get_post_meta($postId, self::ALBUM_META, true)) { return; }
        $model = LayoutModel::get($postId);
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        $changed = false;
        foreach ($nodes as &$node) {
            if (!is_array($node)) { continue; }
            $id = (string) ($node['id'] ?? '');
            if ($id === 'detail-back' && (string) ($node['type'] ?? '') === 'button') {
                $node['props'] = is_array($node['props'] ?? null) ? $node['props'] : [];
                $node['props']['text'] = '← Tilbage til album';
                $changed = true;
            }
            if ($id === 'detail-section' && (string) ($node['type'] ?? '') === 'section') {
                $node['props'] = is_array($node['props'] ?? null) ? $node['props'] : [];
                if (!array_key_exists('paddingBottom', $node['props'])) { $node['props']['paddingBottom'] = 48; }
                $changed = true;
            }
        }
        unset($node);
        if (!$changed) {
            update_post_meta($postId, self::ALBUM_META, ['status'=>'skipped-custom-layout','checkedUtc'=>gmdate('c')]);
            return;
        }
        $model['nodes'] = $nodes;
        $version = LayoutModel::saveVersion($postId, $model, get_current_user_id(), 'V3 alpha.9: album tilbage-link + styrbar bundluft');
        update_post_meta($postId, self::ALBUM_META, ['status'=>'repaired','version'=>$version,'repairedUtc'=>gmdate('c')]);
    }

    /** @return array<string,mixed> */
    private static function geometry(int $x, int $y, int $w, int $h): array
    {
        return [
            'desktop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h],
            'laptop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
            'tablet'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
            'mobile'=>['x'=>0,'y'=>$y,'w'=>120,'h'=>$h,'inheritDesktop'=>false],
        ];
    }

    private function __construct() {}
}
'''
write('src/Migration/V3DetailLayoutRepair.php', repair)

main = read('visual-designer-manager.php')
require_anchor = "require_once H18_CLEAN_DIR . 'src/Migration/SharedPrimaryMenu.php';"
register_anchor = "\\VisualDesignerManager\\Migration\\SharedPrimaryMenu::register();"
if require_anchor not in main or register_anchor not in main:
    raise SystemExit('Alpha.9 migration registration anchors missing')
main = main.replace(require_anchor, require_anchor + "\nrequire_once H18_CLEAN_DIR . 'src/Migration/V3DetailLayoutRepair.php';", 1)
main = main.replace(register_anchor, register_anchor + "\n    \\VisualDesignerManager\\Migration\\V3DetailLayoutRepair::register();", 1)
write('visual-designer-manager.php', main)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not rows or rows[0].get('version') != '3.0.0-alpha.8':
    raise SystemExit('Alpha.8 release-history baseline missing')
alpha9 = {
    'version': VERSION,
    'date': '2026-09-06',
    'items': [
        'Eventdetalje repareres fra den kendte V1 0.1.80/0.1.85 regression til rækkefølgen billede → faktabånd → eventfelter.',
        'Sektioner og kasser får separat padding top/højre/bund/venstre med bagudkompatibel fallback til den gamle fælles padding.',
        'Designerens formular-preview bruger samme felt-gap, breddeberegning og mobile én-kolonne kontrakt som liveformularen.',
        'Billedgalleri viser ikke længere den overflødige hardcodede moduloverskrift; albumdetaljen bruger “Tilbage til album”.',
        'Albumdetaljens grid-højde beregnes ud fra faktisk antal billeder pr. breakpoint, så Footer skubbes efter indholdet; bundluft kan styres med section padding-bottom.',
        'Alpha.8 responsive Header/Page/Footer scopes og 782 px mobil-breakpoint bevares og udvides med dynamiske detailhøjder.'
    ]
}
history_path.write_text(json.dumps({'versions':[alpha9] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Build self-checks.
checks = {
    'visual-designer-manager.php': [
        'Version: 3.0.0-alpha.9', 'V3DetailLayoutRepair.php', 'V3DetailLayoutRepair::register();'
    ],
    'assets/editor-v018-core.js': [
        'paddingTop:', 'paddingRight:', 'paddingBottom:', 'paddingLeft:', 'data-field="paddingBottom"'
    ],
    'assets/admin-v0175.css': [
        '.h18-clean-node-preview--form{padding:0!important', 'gap:var(--vdm-form-field-gap,16px)!important', '@media(max-width:782px)'
    ],
    'src/Frontend/Renderer.php': [
        'private static function galleryDetailRows', 'private static function verticalPaddingPx', "self::galleryDetailRows($node, 'desktop')"
    ],
    'src/Frontend/ResponsiveRenderer.php': [
        'use VisualDesignerManager\\Modules\\ModuleStore;', 'private static function galleryDetailRows', "$type === 'eventfacts' && $device === 'mobile'"
    ],
    'src/Migration/V3DetailLayoutRepair.php': [
        'event-image', 'event-facts', '← Tilbage til album', 'paddingBottom'
    ],
}
for rel, tokens in checks.items():
    text = read(rel)
    for token in tokens:
        if token not in text:
            raise SystemExit(f'Alpha.9 contract token missing in {rel}: {token}')

if '<h2>Køretøjer</h2>' in read(collection_rel):
    raise SystemExit('Gallery collection duplicate heading still present')
if read('release-history.json').find('3.0.0-alpha.9') < 0:
    raise SystemExit('Alpha.9 release history missing')

print('V3 Alpha.9 event detail original-order repair: PASS')
print('V3 Alpha.9 section side-padding: PASS')
print('V3 Alpha.9 Designer/live form geometry: PASS')
print('V3 Alpha.9 gallery heading/back-link/dynamic height: PASS')
print('V3 Alpha.9 responsive dynamic detail rows: PASS')
