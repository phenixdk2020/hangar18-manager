(function () {
    'use strict';

    if (window.__h18HistoryContentBridgeV0823) { return; }

    let forceContentCapture = false;
    let forceToken = 0;
    const baseSetTimeout = window.setTimeout.bind(window);

    document.documentElement.setAttribute('data-h18-v0823-content-history', '1');

    function historyGuard() {
        return window.__h18HistoryTransactionV0814 || window.__h18HistoryObserverGuardV0813 || null;
    }

    function historyBridge() {
        return window.__h18HistoryCoreBridgeV0821 || null;
    }

    function isCoreHistoryCallback(callback) {
        return typeof callback === 'function' && callback.name === 'editorHistoryRecordNow';
    }

    function insideEditor(target) {
        if (!target || !target.closest) { return false; }
        return Boolean(target.closest('#h18-page-editor-form,.h18-visual-builder'));
    }

    function isKnownContentTarget(target) {
        if (!target || !target.closest || !insideEditor(target)) { return false; }
        if (target.closest('#h18-editor-undo,#h18-editor-redo,#h18-editor-restore-draft,#h18-command-palette')) {
            return false;
        }

        if (target.closest(
            '.h18-canvas-image-change,' +
            '.h18-canvas-image-remove,' +
            '.h18-canvas-editable-media,' +
            '.h18-canvas-focal-dot,' +
            '.h18-page-select-bg-media,' +
            '.h18-page-remove-bg-media'
        )) {
            return true;
        }

        const control = target.closest('input,textarea,select,[contenteditable="true"]');
        if (!control) { return false; }

        return Boolean(control.closest(
            '.h18-page-section-body,' +
            '.h18-page-card-row,' +
            '.h18-canvas-direct-controls,' +
            '.h18-canvas-image-tools,' +
            '.h18-canvas-preview'
        ));
    }

    function releaseRestoreLatch(token) {
        if (token !== forceToken) { return; }
        const guard = historyGuard();
        if (guard && typeof guard.markTrustedEdit === 'function') {
            guard.markTrustedEdit(900);
        }
        forceContentCapture = false;
    }

    function armContentCapture(event) {
        if (!event || event.isTrusted !== true || !isKnownContentTarget(event.target)) { return; }
        const bridge = historyBridge();
        if (!bridge || typeof bridge.isLatched !== 'function' || bridge.isLatched() !== true) { return; }

        forceToken += 1;
        const token = forceToken;
        forceContentCapture = true;

        // v0.8.21 blocks trusted release for the first 100 ms after restore.
        // A fresh field/media/design interaction is unambiguously new user intent.
        // Release immediately after that guard window, while the first normal
        // content checkpoint is preserved below instead of being suppressed.
        baseSetTimeout(function () { releaseRestoreLatch(token); }, 120);
        baseSetTimeout(function () {
            if (token === forceToken) { forceContentCapture = false; }
        }, 1800);
    }

    // Preserve the first input/design checkpoint even when it is scheduled while
    // the v0.8.21 restore latch is still active. Wrap the core callback in an
    // anonymous timer so the owner does not discard it at scheduling time. The
    // returned native timer id remains cancellable by the core debounce logic.
    window.setTimeout = function (callback, delay) {
        const args = Array.prototype.slice.call(arguments, 2);
        const milliseconds = Math.max(0, Number(delay) || 0);

        if (forceContentCapture && isCoreHistoryCallback(callback)) {
            return baseSetTimeout(function () {
                callback.apply(window, args);
            }, Math.max(milliseconds, 140));
        }

        return baseSetTimeout.apply(window, [callback, delay].concat(args));
    };

    document.addEventListener('pointerdown', armContentCapture, true);
    document.addEventListener('mousedown', armContentCapture, true);
    document.addEventListener('click', armContentCapture, true);
    document.addEventListener('dblclick', armContentCapture, true);
    document.addEventListener('beforeinput', armContentCapture, true);
    document.addEventListener('input', armContentCapture, true);
    document.addEventListener('change', armContentCapture, true);

    function installRuntimeIdentity() {
        const status = document.getElementById('h18-editor-history-status');
        if (!status) { return; }
        status.setAttribute('data-h18-history-runtime', '0.8.23');
        status.setAttribute('title', 'History runtime 0.8.23');
        const oldBadge = document.getElementById('h18-history-runtime-badge');
        if (oldBadge) { oldBadge.remove(); }
        const badge = document.createElement('small');
        badge.id = 'h18-history-runtime-badge';
        badge.textContent = 'H0.8.23';
        badge.title = 'Aktiv historikmotor 0.8.23';
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

    window.__h18HistoryContentBridgeV0823 = {
        version: '0.8.23',
        isArmed: function () { return forceContentCapture === true; }
    };
}());
