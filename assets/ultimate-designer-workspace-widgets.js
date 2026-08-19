jQuery(function ($) {
    'use strict';

    const $workspace = $('.h18-pages-admin .h18-visual-builder').first();
    if (!$workspace.length) {
        return;
    }

    const $palette = $workspace.children('.h18-builder-palette').first();
    const $inspector = $workspace.children('.h18-builder-inspector').first();
    if (!$palette.length || !$inspector.length) {
        return;
    }

    const STORAGE_KEY = 'hangar18UltimateDesignerWorkspaceWidgetsV0816';
    const desktopQuery = window.matchMedia('(min-width: 1181px)');
    let state = { left: false, right: false };

    function readState() {
        try {
            const raw = window.localStorage ? window.localStorage.getItem(STORAGE_KEY) : '';
            const parsed = raw ? JSON.parse(raw) : null;
            if (parsed && typeof parsed === 'object') {
                state.left = parsed.left === true;
                state.right = parsed.right === true;
            }
        } catch (error) {
            state = { left: false, right: false };
        }
    }

    function writeState() {
        try {
            if (window.localStorage) {
                window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
            }
        } catch (error) {}
    }

    function widgetDefinition(side) {
        if (side === 'left') {
            return {
                title: 'Elementer / funktioner',
                collapseLabel: 'Fold Elementer og Funktioner ind',
                expandLabel: 'Fold Elementer og Funktioner ud',
                collapseIcon: 'dashicons-arrow-left-alt2',
                expandIcon: 'dashicons-arrow-right-alt2'
            };
        }
        return {
            title: 'Inspector',
            collapseLabel: 'Fold Inspector ind',
            expandLabel: 'Fold Inspector ud',
            collapseIcon: 'dashicons-arrow-right-alt2',
            expandIcon: 'dashicons-arrow-left-alt2'
        };
    }

    function installWidget($panel, side) {
        if ($panel.attr('data-h18-workspace-widget') === side) {
            return;
        }

        const def = widgetDefinition(side);
        $panel.attr('data-h18-workspace-widget', side);

        const $toolbar = $('<div>', {
            class: 'h18-workspace-widget-toolbar',
            'data-h18-workspace-toolbar': side
        }).append(
            $('<span>', { class: 'h18-workspace-widget-toolbar-label', text: def.title }),
            $('<button>', {
                type: 'button',
                class: 'button button-small h18-workspace-widget-collapse',
                'data-h18-workspace-collapse': side,
                'aria-label': def.collapseLabel,
                title: def.collapseLabel,
                'aria-expanded': 'true'
            }).append($('<span>', {
                class: 'dashicons ' + def.collapseIcon,
                'aria-hidden': 'true'
            }))
        );

        const $rail = $('<button>', {
            type: 'button',
            class: 'h18-workspace-widget-rail',
            'data-h18-workspace-expand': side,
            'aria-label': def.expandLabel,
            title: def.expandLabel,
            'aria-expanded': 'false'
        }).append(
            $('<span>', { class: 'dashicons ' + def.expandIcon, 'aria-hidden': 'true' }),
            $('<span>', { class: 'h18-workspace-widget-rail-label', text: def.title })
        );

        $panel.prepend($toolbar);
        $panel.append($rail);
    }

    function applyPanelState(side, collapsed, persist) {
        const isDesktop = desktopQuery.matches;
        const effectiveCollapsed = isDesktop && collapsed;
        const $panel = side === 'left' ? $palette : $inspector;
        const workspaceClass = side === 'left' ? 'h18-workspace-left-collapsed' : 'h18-workspace-right-collapsed';

        $workspace.toggleClass(workspaceClass, effectiveCollapsed);
        $panel.toggleClass('is-workspace-collapsed', effectiveCollapsed);
        $panel.attr('data-h18-workspace-collapsed', effectiveCollapsed ? '1' : '0');
        $panel.find('[data-h18-workspace-collapse="' + side + '"]')
            .attr('aria-expanded', effectiveCollapsed ? 'false' : 'true');
        $panel.find('[data-h18-workspace-expand="' + side + '"]')
            .attr('aria-expanded', effectiveCollapsed ? 'true' : 'false');

        if (persist) {
            state[side] = !!collapsed;
            writeState();
        }
    }

    function applyStoredState() {
        applyPanelState('left', state.left, false);
        applyPanelState('right', state.right, false);
    }

    function notifyWorkspaceResize() {
        window.setTimeout(function () {
            $(window).trigger('resize');
            $(document).trigger('h18:workspace-widgets-changed');
        }, 80);
    }

    installWidget($palette, 'left');
    installWidget($inspector, 'right');
    readState();
    applyStoredState();

    $(document).on('click', '[data-h18-workspace-collapse]', function (event) {
        event.preventDefault();
        const side = String($(this).attr('data-h18-workspace-collapse') || '');
        if (side !== 'left' && side !== 'right') { return; }
        applyPanelState(side, true, true);
        notifyWorkspaceResize();
    });

    $(document).on('click', '[data-h18-workspace-expand]', function (event) {
        event.preventDefault();
        const side = String($(this).attr('data-h18-workspace-expand') || '');
        if (side !== 'left' && side !== 'right') { return; }
        applyPanelState(side, false, true);
        notifyWorkspaceResize();
    });

    function handleBreakpointChange() {
        applyStoredState();
        notifyWorkspaceResize();
    }

    if (typeof desktopQuery.addEventListener === 'function') {
        desktopQuery.addEventListener('change', handleBreakpointChange);
    } else if (typeof desktopQuery.addListener === 'function') {
        desktopQuery.addListener(handleBreakpointChange);
    }
});
