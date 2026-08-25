(function () {
    'use strict';

    var STORAGE = 'h18_clean_designer_panels_v1';
    var workspace = null;
    var palette = null;
    var inspector = null;
    var state = { palette: false, inspector: false };
    var explicitPreference = false;

    function loadState() {
        try {
            var raw = window.localStorage.getItem(STORAGE);
            if (!raw) { return; }
            var parsed = JSON.parse(raw);
            if (!parsed || typeof parsed !== 'object') { return; }
            state.palette = !!parsed.palette;
            state.inspector = !!parsed.inspector;
            explicitPreference = true;
        } catch (ignore) {}
    }

    function saveState() {
        explicitPreference = true;
        try { window.localStorage.setItem(STORAGE, JSON.stringify(state)); } catch (ignore) {}
    }

    function titleFor(side) {
        return side === 'palette' ? 'Elementer' : 'Inspector';
    }

    function enhancePanel(panel, side) {
        if (!panel) { return; }
        var heading = panel.querySelector(':scope > h2');
        if (!heading || heading.dataset.h18Collapsible === '1') { return; }
        heading.dataset.h18Collapsible = '1';
        heading.classList.add('h18-clean-panel-head');

        var text = (heading.textContent || titleFor(side)).trim();
        heading.textContent = '';
        var label = document.createElement('span');
        label.className = 'h18-clean-panel-title';
        label.textContent = text;
        heading.appendChild(label);

        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'button h18-clean-panel-toggle';
        button.setAttribute('data-panel-toggle', side);
        button.addEventListener('click', function () {
            state[side] = !state[side];
            saveState();
            applyState();
        });
        heading.appendChild(button);
    }

    function setButton(panel, side, collapsed) {
        if (!panel) { return; }
        var button = panel.querySelector('.h18-clean-panel-toggle[data-panel-toggle="' + side + '"]');
        if (!button) { return; }
        button.textContent = collapsed ? (side === 'palette' ? '›' : '‹') : (side === 'palette' ? '‹' : '›');
        button.title = collapsed ? 'Fold ' + titleFor(side) + ' ud' : 'Fold ' + titleFor(side) + ' ind';
        button.setAttribute('aria-label', button.title);
        button.setAttribute('aria-expanded', collapsed ? 'false' : 'true');
    }

    function applyState() {
        if (!workspace) { return; }
        workspace.classList.toggle('is-palette-collapsed', state.palette);
        workspace.classList.toggle('is-inspector-collapsed', state.inspector);
        if (palette) {
            palette.classList.toggle('is-collapsed', state.palette);
            palette.setAttribute('data-collapsed', state.palette ? '1' : '0');
        }
        if (inspector) {
            inspector.classList.toggle('is-collapsed', state.inspector);
            inspector.setAttribute('data-collapsed', state.inspector ? '1' : '0');
        }
        setButton(palette, 'palette', state.palette);
        setButton(inspector, 'inspector', state.inspector);
        window.requestAnimationFrame(function () {
            window.dispatchEvent(new Event('resize'));
        });
    }

    function installWideCanvasButton() {
        var toolbar = document.querySelector('.h18-clean-toolbar');
        if (!toolbar || document.getElementById('h18-clean-wide-canvas')) { return; }
        var button = document.createElement('button');
        button.type = 'button';
        button.id = 'h18-clean-wide-canvas';
        button.className = 'button';
        button.textContent = '⇔ Mere canvas';
        button.title = 'Fold Elementer og Inspector ind/ud';
        button.addEventListener('click', function () {
            var bothCollapsed = state.palette && state.inspector;
            state.palette = !bothCollapsed;
            state.inspector = !bothCollapsed;
            saveState();
            applyState();
        });
        var switcher = document.getElementById('h18-clean-device-switcher');
        if (switcher && switcher.nextSibling) { toolbar.insertBefore(button, switcher.nextSibling); }
        else { toolbar.insertBefore(button, toolbar.firstChild); }
    }

    function applyAutomaticLaptopMode() {
        if (explicitPreference) { return; }
        // On common laptop/admin viewport widths, start with the palette folded
        // but leave Inspector visible. The user can open either panel at any time.
        if (window.innerWidth <= 1366) {
            state.palette = true;
            state.inspector = window.innerWidth <= 1120;
        }
    }

    function install() {
        workspace = document.querySelector('.h18-clean-workspace');
        palette = document.querySelector('.h18-clean-palette');
        inspector = document.querySelector('.h18-clean-inspector');
        if (!workspace || !palette || !inspector) { return; }

        loadState();
        applyAutomaticLaptopMode();
        enhancePanel(palette, 'palette');
        enhancePanel(inspector, 'inspector');
        installWideCanvasButton();
        applyState();
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
