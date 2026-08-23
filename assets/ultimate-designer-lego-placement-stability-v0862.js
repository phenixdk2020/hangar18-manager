jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    if (!$sections.length) { return; }

    /*
     * LEGO-066:
     * Do not register a second Sortable/drop placement owner here.
     * Existing-element placement is owned exclusively by the canonical
     * nesting-tools runtime, including moveRowIntoBox(), side placement and
     * normal reorder. The Kasse hit surface is widened with CSS instead.
     *
     * Keep only the harmless top-level key preflight used by persistent
     * selection before WordPress moves structural fields into Inspector.
     */
    document.addEventListener('pointerdown', function (event) {
        const target = event.target && event.target.closest ? event.target : null;
        if (!target || !target.closest('.h18-builder-canvas')) { return; }

        const preview = target.closest('.h18-canvas-preview');
        if (!preview) { return; }

        const row = preview.parentElement;
        if (!row || !row.matches('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)')) {
            return;
        }

        const keyField = row.querySelector('.h18-page-section-key');
        const key = String((keyField && keyField.value) || row.getAttribute('data-key') || '').trim();
        if (key) { row.setAttribute('data-key', key); }
    }, true);

    document.documentElement.setAttribute('data-h18-lego-placement-stability', '0.8.66-baseline-owner');
    document.documentElement.setAttribute('data-h18-lego-selection-key-preflight', '0.8.66');

    window.__h18LegoPlacementStabilityV0862 = {
        version: '0.8.66',
        disabled: true,
        placementOwner: 'nesting-tools-baseline',
        selectionKeyPreflight: true
    };
}());
