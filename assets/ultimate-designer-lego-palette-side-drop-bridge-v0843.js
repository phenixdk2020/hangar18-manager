(function () {
    'use strict';

    const SIDE_ZONE_SELECTOR = '.h18-v0838-drop-zone.h18-v0811-side-zone:not(.is-disabled)';
    const OVER_ZONE_SELECTOR = '.h18-v0838-drop-zone[data-h18-v0838-position="over"]:not(.is-disabled)';
    const UNDER_ZONE_SELECTOR = '.h18-v0838-drop-zone[data-h18-v0838-position="under"]:not(.is-disabled)';
    const ACTIVE_ROW_SELECTOR = '#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)';
    const INSPECTOR_SELECTOR = '#h18-page-inspector-target';
    let redispatching = false;

    function activePaletteSource() {
        const api = window.__h18LegoSideBySideV0840;
        if (!api || typeof api.activeSource !== 'function') { return {}; }
        return api.activeSource() || {};
    }
    function activePaletteDrag() {
        return /^palette-/.test(String(activePaletteSource().Mode || ''));
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
    function rowType(row) { return String(row && row.getAttribute('data-section-type') || controlValue(row, '.h18-page-section-type') || ''); }
    function parentKey(row) { return controlValue(row, '.h18-layout-parent-key'); }
    function rowIndex(row) { return String(row && row.getAttribute('data-section-index') || ''); }
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

    /*
     * LEGO-055: the real editor may move a selected row body into Inspector and
     * repaint nested proxies while a palette drop is being created. Key-only
     * snapshots can therefore mistake an old row for the new row. Track DOM
     * identity + key + section-index and filter by the palette element type.
     */
    function snapshotRows() {
        const snapshot = { nodes: new Set(), keys: new Set(), indices: new Set() };
        document.querySelectorAll(ACTIVE_ROW_SELECTOR).forEach(function (row) {
            snapshot.nodes.add(row);
            const key = rowKey(row);
            const index = rowIndex(row);
            if (key) { snapshot.keys.add(key); }
            if (index) { snapshot.indices.add(index); }
        });
        return snapshot;
    }
    function findNewRow(before, expectedType) {
        const wantedType = String(expectedType || '').trim();
        const candidates = [];
        document.querySelectorAll(ACTIVE_ROW_SELECTOR).forEach(function (row) {
            const key = rowKey(row);
            if (!key) { return; }
            const type = rowType(row);
            if (wantedType && type && type !== wantedType) { return; }
            const index = rowIndex(row);
            const newKey = !before.keys.has(key);
            const newIndex = !!index && !before.indices.has(index);
            const newNode = !before.nodes.has(row);
            if (!newKey && !newIndex && !newNode) { return; }
            let score = 0;
            if (newKey) { score += 100; }
            if (newIndex) { score += 40; }
            if (newNode) { score += 20; }
            const numericIndex = parseInt(index, 10);
            candidates.push({ row: row, score: score, index: Number.isFinite(numericIndex) ? numericIndex : -1 });
        });
        candidates.sort(function (a, b) { return b.score - a.score || b.index - a.index; });
        return candidates.length ? candidates[0].row : null;
    }

    function placementEstablished(newRow, targetRow, position, targetParentKey) {
        const api = window.__h18LegoFixesV0851;
        const newKey = rowKey(newRow);
        const targetKey = rowKey(targetRow);
        if (!api || !newKey || !targetKey || parentKey(newRow) !== targetParentKey) { return false; }
        const parentRow = rowByKey(targetParentKey);
        if (!parentRow || rowType(parentRow) !== 'grid') { return true; }
        if (typeof api.stackStateForKey !== 'function') { return false; }
        const childState = api.stackStateForKey(newKey) || {};
        const targetState = api.stackStateForKey(targetKey) || {};
        if (position === 'over') { return String(targetState.StackRootKey || '') === newKey; }
        const expectedRoot = String(targetState.StackRootKey || targetKey);
        return String(childState.StackRootKey || '') === expectedRoot;
    }

    function adoptNestedDrop(before, targetRow, position, expectedType) {
        if (!targetRow) { return; }
        const targetKey = rowKey(targetRow);
        const targetParentKey = parentKey(targetRow);
        if (!targetKey || !targetParentKey) { return; }

        let done = false;
        let observer = null;
        function finish() {
            if (done) { return; }
            done = true;
            if (observer) { observer.disconnect(); observer = null; }
        }
        function tryAdopt() {
            if (done) { return true; }
            const newRow = findNewRow(before, expectedType);
            const liveTarget = rowByKey(targetKey);
            const api = window.__h18LegoFixesV0851;
            if (!newRow || !liveTarget || !api || typeof api.adoptUnder !== 'function') { return false; }
            const liveParent = parentKey(liveTarget) || targetParentKey;
            if (liveParent !== targetParentKey) { return false; }

            const newKey = rowKey(newRow);
            api.adoptUnder(newKey, targetKey, position);
            const stackHotfix = window.__h18LegoStackSelectionV0853;
            if (stackHotfix && typeof stackHotfix.settleStack === 'function') {
                stackHotfix.settleStack(newKey, targetKey, position);
            }

            if (placementEstablished(newRow, liveTarget, position, targetParentKey)) {
                finish();
                return true;
            }
            return false;
        }

        if (window.MutationObserver) {
            const sections = document.getElementById('h18-page-sections-sortable');
            if (sections) {
                observer = new MutationObserver(function () { tryAdopt(); });
                observer.observe(sections, { childList: true, subtree: true });
            }
        }
        [0, 20, 60, 140, 280, 450, 700, 1000, 1400, 2000, 3000].forEach(function (delay) {
            window.setTimeout(tryAdopt, delay);
        });
        window.setTimeout(function () { if (!done) { finish(); } }, 3600);
    }

    window.addEventListener('dragover', function (event) {
        if (redispatching || !activePaletteDrag()) { return; }
        if (directSideZone(event.target) || directOverZone(event.target) || directUnderZone(event.target)) { return; }
        const zone = overZoneAt(event.clientX, event.clientY) || underZoneAt(event.clientX, event.clientY) || sideZoneAt(event.clientX, event.clientY);
        if (zone) { event.preventDefault(); }
    }, true);

    window.addEventListener('drop', function (event) {
        if (redispatching || !activePaletteDrag()) { return; }
        const source = activePaletteSource();
        const expectedType = String(source.Type || '');

        const over = directOverZone(event.target) || overZoneAt(event.clientX, event.clientY);
        if (over) {
            const targetRow = targetRowForZone(over);
            if (targetRow && parentKey(targetRow)) {
                const before = snapshotRows();
                const target = canonicalOverTarget(over);
                if (!target) { return; }
                stopOriginalDrop(event);
                redirectedDrop(event, target);
                adoptNestedDrop(before, targetRow, 'over', expectedType);
                return;
            }
        }

        /* Prefer a real vertical zone over a side-zone target when small nested
         * proxies overlap. This prevents an intended Under from falling through
         * to the legacy side-by-side handler and becoming a third 4/12 column. */
        const under = directUnderZone(event.target) || underZoneAt(event.clientX, event.clientY);
        if (under) {
            const targetRow = targetRowForZone(under);
            const before = snapshotRows();
            const target = canonicalUnderTarget(under);
            if (!target) { return; }
            stopOriginalDrop(event);
            redirectedDrop(event, target);
            if (targetRow && parentKey(targetRow)) { adoptNestedDrop(before, targetRow, 'under', expectedType); }
            return;
        }

        const directSide = directSideZone(event.target);
        if (directSide) { return; }
        const side = sideZoneAt(event.clientX, event.clientY);
        if (side) {
            stopOriginalDrop(event);
            redirectedDrop(event, side);
        }
    }, true);

    document.documentElement.setAttribute('data-h18-lego-palette-side-drop-bridge', '0.8.43');
    document.documentElement.setAttribute('data-h18-lego-palette-vertical-drop-bridge', '0.8.46');
    document.documentElement.setAttribute('data-h18-lego-palette-nested-drop-stability', '0.8.55');
    window.__h18LegoPaletteSideDropBridgeV0843 = {
        version: '0.8.43', capabilityVersion: '0.8.55',
        sideZoneAt: sideZoneAt, overZoneAt: overZoneAt, underZoneAt: underZoneAt,
        canonicalUnderTarget: canonicalUnderTarget, canonicalOverTarget: canonicalOverTarget,
        activePaletteDrag: activePaletteDrag,
        snapshotRows: snapshotRows,
        findNewRow: findNewRow
    };
}());
