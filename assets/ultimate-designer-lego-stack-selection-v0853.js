(function () {
    'use strict';

    if (window.__h18LegoStackSelectionV0853) { return; }

    const VERSION = '0.8.53';
    const STACK_FIELD_CLASS = 'h18-lego-stack-state-v0851-json';
    const NESTED_SELECTOR = [
        '.h18-v0811-auto-box[data-h18-v0811-row]',
        '.h18-v0811-auto-box[data-h18-v0811-box]',
        '.h18-v0811-child-card[data-h18-v0811-child]'
    ].join(',');
    const EXCLUDE_SELECTOR = [
        '.h18-v0841-resize-handle',
        '.h18-v0841-resize-rail',
        '.h18-v0851-stack-resize-handle',
        '.h18-v0838-drop-zone',
        '.h18-v0811-side-zone',
        '.h18-v0814-auto-drop-zone',
        '.h18-v0814-auto-kasse-drop',
        '.h18-ud-box-drop-zone'
    ].join(',');

    let activeKey = '';
    let lastExplicitSelectionAt = 0;
    let selectionFrame = 0;
    let observer = null;

    function jq() { return window.jQuery || null; }
    function $sections() { const $ = jq(); return $ ? $('#h18-page-sections-sortable') : null; }
    function $inspector() { const $ = jq(); return $ ? $('#h18-page-inspector-target') : null; }

    function controls($row, selector) {
        const $ = jq();
        if (!$ || !$row || !$row.length) { return $ ? $() : null; }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) { $result = $result.add($inspector().find(selector)); }
        return $result;
    }

    function activeRows() {
        const $ = jq();
        const $s = $sections();
        return $ && $s && $s.length ? $s.children('.h18-page-section-row:not(.h18-page-section-removed)') : ($ ? $() : null);
    }

    function rowKey($row) {
        if (!$row || !$row.length) { return ''; }
        const $field = controls($row, '.h18-page-section-key').first();
        return String(($field && $field.length ? $field.val() : '') || $row.attr('data-key') || '').trim();
    }

    function rowType($row) {
        if (!$row || !$row.length) { return ''; }
        return String($row.attr('data-section-type') || controls($row, '.h18-page-section-type').first().val() || '').trim();
    }

    function parentKey($row) {
        if (!$row || !$row.length) { return ''; }
        return String(controls($row, '.h18-layout-parent-key').first().val() || '').trim();
    }

    function rowByKey(key) {
        const $ = jq();
        const wanted = String(key || '').trim();
        if (!$ || !wanted) { return $ ? $() : null; }
        return activeRows().filter(function () { return rowKey($(this)) === wanted; }).first();
    }

    function nestedKey(node) {
        if (!node) { return ''; }
        return String(
            node.getAttribute('data-h18-v0811-row') ||
            node.getAttribute('data-h18-v0811-box') ||
            node.getAttribute('data-h18-v0811-child') ||
            ''
        ).trim();
    }

    function inspectorKey() {
        const input = document.querySelector('#h18-page-inspector-target .h18-page-section-key');
        return input && input.value ? String(input.value).trim() : '';
    }

    function selectedRowKey() {
        const $ = jq();
        const $row = $ ? $('#h18-page-sections-sortable > .h18-page-section-row.is-selected').first() : null;
        return $row && $row.length ? rowKey($row) : '';
    }

    function inferKey(node) {
        if (!node || !node.closest) { return ''; }
        const nested = node.closest(NESTED_SELECTOR);
        if (nested) { return nestedKey(nested); }
        const row = node.closest('.h18-page-section-row');
        return row ? rowKey(jq()(row)) : '';
    }

    function visualTarget(proxy) {
        if (!proxy) { return null; }
        return proxy.querySelector(':scope > .h18-v0811-auto-box-preview') ||
            proxy.querySelector(':scope > .h18-v0811-child-preview') ||
            proxy.querySelector('.h18-v0811-auto-box-preview') ||
            proxy.querySelector('.h18-v0811-child-preview') ||
            proxy;
    }

    function rememberExplicitKey(key) {
        const value = String(key || '').trim();
        if (!value) { return activeKey; }
        activeKey = value;
        lastExplicitSelectionAt = Date.now();
        return activeKey;
    }

    function resolveSelectionKey() {
        const inspector = inspectorKey();
        const selected = selectedRowKey();
        const explicitIsFresh = activeKey && (Date.now() - lastExplicitSelectionAt) < 1400;

        if (explicitIsFresh) { return activeKey; }
        if (inspector) { activeKey = inspector; return activeKey; }
        if (selected) { activeKey = selected; return activeKey; }
        return activeKey;
    }

    function applySelectionOutline() {
        selectionFrame = 0;
        document.querySelectorAll('.h18-v0853-selection-target').forEach(function (node) {
            node.classList.remove('h18-v0853-selection-target');
        });

        const key = resolveSelectionKey();
        if (!key) { return false; }

        let matched = false;
        document.querySelectorAll(NESTED_SELECTOR).forEach(function (proxy) {
            if (nestedKey(proxy) !== key) { return; }
            const target = visualTarget(proxy);
            if (!target) { return; }
            target.classList.add('h18-v0853-selection-target');
            matched = true;
        });

        if (!matched) {
            const $row = rowByKey(key);
            if ($row && $row.length) {
                const preview = $row.children('.h18-canvas-preview').first().get(0);
                if (preview) {
                    preview.classList.add('h18-v0853-selection-target');
                    matched = true;
                }
            }
        }

        return matched;
    }

    function queueSelectionOutline() {
        if (selectionFrame) { return; }
        selectionFrame = window.requestAnimationFrame(applySelectionOutline);
    }

    function settleSelectionOutline() {
        queueSelectionOutline();
        [20, 70, 160, 350, 700, 1200].forEach(function (delay) {
            window.setTimeout(applySelectionOutline, delay);
        });
    }

    function stackState($row) {
        if (!$row || !$row.length) { return {}; }
        const $field = controls($row, '.' + STACK_FIELD_CLASS).first();
        if (!$field || !$field.length) { return {}; }
        try { return JSON.parse(String($field.val() || '{}')); }
        catch (error) { return {}; }
    }

    function stackEstablished($child, $target, position) {
        if (!$child || !$child.length || !$target || !$target.length) { return false; }
        if (position === 'over') {
            return String(stackState($target).StackRootKey || '') === rowKey($child);
        }
        return Boolean(String(stackState($child).StackRootKey || '').trim());
    }

    function ensureCanonicalParent($child, parent) {
        if (!$child || !$child.length || !parent) { return false; }
        const $hidden = controls($child, '.h18-layout-parent-key').first();
        const $select = controls($child, '.h18-layout-parent-select').first();
        if (!$hidden || !$hidden.length) { return false; }

        if (String($hidden.val() || '') !== parent) { $hidden.val(parent); }
        $child.attr('data-h18-nested-in-box', parent);

        if ($select && $select.length) {
            const hasOption = $select.find('option').filter(function () {
                return String(jq()(this).val() || '') === parent;
            }).length > 0;
            if (hasOption && String($select.val() || '') !== parent) { $select.val(parent); }
        }

        return String($hidden.val() || '') === parent;
    }

    function settleStack(childKey, targetKey, position) {
        const api = window.__h18LegoFixesV0851;
        if (!api || (position !== 'under' && position !== 'over')) { return; }

        let done = false;
        [0, 25, 70, 150, 300, 600, 1100].forEach(function (delay) {
            window.setTimeout(function () {
                if (done) { return; }

                const $child = rowByKey(childKey);
                const $target = rowByKey(targetKey);
                if (!$child || !$child.length || !$target || !$target.length) { return; }

                const parent = parentKey($target);
                const $parent = rowByKey(parent);
                if (!parent || !$parent || !$parent.length || rowType($parent) !== 'grid') { return; }

                ensureCanonicalParent($child, parent);
                if (stackEstablished($child, $target, position)) {
                    done = true;
                    if (typeof api.refresh === 'function') { api.refresh(); }
                    return;
                }

                const method = position === 'over' ? api.stackOver : api.stackUnder;
                if (typeof method !== 'function') { return; }
                const stacked = method.call(api, childKey, targetKey) === true;
                if (stacked && stackEstablished($child, $target, position)) {
                    done = true;
                    if (typeof api.refresh === 'function') { api.refresh(); }
                    const nesting = window.__h18NestingToolsV0840;
                    if (nesting && typeof nesting.refresh === 'function') { nesting.refresh(); }
                }
            }, delay);
        });
    }

    function wrapAdoptUnder() {
        const api = window.__h18LegoFixesV0851;
        if (!api || typeof api.adoptUnder !== 'function' || api.__h18V0853AdoptWrapped) { return false; }

        const nativeAdoptUnder = api.adoptUnder.bind(api);
        api.adoptUnder = function (childKey, targetKey, position) {
            const result = nativeAdoptUnder(childKey, targetKey, position);
            if (result === true && (position === 'under' || position === 'over')) {
                settleStack(String(childKey || ''), String(targetKey || ''), position);
            }
            return result;
        };
        api.__h18V0853AdoptWrapped = true;
        return true;
    }

    function installObservers() {
        if (!window.MutationObserver || observer) { return; }
        observer = new MutationObserver(function (mutations) {
            let selectionRelevant = false;
            for (const mutation of mutations) {
                if (mutation.type === 'childList') {
                    selectionRelevant = true;
                    break;
                }
            }
            if (!selectionRelevant) { return; }
            const key = inspectorKey();
            if (key && (Date.now() - lastExplicitSelectionAt) >= 1400) { activeKey = key; }
            queueSelectionOutline();
        });
        observer.observe(document.body, { childList: true, subtree: true });
    }

    function install() {
        wrapAdoptUnder();
        installObservers();

        document.addEventListener('click', function (event) {
            const target = event.target && event.target.closest ? event.target : null;
            if (!target || !target.closest('.h18-builder-canvas')) { return; }
            if (target.closest(EXCLUDE_SELECTOR)) { return; }
            const key = inferKey(target);
            if (!key) { return; }
            rememberExplicitKey(key);
            settleSelectionOutline();
        }, true);

        // The v0.8.51 API is enqueued before this file, but keep a bounded
        // retry for cached/admin pages where script execution can be deferred.
        [0, 50, 150, 400, 900].forEach(function (delay) {
            window.setTimeout(wrapAdoptUnder, delay);
        });

        const initial = inspectorKey() || selectedRowKey();
        if (initial) { activeKey = initial; }
        settleSelectionOutline();
        document.documentElement.setAttribute('data-h18-lego-stack-selection-hotfix', VERSION);
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }

    window.__h18LegoStackSelectionV0853 = {
        version: VERSION,
        applySelectionOutline: applySelectionOutline,
        settleSelectionOutline: settleSelectionOutline,
        settleStack: settleStack,
        wrapAdoptUnder: wrapAdoptUnder
    };
}());
