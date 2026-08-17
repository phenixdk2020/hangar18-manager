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


php_path = Path('hangar18-manager.php')
php = php_path.read_text(encoding='utf-8')
php = replace_once(php, ' * Version: 0.5.8', ' * Version: 0.5.9', 'plugin header')
php = replace_once(php, "    const VERSION = '0.5.8';", "    const VERSION = '0.5.9';", 'plugin const')
php_path.write_text(php, encoding='utf-8')

js_path = Path('assets/admin.js')
js = js_path.read_text(encoding='utf-8')
js = replace_once(
    js,
    "    let currentCanvasDevice = 'desktop';\n    let currentCanvasState = 'normal';\n",
    "    let currentCanvasDevice = 'desktop';\n    let currentCanvasState = 'normal';\n    let selectedCanvasCardKey = '';\n",
    'canvas card selection state'
)

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
                    'data-card-key': key,
                    tabindex: '0',
                    role: 'button',
                    'aria-label': 'Kort ' + (String(canvasCardFieldValue($card, 'Title', '')) || 'uden overskrift')
                });
                $cardPreview.append($('<button>', {
                    type: 'button', class: 'h18-canvas-card-drag-handle', title: 'Træk for at flytte kort', 'aria-label': 'Flyt kort'
                }).append($('<span>', { class: 'dashicons dashicons-move' })));
                const titleValue = String(canvasCardFieldValue($card, 'Title', ''));
                const $title = $('<strong>', {
                    class: 'h18-canvas-card-title h18-canvas-card-inline-edit',
                    text: titleValue || 'Kort uden overskrift',
                    'data-card-edit-field': 'Title',
                    contenteditable: 'false',
                    spellcheck: 'true',
                    title: 'Dobbeltklik for at redigere kortets overskrift'
                });
                $cardPreview.append($title);
                const contentHtml = String(canvasCardFieldValue($card, 'Content', '') || '').trim();
                if (contentHtml) {
                    $cardPreview.append($('<div>', {
                        class: 'h18-canvas-card-content h18-canvas-card-rich-edit',
                        'data-card-edit-field': 'Content',
                        contenteditable: 'false',
                        spellcheck: 'true',
                        title: 'Dobbeltklik for at redigere kortets tekst'
                    }).html(contentHtml));
                } else {
                    $cardPreview.append($('<div>', {
                        class: 'h18-canvas-card-content h18-canvas-card-rich-edit is-empty',
                        'data-card-edit-field': 'Content',
                        contenteditable: 'false',
                        spellcheck: 'true',
                        text: 'Dobbeltklik for at tilføje tekst'
                    }));
                }
                if (!active) {
                    $cardPreview.append($('<span>', { class: 'h18-canvas-card-inactive-label', text: 'Skjult på siden' }));
                }
                canvasApplyCardPreviewStyle($card, $cardPreview);
                if (selectedCanvasCardKey === key) {
                    canvasBuildCardTools($card, $cardPreview);
                }
                $grid.append($cardPreview);
            });
            if (!$grid.children().length) { $grid.append($('<div>', { class: 'h18-canvas-card', text: 'Tilføj et kort i Inspector' })); }
            $inner.append($grid);
'''
js = replace_between(
    js,
    "        } else if (type === 'card_grid') {\n",
    "        } else if (type === 'mail_form') {\n",
    card_block,
    'card grid preview block'
)

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
        if ($field.is(':checkbox')) {
            $field.prop('checked', Boolean(value));
        } else {
            $field.val(value);
        }
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
        if (tone === 'Light' || (tone === 'Auto' && ['Olive', 'Steel'].includes(background))) { return '#ffffff'; }
        return '#30382a';
    }

    function canvasFindCardRow($row, cardKey) {
        let $match = $();
        pageSectionControls($row, '.h18-page-card-row:not(.h18-page-card-removed)').each(function () {
            const $card = $(this);
            if (canvasCardKey($card) === String(cardKey || '')) {
                $match = $card;
                return false;
            }
        });
        return $match;
    }

    function canvasApplyCardPreviewStyle($card, $cardPreview) {
        if (!$card.length || !$cardPreview.length) { return; }
        const mobile = currentCanvasDevice === 'mobile';
        const background = canvasPaletteColor(canvasCardFieldValue($card, 'Background', 'OffWhite'));
        const text = canvasCardTextColor($card);
        const borderWidth = Math.max(0, Math.min(8, canvasCardNumber($card, 'BorderWidthPx', 0)));
        const paddingField = mobile ? 'MobilePaddingPx' : 'PaddingPx';
        const paddingMax = mobile ? 60 : 80;
        const padding = Math.max(0, Math.min(paddingMax, canvasCardNumber($card, paddingField, mobile ? 20 : 26)));
        const radius = Math.max(0, Math.min(30, canvasCardNumber($card, 'RadiusPx', 7)));
        const alignField = mobile ? 'MobileAlignment' : 'DesktopAlignment';
        const align = String(canvasCardFieldValue($card, alignField, 'Left')) === 'Center' ? 'center' : 'left';
        $cardPreview.css({
            background: background,
            color: text,
            borderStyle: 'solid',
            borderWidth: borderWidth + 'px',
            borderColor: canvasCardBorderColor(canvasCardFieldValue($card, 'BorderColor', 'Sand')),
            padding: padding + 'px',
            borderRadius: radius + 'px',
            textAlign: align
        });
    }

    function canvasCardRange(label, fieldName, value, min, max, suffix) {
        return $('<label>', { class: 'h18-canvas-card-range' }).append(
            $('<span>', { text: label }),
            $('<input>', { type: 'range', min: min, max: max, step: 1, value: Math.round(value), 'data-card-control-field': fieldName }),
            $('<output>', { text: Math.round(value) + (suffix || '') })
        );
    }

    function canvasCardSelect(label, fieldName, value, options) {
        const $select = $('<select>', { class: 'h18-canvas-card-control', 'data-card-control-field': fieldName });
        options.forEach(function (option) {
            $select.append($('<option>', { value: option[0], text: option[1], selected: String(value) === String(option[0]) }));
        });
        return $('<label>', { class: 'h18-canvas-card-select' }).append($('<span>', { text: label }), $select);
    }

    function canvasBuildCardTools($card, $cardPreview) {
        const mobile = currentCanvasDevice === 'mobile';
        const paddingField = mobile ? 'MobilePaddingPx' : 'PaddingPx';
        const alignField = mobile ? 'MobileAlignment' : 'DesktopAlignment';
        const $tools = $('<div>', { class: 'h18-canvas-card-tools' }).append(
            $('<strong>', { text: 'Kortdesign' }),
            canvasCardSelect('Baggrund', 'Background', canvasCardFieldValue($card, 'Background', 'OffWhite'), [
                ['White', 'Hvid'], ['OffWhite', 'Knækket hvid'], ['Sand', 'Sand'], ['Olive', 'Oliven'], ['Steel', 'Stål']
            ]),
            canvasCardSelect('Tekst', 'TextTone', canvasCardFieldValue($card, 'TextTone', 'Auto'), [
                ['Auto', 'Auto'], ['Dark', 'Mørk'], ['Light', 'Lys']
            ]),
            canvasCardSelect('Placering', alignField, canvasCardFieldValue($card, alignField, 'Left'), [
                ['Left', 'Venstre'], ['Center', 'Midt']
            ]),
            canvasCardRange('Padding', paddingField, canvasCardNumber($card, paddingField, mobile ? 20 : 26), 0, mobile ? 60 : 80, ' px'),
            canvasCardRange('Radius', 'RadiusPx', canvasCardNumber($card, 'RadiusPx', 7), 0, 30, ' px'),
            canvasCardRange('Kant', 'BorderWidthPx', canvasCardNumber($card, 'BorderWidthPx', 0), 0, 8, ' px'),
            $('<label>', { class: 'h18-canvas-card-active' }).append(
                $('<input>', { type: 'checkbox', class: 'h18-canvas-card-control', 'data-card-control-field': 'Active', checked: Boolean(canvasCardFieldValue($card, 'Active', true)) }),
                $('<span>', { text: 'Aktiv' })
            )
        );
        $cardPreview.append($tools);
    }

    function canvasFocusCardEditor($row, cardKey) {
        pageSectionControls($row, '.h18-page-card-row').removeClass('is-canvas-selected-card');
        const $card = canvasFindCardRow($row, cardKey);
        if ($card.length) {
            $card.addClass('is-canvas-selected-card');
            const title = String(canvasCardFieldValue($card, 'Title', '') || 'Kort uden overskrift');
            $pageInspector.find('.h18-builder-inspector-heading span').text('Kort-række · ' + title);
        }
        return $card;
    }

    function initializeCanvasCardGridPreview($row, $preview) {
        const $grid = $preview.find('.h18-canvas-card-grid');
        if (!$grid.length || $grid.hasClass('ui-sortable')) { return; }
        $grid.sortable({
            items: '> .h18-canvas-card[data-card-key]',
            handle: '.h18-canvas-card-drag-handle',
            tolerance: 'pointer',
            placeholder: 'h18-canvas-card-sort-placeholder',
            start: function () { $grid.addClass('is-sorting'); },
            stop: function () { $grid.removeClass('is-sorting'); },
            update: function () {
                const keys = $grid.children('.h18-canvas-card[data-card-key]').map(function () { return String($(this).data('card-key') || ''); }).get();
                const $container = pageSectionControls($row, '.h18-page-cards-sortable').first();
                keys.forEach(function (key) {
                    const $card = canvasFindCardRow($row, key);
                    if ($card.length) { $container.append($card); }
                });
                syncPageCardOrder($container);
                renderCanvasPreview($row);
            }
        });
    }

'''
js = replace_once(js, "    function ensureCanvasPreview($row) {\n", helpers + "    function ensureCanvasPreview($row) {\n", 'card helper insertion')

js = replace_once(
    js,
    "        canvasBuildPreviewContent($row, $preview);\n        $preview.removeAttr('style').css({\n",
    "        canvasBuildPreviewContent($row, $preview);\n        initializeCanvasCardGridPreview($row, $preview);\n        $preview.removeAttr('style').css({\n",
    'card sortable initialization'
)

js = replace_once(
    js,
    "        $bar.append($('<strong>', { class: 'h18-canvas-direct-title', text: 'Direkte design' }), $ranges, $colors);\n        $preview.append($bar);\n",
    "        $bar.append($('<strong>', { class: 'h18-canvas-direct-title', text: 'Direkte design' }), $ranges, $colors);\n        if (String($row.attr('data-section-type') || '') === 'card_grid') {\n            const columnField = currentCanvasDevice === 'mobile' ? 'MobileColumns' : 'Columns';\n            const gapField = currentCanvasDevice === 'mobile' ? 'MobileColumnGapPx' : 'ColumnGapPx';\n            const columnValue = canvasNumber($row, columnField, currentCanvasDevice === 'mobile' ? 1 : 3);\n            const gapValue = canvasNumber($row, gapField, currentCanvasDevice === 'mobile' ? 14 : 16);\n            $bar.append($('<div>', { class: 'h18-canvas-card-grid-controls' }).append(\n                $('<strong>', { text: 'Kort-række' }),\n                canvasQuickRange('Kolonner', columnField, columnValue, 1, 6, ''),\n                canvasQuickRange('Mellemrum', gapField, gapValue, 0, 60, ' px')\n            ));\n        }\n        $preview.append($bar);\n",
    'card grid quick controls'
)

events = r'''
    $(document).on('click keydown', '.h18-canvas-card[data-card-key]', function (event) {
        if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) { return; }
        if ($(event.target).closest('.h18-canvas-card-tools, .h18-canvas-card-drag-handle, .h18-canvas-card-inline-edit.is-editing, .h18-canvas-card-rich-edit.is-editing').length) { return; }
        event.preventDefault();
        event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        inspectPageSection($row);
        selectedCanvasCardKey = String($(this).data('card-key') || '');
        canvasFocusCardEditor($row, selectedCanvasCardKey);
        renderCanvasPreview($row);
    });

    $(document).on('click pointerdown', '.h18-canvas-card-tools, .h18-canvas-card-drag-handle', function (event) {
        event.stopPropagation();
    });

    $(document).on('dblclick', '.h18-canvas-card-inline-edit', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        const key = String($(this).closest('.h18-canvas-card').data('card-key') || '');
        selectedCanvasCardKey = key;
        inspectPageSection($row);
        canvasFocusCardEditor($row, key);
        $(this).data('canvas-original-card-text', String($(this).text() || ''));
        $(this).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });

    $(document).on('input', '.h18-canvas-card-inline-edit.is-editing', function () {
        const $editable = $(this);
        const $row = $editable.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
        if (!$card.length) { return; }
        const value = String($editable.text() || '').replace(/\s+/g, ' ').trim();
        canvasCardSetField($card, String($editable.data('card-edit-field') || 'Title'), value);
        $card.find('.h18-page-card-title-summary').text(value || 'Uden overskrift');
    });

    $(document).on('blur', '.h18-canvas-card-inline-edit.is-editing', function () {
        const $row = $(this).closest('.h18-page-section-row');
        $(this).attr('contenteditable', 'false').removeClass('is-editing');
        renderCanvasPreview($row);
    });

    $(document).on('keydown', '.h18-canvas-card-inline-edit.is-editing', function (event) {
        if (event.key === 'Enter' && !event.shiftKey) {
            event.preventDefault();
            $(this).trigger('blur');
        } else if (event.key === 'Escape') {
            event.preventDefault();
            const $editable = $(this);
            const $row = $editable.closest('.h18-page-section-row');
            const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
            const original = String($editable.data('canvas-original-card-text') || '');
            if ($card.length) {
                canvasCardSetField($card, String($editable.data('card-edit-field') || 'Title'), original);
                $card.find('.h18-page-card-title-summary').text(original || 'Uden overskrift');
            }
            renderCanvasPreview($row);
        }
    });

    $(document).on('dblclick', '.h18-canvas-card-rich-edit', function (event) {
        event.preventDefault();
        event.stopPropagation();
        const $row = $(this).closest('.h18-page-section-row');
        const key = String($(this).closest('.h18-canvas-card').data('card-key') || '');
        selectedCanvasCardKey = key;
        inspectPageSection($row);
        canvasFocusCardEditor($row, key);
        $(this).data('canvas-original-card-html', String($(this).hasClass('is-empty') ? '' : ($(this).html() || '')));
        if ($(this).hasClass('is-empty')) { $(this).empty().removeClass('is-empty'); }
        $(this).attr('contenteditable', 'true').addClass('is-editing').trigger('focus');
    });

    $(document).on('input', '.h18-canvas-card-rich-edit.is-editing', function () {
        const $editable = $(this);
        const $row = $editable.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
        if ($card.length) { canvasCardSetField($card, 'Content', String($editable.html() || '')); }
    });

    $(document).on('blur', '.h18-canvas-card-rich-edit.is-editing', function () {
        const $row = $(this).closest('.h18-page-section-row');
        $(this).attr('contenteditable', 'false').removeClass('is-editing');
        renderCanvasPreview($row);
    });

    $(document).on('keydown', '.h18-canvas-card-rich-edit.is-editing', function (event) {
        if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
            event.preventDefault();
            $(this).trigger('blur');
        } else if (event.key === 'Escape') {
            event.preventDefault();
            const $editable = $(this);
            const $row = $editable.closest('.h18-page-section-row');
            const $card = canvasFindCardRow($row, String($editable.closest('.h18-canvas-card').data('card-key') || ''));
            if ($card.length) { canvasCardSetField($card, 'Content', String($editable.data('canvas-original-card-html') || '')); }
            renderCanvasPreview($row);
        }
    });

    $(document).on('input', '.h18-canvas-card-range input[type=range]', function (event) {
        event.stopPropagation();
        const $input = $(this);
        const $previewCard = $input.closest('.h18-canvas-card');
        const $row = $previewCard.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($previewCard.data('card-key') || ''));
        if (!$card.length) { return; }
        const field = String($input.data('card-control-field') || '');
        const value = parseInt($input.val(), 10) || 0;
        canvasCardSetField($card, field, value);
        $input.closest('.h18-canvas-card-range').find('output').text(value + ' px');
        canvasApplyCardPreviewStyle($card, $previewCard);
    });

    $(document).on('change', '.h18-canvas-card-control', function (event) {
        event.stopPropagation();
        const $control = $(this);
        const $previewCard = $control.closest('.h18-canvas-card');
        const $row = $previewCard.closest('.h18-page-section-row');
        const $card = canvasFindCardRow($row, String($previewCard.data('card-key') || ''));
        if (!$card.length) { return; }
        const field = String($control.data('card-control-field') || '');
        const value = $control.is(':checkbox') ? $control.is(':checked') : $control.val();
        canvasCardSetField($card, field, value);
        renderCanvasPreview($row);
        canvasFocusCardEditor($row, selectedCanvasCardKey);
    });

    $(document).on('change', '.h18-canvas-card-range input[type=range]', function () {
        renderCanvasPreview($(this).closest('.h18-page-section-row'));
    });

'''
js = replace_once(js, "    $(document).on('dblclick', '.h18-canvas-inline-edit', function (event) {\n", events + "    $(document).on('dblclick', '.h18-canvas-inline-edit', function (event) {\n", 'card event insertion')

js_path.write_text(js, encoding='utf-8')

css_path = Path('assets/admin.css')
css = css_path.read_text(encoding='utf-8')
marker = '/* v0.5.9 – direkte Card Grid-redigering */'
if marker not in css:
    css += r'''

/* v0.5.9 – direkte Card Grid-redigering */
.h18-canvas-card{position:relative;min-width:0;transition:outline-color .12s ease,box-shadow .12s ease,opacity .12s ease}
.h18-canvas-card[data-card-key]{cursor:default}
.h18-canvas-card.is-card-selected{outline:3px solid #3858e9;outline-offset:3px;box-shadow:0 10px 28px rgba(56,88,233,.18)}
.h18-canvas-card.is-card-inactive{opacity:.58}
.h18-canvas-card-inactive-label{display:inline-flex;margin-top:8px;padding:3px 7px;border-radius:999px;background:rgba(0,0,0,.10);font-size:10px;font-weight:700}
.h18-canvas-card-drag-handle{position:absolute;z-index:5;top:6px;right:6px;width:28px;height:28px;padding:0;border:1px solid rgba(0,0,0,.18);border-radius:6px;background:rgba(255,255,255,.92);color:#1d2327;cursor:grab;display:flex;align-items:center;justify-content:center}
.h18-canvas-card-drag-handle:active{cursor:grabbing}
.h18-canvas-card-drag-handle .dashicons{width:16px;height:16px;font-size:16px}
.h18-canvas-card-title,.h18-canvas-card-content{display:block;min-width:0}
.h18-canvas-card-title{padding-right:30px}
.h18-canvas-card-content{margin-top:7px}
.h18-canvas-card-content.is-empty{opacity:.65;font-style:italic}
.h18-canvas-card-inline-edit.is-editing,.h18-canvas-card-rich-edit.is-editing{outline:2px dashed currentColor;outline-offset:3px;cursor:text}
.h18-canvas-card-tools{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px;margin-top:12px;padding:9px;border:1px solid rgba(56,88,233,.26);border-radius:7px;background:rgba(255,255,255,.94);color:#1d2327;text-align:left;box-shadow:0 4px 14px rgba(0,0,0,.08)}
.h18-canvas-card-tools>strong{grid-column:1/-1;color:#1935a5;font-size:11px;text-transform:uppercase;letter-spacing:.04em}
.h18-canvas-card-select,.h18-canvas-card-range{display:grid;gap:3px;font-size:10px;font-weight:600}
.h18-canvas-card-select select{width:100%;min-width:0;min-height:28px;font-size:11px}
.h18-canvas-card-range{grid-template-columns:minmax(0,1fr) auto;align-items:center}
.h18-canvas-card-range input{grid-column:1/-1;width:100%}
.h18-canvas-card-range output{font-size:10px;font-variant-numeric:tabular-nums}
.h18-canvas-card-active{display:flex;align-items:center;gap:5px;font-size:11px;font-weight:600}
.h18-canvas-card-sort-placeholder{min-height:90px;border:2px dashed #3858e9;border-radius:7px;background:rgba(56,88,233,.08)}
.h18-canvas-card-grid.is-sorting .h18-canvas-card:not(.ui-sortable-helper){opacity:.72}
.h18-page-card-row.is-canvas-selected-card{border-color:#3858e9;box-shadow:0 0 0 2px rgba(56,88,233,.14)}
.h18-canvas-card-grid-controls{display:grid;grid-template-columns:auto repeat(2,minmax(110px,1fr));gap:8px;align-items:end;margin-top:8px;padding-top:8px;border-top:1px solid rgba(255,255,255,.22)}
.h18-canvas-card-grid-controls>strong{align-self:center;font-size:11px}
@media(max-width:1180px){.h18-canvas-card-tools{grid-template-columns:repeat(2,minmax(0,1fr))}.h18-canvas-card-grid-controls{grid-template-columns:1fr 1fr}.h18-canvas-card-grid-controls>strong{grid-column:1/-1}}
@media(max-width:782px){.h18-canvas-card-tools{grid-template-columns:1fr}.h18-canvas-card-grid-controls{grid-template-columns:1fr}}
'''
css_path.write_text(css, encoding='utf-8')

readme_path = Path('readme.txt')
readme = readme_path.read_text(encoding='utf-8')
readme = replace_once(readme, 'Version: 0.5.8', 'Version: 0.5.9', 'readme version')
section = '''== Version 0.5.9 – Direkte Card Grid-redigering ==\n\nNyt:\n- hvert kort i Card Grid kan vælges direkte i canvas\n- kort kan omarrangeres direkte i canvas med drag-and-drop\n- kortets overskrift og rich-text indhold kan redigeres med dobbeltklik\n- valgt kort får egne hurtigkontroller for baggrund, teksttone, placering, padding, radius, kant og aktiv-status\n- kortdesign følger desktop/mobil-felterne, som allerede fandtes i editorens datamodel\n- Card Grid får direkte kontrol over antal kolonner og mellemrum, så kortbredden kan justeres visuelt\n- valgt kort fremhæves samtidig i Inspector\n- page-editor schema forbliver 1.10; ingen datamigrering er nødvendig\n\n\n'''
readme = replace_once(readme, '== Version 0.5.8 – Direkte canvas-kontroller ==\n', section + '== Version 0.5.8 – Direkte canvas-kontroller ==\n', 'readme changelog insertion')
readme_path.write_text(readme, encoding='utf-8')
