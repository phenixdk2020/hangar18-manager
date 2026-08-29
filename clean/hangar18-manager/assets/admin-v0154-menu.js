(function () {
    'use strict';
    function rows(list) { return Array.from(list ? list.querySelectorAll(':scope > .h18-menu-sort-row') : []); }
    function renumber(list) {
        rows(list).forEach(function (row, index) {
            var input = row.querySelector('.h18-menu-order-input');
            var label = row.querySelector('.h18-menu-order-label');
            if (input) { input.value = String(index + 1); }
            if (label) { label.textContent = String(index + 1); }
        });
    }
    function install() {
        var list = document.getElementById('h18-menu-sort-list');
        if (!list) { return; }
        var dragging = null;
        rows(list).forEach(function (row) {
            row.addEventListener('dragstart', function (event) {
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
            renumber(list);
        });
        list.addEventListener('click', function (event) {
            var button = event.target && event.target.closest ? event.target.closest('[data-menu-move]') : null;
            if (!button) { return; }
            var row = button.closest('.h18-menu-sort-row');
            if (!row) { return; }
            var direction = button.getAttribute('data-menu-move');
            if (direction === 'up' && row.previousElementSibling) { list.insertBefore(row, row.previousElementSibling); }
            if (direction === 'down' && row.nextElementSibling) { list.insertBefore(row.nextElementSibling, row); }
            renumber(list);
        });
        renumber(list);
    }
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
