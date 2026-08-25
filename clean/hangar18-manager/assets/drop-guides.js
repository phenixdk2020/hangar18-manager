(function () {
    'use strict';

    let badge = null;

    function ensureBadge() {
        if (badge && document.body.contains(badge)) { return badge; }
        badge = document.createElement('div');
        badge.className = 'h18-clean-drop-status';
        document.body.appendChild(badge);
        return badge;
    }

    function clearGuides() {
        document.querySelectorAll('.h18-clean-node.has-drop-choice,.h18-clean-node.is-drop-left,.h18-clean-node.is-drop-right').forEach(function (node) {
            node.classList.remove('has-drop-choice', 'is-drop-left', 'is-drop-right');
        });
        document.querySelectorAll('.h18-clean-surface.has-spatial-drop-guide').forEach(function (surface) {
            surface.classList.remove('has-spatial-drop-guide');
        });
        const status = ensureBadge();
        status.classList.remove('is-visible');
        status.textContent = '';
    }

    function directNode(surface, event) {
        if (!surface || !event) { return null; }
        const stack = document.elementsFromPoint ? document.elementsFromPoint(event.clientX, event.clientY) : [];
        for (let i = 0; i < stack.length; i += 1) {
            const candidate = stack[i] && stack[i].closest ? stack[i].closest('.h18-clean-node[data-node-id]') : null;
            if (candidate && candidate.parentElement === surface) { return candidate; }
        }
        const fallback = event.target && event.target.closest ? event.target.closest('.h18-clean-node[data-node-id]') : null;
        return fallback && fallback.parentElement === surface ? fallback : null;
    }

    function nodeLabel(node) {
        const strong = node ? node.querySelector(':scope > .h18-clean-node-header strong') : null;
        return strong ? String(strong.textContent || '').trim() : 'elementet';
    }

    function placeBadge(event, text) {
        const status = ensureBadge();
        status.textContent = text;
        status.classList.add('is-visible');
        const margin = 18;
        const width = Math.min(320, Math.max(160, status.offsetWidth || 220));
        const height = Math.max(36, status.offsetHeight || 36);
        let left = event.clientX + margin;
        let top = event.clientY + margin;
        if (left + width > window.innerWidth - 8) { left = Math.max(8, event.clientX - width - margin); }
        if (top + height > window.innerHeight - 8) { top = Math.max(8, event.clientY - height - margin); }
        status.style.left = left + 'px';
        status.style.top = top + 'px';
    }

    function showGuide(event) {
        const surface = event.target && event.target.closest ? event.target.closest('.h18-clean-surface') : null;
        if (!surface) { return; }

        const target = directNode(surface, event);
        document.querySelectorAll('.h18-clean-node.has-drop-choice,.h18-clean-node.is-drop-left,.h18-clean-node.is-drop-right').forEach(function (node) {
            node.classList.remove('has-drop-choice', 'is-drop-left', 'is-drop-right');
        });
        document.querySelectorAll('.h18-clean-surface.has-spatial-drop-guide').forEach(function (item) {
            item.classList.remove('has-spatial-drop-guide');
        });
        surface.classList.add('has-spatial-drop-guide');

        if (!target) {
            const status = ensureBadge();
            status.classList.remove('is-visible');
            return;
        }

        const rect = target.getBoundingClientRect();
        const left = event.clientX < rect.left + rect.width / 2;
        target.classList.add('has-drop-choice', left ? 'is-drop-left' : 'is-drop-right');
        const label = nodeLabel(target);
        placeBadge(event, left ? '← Slip til VENSTRE for ' + label : 'Slip til HØJRE for ' + label + ' →');
    }

    function install() {
        ensureBadge();
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
