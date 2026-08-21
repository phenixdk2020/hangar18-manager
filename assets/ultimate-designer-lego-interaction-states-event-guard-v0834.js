(function () {
    'use strict';

    document.addEventListener('input', function (event) {
        const target = event.target;
        if (!target || typeof target.matches !== 'function') {
            return;
        }
        if (target.matches('#h18-ud-lego-interaction-states-panel select[data-h18-is-path]')) {
            // Native selects can emit both input and change. The v0.8.34
            // interaction runtime uses change as the one logical history event.
            event.stopPropagation();
        }
    }, true);

    document.documentElement.setAttribute('data-h18-lego-interaction-states-select-guard', '0.8.34');
}());
