jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $palette = $('.h18-builder-palette-list').first();
    if (!$sections.length || !$palette.length) {
        return;
    }

    const AUTO_LABEL = 'Auto-kasser';
    const BOX_LABEL = 'Kasse';
    let pendingTool = '';
    let pendingKeys = new Set();
    let pendingDropTargetKey = '';

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        // The legacy editor physically moves the selected row's body into the
        // Inspector. The source row keeps .is-selected, so include Inspector
        // controls only for that exact row. This avoids leaking values between
        // elements while keeping Auto-kasser/Table compatible with Inspector.
        if ($row.hasClass('is-selected')) {
            $result = $result.add($('#h18-page-inspector-target').find(selector));
        }
        return $result;
    }

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || '');
    }

    function rowLabel($row) {
        return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
    }

    function rowType($row) {
        return String($row.attr('data-section-type') || '');
    }

    function parentKey($row) {
        return String(controls($row, '.h18-layout-parent-key').first().val() || '');
    }

    function rowByKey(key) {
        key = String(key || '');
        return activeRows().filter(function () { return rowKey($(this)) === key; }).first();
    }

    function snapshotKeys() {
        const result = new Set();
        activeRows().each(function () {
            const key = rowKey($(this));
            if (key) { result.add(key); }
        });
        return result;
    }

    function findNewRow(beforeKeys, type) {
        let $match = $();
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (key && !beforeKeys.has(key) && (!type || rowType($row) === type)) {
                $match = $row;
            }
        });
        return $match;
    }

    function setField($row, suffix, value) {
        const $field = controls($row, '[name$="[' + suffix + ']"]').first();
        if (!$field.length) { return; }
        if ($field.is(':checkbox')) {
            $field.prop('checked', !!value).trigger('change');
        } else {
            $field.val(String(value)).trigger('input').trigger('change');
        }
    }

    function setNavigatorLabel($row, label) {
        const $field = controls($row, '.h18-section-navigator-label').first();
        if ($field.length) {
            $field.val(label).trigger('input').trigger('change');
        }
    }

    function setParent($row, key) {
        const $hidden = controls($row, '.h18-layout-parent-key').first();
        const $select = controls($row, '.h18-layout-parent-select').first();
        if ($hidden.length) {
            $hidden.val(String(key || '')).trigger('change');
        }
        if ($select.length) {
            $select.val(String(key || '')).trigger('change');
        }
    }

    function isAutoRow($row) {
        return !!($row && $row.length && rowType($row) === 'grid' && rowLabel($row) === AUTO_LABEL);
    }

    function isBox($row) {
        return !!($row && $row.length && rowType($row) === 'container' && rowLabel($row).indexOf(BOX_LABEL) === 0);
    }

    function autoParentFor($row) {
        const parent = rowByKey(parentKey($row));
        return isAutoRow(parent) ? parent : $();
    }

    function syncOneAutoRow($row) {
        if (!isAutoRow($row)) { return; }
        const key = rowKey($row);
        let count = 0;
        activeRows().each(function () {
            const $child = $(this);
            if (parentKey($child) === key) { count += 1; }
        });
        const columns = Math.max(1, Math.min(6, count || 1));
        const $desktop = controls($row, '[name$="[LayoutColumns]"]').first();
        if ($desktop.length && String($desktop.val()) !== String(columns)) {
            $desktop.val(String(columns)).trigger('input').trigger('change');
        }
        const $mobile = controls($row, '[name$="[MobileLayoutColumns]"]').first();
        if ($mobile.length && !String($mobile.val() || '').trim()) {
            $mobile.val('1').trigger('change');
        }
        $row.attr('data-h18-auto-box-count', String(count));
    }

    function syncAutoRows() {
        activeRows().each(function () { syncOneAutoRow($(this)); });
    }

    function configureAutoRow($row) {
        if (!$row.length) { return; }
        setNavigatorLabel($row, AUTO_LABEL);
        setField($row, 'Title', '');
        setField($row, 'Content', '');
        setField($row, 'LayoutColumns', 1);
        setField($row, 'MobileLayoutColumns', 1);
        setField($row, 'LayoutGapPx', 16);
        setField($row, 'MobileLayoutGapPx', 12);
        setField($row, 'LayoutAlign', 'Stretch');
        $row.attr('data-h18-auto-box-row', '1');
        syncOneAutoRow($row);
    }

    function configureBox($row) {
        if (!$row.length) { return; }
        setNavigatorLabel($row, BOX_LABEL);
        setField($row, 'Title', '');
        setField($row, 'Content', '');
        setField($row, 'PaddingPx', 20);
        setField($row, 'HorizontalPaddingPx', 20);
        setField($row, 'MobilePaddingPx', 16);
        setField($row, 'MobileHorizontalPaddingPx', 16);
        $row.attr('data-h18-box', '1');
    }

    function createStandard(type, callback) {
        const $button = $palette.find('.h18-builder-palette-item[data-section-type="' + type + '"]').not('[data-h18-layout-tool]').first();
        if (!$button.length) { return; }
        const before = snapshotKeys();
        $button.trigger('click');
        window.setTimeout(function () {
            const $row = findNewRow(before, type);
            if ($row.length && typeof callback === 'function') { callback($row); }
        }, 30);
    }

    function createInitialBox($autoRow) {
        createStandard('container', function ($box) {
            configureBox($box);
            setParent($box, rowKey($autoRow));
            syncOneAutoRow($autoRow);
        });
    }

    function createAutoParentForBoxes($existingBox, $newBox) {
        createStandard('grid', function ($grid) {
            configureAutoRow($grid);
            const key = rowKey($grid);
            setParent($existingBox, key);
            setParent($newBox, key);
            syncOneAutoRow($grid);
        });
    }

    function placeNewBox($box, targetKey) {
        const $target = rowByKey(targetKey);
        if (!$target.length) {
            syncAutoRows();
            return;
        }
        if (isAutoRow($target)) {
            setParent($box, rowKey($target));
            syncOneAutoRow($target);
            return;
        }
        const $targetAuto = autoParentFor($target);
        if ($targetAuto.length) {
            setParent($box, rowKey($targetAuto));
            syncOneAutoRow($targetAuto);
            return;
        }
        if (isBox($target) && !parentKey($target)) {
            createAutoParentForBoxes($target, $box);
            return;
        }
        syncAutoRows();
    }

    function paletteButton(label, type, tool, icon) {
        return $('<button>', {
            type: 'button',
            class: 'h18-builder-palette-item h18-ud-layout-palette-item',
            draggable: 'true',
            'data-section-type': type,
            'data-h18-layout-tool': tool
        }).append($('<span>', { class: 'dashicons ' + icon }), document.createTextNode(label));
    }

    function installPaletteTools() {
        if ($palette.find('[data-h18-layout-tool="auto-row"]').length) { return; }
        const $heading = $('<div>', { class: 'h18-ud-layout-palette-heading' }).append(
            $('<strong>', { text: 'Layout+' }),
            $('<small>', { text: 'Auto-kasser og tabel' })
        );
        $palette.append($heading);
        $palette.append(paletteButton('Auto-kasser', 'grid', 'auto-row', 'dashicons-columns'));
        $palette.append(paletteButton('Kasse', 'container', 'box', 'dashicons-align-wide'));
        $palette.append(paletteButton('Tabel', 'html', 'table', 'dashicons-editor-table'));
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    function defaultTableState() {
        return {
            rows: 3,
            cols: 3,
            header: true,
            zebra: false,
            mobile: 'scroll',
            border: '#dcdcde',
            headerBg: '#30382a',
            headerColor: '#ffffff',
            cellBg: '#ffffff',
            textColor: '#20261d',
            fontSize: 16,
            padding: 10,
            cells: [
                ['Kolonne 1', 'Kolonne 2', 'Kolonne 3'],
                ['Celle 1', 'Celle 2', 'Celle 3'],
                ['Celle 4', 'Celle 5', 'Celle 6']
            ]
        };
    }

    function normalizeTableState(state) {
        state = state || defaultTableState();
        state.rows = Math.max(1, Math.min(30, parseInt(state.rows, 10) || 1));
        state.cols = Math.max(1, Math.min(12, parseInt(state.cols, 10) || 1));
        state.fontSize = Math.max(10, Math.min(48, parseInt(state.fontSize, 10) || 16));
        state.padding = Math.max(0, Math.min(40, parseInt(state.padding, 10) || 10));
        state.header = !!state.header;
        state.zebra = !!state.zebra;
        state.mobile = state.mobile === 'normal' ? 'normal' : 'scroll';
        state.cells = Array.isArray(state.cells) ? state.cells : [];
        while (state.cells.length < state.rows) { state.cells.push([]); }
        state.cells = state.cells.slice(0, state.rows);
        state.cells.forEach(function (row) {
            while (row.length < state.cols) { row.push(''); }
            row.splice(state.cols);
        });
        return state;
    }

    function tableHtml(state) {
        state = normalizeTableState(state);
        const attrs = [
            'data-h18-table="1"',
            'data-h18-table-rows="' + state.rows + '"',
            'data-h18-table-cols="' + state.cols + '"',
            'data-h18-table-header="' + (state.header ? '1' : '0') + '"',
            'data-h18-table-zebra="' + (state.zebra ? '1' : '0') + '"',
            'data-h18-table-mobile="' + escapeHtml(state.mobile) + '"',
            'data-h18-table-border="' + escapeHtml(state.border) + '"',
            'data-h18-table-header-bg="' + escapeHtml(state.headerBg) + '"',
            'data-h18-table-header-color="' + escapeHtml(state.headerColor) + '"',
            'data-h18-table-cell-bg="' + escapeHtml(state.cellBg) + '"',
            'data-h18-table-text-color="' + escapeHtml(state.textColor) + '"',
            'data-h18-table-font-size="' + state.fontSize + '"',
            'data-h18-table-padding="' + state.padding + '"'
        ].join(' ');
        const overflow = state.mobile === 'scroll' ? 'auto' : 'visible';
        let html = '<div ' + attrs + ' style="width:100%;max-width:100%;overflow-x:' + overflow + ';">';
        html += '<table style="width:100%;min-width:' + (state.mobile === 'scroll' ? Math.max(320, state.cols * 120) : 0) + 'px;border-collapse:collapse;font-size:' + state.fontSize + 'px;color:' + escapeHtml(state.textColor) + ';">';
        for (let r = 0; r < state.rows; r += 1) {
            if (r === 0 && state.header) { html += '<thead>'; }
            if (r === (state.header ? 1 : 0)) { html += '<tbody>'; }
            const zebraBg = state.zebra && r >= (state.header ? 1 : 0) && ((r - (state.header ? 1 : 0)) % 2 === 1) ? '#f6f7f7' : state.cellBg;
            html += '<tr>';
            for (let c = 0; c < state.cols; c += 1) {
                const value = escapeHtml(state.cells[r][c] || '');
                if (r === 0 && state.header) {
                    html += '<th scope="col" style="padding:' + state.padding + 'px;border:1px solid ' + escapeHtml(state.border) + ';background:' + escapeHtml(state.headerBg) + ';color:' + escapeHtml(state.headerColor) + ';text-align:left;">' + value + '</th>';
                } else {
                    html += '<td style="padding:' + state.padding + 'px;border:1px solid ' + escapeHtml(state.border) + ';background:' + escapeHtml(zebraBg) + ';color:' + escapeHtml(state.textColor) + ';">' + value + '</td>';
                }
            }
            html += '</tr>';
            if (r === 0 && state.header) { html += '</thead>'; }
            if (r === state.rows - 1) { html += '</tbody>'; }
        }
        html += '</table></div>';
        return html;
    }

    function tableStateFromRow($row) {
        const $content = controls($row, '[name$="[Content]"]').first();
        const raw = String($content.val() || '');
        if (!raw || raw.indexOf('data-h18-table="1"') === -1) {
            return defaultTableState();
        }
        const template = document.createElement('template');
        template.innerHTML = raw;
        const wrapper = template.content.querySelector('[data-h18-table="1"]');
        if (!wrapper) { return defaultTableState(); }
        const table = wrapper.querySelector('table');
        const rows = table ? Array.from(table.querySelectorAll('tr')) : [];
        const cells = rows.map(function (tr) { return Array.from(tr.children).map(function (cell) { return cell.textContent || ''; }); });
        return normalizeTableState({
            rows: parseInt(wrapper.getAttribute('data-h18-table-rows'), 10) || rows.length || 3,
            cols: parseInt(wrapper.getAttribute('data-h18-table-cols'), 10) || (cells[0] ? cells[0].length : 3),
            header: wrapper.getAttribute('data-h18-table-header') !== '0',
            zebra: wrapper.getAttribute('data-h18-table-zebra') === '1',
            mobile: wrapper.getAttribute('data-h18-table-mobile') || 'scroll',
            border: wrapper.getAttribute('data-h18-table-border') || '#dcdcde',
            headerBg: wrapper.getAttribute('data-h18-table-header-bg') || '#30382a',
            headerColor: wrapper.getAttribute('data-h18-table-header-color') || '#ffffff',
            cellBg: wrapper.getAttribute('data-h18-table-cell-bg') || '#ffffff',
            textColor: wrapper.getAttribute('data-h18-table-text-color') || '#20261d',
            fontSize: parseInt(wrapper.getAttribute('data-h18-table-font-size'), 10) || 16,
            padding: parseInt(wrapper.getAttribute('data-h18-table-padding'), 10) || 10,
            cells: cells
        });
    }

    function writeTableState($row, state) {
        state = normalizeTableState(state);
        $row.data('h18TableState', state);
        const $content = controls($row, '[name$="[Content]"]').first();
        $content.val(tableHtml(state)).trigger('input').trigger('change');
        window.setTimeout(function () { decorateTableCanvas($row, state); }, 10);
    }

    function decorateTableCanvas($row, state) {
        const $preview = $row.find('.h18-canvas-preview').first();
        if (!$preview.length) { return; }
        $preview.find('.h18-ud-table-canvas').remove();
        const $mini = $('<div>', { class: 'h18-ud-table-canvas' });
        const $table = $('<table>');
        state.cells.slice(0, Math.min(state.rows, 5)).forEach(function (cells, r) {
            const $tr = $('<tr>');
            cells.slice(0, Math.min(state.cols, 5)).forEach(function (value) {
                const tag = r === 0 && state.header ? '<th>' : '<td>';
                $(tag).text(String(value || '')).appendTo($tr);
            });
            $table.append($tr);
        });
        $mini.append($('<strong>', { text: 'Tabel · ' + state.rows + ' × ' + state.cols }), $table);
        $preview.append($mini);
    }

    function renderTableGrid($row, $panel, state) {
        const $grid = $panel.find('.h18-ud-table-cell-grid');
        $grid.empty().css('--h18-table-editor-cols', String(state.cols));
        for (let r = 0; r < state.rows; r += 1) {
            for (let c = 0; c < state.cols; c += 1) {
                const $input = $('<input>', {
                    type: 'text',
                    class: 'h18-ud-table-cell',
                    value: state.cells[r][c] || '',
                    'data-row': String(r),
                    'data-col': String(c),
                    'aria-label': 'Række ' + (r + 1) + ', kolonne ' + (c + 1)
                });
                if (r === 0 && state.header) { $input.addClass('is-header'); }
                $grid.append($input);
            }
        }
    }

    function refreshTablePanel($row, state) {
        const $panel = controls($row, '.h18-ud-table-editor').first();
        if (!$panel.length) { return; }
        $panel.find('[data-table-setting="rows"]').val(state.rows);
        $panel.find('[data-table-setting="cols"]').val(state.cols);
        $panel.find('[data-table-setting="header"]').prop('checked', state.header);
        $panel.find('[data-table-setting="zebra"]').prop('checked', state.zebra);
        $panel.find('[data-table-setting="mobile"]').val(state.mobile);
        $panel.find('[data-table-setting="border"]').val(state.border);
        $panel.find('[data-table-setting="headerBg"]').val(state.headerBg);
        $panel.find('[data-table-setting="headerColor"]').val(state.headerColor);
        $panel.find('[data-table-setting="cellBg"]').val(state.cellBg);
        $panel.find('[data-table-setting="textColor"]').val(state.textColor);
        $panel.find('[data-table-setting="fontSize"]').val(state.fontSize);
        $panel.find('[data-table-setting="padding"]').val(state.padding);
        renderTableGrid($row, $panel, state);
        decorateTableCanvas($row, state);
    }

    function ensureTableEditor($row) {
        if (!$row.length || rowType($row) !== 'html') { return; }
        const $content = controls($row, '[name$="[Content]"]').first();
        const looksLikeTable = rowLabel($row) === 'Tabel' || String($content.val() || '').indexOf('data-h18-table="1"') !== -1;
        if (!looksLikeTable) { return; }
        setNavigatorLabel($row, 'Tabel');
        if (!String($content.val() || '').includes('data-h18-table="1"')) {
            $content.val(tableHtml(defaultTableState())).trigger('input').trigger('change');
        }
        let state = tableStateFromRow($row);
        $row.data('h18TableState', state);
        if (!controls($row, '.h18-ud-table-editor').length) {
            const $panel = $('<div>', { class: 'h18-section-module-box h18-ud-table-editor' });
            $panel.append($('<h4>', { text: 'Tabel' }));
            $panel.append($('<p>', { class: 'description', text: 'Redigér celler direkte. Tabelindholdet gemmes i det eksisterende HTML-element og sanitiseres af WordPress.' }));
            const $settings = $('<div>', { class: 'h18-ud-table-settings' });
            $settings.append(
                $('<label>').append($('<strong>', { text: 'Rækker' }), $('<input>', { type: 'number', min: 1, max: 30, 'data-table-setting': 'rows' })),
                $('<label>').append($('<strong>', { text: 'Kolonner' }), $('<input>', { type: 'number', min: 1, max: 12, 'data-table-setting': 'cols' })),
                $('<label>').append($('<strong>', { text: 'Skrift (px)' }), $('<input>', { type: 'number', min: 10, max: 48, 'data-table-setting': 'fontSize' })),
                $('<label>').append($('<strong>', { text: 'Celleluft (px)' }), $('<input>', { type: 'number', min: 0, max: 40, 'data-table-setting': 'padding' })),
                $('<label>').append($('<strong>', { text: 'Kant' }), $('<input>', { type: 'color', 'data-table-setting': 'border' })),
                $('<label>').append($('<strong>', { text: 'Header baggrund' }), $('<input>', { type: 'color', 'data-table-setting': 'headerBg' })),
                $('<label>').append($('<strong>', { text: 'Header tekst' }), $('<input>', { type: 'color', 'data-table-setting': 'headerColor' })),
                $('<label>').append($('<strong>', { text: 'Celle baggrund' }), $('<input>', { type: 'color', 'data-table-setting': 'cellBg' })),
                $('<label>').append($('<strong>', { text: 'Tekstfarve' }), $('<input>', { type: 'color', 'data-table-setting': 'textColor' })),
                $('<label>').append($('<strong>', { text: 'Mobil' }), $('<select>', { 'data-table-setting': 'mobile' }).append($('<option>', { value: 'scroll', text: 'Vandret scroll' }), $('<option>', { value: 'normal', text: 'Normal tabel' })))
            );
            $panel.append($settings);
            $panel.append($('<div>', { class: 'h18-ud-table-toggles' }).append(
                $('<label>').append($('<input>', { type: 'checkbox', 'data-table-setting': 'header' }), ' Første række er overskrift'),
                $('<label>').append($('<input>', { type: 'checkbox', 'data-table-setting': 'zebra' }), ' Zebra-striber')
            ));
            $panel.append($('<div>', { class: 'h18-ud-table-actions' }).append(
                $('<button>', { type: 'button', class: 'button', 'data-table-action': 'add-row', text: '+ Række' }),
                $('<button>', { type: 'button', class: 'button', 'data-table-action': 'remove-row', text: '− Række' }),
                $('<button>', { type: 'button', class: 'button', 'data-table-action': 'add-col', text: '+ Kolonne' }),
                $('<button>', { type: 'button', class: 'button', 'data-table-action': 'remove-col', text: '− Kolonne' })
            ));
            $panel.append($('<div>', { class: 'h18-ud-table-cell-grid' }));
            $panel.insertAfter($content);
        }
        refreshTablePanel($row, state);
    }

    function configureTable($row) {
        if (!$row.length) { return; }
        setNavigatorLabel($row, 'Tabel');
        setField($row, 'Title', '');
        setField($row, 'Content', tableHtml(defaultTableState()));
        ensureTableEditor($row);
    }

    function configurePendingTool(tool, beforeKeys, targetKey) {
        const type = tool === 'auto-row' ? 'grid' : (tool === 'box' ? 'container' : 'html');
        window.setTimeout(function () {
            const $row = findNewRow(beforeKeys, type);
            if (!$row.length) { return; }
            if (tool === 'auto-row') {
                configureAutoRow($row);
                createInitialBox($row);
            } else if (tool === 'box') {
                configureBox($row);
                placeNewBox($row, targetKey);
            } else if (tool === 'table') {
                configureTable($row);
            }
            pendingTool = '';
            pendingDropTargetKey = '';
            syncAutoRows();
        }, 40);
    }

    document.addEventListener('click', function (event) {
        const button = event.target.closest && event.target.closest('.h18-builder-palette-item[data-h18-layout-tool]');
        if (!button) { return; }
        pendingTool = String(button.getAttribute('data-h18-layout-tool') || '');
        pendingKeys = snapshotKeys();
        pendingDropTargetKey = '';
        configurePendingTool(pendingTool, pendingKeys, '');
    }, true);

    document.addEventListener('dragstart', function (event) {
        const button = event.target.closest && event.target.closest('.h18-builder-palette-item[data-h18-layout-tool]');
        if (!button) { return; }
        pendingTool = String(button.getAttribute('data-h18-layout-tool') || '');
        pendingKeys = snapshotKeys();
        pendingDropTargetKey = '';
    }, true);

    document.addEventListener('drop', function (event) {
        if (!pendingTool) { return; }
        const target = event.target.closest && event.target.closest('.h18-page-section-row');
        pendingDropTargetKey = target ? rowKey($(target)) : '';
        configurePendingTool(pendingTool, pendingKeys, pendingDropTargetKey);
    }, true);

    $(document).on('input change', '.h18-ud-table-editor [data-table-setting], .h18-ud-table-cell', function () {
        const $row = $(this).closest('.h18-page-section-row').length ? $(this).closest('.h18-page-section-row') : $('#h18-page-inspector-target').closest('.h18-builder-inspector').find('.h18-page-section-row.is-selected');
        const $actualRow = $row.length ? $row : activeRows().filter('.is-selected').first();
        if (!$actualRow.length) { return; }
        let state = $actualRow.data('h18TableState') || tableStateFromRow($actualRow);
        const $panel = controls($actualRow, '.h18-ud-table-editor').first();
        state.rows = parseInt($panel.find('[data-table-setting="rows"]').val(), 10) || state.rows;
        state.cols = parseInt($panel.find('[data-table-setting="cols"]').val(), 10) || state.cols;
        state.header = $panel.find('[data-table-setting="header"]').is(':checked');
        state.zebra = $panel.find('[data-table-setting="zebra"]').is(':checked');
        state.mobile = String($panel.find('[data-table-setting="mobile"]').val() || 'scroll');
        state.border = String($panel.find('[data-table-setting="border"]').val() || state.border);
        state.headerBg = String($panel.find('[data-table-setting="headerBg"]').val() || state.headerBg);
        state.headerColor = String($panel.find('[data-table-setting="headerColor"]').val() || state.headerColor);
        state.cellBg = String($panel.find('[data-table-setting="cellBg"]').val() || state.cellBg);
        state.textColor = String($panel.find('[data-table-setting="textColor"]').val() || state.textColor);
        state.fontSize = parseInt($panel.find('[data-table-setting="fontSize"]').val(), 10) || state.fontSize;
        state.padding = parseInt($panel.find('[data-table-setting="padding"]').val(), 10);
        state = normalizeTableState(state);
        $panel.find('.h18-ud-table-cell').each(function () {
            const r = parseInt($(this).attr('data-row'), 10) || 0;
            const c = parseInt($(this).attr('data-col'), 10) || 0;
            if (state.cells[r]) { state.cells[r][c] = String($(this).val() || ''); }
        });
        writeTableState($actualRow, state);
        refreshTablePanel($actualRow, state);
    });

    $(document).on('click', '.h18-ud-table-editor [data-table-action]', function (event) {
        event.preventDefault();
        const $actualRow = activeRows().filter('.is-selected').first();
        if (!$actualRow.length) { return; }
        let state = normalizeTableState($actualRow.data('h18TableState') || tableStateFromRow($actualRow));
        const action = String($(this).attr('data-table-action') || '');
        if (action === 'add-row' && state.rows < 30) { state.rows += 1; state.cells.push(Array(state.cols).fill('')); }
        if (action === 'remove-row' && state.rows > 1) { state.rows -= 1; state.cells.pop(); }
        if (action === 'add-col' && state.cols < 12) { state.cols += 1; state.cells.forEach(function (row) { row.push(''); }); }
        if (action === 'remove-col' && state.cols > 1) { state.cols -= 1; state.cells.forEach(function (row) { row.pop(); }); }
        writeTableState($actualRow, state);
        refreshTablePanel($actualRow, state);
    });

    $(document).on('change', '.h18-layout-parent-select, .h18-layout-parent-key', function () {
        window.setTimeout(syncAutoRows, 20);
    });
    $(document).on('click', '.h18-page-section-delete', function () {
        window.setTimeout(syncAutoRows, 30);
    });

    const observer = new MutationObserver(function () {
        window.setTimeout(function () {
            activeRows().each(function () {
                const $row = $(this);
                if (isAutoRow($row)) { $row.attr('data-h18-auto-box-row', '1'); }
                if (isBox($row)) { $row.attr('data-h18-box', '1'); }
                ensureTableEditor($row);
            });
            syncAutoRows();
        }, 10);
    });
    observer.observe($sections.get(0), { childList: true, subtree: false });

    installPaletteTools();
    activeRows().each(function () {
        const $row = $(this);
        if (isAutoRow($row)) { $row.attr('data-h18-auto-box-row', '1'); }
        if (isBox($row)) { $row.attr('data-h18-box', '1'); }
        ensureTableEditor($row);
    });
    syncAutoRows();
});
