(function () {
    'use strict';

    if (window.__h18InspectorOrderV0884) { return; }

    const VERSION = '0.8.84';
    const ROOT_SELECTOR = '#h18-page-inspector-target > .h18-page-section-body';
    const DYNAMIC_SELECTOR = '.h18-dynamic-binding-box';
    const CONDITIONS_SELECTOR = '.h18-condition-editor';
    const MEDIA_INPUT_SELECTOR = '.h18-section-media-id';
    const MEDIA_TYPES = ['hero', 'text_image', 'image'];
    let observer = null;
    let timer = 0;
    let applying = false;

    function directHeader(box) {
        if (!box) { return null; }
        return Array.from(box.children || []).find(function (node) {
            return node.tagName && node.tagName.toLowerCase() === 'h4';
        }) || box.querySelector('h4');
    }

    function updateMarker(box, collapsed) {
        const header = directHeader(box);
        const marker = header ? header.querySelector('.h18-v0884-collapse-marker') : null;
        if (marker) { marker.textContent = collapsed ? '▸' : '▾'; }
    }

    function setCollapsed(box, collapsed) {
        if (!box) { return; }
        const header = directHeader(box);
        if (!header) { return; }
        const value = collapsed === true;
        box.classList.toggle('h18-v0884-collapsed', value);
        box.setAttribute('data-h18-v0884-collapsed', value ? '1' : '0');
        header.setAttribute('aria-expanded', value ? 'false' : 'true');
        Array.from(box.children).forEach(function (child) {
            if (child === header) { return; }
            child.hidden = value;
        });
        updateMarker(box, value);
    }

    function prepareCollapsible(box) {
        if (!box) { return; }
        const header = directHeader(box);
        if (!header) { return; }

        if (box.getAttribute('data-h18-v0884-collapse-ready') !== '1') {
            box.setAttribute('data-h18-v0884-collapse-ready', '1');
            header.classList.add('h18-v0884-collapse-header');
            header.setAttribute('role', 'button');
            header.setAttribute('tabindex', '0');
            header.setAttribute('aria-expanded', 'false');

            if (!header.querySelector('.h18-v0884-collapse-marker')) {
                const marker = document.createElement('span');
                marker.className = 'h18-v0884-collapse-marker';
                marker.setAttribute('aria-hidden', 'true');
                header.appendChild(marker);
            }

            setCollapsed(box, true);
        }
    }

    function toggleFromHeader(header) {
        const box = header && header.closest
            ? header.closest(DYNAMIC_SELECTOR + ',' + CONDITIONS_SELECTOR)
            : null;
        if (!box) { return; }
        const collapsed = box.getAttribute('data-h18-v0884-collapsed') === '1';
        setCollapsed(box, !collapsed);
    }

    function sectionType(body) {
        if (!body) { return ''; }
        const field = body.querySelector('.h18-page-section-type,[name$="[Type]"]');
        return String(field && field.value || '').trim();
    }

    function mediaBox(body) {
        if (!body || MEDIA_TYPES.indexOf(sectionType(body)) === -1) { return null; }
        const input = body.querySelector(MEDIA_INPUT_SELECTOR);
        return input && input.closest ? input.closest('.h18-section-module-box') : null;
    }

    function tailIsCorrect(body, desired) {
        const nodes = desired.filter(Boolean);
        if (!nodes.length) { return true; }
        const children = Array.from(body.children || []);
        if (children.length < nodes.length) { return false; }
        const start = children.length - nodes.length;
        return nodes.every(function (node, index) {
            return node.parentElement === body && children[start + index] === node;
        });
    }

    function applyOrder() {
        timer = 0;
        if (applying) { return; }
        const body = document.querySelector(ROOT_SELECTOR);
        if (!body) { return; }

        applying = true;
        try {
            const dynamicBox = body.querySelector(DYNAMIC_SELECTOR);
            const conditionsBox = body.querySelector(CONDITIONS_SELECTOR);
            const imageBox = mediaBox(body);

            prepareCollapsible(dynamicBox);
            prepareCollapsible(conditionsBox);

            /*
             * Inspector contract v0.8.84:
             * - all ordinary/type-specific controls remain before the advanced tail
             * - image/media module is immediately before the advanced tail for media-capable types
             * - Dynamic data binding is penultimate
             * - Conditions / synlighed is always last
             */
            const desiredTail = [imageBox, dynamicBox, conditionsBox].filter(Boolean);
            if (!tailIsCorrect(body, desiredTail)) {
                desiredTail.forEach(function (node) { body.appendChild(node); });
            }

            if (body.getAttribute('data-h18-v0884-inspector-order') !== 'media-dynamic-conditions') {
                body.setAttribute('data-h18-v0884-inspector-order', 'media-dynamic-conditions');
            }
        } finally {
            applying = false;
        }
    }

    function scheduleApply(delay) {
        window.clearTimeout(timer);
        timer = window.setTimeout(applyOrder, typeof delay === 'number' ? delay : 0);
    }

    function installObserver() {
        const target = document.getElementById('h18-page-inspector-target');
        if (!target || !window.MutationObserver || observer) { return; }
        observer = new MutationObserver(function () {
            if (!applying) { scheduleApply(0); }
        });
        observer.observe(target, { childList: true, subtree: true });
    }

    document.addEventListener('click', function (event) {
        const header = event.target && event.target.closest
            ? event.target.closest('.h18-v0884-collapse-header')
            : null;
        if (!header) { return; }
        event.preventDefault();
        toggleFromHeader(header);
    }, true);

    document.addEventListener('keydown', function (event) {
        const header = event.target && event.target.closest
            ? event.target.closest('.h18-v0884-collapse-header')
            : null;
        if (!header || (event.key !== 'Enter' && event.key !== ' ')) { return; }
        event.preventDefault();
        toggleFromHeader(header);
    }, true);

    const style = document.createElement('style');
    style.id = 'h18-inspector-order-v0884-style';
    style.textContent = [
        '.h18-v0884-collapse-header{cursor:pointer;display:flex;align-items:center;gap:8px;user-select:none}',
        '.h18-v0884-collapse-marker{margin-left:auto;font-size:13px;line-height:1}',
        '.h18-v0884-collapsed{padding-bottom:8px}',
        '#h18-page-inspector-target .h18-dynamic-binding-box,#h18-page-inspector-target .h18-condition-editor{order:9998}',
        '#h18-page-inspector-target .h18-condition-editor{order:9999}'
    ].join('');
    (document.head || document.documentElement).appendChild(style);

    function install() {
        installObserver();
        scheduleApply(0);
    }

    document.documentElement.setAttribute('data-h18-inspector-order', VERSION);
    window.__h18InspectorOrderV0884 = {
        version: VERSION,
        apply: applyOrder,
        collapse: setCollapsed
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
