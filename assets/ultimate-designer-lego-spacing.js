jQuery(function ($) {
    'use strict';

    const config = window.H18LegoSpacing || {};
    const $form = $('#h18-page-editor-form');
    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector');
    if (!$form.length || !$sections.length || !$inspector.length) {
        return;
    }

    const PANEL_ID = 'h18-ud-lego-spacing-panel';
    const ATTRS = {
        MarginXPx: 'data-h18-lego-margin-x',
        MarginYPx: 'data-h18-lego-margin-y',
        MobileMarginXPx: 'data-h18-lego-mobile-margin-x',
        MobileMarginYPx: 'data-h18-lego-mobile-margin-y',
        GapXPx: 'data-h18-lego-gap-x',
        GapYPx: 'data-h18-lego-gap-y',
        MobileGapXPx: 'data-h18-lego-mobile-gap-x',
        MobileGapYPx: 'data-h18-lego-mobile-gap-y'
    };
    const desktopMax = Math.max(0, parseInt(config.limits && config.limits.desktop, 10) || 160);
    const mobileMax = Math.max(0, parseInt(config.limits && config.limits.mobile, 10) || 120);
    let refreshTimer = null;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($('#h18-page-inspector-target').find(selector));
        }
        return $result;
    }

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || $row.attr('data-key') || '');
    }

    function rowType($row) {
        return String($row.attr('data-section-type') || '');
    }

    function isLayoutRow($row) {
        return ['container', 'flex', 'grid'].indexOf(rowType($row)) !== -1;
    }

    function pageSlug() {
        return String($form.find('[name="page_slug"]').first().val() || '').trim();
    }

    function clamp(value, max, fallback) {
        const parsed = parseInt(value, 10);
        if (!Number.isFinite(parsed)) { return fallback; }
        return Math.max(0, Math.min(max, parsed));
    }

    function legacyNumber($row, suffix, fallback) {
        const $field = controls($row, '[name$="[' + suffix + ']"]').first();
        if (!$field.length) { return fallback; }
        return clamp($field.val(), suffix.indexOf('Mobile') === 0 ? mobileMax : desktopMax, fallback);
    }

    function defaultState($row) {
        const desktopGap = legacyNumber($row, 'LayoutGapPx', 16);
        const mobileGap = legacyNumber($row, 'MobileLayoutGapPx', 12);
        return {
            MarginXPx: 0,
            MarginYPx: 0,
            MobileMarginXPx: 0,
            MobileMarginYPx: 0,
            GapXPx: desktopGap,
            GapYPx: desktopGap,
            MobileGapXPx: mobileGap,
            MobileGapYPx: mobileGap
        };
    }

    function stateForRow($row) {
        const state = defaultState($row);
        Object.keys(ATTRS).forEach(function (name) {
            const attr = ATTRS[name];
            if ($row.is('[' + attr + ']')) {
                const max = name.indexOf('Mobile') === 0 ? mobileMax : desktopMax;
                state[name] = clamp($row.attr(attr), max, state[name]);
            }
        });
        return state;
    }

    function hasMaterializedState($row) {
        return Object.keys(ATTRS).some(function (name) {
            return $row.is('[' + ATTRS[name] + ']');
        });
    }

    function applyRowStyles($row) {
        if (!$row || !$row.length || !hasMaterializedState($row)) { return; }
        const state = stateForRow($row);
        const node = $row.get(0);
        if (!node) { return; }
        node.style.setProperty('--h18-lego-margin-x', state.MarginXPx + 'px');
        node.style.setProperty('--h18-lego-margin-y', state.MarginYPx + 'px');
        node.style.setProperty('--h18-lego-mobile-margin-x', state.MobileMarginXPx + 'px');
        node.style.setProperty('--h18-lego-mobile-margin-y', state.MobileMarginYPx + 'px');
        node.style.setProperty('--h18-lego-gap-x', state.GapXPx + 'px');
        node.style.setProperty('--h18-lego-gap-y', state.GapYPx + 'px');
        node.style.setProperty('--h18-lego-mobile-gap-x', state.MobileGapXPx + 'px');
        node.style.setProperty('--h18-lego-mobile-gap-y', state.MobileGapYPx + 'px');
        $row.attr('data-h18-lego-spacing', '1');
    }

    function materializeState($row, state) {
        Object.keys(ATTRS).forEach(function (name) {
            const max = name.indexOf('Mobile') === 0 ? mobileMax : desktopMax;
            const fallback = defaultState($row)[name];
            $row.attr(ATTRS[name], String(clamp(state[name], max, fallback)));
        });
        applyRowStyles($row);
    }

    function storedSections() {
        const pages = config.pages && typeof config.pages === 'object' ? config.pages : {};
        const page = pages[pageSlug()] && typeof pages[pageSlug()] === 'object' ? pages[pageSlug()] : {};
        return page.Sections && typeof page.Sections === 'object' ? page.Sections : {};
    }

    function hydrateStoredState() {
        const stored = storedSections();
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (!key || !stored[key] || typeof stored[key] !== 'object') { return; }
            const state = defaultState($row);
            Object.keys(ATTRS).forEach(function (name) {
                if (Object.prototype.hasOwnProperty.call(stored[key], name)) {
                    state[name] = stored[key][name];
                }
            });
            materializeState($row, state);
        });
    }

    function selectedRow() {
        return activeRows().filter('.is-selected').first();
    }

    function numberControl(label, field, value, max, help) {
        const $label = $('<label>', { class: 'h18-ud-lego-control' });
        $label.append($('<strong>', { text: label }));
        $label.append(
            $('<span>', { class: 'h18-ud-lego-number' }).append(
                $('<input>', {
                    type: 'number',
                    min: 0,
                    max: max,
                    step: 1,
                    value: value,
                    'data-h18-lego-field': field
                }),
                $('<em>', { text: 'px' })
            )
        );
        if (help) { $label.append($('<small>', { text: help })); }
        return $label;
    }

    function deviceGroup(title, state, mobile, layout) {
        const prefix = mobile ? 'Mobile' : '';
        const max = mobile ? mobileMax : desktopMax;
        const $group = $('<fieldset>', { class: 'h18-ud-lego-device' });
        $group.append($('<legend>', { text: title }));
        const $grid = $('<div>', { class: 'h18-ud-lego-grid' });
        $grid.append(
            numberControl('Element X', prefix + 'MarginXPx', state[prefix + 'MarginXPx'], max, 'Venstre + højre'),
            numberControl('Element Y', prefix + 'MarginYPx', state[prefix + 'MarginYPx'], max, 'Over + under')
        );
        if (layout) {
            $grid.append(
                numberControl('Indhold X', prefix + 'GapXPx', state[prefix + 'GapXPx'], max, 'Mellem kolonner'),
                numberControl('Indhold Y', prefix + 'GapYPx', state[prefix + 'GapYPx'], max, 'Mellem rækker')
            );
        }
        $group.append($grid);
        return $group;
    }

    function renderPanel() {
        $('#' + PANEL_ID).remove();
        const $row = selectedRow();
        if (!$row.length) { return; }

        const state = stateForRow($row);
        const layout = isLayoutRow($row);
        const $panel = $('<section>', {
            id: PANEL_ID,
            class: 'h18-section-module-box h18-canvas-direct-controls h18-ud-lego-spacing-panel',
            'data-h18-lego-key': rowKey($row)
        });
        $panel.append(
            $('<div>', { class: 'h18-ud-lego-heading' }).append(
                $('<div>').append(
                    $('<h4>', { text: 'LEGO-afstand X / Y' }),
                    $('<p>', { class: 'description', text: 'Styr luft omkring elementet separat vandret og lodret.' })
                ),
                $('<span>', { class: 'h18-ud-lego-badge', text: 'v0.8.24' })
            ),
            deviceGroup('Desktop', state, false, layout),
            deviceGroup('Mobil', state, true, layout)
        );
        if (layout) {
            $panel.append($('<p>', {
                class: 'description h18-ud-lego-note',
                text: 'For Kasse/Flex/Auto-kasser er Indhold X/Y afstanden mellem klodserne. Eksisterende LayoutGap bruges automatisk som startværdi.'
            }));
        }
        $inspector.append($panel);
    }

    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(function () {
            activeRows().each(function () { applyRowStyles($(this)); });
            renderPanel();
        }, typeof delay === 'number' ? delay : 30);
    }

    $(document).on('input change', '#' + PANEL_ID + ' [data-h18-lego-field]', function () {
        const $row = selectedRow();
        if (!$row.length) { return; }
        const field = String($(this).attr('data-h18-lego-field') || '');
        if (!Object.prototype.hasOwnProperty.call(ATTRS, field)) { return; }
        const state = stateForRow($row);
        const max = field.indexOf('Mobile') === 0 ? mobileMax : desktopMax;
        state[field] = clamp($(this).val(), max, state[field]);
        materializeState($row, state);
    });

    function appendSavePayload() {
        $form.find('[data-h18-lego-submit="1"]').remove();
        let index = 0;
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (!key) { return; }
            const state = stateForRow($row);
            const values = $.extend({ SectionKey: key }, state);
            Object.keys(values).forEach(function (name) {
                $('<input>', {
                    type: 'hidden',
                    name: 'h18_lego_spacing[' + index + '][' + name + ']',
                    value: values[name],
                    'data-h18-lego-submit': '1'
                }).appendTo($form);
            });
            index += 1;
        });
    }

    $form.on('submit.h18LegoSpacing', appendSavePayload);

    $(document).on(
        'click',
        '.h18-page-section-header,.h18-page-section-edit,.h18-v0811-edit-child,.h18-ud-auto-box-tile,.h18-ud-box-child-chip',
        function () { scheduleRefresh(40); }
    );

    const observer = new MutationObserver(function () { scheduleRefresh(50); });
    observer.observe($sections.get(0), {
        childList: true,
        subtree: true,
        attributes: true,
        attributeFilter: ['class', 'data-h18-lego-margin-x', 'data-h18-lego-margin-y', 'data-h18-lego-gap-x', 'data-h18-lego-gap-y']
    });

    // This runs before the legacy admin.js ready callback because the controller
    // is registered from IntegrationAdminBootstrap before Hangar18_Manager. That
    // means persisted LEGO attributes are part of the initial history snapshot.
    hydrateStoredState();
    activeRows().each(function () { applyRowStyles($(this)); });
    scheduleRefresh(80);

    document.documentElement.setAttribute('data-h18-lego-spacing-runtime', '0.8.24');
    window.__h18LegoSpacingV0824 = {
        version: '0.8.24',
        stateForKey: function (key) {
            const $row = activeRows().filter(function () { return rowKey($(this)) === String(key || ''); }).first();
            return $row.length ? stateForRow($row) : null;
        },
        materialized: function (key) {
            const $row = activeRows().filter(function () { return rowKey($(this)) === String(key || ''); }).first();
            return $row.length ? hasMaterializedState($row) : false;
        }
    };
});
