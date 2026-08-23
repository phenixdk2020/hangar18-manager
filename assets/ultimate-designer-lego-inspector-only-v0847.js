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

    const CANVAS_ELEMENT_SELECTOR = [
        '.h18-v0851-stack-segment[data-h18-v0851-stack-key]',
        '.h18-v0811-auto-box[data-h18-v0811-row]',
        '.h18-v0811-child-card[data-h18-v0811-child]',
        '.h18-page-section-row > .h18-canvas-preview'
    ].join(',');

    const CANVAS_SELECTION_EXCLUDE_SELECTOR = [
        '.h18-v0841-resize-handle',
        '.h18-v0841-resize-rail',
        '.h18-v0851-stack-resize-handle',
        '.h18-v0811-edit-child',
        '.h18-page-section-edit',
        '.h18-v0811-side-zone',
        '.h18-v0814-auto-drop-zone',
        '.h18-v0814-auto-kasse-drop',
        '.h18-ud-box-drop-zone'
    ].join(',');

    const SELECTED_CANVAS_CLASS = 'is-h18-v0848-selected-element';
    const SELECTED_ROW_CLASS = 'is-h18-v0863-selected-row';
    let resizePointerActive = false;
    let selectedCanvasKey = '';

    function rememberSelectedCanvasKey(key) {
        const value = String(key || '').trim();
        if (value) { selectedCanvasKey = value; }
        return selectedCanvasKey;
    }

    function armCompositionReconcile() {
        window.setTimeout(function () {
            const guard = window.__h18LegoParentKeyGuardV0845;
            if (!guard) { return; }
            if (typeof guard.reconcileNow === 'function') { guard.reconcileNow(); }
            if (typeof guard.armVisualReconcile === 'function') { guard.armVisualReconcile(); }
        }, 0);
    }

    function keyFromRow(row) {
        if (!row) { return ''; }
        const direct = row.querySelector('.h18-page-section-key');
        return String((direct && direct.value) || row.getAttribute('data-key') || '').trim();
    }

    function visualKey(node) {
        if (!node || !node.getAttribute) { return ''; }
        return String(
            node.getAttribute('data-h18-v0851-stack-key') ||
            node.getAttribute('data-h18-v0811-row') ||
            node.getAttribute('data-h18-v0811-child') ||
            ''
        ).trim();
    }

    function selectedRowKey() {
        // The clicked key is authoritative during the Inspector handoff and
        // remains authoritative while Grid/stack renderers replace visual DOM.
        if (selectedCanvasKey) { return selectedCanvasKey; }

        const row = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
        const rowKey = keyFromRow(row);
        if (rowKey) { return rememberSelectedCanvasKey(rowKey); }

        const inspector = document.querySelector('#h18-page-inspector-target .h18-page-section-key');
        const inspectorKey = inspector && inspector.value ? String(inspector.value).trim() : '';
        return inspectorKey ? rememberSelectedCanvasKey(inspectorKey) : '';
    }

    function canonicalRowByKey(key) {
        const requested = String(key || '');
        if (!requested) { return null; }
        const rows = document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)');
        for (let i = 0; i < rows.length; i += 1) {
            const row = rows[i];
            if (keyFromRow(row) === requested) { return row; }
        }
        return null;
    }

    function activateCanonicalRow(row) {
        if (!row) { return false; }
        const edit = row.querySelector('.h18-page-section-edit');
        const header = row.querySelector('.h18-page-section-header');
        const target = edit || header;
        if (!target) { return false; }

        if (window.jQuery) { window.jQuery(target).trigger('click'); }
        else if (typeof target.click === 'function') { target.click(); }
        else { return false; }
        return true;
    }

    function refreshSelectedCanvasMarker() {
        const key = selectedRowKey();
        if (!key) { return; }

        document.documentElement.setAttribute('data-h18-selected-element-key', key);

        // Keep a persistent marker on the canonical row as a fallback even when
        // WordPress temporarily removes .is-selected while moving its body into
        // Inspector. This does not change layout or persistence.
        document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)').forEach(function (row) {
            const rowMatches = keyFromRow(row) === key;
            row.classList.toggle(SELECTED_ROW_CLASS, rowMatches);
            if (rowMatches) { row.setAttribute('data-key', key); }
        });

        // LEGO-063: selection follows the canonical element key, not a specific
        // wrapper instance. Stack rendering can replace an Auto-box child with a
        // stack-segment; both forms therefore receive the same persistent class.
        document.querySelectorAll([
            '.h18-v0811-auto-box[data-h18-v0811-row]',
            '.h18-v0811-child-card[data-h18-v0811-child]',
            '.h18-v0851-stack-segment[data-h18-v0851-stack-key]'
        ].join(',')).forEach(function (node) {
            node.classList.toggle(SELECTED_CANVAS_CLASS, visualKey(node) === key);
        });
    }

    function selectInspectorForNode(node) {
        if (!node || !node.closest) { return false; }

        const nested = node.closest([
            '.h18-v0851-stack-segment[data-h18-v0851-stack-key]',
            '.h18-v0811-auto-box[data-h18-v0811-row]',
            '.h18-v0811-child-card[data-h18-v0811-child]'
        ].join(','));
        if (nested) {
            const nestedKey = visualKey(nested);
            rememberSelectedCanvasKey(nestedKey);
            refreshSelectedCanvasMarker();
            const canonicalRow = canonicalRowByKey(nestedKey);
            if (canonicalRow && activateCanonicalRow(canonicalRow)) {
                armCompositionReconcile();
                window.setTimeout(refreshSelectedCanvasMarker, 0);
                return true;
            }

            const edit = nested.querySelector('.h18-v0811-edit-child');
            if (edit) {
                if (window.jQuery) { window.jQuery(edit).trigger('click'); }
                else { edit.click(); }
                armCompositionReconcile();
                window.setTimeout(refreshSelectedCanvasMarker, 0);
                return true;
            }
        }

        const row = node.closest('.h18-page-section-row');
        if (!row) { return false; }
        rememberSelectedCanvasKey(keyFromRow(row));
        if (!activateCanonicalRow(row)) { return false; }
        armCompositionReconcile();
        window.setTimeout(refreshSelectedCanvasMarker, 0);
        return true;
    }

    function suppressDirectSetting(event, selector) {
        const target = event.target && event.target.closest ? event.target.closest(selector) : null;
        if (!target) { return; }
        if (target.closest('.h18-v0841-resize-handle,.h18-v0841-resize-rail,.h18-v0851-stack-resize-handle')) { return; }
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
        const target = event.target && event.target.closest ? event.target.closest('.h18-v0841-resize-handle,.h18-v0841-resize-rail,.h18-v0851-stack-resize-handle') : null;
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
        const triggerRow = trigger.closest('.h18-page-section-row');
        const triggerKey = keyFromRow(triggerRow);
        if (triggerKey) { rememberSelectedCanvasKey(triggerKey); }
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
        clarifyInspectorControls();
        refreshSelectedCanvasMarker();
    }, 0);

    document.documentElement.setAttribute('data-h18-lego-inspector-only', '0.8.47');
    document.documentElement.setAttribute('data-h18-lego-selection-marker', '0.8.63');
    window.__h18LegoInspectorOnlyV0847 = {
        version: '0.8.63',
        selectInspectorForNode: selectInspectorForNode,
        armCompositionReconcile: armCompositionReconcile,
        clarifyInspectorControls: clarifyInspectorControls,
        rememberSelectedCanvasKey: rememberSelectedCanvasKey,
        refreshSelectedCanvasMarker: refreshSelectedCanvasMarker,
        selectedKey: function () { return selectedCanvasKey; }
    };
}(jQuery));
