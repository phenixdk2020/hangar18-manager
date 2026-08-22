(function () {
    'use strict';

    if (window.__h18LegoKasseTerminologyV0850) { return; }

    const VERSION = '0.8.50';
    let frame = 0;

    function setDirectText(node, value) {
        if (!node) { return; }
        const textNode = Array.from(node.childNodes || []).find(function (child) {
            return child.nodeType === Node.TEXT_NODE && String(child.nodeValue || '').trim();
        });
        if (textNode && String(textNode.nodeValue || '').trim() !== value) {
            textNode.nodeValue = value;
        }
    }

    function hideLegacyContainerPalette() {
        const canonicalKasse = document.querySelector('.h18-builder-palette-item[data-h18-layout-tool="box"]');
        if (!canonicalKasse) { return; }

        document.querySelectorAll('.h18-builder-palette-item[data-section-type="container"]:not([data-h18-layout-tool])').forEach(function (button) {
            button.classList.add('h18-v0850-legacy-container-palette');
            const shell = button.closest('.h18-library-item-shell');
            if (shell) { shell.classList.add('h18-v0850-legacy-container-palette-shell'); }
        });
    }

    function renamePaletteTypes() {
        document.querySelectorAll('.h18-builder-palette-item[data-section-type="flex"]:not([data-h18-layout-tool])').forEach(function (button) {
            setDirectText(button, 'Flex-kasse');
            button.setAttribute('title', 'Flex-kasse — kasse der fordeler under-elementer i række eller kolonne.');
        });
        document.querySelectorAll('.h18-builder-palette-item[data-section-type="grid"]:not([data-h18-layout-tool])').forEach(function (button) {
            setDirectText(button, 'Grid-kasse');
            button.setAttribute('title', 'Grid-kasse — manuel kasse med kolonne-layout til under-elementer.');
        });
    }

    function renameInspectorType() {
        const type = document.getElementById('h18-inspector-type');
        if (!type) { return; }
        const value = String(type.textContent || '').trim();
        const labels = {
            'Container': 'Kasse',
            'Flex container': 'Flex-kasse',
            'Grid container': 'Grid-kasse'
        };
        if (labels[value]) { type.textContent = labels[value]; }
    }

    function renameCanvasFallbacks() {
        const labels = {
            container: ['Container', 'Kasse'],
            flex: ['Flex container', 'Flex-kasse'],
            grid: ['Grid container', 'Grid-kasse']
        };
        Object.keys(labels).forEach(function (type) {
            document.querySelectorAll('.h18-canvas-type-' + type + ' .h18-canvas-preview-title').forEach(function (title) {
                if (String(title.textContent || '').trim() === labels[type][0]) {
                    title.textContent = labels[type][1];
                }
            });
        });
    }

    function renameDesignPanel() {
        const panel = document.getElementById('h18-ud-lego-design-panel');
        if (!panel) { return; }
        panel.querySelectorAll('.h18-ud-lego-design-group').forEach(function (group) {
            const legend = group.querySelector('legend');
            if (!legend) { return; }
            const title = String(legend.textContent || '').trim();
            if (title === 'Container · farve og kant' || title === 'Farver og kant') {
                legend.textContent = 'Kasse · farve og kant';
                const description = group.querySelector(':scope > .description');
                if (description) {
                    description.textContent = 'Baggrund, kant og farve gælder elementets ydre kasse. Tekst og billede forbliver indholdet inde i kassen.';
                }
                group.querySelectorAll('.h18-ud-lego-design-control strong').forEach(function (label) {
                    const value = String(label.textContent || '').trim();
                    if (value === 'Containerbaggrund') { label.textContent = 'Baggrund'; }
                    if (value === 'Containerkant') { label.textContent = 'Kantfarve'; }
                });
            }
            if (title === 'Container · form og effekter' || title === 'Form og effekter') {
                legend.textContent = 'Kasse · form og effekter';
            }
        });
    }

    function polish() {
        frame = 0;
        hideLegacyContainerPalette();
        renamePaletteTypes();
        renameInspectorType();
        renameCanvasFallbacks();
        renameDesignPanel();
    }

    function queue() {
        if (frame) { return; }
        frame = window.requestAnimationFrame(polish);
    }

    if (window.MutationObserver) {
        new MutationObserver(queue).observe(document.body, {
            childList: true,
            subtree: true,
            characterData: true
        });
    }

    document.addEventListener('click', queue, true);
    document.addEventListener('input', queue, true);
    document.addEventListener('change', queue, true);

    [0, 80, 300, 900].forEach(function (delay) { window.setTimeout(polish, delay); });

    document.documentElement.setAttribute('data-h18-lego-kasse-terminology', VERSION);
    window.__h18LegoKasseTerminologyV0850 = {
        version: VERSION,
        polish: polish
    };
}());
