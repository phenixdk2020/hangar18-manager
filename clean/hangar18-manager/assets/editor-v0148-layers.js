(function () {
    'use strict';

    const TYPE_NAMES = {
        section: 'Sektion',
        container: 'Kasse',
        text: 'Tekst',
        image: 'Billede',
        button: 'Knap',
        menu: 'Menu'
    };
    const collapsed = new Set();
    let scheduled = false;

    function qsa(root, selector) {
        return Array.prototype.slice.call(root.querySelectorAll(selector));
    }

    function directParentCard(card, canvas) {
        let current = card.parentElement;
        while (current && current !== canvas) {
            if (current.classList && current.classList.contains('h18-clean-node') && current.hasAttribute('data-node-id')) {
                return current;
            }
            current = current.parentElement;
        }
        return null;
    }

    function nodeType(card) {
        const match = Array.from(card.classList).find(function (name) { return name.indexOf('h18-clean-node--') === 0; });
        return match ? match.replace('h18-clean-node--', '') : 'element';
    }

    function previewLabel(card, type) {
        let text = '';
        if (type === 'button') {
            const el = card.querySelector('.h18-clean-button-preview');
            text = el ? el.textContent : '';
        } else if (type === 'text') {
            const el = card.querySelector('.h18-clean-text-body,.h18-clean-text-preview,.h18-clean-node-preview--text');
            text = el ? el.textContent : '';
        } else if (type === 'menu') {
            const el = card.querySelector('.h18-clean-menu-preview,.h18-clean-node-preview--menu');
            text = el ? el.textContent : '';
        } else if (type === 'image') {
            const img = card.querySelector('img');
            text = img ? (img.getAttribute('alt') || '') : '';
        }
        text = String(text || '').replace(/\s+/g, ' ').trim();
        if (text.length > 34) { text = text.slice(0, 31) + '…'; }
        return text;
    }

    function layerLabel(card) {
        const type = nodeType(card);
        const id = card.getAttribute('data-node-id') || '';
        const extra = previewLabel(card, type);
        return (TYPE_NAMES[type] || type) + (extra ? ' · ' + extra : '') + ' · ' + id.slice(-8);
    }

    function selectCard(canvas, id) {
        const card = canvas.querySelector('.h18-clean-node[data-node-id="' + CSS.escape(id) + '"]');
        if (!card) { return; }
        card.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
        try { card.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' }); } catch (ignore) {}
    }

    function buildTree(host, canvas) {
        if (!host || !canvas) { return; }
        const cards = qsa(canvas, '.h18-clean-node[data-node-id]');
        const children = new Map();
        cards.forEach(function (card) {
            const parent = directParentCard(card, canvas);
            const parentId = parent ? (parent.getAttribute('data-node-id') || '') : '';
            if (!children.has(parentId)) { children.set(parentId, []); }
            children.get(parentId).push(card);
        });

        host.innerHTML = '';
        if (!cards.length) {
            host.innerHTML = '<p class="description">Ingen elementer endnu.</p>';
            return;
        }

        function appendLevel(parentId, parentEl, depth) {
            const list = children.get(parentId) || [];
            list.forEach(function (card) {
                const id = card.getAttribute('data-node-id') || '';
                const hasChildren = (children.get(id) || []).length > 0;
                const item = document.createElement('div');
                item.className = 'h18-vd-layer-item' + (card.classList.contains('is-selected') ? ' is-selected' : '');
                item.style.setProperty('--h18-layer-depth', String(depth));

                const disclosure = document.createElement('button');
                disclosure.type = 'button';
                disclosure.className = 'h18-vd-layer-disclosure';
                disclosure.disabled = !hasChildren;
                disclosure.setAttribute('aria-label', hasChildren ? 'Fold lag ind eller ud' : 'Intet underlag');
                disclosure.textContent = hasChildren ? (collapsed.has(id) ? '▸' : '▾') : '·';
                disclosure.addEventListener('click', function (event) {
                    event.stopPropagation();
                    if (!hasChildren) { return; }
                    if (collapsed.has(id)) { collapsed.delete(id); } else { collapsed.add(id); }
                    buildTree(host, canvas);
                });

                const pick = document.createElement('button');
                pick.type = 'button';
                pick.className = 'h18-vd-layer-pick';
                pick.textContent = layerLabel(card);
                pick.title = 'Vælg element på canvas';
                pick.addEventListener('click', function () {
                    selectCard(canvas, id);
                    window.setTimeout(function () { buildTree(host, canvas); }, 0);
                });

                item.appendChild(disclosure);
                item.appendChild(pick);
                parentEl.appendChild(item);

                if (hasChildren && !collapsed.has(id)) {
                    appendLevel(id, parentEl, depth + 1);
                }
            });
        }

        appendLevel('', host, 0);
    }

    function activate(palette, name) {
        qsa(palette, '[data-h18-left-tab]').forEach(function (button) {
            const active = button.getAttribute('data-h18-left-tab') === name;
            button.classList.toggle('is-active', active);
            button.setAttribute('aria-selected', active ? 'true' : 'false');
        });
        qsa(palette, '[data-h18-left-panel]').forEach(function (panel) {
            panel.hidden = panel.getAttribute('data-h18-left-panel') !== name;
        });
        if (name === 'layers') {
            const canvas = document.getElementById('h18-clean-canvas');
            buildTree(palette.querySelector('.h18-vd-layers-tree'), canvas);
        }
    }

    function installPalette(palette) {
        if (!palette || palette.dataset.h18LayersInstalled === '1') { return; }
        palette.dataset.h18LayersInstalled = '1';

        const existing = Array.prototype.slice.call(palette.childNodes);
        const tabs = document.createElement('div');
        tabs.className = 'h18-vd-left-tabs';
        tabs.setAttribute('role', 'tablist');
        tabs.innerHTML = '<button type="button" role="tab" class="is-active" data-h18-left-tab="elements" aria-selected="true">Elementer</button>'
            + '<button type="button" role="tab" data-h18-left-tab="layers" aria-selected="false">Lag</button>';

        const elements = document.createElement('div');
        elements.className = 'h18-vd-left-panel';
        elements.setAttribute('data-h18-left-panel', 'elements');
        existing.forEach(function (node) { elements.appendChild(node); });

        const layers = document.createElement('div');
        layers.className = 'h18-vd-left-panel h18-vd-left-panel--layers';
        layers.setAttribute('data-h18-left-panel', 'layers');
        layers.hidden = true;
        layers.innerHTML = '<p class="description">Vælg et element i hierarkiet, også når det er dækket af et andet element.</p><div class="h18-vd-layers-tree"></div>';

        palette.appendChild(tabs);
        palette.appendChild(elements);
        palette.appendChild(layers);

        tabs.addEventListener('click', function (event) {
            const button = event.target.closest('[data-h18-left-tab]');
            if (!button) { return; }
            activate(palette, button.getAttribute('data-h18-left-tab') || 'elements');
        });

        const canvas = document.getElementById('h18-clean-canvas');
        if (canvas && window.MutationObserver) {
            const observer = new MutationObserver(function () {
                if (scheduled) { return; }
                scheduled = true;
                window.requestAnimationFrame(function () {
                    scheduled = false;
                    const layerPanel = palette.querySelector('[data-h18-left-panel="layers"]');
                    if (layerPanel && !layerPanel.hidden) { buildTree(palette.querySelector('.h18-vd-layers-tree'), canvas); }
                });
            });
            observer.observe(canvas, { subtree: true, childList: true, attributes: true, attributeFilter: ['class'] });
        }
    }

    function install() {
        qsa(document, '.h18-clean-palette').forEach(installPalette);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
})();
