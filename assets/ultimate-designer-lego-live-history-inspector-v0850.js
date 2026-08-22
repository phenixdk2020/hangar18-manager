(function () {
    'use strict';

    if (window.__h18LegoLiveHistoryInspectorV0850) { return; }

    const VERSION = '0.8.50';
    let mediaWrapped = false;
    let refreshTimer = 0;
    let removingMedia = false;

    function jq() {
        return window.jQuery || null;
    }

    function selectedRow() {
        const $ = jq();
        return $ ? $('#h18-page-sections-sortable > .h18-page-section-row.is-selected').first() : null;
    }

    function controls($row, selector) {
        const $ = jq();
        if (!$ || !$row || !$row.length) { return $ ? $() : null; }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($('#h18-page-inspector-target').find(selector));
        }
        return $result;
    }

    function parentKey($row) {
        const $controls = controls($row, '.h18-layout-parent-key');
        return $controls && $controls.length ? String($controls.first().val() || '').trim() : '';
    }

    function reconcileNestedPreview($row) {
        if (!$row || !$row.length || !parentKey($row)) { return; }
        const nesting = window.__h18NestingToolsV0840;
        if (nesting && typeof nesting.refresh === 'function') {
            nesting.refresh();
        }
    }

    function scheduleNestedPreview($row, delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(function () {
            window.requestAnimationFrame(function () {
                reconcileNestedPreview($row && $row.length ? $row : selectedRow());
            });
        }, typeof delay === 'number' ? delay : 0);
    }

    function historyAtomic() {
        const atomic = window.__h18HistoryAtomicV0840;
        return atomic && typeof atomic.begin === 'function' && typeof atomic.end === 'function' ? atomic : null;
    }

    function beginHistory(label) {
        const atomic = historyAtomic();
        if (!atomic) { return false; }
        atomic.begin(label);
        return true;
    }

    function endHistory(commit) {
        const atomic = historyAtomic();
        if (!atomic || !atomic.isActive || !atomic.isActive()) { return; }
        atomic.end(commit !== false, true);
    }

    function wrapWpMedia() {
        if (mediaWrapped || !window.wp || typeof window.wp.media !== 'function') { return false; }

        const nativeMedia = window.wp.media;
        const wrappedMedia = function () {
            const frame = nativeMedia.apply(this, arguments);
            if (!frame || typeof frame.on !== 'function') { return frame; }

            let transactionStarted = false;
            frame.on('select', function () {
                // Register before the editor's frame.on('select') callback. The
                // base callback then mutates MediaId/MediaUrl inside this atomic
                // history transaction instead of merging the image with a later
                // text/drop action.
                transactionStarted = beginHistory('media-selection');
                window.setTimeout(function () {
                    const $row = selectedRow();
                    scheduleNestedPreview($row, 0);
                    if (transactionStarted) {
                        endHistory(true);
                        transactionStarted = false;
                    }
                }, 0);
            });
            frame.on('close', function () {
                if (!transactionStarted) { return; }
                endHistory(false);
                transactionStarted = false;
            });
            return frame;
        };

        Object.keys(nativeMedia).forEach(function (key) {
            try { wrappedMedia[key] = nativeMedia[key]; } catch (ignore) { /* readonly */ }
        });
        if (nativeMedia.prototype) { wrappedMedia.prototype = nativeMedia.prototype; }
        wrappedMedia.__h18V0850Base = nativeMedia;
        window.wp.media = wrappedMedia;
        mediaWrapped = true;
        return true;
    }

    function installDomHandlers() {
        const $ = jq();
        if (!$) { return; }

        // Canonical Inspector fields are the source of truth. admin.js renders
        // the selected source row immediately; nested Grid/Auto-kasse proxies
        // need one extra reconciliation pass to clone that new preview at once.
        $(document).on('input change', '#h18-page-inspector-target :input', function () {
            const $row = selectedRow();
            window.requestAnimationFrame(function () {
                window.requestAnimationFrame(function () {
                    scheduleNestedPreview($row, 0);
                });
            });
        });

        // Programmatic media changes do not necessarily emit input/change.
        // The media wrapper covers selection; removal gets its own explicit
        // history boundary and nested-preview reconciliation here.
        document.addEventListener('click', function (event) {
            const target = event.target && event.target.closest
                ? event.target.closest('.h18-page-remove-media')
                : null;
            if (!target || removingMedia) { return; }
            removingMedia = beginHistory('media-remove');
            window.setTimeout(function () {
                scheduleNestedPreview(selectedRow(), 0);
                if (removingMedia) {
                    endHistory(true);
                    removingMedia = false;
                }
            }, 0);
        }, true);
    }

    function install() {
        wrapWpMedia();
        installDomHandlers();
        // wp.media can be attached late by WordPress media bootstrap.
        [0, 80, 300, 900].forEach(function (delay) {
            window.setTimeout(wrapWpMedia, delay);
        });
        document.documentElement.setAttribute('data-h18-lego-live-history-inspector', VERSION);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }

    window.__h18LegoLiveHistoryInspectorV0850 = {
        version: VERSION,
        reconcileNestedPreview: reconcileNestedPreview,
        wrapWpMedia: wrapWpMedia
    };
}());
