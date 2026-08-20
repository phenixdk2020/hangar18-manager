jQuery(function ($) {
    'use strict';

    const config = window.H18LegoDesignV0832 || {};
    const $form = $('#h18-page-editor-form');
    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector');
    const $inspectorTarget = $('#h18-page-inspector-target');
    if (!$form.length || !$sections.length || !$inspector.length) {
        return;
    }

    const PANEL_ID = 'h18-ud-lego-design-panel';
    const fieldMap = config.fieldMap && typeof config.fieldMap === 'object' ? config.fieldMap : {};
    const fonts = Array.isArray(config.fonts) && config.fonts.length ? config.fonts : ['Global', 'System', 'Segoe UI', 'Arial', 'Verdana', 'Tahoma', 'Trebuchet MS', 'Georgia', 'Times New Roman', 'Courier New'];
    const shadows = Array.isArray(config.shadows) && config.shadows.length ? config.shadows : ['None', 'Soft', 'Medium', 'Strong'];
    const hoverEffects = Array.isArray(config.hoverEffects) && config.hoverEffects.length ? config.hoverEffects : ['None', 'Lift', 'Scale', 'Shadow'];
    let refreshTimer = null;

    function selectedRow() {
        return $sections.find('.h18-page-section-row.is-selected').first();
    }

    function rowBody($row) {
        if (!$row || !$row.length) { return $(); }
        const $direct = $row.children('.h18-page-section-body').first();
        return $direct.length ? $direct : $row.find('.h18-page-section-body').first();
    }

    function rowField($row, fieldName) {
        if (!$row || !$row.length || !fieldName) { return $(); }
        const selector = '[name$="[' + fieldName + ']"]';
        const $body = rowBody($row);
        let $field = $body.find(selector).first();
        if (!$field.length) { $field = $row.find(selector).first(); }
        return $field;
    }

    function mirrorFields($row, fieldName) {
        if (!$row || !$row.length || !fieldName || !$row.hasClass('is-selected')) { return $(); }
        return $inspectorTarget.find('[name$="[' + fieldName + ']"]');
    }

    function rowType($row) {
        const $type = rowField($row, 'Type');
        return String($row.attr('data-section-type') || ($type.length ? $type.val() : '') || 'text');
    }

    function isKasse($row) {
        return ['container', 'grid', 'flex'].indexOf(rowType($row)) !== -1;
    }

    function clamp(value, min, max, fallback) {
        const parsed = parseInt(value, 10);
        if (!Number.isFinite(parsed)) { return fallback; }
        return Math.max(min, Math.min(max, parsed));
    }

    function enumValue(value, allowed, fallback) {
        value = String(value || '');
        return allowed.indexOf(value) !== -1 ? value : fallback;
    }

    function colorValue(value, fallback) {
        value = String(value || '').toLowerCase().trim();
        return /^#[0-9a-f]{6}$/.test(value) ? value : fallback;
    }

    function legacyValue($row, fieldName, fallback) {
        const $field = rowField($row, fieldName);
        return $field.length ? $field.val() : fallback;
    }

    function stateForRow($row) {
        return {
            SchemaVersion: 1,
            Mode: enumValue(legacyValue($row, 'DesignMode', 'Global'), ['Global', 'Custom'], 'Global'),
            Colors: {
                Background: colorValue(legacyValue($row, 'CustomBackgroundColor', '#ffffff'), '#ffffff'),
                Text: colorValue(legacyValue($row, 'CustomTextColor', '#30382a'), '#30382a'),
                Heading: colorValue(legacyValue($row, 'CustomHeadingColor', '#30382a'), '#30382a')
            },
            Border: {
                Width: clamp(legacyValue($row, 'BorderWidthPx', 0), 0, 12, 0),
                Color: colorValue(legacyValue($row, 'CustomBorderColor', '#c3ae83'), '#c3ae83')
            },
            Radius: {
                All: clamp(legacyValue($row, 'RadiusPx', 7), 0, 30, 7),
                TopLeft: clamp(legacyValue($row, 'RadiusTopLeftPx', -1), -1, 60, -1),
                TopRight: clamp(legacyValue($row, 'RadiusTopRightPx', -1), -1, 60, -1),
                BottomRight: clamp(legacyValue($row, 'RadiusBottomRightPx', -1), -1, 60, -1),
                BottomLeft: clamp(legacyValue($row, 'RadiusBottomLeftPx', -1), -1, 60, -1)
            },
            Typography: {
                BodyFont: enumValue(legacyValue($row, 'SectionBodyFontFamily', 'Global'), fonts, 'Global'),
                HeadingFont: enumValue(legacyValue($row, 'SectionHeadingFontFamily', 'Global'), fonts, 'Global'),
                BodySize: clamp(legacyValue($row, 'BodyFontSizePx', 0), 0, 32, 0),
                H1Size: clamp(legacyValue($row, 'H1FontSizePx', 0), 0, 96, 0),
                H2Size: clamp(legacyValue($row, 'H2FontSizePx', 0), 0, 80, 0),
                H3Size: clamp(legacyValue($row, 'H3FontSizePx', 0), 0, 64, 0)
            },
            Effects: {
                Opacity: clamp(legacyValue($row, 'SectionOpacityPercent', 100), 0, 100, 100),
                Shadow: enumValue(legacyValue($row, 'ShadowStyle', 'None'), shadows, 'None')
            },
            States: {
                Hover: {
                    Mode: enumValue(legacyValue($row, 'HoverStyleMode', 'Inherit'), ['Inherit', 'Custom'], 'Inherit'),
                    Background: colorValue(legacyValue($row, 'HoverBackgroundColor', '#ffffff'), '#ffffff'),
                    Text: colorValue(legacyValue($row, 'HoverTextColor', '#30382a'), '#30382a'),
                    Heading: colorValue(legacyValue($row, 'HoverHeadingColor', '#30382a'), '#30382a'),
                    Border: colorValue(legacyValue($row, 'HoverBorderColor', '#c3ae83'), '#c3ae83'),
                    Opacity: clamp(legacyValue($row, 'HoverOpacityPercent', 100), 0, 100, 100),
                    Effect: enumValue(legacyValue($row, 'HoverEffect', 'None'), hoverEffects, 'None'),
                    TransitionMs: clamp(legacyValue($row, 'HoverTransitionMs', 220), 0, 1000, 220)
                }
            }
        };
    }

    function valueAt(state, path) {
        return String(path || '').split('.').reduce(function (current, part) {
            return current && typeof current === 'object' ? current[part] : undefined;
        }, state);
    }

    function markRow($row) {
        if (!$row || !$row.length) { return; }
        const state = stateForRow($row);
        $row.attr('data-h18-lego-design', '1');
        $row.attr('data-h18-lego-design-role', isKasse($row) ? 'kasse' : 'element');
        $row.attr('data-h18-lego-design-mode', state.Mode.toLowerCase());
        $row.attr('data-h18-lego-hover-mode', state.States.Hover.Mode.toLowerCase());
        // Debug/QA mirror only; the persisted legacy fields remain authoritative.
        $row.attr('data-h18-lego-design-state', JSON.stringify(state));
    }

    function setFieldSilently($row, fieldName, value) {
        const $actual = rowField($row, fieldName);
        if (!$actual.length) { return false; }
        if ($actual.is(':checkbox')) {
            $actual.prop('checked', Boolean(value));
            mirrorFields($row, fieldName).prop('checked', Boolean(value));
        } else {
            $actual.val(String(value));
            mirrorFields($row, fieldName).val(String(value));
        }
        return true;
    }

    function refreshLegacyModeUi($row) {
        const mode = String(legacyValue($row, 'DesignMode', 'Global'));
        const hoverMode = String(legacyValue($row, 'HoverStyleMode', 'Inherit'));
        rowBody($row).find('.h18-custom-design-fields').toggle(mode === 'Custom');
        rowBody($row).find('.h18-hover-style-fields').toggle(hoverMode === 'Custom');
        if ($row.hasClass('is-selected')) {
            $inspectorTarget.find('.h18-custom-design-fields').toggle(mode === 'Custom');
            $inspectorTarget.find('.h18-hover-style-fields').toggle(hoverMode === 'Custom');
        }
    }

    function writeLegacyField($row, fieldName, value, eventType) {
        const $actual = rowField($row, fieldName);
        if (!$actual.length) { return false; }
        setFieldSilently($row, fieldName, value);
        markRow($row);
        refreshLegacyModeUi($row);
        // One existing form event per LEGO user action. admin.js/v0.8.23 remains
        // the sole history owner and sees all silent companion changes in the DOM.
        $actual.trigger(eventType === 'change' ? 'change' : 'input');
        return true;
    }

    function pathNeedsCustomMode(path) {
        return /^Colors\./.test(path) || /^Border\./.test(path) || /^Radius\./.test(path) || /^Typography\./.test(path) || /^Effects\./.test(path);
    }

    function pathNeedsHoverCustom(path) {
        return /^States\.Hover\.(Background|Text|Heading|Border|Opacity)$/.test(path);
    }

    function prepareCompanionState($row, path) {
        if (pathNeedsCustomMode(path) && String(legacyValue($row, 'DesignMode', 'Global')) !== 'Custom') {
            setFieldSilently($row, 'DesignMode', 'Custom');
        }
        if (pathNeedsHoverCustom(path) && String(legacyValue($row, 'HoverStyleMode', 'Inherit')) !== 'Custom') {
            setFieldSilently($row, 'HoverStyleMode', 'Custom');
        }
    }

    function controlShell(label, help) {
        const $label = $('<label>', { class: 'h18-ud-lego-design-control' });
        $label.append($('<strong>', { text: label }));
        if (help) { $label.append($('<small>', { text: help })); }
        return $label;
    }

    function selectControl(label, path, value, options, help) {
        const $label = controlShell(label, help);
        const $select = $('<select>', { 'data-h18-lego-design-path': path });
        options.forEach(function (option) {
            const raw = typeof option === 'string' ? option : option.value;
            const text = typeof option === 'string' ? option : option.label;
            $select.append($('<option>', { value: raw, text: text, selected: String(raw) === String(value) }));
        });
        $label.append($select);
        return $label;
    }

    function numberControl(label, path, value, min, max, suffix, help) {
        const $label = controlShell(label, help);
        const $wrap = $('<span>', { class: 'h18-ud-lego-design-number' });
        $wrap.append($('<input>', {
            type: 'number', min: min, max: max, step: 1, value: value,
            'data-h18-lego-design-path': path
        }));
        if (suffix) { $wrap.append($('<em>', { text: suffix })); }
        $label.append($wrap);
        return $label;
    }

    function colorControl(label, path, value, help) {
        const $label = controlShell(label, help);
        $label.append($('<input>', {
            type: 'color', value: value,
            'data-h18-lego-design-path': path
        }));
        return $label;
    }

    function group(title, description) {
        const $group = $('<fieldset>', { class: 'h18-ud-lego-design-group' });
        $group.append($('<legend>', { text: title }));
        if (description) { $group.append($('<p>', { class: 'description', text: description })); }
        $group.append($('<div>', { class: 'h18-ud-lego-design-grid' }));
        return $group;
    }

    function renderPanel() {
        $('#' + PANEL_ID).remove();
        const $row = selectedRow();
        if (!$row.length) { return; }
        markRow($row);
        const state = stateForRow($row);
        const $panel = $('<section>', {
            id: PANEL_ID,
            class: 'h18-section-module-box h18-canvas-direct-controls h18-ud-lego-design-panel',
            'data-h18-lego-design-role': isKasse($row) ? 'kasse' : 'element'
        });

        $panel.append(
            $('<div>', { class: 'h18-ud-lego-design-heading' }).append(
                $('<div>').append(
                    $('<h4>', { text: 'LEGO-design' }),
                    $('<p>', {
                        class: 'description',
                        text: 'Samme designmodel bruges af ' + (isKasse($row) ? 'Kasse/Grid/Flex' : 'almindelige elementer') + '. Felterne gemmes fortsat i det eksisterende side-schema.'
                    })
                ),
                $('<span>', { class: 'h18-ud-lego-design-badge', text: '0.8.32' })
            )
        );

        const $source = group('Designkilde', 'Global bruger det centrale designsystem. Tilpasset bruger værdierne nedenfor.');
        $source.children('.h18-ud-lego-design-grid').append(
            selectControl('Normal', 'Mode', state.Mode, [
                { value: 'Global', label: 'Global design' },
                { value: 'Custom', label: 'Tilpasset' }
            ])
        );
        $panel.append($source);

        const $colors = group('Farver og kant', 'En ændring her skifter automatisk Normal til Tilpasset i samme Undo/Redo-handling.');
        $colors.children('.h18-ud-lego-design-grid').append(
            colorControl('Baggrund', 'Colors.Background', state.Colors.Background),
            colorControl('Tekst', 'Colors.Text', state.Colors.Text),
            colorControl('Overskrift', 'Colors.Heading', state.Colors.Heading),
            colorControl('Kantfarve', 'Border.Color', state.Border.Color),
            numberControl('Kantbredde', 'Border.Width', state.Border.Width, 0, 12, 'px')
        );
        $panel.append($colors);

        const $typography = group('Typografi', '0 px og Global font arver fra det centrale designsystem.');
        $typography.children('.h18-ud-lego-design-grid').append(
            selectControl('Brødtekst-font', 'Typography.BodyFont', state.Typography.BodyFont, fonts),
            selectControl('Overskrift-font', 'Typography.HeadingFont', state.Typography.HeadingFont, fonts),
            numberControl('Brødtekst', 'Typography.BodySize', state.Typography.BodySize, 0, 32, 'px'),
            numberControl('H1', 'Typography.H1Size', state.Typography.H1Size, 0, 96, 'px'),
            numberControl('H2', 'Typography.H2Size', state.Typography.H2Size, 0, 80, 'px'),
            numberControl('H3', 'Typography.H3Size', state.Typography.H3Size, 0, 64, 'px')
        );
        $panel.append($typography);

        const $shape = group('Form og effekter', '-1 på et individuelt hjørne betyder: brug den fælles radius.');
        $shape.children('.h18-ud-lego-design-grid').append(
            numberControl('Radius alle', 'Radius.All', state.Radius.All, 0, 30, 'px'),
            numberControl('Top venstre', 'Radius.TopLeft', state.Radius.TopLeft, -1, 60, 'px'),
            numberControl('Top højre', 'Radius.TopRight', state.Radius.TopRight, -1, 60, 'px'),
            numberControl('Bund højre', 'Radius.BottomRight', state.Radius.BottomRight, -1, 60, 'px'),
            numberControl('Bund venstre', 'Radius.BottomLeft', state.Radius.BottomLeft, -1, 60, 'px'),
            selectControl('Skygge', 'Effects.Shadow', state.Effects.Shadow, shadows),
            numberControl('Opacitet', 'Effects.Opacity', state.Effects.Opacity, 0, 100, '%')
        );
        $panel.append($shape);

        const hover = state.States.Hover;
        const $hover = group('Hover-state', 'Arv Normal bruger normal-state. Tilpassede hover-farver bevarer normal-state urørt.');
        $hover.attr('data-h18-lego-hover-custom', hover.Mode === 'Custom' ? '1' : '0');
        $hover.children('.h18-ud-lego-design-grid').append(
            selectControl('Farver', 'States.Hover.Mode', hover.Mode, [
                { value: 'Inherit', label: 'Arv Normal' },
                { value: 'Custom', label: 'Tilpasset' }
            ]),
            selectControl('Effekt', 'States.Hover.Effect', hover.Effect, hoverEffects),
            numberControl('Transition', 'States.Hover.TransitionMs', hover.TransitionMs, 0, 1000, 'ms'),
            colorControl('Baggrund', 'States.Hover.Background', hover.Background),
            colorControl('Tekst', 'States.Hover.Text', hover.Text),
            colorControl('Overskrift', 'States.Hover.Heading', hover.Heading),
            colorControl('Kant', 'States.Hover.Border', hover.Border),
            numberControl('Opacitet', 'States.Hover.Opacity', hover.Opacity, 0, 100, '%')
        );
        $panel.append($hover);

        $panel.append($('<p>', {
            class: 'description h18-ud-lego-design-note',
            text: 'LEGO-afstand X/Y forbliver i spacing-panelet. v0.8.32 konsoliderer kun design-sproget; public renderer, drag/drop, parent/child og history-motor ændres ikke.'
        }));
        $inspector.append($panel);
    }

    function normalizeInputValue(path, raw) {
        if (/^(Colors\.|Border\.Color|States\.Hover\.(Background|Text|Heading|Border))/.test(path)) {
            return colorValue(raw, '#ffffff');
        }
        if (path === 'Mode') { return enumValue(raw, ['Global', 'Custom'], 'Global'); }
        if (path === 'Typography.BodyFont' || path === 'Typography.HeadingFont') { return enumValue(raw, fonts, 'Global'); }
        if (path === 'Effects.Shadow') { return enumValue(raw, shadows, 'None'); }
        if (path === 'States.Hover.Mode') { return enumValue(raw, ['Inherit', 'Custom'], 'Inherit'); }
        if (path === 'States.Hover.Effect') { return enumValue(raw, hoverEffects, 'None'); }
        const limits = {
            'Border.Width': [0, 12, 0],
            'Radius.All': [0, 30, 7],
            'Radius.TopLeft': [-1, 60, -1],
            'Radius.TopRight': [-1, 60, -1],
            'Radius.BottomRight': [-1, 60, -1],
            'Radius.BottomLeft': [-1, 60, -1],
            'Typography.BodySize': [0, 32, 0],
            'Typography.H1Size': [0, 96, 0],
            'Typography.H2Size': [0, 80, 0],
            'Typography.H3Size': [0, 64, 0],
            'Effects.Opacity': [0, 100, 100],
            'States.Hover.Opacity': [0, 100, 100],
            'States.Hover.TransitionMs': [0, 1000, 220]
        };
        const limit = limits[path] || [0, 9999, 0];
        return clamp(raw, limit[0], limit[1], limit[2]);
    }

    $(document).on('input change', '#' + PANEL_ID + ' [data-h18-lego-design-path]', function (event) {
        const $row = selectedRow();
        if (!$row.length) { return; }
        const path = String($(this).attr('data-h18-lego-design-path') || '');
        const fieldName = String(fieldMap[path] || '');
        if (!fieldName) { return; }
        const value = normalizeInputValue(path, $(this).val());
        prepareCompanionState($row, path);
        const eventType = path === 'Mode' || path === 'States.Hover.Mode' ? 'change' : 'input';
        writeLegacyField($row, fieldName, value, eventType);
        // Do not rebuild on every keystroke. Color/select/number commits are reflected
        // immediately in legacy preview through the existing delegated editor handlers.
        if (event.type === 'change' || $(this).is('[type=color],select')) {
            renderPanel();
        } else {
            markRow($row);
        }
    });

    const mappedFields = Object.keys(fieldMap).map(function (path) { return fieldMap[path]; }).filter(Boolean);
    const mappedSelector = mappedFields.map(function (name) { return '[name$="[' + name + ']"]'; }).join(',');
    if (mappedSelector) {
        $form.on('input change', mappedSelector, function (event) {
            if ($(event.target).closest('#' + PANEL_ID).length) { return; }
            const $row = $(event.target).closest('.h18-page-section-row');
            if ($row.length) { markRow($row); }
            window.clearTimeout(refreshTimer);
            refreshTimer = window.setTimeout(renderPanel, 45);
        });
    }

    $(document).on(
        'click',
        '.h18-page-section-header,.h18-page-section-edit,.h18-v0811-edit-child,.h18-ud-auto-box-tile,.h18-ud-box-child-chip,.h18-navigator-select',
        function () {
            window.clearTimeout(refreshTimer);
            refreshTimer = window.setTimeout(renderPanel, 55);
        }
    );

    const observer = new MutationObserver(function (mutations) {
        const relevant = mutations.some(function (mutation) {
            return mutation.type === 'childList' || (mutation.type === 'attributes' && mutation.attributeName === 'class');
        });
        if (!relevant) { return; }
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(function () {
            $sections.find('.h18-page-section-row').each(function () { markRow($(this)); });
            renderPanel();
        }, 65);
    });
    observer.observe($sections.get(0), { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    if ($inspectorTarget.length) {
        observer.observe($inspectorTarget.get(0), { childList: true, subtree: true });
    }

    $sections.find('.h18-page-section-row').each(function () { markRow($(this)); });
    renderPanel();

    window.__h18LegoDesignV0832 = {
        version: '0.8.32',
        schemaVersion: 1,
        stateForSelectedRow: function () {
            const $row = selectedRow();
            return $row.length ? stateForRow($row) : null;
        },
        fieldMap: fieldMap
    };
});
