from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def replace_between(text, start_marker, end_marker, replacement, label):
    start = text.find(start_marker)
    if start < 0:
        raise SystemExit(f"{label}: start marker missing")
    end = text.find(end_marker, start)
    if end < 0:
        raise SystemExit(f"{label}: end marker missing")
    return text[:start] + replacement + text[end:]


js_path = Path('assets/admin.js')
js = js_path.read_text(encoding='utf-8')

js = replace_once(
    js,
    "    let currentCanvasDevice = 'desktop';\n    let currentCanvasState = 'normal';\n",
    "    let currentCanvasDevice = 'desktop';\n    let currentCanvasState = 'normal';\n    let selectedCanvasCardKey = '';\n",
    'canvas card selection state'
)

start_marker = "        } else if (type === 'card_grid') {\n            addTitle('Kort-række');\n            canvasAddBodyText($inner, content);\n"
end_marker = "        } else if (type === 'mail_form') {\n"
card_block = r'''        } else if (type === 'card_grid') {
            addTitle('Kort-række');
            canvasAddBodyText($inner, content);
            const columns = currentCanvasDevice === 'mobile' ? canvasNumber($row, 'MobileColumns', 1) : canvasNumber($row, 'Columns', 3);
            const gap = currentCanvasDevice === 'mobile' ? canvasNumber($row, 'MobileColumnGapPx', 14) : canvasNumber($row, 'ColumnGapPx', 16);
            const $grid = $('<div>', { class: 'h18-canvas-card-grid' }).css({ gridTemplateColumns: 'repeat(' + Math.max(1, Math.min(6, columns)) + ',minmax(0,1fr))', gap: gap + 'px' });
            pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').each(function () {
                const $card = $(this);
                const key = canvasCardKey($card);
                const active = $card.find('[name$="[Active]"]').is(':checked');
                const $cardPreview = $('<article>', {
                    class: 'h18-canvas-card' + (selectedCanvasCardKey === key ? ' is-card-selected' : '') + (active ? '' : ' is-card-inactive'),
                    'data-card-key': key, tabindex: '0', role: 'button'
                });
                $cardPreview.append($('<button>', { type: 'button', class: 'h18-canvas-card-drag-handle', title: 'Træk for at flytte kort', 'aria-label': 'Flyt kort' }).append($('<span>', { class: 'dashicons dashicons-move' })));
                const titleValue = String(canvasCardFieldValue($card, 'Title', ''));
                $cardPreview.append($('<strong>', {
                    class: 'h18-canvas-card-title h18-canvas-card-inline-edit', text: titleValue || 'Kort uden overskrift',
                    'data-card-edit-field': 'Title', contenteditable: 'false', spellcheck: 'true', title: 'Dobbeltklik for at redigere kortets overskrift'
                }));
                const contentHtml = String(canvasCardFieldValue($card, 'Content', '') || '').trim();
                const $content = $('<div>', {
                    class: 'h18-canvas-card-content h18-canvas-card-rich-edit' + (contentHtml ? '' : ' is-empty'),
                    'data-card-edit-field': 'Content', contenteditable: 'false', spellcheck: 'true', title: 'Dobbeltklik for at redigere kortets tekst'
                });
                if (contentHtml) { $content.html(contentHtml); } else { $content.text('Dobbeltklik for at tilføje tekst'); }
                $cardPreview.append($content);
                if (!active) { $cardPreview.append($('<span>', { class: 'h18-canvas-card-inactive-label', text: 'Skjult på siden' })); }
                canvasApplyCardPreviewStyle($card, $cardPreview);
                if (selectedCanvasCardKey === key) { canvasBuildCardTools($card, $cardPreview); }
                $grid.append($cardPreview);
            });
            if (!$grid.children().length) { $grid.append($('<div>', { class: 'h18-canvas-card', text: 'Tilføj et kort i Inspector' })); }
            $inner.append($grid);
'''
js = replace_between(js, start_marker, end_marker, card_block, 'canvas card-grid preview block')

helpers = r'''
    function canvasCardKey($card) {
        return String($card.find('.h18-page-card-key').val() || $card.attr('data-card-index') || '');
    }

    function canvasCardFieldValue($card, fieldName, fallback) {
        const $field = $card.find('[name$="[' + fieldName + ']"]').first();
        if (!$field.length) { return fallback; }
        if ($field.is(':checkbox')) { return $field.is(':checked'); }
        const value = $field.val();
        return value == null || value === '' ? fallback : value;
    }

    function canvasCardSetField($card, fieldName, value) {
        const $field = $card.find('[name$="[' + fieldName + ']"]').first();
        if (!$field.length) { return false; }
        if ($field.is(':checkbox')) { $field.prop('checked', Boolean(value)); } else { $field.val(value); }
        return true;
    }

    function canvasCardNumber($card, fieldName, fallback) {
        const value = parseFloat(canvasCardFieldValue($card, fieldName, fallback));
        return Number.isFinite(value) ? value : fallback;
    }

    function canvasCardBorderColor(value) {
        const borders = { None: 'transparent', Sand: '#c3ae83', Olive: '#30382a', Steel: '#525a5f' };
        return borders[String(value || 'Sand')] || '#c3ae83';
    }

    function canvasCardTextColor($card) {
        const background = String(canvasCardFieldValue($card, 'Background', 'OffWhite'));
        const tone = String(canvasCardFieldValue($card, 'TextTone', 'Auto'));
        return tone === 'Light' || (tone === 'Auto' && ['Olive', 'Steel'].includes(background)) ? '#ffffff' : '#30382a';
    }

    function canvasFindCardRow($row, cardKey) {
        let $match = $();
        pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').each(function () {
            const $card = $(this);
            if (canvasCardKey($card) === String(cardKey || '')) { $match = $card; return false; }
        });
        return $match;
    }

    function canvasApplyCardPreviewStyle($card, $cardPreview) {
        if (!$card.length || !$cardPreview.length) { return; }
        const mobile = currentCanvasDevice === 'mobile';
        const paddingField = mobile ? 'MobilePaddingPx' : 'PaddingPx';
        const alignField = mobile ? 'MobileAlignment' : 'DesktopAlignment';
        const padding = Math.max(0, Math.min(mobile ? 60 : 80, canvasCardNumber($card, paddingField, mobile ? 20 : 26)));
        const radius = Math.max(0, Math.min(30, canvasCardNumber($card, 'RadiusPx', 7)));
        const borderWidth = Math.max(0, Math.min(8, canvasCardNumber($card, 'BorderWidthPx', 0)));
        $cardPreview.css({
            background: canvasPaletteColor(canvasCardFieldValue($card, 'Background', 'OffWhite')),
            color: canvasCardTextColor($card),
            borderStyle: 'solid', borderWidth: borderWidth + 'px', borderColor: canvasCardBorderColor(canvasCardFieldValue($card, 'BorderColor', 'Sand')),
            padding: padding + 'px', borderRadius: radius + 'px',
            textAlign: String(canvasCardFieldValue($card, alignField, 'Left')) === 'Center' ? 'center' : 'left'
        });
    }

    function canvasCardRange(label, fieldName, value, min, max) {
        return $('<label>', { class: 'h18-canvas-card-range' }).append(
            $('<span>', { text: label }),
            $('<input>', { type: 'range', min: min, max: max, step: 1, value: Math.round(value), 'data-card-control-field': fieldName }),
            $('<output>', { text: Math.round(value) + ' px' })
        );
    }

    function canvasCardSelect(label, fieldName, value, options) {
        const $select = $('<select>', { class: 'h18-canvas-card-control', 'data-card-control-field': fieldName });
        options.forEach(function (option) { $select.append($('<option>', { value: option[0], text: option[1], selected: String(value) === String(option[0]) })); });
        return $('<label>', { class: 'h18-canvas-card-select' }).append($('<span>', { text: label }), $select);
    }

    function canvasBuildCardTools($card, $cardPreview) {
        const mobile = currentCanvasDevice === 'mobile';
        const paddingField = mobile ? 'MobilePaddingPx' : 'PaddingPx';
        const alignField = mobile ? 'MobileAlignment' : 'DesktopAlignment';
        $cardPreview.append($('<div>', { class: 'h18-canvas-card-tools' }).append(
            $('<strong>', { text: 'Kortdesign' }),
            canvasCardSelect('Baggrund', 'Background', canvasCardFieldValue($card, 'Background', 'OffWhite'), [['White','Hvid'],['OffWhite','Knækket hvid'],['Sand','Sand'],['Olive','Oliven'],['Steel','Stål']]),
            canvasCardSelect('Tekst', 'TextTone', canvasCardFieldValue($card, 'TextTone', 'Auto'), [['Auto','Auto'],['Dark','Mørk'],['Light','Lys']]),
            canvasCardSelect('Placering', alignField, canvasCardFieldValue($card, alignField, 'Left'), [['Left','Venstre'],['Center','Midt']]),
            canvasCardRange('Padding', paddingField, canvasCardNumber($card, paddingField, mobile ? 20 : 26), 0, mobile ? 60 : 80),
            canvasCardRange('Radius', 'RadiusPx', canvasCardNumber($card, 'RadiusPx', 7), 0, 30),
            canvasCardRange('Kant', 'BorderWidthPx', canvasCardNumber($card, 'BorderWidthPx', 0), 0, 8),
            $('<label>', { class: 'h18-canvas-card-active' }).append($('<input>', { type: 'checkbox', class: 'h18-canvas-card-control', 'data-card-control-field': 'Active', checked: Boolean(canvasCardFieldValue($card, 'Active', true)) }), $('<span>', { text: 'Aktiv' }))
        ));
    }

    function canvasFocusCardEditor($row, cardKey) {
        pageSectionControls($row, '.h18-page-card-row').removeClass('is-canvas-selected-card');
        const $card = canvasFindCardRow($row, cardKey);
        if ($card.length) {
            $card.addClass('is-canvas-selected-card');
            $pageInspector.find('.h18-builder-inspector-heading span').text('Kort-række · ' + String(canvasCardFieldValue($card, 'Title', '') || 'Kort uden overskrift'));
        }
        return $card;
    }

    function initializeCanvasCardGridPreview($row, $preview) {
        const $grid = $preview.find('.h18-canvas-card-grid');
        if (!$grid.length || $grid.hasClass('ui-sortable')) { return; }
        $grid.sortable({
            items: '> .h18-canvas-card[data-card-key]', handle: '.h18-canvas-card-drag-handle', tolerance: 'pointer', placeholder: 'h18-canvas-card-sort-placeholder',
            update: function () {
                const keys = $grid.children('.h18-canvas-card[data-card-key]').map(function () { return String($(this).data('card-key') || ''); }).get();
                const $container = pageSectionControls($row, '.h18-page-cards-sortable').first();
                keys.forEach(function (key) { const $card = canvasFindCardRow($row, key); if ($card.length) { $container.append($card); } });
                syncPageCardOrder($container);
                renderCanvasPreview($row);
            }
        });
    }

'''
js = replace_once(js, "    function ensureCanvasPreview($row) {\n", helpers + "    function ensureCanvasPreview($row) {\n", 'card helper insertion')
js = replace_once(js, "        canvasBuildPreviewContent($row, $preview);\n        $preview.removeAttr('style').css({\n", "        canvasBuildPreviewContent($row, $preview);\n        initializeCanvasCardGridPreview($row, $preview);\n        $preview.removeAttr('style').css({\n", 'card sortable init')

js = replace_once(
    js,
    "        $bar.append($('<strong>', { class: 'h18-canvas-direct-title', text: 'Direkte design' }), $ranges, $colors);\n        $preview.append($bar);\n",
    "        $bar.append($('<strong>', { class: 'h18-canvas-direct-title', text: 'Direkte design' }), $ranges, $colors);\n        if (String($row.attr('data-section-type') || '') === 'card_grid') {\n            const columnField = currentCanvasDevice === 'mobile' ? 'MobileColumns' : 'Columns';\n            const gapField = currentCanvasDevice === 'mobile' ? 'MobileColumnGapPx' : 'ColumnGapPx';\n            $bar.append($('<div>', { class: 'h18-canvas-card-grid-controls' }).append(\n                $('<strong>', { text: 'Kort-række' }),\n                canvasQuickRange('Kolonner', columnField, canvasNumber($row, columnField, currentCanvasDevice === 'mobile' ? 1 : 3), 1, 6, ''),\n                canvasQuickRange('Mellemrum', gapField, canvasNumber($row, gapField, currentCanvasDevice === 'mobile' ? 14 : 16), 0, 60, ' px')\n            ));\n        }\n        $preview.append($bar);\n",
    'grid quick controls'
)

events = r'''
    $(document).on('click keydown', '.h18-canvas-card[data-card-key]', function (event) {
        if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) { return; }
        if ($(event.target).closest('.h18-canvas-card-tools, .h18-canvas-card-drag-handle, .h18-canvas-card-inline-edit.is-editing, .h18-canvas-card-rich-edit.is-editing').length) { return; }
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        inspectPageSection($row);
        selectedCanvasCardKey = String($(this).data('card-key') || '');
        canvasFocusCardEditor($row, selectedCanvasCardKey);
        renderCanvasPreview($row);
    });

    $(document).on('click pointerdown', '.h18-canvas-card-tools, .h18-canvas-card-drag-handle', function (event) { event.stopPropagation(); });

    $(document).on('dblclick', '.h18-canvas-card-inline-edit', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        selectedCanvasCardKey = String($(this).closest('.h18-canvas-card').data('card-key') || '');
        inspectPageSection($row); canvasFocusCardEditor($row, selectedCanvasCardKey);
        $(this).data('canvas-original-card-text', String($(this).text() || '')).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });

    $(document).on('input', '.h18-canvas-card-inline-edit.is-editing', function () {
        const $editable = $(this), $row = $editable.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
        if (!$card.length) { return; }
        const value = String($editable.text() || '').replace(/\s+/g, ' ').trim();
        canvasCardSetField($card, 'Title', value); $card.find('.h18-page-card-title-summary').text(value || 'Uden overskrift');
    });

    $(document).on('blur', '.h18-canvas-card-inline-edit.is-editing', function () { const $row = $(this).closest('.h18-page-section-row'); $(this).attr('contenteditable', 'false').removeClass('is-editing'); renderCanvasPreview($row); });

    $(document).on('keydown', '.h18-canvas-card-inline-edit.is-editing', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) { event.preventDefault(); $(this).trigger('blur'); }
        else if (event.key === 'Escape') {
            event.preventDefault();
            const $editable = $(this), $row = $editable.closest('.h18-page-section-row');
            const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
            const original = String($editable.data('canvas-original-card-text') || '');
            if ($card.length) { canvasCardSetField($card, 'Title', original); $card.find('.h18-page-card-title-summary').text(original || 'Uden overskrift'); }
            renderCanvasPreview($row);
        }
    });

    $(document).on('dblclick', '.h18-canvas-card-rich-edit', function (event) {
        event.preventDefault(); event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        selectedCanvasCardKey = String($(this).closest('.h18-canvas-card').data('card-key') || '');
        inspectPageSection($row); canvasFocusCardEditor($row, selectedCanvasCardKey);
        $(this).data('canvas-original-card-html', String($(this).hasClass('is-empty') ? '' : ($(this).html() || '')));
        if ($(this).hasClass('is-empty')) { $(this).empty().removeClass('is-empty'); }
        $(this).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });

    $(document).on('input', '.h18-canvas-card-rich-edit.is-editing', function () {
        const $editable = $(this), $row = $editable.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
        if ($card.length) { canvasCardSetField($card, 'Content', String($editable.html() || '')); }
    });

    $(document).on('blur', '.h18-canvas-card-rich-edit.is-editing', function () { const $row = $(this).closest('.h18-page-section-row'); $(this).attr('contenteditable', 'false').removeClass('is-editing'); renderCanvasPreview($row); });

    $(document).on('keydown', '.h18-canvas-card-rich-edit.is-editing', function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') { event.preventDefault(); $(this).trigger('blur'); }
        else if (event.key === 'Escape') {
            event.preventDefault();
            const $editable = $(this), $row = $editable.closest('.h18-page-section-row');
            const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
            if ($card.length) { canvasCardSetField($card, 'Content', String($editable.data('canvas-original-card-html') || '')); }
            renderCanvasPreview($row);
        }
    });

    $(document).on('input', '.h18-canvas-card-range input[type=range]', function (event) {
        event.stopPropagation();
        const $input = $(this), $previewCard = $input.closest('.h18-canvas-card'), $row = $previewCard.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($previewCard.data('card-key') || ''));
        if (!$card.length) { return; }
        const value = parseInt($input.val(), 10) || 0;
        canvasCardSetField($card, String($input.data('card-control-field') || ''), value);
        $input.closest('.h18-canvas-card-range').find('output').text(value + ' px');
        canvasApplyCardPreviewStyle($card, $previewCard);
    });

    $(document).on('change', '.h18-canvas-card-control', function (event) {
        event.stopPropagation();
        const $control = $(this), $previewCard = $control.closest('.h18-canvas-card'), $row = $previewCard.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($previewCard.data('card-key') || ''));
        if (!$card.length) { return; }
        canvasCardSetField($card, String($control.data('card-control-field') || ''), $control.is(':checkbox') ? $control.is(':checked') : $control.val());
        renderCanvasPreview($row); canvasFocusCardEditor($row, selectedCanvasCardKey);
    });

    $(document).on('change', '.h18-canvas-card-range input[type=range]', function () { renderCanvasPreview($(this).closest('.h18-page-section-row')); });

'''
js = replace_once(js, "    $(document).on('dblclick', '.h18-canvas-inline-edit', function (event) {\n", events + "    $(document).on('dblclick', '.h18-canvas-inline-edit', function (event) {\n", 'card events')

js_path.write_text(js, encoding='utf-8')
