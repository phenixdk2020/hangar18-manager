(function ($) {
    'use strict';

    if (window.__h18LegoInspectorOnlyV0847) { return; }

    const INLINE_EDIT_SELECTOR = [
        '.h18-canvas-inline-edit',
        '.h18-canvas-rich-edit',
        '.h18-canvas-card-inline-edit',
        '.h18-canvas-card-rich-edit',
        '.h18-canvas-editable-media'
    ].join(',');

    const DIRECT_SETTING_SELECTOR = [
        '.h18-canvas-image-change',
        '.h18-canvas-image-remove',
        '.h18-canvas-aspect-lock',
        '.h18-canvas-image-tools input',
        '.h18-canvas-image-tools select',
        '.h18-canvas-image-tools button',
        '.h18-canvas-focal-dot'
    ].join(',');

    const INSPECTOR_SELECTION_SELECTOR = [
        '.h18-page-section-edit',
        '.h18-page-section-header',
        '.h18-v0811-edit-child'
    ].join(',');

    const NESTED_SELECTOR = '.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child]';
    const CANVAS_ELEMENT_SELECTOR = [
        NESTED_SELECTOR,
        '.h18-page-section-row > .h18-canvas-preview'
    ].join(',');

    const CANVAS_SELECTION_EXCLUDE_SELECTOR = [
        '.h18-v0841-resize-handle',
        '.h18-v0841-resize-rail',
        '.h18-v0811-edit-child',
        '.h18-page-section-edit',
        '.h18-v0811-side-zone',
        '.h18-v0814-auto-drop-zone',
        '.h18-v0814-auto-kasse-drop',
        '.h18-ud-box-drop-zone',
        '.h18-v0838-drop-zone'
    ].join(',');

    const SELECTED_CANVAS_CLASS = 'is-h18-v0848-selected-element';
    let resizePointerActive = false;
    let activeCanvasKey = '';
    let activeSelectionMode = 'top';

    function rowKey(row) {
        if (!row) { return ''; }
        const direct = row.querySelector('.h18-page-section-key');
        if (direct && direct.value) { return String(direct.value); }
        return String(row.getAttribute('data-key') || '');
    }

    function nestedKey(node) {
        if (!node) { return ''; }
        return String(node.getAttribute('data-h18-v0811-row') || node.getAttribute('data-h18-v0811-child') || '');
    }

    function rememberSelection(key, mode) {
        const value = String(key || '').trim();
        if (!value) { return ''; }
        activeCanvasKey = value;
        activeSelectionMode = mode === 'nested' ? 'nested' : 'top';
        document.documentElement.setAttribute('data-h18-v0872-selection-mode', activeSelectionMode);
        document.documentElement.setAttribute('data-h18-v0872-selection-key', value);
        return value;
    }

    function armCompositionReconcile() {
        window.setTimeout(function () {
            const guard = window.__h18LegoParentKeyGuardV0845;
            if (!guard) { return; }
            if (typeof guard.reconcileNow === 'function') { guard.reconcileNow(); }
            if (typeof guard.armVisualReconcile === 'function') { guard.armVisualReconcile(); }
        }, 0);
    }

    function selectedRowKey() {
        const row = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
        if (!row) { return ''; }
        const direct = row.querySelector('.h18-page-section-key');
        if (direct && direct.value) { return String(direct.value); }
        const inspector = document.querySelector('#h18-page-inspector-target .h18-page-section-key');
        if (inspector && inspector.value) { return String(inspector.value); }
        return rowKey(row);
    }

    function refreshSelectedCanvasMarker() {
        if (!activeCanvasKey) {
            const initial = selectedRowKey();
            if (initial) { rememberSelection(initial, 'top'); }
        }

        const key = activeCanvasKey;
        const nestedMode = activeSelectionMode === 'nested';
        document.querySelectorAll(NESTED_SELECTOR).forEach(function (node) {
            const shouldSelect = Boolean(key && nestedMode && nestedKey(node) === key);
            node.classList.toggle(SELECTED_CANVAS_CLASS, shouldSelect);
        });

        if (!nestedMode) {
            const selectedRow = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
            if (selectedRow && key) { selectedRow.setAttribute('data-key', key); }
        }
    }

    function selectInspectorForNode(node) {
        if (!node || !node.closest) { return false; }

        const nested = node.closest(NESTED_SELECTOR);
        if (nested) {
            const key = nestedKey(nested);
            if (key) { rememberSelection(key, 'nested'); }
            refreshSelectedCanvasMarker();

            const edit = nested.querySelector('.h18-v0811-edit-child');
            if (edit) {
                edit.click();
                armCompositionReconcile();
                window.setTimeout(refreshSelectedCanvasMarker, 0);
                return true;
            }
        }

        const row = node.closest('.h18-page-section-row');
        if (!row) { return false; }
        const key = rowKey(row) || selectedRowKey();
        if (key) { rememberSelection(key, 'top'); }
        const edit = row.querySelector('.h18-page-section-edit');
        const header = row.querySelector('.h18-page-section-header');
        if (edit) { edit.click(); }
        else if (header) { header.click(); }
        else { return false; }
        armCompositionReconcile();
        window.setTimeout(refreshSelectedCanvasMarker, 0);
        return true;
    }

    function suppressDirectSetting(event, selector) {
        const target = event.target && event.target.closest ? event.target.closest(selector) : null;
        if (!target) { return; }
        if (target.closest('.h18-v0841-resize-handle,.h18-v0841-resize-rail')) { return; }
        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === 'function') { event.stopImmediatePropagation(); }
        selectInspectorForNode(target);
    }

    function setTextIfChanged(node, value) {
        if (!node) { return; }
        const next = String(value || '');
        if (String(node.textContent || '') !== next) { node.textContent = next; }
    }

    function setControlLabel(input, label, help) {
        if (!input || !input.closest) { return; }
        const shell = input.closest('label');
        if (!shell) { return; }
        const strong = shell.querySelector('strong');
        setTextIfChanged(strong, label);
        if (help) {
            let note = shell.querySelector('.h18-v0847-control-help');
            if (!note) {
                note = document.createElement('small');
                note.className = 'h18-v0847-control-help';
                shell.appendChild(note);
            }
            setTextIfChanged(note, help);
        }
    }

    function clarifyInspectorControls() {
        const spacing = document.querySelector('#h18-ud-lego-spacing-panel');
        if (spacing) {
            spacing.querySelectorAll('[data-h18-lego-path$=".Margin.X"]').forEach(function (input) {
                setControlLabel(input, 'Vandret afstand omkring element', 'Luft til venstre og højre om elementet.');
            });
            spacing.querySelectorAll('[data-h18-lego-path$=".Margin.Y"]').forEach(function (input) {
                setControlLabel(input, 'Lodret afstand omkring element', 'Luft over og under elementet.');
            });
            spacing.querySelectorAll('[data-h18-lego-path$=".Gap.X"]').forEach(function (input) {
                setControlLabel(input, 'Mellem elementer vandret', 'Afstand mellem elementer, når flere ligger på samme række.');
            });
            spacing.querySelectorAll('[data-h18-lego-path$=".Gap.Y"]').forEach(function (input) {
                setControlLabel(input, 'Mellem rækker lodret', 'Afstand i højden mellem rækker/elementer.');
            });
            setTextIfChanged(spacing.querySelector('.h18-ud-lego-heading h4'), 'Afstand og spacing');
        }

        const design = document.querySelector('#h18-ud-lego-design-panel');
        if (design) {
            setControlLabel(design.querySelector('[data-h18-lego-design-path="Colors.Background"]'), 'Elementfarve / baggrund', 'Farven på selve elementets flade.');
            setControlLabel(design.querySelector('[data-h18-lego-design-path="Border.Color"]'), 'Kantfarve', 'Bruges når kanttykkelsen er større end 0 px.');
            setControlLabel(design.querySelector('[data-h18-lego-design-path="Border.Width"]'), 'Kanttykkelse', '0 px = ingen synlig kant. 1-12 px = synlig kant.');
            setControlLabel(design.querySelector('[data-h18-lego-design-path="Radius.All"]'), 'Hjørner / runding', '0 px = helt lige hjørner. Højere værdi = mere buede hjørner.');
        }
    }

    document.addEventListener('click', function (event) {
        const target = event.target && event.target.closest ? event.target : null;
        if (!target || !target.closest('.h18-builder-canvas')) { return; }
        if (target.closest(CANVAS_SELECTION_EXCLUDE_SELECTOR)) { return; }
        const element = target.closest(CANVAS_ELEMENT_SELECTOR);
        if (!element) { return; }

        event.preventDefault();
        event.stopPropagation();
        if (typeof event.stopImmediatePropagation === 'function') { event.stopImmediatePropagation(); }
        selectInspectorForNode(element);
        window.setTimeout(function () {
            clarifyInspectorControls();
            refreshSelectedCanvasMarker();
        }, 0);
    }, true);

    document.addEventListener('dblclick', function (event) {
        suppressDirectSetting(event, INLINE_EDIT_SELECTOR);
    }, true);

    document.addEventListener('click', function (event) {
        suppressDirectSetting(event, DIRECT_SETTING_SELECTOR);
    }, true);
    document.addEventListener('pointerdown', function (event) {
        suppressDirectSetting(event, '.h18-canvas-focal-dot');
    }, true);

    document.addEventListener('pointerdown', function (event) {
        const target = event.target && event.target.closest ? event.target.closest('.h18-v0841-resize-handle,.h18-v0841-resize-rail') : null;
        if (!target) { return; }
        refreshSelectedCanvasMarker();
        resizePointerActive = true;
    }, true);
    document.addEventListener('pointerup', function () {
        if (!resizePointerActive) { return; }
        resizePointerActive = false;
        armCompositionReconcile();
        window.setTimeout(refreshSelectedCanvasMarker, 0);
    }, true);
    document.addEventListener('pointercancel', function () {
        if (!resizePointerActive) { return; }
        resizePointerActive = false;
        armCompositionReconcile();
        window.setTimeout(refreshSelectedCanvasMarker, 0);
    }, true);

    document.addEventListener('click', function (event) {
        const trigger = event.target && event.target.closest ? event.target.closest(INSPECTOR_SELECTION_SELECTOR) : null;
        if (!trigger) { return; }

        if (trigger.classList.contains('h18-v0811-edit-child')) {
            const key = String(trigger.getAttribute('data-h18-v0811-edit-child') || '').trim();
            if (key) { rememberSelection(key, 'nested'); }
        } else {
            const row = trigger.closest('.h18-page-section-row');
            const key = rowKey(row) || selectedRowKey();
            /* Nested selection opens the same canonical row in Inspector. That
             * programmatic handoff must not downgrade the active child to a
             * top-level selection for the identical key. */
            const sameNestedHandoff = Boolean(
                key &&
                activeSelectionMode === 'nested' &&
                activeCanvasKey === key
            );
            if (key && !sameNestedHandoff) { rememberSelection(key, 'top'); }
        }

        armCompositionReconcile();
        window.setTimeout(function () {
            clarifyInspectorControls();
            refreshSelectedCanvasMarker();
        }, 0);
    }, false);

    if (window.MutationObserver) {
        const observer = new MutationObserver(function () {
            clarifyInspectorControls();
            refreshSelectedCanvasMarker();
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    window.setTimeout(function () {
        const initial = selectedRowKey();
        if (initial && !activeCanvasKey) { rememberSelection(initial, 'top'); }
        clarifyInspectorControls();
        refreshSelectedCanvasMarker();
    }, 0);

    document.documentElement.setAttribute('data-h18-lego-inspector-only', '0.8.47');
    document.documentElement.setAttribute('data-h18-lego-selection-marker', '0.8.72');
    window.__h18LegoInspectorOnlyV0847 = {
        version: '0.8.72',
        selectionOwner: 'stable-v0848-key-preserve-nested-handoff',
        selectInspectorForNode: selectInspectorForNode,
        armCompositionReconcile: armCompositionReconcile,
        clarifyInspectorControls: clarifyInspectorControls,
        refreshSelectedCanvasMarker: refreshSelectedCanvasMarker,
        rememberSelectedCanvasKey: function (key, nested) { return rememberSelection(key, nested ? 'nested' : 'top'); },
        activeSelection: function () { return { key: activeCanvasKey, mode: activeSelectionMode }; }
    };
}(jQuery));
