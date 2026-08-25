(function () {
    'use strict';

    const UNITS = 120;

    function clearGuides() {
        document.querySelectorAll('.h18-clean-node.is-drop-left,.h18-clean-node.is-drop-right').forEach(function (node) {
            node.classList.remove('is-drop-left', 'is-drop-right');
        });
        document.querySelectorAll('.h18-clean-surface.has-spatial-drop-guide').forEach(function (surface) {
            surface.classList.remove('has-spatial-drop-guide');
        });
    }

    function activeDragWidth() {
        const moving = document.querySelector('.h18-clean-node.is-dragging[data-geometry]');
        if (moving) {
            const parts = String(moving.getAttribute('data-geometry') || '').split(',');
            const width = parseInt(parts[2] || '0', 10) || 0;
            if (width > 0) { return Math.min(UNITS, width); }
        }
        const palette = document.querySelector('.h18-clean-add.is-palette-dragging[data-type]');
        if (palette) {
            return String(palette.getAttribute('data-type') || '') === 'section' ? UNITS : 60;
        }
        return 60;
    }

    function directNode(surface, target) {
        if (!surface || !target || !target.closest) { return null; }
        const node = target.closest('.h18-clean-node[data-node-id]');
        return node && node.parentElement === surface ? node : null;
    }

    function showGuide(event) {
        const surface = event.target && event.target.closest ? event.target.closest('.h18-clean-surface') : null;
        if (!surface) { return; }
        const target = directNode(surface, event.target);
        clearGuides();
        surface.classList.add('has-spatial-drop-guide');
        if (!target) { return; }

        const rect = target.getBoundingClientRect();
        const left = event.clientX < rect.left + rect.width / 2;
        target.classList.add(left ? 'is-drop-left' : 'is-drop-right');
        target.style.setProperty('--h18-drop-width', String(activeDragWidth()));
    }

    function install() {
        document.addEventListener('dragover', showGuide, true);
        document.addEventListener('drop', clearGuides, true);
        document.addEventListener('dragend', clearGuides, true);
        document.addEventListener('dragleave', function (event) {
            if (!event.relatedTarget) { clearGuides(); }
        }, true);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
