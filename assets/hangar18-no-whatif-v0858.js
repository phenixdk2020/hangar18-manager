(function () {
    'use strict';

    if (window.__h18NoWhatIfV0858) { return; }

    function removeWhatIfUi() {
        const root = document.querySelector('.h18-admin') || document;

        root.querySelectorAll('input[name="whatif"]').forEach(function (input) {
            input.checked = false;
            const shell = input.closest('.h18-whatif-help,.h18-safe-switch,label');
            if (shell) {
                shell.remove();
            } else {
                input.remove();
            }
        });

        root.querySelectorAll('.h18-whatif-help').forEach(function (node) {
            node.remove();
        });

        root.querySelectorAll('button,a,label,p,span,strong,small,div').forEach(function (node) {
            if (node.children.length > 0) { return; }
            if (/whatif/i.test(String(node.textContent || ''))) {
                node.remove();
            }
        });
    }

    removeWhatIfUi();
    window.setTimeout(removeWhatIfUi, 100);
    window.setTimeout(removeWhatIfUi, 500);

    window.__h18NoWhatIfV0858 = {
        version: '0.8.58',
        refresh: removeWhatIfUi
    };
}());
