(function () {
    'use strict';

    var BASE_HEIGHT = 650;
    var BOTTOM_SPACE = 32;
    var root = null;
    var resizeObserver = null;
    var mutationObserver = null;
    var observedSections = [];
    var scheduled = false;
    var lastHeight = 0;

    function directSections() {
        if (!root) { return []; }
        return Array.prototype.filter.call(root.children, function (child) {
            return child && child.classList && child.classList.contains('h18-clean-node--section') && child.hasAttribute('data-node-id');
        });
    }

    function positiveTranslateY(element) {
        if (!element || !element.style || !element.style.transform) { return 0; }
        var match = String(element.style.transform).match(/translate\([^,]+,\s*(-?\d+(?:\.\d+)?)px\)/i);
        if (!match) { return 0; }
        var value = parseFloat(match[1]);
        return Number.isFinite(value) && value > 0 ? value : 0;
    }

    function sectionBottom(section) {
        return Math.max(0, Number(section.offsetTop || 0)) +
            Math.max(0, Number(section.offsetHeight || 0)) +
            positiveTranslateY(section);
    }

    function desiredHeight() {
        var bottom = 0;
        directSections().forEach(function (section) {
            bottom = Math.max(bottom, sectionBottom(section));
        });
        return Math.max(BASE_HEIGHT, Math.ceil(bottom + (bottom > 0 ? BOTTOM_SPACE : 0)));
    }

    function observeSections() {
        if (!resizeObserver) { return; }
        observedSections.forEach(function (section) {
            try { resizeObserver.unobserve(section); } catch (ignore) {}
        });
        observedSections = directSections();
        observedSections.forEach(function (section) { resizeObserver.observe(section); });
    }

    function sync() {
        scheduled = false;
        root = document.getElementById('h18-clean-canvas');
        if (!root) { return; }
        observeSections();
        var next = desiredHeight();
        if (next !== lastHeight || root.style.minHeight !== String(next) + 'px') {
            lastHeight = next;
            root.style.height = 'auto';
            root.style.minHeight = String(next) + 'px';
            root.setAttribute('data-vd-auto-height', '1');
            root.setAttribute('data-vd-auto-height-px', String(next));
            window.dispatchEvent(new CustomEvent('h18-vd-canvas-height', { detail: { height: next } }));
        }
    }

    function schedule() {
        if (scheduled) { return; }
        scheduled = true;
        window.requestAnimationFrame(sync);
    }

    function install() {
        root = document.getElementById('h18-clean-canvas');
        if (!root) { return; }
        if (window.ResizeObserver) {
            resizeObserver = new ResizeObserver(schedule);
            observeSections();
        }
        if (window.MutationObserver) {
            mutationObserver = new MutationObserver(schedule);
            mutationObserver.observe(root, {
                childList: true,
                subtree: true,
                attributes: true,
                attributeFilter: ['style', 'class', 'data-geometry']
            });
        }
        window.addEventListener('h18-vd-viewport-fit', schedule);
        window.addEventListener('resize', schedule, { passive: true });
        document.addEventListener('click', function (event) {
            if (!event.target || !event.target.closest) { return; }
            if (event.target.closest('.h18-clean-device-button,#h18-clean-undo,#h18-clean-redo,#h18-clean-delete,#h18-clean-paste,#h18-clean-duplicate')) {
                schedule();
            }
        }, true);
        schedule();
    }

    window.H18VDCanvasAutoHeight = {
        refresh: schedule,
        height: function () { return lastHeight || desiredHeight(); },
        baseHeight: BASE_HEIGHT,
        bottomSpace: BOTTOM_SPACE
    };

    if (document.getElementById('h18-clean-canvas')) { install(); }
    else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
