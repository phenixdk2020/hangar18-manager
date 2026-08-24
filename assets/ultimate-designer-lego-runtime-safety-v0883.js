(function () {
    'use strict';

    if (window.__h18LegoRuntimeSafetyV0883) { return; }

    const VERSION = '0.8.84';
    const TRACE_UI_SELECTOR = '#h18-ultimate-designer-trace-v0876,#h18-trace-tools-v0879,#h18-trace-recording-indicator-v0879';
    const TRACE_PANEL_ID = 'h18-ultimate-designer-trace-v0876';
    const NativeMutationObserver = window.MutationObserver;

    function callbackSource(callback) {
        try { return Function.prototype.toString.call(callback); }
        catch (ignore) { return String(callback || ''); }
    }

    function isTraceObserver(callback) {
        const source = callbackSource(callback);
        return source.indexOf('mutationBucket') !== -1 &&
            source.indexOf('DOM_MUTATIONS') !== -1 &&
            source.indexOf('MUTATION_MS') !== -1;
    }

    function isInspectorSelectionObserver(callback) {
        const source = callbackSource(callback);
        return source.indexOf('clarifyInspectorControls') !== -1 &&
            source.indexOf('refreshSelectedCanvasMarker') !== -1;
    }

    function insideTraceUi(node) {
        if (!node) { return false; }
        if (node.nodeType === 3) { node = node.parentNode; }
        if (!node || node.nodeType !== 1) { return false; }
        if (node.matches && node.matches(TRACE_UI_SELECTOR)) { return true; }
        return !!(node.closest && node.closest(TRACE_UI_SELECTOR));
    }

    function insideInspector(node) {
        if (!node) { return false; }
        if (node.nodeType === 3) { node = node.parentNode; }
        if (!node || node.nodeType !== 1) { return false; }
        if (node.id === 'h18-page-inspector-target') { return true; }
        return !!(node.closest && node.closest('#h18-page-inspector-target'));
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

    function keepTracePanelVisible() {
        const panel = document.getElementById(TRACE_PANEL_ID);
        if (!panel) { return false; }
        panel.style.setProperty('position', 'fixed', 'important');
        panel.style.setProperty('left', '206px', 'important');
        panel.style.setProperty('right', 'auto', 'important');
        panel.style.setProperty('top', 'auto', 'important');
        panel.style.setProperty('bottom', '76px', 'important');
        panel.style.setProperty('width', 'min(760px,calc(100vw - 238px))', 'important');
        panel.style.setProperty('max-height', 'calc(100vh - 120px)', 'important');
        panel.style.setProperty('overflow', 'auto', 'important');
        panel.style.setProperty('z-index', '2147483100', 'important');
        panel.setAttribute('data-h18-v0884-viewport-safe', '1');
        return true;
    }

    if (NativeMutationObserver) {
        function RuntimeSafeMutationObserver(callback) {
            if (isInspectorSelectionObserver(callback)) {
                return new NativeMutationObserver(function (records, nativeObserver) {
                    const relevant = records.filter(function (record) {
                        return !insideInspector(record && record.target);
                    });
                    if (relevant.length) {
                        callback(relevant, nativeObserver);
                    }
                });
            }

            if (isTraceObserver(callback)) {
                return new NativeMutationObserver(function (records, nativeObserver) {
                    const relevant = records.filter(function (record) { return !traceUiMutation(record); });
                    if (relevant.length) { callback(relevant, nativeObserver); }
                });
            }

            return new NativeMutationObserver(callback);
        }

        RuntimeSafeMutationObserver.prototype = NativeMutationObserver.prototype;
        window.MutationObserver = RuntimeSafeMutationObserver;

        const tracePanelObserver = new NativeMutationObserver(function () {
            if (keepTracePanelVisible()) { tracePanelObserver.disconnect(); }
        });
        if (document.documentElement) {
            tracePanelObserver.observe(document.documentElement, { childList: true, subtree: true });
        }
        document.addEventListener('DOMContentLoaded', keepTracePanelVisible, { once: true });
    }

    /*
     * v0.8.84 rollback contract:
     * This compatibility layer MUST NOT listen to dragstart/dragover/drop/dragend,
     * synthesize drag events, remove placement overlays, or own placement state.
     * The proven v0.8.82 stack (v0838/v0843/v0851/v0862) is again the sole
     * placement authority for left/right/over/under/inside behaviour.
     */
    document.documentElement.setAttribute('data-h18-lego-runtime-safety', VERSION);
    document.documentElement.setAttribute('data-h18-v0884-placement-owner', 'legacy-v0838-v0862');
    window.__h18LegoRuntimeSafetyV0883 = {
        version: VERSION,
        placementOwner: 'legacy-v0838-v0862',
        keepTracePanelVisible: keepTracePanelVisible,
        cleanup: function () {},
        isDragActive: function () { return false; }
    };
}());
