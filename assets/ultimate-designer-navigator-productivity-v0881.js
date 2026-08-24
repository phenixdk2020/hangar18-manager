(function ($) {
    'use strict';

    if (window.__h18NavigatorProductivityV0881) { return; }

    const VERSION = '0.8.81';
    let panel = null;
    let tree = null;
    let typeFilter = null;
    let menu = null;
    let lastScrolledKey = '';
    let enhanceTimer = 0;

    function api() {
        return window.__h18NavigatorV0880 || null;
    }

    function rowByKey(key) {
        let found = $();
        $('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const row = $(this);
            const value = String(row.find('.h18-page-section-key').first().val() || row.attr('data-key') || '');
            if (!found.length && value === String(key || '')) { found = row; }
        });
        return found;
    }

    function rowType(key) {
        const row = rowByKey(key);
        return row.length ? String(row.attr('data-section-type') || 'unknown') : 'unknown';
    }

    function parentKey(key) {
        const row = rowByKey(key);
        if (!row.length) { return ''; }
        return String(row.find('.h18-layout-parent-key').first().val() || '');
    }

    function control(row, selector) {
        let result = row.find(selector).first();
        if (!result.length && row.hasClass('is-selected')) {
            result = $('#h18-page-inspector-target').find(selector).first();
        }
        return result;
    }

    function selectedKey() {
        const selected = tree ? tree.querySelector('.h18-v0880-tree-node.is-selected') : null;
        return selected ? String(selected.getAttribute('data-key') || '') : '';
    }

    function populateTypeFilter() {
        if (!typeFilter) { return; }
        const current = String(typeFilter.value || 'all');
        const types = new Set();
        $('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const type = String($(this).attr('data-section-type') || '').trim();
            if (type) { types.add(type); }
        });
        typeFilter.innerHTML = '<option value="all">Alle typer</option>';
        Array.from(types).sort().forEach(function (type) {
            const option = document.createElement('option');
            option.value = type;
            option.textContent = type;
            typeFilter.appendChild(option);
        });
        typeFilter.value = Array.from(typeFilter.options).some(function (option) { return option.value === current; }) ? current : 'all';
    }

    function matchingAndAncestorKeys(filter) {
        const visible = new Set();
        if (!filter || filter === 'all') { return visible; }
        $('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const row = $(this);
            const type = String(row.attr('data-section-type') || '');
            if (type !== filter) { return; }
            let key = String(row.find('.h18-page-section-key').first().val() || row.attr('data-key') || '');
            const seen = new Set();
            while (key && !seen.has(key)) {
                seen.add(key);
                visible.add(key);
                key = parentKey(key);
            }
        });
        return visible;
    }

    function applyTypeFilter() {
        if (!tree || !typeFilter) { return; }
        const filter = String(typeFilter.value || 'all');
        const keep = matchingAndAncestorKeys(filter);
        tree.querySelectorAll('.h18-v0880-tree-node[data-key]').forEach(function (node) {
            const key = String(node.getAttribute('data-key') || '');
            node.hidden = filter !== 'all' && !keep.has(key);
            node.setAttribute('data-h18-v0881-type', rowType(key));
        });
        document.documentElement.setAttribute('data-h18-v0881-navigator-filter', filter);
    }

    function autoscrollSelection() {
        if (!tree) { return; }
        const selected = tree.querySelector('.h18-v0880-tree-node.is-selected:not([hidden])');
        if (!selected) { return; }
        const key = String(selected.getAttribute('data-key') || '');
        if (!key || key === lastScrolledKey) { return; }
        lastScrolledKey = key;
        try { selected.scrollIntoView({ block: 'nearest', inline: 'nearest', behavior: 'smooth' }); }
        catch (ignore) { selected.scrollIntoView(false); }
    }

    function scheduleEnhance(delay) {
        clearTimeout(enhanceTimer);
        enhanceTimer = window.setTimeout(function () {
            populateTypeFilter();
            applyTypeFilter();
            autoscrollSelection();
        }, typeof delay === 'number' ? delay : 30);
    }

    function closeMenu() {
        if (menu) { menu.hidden = true; }
    }

    function existingAction(key, action) {
        const nav = api();
        const row = rowByKey(key);
        if (!nav || !row.length) { return; }
        nav.select(key);
        window.setTimeout(function () {
            if (action === 'edit') { return; }
            if (action === 'duplicate') { row.find('.h18-page-section-duplicate').first().trigger('click'); }
            else if (action === 'copy-design') { $('#h18-inspector-copy-design').trigger('click'); }
            else if (action === 'paste-design') { $('#h18-inspector-paste-design').trigger('click'); }
            else if (action === 'move') {
                const target = panel && panel.querySelector('.h18-v0880-parent');
                if (target) { target.focus(); target.scrollIntoView({ block: 'nearest' }); }
            }
            else if (action === 'toggle-active') {
                const active = control(row, '.h18-section-active,[name$="[Active]"]');
                if (active.length) { active.prop('checked', !active.is(':checked')).trigger('change'); }
            }
            else if (action === 'delete') { row.find('.h18-page-section-delete').first().trigger('click'); }
        }, 0);
    }

    function buildMenu() {
        menu = document.createElement('div');
        menu.className = 'h18-v0881-context-menu';
        menu.hidden = true;
        menu.setAttribute('role', 'menu');
        const actions = [
            ['edit', 'Redigér'],
            ['duplicate', 'Duplikér'],
            ['copy-design', 'Kopiér design'],
            ['paste-design', 'Indsæt design'],
            ['move', 'Flyt til…'],
            ['toggle-active', 'Vis/skjul'],
            ['delete', 'Fjern']
        ];
        actions.forEach(function (entry) {
            const button = document.createElement('button');
            button.type = 'button';
            button.setAttribute('role', 'menuitem');
            button.setAttribute('data-action', entry[0]);
            button.textContent = entry[1];
            if (entry[0] === 'delete') { button.classList.add('is-danger'); }
            menu.appendChild(button);
        });
        document.body.appendChild(menu);
        menu.addEventListener('click', function (event) {
            const button = event.target && event.target.closest ? event.target.closest('button[data-action]') : null;
            if (!button) { return; }
            const key = String(menu.getAttribute('data-key') || '');
            const action = String(button.getAttribute('data-action') || '');
            closeMenu();
            existingAction(key, action);
        });
    }

    function openMenu(event, key) {
        if (!menu) { buildMenu(); }
        menu.setAttribute('data-key', key);
        menu.style.left = Math.max(8, Math.min(window.innerWidth - 210, event.clientX)) + 'px';
        menu.style.top = Math.max(8, Math.min(window.innerHeight - 260, event.clientY)) + 'px';
        menu.hidden = false;
        const first = menu.querySelector('button');
        if (first) { first.focus(); }
    }

    function install() {
        panel = document.getElementById('h18-ultimate-designer-navigator-v0880');
        const nav = api();
        if (!panel || !nav) {
            window.setTimeout(install, 80);
            return;
        }
        tree = panel.querySelector('.h18-v0880-tree');
        const search = panel.querySelector('.h18-v0880-search');
        if (!tree || !search) { return; }

        const filterLabel = document.createElement('label');
        filterLabel.className = 'h18-v0881-type-filter';
        filterLabel.innerHTML = '<span>Type</span><select><option value="all">Alle typer</option></select>';
        search.insertAdjacentElement('afterend', filterLabel);
        typeFilter = filterLabel.querySelector('select');
        typeFilter.addEventListener('change', function () { applyTypeFilter(); autoscrollSelection(); });

        tree.addEventListener('contextmenu', function (event) {
            const button = event.target && event.target.closest ? event.target.closest('.h18-v0880-node-select') : null;
            if (!button) { return; }
            const node = button.closest('.h18-v0880-tree-node[data-key]');
            if (!node) { return; }
            event.preventDefault();
            event.stopPropagation();
            const key = String(node.getAttribute('data-key') || '');
            nav.select(key);
            openMenu(event, key);
        });

        document.addEventListener('pointerdown', function (event) {
            if (menu && !menu.hidden && !event.target.closest('.h18-v0881-context-menu')) { closeMenu(); }
        }, true);
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape') { closeMenu(); }
        }, true);

        const observer = new MutationObserver(function () { scheduleEnhance(20); });
        observer.observe(tree, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
        document.addEventListener('change', function (event) {
            if (event.target && event.target.matches && event.target.matches('.h18-section-active,[name$="[Active]"],.h18-layout-parent-key,.h18-layout-parent-select')) {
                scheduleEnhance(20);
            }
        }, true);

        document.documentElement.setAttribute('data-h18-navigator-productivity', VERSION);
        window.__h18NavigatorProductivityV0881 = {
            version: VERSION,
            filter: function (type) {
                if (!typeFilter) { return false; }
                typeFilter.value = String(type || 'all');
                applyTypeFilter();
                return true;
            },
            openContextMenuFor: function (key) {
                const node = tree.querySelector('.h18-v0880-tree-node[data-key="' + String(key || '') + '"] .h18-v0880-node-select');
                if (!node) { return false; }
                node.dispatchEvent(new MouseEvent('contextmenu', { bubbles: true, cancelable: true, clientX: 120, clientY: 120 }));
                return true;
            },
            selectedKey: selectedKey
        };
        scheduleEnhance(0);
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { window.setTimeout(install, 0); }
}(jQuery));
