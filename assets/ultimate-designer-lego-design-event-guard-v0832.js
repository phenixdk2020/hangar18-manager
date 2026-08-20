(function () {
    'use strict';

    document.addEventListener('input', function (event) {
        const target = event.target;
        if (!target || typeof target.matches !== 'function') {
            return;
        }
        if (target.matches('#h18-ud-lego-design-panel select[data-h18-lego-design-path]')) {
            // Native selects emit input + change in modern browsers. The design
            // runtime intentionally handles the change event only as the logical
            // user action, so stop the redundant bubbling input before jQuery's
            // delegated document handler can turn it into a second checkpoint.
            event.stopPropagation();
        }
    }, true);

    document.documentElement.setAttribute('data-h18-lego-design-select-guard', '0.8.32');
}());
