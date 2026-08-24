(function () {
    'use strict';

    if (window.__h18ElementSizingV0887) { return; }

    const VERSION = '0.8.87';
    const HANDLE_ID = 'h18-v0887-element-height-handle';
    let frame = 0;
    let handle = null;
    let drag = null;

    function canvasDevice() {
        const canvas = document.querySelector('.h18-builder-canvas');
        return String(canvas ? canvas.getAttribute('data-canvas-device') || 'desktop' : 'desktop').toLowerCase();
    }

    function selectedRow() {
        return document.querySelector('#h18-page-sections-sortable .h18-page-section-row.is-selected');
    }

    function rowType(row) {
        return String(row ? row.getAttribute('data-section-type') || '' : '').toLowerCase();
    }

    function rowKey(row) {
        if (!row) { return ''; }
        const key = row.querySelector('.h18-page-section-key');
        return String(key ? key.value || '' : '').trim();
    }

    function fieldSelector(name) {
        return '[name$="[' + String(name || '') + ']"]';
    }

    function controls(row, name) {
        if (!row || !name) { return []; }
        const selector = fieldSelector(name);
        const found = Array.from(row.querySelectorAll(selector));
        if (row.classList.contains('is-selected')) {
            const inspector = document.getElementById('h18-page-inspector-target');
            if (inspector) { found.push.apply(found, Array.from(inspector.querySelectorAll(selector))); }
        }
        return found.filter(function (node, index, list) { return list.indexOf(node) === index; });
    }

    function readValue(row, name, fallback) {
        const list = controls(row, name);
        if (!list.length) { return fallback; }
        const node = list[0];
        if (node.type === 'checkbox') { return Boolean(node.checked); }
        const value = node.value;
        return value === undefined || value === null || value === '' ? fallback : value;
    }

    function readNumber(row, name, fallback) {
        const value = parseInt(readValue(row, name, fallback), 10);
        return Number.isFinite(value) ? value : fallback;
    }

    function writeValue(row, name, value, emit) {
        const list = controls(row, name);
        list.forEach(function (node) {
            if (node.type === 'checkbox') { node.checked = Boolean(value); }
            else { node.value = String(value); }
        });
        if (emit && list.length) {
            ['input', 'change'].forEach(function (type) {
                try { list[0].dispatchEvent(new Event(type, { bubbles: true })); } catch (ignore) {}
            });
        }
        return list.length > 0;
    }

    function cssEscape(value) {
        const raw = String(value || '');
        if (window.CSS && typeof window.CSS.escape === 'function') { return window.CSS.escape(raw); }
        return raw.replace(/(["\\])/g, '\\$1');
    }

    function visualTarget(row) {
        const canvas = document.querySelector('.h18-builder-canvas');
        if (!canvas || !row) { return null; }
        const selected = canvas.querySelector('.h18-v0851-selection-target');
        if (selected) { return selected; }

        const key = rowKey(row);
        if (key) {
            const escaped = cssEscape(key);
            const tile = canvas.querySelector('[data-h18-v0811-row="' + escaped + '"],[data-h18-v0840-auto-child="' + escaped + '"],[data-h18-v0811-child="' + escaped + '"]');
            if (tile) {
                return tile.querySelector('.h18-v0811-auto-box-preview,.h18-v0811-child-preview') || tile;
            }
        }
        return row.querySelector(':scope > .h18-canvas-preview') || row.querySelector('.h18-canvas-preview');
    }

    function heightFieldFor(row) {
        const device = canvasDevice();
        if (rowType(row) === 'image') {
            return device === 'mobile' ? 'MobileImageHeightPx' : 'ImageHeightPx';
        }
        if (device === 'mobile') { return 'MobileMinHeightPx'; }
        if (device === 'tablet') { return 'TabletMinHeightPx'; }
        return 'ElementMinHeightPx';
    }

    function imageWidthField() {
        return canvasDevice() === 'mobile' ? 'MobileImageWidthPercent' : 'ImageWidthPercent';
    }

    function applyImageSizing(row, target) {
        if (!row || rowType(row) !== 'image' || !target) { return; }
        const images = Array.from(target.querySelectorAll('img'));
        if (!images.length) { return; }

        const aspectValue = String(readValue(row, 'ImageAspectRatio', 'Auto'));
        const locked = Boolean(readValue(row, 'ImageAspectLocked', false));
        const smartAuto = aspectValue.toLowerCase() === 'auto' && !locked;
        const fit = smartAuto ? 'contain' : String(readValue(row, 'ImageFit', 'Cover')).toLowerCase();
        const height = Math.max(0, readNumber(row, heightFieldFor(row), 0));
        const width = Math.max(20, Math.min(100, readNumber(row, imageWidthField(), 100)));
        const maxWidth = Math.max(0, readNumber(row, 'ImageMaxWidthPx', 0));
        const aspectMap = { '1:1': '1 / 1', '4:3': '4 / 3', '3:2': '3 / 2', '16:9': '16 / 9' };
        const aspect = smartAuto ? 'auto' : (aspectMap[aspectValue] || 'auto');

        target.setAttribute('data-h18-v0887-image-fit', smartAuto ? 'auto-contain' : fit);
        target.style.overflow = 'visible';
        images.forEach(function (image) {
            image.style.boxSizing = 'border-box';
            image.style.display = 'block';
            image.style.width = width + '%';
            image.style.maxWidth = maxWidth > 0 ? Math.min(maxWidth, target.getBoundingClientRect().width || maxWidth) + 'px' : '100%';
            image.style.height = height > 0 ? height + 'px' : 'auto';
            image.style.aspectRatio = aspect;
            image.style.objectFit = fit;
            image.style.objectPosition = readNumber(row, 'ImageFocalXPercent', 50) + '% ' + readNumber(row, 'ImageFocalYPercent', 50) + '%';
            image.style.marginInline = 'auto';
        });
    }

    function ensureHandle() {
        if (handle && document.body.contains(handle)) { return handle; }
        handle = document.getElementById(HANDLE_ID);
        if (handle) { return handle; }
        handle = document.createElement('button');
        handle.type = 'button';
        handle.id = HANDLE_ID;
        handle.className = 'h18-v0887-element-height-handle';
        handle.title = 'Træk op eller ned for at ændre elementets højde';
        handle.setAttribute('aria-label', 'Juster elementets højde');
        const glyph = document.createElement('span');
        glyph.setAttribute('aria-hidden', 'true');
        glyph.textContent = '↕';
        handle.appendChild(glyph);
        document.body.appendChild(handle);
        return handle;
    }

    function placeHandle(row, target) {
        const button = ensureHandle();
        if (!row || !target) {
            if (!drag) { button.hidden = true; }
            return;
        }
        const rect = target.getBoundingClientRect();
        if (rect.width < 20 || rect.height < 20 || rect.bottom < 0 || rect.top > window.innerHeight) {
            if (!drag) { button.hidden = true; }
            return;
        }
        button.hidden = false;
        button.style.left = Math.round(rect.left + (rect.width / 2)) + 'px';
        button.style.top = Math.round(rect.bottom) + 'px';
        button.setAttribute('data-h18-v0887-key', rowKey(row));
        button.setAttribute('data-h18-v0887-type', rowType(row));
    }

    function measureNaturalHeight(target) {
        if (!target) { return 48; }
        const previous = target.style.minHeight;
        target.style.minHeight = '0px';
        const value = Math.max(48, target.scrollHeight, target.getBoundingClientRect().height);
        target.style.minHeight = previous;
        return value;
    }

    function apply() {
        frame = 0;
        const row = selectedRow();
        const target = visualTarget(row);
        if (row && target) { applyImageSizing(row, target); }
        if (!drag) { placeHandle(row, target); }
        document.documentElement.setAttribute('data-h18-element-sizing', VERSION);
    }

    function schedule() {
        if (frame) { return; }
        frame = window.requestAnimationFrame(apply);
    }

    function beginDrag(event) {
        const row = selectedRow();
        const target = visualTarget(row);
        if (!row || !target || event.button !== 0 || drag) { return; }
        event.preventDefault();
        event.stopPropagation();

        const type = rowType(row);
        const field = heightFieldFor(row);
        const device = canvasDevice();
        const history = window.__h18HistoryAtomicV0840;
        if (history && typeof history.begin === 'function') {
            try { history.begin(type === 'image' ? 'image-height-resize' : 'element-height-resize'); } catch (ignore) {}
        }

        if (type === 'image') {
            const image = target.querySelector('img');
            const startHeight = image ? image.getBoundingClientRect().height : target.getBoundingClientRect().height;
            drag = {
                pointerId: event.pointerId,
                row: row,
                target: target,
                field: field,
                mode: 'image',
                startY: event.clientY,
                startHeight: Math.max(80, startHeight),
                minHeight: 80,
                maxHeight: device === 'mobile' ? 900 : 1200,
                history: history
            };
        } else {
            const rect = target.getBoundingClientRect();
            drag = {
                pointerId: event.pointerId,
                row: row,
                target: target,
                field: field,
                mode: 'element',
                startY: event.clientY,
                startHeight: rect.height,
                naturalHeight: measureNaturalHeight(target),
                minHeight: 48,
                maxHeight: device === 'mobile' ? 1200 : 1600,
                history: history
            };
        }

        handle.classList.add('is-active');
        if (handle.setPointerCapture) {
            try { handle.setPointerCapture(event.pointerId); } catch (ignore) {}
        }
    }

    function moveDrag(event) {
        if (!drag || event.pointerId !== drag.pointerId) { return; }
        event.preventDefault();
        const delta = event.clientY - drag.startY;

        if (drag.mode === 'image') {
            const next = Math.max(drag.minHeight, Math.min(drag.maxHeight, Math.round(drag.startHeight + delta)));
            writeValue(drag.row, drag.field, next, false);
            applyImageSizing(drag.row, drag.target);
        } else {
            const proposed = Math.max(drag.minHeight, Math.min(drag.maxHeight, Math.round(drag.startHeight + delta)));
            const next = proposed <= drag.naturalHeight + 4 ? 0 : proposed;
            writeValue(drag.row, drag.field, next, false);
            drag.target.style.minHeight = next > 0 ? next + 'px' : '0px';
        }
        placeHandle(drag.row, drag.target);
    }

    function finishDrag(event, commit) {
        if (!drag || (event && event.pointerId !== drag.pointerId)) { return; }
        const current = drag;
        drag = null;
        if (handle) { handle.classList.remove('is-active'); }
        if (commit !== false) {
            const value = readValue(current.row, current.field, 0);
            writeValue(current.row, current.field, value, true);
        }
        if (current.history && typeof current.history.end === 'function') {
            try { current.history.end(commit !== false); } catch (ignore) {}
        }
        window.setTimeout(function () {
            if (window.__h18LegoStackAutosizeV0886 && typeof window.__h18LegoStackAutosizeV0886.refresh === 'function') {
                try { window.__h18LegoStackAutosizeV0886.refresh(); } catch (ignore) {}
            }
            schedule();
        }, 0);
    }

    function install() {
        ensureHandle();
        handle.addEventListener('pointerdown', beginDrag, true);
        document.addEventListener('pointermove', moveDrag, true);
        document.addEventListener('pointerup', function (event) { finishDrag(event, true); }, true);
        document.addEventListener('pointercancel', function (event) { finishDrag(event, false); }, true);
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && drag) { finishDrag(null, false); }
        }, true);

        document.addEventListener('click', schedule, true);
        document.addEventListener('input', schedule, true);
        document.addEventListener('change', schedule, true);
        window.addEventListener('resize', schedule, { passive: true });
        window.addEventListener('scroll', schedule, { passive: true, capture: true });

        const canvas = document.querySelector('.h18-builder-canvas');
        const sections = document.getElementById('h18-page-sections-sortable');
        if (window.MutationObserver && sections) {
            new MutationObserver(function (mutations) {
                if (mutations.some(function (mutation) { return mutation.type === 'childList'; })) { schedule(); }
            }).observe(sections, { childList: true, subtree: true });
        }
        if (window.MutationObserver && canvas) {
            new MutationObserver(schedule).observe(canvas, { attributes: true, attributeFilter: ['data-canvas-device'] });
        }
        [0, 60, 180, 500].forEach(function (delay) { window.setTimeout(schedule, delay); });
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }

    window.__h18ElementSizingV0887 = {
        version: VERSION,
        refresh: apply
    };
}());
