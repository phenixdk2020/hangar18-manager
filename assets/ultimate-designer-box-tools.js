jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $inspectorTarget = $('#h18-page-inspector-target');
    if (!$sections.length || !$inspectorTarget.length) {
        return;
    }

    const AUTO_LABEL = 'Auto-kasser';
    const BOX_LABEL = 'Kasse';
    const PANEL_CLASS = 'h18-ud-box-inspector';
    let refreshTimer = null;
    let currentPanelKey = '';
    let currentPanelMode = '';

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function selectedRow() {
        return activeRows().filter('.is-selected').first();
    }

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || '');
    }

    function rowType($row) {
        return String($row.attr('data-section-type') || '');
    }

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($inspectorTarget.find(selector));
        }
        return $result;
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

    function numberValue($row, name, fallback) {
        const parsed = parseFloat(String(fieldValue($row, name, fallback)));
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function setField($row, name, value) {
        const $field = field($row, name);
        if (!$field.length) { return false; }
        if ($field.is(':checkbox')) {
            $field.prop('checked', !!value).trigger('change');
        } else {
            $field.val(String(value)).trigger('input').trigger('change');
        }
        return true;
    }

    function rowLabel($row) {
        return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
    }

    function parentKey($row) {
        return String(controls($row, '.h18-layout-parent-key').first().val() || '');
    }

    function rowByKey(key) {
        key = String(key || '');
        if (!key) { return $(); }
        return activeRows().filter(function () {
            return rowKey($(this)) === key;
        }).first();
    }

    function isAutoRow($row) {
        return !!($row && $row.length && rowType($row) === 'grid' && rowLabel($row) === AUTO_LABEL);
    }

    function isBox($row) {
        return !!($row && $row.length && rowType($row) === 'container' && rowLabel($row).indexOf(BOX_LABEL) === 0);
    }

    function parentAutoRow($row) {
        const $parent = rowByKey(parentKey($row));
        return isAutoRow($parent) ? $parent : $();
    }

    function childBoxes($autoRow) {
        const key = rowKey($autoRow);
        if (!key) { return $(); }
        return activeRows().filter(function () {
            const $candidate = $(this);
            return parentKey($candidate) === key && isBox($candidate);
        });
    }

    function nestedChildCount($row) {
        const key = rowKey($row);
        if (!key) { return 0; }
        return activeRows().filter(function () {
            return parentKey($(this)) === key;
        }).length;
    }

    function normalizeHex(value, fallback) {
        const text = String(value || '').trim();
        if (/^#[0-9a-f]{6}$/i.test(text)) { return text; }
        if (/^#[0-9a-f]{3}$/i.test(text)) {
            return '#' + text.slice(1).split('').map(function (ch) { return ch + ch; }).join('');
        }
        return fallback;
    }

    function ensureCustomDesign($row) {
        if (String(fieldValue($row, 'DesignMode', 'Global')) !== 'Custom') {
            setField($row, 'DesignMode', 'Custom');
        }
    }

    function groupTitle(text, description) {
        const $wrap = $('<div>', { class: 'h18-ud-box-group-title' }).append($('<strong>', { text: text }));
        if (description) {
            $wrap.append($('<small>', { text: description }));
        }
        return $wrap;
    }

    function numberControl(label, fieldName, value, min, max, target, suffix) {
        return $('<label>', { class: 'h18-ud-box-control-row' }).append(
            $('<span>', { text: label }),
            $('<span>', { class: 'h18-ud-box-input-with-suffix' }).append(
                $('<input>', {
                    type: 'number',
                    min: min,
                    max: max,
                    step: 1,
                    value: Math.round(Number(value) || 0),
                    class: 'h18-ud-box-control',
                    'data-box-field': fieldName,
                    'data-box-target': target || 'self'
                }),
                suffix ? $('<em>', { text: suffix }) : $()
            )
        );
    }

    function colorControl(label, fieldName, value) {
        const color = normalizeHex(value, '#ffffff');
        return $('<label>', { class: 'h18-ud-box-control-row' }).append(
            $('<span>', { text: label }),
            $('<span>', { class: 'h18-ud-box-color-control' }).append(
                $('<input>', {
                    type: 'color',
                    value: color,
                    class: 'h18-ud-box-control',
                    'data-box-field': fieldName,
                    'data-box-target': 'self',
                    'data-box-custom-design': '1'
                }),
                $('<code>', { text: color })
            )
        );
    }

    function textControl(label, fieldName, value, placeholder) {
        const attrs = {
            type: 'text',
            value: String(value || ''),
            placeholder: placeholder || '',
            class: 'h18-ud-box-control',
            'data-box-field': fieldName,
            'data-box-target': 'self'
        };
        if (fieldName === 'SectionBodyFontFamily' || fieldName === 'SectionHeadingFontFamily') {
            attrs.list = 'h18-ud-box-fonts';
        }
        return $('<label>', { class: 'h18-ud-box-control-row h18-ud-box-control-row--wide' }).append(
            $('<span>', { text: label }),
            $('<input>', attrs)
        );
    }

    function ensureFontSuggestions() {
        if ($('#h18-ud-box-fonts').length) { return; }
        const $list = $('<datalist>', { id: 'h18-ud-box-fonts' });
        [
            'Arial, sans-serif',
            'Verdana, sans-serif',
            'Tahoma, sans-serif',
            'Trebuchet MS, sans-serif',
            'Georgia, serif',
            'Times New Roman, serif',
            'Courier New, monospace',
            'system-ui, sans-serif'
        ].forEach(function (font) {
            $list.append($('<option>', { value: font }));
        });
        $('body').append($list);
    }

    function buildGapControls($panel, $autoRow, description) {
        if (!$autoRow || !$autoRow.length) { return; }
        const count = childBoxes($autoRow).length;
        $panel.append(groupTitle('Afstand mellem kasser', description || 'Rækken styrer afstanden; hver kasse beholder sit eget design.'));
        const $grid = $('<div>', { class: 'h18-ud-box-control-grid' });
        $grid.append(
            numberControl('Desktop', 'LayoutGapPx', numberValue($autoRow, 'LayoutGapPx', 16), 0, 160, 'parent', 'px'),
            numberControl('Mobil', 'MobileLayoutGapPx', numberValue($autoRow, 'MobileLayoutGapPx', 12), 0, 160, 'parent', 'px')
        );
        $panel.append($grid);
        $panel.append($('<p>', {
            class: 'description h18-ud-box-layout-note',
            text: count + ' kasse' + (count === 1 ? '' : 'r') + ' i rækken. På desktop sættes kolonnerne automatisk efter antallet af kasser; mobil starter med 1 kolonne.'
        }));
    }

    function buildRadiusControls($panel, $row) {
        $panel.append(groupTitle('Hjørner', '0 px giver helt firkantede kasser. Højere værdi giver mere afrundede hjørner.'));
        const radius = numberValue($row, 'RadiusPx', 7);
        const $radiusLine = $('<div>', { class: 'h18-ud-box-radius-line' }).append(
            numberControl('Radius', 'RadiusPx', radius, 0, 160, 'self', 'px'),
            $('<div>', { class: 'h18-ud-box-radius-presets' }).append(
                $('<button>', { type: 'button', class: 'button', 'data-box-radius-preset': '0', text: 'Firkantet' }),
                $('<button>', { type: 'button', class: 'button', 'data-box-radius-preset': '8', text: '8 px' }),
                $('<button>', { type: 'button', class: 'button', 'data-box-radius-preset': '16', text: '16 px' }),
                $('<button>', { type: 'button', class: 'button', 'data-box-radius-preset': '24', text: '24 px' })
            )
        );
        $panel.append($radiusLine);

        const cornerFields = ['RadiusTopLeftPx', 'RadiusTopRightPx', 'RadiusBottomRightPx', 'RadiusBottomLeftPx'];
        const individual = cornerFields.some(function (name) { return numberValue($row, name, -1) >= 0; });
        const $toggle = $('<label>', { class: 'h18-ud-box-corner-toggle' }).append(
            $('<input>', { type: 'checkbox', 'data-box-individual-corners': '1', checked: individual }),
            $('<span>', { text: 'Styr hvert hjørne separat' })
        );
        $panel.append($toggle);
        const $corners = $('<div>', { class: 'h18-ud-box-corner-grid' }).toggle(individual);
        [
            ['Øverst venstre', 'RadiusTopLeftPx'],
            ['Øverst højre', 'RadiusTopRightPx'],
            ['Nederst højre', 'RadiusBottomRightPx'],
            ['Nederst venstre', 'RadiusBottomLeftPx']
        ].forEach(function (item) {
            const current = numberValue($row, item[1], -1);
            $corners.append(numberControl(item[0], item[1], current < 0 ? radius : current, 0, 160, 'self', 'px'));
        });
        $panel.append($corners);
    }

    function buildBoxPanel($row) {
        ensureFontSuggestions();
        const $panel = $('<div>', { class: 'h18-section-module-box ' + PANEL_CLASS, 'data-box-panel-mode': 'box' });
        $panel.append($('<h4>', { text: 'Kasse · eget design' }));
        $panel.append($('<p>', {
            class: 'description',
            text: 'Disse indstillinger gælder kun denne kasse. De andre kasser i rækken ændres ikke.'
        }));

        const $autoRow = parentAutoRow($row);
        if ($autoRow.length) {
            buildGapControls($panel, $autoRow, 'Afstanden gælder hele rækken, mens farver, skrift, padding og hjørner styres pr. kasse.');
        }

        buildRadiusControls($panel, $row);

        $panel.append(groupTitle('Farver', 'Farverne gemmes som custom design på den valgte kasse.'));
        const $colors = $('<div>', { class: 'h18-ud-box-control-grid h18-ud-box-control-grid--colors' });
        $colors.append(
            colorControl('Baggrund', 'CustomBackgroundColor', fieldValue($row, 'CustomBackgroundColor', '#ffffff')),
            colorControl('Tekst', 'CustomTextColor', fieldValue($row, 'CustomTextColor', '#30382a')),
            colorControl('Overskrift', 'CustomHeadingColor', fieldValue($row, 'CustomHeadingColor', '#30382a')),
            colorControl('Kant', 'CustomBorderColor', fieldValue($row, 'CustomBorderColor', '#c3ae83'))
        );
        $panel.append($colors);

        $panel.append(groupTitle('Skrift', 'Body og overskrifter kan have forskellig font i hver kasse.'));
        const $fonts = $('<div>', { class: 'h18-ud-box-control-grid' });
        $fonts.append(
            textControl('Brødtekst font', 'SectionBodyFontFamily', fieldValue($row, 'SectionBodyFontFamily', ''), 'fx Arial, sans-serif'),
            textControl('Overskrift font', 'SectionHeadingFontFamily', fieldValue($row, 'SectionHeadingFontFamily', ''), 'fx Georgia, serif'),
            numberControl('Brødtekst størrelse', 'BodyFontSizePx', numberValue($row, 'BodyFontSizePx', 16), 8, 96, 'self', 'px'),
            numberControl('H2 størrelse', 'H2FontSizePx', numberValue($row, 'H2FontSizePx', 28), 8, 120, 'self', 'px')
        );
        $panel.append($fonts);

        $panel.append(groupTitle('Luft og kant', 'Padding er luften inde i selve kassen.'));
        const $spacing = $('<div>', { class: 'h18-ud-box-control-grid' });
        $spacing.append(
            numberControl('Lodret padding', 'PaddingPx', numberValue($row, 'PaddingPx', 20), 0, 160, 'self', 'px'),
            numberControl('Vandret padding', 'HorizontalPaddingPx', numberValue($row, 'HorizontalPaddingPx', 20), 0, 160, 'self', 'px'),
            numberControl('Kantbredde', 'BorderWidthPx', numberValue($row, 'BorderWidthPx', 0), 0, 16, 'self', 'px')
        );
        $panel.append($spacing);

        return $panel;
    }

    function buildAutoPanel($row) {
        const $panel = $('<div>', { class: 'h18-section-module-box ' + PANEL_CLASS, 'data-box-panel-mode': 'auto' });
        $panel.append($('<h4>', { text: 'Auto-kasser · række' }));
        $panel.append($('<p>', {
            class: 'description',
            text: 'Kasser i denne række ligger ved siden af hinanden på desktop. Hver kasse kan stadig have sit eget design.'
        }));
        buildGapControls($panel, $row);
        return $panel;
    }

    function syncPanelValues($row, mode) {
        const $panel = $inspectorTarget.find('.' + PANEL_CLASS).first();
        if (!$panel.length) { return; }
        $panel.find('.h18-ud-box-control').each(function () {
            const $control = $(this);
            const name = String($control.attr('data-box-field') || '');
            const target = String($control.attr('data-box-target') || 'self');
            let $targetRow = $row;
            if (target === 'parent') {
                $targetRow = mode === 'auto' ? $row : parentAutoRow($row);
            }
            if (!$targetRow.length || !name) { return; }
            let value = fieldValue($targetRow, name, $control.val());
            if ($control.attr('type') === 'color') {
                value = normalizeHex(value, String($control.val() || '#ffffff'));
                $control.closest('.h18-ud-box-color-control').find('code').text(value);
            }
            $control.val(String(value));
        });
    }

    function refreshInspectorPanel(force) {
        const $row = selectedRow();
        if (!$row.length) {
            $inspectorTarget.find('.' + PANEL_CLASS).remove();
            currentPanelKey = '';
            currentPanelMode = '';
            return;
        }

        let mode = '';
        if (isBox($row)) { mode = 'box'; }
        if (isAutoRow($row)) { mode = 'auto'; }
        if (!mode) {
            $inspectorTarget.find('.' + PANEL_CLASS).remove();
            currentPanelKey = rowKey($row);
            currentPanelMode = '';
            return;
        }

        const key = rowKey($row);
        const exists = $inspectorTarget.find('.' + PANEL_CLASS + '[data-box-panel-mode="' + mode + '"]').length > 0;
        if (force || key !== currentPanelKey || mode !== currentPanelMode || !exists) {
            $inspectorTarget.find('.' + PANEL_CLASS).remove();
            $inspectorTarget.append(mode === 'box' ? buildBoxPanel($row) : buildAutoPanel($row));
            currentPanelKey = key;
            currentPanelMode = mode;
        } else {
            syncPanelValues($row, mode);
        }
    }

    function computedBoxAppearance($box) {
        const $preview = $box.find('.h18-canvas-preview').first();
        const node = $preview.get(0);
        if (node && window.getComputedStyle) {
            const style = window.getComputedStyle(node);
            return {
                background: style.backgroundColor || '#ffffff',
                color: style.color || '#30382a',
                borderColor: style.borderColor || '#c3ae83',
                borderWidth: style.borderWidth || '0px',
                borderRadius: style.borderRadius || (numberValue($box, 'RadiusPx', 7) + 'px'),
                fontFamily: style.fontFamily || String(fieldValue($box, 'SectionBodyFontFamily', 'inherit')),
                fontSize: style.fontSize || (numberValue($box, 'BodyFontSizePx', 16) + 'px')
            };
        }
        return {
            background: normalizeHex(fieldValue($box, 'CustomBackgroundColor', '#ffffff'), '#ffffff'),
            color: normalizeHex(fieldValue($box, 'CustomTextColor', '#30382a'), '#30382a'),
            borderColor: normalizeHex(fieldValue($box, 'CustomBorderColor', '#c3ae83'), '#c3ae83'),
            borderWidth: numberValue($box, 'BorderWidthPx', 0) + 'px',
            borderRadius: numberValue($box, 'RadiusPx', 7) + 'px',
            fontFamily: String(fieldValue($box, 'SectionBodyFontFamily', 'inherit')),
            fontSize: numberValue($box, 'BodyFontSizePx', 16) + 'px'
        };
    }

    function decorateAutoRow($autoRow) {
        if (!isAutoRow($autoRow)) { return; }
        $autoRow.attr('data-h18-auto-box-row', '1');
        const $preview = $autoRow.find('.h18-canvas-preview').first();
        if (!$preview.length) { return; }

        $preview.find('.h18-ud-auto-box-canvas').remove();
        const $boxes = childBoxes($autoRow);
        const count = $boxes.length;
        const columns = Math.max(1, Math.min(6, Math.round(numberValue($autoRow, 'LayoutColumns', count || 1))));
        const gap = Math.max(0, Math.min(160, numberValue($autoRow, 'LayoutGapPx', 16)));
        const $canvas = $('<div>', { class: 'h18-ud-auto-box-canvas' }).css({
            '--h18-ud-box-columns': String(columns),
            '--h18-ud-box-gap': gap + 'px'
        });
        $canvas.append($('<div>', { class: 'h18-ud-auto-box-canvas-head' }).append(
            $('<strong>', { text: 'Kasser i rækken' }),
            $('<span>', { text: count + ' stk. · ' + gap + ' px mellemrum' })
        ));

        const $grid = $('<div>', { class: 'h18-ud-auto-box-grid' });
        if (!count) {
            $grid.append($('<div>', { class: 'h18-ud-auto-box-empty', text: 'Træk en Kasse ind i Auto-kasser.' }));
        } else {
            $boxes.each(function (index) {
                const $box = $(this);
                $box.attr('data-h18-box', '1');
                const appearance = computedBoxAppearance($box);
                const nested = nestedChildCount($box);
                const label = rowLabel($box) || (BOX_LABEL + ' ' + (index + 1));
                const $tile = $('<button>', {
                    type: 'button',
                    class: 'h18-ud-auto-box-tile',
                    'data-h18-box-key': rowKey($box),
                    title: 'Vælg ' + label + ' og redigér dens eget design.'
                }).css({
                    background: appearance.background,
                    color: appearance.color,
                    borderColor: appearance.borderColor,
                    borderWidth: appearance.borderWidth,
                    borderRadius: appearance.borderRadius,
                    fontFamily: appearance.fontFamily,
                    fontSize: appearance.fontSize
                });
                $tile.append(
                    $('<strong>', { text: label === BOX_LABEL ? BOX_LABEL + ' ' + (index + 1) : label }),
                    $('<small>', { text: nested ? (nested + ' element' + (nested === 1 ? '' : 'er') + ' i kassen') : 'Tom kasse · træk indhold ind her' })
                );
                $grid.append($tile);
            });
        }
        $canvas.append($grid);
        $preview.append($canvas);
    }

    function markAndDecorateRows() {
        activeRows().each(function () {
            const $row = $(this);
            if (isAutoRow($row)) {
                decorateAutoRow($row);
            } else if (isBox($row)) {
                $row.attr('data-h18-box', '1');
            }
        });
    }

    function runRefresh(forceInspector) {
        refreshTimer = null;
        markAndDecorateRows();
        refreshInspectorPanel(!!forceInspector);
    }

    function scheduleRefresh(forceInspector) {
        if (refreshTimer) {
            window.clearTimeout(refreshTimer);
        }
        refreshTimer = window.setTimeout(function () {
            runRefresh(forceInspector);
        }, 30);
    }

    $(document).on('input change', '.' + PANEL_CLASS + ' .h18-ud-box-control', function () {
        const $control = $(this);
        const $row = selectedRow();
        if (!$row.length) { return; }
        const mode = isAutoRow($row) ? 'auto' : (isBox($row) ? 'box' : '');
        if (!mode) { return; }
        const name = String($control.attr('data-box-field') || '');
        const target = String($control.attr('data-box-target') || 'self');
        let $targetRow = $row;
        if (target === 'parent') {
            $targetRow = mode === 'auto' ? $row : parentAutoRow($row);
        }
        if (!$targetRow.length || !name) { return; }
        if ($control.attr('data-box-custom-design') === '1') {
            ensureCustomDesign($targetRow);
        }
        setField($targetRow, name, $control.val());
        if ($control.attr('type') === 'color') {
            $control.closest('.h18-ud-box-color-control').find('code').text(String($control.val() || ''));
        }
        scheduleRefresh(false);
    });

    $(document).on('click', '.' + PANEL_CLASS + ' [data-box-radius-preset]', function (event) {
        event.preventDefault();
        const $row = selectedRow();
        if (!isBox($row)) { return; }
        const radius = Math.max(0, Math.min(160, parseInt(String($(this).attr('data-box-radius-preset') || '0'), 10) || 0));
        setField($row, 'RadiusPx', radius);
        ['RadiusTopLeftPx', 'RadiusTopRightPx', 'RadiusBottomRightPx', 'RadiusBottomLeftPx'].forEach(function (name) {
            setField($row, name, -1);
        });
        const $panel = $inspectorTarget.find('.' + PANEL_CLASS);
        $panel.find('[data-box-field="RadiusPx"]').val(String(radius));
        $panel.find('[data-box-individual-corners="1"]').prop('checked', false);
        $panel.find('.h18-ud-box-corner-grid').hide();
        scheduleRefresh(false);
    });

    $(document).on('change', '.' + PANEL_CLASS + ' [data-box-individual-corners="1"]', function () {
        const $row = selectedRow();
        if (!isBox($row)) { return; }
        const enabled = $(this).is(':checked');
        const radius = numberValue($row, 'RadiusPx', 7);
        const fields = ['RadiusTopLeftPx', 'RadiusTopRightPx', 'RadiusBottomRightPx', 'RadiusBottomLeftPx'];
        fields.forEach(function (name) {
            setField($row, name, enabled ? radius : -1);
        });
        const $panel = $inspectorTarget.find('.' + PANEL_CLASS);
        $panel.find('.h18-ud-box-corner-grid').toggle(enabled);
        if (enabled) {
            fields.forEach(function (name) {
                $panel.find('[data-box-field="' + name + '"]').val(String(radius));
            });
        }
        scheduleRefresh(false);
    });

    $(document).on('click', '.h18-ud-auto-box-tile', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $row = rowByKey(String($(this).attr('data-h18-box-key') || ''));
        if (!$row.length) { return; }
        const $header = $row.children('.h18-page-section-header').first();
        if ($header.length) {
            $header.trigger('click');
        } else {
            $row.trigger('click');
        }
        window.setTimeout(function () { scheduleRefresh(true); }, 20);
    });

    $(document).on('input change', '#h18-page-inspector-target input, #h18-page-inspector-target select, #h18-page-inspector-target textarea', function () {
        if ($(this).closest('.' + PANEL_CLASS).length) { return; }
        scheduleRefresh(false);
    });

    $(document).on('change', '.h18-layout-parent-select, .h18-layout-parent-key', function () {
        scheduleRefresh(true);
    });

    $(document).on('click', '.h18-page-section-header, .h18-page-section-delete, .h18-builder-palette-item', function () {
        window.setTimeout(function () { scheduleRefresh(true); }, 20);
    });

    const sectionObserver = new MutationObserver(function () {
        scheduleRefresh(true);
    });
    sectionObserver.observe($sections.get(0), { childList: true, subtree: false, attributes: true, attributeFilter: ['class'] });

    const inspectorObserver = new MutationObserver(function () {
        scheduleRefresh(false);
    });
    inspectorObserver.observe($inspectorTarget.get(0), { childList: true, subtree: false });

    runRefresh(true);
});
