(function () {
    'use strict';

    if (window.__h18LegoSelectionInspectorV0849) { return; }

    const SELECTED_CLASS = 'is-h18-v0848-selected-element';
    const NESTED_SELECTOR = '.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child]';
    const EXCLUDE_SELECTOR = [
        '.h18-v0841-resize-handle',
        '.h18-v0841-resize-rail',
        '.h18-v0811-side-zone',
        '.h18-v0814-auto-drop-zone',
        '.h18-v0814-auto-kasse-drop',
        '.h18-ud-box-drop-zone'
    ].join(',');
    const ADVANCED_LABELS = ['dynamic data binding', 'conditions / synlighed'];

    let activeKey = '';
    let markerFrame = 0;
    let advancedFrame = 0;

    function normalizedText(value) {
        return String(value || '').replace(/\s+/g, ' ').trim().toLowerCase();
    }

    function keyFromNested(node) {
        if (!node) { return ''; }
        return String(node.getAttribute('data-h18-v0811-row') || node.getAttribute('data-h18-v0811-child') || '').trim();
    }

    function keyFromRow(row) {
        if (!row) { return ''; }
        const direct = row.querySelector('.h18-page-section-key');
        if (direct && direct.value) { return String(direct.value).trim(); }
        const dataKey = String(row.getAttribute('data-key') || '').trim();
        if (dataKey) { return dataKey; }
        if (row.classList.contains('is-selected')) {
            const inspector = document.querySelector('#h18-page-inspector-target .h18-page-section-key');
            if (inspector && inspector.value) { return String(inspector.value).trim(); }
        }
        return '';
    }

    function selectedDomKey() {
        const row = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
        const rowKey = keyFromRow(row);
        if (rowKey) { return rowKey; }
        const inspector = document.querySelector('#h18-page-inspector-target .h18-page-section-key');
        return inspector && inspector.value ? String(inspector.value).trim() : '';
    }

    function rememberKey(key) {
        const value = String(key || '').trim();
        if (value) { activeKey = value; }
        return activeKey;
    }

    function inferKey(node) {
        if (!node || !node.closest) { return ''; }
        const nested = node.closest(NESTED_SELECTOR);
        if (nested) { return keyFromNested(nested); }
        const row = node.closest('.h18-page-section-row');
        return keyFromRow(row);
    }

    function applyMarker() {
        markerFrame = 0;
        document.querySelectorAll('.' + SELECTED_CLASS).forEach(function (node) {
            node.classList.remove(SELECTED_CLASS);
        });

        const domKey = selectedDomKey();
        if (domKey) { activeKey = domKey; }
        const key = activeKey;
        if (!key) { return; }

        document.querySelectorAll(NESTED_SELECTOR).forEach(function (node) {
            if (keyFromNested(node) === key) {
                node.classList.add(SELECTED_CLASS);
            }
        });
    }

    function queueMarker() {
        if (markerFrame) { return; }
        markerFrame = window.requestAnimationFrame(applyMarker);
    }

    function settleMarker() {
        queueMarker();
        [40, 180, 450, 900].forEach(function (delay) {
            window.setTimeout(applyMarker, delay);
        });
    }

    function directChildUnder(root, node) {
        if (!root || !node || !root.contains(node)) { return null; }
        let cursor = node;
        while (cursor && cursor.parentElement && cursor.parentElement !== root) {
            cursor = cursor.parentElement;
        }
        return cursor && cursor.parentElement === root ? cursor : null;
    }

    function findAdvancedBlocks(root) {
        const found = [];
        root.querySelectorAll('legend,h2,h3,h4,h5,strong,label,summary').forEach(function (heading) {
            const text = normalizedText(heading.textContent);
            if (!ADVANCED_LABELS.some(function (label) { return text === label || text.indexOf(label) === 0; })) { return; }
            const block = directChildUnder(root, heading);
            if (block && found.indexOf(block) === -1) { found.push(block); }
        });
        return found;
    }

    function moveAdvancedInspectorBlocks() {
        advancedFrame = 0;
        const target = document.querySelector('#h18-page-inspector-target');
        if (!target) { return; }
        const root = target.querySelector('.h18-page-section-body') || target;
        const blocks = findAdvancedBlocks(root);
        if (!blocks.length) { return; }

        let heading = root.querySelector(':scope > .h18-v0849-advanced-heading');
        if (!heading) {
            heading = document.createElement('div');
            heading.className = 'h18-v0849-advanced-heading';
            heading.innerHTML = '<strong>Avanceret</strong><span>Dynamiske data og regler for synlighed</span>';
        }

        blocks.forEach(function (block) {
            block.classList.add('h18-v0849-advanced-block');
            root.appendChild(block);
        });
        root.insertBefore(heading, blocks[0]);
    }

    function queueAdvancedLayout() {
        if (advancedFrame) { return; }
        advancedFrame = window.requestAnimationFrame(moveAdvancedInspectorBlocks);
    }

    document.addEventListener('click', function (event) {
        const target = event.target && event.target.closest ? event.target : null;
        if (!target || !target.closest('.h18-builder-canvas')) { return; }
        if (target.closest(EXCLUDE_SELECTOR)) { return; }
        const key = inferKey(target);
        if (!key) { return; }
        rememberKey(key);
        settleMarker();
        queueAdvancedLayout();
    }, true);

    document.addEventListener('click', function (event) {
        const trigger = event.target && event.target.closest
            ? event.target.closest('.h18-v0811-edit-child,.h18-page-section-edit,.h18-page-section-header')
            : null;
        if (!trigger) { return; }
        const key = inferKey(trigger);
        if (key) { rememberKey(key); }
        settleMarker();
        queueAdvancedLayout();
        window.setTimeout(moveAdvancedInspectorBlocks, 120);
    }, true);

    if (window.MutationObserver) {
        const canvas = document.querySelector('#h18-page-sections-sortable');
        if (canvas) {
            new MutationObserver(function () { queueMarker(); }).observe(canvas, { childList: true, subtree: true });
        }
        const inspector = document.querySelector('#h18-page-inspector-target');
        if (inspector) {
            new MutationObserver(function () {
                const key = selectedDomKey();
                if (key) { rememberKey(key); }
                queueMarker();
                queueAdvancedLayout();
            }).observe(inspector, { childList: true, subtree: true });
        }
    }

    // Nesting/runtime reconciliation can replace the visual tile after selection.
    // Keep the selected key outside that transient DOM and reapply the outline
    // after every explicit nesting refresh when the public refresh hook exists.
    const nesting = window.__h18NestingToolsV0840;
    if (nesting && typeof nesting.refresh === 'function' && !nesting.__h18V0849Wrapped) {
        const nativeRefresh = nesting.refresh.bind(nesting);
        nesting.refresh = function () {
            const result = nativeRefresh.apply(null, arguments);
            settleMarker();
            return result;
        };
        nesting.__h18V0849Wrapped = true;
    }

    window.setTimeout(function () {
        const key = selectedDomKey();
        if (key) { rememberKey(key); }
        applyMarker();
        moveAdvancedInspectorBlocks();
    }, 0);

    document.documentElement.setAttribute('data-h18-lego-selection-inspector', '0.8.49');
    window.__h18LegoSelectionInspectorV0849 = {
        version: '0.8.49',
        rememberKey: rememberKey,
        applyMarker: applyMarker,
        moveAdvancedInspectorBlocks: moveAdvancedInspectorBlocks
    };
}());
