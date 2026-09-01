(() => {
    'use strict';

    const panel = document.querySelector('.h18-vd-module-design-panel');
    const hidden = document.getElementById('h18-module-design-json');
    const frame = document.querySelector('.h18-vd-module-canonical-frame');
    if (!panel || !hidden || !frame) return;

    const fields = Array.from(panel.querySelectorAll('[data-module-design-key]'));
    const reset = panel.querySelector('[data-module-design-reset]');
    let state = {};
    let defaults = {};
    try { state = JSON.parse(hidden.value || '{}') || {}; } catch (error) { state = {}; }
    try { defaults = JSON.parse(panel.getAttribute('data-defaults') || '{}') || {}; } catch (error) { defaults = {}; }

    const readValue = (field) => {
        if (field.type === 'number' || field.type === 'range') {
            const value = Number(field.value);
            return Number.isFinite(value) ? value : 0;
        }
        return String(field.value || '');
    };

    const writeFields = (source) => {
        fields.forEach((field) => {
            const key = field.getAttribute('data-module-design-key');
            if (!key || !(key in source)) return;
            field.value = String(source[key]);
        });
    };

    const syncState = () => {
        fields.forEach((field) => {
            const key = field.getAttribute('data-module-design-key');
            if (!key) return;
            state[key] = readValue(field);
        });
        hidden.value = JSON.stringify(state);
    };

    let timer = 0;
    const refreshPreview = (immediate = false) => {
        syncState();
        window.clearTimeout(timer);
        const run = () => {
            const base = frame.getAttribute('data-base-url') || frame.src;
            const url = new URL(base, window.location.href);
            url.searchParams.set('h18_vd_module_preview', '1');
            url.searchParams.set('h18_vd_module_preview_version', String(window.H18CleanEditor?.version || '0.1.77'));
            url.searchParams.set('h18_vd_module_design', JSON.stringify(state));
            frame.src = url.toString();
        };
        if (immediate) run(); else timer = window.setTimeout(run, 220);
    };

    fields.forEach((field) => {
        field.addEventListener('input', () => refreshPreview(false));
        field.addEventListener('change', () => refreshPreview(true));
    });

    if (reset) {
        reset.addEventListener('click', () => {
            state = { ...defaults };
            writeFields(state);
            refreshPreview(true);
        });
    }

    writeFields(state);
})();
