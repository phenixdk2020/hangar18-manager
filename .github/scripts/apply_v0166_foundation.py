from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    (ROOT / rel).write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected one replacement anchor, found {count}: {old[:120]!r}')
    write(rel, text.replace(old, new, 1))


def regex_once(rel: str, pattern: str, repl: str, flags: int = 0) -> None:
    text = read(rel)
    new, count = re.subn(pattern, repl, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f'{rel}: regex expected one match, found {count}: {pattern[:120]!r}')
    write(rel, new)


def append_once(rel: str, marker: str, block: str) -> None:
    text = read(rel)
    if marker in text:
        return
    write(rel, text.rstrip() + '\n\n' + block.strip() + '\n')


# ---------------------------------------------------------------------------
# Version + shared bootstrap
# ---------------------------------------------------------------------------
plugin = 'clean/hangar18-manager/hangar18-manager.php'
text = read(plugin)
text2 = re.sub(r'Version:\s*0\.1\.65\b', 'Version: 0.1.66', text, count=1)
text2 = text2.replace("define('H18_CLEAN_VERSION', '0.1.65');", "define('H18_CLEAN_VERSION', '0.1.66');", 1)
if text2 == text and 'Version: 0.1.66' not in text:
    raise SystemExit('plugin version anchors not found')
write(plugin, text2)

replace_once(
    plugin,
    "require_once H18_CLEAN_DIR . 'src/Model/HierarchyNormalizer.php';",
    "require_once H18_CLEAN_DIR . 'src/Icons/IconRegistry.php';\nrequire_once H18_CLEAN_DIR . 'src/Model/HierarchyNormalizer.php';",
)
replace_once(
    plugin,
    "        'contextLabel' => $contextLabel,\n        'initialModel' => $model,",
    "        'contextLabel' => $contextLabel,\n        'iconLibrary' => \\VisualDesignerManager\\Icons\\IconRegistry::editorCatalog(),\n        'initialModel' => $model,",
)
replace_once(
    plugin,
    """    wp_enqueue_style(\n        'h18-clean-editor-v0165-elements',\n        H18_CLEAN_URL . 'assets/editor-v0165-elements.css',\n        ['h18-clean-editor-v0154-menu'],\n        H18_CLEAN_VERSION\n    );\n\n    wp_enqueue_script(\n""",
    """    wp_enqueue_style(\n        'h18-clean-editor-v0165-elements',\n        H18_CLEAN_URL . 'assets/editor-v0165-elements.css',\n        ['h18-clean-editor-v0154-menu'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_style(\n        'h18-clean-editor-v0166-foundation',\n        H18_CLEAN_URL . 'assets/editor-v0166-foundation.css',\n        ['h18-clean-editor-v0165-elements'],\n        H18_CLEAN_VERSION\n    );\n\n    wp_enqueue_script(\n""",
)


# ---------------------------------------------------------------------------
# Admin status + Menu structure preview
# ---------------------------------------------------------------------------
admin_status = 'clean/hangar18-manager/assets/admin-v0123.js'
replace_once(admin_status, "        'h18-clean-log': ['Under udvikling', 'partial'],", "        'h18-clean-log': ['Klar', 'ready'],")
text = read(admin_status)
if "'h18-clean-conversion': ['Klar', 'ready']" not in text:
    anchor = "        'h18-clean-pages': ['Under udvikling', 'partial'],\n"
    if text.count(anchor) != 1:
        raise SystemExit('admin status conversion anchor missing')
    text = text.replace(anchor, anchor + "        'h18-clean-conversion': ['Klar', 'ready'],\n", 1)
    write(admin_status, text)

menu_css = 'clean/hangar18-manager/assets/admin-v0156-menu.css'
replace_once(menu_css, '.h18-menu-visual-admin{max-width:1480px}', '.h18-menu-visual-admin{max-width:1800px}')
replace_once(menu_css, '.h18-menu-workspace{display:grid;grid-template-columns:minmax(520px,1fr) minmax(300px,420px);gap:24px;align-items:start}', '.h18-menu-workspace{display:grid;grid-template-columns:minmax(520px,1fr) minmax(520px,580px);gap:24px;align-items:start}')
replace_once(menu_css, '.h18-menu-preview-device{margin-top:16px;padding:12px;border:1px solid #dcdcde;border-radius:7px;background:#fff}', '.h18-menu-preview-device{margin-top:16px;padding:12px;border:1px solid #dcdcde;border-radius:7px;background:#fff;overflow-x:auto}')
replace_once(menu_css, '.h18-menu-preview-tree{display:flex;gap:16px;align-items:flex-start;list-style:none;margin:10px 0 0;padding:0}', '.h18-menu-preview-tree{display:flex;flex-wrap:nowrap;gap:16px;align-items:flex-start;list-style:none;margin:10px 0 0;padding:0;white-space:nowrap;min-width:max-content}')
replace_once(menu_css, '.h18-menu-preview-tree li{position:relative;margin:0;padding:0;font-weight:600}', '.h18-menu-preview-tree li{position:relative;flex:0 0 auto;margin:0;padding:0;font-weight:600;white-space:nowrap}')
replace_once(menu_css, '@media(max-width:1100px)', '@media(max-width:1250px)')


# ---------------------------------------------------------------------------
# Canonical PHP model: icon registry + Excel-like table borders
# ---------------------------------------------------------------------------
layout = 'clean/hangar18-manager/src/Model/LayoutModel.php'
replace_once(layout, "namespace VisualDesignerManager\\Model;\n\nfinal class LayoutModel", "namespace VisualDesignerManager\\Model;\n\nuse VisualDesignerManager\\Icons\\IconRegistry;\n\nfinal class LayoutModel")
replace_once(
    layout,
    """        if ($type === 'icon') {\n            $align = strtolower((string) ($raw['align'] ?? 'center'));\n            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'center'; }\n            return array_merge([\n                'icon' => self::iconToken($raw['icon'] ?? 'star'),\n""",
    """        if ($type === 'icon') {\n            $align = strtolower((string) ($raw['align'] ?? 'center'));\n            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'center'; }\n            $selection = IconRegistry::normalizeSelection((string) ($raw['iconSet'] ?? 'core'), (string) ($raw['icon'] ?? 'star'));\n            return array_merge([\n                'iconSet' => $selection['set'],\n                'icon' => $selection['icon'],\n""",
)
replace_once(
    layout,
    """                'cellBorderColor' => sanitize_hex_color((string) ($raw['cellBorderColor'] ?? '#dcdcde')) ?: '#dcdcde',\n                'cellBorderWidth' => self::clamp($raw['cellBorderWidth'] ?? 1, 0, 10, 1),\n                'cellPadding' => self::clamp($raw['cellPadding'] ?? 8, 0, 60, 8),\n""",
    """                'cellBorderColor' => sanitize_hex_color((string) ($raw['cellBorderColor'] ?? '#dcdcde')) ?: '#dcdcde',\n                'cellBorderWidth' => self::clamp($raw['cellBorderWidth'] ?? 1, 0, 10, 1),\n                'cellBorderStyle' => self::lineStyle($raw['cellBorderStyle'] ?? 'solid'),\n                'borderMode' => self::tableBorderMode($raw['borderMode'] ?? 'all'),\n                'cellBorders' => self::tableCellBorders($raw['cellBorders'] ?? []),\n                'cellPadding' => self::clamp($raw['cellPadding'] ?? 8, 0, 60, 8),\n""",
)

model_helpers = r'''    /** @param mixed $value */
    private static function lineStyle($value): string
    {
        $style = strtolower((string) $value);
        return in_array($style, ['solid', 'dashed', 'dotted'], true) ? $style : 'solid';
    }

    /** @param mixed $value */
    private static function tableBorderMode($value): string
    {
        $mode = strtolower((string) $value);
        return in_array($mode, ['all', 'outer', 'inner', 'none'], true) ? $mode : 'all';
    }

    /** @param mixed $value @return array<string,array<string,array<string,mixed>>> */
    private static function tableCellBorders($value): array
    {
        if (!is_array($value)) { return []; }
        $out = [];
        $count = 0;
        foreach ($value as $key => $cell) {
            if ($count >= 700 || !is_array($cell)) { break; }
            $key = (string) $key;
            if (!preg_match('/^(?:h\d+|r\d+c\d+)$/', $key)) { continue; }
            foreach (['top', 'right', 'bottom', 'left'] as $side) {
                if (!array_key_exists($side, $cell) || !is_array($cell[$side])) { continue; }
                $raw = $cell[$side];
                $out[$key][$side] = [
                    'enabled' => array_key_exists('enabled', $raw) ? (bool) $raw['enabled'] : true,
                    'width' => self::clamp($raw['width'] ?? 1, 0, 10, 1),
                    'color' => sanitize_hex_color((string) ($raw['color'] ?? '#dcdcde')) ?: '#dcdcde',
                    'style' => self::lineStyle($raw['style'] ?? 'solid'),
                ];
            }
            if (isset($out[$key])) { $count++; }
        }
        return $out;
    }

'''
text = read(layout)
marker = "    /** @param mixed $value */\n    private static function iconToken($value): string\n"
if 'private static function tableCellBorders' not in text:
    if text.count(marker) != 1:
        raise SystemExit('LayoutModel helper insertion marker missing')
    text = text.replace(marker, model_helpers + marker, 1)
    write(layout, text)
replace_once(
    layout,
    """    private static function iconToken($value): string\n    {\n        $token = sanitize_key((string) $value);\n        return in_array($token, ['star', 'check', 'info', 'calendar', 'camera', 'people', 'ruler', 'weight', 'gear', 'link'], true) ? $token : 'star';\n    }\n""",
    """    private static function iconToken($value): string\n    {\n        return IconRegistry::normalizeSelection('core', (string) $value)['icon'];\n    }\n""",
)


# ---------------------------------------------------------------------------
# Shared JS core
# ---------------------------------------------------------------------------
core = 'clean/hangar18-manager/assets/editor-v018-core.js'
replace_once(core, '    let productivityNoticeTimer = 0;\n', "    let productivityNoticeTimer = 0;\n    let tableCellSelection = null;\n")

helper_block = r'''    function iconLibrarySets() {
        const library = CFG.iconLibrary && typeof CFG.iconLibrary === 'object' ? CFG.iconLibrary : {};
        return Array.isArray(library.sets) ? library.sets : [];
    }
    function iconEntry(setKey, iconKey) {
        setKey = String(setKey || 'core'); iconKey = String(iconKey || 'star');
        for (const set of iconLibrarySets()) {
            if (String(set.key || '') !== setKey) { continue; }
            for (const category of (Array.isArray(set.categories) ? set.categories : [])) {
                for (const icon of (Array.isArray(category.icons) ? category.icons : [])) {
                    if (String(icon.key || '') === iconKey) { return {set:set, category:category, icon:icon}; }
                }
            }
        }
        return null;
    }
    function normalizeIconSelection(setKey, iconKey) {
        const direct = iconEntry(setKey, iconKey);
        if (direct) { return {set:String(direct.set.key), icon:String(direct.icon.key)}; }
        const legacy = iconEntry('core', iconKey);
        if (legacy) { return {set:'core', icon:String(legacy.icon.key)}; }
        return {set:'core', icon:'star'};
    }
    function registryIconSvgMarkup(setKey, iconKey) {
        const entry = iconEntry(setKey, iconKey);
        return entry && entry.icon && entry.icon.svg ? String(entry.icon.svg) : iconSvgMarkup(iconKey);
    }
    function currentIconLabel(setKey, iconKey) {
        const entry = iconEntry(setKey, iconKey);
        return entry ? String(entry.icon.label || entry.icon.key || iconKey) : String(iconKey || 'star');
    }

    function normalizeTableCellBorders(raw) {
        raw = raw && typeof raw === 'object' && !Array.isArray(raw) ? raw : {};
        const out = {}; let count = 0;
        Object.keys(raw).forEach(function (key) {
            if (count >= 700 || !/^(?:h\d+|r\d+c\d+)$/.test(key)) { return; }
            const cell = raw[key] && typeof raw[key] === 'object' ? raw[key] : {};
            ['top','right','bottom','left'].forEach(function (side) {
                if (!cell[side] || typeof cell[side] !== 'object') { return; }
                const value = cell[side];
                if (!out[key]) { out[key] = {}; }
                out[key][side] = {
                    enabled: value.enabled !== false,
                    width: clamp(parseInt(value.width != null ? value.width : 1, 10) || 0, 0, 10),
                    color: /^#[0-9a-f]{6}$/i.test(String(value.color || '')) ? String(value.color).toLowerCase() : '#dcdcde',
                    style: ['solid','dashed','dotted'].includes(String(value.style || '').toLowerCase()) ? String(value.style).toLowerCase() : 'solid'
                };
            });
            if (out[key]) { count += 1; }
        });
        return out;
    }
    function tableGrid(node) {
        const headers = normalizeHeaders(node && node.props ? node.props.headers : []);
        const rows = normalizeMatrixRows(node && node.props ? node.props.rows : [], headers.length);
        const grid = [headers.map(function (_value, col) { return 'h' + col; })];
        rows.forEach(function (row, rowIndex) { grid.push(row.map(function (_value, col) { return 'r' + rowIndex + 'c' + col; })); });
        const pos = {};
        grid.forEach(function (row, r) { row.forEach(function (key, c) { pos[key] = {row:r,col:c}; }); });
        return {headers:headers, rows:rows, grid:grid, pos:pos, rowCount:grid.length, colCount:headers.length};
    }
    function tableSelectionKeys(node) {
        if (!tableCellSelection || !node || tableCellSelection.nodeId !== node.id) { return []; }
        const grid = tableGrid(node);
        return (Array.isArray(tableCellSelection.keys) ? tableCellSelection.keys : []).filter(function (key) { return !!grid.pos[key]; });
    }
    function tableRangeKeys(node, fromKey, toKey) {
        const grid = tableGrid(node), a = grid.pos[fromKey], b = grid.pos[toKey];
        if (!a || !b) { return [toKey]; }
        const out = [];
        const minR = Math.min(a.row,b.row), maxR = Math.max(a.row,b.row), minC = Math.min(a.col,b.col), maxC = Math.max(a.col,b.col);
        for (let r=minR; r<=maxR; r+=1) { for (let c=minC; c<=maxC; c+=1) { if (grid.grid[r] && grid.grid[r][c]) { out.push(grid.grid[r][c]); } } }
        return out;
    }
    function tableNeighborKey(node, key, side) {
        const grid = tableGrid(node), p = grid.pos[key]; if (!p) { return ''; }
        const delta = {top:[-1,0],right:[0,1],bottom:[1,0],left:[0,-1]}[side];
        const r = p.row + delta[0], c = p.col + delta[1];
        return grid.grid[r] && grid.grid[r][c] ? grid.grid[r][c] : '';
    }
    function tableBaseSideEnabled(node, key, side) {
        const grid = tableGrid(node), p = grid.pos[key]; if (!p) { return false; }
        const mode = ['all','outer','inner','none'].includes(String(node.props.borderMode || 'all')) ? String(node.props.borderMode || 'all') : 'all';
        if (mode === 'all') { return true; }
        if (mode === 'none') { return false; }
        const outer = side === 'top' ? p.row === 0 : side === 'bottom' ? p.row === grid.rowCount - 1 : side === 'left' ? p.col === 0 : p.col === grid.colCount - 1;
        return mode === 'outer' ? outer : !outer;
    }
    function tableEffectiveSide(node, key, side) {
        const custom = node.props.cellBorders && node.props.cellBorders[key] && node.props.cellBorders[key][side];
        if (custom) { return custom; }
        return {
            enabled: tableBaseSideEnabled(node,key,side),
            width: clamp(parseInt(node.props.cellBorderWidth != null ? node.props.cellBorderWidth : 1,10) || 0,0,10),
            color: /^#[0-9a-f]{6}$/i.test(String(node.props.cellBorderColor || '')) ? String(node.props.cellBorderColor).toLowerCase() : '#dcdcde',
            style: ['solid','dashed','dotted'].includes(String(node.props.cellBorderStyle || '').toLowerCase()) ? String(node.props.cellBorderStyle).toLowerCase() : 'solid'
        };
    }
    function tableBorderCssValue(value) { return value && value.enabled && value.width > 0 ? (String(value.width) + 'px ' + value.style + ' ' + value.color) : '0'; }
    function applyTableCellBorders(element, node, key) {
        element.style.borderTop = tableBorderCssValue(tableEffectiveSide(node,key,'top'));
        element.style.borderRight = tableBorderCssValue(tableEffectiveSide(node,key,'right'));
        element.style.borderBottom = tableBorderCssValue(tableEffectiveSide(node,key,'bottom'));
        element.style.borderLeft = tableBorderCssValue(tableEffectiveSide(node,key,'left'));
    }
    function setTableCellSide(node, key, side, enabled, pen) {
        if (!node.props.cellBorders || typeof node.props.cellBorders !== 'object') { node.props.cellBorders = {}; }
        if (!node.props.cellBorders[key]) { node.props.cellBorders[key] = {}; }
        const value = {enabled:!!enabled,width:pen.width,color:pen.color,style:pen.style};
        node.props.cellBorders[key][side] = value;
        const opposite = {top:'bottom',right:'left',bottom:'top',left:'right'}[side];
        const neighbor = tableNeighborKey(node,key,side);
        if (neighbor) {
            if (!node.props.cellBorders[neighbor]) { node.props.cellBorders[neighbor] = {}; }
            node.props.cellBorders[neighbor][opposite] = clone(value);
        }
    }
    function applyTableBorderAction(node, keys, action, pen) {
        const selected = new Set(keys);
        function neighborSelected(key, side) { const n = tableNeighborKey(node,key,side); return !!n && selected.has(n); }
        keys.forEach(function (key) {
            if (action === 'none') { ['top','right','bottom','left'].forEach(function (side) { setTableCellSide(node,key,side,false,pen); }); return; }
            if (action === 'all') { ['top','right','bottom','left'].forEach(function (side) { setTableCellSide(node,key,side,true,pen); }); return; }
            if (action === 'outer') { ['top','right','bottom','left'].forEach(function (side) { if (!neighborSelected(key,side)) { setTableCellSide(node,key,side,true,pen); } }); return; }
            if (action === 'inner') { ['right','bottom'].forEach(function (side) { if (neighborSelected(key,side)) { setTableCellSide(node,key,side,true,pen); } }); return; }
            if (action === 'horizontal') { if (neighborSelected(key,'bottom')) { setTableCellSide(node,key,'bottom',true,pen); } return; }
            if (action === 'vertical') { if (neighborSelected(key,'right')) { setTableCellSide(node,key,'right',true,pen); } return; }
            if (['top','right','bottom','left'].includes(action) && !neighborSelected(key,action)) { setTableCellSide(node,key,action,true,pen); }
        });
    }
    function selectTableCell(node, key, event) {
        const current = tableCellSelection && tableCellSelection.nodeId === node.id ? tableCellSelection : {nodeId:node.id,keys:[],anchorKey:key};
        let keys = [];
        if (event.shiftKey && current.anchorKey) {
            keys = tableRangeKeys(node,current.anchorKey,key);
        } else if (event.ctrlKey || event.metaKey) {
            keys = Array.isArray(current.keys) ? current.keys.slice() : [];
            const index = keys.indexOf(key); if (index >= 0) { keys.splice(index,1); } else { keys.push(key); }
            if (!keys.length) { keys = [key]; }
        } else { keys = [key]; current.anchorKey = key; }
        tableCellSelection = {nodeId:node.id,keys:keys,anchorKey:current.anchorKey || key};
        selectedId = node.id;
        render();
    }

    function openIconLibrary() {
        const node = nodeById(selectedId); if (!node || node.type !== 'icon') { return; }
        const old = document.getElementById('h18-vd-icon-library-dialog'); if (old) { old.remove(); }
        const dialog = document.createElement('div'); dialog.id = 'h18-vd-icon-library-dialog'; dialog.className = 'h18-vd-icon-library-dialog';
        const backdrop = document.createElement('div'); backdrop.className = 'h18-vd-icon-library-backdrop'; dialog.appendChild(backdrop);
        const card = document.createElement('div'); card.className = 'h18-vd-icon-library-card'; dialog.appendChild(card);
        const head = document.createElement('div'); head.className = 'h18-vd-icon-library-head'; head.innerHTML = '<div><h2>Ikonbibliotek</h2><p class="description">Core icons følger med Designer. Module icons registreres af moduler. Egne SVG-ikoner er reserveret til en senere Custom icons-funktion.</p></div><button type="button" class="button" data-icon-close>Luk</button>'; card.appendChild(head);
        const tools = document.createElement('div'); tools.className = 'h18-vd-icon-library-tools'; tools.innerHTML = '<input type="search" placeholder="Søg efter ikon…" aria-label="Søg efter ikon"><select aria-label="Ikonsæt"><option value="">Alle ikonsæt</option></select>'; card.appendChild(tools);
        const search = tools.querySelector('input'), setSelect = tools.querySelector('select');
        iconLibrarySets().forEach(function (set) { const option = document.createElement('option'); option.value = String(set.key || ''); option.textContent = String(set.label || set.key || 'Ikonsæt'); setSelect.appendChild(option); });
        const scroll = document.createElement('div'); scroll.className = 'h18-vd-icon-library-scroll'; card.appendChild(scroll);
        const footer = document.createElement('div'); footer.className = 'h18-vd-icon-library-footer'; footer.textContent = 'Custom icons: upload/indsæt af egne SVG-filer er planlagt som næste udvidelsesniveau og er ikke aktiveret endnu.'; card.appendChild(footer);
        function close() { dialog.remove(); }
        function rebuild() {
            const needle = String(search.value || '').toLowerCase().trim(), setFilter = String(setSelect.value || ''); scroll.replaceChildren();
            iconLibrarySets().forEach(function (set) {
                if (setFilter && String(set.key || '') !== setFilter) { return; }
                const setBox = document.createElement('section'); setBox.className = 'h18-vd-icon-library-set'; const h3 = document.createElement('h3'); h3.textContent = String(set.label || set.key || 'Ikonsæt'); setBox.appendChild(h3); let count = 0;
                (Array.isArray(set.categories) ? set.categories : []).forEach(function (category) {
                    const matches = (Array.isArray(category.icons) ? category.icons : []).filter(function (icon) { const hay = [set.label,category.label,icon.label,icon.key].join(' ').toLowerCase(); return !needle || hay.indexOf(needle) >= 0; });
                    if (!matches.length) { return; }
                    const cat = document.createElement('section'); cat.className = 'h18-vd-icon-library-category'; const h4 = document.createElement('h4'); h4.textContent = String(category.label || category.key || 'Kategori'); cat.appendChild(h4); const grid = document.createElement('div'); grid.className = 'h18-vd-icon-library-grid';
                    matches.forEach(function (icon) {
                        const button = document.createElement('button'); button.type = 'button'; button.className = 'h18-vd-icon-library-item'; const selection = normalizeIconSelection(node.props.iconSet || 'core', node.props.icon || 'star'); if (selection.set === String(set.key) && selection.icon === String(icon.key)) { button.classList.add('is-current'); }
                        const mark = document.createElement('span'); mark.innerHTML = String(icon.svg || ''); const label = document.createElement('small'); label.textContent = String(icon.label || icon.key || 'Ikon'); button.appendChild(mark); button.appendChild(label);
                        button.addEventListener('click', function () { const before = clone(state); node.props.iconSet = String(set.key || 'core'); node.props.icon = String(icon.key || 'star'); commit(before, 'Skift ikon'); close(); render(); }); grid.appendChild(button); count += 1;
                    }); cat.appendChild(grid); setBox.appendChild(cat);
                });
                if (count) { scroll.appendChild(setBox); }
            });
            if (!scroll.children.length) { const empty = document.createElement('p'); empty.textContent = 'Ingen ikoner matcher søgningen.'; scroll.appendChild(empty); }
        }
        backdrop.addEventListener('click', close); head.querySelector('[data-icon-close]').addEventListener('click', close); search.addEventListener('input', rebuild); setSelect.addEventListener('change', rebuild); dialog.addEventListener('keydown', function (event) { if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); close(); } });
        document.body.appendChild(dialog); rebuild(); setTimeout(function () { search.focus(); },0);
    }

'''
text = read(core)
marker = '    function iconSvgMarkup(token) {\n'
if 'function iconLibrarySets()' not in text:
    if text.count(marker) != 1:
        raise SystemExit('editor helper insertion marker missing')
    text = text.replace(marker, helper_block + marker, 1)
    write(core, text)

replace_once(
    core,
    """        if (type === 'icon') {\n            return Object.assign(common, {\n                icon: ['star','check','info','calendar','camera','people','ruler','weight','gear','link'].includes(String(raw.icon || '').toLowerCase()) ? String(raw.icon).toLowerCase() : 'star',\n""",
    """        if (type === 'icon') {\n            const iconSelection = normalizeIconSelection(raw.iconSet || 'core', raw.icon || 'star');\n            return Object.assign(common, {\n                iconSet: iconSelection.set,\n                icon: iconSelection.icon,\n""",
)
replace_once(
    core,
    """                cellBorderColor: /^#[0-9a-f]{6}$/i.test(String(raw.cellBorderColor || '')) ? String(raw.cellBorderColor).toLowerCase() : '#dcdcde',\n                cellBorderWidth: clamp(parseInt(raw.cellBorderWidth != null ? raw.cellBorderWidth : 1, 10) || 0, 0, 10),\n                cellPadding: clamp(parseInt(raw.cellPadding || 8, 10) || 8, 0, 60),\n""",
    """                cellBorderColor: /^#[0-9a-f]{6}$/i.test(String(raw.cellBorderColor || '')) ? String(raw.cellBorderColor).toLowerCase() : '#dcdcde',\n                cellBorderWidth: clamp(parseInt(raw.cellBorderWidth != null ? raw.cellBorderWidth : 1, 10) || 0, 0, 10),\n                cellBorderStyle: ['solid','dashed','dotted'].includes(String(raw.cellBorderStyle || '').toLowerCase()) ? String(raw.cellBorderStyle).toLowerCase() : 'solid',\n                borderMode: ['all','outer','inner','none'].includes(String(raw.borderMode || '').toLowerCase()) ? String(raw.borderMode).toLowerCase() : 'all',\n                cellBorders: normalizeTableCellBorders(raw.cellBorders),\n                cellPadding: clamp(parseInt(raw.cellPadding || 8, 10) || 8, 0, 60),\n""",
)
replace_once(core, "            icon.innerHTML = iconSvgMarkup(node.props.icon || 'star'); wrap.appendChild(icon);", "            icon.innerHTML = registryIconSvgMarkup(node.props.iconSet || 'core', node.props.icon || 'star'); wrap.appendChild(icon);")

preview_table = r'''        } else if (node.type === 'table') {
            wrap.classList.add('h18-clean-node-preview--table');
            const table = document.createElement('table'); table.className = 'h18-vd-table-preview'; table.style.fontFamily = fontCss(node.props.fontFamily || 'system'); table.style.fontSize = String(node.props.fontSize || 14) + 'px';
            const grid = tableGrid(node), selectedCells = new Set(tableSelectionKeys(node));
            function configureCell(cell, key) {
                cell.dataset.vdTableCell = key; applyTableCellBorders(cell,node,key); if (selectedCells.has(key)) { cell.classList.add('is-vd-table-cell-selected'); }
                cell.addEventListener('click', function (event) { event.preventDefault(); event.stopPropagation(); selectTableCell(node,key,event); });
            }
            const head = document.createElement('thead'), hr = document.createElement('tr');
            grid.headers.forEach(function (value,col) { const th = document.createElement('th'); th.textContent = value; th.style.background = node.props.headerBackground || '#30382a'; th.style.color = node.props.headerTextColor || '#ffffff'; th.style.fontWeight = String(node.props.headerWeight || 700); th.style.padding = String(node.props.cellPadding || 8) + 'px'; configureCell(th,'h'+col); hr.appendChild(th); }); head.appendChild(hr); table.appendChild(head);
            const body = document.createElement('tbody');
            grid.rows.forEach(function (row,rowIndex) { const tr = document.createElement('tr'); row.forEach(function (value,col) { const td = document.createElement('td'); td.textContent = value; td.style.background = node.props.zebra && rowIndex % 2 ? (node.props.zebraBackground || '#f6f7f7') : (node.props.cellBackground || '#ffffff'); td.style.color = node.props.cellTextColor || '#30382a'; td.style.padding = String(node.props.cellPadding || 8) + 'px'; configureCell(td,'r'+rowIndex+'c'+col); tr.appendChild(td); }); body.appendChild(tr); }); table.appendChild(body); wrap.appendChild(table);
'''
text = read(core)
pattern = r"        \} else if \(node\.type === 'table'\) \{\n            wrap\.classList\.add\('h18-clean-node-preview--table'\);.*?\n        \} else if \(node\.type === 'image'\) \{"
new, count = re.subn(pattern, preview_table + "        } else if (node.type === 'image') {", text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'editor table preview replacement expected 1, got {count}')
write(core, new)

icon_inspector = r'''        } else if (node.type === 'icon') {
            const selection = normalizeIconSelection(node.props.iconSet || 'core', node.props.icon || 'star');
            html += '<button type="button" class="button" id="h18-vd-icon-library-open">Vælg ikon fra bibliotek</button><div class="h18-vd-icon-current"><span class="h18-vd-icon-current-mark">' + registryIconSvgMarkup(selection.set,selection.icon) + '</span><span><strong>' + escapeHtml(currentIconLabel(selection.set,selection.icon)) + '</strong><br><small>' + escapeHtml(selection.set) + '</small></span></div><div class="h18-clean-field-grid"><label>Størrelse px<input data-field="iconSize" type="number" min="8" max="240" value="' + (node.props.iconSize || 32) + '"></label><label>Farve<input data-field="iconColor" type="color" value="' + escapeAttr(node.props.iconColor || '#30382a') + '"></label></div><label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label><label class="h18-clean-checkbox"><input data-field="backgroundTransparent" type="checkbox"' + (node.props.backgroundTransparent !== false ? ' checked' : '') + '> Gennemsigtig baggrund</label><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#ffffff') + '"></label><div class="h18-clean-field-grid"><label>Padding px<input data-field="padding" type="number" min="0" max="120" value="' + (node.props.padding || 0) + '"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 0) + '"></label></div>';
'''
text = read(core)
pattern = r"        \} else if \(node\.type === 'icon'\) \{\n            html \+= .*?\n        \} else if \(node\.type === 'badge'\) \{"
new, count = re.subn(pattern, icon_inspector + "        } else if (node.type === 'badge') {", text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'editor icon inspector replacement expected 1, got {count}')
write(core, new)

table_inspector = r'''        } else if (node.type === 'table') {
            const tableHeaders = normalizeHeaders(node.props.headers), selectedCells = tableSelectionKeys(node);
            html += '<div class="h18-vd-structured-editor"><div class="h18-vd-element-note"><strong>Statisk Tabel · test</strong><br>Kolonner og rækker redigeres med <code>|</code> som separator. Klik celler i preview for Excel-lignende kantstyring; Ctrl/Cmd vælger flere og Shift vælger et område.</div><label>Kolonner<input data-field="tableHeaders" type="text" value="' + escapeAttr(headersText(tableHeaders)) + '"></label><label>Rækker<textarea data-field="tableRows" rows="8">' + escapeHtml(matrixRowsText(node.props.rows, tableHeaders.length)) + '</textarea></label><label>Mobilvisning<select data-field="mobileTableMode"><option value="scroll"' + (node.props.mobileMode === 'scroll' ? ' selected' : '') + '>Horisontal scroll</option><option value="cards"' + (node.props.mobileMode === 'cards' ? ' selected' : '') + '>Kort · kolonnenavn + værdi</option></select></label><label>Tabelstandard for kanter<select data-field="tableBorderMode"><option value="all"' + (node.props.borderMode === 'all' ? ' selected' : '') + '>Alle kanter</option><option value="outer"' + (node.props.borderMode === 'outer' ? ' selected' : '') + '>Kun yderramme</option><option value="inner"' + (node.props.borderMode === 'inner' ? ' selected' : '') + '>Kun indvendige linjer</option><option value="none"' + (node.props.borderMode === 'none' ? ' selected' : '') + '>Ingen kanter</option></select></label><div class="h18-clean-field-grid"><label>Standard ramme px<input data-field="cellBorderWidth" type="number" min="0" max="10" value="' + (node.props.cellBorderWidth || 0) + '"></label><label>Standard streg<select data-field="cellBorderStyle"><option value="solid"' + (node.props.cellBorderStyle === 'solid' ? ' selected' : '') + '>Solid</option><option value="dashed"' + (node.props.cellBorderStyle === 'dashed' ? ' selected' : '') + '>Stiplet</option><option value="dotted"' + (node.props.cellBorderStyle === 'dotted' ? ' selected' : '') + '>Prikket</option></select></label><label>Standard farve<input data-field="cellBorderColor" type="color" value="' + escapeAttr(node.props.cellBorderColor || '#dcdcde') + '"></label><label>Cell padding px<input data-field="cellPadding" type="number" min="0" max="60" value="' + (node.props.cellPadding || 8) + '"></label><label>Skrift px<input data-field="fontSize" type="number" min="8" max="80" value="' + (node.props.fontSize || 14) + '"></label><label>Header tykkelse<input data-field="headerWeight" type="number" min="100" max="900" step="100" value="' + (node.props.headerWeight || 700) + '"></label></div><label class="h18-clean-checkbox"><input data-field="zebra" type="checkbox"' + (node.props.zebra !== false ? ' checked' : '') + '> Zebra-rækker</label><div class="h18-clean-field-grid"><label>Header baggrund<input data-field="headerBackground" type="color" value="' + escapeAttr(node.props.headerBackground || '#30382a') + '"></label><label>Header tekst<input data-field="headerTextColor" type="color" value="' + escapeAttr(node.props.headerTextColor || '#ffffff') + '"></label><label>Cell baggrund<input data-field="cellBackground" type="color" value="' + escapeAttr(node.props.cellBackground || '#ffffff') + '"></label><label>Cell tekst<input data-field="cellTextColor" type="color" value="' + escapeAttr(node.props.cellTextColor || '#30382a') + '"></label><label>Zebra<input data-field="zebraBackground" type="color" value="' + escapeAttr(node.props.zebraBackground || '#f6f7f7') + '"></label></div>';
            if (selectedCells.length) {
                html += '<div class="h18-vd-table-selection-note"><strong>' + selectedCells.length + ' celle' + (selectedCells.length === 1 ? '' : 'r') + ' markeret.</strong><div class="h18-vd-table-selection-help">Klik = ny markering · Ctrl/Cmd+klik = til/fra · Shift+klik = rektangulært område.</div></div><div class="h18-vd-table-border-designer"><h4>Kantværktøj</h4><div class="h18-vd-table-pen"><label>Tykkelse px<input id="h18-vd-table-pen-width" type="number" min="0" max="10" value="' + (node.props.cellBorderWidth || 1) + '"></label><label>Farve<input id="h18-vd-table-pen-color" type="color" value="' + escapeAttr(node.props.cellBorderColor || '#dcdcde') + '"></label><label>Stil<select id="h18-vd-table-pen-style"><option value="solid">Solid</option><option value="dashed">Stiplet</option><option value="dotted">Prikket</option></select></label></div><div class="h18-vd-table-border-actions"><button type="button" class="button" data-table-border-action="outer">Yderramme</button><button type="button" class="button" data-table-border-action="inner">Indvendige</button><button type="button" class="button" data-table-border-action="all">Alle</button><button type="button" class="button" data-table-border-action="horizontal">Vandret</button><button type="button" class="button" data-table-border-action="vertical">Lodret</button><button type="button" class="button" data-table-border-action="top">Top</button><button type="button" class="button" data-table-border-action="right">Højre</button><button type="button" class="button" data-table-border-action="bottom">Bund</button><button type="button" class="button" data-table-border-action="left">Venstre</button><button type="button" class="button" data-table-border-action="none">Ingen</button></div></div>';
            } else { html += '<div class="h18-vd-table-selection-note">Klik en eller flere celler i tabel-previewet for at tegne kanter på det valgte område.</div>'; }
            html += '</div>';
'''
text = read(core)
pattern = r"        \} else if \(node\.type === 'table'\) \{\n            const tableHeaders = normalizeHeaders\(node\.props\.headers\);.*?\n        \} else if \(node\.type === 'image'\) \{"
new, count = re.subn(pattern, table_inspector + "        } else if (node.type === 'image') {", text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'editor table inspector replacement expected 1, got {count}')
write(core, new)

replace_once(
    core,
    """                else if (field === 'cellBorderColor') { current.props.cellBorderColor = normalizeColor(control.value || '#dcdcde'); }\n                else if (field === 'cellBorderWidth') { current.props.cellBorderWidth = clamp(parseInt(control.value || 0, 10) || 0, 0, 10); }\n                else if (field === 'headerWeight') { current.props.headerWeight = clamp(parseInt(control.value || 700, 10) || 700, 100, 900); }\n""",
    """                else if (field === 'cellBorderColor') { current.props.cellBorderColor = normalizeColor(control.value || '#dcdcde'); }\n                else if (field === 'cellBorderWidth') { current.props.cellBorderWidth = clamp(parseInt(control.value || 0, 10) || 0, 0, 10); }\n                else if (field === 'cellBorderStyle') { current.props.cellBorderStyle = ['solid','dashed','dotted'].includes(control.value) ? control.value : 'solid'; }\n                else if (field === 'tableBorderMode') { current.props.borderMode = ['all','outer','inner','none'].includes(control.value) ? control.value : 'all'; }\n                else if (field === 'headerWeight') { current.props.headerWeight = clamp(parseInt(control.value || 700, 10) || 700, 100, 900); }\n""",
)

binding_block = r'''        const iconLibraryOpen = document.getElementById('h18-vd-icon-library-open');
        if (iconLibraryOpen) { iconLibraryOpen.addEventListener('click', openIconLibrary); }
        document.querySelectorAll('[data-table-border-action]').forEach(function (button) {
            button.addEventListener('click', function () {
                const current = nodeById(selectedId); if (!current || current.type !== 'table') { return; }
                const keys = tableSelectionKeys(current); if (!keys.length) { return; }
                const widthInput = document.getElementById('h18-vd-table-pen-width'), colorInput = document.getElementById('h18-vd-table-pen-color'), styleInput = document.getElementById('h18-vd-table-pen-style');
                const pen = {width:clamp(parseInt(widthInput && widthInput.value || current.props.cellBorderWidth || 1,10) || 0,0,10),color:normalizeColor(colorInput && colorInput.value || current.props.cellBorderColor || '#dcdcde'),style:['solid','dashed','dotted'].includes(String(styleInput && styleInput.value || 'solid')) ? String(styleInput && styleInput.value || 'solid') : 'solid'};
                const before = clone(state), action = String(button.getAttribute('data-table-border-action') || 'all');
                applyTableBorderAction(current,keys,action,pen); commit(before,'Tabelkanter · ' + action); render();
            });
        });
'''
text = read(core)
marker = "        const resetOffset = document.getElementById('h18-clean-reset-offset');\n"
if 'const iconLibraryOpen = document.getElementById' not in text:
    if text.count(marker) != 1:
        raise SystemExit('editor inspector binding marker missing')
    text = text.replace(marker, binding_block + marker, 1)
    write(core, text)


# ---------------------------------------------------------------------------
# Frontend renderer parity
# ---------------------------------------------------------------------------
renderer = 'clean/hangar18-manager/src/Frontend/Renderer.php'
replace_once(renderer, "namespace VisualDesignerManager\\Frontend;\n\nuse VisualDesignerManager\\Model\\LayoutModel;", "namespace VisualDesignerManager\\Frontend;\n\nuse VisualDesignerManager\\Icons\\IconRegistry;\nuse VisualDesignerManager\\Model\\LayoutModel;")
replace_once(renderer, "self::iconSvg((string) ($props['icon'] ?? 'star'))", "IconRegistry::svg((string) ($props['iconSet'] ?? 'core'), (string) ($props['icon'] ?? 'star'))")

text = read(renderer)
pattern = r"            \$cellBorderColor = sanitize_hex_color\(\(string\) \(\$props\['cellBorderColor'\] \?\? '#dcdcde'\)\) \?: '#dcdcde';.*?            \$tbody \.= '</tbody>';"
replacement = r'''            $cellBorderColor = sanitize_hex_color((string) ($props['cellBorderColor'] ?? '#dcdcde')) ?: '#dcdcde';
            $cellBorderWidth = max(0, min(10, (int) ($props['cellBorderWidth'] ?? 1)));
            $cellPadding = max(0, min(60, (int) ($props['cellPadding'] ?? 8)));
            $fontSize = max(8, min(80, (int) ($props['fontSize'] ?? 14)));
            $headerWeight = max(100, min(900, (int) ($props['headerWeight'] ?? 700)));
            $totalRows = count($rows) + 1;
            $totalCols = count($headers);
            $thead = '<thead><tr>';
            foreach ($headers as $columnIndex => $header) {
                $cellKey = 'h' . $columnIndex;
                $cellBorderCss = self::tableCellBorderCss($props, $cellKey, 0, $columnIndex, $totalRows, $totalCols);
                $thead .= '<th style="background:' . esc_attr($headerBg) . ';color:' . esc_attr($headerColor) . ';font-weight:' . esc_attr((string) $headerWeight) . ';padding:' . esc_attr((string) $cellPadding) . 'px;' . esc_attr($cellBorderCss) . '">' . esc_html((string) $header) . '</th>';
            }
            $thead .= '</tr></thead>';
            $tbody = '<tbody>';
            foreach ($rows as $rowIndex => $row) {
                $rowBg = !empty($props['zebra']) && $rowIndex % 2 ? $zebraBg : $cellBg;
                $tbody .= '<tr>';
                foreach ($headers as $columnIndex => $header) {
                    $cellKey = 'r' . $rowIndex . 'c' . $columnIndex;
                    $cellBorderCss = self::tableCellBorderCss($props, $cellKey, $rowIndex + 1, $columnIndex, $totalRows, $totalCols);
                    $tbody .= '<td data-label="' . esc_attr((string) $header) . '" style="background:' . esc_attr($rowBg) . ';color:' . esc_attr($cellColor) . ';padding:' . esc_attr((string) $cellPadding) . 'px;' . esc_attr($cellBorderCss) . '">' . esc_html((string) ($row[$columnIndex] ?? '')) . '</td>';
                }
                $tbody .= '</tr>';
            }
            $tbody .= '</tbody>';'''
new, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
if count != 1:
    raise SystemExit(f'Renderer table replacement expected 1, got {count}')
write(renderer, new)

renderer_helper = r'''    /** @param array<string,mixed> $props */
    private static function tableCellBorderCss(array $props, string $key, int $row, int $col, int $rowCount, int $colCount): string
    {
        $mode = in_array((string) ($props['borderMode'] ?? 'all'), ['all', 'outer', 'inner', 'none'], true) ? (string) ($props['borderMode'] ?? 'all') : 'all';
        $width = max(0, min(10, (int) ($props['cellBorderWidth'] ?? 1)));
        $color = sanitize_hex_color((string) ($props['cellBorderColor'] ?? '#dcdcde')) ?: '#dcdcde';
        $style = in_array((string) ($props['cellBorderStyle'] ?? 'solid'), ['solid', 'dashed', 'dotted'], true) ? (string) ($props['cellBorderStyle'] ?? 'solid') : 'solid';
        $custom = isset($props['cellBorders'][$key]) && is_array($props['cellBorders'][$key]) ? $props['cellBorders'][$key] : [];
        $values = [];
        foreach (['top', 'right', 'bottom', 'left'] as $side) {
            $outer = $side === 'top' ? $row === 0 : ($side === 'bottom' ? $row === $rowCount - 1 : ($side === 'left' ? $col === 0 : $col === $colCount - 1));
            $enabled = $mode === 'all' || ($mode === 'outer' && $outer) || ($mode === 'inner' && !$outer);
            $sideWidth = $width; $sideColor = $color; $sideStyle = $style;
            if (isset($custom[$side]) && is_array($custom[$side])) {
                $entry = $custom[$side];
                $enabled = array_key_exists('enabled', $entry) ? (bool) $entry['enabled'] : true;
                $sideWidth = max(0, min(10, (int) ($entry['width'] ?? $width)));
                $sideColor = sanitize_hex_color((string) ($entry['color'] ?? $color)) ?: $color;
                $sideStyle = in_array((string) ($entry['style'] ?? $style), ['solid', 'dashed', 'dotted'], true) ? (string) ($entry['style'] ?? $style) : $style;
            }
            $values[$side] = $enabled && $sideWidth > 0 ? ($sideWidth . 'px ' . $sideStyle . ' ' . $sideColor) : '0';
        }
        return 'border-top:' . $values['top'] . ';border-right:' . $values['right'] . ';border-bottom:' . $values['bottom'] . ';border-left:' . $values['left'] . ';';
    }

'''
text = read(renderer)
marker = '    private static function iconSvg(string $token): string\n'
if 'private static function tableCellBorderCss' not in text:
    if text.count(marker) != 1:
        raise SystemExit('Renderer helper insertion marker missing')
    text = text.replace(marker, renderer_helper + marker, 1)
    write(renderer, text)


# ---------------------------------------------------------------------------
# Manuals/status/release metadata
# ---------------------------------------------------------------------------
design_block = '''## 25. Ikonbibliotek\n\nVisual Designer bruger et centralt SVG-ikonregister. Et Icon-element gemmer kun sin canonical kilde (`iconSet`) og sit ikon-ID (`icon`). SVG-geometrien ligger i biblioteket og må ikke kopieres ind i hver side.\n\nIkonbiblioteket har tre permanente niveauer:\n\n1. **Core icons** – følger med Visual Designer Manager og organiseres i kategorier.\n2. **Module icons** – moduler som Køretøjer, Events og Galleri kan registrere ekstra ikon-sæt uden at ændre core-biblioteket.\n3. **Custom icons** – reserveret udvidelsesniveau, hvor administrator senere skal kunne uploade eller indsætte egne sanitiserede SVG-ikoner. Persistent Custom-upload er ikke aktiveret i v0.1.66.\n\nCore-biblioteket skal være lokalt, SVG-baseret og uden eksterne font-/ikonafhængigheder. Designer og frontend skal bruge samme registry.\n\n## 26. Tabel – kantdesign\n\nTabel er et struktureret Designer-element og skal understøtte Excel-lignende kantstyring. En eller flere celler kan markeres, og kantværktøjet kan anvende Yderramme, Indvendige, Alle, Vandret, Lodret, Top, Højre, Bund, Venstre eller Ingen. Stregens tykkelse, farve og stil (`solid`, `dashed`, `dotted`) er canonical data. Celle-overrides gemmes separat fra tabelstandarden og skal fungere med Copy/Paste, Undo/Redo, Save/Reload, Preview og frontend.\n'''
append_once('CLEAN-DESIGN-MANUAL.md', '## 25. Ikonbibliotek', design_block)

tech_block = '''## 27. v0.1.66 – ikonregister, tabelkanter og Menu-preview\n\n### VD-ICON-LIBRARY-001\n\n- Core icons er lokal SVG og kategoriseret i det centrale `IconRegistry`.\n- Module icons registreres via den dokumenterede module-filterkontrakt.\n- Custom icons er reserveret som tredje niveau; upload/indsæt-UI kommer senere.\n- Side Designer og Header/Footer bruger samme ikonregister og samme SVG-rendering som frontend.\n\n### VD-TABLE-BORDERS-001\n\n- Klik markerer én tabelcelle. Ctrl/Cmd+klik tilføjer/fjerner celler. Shift+klik markerer et rektangulært område.\n- Markeret område understøtter Yderramme, Indvendige, Alle, Vandret, Lodret, Top, Højre, Bund, Venstre og Ingen.\n- Border-pen styrer tykkelse, farve og `solid/dashed/dotted`.\n- Cellekanter er canonical `cellBorders`; tabelstandard er `borderMode`, `cellBorderWidth`, `cellBorderColor`, `cellBorderStyle`.\n- Samme data bruges i Designer-preview og frontend.\n\n### VD-MENU-PREVIEW-001\n\n- Struktur-preview er bredere på store skærme og holder Desktop-menuens root-punkter på én vandret række.\n- Hvis strukturen stadig er bredere end previewet, bruges vandret scroll i previewet i stedet for kunstig line-wrap.\n- På smallere adminskærme flyttes previewet fortsat under menu-editoren.\n\n### VD-ADMIN-STATUS-002\n\n- `Log` og `Konvertering` vises som `Klar` i Visual Designer Manager-menuen.\n'''
append_once('CLEAN-TECHNICAL-MANUAL.md', 'VD-ICON-LIBRARY-001', tech_block)

# Update the older table contract from "later" to current requirement.
text = read('CLEAN-TECHNICAL-MANUAL.md')
text = text.replace('- senere eventuelt solid/dashed/dotted.', '- solid/dashed/dotted.')
write('CLEAN-TECHNICAL-MANUAL.md', text)

status_doc = '''# Visual Designer Manager v0.1.66 – teststatus\n\nStatus: TESTKANDIDAT\n\nScope:\n- Icon Library foundation med Core / Module / Custom-arkitektur.\n- Core SVG-bibliotek med kategorier og søgbar picker.\n- Excel-lignende Tabel Border Designer med multi-cell selection og canonical cellekanter.\n- Menu Struktur-preview udvidet til 580 px med nowrap + horisontal scroll.\n- Log og Konvertering markeret Klar i Admin.\n\nIkke med i denne version:\n- Custom icon upload/indsæt UI og persistent storage.\n- Dynamic datasource/binding og Køretøjsmodulet.\n'''
write('docs/v0166-status.md', status_doc)

release_notes = '''<h4>0.1.66 – Icon Library, Tabelkanter og Menu-preview · testversion</h4><ul><li><strong>VD-ICON-LIBRARY-001:</strong> Centralt SVG-ikonregister med kategorier og søgbar Icon-picker. Arkitekturen har Core, Module og reserveret Custom-niveau.</li><li><strong>VD-TABLE-BORDERS-001:</strong> Tabel får Excel-lignende multi-cell selection og kanter: Yderramme, Indvendige, Alle, Vandret, Lodret, Top, Højre, Bund, Venstre og Ingen samt tykkelse, farve og solid/stiplet/prikket.</li><li><strong>VD-MENU-PREVIEW-001:</strong> Menuens Desktop Struktur-preview er bredere, nowrap og kan scrolle vandret i stedet for at bryde menupunkter kunstigt.</li><li><strong>VD-ADMIN-STATUS-002:</strong> Log og Konvertering vises som Klar.</li><li>Custom SVG-upload og dynamisk databinding er fortsat reserveret til senere versioner.</li></ul>\n'''
notes = read('clean-release-notes.html')
if '0.1.66 – Icon Library' not in notes:
    write('clean-release-notes.html', release_notes + notes)

history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
if not any(str(row.get('version')) == '0.1.66' for row in history if isinstance(row, dict)):
    history.insert(0, {
        'version': '0.1.66',
        'title': 'Icon Library, Tabelkanter og Menu-preview',
        'status': 'test',
        'contracts': ['VD-ICON-LIBRARY-001','VD-TABLE-BORDERS-001','VD-MENU-PREVIEW-001','VD-ADMIN-STATUS-002'],
    })
    write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

print('Applied Visual Designer Manager v0.1.66 foundation changes.')
