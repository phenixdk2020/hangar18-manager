(function () {
    'use strict';

    var STATUS = {
        'h18-clean-manager': ['Klar', 'ready'],
        'h18-clean-editor': ['Klar', 'ready'],
        'h18-clean-pages': ['Klar', 'ready'],
        'h18-clean-backup': ['Klar', 'ready'],
        'h18-clean-updates': ['Klar', 'ready'],
        'h18-clean-log': ['Klar', 'ready'],
        'h18-clean-export': ['Klar', 'ready'],
        'h18-clean-menu': ['Under udvikling', 'partial'],
        'h18-clean-theme': ['Under udvikling', 'partial'],
        'h18-clean-header-footer': ['Ikke færdig', 'planned'],
        'h18-clean-vehicles': ['Ikke færdig', 'planned'],
        'h18-clean-vehicle-fields': ['Ikke færdig', 'planned'],
        'h18-clean-events': ['Ikke færdig', 'planned'],
        'h18-clean-gallery': ['Ikke færdig', 'planned'],
        'h18-clean-data': ['Ikke færdig', 'planned']
    };

    function pageFromHref(href) {
        try { return new URL(href, window.location.href).searchParams.get('page') || ''; }
        catch (ignore) { return ''; }
    }

    function badge(label, state) {
        var span = document.createElement('span');
        span.className = 'vd-manager-status vd-manager-status--' + state;
        span.textContent = label;
        span.title = label;
        return span;
    }

    function addMenuStatuses() {
        var root = document.getElementById('toplevel_page_h18-clean-manager');
        if (!root) { return; }
        root.querySelectorAll('.wp-submenu a[href]').forEach(function (link) {
            var page = pageFromHref(link.href);
            var info = STATUS[page];
            if (!info || link.querySelector('.vd-manager-status')) { return; }
            link.appendChild(badge(info[0], info[1]));
        });
    }

    function addDashboardLegend() {
        if (pageFromHref(window.location.href) !== 'h18-clean-manager') { return; }
        var hero = document.querySelector('.h18-manager-hero');
        if (!hero || document.querySelector('.vd-manager-status-legend')) { return; }
        var legend = document.createElement('div');
        legend.className = 'vd-manager-status-legend';
        legend.innerHTML = '<strong>Modulstatus:</strong> <span class="vd-manager-status vd-manager-status--ready">Klar</span> <span class="vd-manager-status vd-manager-status--partial">Under udvikling</span> <span class="vd-manager-status vd-manager-status--planned">Ikke færdig</span>';
        hero.insertAdjacentElement('afterend', legend);
    }

    function collapseCard(card, label) {
        if (!card || card.dataset.vdCollapsed === '1') { return; }
        card.dataset.vdCollapsed = '1';
        var details = document.createElement('details');
        details.className = 'vd-manager-advanced';
        var summary = document.createElement('summary');
        summary.textContent = label;
        details.appendChild(summary);
        while (card.firstChild) { details.appendChild(card.firstChild); }
        card.appendChild(details);
    }

    function rowId(row) {
        var input = row.querySelector('input[name^="item_title["]');
        if (!input) { return ''; }
        var match = String(input.name || '').match(/item_title\[(\d+)\]/);
        return match ? match[1] : '';
    }

    function parentSelect(row) {
        return row.querySelector('select[name^="item_parent["]');
    }

    function orderInput(row) {
        return row.querySelector('input[name^="item_order["]');
    }

    function rowsOf(table) {
        return Array.prototype.slice.call(table.querySelectorAll('tbody > tr'));
    }

    function depthFor(row, byId) {
        var depth = 0;
        var seen = {};
        var current = row;
        while (current && depth < 8) {
            var select = parentSelect(current);
            var parentId = select ? String(select.value || '0') : '0';
            if (!parentId || parentId === '0' || seen[parentId]) { break; }
            seen[parentId] = true;
            current = byId[parentId] || null;
            if (current) { depth += 1; }
        }
        return depth;
    }

    function renumber(table) {
        rowsOf(table).forEach(function (row, index) {
            var input = orderInput(row);
            if (input) { input.value = String(index + 1); }
        });
    }

    function refreshDepth(table) {
        var byId = Object.create(null);
        rowsOf(table).forEach(function (row) {
            var id = rowId(row);
            if (id) { byId[id] = row; }
        });
        rowsOf(table).forEach(function (row) {
            var depth = depthFor(row, byId);
            row.dataset.vdDepth = String(depth);
            var title = row.cells && row.cells[0] ? row.cells[0] : null;
            if (title) { title.style.paddingLeft = (12 + depth * 22) + 'px'; }
        });
    }

    function moveRow(table, row, direction) {
        var rows = rowsOf(table);
        var index = rows.indexOf(row);
        if (index < 0) { return; }
        var select = parentSelect(row);
        var parent = select ? String(select.value || '0') : '0';
        var target = null;
        if (direction < 0) {
            for (var i = index - 1; i >= 0; i -= 1) {
                var ps = parentSelect(rows[i]);
                if ((ps ? String(ps.value || '0') : '0') === parent) { target = rows[i]; break; }
            }
            if (target) { row.parentNode.insertBefore(row, target); }
        } else {
            for (var j = index + 1; j < rows.length; j += 1) {
                var ns = parentSelect(rows[j]);
                if ((ns ? String(ns.value || '0') : '0') === parent) { target = rows[j]; break; }
            }
            if (target) { target.parentNode.insertBefore(row, target.nextSibling); }
        }
        renumber(table);
        refreshDepth(table);
    }

    function indentRow(table, row) {
        var rows = rowsOf(table);
        var index = rows.indexOf(row);
        if (index <= 0) { return; }
        var previous = rows[index - 1];
        var previousId = rowId(previous);
        var select = parentSelect(row);
        if (!select || !previousId) { return; }
        select.value = previousId;
        refreshDepth(table);
    }

    function outdentRow(table, row) {
        var select = parentSelect(row);
        if (!select || !select.value || select.value === '0') { return; }
        var parentId = String(select.value);
        var parentRow = rowsOf(table).find(function (candidate) { return rowId(candidate) === parentId; });
        var parentParent = parentRow ? parentSelect(parentRow) : null;
        select.value = parentParent ? String(parentParent.value || '0') : '0';
        refreshDepth(table);
    }

    function moveDeleteForms(card, table) {
        card.querySelectorAll('form input[name="item_id"]').forEach(function (input) {
            var form = input.closest('form');
            if (!form) { return; }
            var id = String(input.value || '');
            var row = rowsOf(table).find(function (candidate) { return rowId(candidate) === id; });
            var actions = row && row.querySelector('.vd-menu-row-actions');
            if (!actions) { return; }
            var button = form.querySelector('button');
            if (button) {
                button.textContent = 'Slet';
                button.classList.add('button-link-delete');
            }
            actions.appendChild(form);
        });
        Array.prototype.slice.call(card.querySelectorAll('h3')).forEach(function (heading) {
            if ((heading.textContent || '').trim() === 'Slet menupunkt') { heading.style.display = 'none'; }
        });
    }

    function simplifyEditTable(card) {
        var table = card.querySelector('table.h18-manager-table');
        if (!table || table.dataset.vdSimple === '1') { return; }
        table.dataset.vdSimple = '1';
        table.classList.add('vd-simple-menu-table');
        var headRow = table.querySelector('thead tr');
        if (!headRow) { return; }
        [1, 2, 3, 4].forEach(function (index) {
            if (headRow.cells[index]) { headRow.cells[index].classList.add('vd-menu-technical'); }
        });
        var th = document.createElement('th');
        th.textContent = 'Flyt / handlinger';
        headRow.appendChild(th);

        rowsOf(table).forEach(function (row) {
            [1, 2, 3, 4].forEach(function (index) {
                if (row.cells[index]) { row.cells[index].classList.add('vd-menu-technical'); }
            });
            var td = document.createElement('td');
            td.className = 'vd-menu-row-actions';
            [
                ['↑', 'Flyt op', function () { moveRow(table, row, -1); }],
                ['↓', 'Flyt ned', function () { moveRow(table, row, 1); }],
                ['→', 'Gør til undermenu under punktet ovenfor', function () { indentRow(table, row); }],
                ['←', 'Flyt et niveau ud', function () { outdentRow(table, row); }]
            ].forEach(function (cfg) {
                var button = document.createElement('button');
                button.type = 'button';
                button.className = 'button vd-menu-move';
                button.textContent = cfg[0];
                button.title = cfg[1];
                button.setAttribute('aria-label', cfg[1]);
                button.addEventListener('click', cfg[2]);
                td.appendChild(button);
            });
            row.appendChild(td);
        });
        moveDeleteForms(card, table);
        renumber(table);
        refreshDepth(table);
    }

    function simplifyNavigationPage() {
        if (pageFromHref(window.location.href) !== 'h18-clean-menu') { return; }
        var wrap = document.querySelector('.wrap.h18-manager-admin');
        if (!wrap) { return; }
        wrap.classList.add('vd-simple-navigation');
        var description = wrap.querySelector(':scope > .h18-manager-description');
        if (description) { description.textContent = 'Vælg en menu, redigér punkterne og gem. Tekniske indstillinger og versionshistorik ligger under Avanceret.'; }

        var firstTwoCol = wrap.querySelector(':scope > .h18-manager-two-col');
        if (firstTwoCol && firstTwoCol.children[1]) {
            collapseCard(firstTwoCol.children[1], 'Avanceret · Placering i tema');
        }

        Array.prototype.slice.call(wrap.querySelectorAll(':scope > section.h18-manager-card')).forEach(function (card) {
            var heading = card.querySelector(':scope > h2');
            var title = heading ? (heading.textContent || '').trim() : '';
            if (title.indexOf('Redigér:') === 0) {
                simplifyEditTable(card);
                var wpLink = Array.prototype.slice.call(card.querySelectorAll('a.button')).find(function (link) {
                    return (link.textContent || '').indexOf('WordPress Menu-editor') !== -1;
                });
                if (wpLink) { wpLink.classList.add('vd-menu-wordpress-advanced'); }
                var addColumns = card.querySelector('.h18-manager-two-col');
                if (addColumns && addColumns.children[1]) {
                    var custom = addColumns.children[1];
                    var details = document.createElement('details');
                    details.className = 'vd-inline-advanced';
                    var summary = document.createElement('summary');
                    summary.textContent = 'Tilføj eksternt link';
                    details.appendChild(summary);
                    while (custom.firstChild) { details.appendChild(custom.firstChild); }
                    custom.appendChild(details);
                }
            }
            if (title === 'Navigationens versionshistorik') {
                collapseCard(card, 'Avanceret · Versionshistorik og gendannelse');
            }
        });
    }

    function install() {
        addMenuStatuses();
        addDashboardLegend();
        simplifyNavigationPage();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
