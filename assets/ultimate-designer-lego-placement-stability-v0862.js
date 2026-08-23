jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector-target');
    if (!$sections.length) { return; }

    const MAX_NESTING_DEPTH = 2;
    let insideDrag = null;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) { $result = $result.add($inspector.find(selector)); }
        return $result;
    }

    function rowKey($row) {
        if (!$row || !$row.length) { return ''; }
        const direct = String($row.find('.h18-page-section-key').first().val() || '').trim();
        if (direct) { return direct; }
        const cached = String($row.attr('data-key') || '').trim();
        if (cached) { return cached; }
        if ($row.hasClass('is-selected')) {
            return String($inspector.find('.h18-page-section-key').first().val() || '').trim();
        }
        return '';
    }

    function rowType($row) {
        if (!$row || !$row.length) { return ''; }
        return String($row.attr('data-section-type') || controls($row, '.h18-page-section-type').first().val() || '').trim();
    }

    function rowLabel($row) {
        if (!$row || !$row.length) { return ''; }
        return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
    }

    function parentKey($row) {
        if (!$row || !$row.length) { return ''; }
        return String(controls($row, '.h18-layout-parent-key').first().val() || '').trim();
    }

    function rowByKey(key) {
        const wanted = String(key || '').trim();
        if (!wanted) { return $(); }
        return activeRows().filter(function () { return rowKey($(this)) === wanted; }).first();
    }

    function isBox($row) {
        if (!$row || !$row.length || rowType($row) !== 'container') { return false; }
        return String($row.attr('data-h18-box') || '') === '1' || rowLabel($row).indexOf('Kasse') === 0;
    }

    function isPlainElement($row) {
        const type = rowType($row);
        return !!($row && $row.length && type && type !== 'container' && type !== 'grid' && type !== 'flex');
    }

    function parentDepth($row) {
        let depth = 0;
        let cursor = parentKey($row);
        const seen = new Set();
        while (cursor) {
            if (seen.has(cursor)) { return MAX_NESTING_DEPTH + 1; }
            seen.add(cursor);
            depth += 1;
            if (depth > MAX_NESTING_DEPTH) { return depth; }
            const $parent = rowByKey(cursor);
            if (!$parent.length) { break; }
            cursor = parentKey($parent);
        }
        return depth;
    }

    function canMovePlainElementIntoBox($source, $box) {
        if (!$source.length || !$box.length || !isPlainElement($source) || !isBox($box)) { return false; }
        if (rowKey($source) === rowKey($box)) { return false; }
        return parentDepth($box) + 1 <= MAX_NESTING_DEPTH;
    }

    function directChildren($box) {
        const key = rowKey($box);
        if (!key) { return $(); }
        return activeRows().filter(function () { return parentKey($(this)) === key; });
    }

    function ensureParentOption(childKey, boxKey) {
        const guard = window.__h18LegoParentKeyGuardV0845;
        if (guard && typeof guard.ensureParentOption === 'function') {
            guard.ensureParentOption(childKey, boxKey);
        }
    }

    function setParent($row, boxKey) {
        if (!$row || !$row.length || !boxKey) { return false; }
        const childKey = rowKey($row);
        ensureParentOption(childKey, boxKey);

        const $hidden = controls($row, '.h18-layout-parent-key').first();
        const $select = controls($row, '.h18-layout-parent-select').first();
        if (!$hidden.length) { return false; }

        $hidden.val(boxKey).trigger('change');
        ensureParentOption(childKey, boxKey);
        if ($select.length) { $select.val(boxKey).trigger('change'); }
        if (String($hidden.val() || '') !== boxKey) { return false; }

        $row.attr('data-h18-nested-in-box', boxKey).attr('data-h18-v0811-child-source', '1');
        return true;
    }

    function syncFlatOrder() {
        let order = 0;
        $sections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            if ($row.hasClass('h18-page-section-removed')) { return; }
            order += 1;
            controls($row, '.h18-page-section-order').val(order * 10);
        });
        if ($sections.hasClass('ui-sortable')) { $sections.sortable('refresh'); }
    }

    function insideZoneAtClientPoint(clientX, clientY, sourceKey) {
        let match = null;
        let bestArea = Number.POSITIVE_INFINITY;
        document.querySelectorAll('.h18-v0838-drop-zone.is-inside:not(.is-disabled)[data-h18-v0870-inside-kasse]').forEach(function (zone) {
            if (!zone.getClientRects || !zone.getClientRects().length) { return; }
            const boxKey = String(zone.getAttribute('data-h18-v0870-inside-kasse') || '').trim();
            if (!boxKey || boxKey === sourceKey) { return; }
            const $box = rowByKey(boxKey);
            const $source = rowByKey(sourceKey);
            if (!canMovePlainElementIntoBox($source, $box)) { return; }
            const rect = zone.getBoundingClientRect();
            if (clientX < rect.left || clientX > rect.right || clientY < rect.top || clientY > rect.bottom) { return; }
            const area = Math.max(1, rect.width * rect.height);
            if (area < bestArea) {
                bestArea = area;
                match = { boxKey: boxKey, zone: zone };
            }
        });
        return match;
    }

    function movePlainElementIntoBox(sourceKey, boxKey) {
        const $source = rowByKey(sourceKey);
        const $box = rowByKey(boxKey);
        if (!canMovePlainElementIntoBox($source, $box)) {
            document.documentElement.setAttribute('data-h18-v0870-last-inside-result', 'invalid-target');
            return false;
        }

        const stackApi = window.__h18LegoFixesV0851;
        if (stackApi && typeof stackApi.clearStackForKey === 'function') {
            stackApi.clearStackForKey(sourceKey, false);
        }

        const $children = directChildren($box).not($source);
        const $anchor = $children.length ? $children.last() : $box;
        $source.insertAfter($anchor);

        if (!setParent($source, boxKey)) {
            document.documentElement.setAttribute('data-h18-v0870-last-inside-result', 'parent-write-failed');
            return false;
        }

        syncFlatOrder();
        document.documentElement.setAttribute('data-h18-v0870-last-inside-result', 'ok');
        document.documentElement.setAttribute('data-h18-v0870-last-inside-source', sourceKey);
        document.documentElement.setAttribute('data-h18-v0870-last-inside-box', boxKey);

        const nesting = window.__h18NestingToolsV0840;
        if (nesting && typeof nesting.refresh === 'function') { nesting.refresh(); }

        const selection = window.__h18LegoInspectorOnlyV0847;
        if (selection && typeof selection.refreshSelectedCanvasMarker === 'function') {
            window.setTimeout(selection.refreshSelectedCanvasMarker, 0);
        }
        return true;
    }

    function trackPointer(event) {
        if (!insideDrag) { return; }
        const clientX = Number(event.clientX);
        const clientY = Number(event.clientY);
        if (!Number.isFinite(clientX) || !Number.isFinite(clientY)) { return; }
        insideDrag.lastClientX = clientX;
        insideDrag.lastClientY = clientY;
        const hit = insideZoneAtClientPoint(clientX, clientY, insideDrag.sourceKey);
        insideDrag.boxKey = hit ? hit.boxKey : '';
    }

    document.addEventListener('mousemove', trackPointer, true);
    document.addEventListener('pointermove', trackPointer, true);

    $sections.on('sortstart.h18V0870InsideKasse', function (event, ui) {
        const $source = ui && ui.item ? ui.item : $();
        const sourceKey = rowKey($source);
        insideDrag = sourceKey && isPlainElement($source)
            ? { sourceKey: sourceKey, boxKey: '', lastClientX: NaN, lastClientY: NaN }
            : null;
        if (insideDrag) {
            $source.attr('data-key', sourceKey);
            document.documentElement.setAttribute('data-h18-v0870-last-inside-result', 'dragging');
        }
    });

    $sections.on('sort.h18V0870InsideKasse', function (event) {
        if (!insideDrag) { return; }
        const original = event && event.originalEvent ? event.originalEvent : event;
        const clientX = Number(original && original.clientX);
        const clientY = Number(original && original.clientY);
        if (Number.isFinite(clientX) && Number.isFinite(clientY)) {
            insideDrag.lastClientX = clientX;
            insideDrag.lastClientY = clientY;
            const hit = insideZoneAtClientPoint(clientX, clientY, insideDrag.sourceKey);
            insideDrag.boxKey = hit ? hit.boxKey : '';
        }
    });

    $sections.on('sortstop.h18V0870InsideKasse', function () {
        if (!insideDrag) { return; }
        const state = insideDrag;
        insideDrag = null;

        let finalBoxKey = '';
        if (Number.isFinite(state.lastClientX) && Number.isFinite(state.lastClientY)) {
            const finalHit = insideZoneAtClientPoint(state.lastClientX, state.lastClientY, state.sourceKey);
            finalBoxKey = finalHit ? finalHit.boxKey : '';
        }
        if (!finalBoxKey) { finalBoxKey = state.boxKey; }

        if (!finalBoxKey) {
            document.documentElement.setAttribute('data-h18-v0870-last-inside-result', 'no-inside-zone');
            return;
        }
        movePlainElementIntoBox(state.sourceKey, finalBoxKey);
    });

    $sections.on('sortcancel.h18V0870InsideKasse', function () {
        insideDrag = null;
    });

    document.documentElement.setAttribute('data-h18-lego-placement-stability', '0.8.70-explicit-inside-zone');
    window.__h18LegoPlacementStabilityV0862 = {
        version: '0.8.70',
        placementOwner: 'explicit-inside-zone-only',
        moveElementIntoBox: movePlainElementIntoBox
    };
}());
