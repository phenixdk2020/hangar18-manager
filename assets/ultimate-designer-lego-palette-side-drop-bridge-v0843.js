(function () {
    'use strict';

    const SIDE_ZONE_SELECTOR = '.h18-v0838-drop-zone.h18-v0811-side-zone:not(.is-disabled)';
    let redispatching = false;

    function activePaletteDrag() {
        const api = window.__h18LegoSideBySideV0840;
        if (!api || typeof api.activeSource !== 'function') {
            return false;
        }
        const state = api.activeSource() || {};
        return /^palette-/.test(String(state.Mode || ''));
    }

    function directSideZone(target) {
        return target && target.closest ? target.closest(SIDE_ZONE_SELECTOR) : null;
    }

    function sideZoneAt(clientX, clientY) {
        let match = null;
        document.querySelectorAll(SIDE_ZONE_SELECTOR).forEach(function (zone) {
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

    function redirectedDrop(sourceEvent, zone) {
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
            zone.dispatchEvent(redirected);
        } finally {
            redispatching = false;
        }
    }

    window.addEventListener('dragover', function (event) {
        if (redispatching || !activePaletteDrag() || directSideZone(event.target)) {
            return;
        }
        const zone = sideZoneAt(event.clientX, event.clientY);
        if (!zone) {
            return;
        }

        // HTML5 DnD only emits drop for a location whose dragover was accepted.
        // The visual LEGO layer already owns highlighting by coordinates; this
        // bridge only makes the same coordinate hit acceptable to the browser.
        event.preventDefault();
    }, true);

    window.addEventListener('drop', function (event) {
        if (redispatching || !activePaletteDrag() || directSideZone(event.target)) {
            return;
        }
        const zone = sideZoneAt(event.clientX, event.clientY);
        if (!zone) {
            return;
        }

        // Some browsers keep the native drag event targeted at the preview row
        // even while the pointer is visibly inside the overlaid side zone. Stop
        // that fallback before nesting-tools sees it, then replay the SAME drop
        // against the canonical .h18-v0811-side-zone contract. Placement,
        // LayoutParentKey, Auto-kasser and history remain owned by nesting-tools.
        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === 'function') {
            event.stopImmediatePropagation();
        }
        redirectedDrop(event, zone);
    }, true);

    document.documentElement.setAttribute('data-h18-lego-palette-side-drop-bridge', '0.8.43');
    window.__h18LegoPaletteSideDropBridgeV0843 = {
        version: '0.8.43',
        sideZoneAt: sideZoneAt,
        activePaletteDrag: activePaletteDrag
    };
}());
