(function () {
    'use strict';

    /*
     * Status rule:
     * ready   = the agreed backlog / Definition of Done for this module is complete.
     * partial = usable work exists, but the agreed module scope is not complete.
     * planned = placeholder / not yet implemented to a usable level.
     */
    var STATUS = {
        'h18-clean-manager': ['Under udvikling', 'partial'],
        'h18-clean-editor': ['Under udvikling', 'partial'],
        'h18-clean-pages': ['Under udvikling', 'partial'],
        'h18-clean-backup': ['Under udvikling', 'partial'],
        'h18-clean-updates': ['Klar', 'ready'],
        'h18-clean-log': ['Under udvikling', 'partial'],
        'h18-clean-export': ['Under udvikling', 'partial'],
        'h18-clean-menu': ['Klar', 'ready'],
        'h18-clean-theme': ['Under udvikling', 'partial'],
        'h18-clean-header-footer': ['Klar', 'ready'],
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

    function install() {
        addMenuStatuses();
        addDashboardLegend();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
