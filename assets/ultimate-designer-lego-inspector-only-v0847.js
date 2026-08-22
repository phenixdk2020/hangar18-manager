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

    // A normal click anywhere in a visible element should select that element
    // for Inspector editing. Nested Auto-kasse/Kasse tiles win over their cloned
    // source preview; a normal top-level preview resolves to its source row.
    const CANVAS_ELEMENT_SELECTOR = [
        '.h18-v0811-auto-box[data-h18-v0811-row]',
        '.h18-v0811-child-card[data-h18-v0811-child]',
        '.h18-page-section-row > .h18-canvas-preview'
    ].join(',');

    // These controls remain direct canvas/layout manipulation and must never be
    // converted into Inspector-selection clicks.
    const CANVAS_SELECTION_EXCLUDE_SELECTOR = [
        '.h18-v0841-resize-handle',
        '.h18-v0841-resize-rail',
        '.h18-v0811-edit-child',
        '.h18-page-section-edit',
        '.h18-v0811-side-zone',
        '.h18-v0814-auto-drop-zone',
        '.h18-v0814-auto-kasse-drop',
        '.h18-ud-box-drop-zone'
    ].join(',');

    function armCompositionReconcile() {
        window.setTimeout(function () {
            const guard = window.__h18LegoParentKeyGuardV0845;
            if (!guard) { return; }
            if (typeof guard.reconcileNow === 'function') { guard.reconcileNow(); }
            if (typeof guard.armVisualReconcile === 'function') { guard.armVisualReconcile(); }
        }, 0);
    }

    function selectInspectorForNode(node) {
        if (!node || !node.closest) { return false; }

        const nested = node.closest('.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child]');
        if (nested) {
            const edit = nested.querySelector('.h18-v0811-edit-child');
            if (edit) {
                edit.click();
                armCompositionReconcile();
                return true;
            }
        }

        const row = node.closest('.h18-page-section-row');
        if (!row) { return false; }
        const edit = row.querySelector('.h18-page-section-edit');
        const header = row.querySelector('.h18-page-section-header');
        if (edit) { edit.click(); }
        else if (header) { header.click(); }
        else { return false; }
        armCompositionReconcile();
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
        if (String(node.textContent || '') !== next) {
            node.textContent = next;
        }
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
            const background = design.querySelector('[data-h18-lego-design-path="Colors.Background"]');
            setControlLabel(background, 'Elementfarve / baggrund', 'Farven på selve elementets flade.');

            const borderColor = design.querySelector('[data-h18-lego-design-path="Border.Color"]');
            setControlLabel(borderColor, 'Kantfarve', 'Bruges når kanttykkelsen er større end 0 px.');

            const borderWidth = design.querySelector('[data-h18-lego-design-path="Border.Width"]');
            setControlLabel(borderWidth, 'Kanttykkelse', '0 px = ingen synlig kant. 1-12 px = synlig kant.');

            const radius = design.querySelector('[data-h18-lego-design-path="Radius.All"]');
            setControlLabel(radius, 'Hjørner / runding', '0 px = helt lige hjørner. Højere værdi = mere buede hjørner.');
        }
    }

    // Single-click is the primary LEGO selection gesture: click the element,
    // then edit all content/design settings in Inspector. Embedded preview
    // actions are deliberately suppressed; drag/drop and resize controls above
    // are excluded and keep their direct-manipulation behavior.
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
        window.setTimeout(clarifyInspectorControls, 0);
    }, true);

    // Content, typography, media and image settings are Inspector-owned.
    // Double-click on canvas content therefore selects the element instead of
    // activating the legacy inline editor/media picker.
    document.addEventListener('dblclick', function (event) {
        suppressDirectSetting(event, INLINE_EDIT_SELECTOR);
    }, true);

    // Old image controls can still exist in a cached preview. Block them at the
    // event boundary and route the user to Inspector. Resize handles are not part
    // of this selector and remain direct-manipulation controls on the canvas.
    document.addEventListener('click', function (event) {
        suppressDirectSetting(event, DIRECT_SETTING_SELECTOR);
    }, true);
    document.addEventListener('pointerdown', function (event) {
        suppressDirectSetting(event, '.h18-canvas-focal-dot');
    }, true);

    // Selecting through explicit Rediger/header controls also keeps the same
    // reconciliation contract. The base editor can repaint the parent Grid during
    // Inspector handoff; re-arm the existing read-only visual reconciliation.
    document.addEventListener('click', function (event) {
        const trigger = event.target && event.target.closest ? event.target.closest(INSPECTOR_SELECTION_SELECTOR) : null;
        if (!trigger) { return; }
        armCompositionReconcile();
        window.setTimeout(clarifyInspectorControls, 0);
    }, false);

    // Spacing/design panels are rendered dynamically when selection changes.
    // Keep the canonical fields unchanged and only give the existing controls the
    // user-facing names that match the LEGO editing model. Relabeling is strictly
    // idempotent so this observer never feeds itself with redundant text writes.
    if (window.MutationObserver) {
        const observer = new MutationObserver(function () { clarifyInspectorControls(); });
        observer.observe(document.body, { childList: true, subtree: true });
    }
    window.setTimeout(clarifyInspectorControls, 0);

    document.documentElement.setAttribute('data-h18-lego-inspector-only', '0.8.47');
    window.__h18LegoInspectorOnlyV0847 = {
        version: '0.8.47',
        selectInspectorForNode: selectInspectorForNode,
        armCompositionReconcile: armCompositionReconcile,
        clarifyInspectorControls: clarifyInspectorControls
    };
}(jQuery));
