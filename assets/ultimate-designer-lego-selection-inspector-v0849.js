(function () {
    'use strict';

    if (window.__h18LegoSelectionInspectorV0849) { return; }

    const SELECTED_CLASS = 'is-h18-v0848-selected-element';
    const NESTED_SELECTOR = '.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child]';
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
        return String(row.getAttribute('data-key') || '').trim();
    }

    function selectedDomKey() {
        const inspector = document.querySelector('#h18-page-inspector-target .h18-page-section-key');
        if (inspector && inspector.value) { return String(inspector.value).trim(); }
        const row = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
        return keyFromRow(row);
    }

    function markerIsCurrent(key) {
        const nested = Array.from(document.querySelectorAll(NESTED_SELECTOR));
        const matching = nested.filter(function (node) { return keyFromNested(node) === key; });
        if (matching.length) {
            const wrongSelected = nested.some(function (node) {
                return node.classList.contains(SELECTED_CLASS) && keyFromNested(node) !== key;
            });
            return !wrongSelected && matching.some(function (node) { return node.classList.contains(SELECTED_CLASS); });
        }

        const row = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
        return Boolean(row && keyFromRow(row) === key);
    }

    function applyMarker() {
        const key = selectedDomKey();
        if (!key || markerIsCurrent(key)) { return; }
        const owner = selectionOwner();
        if (owner && typeof owner.refreshSelectedCanvasMarker === 'function') {
            owner.refreshSelectedCanvasMarker();
        }
    }

    function rememberKey() {
        return selectedDomKey();
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

    function loadDiagnostics() {
        if (window.__h18LegoDiagnosticsV0873 || document.querySelector('script[data-h18-lego-diagnostics-loader="1"]')) { return; }
        const scripts = Array.from(document.scripts || []);
        const self = scripts.reverse().find(function (script) { return /ultimate-designer-lego-selection-inspector-v0849\.js/.test(String(script.src || '')); });
        if (!self || !self.src) { return; }
        const url = self.src.replace(/ultimate-designer-lego-selection-inspector-v0849\.js(?:\?.*)?$/, 'ultimate-designer-lego-diagnostics-v0873.js?ver=0.8.73');
        if (!url || url === self.src) { return; }
        const script = document.createElement('script');
        script.src = url;
        script.async = false;
        script.setAttribute('data-h18-lego-diagnostics-loader', '1');
        document.head.appendChild(script);
    }

    const inspector = document.querySelector('#h18-page-inspector-target');
    if (window.MutationObserver && inspector) {
        new MutationObserver(function () {
            queueAdvancedLayout();
        }).observe(inspector, { childList: true, subtree: true });
    }

    window.setTimeout(function () {
        moveAdvancedInspectorBlocks();
        applyMarker();
        loadDiagnostics();
    }, 0);

    document.documentElement.setAttribute('data-h18-lego-selection-inspector', '0.8.73-advanced-only');
    window.__h18LegoSelectionInspectorV0849 = {
        version: '0.8.73',
        selectionOwner: 'v0.8.71-inspector-only',
        rememberKey: rememberKey,
        applyMarker: applyMarker,
        moveAdvancedInspectorBlocks: moveAdvancedInspectorBlocks
    };
}());
