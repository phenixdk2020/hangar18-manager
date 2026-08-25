(function () {
    'use strict';

    if (window.__h18PhysicalImageV0903) { return; }

    const VERSION = '0.9.3';
    const CFG = window.H18PhysicalImageV0903 || {};
    const DEFAULT_MODE = String(CFG.defaultMode || 'Cover');
    const HOST_ID = 'h18-page-sections-sortable';
    const CELL_SELECTOR = '.h18-v0901-physical-cell[data-h18-v0901-key]';

    let persisted = {};
    let hydrated = {};
    let frame = 0;
    let timer = 0;

    function cleanKey(value) {
        return String(value == null ? '' : value).trim().toLowerCase().replace(/[^a-z0-9._-]/g, '').slice(0, 120);
    }
    function pageSlug() {
        const form = document.getElementById('h18-page-editor-form');
        const field = form && form.querySelector('[name="page_slug"]');
        return String(field && field.value || '').trim();
    }
    function physicalApi() { return window.__h18PhysicalCanvasV0901 || null; }
    function traceApi() { return window.__h18UltimateDesignerTraceV0876 || null; }
    function canvasDevice() {
        const canvas = document.querySelector('.h18-builder-canvas');
        return String(canvas && canvas.getAttribute('data-canvas-device') || 'desktop').toLowerCase();
    }
    function rows() {
        const host = document.getElementById(HOST_ID);
        return host ? Array.from(host.children).filter(function (node) {
            return node && node.classList && node.classList.contains('h18-page-section-row');
        }) : [];
    }
    function rowKey(row) {
        const field = row && row.querySelector('.h18-page-section-key,[name$="[Key]"]');
        return cleanKey(field && field.value || row && row.getAttribute('data-key') || '');
    }
    function rowType(row) {
        const field = row && row.querySelector('[name$="[Type]"]');
        return String(row && row.getAttribute('data-section-type') || field && field.value || '').trim().toLowerCase();
    }
    function rowMap() {
        const map = {};
        rows().forEach(function (row) {
            const key = rowKey(row);
            if (key) { map[key] = row; }
        });
        return map;
    }
    function controls(row, suffix) {
        if (!row) { return []; }
        const selector = '[name$="[' + suffix + ']"]';
        const list = Array.from(row.querySelectorAll(selector));
        if (row.classList.contains('is-selected')) {
            const inspector = document.getElementById('h18-page-inspector-target');
            if (inspector) {
                Array.from(inspector.querySelectorAll(selector)).forEach(function (node) {
                    if (list.indexOf(node) === -1) { list.push(node); }
                });
            }
        }
        return list;
    }
    function firstControl(row, suffix) {
        const list = controls(row, suffix);
        return list.length ? list[0] : null;
    }
    function numberControl(row, suffix, fallback) {
        const node = firstControl(row, suffix);
        const value = parseInt(node && node.value || String(fallback), 10);
        return Number.isFinite(value) ? Math.max(0, Math.min(100, value)) : fallback;
    }
    function modeValue(value) {
        const text = String(value || '').trim().toLowerCase();
        if (text === 'contain') { return 'Contain'; }
        if (text === 'stretch') { return 'Stretch'; }
        return 'Cover';
    }
    function pagePersisted() {
        const pages = CFG.pages && typeof CFG.pages === 'object' ? CFG.pages : {};
        const state = pages[pageSlug()];
        return state && typeof state === 'object' ? state : {};
    }
    function normalizeSetting(raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        return {
            SchemaVersion: 1,
            Mode: modeValue(raw.Mode || DEFAULT_MODE),
            FocalX: Math.max(0, Math.min(100, parseInt(raw.FocalX, 10) || 50)),
            FocalY: Math.max(0, Math.min(100, parseInt(raw.FocalY, 10) || 50))
        };
    }
    function loadPersisted() {
        persisted = {};
        const source = pagePersisted();
        Object.keys(source).forEach(function (key) {
            const clean = cleanKey(key);
            if (clean) { persisted[clean] = normalizeSetting(source[key]); }
        });
    }
    function ensureStretchOption(select) {
        if (!select || String(select.tagName || '').toLowerCase() !== 'select') { return; }
        const exists = Array.from(select.options || []).some(function (option) {
            return String(option.value || '').toLowerCase() === 'stretch';
        });
        if (!exists) {
            const option = document.createElement('option');
            option.value = 'Stretch';
            option.textContent = 'Fri bredde/højde · stræk';
            select.appendChild(option);
        }
    }
    function settingFor(row, key) {
        const select = firstControl(row, 'ImageFit');
        if (select) { ensureStretchOption(select); }

        if (!hydrated[key]) {
            hydrated[key] = true;
            if (persisted[key] && select) {
                select.value = persisted[key].Mode;
            }
            if (persisted[key]) {
                const x = firstControl(row, 'ImageFocalXPercent');
                const y = firstControl(row, 'ImageFocalYPercent');
                if (x) { x.value = String(persisted[key].FocalX); }
                if (y) { y.value = String(persisted[key].FocalY); }
            }
        }

        const current = {
            SchemaVersion: 1,
            Mode: modeValue(select && select.value || (persisted[key] && persisted[key].Mode) || DEFAULT_MODE),
            FocalX: numberControl(row, 'ImageFocalXPercent', persisted[key] ? persisted[key].FocalX : 50),
            FocalY: numberControl(row, 'ImageFocalYPercent', persisted[key] ? persisted[key].FocalY : 50)
        };
        persisted[key] = current;
        return current;
    }
    function effectiveGeometry(key) {
        const api = physicalApi();
        let raw = null;
        try { raw = api && typeof api.geometryForKey === 'function' ? api.geometryForKey(key) : null; } catch (ignore) {}
        if (!raw || typeof raw !== 'object') { return null; }
        const device = canvasDevice();
        if (device === 'desktop') { return raw.Desktop || null; }
        const branch = device === 'mobile' ? raw.Mobile : raw.Tablet;
        if (!branch || branch.InheritDesktop !== false) { return raw.Desktop || branch || null; }
        return branch;
    }
    function imageParts(cell) {
        if (!cell) { return { figure: null, image: null }; }
        const figure = cell.querySelector('.h18-editor-image') || cell.querySelector('figure');
        const image = figure ? figure.querySelector('img') : cell.querySelector('img');
        return { figure: figure || (image && image.parentElement) || null, image: image || null };
    }
    function applyCell(cell, map) {
        const key = cleanKey(cell && cell.getAttribute('data-h18-v0901-key') || '');
        const row = key ? map[key] : null;
        if (!key || !row || rowType(row) !== 'image') {
            if (cell) {
                cell.removeAttribute('data-h18-v0903-image-box');
                cell.removeAttribute('data-h18-v0903-fit');
                cell.removeAttribute('data-h18-v0903-box-height');
            }
            return;
        }

        const state = settingFor(row, key);
        const geometry = effectiveGeometry(key);
        const explicitHeight = Boolean(geometry && geometry.Explicit && Number(geometry.H || 0) > 0);
        const parts = imageParts(cell);

        cell.setAttribute('data-h18-v0903-image-box', '1');
        cell.setAttribute('data-h18-v0903-fit', state.Mode.toLowerCase());
        cell.setAttribute('data-h18-v0903-box-height', explicitHeight ? 'explicit' : 'auto');
        cell.style.setProperty('--h18-v0903-focal-x', String(state.FocalX) + '%');
        cell.style.setProperty('--h18-v0903-focal-y', String(state.FocalY) + '%');

        if (parts.figure) {
            parts.figure.style.width = '100%';
            parts.figure.style.maxWidth = 'none';
            parts.figure.style.margin = '0';
            parts.figure.style.overflow = 'hidden';
            parts.figure.style.height = explicitHeight ? '100%' : 'auto';
        }
        if (parts.image) {
            parts.image.style.display = 'block';
            parts.image.style.width = '100%';
            parts.image.style.maxWidth = 'none';
            parts.image.style.height = explicitHeight ? '100%' : 'auto';
            parts.image.style.aspectRatio = 'auto';
            parts.image.style.objectFit = state.Mode === 'Contain' ? 'contain' : (state.Mode === 'Stretch' ? 'fill' : 'cover');
            parts.image.style.objectPosition = String(state.FocalX) + '% ' + String(state.FocalY) + '%';
            parts.image.style.margin = '0';
        }
    }
    function apply() {
        frame = 0;
        const map = rowMap();
        document.querySelectorAll(CELL_SELECTOR).forEach(function (cell) { applyCell(cell, map); });
        document.documentElement.setAttribute('data-h18-physical-image', VERSION);
    }
    function schedule(delay) {
        if (delay) {
            window.setTimeout(function () { schedule(); }, delay);
            return;
        }
        if (frame) { return; }
        frame = window.requestAnimationFrame(apply);
    }
    function traceChange(row) {
        const api = traceApi();
        if (!api || typeof api.record !== 'function') { return; }
        const key = rowKey(row);
        if (!key || rowType(row) !== 'image') { return; }
        const state = settingFor(row, key);
        const geo = effectiveGeometry(key);
        try {
            api.record('DIAG_IMAGE_PHYSICAL_MODE_V0903', row, {
                key: key,
                mode: state.Mode,
                focalX: state.FocalX,
                focalY: state.FocalY,
                geometry: geo ? {
                    x: Number(geo.X || 0), y: Number(geo.Y || 0),
                    w: Number(geo.W || 0), h: Number(geo.H || 0),
                    explicit: Boolean(geo.Explicit)
                } : null
            }, { force: true });
        } catch (ignore) {}
        const live = window.__h18LiveDiagnosticsV0888;
        if (live && typeof live.flush === 'function') {
            window.setTimeout(function () { try { live.flush(); } catch (ignore) {} }, 20);
        }
    }
    function rowForControl(control) {
        const row = control && control.closest ? control.closest('.h18-page-section-row') : null;
        if (row) { return row; }
        const selected = rows().find(function (candidate) { return candidate.classList.contains('is-selected'); });
        return selected || null;
    }
    function installEvents() {
        document.addEventListener('change', function (event) {
            const target = event.target;
            if (!target || !target.matches || !target.matches('[name$="[ImageFit]"],[name$="[ImageFocalXPercent]"],[name$="[ImageFocalYPercent]"]')) { return; }
            const row = rowForControl(target);
            if (!row || rowType(row) !== 'image') { return; }
            traceChange(row);
            schedule();
        }, true);
        document.addEventListener('input', function (event) {
            const target = event.target;
            if (!target || !target.matches || !target.matches('[name$="[ImageFocalXPercent]"],[name$="[ImageFocalYPercent]"]')) { return; }
            schedule();
        }, true);
        document.addEventListener('click', function (event) {
            if (event.target && event.target.closest && event.target.closest('.h18-v0901-undo,.h18-v0901-redo')) {
                schedule(30);
            }
        }, true);
        document.addEventListener('keydown', function (event) {
            const key = String(event.key || '').toLowerCase();
            if ((event.ctrlKey || event.metaKey) && (key === 'z' || key === 'y')) { schedule(30); }
        }, true);
        const host = document.getElementById(HOST_ID);
        if (window.MutationObserver && host) {
            new MutationObserver(function () { schedule(); }).observe(host, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
        }
        const canvas = document.querySelector('.h18-builder-canvas');
        if (window.MutationObserver && canvas) {
            new MutationObserver(function () { schedule(); }).observe(canvas, { attributes: true, attributeFilter: ['data-canvas-device'] });
        }
        window.addEventListener('resize', function () { schedule(); }, { passive: true });
    }
    function install() {
        loadPersisted();
        installEvents();
        schedule();
        [80, 250, 700].forEach(function (delay) { schedule(delay); });
        timer = window.setInterval(function () { schedule(); }, 500);
        const api = traceApi();
        if (api && typeof api.record === 'function') {
            try { api.record('DIAG_IMAGE_PHYSICAL_BOOT_V0903', document.body, { version: VERSION, defaultMode: DEFAULT_MODE }, { force: true }); } catch (ignore) {}
        }
    }

    window.addEventListener('pagehide', function () {
        if (timer) { window.clearInterval(timer); timer = 0; }
    });

    window.__h18PhysicalImageV0903 = {
        version: VERSION,
        refresh: apply,
        settingForKey: function (key) { return persisted[cleanKey(key)] || null; }
    };

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
