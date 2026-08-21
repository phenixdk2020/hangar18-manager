jQuery(function ($) {
    'use strict';

    const root = document.getElementById('h18-page-sections-sortable');
    if (!root) {
        return;
    }

    const STORAGE_KEY = 'hangar18CanvasPanelCollapseV0839';
    const STORAGE_VERSION = 2;
    const DEFAULT_STATE = {
        direct: true,
        image: true
    };
    const configs = [
        {
            kind: 'direct',
            selector: '.h18-page-section-row.is-selected > .h18-canvas-preview > .h18-canvas-direct-controls',
            titleSelector: ':scope > .h18-canvas-direct-title',
            label: 'Direkte design'
        },
        {
            kind: 'image',
            selector: '.h18-page-section-row.is-selected .h18-canvas-image-tools',
            titleSelector: ':scope > strong:first-of-type',
            label: 'Billede'
        }
    ];

    let state = readState();
    let decorateFrame = 0;

    function normalizedState(parsed) {
        return {
            __defaultsVersion: STORAGE_VERSION,
            direct: typeof parsed.direct === 'boolean' ? parsed.direct : DEFAULT_STATE.direct,
            image: typeof parsed.image === 'boolean' ? parsed.image : DEFAULT_STATE.image
        };
    }

    function readState() {
        try {
            const raw = window.localStorage ? window.localStorage.getItem(STORAGE_KEY) : '';
            const parsed = raw ? JSON.parse(raw) : {};
            if (!parsed || typeof parsed !== 'object') {
                return normalizedState({});
            }

            // v0.8.40 UX migration: the two canvas configuration panels now
            // start collapsed by default. Ignore the old v0.8.39 open/closed
            // preference once, then persist explicit user choices normally.
            if (parseInt(parsed.__defaultsVersion, 10) !== STORAGE_VERSION) {
                return normalizedState({});
            }
            return normalizedState(parsed);
        } catch (error) {
            return normalizedState({});
        }
    }

    function writeState() {
        try {
            if (window.localStorage) {
                window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
            }
        } catch (error) {
            // Browser-local convenience only; editor functionality must not depend on storage.
        }
    }

    function panelLabel(kind) {
        const config = configs.find(function (item) { return item.kind === kind; });
        return config ? config.label : 'Panel';
    }

    function syncPanel($panel, kind) {
        const collapsed = state[kind] !== false;
        const label = panelLabel(kind);
        $panel.toggleClass('h18-canvas-panel-collapsed', collapsed)
            .attr('data-h18-canvas-panel-collapsed', collapsed ? '1' : '0');

        const $toggle = $panel.children('.h18-canvas-panel-collapse-toggle').first();
        $toggle
            .attr('aria-expanded', collapsed ? 'false' : 'true')
            .attr('aria-label', collapsed ? ('Udvid ' + label) : ('Minimér ' + label))
            .attr('title', collapsed ? ('Udvid ' + label) : ('Minimér ' + label))
            .text(collapsed ? '+' : '−');
    }

    function decoratePanel(panel, config) {
        const $panel = $(panel);
        if (!$panel.length) {
            return;
        }

        if ($panel.attr('data-h18-canvas-panel-collapse-ready') !== '1') {
            $panel.attr('data-h18-canvas-panel-collapse-ready', '1')
                .attr('data-h18-canvas-panel-kind', config.kind)
                .addClass('h18-canvas-panel-collapsible');

            let $title = $panel.find(config.titleSelector).first();
            if (!$title.length) {
                $title = $('<strong>', {
                    class: 'h18-canvas-panel-collapse-title',
                    text: config.label
                });
                $panel.prepend($title);
            } else {
                $title.addClass('h18-canvas-panel-collapse-title');
            }

            const $toggle = $('<button>', {
                type: 'button',
                class: 'h18-canvas-panel-collapse-toggle',
                'data-h18-canvas-panel-toggle': config.kind
            });
            $title.after($toggle);
        }

        syncPanel($panel, config.kind);
    }

    function decoratePanels() {
        decorateFrame = 0;
        configs.forEach(function (config) {
            $(config.selector).each(function () {
                decoratePanel(this, config);
            });
        });
        document.documentElement.setAttribute('data-h18-canvas-panel-collapse-runtime', '0.8.40');
    }

    function scheduleDecorate() {
        if (decorateFrame) {
            return;
        }
        decorateFrame = window.requestAnimationFrame(decoratePanels);
    }

    $(document).on('click', '.h18-canvas-panel-collapse-toggle', function (event) {
        event.preventDefault();
        event.stopPropagation();

        const $button = $(this);
        const $panel = $button.closest('.h18-canvas-panel-collapsible');
        const kind = String($button.attr('data-h18-canvas-panel-toggle') || $panel.attr('data-h18-canvas-panel-kind') || '');
        if (!kind) {
            return;
        }

        state[kind] = !($panel.attr('data-h18-canvas-panel-collapsed') === '1');
        writeState();
        syncPanel($panel, kind);
        $button.trigger('focus');
    });

    const observer = new MutationObserver(function () {
        scheduleDecorate();
    });
    observer.observe(root, {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class']
    });

    decoratePanels();
});
