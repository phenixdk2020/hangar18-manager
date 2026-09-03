(function ($) {
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
