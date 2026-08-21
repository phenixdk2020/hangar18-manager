jQuery(function ($) {
    'use strict';

    const config = window.H18LegoResizeV0841 || {};
    const $form = $('#h18-page-editor-form');
    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector-target');
    const $canvas = $('.h18-builder-canvas').first();
    if (!$form.length || !$sections.length || !$canvas.length) { return; }

    const COLUMN_COUNT = Math.max(2, parseInt(config.columns, 10) || 12);
    const STATE_CLASS = 'h18-lego-layout-span-state-json';
    const SUBMIT_ATTR = 'data-h18-lego-layout-span-submit';
    const AUTO_LABEL = 'Auto-kasser';
    let decorateFrame = 0;
    let resizeDrag = null;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($inspector.find(selector));
        }
        return $result;
    }

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || $row.attr('data-key') || '');
    }

    function parentKey($row) {
        return String(controls($row, '.h18-layout-parent-key').first().val() || '');
    }

    function rowLabel($row) {
        return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
    }

    function rowByKey(key) {
        key = String(key || '');
        if (!key) { return $(); }
        return activeRows().filter(function () { return rowKey($(this)) === key; }).first();
    }

    function isAuto($row) {
        return Boolean(
            $row && $row.length &&
            String($row.attr('data-section-type') || '') === 'grid' &&
            rowLabel($row) === AUTO_LABEL
        );
    }

    function canvasDevice() {
        return String($canvas.attr('data-canvas-device') || 'desktop').toLowerCase();
    }

    function directChildren($auto) {
        const key = rowKey($auto);
        if (!key) { return $(); }
        return activeRows().filter(function () { return parentKey($(this)) === key; });
    }

    function pageSlug() {
        return String($form.find('[name="page_slug"]').first().val() || '').trim();
    }

    function storedSections() {
        const pages = config.pages && typeof config.pages === 'object' ? config.pages : {};
        const page = pages[pageSlug()] && typeof pages[pageSlug()] === 'object' ? pages[pageSlug()] : {};
        return page.Sections && typeof page.Sections === 'object' ? page.Sections : {};
    }

    function clampSpan(value) {
        const parsed = parseInt(value, 10);
        if (!Number.isFinite(parsed) || parsed <= 0) { return 0; }
        return Math.max(1, Math.min(COLUMN_COUNT, parsed));
    }

    function normalizeState(raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        const desktop = raw.Desktop && typeof raw.Desktop === 'object' ? raw.Desktop : {};
        const tablet = raw.Tablet && typeof raw.Tablet === 'object' ? raw.Tablet : {};
        const mobile = raw.Mobile && typeof raw.Mobile === 'object' ? raw.Mobile : {};
        return {
            SchemaVersion: 1,
            Desktop: { Span: clampSpan(desktop.Span) },
            Tablet: { InheritDesktop: true, Span: clampSpan(tablet.Span) },
            Mobile: { InheritDesktop: true, Span: clampSpan(mobile.Span) }
        };
    }

    function canonicalField($row) {
        return controls($row, '.' + STATE_CLASS).first();
    }

    function ensureCanonicalField($row, state) {
        let $field = canonicalField($row);
        if ($field.length) { return $field; }
        $field = $('<input>', {
            type: 'hidden',
            class: STATE_CLASS,
            value: JSON.stringify(normalizeState(state || {})),
            'data-h18-v0841-layout-span': '1'
        });
        let $body = $row.children('.h18-page-section-body').first();
        if (!$body.length) { $body = $row.find('.h18-page-section-body').first(); }
        ($body.length ? $body : $row).append($field);
        return $field;
    }

    function stateForRow($row) {
        const $field = canonicalField($row);
        if ($field.length) {
            try { return normalizeState(JSON.parse(String($field.val() || '{}'))); }
            catch (error) { return normalizeState({}); }
        }
        const key = rowKey($row);
        const stored = storedSections();
        return normalizeState(key && stored[key] && typeof stored[key] === 'object' ? stored[key] : {});
    }

    function hydrateRow($row) {
        if (!$row || !$row.length) { return; }
        const state = stateForRow($row);
        ensureCanonicalField($row, state).val(JSON.stringify(state));
        $row.attr('data-h18-v0841-explicit-span', state.Desktop.Span > 0 ? String(state.Desktop.Span) : 'auto');
    }

    function writeDesktopSpan($row, span, captureHistory) {
        if (!$row || !$row.length) { return; }
        const state = stateForRow($row);
        state.Desktop.Span = Math.max(1, Math.min(COLUMN_COUNT, parseInt(span, 10) || 1));
        state.Tablet.InheritDesktop = true;
        state.Mobile.InheritDesktop = true;
        const $field = ensureCanonicalField($row, state);
        $field.val(JSON.stringify(normalizeState(state)));
        $row.attr('data-h18-v0841-explicit-span', String(state.Desktop.Span));
        if (captureHistory) { $field.trigger('input'); }
    }

    function equalSpans(count) {
        count = Math.max(1, Math.min(COLUMN_COUNT, parseInt(count, 10) || 1));
        const base = Math.floor(COLUMN_COUNT / count);
        let remainder = COLUMN_COUNT - (base * count);
        const result = [];
        for (let index = 0; index < count; index += 1) {
            result.push(base + (remainder > 0 ? 1 : 0));
            if (remainder > 0) { remainder -= 1; }
        }
        return result;
    }

    function reduceToBudget(values, budget) {
        const result = values.slice();
        let total = result.reduce(function (sum, value) { return sum + value; }, 0);
        while (total > budget) {
            let best = -1;
            for (let index = 0; index < result.length; index += 1) {
                if (result[index] > 1 && (best < 0 || result[index] > result[best])) { best = index; }
            }
            if (best < 0) { break; }
            result[best] -= 1;
            total -= 1;
        }
        return result;
    }

    function distribute(total, count) {
        if (count <= 0) { return []; }
        const base = Math.floor(total / count);
        let remainder = total - (base * count);
        const result = [];
        for (let index = 0; index < count; index += 1) {
            result.push(Math.max(1, base + (remainder > 0 ? 1 : 0)));
            if (remainder > 0) { remainder -= 1; }
        }
        return result;
    }

    function effectiveSpans($children) {
        const rows = $children.toArray().map(function (node) { return $(node); });
        if (!rows.length) { return []; }
        if (rows.length > COLUMN_COUNT) {
            return rows.map(function () { return 1; });
        }

        const explicit = rows.map(function ($row) {
            hydrateRow($row);
            return clampSpan(stateForRow($row).Desktop.Span);
        });
        if (explicit.every(function (span) { return span === 0; })) {
            return equalSpans(rows.length);
        }

        const autoIndexes = [];
        const explicitIndexes = [];
        explicit.forEach(function (span, index) {
            if (span > 0) { explicitIndexes.push(index); }
            else { autoIndexes.push(index); }
        });

        const result = new Array(rows.length).fill(0);
        let explicitValues = explicitIndexes.map(function (index) { return explicit[index]; });
        const explicitBudget = COLUMN_COUNT - autoIndexes.length;
        explicitValues = reduceToBudget(explicitValues, Math.max(explicitIndexes.length, explicitBudget));
        explicitIndexes.forEach(function (index, valueIndex) { result[index] = explicitValues[valueIndex]; });

        let used = result.reduce(function (sum, value) { return sum + value; }, 0);
        if (autoIndexes.length) {
            const autoValues = distribute(Math.max(autoIndexes.length, COLUMN_COUNT - used), autoIndexes.length);
            autoIndexes.forEach(function (index, valueIndex) { result[index] = autoValues[valueIndex]; });
            used = result.reduce(function (sum, value) { return sum + value; }, 0);
        }

        if (!autoIndexes.length && used < COLUMN_COUNT) {
            let remainder = COLUMN_COUNT - used;
            let cursor = 0;
            while (remainder > 0 && result.length) {
                result[cursor % result.length] += 1;
                cursor += 1;
                remainder -= 1;
            }
        }
        if (result.reduce(function (sum, value) { return sum + value; }, 0) > COLUMN_COUNT) {
            return reduceToBudget(result, COLUMN_COUNT);
        }
        return result;
    }

    function childRowsForGrid($grid) {
        const rows = [];
        $grid.children('.h18-v0811-auto-box').each(function () {
            const key = String($(this).attr('data-h18-v0840-auto-child') || $(this).attr('data-h18-v0811-row') || '');
            const $row = rowByKey(key);
            if ($row.length) { rows.push($row); }
        });
        return $(rows.map(function ($row) { return $row.get(0); }));
    }

    function updateTile($tile, span) {
        span = Math.max(1, Math.min(COLUMN_COUNT, parseInt(span, 10) || 1));
        $tile.attr('data-h18-v0841-effective-span', String(span));
        $tile.get(0).style.setProperty('--h18-v0841-span', String(span));
        $tile.children('.h18-v0841-span-badge').text(span + '/' + COLUMN_COUNT);
    }

    function ensureHandle($tile, $rightTile, index) {
        let $handle = $tile.children('.h18-v0841-resize-handle').first();
        if (!$rightTile || !$rightTile.length) {
            if ($handle.length) { $handle.remove(); }
            return;
        }
        const leftKey = String($tile.attr('data-h18-v0840-auto-child') || $tile.attr('data-h18-v0811-row') || '');
        const rightKey = String($rightTile.attr('data-h18-v0840-auto-child') || $rightTile.attr('data-h18-v0811-row') || '');
        if (!$handle.length) {
            $handle = $('<button>', {
                type: 'button',
                class: 'h18-v0841-resize-handle',
                'aria-label': 'Juster kolonnebredde mellem elementerne',
                title: 'Træk for at justere bredde'
            }).append($('<span>', { 'aria-hidden': 'true', text: '↔' }));
            $tile.append($handle);
        }
        $handle
            .attr('data-h18-v0841-pair-index', String(index))
            .attr('data-h18-v0841-left', leftKey)
            .attr('data-h18-v0841-right', rightKey);
    }

    function decorateGrid(grid) {
        const $grid = $(grid);
        const autoKey = String($grid.attr('data-h18-v0814-auto-key') || '');
        const $auto = rowByKey(autoKey);
        if (!$auto.length || !isAuto($auto)) { return; }

        const $tiles = $grid.children('.h18-v0811-auto-box');
        const $children = childRowsForGrid($grid);
        if (!$tiles.length || $tiles.length !== $children.length) { return; }
        const spans = effectiveSpans($children);

        $grid.addClass('h18-v0841-resize-grid')
            .attr('data-h18-v0841-resize-grid', '1')
            .attr('data-h18-v0841-columns', String(COLUMN_COUNT));

        $tiles.each(function (index) {
            const $tile = $(this);
            $tile.addClass('h18-v0841-resize-tile');
            if (!$tile.children('.h18-v0841-span-badge').length) {
                $tile.append($('<span>', { class: 'h18-v0841-span-badge', 'aria-hidden': 'true' }));
            }
            updateTile($tile, spans[index]);
            ensureHandle($tile, index < $tiles.length - 1 ? $tiles.eq(index + 1) : $(), index);
        });
    }

    function decorate() {
        decorateFrame = 0;
        if (resizeDrag) { return; }
        activeRows().each(function () { hydrateRow($(this)); });
        $sections.find('.h18-v0811-auto-grid[data-h18-v0840-auto-row="1"]').each(function () { decorateGrid(this); });
        document.documentElement.setAttribute('data-h18-lego-resize-runtime', '0.8.41');
        document.documentElement.setAttribute('data-h18-lego-resize-device', canvasDevice());
    }

    function scheduleDecorate() {
        if (decorateFrame || resizeDrag) { return; }
        decorateFrame = window.requestAnimationFrame(decorate);
    }

    function gridStepPx($grid) {
        const node = $grid.get(0);
        if (!node) { return 1; }
        const rect = node.getBoundingClientRect();
        const style = window.getComputedStyle(node);
        const gap = parseFloat(style.columnGap || style.gap || '0') || 0;
        return Math.max(1, (rect.width + gap) / COLUMN_COUNT);
    }

    function atomicBridge() {
        return window.__h18HistoryAtomicV0840 && typeof window.__h18HistoryAtomicV0840.begin === 'function'
            ? window.__h18HistoryAtomicV0840
            : null;
    }

    $(document).on('pointerdown', '.h18-v0841-resize-handle', function (event) {
        if (canvasDevice() !== 'desktop' || event.button !== 0) { return; }
        const $handle = $(this);
        const $leftTile = $handle.closest('.h18-v0841-resize-tile');
        const $grid = $leftTile.closest('.h18-v0841-resize-grid');
        const $tiles = $grid.children('.h18-v0841-resize-tile');
        const leftIndex = $tiles.index($leftTile);
        if (leftIndex < 0 || leftIndex >= $tiles.length - 1) { return; }
        const $rightTile = $tiles.eq(leftIndex + 1);
        const $leftRow = rowByKey(String($handle.attr('data-h18-v0841-left') || ''));
        const $rightRow = rowByKey(String($handle.attr('data-h18-v0841-right') || ''));
        if (!$leftRow.length || !$rightRow.length) { return; }

        event.preventDefault();
        event.stopPropagation();
        const leftSpan = parseInt($leftTile.attr('data-h18-v0841-effective-span'), 10) || 1;
        const rightSpan = parseInt($rightTile.attr('data-h18-v0841-effective-span'), 10) || 1;
        const pairTotal = leftSpan + rightSpan;
        if (pairTotal < 2) { return; }

        const bridge = atomicBridge();
        if (bridge) { bridge.begin('lego-resize'); }
        resizeDrag = {
            pointerId: event.pointerId,
            startX: event.clientX,
            stepPx: gridStepPx($grid),
            leftSpan: leftSpan,
            rightSpan: rightSpan,
            currentLeft: leftSpan,
            currentRight: rightSpan,
            pairTotal: pairTotal,
            $grid: $grid,
            $leftTile: $leftTile,
            $rightTile: $rightTile,
            $leftRow: $leftRow,
            $rightRow: $rightRow,
            bridge: bridge
        };
        $grid.addClass('is-h18-v0841-resizing');
        $handle.addClass('is-active');
        if (this.setPointerCapture) {
            try { this.setPointerCapture(event.pointerId); } catch (error) { /* no-op */ }
        }
    });

    $(document).on('pointermove', function (event) {
        if (!resizeDrag || event.pointerId !== resizeDrag.pointerId) { return; }
        event.preventDefault();
        const delta = Math.round((event.clientX - resizeDrag.startX) / resizeDrag.stepPx);
        const nextLeft = Math.max(1, Math.min(resizeDrag.pairTotal - 1, resizeDrag.leftSpan + delta));
        const nextRight = resizeDrag.pairTotal - nextLeft;
        if (nextLeft === resizeDrag.currentLeft && nextRight === resizeDrag.currentRight) { return; }
        resizeDrag.currentLeft = nextLeft;
        resizeDrag.currentRight = nextRight;
        updateTile(resizeDrag.$leftTile, nextLeft);
        updateTile(resizeDrag.$rightTile, nextRight);
    });

    function finishResize(commit) {
        if (!resizeDrag) { return; }
        const drag = resizeDrag;
        resizeDrag = null;
        drag.$grid.removeClass('is-h18-v0841-resizing');
        drag.$grid.find('.h18-v0841-resize-handle.is-active').removeClass('is-active');
        const changed = drag.currentLeft !== drag.leftSpan || drag.currentRight !== drag.rightSpan;

        if (commit !== false && changed) {
            writeDesktopSpan(drag.$leftRow, drag.currentLeft, true);
            writeDesktopSpan(drag.$rightRow, drag.currentRight, true);
            if (drag.bridge) { drag.bridge.end(true); }
        } else {
            if (drag.bridge) { drag.bridge.end(false); }
        }
        scheduleDecorate();
    }

    $(document).on('pointerup', function (event) {
        if (!resizeDrag || event.pointerId !== resizeDrag.pointerId) { return; }
        finishResize(true);
    });
    $(document).on('pointercancel', function (event) {
        if (!resizeDrag || event.pointerId !== resizeDrag.pointerId) { return; }
        finishResize(false);
    });

    function appendSavePayload() {
        $form.find('[' + SUBMIT_ATTR + '="1"]').remove();
        let index = 0;
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (!key) { return; }
            hydrateRow($row);
            const values = {
                SectionKey: key,
                StateJson: String(canonicalField($row).val() || JSON.stringify(normalizeState({})))
            };
            Object.keys(values).forEach(function (name) {
                $('<input>', {
                    type: 'hidden',
                    name: 'h18_lego_layout_span[' + index + '][' + name + ']',
                    value: values[name]
                }).attr(SUBMIT_ATTR, '1').appendTo($form);
            });
            index += 1;
        });
    }

    $form.on('submit.h18V0841Resize', appendSavePayload);

    const observer = new MutationObserver(function (mutations) {
        if (mutations.some(function (mutation) { return mutation.type === 'childList'; })) {
            scheduleDecorate();
        }
    });
    observer.observe($sections.get(0), { childList: true, subtree: true });

    const canvasObserver = new MutationObserver(scheduleDecorate);
    canvasObserver.observe($canvas.get(0), { attributes: true, attributeFilter: ['data-canvas-device'] });

    decorate();
    window.__h18LegoResizeV0841 = {
        version: '0.8.41',
        columns: COLUMN_COUNT,
        refresh: decorate,
        stateForKey: function (key) {
            const $row = rowByKey(key);
            return $row.length ? stateForRow($row) : null;
        },
        effectiveForAuto: function (key) {
            const $auto = rowByKey(key);
            if (!$auto.length || !isAuto($auto)) { return []; }
            return effectiveSpans(directChildren($auto));
        }
    };
});
