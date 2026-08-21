(function () {
    'use strict';

    if (window.__h18HistoryAtomicV0840) { return; }

    const inheritedSetTimeout = window.setTimeout.bind(window);
    const inheritedClearTimeout = window.clearTimeout.bind(window);
    let depth = 0;
    let pendingCapture = null;
    let syntheticTimerSerial = 0;

    function isCoreHistoryCallback(callback) {
        return typeof callback === 'function' && callback.name === 'editorHistoryRecordNow';
    }

    function syntheticTimerId() {
        syntheticTimerSerial += 1;
        return -840000 - syntheticTimerSerial;
    }

    window.setTimeout = function (callback, delay) {
        const args = Array.prototype.slice.call(arguments, 2);
        if (depth > 0 && isCoreHistoryCallback(callback)) {
            pendingCapture = { callback: callback, args: args };
            return syntheticTimerId();
        }
        return inheritedSetTimeout.apply(window, [callback, delay].concat(args));
    };

    window.clearTimeout = function (timerId) {
        if (typeof timerId === 'number' && timerId <= -840001 && timerId > -850000) {
            return;
        }
        return inheritedClearTimeout(timerId);
    };

    function begin(label) {
        if (depth === 0) {
            const bridge = window.__h18HistoryCoreBridgeV0821;
            if (bridge && typeof bridge.flushPending === 'function') {
                bridge.flushPending();
            }
            pendingCapture = null;
            document.documentElement.setAttribute('data-h18-v0840-history-atomic', '1');
            if (label) {
                document.documentElement.setAttribute('data-h18-v0840-history-action', String(label));
            }
        }
        depth += 1;
        return depth;
    }

    function end(commit) {
        if (depth <= 0) { return false; }
        depth -= 1;
        if (depth > 0) { return true; }

        document.documentElement.removeAttribute('data-h18-v0840-history-atomic');
        document.documentElement.removeAttribute('data-h18-v0840-history-action');

        const capture = pendingCapture;
        pendingCapture = null;
        if (commit === false || !capture || typeof capture.callback !== 'function') {
            return true;
        }

        // Pass the single final capture back through the existing v0.8.21
        // bridge. That bridge remains authoritative for restore suppression,
        // pending edits and the real editor history stack.
        inheritedSetTimeout.apply(window, [capture.callback, 0].concat(capture.args || []));
        return true;
    }

    function cancel() {
        depth = 0;
        pendingCapture = null;
        document.documentElement.removeAttribute('data-h18-v0840-history-atomic');
        document.documentElement.removeAttribute('data-h18-v0840-history-action');
    }

    window.__h18HistoryAtomicV0840 = {
        version: '0.8.40',
        begin: begin,
        end: end,
        cancel: cancel,
        isActive: function () { return depth > 0; },
        depth: function () { return depth; },
        hasPendingCapture: function () { return Boolean(pendingCapture); }
    };
}());
