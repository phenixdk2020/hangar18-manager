(function () {
    'use strict';

    if (window.__h18HistoryPostRestoreBridgeV0822) { return; }

    let forceNextStructuralCapture = false;
    let forceToken = 0;
    const baseSetTimeout = window.setTimeout.bind(window);

    document.documentElement.setAttribute('data-h18-v0822-post-restore-history', '1');

    function historyGuard() {
        return window.__h18HistoryTransactionV0814 || window.__h18HistoryObserverGuardV0813 || null;
    }

    function activeHistoryBridge() {
        return window.__h18HistoryCoreBridgeV0821 || null;
    }

    function isCoreHistoryCallback(callback) {
        return typeof callback === 'function' && callback.name === 'editorHistoryRecordNow';
    }

    function isKnownStructuralTarget(target) {
        if (!target || !target.closest) { return false; }
        if (target.closest('#h18-editor-undo,#h18-editor-redo,#h18-editor-restore-draft,#h18-command-palette')) {
            return false;
        }
        return Boolean(target.closest(
            '.h18-builder-palette-item,' +
            '.h18-page-section-drag,' +
            '.h18-page-card-drag,' +
            '.h18-canvas-card-drag-handle,' +
            '.h18-navigator-drag,' +
            '.h18-page-section-delete,' +
            '.h18-page-section-duplicate,' +
            '.h18-page-card-delete,' +
            '.h18-page-card-remove,' +
            '.h18-page-card-duplicate,' +
            '#h18-multi-apply,' +
            '.h18-context-item,' +
            '#h18-inspector-paste-design'
        ));
    }

    function armStructuralCapture(event) {
        if (!event || event.isTrusted !== true || !isKnownStructuralTarget(event.target)) { return; }

        forceToken += 1;
        const token = forceToken;
        forceNextStructuralCapture = true;

        // v0.8.21 deliberately blocks trusted-release for the first 100 ms after
        // Undo/Redo so the restore gesture itself cannot reopen history. A new
        // structural gesture is unambiguously new user intent, so preserve this
        // operation immediately and release the old latch just after that window.
        baseSetTimeout(function () {
            if (token !== forceToken) { return; }
            const guard = historyGuard();
            if (guard && typeof guard.markTrustedEdit === 'function') {
                guard.markTrustedEdit(900);
            }
        }, 120);

        baseSetTimeout(function () {
            if (token === forceToken) { forceNextStructuralCapture = false; }
        }, 1500);
    }

    // v0.8.21 owns the normal history scheduling. This narrow successor only
    // bypasses a still-latched restore for the first known structural operation
    // after Undo/Redo. It creates no stack and never touches persistence.
    window.setTimeout = function (callback, delay) {
        const args = Array.prototype.slice.call(arguments, 2);
        const milliseconds = Math.max(0, Number(delay) || 0);

        if (forceNextStructuralCapture && isCoreHistoryCallback(callback) && milliseconds <= 120) {
            forceNextStructuralCapture = false;
            const bridge = activeHistoryBridge();
            if (bridge && typeof bridge.flushPending === 'function') {
                bridge.flushPending();
            }
            callback.apply(window, args);
            return 0;
        }

        return baseSetTimeout.apply(window, [callback, delay].concat(args));
    };

    document.addEventListener('pointerdown', armStructuralCapture, true);
    document.addEventListener('mousedown', armStructuralCapture, true);
    document.addEventListener('dragstart', armStructuralCapture, true);
    document.addEventListener('click', armStructuralCapture, true);

    function installRuntimeIdentity() {
        const status = document.getElementById('h18-editor-history-status');
        if (!status) { return; }
        status.setAttribute('data-h18-history-runtime', '0.8.22');
        status.setAttribute('title', 'History runtime 0.8.22');
        const oldBadge = document.getElementById('h18-history-runtime-badge');
        if (oldBadge) { oldBadge.remove(); }
        const badge = document.createElement('small');
        badge.id = 'h18-history-runtime-badge';
        badge.textContent = 'H0.8.22';
        badge.title = 'Aktiv historikmotor 0.8.22';
        badge.style.cssText = 'margin-left:6px;opacity:.55;font-size:10px;white-space:nowrap';
        status.insertAdjacentElement('afterend', badge);
    }

    if (window.jQuery) {
        window.jQuery(function () { baseSetTimeout(installRuntimeIdentity, 0); });
    } else if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', installRuntimeIdentity, { once: true });
    } else {
        installRuntimeIdentity();
    }

    window.__h18HistoryPostRestoreBridgeV0822 = {
        version: '0.8.22',
        isArmed: function () { return forceNextStructuralCapture === true; }
    };
}());
