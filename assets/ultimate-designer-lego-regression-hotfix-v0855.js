(function () {
    'use strict';

    if (window.__h18LegoRegressionHotfixV0855) { return; }

    const VERSION = '0.8.56';

    /*
     * v0.8.55 removed legacy Auto-kasse helper nodes from a MutationObserver.
     * nesting-tools legitimately regenerates those nodes during render, which
     * created a remove/recreate feedback loop on nested Under/Over drops.
     *
     * v0.8.56 deliberately performs no DOM removal and no adoptUnder wrapping.
     * Visibility is CSS-owned and nested adoption is handled idempotently by
     * ultimate-designer-lego-palette-side-drop-bridge-v0843.js.
     */
    function installSafetyCss() {
        if (document.getElementById('h18-lego-regression-safety-v0856')) { return; }
        const style = document.createElement('style');
        style.id = 'h18-lego-regression-safety-v0856';
        style.textContent = [
            '.h18-builder-canvas .h18-v0814-auto-drop-zone,',
            '.h18-builder-canvas .h18-v0814-auto-kasse-drop,',
            '.h18-builder-canvas .h18-ud-auto-box-empty-drop,',
            '.h18-builder-canvas [data-h18-v0814-auto-drop]{display:none!important;pointer-events:none!important;width:0!important;height:0!important;min-width:0!important;min-height:0!important;margin:0!important;padding:0!important;border:0!important;overflow:hidden!important}'
        ].join('');
        (document.head || document.documentElement).appendChild(style);
    }

    function install() {
        installSafetyCss();
        document.documentElement.setAttribute('data-h18-lego-regression-hotfix', VERSION);
    }

    window.__h18LegoRegressionHotfixV0855 = {
        version: VERSION,
        purgeLegacyAutoDropPrompts: function () { installSafetyCss(); },
        installAdoptGuard: function () { return true; },
        legacyPromptObserver: null
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
