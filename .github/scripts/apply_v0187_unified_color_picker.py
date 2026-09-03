from pathlib import Path
import json

ROOT = Path('clean/hangar18-manager')
PLUGIN = ROOT / 'hangar18-manager.php'
CORE = ROOT / 'assets/editor-v018-core.js'
PICKER = ROOT / 'assets/editor-v0181-color-picker.js'
HISTORY = ROOT / 'release-history.json'
NOTES = Path('clean-release-notes.html')
STATUS = Path('docs/v0187-status.md')


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

plugin = PLUGIN.read_text(encoding='utf-8')
if 'Version: 0.1.86' not in plugin:
    raise SystemExit('Expected v0.1.86 bootstrap before applying v0.1.87')
plugin = plugin.replace('Version: 0.1.86', 'Version: 0.1.87', 1)
plugin = plugin.replace("define('VDM_VERSION', '0.1.86');", "define('VDM_VERSION', '0.1.87');", 1)
plugin = plugin.replace("define('H18_CLEAN_VERSION', '0.1.86');", "define('H18_CLEAN_VERSION', '0.1.87');", 1)

legacy_css = """    wp_enqueue_style(\n        'h18-clean-editor-v0135',\n        H18_CLEAN_URL . 'assets/editor-v0135.css',\n        ['h18-clean-editor-v0134'],\n        H18_CLEAN_VERSION\n    );\n"""
plugin = replace_once(plugin, legacy_css, '', 'retire v0.1.35 color picker CSS')
plugin = replace_once(
    plugin,
    "        ['h18-clean-editor-v0135'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_style(\n        'h18-clean-editor-v0148-layers',",
    "        ['h18-clean-editor-v0134'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_style(\n        'h18-clean-editor-v0148-layers',",
    'relink v0.1.44 stylesheet after retiring v0.1.35'
)

legacy_js = """    wp_enqueue_script(\n        'h18-clean-editor-v0135',\n        H18_CLEAN_URL . 'assets/editor-v0135.js',\n        ['h18-clean-editor-v0132'],\n        H18_CLEAN_VERSION,\n        true\n    );\n"""
plugin = replace_once(plugin, legacy_js, '', 'retire v0.1.35 color picker JavaScript')
plugin = replace_once(
    plugin,
    "        ['h18-clean-editor-v0135'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    wp_enqueue_script(\n        'h18-clean-editor-v0169-canvas-height',",
    "        ['h18-clean-editor-v0132'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    wp_enqueue_script(\n        'h18-clean-editor-v0169-canvas-height',",
    'relink v0.1.48 script after retiring v0.1.35'
)
PLUGIN.write_text(plugin, encoding='utf-8')

picker = r'''(function ($) {
    'use strict';

    const CFG = window.H18CleanEditor || {};
    const RECENT_KEY = 'vdm-recent-colors-v1';
    const LEGACY_RECENT_KEY = 'h18-vd-recent-colors-v1';
    const MAX_RECENT = 8;
    const COLOR_SELECTOR = 'input[type="color"]';

    function normalize(value) {
        value = String(value || '').trim().toLowerCase();
        if (/^#[0-9a-f]{3}$/.test(value)) {
            return '#' + value[1] + value[1] + value[2] + value[2] + value[3] + value[3];
        }
        return /^#[0-9a-f]{6}$/.test(value) ? value : '';
    }

    function themePalette() {
        const list = Array.isArray(CFG.themePalette) ? CFG.themePalette : [];
        return list.map(normalize).filter(Boolean).filter(function (value, index, source) {
            return source.indexOf(value) === index;
        }).slice(0, 24);
    }

    function storedRecent() {
        try {
            let raw = window.localStorage.getItem(RECENT_KEY);
            if (!raw) {
                raw = window.localStorage.getItem(LEGACY_RECENT_KEY);
                if (raw) { window.localStorage.setItem(RECENT_KEY, raw); }
            }
            const list = JSON.parse(raw || '[]');
            return Array.isArray(list) ? list.map(normalize).filter(Boolean).slice(0, MAX_RECENT) : [];
        } catch (error) { return []; }
    }

    function recentColors() { return storedRecent(); }

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
        if (button) {
            button.classList.remove('wp-picker-open');
            button.setAttribute('aria-expanded', 'false');
        }
    }

    function swatchRow(input, title, colors, className) {
        if (!colors.length) { return null; }
        const row = document.createElement('div');
        row.className = 'h18-vd-color-shortcuts ' + className;
        const label = document.createElement('strong');
        label.textContent = title;
        row.appendChild(label);
        const buttons = document.createElement('div');
        buttons.className = 'h18-vd-color-shortcut-list';
        colors.forEach(function (color) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'h18-vd-color-shortcut';
            button.style.backgroundColor = color;
            button.title = title + ': ' + color;
            button.setAttribute('aria-label', title + ' ' + color);
            button.addEventListener('click', function () {
                $(input).wpColorPicker('color', color);
                input.value = color;
            });
            buttons.appendChild(button);
        });
        row.appendChild(buttons);
        return row;
    }

    function refreshRecentRow(input, extra) {
        const oldRecent = extra.querySelector('.h18-vd-color-shortcuts.is-recent');
        if (oldRecent) { oldRecent.remove(); }
        const newRecent = swatchRow(input, 'Senest brugt', recentColors(), 'is-recent');
        if (newRecent) {
            const noteNode = extra.querySelector('.h18-vd-color-note');
            extra.insertBefore(newRecent, noteNode);
        }
    }

    function addChrome(input) {
        const container = input.closest('.wp-picker-container');
        if (!container || container.querySelector('.h18-vd-color-picker-extra')) { return; }
        const holder = container.querySelector('.wp-picker-holder');
        if (!holder) { return; }

        const extra = document.createElement('div');
        extra.className = 'h18-vd-color-picker-extra';
        const theme = swatchRow(input, 'Temafarver', themePalette(), 'is-theme');
        if (theme) { extra.appendChild(theme); }
        const recent = swatchRow(input, 'Senest brugt', recentColors(), 'is-recent');
        if (recent) { extra.appendChild(recent); }

        const note = document.createElement('p');
        note.className = 'description h18-vd-color-note';
        note.textContent = 'Temafarver er genveje. Du kan stadig vælge enhver farve eller skrive HEX-koden direkte.';
        extra.appendChild(note);

        const actions = document.createElement('div');
        actions.className = 'h18-vd-color-actions';
        const cancel = document.createElement('button');
        cancel.type = 'button';
        cancel.className = 'button';
        cancel.textContent = 'Annuller';
        const apply = document.createElement('button');
        apply.type = 'button';
        apply.className = 'button button-primary';
        apply.textContent = 'Anvend';

        cancel.addEventListener('click', function () {
            const original = normalize(input.getAttribute('data-h18-vd-color-original')) || '#000000';
            $(input).wpColorPicker('color', original);
            input.value = original;
            closePicker(input);
        });
        apply.addEventListener('click', function () {
            const value = normalize(input.value); if (!value) { return; }
            remember(value);
            commit(input, value);
            closePicker(input);
        });

        actions.appendChild(cancel);
        actions.appendChild(apply);
        extra.appendChild(actions);
        holder.appendChild(extra);

        const result = container.querySelector('.wp-color-result');
        if (result) {
            result.addEventListener('click', function () {
                input.setAttribute('data-h18-vd-color-original', normalize(input.value) || '#000000');
                window.setTimeout(function () { refreshRecentRow(input, extra); }, 0);
            });
        }
    }

    function enhance(input) {
        if (!(input instanceof HTMLInputElement) || input.getAttribute('data-h18-vd-color-managed') === '1') { return; }
        if (!window.jQuery || !$.fn || typeof $.fn.wpColorPicker !== 'function') { return; }

        const value = normalize(input.value) || '#000000';
        input.setAttribute('data-h18-vd-color-managed', '1');
        input.setAttribute('data-h18-vd-color-original', value);
        input.type = 'text';
        input.value = value;
        input.classList.add('h18-vd-color-source');

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
        const scope = root && (root.querySelectorAll || root.matches) ? root : document;
        if (scope.matches && scope.matches(COLOR_SELECTOR)) { enhance(scope); }
        if (scope.querySelectorAll) { scope.querySelectorAll(COLOR_SELECTOR).forEach(enhance); }
    }

    function init() {
        scan(document);
        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                mutation.addedNodes.forEach(function (node) {
                    if (node instanceof Element) { scan(node); }
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
                $(input).wpColorPicker('color', original);
                input.value = original;
                closePicker(input);
            });
        });
    }

    const api = { refresh: scan, normalize: normalize, themePalette: themePalette, recentColors: recentColors };
    window.VDMColorPicker = api;
    window.H18VDColorPicker = api; // temporary compatibility alias for pre-v0.2 integrations

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})(jQuery);
'''
PICKER.write_text(picker, encoding='utf-8')

core = CORE.read_text(encoding='utf-8')
anchor = """        host.innerHTML = html;\n\n        host.querySelectorAll('[data-field]').forEach(function (control) {\n"""
replacement = """        host.innerHTML = html;\n        // v0.1.87: Inspector is rebuilt on every render. Refresh the one canonical\n        // VDM color picker synchronously when available instead of relying only on\n        // MutationObserver ordering. Initial render is still covered by picker init.\n        if (window.VDMColorPicker && typeof window.VDMColorPicker.refresh === 'function') {\n            window.VDMColorPicker.refresh(host);\n        }\n\n        host.querySelectorAll('[data-field]').forEach(function (control) {\n"""
core = replace_once(core, anchor, replacement, 'explicit color picker refresh after Inspector render')
CORE.write_text(core, encoding='utf-8')

history = json.loads(HISTORY.read_text(encoding='utf-8'))
versions = history.setdefault('versions', [])
if not any(str(row.get('version')) == '0.1.87' for row in versions if isinstance(row, dict)):
    versions.insert(0, {
        'version': '0.1.87',
        'date': '2026-09-03',
        'items': [
            'Farvevælgeren er samlet til én canonical VDM-picker på både side-Designer og Header/Footer Designer.',
            'Den historiske v0.1.35 custom picker er fjernet fra runtime, så den ikke længere konkurrerer med v0.1.81-pickeren.',
            'Alle color-inputs på Designer-siden dækkes, inklusive Baggrund, Tekstfarve, Overskriftsfarve, Rammefarve, hover/focus, accent, formular-, event-, køretøjs-, galleri- og tabelfarver.',
            'Temafarver og senest brugte farver vises som hurtige genveje, mens fri HEX/farve fortsat er mulig.',
            'Inspector kalder nu picker-refresh direkte efter dynamisk genrendering; MutationObserver er kun fallback.',
            'Farveændringer gemmes fortsat først ved Anvend, så Fortryd/Gentag og versionshistorik får én kontrolleret ændring.'
        ]
    })
HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

notes = NOTES.read_text(encoding='utf-8') if NOTES.exists() else ''
section = '''<section data-version="0.1.87"><h2>0.1.87</h2><ul><li><strong>Én farvevælger overalt:</strong> Designerens gamle v0.1.35-picker er fjernet fra runtime, så alle farvefelter bruger den fælles WordPress/VDM-farvevælger.</li><li>Baggrund, Tekstfarve, Overskriftsfarve, Rammefarve samt hover/focus/accent- og modulfarver bruger nu samme UI.</li><li><strong>Temafarver</strong> er direkte genveje i farvevælgeren, sammen med <strong>Senest brugt</strong> og fri HEX/farve.</li><li>Dynamisk genopbyggede Inspector-felter bliver eksplicit geninitialiseret, så browserens native Windows-farvedialog ikke længere dukker op på enkelte felter.</li><li>Farven committes fortsat først ved <strong>Anvend</strong>; Annuller/Escape gendanner den tidligere farve.</li></ul></section>\n'''
if 'data-version="0.1.87"' not in notes:
    NOTES.write_text(section + notes, encoding='utf-8')

STATUS.write_text('''# Visual Designer Manager v0.1.87 status\n\n## Unified color picker\n\nStatus: release candidate\n\n- Én canonical VDM color picker ejer alle `input[type="color"]` på side-Designer og Global Header/Footer Designer.\n- Historisk v0.1.35 picker-JS/CSS er ikke længere en del af runtime dependency chain.\n- v0.1.81 WordPress `wp-color-picker` er den eneste aktive picker.\n- Temafarver, senest brugte farver, fri HEX og WordPress/Iris-farvevalg bevares.\n- Inspector kalder `VDMColorPicker.refresh(host)` direkte efter hver render.\n- MutationObserver håndterer øvrige dynamisk indsatte farveinputs som fallback.\n- `Anvend` er eneste commit-path; `Annuller` og Escape ændrer ikke canonical model.\n- QA kræver at Baggrund, Tekstfarve, Overskriftsfarve og Rammefarve alle er dækket.\n''', encoding='utf-8')

print('Applied Visual Designer Manager v0.1.87 unified color picker candidate')
