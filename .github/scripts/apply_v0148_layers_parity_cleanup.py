from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / 'clean' / 'hangar18-manager'


def read(path: Path) -> str:
    return path.read_text(encoding='utf-8')


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


# ---------------------------------------------------------------------------
# Plugin version + stop legacy conversion runtime + load Layers UI.
# ---------------------------------------------------------------------------
plugin_path = PLUGIN / 'hangar18-manager.php'
plugin = read(plugin_path)
plugin = replace_once(plugin, ' * Version: 0.1.47', ' * Version: 0.1.48', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.47');", "define('H18_CLEAN_VERSION', '0.1.48');", 'plugin constant version')
plugin = replace_once(plugin, "    \\Hangar18\\Clean\\Migration\\LegacyHeaderConverter::register();\n", '', 'legacy header runtime registration')
plugin = replace_once(plugin, "    \\Hangar18\\Clean\\Migration\\LegacyFooterConverter::register();\n", '', 'legacy footer runtime registration')

style_anchor = """    wp_enqueue_style(\n        'h18-clean-editor-v0144',\n        H18_CLEAN_URL . 'assets/editor-v0144.css',\n        ['h18-clean-editor-v0135'],\n        H18_CLEAN_VERSION\n    );\n"""
style_insert = style_anchor + """    wp_enqueue_style(\n        'h18-clean-editor-v0148-layers',\n        H18_CLEAN_URL . 'assets/editor-v0148-layers.css',\n        ['h18-clean-editor-v0144'],\n        H18_CLEAN_VERSION\n    );\n"""
plugin = replace_once(plugin, style_anchor, style_insert, 'layers stylesheet enqueue')

script_anchor = """    wp_enqueue_script(\n        'h18-clean-editor-v0135',\n        H18_CLEAN_URL . 'assets/editor-v0135.js',\n        ['h18-clean-editor-v0132'],\n        H18_CLEAN_VERSION,\n        true\n    );\n"""
script_insert = script_anchor + """    wp_enqueue_script(\n        'h18-clean-editor-v0148-layers',\n        H18_CLEAN_URL . 'assets/editor-v0148-layers.js',\n        ['h18-clean-editor-v0135'],\n        H18_CLEAN_VERSION,\n        true\n    );\n"""
plugin = replace_once(plugin, script_anchor, script_insert, 'layers script enqueue')
write(plugin_path, plugin)


# ---------------------------------------------------------------------------
# Remove old Header/Footer conversion UI and POST runtime from global Designer.
# Keep migration classes/files dormant for historical QA and data compatibility.
# ---------------------------------------------------------------------------
global_path = PLUGIN / 'src' / 'Admin' / 'GlobalDesignerController.php'
global_php = read(global_path)
for old, label in [
    ("        add_action('admin_post_' . self::CONVERT_ACTION, [self::class, 'convertLegacyHeader']);\n", 'legacy header POST action'),
    ("        add_action('admin_post_' . self::FOOTER_CONVERT_ACTION, [self::class, 'convertLegacyFooter']);\n", 'legacy footer POST action'),
    ("        if ($part === 'header') { self::renderLegacyHeaderConversion(); }\n", 'legacy header panel'),
    ("        if ($part === 'footer') { self::renderLegacyFooterConversion(); }\n", 'legacy footer panel'),
]:
    global_php = replace_once(global_php, old, '', label)
write(global_path, global_php)


# ---------------------------------------------------------------------------
# BUG-17: local Header/Footer preview must not blank canonical leaf borders.
# ---------------------------------------------------------------------------
preview_css_path = PLUGIN / 'assets' / 'global-designer-v0123.css'
preview_css = read(preview_css_path)
preview_css = replace_once(
    preview_css,
    '.vd-global-preview-canvas .h18-clean-node:not([data-h18-parent-painted-box="1"]){background:transparent!important;border-color:transparent!important}\n',
    '',
    'local preview blanket border reset',
)
write(preview_css_path, preview_css)


# ---------------------------------------------------------------------------
# BUG-17: frontend Button paints border/radius on the visible clickable surface.
# Geometry/spacing remain on the wrapper.
# ---------------------------------------------------------------------------
renderer_path = PLUGIN / 'src' / 'Frontend' / 'Renderer.php'
renderer = read(renderer_path)
old_button = """            $buttonStyle = $layoutStyle . $borderStyle . $spacingStyle . $radiusStyle\n                . '--h18-btn-bg:' . $background . ';--h18-btn-color:' . $textColor . ';--h18-btn-hover-bg:' . $hoverBackground . ';--h18-btn-hover-color:' . $hoverTextColor . ';--h18-btn-focus:' . $focusColor . ';padding:0;overflow:visible;';\n            $linkStyle = 'border-radius:' . $radius . 'px;padding:' . $paddingY . 'px ' . $paddingX . 'px;';\n"""
new_button = """            $buttonStyle = $layoutStyle . $spacingStyle\n                . '--h18-btn-bg:' . $background . ';--h18-btn-color:' . $textColor . ';--h18-btn-hover-bg:' . $hoverBackground . ';--h18-btn-hover-color:' . $hoverTextColor . ';--h18-btn-focus:' . $focusColor . ';padding:0;overflow:visible;';\n            $linkStyle = $borderStyle . $radiusStyle . 'padding:' . $paddingY . 'px ' . $paddingX . 'px;';\n"""
renderer = replace_once(renderer, old_button, new_button, 'frontend button paint surface')
write(renderer_path, renderer)


# ---------------------------------------------------------------------------
# Layers/Object tree: inserted into the existing palette at runtime so it works
# for both Page Designer and Header/Footer Designer without duplicating markup.
# ---------------------------------------------------------------------------
layers_js = r"""(function () {
    'use strict';

    const TYPE_NAMES = {
        section: 'Sektion',
        container: 'Kasse',
        text: 'Tekst',
        image: 'Billede',
        button: 'Knap',
        menu: 'Menu'
    };
    const collapsed = new Set();
    let scheduled = false;

    function qsa(root, selector) {
        return Array.prototype.slice.call(root.querySelectorAll(selector));
    }

    function directParentCard(card, canvas) {
        let current = card.parentElement;
        while (current && current !== canvas) {
            if (current.classList && current.classList.contains('h18-clean-node') && current.hasAttribute('data-node-id')) {
                return current;
            }
            current = current.parentElement;
        }
        return null;
    }

    function nodeType(card) {
        const match = Array.from(card.classList).find(function (name) { return name.indexOf('h18-clean-node--') === 0; });
        return match ? match.replace('h18-clean-node--', '') : 'element';
    }

    function previewLabel(card, type) {
        let text = '';
        if (type === 'button') {
            const el = card.querySelector('.h18-clean-button-preview');
            text = el ? el.textContent : '';
        } else if (type === 'text') {
            const el = card.querySelector('.h18-clean-text-body,.h18-clean-text-preview,.h18-clean-node-preview--text');
            text = el ? el.textContent : '';
        } else if (type === 'menu') {
            const el = card.querySelector('.h18-clean-menu-preview,.h18-clean-node-preview--menu');
            text = el ? el.textContent : '';
        } else if (type === 'image') {
            const img = card.querySelector('img');
            text = img ? (img.getAttribute('alt') || '') : '';
        }
        text = String(text || '').replace(/\s+/g, ' ').trim();
        if (text.length > 34) { text = text.slice(0, 31) + '…'; }
        return text;
    }

    function layerLabel(card) {
        const type = nodeType(card);
        const id = card.getAttribute('data-node-id') || '';
        const extra = previewLabel(card, type);
        return (TYPE_NAMES[type] || type) + (extra ? ' · ' + extra : '') + ' · ' + id.slice(-8);
    }

    function selectCard(canvas, id) {
        const card = canvas.querySelector('.h18-clean-node[data-node-id="' + CSS.escape(id) + '"]');
        if (!card) { return; }
        card.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
        try { card.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' }); } catch (ignore) {}
    }

    function buildTree(host, canvas) {
        if (!host || !canvas) { return; }
        const cards = qsa(canvas, '.h18-clean-node[data-node-id]');
        const children = new Map();
        cards.forEach(function (card) {
            const parent = directParentCard(card, canvas);
            const parentId = parent ? (parent.getAttribute('data-node-id') || '') : '';
            if (!children.has(parentId)) { children.set(parentId, []); }
            children.get(parentId).push(card);
        });

        host.innerHTML = '';
        if (!cards.length) {
            host.innerHTML = '<p class="description">Ingen elementer endnu.</p>';
            return;
        }

        function appendLevel(parentId, parentEl, depth) {
            const list = children.get(parentId) || [];
            list.forEach(function (card) {
                const id = card.getAttribute('data-node-id') || '';
                const hasChildren = (children.get(id) || []).length > 0;
                const item = document.createElement('div');
                item.className = 'h18-vd-layer-item' + (card.classList.contains('is-selected') ? ' is-selected' : '');
                item.style.setProperty('--h18-layer-depth', String(depth));

                const disclosure = document.createElement('button');
                disclosure.type = 'button';
                disclosure.className = 'h18-vd-layer-disclosure';
                disclosure.disabled = !hasChildren;
                disclosure.setAttribute('aria-label', hasChildren ? 'Fold lag ind eller ud' : 'Intet underlag');
                disclosure.textContent = hasChildren ? (collapsed.has(id) ? '▸' : '▾') : '·';
                disclosure.addEventListener('click', function (event) {
                    event.stopPropagation();
                    if (!hasChildren) { return; }
                    if (collapsed.has(id)) { collapsed.delete(id); } else { collapsed.add(id); }
                    buildTree(host, canvas);
                });

                const pick = document.createElement('button');
                pick.type = 'button';
                pick.className = 'h18-vd-layer-pick';
                pick.textContent = layerLabel(card);
                pick.title = 'Vælg element på canvas';
                pick.addEventListener('click', function () {
                    selectCard(canvas, id);
                    window.setTimeout(function () { buildTree(host, canvas); }, 0);
                });

                item.appendChild(disclosure);
                item.appendChild(pick);
                parentEl.appendChild(item);

                if (hasChildren && !collapsed.has(id)) {
                    appendLevel(id, parentEl, depth + 1);
                }
            });
        }

        appendLevel('', host, 0);
    }

    function activate(palette, name) {
        qsa(palette, '[data-h18-left-tab]').forEach(function (button) {
            const active = button.getAttribute('data-h18-left-tab') === name;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-selected', active ? 'true' : 'false');
        });
        qsa(palette, '[data-h18-left-panel]').forEach(function (panel) {
            panel.hidden = panel.getAttribute('data-h18-left-panel') !== name;
        });
        if (name === 'layers') {
            const canvas = document.getElementById('h18-clean-canvas');
            buildTree(palette.querySelector('.h18-vd-layers-tree'), canvas);
        }
    }

    function installPalette(palette) {
        if (!palette || palette.dataset.h18LayersInstalled === '1') { return; }
        palette.dataset.h18LayersInstalled = '1';

        const existing = Array.prototype.slice.call(palette.childNodes);
        const tabs = document.createElement('div');
        tabs.className = 'h18-vd-left-tabs';
        tabs.setAttribute('role', 'tablist');
        tabs.innerHTML = '<button type="button" role="tab" class="is-active" data-h18-left-tab="elements" aria-selected="true">Elementer</button>'
            + '<button type="button" role="tab" data-h18-left-tab="layers" aria-selected="false">Lag</button>';

        const elements = document.createElement('div');
        elements.className = 'h18-vd-left-panel';
        elements.setAttribute('data-h18-left-panel', 'elements');
        existing.forEach(function (node) { elements.appendChild(node); });

        const layers = document.createElement('div');
        layers.className = 'h18-vd-left-panel h18-vd-left-panel--layers';
        layers.setAttribute('data-h18-left-panel', 'layers');
        layers.hidden = true;
        layers.innerHTML = '<p class="description">Vælg et element i hierarkiet, også når det er dækket af et andet element.</p><div class="h18-vd-layers-tree"></div>';

        palette.appendChild(tabs);
        palette.appendChild(elements);
        palette.appendChild(layers);

        tabs.addEventListener('click', function (event) {
            const button = event.target.closest('[data-h18-left-tab]');
            if (!button) { return; }
            activate(palette, button.getAttribute('data-h18-left-tab') || 'elements');
        });

        const canvas = document.getElementById('h18-clean-canvas');
        if (canvas && window.MutationObserver) {
            const observer = new MutationObserver(function () {
                if (scheduled) { return; }
                scheduled = true;
                window.requestAnimationFrame(function () {
                    scheduled = false;
                    const layerPanel = palette.querySelector('[data-h18-left-panel="layers"]');
                    if (layerPanel && !layerPanel.hidden) { buildTree(palette.querySelector('.h18-vd-layers-tree'), canvas); }
                });
            });
            observer.observe(canvas, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] });
        }
    }

    function install() {
        qsa(document, '.h18-clean-palette').forEach(installPalette);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
})();
"""
write(PLUGIN / 'assets' / 'editor-v0148-layers.js', layers_js)

layers_css = r"""/* Visual Designer Manager 0.1.48 - Elementer/Lag */
.h18-vd-left-tabs{display:grid;grid-template-columns:1fr 1fr;gap:4px;margin:0 0 10px}
.h18-vd-left-tabs button{appearance:none;border:1px solid #c3c4c7;background:#f6f7f7;color:#1d2327;border-radius:3px;padding:7px 6px;font-weight:600;cursor:pointer}
.h18-vd-left-tabs button.is-active{background:#2271b1;border-color:#2271b1;color:#fff}
.h18-vd-left-panel[hidden]{display:none!important}
.h18-vd-left-panel--layers{min-width:0}
.h18-vd-layers-tree{display:flex;flex-direction:column;gap:2px;max-height:calc(100vh - 260px);overflow:auto;padding:2px 0 12px}
.h18-vd-layer-item{display:grid;grid-template-columns:22px minmax(0,1fr);align-items:center;padding-left:calc(var(--h18-layer-depth,0) * 12px);border-radius:3px}
.h18-vd-layer-item.is-selected{background:#e7f5eb;box-shadow:inset 3px 0 #00a32a}
.h18-vd-layer-disclosure,.h18-vd-layer-pick{appearance:none;border:0;background:transparent;color:#1d2327;min-height:30px;cursor:pointer}
.h18-vd-layer-disclosure{padding:0;text-align:center;font-size:14px}
.h18-vd-layer-disclosure:disabled{cursor:default;color:#8c8f94}
.h18-vd-layer-pick{padding:4px 6px;text-align:left;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px}
.h18-vd-layer-pick:hover,.h18-vd-layer-pick:focus-visible{background:#f0f6fc;outline:1px solid #72aee6}
"""
write(PLUGIN / 'assets' / 'editor-v0148-layers.css', layers_css)


# ---------------------------------------------------------------------------
# Visible theme rename: keep folder, text-domain and compatibility slug stable.
# Bump theme version so the existing updater can deliver the visible rename.
# ---------------------------------------------------------------------------
theme_style_path = ROOT / 'theme' / 'legacy-v1.2.0' / 'style.css'
theme_style = read(theme_style_path)
theme_style = replace_once(theme_style, 'Theme Name: Hangar18 Base Theme', 'Theme Name: AKVPK', 'theme visible name')
theme_style = replace_once(theme_style, 'Author: Hangar18', 'Author: AKVPK', 'theme visible author')
theme_style = replace_once(
    theme_style,
    'Description: Minimalt WordPress-basistema til Hangar18. Hangar18 Manager styrer header, menu, footer og de administrerede sider.',
    'Description: Minimalt WordPress-basistema til AKVPK. Visual Designer Manager styrer Header, Menu, Footer og de administrerede sider.',
    'theme visible description',
)
theme_style = replace_once(theme_style, 'Version: 1.2.0', 'Version: 1.2.1', 'theme version')
write(theme_style_path, theme_style)

# Manifest SHA is filled by the apply workflow after packaging.
theme_update_path = ROOT / 'theme-update.json'
theme_update = json.loads(read(theme_update_path))
theme_update['version'] = '1.2.1'
theme_update['last_updated'] = '2026-08-29T18:00:00Z'
theme_update['changelog'] = '<h4>AKVPK 1.2.1</h4><ul><li>Det synlige WordPress-temanavn er ændret fra Hangar18 Base Theme til AKVPK.</li><li>Teknisk theme-slug, mappe og Text Domain bevares for kompatibilitet.</li><li>Ingen layout- eller Theme Shell-cutover ændringer.</li></ul>'
write(theme_update_path, json.dumps(theme_update, ensure_ascii=False, indent=2) + '\n')


# ---------------------------------------------------------------------------
# Release notes/history/status. Menu remains the next UX workstream after Footer.
# ---------------------------------------------------------------------------
history_path = PLUGIN / 'release-history.json'
history = json.loads(read(history_path))
if not history or history[0].get('version') != '0.1.48':
    history.insert(0, {
        'version': '0.1.48',
        'date': '2026-08-29',
        'items': [
            'Ny Elementer/Lag-fane viser det fysiske hierarki og kan vælge dækkede eller fuldt overlappede elementer direkte fra lagtræet.',
            'BUG-17: Button-ramme/radius males på den synlige klikflade på frontend, og lokal Header/Footer-preview skjuler ikke længere canonical elementrammer.',
            'Legacy Header/Footer-konverteringspaneler og deres POST/automatisk runtime er fjernet; eksisterende templates og versionshistorik bevares.',
            'Canvas starter fortsat i Fit og BUG-02 multiline rich-text selection forbliver release-gated fra 0.1.47.',
            'Det synlige WordPress-temanavn bliver AKVPK 1.2.1; teknisk hangar18-base kompatibilitet bevares.',
            'Theme Shell forbliver OFF; Menu er fortsat næste hovedspor efter Footer-parity.'
        ]
    })
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes = '''<h4>0.1.48 – Lag, Button parity og oprydning</h4>
<ul>
<li>Ny <strong>Elementer | Lag</strong>-fane i venstre panel. Lag viser Sektion/Kasse/leaf-hierarkiet og kan vælge et element, selv når et andet element dækker det 100%.</li>
<li><strong>BUG-17:</strong> Knapramme og radius gengives på den synlige klikflade på frontend, og Header/Footer-preview nulstiller ikke længere canonical rammefarver.</li>
<li>Den gamle Header/Footer-konverteringsbrugerflade og converter-runtime er fjernet. Eksisterende Header/Footer-modeller, valg og historik ændres ikke.</li>
<li>Canvas starter fortsat i <strong>Fit</strong>; manuel zoom er kun sessionsadfærd. BUG-02 multiline selection fra 0.1.47 beholdes som release-gate.</li>
<li>WordPress-temaets synlige navn bliver <strong>AKVPK</strong> i theme 1.2.1. Slug/mappe/Text Domain forbliver <code>hangar18-base</code> af kompatibilitetshensyn.</li>
<li>Theme Shell er fortsat OFF. Menu-UX ændres ikke i denne release.</li>
</ul>
'''
write(ROOT / 'clean-release-notes.html', notes)

status = '''# Visual Designer Manager 0.1.48 status

Dato: 2026-08-29

## Scope

- Elementer/Lag-viser i både Side Designer og Header/Footer Designer.
- BUG-17 Button border parity i lokal template-preview og canonical frontend-renderer.
- Legacy Header/Footer converter UI/runtime fjernet uden ændring af eksisterende template-data/historik.
- Fit-start og BUG-02 multiline selection regression-gated fra 0.1.47.
- Synligt tema omdøbt til AKVPK 1.2.1 med teknisk `hangar18-base` kompatibilitet bevaret.
- Theme Shell forbliver OFF.
- Menu-UX forbliver næste hovedspor efter Footer-parity.
'''
write(ROOT / 'docs' / 'v0148-status.md', status)

manual_path = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
manual = read(manual_path)
marker = '## 0.1.48 – Lag, parity og legacy-oprydning'
if marker not in manual:
    manual += '''\n\n## 0.1.48 – Lag, parity og legacy-oprydning\n\n- Venstre Designer-panel har `Elementer | Lag`; Lag-træet er editor-chrome og ændrer aldrig canonical modellen.\n- Klik på et Lag vælger den tilsvarende canvas-node, også når den er fysisk dækket af en anden node.\n- Button border/background/radius skal males på samme synlige surface i Designer, lokal Preview og frontend.\n- Legacy Header/Footer converter UI og automatisk runtime er retired; historiske klasser må kun eksistere dormant for QA/data-kompatibilitet.\n- Editor entry og breakpointskift starter i Fit.\n- Theme Shell er fortsat OFF.\n- Synligt theme-navn er AKVPK; intern `hangar18-base` slug/Text Domain bevares.\n'''
write(manual_path, manual)

print('Visual Designer Manager 0.1.48 patch applied.')
