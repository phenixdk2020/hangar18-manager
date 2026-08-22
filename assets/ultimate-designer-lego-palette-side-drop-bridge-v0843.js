(function () {
    'use strict';

    const SIDE_ZONE_SELECTOR = '.h18-v0838-drop-zone.h18-v0811-side-zone:not(.is-disabled)';
    const OVER_ZONE_SELECTOR = '.h18-v0838-drop-zone[data-h18-v0838-position="over"]:not(.is-disabled)';
    const UNDER_ZONE_SELECTOR = '.h18-v0838-drop-zone[data-h18-v0838-position="under"]:not(.is-disabled)';
    const ACTIVE_ROW_SELECTOR = '#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)';
    const INSPECTOR_SELECTOR = '#h18-page-inspector-target';
    let redispatching = false;

    function activePaletteDrag() {
        const api = window.__h18LegoSideBySideV0840;
        if (!api || typeof api.activeSource !== 'function') { return false; }
        const state = api.activeSource() || {};
        return /^palette-/.test(String(state.Mode || ''));
    }
    function directZone(target, selector) { return target && target.closest ? target.closest(selector) : null; }
    function directSideZone(target) { return directZone(target, SIDE_ZONE_SELECTOR); }
    function directOverZone(target) { return directZone(target, OVER_ZONE_SELECTOR); }
    function directUnderZone(target) { return directZone(target, UNDER_ZONE_SELECTOR); }
    function zoneAt(selector, clientX, clientY) {
        let match = null;
        document.querySelectorAll(selector).forEach(function (zone) {
            const rect = zone.getBoundingClientRect();
            if (Number(clientX) >= rect.left && Number(clientX) <= rect.right && Number(clientY) >= rect.top && Number(clientY) <= rect.bottom) { match = zone; }
        });
        return match;
    }
    function sideZoneAt(clientX, clientY) { return zoneAt(SIDE_ZONE_SELECTOR, clientX, clientY); }
    function overZoneAt(clientX, clientY) { return zoneAt(OVER_ZONE_SELECTOR, clientX, clientY); }
    function underZoneAt(clientX, clientY) { return zoneAt(UNDER_ZONE_SELECTOR, clientX, clientY); }

    function controlValue(row, selector) {
        if (!row) { return ''; }
        let field = row.querySelector(selector);
        if (!field && row.classList.contains('is-selected')) { field = document.querySelector(INSPECTOR_SELECTOR + ' ' + selector); }
        return field ? String(field.value || '') : '';
    }
    function rowKey(row) { return controlValue(row, '.h18-page-section-key') || String(row && row.getAttribute('data-key') || ''); }
    function parentKey(row) { return controlValue(row, '.h18-layout-parent-key'); }
    function rowByKey(key) {
        const wanted = String(key || '');
        if (!wanted) { return null; }
        return Array.from(document.querySelectorAll(ACTIVE_ROW_SELECTOR)).find(function (row) { return rowKey(row) === wanted; }) || null;
    }
    function targetRowForZone(zone) {
        if (!zone) { return null; }
        const key = String(zone.getAttribute('data-h18-v0838-target') || zone.getAttribute('data-box') || '');
        return rowByKey(key) || (zone.closest ? zone.closest('.h18-page-section-row') : null);
    }
    function nextActiveRow(row) {
        let candidate = row ? row.nextElementSibling : null;
        while (candidate) {
            if (candidate.matches && candidate.matches(ACTIVE_ROW_SELECTOR)) { return candidate; }
            candidate = candidate.nextElementSibling;
        }
        return null;
    }
    function nextTopLevelRow(row) {
        let candidate = row ? row.nextElementSibling : null;
        while (candidate) {
            if (candidate.matches && candidate.matches(ACTIVE_ROW_SELECTOR) && !parentKey(candidate)) { return candidate; }
            candidate = candidate.nextElementSibling;
        }
        return null;
    }
    function previewTarget(row) { return row ? (row.querySelector('.h18-canvas-preview') || row) : null; }

    function canonicalUnderTarget(zone) {
        const row = targetRowForZone(zone);
        if (!row) { return null; }
        if (parentKey(row)) {
            const next = nextActiveRow(row);
            return next ? previewTarget(next) : (document.getElementById('h18-page-sections-sortable') || document.querySelector('.h18-builder-canvas'));
        }
        const next = nextTopLevelRow(row);
        if (next) { return previewTarget(next); }
        return document.getElementById('h18-page-sections-sortable') || document.querySelector('.h18-builder-canvas');
    }
    function canonicalOverTarget(zone) { return previewTarget(targetRowForZone(zone)); }

    function redirectedDrop(sourceEvent, target) {
        if (!target || typeof target.dispatchEvent !== 'function') { return false; }
        const init = {
            bubbles: true, cancelable: true, composed: true,
            clientX: Number(sourceEvent.clientX) || 0, clientY: Number(sourceEvent.clientY) || 0,
            screenX: Number(sourceEvent.screenX) || 0, screenY: Number(sourceEvent.screenY) || 0,
            ctrlKey: !!sourceEvent.ctrlKey, shiftKey: !!sourceEvent.shiftKey,
            altKey: !!sourceEvent.altKey, metaKey: !!sourceEvent.metaKey,
            dataTransfer: sourceEvent.dataTransfer || null
        };
        let redirected;
        try { redirected = new DragEvent('drop', init); }
        catch (error) {
            redirected = new Event('drop', { bubbles: true, cancelable: true });
            ['clientX', 'clientY', 'screenX', 'screenY', 'dataTransfer'].forEach(function (name) {
                try { Object.defineProperty(redirected, name, { value: init[name] }); } catch (ignored) {}
            });
        }
        redispatching = true;
        try { target.dispatchEvent(redirected); }
        finally { redispatching = false; }
        return true;
    }
    function stopOriginalDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === 'function') { event.stopImmediatePropagation(); }
    }
    function snapshotKeys() {
        const keys = new Set();
        document.querySelectorAll(ACTIVE_ROW_SELECTOR).forEach(function (row) { const key = rowKey(row); if (key) { keys.add(key); } });
        return keys;
    }
    function findNewRow(before) {
        let found = null;
        document.querySelectorAll(ACTIVE_ROW_SELECTOR).forEach(function (row) {
            const key = rowKey(row);
            if (key && !before.has(key)) { found = row; }
        });
        return found;
    }
    function adoptNestedDrop(before, targetRow, position) {
        if (!targetRow || !parentKey(targetRow)) { return; }
        const targetKey = rowKey(targetRow);
        let done = false;
        [0, 20, 60, 140, 280].forEach(function (delay) {
            window.setTimeout(function () {
                if (done) { return; }
                const newRow = findNewRow(before);
                const api = window.__h18LegoFixesV0851;
                if (!newRow || !api || typeof api.adoptUnder !== 'function') { return; }
                done = api.adoptUnder(rowKey(newRow), targetKey, position) === true;
            }, delay);
        });
    }

    window.addEventListener('dragover', function (event) {
        if (redispatching || !activePaletteDrag()) { return; }
        if (directSideZone(event.target) || directOverZone(event.target) || directUnderZone(event.target)) { return; }
        const zone = sideZoneAt(event.clientX, event.clientY) || overZoneAt(event.clientX, event.clientY) || underZoneAt(event.clientX, event.clientY);
        if (zone) { event.preventDefault(); }
    }, true);

    window.addEventListener('drop', function (event) {
        if (redispatching || !activePaletteDrag()) { return; }
        const directSide = directSideZone(event.target);
        if (directSide) { return; }

        const over = directOverZone(event.target) || overZoneAt(event.clientX, event.clientY);
        if (over) {
            const targetRow = targetRowForZone(over);
            if (targetRow && parentKey(targetRow)) {
                const before = snapshotKeys();
                const target = canonicalOverTarget(over);
                if (!target) { return; }
                stopOriginalDrop(event);
                redirectedDrop(event, target);
                adoptNestedDrop(before, targetRow, 'over');
                return;
            }
            if (directOverZone(event.target)) { return; }
        }

        const directUnder = directUnderZone(event.target);
        if (directUnder) {
            const targetRow = targetRowForZone(directUnder);
            const before = snapshotKeys();
            const target = canonicalUnderTarget(directUnder);
            if (!target) { return; }
            stopOriginalDrop(event);
            redirectedDrop(event, target);
            adoptNestedDrop(before, targetRow, 'under');
            return;
        }

        const side = sideZoneAt(event.clientX, event.clientY);
        if (side) {
            stopOriginalDrop(event);
            redirectedDrop(event, side);
            return;
        }

        const under = underZoneAt(event.clientX, event.clientY);
        if (!under) { return; }
        const targetRow = targetRowForZone(under);
        const before = snapshotKeys();
        const target = canonicalUnderTarget(under);
        if (!target) { return; }
        stopOriginalDrop(event);
        redirectedDrop(event, target);
        adoptNestedDrop(before, targetRow, 'under');
    }, true);

    document.documentElement.setAttribute('data-h18-lego-palette-side-drop-bridge', '0.8.43');
    // Keep the established LEGO-046 marker stable for old regression suites and
    // integrations. LEGO-051 nested vertical placement has its own capability
    // marker in the dedicated fixes/drop-zone layer.
    document.documentElement.setAttribute('data-h18-lego-palette-vertical-drop-bridge', '0.8.46');
    window.__h18LegoPaletteSideDropBridgeV0843 = {
        version: '0.8.43', capabilityVersion: '0.8.51',
        sideZoneAt: sideZoneAt, overZoneAt: overZoneAt, underZoneAt: underZoneAt,
        canonicalUnderTarget: canonicalUnderTarget, canonicalOverTarget: canonicalOverTarget,
        activePaletteDrag: activePaletteDrag
    };
}());
