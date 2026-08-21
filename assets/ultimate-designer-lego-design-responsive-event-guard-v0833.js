(function () {
    'use strict';

    document.addEventListener('input', function (event) {
        const target = event.target;
        if (!target || typeof target.matches !== 'function') {
            return;
        }
        if (target.matches('#h18-ud-lego-responsive-design-panel select[data-h18-rd-path]')) {
            // Native selects can emit both input and change. The responsive design
            // runtime owns the logical change event; suppress the redundant input
            // before delegated history listeners can create a second checkpoint.
            event.stopPropagation();
        }
    }, true);

    document.documentElement.setAttribute('data-h18-lego-responsive-design-select-guard', '0.8.33');
}());
