(function ($) {
    'use strict';

    if (window.__h18NavigatorV0880) { return; }

    const cfg = window.H18NavigatorV0880 || {};
    const VERSION = String(cfg.version || '0.8.80');
    const STORAGE_KEY = String(cfg.workspaceKey || 'h18.ultimate-designer.navigator.v0880');
    const OUTLINE_KEY = String(cfg.outlineKey || 'h18.ultimate-designer.container-outlines.v0880');
    const MAX_DEPTH = 2;

    let $sections = $();
    let $inspector = $();
    let panel = null;
    let treeRoot = null;
    let breadcrumbNode = null;
    let searchNode = null;
    let parentSelect = null;
    let siblingSelect = null;
    let selectedKey = '';
    let mutationTimer = 0;
    let collapsed = {};
    let panelCollapsed = false;

    function storageRead() {
        try {
            const data = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}');
            collapsed = data && typeof data.collapsed === 'object' ? data.collapsed : {};
            panelCollapsed = !!(data && data.panelCollapsed);
        } catch (ignore) {
            collapsed = {};
            panelCollapsed = false;
        }
    }

    function storageWrite() {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({ collapsed: collapsed, panelCollapsed: panelCollapsed }));
        } catch (ignore) { /* browser storage unavailable */ }
    }

    function allRows() {
        return $sections.children('.h18-page-section-row');
    }

    function activeRows() {
        return allRows().filter(':not(.h18-page-section-removed)');
    }

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($inspector.find(selector));
        }
        return $result;
    }

    function rowKey($row) {
        return String(controls($row, '.h18-page-section-key').first().val() || $row.attr('data-key') || '').trim();
    }

    function rowType($row) {
        return String($row.attr('data-section-type') || '').trim();
    }

    function rowLabel($row) {
        const nav = String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
        if (nav) { return nav; }
        const summary = String($row.find('.h18-page-section-title-summary').first().text() || '').trim();
        if (summary) { return summary; }
        const labels = {
            container: 'Kasse', flex: 'Række-/kolonne-kasse', grid: 'Række- og kolonne-kasse',
            text: 'Tekst', image: 'Billede', text_image: 'Tekst + billede', hero: 'Hero', buttons: 'Knapper',
            card: 'Kort', card_grid: 'Kort-grid', highlight: 'Fremhævning', icon: 'Ikon', list: 'Liste',
            badge: 'Badge', quote: 'Citat', spacer: 'Spacer', divider: 'Skillelinje', tabs: 'Faner',
            accordion: 'Accordion', carousel: 'Carousel', mail_form: 'Formular', poll: 'Afstemning',
            query_list: 'Dynamisk liste', component: 'Komponent', embed: 'Embed', shortcode: 'Shortcode', html: 'HTML'
        };
        return labels[rowType($row)] || rowType($row) || 'Element';
    }

    function parentKey($row) {
        return String(controls($row, '.h18-layout-parent-key').first().val() || '').trim();
    }

    function rowByKey(key) {
        let $found = $();
        const wanted = String(key || '').trim();
        if (!wanted) { return $found; }
        activeRows().each(function () {
            const $row = $(this);
            if (!$found.length && rowKey($row) === wanted) { $found = $row; }
        });
        return $found;
    }

    function isRemoved($row) {
        return $row.hasClass('h18-page-section-removed');
    }

    function isActive($row) {
        const $field = controls($row, '[name$="[Active]"]').first();
        return !$field.length || $field.is(':checked');
    }

    function isContainer($row) {
        const type = rowType($row);
        return type === 'container' || type === 'flex' || type === 'grid';
    }

    function isAutoKasse($row) {
        return rowType($row) === 'grid' && rowLabel($row) === 'Auto-kasser';
    }

    function directChildren(key) {
        const wanted = String(key || '');
        return activeRows().filter(function () { return parentKey($(this)) === wanted; });
    }

    function parentChain(key) {
        const result = [];
        const seen = new Set();
        let cursor = String(key || '');
        while (cursor) {
            if (seen.has(cursor)) { break; }
            seen.add(cursor);
            const $row = rowByKey(cursor);
            if (!$row.length) { break; }
            result.unshift({ key: cursor, label: rowLabel($row), type: rowType($row) });
            cursor = parentKey($row);
        }
        return result;
    }

    function depthForParent(parent) {
        if (!parent) { return 0; }
        return parentChain(parent).length;
    }

    function wouldCycle(sourceKey, targetParent) {
        let cursor = String(targetParent || '');
        const seen = new Set();
        while (cursor) {
            if (cursor === sourceKey) { return true; }
            if (seen.has(cursor)) { return true; }
            seen.add(cursor);
            const $row = rowByKey(cursor);
            if (!$row.length) { return false; }
            cursor = parentKey($row);
        }
        return false;
    }

    function canParent($source, $target) {
        if (!$source.length || !$target.length || !isContainer($target)) { return false; }
        const sourceKey = rowKey($source);
        const targetKey = rowKey($target);
        if (!sourceKey || !targetKey || sourceKey === targetKey || wouldCycle(sourceKey, targetKey)) { return false; }
        if (depthForParent(targetKey) >= MAX_DEPTH) { return false; }
        if (isAutoKasse($target) && rowType($source) !== 'container') { return false; }
        return true;
    }

    function setParent($row, key) {
        const value = String(key || '');
        const $hidden = controls($row, '.h18-layout-parent-key').first();
        const $select = controls($row, '.h18-layout-parent-select').first();
        if (!$hidden.length) { return false; }
        if (String($hidden.val() || '') !== value) { $hidden.val(value).trigger('change'); }
        if ($select.length && String($select.val() || '') !== value) { $select.val(value).trigger('change'); }
        if (value) { $row.attr('data-h18-nested-in-box', value); }
        else { $row.removeAttr('data-h18-nested-in-box'); }
        return true;
    }

    function descendantKeys(rootKey) {
        const result = [];
        const queue = [String(rootKey || '')];
        const seen = new Set(queue);
        while (queue.length) {
            const current = queue.shift();
            directChildren(current).each(function () {
                const childKey = rowKey($(this));
                if (childKey && !seen.has(childKey)) {
                    seen.add(childKey);
                    result.push(childKey);
                    queue.push(childKey);
                }
            });
        }
        return result;
    }

    function subtreeEnd($row) {
        if (!$row.length) { return $row; }
        const descendants = new Set(descendantKeys(rowKey($row)));
        let $end = $row;
        let $cursor = $row.next();
        while ($cursor.length && descendants.has(rowKey($cursor))) {
            $end = $cursor;
            $cursor = $cursor.next();
        }
        return $end;
    }

    function syncOrder() {
        let index = 0;
        allRows().each(function () {
            const $row = $(this);
            if (isRemoved($row)) { return; }
            index += 1;
            controls($row, '.h18-page-section-order').val(index * 10).trigger('change');
        });
        if ($sections.hasClass('ui-sortable')) { $sections.sortable('refresh'); }
    }

    function refreshCanonical(reason) {
        syncOrder();
        const nesting = window.__h18NestingToolsV0840;
        if (nesting && typeof nesting.refresh === 'function') { nesting.refresh(); }
        const selection = window.__h18LegoInspectorOnlyV0847;
        if (selection && typeof selection.refreshSelectedCanvasMarker === 'function') {
            window.setTimeout(function () { selection.refreshSelectedCanvasMarker(); }, 0);
        }
        const trace = window.__h18UltimateDesignerTraceV0876;
        if (trace && typeof trace.record === 'function') {
            trace.record('NAVIGATOR_STRUCTURE', document.activeElement, { reason: reason || 'navigator', key: selectedKey });
        }
        scheduleRender(20);
    }

    function moveInto(sourceKey, targetKey) {
        const $source = rowByKey(sourceKey);
        const $target = rowByKey(targetKey);
        if (!canParent($source, $target)) { return false; }
        if (!setParent($source, targetKey)) { return false; }
        subtreeEnd($target).after($source);
        refreshCanonical('move-into');
        return true;
    }

    function moveOut(sourceKey) {
        const $source = rowByKey(sourceKey);
        if (!$source.length) { return false; }
        const currentParent = parentKey($source);
        if (!currentParent) { return false; }
        const $parent = rowByKey(currentParent);
        const grandParent = $parent.length ? parentKey($parent) : '';
        if (grandParent && wouldCycle(sourceKey, grandParent)) { return false; }
        const $end = $parent.length ? subtreeEnd($parent) : $source;
        if (!setParent($source, grandParent)) { return false; }
        $end.after($source);
        refreshCanonical('move-out');
        return true;
    }

    function siblingsFor($source) {
        const parent = parentKey($source);
        return activeRows().filter(function () { return parentKey($(this)) === parent; });
    }

    function moveTopBottom(sourceKey, bottom) {
        const $source = rowByKey(sourceKey);
        if (!$source.length) { return false; }
        const $siblings = siblingsFor($source).not($source);
        if (!$siblings.length) { return false; }
        if (bottom) {
            subtreeEnd($siblings.last()).after($source);
        } else {
            $siblings.first().before($source);
        }
        refreshCanonical(bottom ? 'move-bottom' : 'move-top');
        return true;
    }

    function moveBeforeAfter(sourceKey, targetKey, after) {
        const $source = rowByKey(sourceKey);
        const $target = rowByKey(targetKey);
        if (!$source.length || !$target.length || sourceKey === targetKey) { return false; }
        if (parentKey($source) !== parentKey($target)) { return false; }
        if (after) { subtreeEnd($target).after($source); }
        else { $target.before($source); }
        refreshCanonical(after ? 'move-after' : 'move-before');
        return true;
    }

    function selectCanonical(key) {
        const $row = rowByKey(key);
        if (!$row.length) { return false; }
        selectedKey = key;
        const selection = window.__h18LegoInspectorOnlyV0847;
        let node = null;
        const parent = parentKey($row);
        if (parent) {
            node = document.querySelector('[data-h18-v0811-child="' + key + '"]') ||
                document.querySelector('[data-h18-v0811-row="' + key + '"]');
        }
        if (!node) { node = $row.get(0); }
        if (selection && typeof selection.selectInspectorForNode === 'function') {
            selection.selectInspectorForNode(node);
        } else {
            const edit = $row.find('.h18-page-section-edit').get(0) || $row.find('.h18-page-section-header').get(0);
            if (edit) { edit.click(); }
        }
        scheduleRender(0);
        return true;
    }

    function currentSelectionKey() {
        const api = window.__h18LegoInspectorOnlyV0847;
        if (api && typeof api.activeSelection === 'function') {
            try {
                const active = api.activeSelection();
                if (active && active.key) { return String(active.key); }
            } catch (ignore) { /* noop */ }
        }
        const $selected = activeRows().filter('.is-selected').first();
        return rowKey($selected);
    }

    function makeButton(label, action, title) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'button button-small';
        button.textContent = label;
        if (title) { button.title = title; }
        button.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            action();
        });
        return button;
    }

    function treeData() {
        const nodes = new Map();
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (!key) { return; }
            nodes.set(key, {
                key: key,
                parent: parentKey($row),
                label: rowLabel($row),
                type: rowType($row),
                active: isActive($row),
                children: []
            });
        });
        const roots = [];
        nodes.forEach(function (node) {
            if (node.parent && nodes.has(node.parent)) { nodes.get(node.parent).children.push(node); }
            else { roots.push(node); }
        });
        return { nodes: nodes, roots: roots };
    }

    function matchesSearch(node, query) {
        if (!query) { return true; }
        const hay = (node.label + ' ' + node.type + ' ' + node.key).toLowerCase();
        if (hay.indexOf(query) >= 0) { return true; }
        return node.children.some(function (child) { return matchesSearch(child, query); });
    }

    function renderTreeNode(node, query) {
        if (!matchesSearch(node, query)) { return null; }
        const li = document.createElement('li');
        li.className = 'h18-v0880-tree-node';
        li.setAttribute('data-key', node.key);
        if (node.key === selectedKey) { li.classList.add('is-selected'); }
        if (!node.active) { li.classList.add('is-inactive'); }

        const row = document.createElement('div');
        row.className = 'h18-v0880-tree-row';
        if (node.children.length) {
            const fold = document.createElement('button');
            fold.type = 'button';
            fold.className = 'h18-v0880-fold';
            fold.textContent = collapsed[node.key] ? '▸' : '▾';
            fold.title = collapsed[node.key] ? 'Fold ud' : 'Fold sammen';
            fold.addEventListener('click', function (event) {
                event.stopPropagation();
                collapsed[node.key] = !collapsed[node.key];
                storageWrite();
                render();
            });
            row.appendChild(fold);
        } else {
            const spacer = document.createElement('span');
            spacer.className = 'h18-v0880-fold-spacer';
            row.appendChild(spacer);
        }

        const select = document.createElement('button');
        select.type = 'button';
        select.className = 'h18-v0880-node-select';
        select.innerHTML = '<strong></strong><small></small>';
        select.querySelector('strong').textContent = node.label;
        select.querySelector('small').textContent = node.type + (node.active ? '' : ' · skjult/inaktiv');
        select.addEventListener('click', function () { selectCanonical(node.key); });
        row.appendChild(select);
        li.appendChild(row);

        if (node.children.length && !collapsed[node.key]) {
            const ul = document.createElement('ul');
            node.children.forEach(function (child) {
                const childLi = renderTreeNode(child, query);
                if (childLi) { ul.appendChild(childLi); }
            });
            if (ul.children.length) { li.appendChild(ul); }
        }
        return li;
    }

    function renderBreadcrumb() {
        if (!breadcrumbNode) { return; }
        breadcrumbNode.innerHTML = '';
        if (!selectedKey) {
            breadcrumbNode.textContent = 'Ingen valgt';
            return;
        }
        const chain = parentChain(selectedKey);
        const root = document.createElement('span');
        root.textContent = 'Side';
        breadcrumbNode.appendChild(root);
        chain.forEach(function (part) {
            breadcrumbNode.appendChild(document.createTextNode(' › '));
            const button = document.createElement('button');
            button.type = 'button';
            button.textContent = part.label;
            button.addEventListener('click', function () { selectCanonical(part.key); });
            breadcrumbNode.appendChild(button);
        });
    }

    function renderMoveControls() {
        if (!parentSelect || !siblingSelect) { return; }
        parentSelect.innerHTML = '<option value="">— Topniveau —</option>';
        siblingSelect.innerHTML = '<option value="">— Vælg sibling —</option>';
        const $source = rowByKey(selectedKey);
        if (!$source.length) { return; }

        activeRows().each(function () {
            const $candidate = $(this);
            const key = rowKey($candidate);
            if (!canParent($source, $candidate)) { return; }
            const option = document.createElement('option');
            option.value = key;
            option.textContent = rowLabel($candidate) + ' [' + rowType($candidate) + ']';
            if (key === parentKey($source)) { option.selected = true; }
            parentSelect.appendChild(option);
        });
        if (!parentKey($source)) { parentSelect.value = ''; }

        siblingsFor($source).not($source).each(function () {
            const $candidate = $(this);
            const option = document.createElement('option');
            option.value = rowKey($candidate);
            option.textContent = rowLabel($candidate);
            siblingSelect.appendChild(option);
        });
    }

    function render() {
        if (!panel || !treeRoot) { return; }
        selectedKey = currentSelectionKey() || selectedKey;
        panel.classList.toggle('is-collapsed', panelCollapsed);
        const query = String(searchNode && searchNode.value || '').trim().toLowerCase();
        treeRoot.innerHTML = '';
        treeData().roots.forEach(function (node) {
            const li = renderTreeNode(node, query);
            if (li) { treeRoot.appendChild(li); }
        });
        renderBreadcrumb();
        renderMoveControls();
    }

    function scheduleRender(delay) {
        clearTimeout(mutationTimer);
        mutationTimer = window.setTimeout(render, typeof delay === 'number' ? delay : 50);
    }

    function applyOutlineState(enabled) {
        document.documentElement.classList.toggle('h18-v0880-show-container-outlines', !!enabled);
        try { localStorage.setItem(OUTLINE_KEY, enabled ? '1' : '0'); } catch (ignore) { /* noop */ }
    }

    function installPanel() {
        if (panel || !document.body) { return; }
        $sections = $('#h18-page-sections-sortable');
        $inspector = $('#h18-page-inspector-target');
        if (!$sections.length) { return; }

        storageRead();
        panel = document.createElement('aside');
        panel.id = 'h18-ultimate-designer-navigator-v0880';
        panel.innerHTML = [
            '<header><div><strong>Navigator</strong><small>v' + VERSION + '</small></div><button type="button" class="button button-small h18-v0880-collapse">−</button></header>',
            '<div class="h18-v0880-body">',
            '<div class="h18-v0880-breadcrumb"></div>',
            '<label class="h18-v0880-search"><span>Søg</span><input type="search" placeholder="Navn, type eller key"></label>',
            '<ul class="h18-v0880-tree"></ul>',
            '<section class="h18-v0880-move"><h4>Flyt valgt element</h4>',
            '<label>Flyt til<select class="h18-v0880-parent"></select></label>',
            '<div class="h18-v0880-actions h18-v0880-parent-actions"></div>',
            '<label>Placér ved<select class="h18-v0880-sibling"></select></label>',
            '<div class="h18-v0880-actions h18-v0880-sibling-actions"></div>',
            '</section>',
            '<label class="h18-v0880-outline"><input type="checkbox"> Vis kontur på alle Kasser/Grid/Flex</label>',
            '</div>'
        ].join('');
        document.body.appendChild(panel);

        treeRoot = panel.querySelector('.h18-v0880-tree');
        breadcrumbNode = panel.querySelector('.h18-v0880-breadcrumb');
        searchNode = panel.querySelector('.h18-v0880-search input');
        parentSelect = panel.querySelector('.h18-v0880-parent');
        siblingSelect = panel.querySelector('.h18-v0880-sibling');

        panel.querySelector('.h18-v0880-collapse').addEventListener('click', function () {
            panelCollapsed = !panelCollapsed;
            this.textContent = panelCollapsed ? '+' : '−';
            storageWrite();
            render();
        });
        searchNode.addEventListener('input', function () { render(); });

        const parentActions = panel.querySelector('.h18-v0880-parent-actions');
        parentActions.appendChild(makeButton('Flyt til', function () {
            const target = String(parentSelect.value || '');
            if (!selectedKey) { return; }
            if (!target) {
                const $source = rowByKey(selectedKey);
                if (!$source.length || !setParent($source, '')) { return; }
                $sections.append($source);
                refreshCanonical('move-root');
            } else {
                moveInto(selectedKey, target);
            }
        }, 'Sæt valgt element ind i den valgte Kasse/Grid/Flex'));
        parentActions.appendChild(makeButton('Flyt ud', function () { if (selectedKey) { moveOut(selectedKey); } }, 'Flyt ét niveau ud af nuværende parent'));
        parentActions.appendChild(makeButton('Til top', function () { if (selectedKey) { moveTopBottom(selectedKey, false); } }));
        parentActions.appendChild(makeButton('Til bund', function () { if (selectedKey) { moveTopBottom(selectedKey, true); } }));

        const siblingActions = panel.querySelector('.h18-v0880-sibling-actions');
        siblingActions.appendChild(makeButton('Før', function () {
            if (selectedKey && siblingSelect.value) { moveBeforeAfter(selectedKey, siblingSelect.value, false); }
        }));
        siblingActions.appendChild(makeButton('Efter', function () {
            if (selectedKey && siblingSelect.value) { moveBeforeAfter(selectedKey, siblingSelect.value, true); }
        }));

        const outline = panel.querySelector('.h18-v0880-outline input');
        let outlines = false;
        try { outlines = localStorage.getItem(OUTLINE_KEY) === '1'; } catch (ignore) { /* noop */ }
        outline.checked = outlines;
        applyOutlineState(outlines);
        outline.addEventListener('change', function () { applyOutlineState(outline.checked); });

        const observer = new MutationObserver(function (mutations) {
            const structural = mutations.some(function (m) {
                return m.type === 'childList' || (m.type === 'attributes' && (m.attributeName === 'class' || m.attributeName === 'data-section-type'));
            });
            if (structural) { scheduleRender(60); }
        });
        observer.observe($sections.get(0), { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'data-section-type'] });

        document.addEventListener('change', function (event) {
            if (event.target && event.target.matches && event.target.matches('.h18-layout-parent-key,.h18-layout-parent-select,.h18-section-navigator-label,[name$="[Active]"]')) {
                scheduleRender(20);
            }
        }, true);
        document.addEventListener('click', function (event) {
            if (event.target && event.target.closest && event.target.closest('.h18-page-section-edit,.h18-page-section-header,.h18-v0811-edit-child')) {
                scheduleRender(0);
            }
        }, false);

        document.documentElement.setAttribute('data-h18-navigator', VERSION);
        window.__h18NavigatorV0880 = {
            version: VERSION,
            render: render,
            select: selectCanonical,
            moveInto: moveInto,
            moveOut: moveOut,
            moveBeforeAfter: moveBeforeAfter,
            moveTopBottom: moveTopBottom,
            canParent: function (sourceKey, targetKey) { return canParent(rowByKey(sourceKey), rowByKey(targetKey)); }
        };
        render();
    }

    if (document.body) { window.setTimeout(installPanel, 0); }
    else { document.addEventListener('DOMContentLoaded', installPanel, { once: true }); }
}(jQuery));
