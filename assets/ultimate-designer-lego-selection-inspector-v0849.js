(function () {
    'use strict';

    if (window.__h18LegoSelectionInspectorV0849) { return; }

    const NESTED_SELECTOR = '.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child]';
    const EXCLUDE_SELECTOR = [
        '.h18-v0841-resize-handle',
        '.h18-v0841-resize-rail',
        '.h18-v0811-side-zone',
        '.h18-v0814-auto-drop-zone',
        '.h18-v0814-auto-kasse-drop',
        '.h18-ud-box-drop-zone'
    ].join(',');

    let activeKey = '';
    let markerFrame = 0;
    let advancedFrame = 0;

    function selectionOwner() {
        return window.__h18LegoInspectorOnlyV0847 || null;
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
        return dataKey;
    }

    function selectedDomKey() {
        const inspector = document.querySelector('#h18-page-inspector-target .h18-page-section-key');
        if (inspector && inspector.value) { return String(inspector.value).trim(); }
        const row = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
        return keyFromRow(row);
    }

    function rememberKey(key) {
        const value = String(key || '').trim();
        if (value) {
            activeKey = value;
            const owner = selectionOwner();
            if (owner && typeof owner.rememberSelectedCanvasKey === 'function') {
                owner.rememberSelectedCanvasKey(value);
            }
        }
        return activeKey;
    }

    function inferKey(node) {
        if (!node || !node.closest) { return ''; }
        const nested = node.closest(NESTED_SELECTOR);
        if (nested) { return keyFromNested(nested); }
        return keyFromRow(node.closest('.h18-page-section-row'));
    }

    function applyMarker() {
        markerFrame = 0;
        const owner = selectionOwner();
        if (owner && typeof owner.refreshSelectedCanvasMarker === 'function') {
            owner.refreshSelectedCanvasMarker();
        }
    }

    function queueMarker() {
        if (markerFrame) { return; }
        markerFrame = window.requestAnimationFrame(applyMarker);
    }

    // Old v0.8.49 called applyMarker again after 40/180/450/900 ms.
    // That repeatedly removed/re-added the selection class and caused the
    // visible multi-flash. One animation-frame update is enough now because
    // v0.8.47 owns a persistent key through the Inspector handoff.
    function settleMarker() {
        queueMarker();
    }

    function advancedLayoutIsStable(root, heading, blocks) {
        if (!heading || !root || !blocks.length) { return false; }
        if (heading.nextElementSibling !== blocks[0]) { return false; }
        for (let index = 1; index < blocks.length; index += 1) {
            if (blocks[index - 1].nextElementSibling !== blocks[index]) { return false; }
        }
        return blocks[blocks.length - 1] === root.lastElementChild;
    }

    function moveAdvancedInspectorBlocks() {
        advancedFrame = 0;
        const target = document.querySelector('#h18-page-inspector-target');
        if (!target) { return; }

        const dynamic = target.querySelector('.h18-dynamic-binding-box');
        const conditions = target.querySelector('.h18-condition-editor');
        const blocks = [dynamic, conditions].filter(Boolean);
        if (!blocks.length) { return; }

        const body = target.querySelector('.h18-page-section-body') || target;
        const commonParent = dynamic && conditions && dynamic.parentElement === conditions.parentElement
            ? dynamic.parentElement
            : null;
        const root = commonParent || body;
        if (!root) { return; }

        const movable = blocks.filter(function (block) { return block.parentElement === root; });
        if (!movable.length) { return; }

        let heading = root.querySelector(':scope > .h18-v0849-advanced-heading');
        movable.forEach(function (block) { block.classList.add('h18-v0849-advanced-block'); });
        if (advancedLayoutIsStable(root, heading, movable)) { return; }

        if (!heading) {
            heading = document.createElement('div');
            heading.className = 'h18-v0849-advanced-heading';
            heading.innerHTML = '<strong>Avanceret</strong><span>Dynamiske data og regler for synlighed</span>';
        } else if (heading.parentElement === root) {
            root.removeChild(heading);
        }

        movable.forEach(function (block) { root.appendChild(block); });
        root.insertBefore(heading, movable[0]);
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
        // Keep only one queued refresh. Do not overwrite a click-cached key with
        // a transient Inspector key while the settings body is moving.
        new MutationObserver(function () {
            if (!activeKey) {
                const key = selectedDomKey();
                if (key) { rememberKey(key); }
            }
            queueMarker();
        }).observe(document.body, { childList: true, subtree: true });

        const inspector = document.querySelector('#h18-page-inspector-target');
        if (inspector) {
            new MutationObserver(function () {
                queueAdvancedLayout();
            }).observe(inspector, { childList: true, subtree: true });
        }
    }

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

    document.documentElement.setAttribute('data-h18-lego-selection-inspector', '0.8.61');
    window.__h18LegoSelectionInspectorV0849 = {
        version: '0.8.61',
        rememberKey: rememberKey,
        applyMarker: applyMarker,
        moveAdvancedInspectorBlocks: moveAdvancedInspectorBlocks
    };
}());
