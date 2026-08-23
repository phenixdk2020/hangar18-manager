(function () {
    'use strict';

    const SIDE_ZONE_SELECTOR = '.h18-v0838-drop-zone.h18-v0811-side-zone:not(.is-disabled)';
    const OVER_ZONE_SELECTOR = '.h18-v0838-drop-zone[data-h18-v0838-position="over"]:not(.is-disabled)';
    const UNDER_ZONE_SELECTOR = '.h18-v0838-drop-zone[data-h18-v0838-position="under"]:not(.is-disabled)';
    const ACTIVE_ROW_SELECTOR = '#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)';
    const INSPECTOR_SELECTOR = '#h18-page-inspector-target';
    const LEGACY_AUTO_DROP_SELECTOR = '.h18-v0814-auto-drop-zone,.h18-v0814-auto-kasse-drop,.h18-ud-auto-box-empty-drop,[data-h18-v0814-auto-drop]';
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
            if (Number(clientX) >= rect.left && Number(clientX) <= rect.right && Number(clientY) >= rect.top && Number(clientY) <= rect.bottom) {
                match = zone;
            }
        });
        return match;
    }

    function sideZoneAt(clientX, clientY) { return zoneAt(SIDE_ZONE_SELECTOR, clientX, clientY); }
    function overZoneAt(clientX, clientY) { return zoneAt(OVER_ZONE_SELECTOR, clientX, clientY); }
    function underZoneAt(clientX, clientY) { return zoneAt(UNDER_ZONE_SELECTOR, clientX, clientY); }

    function controlValue(row, selector) {
        if (!row) { return ''; }
        let field = row.querySelector(selector);
        if (!field && row.classList.contains('is-selected')) {
            field = document.querySelector(INSPECTOR_SELECTOR + ' ' + selector);
        }
        return field ? String(field.value || '') : '';
    }

    function rowKey(row) { return controlValue(row, '.h18-page-section-key') || String(row && row.getAttribute('data-key') || ''); }
    function parentKey(row) { return controlValue(row, '.h18-layout-parent-key'); }

    function rowByKey(key) {
        const wanted = String(key || '');
        if (!wanted) { return null; }
        return Array.from(document.querySelectorAll(ACTIVE_ROW_SELECTOR)).find(function (row) {
            return rowKey(row) === wanted;
        }) || null;
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
            bubbles: true,
            cancelable: true,
            composed: true,
            clientX: Number(sourceEvent.clientX) || 0,
            clientY: Number(sourceEvent.clientY) || 0,
            screenX: Number(sourceEvent.screenX) || 0,
            screenY: Number(sourceEvent.screenY) || 0,
            ctrlKey: !!sourceEvent.ctrlKey,
            shiftKey: !!sourceEvent.shiftKey,
            altKey: !!sourceEvent.altKey,
            metaKey: !!sourceEvent.metaKey,
            dataTransfer: sourceEvent.dataTransfer || null
        };
        let redirected;
        try {
            redirected = new DragEvent('drop', init);
        } catch (error) {
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
        document.querySelectorAll(ACTIVE_ROW_SELECTOR).forEach(function (row) {
            const key = rowKey(row);
            if (key) { keys.add(key); }
        });
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

    /* LEGO-056: legacy Auto-kasse insertion chrome stays in the DOM because
     * nesting-tools may regenerate it during render. Removing it from a
     * MutationObserver created a remove/recreate feedback loop. CSS owns
     * visibility; the actual Auto-kasse grid remains the drop surface. */
    function installLegacyAutoDropCss() {
        if (document.getElementById('h18-lego-legacy-auto-drop-hide-v0856')) { return; }
        const style = document.createElement('style');
        style.id = 'h18-lego-legacy-auto-drop-hide-v0856';
        style.textContent = [
            '.h18-builder-canvas .h18-v0814-auto-drop-zone,',
            '.h18-builder-canvas .h18-v0814-auto-kasse-drop,',
            '.h18-builder-canvas .h18-ud-auto-box-empty-drop,',
            '.h18-builder-canvas [data-h18-v0814-auto-drop]{display:none!important;pointer-events:none!important;width:0!important;height:0!important;min-width:0!important;min-height:0!important;margin:0!important;padding:0!important;border:0!important;overflow:hidden!important}'
        ].join('');
        (document.head || document.documentElement).appendChild(style);
    }

    function ensureParentOption(childKey, targetParentKey) {
        const guard = window.__h18LegoParentKeyGuardV0845;
        if (!guard || typeof guard.ensureParentOption !== 'function') { return false; }
        return guard.ensureParentOption(childKey, targetParentKey) === true;
    }

    function nestedAdoptionComplete(api, childKey, targetKey, targetParentKey, position) {
        const liveChild = rowByKey(childKey);
        const liveTarget = rowByKey(targetKey);
        if (!liveChild || !liveTarget) { return false; }
        if (parentKey(liveChild) !== targetParentKey || parentKey(liveTarget) !== targetParentKey) { return false; }

        if (typeof api.rowByKey !== 'function' || typeof api.rowType !== 'function' || typeof api.stackStateForKey !== 'function') {
            return false;
        }
        const apiParent = api.rowByKey(targetParentKey);
        if (!apiParent || !apiParent.length) { return false; }
        if (api.rowType(apiParent) !== 'grid') { return true; }

        const childStack = api.stackStateForKey(childKey) || {};
        const targetStack = api.stackStateForKey(targetKey) || {};
        const childRoot = String(childStack.StackRootKey || '');
        const targetRoot = String(targetStack.StackRootKey || targetKey);
        const childOrder = Number(childStack.StackOrder || 0);
        const targetOrder = Number(targetStack.StackOrder || 0);

        if (position === 'over') {
            /* stackOver makes the new element the root; the root itself has an
             * empty StackRootKey while the old target points back to it. */
            const oldTargetRoot = String(targetStack.StackRootKey || '');
            return childRoot === '' && oldTargetRoot === childKey && targetOrder > childOrder;
        }

        return !!childRoot && childRoot === targetRoot && childOrder > targetOrder;
    }

    function repairExistingPartialAdoption(api, childKey, targetKey, targetParentKey, position) {
        const child = rowByKey(childKey);
        if (!child || parentKey(child) !== targetParentKey) { return false; }
        if (nestedAdoptionComplete(api, childKey, targetKey, targetParentKey, position)) { return true; }

        const parent = typeof api.rowByKey === 'function' ? api.rowByKey(targetParentKey) : null;
        if (!parent || !parent.length || typeof api.rowType !== 'function' || api.rowType(parent) !== 'grid') {
            return nestedAdoptionComplete(api, childKey, targetKey, targetParentKey, position);
        }

        const stackFn = position === 'over' ? api.stackOver : api.stackUnder;
        if (typeof stackFn !== 'function') { return false; }
        if (stackFn(childKey, targetKey) !== true) { return false; }
        return nestedAdoptionComplete(api, childKey, targetKey, targetParentKey, position);
    }

    function adoptNestedDrop(before, targetRow, position) {
        if (!targetRow) { return; }
        const targetKey = rowKey(targetRow);
        const targetParentKey = parentKey(targetRow);
        if (!targetKey || !targetParentKey) { return; }

        let done = false;
        let observer = null;
        let lastChildKey = '';

        function finish() {
            if (done) { return; }
            done = true;
            if (observer) { observer.disconnect(); observer = null; }
        }

        function tryAdopt() {
            if (done) { return true; }
            const newRow = findNewRow(before);
            const liveTarget = rowByKey(targetKey);
            const api = window.__h18LegoFixesV0851;
            if (!newRow || !liveTarget || !api || typeof api.adoptUnder !== 'function') { return false; }

            const childKey = rowKey(newRow);
            const liveParent = parentKey(liveTarget) || targetParentKey;
            if (!childKey || liveParent !== targetParentKey) { return false; }
            lastChildKey = childKey;

            if (nestedAdoptionComplete(api, childKey, targetKey, targetParentKey, position)) {
                finish();
                return true;
            }

            if (parentKey(newRow) === targetParentKey) {
                if (repairExistingPartialAdoption(api, childKey, targetKey, targetParentKey, position)) {
                    finish();
                    return true;
                }
                return false;
            }

            ensureParentOption(childKey, targetParentKey);
            if (api.adoptUnder(childKey, targetKey, position) !== true) { return false; }

            if (nestedAdoptionComplete(api, childKey, targetKey, targetParentKey, position) ||
                repairExistingPartialAdoption(api, childKey, targetKey, targetParentKey, position)) {
                finish();
                return true;
            }
            return false;
        }

        /* Only watch direct row insertion. Subtree observation previously reacted
         * to stack hidden-field and canvas repaint mutations caused by adoption. */
        if (window.MutationObserver) {
            const sections = document.getElementById('h18-page-sections-sortable');
            if (sections) {
                observer = new MutationObserver(function (mutations) {
                    const rowAdded = (mutations || []).some(function (mutation) {
                        return Array.from(mutation.addedNodes || []).some(function (node) {
                            return node && node.nodeType === 1 && node.matches && node.matches('.h18-page-section-row');
                        });
                    });
                    if (rowAdded) { tryAdopt(); }
                });
                observer.observe(sections, { childList: true, subtree: false });
            }
        }

        [0, 30, 80, 160, 320, 600, 1000, 1600, 2400, 3200].forEach(function (delay) {
            window.setTimeout(tryAdopt, delay);
        });
        window.setTimeout(function () { if (!done) { finish(); } }, 3600);
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

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', installLegacyAutoDropCss, { once: true });
    } else {
        installLegacyAutoDropCss();
    }

    document.documentElement.setAttribute('data-h18-lego-palette-side-drop-bridge', '0.8.43');
    document.documentElement.setAttribute('data-h18-lego-palette-vertical-drop-bridge', '0.8.46');
    document.documentElement.setAttribute('data-h18-lego-palette-nested-drop-stability', '0.8.56');
    window.__h18LegoPaletteSideDropBridgeV0843 = {
        version: '0.8.43',
        capabilityVersion: '0.8.56',
        sideZoneAt: sideZoneAt,
        overZoneAt: overZoneAt,
        underZoneAt: underZoneAt,
        canonicalUnderTarget: canonicalUnderTarget,
        canonicalOverTarget: canonicalOverTarget,
        activePaletteDrag: activePaletteDrag
    };
}());
