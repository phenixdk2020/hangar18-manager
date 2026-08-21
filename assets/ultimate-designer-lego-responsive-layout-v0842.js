jQuery(function ($) {
    'use strict';

    const $canvas = $('.h18-builder-canvas').first();
    const $sections = $('#h18-page-sections-sortable');
    if (!$canvas.length || !$sections.length) { return; }

    const base = window.__h18LegoResizeV0841;
    if (!base || typeof base.stateForKey !== 'function' || typeof base.writeStateForKey !== 'function') { return; }

    const COLUMN_COUNT = parseInt(base.columns, 10) || 12;
    let refreshTimer = null;
    let drag = null;

    function deviceName() {
        const raw = String($canvas.attr('data-canvas-device') || 'desktop').toLowerCase();
        if (raw === 'tablet') { return 'Tablet'; }
        if (raw === 'mobile') { return 'Mobile'; }
        return 'Desktop';
    }

    function clampSpan(value) {
        const parsed = parseInt(value, 10);
        if (!Number.isFinite(parsed) || parsed <= 0) { return 0; }
        return Math.max(1, Math.min(COLUMN_COUNT, parsed));
    }

    function boolValue(value, fallback) {
        if (typeof value === 'boolean') { return value; }
        if (value === null || typeof value === 'undefined' || value === '') { return fallback; }
        if (typeof value === 'number') { return value !== 0; }
        return ['1', 'true', 'yes', 'on'].indexOf(String(value).toLowerCase().trim()) !== -1;
    }

    function normalizeState(raw) {
        if (typeof base.normalizeState === 'function') {
            return base.normalizeState(raw || {});
        }
        raw = raw && typeof raw === 'object' ? raw : {};
        const normalizeDevice = function (entry) {
            entry = entry && typeof entry === 'object' ? entry : {};
            const inherit = Object.prototype.hasOwnProperty.call(entry, 'InheritDesktop')
                ? boolValue(entry.InheritDesktop, true)
                : true;
            const span = clampSpan(entry.Span);
            return {
                InheritDesktop: inherit,
                HasOverride: Object.prototype.hasOwnProperty.call(entry, 'HasOverride')
                    ? boolValue(entry.HasOverride, !inherit)
                    : (!inherit || span > 0),
                Span: span
            };
        };
        return {
            SchemaVersion: 2,
            Desktop: { Span: clampSpan(raw.Desktop && raw.Desktop.Span) },
            Tablet: normalizeDevice(raw.Tablet),
            Mobile: normalizeDevice(raw.Mobile)
        };
    }

    function stateForKey(key) {
        return normalizeState(base.stateForKey(String(key || '')) || {});
    }

    function rowKeysForAuto(autoKey) {
        return typeof base.rowKeysForAuto === 'function' ? base.rowKeysForAuto(autoKey) : [];
    }

    function explicitForDevice(state, device) {
        state = normalizeState(state);
        if (device === 'Desktop') { return clampSpan(state.Desktop.Span); }
        const entry = state[device] || {};
        return entry.InheritDesktop ? clampSpan(state.Desktop.Span) : clampSpan(entry.Span);
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
        const baseValue = Math.floor(total / count);
        let remainder = total - (baseValue * count);
        const result = [];
        for (let index = 0; index < count; index += 1) {
            result.push(Math.max(1, baseValue + (remainder > 0 ? 1 : 0)));
            if (remainder > 0) { remainder -= 1; }
        }
        return result;
    }

    function effectiveSpans(autoKey, device) {
        const keys = rowKeysForAuto(autoKey);
        if (!keys.length) { return []; }
        if (keys.length > COLUMN_COUNT) { return keys.map(function () { return 1; }); }

        const explicit = keys.map(function (key) { return explicitForDevice(stateForKey(key), device); });
        const autoIndexes = [];
        const explicitIndexes = [];
        explicit.forEach(function (span, index) {
            if (span > 0) { explicitIndexes.push(index); }
            else { autoIndexes.push(index); }
        });

        if (!explicitIndexes.length) {
            return distribute(COLUMN_COUNT, keys.length);
        }

        const result = new Array(keys.length).fill(0);
        const explicitBudget = Math.max(explicitIndexes.length, COLUMN_COUNT - autoIndexes.length);
        const explicitValues = reduceToBudget(
            explicitIndexes.map(function (index) { return explicit[index]; }),
            explicitBudget
        );
        explicitIndexes.forEach(function (index, valueIndex) { result[index] = explicitValues[valueIndex]; });

        if (autoIndexes.length) {
            const used = result.reduce(function (sum, value) { return sum + value; }, 0);
            const remaining = Math.max(autoIndexes.length, COLUMN_COUNT - used);
            const autoValues = distribute(remaining, autoIndexes.length);
            autoIndexes.forEach(function (index, valueIndex) { result[index] = autoValues[valueIndex]; });
        }

        return reduceToBudget(result, COLUMN_COUNT);
    }

    function tileKey($tile) {
        return String($tile.attr('data-h18-v0840-auto-child') || $tile.attr('data-h18-v0811-row') || '');
    }

    function updateTile($tile, span, device) {
        span = Math.max(1, Math.min(COLUMN_COUNT, parseInt(span, 10) || 1));
        $tile.attr('data-h18-v0842-effective-span', String(span));
        $tile.attr('data-h18-v0842-device', device.toLowerCase());
        $tile.get(0).style.setProperty('--h18-v0841-span', String(span));
        const $badge = $tile.children('.h18-v0841-span-badge').first();
        const text = span + '/' + COLUMN_COUNT;
        if ($badge.length && String($badge.text() || '') !== text) { $badge.text(text); }
    }

    function ensureInheritanceButton($tile, device) {
        const key = tileKey($tile);
        if (!key || device === 'Desktop') {
            $tile.children('.h18-v0842-inherit-toggle').remove();
            return;
        }
        const state = stateForKey(key);
        const inherited = Boolean(state[device] && state[device].InheritDesktop);
        let $button = $tile.children('.h18-v0842-inherit-toggle').first();
        if (!$button.length) {
            $button = $('<button>', {
                type: 'button',
                class: 'h18-v0842-inherit-toggle'
            });
            $tile.append($button);
        }
        const label = inherited ? 'Arv Desktop ✓' : 'Arv Desktop';
        if (String($button.text() || '') !== label) { $button.text(label); }
        $button
            .attr('data-h18-v0842-key', key)
            .attr('data-h18-v0842-device', device)
            .attr('aria-pressed', inherited ? 'true' : 'false')
            .attr('title', inherited ? 'Klik for at bruge eget ' + device + '-layout' : 'Klik for at arve Desktop-layout igen');
    }

    function decorateGrid(grid, device) {
        const $grid = $(grid);
        const autoKey = String($grid.attr('data-h18-v0814-auto-key') || '');
        if (!autoKey) { return; }
        const keys = rowKeysForAuto(autoKey);
        const $tiles = $grid.children('.h18-v0811-auto-box');
        if (!$tiles.length || keys.length !== $tiles.length) { return; }
        const spans = effectiveSpans(autoKey, device);

        $grid.attr('data-h18-v0842-responsive-layout', device.toLowerCase());
        $tiles.each(function (index) {
            const $tile = $(this);
            updateTile($tile, spans[index], device);
            ensureInheritanceButton($tile, device);
        });
    }

    function decorate() {
        const device = deviceName();
        if (device === 'Desktop') {
            $('.h18-v0842-inherit-toggle').remove();
            $('.h18-v0841-resize-grid').removeAttr('data-h18-v0842-responsive-layout');
            document.documentElement.setAttribute('data-h18-lego-responsive-layout-device', 'desktop');
            return;
        }
        $('.h18-v0841-resize-grid[data-h18-v0841-resize-grid="1"]').each(function () {
            decorateGrid(this, device);
        });
        document.documentElement.setAttribute('data-h18-lego-responsive-layout-runtime', '0.8.42');
        document.documentElement.setAttribute('data-h18-lego-responsive-layout-device', device.toLowerCase());
    }

    function scheduleDecorate() {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(function () {
            if (typeof base.refresh === 'function') { base.refresh(); }
            window.requestAnimationFrame(function () { window.requestAnimationFrame(decorate); });
        }, 0);
    }

    function atomicBridge() {
        return window.__h18HistoryAtomicV0840 && typeof window.__h18HistoryAtomicV0840.begin === 'function'
            ? window.__h18HistoryAtomicV0840
            : null;
    }

    function gridStepPx($grid) {
        const node = $grid.get(0);
        if (!node) { return 1; }
        const rect = node.getBoundingClientRect();
        const style = window.getComputedStyle(node);
        const gap = parseFloat(style.columnGap || style.gap || '0') || 0;
        return Math.max(1, (rect.width + gap) / COLUMN_COUNT);
    }

    function responsiveWrite(key, device, span, captureHistory) {
        const state = stateForKey(key);
        state[device].InheritDesktop = false;
        state[device].HasOverride = true;
        state[device].Span = Math.max(1, Math.min(COLUMN_COUNT, parseInt(span, 10) || 1));
        return base.writeStateForKey(key, state, captureHistory === true);
    }

    $(document).on('pointerdown.h18V0842Responsive', '.h18-v0841-resize-handle', function (event) {
        const device = deviceName();
        if (device === 'Desktop' || event.button !== 0) { return; }
        const $handle = $(this);
        const $leftTile = $handle.closest('.h18-v0841-resize-tile');
        const $grid = $leftTile.closest('.h18-v0841-resize-grid');
        const $tiles = $grid.children('.h18-v0841-resize-tile');
        const leftIndex = $tiles.index($leftTile);
        if (leftIndex < 0 || leftIndex >= $tiles.length - 1) { return; }
        const $rightTile = $tiles.eq(leftIndex + 1);
        const leftKey = tileKey($leftTile);
        const rightKey = tileKey($rightTile);
        if (!leftKey || !rightKey) { return; }

        event.preventDefault();
        event.stopPropagation();
        const leftSpan = parseInt($leftTile.attr('data-h18-v0842-effective-span'), 10) || 1;
        const rightSpan = parseInt($rightTile.attr('data-h18-v0842-effective-span'), 10) || 1;
        const pairTotal = leftSpan + rightSpan;
        if (pairTotal < 2) { return; }
        const bridge = atomicBridge();
        if (bridge) { bridge.begin('lego-responsive-resize'); }

        drag = {
            pointerId: event.pointerId,
            device: device,
            startX: Number(event.clientX),
            stepPx: gridStepPx($grid),
            pairTotal: pairTotal,
            leftSpan: leftSpan,
            rightSpan: rightSpan,
            currentLeft: leftSpan,
            currentRight: rightSpan,
            leftKey: leftKey,
            rightKey: rightKey,
            $grid: $grid,
            $leftTile: $leftTile,
            $rightTile: $rightTile,
            bridge: bridge
        };
        $grid.addClass('is-h18-v0842-responsive-resizing');
        $handle.addClass('is-active');
        if (this.setPointerCapture) {
            try { this.setPointerCapture(event.pointerId); } catch (error) { /* no-op */ }
        }
    });

    $(document).on('pointermove.h18V0842Responsive', function (event) {
        if (!drag || event.pointerId !== drag.pointerId) { return; }
        event.preventDefault();
        const delta = Math.round((Number(event.clientX) - drag.startX) / drag.stepPx);
        const nextLeft = Math.max(1, Math.min(drag.pairTotal - 1, drag.leftSpan + delta));
        const nextRight = drag.pairTotal - nextLeft;
        if (nextLeft === drag.currentLeft && nextRight === drag.currentRight) { return; }
        drag.currentLeft = nextLeft;
        drag.currentRight = nextRight;
        updateTile(drag.$leftTile, nextLeft, drag.device);
        updateTile(drag.$rightTile, nextRight, drag.device);
    });

    function finishDrag(commit) {
        if (!drag) { return; }
        const current = drag;
        drag = null;
        current.$grid.removeClass('is-h18-v0842-responsive-resizing');
        current.$grid.find('.h18-v0841-resize-handle.is-active').removeClass('is-active');
        const changed = current.currentLeft !== current.leftSpan || current.currentRight !== current.rightSpan;
        if (commit !== false && changed) {
            responsiveWrite(current.leftKey, current.device, current.currentLeft, true);
            responsiveWrite(current.rightKey, current.device, current.currentRight, true);
            if (current.bridge) { current.bridge.end(true); }
        } else if (current.bridge) {
            current.bridge.end(false);
        }
        scheduleDecorate();
    }

    $(document).on('pointerup.h18V0842Responsive', function (event) {
        if (!drag || event.pointerId !== drag.pointerId) { return; }
        finishDrag(true);
    });
    $(document).on('pointercancel.h18V0842Responsive', function (event) {
        if (!drag || event.pointerId !== drag.pointerId) { return; }
        finishDrag(false);
    });

    $(document).on('click.h18V0842Responsive', '.h18-v0842-inherit-toggle', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $button = $(this);
        const key = String($button.attr('data-h18-v0842-key') || '');
        const device = String($button.attr('data-h18-v0842-device') || '');
        if (!key || (device !== 'Tablet' && device !== 'Mobile')) { return; }
        const state = stateForKey(key);
        const entry = state[device];
        if (entry.InheritDesktop) {
            const $tile = $button.closest('.h18-v0841-resize-tile');
            const seed = parseInt($tile.attr('data-h18-v0842-effective-span'), 10) || 1;
            entry.InheritDesktop = false;
            entry.HasOverride = true;
            if (!clampSpan(entry.Span)) { entry.Span = seed; }
        } else {
            entry.InheritDesktop = true;
        }
        base.writeStateForKey(key, state, true);
        scheduleDecorate();
    });

    const canvasObserver = new MutationObserver(scheduleDecorate);
    canvasObserver.observe($canvas.get(0), { attributes: true, attributeFilter: ['data-canvas-device'] });

    const sectionsObserver = new MutationObserver(function (mutations) {
        if (mutations.some(function (mutation) { return mutation.type === 'childList'; })) { scheduleDecorate(); }
    });
    sectionsObserver.observe($sections.get(0), { childList: true, subtree: true });

    scheduleDecorate();
    window.__h18LegoResponsiveLayoutV0842 = {
        version: '0.8.42',
        columns: COLUMN_COUNT,
        refresh: scheduleDecorate,
        effectiveForAuto: function (autoKey, device) {
            return effectiveSpans(autoKey, device || deviceName());
        },
        stateForKey: stateForKey
    };
});
