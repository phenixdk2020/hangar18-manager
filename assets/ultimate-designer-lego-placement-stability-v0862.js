jQuery(function () {
    'use strict';

    /*
     * LEGO-064 rollback:
     * v0.8.62 introduced a second placement owner on top of the established
     * v0.8.58/v0.8.51 nesting + drop-zone runtime. Manual v0.8.63 evidence
     * shows existing element drag can still degrade to raw Sortable reorder.
     *
     * Keep this file as an inert compatibility marker, but register no drag,
     * sort, drop, placement, parent or refresh handlers. Placement is again
     * owned exclusively by the canonical pre-v0.8.62 runtime.
     */
    document.documentElement.setAttribute('data-h18-lego-placement-stability', '0.8.64-disabled');
    window.__h18LegoPlacementStabilityV0862 = {
        version: '0.8.64',
        disabled: true,
        placementOwner: 'v0.8.58-baseline'
    };
}());
