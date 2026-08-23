(function () {
    'use strict';

    if (window.__h18LegoRenderObserverScopeV0861 || !window.MutationObserver) { return; }

    const NativeMutationObserver = window.MutationObserver;

    function isLegacyFullRenderCallback(callback) {
        const source = String(callback || '');
        return source.indexOf('suppressObserverUntil') !== -1 &&
            source.indexOf('scheduleRender()') !== -1 &&
            source.indexOf('queueInspector()') !== -1;
    }

    function relevantStructuralMutation(record) {
        if (!record) { return false; }
        const target = record.target && record.target.nodeType === 1 ? record.target : null;
        if (target && target.closest && target.closest('#h18-page-sections-sortable,.h18-builder-canvas')) {
            return true;
        }

        const nodes = Array.prototype.slice.call(record.addedNodes || [])
            .concat(Array.prototype.slice.call(record.removedNodes || []));

        return nodes.some(function (node) {
            if (!node || node.nodeType !== 1) { return false; }
            if (node.matches && node.matches('#h18-page-sections-sortable,.h18-builder-canvas,.h18-page-section-row,.h18-v0811-auto-grid,.h18-v0811-auto-box,.h18-v0811-child-card')) {
                return true;
            }
            return !!(node.querySelector && node.querySelector('#h18-page-sections-sortable,.h18-builder-canvas,.h18-page-section-row,.h18-v0811-auto-grid,.h18-v0811-auto-box,.h18-v0811-child-card'));
        });
    }

    function ScopedMutationObserver(callback) {
        if (!isLegacyFullRenderCallback(callback)) {
            return new NativeMutationObserver(callback);
        }

        // This is the single v0.8.51 body-wide observer that used to rebuild
        // every Grid/stack when Inspector markup changed. Filter only this one.
        const observer = new NativeMutationObserver(function (records, nativeObserver) {
            const relevant = records.filter(relevantStructuralMutation);
            if (relevant.length) {
                callback(relevant, nativeObserver);
            }
        });

        // The target callback has been identified; later observers must use the
        // browser-native constructor without any interception.
        window.MutationObserver = NativeMutationObserver;
        return observer;
    }

    ScopedMutationObserver.prototype = NativeMutationObserver.prototype;
    window.MutationObserver = ScopedMutationObserver;

    window.__h18LegoRenderObserverScopeV0861 = {
        version: '0.8.61'
    };
}());
