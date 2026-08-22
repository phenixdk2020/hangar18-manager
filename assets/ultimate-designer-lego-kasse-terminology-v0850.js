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
            button.setAttribute('data-h18-v0850-duplicate-container', '1');
            const shell = button.closest('.h18-library-item-shell');
            if (shell) {
                shell.classList.add('h18-v0850-legacy-container-palette-shell');
                shell.setAttribute('data-h18-v0850-duplicate-container', '1');
            }
        });
    }

    function renamePaletteTypes() {
        document.querySelectorAll('.h18-builder-palette-item[data-section-type="flex"]:not([data-h18-layout-tool])').forEach(function (button) {
            setDirectText(button, 'Række-/kolonne-kasse');
            button.setAttribute('title', 'Række-/kolonne-kasse — fordeler under-elementer vandret eller lodret i én fleksibel retning.');
        });
        document.querySelectorAll('.h18-builder-palette-item[data-section-type="grid"]:not([data-h18-layout-tool])').forEach(function (button) {
            setDirectText(button, 'Række- og kolonne-kasse');
            button.setAttribute('title', 'Række- og kolonne-kasse — opbygger et layout med flere kolonner og eventuelt flere rækker.');
        });
        document.querySelectorAll('.h18-builder-palette-item[data-h18-layout-tool="box"]').forEach(function (button) {
            setDirectText(button, 'Kasse');
            button.setAttribute('title', 'Kasse — almindelig beholder omkring et eller flere elementer.');
        });
        document.querySelectorAll('.h18-builder-palette-item[data-h18-layout-tool="auto-row"]').forEach(function (button) {
            setDirectText(button, 'Auto-kasser');
            button.setAttribute('title', 'Auto-kasser — opretter og fordeler automatisk kasser ved siden af hinanden.');
        });
    }

    function renameInspectorType() {
        const type = document.getElementById('h18-inspector-type');
        if (!type) { return; }
        const value = String(type.textContent || '').trim();
        const labels = {
            'Container': 'Kasse',
            'Flex container': 'Række-/kolonne-kasse',
            'Grid container': 'Række- og kolonne-kasse',
            'Flex-kasse': 'Række-/kolonne-kasse',
            'Grid-kasse': 'Række- og kolonne-kasse'
        };
        if (labels[value]) { type.textContent = labels[value]; }
    }

    function renameCanvasFallbacks() {
        const labels = {
            container: ['Container', 'Kasse'],
            flex: ['Flex container', 'Række-/kolonne-kasse'],
            grid: ['Grid container', 'Række- og kolonne-kasse']
        };
        Object.keys(labels).forEach(function (type) {
            document.querySelectorAll('.h18-canvas-type-' + type + ' .h18-canvas-preview-title').forEach(function (title) {
                const value = String(title.textContent || '').trim();
                if (value === labels[type][0] || value === 'Flex-kasse' || value === 'Grid-kasse') {
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
            if (title === 'Container · farve og kant' || title === 'Farver og kant' || title === 'Kasse · farve og kant') {
                legend.textContent = 'Kasse · farve og kant';
                const description = group.querySelector(':scope > .description');
                if (description) {
                    description.textContent = 'Baggrund, kant og farve gælder elementets ydre kasse. Tekst og billede forbliver indholdet inde i kassen.';
                }
                group.querySelectorAll('.h18-ud-lego-design-control strong').forEach(function (label) {
                    const value = String(label.textContent || '').trim();
                    if (value === 'Containerbaggrund') { label.textContent = 'Kassebaggrund'; }
                    if (value === 'Containerkant') { label.textContent = 'Kassekant'; }
                });
            }
            if (title === 'Container · form og effekter' || title === 'Form og effekter') {
                legend.textContent = 'Kasse · form og effekter';
            }
        });
    }

    function renameLibraryMetadata() {
        document.querySelectorAll('.h18-library-item-shell').forEach(function (shell) {
            const type = String(shell.getAttribute('data-library-type') || '');
            const tool = String(shell.getAttribute('data-library-tool') || '');
            if (type === 'container' && tool === 'box') {
                shell.setAttribute('data-library-label', 'kasse');
                shell.setAttribute('data-library-description', 'almindelig beholder omkring et eller flere elementer');
            } else if (type === 'flex') {
                shell.setAttribute('data-library-label', 'række-/kolonne-kasse');
                shell.setAttribute('data-library-description', 'fordeler under-elementer vandret eller lodret');
            } else if (type === 'grid' && tool !== 'auto-row') {
                shell.setAttribute('data-library-label', 'række- og kolonne-kasse');
                shell.setAttribute('data-library-description', 'layout med flere kolonner og eventuelt flere rækker');
            } else if (tool === 'auto-row') {
                shell.setAttribute('data-library-label', 'auto-kasser');
                shell.setAttribute('data-library-description', 'opretter og fordeler automatisk kasser ved siden af hinanden');
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
        renameLibraryMetadata();
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
