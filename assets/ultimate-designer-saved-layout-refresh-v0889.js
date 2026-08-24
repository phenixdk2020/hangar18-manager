(function () {
    'use strict';
    if (window.__h18SavedLayoutRefreshV0889) { return; }
    const VERSION = '0.8.89';
    let timer = 0;

    function invalidate() {
        document.querySelectorAll('.h18-v0889-saved-layout[data-h18-v0889-signature]').forEach(function (node) {
            node.removeAttribute('data-h18-v0889-signature');
        });
    }
    function refresh() {
        timer = 0;
        invalidate();
        const api = window.__h18SavedLayoutRebuildV0889;
        if (api && typeof api.refresh === 'function') {
            try { api.refresh(); } catch (ignore) {}
        }
    }
    function schedule() {
        if (timer) { window.clearTimeout(timer); }
        timer = window.setTimeout(refresh, 40);
    }
    document.addEventListener('input', schedule, false);
    document.addEventListener('change', schedule, false);
    document.addEventListener('h18:lego:resize', schedule, false);
    document.addEventListener('h18:lego:stack-changed', schedule, false);
    window.__h18SavedLayoutRefreshV0889 = { version: VERSION, refresh: refresh };
}());
