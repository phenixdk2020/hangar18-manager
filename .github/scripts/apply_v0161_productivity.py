from pathlib import Path

ROOT = Path('.')
PLUGIN_ROOT = ROOT / 'clean/hangar18-manager'
PLUGIN = PLUGIN_ROOT / 'hangar18-manager.php'
MODEL = PLUGIN_ROOT / 'src/Model/LayoutModel.php'
RENDERER = PLUGIN_ROOT / 'src/Frontend/Renderer.php'
EDITOR = PLUGIN_ROOT / 'assets/editor-v018-core.js'
EDITOR_CSS = PLUGIN_ROOT / 'assets/editor.css'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


# Version + a readable/user-specific Designer context for cross-page clipboard.
plugin = PLUGIN.read_text(encoding='utf-8')
plugin = replace_once(plugin, ' * Version: 0.1.60', ' * Version: 0.1.61', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.60');", "define('H18_CLEAN_VERSION', '0.1.61');", 'runtime version')
context_old = """        $model = $templateId !== '' ? \\VisualDesignerManager\\Model\\TemplateLayoutModel::model($templateId) : \\VisualDesignerManager\\Model\\LayoutModel::empty();
    } else {
        $model = $postId > 0 && get_post_type($postId) === 'page'
            ? \\VisualDesignerManager\\Model\\LayoutModel::get($postId)
            : \\VisualDesignerManager\\Model\\LayoutModel::empty();
    }
"""
context_new = """        $model = $templateId !== '' ? \\VisualDesignerManager\\Model\\TemplateLayoutModel::model($templateId) : \\VisualDesignerManager\\Model\\LayoutModel::empty();
        $templateMeta = $templateId !== '' ? \\VisualDesignerManager\\Model\\TemplateLayoutModel::meta($templateId) : null;
        $contextLabel = is_array($templateMeta) ? (string) ($templateMeta['name'] ?? ($part === 'header' ? 'Header' : 'Footer')) : ($part === 'header' ? 'Header' : 'Footer');
    } else {
        $model = $postId > 0 && get_post_type($postId) === 'page'
            ? \\VisualDesignerManager\\Model\\LayoutModel::get($postId)
            : \\VisualDesignerManager\\Model\\LayoutModel::empty();
        $contextLabel = $postId > 0 ? (string) get_the_title($postId) : 'Visual Designer';
    }
"""
plugin = replace_once(plugin, context_old, context_new, 'editor clipboard context label')
localize_old = """        'postId' => $postId,
        'initialModel' => $model,
"""
localize_new = """        'postId' => $postId,
        'userId' => get_current_user_id(),
        'contextLabel' => $contextLabel,
        'initialModel' => $model,
"""
plugin = replace_once(plugin, localize_old, localize_new, 'editor clipboard localization')
PLUGIN.write_text(plugin, encoding='utf-8')


# Canonical pixel offsets are common properties, while grid geometry stays unchanged.
model = MODEL.read_text(encoding='utf-8')
border_old = """            'gapX' => self::clamp($raw['gapX'] ?? 0, 0, 200, 0),
            'gapY' => self::clamp($raw['gapY'] ?? 0, 0, 200, 0),
"""
border_new = """            'gapX' => self::clamp($raw['gapX'] ?? 0, 0, 200, 0),
            'gapY' => self::clamp($raw['gapY'] ?? 0, 0, 200, 0),
            'offsetX' => self::clamp($raw['offsetX'] ?? 0, -2000, 2000, 0),
            'offsetY' => self::clamp($raw['offsetY'] ?? 0, -2000, 2000, 0),
"""
model = replace_once(model, border_old, border_new, 'canonical pixel offsets')
MODEL.write_text(model, encoding='utf-8')


# Frontend paints the same visual offsets as the Designer.
renderer = RENDERER.read_text(encoding='utf-8')
renderer_props_old = """        $props = is_array($node['props'] ?? null) ? $node['props'] : [];
        $borderStyle = self::borderStyle($props);
"""
renderer_props_new = """        $props = is_array($node['props'] ?? null) ? $node['props'] : [];
        $offsetX = max(-2000, min(2000, (int) ($props['offsetX'] ?? 0)));
        $offsetY = max(-2000, min(2000, (int) ($props['offsetY'] ?? 0)));
        $offsetStyle = ($offsetX !== 0 || $offsetY !== 0) ? 'transform:translate(' . $offsetX . 'px,' . $offsetY . 'px);' : '';
        $style .= $offsetStyle;
        $borderStyle = self::borderStyle($props);
"""
renderer = replace_once(renderer, renderer_props_old, renderer_props_new, 'frontend offset style')
floating_old = """                $layoutStyle = 'position:absolute;left:' . $leftPct . '%;top:' . ($y * LayoutModel::ROW_PX) . 'px;width:' . $widthPct . '%;' . $heightCss . 'z-index:' . $zIndex . ';grid-column:auto;grid-row:auto;margin-top:0;';
"""
floating_new = """                $layoutStyle = 'position:absolute;left:' . $leftPct . '%;top:' . ($y * LayoutModel::ROW_PX) . 'px;width:' . $widthPct . '%;' . $heightCss . 'z-index:' . $zIndex . ';grid-column:auto;grid-row:auto;margin-top:0;' . $offsetStyle;
"""
renderer = replace_once(renderer, floating_old, floating_new, 'floating button offset style')
RENDERER.write_text(renderer, encoding='utf-8')


editor = EDITOR.read_text(encoding='utf-8')
const_old = """    const POST_ID = parseInt(CFG.postId || 0, 10) || 0;
    const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu'];
"""
const_new = """    const POST_ID = parseInt(CFG.postId || 0, 10) || 0;
    const USER_ID = Math.max(0, parseInt(CFG.userId || 0, 10) || 0);
    const CONTEXT_LABEL = String(CFG.contextLabel || (POST_ID ? ('Side ' + POST_ID) : 'Global Designer'));
    const CLIPBOARD_KEY = 'h18-vd-clipboard-v1-u' + String(USER_ID);
    const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu'];
"""
editor = replace_once(editor, const_old, const_new, 'clipboard constants')
state_old = """    let resize = null;
    let lastAction = '';
"""
state_new = """    let resize = null;
    let lastAction = '';
    let nudgeSession = null;
    let memoryClipboard = null;
"""
editor = replace_once(editor, state_old, state_new, 'keyboard clipboard runtime state')
field_old = "gapX:'Afstand X',gapY:'Afstand Y',buttonText:'knaptekst'"
field_new = "gapX:'Afstand X',gapY:'Afstand Y',offsetX:'finjustering X',offsetY:'finjustering Y',buttonText:'knaptekst'"
editor = replace_once(editor, field_old, field_new, 'offset field labels')
common_old = """            borderColor: normalizeColor(raw.borderColor || '#000000'),
            gapX: clamp(parseInt(raw.gapX || 0, 10) || 0, 0, 200),
            gapY: clamp(parseInt(raw.gapY || 0, 10) || 0, 0, 200)
"""
common_new = """            borderColor: normalizeColor(raw.borderColor || '#000000'),
            gapX: clamp(parseInt(raw.gapX || 0, 10) || 0, 0, 200),
            gapY: clamp(parseInt(raw.gapY || 0, 10) || 0, 0, 200),
            offsetX: clamp(parseInt(raw.offsetX || 0, 10) || 0, -2000, 2000),
            offsetY: clamp(parseInt(raw.offsetY || 0, 10) || 0, -2000, 2000)
"""
editor = replace_once(editor, common_old, common_new, 'Designer offset normalization')

# Productivity functions are inserted after the existing hierarchy helpers.
marker = "    function structuralSummary() {\n"
productivity = r'''    function isEditableTarget(target) {
        if (!target || typeof target.closest !== 'function') { return false; }
        return !!target.closest('input,textarea,select,[contenteditable="true"],.wp-editor-area,.mce-content-body');
    }

    function clipboardPayloadFor(id) {
        const root = nodeById(id);
        if (!root) { return null; }
        const ids = new Set([root.id].concat(descendants(root.id)));
        return {
            schemaVersion: 1,
            sourcePostId: POST_ID,
            sourceContext: CONTEXT_LABEL,
            copiedUtc: new Date().toISOString(),
            rootId: root.id,
            rootType: root.type,
            nodes: clone(state.nodes.filter(function (node) { return ids.has(node.id); }))
        };
    }

    function readClipboard() {
        let value = memoryClipboard;
        try {
            const raw = window.localStorage ? window.localStorage.getItem(CLIPBOARD_KEY) : '';
            if (raw) { value = JSON.parse(raw); memoryClipboard = value; }
        } catch (ignore) {}
        if (!value || !Array.isArray(value.nodes) || !value.nodes.length || !value.rootId) { return null; }
        return value;
    }

    function writeClipboard(value) {
        memoryClipboard = value;
        try { if (window.localStorage) { window.localStorage.setItem(CLIPBOARD_KEY, JSON.stringify(value)); } } catch (ignore) {}
        updateProductivityToolbar();
    }

    function clearClipboard() {
        memoryClipboard = null;
        try { if (window.localStorage) { window.localStorage.removeItem(CLIPBOARD_KEY); } } catch (ignore) {}
        updateProductivityToolbar();
    }

    function copySelected() {
        const payload = clipboardPayloadFor(selectedId);
        if (!payload) { return false; }
        writeClipboard(payload);
        lastAction = 'Kopiér ' + typeLabel(payload.rootType);
        diag('clipboard_copy', { rootId: payload.rootId, rootType: payload.rootType, nodeCount: payload.nodes.length, sourcePostId: POST_ID });
        return true;
    }

    function resolvePasteParent(payload) {
        const selected = nodeById(selectedId);
        if (selected && PARENT_TYPES.includes(selected.type) && selected.id !== payload.rootId) { return selected.id; }
        if (selected && !PARENT_TYPES.includes(selected.type)) { return selected.parentId; }
        if (parseInt(payload.sourcePostId || 0, 10) === POST_ID) {
            const source = nodeById(payload.rootId);
            if (source) { return source.parentId; }
        }
        return '';
    }

    function pastePayload(payload, duplicateMode) {
        if (!payload || !Array.isArray(payload.nodes) || !payload.nodes.length) { return false; }
        if (state.nodes.length + payload.nodes.length > 300) {
            window.alert('Indsætning ville overskride Designerens maksimum på 300 elementer.');
            return false;
        }
        const sourceRoot = payload.nodes.find(function (node) { return node && node.id === payload.rootId; });
        if (!sourceRoot || !TYPES.includes(String(sourceRoot.type || '').toLowerCase())) { return false; }
        let parentId = resolvePasteParent(payload);
        const parent = parentId ? nodeById(parentId) : null;
        if (parentId && (!parent || !PARENT_TYPES.includes(parent.type))) { parentId = ''; }

        const before = clone(state);
        const idMap = {};
        payload.nodes.forEach(function (source) {
            if (!source || !TYPES.includes(String(source.type || '').toLowerCase())) { return; }
            let next = makeId(String(source.type));
            while (nodeById(next) || Object.values(idMap).includes(next)) { next = makeId(String(source.type)); }
            idMap[String(source.id)] = next;
        });
        if (!idMap[payload.rootId]) { return false; }

        const newNodes = [];
        payload.nodes.forEach(function (source) {
            if (!source || !idMap[source.id]) { return; }
            const next = clone(source);
            next.id = idMap[source.id];
            if (source.id === payload.rootId) {
                next.parentId = parentId;
                next.order = nextOrder(parentId);
                if (!next.geometry || !next.geometry.desktop) { next.geometry = { desktop: normalizeDevice({}, false) }; }
                next.geometry.desktop.y = nextFreeY(parentId);
                next.geometry.desktop.x = clamp(parseInt(next.geometry.desktop.x || 0, 10) || 0, 0, UNITS - 1);
                next.geometry.desktop.w = clamp(parseInt(next.geometry.desktop.w || UNITS, 10) || UNITS, 1, UNITS - next.geometry.desktop.x);
            } else {
                next.parentId = idMap[source.parentId] || '';
            }
            newNodes.push(next);
        });
        state.nodes = state.nodes.concat(newNodes);
        state = normalizeModel(state);
        selectedId = idMap[payload.rootId];
        const label = (duplicateMode ? 'Duplikér ' : 'Indsæt ') + typeLabel(sourceRoot.type) + (payload.nodes.length > 1 ? ' + indhold' : '');
        commit(before, label);
        render();
        diag(duplicateMode ? 'clipboard_duplicate' : 'clipboard_paste', { sourceRootId: payload.rootId, newRootId: selectedId, nodeCount: payload.nodes.length, targetParentId: parentId, sourcePostId: parseInt(payload.sourcePostId || 0, 10) || 0, targetPostId: POST_ID });
        return true;
    }

    function pasteClipboard() { return pastePayload(readClipboard(), false); }
    function duplicateSelected() {
        const payload = clipboardPayloadFor(selectedId);
        return payload ? pastePayload(payload, true) : false;
    }

    function finalizeNudge() {
        if (!nudgeSession) { return; }
        const session = nudgeSession;
        nudgeSession = null;
        const node = nodeById(session.id);
        commit(session.before, 'Finjuster ' + typeLabel(node ? node.type : session.type) + ' med piletaster');
        diag('keyboard_nudge_commit', { id: session.id, offsetX: node ? node.props.offsetX : 0, offsetY: node ? node.props.offsetY : 0, state: structuralSummary() });
    }

    function nudgeSelected(dx, dy) {
        const node = nodeById(selectedId);
        if (!node || resize) { return false; }
        if (!nudgeSession || nudgeSession.id !== node.id) {
            finalizeNudge();
            nudgeSession = { id: node.id, type: node.type, before: clone(state) };
        }
        node.props.offsetX = clamp((parseInt(node.props.offsetX || 0, 10) || 0) + dx, -2000, 2000);
        node.props.offsetY = clamp((parseInt(node.props.offsetY || 0, 10) || 0) + dy, -2000, 2000);
        lastAction = 'Finjuster ' + typeLabel(node.type);
        render();
        return true;
    }

    function ensureProductivityToolbar() {
        if (document.getElementById('h18-vd-productivity')) { return; }
        const toolbar = document.querySelector('.h18-clean-toolbar');
        if (!toolbar) { return; }
        const host = document.createElement('span');
        host.id = 'h18-vd-productivity';
        host.className = 'h18-vd-productivity';
        host.innerHTML = '<button type="button" class="button" id="h18-vd-copy">Kopiér</button><button type="button" class="button" id="h18-vd-paste">Indsæt</button><button type="button" class="button" id="h18-vd-duplicate">Duplikér</button><span id="h18-vd-clipboard-status" class="h18-vd-clipboard-status" aria-live="polite"></span><button type="button" class="button-link" id="h18-vd-clear-clipboard">Ryd clipboard</button>';
        toolbar.appendChild(host);
        host.querySelector('#h18-vd-copy').addEventListener('click', copySelected);
        host.querySelector('#h18-vd-paste').addEventListener('click', pasteClipboard);
        host.querySelector('#h18-vd-duplicate').addEventListener('click', duplicateSelected);
        host.querySelector('#h18-vd-clear-clipboard').addEventListener('click', clearClipboard);
        updateProductivityToolbar();
    }

    function updateProductivityToolbar() {
        const host = document.getElementById('h18-vd-productivity');
        if (!host) { return; }
        const payload = readClipboard();
        const copyButton = host.querySelector('#h18-vd-copy');
        const pasteButton = host.querySelector('#h18-vd-paste');
        const duplicateButton = host.querySelector('#h18-vd-duplicate');
        const clearButton = host.querySelector('#h18-vd-clear-clipboard');
        const status = host.querySelector('#h18-vd-clipboard-status');
        if (copyButton) { copyButton.disabled = !nodeById(selectedId); }
        if (duplicateButton) { duplicateButton.disabled = !nodeById(selectedId); }
        if (pasteButton) { pasteButton.disabled = !payload; }
        if (clearButton) { clearButton.disabled = !payload; }
        if (status) {
            status.textContent = payload ? ('Clipboard: ' + typeLabel(payload.rootType || '') + ' · ' + payload.nodes.length + ' element' + (payload.nodes.length === 1 ? '' : 'er') + (payload.sourceContext ? ' · ' + payload.sourceContext : '')) : 'Clipboard: tom';
        }
    }

'''
if marker not in editor:
    raise SystemExit('Could not find structuralSummary marker')
editor = editor.replace(marker, productivity + marker, 1)

visual_old = """        const gapY = clamp(parseInt(props.gapY || 0, 10) || 0, 0, 200);
        card.style.boxSizing = 'border-box';
"""
visual_new = """        const gapY = clamp(parseInt(props.gapY || 0, 10) || 0, 0, 200);
        const offsetX = clamp(parseInt(props.offsetX || 0, 10) || 0, -2000, 2000);
        const offsetY = clamp(parseInt(props.offsetY || 0, 10) || 0, -2000, 2000);
        card.style.transform = (offsetX || offsetY) ? ('translate(' + offsetX + 'px,' + offsetY + 'px)') : '';
        card.style.boxSizing = 'border-box';
"""
editor = replace_once(editor, visual_old, visual_new, 'Designer visual pixel offset')

inspector_old = """        html += '<div class=\"h18-clean-field-grid\"><label>X / 120<input data-field=\"gx\" type=\"number\" min=\"0\" max=\"119\" value=\"' + g.x + '\"></label><label>Bredde / 120<input data-field=\"gw\" type=\"number\" min=\"1\" max=\"120\" value=\"' + g.w + '\"></label><label>Y · 8px<input data-field=\"gy\" type=\"number\" value=\"' + g.y + '\"></label><label>Højde · 8px<input data-field=\"gh\" type=\"number\" min=\"0\" value=\"' + g.h + '\"></label></div>';
"""
inspector_new = inspector_old + """        html += '<div class=\"h18-vd-nudge-inspector\"><strong>Finjustering · pixels</strong><div class=\"h18-clean-field-grid\"><label>Offset X px<input data-field=\"offsetX\" type=\"number\" min=\"-2000\" max=\"2000\" value=\"' + (node.props.offsetX || 0) + '\"></label><label>Offset Y px<input data-field=\"offsetY\" type=\"number\" min=\"-2000\" max=\"2000\" value=\"' + (node.props.offsetY || 0) + '\"></label></div><button type=\"button\" class=\"button\" id=\"h18-clean-reset-offset\">Nulstil finjustering</button><p class=\"description\">Piletaster flytter 1 px. Shift + piletast flytter 10 px. Grid-positionen ændres ikke.</p></div>';
"""
editor = replace_once(editor, inspector_old, inspector_new, 'Inspector pixel offset controls')

change_old = """                else if (field === 'gapX') { current.props.gapX = clamp(parseInt(control.value || 0, 10) || 0, 0, 200); }
                else if (field === 'gapY') {
"""
change_new = """                else if (field === 'gapX') { current.props.gapX = clamp(parseInt(control.value || 0, 10) || 0, 0, 200); }
                else if (field === 'offsetX') { current.props.offsetX = clamp(parseInt(control.value || 0, 10) || 0, -2000, 2000); }
                else if (field === 'offsetY') { current.props.offsetY = clamp(parseInt(control.value || 0, 10) || 0, -2000, 2000); }
                else if (field === 'gapY') {
"""
editor = replace_once(editor, change_old, change_new, 'Inspector offset change handling')

reset_old = """        const del = document.getElementById('h18-clean-delete');
        if (del) { del.addEventListener('click', function () { if (window.confirm('Slet det valgte element?')) { deleteSelected(); } }); }
        const pick = document.getElementById('h18-clean-pick-image');
"""
reset_new = """        const resetOffset = document.getElementById('h18-clean-reset-offset');
        if (resetOffset) {
            resetOffset.addEventListener('click', function () {
                const current = nodeById(selectedId);
                if (!current) { return; }
                const before = clone(state);
                current.props.offsetX = 0;
                current.props.offsetY = 0;
                commit(before, 'Nulstil finjustering på ' + typeLabel(current.type));
                render();
            });
        }
        const del = document.getElementById('h18-clean-delete');
        if (del) { del.addEventListener('click', function () { if (window.confirm('Slet det valgte element?')) { deleteSelected(); } }); }
        const pick = document.getElementById('h18-clean-pick-image');
"""
editor = replace_once(editor, reset_old, reset_new, 'offset reset control')

render_old = """        renderInspector();
        updateHidden();
        updateHistoryUi();
    }
"""
render_new = """        renderInspector();
        updateHidden();
        updateHistoryUi();
        updateProductivityToolbar();
    }
"""
editor = replace_once(editor, render_old, render_new, 'productivity toolbar refresh')

key_old = """        document.addEventListener('keydown', function (event) {
            const key = String(event.key || '').toLowerCase();
            if (!(event.ctrlKey || event.metaKey)) { return; }
            if (key === 'z' && event.shiftKey) { event.preventDefault(); redo(); }
            else if (key === 'z') { event.preventDefault(); undo(); }
            else if (key === 'y') { event.preventDefault(); redo(); }
        });
"""
key_new = """        document.addEventListener('keydown', function (event) {
            if (isEditableTarget(event.target)) { return; }
            const key = String(event.key || '').toLowerCase();
            if (event.ctrlKey || event.metaKey) {
                if (key === 'z' && event.shiftKey) { event.preventDefault(); finalizeNudge(); redo(); }
                else if (key === 'z') { event.preventDefault(); finalizeNudge(); undo(); }
                else if (key === 'y') { event.preventDefault(); finalizeNudge(); redo(); }
                else if (key === 'c' && nodeById(selectedId)) { event.preventDefault(); finalizeNudge(); copySelected(); }
                else if (key === 'v' && readClipboard()) { event.preventDefault(); finalizeNudge(); pasteClipboard(); }
                else if (key === 'd' && nodeById(selectedId)) { event.preventDefault(); finalizeNudge(); duplicateSelected(); }
                return;
            }
            const step = event.shiftKey ? 10 : 1;
            if (key === 'arrowleft' && nudgeSelected(-step, 0)) { event.preventDefault(); }
            else if (key === 'arrowright' && nudgeSelected(step, 0)) { event.preventDefault(); }
            else if (key === 'arrowup' && nudgeSelected(0, -step)) { event.preventDefault(); }
            else if (key === 'arrowdown' && nudgeSelected(0, step)) { event.preventDefault(); }
        });
        document.addEventListener('keyup', function (event) {
            if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(String(event.key || ''))) { finalizeNudge(); }
        });
        window.addEventListener('blur', finalizeNudge);
"""
editor = replace_once(editor, key_old, key_new, 'keyboard shortcuts and nudge grouping')

install_old = """        render();
        diag('editor_boot', { version: CFG.version || '', layoutMode: 'cell-split-grid', state: structuralSummary() });
"""
install_new = """        ensureProductivityToolbar();
        render();
        diag('editor_boot', { version: CFG.version || '', layoutMode: 'cell-split-grid', state: structuralSummary() });
"""
editor = replace_once(editor, install_old, install_new, 'productivity toolbar install')
EDITOR.write_text(editor, encoding='utf-8')


css = EDITOR_CSS.read_text(encoding='utf-8')
if '0.1.61 keyboard + clipboard productivity' not in css:
    css += r'''

/* 0.1.61 keyboard + clipboard productivity */
.h18-vd-productivity{display:inline-flex;align-items:center;gap:6px;flex-wrap:wrap}
.h18-vd-clipboard-status{font-size:12px;color:#50575e;max-width:360px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.h18-vd-nudge-inspector{margin:12px 0;padding:10px;border:1px solid #dcdcde;border-radius:6px;background:#f9f9f9}
.h18-vd-nudge-inspector>strong{display:block;margin-bottom:6px}
'''
EDITOR_CSS.write_text(css, encoding='utf-8')

print('Applied v0.1.61 keyboard and clipboard productivity patch.')
