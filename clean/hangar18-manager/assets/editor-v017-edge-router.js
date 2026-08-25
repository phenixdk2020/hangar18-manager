(function () {
    'use strict';

    function directChildNode(surface, target) {
        if (!surface || !target || !target.closest) { return null; }
        const node = target.closest('.h18-clean-node[data-node-id]');
        return node && node.parentElement === surface ? node : null;
    }

    function shouldRouteToOuter(surface, event) {
        if (!surface.classList.contains('h18-clean-inner-surface')) { return false; }
        if (directChildNode(surface, event.target)) { return false; }
        const card = surface.closest('.h18-clean-node[data-node-id]');
        if (!card || !card.parentElement || !card.parentElement.classList.contains('h18-clean-surface')) { return false; }
        const rect = card.getBoundingClientRect();
        const rx = Math.max(0, Math.min(1, (event.clientX - rect.left) / Math.max(1, rect.width)));
        const ry = Math.max(0, Math.min(1, (event.clientY - rect.top) / Math.max(1, rect.height)));
        return ry < 0.22 || ry > 0.78 || rx < 0.22 || rx > 0.78;
    }

    function wrap(surface) {
        if (!surface || surface.dataset.h18V017EdgeRouter === '1') { return; }
        if (typeof surface.ondragover !== 'function' || typeof surface.ondrop !== 'function') { return; }
        surface.dataset.h18V017EdgeRouter = '1';
        const oldOver = surface.ondragover;
        const oldDrop = surface.ondrop;
        const oldLeave = surface.ondragleave;

        surface.ondragover = function (event) {
            if (shouldRouteToOuter(surface, event)) { return; }
            return oldOver.call(surface, event);
        };
        surface.ondrop = function (event) {
            if (shouldRouteToOuter(surface, event)) { return; }
            return oldDrop.call(surface, event);
        };
        surface.ondragleave = function (event) {
            if (typeof oldLeave === 'function') { return oldLeave.call(surface, event); }
        };
    }

    function scan() {
        document.querySelectorAll('.h18-clean-inner-surface').forEach(wrap);
    }

    function install() {
        scan();
        const workspace = document.querySelector('.h18-clean-workspace');
        if (workspace && window.MutationObserver) {
            const observer = new MutationObserver(scan);
            observer.observe(workspace, { childList: true, subtree: true });
        }
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
