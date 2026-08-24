(function () {
    'use strict';

    if (window.__h18LegoRuntimeSafetyV0883) { return; }

    const VERSION = '0.8.83';
    const TRACE_UI_SELECTOR = '#h18-ultimate-designer-trace-v0876,#h18-trace-tools-v0879,#h18-trace-recording-indicator-v0879';
    const NativeMutationObserver = window.MutationObserver;
    let editorDragActive = false;
    let lastDragActivity = 0;
    let watchdogTimer = 0;
    let safetyDispatchingDragEnd = false;

    function isTraceObserver(callback) {
        const source = String(callback || '');
        return source.indexOf('mutationBucket') !== -1 &&
            source.indexOf('DOM_MUTATIONS') !== -1 &&
            source.indexOf('MUTATION_MS') !== -1;
    }

    function insideTraceUi(node) {
        if (!node) { return false; }
        if (node.nodeType === 3) { node = node.parentNode; }
        if (!node || node.nodeType !== 1) { return false; }
        if (node.matches && node.matches(TRACE_UI_SELECTOR)) { return true; }
        return !!(node.closest && node.closest(TRACE_UI_SELECTOR));
    }

    function addedOrRemovedTraceUi(record) {
        const nodes = Array.prototype.slice.call(record && record.addedNodes || [])
            .concat(Array.prototype.slice.call(record && record.removedNodes || []));
        return nodes.length > 0 && nodes.every(function (node) {
            return node.nodeType !== 1 || insideTraceUi(node);
        });
    }

    function traceUiMutation(record) {
        if (!record) { return false; }
        if (insideTraceUi(record.target)) { return true; }
        return record.type === 'childList' && addedOrRemovedTraceUi(record);
    }

    if (NativeMutationObserver) {
        function TraceSafeMutationObserver(callback) {
            if (!isTraceObserver(callback)) {
                return new NativeMutationObserver(callback);
            }

            const observer = new NativeMutationObserver(function (records, nativeObserver) {
                const relevant = records.filter(function (record) { return !traceUiMutation(record); });
                if (relevant.length) { callback(relevant, nativeObserver); }
            });

            // Only the known trace observer needs this isolation. Restore the
            // constructor afterwards so unrelated late runtimes stay native.
            window.MutationObserver = NativeMutationObserver;
            return observer;
        }

        TraceSafeMutationObserver.prototype = NativeMutationObserver.prototype;
        window.MutationObserver = TraceSafeMutationObserver;
    }

    function editorSections() {
        return document.getElementById('h18-page-sections-sortable');
    }

    function clearVisualDragState() {
        const sections = editorSections();
        const api = window.__h18LegoDropZonesV0838;
        if (api && typeof api.clear === 'function') {
            try { api.clear(); } catch (ignore) {}
        }

        document.querySelectorAll('.h18-v0838-drop-overlay').forEach(function (node) { node.remove(); });
        document.querySelectorAll('.h18-v0838-drop-zone.is-active').forEach(function (node) { node.classList.remove('is-active'); });
        document.querySelectorAll('.h18-ud-nesting-drop-target,.h18-v0814-auto-drop-target').forEach(function (node) {
            node.classList.remove('h18-ud-nesting-drop-target', 'h18-v0814-auto-drop-target');
        });
        document.querySelectorAll('.h18-v0814-auto-drop-active').forEach(function (node) { node.classList.remove('h18-v0814-auto-drop-active'); });

        if (sections) {
            sections.classList.remove(
                'h18-v0838-drop-zones-active',
                'h18-v0838-box-source',
                'h18-v0838-element-source',
                'h18-v0811-box-drag',
                'h18-ud-existing-row-drag'
            );
        }
    }

    function clearTimers() {
        if (watchdogTimer) {
            window.clearTimeout(watchdogTimer);
            watchdogTimer = 0;
        }
    }

    function dispatchCleanupDragEnd() {
        if (safetyDispatchingDragEnd) { return; }
        safetyDispatchingDragEnd = true;
        try {
            document.dispatchEvent(new Event('dragend', { bubbles: true, cancelable: false }));
        } catch (ignore) {
            // Direct visual cleanup below is still safe if synthetic dispatch is unavailable.
        } finally {
            safetyDispatchingDragEnd = false;
        }
    }

    function forceDragCleanup(reason) {
        clearTimers();
        const wasActive = editorDragActive;
        editorDragActive = false;
        clearVisualDragState();
        if (wasActive) { dispatchCleanupDragEnd(); }
        clearVisualDragState();
        document.documentElement.setAttribute('data-h18-v0883-last-drag-reset', String(reason || 'cleanup'));
    }

    function armWatchdog() {
        clearTimers();
        watchdogTimer = window.setTimeout(function check() {
            if (!editorDragActive) { watchdogTimer = 0; return; }
            if (Date.now() - lastDragActivity >= 12000) {
                forceDragCleanup('watchdog');
                return;
            }
            watchdogTimer = window.setTimeout(check, 3000);
        }, 3000);
    }

    function editorDragSource(target) {
        return target && target.closest
            ? target.closest('.h18-builder-palette-item,.h18-page-section-row')
            : null;
    }

    document.addEventListener('dragstart', function (event) {
        if (!editorSections() || !editorDragSource(event.target)) { return; }
        editorDragActive = true;
        lastDragActivity = Date.now();
        armWatchdog();
        document.documentElement.setAttribute('data-h18-v0883-drag-state', 'active');
    }, true);

    document.addEventListener('dragover', function () {
        if (editorDragActive) { lastDragActivity = Date.now(); }
    }, true);

    // Installed before the palette redirect bridge. That bridge can call
    // stopImmediatePropagation() on the native drop; this queued cleanup still
    // runs after the synchronous drop chain and cannot be skipped by that call.
    window.addEventListener('drop', function () {
        if (!editorDragActive) { return; }
        lastDragActivity = Date.now();
        const settle = function () { if (editorDragActive) { forceDragCleanup('drop-settle'); } };
        if (typeof window.queueMicrotask === 'function') { window.queueMicrotask(settle); }
        else { Promise.resolve().then(settle); }
    }, true);

    document.addEventListener('dragend', function () {
        if (safetyDispatchingDragEnd) { return; }
        editorDragActive = false;
        clearTimers();
        window.setTimeout(clearVisualDragState, 0);
        document.documentElement.setAttribute('data-h18-v0883-drag-state', 'idle');
    }, true);

    document.addEventListener('keydown', function (event) {
        if (editorDragActive && String(event.key || '') === 'Escape') { forceDragCleanup('escape'); }
    }, true);

    window.addEventListener('blur', function () {
        if (editorDragActive) { forceDragCleanup('window-blur'); }
    });

    document.addEventListener('visibilitychange', function () {
        if (document.hidden && editorDragActive) { forceDragCleanup('visibility-hidden'); }
    });

    document.documentElement.setAttribute('data-h18-lego-runtime-safety', VERSION);
    window.__h18LegoRuntimeSafetyV0883 = {
        version: VERSION,
        cleanup: forceDragCleanup,
        isDragActive: function () { return editorDragActive; }
    };
}());
