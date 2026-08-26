(function () {
    'use strict';

    const TYPES = ['section', 'container', 'text', 'image', 'button'];
    const LABELS = {
        section: 'Sektion',
        container: 'Kasse',
        text: 'Tekst',
        image: 'Billede',
        button: 'Knap'
    };
    let activeDrag = null;
    let toastTimer = 0;

    function cleanType(value) {
        const type = String(value || '').toLowerCase();
        return TYPES.includes(type) ? type : '';
    }

    function nodeType(card) {
        if (!card || !card.classList) { return ''; }
        for (const type of TYPES) {
            if (card.classList.contains('h18-clean-node--' + type)) { return type; }
        }
        return '';
    }

    function nodeId(card) {
        return card ? String(card.getAttribute('data-node-id') || '') : '';
    }

    function directTarget(event, surface) {
        const raw = event && event.target && event.target.closest
            ? event.target.closest('.h18-clean-node[data-node-id]')
            : null;
        if (!raw || !surface || raw.parentElement !== surface) { return null; }
        return {
            card: raw,
            id: nodeId(raw),
            type: nodeType(raw)
        };
    }

    function zoneFor(event, target) {
        if (!target || !target.card) { return 'free'; }
        const rect = target.card.getBoundingClientRect();
        const rx = Math.max(0, Math.min(1, (event.clientX - rect.left) / Math.max(1, rect.width)));
        const ry = Math.max(0, Math.min(1, (event.clientY - rect.top) / Math.max(1, rect.height)));
        const parentType = target.type === 'section' || target.type === 'container';
        if (parentType) {
            if (ry < 0.22) { return 'above'; }
            if (ry > 0.78) { return 'below'; }
            if (rx < 0.22) { return 'left'; }
            if (rx > 0.78) { return 'right'; }
            return 'inside';
        }
        if (ry < 0.28) { return 'above'; }
        if (ry > 0.72) { return 'below'; }
        return rx < 0.5 ? 'left' : 'right';
    }

    function decision(event, surface, type) {
        type = cleanType(type);
        if (!type || !surface) {
            return { allowed: true, message: '' };
        }

        const baseParentId = String(surface.getAttribute('data-parent-id') || '');
        const target = directTarget(event, surface);
        const zone = zoneFor(event, target);
        let effectiveParentId = baseParentId;

        if (target && zone === 'inside' && (target.type === 'section' || target.type === 'container')) {
            effectiveParentId = target.id;
        }

        if (type === 'section') {
            if (baseParentId !== '') {
                return {
                    allowed: false,
                    message: 'Sektion kan kun placeres på sideniveau. Brug Kasse inde i en Sektion eller Kasse.'
                };
            }
            if (target && !['above', 'below'].includes(zone)) {
                return {
                    allowed: false,
                    message: 'Sektioner ligger på sideniveau over/under hinanden. Slip over eller under en Sektion.'
                };
            }
            return { allowed: true, message: '' };
        }

        if (effectiveParentId === '') {
            return {
                allowed: false,
                message: (LABELS[type] || 'Elementet') + ' skal ligge inde i en Sektion eller Kasse.'
            };
        }

        return { allowed: true, message: '' };
    }

    function toast(message, event) {
        let el = document.getElementById('h18-clean-hierarchy-toast');
        if (!el) {
            el = document.createElement('div');
            el.id = 'h18-clean-hierarchy-toast';
            el.className = 'h18-clean-hierarchy-toast';
            el.setAttribute('role', 'status');
            el.setAttribute('aria-live', 'polite');
            document.body.appendChild(el);
        }
        el.textContent = String(message || 'Ulovlig placering');
        if (event && Number.isFinite(event.clientX) && Number.isFinite(event.clientY)) {
            el.style.left = Math.min(window.innerWidth - 330, Math.max(10, event.clientX + 16)) + 'px';
            el.style.top = Math.min(window.innerHeight - 70, Math.max(10, event.clientY + 16)) + 'px';
        } else {
            el.style.left = '50%';
            el.style.top = '90px';
        }
        el.classList.add('is-visible');
        window.clearTimeout(toastTimer);
        toastTimer = window.setTimeout(function () {
            el.classList.remove('is-visible');
        }, 2600);
    }

    function clearInvalid() {
        document.querySelectorAll('.h18-clean-hierarchy-invalid').forEach(function (surface) {
            surface.classList.remove('h18-clean-hierarchy-invalid');
        });
    }

    function beginDrag(event) {
        const target = event.target;
        if (!target || !target.closest) { return; }

        const palette = target.closest('.h18-clean-add[data-type]');
        if (palette) {
            const type = cleanType(palette.getAttribute('data-type'));
            activeDrag = type ? { kind: 'palette', type: type } : null;
            return;
        }

        const move = target.closest('.h18-clean-move');
        if (!move) { return; }
        const card = move.closest('.h18-clean-node[data-node-id]');
        const type = nodeType(card);
        activeDrag = type ? { kind: 'node', type: type, id: nodeId(card) } : null;
    }

    function endDrag() {
        activeDrag = null;
        clearInvalid();
    }

    function interceptDrag(event) {
        if (!activeDrag || !event.target || !event.target.closest) { return; }
        const surface = event.target.closest('.h18-clean-surface');
        if (!surface) { return; }

        const result = decision(event, surface, activeDrag.type);
        if (result.allowed) {
            surface.classList.remove('h18-clean-hierarchy-invalid');
            return;
        }

        event.preventDefault();
        event.stopImmediatePropagation();
        if (event.dataTransfer) {
            try { event.dataTransfer.dropEffect = 'none'; } catch (ignore) {}
        }
        surface.classList.add('h18-clean-hierarchy-invalid');
        if (event.type === 'drop') {
            toast(result.message, event);
            endDrag();
        }
    }

    function interceptPaletteClick(event) {
        if (!event.target || !event.target.closest) { return; }
        const button = event.target.closest('.h18-clean-add[data-type]');
        if (!button) { return; }
        const type = cleanType(button.getAttribute('data-type'));
        if (!type || type === 'section') { return; }

        // Core 0.1.21 click-add always targets root. 0.1.22 keeps click-add for
        // Section only; all child element types must be dragged into a wrapper.
        event.preventDefault();
        event.stopImmediatePropagation();
        toast((LABELS[type] || 'Elementet') + ' skal trækkes ind i en Sektion eller Kasse.', null);
    }

    function installHints() {
        document.querySelectorAll('.h18-clean-add[data-type]').forEach(function (button) {
            const type = cleanType(button.getAttribute('data-type'));
            if (type === 'section') {
                button.title = 'Klik eller træk: opret Sektion på sideniveau';
            } else if (type) {
                button.title = 'Træk ' + (LABELS[type] || type) + ' ind i en Sektion eller Kasse';
            }
        });
    }

    function install() {
        installHints();
        document.addEventListener('click', interceptPaletteClick, true);
        document.addEventListener('dragstart', beginDrag, true);
        document.addEventListener('dragend', endDrag, true);
        document.addEventListener('dragover', interceptDrag, true);
        document.addEventListener('drop', interceptDrag, true);
        document.addEventListener('dragleave', function (event) {
            const surface = event.target && event.target.closest ? event.target.closest('.h18-clean-surface') : null;
            if (surface && (!event.relatedTarget || !surface.contains(event.relatedTarget))) {
                surface.classList.remove('h18-clean-hierarchy-invalid');
            }
        }, true);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
