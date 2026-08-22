(function () {
    'use strict';

    if (window.__h18LegoLiveHistoryInspectorV0850) { return; }

    const VERSION = '0.8.50';
    let mediaWrapped = false;
    let refreshTimer = 0;
    let removingMedia = false;
    let labelFrame = 0;

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

    function rowKey($row) {
        const $controls = controls($row, '.h18-page-section-key');
        return $controls && $controls.length ? String($controls.first().val() || '').trim() : '';
    }

    function parentKey($row) {
        const $controls = controls($row, '.h18-layout-parent-key');
        return $controls && $controls.length ? String($controls.first().val() || '').trim() : '';
    }

    function escapeSelectorValue(value) {
        const raw = String(value || '');
        if (window.CSS && typeof window.CSS.escape === 'function') { return window.CSS.escape(raw); }
        return raw.replace(/(["\\])/g, '\\$1');
    }

    function activeRows() {
        const $ = jq();
        return $ ? $('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)') : null;
    }

    function nestedNodesForKey(key) {
        const $ = jq();
        if (!$ || !key) { return $ ? $() : null; }
        const escaped = escapeSelectorValue(key);
        return $('.h18-builder-canvas .h18-v0811-auto-box[data-h18-v0811-row="' + escaped + '"],.h18-builder-canvas .h18-v0811-child-card[data-h18-v0811-child="' + escaped + '"]');
    }

    function sourcePreview($row) {
        return $row && $row.length ? $row.children('.h18-canvas-preview').first() : null;
    }

    function applyContainerDesignForRow($row) {
        if (!$row || !$row.length || !parentKey($row)) { return; }
        const key = rowKey($row);
        const $nodes = nestedNodesForKey(key);
        const $preview = sourcePreview($row);
        const previewNode = $preview && $preview.length ? $preview.get(0) : null;
        if (!$nodes || !$nodes.length || !previewNode || !window.getComputedStyle) { return; }

        const style = window.getComputedStyle(previewNode);
        const background = style.backgroundColor || 'transparent';
        const backgroundImage = style.backgroundImage || 'none';
        const borderWidth = style.borderTopWidth || '0px';
        const borderStyle = style.borderTopStyle === 'none' ? (parseFloat(borderWidth) > 0 ? 'solid' : 'none') : style.borderTopStyle;
        const borderColor = style.borderTopColor || 'transparent';
        const radius = style.borderRadius || '0px';

        $nodes.each(function () {
            const node = this;
            node.setAttribute('data-h18-v0850-container-design', '1');
            node.style.backgroundColor = background;
            node.style.backgroundImage = backgroundImage;
            node.style.borderWidth = borderWidth;
            node.style.borderStyle = borderStyle;
            node.style.borderColor = borderColor;
            node.style.borderRadius = radius;
        });
    }

    function applyAllNestedContainerDesign() {
        const $rows = activeRows();
        if (!$rows || !$rows.length) { return; }
        $rows.each(function () { applyContainerDesignForRow(jq()(this)); });
    }

    function reassertSelection() {
        const selection = window.__h18LegoSelectionInspectorV0849;
        if (!selection || typeof selection.applyMarker !== 'function') { return; }
        selection.applyMarker();
        [40, 180, 450].forEach(function (delay) {
            window.setTimeout(function () {
                if (window.__h18LegoSelectionInspectorV0849 && typeof window.__h18LegoSelectionInspectorV0849.applyMarker === 'function') {
                    window.__h18LegoSelectionInspectorV0849.applyMarker();
                }
            }, delay);
        });
    }

    function reconcileNestedPreview($row) {
        if (!$row || !$row.length || !parentKey($row)) {
            reassertSelection();
            return;
        }
        const nesting = window.__h18NestingToolsV0840;
        if (nesting && typeof nesting.refresh === 'function') {
            nesting.refresh();
        }
        applyAllNestedContainerDesign();
        reassertSelection();
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

    function setTextIfDifferent(node, text) {
        if (node && String(node.textContent || '') !== text) { node.textContent = text; }
    }

    function polishContainerDesignLabels() {
        labelFrame = 0;
        const panel = document.getElementById('h18-ud-lego-design-panel');
        if (!panel) { return; }
        Array.from(panel.querySelectorAll('.h18-ud-lego-design-group')).forEach(function (group) {
            const legend = group.querySelector('legend');
            const title = String(legend ? legend.textContent : '').trim();
            if (title === 'Farver og kant' || title === 'Container · farve og kant') {
                setTextIfDifferent(legend, 'Container · farve og kant');
                const description = group.querySelector(':scope > .description');
                setTextIfDifferent(description, 'Baggrund, kant og farve gælder elementets ydre container. Tekst og billede forbliver indholdet inde i containeren.');
                group.querySelectorAll('.h18-ud-lego-design-control').forEach(function (control) {
                    const strong = control.querySelector('strong');
                    const label = String(strong ? strong.textContent : '').trim();
                    if (label === 'Baggrund') { setTextIfDifferent(strong, 'Containerbaggrund'); }
                    else if (label === 'Kantfarve') { setTextIfDifferent(strong, 'Containerkant'); }
                    else if (label === 'Kantbredde') { setTextIfDifferent(strong, 'Kanttykkelse'); }
                });
            }
            if (title === 'Form og effekter') {
                setTextIfDifferent(legend, 'Container · form og effekter');
            }
        });
    }

    function queueContainerLabels() {
        if (labelFrame) { return; }
        labelFrame = window.requestAnimationFrame(polishContainerDesignLabels);
    }

    function installDomHandlers() {
        const $ = jq();
        if (!$) { return; }

        // Canonical Inspector fields are the source of truth. admin.js renders
        // the selected source row immediately; nested Grid/Auto-kasse proxies
        // need one extra reconciliation pass to clone that new preview at once.
        $(document).on('input change', '#h18-page-inspector-target :input,#h18-ud-lego-design-panel :input', function () {
            const $row = selectedRow();
            window.requestAnimationFrame(function () {
                window.requestAnimationFrame(function () {
                    scheduleNestedPreview($row, 0);
                    queueContainerLabels();
                    reassertSelection();
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

        if (window.MutationObserver) {
            new MutationObserver(function (mutations) {
                let relevant = false;
                mutations.forEach(function (mutation) {
                    Array.from(mutation.addedNodes || []).forEach(function (node) {
                        if (node.nodeType !== 1) { return; }
                        if ((node.id === 'h18-ud-lego-design-panel') || (node.querySelector && node.querySelector('#h18-ud-lego-design-panel'))) {
                            relevant = true;
                        }
                    });
                });
                if (relevant) {
                    queueContainerLabels();
                    applyAllNestedContainerDesign();
                    reassertSelection();
                }
            }).observe(document.body, { childList: true, subtree: true });
        }
    }

    function install() {
        wrapWpMedia();
        installDomHandlers();
        // wp.media can be attached late by WordPress media bootstrap.
        [0, 80, 300, 900].forEach(function (delay) {
            window.setTimeout(wrapWpMedia, delay);
        });
        [0, 80, 300].forEach(function (delay) {
            window.setTimeout(function () {
                applyAllNestedContainerDesign();
                queueContainerLabels();
                reassertSelection();
            }, delay);
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
        applyAllNestedContainerDesign: applyAllNestedContainerDesign,
        polishContainerDesignLabels: polishContainerDesignLabels,
        reassertSelection: reassertSelection,
        wrapWpMedia: wrapWpMedia
    };
}());
