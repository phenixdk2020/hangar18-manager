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

    // Selecting a nested child moves its authoritative settings body into the
    // existing Inspector. The base editor can repaint the parent Grid during that
    // handoff. Re-arm the existing read-only visual reconciliation so the canvas
    // continues to show the same children while settings are edited in Inspector.
    document.addEventListener('click', function (event) {
        const trigger = event.target && event.target.closest ? event.target.closest(INSPECTOR_SELECTION_SELECTOR) : null;
        if (!trigger) { return; }
        armCompositionReconcile();
    }, false);

    document.documentElement.setAttribute('data-h18-lego-inspector-only', '0.8.47');
    window.__h18LegoInspectorOnlyV0847 = {
        version: '0.8.47',
        selectInspectorForNode: selectInspectorForNode,
        armCompositionReconcile: armCompositionReconcile
    };
}(jQuery));
