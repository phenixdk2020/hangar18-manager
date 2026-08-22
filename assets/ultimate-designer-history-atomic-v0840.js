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

    function end(commit, immediate) {
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

        // Normal transactions still hand the single final capture back through
        // the existing v0.8.21 owner asynchronously. LEGO-046 may close a prior
        // palette gesture synchronously when a NEW trusted palette gesture drops
        // before the old 520 ms settling window has expired. The synchronous path
        // is required so the previous checkpoint is serialized BEFORE the new
        // base palette handler mutates the DOM.
        if (immediate === true) {
            capture.callback.apply(window, capture.args || []);
        } else {
            inheritedSetTimeout.apply(window, [capture.callback, 0].concat(capture.args || []));
        }
        return true;
    }

    function cancel() {
        depth = 0;
        pendingCapture = null;
        document.documentElement.removeAttribute('data-h18-v0840-history-atomic');
        document.documentElement.removeAttribute('data-h18-v0840-history-action');
    }

    function installEditorDragTransactions() {
        const jq = window.jQuery;
        if (!jq) { return; }
        const $sections = jq('#h18-page-sections-sortable');
        if (!$sections.length) { return; }

        let paletteDrag = false;
        let paletteAtomicActive = false;
        let paletteGestureSerial = 0;
        let activePaletteGestureSerial = 0;
        let sortAtomicActive = false;

        document.addEventListener('dragstart', function (event) {
            const item = event.target && event.target.closest
                ? event.target.closest('.h18-builder-palette-item')
                : null;
            paletteDrag = Boolean(item);
            if (paletteDrag) {
                paletteGestureSerial += 1;
            }
        }, true);

        // The nesting runtime's capture-phase drop handler is registered before
        // this adapter. Beginning here therefore still happens before the base
        // canvas bubble handler creates a new section, while the nesting runtime
        // has already resolved whether the drop is side/inside/Auto.
        document.addEventListener('drop', function (event) {
            if (!paletteDrag) { return; }
            const target = event.target && event.target.closest
                ? event.target.closest('#h18-page-sections-sortable,.h18-builder-canvas')
                : null;
            if (!target) { return; }

            const gesture = paletteGestureSerial || 1;

            if (paletteAtomicActive) {
                if (activePaletteGestureSerial === gesture) {
                    // Same native gesture can be re-dispatched by the visual
                    // side/vertical bridges. It still belongs to one transaction.
                    return;
                }

                // A genuinely new palette gesture started before the previous
                // 520 ms settle timer fired. Commit the previous pending snapshot
                // synchronously while the DOM still represents the previous user
                // action, then open a fresh transaction for the new drop.
                paletteAtomicActive = false;
                activePaletteGestureSerial = 0;
                end(true, true);
            }

            paletteAtomicActive = true;
            activePaletteGestureSerial = gesture;
            begin('palette-drag-drop');
            inheritedSetTimeout(function () {
                // Ignore stale settle timers belonging to an earlier gesture.
                if (!paletteAtomicActive || activePaletteGestureSerial !== gesture) {
                    return;
                }
                paletteAtomicActive = false;
                activePaletteGestureSerial = 0;
                end(true);
            }, 520);
        }, true);

        document.addEventListener('dragend', function () {
            paletteDrag = false;
        }, true);

        // Start before jQuery Sortable can expose intermediate DOM order to the
        // editor history observer. The delayed end covers the existing
        // createAutoForRows() + composition refresh timers without owning them.
        $sections.on('sortstart.h18V0840HistoryAtomic', function (event, ui) {
            const $row = ui && ui.item ? ui.item : jq();
            if (!$row.length || sortAtomicActive) { return; }
            sortAtomicActive = true;
            begin('existing-row-drag-drop');
        });

        $sections.on('sortstop.h18V0840HistoryAtomic', function () {
            if (!sortAtomicActive) { return; }
            sortAtomicActive = false;
            inheritedSetTimeout(function () { end(true); }, 360);
        });
    }

    document.documentElement.setAttribute('data-h18-v0846-history-gesture-boundary', '1');
    window.__h18HistoryAtomicV0840 = {
        version: '0.8.40',
        capabilityVersion: '0.8.46',
        begin: begin,
        end: end,
        cancel: cancel,
        isActive: function () { return depth > 0; },
        depth: function () { return depth; },
        hasPendingCapture: function () { return Boolean(pendingCapture); }
    };

    if (window.jQuery) {
        window.jQuery(installEditorDragTransactions);
    } else if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', installEditorDragTransactions, { once: true });
    } else {
        installEditorDragTransactions();
    }
}());
