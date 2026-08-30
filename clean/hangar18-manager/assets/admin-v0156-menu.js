(function () {
    'use strict';

    function q(sel, root) { return (root || document).querySelector(sel); }
    function qa(sel, root) { return Array.from((root || document).querySelectorAll(sel)); }
    function rows(list) { return qa(':scope > .h18-menu-sort-row', list); }
    function itemId(row) { return parseInt(row && row.dataset.menuItemId || '0', 10) || 0; }
    function parentInput(row) { return q('.h18-menu-parent-input', row); }
    function parentId(row) { var input = parentInput(row); return parseInt(input && input.value || '0', 10) || 0; }
    function setParent(row, id) {
        var input = parentInput(row);
        if (input) { input.value = String(id || 0); }
        row.dataset.parentId = String(id || 0);
    }
    function rowById(list, id) { return rows(list).find(function (row) { return itemId(row) === id; }) || null; }
    function isDescendant(list, candidateId, ancestorId) {
        var cursor = candidateId, seen = {};
        while (cursor && !seen[cursor]) {
            if (cursor === ancestorId) { return true; }
            seen[cursor] = true;
            var row = rowById(list, cursor);
            cursor = row ? parentId(row) : 0;
        }
        return false;
    }
    function depth(list, row) {
        var d = 0, cursor = parentId(row), seen = {};
        while (cursor && !seen[cursor] && d < 6) {
            seen[cursor] = true;
            var parent = rowById(list, cursor);
            if (!parent) { break; }
            d += 1;
            cursor = parentId(parent);
        }
        return d;
    }
    function renumber(list) {
        rows(list).forEach(function (row, index) {
            var input = q('.h18-menu-order-input', row);
            if (input) { input.value = String(index + 1); }
            row.style.setProperty('--vd-menu-depth', String(depth(list, row)));
        });
        updatePreview(list);
    }
    function titleFor(row) {
        var input = q('.h18-menu-title-input', row);
        var preview = q('.h18-menu-item-title-preview', row);
        return (input && input.value || preview && preview.textContent || '').trim();
    }
    function buildTree(list) {
        var all = rows(list), map = {}, roots = [];
        all.forEach(function (row) { map[itemId(row)] = { row: row, children: [] }; });
        all.forEach(function (row) {
            var id = itemId(row), parent = parentId(row), node = map[id];
            if (parent && map[parent] && parent !== id) { map[parent].children.push(node); }
            else { roots.push(node); }
        });
        return roots;
    }
    function renderTree(nodes, mobile) {
        var ul = document.createElement('ul');
        ul.className = mobile ? 'h18-menu-preview-tree is-mobile' : 'h18-menu-preview-tree';
        nodes.forEach(function (node) {
            var li = document.createElement('li');
            var label = document.createElement('span');
            label.textContent = titleFor(node.row) || 'Uden navn';
            li.appendChild(label);
            if (node.children.length) { li.appendChild(renderTree(node.children, mobile)); }
            ul.appendChild(li);
        });
        return ul;
    }
    function updatePreview(list) {
        var tree = buildTree(list);
        var desktop = document.getElementById('h18-menu-preview-desktop');
        var mobile = document.getElementById('h18-menu-preview-mobile');
        if (desktop) { desktop.replaceChildren(renderTree(tree, false)); }
        if (mobile) { mobile.replaceChildren(renderTree(tree, true)); }
    }
    function moveRow(list, row, direction) {
        if (direction === 'up' && row.previousElementSibling) { list.insertBefore(row, row.previousElementSibling); }
        if (direction === 'down' && row.nextElementSibling) { list.insertBefore(row.nextElementSibling, row); }
        renumber(list);
    }
    function indentRow(list, row) {
        var previous = row.previousElementSibling;
        if (!previous) { return; }
        var newParent = itemId(previous);
        if (!newParent || isDescendant(list, newParent, itemId(row))) { return; }
        setParent(row, newParent);
        renumber(list);
    }
    function outdentRow(list, row) {
        var currentParent = parentId(row);
        if (!currentParent) { return; }
        var parentRow = rowById(list, currentParent);
        setParent(row, parentRow ? parentId(parentRow) : 0);
        renumber(list);
    }
    function installDialog() {
        var dialog = document.getElementById('h18-menu-add-dialog');
        if (!dialog) { return; }
        var lastFocus = null;
        function open() {
            lastFocus = document.activeElement;
            dialog.hidden = false;
            document.body.classList.add('h18-menu-dialog-open');
            var focus = q('input:not([disabled]),button:not([disabled])', dialog);
            if (focus) { setTimeout(function () { focus.focus(); }, 0); }
        }
        function close() {
            dialog.hidden = true;
            document.body.classList.remove('h18-menu-dialog-open');
            if (lastFocus && lastFocus.focus) { lastFocus.focus(); }
        }
        qa('[data-menu-add-open]').forEach(function (button) { button.addEventListener('click', open); });
        qa('[data-menu-add-close]', dialog).forEach(function (button) { button.addEventListener('click', close); });
        qa('[data-menu-add-tab]', dialog).forEach(function (button) {
            button.addEventListener('click', function () {
                var key = button.getAttribute('data-menu-add-tab');
                qa('[data-menu-add-tab]', dialog).forEach(function (b) { b.classList.toggle('button-primary', b === button); });
                qa('[data-menu-add-panel]', dialog).forEach(function (panel) { panel.hidden = panel.getAttribute('data-menu-add-panel') !== key; });
            });
        });
        document.addEventListener('keydown', function (event) { if (!dialog.hidden && event.key === 'Escape') { close(); } });
    }
    function install() {
        var list = document.getElementById('h18-menu-sort-list');
        installDialog();
        if (!list) { return; }
        var dragging = null;
        rows(list).forEach(function (row) {
            row.addEventListener('dragstart', function (event) {
                var handle = event.target && event.target.closest ? event.target.closest('.h18-menu-drag-handle') : null;
                if (!handle) { event.preventDefault(); return; }
                dragging = row;
                row.classList.add('is-dragging');
                if (event.dataTransfer) { event.dataTransfer.effectAllowed = 'move'; event.dataTransfer.setData('text/plain', row.dataset.menuItemId || ''); }
            });
            row.addEventListener('dragend', function () { row.classList.remove('is-dragging'); dragging = null; renumber(list); });
        });
        list.addEventListener('dragover', function (event) {
            if (!dragging) { return; }
            event.preventDefault();
            var target = event.target && event.target.closest ? event.target.closest('.h18-menu-sort-row') : null;
            if (!target || target === dragging || target.parentNode !== list) { return; }
            var rect = target.getBoundingClientRect();
            var before = event.clientY < rect.top + rect.height / 2;
            list.insertBefore(dragging, before ? target : target.nextSibling);
            var wantsChild = event.clientX > rect.left + Math.min(150, rect.width * 0.28);
            if (wantsChild && !isDescendant(list, itemId(target), itemId(dragging))) { setParent(dragging, itemId(target)); }
            else { setParent(dragging, parentId(target)); }
            renumber(list);
        });
        list.addEventListener('click', function (event) {
            var row = event.target && event.target.closest ? event.target.closest('.h18-menu-sort-row') : null;
            if (!row) { return; }
            var move = event.target.closest('[data-menu-move]');
            if (move) { moveRow(list, row, move.getAttribute('data-menu-move')); return; }
            if (event.target.closest('[data-menu-indent]')) { indentRow(list, row); return; }
            if (event.target.closest('[data-menu-outdent]')) { outdentRow(list, row); return; }
            var edit = event.target.closest('[data-menu-edit]');
            if (edit) {
                var editor = q('.h18-menu-item-editor', row);
                var open = editor && editor.hidden;
                if (editor) { editor.hidden = !open; }
                edit.setAttribute('aria-expanded', open ? 'true' : 'false');
                edit.textContent = open ? 'Luk' : 'Redigér';
            }
        });
        list.addEventListener('input', function (event) {
            if (!event.target.classList.contains('h18-menu-title-input')) { return; }
            var row = event.target.closest('.h18-menu-sort-row');
            var title = row && q('.h18-menu-item-title-preview', row);
            if (title) { title.textContent = event.target.value || 'Uden navn'; }
            updatePreview(list);
        });
        renumber(list);
    }
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());

