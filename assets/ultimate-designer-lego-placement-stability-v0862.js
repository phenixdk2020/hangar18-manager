jQuery(function ($) {
    'use strict';

    if (window.__h18LegoPlacementStabilityV0862) { return; }

    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector-target');
    if (!$sections.length) { return; }

    const ZONE_SELECTOR = '.h18-v0838-drop-zone:not(.is-disabled)';
    let drag = null;

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
        return String(controls($row, '.h18-page-section-key').first().val() || $row.attr('data-key') || '').trim();
    }

    function rowType($row) {
        return String($row.attr('data-section-type') || controls($row, '.h18-page-section-type').first().val() || '').trim();
    }

    function rowLabel($row) {
        return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
    }

    function parentKey($row) {
        return String(controls($row, '.h18-layout-parent-key').first().val() || '').trim();
    }

    function rowByKey(key) {
        const wanted = String(key || '').trim();
        if (!wanted) { return $(); }
        return activeRows().filter(function () { return rowKey($(this)) === wanted; }).first();
    }

    function isAuto($row) {
        return !!($row && $row.length && rowType($row) === 'grid' && rowLabel($row) === 'Auto-kasser');
    }

    function snapshotKeys() {
        const keys = new Set();
        activeRows().each(function () {
            const key = rowKey($(this));
            if (key) { keys.add(key); }
        });
        return keys;
    }

    function findNewRow(beforeKeys, type) {
        let $match = $();
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (key && !beforeKeys.has(key) && (!type || rowType($row) === type)) {
                $match = $row;
            }
        });
        return $match;
    }

    function ensureParentOption(rowKeyValue, parentKeyValue) {
        const guard = window.__h18LegoParentKeyGuardV0845;
        if (!parentKeyValue || !guard || typeof guard.ensureParentOption !== 'function') { return; }
        guard.ensureParentOption(rowKeyValue, parentKeyValue);
    }

    function setParent($row, key) {
        if (!$row || !$row.length) { return false; }
        const value = String(key || '').trim();
        const childKey = rowKey($row);
        if (value) { ensureParentOption(childKey, value); }

        const $hidden = controls($row, '.h18-layout-parent-key').first();
        const $select = controls($row, '.h18-layout-parent-select').first();
        if (!$hidden.length) { return false; }

        if (String($hidden.val() || '') !== value) { $hidden.val(value).trigger('change'); }
        if ($select.length && String($select.val() || '') !== value) {
            if (value) { ensureParentOption(childKey, value); }
            $select.val(value).trigger('change');
        }
        if (value) { $row.attr('data-h18-nested-in-box', value); }
        else { $row.removeAttr('data-h18-nested-in-box'); }
        return true;
    }

    function setField($row, name, value) {
        const $field = controls($row, '[name$="[' + name + ']"]').first();
        if (!$field.length) { return; }
        if ($field.is(':checkbox')) {
            if ($field.is(':checked') !== !!value) { $field.prop('checked', !!value).trigger('change'); }
            return;
        }
        if (String($field.val() || '') !== String(value)) {
            $field.val(String(value)).trigger('input').trigger('change');
        }
    }

    function setLabel($row, value) {
        const $field = controls($row, '.h18-section-navigator-label').first();
        if ($field.length && String($field.val() || '') !== String(value)) {
            $field.val(String(value)).trigger('input').trigger('change');
        }
    }

    function configureAuto($row) {
        if (!$row.length || rowType($row) !== 'grid') { return; }
        setLabel($row, 'Auto-kasser');
        setField($row, 'Title', '');
        setField($row, 'Content', '');
        setField($row, 'LayoutColumns', 1);
        setField($row, 'MobileLayoutColumns', 1);
        setField($row, 'LayoutGapPx', 16);
        setField($row, 'MobileLayoutGapPx', 12);
        setField($row, 'LayoutAlign', 'Stretch');
        setParent($row, '');
        $row.attr('data-h18-auto-box-row', '1');
    }

    function syncFlatOrder() {
        let index = 0;
        $sections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            if ($row.hasClass('h18-page-section-removed')) { return; }
            index += 1;
            controls($row, '.h18-page-section-order').val(index * 10);
        });
        if ($sections.hasClass('ui-sortable')) { $sections.sortable('refresh'); }
    }

    function clearStack(key, capture) {
        const api = window.__h18LegoFixesV0851;
        if (api && typeof api.clearStackForKey === 'function') {
            api.clearStackForKey(key, capture === true);
        }
    }

    function refreshOnce(selectedKey) {
        const nesting = window.__h18NestingToolsV0840;
        if (nesting && typeof nesting.refresh === 'function') { nesting.refresh(); }

        const selection = window.__h18LegoInspectorOnlyV0847;
        if (selection) {
            if (selectedKey && typeof selection.rememberSelectedCanvasKey === 'function') {
                selection.rememberSelectedCanvasKey(selectedKey);
            }
            if (typeof selection.refreshSelectedCanvasMarker === 'function') {
                window.requestAnimationFrame(function () { selection.refreshSelectedCanvasMarker(); });
            }
        }
    }

    function hitPlacement(pageX, pageY) {
        const clientX = Number(pageX) - (window.pageXOffset || document.documentElement.scrollLeft || 0);
        const clientY = Number(pageY) - (window.pageYOffset || document.documentElement.scrollTop || 0);
        let placement = null;
        $(ZONE_SELECTOR).each(function () {
            const target = String(this.getAttribute('data-h18-v0838-target') || '').trim();
            const position = String(this.getAttribute('data-h18-v0838-position') || '').trim();
            if (!target || !position || (drag && target === drag.sourceKey)) { return; }
            const rect = this.getBoundingClientRect();
            if (clientX >= rect.left && clientX <= rect.right && clientY >= rect.top && clientY <= rect.bottom) {
                placement = { targetKey: target, position: position };
            }
        });
        return placement;
    }

    function arrangeInAuto($source, $target, position, $auto) {
        if (!$source.length || !$target.length || !$auto.length) { return false; }
        const autoKey = rowKey($auto);
        if (!autoKey) { return false; }

        clearStack(rowKey($source), false);
        if (!setParent($source, autoKey)) { return false; }
        if (position === 'left') { $source.insertBefore($target); }
        else { $source.insertAfter($target); }
        syncFlatOrder();
        refreshOnce(rowKey($source));
        return true;
    }

    function createAutoForPair(sourceKey, targetKey, position) {
        const $source = rowByKey(sourceKey);
        const $target = rowByKey(targetKey);
        if (!$source.length || !$target.length) { return false; }

        const before = snapshotKeys();
        const $gridButton = $('.h18-builder-palette-item[data-section-type="grid"]').not('[data-h18-layout-tool]').first();
        if (!$gridButton.length) { return false; }
        $gridButton.trigger('click');

        window.setTimeout(function () {
            const $freshSource = rowByKey(sourceKey);
            const $freshTarget = rowByKey(targetKey);
            const $grid = findNewRow(before, 'grid');
            if (!$freshSource.length || !$freshTarget.length || !$grid.length) { return; }

            configureAuto($grid);
            const gridKey = rowKey($grid);
            if (!gridKey) { return; }

            clearStack(sourceKey, false);
            setParent($freshSource, gridKey);
            setParent($freshTarget, gridKey);
            $grid.insertBefore($freshTarget);
            if (position === 'left') {
                $freshSource.insertAfter($grid);
                $freshTarget.insertAfter($freshSource);
            } else {
                $freshTarget.insertAfter($grid);
                $freshSource.insertAfter($freshTarget);
            }
            syncFlatOrder();
            refreshOnce(sourceKey);
        }, 120);
        return true;
    }

    function enforceSidePlacement(state) {
        const $source = rowByKey(state.sourceKey);
        const $target = rowByKey(state.targetKey);
        if (!$source.length || !$target.length) { return; }

        const $targetParent = rowByKey(parentKey($target));
        if (isAuto($targetParent)) {
            arrangeInAuto($source, $target, state.position, $targetParent);
            return;
        }

        // The old nesting runtime may have completed the same side drop
        // asynchronously. Re-check after its 100 ms window before creating a
        // second Auto-kasse.
        window.setTimeout(function () {
            const $againSource = rowByKey(state.sourceKey);
            const $againTarget = rowByKey(state.targetKey);
            if (!$againSource.length || !$againTarget.length) { return; }
            const $againParent = rowByKey(parentKey($againTarget));
            if (isAuto($againParent)) {
                arrangeInAuto($againSource, $againTarget, state.position, $againParent);
                return;
            }
            createAutoForPair(state.sourceKey, state.targetKey, state.position);
        }, 150);
    }

    function enforceVerticalPlacement(state) {
        const $source = rowByKey(state.sourceKey);
        const $target = rowByKey(state.targetKey);
        if (!$source.length || !$target.length) { return; }

        const targetParent = parentKey($target);
        const $parent = rowByKey(targetParent);
        const api = window.__h18LegoFixesV0851;

        if (isAuto($parent) && api && typeof api.adoptUnder === 'function') {
            ensureParentOption(state.sourceKey, targetParent);
            if (api.adoptUnder(state.sourceKey, state.targetKey, state.position)) {
                refreshOnce(state.sourceKey);
                return;
            }
        }

        clearStack(state.sourceKey, false);
        setParent($source, targetParent);
        if (state.position === 'over') { $source.insertBefore($target); }
        else { $source.insertAfter($target); }
        syncFlatOrder();
        refreshOnce(state.sourceKey);
    }

    function enforcePlacement(state) {
        if (!state || !state.sourceKey || !state.targetKey || state.sourceKey === state.targetKey) { return; }
        if (state.position === 'left' || state.position === 'right') {
            enforceSidePlacement(state);
            return;
        }
        if (state.position === 'over' || state.position === 'under') {
            enforceVerticalPlacement(state);
        }
    }

    function removeLegacySelectionRefreshHandlers() {
        // nesting-tools historically refreshed the complete visual composition
        // 120 ms after merely selecting a section/header. That is not a
        // structural change and is the main visible selection flash.
        if (!$._data) { return; }
        const events = $._data(document, 'events') || {};
        (events.click || []).slice().forEach(function (entry) {
            const selector = String(entry.selector || '');
            if (
                selector.indexOf('.h18-preview-device') !== -1 &&
                selector.indexOf('.h18-page-section-header') !== -1 &&
                selector.indexOf('.h18-page-section-edit') !== -1 &&
                typeof entry.handler === 'function'
            ) {
                $(document).off('click', entry.selector, entry.handler);
            }
        });

        // The nested Rediger helper did the same unnecessary refresh after it
        // delegated selection to the canonical row. Replace only that exact
        // legacy delegated handler and keep the established selection contract.
        const clickEvents = ($._data(document, 'events') || {}).click || [];
        clickEvents.slice().forEach(function (entry) {
            if (String(entry.selector || '') === '.h18-v0811-edit-child' && typeof entry.handler === 'function') {
                $(document).off('click', entry.selector, entry.handler);
            }
        });
        $(document).off('click.h18V0862StableEditChild').on('click.h18V0862StableEditChild', '.h18-v0811-edit-child', function (event) {
            event.preventDefault();
            event.stopPropagation();
            const key = String($(this).attr('data-h18-v0811-edit-child') || '').trim();
            const $row = rowByKey(key);
            if ($row.length) { $row.children('.h18-page-section-header').trigger('click'); }
        });
    }

    $sections.on('sortstart.h18V0862Placement', function (event, ui) {
        const $row = ui && ui.item ? ui.item : $();
        const sourceKey = rowKey($row);
        drag = sourceKey ? { sourceKey: sourceKey, placement: null } : null;
    });

    $sections.on('sort.h18V0862Placement', function (event) {
        if (!drag) { return; }
        drag.placement = hitPlacement(event.pageX, event.pageY);
    });

    $sections.on('sortstop.h18V0862Placement', function () {
        if (!drag) { return; }
        const state = drag.placement ? {
            sourceKey: drag.sourceKey,
            targetKey: drag.placement.targetKey,
            position: drag.placement.position
        } : null;
        drag = null;
        if (!state) { return; }

        // Run after the legacy sortstop handlers. If they already performed a
        // valid side placement we normalize it; otherwise this converts the raw
        // Sortable reorder into the explicit LEGO placement the user chose.
        window.setTimeout(function () { enforcePlacement(state); }, 0);
    });

    removeLegacySelectionRefreshHandlers();

    document.documentElement.setAttribute('data-h18-lego-placement-stability', '0.8.62');
    window.__h18LegoPlacementStabilityV0862 = {
        version: '0.8.62',
        enforcePlacement: enforcePlacement,
        removeLegacySelectionRefreshHandlers: removeLegacySelectionRefreshHandlers
    };
}());
