(function () {
    'use strict';

    const SIDE_ZONE_SELECTOR = '.h18-v0838-drop-zone.h18-v0811-side-zone:not(.is-disabled)';
    const UNDER_ZONE_SELECTOR = '.h18-v0838-drop-zone[data-h18-v0838-position="under"]:not(.is-disabled)';
    const ACTIVE_ROW_SELECTOR = '#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)';
    const INSPECTOR_SELECTOR = '#h18-page-inspector-target';
    let redispatching = false;

    function activePaletteDrag() {
        const api = window.__h18LegoSideBySideV0840;
        if (!api || typeof api.activeSource !== 'function') {
            return false;
        }
        const state = api.activeSource() || {};
        return /^palette-/.test(String(state.Mode || ''));
    }

    function directZone(target, selector) {
        return target && target.closest ? target.closest(selector) : null;
    }

    function directSideZone(target) {
        return directZone(target, SIDE_ZONE_SELECTOR);
    }

    function directUnderZone(target) {
        return directZone(target, UNDER_ZONE_SELECTOR);
    }

    function zoneAt(selector, clientX, clientY) {
        let match = null;
        document.querySelectorAll(selector).forEach(function (zone) {
            const rect = zone.getBoundingClientRect();
            if (
                Number(clientX) >= rect.left && Number(clientX) <= rect.right &&
                Number(clientY) >= rect.top && Number(clientY) <= rect.bottom
            ) {
                match = zone;
            }
        });
        return match;
    }

    function sideZoneAt(clientX, clientY) {
        return zoneAt(SIDE_ZONE_SELECTOR, clientX, clientY);
    }

    function underZoneAt(clientX, clientY) {
        return zoneAt(UNDER_ZONE_SELECTOR, clientX, clientY);
    }

    function controlValue(row, selector) {
        if (!row) { return ''; }
        let field = row.querySelector(selector);
        if (!field && row.classList.contains('is-selected')) {
            field = document.querySelector(INSPECTOR_SELECTOR + ' ' + selector);
        }
        return field ? String(field.value || '') : '';
    }

    function parentKey(row) {
        return controlValue(row, '.h18-layout-parent-key');
    }

    function nextTopLevelRow(row) {
        let candidate = row ? row.nextElementSibling : null;
        while (candidate) {
            if (candidate.matches && candidate.matches(ACTIVE_ROW_SELECTOR) && !parentKey(candidate)) {
                return candidate;
            }
            candidate = candidate.nextElementSibling;
        }
        return null;
    }

    function canonicalUnderTarget(zone) {
        const row = zone && zone.closest ? zone.closest('.h18-page-section-row') : null;
        if (!row) { return null; }

        // The editor stores nested children as flat source rows immediately after
        // their parent. "Under" must therefore skip those hidden child rows and
        // target the next top-level row. If none exists, bubble from the sortable
        // root so the existing base palette handler appends the new section.
        const next = nextTopLevelRow(row);
        if (next) {
            return next.querySelector('.h18-canvas-preview') || next;
        }
        return document.getElementById('h18-page-sections-sortable') || document.querySelector('.h18-builder-canvas');
    }

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
                try {
                    Object.defineProperty(redirected, name, { value: init[name] });
                } catch (ignored) {
                    // Old browser fallback only; target identity is the critical contract.
                }
            });
        }

        redispatching = true;
        try {
            target.dispatchEvent(redirected);
        } finally {
            redispatching = false;
        }
        return true;
    }

    function stopOriginalDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === 'function') {
            event.stopImmediatePropagation();
        }
    }

    window.addEventListener('dragover', function (event) {
        if (redispatching || !activePaletteDrag()) {
            return;
        }
        if (directSideZone(event.target) || directUnderZone(event.target)) {
            return;
        }
        const zone = sideZoneAt(event.clientX, event.clientY) || underZoneAt(event.clientX, event.clientY);
        if (!zone) {
            return;
        }

        // HTML5 DnD only emits drop for a location whose dragover was accepted.
        // The visual LEGO layer already owns highlighting by coordinates; this
        // bridge only makes the same coordinate hit acceptable to the browser.
        event.preventDefault();
    }, true);

    window.addEventListener('drop', function (event) {
        if (redispatching || !activePaletteDrag()) {
            return;
        }

        const directSide = directSideZone(event.target);
        if (directSide) {
            // Already on the canonical nesting-tools side-zone contract.
            return;
        }

        const directUnder = directUnderZone(event.target);
        if (directUnder) {
            const target = canonicalUnderTarget(directUnder);
            if (!target) { return; }
            stopOriginalDrop(event);
            redirectedDrop(event, target);
            return;
        }

        const side = sideZoneAt(event.clientX, event.clientY);
        if (side) {
            // Some browsers keep the native drag event targeted at the preview row
            // even while the pointer is visibly inside the overlaid side zone. Stop
            // that fallback before nesting-tools sees it, then replay the SAME drop
            // against the canonical .h18-v0811-side-zone contract. Placement,
            // LayoutParentKey, Auto-kasser and history remain owned by nesting-tools.
            stopOriginalDrop(event);
            redirectedDrop(event, side);
            return;
        }

        const under = underZoneAt(event.clientX, event.clientY);
        if (!under) {
            return;
        }

        // The base WordPress palette handler intentionally accepts only a
        // "$before" row. Without this translation both Over and Under therefore
        // resolve to "insert before target". Re-target Under to the next top-level
        // row (or sortable root) so the existing base handler performs the correct
        // operation without introducing a second creator/order/persistence owner.
        const target = canonicalUnderTarget(under);
        if (!target) { return; }
        stopOriginalDrop(event);
        redirectedDrop(event, target);
    }, true);

    // Preserve the historical side-drop marker for existing contracts and expose
    // the new vertical capability separately.
    document.documentElement.setAttribute('data-h18-lego-palette-side-drop-bridge', '0.8.43');
    document.documentElement.setAttribute('data-h18-lego-palette-vertical-drop-bridge', '0.8.46');
    window.__h18LegoPaletteSideDropBridgeV0843 = {
        version: '0.8.43',
        capabilityVersion: '0.8.46',
        sideZoneAt: sideZoneAt,
        underZoneAt: underZoneAt,
        canonicalUnderTarget: canonicalUnderTarget,
        activePaletteDrag: activePaletteDrag
    };
}());
