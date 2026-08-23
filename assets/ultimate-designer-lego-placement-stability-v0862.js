jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector-target');
    if (!$sections.length) { return; }

    let insideDrag = null;

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
        if (!$row || !$row.length) { return ''; }
        return String(controls($row, '.h18-page-section-key').first().val() || $row.attr('data-key') || '').trim();
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

        if (String($hidden.val() || '') !== boxKey) {
            $hidden.val(boxKey).trigger('change');
        }
        if ($select.length && String($select.val() || '') !== boxKey) {
            ensureParentOption(childKey, boxKey);
            $select.val(boxKey).trigger('change');
        }
        $row.attr('data-h18-nested-in-box', boxKey);
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

    function pointFromEvent(event) {
        const original = event && event.originalEvent ? event.originalEvent : event;
        const pageX = Number(event && event.pageX);
        const pageY = Number(event && event.pageY);
        if (Number.isFinite(pageX) && Number.isFinite(pageY)) {
            return { pageX: pageX, pageY: pageY };
        }
        const clientX = Number(original && original.clientX);
        const clientY = Number(original && original.clientY);
        if (Number.isFinite(clientX) && Number.isFinite(clientY)) {
            return {
                pageX: clientX + (window.pageXOffset || document.documentElement.scrollLeft || 0),
                pageY: clientY + (window.pageYOffset || document.documentElement.scrollTop || 0)
            };
        }
        return null;
    }

    function clearInsideTarget() {
        $('.h18-v0865-box-inside-target').removeClass('h18-v0865-box-inside-target');
        $('.h18-ud-box-drop-zone.is-active').removeClass('is-active');
    }

    function boxAtPoint(pageX, pageY, sourceKey) {
        const clientX = Number(pageX) - (window.pageXOffset || document.documentElement.scrollLeft || 0);
        const clientY = Number(pageY) - (window.pageYOffset || document.documentElement.scrollTop || 0);
        let $match = $();

        activeRows().each(function () {
            const $box = $(this);
            if (!isBox($box) || rowKey($box) === sourceKey) { return; }

            const preview = $box.children('.h18-canvas-preview').first().get(0);
            if (!preview) { return; }
            const surface = preview.querySelector('.h18-ud-box-contents-preview') || preview;
            if (!surface || !surface.getClientRects || !surface.getClientRects().length) { return; }

            const rect = surface.getBoundingClientRect();
            if (clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom) {
                $match = $box;
            }
        });
        return $match;
    }

    function showInsideTarget($box) {
        clearInsideTarget();
        if (!$box || !$box.length) { return; }
        $box.addClass('h18-v0865-box-inside-target');
        $box.find('.h18-ud-box-drop-zone').first().addClass('is-active');
    }

    function moveElementIntoBox(sourceKey, boxKey) {
        const $source = rowByKey(sourceKey);
        const $box = rowByKey(boxKey);
        if (!$source.length || !$box.length || !isPlainElement($source) || !isBox($box)) { return false; }

        const $existingChildren = directChildren($box).not($source);
        const $anchor = $existingChildren.length ? $existingChildren.last() : $box;

        const stackApi = window.__h18LegoFixesV0851;
        if (stackApi && typeof stackApi.clearStackForKey === 'function') {
            stackApi.clearStackForKey(sourceKey, false);
        }

        $source.insertAfter($anchor);
        if (!setParent($source, boxKey)) { return false; }
        $source.attr('data-h18-v0811-child-source', '1');
        syncFlatOrder();

        const nesting = window.__h18NestingToolsV0840;
        if (nesting && typeof nesting.refresh === 'function') {
            nesting.refresh();
        }

        const selection = window.__h18LegoInspectorOnlyV0847;
        if (selection) {
            if (typeof selection.rememberSelectedCanvasKey === 'function') {
                selection.rememberSelectedCanvasKey(sourceKey);
            }
            if (typeof selection.refreshSelectedCanvasMarker === 'function') {
                window.requestAnimationFrame(function () { selection.refreshSelectedCanvasMarker(); });
            }
        }
        return true;
    }

    /* Preserve the canonical key before Inspector moves the structural fields. */
    document.addEventListener('pointerdown', function (event) {
        const target = event.target && event.target.closest ? event.target : null;
        if (!target || !target.closest('.h18-builder-canvas')) { return; }
        const preview = target.closest('.h18-canvas-preview');
        if (!preview) { return; }
        const row = preview.parentElement;
        if (!row || !row.matches('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)')) { return; }
        const keyField = row.querySelector('.h18-page-section-key');
        const key = String((keyField && keyField.value) || row.getAttribute('data-key') || '').trim();
        if (key) { row.setAttribute('data-key', key); }
    }, true);

    /* LEGO-065 only owns existing plain-element -> Kasse INSIDE placement.
     * Side-by-side and Over/Under remain owned by the established baseline. */
    $sections.on('sortstart.h18V0865InsideKasse', function (event, ui) {
        const $source = ui && ui.item ? ui.item : $();
        const sourceKey = rowKey($source);
        insideDrag = sourceKey && isPlainElement($source)
            ? { sourceKey: sourceKey, boxKey: '' }
            : null;
    });

    $sections.on('sort.h18V0865InsideKasse', function (event) {
        if (!insideDrag) { return; }
        const point = pointFromEvent(event);
        if (!point) { return; }
        const $box = boxAtPoint(point.pageX, point.pageY, insideDrag.sourceKey);
        insideDrag.boxKey = $box.length ? rowKey($box) : '';
        showInsideTarget($box);
    });

    $sections.on('sortstop.h18V0865InsideKasse', function () {
        if (!insideDrag) { return; }
        const state = insideDrag;
        insideDrag = null;
        clearInsideTarget();
        if (!state.boxKey) { return; }

        /* Registered after the baseline sort handlers, so this finalizes the
         * explicit INSIDE intention after any temporary Sortable reorder. */
        moveElementIntoBox(state.sourceKey, state.boxKey);
    });

    document.documentElement.setAttribute('data-h18-lego-placement-stability', '0.8.65-inside-kasse');
    document.documentElement.setAttribute('data-h18-lego-selection-key-preflight', '0.8.65');

    window.__h18LegoPlacementStabilityV0862 = {
        version: '0.8.65',
        placementOwner: 'baseline-plus-inside-kasse',
        selectionKeyPreflight: true,
        moveElementIntoBox: moveElementIntoBox
    };
}());
