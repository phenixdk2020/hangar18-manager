from pathlib import Path
import json

ROOT = Path('.')

def read(path):
    return (ROOT / path).read_text(encoding='utf-8')

def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    return text.replace(old, new, 1)

def replace_span(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f'Missing start marker: {label}')
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f'Missing end marker: {label}')
    return text[:start] + replacement + text[end:]

# -----------------------------------------------------------------------------
# Version + enqueue the viewport layer before the core so first render already
# happens at the real virtual frontend width.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/hangar18-manager.php'
s = read(path)
s = replace_once(s, ' * Version: 0.1.43', ' * Version: 0.1.44', 'plugin header version')
s = replace_once(s, "define('H18_CLEAN_VERSION', '0.1.43');", "define('H18_CLEAN_VERSION', '0.1.44');", 'version constant')
anchor = "    wp_enqueue_script(\n        'h18-clean-editor-v018-core',"
insert = """    wp_enqueue_script(
        'h18-clean-editor-v0144-viewport',
        H18_CLEAN_URL . 'assets/editor-v0144-viewport.js',
        ['jquery'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v018-core',"""
s = replace_once(s, anchor, insert, 'viewport script enqueue')
s = replace_once(s, "        ['jquery'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    wp_localize_script('h18-clean-editor-v018-core'", "        ['jquery', 'h18-clean-editor-v0144-viewport'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    wp_localize_script('h18-clean-editor-v018-core'", 'core dependency')
css_anchor = "    wp_enqueue_style(\n        'h18-clean-editor-v0135',\n        H18_CLEAN_URL . 'assets/editor-v0135.css',\n        ['h18-clean-editor-v0134'],\n        H18_CLEAN_VERSION\n    );"
css_insert = css_anchor + """
    wp_enqueue_style(
        'h18-clean-editor-v0144',
        H18_CLEAN_URL . 'assets/editor-v0144.css',
        ['h18-clean-editor-v0135'],
        H18_CLEAN_VERSION
    );"""
s = replace_once(s, css_anchor, css_insert, 'viewport css enqueue')
write(path, s)

# -----------------------------------------------------------------------------
# BUG-14 viewport bootstrap. It executes before editor-v018-core and fixes the
# physical layout width before natural text heights are materialised.
# -----------------------------------------------------------------------------
viewport_js = r'''(function () {
    'use strict';

    var WIDTHS = { desktop: 1920, laptop: 1180, mobile: 390 };
    var MIN_SCALE = 0.15;
    var root = null;
    var column = null;
    var stage = null;
    var currentScale = 1;
    var currentWidth = WIDTHS.desktop;
    var scheduled = false;
    var rootObserver = null;
    var columnObserver = null;
    var bodyObserver = null;

    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
    function activeDevice() {
        if (window.H18CleanResponsive && typeof window.H18CleanResponsive.device === 'function') {
            var responsiveDevice = String(window.H18CleanResponsive.device() || '');
            if (WIDTHS[responsiveDevice]) { return responsiveDevice; }
        }
        var bodyDevice = document.body ? String(document.body.getAttribute('data-h18-clean-device') || '') : '';
        if (WIDTHS[bodyDevice]) { return bodyDevice; }
        var rootDevice = root ? String(root.getAttribute('data-h18-device') || '') : '';
        return WIDTHS[rootDevice] ? rootDevice : 'desktop';
    }
    function availableWidth() {
        if (!column) { return currentWidth; }
        var style = window.getComputedStyle(column);
        var left = parseFloat(style.paddingLeft || '0') || 0;
        var right = parseFloat(style.paddingRight || '0') || 0;
        return Math.max(80, column.clientWidth - left - right - 2);
    }
    function ensureStage() {
        root = document.getElementById('h18-clean-canvas');
        if (!root) { return false; }
        column = root.closest('.h18-clean-canvas-column') || root.parentElement;
        if (!column) { return false; }
        if (root.parentElement && root.parentElement.classList.contains('h18-vd-viewport-stage')) {
            stage = root.parentElement;
            return true;
        }
        stage = document.createElement('div');
        stage.className = 'h18-vd-viewport-stage';
        column.insertBefore(stage, root);
        stage.appendChild(root);
        return true;
    }
    function ensureStatus() {
        var toolbar = document.querySelector('.h18-clean-toolbar');
        if (!toolbar) { return null; }
        var status = document.getElementById('h18-vd-viewport-status');
        if (status) { return status; }
        status = document.createElement('span');
        status.id = 'h18-vd-viewport-status';
        status.className = 'h18-vd-viewport-status';
        var gridLabel = toolbar.querySelector('.h18-clean-grid-label');
        if (gridLabel) { gridLabel.insertAdjacentElement('afterend', status); }
        else { toolbar.appendChild(status); }
        return status;
    }
    function syncStageHeight() {
        if (!root || !stage) { return; }
        var height = Math.max(1, root.offsetHeight || root.scrollHeight || 1);
        stage.style.height = Math.ceil(height * currentScale) + 'px';
    }
    function applyFit() {
        if (!ensureStage()) { return; }
        var device = activeDevice();
        currentWidth = WIDTHS[device] || WIDTHS.desktop;
        currentScale = clamp(Math.min(1, availableWidth() / currentWidth), MIN_SCALE, 1);

        root.setAttribute('data-h18-viewport-width', String(currentWidth));
        root.setAttribute('data-h18-viewport-scale', String(currentScale));
        root.style.width = currentWidth + 'px';
        root.style.maxWidth = 'none';
        root.style.transformOrigin = '0 0';
        root.style.transform = 'scale(' + currentScale + ')';

        stage.style.width = Math.ceil(currentWidth * currentScale) + 'px';
        syncStageHeight();

        var status = ensureStatus();
        if (status) {
            var label = ({ desktop: 'Desktop', laptop: 'Laptop', mobile: 'Mobil' })[device] || device;
            status.textContent = label + ' · ' + currentWidth + ' px · Fit ' + Math.round(currentScale * 100) + '%';
            status.title = 'Virtuel frontendbredde. Fit ændrer kun editor-zoom, aldrig layoutgeometri.';
        }
        window.dispatchEvent(new CustomEvent('h18-vd-viewport-fit', { detail: { device: device, width: currentWidth, scale: currentScale } }));
    }
    function schedule() {
        if (scheduled) { return; }
        scheduled = true;
        window.requestAnimationFrame(function () {
            scheduled = false;
            applyFit();
        });
    }
    function installObservers() {
        if (window.ResizeObserver && column && !columnObserver) {
            columnObserver = new ResizeObserver(schedule);
            columnObserver.observe(column);
        }
        if (window.ResizeObserver && root && !rootObserver) {
            rootObserver = new ResizeObserver(function () { syncStageHeight(); });
            rootObserver.observe(root);
        }
        if (window.MutationObserver && document.body && !bodyObserver) {
            bodyObserver = new MutationObserver(function (records) {
                var relevant = records.some(function (record) {
                    return record.type === 'attributes' && (record.attributeName === 'data-h18-clean-device' || record.attributeName === 'class');
                });
                if (relevant) { schedule(); }
            });
            bodyObserver.observe(document.body, { attributes: true, attributeFilter: ['data-h18-clean-device', 'class'] });
        }
        window.addEventListener('resize', schedule, { passive: true });
        document.addEventListener('click', function (event) {
            if (event.target && event.target.closest && event.target.closest('.h18-clean-device-button,#h18-clean-wide-canvas,.h18-clean-panel-toggle')) {
                window.requestAnimationFrame(schedule);
            }
        }, true);
    }
    function install() {
        if (!ensureStage()) { return; }
        applyFit();
        installObservers();
    }

    window.H18VDViewport = {
        scale: function () { return currentScale || 1; },
        virtualWidth: function () { return currentWidth || WIDTHS.desktop; },
        unscalePx: function (pixels) { return Number(pixels || 0) / Math.max(MIN_SCALE, currentScale || 1); },
        scaledRowPx: function (rowPx) { return Number(rowPx || 0) * Math.max(MIN_SCALE, currentScale || 1); },
        refresh: schedule,
        widths: Object.assign({}, WIDTHS)
    };

    // Admin scripts are printed after the Designer markup. Prime immediately so
    // editor-v018-core measures text at the virtual frontend width on first render.
    if (document.getElementById('h18-clean-canvas')) { install(); }
    else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
'''
write('clean/hangar18-manager/assets/editor-v0144-viewport.js', viewport_js)

viewport_css = r'''/* Visual Designer Manager 0.1.44 · BUG-13 / BUG-14 */
.h18-vd-viewport-stage{
    position:relative;
    display:block;
    margin:0 auto;
    min-height:1px;
    box-sizing:border-box;
}
.h18-vd-viewport-stage>.h18-clean-root{
    position:absolute!important;
    top:0!important;
    left:0!important;
    margin:0!important;
    max-width:none!important;
    transition:none!important;
    transform-origin:0 0!important;
}
.h18-vd-viewport-status{
    display:inline-flex;
    align-items:center;
    min-height:28px;
    padding:0 8px;
    border:1px solid #c3c4c7;
    border-radius:5px;
    background:#fff;
    color:#50575e;
    font-size:12px;
    font-weight:700;
    white-space:nowrap;
}
/* Device width is owned by the virtual viewport layer, never by the editor's
   remaining physical column width. */
.h18-vd-viewport-stage>.h18-clean-root[data-h18-device="desktop"],
.h18-vd-viewport-stage>.h18-clean-root[data-h18-device="laptop"],
.h18-vd-viewport-stage>.h18-clean-root[data-h18-device="mobile"]{
    max-width:none!important;
}
/* BUG-13: Section/Box owns the physical painted box. The inner surface is only
   a transparent child-layout grid and fills the complete canonical geometry. */
.h18-clean-node--section,.h18-clean-node--container{
    background-clip:border-box!important;
}
.h18-clean-node--section>.h18-clean-inner-surface,
.h18-clean-node--container>.h18-clean-inner-surface{
    position:absolute!important;
    inset:0!important;
    width:100%!important;
    height:100%!important;
    min-height:0!important;
    margin:0!important;
    box-sizing:border-box!important;
    background:transparent!important;
    border-color:transparent!important;
    border-radius:inherit!important;
}
'''
write('clean/hangar18-manager/assets/editor-v0144.css', viewport_css)

# -----------------------------------------------------------------------------
# Core editor: scale-aware physical measurements + parent-box painting.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/assets/editor-v018-core.js'
s = read(path)
helper_anchor = "    const FONT_TOKENS = ['system','arial','verdana','tahoma','trebuchet','georgia','times','courier'];\n"
helper_insert = helper_anchor + """
    function editorScale() {
        if (window.H18VDViewport && typeof window.H18VDViewport.scale === 'function') {
            const value = parseFloat(window.H18VDViewport.scale());
            if (Number.isFinite(value) && value > 0) { return value; }
        }
        const canvas = document.getElementById('h18-clean-canvas');
        const value = canvas ? parseFloat(canvas.getAttribute('data-h18-viewport-scale') || '1') : 1;
        return Number.isFinite(value) && value > 0 ? value : 1;
    }
    function editorRowPx() { return ROW_PX * editorScale(); }
"""
s = replace_once(s, helper_anchor, helper_insert, 'core viewport helper')
s = replace_once(s,
"            const rows = Math.max(1, Math.ceil((Math.max(1, rect.height) + Math.max(0, parseInt(node.props.gapY || 0, 10) || 0)) / ROW_PX));",
"            const rows = Math.max(1, Math.ceil((Math.max(1, rect.height / editorScale()) + Math.max(0, parseInt(node.props.gapY || 0, 10) || 0)) / ROW_PX));",
'materialized leaf height')
s = replace_once(s,
"            const nextH = clamp(Math.ceil(Math.max(1, rect.height) / ROW_PX), 1, 4000);",
"            const nextH = clamp(Math.ceil(Math.max(1, rect.height) / editorRowPx()), 1, 4000);",
'auto button height')
s = replace_once(s,
"        return Math.max(MIN_SPLIT_H, Math.round(card.getBoundingClientRect().height / ROW_PX));",
"        return Math.max(MIN_SPLIT_H, Math.round(card.getBoundingClientRect().height / editorRowPx()));",
'effective rows')
s = replace_once(s,
"            const pointerRow = clamp(Math.round((event.clientY - rect.top) / ROW_PX), 0, 10000);",
"            const pointerRow = clamp(Math.round((event.clientY - rect.top) / editorRowPx()), 0, 10000);",
'floating drop row')
s = replace_once(s,
"        const startH = g.h > 0 ? g.h : Math.max(1, Math.round(rect.height / ROW_PX));",
"        const startH = g.h > 0 ? g.h : Math.max(1, Math.round(rect.height / editorRowPx()));",
'resize start height')
s = replace_once(s,
"        const dy = Math.round((event.clientY - resize.startY) / ROW_PX);",
"        const dy = Math.round((event.clientY - resize.startY) / editorRowPx());",
'resize vertical delta')
visual_anchor = "        card.setAttribute('data-gap-y', String(gapY));\n"
visual_insert = visual_anchor + """        if (PARENT_TYPES.includes(node.type)) {
            const background = /^#[0-9a-f]{6}$/i.test(String(props.background || '')) ? String(props.background).toLowerCase() : 'transparent';
            card.style.background = background;
            card.style.borderRadius = clamp(parseInt(props.radius || 0, 10) || 0, 0, 100) + 'px';
            card.setAttribute('data-h18-parent-painted-box', '1');
        }
"""
s = replace_once(s, visual_anchor, visual_insert, 'parent paint style')
old_card_content = """            try {
                card.appendChild(cardContent(node));
            } catch (error) {
                const failed = document.createElement('div');
                failed.className = 'h18-clean-render-error';
                failed.textContent = 'Elementet kunne ikke vises: ' + (error && error.message ? error.message : 'ukendt render-fejl');
                card.appendChild(failed);
                diag('node_render_error', { id: node.id, type: node.type, message: String(error && error.message || error || 'unknown') });
            }

            if (PARENT_TYPES.includes(node.type)) {"""
new_card_content = """            if (!PARENT_TYPES.includes(node.type)) {
                try {
                    card.appendChild(cardContent(node));
                } catch (error) {
                    const failed = document.createElement('div');
                    failed.className = 'h18-clean-render-error';
                    failed.textContent = 'Elementet kunne ikke vises: ' + (error && error.message ? error.message : 'ukendt render-fejl');
                    card.appendChild(failed);
                    diag('node_render_error', { id: node.id, type: node.type, message: String(error && error.message || error || 'unknown') });
                }
            }

            if (PARENT_TYPES.includes(node.type)) {"""
s = replace_once(s, old_card_content, new_card_content, 'parent chrome not in layout')
s = replace_once(s,
"                inner.style.background = p.background || 'transparent';\n                inner.style.borderRadius = (p.radius || 0) + 'px';\n                inner.style.padding = (p.padding || 0) + 'px';",
"                inner.style.background = 'transparent';\n                inner.style.borderRadius = 'inherit';\n                inner.style.padding = (p.padding || 0) + 'px';",
'inner surface transparent')
write(path, s)

# -----------------------------------------------------------------------------
# Manual image transform: physical pointer pixels -> virtual canvas pixels.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/assets/editor-v0120.js'
s = read(path)
anchor = "    function clone(value) { return JSON.parse(JSON.stringify(value)); }\n"
insert = anchor + """    function editorScale() {
        if (window.H18VDViewport && typeof window.H18VDViewport.scale === 'function') {
            var value = parseFloat(window.H18VDViewport.scale());
            if (Number.isFinite(value) && value > 0) { return value; }
        }
        return 1;
    }
"""
s = replace_once(s, anchor, insert, 'v0120 scale helper')
s = replace_once(s,
"        var box = preview.getBoundingClientRect();\n        if (box.width <= 0 || box.height <= 0) { return; }",
"        var box = preview.getBoundingClientRect();\n        var scale = editorScale();\n        var boxWidth = box.width / scale;\n        var boxHeight = box.height / scale;\n        if (boxWidth <= 0 || boxHeight <= 0) { return; }",
'manual image virtual box')
s = replace_once(s, "        if ((box.width / box.height) >= ratio) {\n            height = box.height;", "        if ((boxWidth / boxHeight) >= ratio) {\n            height = boxHeight;", 'manual image ratio')
s = replace_once(s, "            width = box.width;", "            width = boxWidth;", 'manual image width')
s = replace_once(s, "        e.manualX = Math.round((box.width - width) / 2);\n        e.manualY = Math.round((box.height - height) / 2);", "        e.manualX = Math.round((boxWidth - width) / 2);\n        e.manualY = Math.round((boxHeight - height) / 2);", 'manual image centering')
s = replace_once(s,
"        var dx = event.clientX - transform.startX;\n        var dy = event.clientY - transform.startY;",
"        var scale = editorScale();\n        var dx = (event.clientX - transform.startX) / scale;\n        var dy = (event.clientY - transform.startY) / scale;",
'manual image pointer delta')
write(path, s)

# -----------------------------------------------------------------------------
# Responsive Laptop/Mobile drag/resize must use scaled physical row height.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/assets/editor-v0121.js'
s = read(path)
anchor = "    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }\n"
insert = anchor + """    function editorScale() {
        if (window.H18VDViewport && typeof window.H18VDViewport.scale === 'function') {
            var value = parseFloat(window.H18VDViewport.scale());
            if (Number.isFinite(value) && value > 0) { return value; }
        }
        return 1;
    }
"""
s = replace_once(s, anchor, insert, 'responsive scale helper')
s = replace_once(s,
"        var dy = Math.round((event.clientY - transform.startY) / ROW_PX);",
"        var dy = Math.round((event.clientY - transform.startY) / (ROW_PX * editorScale()));",
'responsive vertical pointer delta')
write(path, s)

# -----------------------------------------------------------------------------
# Floating button move uses units/rows, not CSS pixels, so it remains correct at
# any Fit zoom.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/assets/editor-v0131.js'
s = read(path)
anchor = "    function clamp(value, min, max) {\n        return Math.max(min, Math.min(max, value));\n    }\n"
insert = anchor + """
    function editorScale() {
        if (window.H18VDViewport && typeof window.H18VDViewport.scale === 'function') {
            var value = parseFloat(window.H18VDViewport.scale());
            if (Number.isFinite(value) && value > 0) { return value; }
        }
        return 1;
    }
"""
s = replace_once(s, anchor, insert, 'floating scale helper')
new_float = r'''    function beginFloatingDrag(event, initialCard) {
        let card = selectFloatingCard(initialCard);
        if (!card || !card.isConnected) { return; }
        refreshFloatingHandles(card.parentElement || document);

        const id = cleanId(card.getAttribute('data-node-id') || '');
        const surface = card.parentElement;
        if (!id || !surface || !surface.classList.contains('h18-clean-surface')) { return; }

        const surfaceRect = surface.getBoundingClientRect();
        const cardRect = card.getBoundingClientRect();
        const startX = clamp(inspectorNumber('gx', 0), 0, UNITS - 1);
        const widthUnits = clamp(inspectorNumber('gw', Math.max(1, Math.round((cardRect.width / Math.max(1, surfaceRect.width)) * UNITS))), 1, UNITS - startX);
        const startY = Math.max(0, inspectorNumber('gy', 0));
        const unitPx = Math.max(0.1, surfaceRect.width / UNITS);

        floatingDrag = {
            pointerId: event.pointerId,
            id: id,
            card: card,
            surface: surface,
            startClientX: event.clientX,
            startClientY: event.clientY,
            startX: startX,
            startY: startY,
            unitPx: unitPx,
            widthUnits: widthUnits,
            x: startX,
            y: startY
        };
        card.classList.add('h18-v0131-floating-drag');
    }

    function moveFloatingDrag(event) {
        if (!floatingDrag || event.pointerId !== floatingDrag.pointerId) { return; }
        const drag = floatingDrag;
        if (!drag.card || !drag.card.isConnected) { floatingDrag = null; return; }
        const dxUnits = Math.round((event.clientX - drag.startClientX) / drag.unitPx);
        const dyRows = Math.round((event.clientY - drag.startClientY) / (ROW_PX * editorScale()));
        drag.x = clamp(drag.startX + dxUnits, 0, UNITS - drag.widthUnits);
        drag.y = clamp(drag.startY + dyRows, 0, 10000);
        drag.card.style.left = ((drag.x / UNITS) * 100) + '%';
        drag.card.style.top = (drag.y * ROW_PX) + 'px';
        event.preventDefault();
    }

'''
s = replace_span(s, '    function beginFloatingDrag(event, initialCard) {', '    function commitInspectorField(field, value, done) {', new_float, 'floating drag block')
write(path, s)

# -----------------------------------------------------------------------------
# Frontend parent box: do not force height:auto!important. The element itself
# owns background/radius and its min-height is max(manual, required children).
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/src/Frontend/Renderer.php'
s = read(path)
s = replace_once(s,
"        echo '.h18-clean-front-container,.h18-clean-front-section{display:grid;grid-template-columns:repeat(120,minmax(0,1fr));grid-auto-rows:' . esc_attr((string) $rowPx) . 'px;align-items:stretch;min-width:0;box-sizing:border-box;height:auto!important}';",
"        echo '.h18-clean-front-container,.h18-clean-front-section{display:grid;grid-template-columns:repeat(120,minmax(0,1fr));grid-auto-rows:' . esc_attr((string) $rowPx) . 'px;align-items:stretch;min-width:0;box-sizing:border-box;background-clip:border-box}';",
'frontend parent height override')
write(path, s)

# -----------------------------------------------------------------------------
# Model QA marker + explicit source-contract checks for BUG-13/14.
# -----------------------------------------------------------------------------
path = '.github/scripts/v0125_model_qa.php'
s = read(path)
s = replace_once(s, 'echo "Visual Designer Manager 0.1.43 model QA PASS\\\\n";', '''$viewportJs = file_get_contents(__DIR__ . '/../../clean/hangar18-manager/assets/editor-v0144-viewport.js');
$viewportCss = file_get_contents(__DIR__ . '/../../clean/hangar18-manager/assets/editor-v0144.css');
$coreJs = file_get_contents(__DIR__ . '/../../clean/hangar18-manager/assets/editor-v018-core.js');
$rendererPhp = file_get_contents(__DIR__ . '/../../clean/hangar18-manager/src/Frontend/Renderer.php');
vdAssert(is_string($viewportJs) && str_contains($viewportJs, "desktop: 1920") && str_contains($viewportJs, "laptop: 1180") && str_contains($viewportJs, "mobile: 390"), 'BUG-14 virtual viewport widths are missing.');
vdAssert(str_contains((string) $viewportJs, 'ResizeObserver') && str_contains((string) $viewportJs, 'h18-clean-wide-canvas') && str_contains((string) $viewportJs, 'h18-clean-panel-toggle'), 'BUG-14 Fit zoom is not wired to dynamic editor width changes.');
vdAssert(str_contains((string) $viewportJs, 'data-h18-viewport-scale') && str_contains((string) $coreJs, 'editorRowPx()'), 'BUG-14 scale is not consumed by core pointer geometry.');
vdAssert(str_contains((string) $coreJs, "data-h18-parent-painted-box") && str_contains((string) $coreJs, "inner.style.background = 'transparent'"), 'BUG-13 parent box does not own its background.');
vdAssert(str_contains((string) $viewportCss, 'height:100%!important') && str_contains((string) $viewportCss, 'background:transparent!important'), 'BUG-13 inner surface does not fill the parent transparently.');
vdAssert(!str_contains((string) $rendererPhp, 'height:auto!important'), 'Frontend still forces parent height:auto!important.');

echo "Visual Designer Manager 0.1.44 model QA PASS\\n";''', 'QA version and contracts')
write(path, s)

# -----------------------------------------------------------------------------
# Release history, release notes, status and technical contract.
# -----------------------------------------------------------------------------
path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(path))
entry = {
    'version': '0.1.44',
    'date': '2026-08-29',
    'items': [
        'BUG-13: Sektion/Kasse ejer nu hele sin fysiske baggrund, ramme og radius; den indre child-surface er transparent og fylder hele canonical geometri.',
        'BUG-13: manuel højde er fortsat minimumshøjde, mens indhold kan autogrow; editor-chrome tæller ikke som layoutindhold.',
        'BUG-14: Designer bruger virtuelle frontend-viewports på 1920 px Desktop, 1180 px Laptop og 390 px Mobil.',
        'BUG-14: Fit-zoom genberegnes automatisk ved Mere canvas, foldning af Elementer/Inspector og ændringer i editorbredden uden at ændre modellen.',
        'Drag/resize, floating Knap og manuel billedplacering er scale-aware, så pointerbevægelser oversættes tilbage til virtuelle pixels/8px-rækker.',
        'Theme Shell forbliver OFF; Header/Footer parity testes igen på det nye WYSIWYG-canvas.'
    ]
}
history = [row for row in history if row.get('version') != '0.1.44']
history.insert(0, entry)
write(path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write('clean-release-notes.html', '''<h4>0.1.44</h4><ul><li><strong>BUG-13:</strong> Sektion/Kasse farvelægger nu hele sin canonical geometri; child-surface er transparent og fylder hele boksen.</li><li><strong>Auto-grow:</strong> manuel højde er minimum, mens indhold fortsat kan udvide boksen.</li><li><strong>BUG-14 WYSIWYG:</strong> Designer beregner layout ved 1920 px Desktop, 1180 px Laptop og 390 px Mobil og skalerer kun visningen med Fit.</li><li><strong>Dynamisk Fit:</strong> Mere canvas, Inspector/Elementer ind/ud og resize genberegner zoom automatisk uden at flytte elementerne.</li><li><strong>Scale-aware input:</strong> drag/resize, floating Knap og manuel billedredigering bruger virtuelle koordinater under zoom.</li><li><strong>Sikkerhed:</strong> Theme Shell forbliver OFF indtil Header/Footer parity er bruger-QA PASS.</li></ul>''')

write('docs/v0144-status.md', '''# Visual Designer Manager 0.1.44 status

## Scope

- BUG-13: Section/Box physical painted geometry.
- BUG-14: virtual viewport + dynamic Fit zoom.
- Preserve 0.1.43 Header/Footer conversion and keep Theme Shell cutover OFF.

## Fixed contract

- Desktop virtual viewport: 1920 px.
- Laptop virtual viewport: 1180 px.
- Mobile virtual viewport: 390 px.
- The model is laid out at the virtual viewport width; available admin/editor width only changes Fit zoom.
- Fit is recalculated when canvas-column width changes, including More canvas and Elementer/Inspector collapse/expand.
- Pointer deltas are converted from physical screen pixels back to virtual pixels/8px rows.
- Section/Box owns background, border and radius over the full physical geometry.
- Inner child surface is transparent and fills the Section/Box; editor chrome is not physical geometry.
- Manual height remains a minimum and children may auto-grow the parent.

## QA gate

- PHP syntax.
- JavaScript syntax.
- hierarchy normalizer QA.
- canonical model QA.
- source contract checks for virtual widths, ResizeObserver Fit, scale-aware geometry and parent painted box.
- Theme Shell cutover remains explicit OFF.
''')

tech_path = 'CLEAN-TECHNICAL-MANUAL.md'
tech = read(tech_path)
section = '''\n\n## 22. WYSIWYG viewport- og containerkontrakt · 0.1.44\n\n### VD-CONTAINER-PAINT-001 · IMPLEMENTERET 0.1.44\nSektion og Kasse ejer hele deres fysiske canonical geometri. Baggrund, ramme og radius må ikke afhænge af, om child-elementer fylder højden. Den indre child-surface er transparent og fylder hele parentens geometri. Manuel højde er et minimum; required child height kan autogrow parenten. Editor-labels/handles er chrome og tæller ikke i layoutgeometrien.\n\n### VD-WYSIWYG-VIEWPORT-001 · IMPLEMENTERET 0.1.44\nDesignerens layoutbredde må aldrig være den tilfældige restbredde mellem WordPress-adminmenu, Elementer og Inspector. Layout beregnes ved en virtuel frontend-viewport: Desktop 1920 px, Laptop 1180 px og Mobil 390 px. Editorens tilgængelige plads styrer kun Fit-zoom.\n\n### VD-WYSIWYG-FIT-001 · IMPLEMENTERET 0.1.44\nFit-zoom genberegnes dynamisk ved ResizeObserver på canvas-kolonnen samt ved breakpointskift, Mere canvas og foldning af Elementer/Inspector. Ændret Fit må aldrig mutere canonical x/y/w/h eller responsive inheritance. Drag/resize og pixelbaserede editorfunktioner skal omsætte fysiske pointer-deltaer tilbage til virtuelle pixels/8px-rækker.\n'''
if '## 22. WYSIWYG viewport- og containerkontrakt · 0.1.44' not in tech:
    tech += section
write(tech_path, tech)
