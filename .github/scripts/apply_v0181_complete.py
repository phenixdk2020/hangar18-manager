from pathlib import Path
import json
import re

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


# -----------------------------------------------------------------------------
# Version + dynamic theme palette + v0.1.81 assets
# -----------------------------------------------------------------------------
plugin_path = 'clean/hangar18-manager/hangar18-manager.php'
plugin = read(plugin_path)
plugin = replace_once(plugin, 'Version: 0.1.80', 'Version: 0.1.81', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.80');", "define('H18_CLEAN_VERSION', '0.1.81');", 'runtime version')

palette_anchor = "    wp_enqueue_script(\n        'h18-clean-editor-v0144-viewport',"
palette_block = r'''    /* v0.1.81: collect an active theme/Designer palette without restricting free color choice. */
    $themePalette = [];
    $collectPaletteColor = static function ($value) use (&$themePalette): void {
        if (!is_scalar($value)) { return; }
        $hex = sanitize_hex_color((string) $value);
        if (!is_string($hex) || $hex === '') { return; }
        $hex = strtolower($hex);
        if (strlen($hex) === 4) {
            $hex = '#' . $hex[1] . $hex[1] . $hex[2] . $hex[2] . $hex[3] . $hex[3];
        }
        if (!in_array($hex, $themePalette, true)) { $themePalette[] = $hex; }
    };
    $collectPaletteTree = null;
    $collectPaletteTree = static function ($value) use (&$collectPaletteTree, $collectPaletteColor): void {
        if (is_array($value)) {
            if (isset($value['color'])) { $collectPaletteColor($value['color']); }
            foreach ($value as $child) { $collectPaletteTree($child); }
            return;
        }
        $collectPaletteColor($value);
    };
    if (function_exists('wp_get_global_settings')) {
        foreach (['theme', 'custom', 'default'] as $origin) {
            $candidate = wp_get_global_settings(['color', 'palette', $origin]);
            if (is_array($candidate)) { $collectPaletteTree($candidate); }
        }
    }
    $themeMods = get_theme_mods();
    if (is_array($themeMods)) { $collectPaletteTree($themeMods); }
    $collectPaletteTree($model);
    $themePalette = array_slice(array_values(array_unique($themePalette)), 0, 24);

'''
if 'v0.1.81: collect an active theme/Designer palette' not in plugin:
    plugin = replace_once(plugin, palette_anchor, palette_block + palette_anchor, 'palette insertion')

plugin = replace_once(
    plugin,
    "        'contextLabel' => $contextLabel,\n        'iconLibrary' =>",
    "        'contextLabel' => $contextLabel,\n        'themePalette' => $themePalette,\n        'iconLibrary' =>",
    'palette localization'
)

style_anchor = "    wp_enqueue_style(\n        'h18-clean-editor-v016',"
style_insert = "    wp_enqueue_style('wp-color-picker');\n    wp_enqueue_style(\n        'h18-clean-editor-v0181',\n        H18_CLEAN_URL . 'assets/editor-v0181.css',\n        ['h18-clean-editor-v0166-foundation', 'wp-color-picker'],\n        H18_CLEAN_VERSION\n    );\n"
# Must be enqueued after foundation, not before it. Insert after the foundation block instead.
foundation_block = "    wp_enqueue_style(\n        'h18-clean-editor-v0166-foundation',\n        H18_CLEAN_URL . 'assets/editor-v0166-foundation.css',\n        ['h18-clean-editor-v0165-elements'],\n        H18_CLEAN_VERSION\n    );\n"
if "'h18-clean-editor-v0181'" not in plugin:
    plugin = replace_once(plugin, foundation_block, foundation_block + "    wp_enqueue_style('wp-color-picker');\n    wp_enqueue_style(\n        'h18-clean-editor-v0181',\n        H18_CLEAN_URL . 'assets/editor-v0181.css',\n        ['h18-clean-editor-v0166-foundation', 'wp-color-picker'],\n        H18_CLEAN_VERSION\n    );\n", 'v0181 style enqueue')

script_tail = "    wp_enqueue_script(\n        'h18-clean-editor-v0169-canvas-height',\n        H18_CLEAN_URL . 'assets/editor-v0169-canvas-height.js',\n        ['h18-clean-editor-v0148-layers'],\n        H18_CLEAN_VERSION,\n        true\n    );\n"
if "'h18-clean-editor-v0181-color-picker'" not in plugin:
    plugin = replace_once(plugin, script_tail, script_tail + "    wp_enqueue_script(\n        'h18-clean-editor-v0181-color-picker',\n        H18_CLEAN_URL . 'assets/editor-v0181-color-picker.js',\n        ['jquery', 'wp-color-picker', 'h18-clean-editor-v0169-canvas-height'],\n        H18_CLEAN_VERSION,\n        true\n    );\n", 'v0181 script enqueue')
write(plugin_path, plugin)


# -----------------------------------------------------------------------------
# Admin status: Sider + Eventfelter are ready
# -----------------------------------------------------------------------------
status_path = 'clean/hangar18-manager/assets/admin-v0123.js'
status = read(status_path)
status = status.replace("'h18-clean-pages': ['Under udvikling', 'partial']", "'h18-clean-pages': ['Klar', 'ready']")
if "'h18-clean-event-fields': ['Klar', 'ready']" not in status:
    status = replace_once(status, "'h18-clean-events': ['Klar', 'ready'],", "'h18-clean-events': ['Klar', 'ready'],\n        'h18-clean-event-fields': ['Klar', 'ready'],", 'event fields status')
write(status_path, status)


# -----------------------------------------------------------------------------
# Core Designer: real form structure in preview + color commit guard
# -----------------------------------------------------------------------------
core_path = 'clean/hangar18-manager/assets/editor-v018-core.js'
core = read(core_path)

preview_start = "        } else if (node.type === 'contactform' || node.type === 'membershipform') {\n            wrap.classList.add('h18-clean-node-preview--form');"
start = core.find(preview_start)
if start < 0:
    raise SystemExit('form preview start anchor not found')
end_marker = "        } else if (node.type === 'image') {"
end = core.find(end_marker, start)
if end < 0:
    raise SystemExit('form preview end anchor not found')

new_form_preview = r'''        } else if (node.type === 'contactform' || node.type === 'membershipform') {
            wrap.classList.add('h18-clean-node-preview--form');
            const membership = node.type === 'membershipform';
            const box = document.createElement('div'); box.className = 'h18-vd-form-preview h18-vd-form-preview--' + node.type;
            box.style.background = node.props.background || '#f4f1e8';
            box.style.color = node.props.textColor || '#30382a';
            box.style.padding = String(node.props.padding || 24) + 'px';
            box.style.borderRadius = String(node.props.radius || 6) + 'px';
            box.style.setProperty('--h18-form-preview-field-bg', node.props.fieldBackground || '#ffffff');
            box.style.setProperty('--h18-form-preview-accent', node.props.accentColor || '#30382a');

            const heading = document.createElement('h2');
            heading.textContent = String(node.props.heading || (membership ? 'Bliv medlem' : 'Kontakt os'));
            if (heading.textContent) { box.appendChild(heading); }
            const intro = document.createElement('p'); intro.className = 'h18-vd-form-preview-intro';
            intro.textContent = String(node.props.intro || ''); if (intro.textContent) { box.appendChild(intro); }

            const form = document.createElement('div'); form.className = 'h18-vd-form-preview-body';
            const grid = document.createElement('div'); grid.className = 'h18-vd-form-preview-grid';
            const addField = function (labelText, kind, wide) {
                const field = document.createElement('label'); field.className = 'h18-vd-form-preview-field' + (wide ? ' is-wide' : '');
                const label = document.createElement('span'); label.textContent = labelText; field.appendChild(label);
                const control = kind === 'textarea' ? document.createElement('textarea') : document.createElement('input');
                if (kind !== 'textarea') { control.type = kind || 'text'; }
                else { control.rows = 5; }
                control.disabled = true; control.tabIndex = -1; control.setAttribute('aria-hidden', 'true');
                field.appendChild(control); grid.appendChild(field);
            };
            addField('Navn *', 'text', false);
            addField('E-mail *', 'email', false);
            if (membership || node.props.showPhone !== false) { addField('Telefon' + (membership ? ' *' : ''), 'tel', false); }
            if (membership) {
                addField('Adresse *', 'text', false);
                addField('Postnr. *', 'text', false);
                addField('By *', 'text', false);
                addField('Kommentar', 'textarea', true);
            } else {
                addField('Emne *', 'text', false);
                addField('Besked *', 'textarea', true);
            }
            form.appendChild(grid);
            if (node.props.requireConsent !== false) {
                const consent = document.createElement('label'); consent.className = 'h18-vd-form-preview-consent';
                const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.disabled = true; checkbox.tabIndex = -1;
                const consentText = document.createElement('span'); consentText.textContent = 'Jeg accepterer, at oplysningerne bruges til at besvare min henvendelse.';
                consent.appendChild(checkbox); consent.appendChild(consentText); form.appendChild(consent);
            }
            const submit = document.createElement('button'); submit.type = 'button'; submit.disabled = true; submit.className = 'h18-vd-form-preview-submit';
            submit.textContent = String(node.props.buttonText || (membership ? 'Send indmeldelse' : 'Send besked'));
            form.appendChild(submit); box.appendChild(form); wrap.appendChild(box);
'''
core = core[:start] + new_form_preview + core[end:]

change_anchor = "        host.querySelectorAll('[data-field]').forEach(function (control) {\n            control.addEventListener('change', function () {\n                const current = nodeById(selectedId);"
change_new = "        host.querySelectorAll('[data-field]').forEach(function (control) {\n            control.addEventListener('change', function () {\n                if (control.getAttribute('data-h18-vd-color-managed') === '1' && control.getAttribute('data-h18-vd-color-commit') !== '1') { return; }\n                if (control.getAttribute('data-h18-vd-color-commit') === '1') { control.removeAttribute('data-h18-vd-color-commit'); }\n                const current = nodeById(selectedId);"
if 'data-h18-vd-color-managed' not in core:
    core = replace_once(core, change_anchor, change_new, 'color commit guard')
write(core_path, core)


# -----------------------------------------------------------------------------
# Unified web color picker using WordPress Iris/wpColorPicker.
# Existing color inputs stay canonical; changes commit only on Apply.
# -----------------------------------------------------------------------------
color_js = r'''(function ($) {
    'use strict';

    const CFG = window.H18CleanEditor || {};
    const RECENT_KEY = 'h18-vd-recent-colors-v1';
    const MAX_RECENT = 8;

    function normalize(value) {
        value = String(value || '').trim().toLowerCase();
        if (/^#[0-9a-f]{3}$/.test(value)) {
            return '#' + value[1] + value[1] + value[2] + value[2] + value[3] + value[3];
        }
        return /^#[0-9a-f]{6}$/.test(value) ? value : '';
    }

    function themePalette() {
        const list = Array.isArray(CFG.themePalette) ? CFG.themePalette : [];
        return list.map(normalize).filter(Boolean).filter(function (value, index, source) { return source.indexOf(value) === index; }).slice(0, 24);
    }

    function recentColors() {
        try {
            const list = JSON.parse(window.localStorage.getItem(RECENT_KEY) || '[]');
            return Array.isArray(list) ? list.map(normalize).filter(Boolean).slice(0, MAX_RECENT) : [];
        } catch (error) { return []; }
    }

    function remember(value) {
        value = normalize(value); if (!value) { return; }
        const next = [value].concat(recentColors().filter(function (item) { return item !== value; })).slice(0, MAX_RECENT);
        try { window.localStorage.setItem(RECENT_KEY, JSON.stringify(next)); } catch (error) {}
    }

    function commit(input, value) {
        value = normalize(value); if (!value) { return; }
        input.value = value;
        input.setAttribute('data-h18-vd-color-commit', '1');
        input.dispatchEvent(new Event('change', { bubbles: true }));
    }

    function closePicker(input) {
        const container = input.closest('.wp-picker-container');
        if (!container) { return; }
        const holder = container.querySelector('.wp-picker-holder');
        if (holder) { holder.style.display = 'none'; }
        const button = container.querySelector('.wp-color-result');
        if (button) { button.classList.remove('wp-picker-open'); button.setAttribute('aria-expanded', 'false'); }
    }

    function swatchRow(input, title, colors, className) {
        if (!colors.length) { return null; }
        const row = document.createElement('div'); row.className = 'h18-vd-color-shortcuts ' + className;
        const label = document.createElement('strong'); label.textContent = title; row.appendChild(label);
        const buttons = document.createElement('div'); buttons.className = 'h18-vd-color-shortcut-list';
        colors.forEach(function (color) {
            const button = document.createElement('button'); button.type = 'button'; button.className = 'h18-vd-color-shortcut';
            button.style.backgroundColor = color; button.title = title + ': ' + color; button.setAttribute('aria-label', title + ' ' + color);
            button.addEventListener('click', function () { $(input).wpColorPicker('color', color); input.value = color; });
            buttons.appendChild(button);
        });
        row.appendChild(buttons); return row;
    }

    function addChrome(input) {
        const container = input.closest('.wp-picker-container');
        if (!container || container.querySelector('.h18-vd-color-picker-extra')) { return; }
        const holder = container.querySelector('.wp-picker-holder');
        if (!holder) { return; }
        const extra = document.createElement('div'); extra.className = 'h18-vd-color-picker-extra';
        const theme = swatchRow(input, 'Temafarver', themePalette(), 'is-theme'); if (theme) { extra.appendChild(theme); }
        const recent = swatchRow(input, 'Senest brugt', recentColors(), 'is-recent'); if (recent) { extra.appendChild(recent); }
        const note = document.createElement('p'); note.className = 'description h18-vd-color-note'; note.textContent = 'Temafarver er genveje. Du kan stadig vælge enhver farve eller skrive HEX-koden direkte.'; extra.appendChild(note);
        const actions = document.createElement('div'); actions.className = 'h18-vd-color-actions';
        const cancel = document.createElement('button'); cancel.type = 'button'; cancel.className = 'button'; cancel.textContent = 'Annuller';
        const apply = document.createElement('button'); apply.type = 'button'; apply.className = 'button button-primary'; apply.textContent = 'Anvend';
        cancel.addEventListener('click', function () {
            const original = normalize(input.getAttribute('data-h18-vd-color-original')) || '#000000';
            $(input).wpColorPicker('color', original); input.value = original; closePicker(input);
        });
        apply.addEventListener('click', function () {
            const value = normalize(input.value); if (!value) { return; }
            remember(value); commit(input, value);
        });
        actions.appendChild(cancel); actions.appendChild(apply); extra.appendChild(actions);
        holder.appendChild(extra);

        const result = container.querySelector('.wp-color-result');
        if (result) {
            result.addEventListener('click', function () {
                input.setAttribute('data-h18-vd-color-original', normalize(input.value) || '#000000');
                window.setTimeout(function () {
                    const oldRecent = extra.querySelector('.h18-vd-color-shortcuts.is-recent'); if (oldRecent) { oldRecent.remove(); }
                    const newRecent = swatchRow(input, 'Senest brugt', recentColors(), 'is-recent');
                    if (newRecent) { const noteNode = extra.querySelector('.h18-vd-color-note'); extra.insertBefore(newRecent, noteNode); }
                }, 0);
            });
        }
    }

    function enhance(input) {
        if (!(input instanceof HTMLInputElement) || input.getAttribute('data-h18-vd-color-managed') === '1') { return; }
        if (!window.jQuery || !$.fn || typeof $.fn.wpColorPicker !== 'function') { return; }
        const value = normalize(input.value) || '#000000';
        input.setAttribute('data-h18-vd-color-managed', '1');
        input.setAttribute('data-h18-vd-color-original', value);
        input.type = 'text'; input.value = value; input.classList.add('h18-vd-color-source');
        $(input).wpColorPicker({
            defaultColor: value,
            clear: false,
            palettes: themePalette().length ? themePalette() : true,
            change: function (event, ui) {
                if (ui && ui.color) { input.value = normalize(ui.color.toString()) || input.value; }
            }
        });
        addChrome(input);
    }

    function scan(root) {
        const scope = root && root.querySelectorAll ? root : document;
        scope.querySelectorAll('input[type="color"][data-field], input[type="color"]#h18-vd-table-pen-color').forEach(enhance);
    }

    function init() {
        scan(document);
        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                mutation.addedNodes.forEach(function (node) {
                    if (!(node instanceof Element)) { return; }
                    if (node.matches && node.matches('input[type="color"][data-field], input[type="color"]#h18-vd-table-pen-color')) { enhance(node); }
                    scan(node);
                });
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
        document.addEventListener('keydown', function (event) {
            if (event.key !== 'Escape') { return; }
            document.querySelectorAll('.h18-vd-color-source[data-h18-vd-color-original]').forEach(function (input) {
                const container = input.closest('.wp-picker-container');
                if (!container || !container.querySelector('.wp-picker-open')) { return; }
                const original = normalize(input.getAttribute('data-h18-vd-color-original')) || '#000000';
                $(input).wpColorPicker('color', original); input.value = original; closePicker(input);
            });
        });
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', init); } else { init(); }
})(jQuery);
'''
write('clean/hangar18-manager/assets/editor-v0181-color-picker.js', color_js)

color_css = r'''/* Visual Designer Manager v0.1.81: unified color picker + form WYSIWYG parity. */
.h18-clean-inspector .wp-picker-container{display:block;margin-top:4px}
.h18-clean-inspector .wp-picker-container .wp-color-result.button{margin:0;min-height:32px}
.h18-clean-inspector .wp-picker-container .wp-color-result-text{min-width:78px;text-transform:uppercase;font-family:ui-monospace,SFMono-Regular,Consolas,monospace}
.h18-clean-inspector .wp-picker-input-wrap{display:inline-flex;gap:6px;align-items:center}
.h18-clean-inspector .wp-picker-input-wrap input.h18-vd-color-source{width:96px!important;font-family:ui-monospace,SFMono-Regular,Consolas,monospace;text-transform:uppercase}
.h18-clean-inspector .wp-picker-holder{position:relative;z-index:1000;max-width:320px}
.h18-vd-color-picker-extra{box-sizing:border-box;width:255px;max-width:100%;padding:9px 0 0}
.h18-vd-color-shortcuts{margin:0 0 9px}
.h18-vd-color-shortcuts>strong{display:block;margin-bottom:5px;font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#50575e}
.h18-vd-color-shortcut-list{display:flex;flex-wrap:wrap;gap:5px}
.h18-vd-color-shortcut{width:24px;height:24px;border:1px solid #8c8f94;border-radius:3px;padding:0;cursor:pointer;box-shadow:inset 0 0 0 1px rgba(255,255,255,.35)}
.h18-vd-color-shortcut:focus-visible{outline:2px solid #2271b1;outline-offset:2px}
.h18-vd-color-note{margin:7px 0 9px!important;font-size:11px!important;line-height:1.35!important}
.h18-vd-color-actions{display:flex;justify-content:flex-end;gap:7px;padding-top:8px;border-top:1px solid #dcdcde}

.h18-clean-node-preview--form{overflow:auto!important}
.h18-vd-form-preview{box-sizing:border-box;width:100%;min-height:100%;font-family:system-ui,-apple-system,"Segoe UI",sans-serif;text-align:left}
.h18-vd-form-preview h2{margin:0 0 8px!important;padding:0!important;color:inherit;font:700 32px/1.2 system-ui,-apple-system,"Segoe UI",sans-serif}
.h18-vd-form-preview-intro{margin:0 0 20px!important;padding:0!important;color:inherit;font:400 16px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif}
.h18-vd-form-preview-body{display:block}
.h18-vd-form-preview-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.h18-vd-form-preview-field{display:flex;flex-direction:column;gap:6px;min-width:0;font-size:14px;font-weight:600;line-height:1.35;color:inherit}
.h18-vd-form-preview-field.is-wide{grid-column:1/-1}
.h18-vd-form-preview-field input,.h18-vd-form-preview-field textarea{box-sizing:border-box;width:100%;min-height:42px;border:1px solid #b8b8b2;border-radius:4px;background:var(--h18-form-preview-field-bg);color:inherit;padding:11px 12px;font:400 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif;opacity:1}
.h18-vd-form-preview-field textarea{height:112px;resize:none}
.h18-vd-form-preview-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0;font-size:14px;font-weight:400;line-height:1.4;color:inherit}
.h18-vd-form-preview-consent input{width:auto!important;min-height:0!important;margin-top:3px;opacity:1}
.h18-vd-form-preview-submit{display:inline-block;border:0;border-radius:4px;background:var(--h18-form-preview-accent);color:#fff;padding:11px 20px;font:700 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif;opacity:1;cursor:default}
@media(max-width:782px){.h18-vd-form-preview-grid{grid-template-columns:1fr}.h18-vd-form-preview-field.is-wide{grid-column:auto}}
'''
write('clean/hangar18-manager/assets/editor-v0181.css', color_css)


# -----------------------------------------------------------------------------
# Documentation graphics (SVGs are source-controlled and viewable in GitHub).
# -----------------------------------------------------------------------------
svg_color = '''<svg xmlns="http://www.w3.org/2000/svg" width="980" height="560" viewBox="0 0 980 560">
<rect width="980" height="560" fill="#f6f7f7"/><text x="40" y="48" font-family="Arial" font-size="28" font-weight="700" fill="#1d2327">Visual Designer · farvevælger</text>
<rect x="40" y="80" width="900" height="430" rx="10" fill="#fff" stroke="#c3c4c7"/><text x="70" y="122" font-family="Arial" font-size="18" font-weight="700">1 · Aktuel farve + HEX</text>
<rect x="70" y="142" width="54" height="34" rx="4" fill="#6a6963" stroke="#444"/><rect x="136" y="142" width="150" height="34" rx="4" fill="#fff" stroke="#8c8f94"/><text x="150" y="165" font-family="monospace" font-size="17">#6A6963</text>
<text x="70" y="218" font-family="Arial" font-size="18" font-weight="700">2 · Fri farve</text><defs><linearGradient id="sat" x1="0" x2="1"><stop stop-color="#fff"/><stop offset="1" stop-color="#f00"/></linearGradient><linearGradient id="val" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000"/></linearGradient></defs><rect x="70" y="238" width="390" height="150" fill="url(#sat)"/><rect x="70" y="238" width="390" height="150" fill="url(#val)"/><text x="500" y="218" font-family="Arial" font-size="18" font-weight="700">3 · Temafarver</text>
<g transform="translate(500 238)"><rect width="42" height="42" fill="#30382a"/><rect x="52" width="42" height="42" fill="#c3ae83"/><rect x="104" width="42" height="42" fill="#eee8dc"/><rect x="156" width="42" height="42" fill="#6a6963"/><rect x="208" width="42" height="42" fill="#fff" stroke="#aaa"/><rect x="260" width="42" height="42" fill="#111"/></g>
<text x="500" y="318" font-family="Arial" font-size="15" fill="#50575e">Temafarver er genveje – de begrænser ikke valget.</text><text x="500" y="358" font-family="Arial" font-size="18" font-weight="700">4 · Senest brugt</text><g transform="translate(500 374)"><rect width="34" height="34" fill="#2271b1"/><rect x="44" width="34" height="34" fill="#d63638"/><rect x="88" width="34" height="34" fill="#00a32a"/></g>
<rect x="735" y="445" width="82" height="36" rx="4" fill="#f6f7f7" stroke="#8c8f94"/><text x="751" y="468" font-family="Arial" font-size="14">Annuller</text><rect x="830" y="445" width="82" height="36" rx="4" fill="#2271b1"/><text x="849" y="468" font-family="Arial" font-size="14" fill="#fff">Anvend</text></svg>'''
write('docs/user-manual-assets/v0181-color-picker.svg', svg_color)

svg_forms = '''<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="620" viewBox="0 0 1100 620">
<rect width="1100" height="620" fill="#f6f7f7"/><text x="40" y="45" font-family="Arial" font-size="26" font-weight="700">Formularer · Designer og frontend bruger samme struktur</text>
<rect x="40" y="75" width="490" height="500" rx="10" fill="#fff" stroke="#2271b1" stroke-width="3"/><text x="65" y="110" font-family="Arial" font-size="18" font-weight="700" fill="#2271b1">DESIGNER</text>
<rect x="570" y="75" width="490" height="500" rx="10" fill="#fff" stroke="#00a32a" stroke-width="3"/><text x="595" y="110" font-family="Arial" font-size="18" font-weight="700" fill="#007017">FRONTEND</text>
<g font-family="Arial" fill="#30382a"><text x="70" y="155" font-size="25" font-weight="700">Kontakt os</text><text x="600" y="155" font-size="25" font-weight="700">Kontakt os</text></g>
<g fill="#eee8dc" stroke="#b8b8b2"><rect x="70" y="195" width="200" height="44" rx="4"/><rect x="290" y="195" width="200" height="44" rx="4"/><rect x="70" y="270" width="200" height="44" rx="4"/><rect x="290" y="270" width="200" height="44" rx="4"/><rect x="70" y="345" width="420" height="95" rx="4"/><rect x="600" y="195" width="200" height="44" rx="4"/><rect x="820" y="195" width="200" height="44" rx="4"/><rect x="600" y="270" width="200" height="44" rx="4"/><rect x="820" y="270" width="200" height="44" rx="4"/><rect x="600" y="345" width="420" height="95" rx="4"/></g>
<g font-family="Arial" font-size="13" fill="#30382a"><text x="70" y="187">Navn *</text><text x="290" y="187">E-mail *</text><text x="70" y="262">Telefon</text><text x="290" y="262">Emne *</text><text x="70" y="337">Besked *</text><text x="600" y="187">Navn *</text><text x="820" y="187">E-mail *</text><text x="600" y="262">Telefon</text><text x="820" y="262">Emne *</text><text x="600" y="337">Besked *</text></g>
<rect x="70" y="505" width="135" height="40" rx="4" fill="#30382a"/><rect x="600" y="505" width="135" height="40" rx="4" fill="#30382a"/><g font-family="Arial" font-size="14" fill="#fff"><text x="91" y="530">Send besked</text><text x="621" y="530">Send besked</text></g><path d="M525 320h40" stroke="#00a32a" stroke-width="5"/><path d="M553 309l14 11-14 11" fill="none" stroke="#00a32a" stroke-width="5"/></svg>'''
write('docs/user-manual-assets/v0181-form-wysiwyg.svg', svg_forms)

svg_overview = '''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650"><rect width="1200" height="650" fill="#f6f7f7"/><text x="35" y="42" font-family="Arial" font-size="26" font-weight="700">Visual Designer · arbejdsfladen</text><rect x="35" y="70" width="1130" height="525" rx="8" fill="#fff" stroke="#c3c4c7"/><rect x="35" y="70" width="210" height="525" fill="#f0f0f1"/><rect x="940" y="70" width="225" height="525" fill="#f0f0f1"/><rect x="245" y="70" width="695" height="58" fill="#1d2327"/><rect x="270" y="155" width="645" height="405" fill="#fafafa" stroke="#8c8f94" stroke-dasharray="6 5"/><g font-family="Arial" fill="#1d2327"><text x="62" y="112" font-size="18" font-weight="700">1 · Elementer</text><text x="970" y="112" font-size="18" font-weight="700">3 · Inspector</text><text x="470" y="105" font-size="18" font-weight="700" fill="#fff">2 · Toolbar / breakpoints</text><text x="475" y="350" font-size="25" font-weight="700">4 · Canvas</text></g><g fill="#fff" stroke="#8c8f94"><rect x="60" y="145" width="155" height="38"/><rect x="60" y="193" width="155" height="38"/><rect x="60" y="241" width="155" height="38"/><rect x="970" y="145" width="165" height="38"/><rect x="970" y="193" width="165" height="38"/><rect x="970" y="241" width="165" height="38"/></g><g font-family="Arial" font-size="14" fill="#3c434a"><text x="80" y="169">Tekst / overskrift</text><text x="80" y="217">Billede / knap</text><text x="80" y="265">Moduler / formular</text><text x="985" y="169">Placering</text><text x="985" y="217">Typografi</text><text x="985" y="265">Farver / design</text></g><text x="280" y="585" font-family="Arial" font-size="14" fill="#50575e">Desktop · Laptop · Tablet · Mobil redigeres i samme Designer.</text></svg>'''
write('docs/user-manual-assets/v0181-designer-overview.svg', svg_overview)


# -----------------------------------------------------------------------------
# Manuals: visual, task-oriented documentation.
# -----------------------------------------------------------------------------
user_manual_path = 'CLEAN-USER-MANUAL.md'
user_manual = read(user_manual_path)
manual_section = r'''

---

## Visual Designer v0.1.81 – sådan arbejder du visuelt

![Visual Designer – arbejdsfladen](docs/user-manual-assets/v0181-designer-overview.svg)

### Elementguide

| Element | Hvad bruges det til? | Typisk brug | Vigtigste indstillinger |
|---|---|---|---|
| Sektion | Samler et område af siden | Hero, indholdsblok, modulslot | baggrund, padding, højde, responsive placering |
| Kasse | Grupperer elementer inde i en sektion | kort, infoboks, kolonne | baggrund, ramme, radius, padding |
| Tekst | Overskrift og brødtekst | H1/H2, intro, artikler | typografi, farve, justering, spacing |
| Billede | Viser WordPress-medie | hero, køretøj, illustration | contain/cover, fokuspunkt, alt-tekst |
| Knap | Handling eller navigation | Bliv medlem, Læs mere | destination, farver, hover/focus, radius |
| Menu | WordPress-navigation | header/mobilmenu | menuvalg, retning, responsive mobilvisning |
| Tabel | Strukturerede rækker/kolonner | specifikationer, oversigter | kanter, zebra, mobilkort/scroll |
| Eventliste | Dynamiske events | Events-side | sortering, dato-filter, kortdesign |
| Eventværdi | Én dynamisk eventværdi | titel, dato, sted, beskrivelse | værdi, HTML-tag, typografi |
| Eventfelt | Fleksibelt eventfelt | Program, Om arrangementet, Praktisk info | feltvalg, overskrift, design |
| Køretøjsliste | Dynamiske køretøjer | Køretøjer og materiel | sortering, kolonner, kortdesign |
| Gallerioversigt | Dynamiske album | Billedgalleri | kolonner, cover, antal billeder |
| Kontaktformular | Kontakt fra besøgende | Kontakt-side | intro, modtager, telefon, samtykke, design |
| Bliv medlem-formular | Medlemsforespørgsler | Bliv medlem | intro, modtager, samtykke, design |

### Kontaktformular og Bliv medlem – WYSIWYG

Fra v0.1.81 viser Designer formularerne med samme struktur som frontend: labels, rigtige inputfelter, textarea, samtykke og knap. Det betyder, at højde, kolonner og spacing kan vurderes direkte i Designeren.

![Formular – Designer og frontend](docs/user-manual-assets/v0181-form-wysiwyg.svg)

**Arbejdsgang:**
1. Træk formularen ind på siden.
2. Vælg formularen og skriv overskrift/intro i Inspector.
3. Vælg modtager-e-mail eller lad feltet være tomt for WordPress admin-e-mail.
4. Slå telefon og samtykke til/fra efter behov.
5. Tilpas baggrund, feltbaggrund, tekst og accent med den fælles farvevælger.
6. Kontroller Desktop, Laptop, Tablet og Mobil før Gem.

### Fælles farvevælger

![Visual Designer – farvevælger](docs/user-manual-assets/v0181-color-picker.svg)

Farvevælgeren har **temafarver som hurtigvalg**, men du kan altid vælge en helt fri farve eller skrive en HEX-kode direkte. Temafarver er altså genveje – ikke en begrænsning. De senest anvendte farver huskes lokalt i browseren.

Hvis et element har en særskilt indstilling **Gennemsigtig**, bruges den fortsat til gennemsigtighed; farvefeltet beholder sin normale HEX-værdi.

### Godt og dårligt eksempel

| God praksis | Undgå |
|---|---|
| Brug temafarver til de gennemgående brandfarver | Næsten-identiske specialfarver på hver side |
| Brug H1 én gang som sidens hovedoverskrift | Flere konkurrerende H1-overskrifter |
| Kontroller alle fire breakpoints | Kun at designe Desktop |
| Brug Sektion/Kasse til struktur | Tilfældige overlap som er svære at vedligeholde |
| Brug dynamiske Event/Køretøj/Galleri-elementer til data | At kopiere dynamiske data ind som statisk tekst |

### Byg en enkel side fra bunden

1. Opret/åbn siden i Visual Designer.
2. Træk en **Sektion** ind som hovedområde.
3. Tilføj **Tekst** og vælg H1 til sidens hovedtitel.
4. Tilføj brødtekst og evt. **Billede**.
5. Tilføj en **Knap** med intern side eller URL.
6. Brug **Kasse** når flere elementer skal høre visuelt sammen.
7. Skift til Laptop, Tablet og Mobil og justér kun de breakpoints, der kræver det.
8. Brug Preview og Gem; sammenlign derefter den offentlige side.
'''
if '## Visual Designer v0.1.81 – sådan arbejder du visuelt' not in user_manual:
    user_manual += manual_section
write(user_manual_path, user_manual)

design_manual_path = 'CLEAN-DESIGN-MANUAL.md'
design_manual = read(design_manual_path)
design_section = r'''

---

## v0.1.81 – visuelle Designer-regler

### Farvesystem

![Farvevælger med temafarver og fri HEX](docs/user-manual-assets/v0181-color-picker.svg)

| Regel | Krav |
|---|---|
| Temafarver | Hentes dynamisk fra aktivt WordPress-tema/Designer-kontekst og vises som genveje |
| Frie farver | Skal altid være mulige; HEX kan indtastes direkte |
| Canonical værdi | Gemmes fortsat som eksisterende HEX-prop – ingen layoutmigration |
| Transparens | Styres af eksisterende transparens-prop/checkbox hvor elementet understøtter det |
| Genbrug | Samme webbaserede picker anvendes på baggrund, tekst, ramme, knap, hover/focus og modulfarver |
| Platform | Primær Designer-oplevelse må ikke afhænge af Windows/macOS native farvedialog |

### Formular-paritet

Kontaktformular og Bliv medlem-formular skal i Designer bruge samme visuelle struktur som frontend. En forenklet mockup med tekstbokse er ikke acceptabel som WYSIWYG-reference.

![Formularparitet](docs/user-manual-assets/v0181-form-wysiwyg.svg)

**Paritetskontrakt:**
- samme feltorden og 2-kolonne grid på store breakpoints;
- samme wide textarea;
- telefon følger formularens `showPhone`-regel for Kontakt og er obligatorisk på medlemsformularen;
- samtykke vises/skjules efter `requireConsent`;
- baggrund, feltbaggrund, tekst, accent, padding og radius kommer fra samme node-props;
- ved mobil breakpoint vises én kolonne;
- Designerens previewfelter er ikke interaktive og kan ikke indsende data.

### Elementdesign

Brugeren skal kunne forstå elementets formål ud fra paletten/Inspector. Manualen skal derfor ved nye elementer dokumentere **formål, typiske anvendelser, centrale indstillinger, responsive regler og et visuelt eksempel**. v0.1.81-elementoversigten i brugermanualen er minimumsstandarden for kommende elementer.
'''
if '## v0.1.81 – visuelle Designer-regler' not in design_manual:
    design_manual += design_section
write(design_manual_path, design_manual)


# -----------------------------------------------------------------------------
# Release history, release notes and status doc
# -----------------------------------------------------------------------------
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
versions = history.get('versions', [])
if not any(str(item.get('version')) == '0.1.81' for item in versions if isinstance(item, dict)):
    versions.insert(0, {
        'version': '0.1.81',
        'date': '2026-09-02',
        'items': [
            'STATUS-READY-001: Sider og Eventfelter markeres Klar i Manager-status.',
            'VD-COLOR-PICKER-001: fælles webbaseret WordPress/Iris-farvevælger med dynamiske temafarver, fri HEX/farve og senest brugte farver.',
            'Kontaktformular og Bliv medlem-formular viser nu labels, inputs, textarea, samtykke og knap i Designer med samme feltstruktur som frontend.',
            'Brugermanual og designmanual er opdateret med grafiske SVG-illustrationer, elementtabel, arbejdsvejledning, responsive/designregler og formular-/farveeksempler.'
        ]
    })
history['versions'] = versions
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

notes_path = 'clean-release-notes.html'
notes = read(notes_path)
section = '''<section data-version="0.1.81"><h2>0.1.81</h2><ul><li>Sider og Eventfelter er markeret Klar.</li><li>Ny fælles webbaseret farvevælger med temafarver, fri HEX/farve og senest brugte farver.</li><li>Kontakt- og medlemsformular-preview matcher frontendens faktiske feltstruktur.</li><li>Bruger- og designmanual er udbygget med grafiske illustrationer og tabeller.</li></ul></section>\n'''
if 'data-version="0.1.81"' not in notes:
    body = notes.find('<body>')
    if body >= 0:
        notes = notes[:body + len('<body>')] + '\n' + section + notes[body + len('<body>'):]
    else:
        notes = section + notes
write(notes_path, notes)

plan_path = 'docs/v0181-plan.md'
plan = read(plan_path)
plan = plan.replace('**Status:** Planlagt – ikke frigivet', '**Status:** Implementeret kandidat – afventer verificeret release')
if '### FORM-WYSIWYG-001' not in plan:
    plan += r'''

### FORM-WYSIWYG-001 — Kontakt og Bliv medlem

- Designer-preview skal bruge samme feltorden og layoutkontrakt som frontend.
- Preview skal vise labels, inputs, textarea, samtykke og knap – ikke simplificerede labelbokse.
- Kontakt respekterer `showPhone`; medlemsformularen viser altid Telefon som obligatorisk.
- Mobil skifter til én kolonne ved 782 px.
- Previewfelter er deaktiverede og må aldrig indsende data fra Designer.

### DOC-VISUAL-001 — Grafiske manualer

- `CLEAN-USER-MANUAL.md` og `CLEAN-DESIGN-MANUAL.md` opdateres i samme release.
- Manualerne indeholder SVG-illustrationer, elementtabel, arbejdsgange, responsive regler samt godt/dårligt-eksempler.
'''
write(plan_path, plan)

status_doc = '''# Visual Designer Manager v0.1.81 – kandidatstatus\n\n- Version: 0.1.81\n- Sider: Klar\n- Eventfelter: Klar\n- Farvevælger: fælles webbaseret picker, temafarver + fri HEX/farve\n- Formular-WYSIWYG: Kontakt + Bliv medlem bruger frontend-lignende feltstruktur i Designer\n- Dokumentation: bruger- og designmanual med grafiske SVG-illustrationer og tabeller\n- Release: må først markeres frigivet når candidate-QA og central ZIP/manifest-workflow er grønne.\n'''
write('docs/v0181-status.md', status_doc)

print('Applied Visual Designer Manager v0.1.81 complete candidate changes.')
