from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding="utf-8")


def write(rel: str, value: str) -> None:
    (ROOT / rel).write_text(value, encoding="utf-8")


def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{rel}: expected one replacement anchor, found {count}: {old[:90]!r}")
    write(rel, text.replace(old, new, 1))


def insert_before_once(rel: str, marker: str, block: str, sentinel: str) -> None:
    text = read(rel)
    if sentinel in text:
        return
    count = text.count(marker)
    if count != 1:
        raise SystemExit(f"{rel}: expected one insertion marker, found {count}: {marker[:90]!r}")
    write(rel, text.replace(marker, block + marker, 1))


def prepend_once(rel: str, block: str, sentinel: str) -> None:
    text = read(rel)
    if sentinel in text:
        return
    write(rel, block + text)


# ---------------------------------------------------------------------------
# Version + shared editor CSS
# ---------------------------------------------------------------------------
plugin = "clean/hangar18-manager/hangar18-manager.php"
text = read(plugin)
text2 = re.sub(r"Version:\s*0\.1\.64", "Version: 0.1.65", text, count=1)
text2 = text2.replace("define('H18_CLEAN_VERSION', '0.1.64');", "define('H18_CLEAN_VERSION', '0.1.65');", 1)
if text2 == text and "Version: 0.1.65" not in text:
    raise SystemExit("Plugin version anchors not found")
write(plugin, text2)

replace_once(
    plugin,
    """    wp_enqueue_style(\n        'h18-clean-editor-v0154-menu',\n        H18_CLEAN_URL . 'assets/editor-v0154-menu.css',\n        ['h18-clean-editor-v0153-transparent'],\n        H18_CLEAN_VERSION\n    );\n\n    wp_enqueue_script(\n""",
    """    wp_enqueue_style(\n        'h18-clean-editor-v0154-menu',\n        H18_CLEAN_URL . 'assets/editor-v0154-menu.css',\n        ['h18-clean-editor-v0153-transparent'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_style(\n        'h18-clean-editor-v0165-elements',\n        H18_CLEAN_URL . 'assets/editor-v0165-elements.css',\n        ['h18-clean-editor-v0154-menu'],\n        H18_CLEAN_VERSION\n    );\n\n    wp_enqueue_script(\n""",
)

css = r"""/* Visual Designer Manager 0.1.65 · general element previews */
.h18-clean-node--spacer>.h18-clean-node-preview{min-height:100%;display:flex;align-items:center;justify-content:center;background:repeating-linear-gradient(135deg,rgba(34,113,177,.05),rgba(34,113,177,.05) 8px,rgba(34,113,177,.11) 8px,rgba(34,113,177,.11) 16px);border:1px dashed #72aee6;color:#135e96;font-size:11px;text-transform:uppercase;letter-spacing:.06em}
.h18-clean-node-preview--divider{display:flex;align-items:center;justify-content:center;height:100%;box-sizing:border-box}.h18-vd-divider-line{display:block;box-sizing:border-box}
.h18-clean-node-preview--icon,.h18-clean-node-preview--badge,.h18-clean-node-preview--link{display:flex;align-items:center;height:100%;box-sizing:border-box}.h18-clean-node-preview--icon svg{display:block;width:100%;height:100%;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}
.h18-vd-icon-preview{display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box}.h18-vd-badge-preview{display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;white-space:nowrap}.h18-vd-link-preview{cursor:default}
.h18-clean-node-preview--datalist,.h18-clean-node-preview--table{padding:8px!important;overflow:auto!important}.h18-vd-datalist-preview{width:100%;box-sizing:border-box}.h18-vd-datalist-row{display:grid;grid-template-columns:var(--h18-vd-label-width,40%) minmax(0,1fr);box-sizing:border-box}.h18-vd-datalist-preview.is-stacked .h18-vd-datalist-row{grid-template-columns:1fr}.h18-vd-datalist-label{font-weight:600}.h18-vd-table-preview{width:100%;border-collapse:collapse;table-layout:auto}.h18-vd-table-preview th,.h18-vd-table-preview td{text-align:left;vertical-align:top}
.h18-vd-structured-editor textarea[data-field="dataRows"],.h18-vd-structured-editor textarea[data-field="tableRows"]{min-height:120px;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px}.h18-vd-structured-editor input[data-field="tableHeaders"]{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.h18-vd-element-note{margin:8px 0;padding:8px 10px;border-left:3px solid #72aee6;background:#f0f6fc;color:#1d2327}
"""
write("clean/hangar18-manager/assets/editor-v0165-elements.css", css)


# ---------------------------------------------------------------------------
# Canonical PHP model
# ---------------------------------------------------------------------------
layout = "clean/hangar18-manager/src/Model/LayoutModel.php"
replace_once(
    layout,
    "if (!in_array($type, ['section', 'container', 'text', 'image', 'button', 'menu'], true)) {",
    "if (!in_array($type, ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table'], true)) {",
)

model_props = r"""        if ($type === 'spacer') {
            return $border;
        }
        if ($type === 'divider') {
            $orientation = strtolower((string) ($raw['orientation'] ?? 'horizontal'));
            if (!in_array($orientation, ['horizontal', 'vertical'], true)) { $orientation = 'horizontal'; }
            $lineStyle = strtolower((string) ($raw['lineStyle'] ?? 'solid'));
            if (!in_array($lineStyle, ['solid', 'dashed', 'dotted'], true)) { $lineStyle = 'solid'; }
            return array_merge([
                'orientation' => $orientation,
                'lineColor' => sanitize_hex_color((string) ($raw['lineColor'] ?? '#c3c4c7')) ?: '#c3c4c7',
                'lineWidth' => self::clamp($raw['lineWidth'] ?? 1, 1, 20, 1),
                'lineStyle' => $lineStyle,
            ], $border);
        }
        if ($type === 'icon') {
            $align = strtolower((string) ($raw['align'] ?? 'center'));
            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'center'; }
            return array_merge([
                'icon' => self::iconToken($raw['icon'] ?? 'star'),
                'iconSize' => self::clamp($raw['iconSize'] ?? 32, 8, 240, 32),
                'iconColor' => sanitize_hex_color((string) ($raw['iconColor'] ?? '#30382a')) ?: '#30382a',
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'backgroundTransparent' => array_key_exists('backgroundTransparent', $raw) ? (bool) $raw['backgroundTransparent'] : true,
                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),
                'align' => $align,
            ], $border);
        }
        if ($type === 'badge') {
            $align = strtolower((string) ($raw['align'] ?? 'left'));
            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'left'; }
            return array_merge([
                'text' => sanitize_text_field((string) ($raw['text'] ?? 'Badge')),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#c3ae83')) ?: '#c3ae83',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 13, 8, 80, 13),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 700, 100, 900, 700),
                'paddingX' => self::clamp($raw['paddingX'] ?? 12, 0, 120, 12),
                'paddingY' => self::clamp($raw['paddingY'] ?? 5, 0, 120, 5),
                'radius' => self::clamp($raw['radius'] ?? 20, 0, 100, 20),
                'align' => $align,
            ], $border);
        }
        if ($type === 'link') {
            $linkType = strtolower((string) ($raw['linkType'] ?? 'url'));
            if (!in_array($linkType, ['page', 'url', 'anchor', 'email', 'phone'], true)) { $linkType = 'url'; }
            $align = strtolower((string) ($raw['align'] ?? 'left'));
            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'left'; }
            return array_merge([
                'text' => sanitize_text_field((string) ($raw['text'] ?? 'Læs mere →')),
                'linkType' => $linkType,
                'pageId' => absint($raw['pageId'] ?? 0),
                'url' => sanitize_text_field((string) ($raw['url'] ?? '')),
                'targetBlank' => !empty($raw['targetBlank']),
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#2271b1')) ?: '#2271b1',
                'hoverTextColor' => sanitize_hex_color((string) ($raw['hoverTextColor'] ?? '#135e96')) ?: '#135e96',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 120, 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 600, 100, 900, 600),
                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.3, 0.8, 3.0, 1.3),
                'letterSpacing' => self::clampFloat($raw['letterSpacing'] ?? 0, -10.0, 30.0, 0.0),
                'underline' => array_key_exists('underline', $raw) ? (bool) $raw['underline'] : false,
                'align' => $align,
            ], $border);
        }
        if ($type === 'datalist') {
            $layout = strtolower((string) ($raw['layout'] ?? 'rows'));
            if (!in_array($layout, ['rows', 'stacked'], true)) { $layout = 'rows'; }
            return array_merge([
                'rows' => self::pairRows($raw['rows'] ?? []),
                'layout' => $layout,
                'labelWidth' => self::clamp($raw['labelWidth'] ?? 40, 15, 80, 40),
                'cellPadding' => self::clamp($raw['cellPadding'] ?? 8, 0, 60, 8),
                'showDividers' => array_key_exists('showDividers', $raw) ? (bool) $raw['showDividers'] : true,
                'zebra' => !empty($raw['zebra']),
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#ffffff')) ?: '#ffffff',
                'zebraBackground' => sanitize_hex_color((string) ($raw['zebraBackground'] ?? '#f6f7f7')) ?: '#f6f7f7',
                'lineColor' => sanitize_hex_color((string) ($raw['lineColor'] ?? '#dcdcde')) ?: '#dcdcde',
                'labelColor' => sanitize_hex_color((string) ($raw['labelColor'] ?? '#30382a')) ?: '#30382a',
                'valueColor' => sanitize_hex_color((string) ($raw['valueColor'] ?? '#30382a')) ?: '#30382a',
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 15, 8, 80, 15),
                'labelWeight' => self::clamp($raw['labelWeight'] ?? 600, 100, 900, 600),
                'valueWeight' => self::clamp($raw['valueWeight'] ?? 400, 100, 900, 400),
            ], $border);
        }
        if ($type === 'table') {
            $headers = self::stringList($raw['headers'] ?? [], 12, ['Kolonne 1', 'Kolonne 2', 'Kolonne 3']);
            $mobileMode = strtolower((string) ($raw['mobileMode'] ?? 'scroll'));
            if (!in_array($mobileMode, ['scroll', 'cards'], true)) { $mobileMode = 'scroll'; }
            return array_merge([
                'headers' => $headers,
                'rows' => self::matrixRows($raw['rows'] ?? [], count($headers), 50),
                'headerBackground' => sanitize_hex_color((string) ($raw['headerBackground'] ?? '#30382a')) ?: '#30382a',
                'headerTextColor' => sanitize_hex_color((string) ($raw['headerTextColor'] ?? '#ffffff')) ?: '#ffffff',
                'cellBackground' => sanitize_hex_color((string) ($raw['cellBackground'] ?? '#ffffff')) ?: '#ffffff',
                'cellTextColor' => sanitize_hex_color((string) ($raw['cellTextColor'] ?? '#30382a')) ?: '#30382a',
                'zebra' => array_key_exists('zebra', $raw) ? (bool) $raw['zebra'] : true,
                'zebraBackground' => sanitize_hex_color((string) ($raw['zebraBackground'] ?? '#f6f7f7')) ?: '#f6f7f7',
                'cellBorderColor' => sanitize_hex_color((string) ($raw['cellBorderColor'] ?? '#dcdcde')) ?: '#dcdcde',
                'cellBorderWidth' => self::clamp($raw['cellBorderWidth'] ?? 1, 0, 10, 1),
                'cellPadding' => self::clamp($raw['cellPadding'] ?? 8, 0, 60, 8),
                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),
                'fontSize' => self::clamp($raw['fontSize'] ?? 14, 8, 80, 14),
                'headerWeight' => self::clamp($raw['headerWeight'] ?? 700, 100, 900, 700),
                'mobileMode' => $mobileMode,
            ], $border);
        }
"""
insert_before_once(layout, "        if ($type === 'image') {\n", model_props, "if ($type === 'datalist')")

model_helpers = r"""    /** @param mixed $value @return array<int,array{label:string,value:string}> */
    private static function pairRows($value): array
    {
        $source = is_array($value) ? array_values($value) : [];
        $rows = [];
        foreach (array_slice($source, 0, 50) as $row) {
            if (!is_array($row)) { continue; }
            $label = sanitize_text_field((string) ($row['label'] ?? ''));
            $cellValue = sanitize_text_field((string) ($row['value'] ?? ''));
            if ($label === '' && $cellValue === '') { continue; }
            $rows[] = ['label' => $label, 'value' => $cellValue];
        }
        return $rows ?: [
            ['label' => 'Felt', 'value' => 'Værdi'],
            ['label' => 'Eksempel', 'value' => 'Indhold'],
        ];
    }

    /** @param mixed $value @param array<int,string> $fallback @return array<int,string> */
    private static function stringList($value, int $max, array $fallback): array
    {
        $source = is_array($value) ? array_values($value) : [];
        $out = [];
        foreach (array_slice($source, 0, max(1, $max)) as $item) {
            $cell = sanitize_text_field((string) $item);
            if ($cell !== '') { $out[] = $cell; }
        }
        return $out ?: $fallback;
    }

    /** @param mixed $value @return array<int,array<int,string>> */
    private static function matrixRows($value, int $columns, int $maxRows): array
    {
        $columns = max(1, min(12, $columns));
        $source = is_array($value) ? array_values($value) : [];
        $out = [];
        foreach (array_slice($source, 0, max(1, $maxRows)) as $row) {
            if (!is_array($row)) { continue; }
            $cells = [];
            for ($i = 0; $i < $columns; $i++) {
                $cells[] = sanitize_text_field((string) ($row[$i] ?? ''));
            }
            if (implode('', $cells) !== '') { $out[] = $cells; }
        }
        if (!$out) {
            $sample1 = array_fill(0, $columns, '');
            $sample2 = array_fill(0, $columns, '');
            $sample1[0] = 'Række 1';
            $sample2[0] = 'Række 2';
            if ($columns > 1) { $sample1[1] = 'Værdi'; $sample2[1] = 'Værdi'; }
            $out = [$sample1, $sample2];
        }
        return $out;
    }

    /** @param mixed $value */
    private static function iconToken($value): string
    {
        $token = sanitize_key((string) $value);
        return in_array($token, ['star', 'check', 'info', 'calendar', 'camera', 'people', 'ruler', 'weight', 'gear', 'link'], true) ? $token : 'star';
    }

"""
insert_before_once(layout, "    /** @param array<string,mixed> $raw @return array<string,mixed> */\n    private static function borderProps", model_helpers, "private static function pairRows")


# ---------------------------------------------------------------------------
# Editor core: types, normalization, previews, Inspector and edit handlers
# ---------------------------------------------------------------------------
editor = "clean/hangar18-manager/assets/editor-v018-core.js"
replace_once(editor, "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu'];", "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table'];")
replace_once(editor, "function typeLabel(type) { return ({section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap',menu:'Menu'})[String(type || '')] || String(type || 'Element'); }", "function typeLabel(type) { return ({section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap',menu:'Menu',spacer:'Mellemrum',divider:'Skillelinje',icon:'Ikon',badge:'Badge',link:'Link',datalist:'Data List',table:'Tabel'})[String(type || '')] || String(type || 'Element'); }")

js_helpers = r"""    function normalizePairRows(raw) {
        const source = Array.isArray(raw) ? raw : [];
        const rows = source.slice(0, 50).map(function (row) {
            row = row && typeof row === 'object' ? row : {};
            return { label: String(row.label || '').trim(), value: String(row.value || '').trim() };
        }).filter(function (row) { return row.label || row.value; });
        return rows.length ? rows : [{label:'Felt',value:'Værdi'},{label:'Eksempel',value:'Indhold'}];
    }
    function normalizeHeaders(raw) {
        const headers = (Array.isArray(raw) ? raw : []).slice(0, 12).map(function (item) { return String(item || '').trim(); }).filter(Boolean);
        return headers.length ? headers : ['Kolonne 1','Kolonne 2','Kolonne 3'];
    }
    function normalizeMatrixRows(raw, columns) {
        columns = clamp(parseInt(columns || 1, 10) || 1, 1, 12);
        const rows = (Array.isArray(raw) ? raw : []).slice(0, 50).map(function (row) {
            const source = Array.isArray(row) ? row : [];
            const cells = [];
            for (let i = 0; i < columns; i += 1) { cells.push(String(source[i] || '').trim()); }
            return cells;
        }).filter(function (row) { return row.join('').length > 0; });
        if (rows.length) { return rows; }
        const a = Array(columns).fill(''); const b = Array(columns).fill('');
        a[0] = 'Række 1'; b[0] = 'Række 2'; if (columns > 1) { a[1] = 'Værdi'; b[1] = 'Værdi'; }
        return [a,b];
    }
    function pairRowsText(rows) { return normalizePairRows(rows).map(function (row) { return row.label + ' | ' + row.value; }).join('\n'); }
    function parsePairRowsText(value) {
        return String(value || '').split(/\r?\n/).slice(0,50).map(function (line) {
            const parts = line.split('|'); return {label:String(parts.shift() || '').trim(),value:String(parts.join('|') || '').trim()};
        }).filter(function (row) { return row.label || row.value; });
    }
    function headersText(headers) { return normalizeHeaders(headers).join(' | '); }
    function parseHeadersText(value) { return normalizeHeaders(String(value || '').split('|')); }
    function matrixRowsText(rows, columns) { return normalizeMatrixRows(rows, columns).map(function (row) { return row.join(' | '); }).join('\n'); }
    function parseMatrixRowsText(value, columns) {
        const rows = String(value || '').split(/\r?\n/).slice(0,50).map(function (line) { return line.split('|').map(function (cell) { return cell.trim(); }); });
        return normalizeMatrixRows(rows, columns);
    }
    function iconSvgMarkup(token) {
        const shapes = {
            star:'<polygon points="12 2.7 14.8 8.4 21 9.3 16.5 13.7 17.6 20 12 17 6.4 20 7.5 13.7 3 9.3 9.2 8.4 12 2.7"/>',
            check:'<polyline points="4 12.5 9.5 18 20 6"/>',
            info:'<circle cx="12" cy="12" r="9"/><line x1="12" y1="10.5" x2="12" y2="17"/><line x1="12" y1="7" x2="12.01" y2="7"/>',
            calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><line x1="7" y1="3" x2="7" y2="7"/><line x1="17" y1="3" x2="17" y2="7"/><line x1="3" y1="10" x2="21" y2="10"/>',
            camera:'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7l1.5-3h5L16 7"/><circle cx="12" cy="13.5" r="3.5"/>',
            people:'<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c.8-4 3-6 6-6s5.2 2 6 6"/><path d="M14 15c3.5-.5 6 1.1 7 4"/>',
            ruler:'<path d="M4 17L17 4l3 3L7 20z"/><line x1="13" y1="8" x2="16" y2="11"/><line x1="10" y1="11" x2="12" y2="13"/><line x1="7" y1="14" x2="10" y2="17"/>',
            weight:'<path d="M6 8h12l2 12H4z"/><path d="M9 8a3 3 0 016 0"/><line x1="12" y1="11" x2="14" y2="14"/>',
            gear:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
            link:'<path d="M10 13a5 5 0 007 0l2-2a5 5 0 00-7-7l-1 1"/><path d="M14 11a5 5 0 00-7 0l-2 2a5 5 0 007 7l1-1"/>'
        };
        return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + (shapes[String(token || '')] || shapes.star) + '</svg>';
    }

"""
insert_before_once(editor, "    function normalizeProps(type, raw) {\n", js_helpers, "function normalizePairRows(raw)")

js_props = r"""        if (type === 'spacer') { return common; }
        if (type === 'divider') {
            return Object.assign(common, {
                orientation: ['horizontal','vertical'].includes(String(raw.orientation || '').toLowerCase()) ? String(raw.orientation).toLowerCase() : 'horizontal',
                lineColor: /^#[0-9a-f]{6}$/i.test(String(raw.lineColor || '')) ? String(raw.lineColor).toLowerCase() : '#c3c4c7',
                lineWidth: clamp(parseInt(raw.lineWidth || 1, 10) || 1, 1, 20),
                lineStyle: ['solid','dashed','dotted'].includes(String(raw.lineStyle || '').toLowerCase()) ? String(raw.lineStyle).toLowerCase() : 'solid'
            });
        }
        if (type === 'icon') {
            return Object.assign(common, {
                icon: ['star','check','info','calendar','camera','people','ruler','weight','gear','link'].includes(String(raw.icon || '').toLowerCase()) ? String(raw.icon).toLowerCase() : 'star',
                iconSize: clamp(parseInt(raw.iconSize || 32, 10) || 32, 8, 240),
                iconColor: /^#[0-9a-f]{6}$/i.test(String(raw.iconColor || '')) ? String(raw.iconColor).toLowerCase() : '#30382a',
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#ffffff',
                backgroundTransparent: raw.backgroundTransparent !== false,
                padding: clamp(parseInt(raw.padding || 0, 10) || 0, 0, 120),
                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),
                align: ['left','center','right'].includes(String(raw.align || '').toLowerCase()) ? String(raw.align).toLowerCase() : 'center'
            });
        }
        if (type === 'badge') {
            return Object.assign(common, {
                text: String(raw.text || 'Badge'),
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#c3ae83',
                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#30382a',
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 13, 10) || 13, 8, 80),
                fontWeight: clamp(parseInt(raw.fontWeight || 700, 10) || 700, 100, 900),
                paddingX: clamp(parseInt(raw.paddingX || 12, 10) || 12, 0, 120),
                paddingY: clamp(parseInt(raw.paddingY || 5, 10) || 5, 0, 120),
                radius: clamp(parseInt(raw.radius || 20, 10) || 20, 0, 100),
                align: ['left','center','right'].includes(String(raw.align || '').toLowerCase()) ? String(raw.align).toLowerCase() : 'left'
            });
        }
        if (type === 'link') {
            return Object.assign(common, {
                text: String(raw.text || 'Læs mere →'),
                linkType: ['page','url','anchor','email','phone'].includes(String(raw.linkType || '').toLowerCase()) ? String(raw.linkType).toLowerCase() : 'url',
                pageId: parseInt(raw.pageId || 0, 10) || 0,
                url: String(raw.url || ''),
                targetBlank: !!raw.targetBlank,
                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#2271b1',
                hoverTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.hoverTextColor || '')) ? String(raw.hoverTextColor).toLowerCase() : '#135e96',
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 16, 10) || 16, 8, 120),
                fontWeight: clamp(parseInt(raw.fontWeight || 600, 10) || 600, 100, 900),
                lineHeight: Math.max(0.8, Math.min(3, parseFloat(raw.lineHeight || 1.3) || 1.3)),
                letterSpacing: Math.max(-10, Math.min(30, parseFloat(raw.letterSpacing || 0) || 0)),
                underline: !!raw.underline,
                align: ['left','center','right'].includes(String(raw.align || '').toLowerCase()) ? String(raw.align).toLowerCase() : 'left'
            });
        }
        if (type === 'datalist') {
            return Object.assign(common, {
                rows: normalizePairRows(raw.rows),
                layout: ['rows','stacked'].includes(String(raw.layout || '').toLowerCase()) ? String(raw.layout).toLowerCase() : 'rows',
                labelWidth: clamp(parseInt(raw.labelWidth || 40, 10) || 40, 15, 80),
                cellPadding: clamp(parseInt(raw.cellPadding || 8, 10) || 8, 0, 60),
                showDividers: raw.showDividers !== false,
                zebra: !!raw.zebra,
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#ffffff',
                zebraBackground: /^#[0-9a-f]{6}$/i.test(String(raw.zebraBackground || '')) ? String(raw.zebraBackground).toLowerCase() : '#f6f7f7',
                lineColor: /^#[0-9a-f]{6}$/i.test(String(raw.lineColor || '')) ? String(raw.lineColor).toLowerCase() : '#dcdcde',
                labelColor: /^#[0-9a-f]{6}$/i.test(String(raw.labelColor || '')) ? String(raw.labelColor).toLowerCase() : '#30382a',
                valueColor: /^#[0-9a-f]{6}$/i.test(String(raw.valueColor || '')) ? String(raw.valueColor).toLowerCase() : '#30382a',
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 15, 10) || 15, 8, 80),
                labelWeight: clamp(parseInt(raw.labelWeight || 600, 10) || 600, 100, 900),
                valueWeight: clamp(parseInt(raw.valueWeight || 400, 10) || 400, 100, 900)
            });
        }
        if (type === 'table') {
            const headers = normalizeHeaders(raw.headers);
            return Object.assign(common, {
                headers: headers,
                rows: normalizeMatrixRows(raw.rows, headers.length),
                headerBackground: /^#[0-9a-f]{6}$/i.test(String(raw.headerBackground || '')) ? String(raw.headerBackground).toLowerCase() : '#30382a',
                headerTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.headerTextColor || '')) ? String(raw.headerTextColor).toLowerCase() : '#ffffff',
                cellBackground: /^#[0-9a-f]{6}$/i.test(String(raw.cellBackground || '')) ? String(raw.cellBackground).toLowerCase() : '#ffffff',
                cellTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.cellTextColor || '')) ? String(raw.cellTextColor).toLowerCase() : '#30382a',
                zebra: raw.zebra !== false,
                zebraBackground: /^#[0-9a-f]{6}$/i.test(String(raw.zebraBackground || '')) ? String(raw.zebraBackground).toLowerCase() : '#f6f7f7',
                cellBorderColor: /^#[0-9a-f]{6}$/i.test(String(raw.cellBorderColor || '')) ? String(raw.cellBorderColor).toLowerCase() : '#dcdcde',
                cellBorderWidth: clamp(parseInt(raw.cellBorderWidth || 1, 10) || 0, 0, 10),
                cellPadding: clamp(parseInt(raw.cellPadding || 8, 10) || 8, 0, 60),
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 14, 10) || 14, 8, 80),
                headerWeight: clamp(parseInt(raw.headerWeight || 700, 10) || 700, 100, 900),
                mobileMode: ['scroll','cards'].includes(String(raw.mobileMode || '').toLowerCase()) ? String(raw.mobileMode).toLowerCase() : 'scroll'
            });
        }
"""
insert_before_once(editor, "        if (type === 'image') {\n", js_props, "if (type === 'datalist')")

replace_once(
    editor,
    "const defaultRows = { section: 20, container: 16, text: 14, image: 20, button: 8, menu: 10 };",
    "const defaultRows = { section: 20, container: 16, text: 14, image: 20, button: 8, menu: 10, spacer: 4, divider: 6, icon: 10, badge: 8, link: 8, datalist: 18, table: 22 };",
)

replace_once(
    editor,
    "title.textContent = ({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP',menu:'MENU'}[node.type] || node.type.toUpperCase()) + ' · ' + node.id.slice(-8);",
    "title.textContent = ({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP',menu:'MENU',spacer:'MELLEMRUM',divider:'SKILLELINJE',icon:'IKON',badge:'BADGE',link:'LINK',datalist:'DATA LIST',table:'TABEL'}[node.type] || node.type.toUpperCase()) + ' · ' + node.id.slice(-8);",
)
replace_once(
    editor,
    "let html = '<div class=\"h18-clean-inspector-head\"><strong>' + escapeHtml(({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP',menu:'MENU'}[node.type] || node.type.toUpperCase())) + '</strong><code>' + escapeHtml(node.id) + '</code></div>';",
    "let html = '<div class=\"h18-clean-inspector-head\"><strong>' + escapeHtml(({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP',menu:'MENU',spacer:'MELLEMRUM',divider:'SKILLELINJE',icon:'IKON',badge:'BADGE',link:'LINK',datalist:'DATA LIST',table:'TABEL'}[node.type] || node.type.toUpperCase())) + '</strong><code>' + escapeHtml(node.id) + '</code></div>';",
)

preview_branches = r"""        } else if (node.type === 'spacer') {
            wrap.classList.add('h18-clean-node-preview--spacer');
            wrap.textContent = 'Mellemrum · ' + Math.max(0, node.geometry.desktop.h * ROW_PX) + ' px';
        } else if (node.type === 'divider') {
            wrap.classList.add('h18-clean-node-preview--divider');
            const line = document.createElement('span');
            line.className = 'h18-vd-divider-line';
            const vertical = node.props.orientation === 'vertical';
            line.style.width = vertical ? String(node.props.lineWidth || 1) + 'px' : '100%';
            line.style.height = vertical ? '100%' : String(node.props.lineWidth || 1) + 'px';
            line.style.borderStyle = node.props.lineStyle || 'solid';
            line.style.borderColor = node.props.lineColor || '#c3c4c7';
            line.style.borderWidth = vertical ? '0 0 0 ' + String(node.props.lineWidth || 1) + 'px' : String(node.props.lineWidth || 1) + 'px 0 0 0';
            wrap.appendChild(line);
        } else if (node.type === 'icon') {
            wrap.classList.add('h18-clean-node-preview--icon');
            wrap.style.justifyContent = ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'center';
            const icon = document.createElement('span');
            icon.className = 'h18-vd-icon-preview';
            icon.style.width = String(node.props.iconSize || 32) + 'px'; icon.style.height = String(node.props.iconSize || 32) + 'px';
            icon.style.color = node.props.iconColor || '#30382a';
            icon.style.background = node.props.backgroundTransparent === false ? (node.props.background || '#ffffff') : 'transparent';
            icon.style.padding = String(node.props.padding || 0) + 'px'; icon.style.borderRadius = String(node.props.radius || 0) + 'px';
            icon.innerHTML = iconSvgMarkup(node.props.icon || 'star'); wrap.appendChild(icon);
        } else if (node.type === 'badge') {
            wrap.classList.add('h18-clean-node-preview--badge');
            wrap.style.justifyContent = ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-start';
            const badge = document.createElement('span'); badge.className = 'h18-vd-badge-preview'; badge.textContent = String(node.props.text || 'Badge');
            badge.style.background = node.props.background || '#c3ae83'; badge.style.color = node.props.textColor || '#30382a'; badge.style.fontFamily = fontCss(node.props.fontFamily || 'system');
            badge.style.fontSize = String(node.props.fontSize || 13) + 'px'; badge.style.fontWeight = String(node.props.fontWeight || 700); badge.style.padding = String(node.props.paddingY || 5) + 'px ' + String(node.props.paddingX || 12) + 'px'; badge.style.borderRadius = String(node.props.radius || 20) + 'px'; wrap.appendChild(badge);
        } else if (node.type === 'link') {
            wrap.classList.add('h18-clean-node-preview--link'); wrap.style.justifyContent = ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-start';
            const link = document.createElement('span'); link.className = 'h18-vd-link-preview'; link.textContent = String(node.props.text || 'Læs mere →'); link.style.color = node.props.textColor || '#2271b1'; link.style.fontFamily = fontCss(node.props.fontFamily || 'system'); link.style.fontSize = String(node.props.fontSize || 16) + 'px'; link.style.fontWeight = String(node.props.fontWeight || 600); link.style.lineHeight = String(node.props.lineHeight || 1.3); link.style.letterSpacing = String(node.props.letterSpacing || 0) + 'px'; link.style.textDecoration = node.props.underline ? 'underline' : 'none'; wrap.appendChild(link);
        } else if (node.type === 'datalist') {
            wrap.classList.add('h18-clean-node-preview--datalist'); const list = document.createElement('div'); list.className = 'h18-vd-datalist-preview' + (node.props.layout === 'stacked' ? ' is-stacked' : ''); list.style.setProperty('--h18-vd-label-width', String(node.props.labelWidth || 40) + '%'); list.style.fontFamily = fontCss(node.props.fontFamily || 'system'); list.style.fontSize = String(node.props.fontSize || 15) + 'px';
            normalizePairRows(node.props.rows).forEach(function (row, index) { const item = document.createElement('div'); item.className = 'h18-vd-datalist-row'; item.style.background = node.props.zebra && index % 2 ? (node.props.zebraBackground || '#f6f7f7') : (node.props.background || '#ffffff'); if (node.props.showDividers && index) { item.style.borderTop = '1px solid ' + (node.props.lineColor || '#dcdcde'); } const label = document.createElement('span'); label.className = 'h18-vd-datalist-label'; label.textContent = row.label; label.style.padding = String(node.props.cellPadding || 8) + 'px'; label.style.color = node.props.labelColor || '#30382a'; label.style.fontWeight = String(node.props.labelWeight || 600); const value = document.createElement('span'); value.textContent = row.value; value.style.padding = String(node.props.cellPadding || 8) + 'px'; value.style.color = node.props.valueColor || '#30382a'; value.style.fontWeight = String(node.props.valueWeight || 400); item.appendChild(label); item.appendChild(value); list.appendChild(item); }); wrap.appendChild(list);
        } else if (node.type === 'table') {
            wrap.classList.add('h18-clean-node-preview--table'); const table = document.createElement('table'); table.className = 'h18-vd-table-preview'; table.style.fontFamily = fontCss(node.props.fontFamily || 'system'); table.style.fontSize = String(node.props.fontSize || 14) + 'px'; const headers = normalizeHeaders(node.props.headers); const head = document.createElement('thead'); const hr = document.createElement('tr'); headers.forEach(function (value) { const th = document.createElement('th'); th.textContent = value; th.style.background = node.props.headerBackground || '#30382a'; th.style.color = node.props.headerTextColor || '#ffffff'; th.style.fontWeight = String(node.props.headerWeight || 700); th.style.padding = String(node.props.cellPadding || 8) + 'px'; th.style.border = String(node.props.cellBorderWidth || 0) + 'px solid ' + (node.props.cellBorderColor || '#dcdcde'); hr.appendChild(th); }); head.appendChild(hr); table.appendChild(head); const body = document.createElement('tbody'); normalizeMatrixRows(node.props.rows, headers.length).forEach(function (row, index) { const tr = document.createElement('tr'); row.forEach(function (value) { const td = document.createElement('td'); td.textContent = value; td.style.background = node.props.zebra && index % 2 ? (node.props.zebraBackground || '#f6f7f7') : (node.props.cellBackground || '#ffffff'); td.style.color = node.props.cellTextColor || '#30382a'; td.style.padding = String(node.props.cellPadding || 8) + 'px'; td.style.border = String(node.props.cellBorderWidth || 0) + 'px solid ' + (node.props.cellBorderColor || '#dcdcde'); tr.appendChild(td); }); body.appendChild(tr); }); table.appendChild(body); wrap.appendChild(table);
"""
insert_before_once(editor, "        } else if (node.type === 'image') {\n", preview_branches, "node.type === 'datalist'")

inspector_branches = r"""        } else if (node.type === 'spacer') {
            html += '<div class="h18-vd-element-note"><strong>Mellemrum</strong><br>Elementet er usynligt på frontend. Brug Højde ovenfor og responsive Desktop/Laptop/Tablet/Mobil-indstillinger til at styre luften.</div>';
        } else if (node.type === 'divider') {
            html += '<label>Retning<select data-field="orientation"><option value="horizontal"' + (node.props.orientation === 'horizontal' ? ' selected' : '') + '>Vandret</option><option value="vertical"' + (node.props.orientation === 'vertical' ? ' selected' : '') + '>Lodret</option></select></label><div class="h18-clean-field-grid"><label>Tykkelse px<input data-field="lineWidth" type="number" min="1" max="20" value="' + (node.props.lineWidth || 1) + '"></label><label>Farve<input data-field="lineColor" type="color" value="' + escapeAttr(node.props.lineColor || '#c3c4c7') + '"></label></div><label>Stil<select data-field="lineStyle"><option value="solid"' + (node.props.lineStyle === 'solid' ? ' selected' : '') + '>Solid</option><option value="dashed"' + (node.props.lineStyle === 'dashed' ? ' selected' : '') + '>Stiplet</option><option value="dotted"' + (node.props.lineStyle === 'dotted' ? ' selected' : '') + '>Prikket</option></select></label>';
        } else if (node.type === 'icon') {
            html += '<label>Ikon<select data-field="icon">' + [['star','Stjerne'],['check','Check'],['info','Info'],['calendar','Kalender'],['camera','Kamera'],['people','Personer'],['ruler','Lineal'],['weight','Vægt'],['gear','Tandhjul'],['link','Link']].map(function (item) { return '<option value="' + item[0] + '"' + (node.props.icon === item[0] ? ' selected' : '') + '>' + item[1] + '</option>'; }).join('') + '</select></label><div class="h18-clean-field-grid"><label>Størrelse px<input data-field="iconSize" type="number" min="8" max="240" value="' + (node.props.iconSize || 32) + '"></label><label>Farve<input data-field="iconColor" type="color" value="' + escapeAttr(node.props.iconColor || '#30382a') + '"></label></div><label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label><label class="h18-clean-checkbox"><input data-field="backgroundTransparent" type="checkbox"' + (node.props.backgroundTransparent !== false ? ' checked' : '') + '> Gennemsigtig baggrund</label><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#ffffff') + '"></label><div class="h18-clean-field-grid"><label>Padding px<input data-field="padding" type="number" min="0" max="120" value="' + (node.props.padding || 0) + '"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 0) + '"></label></div>';
        } else if (node.type === 'badge') {
            html += '<label>Tekst<input data-field="badgeText" type="text" value="' + escapeAttr(node.props.text || 'Badge') + '"></label><label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label><div class="h18-clean-field-grid"><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#c3ae83') + '"></label><label>Tekst<input data-field="textColor" type="color" value="' + escapeAttr(node.props.textColor || '#30382a') + '"></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="80" value="' + (node.props.fontSize || 13) + '"></label><label>Tykkelse<input data-field="fontWeight" type="number" min="100" max="900" step="100" value="' + (node.props.fontWeight || 700) + '"></label><label>Padding X<input data-field="paddingX" type="number" min="0" max="120" value="' + (node.props.paddingX || 12) + '"></label><label>Padding Y<input data-field="paddingY" type="number" min="0" max="120" value="' + (node.props.paddingY || 5) + '"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 20) + '"></label></div>';
        } else if (node.type === 'link') {
            html += '<label>Linktekst<input data-field="linkText" type="text" value="' + escapeAttr(node.props.text || 'Læs mere →') + '"></label><label>Linktype<select data-field="linkType"><option value="page"' + (node.props.linkType === 'page' ? ' selected' : '') + '>Intern side</option><option value="url"' + (node.props.linkType === 'url' ? ' selected' : '') + '>Ekstern URL</option><option value="anchor"' + (node.props.linkType === 'anchor' ? ' selected' : '') + '>Anker</option><option value="email"' + (node.props.linkType === 'email' ? ' selected' : '') + '>E-mail</option><option value="phone"' + (node.props.linkType === 'phone' ? ' selected' : '') + '>Telefon</option></select></label>';
            if (node.props.linkType === 'page') { html += '<label>Intern side<select data-field="pageId"><option value="0">Vælg side…</option>' + (Array.isArray(CFG.pages) ? CFG.pages.map(function (page) { const id = parseInt(page.id || 0, 10) || 0; return '<option value="' + id + '"' + (parseInt(node.props.pageId || 0, 10) === id ? ' selected' : '') + '>' + escapeHtml(String(page.title || ('Side ' + id))) + '</option>'; }).join('') : '') + '</select></label>'; } else { html += '<label>Destination<input data-field="url" type="text" value="' + escapeAttr(node.props.url || '') + '"></label>'; }
            html += '<label class="h18-clean-checkbox"><input data-field="targetBlank" type="checkbox"' + (node.props.targetBlank ? ' checked' : '') + '> Åbn i ny fane</label><label class="h18-clean-checkbox"><input data-field="underline" type="checkbox"' + (node.props.underline ? ' checked' : '') + '> Understreg link</label><label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label><div class="h18-clean-field-grid"><label>Tekstfarve<input data-field="textColor" type="color" value="' + escapeAttr(node.props.textColor || '#2271b1') + '"></label><label>Hoverfarve<input data-field="hoverTextColor" type="color" value="' + escapeAttr(node.props.hoverTextColor || '#135e96') + '"></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="120" value="' + (node.props.fontSize || 16) + '"></label><label>Tykkelse<input data-field="fontWeight" type="number" min="100" max="900" step="100" value="' + (node.props.fontWeight || 600) + '"></label></div>';
        } else if (node.type === 'datalist') {
            html += '<div class="h18-vd-structured-editor"><div class="h18-vd-element-note"><strong>Statisk Data List · test</strong><br>Én linje pr. felt: <code>Felt | Værdi</code>. Dynamisk datakilde kobles på i næste fundament-version.</div><label>Rækker<textarea data-field="dataRows" rows="7">' + escapeHtml(pairRowsText(node.props.rows)) + '</textarea></label><label>Layout<select data-field="dataLayout"><option value="rows"' + (node.props.layout === 'rows' ? ' selected' : '') + '>Felt + værdi i samme række</option><option value="stacked"' + (node.props.layout === 'stacked' ? ' selected' : '') + '>Felt over værdi</option></select></label><div class="h18-clean-field-grid"><label>Labelbredde %<input data-field="labelWidth" type="number" min="15" max="80" value="' + (node.props.labelWidth || 40) + '"></label><label>Cell padding px<input data-field="cellPadding" type="number" min="0" max="60" value="' + (node.props.cellPadding || 8) + '"></label><label>Skrift px<input data-field="fontSize" type="number" min="8" max="80" value="' + (node.props.fontSize || 15) + '"></label><label>Label tykkelse<input data-field="labelWeight" type="number" min="100" max="900" step="100" value="' + (node.props.labelWeight || 600) + '"></label><label>Værdi tykkelse<input data-field="valueWeight" type="number" min="100" max="900" step="100" value="' + (node.props.valueWeight || 400) + '"></label></div><label class="h18-clean-checkbox"><input data-field="showDividers" type="checkbox"' + (node.props.showDividers !== false ? ' checked' : '') + '> Skillelinjer mellem rækker</label><label class="h18-clean-checkbox"><input data-field="zebra" type="checkbox"' + (node.props.zebra ? ' checked' : '') + '> Zebra-baggrund</label><div class="h18-clean-field-grid"><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#ffffff') + '"></label><label>Zebra<input data-field="zebraBackground" type="color" value="' + escapeAttr(node.props.zebraBackground || '#f6f7f7') + '"></label><label>Linje<input data-field="lineColor" type="color" value="' + escapeAttr(node.props.lineColor || '#dcdcde') + '"></label><label>Label<input data-field="labelColor" type="color" value="' + escapeAttr(node.props.labelColor || '#30382a') + '"></label><label>Værdi<input data-field="valueColor" type="color" value="' + escapeAttr(node.props.valueColor || '#30382a') + '"></label></div></div>';
        } else if (node.type === 'table') {
            const tableHeaders = normalizeHeaders(node.props.headers);
            html += '<div class="h18-vd-structured-editor"><div class="h18-vd-element-note"><strong>Statisk Tabel · test</strong><br>Kolonner og rækker redigeres med <code>|</code> som separator. Mobil kan scrolle eller vises som kort.</div><label>Kolonner<input data-field="tableHeaders" type="text" value="' + escapeAttr(headersText(tableHeaders)) + '"></label><label>Rækker<textarea data-field="tableRows" rows="8">' + escapeHtml(matrixRowsText(node.props.rows, tableHeaders.length)) + '</textarea></label><label>Mobilvisning<select data-field="mobileTableMode"><option value="scroll"' + (node.props.mobileMode === 'scroll' ? ' selected' : '') + '>Horisontal scroll</option><option value="cards"' + (node.props.mobileMode === 'cards' ? ' selected' : '') + '>Kort · kolonnenavn + værdi</option></select></label><div class="h18-clean-field-grid"><label>Cell padding px<input data-field="cellPadding" type="number" min="0" max="60" value="' + (node.props.cellPadding || 8) + '"></label><label>Cell ramme px<input data-field="cellBorderWidth" type="number" min="0" max="10" value="' + (node.props.cellBorderWidth || 0) + '"></label><label>Skrift px<input data-field="fontSize" type="number" min="8" max="80" value="' + (node.props.fontSize || 14) + '"></label><label>Header tykkelse<input data-field="headerWeight" type="number" min="100" max="900" step="100" value="' + (node.props.headerWeight || 700) + '"></label></div><label class="h18-clean-checkbox"><input data-field="zebra" type="checkbox"' + (node.props.zebra !== false ? ' checked' : '') + '> Zebra-rækker</label><div class="h18-clean-field-grid"><label>Header baggrund<input data-field="headerBackground" type="color" value="' + escapeAttr(node.props.headerBackground || '#30382a') + '"></label><label>Header tekst<input data-field="headerTextColor" type="color" value="' + escapeAttr(node.props.headerTextColor || '#ffffff') + '"></label><label>Cell baggrund<input data-field="cellBackground" type="color" value="' + escapeAttr(node.props.cellBackground || '#ffffff') + '"></label><label>Cell tekst<input data-field="cellTextColor" type="color" value="' + escapeAttr(node.props.cellTextColor || '#30382a') + '"></label><label>Zebra<input data-field="zebraBackground" type="color" value="' + escapeAttr(node.props.zebraBackground || '#f6f7f7') + '"></label><label>Cell ramme<input data-field="cellBorderColor" type="color" value="' + escapeAttr(node.props.cellBorderColor || '#dcdcde') + '"></label></div></div>';
"""
insert_before_once(editor, "        } else if (node.type === 'image') {\n", inspector_branches, "Statisk Tabel · test")

# Spacer is deliberately invisible on frontend; do not expose generic painted border/spacing controls there.
replace_once(
    editor,
    "        html += '<div class=\"h18-clean-v0111-layout-style\"><strong>Ramme og afstand</strong><div class=\"h18-clean-field-grid\">';",
    "        if (node.type !== 'spacer') { html += '<div class=\"h18-clean-v0111-layout-style\"><strong>Ramme og afstand</strong><div class=\"h18-clean-field-grid\">';",
)
replace_once(
    editor,
    "        html += '</div><p class=\"description\">0 = ingen ramme/afstand. X er luft mod næste element til højre; Y er luft mod næste element under.</p></div>';\n        html += '<button type=\"button\" class=\"button button-link-delete\" id=\"h18-clean-delete\">",
    "        html += '</div><p class=\"description\">0 = ingen ramme/afstand. X er luft mod næste element til højre; Y er luft mod næste element under.</p></div>'; }\n        html += '<button type=\"button\" class=\"button button-link-delete\" id=\"h18-clean-delete\">",
)

handler_fields = r"""                else if (field === 'badgeText') { current.props.text = String(control.value || 'Badge'); }
                else if (field === 'linkText') { current.props.text = String(control.value || 'Læs mere →'); }
                else if (field === 'underline') { current.props.underline = !!control.checked; }
                else if (field === 'lineWidth') { current.props.lineWidth = clamp(parseInt(control.value || 1, 10) || 1, 1, 20); }
                else if (field === 'lineColor') { current.props.lineColor = normalizeColor(control.value || '#dcdcde'); }
                else if (field === 'lineStyle') { current.props.lineStyle = ['solid','dashed','dotted'].includes(control.value) ? control.value : 'solid'; }
                else if (field === 'icon') { current.props.icon = ['star','check','info','calendar','camera','people','ruler','weight','gear','link'].includes(control.value) ? control.value : 'star'; }
                else if (field === 'iconSize') { current.props.iconSize = clamp(parseInt(control.value || 32, 10) || 32, 8, 240); }
                else if (field === 'iconColor') { current.props.iconColor = normalizeColor(control.value || '#30382a'); }
                else if (field === 'dataRows') { current.props.rows = normalizePairRows(parsePairRowsText(control.value)); }
                else if (field === 'dataLayout') { current.props.layout = ['rows','stacked'].includes(control.value) ? control.value : 'rows'; }
                else if (field === 'labelWidth') { current.props.labelWidth = clamp(parseInt(control.value || 40, 10) || 40, 15, 80); }
                else if (field === 'cellPadding') { current.props.cellPadding = clamp(parseInt(control.value || 8, 10) || 8, 0, 60); }
                else if (field === 'showDividers') { current.props.showDividers = !!control.checked; }
                else if (field === 'zebra') { current.props.zebra = !!control.checked; }
                else if (field === 'zebraBackground') { current.props.zebraBackground = normalizeColor(control.value || '#f6f7f7'); }
                else if (field === 'labelColor') { current.props.labelColor = normalizeColor(control.value || '#30382a'); }
                else if (field === 'valueColor') { current.props.valueColor = normalizeColor(control.value || '#30382a'); }
                else if (field === 'labelWeight') { current.props.labelWeight = clamp(parseInt(control.value || 600, 10) || 600, 100, 900); }
                else if (field === 'valueWeight') { current.props.valueWeight = clamp(parseInt(control.value || 400, 10) || 400, 100, 900); }
                else if (field === 'tableHeaders') { current.props.headers = parseHeadersText(control.value); current.props.rows = normalizeMatrixRows(current.props.rows, current.props.headers.length); }
                else if (field === 'tableRows') { current.props.rows = parseMatrixRowsText(control.value, normalizeHeaders(current.props.headers).length); }
                else if (field === 'headerBackground') { current.props.headerBackground = normalizeColor(control.value || '#30382a'); }
                else if (field === 'headerTextColor') { current.props.headerTextColor = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'cellBackground') { current.props.cellBackground = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'cellTextColor') { current.props.cellTextColor = normalizeColor(control.value || '#30382a'); }
                else if (field === 'cellBorderColor') { current.props.cellBorderColor = normalizeColor(control.value || '#dcdcde'); }
                else if (field === 'cellBorderWidth') { current.props.cellBorderWidth = clamp(parseInt(control.value || 0, 10) || 0, 0, 10); }
                else if (field === 'headerWeight') { current.props.headerWeight = clamp(parseInt(control.value || 700, 10) || 700, 100, 900); }
                else if (field === 'mobileTableMode') { current.props.mobileMode = ['scroll','cards'].includes(control.value) ? control.value : 'scroll'; }
"""
insert_before_once(editor, "                else if (field === 'buttonText') { current.props.text = String(control.value || 'Knap'); }\n", handler_fields, "field === 'tableHeaders'")

# ---------------------------------------------------------------------------
# Palette entries on page Designer + Header/Footer Designer
# ---------------------------------------------------------------------------
page_controller = "clean/hangar18-manager/src/Admin/EditorController.php"
replace_once(
    page_controller,
    """            'button' => 'Knap',\n        ] as $type => $label) {\n""",
    """            'button' => 'Knap',\n            'link' => 'Link',\n            'spacer' => 'Mellemrum',\n            'divider' => 'Skillelinje',\n            'icon' => 'Ikon',\n            'badge' => 'Badge',\n            'datalist' => 'Data List',\n            'table' => 'Tabel',\n        ] as $type => $label) {\n""",
)

global_controller = "clean/hangar18-manager/src/Admin/GlobalDesignerController.php"
replace_once(
    global_controller,
    "foreach (['section' => 'Sektion', 'container' => 'Kasse', 'text' => 'Tekst', 'image' => 'Billede', 'button' => 'Knap', 'menu' => 'Menu'] as $type => $elementLabel)",
    "foreach (['section' => 'Sektion', 'container' => 'Kasse', 'text' => 'Tekst', 'image' => 'Billede', 'button' => 'Knap', 'link' => 'Link', 'menu' => 'Menu', 'spacer' => 'Mellemrum', 'divider' => 'Skillelinje', 'icon' => 'Ikon', 'badge' => 'Badge', 'datalist' => 'Data List', 'table' => 'Tabel'] as $type => $elementLabel)",
)


# ---------------------------------------------------------------------------
# Frontend Renderer
# ---------------------------------------------------------------------------
renderer = "clean/hangar18-manager/src/Frontend/Renderer.php"
replace_once(
    renderer,
    "        echo '.h18-clean-front-image img{display:block;max-width:none;margin:0;box-sizing:border-box}';\n",
    """        echo '.h18-clean-front-image img{display:block;max-width:none;margin:0;box-sizing:border-box}';\n        echo '.h18-clean-front-spacer{pointer-events:none;background:transparent!important;border:0!important}';\n        echo '.h18-clean-front-divider{display:flex;align-items:center;justify-content:center;box-sizing:border-box}.h18-clean-front-divider-line{display:block;box-sizing:border-box}';\n        echo '.h18-clean-front-icon{display:flex;align-items:center;box-sizing:border-box}.h18-clean-front-icon-mark{display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box}.h18-clean-front-icon svg{display:block;width:100%;height:100%;stroke:currentColor;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}';\n        echo '.h18-clean-front-badge{display:flex;align-items:center;box-sizing:border-box}.h18-clean-front-badge-mark{display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;white-space:nowrap}';\n        echo '.h18-clean-front-link{display:flex;align-items:center;box-sizing:border-box}.h18-clean-front-link a{color:var(--h18-link-color);text-decoration:var(--h18-link-decoration);font:inherit}.h18-clean-front-link a:hover,.h18-clean-front-link a:focus-visible{color:var(--h18-link-hover)}';\n        echo '.h18-clean-front-datalist{width:100%;box-sizing:border-box}.h18-clean-front-datalist-row{display:grid;grid-template-columns:var(--h18-data-label-width) minmax(0,1fr);box-sizing:border-box}.h18-clean-front-datalist.is-stacked .h18-clean-front-datalist-row{grid-template-columns:1fr}';\n        echo '.h18-clean-front-table-wrap{width:100%;overflow-x:auto;box-sizing:border-box}.h18-clean-front-table{width:100%;border-collapse:collapse;table-layout:auto}.h18-clean-front-table th,.h18-clean-front-table td{text-align:left;vertical-align:top;box-sizing:border-box}@media(max-width:782px){.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"]{overflow:visible}.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"] .h18-clean-front-table,.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"] tbody,.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"] tr,.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"] td{display:block;width:100%}.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"] thead{display:none}.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"] tr{margin-bottom:12px;border:1px solid var(--h18-table-border)}.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"] td{display:grid;grid-template-columns:minmax(100px,40%) minmax(0,1fr);gap:10px;border-width:0 0 1px!important}.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"] td:last-child{border-bottom:0!important}.h18-clean-front-table-wrap[data-mobile-mode=\"cards\"] td:before{content:attr(data-label);font-weight:700}}';\n""",
)

renderer_branches = r"""        if ($type === 'spacer') {
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-spacer" aria-hidden="true" style="' . esc_attr($style . $spacingStyle) . '"></div>';
        }

        if ($type === 'divider') {
            $vertical = (string) ($props['orientation'] ?? 'horizontal') === 'vertical';
            $lineColor = sanitize_hex_color((string) ($props['lineColor'] ?? '#c3c4c7')) ?: '#c3c4c7';
            $lineWidth = max(1, min(20, (int) ($props['lineWidth'] ?? 1)));
            $lineStyle = in_array((string) ($props['lineStyle'] ?? 'solid'), ['solid', 'dashed', 'dotted'], true) ? (string) $props['lineStyle'] : 'solid';
            $lineCss = $vertical ? 'height:100%;width:0;border-left:' . $lineWidth . 'px ' . $lineStyle . ' ' . $lineColor . ';' : 'width:100%;height:0;border-top:' . $lineWidth . 'px ' . $lineStyle . ' ' . $lineColor . ';';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-divider" style="' . esc_attr($style . $spacingStyle) . '"><span class="h18-clean-front-divider-line" style="' . esc_attr($lineCss) . '"></span></div>';
        }

        if ($type === 'icon') {
            $align = in_array((string) ($props['align'] ?? 'center'), ['left', 'center', 'right'], true) ? (string) $props['align'] : 'center';
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $size = max(8, min(240, (int) ($props['iconSize'] ?? 32)));
            $color = sanitize_hex_color((string) ($props['iconColor'] ?? '#30382a')) ?: '#30382a';
            $background = !empty($props['backgroundTransparent']) ? 'transparent' : (sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff');
            $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));
            $markStyle = 'width:' . $size . 'px;height:' . $size . 'px;color:' . $color . ';background:' . $background . ';padding:' . $padding . 'px;' . $radiusStyle;
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-icon" style="' . esc_attr($style . $borderStyle . $spacingStyle . 'justify-content:' . $justify . ';') . '"><span class="h18-clean-front-icon-mark" style="' . esc_attr($markStyle) . '">' . self::iconSvg((string) ($props['icon'] ?? 'star')) . '</span></div>';
        }

        if ($type === 'badge') {
            $align = in_array((string) ($props['align'] ?? 'left'), ['left', 'center', 'right'], true) ? (string) $props['align'] : 'left';
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $background = sanitize_hex_color((string) ($props['background'] ?? '#c3ae83')) ?: '#c3ae83';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#30382a')) ?: '#30382a';
            $fontSize = max(8, min(80, (int) ($props['fontSize'] ?? 13)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 700)));
            $paddingX = max(0, min(120, (int) ($props['paddingX'] ?? 12)));
            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 5)));
            $markStyle = 'background:' . $background . ';color:' . $textColor . ';font-family:' . self::fontCss((string) ($props['fontFamily'] ?? 'system')) . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';padding:' . $paddingY . 'px ' . $paddingX . 'px;' . $radiusStyle;
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-badge" style="' . esc_attr($style . $borderStyle . $spacingStyle . 'justify-content:' . $justify . ';') . '"><span class="h18-clean-front-badge-mark" style="' . esc_attr($markStyle) . '">' . esc_html((string) ($props['text'] ?? 'Badge')) . '</span></div>';
        }

        if ($type === 'link') {
            $linkType = in_array((string) ($props['linkType'] ?? 'url'), ['page', 'url', 'anchor', 'email', 'phone'], true) ? (string) $props['linkType'] : 'url';
            $href = '';
            if ($linkType === 'page') { $pageId = absint($props['pageId'] ?? 0); $permalink = $pageId > 0 ? get_permalink($pageId) : false; $href = is_string($permalink) ? $permalink : ''; }
            elseif ($linkType === 'anchor') { $anchor = trim((string) ($props['url'] ?? '')); $href = preg_match('/^#[A-Za-z][A-Za-z0-9_\-:.]*$/', $anchor) ? $anchor : ''; }
            elseif ($linkType === 'email') { $mail = sanitize_email((string) ($props['url'] ?? '')); $href = $mail !== '' ? 'mailto:' . $mail : ''; }
            elseif ($linkType === 'phone') { $phone = preg_replace('/[^0-9+() .\-]/', '', (string) ($props['url'] ?? '')); $href = is_string($phone) && trim($phone) !== '' ? 'tel:' . preg_replace('/[() .\-]/', '', $phone) : ''; }
            else { $href = esc_url_raw((string) ($props['url'] ?? '')); }
            if ($href === '') { $href = '#'; }
            $align = in_array((string) ($props['align'] ?? 'left'), ['left', 'center', 'right'], true) ? (string) $props['align'] : 'left';
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#2271b1')) ?: '#2271b1';
            $hoverColor = sanitize_hex_color((string) ($props['hoverTextColor'] ?? '#135e96')) ?: '#135e96';
            $fontSize = max(8, min(120, (int) ($props['fontSize'] ?? 16)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 600)));
            $lineHeight = max(0.8, min(3.0, (float) ($props['lineHeight'] ?? 1.3)));
            $letterSpacing = max(-10.0, min(30.0, (float) ($props['letterSpacing'] ?? 0)));
            $linkStyle = '--h18-link-color:' . $textColor . ';--h18-link-hover:' . $hoverColor . ';--h18-link-decoration:' . (!empty($props['underline']) ? 'underline' : 'none') . ';font-family:' . self::fontCss((string) ($props['fontFamily'] ?? 'system')) . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';line-height:' . $lineHeight . ';letter-spacing:' . $letterSpacing . 'px;justify-content:' . $justify . ';';
            $target = !empty($props['targetBlank']) ? ' target="_blank" rel="noopener"' : '';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-link" style="' . esc_attr($style . $borderStyle . $spacingStyle . $linkStyle) . '"><a href="' . esc_url($href) . '"' . $target . '>' . esc_html((string) ($props['text'] ?? 'Læs mere →')) . '</a></div>';
        }

        if ($type === 'datalist') {
            $rows = is_array($props['rows'] ?? null) ? $props['rows'] : [];
            $stacked = (string) ($props['layout'] ?? 'rows') === 'stacked';
            $labelWidth = max(15, min(80, (int) ($props['labelWidth'] ?? 40)));
            $padding = max(0, min(60, (int) ($props['cellPadding'] ?? 8)));
            $background = sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff';
            $zebraBg = sanitize_hex_color((string) ($props['zebraBackground'] ?? '#f6f7f7')) ?: '#f6f7f7';
            $lineColor = sanitize_hex_color((string) ($props['lineColor'] ?? '#dcdcde')) ?: '#dcdcde';
            $labelColor = sanitize_hex_color((string) ($props['labelColor'] ?? '#30382a')) ?: '#30382a';
            $valueColor = sanitize_hex_color((string) ($props['valueColor'] ?? '#30382a')) ?: '#30382a';
            $labelWeight = max(100, min(900, (int) ($props['labelWeight'] ?? 600)));
            $valueWeight = max(100, min(900, (int) ($props['valueWeight'] ?? 400)));
            $fontSize = max(8, min(80, (int) ($props['fontSize'] ?? 15)));
            $listHtml = '';
            foreach ($rows as $index => $row) {
                if (!is_array($row)) { continue; }
                $rowBg = !empty($props['zebra']) && ((int) $index % 2 === 1) ? $zebraBg : $background;
                $divider = !empty($props['showDividers']) && (int) $index > 0 ? 'border-top:1px solid ' . $lineColor . ';' : '';
                $listHtml .= '<div class="h18-clean-front-datalist-row" style="background:' . esc_attr($rowBg) . ';' . esc_attr($divider) . '"><span style="padding:' . esc_attr((string) $padding) . 'px;color:' . esc_attr($labelColor) . ';font-weight:' . esc_attr((string) $labelWeight) . '">' . esc_html((string) ($row['label'] ?? '')) . '</span><span style="padding:' . esc_attr((string) $padding) . 'px;color:' . esc_attr($valueColor) . ';font-weight:' . esc_attr((string) $valueWeight) . '">' . esc_html((string) ($row['value'] ?? '')) . '</span></div>';
            }
            $listStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . '--h18-data-label-width:' . $labelWidth . '%;font-family:' . self::fontCss((string) ($props['fontFamily'] ?? 'system')) . ';font-size:' . $fontSize . 'px;overflow:hidden;';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-datalist' . ($stacked ? ' is-stacked' : '') . '" style="' . esc_attr($listStyle) . '">' . $listHtml . '</div>';
        }

        if ($type === 'table') {
            $headers = is_array($props['headers'] ?? null) ? array_values($props['headers']) : [];
            $rows = is_array($props['rows'] ?? null) ? array_values($props['rows']) : [];
            $headerBg = sanitize_hex_color((string) ($props['headerBackground'] ?? '#30382a')) ?: '#30382a';
            $headerColor = sanitize_hex_color((string) ($props['headerTextColor'] ?? '#ffffff')) ?: '#ffffff';
            $cellBg = sanitize_hex_color((string) ($props['cellBackground'] ?? '#ffffff')) ?: '#ffffff';
            $cellColor = sanitize_hex_color((string) ($props['cellTextColor'] ?? '#30382a')) ?: '#30382a';
            $zebraBg = sanitize_hex_color((string) ($props['zebraBackground'] ?? '#f6f7f7')) ?: '#f6f7f7';
            $cellBorderColor = sanitize_hex_color((string) ($props['cellBorderColor'] ?? '#dcdcde')) ?: '#dcdcde';
            $cellBorderWidth = max(0, min(10, (int) ($props['cellBorderWidth'] ?? 1)));
            $cellPadding = max(0, min(60, (int) ($props['cellPadding'] ?? 8)));
            $fontSize = max(8, min(80, (int) ($props['fontSize'] ?? 14)));
            $headerWeight = max(100, min(900, (int) ($props['headerWeight'] ?? 700)));
            $cellBorder = $cellBorderWidth . 'px solid ' . $cellBorderColor;
            $thead = '<thead><tr>';
            foreach ($headers as $header) { $thead .= '<th style="background:' . esc_attr($headerBg) . ';color:' . esc_attr($headerColor) . ';font-weight:' . esc_attr((string) $headerWeight) . ';padding:' . esc_attr((string) $cellPadding) . 'px;border:' . esc_attr($cellBorder) . '">' . esc_html((string) $header) . '</th>'; }
            $thead .= '</tr></thead>';
            $tbody = '<tbody>';
            foreach ($rows as $rowIndex => $row) {
                if (!is_array($row)) { continue; }
                $rowBg = !empty($props['zebra']) && ((int) $rowIndex % 2 === 1) ? $zebraBg : $cellBg;
                $tbody .= '<tr>';
                foreach ($headers as $columnIndex => $header) { $tbody .= '<td data-label="' . esc_attr((string) $header) . '" style="background:' . esc_attr($rowBg) . ';color:' . esc_attr($cellColor) . ';padding:' . esc_attr((string) $cellPadding) . 'px;border:' . esc_attr($cellBorder) . '">' . esc_html((string) ($row[$columnIndex] ?? '')) . '</td>'; }
                $tbody .= '</tr>';
            }
            $tbody .= '</tbody>';
            $mobileMode = (string) ($props['mobileMode'] ?? 'scroll') === 'cards' ? 'cards' : 'scroll';
            $outerStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . '--h18-table-border:' . $cellBorderColor . ';font-family:' . self::fontCss((string) ($props['fontFamily'] ?? 'system')) . ';font-size:' . $fontSize . 'px;overflow:hidden;';
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node" style="' . esc_attr($outerStyle) . '"><div class="h18-clean-front-table-wrap" data-mobile-mode="' . esc_attr($mobileMode) . '"><table class="h18-clean-front-table">' . $thead . $tbody . '</table></div></div>';
        }

"""
insert_before_once(renderer, "        if ($type === 'image') {\n", renderer_branches, "if ($type === 'datalist')")

icon_helper = r"""    private static function iconSvg(string $token): string
    {
        $shapes = [
            'star' => '<polygon points="12 2.7 14.8 8.4 21 9.3 16.5 13.7 17.6 20 12 17 6.4 20 7.5 13.7 3 9.3 9.2 8.4 12 2.7"/>',
            'check' => '<polyline points="4 12.5 9.5 18 20 6"/>',
            'info' => '<circle cx="12" cy="12" r="9"/><line x1="12" y1="10.5" x2="12" y2="17"/><line x1="12" y1="7" x2="12.01" y2="7"/>',
            'calendar' => '<rect x="3" y="5" width="18" height="16" rx="2"/><line x1="7" y1="3" x2="7" y2="7"/><line x1="17" y1="3" x2="17" y2="7"/><line x1="3" y1="10" x2="21" y2="10"/>',
            'camera' => '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7l1.5-3h5L16 7"/><circle cx="12" cy="13.5" r="3.5"/>',
            'people' => '<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c.8-4 3-6 6-6s5.2 2 6 6"/><path d="M14 15c3.5-.5 6 1.1 7 4"/>',
            'ruler' => '<path d="M4 17L17 4l3 3L7 20z"/><line x1="13" y1="8" x2="16" y2="11"/><line x1="10" y1="11" x2="12" y2="13"/><line x1="7" y1="14" x2="10" y2="17"/>',
            'weight' => '<path d="M6 8h12l2 12H4z"/><path d="M9 8a3 3 0 016 0"/><line x1="12" y1="11" x2="14" y2="14"/>',
            'gear' => '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
            'link' => '<path d="M10 13a5 5 0 007 0l2-2a5 5 0 00-7-7l-1 1"/><path d="M14 11a5 5 0 00-7 0l-2 2a5 5 0 007 7l1-1"/>',
        ];
        $token = sanitize_key($token);
        $shape = $shapes[$token] ?? $shapes['star'];
        return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' . $shape . '</svg>';
    }

"""
insert_before_once(renderer, "    private static function fontCss(string $token): string\n", icon_helper, "private static function iconSvg")


# ---------------------------------------------------------------------------
# Release documentation and history
# ---------------------------------------------------------------------------
notes = "clean-release-notes.html"
prepend_once(
    notes,
    """<h4>0.1.65 – General Designer Elements · testversion</h4><ul><li><strong>VD-ELEMENTS-001:</strong> Nye generelle elementer: Mellemrum, Skillelinje, Ikon, Badge, Link, Data List og Tabel.</li><li>Data List og Tabel er i denne testversion statiske Designer-elementer med canonical model, Inspector, Preview og frontend-rendering.</li><li>Tabel understøtter header/celler, zebra, rammer, padding og mobilvisning som horisontal scroll eller kort.</li><li>Elementerne bruger samme 120-unit layout, responsive geometri, Copy/Paste, Undo/Redo og fælles runtime i Side Designer samt Header/Footer.</li><li>Dynamisk datakilde/binding er bevidst ikke med i 0.1.65 og kommer før Køretøjsmodulet.</li></ul>\n""",
    "0.1.65 – General Designer Elements",
)

manual = "CLEAN-TECHNICAL-MANUAL.md"
manual_text = read(manual)
if "VD-ELEMENTS-001" not in manual_text:
    manual_text += """

## VD-ELEMENTS-001 · General Designer Elements v0.1.65

Visual Designer har canonical leaf-typerne `spacer`, `divider`, `icon`, `badge`, `link`, `datalist` og `table`. De skal fungere i samme layout-/clipboard-/historikmotor som eksisterende elementer og i både Side Designer og Header/Footer Designer. `datalist` og `table` er i v0.1.65 statiske; dynamisk datasource/binding er et separat efterfølgende kontraktlag.
"""
    write(manual, manual_text)

status = """# Visual Designer Manager 0.1.65 – General Designer Elements test

Status: TESTKANDIDAT
Dato: 2026-08-31
Kontrakt: VD-ELEMENTS-001

## Scope
- Mellemrum / Spacer
- Skillelinje / Divider
- Ikon med indbygget SVG-sæt
- Badge
- Link
- Data List med statiske felt/værdi-rækker
- Tabel med statiske kolonner/rækker
- Mobil Tabel: scroll eller kort
- Samme canonical model og frontend/preview-rendering i Side Designer og Header/Footer

## Ikke i denne version
- Dynamisk datasource/binding
- Køretøjsdata
- Events-/Galleri-data
- Sortering, filtrering og pagination på dynamiske tabeller

## Testfokus
1. Tilføj hvert nyt element fra palette.
2. Gem/genindlæs og kontrollér at værdier bevares.
3. Kopiér/indsæt/duplikér elementerne.
4. Test Desktop/Laptop/Tablet/Mobil.
5. Test Data List og Tabel på frontend samt i Header/Footer Designer.
6. Test Tabel mobil som både Scroll og Kort.
"""
write("docs/v0165-status.md", status)

history_path = ROOT / "clean/hangar18-manager/release-history.json"
history = json.loads(history_path.read_text(encoding="utf-8"))
versions = history.setdefault("versions", [])
if not any(str(row.get("version")) == "0.1.65" for row in versions if isinstance(row, dict)):
    versions.insert(0, {
        "version": "0.1.65",
        "date": "2026-08-31",
        "items": [
            "VD-ELEMENTS-001: Mellemrum, Skillelinje, Ikon, Badge, Link, Data List og Tabel er canonical Designer-elementer.",
            "Data List og Tabel har statisk testdata, Inspector, Designer-preview og frontend-rendering.",
            "Tabel understøtter mobil scroll/kort samt header-, celle-, zebra-, border- og padding-design.",
            "Dynamisk binding og Køretøjsmodulet er bevidst ikke en del af 0.1.65."
        ]
    })
history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Applied Visual Designer Manager v0.1.65 general elements test candidate")
