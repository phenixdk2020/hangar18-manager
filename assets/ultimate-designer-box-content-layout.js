jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector-target');
    if (!$sections.length || !$inspector.length) {
        return;
    }

    const BOX_LABEL = 'Kasse';
    const PANEL_CLASS = 'h18-ud-box-content-layout';
    let refreshTimer = null;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || '');
    }

    function controls($row, selector) {
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($inspector.find(selector));
        }
        return $result;
    }

    function rowLabel($row) {
        return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
    }

    function isBox($row) {
        return !!($row && $row.length && String($row.attr('data-section-type') || '') === 'container' && rowLabel($row).indexOf(BOX_LABEL) === 0);
    }

    function selectedBox() {
        const $row = activeRows().filter('.is-selected').first();
        return isBox($row) ? $row : $();
    }

    function field($row, name) {
        return controls($row, '[name$="[' + name + ']"]').first();
    }

    function fieldValue($row, name, fallback) {
        const $field = field($row, name);
        if (!$field.length) { return fallback; }
        if ($field.is(':checkbox')) { return $field.is(':checked'); }
        const value = $field.val();
        return value === undefined || value === null || String(value) === '' ? fallback : value;
    }

    function setField($row, name, value) {
        const $all = controls($row, '[name$="[' + name + ']"]');
        if (!$all.length) { return false; }
        $all.each(function () {
            const $field = $(this);
            if ($field.is(':checkbox')) {
                $field.prop('checked', !!value);
            } else {
                $field.val(String(value));
            }
        });
        $all.first().trigger('input').trigger('change');
        return true;
    }

    function directChildCount($row) {
        const key = rowKey($row);
        if (!key) { return 0; }
        let count = 0;
        activeRows().each(function () {
            if (String(controls($(this), '.h18-layout-parent-key').first().val() || '') === key) { count += 1; }
        });
        return count;
    }

    function selectControl(label, name, value, options) {
        const $select = $('<select>', { 'data-box-content-field': name });
        options.forEach(function (entry) {
            $select.append($('<option>', { value: entry[0], text: entry[1], selected: String(entry[0]) === String(value) }));
        });
        return $('<label>', { class: 'h18-ud-box-content-control' }).append($('<strong>', { text: label }), $select);
    }

    function numberControl(label, name, value, min, max) {
        return $('<label>', { class: 'h18-ud-box-content-control' }).append(
            $('<strong>', { text: label }),
            $('<span>', { class: 'h18-ud-box-content-number' }).append(
                $('<input>', { type: 'number', min: min, max: max, step: 1, value: parseInt(value, 10) || 0, 'data-box-content-field': name }),
                $('<em>', { text: 'px' })
            )
        );
    }

    function renderPanel() {
        const $row = selectedBox();
        $inspector.find('.' + PANEL_CLASS).remove();
        if (!$row.length) { return; }

        const count = directChildCount($row);
        const direction = String(fieldValue($row, 'LayoutDirection', 'Column'));
        const $panel = $('<div>', { class: 'h18-section-module-box ' + PANEL_CLASS });
        $panel.append(
            $('<h4>', { text: 'Indholdslayout i kassen' }),
            $('<p>', {
                class: 'description',
                text: 'Kassen kan indeholde flere elementer. Styr hvordan Billede, Tekst, Knap osv. placeres inde i netop denne kasse.'
            }),
            $('<div>', { class: 'h18-ud-box-content-summary' }).append(
                $('<strong>', { text: count + ' element' + (count === 1 ? '' : 'er') + ' i kassen' }),
                $('<span>', { text: direction === 'Row' ? 'Vandret på desktop' : 'Lodret på desktop' })
            )
        );

        const $grid = $('<div>', { class: 'h18-ud-box-content-grid' });
        $grid.append(
            selectControl('Retning desktop', 'LayoutDirection', direction, [['Column', 'Lodret'], ['Row', 'Vandret']]),
            selectControl('Justering', 'LayoutAlign', fieldValue($row, 'LayoutAlign', 'Stretch'), [['Stretch', 'Stræk'], ['Start', 'Start'], ['Center', 'Centrér'], ['End', 'Slut']]),
            selectControl('Fordeling', 'LayoutJustify', fieldValue($row, 'LayoutJustify', 'Start'), [['Start', 'Start'], ['Center', 'Centrér'], ['End', 'Slut'], ['SpaceBetween', 'Fordel mellemrum']]),
            numberControl('Intern afstand desktop', 'LayoutGapPx', fieldValue($row, 'LayoutGapPx', 12), 0, 120),
            numberControl('Intern afstand mobil', 'MobileLayoutGapPx', fieldValue($row, 'MobileLayoutGapPx', 10), 0, 80)
        );
        $panel.append($grid);
        $panel.append(
            $('<label>', { class: 'h18-ud-box-content-check' }).append(
                $('<input>', { type: 'checkbox', checked: !!fieldValue($row, 'LayoutWrap', true), 'data-box-content-field': 'LayoutWrap' }),
                $('<span>', { text: 'Tillad wrap hvis elementerne ikke kan være på samme linje' })
            ),
            $('<label>', { class: 'h18-ud-box-content-check' }).append(
                $('<input>', { type: 'checkbox', checked: !!fieldValue($row, 'MobileLayoutStack', true), 'data-box-content-field': 'MobileLayoutStack' }),
                $('<span>', { text: 'Stak indhold lodret på mobil' })
            ),
            $('<p>', { class: 'description', text: 'Til almindeligt Billede + Tekst anbefales lodret på mobil. Tabel er beregnet til tabeldata, ikke side-layout.' })
        );
        $inspector.append($panel);
    }

    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(renderPanel, typeof delay === 'number' ? delay : 30);
    }

    $(document).on('input change', '.' + PANEL_CLASS + ' [data-box-content-field]', function () {
        const $row = selectedBox();
        if (!$row.length) { return; }
        const name = String($(this).attr('data-box-content-field') || '');
        const value = $(this).is(':checkbox') ? $(this).is(':checked') : $(this).val();
        if (name && setField($row, name, value)) {
            scheduleRefresh(20);
        }
    });

    // v0.8.14: this addon is Inspector-only. Kasse creation, drag/drop,
    // defaults and parent assignment are owned exclusively by the direct
    // nesting runtime. The former delayed post-drop default writer was removed
    // because its synthetic input/change events created duplicate history steps.
    $(document).on('click', '.h18-page-section-header, .h18-page-section-edit, .h18-ud-auto-box-tile, .h18-ud-box-child-chip', function () {
        scheduleRefresh(40);
    });
    $(document).on('change input', '.h18-layout-parent-key, .h18-section-navigator-label', function () { scheduleRefresh(30); });

    scheduleRefresh(80);
});
