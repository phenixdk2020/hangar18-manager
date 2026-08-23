(function () {
    'use strict';

    if (window.__h18LegoObserverFilterV0859 || !window.MutationObserver) { return; }

    const NativeMutationObserver = window.MutationObserver;
    let captureNextBodyObserver = true;

    function isSelectionOverlayNode(node) {
        if (!node || node.nodeType !== 1) { return false; }
        return node.matches('.h18-v0851-selection-overlay') || !!node.closest('.h18-v0851-selection-overlay');
    }

    function isRelevantCanvasMutation(record) {
        const target = record && record.target && record.target.nodeType === 1 ? record.target : null;
        if (!target) { return false; }

        // Inspector selection replaces/moves controls frequently. v0.8.51 already
        // has click/input hooks for Inspector enhancement; these mutations must not
        // force a complete Grid/stack render.
        if (target.closest('#h18-page-inspector-target')) { return false; }

        const nodes = Array.prototype.slice.call(record.addedNodes || [])
            .concat(Array.prototype.slice.call(record.removedNodes || []));

        if (nodes.length && nodes.every(isSelectionOverlayNode)) { return false; }

        // Only structural editor/canvas mutations are allowed to wake the old
        // v0.8.51 full render pipeline. Changes elsewhere in wp-admin are ignored.
        if (target.closest('#h18-page-sections-sortable,.h18-builder-canvas')) { return true; }

        return nodes.some(function (node) {
            if (!node || node.nodeType !== 1) { return false; }
            return node.matches('#h18-page-sections-sortable,.h18-builder-canvas,.h18-page-section-row,.h18-v0811-auto-grid,.h18-v0811-auto-box,.h18-v0811-child-card') ||
                !!node.querySelector('#h18-page-sections-sortable,.h18-builder-canvas,.h18-page-section-row,.h18-v0811-auto-grid,.h18-v0811-auto-box,.h18-v0811-child-card');
        });
    }

    function FilteredMutationObserver(callback) {
        let filterThisObserver = false;

        const observer = new NativeMutationObserver(function (records, nativeObserver) {
            if (!filterThisObserver) {
                callback(records, nativeObserver);
                return;
            }

            const relevant = records.filter(isRelevantCanvasMutation);
            if (relevant.length) {
                callback(relevant, nativeObserver);
            }
        });

        const nativeObserve = observer.observe.bind(observer);
        observer.observe = function (target, options) {
            if (
                captureNextBodyObserver &&
                target === document.body &&
                options && options.childList === true && options.subtree === true
            ) {
                captureNextBodyObserver = false;
                filterThisObserver = true;
                // The observer we wanted has now been captured. Restore the native
                // constructor immediately so later runtimes are completely untouched.
                window.MutationObserver = NativeMutationObserver;
            }
            return nativeObserve(target, options);
        };

        return observer;
    }

    FilteredMutationObserver.prototype = NativeMutationObserver.prototype;
    window.MutationObserver = FilteredMutationObserver;

    window.__h18LegoObserverFilterV0859 = {
        version: '0.8.59'
    };
}());
