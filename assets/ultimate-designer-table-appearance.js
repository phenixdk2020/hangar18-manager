jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector-target');
    if (!$sections.length || !$inspector.length) {
        return;
    }

    const prefs = new Map();
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

    function contentField($row) {
        return controls($row, '[name$="[Content]"]').first();
    }

    function selectedTableRow() {
        const $row = activeRows().filter('.is-selected').first();
        if (!$row.length || String($row.attr('data-section-type') || '') !== 'html') { return $(); }
        const raw = String(contentField($row).val() || '');
        return raw.includes('data-h18-table="1"') ? $row : $();
    }

    function tableDocument(raw) {
        const template = document.createElement('template');
        template.innerHTML = String(raw || '');
        const wrapper = template.content.querySelector('[data-h18-table="1"]');
        return { template: template, wrapper: wrapper };
    }

    function borderWidthFromRaw(raw) {
        const parsed = tableDocument(raw);
        if (!parsed.wrapper) { return 1; }
        const explicit = parseInt(parsed.wrapper.getAttribute('data-h18-table-border-width'), 10);
        if (Number.isFinite(explicit)) { return Math.max(0, Math.min(8, explicit)); }
        if (parsed.wrapper.getAttribute('data-h18-table-border-hidden') === '1') { return 0; }
        const cell = parsed.wrapper.querySelector('th,td');
        if (cell && cell.style && String(cell.style.border || '').startsWith('0')) { return 0; }
        return 1;
    }

    function borderColor(wrapper) {
        const value = String(wrapper.getAttribute('data-h18-table-border') || '#dcdcde').trim();
        return /^#[0-9a-f]{3,8}$/i.test(value) ? value : '#dcdcde';
    }

    function applyBorderWidthToRaw(raw, width) {
        const parsed = tableDocument(raw);
        if (!parsed.wrapper) { return raw; }
        width = Math.max(0, Math.min(8, parseInt(width, 10) || 0));
        const color = borderColor(parsed.wrapper);
        parsed.wrapper.setAttribute('data-h18-table-border-width', String(width));
        parsed.wrapper.setAttribute('data-h18-table-border-hidden', width === 0 ? '1' : '0');
        parsed.wrapper.querySelectorAll('th,td').forEach(function (cell) {
            cell.style.border = width === 0 ? '0 solid transparent' : width + 'px solid ' + color;
        });
        return parsed.template.innerHTML;
    }

    function writeWidth($row, width) {
        const $content = contentField($row);
        if (!$content.length) { return; }
        const key = rowKey($row);
        width = Math.max(0, Math.min(8, parseInt(width, 10) || 0));
        prefs.set(key, width);
        const raw = String($content.val() || '');
        const updated = applyBorderWidthToRaw(raw, width);
        if (updated !== raw) {
            $content.val(updated).trigger('input').trigger('change');
        }
        $row.attr('data-h18-table-border-width', String(width));
        controls($row, '.h18-ud-table-canvas').find('th,td').css('border-width', width + 'px').css('border-style', width === 0 ? 'none' : 'solid');
        refreshPanel($row);
    }

    function ensurePreference($row) {
        const key = rowKey($row);
        if (!key) { return 1; }
        if (!prefs.has(key)) {
            prefs.set(key, borderWidthFromRaw(String(contentField($row).val() || '')));
        }
        return prefs.get(key);
    }

    function refreshPanel($row) {
        if (!$row || !$row.length) { return; }
        const $panel = controls($row, '.h18-ud-table-editor').first();
        if (!$panel.length) { return; }
        let $appearance = $panel.find('.h18-ud-table-border-appearance');
        if (!$appearance.length) {
            $appearance = $('<div>', { class: 'h18-ud-table-border-appearance' }).append(
                $('<label>', { class: 'h18-ud-table-border-control' }).append(
                    $('<strong>', { text: 'Kantbredde' }),
                    $('<span>').append(
                        $('<input>', { type: 'number', min: 0, max: 8, step: 1, 'data-h18-table-border-width': '1' }),
                        $('<em>', { text: 'px' })
                    )
                ),
                $('<button>', { type: 'button', class: 'button h18-ud-table-hide-borders', text: 'Skjul kanter' }),
                $('<p>', { class: 'description', text: '0 px gør alle celle- og tabelkanter helt usynlige. Brug tabellen til tabeldata; brug Kasse/Flex/Grid til side-layout.' })
            );
            $panel.find('.h18-ud-table-settings').after($appearance);
        }
        const width = ensurePreference($row);
        $appearance.find('[data-h18-table-border-width]').val(String(width));
        $appearance.find('.h18-ud-table-hide-borders').text(width === 0 ? 'Vis kanter (1 px)' : 'Skjul kanter');
        $row.attr('data-h18-table-border-width', String(width));
        controls($row, '.h18-ud-table-canvas').find('th,td').css('border-width', width + 'px').css('border-style', width === 0 ? 'none' : 'solid');
    }

    function refreshSelected() {
        const $row = selectedTableRow();
        if ($row.length) { refreshPanel($row); }
    }

    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(refreshSelected, typeof delay === 'number' ? delay : 30);
    }

    $(document).on('input change', '[data-h18-table-border-width]', function () {
        const $row = selectedTableRow();
        if ($row.length) { writeWidth($row, $(this).val()); }
    });

    $(document).on('click', '.h18-ud-table-hide-borders', function (event) {
        event.preventDefault();
        const $row = selectedTableRow();
        if (!$row.length) { return; }
        writeWidth($row, ensurePreference($row) === 0 ? 1 : 0);
    });

    $(document).on('input change', '.h18-ud-table-editor [data-table-setting], .h18-ud-table-cell', function () {
        const $row = selectedTableRow();
        if (!$row.length) { return; }
        const width = ensurePreference($row);
        window.setTimeout(function () { writeWidth($row, width); }, 0);
    });

    $(document).on('click', '.h18-ud-table-editor [data-table-action]', function () {
        const $row = selectedTableRow();
        if (!$row.length) { return; }
        const width = ensurePreference($row);
        window.setTimeout(function () { writeWidth($row, width); }, 20);
    });

    $(document).on('click', '.h18-page-section-header, .h18-page-section-edit', function () { scheduleRefresh(50); });
    scheduleRefresh(100);
});
