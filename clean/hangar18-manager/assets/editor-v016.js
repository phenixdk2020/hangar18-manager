(function () {
    'use strict';

    const CFG = window.H18CleanEditor || {};
    const ROW_PX = Math.max(2, parseInt(CFG.rowPx || 8, 10) || 8);
    const decorations = Object.create(null);
    let syncQueued = false;

    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function cleanId(value) {
        return String(value || '').toLowerCase().replace(/[^a-z0-9._-]/g, '').slice(0, 100);
    }

    function normalizeColor(value) {
        const color = String(value || '').trim();
        return /^#[0-9a-f]{6}$/i.test(color) ? color.toLowerCase() : '#000000';
    }

    function loadDecorations() {
        const nodes = CFG.initialModel && Array.isArray(CFG.initialModel.nodes) ? CFG.initialModel.nodes : [];
        nodes.forEach(function (node) {
            const id = cleanId(node && node.id);
            if (!id) { return; }
            const props = node && node.props && typeof node.props === 'object' ? node.props : {};
            decorations[id] = {
                borderWidth: clamp(parseInt(props.borderWidth || 0, 10) || 0, 0, 20),
                borderColor: normalizeColor(props.borderColor || '#000000')
            };
        });
    }

    function decoration(id) {
        id = cleanId(id);
        if (!decorations[id]) {
            decorations[id] = { borderWidth: 0, borderColor: '#000000' };
        }
        return decorations[id];
    }

    function selectedId() {
        const selected = document.querySelector('.h18-clean-node.is-selected[data-node-id]');
        return selected ? cleanId(selected.getAttribute('data-node-id') || '') : '';
    }

    function applyBorders() {
        document.querySelectorAll('.h18-clean-node[data-node-id]').forEach(function (card) {
            const id = cleanId(card.getAttribute('data-node-id') || '');
            const item = decoration(id);
            card.style.boxSizing = 'border-box';
            card.style.borderStyle = item.borderWidth > 0 ? 'solid' : 'none';
            card.style.borderWidth = item.borderWidth + 'px';
            card.style.borderColor = item.borderColor;
        });
    }

    function injectBordersIntoHiddenModel() {
        const field = document.getElementById('h18-clean-model-json');
        if (!field || !field.value) { return; }
        try {
            const model = JSON.parse(field.value);
            if (!model || !Array.isArray(model.nodes)) { return; }
            model.nodes.forEach(function (node) {
                const id = cleanId(node && node.id);
                if (!id) { return; }
                const item = decoration(id);
                if (!node.props || typeof node.props !== 'object') { node.props = {}; }
                node.props.borderWidth = item.borderWidth;
                node.props.borderColor = item.borderColor;
            });
            field.value = JSON.stringify(model);
        } catch (ignore) {}
    }

    function diag(type, detail) {
        if (!CFG.postId || !CFG.ajaxUrl || !CFG.diagNonce) { return; }
        const body = new URLSearchParams();
        body.set('action', CFG.diagAction || 'h18_clean_diag_append');
        body.set('nonce', CFG.diagNonce);
        body.set('post_id', String(CFG.postId));
        body.set('event_type', String(type || 'client'));
        body.set('detail_json', JSON.stringify(detail || {}));
        fetch(CFG.ajaxUrl, {
            method: 'POST',
            credentials: 'same-origin',
            keepalive: true,
            headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
            body: body.toString(),
            cache: 'no-store'
        }).catch(function () {});
    }

    function installBorderControls() {
        const host = document.getElementById('h18-clean-inspector');
        const id = selectedId();
        if (!host || !id || host.querySelector('.h18-clean-v016-border-controls')) { return; }

        const item = decoration(id);
        const block = document.createElement('div');
        block.className = 'h18-clean-v016-border-controls';
        block.innerHTML = '<strong>Ramme</strong>' +
            '<div class="h18-clean-field-grid">' +
            '<label>Tykkelse px<input data-v016-field="borderWidth" type="number" min="0" max="20" step="1" value="' + item.borderWidth + '"></label>' +
            '<label>Farve<input data-v016-field="borderColor" type="color" value="' + item.borderColor + '"></label>' +
            '</div><p class="description">0 px = ingen ramme.</p>';

        const deleteButton = host.querySelector('#h18-clean-delete');
        if (deleteButton) { host.insertBefore(block, deleteButton); }
        else { host.appendChild(block); }

        block.querySelectorAll('[data-v016-field]').forEach(function (control) {
            control.addEventListener('change', function () {
                const currentId = selectedId();
                if (!currentId) { return; }
                const current = decoration(currentId);
                const field = String(control.getAttribute('data-v016-field') || '');
                if (field === 'borderWidth') {
                    current.borderWidth = clamp(parseInt(control.value || 0, 10) || 0, 0, 20);
                    control.value = String(current.borderWidth);
                } else if (field === 'borderColor') {
                    current.borderColor = normalizeColor(control.value);
                    control.value = current.borderColor;
                }
                applyBorders();
                injectBordersIntoHiddenModel();
                diag('border_change', {
                    id: currentId,
                    borderWidth: current.borderWidth,
                    borderColor: current.borderColor
                });
            });
        });
    }

    function directInnerSurface(card) {
        for (let i = 0; i < card.children.length; i += 1) {
            const child = card.children[i];
            if (child.classList && child.classList.contains('h18-clean-inner-surface')) { return child; }
        }
        return null;
    }

    function cardDepth(card) {
        let depth = 0;
        let cursor = card.parentElement;
        while (cursor) {
            if (cursor.classList && cursor.classList.contains('h18-clean-node')) { depth += 1; }
            cursor = cursor.parentElement;
        }
        return depth;
    }

    function autoGrowContainers() {
        const cards = Array.from(document.querySelectorAll('.h18-clean-node--section[data-node-id],.h18-clean-node--container[data-node-id]'));
        cards.sort(function (a, b) { return cardDepth(b) - cardDepth(a); });

        cards.forEach(function (card) {
            const geometry = String(card.getAttribute('data-geometry') || '').split(',');
            const selectedRows = Math.max(0, parseInt(geometry[3] || '0', 10) || 0);
            const selectedMin = selectedRows * ROW_PX;
            const inner = directInnerSurface(card);
            if (!inner) {
                card.style.minHeight = selectedMin > 0 ? selectedMin + 'px' : '';
                return;
            }

            const cardRect = card.getBoundingClientRect();
            const innerRect = inner.getBoundingClientRect();
            let required = Math.max(0, Math.ceil(innerRect.top - cardRect.top + inner.scrollHeight));

            Array.from(inner.children).forEach(function (child) {
                if (!child.classList || !child.classList.contains('h18-clean-node')) { return; }
                const rect = child.getBoundingClientRect();
                required = Math.max(required, Math.ceil(rect.bottom - cardRect.top));
            });

            const border = decoration(card.getAttribute('data-node-id') || '').borderWidth * 2;
            required += border;
            const next = Math.max(selectedMin, required);
            card.style.minHeight = next > 0 ? next + 'px' : '';
        });
    }

    function sync() {
        syncQueued = false;
        applyBorders();
        installBorderControls();
        autoGrowContainers();
    }

    function scheduleSync() {
        if (syncQueued) { return; }
        syncQueued = true;
        window.requestAnimationFrame(function () {
            window.requestAnimationFrame(sync);
        });
    }

    function install() {
        loadDecorations();

        const form = document.getElementById('h18-clean-save-form');
        if (form) {
            form.addEventListener('submit', function () {
                injectBordersIntoHiddenModel();
            }, true);
        }

        const workspace = document.querySelector('.h18-clean-workspace');
        if (workspace && window.MutationObserver) {
            const observer = new MutationObserver(scheduleSync);
            observer.observe(workspace, { childList: true, subtree: true });
        }

        ['click', 'change', 'drop', 'dragend', 'pointerup'].forEach(function (name) {
            document.addEventListener(name, scheduleSync, true);
        });

        window.addEventListener('resize', scheduleSync);
        scheduleSync();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
