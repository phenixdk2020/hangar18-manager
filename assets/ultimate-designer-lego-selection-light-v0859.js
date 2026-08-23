(function () {
    'use strict';

    if (window.__h18LegoSelectionLightV0859) { return; }

    const TARGET_CLASS = 'h18-v0859-selected-target';
    let activeKey = '';
    let frame = 0;

    function cssEscape(value) {
        const raw = String(value || '');
        if (window.CSS && typeof window.CSS.escape === 'function') { return window.CSS.escape(raw); }
        return raw.replace(/(["\\])/g, '\\$1');
    }

    function keyFromRow(row) {
        if (!row) { return ''; }
        const keyField = row.querySelector('.h18-page-section-key');
        return String((keyField && keyField.value) || row.getAttribute('data-key') || '').trim();
    }

    function keyFromNode(node) {
        if (!node || !node.closest) { return ''; }
        const nested = node.closest('.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child]');
        if (nested) {
            return String(nested.getAttribute('data-h18-v0811-row') || nested.getAttribute('data-h18-v0811-child') || '').trim();
        }
        return keyFromRow(node.closest('.h18-page-section-row'));
    }

    function inspectorKey() {
        const field = document.querySelector('#h18-page-inspector-target .h18-page-section-key');
        return field && field.value ? String(field.value).trim() : '';
    }

    function visualTargetForKey(key) {
        const wanted = String(key || '').trim();
        if (!wanted) { return null; }
        const escaped = cssEscape(wanted);

        const auto = document.querySelector('.h18-builder-canvas .h18-v0811-auto-box[data-h18-v0811-row="' + escaped + '"]');
        if (auto) {
            return auto.querySelector('.h18-v0851-stack-root > .h18-v0811-auto-box-preview') ||
                auto.querySelector(':scope > .h18-v0811-auto-box-preview') || auto;
        }

        const child = document.querySelector('.h18-builder-canvas .h18-v0811-child-card[data-h18-v0811-child="' + escaped + '"]');
        if (child) {
            return child.querySelector(':scope > .h18-v0811-child-preview') || child;
        }

        const rows = document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row');
        for (let i = 0; i < rows.length; i += 1) {
            if (keyFromRow(rows[i]) === wanted) {
                return rows[i].querySelector(':scope > .h18-canvas-preview') || rows[i];
            }
        }
        return null;
    }

    function applySelection() {
        frame = 0;
        document.querySelectorAll('.' + TARGET_CLASS).forEach(function (node) {
            node.classList.remove(TARGET_CLASS);
        });

        const currentInspectorKey = inspectorKey();
        if (currentInspectorKey) { activeKey = currentInspectorKey; }
        if (!activeKey) { return; }

        const target = visualTargetForKey(activeKey);
        if (target) { target.classList.add(TARGET_CLASS); }
    }

    function queueSelection() {
        if (frame) { return; }
        frame = window.requestAnimationFrame(applySelection);
    }

    document.addEventListener('click', function (event) {
        const target = event.target && event.target.closest ? event.target : null;
        if (!target || !target.closest('.h18-builder-canvas')) { return; }
        if (target.closest('.h18-v0841-resize-handle,.h18-v0841-resize-rail,.h18-v0851-stack-resize-handle,.h18-v0811-side-zone,.h18-v0838-drop-zone')) { return; }
        const key = keyFromNode(target);
        if (key) { activeKey = key; }
        queueSelection();
        window.setTimeout(queueSelection, 0);
    }, true);

    const inspector = document.querySelector('#h18-page-inspector-target');
    if (inspector && window.MutationObserver) {
        new MutationObserver(function () {
            const key = inspectorKey();
            if (key) { activeKey = key; }
            queueSelection();
        }).observe(inspector, { childList: true, subtree: true });
    }

    const canvas = document.querySelector('.h18-builder-canvas');
    if (canvas && window.MutationObserver) {
        new MutationObserver(function () {
            queueSelection();
        }).observe(canvas, { childList: true, subtree: true });
    }

    window.setTimeout(function () {
        activeKey = inspectorKey() || activeKey;
        applySelection();
    }, 0);

    window.__h18LegoSelectionLightV0859 = {
        version: '0.8.59',
        apply: applySelection
    };
}());
