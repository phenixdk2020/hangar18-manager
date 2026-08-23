jQuery(function () {
    'use strict';

    /*
     * LEGO-064 controlled rollback:
     *
     * 1) v0.8.62's second placement owner stays disabled. Existing-element
     *    placement is again owned exclusively by the known v0.8.58/v0.8.51
     *    nesting + drop-zone runtime.
     *
     * 2) Top-level selection identity is captured on pointerdown, before the
     *    canonical click moves .h18-page-section-key into Inspector. The normal
     *    v0.8.63 selection owner can then resolve the row through data-key and
     *    keep its persistent red frame. No render, refresh, timeout or observer
     *    is introduced here.
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

    document.documentElement.setAttribute('data-h18-lego-placement-stability', '0.8.64-disabled');
    document.documentElement.setAttribute('data-h18-lego-selection-key-preflight', '0.8.64');

    window.__h18LegoPlacementStabilityV0862 = {
        version: '0.8.64',
        disabled: true,
        placementOwner: 'v0.8.58-baseline',
        selectionKeyPreflight: true
    };
}());
