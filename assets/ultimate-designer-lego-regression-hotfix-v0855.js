(function () {
    'use strict';

    if (window.__h18LegoRegressionHotfixV0855) { return; }

    const VERSION = '0.8.55';
    const LEGACY_AUTO_DROP_SELECTOR = [
        '.h18-builder-canvas .h18-v0814-auto-drop-zone',
        '.h18-builder-canvas .h18-v0814-auto-kasse-drop',
        '.h18-builder-canvas .h18-ud-auto-box-empty-drop'
    ].join(',');

    function activeRows() {
        return Array.from(document.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)'));
    }

    function rowKey(row) {
        if (!row) { return ''; }
        const field = row.querySelector('.h18-page-section-key');
        return field ? String(field.value || '') : '';
    }

    function rowByKey(key) {
        const wanted = String(key || '');
        if (!wanted) { return null; }
        return activeRows().find(function (row) { return rowKey(row) === wanted; }) || null;
    }

    function parentKey(row) {
        if (!row) { return ''; }
        const field = row.querySelector('.h18-layout-parent-key');
        return field ? String(field.value || '') : '';
    }

    function stackState(row) {
        if (!row) { return {}; }
        const field = row.querySelector('.h18-lego-stack-state-v0851-json');
        if (!field) { return {}; }
        try {
            const value = JSON.parse(String(field.value || '{}'));
            return value && typeof value === 'object' ? value : {};
        } catch (error) {
            return {};
        }
    }

    function removeLegacyNode(node) {
        if (!node || node.nodeType !== 1) { return; }
        if (node.matches && node.matches(LEGACY_AUTO_DROP_SELECTOR)) {
            node.remove();
            return;
        }
        if (node.querySelectorAll) {
            node.querySelectorAll(LEGACY_AUTO_DROP_SELECTOR).forEach(function (legacy) {
                legacy.remove();
            });
        }
    }

    function purgeLegacyAutoDropPrompts(root) {
        const scope = root && root.querySelectorAll ? root : document;
        scope.querySelectorAll(LEGACY_AUTO_DROP_SELECTOR).forEach(function (node) {
            node.remove();
        });
    }

    function installLegacyPromptGuard() {
        purgeLegacyAutoDropPrompts(document);
        if (!window.MutationObserver || !document.body) { return; }
        const observer = new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                Array.from(mutation.addedNodes || []).forEach(removeLegacyNode);
            });
        });
        observer.observe(document.body, { childList: true, subtree: true });
        window.__h18LegoRegressionHotfixV0855.legacyPromptObserver = observer;
    }

    function installAdoptGuard() {
        const api = window.__h18LegoFixesV0851;
        if (!api || typeof api.adoptUnder !== 'function') { return false; }
        if (api.adoptUnder.__h18V0855Guarded === true) { return true; }

        const original = api.adoptUnder;
        const guarded = function (newKey, targetKey, position) {
            const targetBefore = rowByKey(targetKey);
            const targetParentKey = parentKey(targetBefore);
            if (!targetBefore || !targetParentKey) { return false; }

            const targetStateBefore = stackState(targetBefore);
            const expectedRootKey = String(targetStateBefore.StackRootKey || targetKey || '');
            const result = original.call(api, newKey, targetKey, position);
            if (result !== true) { return false; }

            const childAfter = rowByKey(newKey);
            const targetAfter = rowByKey(targetKey);
            if (!childAfter || !targetAfter) { return false; }
            if (parentKey(targetAfter) !== targetParentKey || parentKey(childAfter) !== targetParentKey) {
                return false;
            }

            const parent = rowByKey(targetParentKey);
            if (parent && String(parent.getAttribute('data-section-type') || '') === 'grid') {
                const childState = stackState(childAfter);
                if (!expectedRootKey || String(childState.StackRootKey || '') !== expectedRootKey) {
                    return false;
                }
            }

            return true;
        };
        guarded.__h18V0855Guarded = true;
        guarded.__h18V0855Original = original;
        api.adoptUnder = guarded;
        return true;
    }

    function install() {
        installLegacyPromptGuard();
        if (!installAdoptGuard()) {
            [0, 40, 120, 300, 700, 1400].forEach(function (delay) {
                window.setTimeout(installAdoptGuard, delay);
            });
        }
        document.documentElement.setAttribute('data-h18-lego-regression-hotfix', VERSION);
    }

    window.__h18LegoRegressionHotfixV0855 = {
        version: VERSION,
        purgeLegacyAutoDropPrompts: purgeLegacyAutoDropPrompts,
        installAdoptGuard: installAdoptGuard,
        legacyPromptObserver: null
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
