jQuery(function ($) {
    'use strict';

    const config = window.H18LegoResponsiveDesignV0833 || {};
    const $form = $('#h18-page-editor-form');
    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector');
    const $inspectorTarget = $('#h18-page-inspector-target');
    const $canvas = $('.h18-builder-canvas').first();
    if (!$form.length || !$sections.length || !$inspector.length) { return; }

    const PANEL_ID = 'h18-ud-lego-responsive-design-panel';
    const STATE_CLASS = 'h18-lego-responsive-design-state-json';
    const SUBMIT_ATTR = 'data-h18-lego-responsive-design-submit';
    const fieldMap = config.fieldMap && typeof config.fieldMap === 'object' ? config.fieldMap : {};
    const fonts = Array.isArray(config.fonts) ? config.fonts : ['Global','System','Segoe UI','Arial','Verdana','Tahoma','Trebuchet MS','Georgia','Times New Roman','Courier New'];
    const shadows = Array.isArray(config.shadows) ? config.shadows : ['None','Soft','Medium','Strong'];
    const hoverEffects = Array.isArray(config.hoverEffects) ? config.hoverEffects : ['None','Lift','Scale','Shadow'];
    let panelDevice = 'Desktop';
    let refreshTimer = null;

    function activeRows() { return $sections.find('.h18-page-section-row:not(.h18-page-section-removed)'); }
    function selectedRow() { return activeRows().filter('.is-selected').first(); }
    function rowBody($row) {
        const $direct = $row.children('.h18-page-section-body').first();
        return $direct.length ? $direct : $row.find('.h18-page-section-body').first();
    }
    function rowField($row, name) {
        if (!$row || !$row.length || !name) { return $(); }
        let $field = rowBody($row).find('[name$="[' + name + ']"]').first();
        if (!$field.length) { $field = $row.find('[name$="[' + name + ']"]').first(); }
        return $field;
    }
    function mirrorFields($row, name) {
        return $row.hasClass('is-selected') ? $inspectorTarget.find('[name$="[' + name + ']"]') : $();
    }
    function rowKey($row) {
        const $key = rowField($row, 'Key');
        return String($row.find('.h18-page-section-key').first().val() || ($key.length ? $key.val() : '') || $row.attr('data-key') || '');
    }
    function rowType($row) {
        return String($row.attr('data-section-type') || rowField($row, 'Type').val() || 'text');
    }
    function isKasse($row) { return ['container','grid','flex'].indexOf(rowType($row)) !== -1; }
    function pageSlug() { return String($form.find('[name="page_slug"]').first().val() || '').trim(); }

    function clamp(value, min, max, fallback) {
        const parsed = parseInt(value, 10);
        return Number.isFinite(parsed) ? Math.max(min, Math.min(max, parsed)) : fallback;
    }
    function enumValue(value, allowed, fallback) {
        value = String(value || '');
        return allowed.indexOf(value) !== -1 ? value : fallback;
    }
    function colorValue(value, fallback) {
        value = String(value || '').toLowerCase().trim();
        return /^#[0-9a-f]{6}$/.test(value) ? value : fallback;
    }
    function boolValue(value, fallback) {
        if (typeof value === 'boolean') { return value; }
        if (value === null || typeof value === 'undefined' || value === '') { return fallback; }
        if (typeof value === 'number') { return value !== 0; }
        return ['1','true','yes','on'].indexOf(String(value).toLowerCase().trim()) !== -1;
    }
    function legacyValue($row, name, fallback) {
        const $field = rowField($row, name);
        return $field.length ? $field.val() : fallback;
    }

    function normalizeDesign(raw, fallback) {
        fallback = fallback && typeof fallback === 'object' ? fallback : {};
        raw = raw && typeof raw === 'object' ? raw : {};
        const rawColors = raw.Colors && typeof raw.Colors === 'object' ? raw.Colors : {};
        const rawBorder = raw.Border && typeof raw.Border === 'object' ? raw.Border : {};
        const rawRadius = raw.Radius && typeof raw.Radius === 'object' ? raw.Radius : {};
        const rawTypography = raw.Typography && typeof raw.Typography === 'object' ? raw.Typography : {};
        const rawEffects = raw.Effects && typeof raw.Effects === 'object' ? raw.Effects : {};
        const rawStates = raw.States && typeof raw.States === 'object' ? raw.States : {};
        const rawHover = rawStates.Hover && typeof rawStates.Hover === 'object' ? rawStates.Hover : {};
        const fColors = fallback.Colors || {};
        const fBorder = fallback.Border || {};
        const fRadius = fallback.Radius || {};
        const fTypography = fallback.Typography || {};
        const fEffects = fallback.Effects || {};
        const fHover = fallback.States && fallback.States.Hover ? fallback.States.Hover : {};
        return {
            SchemaVersion: 1,
            Mode: enumValue(raw.Mode, ['Global','Custom'], enumValue(fallback.Mode, ['Global','Custom'], 'Global')),
            Colors: {
                Background: colorValue(rawColors.Background, colorValue(fColors.Background, '#ffffff')),
                Text: colorValue(rawColors.Text, colorValue(fColors.Text, '#30382a')),
                Heading: colorValue(rawColors.Heading, colorValue(fColors.Heading, '#30382a'))
            },
            Border: {
                Width: clamp(rawBorder.Width, 0, 12, clamp(fBorder.Width, 0, 12, 0)),
                Color: colorValue(rawBorder.Color, colorValue(fBorder.Color, '#c3ae83'))
            },
            Radius: {
                All: clamp(rawRadius.All, 0, 30, clamp(fRadius.All, 0, 30, 7)),
                TopLeft: clamp(rawRadius.TopLeft, -1, 60, clamp(fRadius.TopLeft, -1, 60, -1)),
                TopRight: clamp(rawRadius.TopRight, -1, 60, clamp(fRadius.TopRight, -1, 60, -1)),
                BottomRight: clamp(rawRadius.BottomRight, -1, 60, clamp(fRadius.BottomRight, -1, 60, -1)),
                BottomLeft: clamp(rawRadius.BottomLeft, -1, 60, clamp(fRadius.BottomLeft, -1, 60, -1))
            },
            Typography: {
                BodyFont: enumValue(rawTypography.BodyFont, fonts, enumValue(fTypography.BodyFont, fonts, 'Global')),
                HeadingFont: enumValue(rawTypography.HeadingFont, fonts, enumValue(fTypography.HeadingFont, fonts, 'Global')),
                BodySize: clamp(rawTypography.BodySize, 0, 32, clamp(fTypography.BodySize, 0, 32, 0)),
                H1Size: clamp(rawTypography.H1Size, 0, 96, clamp(fTypography.H1Size, 0, 96, 0)),
                H2Size: clamp(rawTypography.H2Size, 0, 80, clamp(fTypography.H2Size, 0, 80, 0)),
                H3Size: clamp(rawTypography.H3Size, 0, 64, clamp(fTypography.H3Size, 0, 64, 0))
            },
            Effects: {
                Opacity: clamp(rawEffects.Opacity, 0, 100, clamp(fEffects.Opacity, 0, 100, 100)),
                Shadow: enumValue(rawEffects.Shadow, shadows, enumValue(fEffects.Shadow, shadows, 'None'))
            },
            States: { Hover: {
                Mode: enumValue(rawHover.Mode, ['Inherit','Custom'], enumValue(fHover.Mode, ['Inherit','Custom'], 'Inherit')),
                Background: colorValue(rawHover.Background, colorValue(fHover.Background, '#ffffff')),
                Text: colorValue(rawHover.Text, colorValue(fHover.Text, '#30382a')),
                Heading: colorValue(rawHover.Heading, colorValue(fHover.Heading, '#30382a')),
                Border: colorValue(rawHover.Border, colorValue(fHover.Border, '#c3ae83')),
                Opacity: clamp(rawHover.Opacity, 0, 100, clamp(fHover.Opacity, 0, 100, 100)),
                Effect: enumValue(rawHover.Effect, hoverEffects, enumValue(fHover.Effect, hoverEffects, 'None')),
                TransitionMs: clamp(rawHover.TransitionMs, 0, 1000, clamp(fHover.TransitionMs, 0, 1000, 220))
            }}
        };
    }

    function desktopState($row) {
        return normalizeDesign({
            Mode: legacyValue($row, 'DesignMode', 'Global'),
            Colors: {
                Background: legacyValue($row, 'CustomBackgroundColor', '#ffffff'),
                Text: legacyValue($row, 'CustomTextColor', '#30382a'),
                Heading: legacyValue($row, 'CustomHeadingColor', '#30382a')
            },
            Border: { Width: legacyValue($row, 'BorderWidthPx', 0), Color: legacyValue($row, 'CustomBorderColor', '#c3ae83') },
            Radius: {
                All: legacyValue($row, 'RadiusPx', 7), TopLeft: legacyValue($row, 'RadiusTopLeftPx', -1),
                TopRight: legacyValue($row, 'RadiusTopRightPx', -1), BottomRight: legacyValue($row, 'RadiusBottomRightPx', -1), BottomLeft: legacyValue($row, 'RadiusBottomLeftPx', -1)
            },
            Typography: {
                BodyFont: legacyValue($row, 'SectionBodyFontFamily', 'Global'), HeadingFont: legacyValue($row, 'SectionHeadingFontFamily', 'Global'),
                BodySize: legacyValue($row, 'BodyFontSizePx', 0), H1Size: legacyValue($row, 'H1FontSizePx', 0),
                H2Size: legacyValue($row, 'H2FontSizePx', 0), H3Size: legacyValue($row, 'H3FontSizePx', 0)
            },
            Effects: { Opacity: legacyValue($row, 'SectionOpacityPercent', 100), Shadow: legacyValue($row, 'ShadowStyle', 'None') },
            States: { Hover: {
                Mode: legacyValue($row, 'HoverStyleMode', 'Inherit'), Background: legacyValue($row, 'HoverBackgroundColor', '#ffffff'),
                Text: legacyValue($row, 'HoverTextColor', '#30382a'), Heading: legacyValue($row, 'HoverHeadingColor', '#30382a'),
                Border: legacyValue($row, 'HoverBorderColor', '#c3ae83'), Opacity: legacyValue($row, 'HoverOpacityPercent', 100),
                Effect: legacyValue($row, 'HoverEffect', 'None'), TransitionMs: legacyValue($row, 'HoverTransitionMs', 220)
            }}
        }, {});
    }

    function normalizeResponsive($row, raw) {
        const desktop = desktopState($row);
        raw = raw && typeof raw === 'object' ? raw : {};
        function device(name) {
            const value = raw[name] && typeof raw[name] === 'object' ? raw[name] : {};
            return {
                InheritDesktop: Object.prototype.hasOwnProperty.call(value, 'InheritDesktop') ? boolValue(value.InheritDesktop, true) : true,
                Design: normalizeDesign(value.Design, desktop)
            };
        }
        return { SchemaVersion: 1, Tablet: device('Tablet'), Mobile: device('Mobile') };
    }

    function effectiveFor($row, state, device) {
        const desktop = desktopState($row);
        if (device === 'Desktop') { return { Design: desktop, Inherited: false }; }
        const entry = state[device];
        return entry && entry.InheritDesktop
            ? { Design: desktop, Inherited: true }
            : { Design: normalizeDesign(entry ? entry.Design : {}, desktop), Inherited: false };
    }

    function storedSections() {
        const pages = config.pages && typeof config.pages === 'object' ? config.pages : {};
        const page = pages[pageSlug()] && typeof pages[pageSlug()] === 'object' ? pages[pageSlug()] : {};
        return page.Sections && typeof page.Sections === 'object' ? page.Sections : {};
    }
    function canonicalField($row) { return rowBody($row).find('.' + STATE_CLASS).first(); }
    function ensureCanonicalField($row, state) {
        let $field = canonicalField($row);
        if ($field.length) { return $field; }
        $field = $('<input>', { type: 'hidden', class: STATE_CLASS, value: JSON.stringify(normalizeResponsive($row, state)), 'data-h18-lego-responsive-design-canonical': '1' });
        rowBody($row).append($field);
        return $field;
    }
    function stateForRow($row) {
        const $field = canonicalField($row);
        if ($field.length) {
            try { return normalizeResponsive($row, JSON.parse(String($field.val() || '{}'))); }
            catch (error) { return normalizeResponsive($row, {}); }
        }
        const stored = storedSections();
        const key = rowKey($row);
        return normalizeResponsive($row, key && stored[key] ? stored[key] : {});
    }
    function writeState($row, state, captureHistory) {
        state = normalizeResponsive($row, state);
        const $field = ensureCanonicalField($row, state);
        $field.val(JSON.stringify(state));
        $row.attr('data-h18-responsive-design', '1')
            .attr('data-h18-responsive-design-tablet-inherit', state.Tablet.InheritDesktop ? '1' : '0')
            .attr('data-h18-responsive-design-mobile-inherit', state.Mobile.InheritDesktop ? '1' : '0');
        applyPreview($row);
        if (captureHistory) { $field.trigger('input'); }
        return state;
    }
    function hydrateRow($row) {
        if (canonicalField($row).length) { writeState($row, stateForRow($row), false); return; }
        const stored = storedSections();
        const key = rowKey($row);
        writeState($row, normalizeResponsive($row, key && stored[key] ? stored[key] : {}), false);
    }

    function getAt(value, path) {
        return String(path || '').split('.').reduce(function (current, key) { return current && typeof current === 'object' ? current[key] : undefined; }, value);
    }
    function setAt(value, path, next) {
        const parts = String(path || '').split('.');
        let current = value;
        parts.slice(0,-1).forEach(function (key) { if (!current[key] || typeof current[key] !== 'object') { current[key] = {}; } current = current[key]; });
        current[parts[parts.length - 1]] = next;
    }

    function setLegacySilently($row, fieldName, value) {
        const $field = rowField($row, fieldName);
        if (!$field.length) { return false; }
        if ($field.is(':checkbox')) { $field.prop('checked', Boolean(value)); mirrorFields($row, fieldName).prop('checked', Boolean(value)); }
        else { $field.val(String(value)); mirrorFields($row, fieldName).val(String(value)); }
        return true;
    }
    function needsCustom(path) { return /^(Colors|Border|Radius|Typography|Effects)\./.test(path); }
    function needsHoverCustom(path) { return /^States\.Hover\.(Background|Text|Heading|Border|Opacity)$/.test(path); }
    function writeDesktop($row, path, value, eventType) {
        const fieldName = String(fieldMap[path] || '');
        const $field = rowField($row, fieldName);
        if (!$field.length) { return false; }
        if (needsCustom(path) && String(legacyValue($row, 'DesignMode', 'Global')) !== 'Custom') { setLegacySilently($row, 'DesignMode', 'Custom'); }
        if (needsHoverCustom(path) && String(legacyValue($row, 'HoverStyleMode', 'Inherit')) !== 'Custom') { setLegacySilently($row, 'HoverStyleMode', 'Custom'); }
        setLegacySilently($row, fieldName, value);
        $field.trigger(eventType);
        // Inherited devices are live views of Desktop; their stored overrides stay untouched.
        applyPreview($row);
        return true;
    }

    function shadowCss(value) {
        return { None:'none', Soft:'0 4px 14px rgba(0,0,0,.12)', Medium:'0 8px 24px rgba(0,0,0,.18)', Strong:'0 12px 36px rgba(0,0,0,.26)' }[value] || 'none';
    }
    function activeCanvasDevice() {
        const raw = String($canvas.attr('data-canvas-device') || 'desktop').toLowerCase();
        return raw === 'tablet' ? 'Tablet' : (raw === 'mobile' ? 'Mobile' : 'Desktop');
    }
    function activeCanvasState() { return String($canvas.attr('data-canvas-state') || 'normal').toLowerCase(); }
    function radiusValue(design) {
        const r = design.Radius;
        return [r.TopLeft < 0 ? r.All : r.TopLeft, r.TopRight < 0 ? r.All : r.TopRight, r.BottomRight < 0 ? r.All : r.BottomRight, r.BottomLeft < 0 ? r.All : r.BottomLeft].join('px ') + 'px';
    }
    function applyPreview($row) {
        if (!$row || !$row.length) { return; }
        const device = activeCanvasDevice();
        const effective = effectiveFor($row, stateForRow($row), device);
        const design = effective.Design;
        const hover = activeCanvasState() === 'hover' && design.States.Hover.Mode === 'Custom';
        const custom = hover || design.Mode === 'Custom';
        const node = $row.get(0);
        if (!node) { return; }
        node.setAttribute('data-h18-responsive-design-active', device !== 'Desktop' && !effective.Inherited ? '1' : '0');
        node.setAttribute('data-h18-responsive-design-custom', custom ? '1' : '0');
        node.setAttribute('data-h18-responsive-design-hover', hover ? '1' : '0');
        node.setAttribute('data-h18-responsive-body-font', design.Typography.BodyFont !== 'Global' ? '1' : '0');
        node.setAttribute('data-h18-responsive-heading-font', design.Typography.HeadingFont !== 'Global' ? '1' : '0');
        node.setAttribute('data-h18-responsive-body-size', design.Typography.BodySize > 0 ? '1' : '0');
        node.setAttribute('data-h18-responsive-h1-size', design.Typography.H1Size > 0 ? '1' : '0');
        node.setAttribute('data-h18-responsive-h2-size', design.Typography.H2Size > 0 ? '1' : '0');
        node.setAttribute('data-h18-responsive-h3-size', design.Typography.H3Size > 0 ? '1' : '0');
        const colors = hover ? { Background:design.States.Hover.Background, Text:design.States.Hover.Text, Heading:design.States.Hover.Heading, Border:design.States.Hover.Border, Opacity:design.States.Hover.Opacity } : { Background:design.Colors.Background, Text:design.Colors.Text, Heading:design.Colors.Heading, Border:design.Border.Color, Opacity:design.Effects.Opacity };
        node.style.setProperty('--h18-rd-background', colors.Background);
        node.style.setProperty('--h18-rd-text', colors.Text);
        node.style.setProperty('--h18-rd-heading', colors.Heading);
        node.style.setProperty('--h18-rd-border-color', colors.Border);
        node.style.setProperty('--h18-rd-border-width', design.Border.Width + 'px');
        node.style.setProperty('--h18-rd-radius', radiusValue(design));
        node.style.setProperty('--h18-rd-opacity', String(colors.Opacity / 100));
        node.style.setProperty('--h18-rd-shadow', hover && design.States.Hover.Effect === 'Shadow' ? '0 14px 38px rgba(0,0,0,.3)' : shadowCss(design.Effects.Shadow));
        node.style.setProperty('--h18-rd-transition', design.States.Hover.TransitionMs + 'ms');
        node.style.setProperty('--h18-rd-body-font', design.Typography.BodyFont === 'System' ? 'system-ui' : design.Typography.BodyFont);
        node.style.setProperty('--h18-rd-heading-font', design.Typography.HeadingFont === 'System' ? 'system-ui' : design.Typography.HeadingFont);
        node.style.setProperty('--h18-rd-body-size', design.Typography.BodySize + 'px');
        node.style.setProperty('--h18-rd-h1-size', design.Typography.H1Size + 'px');
        node.style.setProperty('--h18-rd-h2-size', design.Typography.H2Size + 'px');
        node.style.setProperty('--h18-rd-h3-size', design.Typography.H3Size + 'px');
        node.style.setProperty('--h18-rd-hover-transform', hover && design.States.Hover.Effect === 'Lift' ? 'translateY(-4px)' : (hover && design.States.Hover.Effect === 'Scale' ? 'scale(1.03)' : 'none'));
    }
    function applyAllPreview() { activeRows().each(function () { hydrateRow($(this)); applyPreview($(this)); }); }

    function normalizeInput(path, raw) {
        if (/^(Colors\.|Border\.Color|States\.Hover\.(Background|Text|Heading|Border))/.test(path)) { return colorValue(raw, '#ffffff'); }
        if (path === 'Mode') { return enumValue(raw, ['Global','Custom'], 'Global'); }
        if (path === 'Typography.BodyFont' || path === 'Typography.HeadingFont') { return enumValue(raw, fonts, 'Global'); }
        if (path === 'Effects.Shadow') { return enumValue(raw, shadows, 'None'); }
        if (path === 'States.Hover.Mode') { return enumValue(raw, ['Inherit','Custom'], 'Inherit'); }
        if (path === 'States.Hover.Effect') { return enumValue(raw, hoverEffects, 'None'); }
        const bounds = {
            'Border.Width':[0,12,0], 'Radius.All':[0,30,7], 'Radius.TopLeft':[-1,60,-1], 'Radius.TopRight':[-1,60,-1],
            'Radius.BottomRight':[-1,60,-1], 'Radius.BottomLeft':[-1,60,-1], 'Typography.BodySize':[0,32,0], 'Typography.H1Size':[0,96,0],
            'Typography.H2Size':[0,80,0], 'Typography.H3Size':[0,64,0], 'Effects.Opacity':[0,100,100], 'States.Hover.Opacity':[0,100,100], 'States.Hover.TransitionMs':[0,1000,220]
        };
        const b = bounds[path] || [0,9999,0];
        return clamp(raw, b[0], b[1], b[2]);
    }

    function control(label, path, value, options, disabled, suffix) {
        const $label = $('<label>', { class:'h18-rd-control' }).append($('<strong>', { text:label }));
        let $input;
        if (Array.isArray(options)) {
            $input = $('<select>', { 'data-h18-rd-path':path, disabled:Boolean(disabled) });
            options.forEach(function (option) {
                const raw = typeof option === 'string' ? option : option.value;
                const text = typeof option === 'string' ? option : option.label;
                $input.append($('<option>', { value:raw, text:text, selected:String(raw) === String(value) }));
            });
        } else if (/^(Colors\.|Border\.Color|States\.Hover\.(Background|Text|Heading|Border))/.test(path)) {
            $input = $('<input>', { type:'color', value:value, disabled:Boolean(disabled), 'data-h18-rd-path':path });
        } else {
            const bounds = { 'Border.Width':[0,12], 'Radius.All':[0,30], 'Radius.TopLeft':[-1,60], 'Radius.TopRight':[-1,60], 'Radius.BottomRight':[-1,60], 'Radius.BottomLeft':[-1,60], 'Typography.BodySize':[0,32], 'Typography.H1Size':[0,96], 'Typography.H2Size':[0,80], 'Typography.H3Size':[0,64], 'Effects.Opacity':[0,100], 'States.Hover.Opacity':[0,100], 'States.Hover.TransitionMs':[0,1000] };
            const b = bounds[path] || [0,9999];
            $input = $('<input>', { type:'number', min:b[0], max:b[1], step:1, value:value, disabled:Boolean(disabled), 'data-h18-rd-path':path });
        }
        const $wrap = $('<span>', { class:'h18-rd-input' }).append($input);
        if (suffix) { $wrap.append($('<em>', { text:suffix })); }
        return $label.append($wrap);
    }
    function deviceDesign($row, state, device) { return effectiveFor($row, state, device).Design; }
    function renderControls($row, state, device) {
        const design = deviceDesign($row, state, device);
        const inherited = device !== 'Desktop' && state[device].InheritDesktop;
        const $root = $('<div>', { class:'h18-rd-device-panel', 'data-h18-rd-device-panel':device, hidden:panelDevice !== device });
        if (device !== 'Desktop') {
            $root.append(
                $('<label>', { class:'h18-rd-inherit' }).append(
                    $('<input>', { type:'checkbox', checked:inherited, 'data-h18-rd-inherit':device }),
                    $('<span>', { text:'Arv fra Desktop' })
                ),
                $('<p>', { class:'description', text: inherited ? 'Aktive værdier følger Desktop. Dine tidligere overrides gemmes og kan aktiveres igen.' : 'Egne designværdier er aktive på ' + (device === 'Mobile' ? 'mobil' : 'tablet') + '.' })
            );
        }
        const disabled = inherited;
        const sections = [
            ['Design', [
                control('Designkilde','Mode',design.Mode,[{value:'Global',label:'Global design'},{value:'Custom',label:'Tilpasset'}],disabled),
                control('Baggrund','Colors.Background',design.Colors.Background,null,disabled), control('Tekst','Colors.Text',design.Colors.Text,null,disabled),
                control('Overskrift','Colors.Heading',design.Colors.Heading,null,disabled), control('Kantfarve','Border.Color',design.Border.Color,null,disabled),
                control('Kantbredde','Border.Width',design.Border.Width,null,disabled,'px')
            ]],
            ['Typografi', [
                control('Brødtekst-font','Typography.BodyFont',design.Typography.BodyFont,fonts,disabled), control('Overskrift-font','Typography.HeadingFont',design.Typography.HeadingFont,fonts,disabled),
                control('Brødtekst','Typography.BodySize',design.Typography.BodySize,null,disabled,'px'), control('H1','Typography.H1Size',design.Typography.H1Size,null,disabled,'px'),
                control('H2','Typography.H2Size',design.Typography.H2Size,null,disabled,'px'), control('H3','Typography.H3Size',design.Typography.H3Size,null,disabled,'px')
            ]],
            ['Form og effekter', [
                control('Radius alle','Radius.All',design.Radius.All,null,disabled,'px'), control('Top venstre','Radius.TopLeft',design.Radius.TopLeft,null,disabled,'px'),
                control('Top højre','Radius.TopRight',design.Radius.TopRight,null,disabled,'px'), control('Bund højre','Radius.BottomRight',design.Radius.BottomRight,null,disabled,'px'),
                control('Bund venstre','Radius.BottomLeft',design.Radius.BottomLeft,null,disabled,'px'), control('Skygge','Effects.Shadow',design.Effects.Shadow,shadows,disabled),
                control('Opacitet','Effects.Opacity',design.Effects.Opacity,null,disabled,'%')
            ]],
            ['Hover', [
                control('Hover-farver','States.Hover.Mode',design.States.Hover.Mode,[{value:'Inherit',label:'Arv Normal'},{value:'Custom',label:'Tilpasset'}],disabled),
                control('Effekt','States.Hover.Effect',design.States.Hover.Effect,hoverEffects,disabled), control('Transition','States.Hover.TransitionMs',design.States.Hover.TransitionMs,null,disabled,'ms'),
                control('Baggrund','States.Hover.Background',design.States.Hover.Background,null,disabled), control('Tekst','States.Hover.Text',design.States.Hover.Text,null,disabled),
                control('Overskrift','States.Hover.Heading',design.States.Hover.Heading,null,disabled), control('Kant','States.Hover.Border',design.States.Hover.Border,null,disabled),
                control('Opacitet','States.Hover.Opacity',design.States.Hover.Opacity,null,disabled,'%')
            ]]
        ];
        sections.forEach(function (section) {
            const $fieldset = $('<fieldset>', { class:'h18-rd-group' }).append($('<legend>', { text:section[0] }), $('<div>', { class:'h18-rd-grid' }));
            $fieldset.children('.h18-rd-grid').append(section[1]);
            $root.append($fieldset);
        });
        return $root;
    }
    function renderPanel() {
        $('#' + PANEL_ID).remove();
        const $row = selectedRow();
        if (!$row.length) { return; }
        hydrateRow($row);
        const state = stateForRow($row);
        const canvasDevice = activeCanvasDevice();
        if (!$('#' + PANEL_ID).length && ['Desktop','Tablet','Mobile'].indexOf(panelDevice) === -1) { panelDevice = canvasDevice; }
        const $panel = $('<section>', { id:PANEL_ID, class:'h18-section-module-box h18-canvas-direct-controls h18-rd-panel', 'data-h18-rd-role':isKasse($row)?'kasse':'element' });
        $panel.append(
            $('<div>', { class:'h18-rd-heading' }).append(
                $('<div>').append($('<h4>', { text:'LEGO-design · Responsive' }), $('<p>', { class:'description', text:'Desktop er basis. Tablet og Mobil kan arve eller bruge bevarede overrides.' })),
                $('<span>', { class:'h18-rd-badge', text:'0.8.33' })
            ),
            $('<div>', { class:'h18-rd-tabs', role:'tablist' }).append(
                ['Desktop','Tablet','Mobile'].map(function (device) { return $('<button>', { type:'button', class:'button h18-rd-tab' + (panelDevice===device?' is-active':''), text:device==='Mobile'?'Mobil':device, 'data-h18-rd-tab':device }); })
            ),
            renderControls($row,state,'Desktop'), renderControls($row,state,'Tablet'), renderControls($row,state,'Mobile'),
            $('<p>', { class:'description h18-rd-note', text:'Responsive design-overlayet er admin-only. Desktop/save/public renderer og v0.8.31 spacing forbliver autoritative og separate.' })
        );
        $inspector.append($panel);
    }

    $(document).on('click', '#' + PANEL_ID + ' [data-h18-rd-tab]', function () {
        panelDevice = String($(this).attr('data-h18-rd-tab') || 'Desktop');
        renderPanel();
    });
    $(document).on('change', '#' + PANEL_ID + ' [data-h18-rd-inherit]', function () {
        const $row = selectedRow(); if (!$row.length) { return; }
        const device = String($(this).attr('data-h18-rd-inherit') || ''); if (device !== 'Tablet' && device !== 'Mobile') { return; }
        const state = stateForRow($row); state[device].InheritDesktop = $(this).is(':checked');
        writeState($row,state,true); renderPanel();
    });
    $(document).on('input', '#' + PANEL_ID + ' input[data-h18-rd-path]', function () {
        const $row = selectedRow(); if (!$row.length) { return; }
        const path = String($(this).attr('data-h18-rd-path') || ''); const value = normalizeInput(path,$(this).val());
        if (panelDevice === 'Desktop') { writeDesktop($row,path,value,'input'); }
        else { const state = stateForRow($row); if (state[panelDevice].InheritDesktop) { return; } if (needsCustom(path) && getAt(state[panelDevice].Design,'Mode') !== 'Custom') { setAt(state[panelDevice].Design,'Mode','Custom'); } if (needsHoverCustom(path) && getAt(state[panelDevice].Design,'States.Hover.Mode') !== 'Custom') { setAt(state[panelDevice].Design,'States.Hover.Mode','Custom'); } setAt(state[panelDevice].Design,path,value); writeState($row,state,true); }
        scheduleRefresh(35);
    });
    $(document).on('change', '#' + PANEL_ID + ' select[data-h18-rd-path]', function () {
        const $row = selectedRow(); if (!$row.length) { return; }
        const path = String($(this).attr('data-h18-rd-path') || ''); const value = normalizeInput(path,$(this).val());
        if (panelDevice === 'Desktop') { writeDesktop($row,path,value,'change'); }
        else { const state = stateForRow($row); if (state[panelDevice].InheritDesktop) { return; } if (needsCustom(path) && path !== 'Mode' && getAt(state[panelDevice].Design,'Mode') !== 'Custom') { setAt(state[panelDevice].Design,'Mode','Custom'); } setAt(state[panelDevice].Design,path,value); writeState($row,state,true); }
        scheduleRefresh(35);
    });

    const legacySelector = Object.keys(fieldMap).map(function (path) { return '[name$="[' + fieldMap[path] + ']"]'; }).join(',');
    if (legacySelector) {
        $form.on('input change', legacySelector, function () { window.clearTimeout(refreshTimer); refreshTimer = window.setTimeout(function () { applyAllPreview(); renderPanel(); },45); });
    }

    function appendSavePayload() {
        $form.find('[' + SUBMIT_ATTR + '="1"]').remove();
        let index = 0;
        activeRows().each(function () {
            const $row = $(this); const key = rowKey($row); if (!key) { return; }
            hydrateRow($row);
            const values = { SectionKey:key, StateJson:JSON.stringify(stateForRow($row)) };
            Object.keys(values).forEach(function (name) { $('<input>', { type:'hidden', name:'h18_lego_responsive_design[' + index + '][' + name + ']', value:values[name] }).attr(SUBMIT_ATTR,'1').appendTo($form); });
            index += 1;
        });
    }
    $form.on('submit.h18ResponsiveDesignV0833', appendSavePayload);

    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(function () { applyAllPreview(); renderPanel(); }, typeof delay === 'number' ? delay : 50);
    }
    $(document).on('click', '.h18-page-section-header,.h18-page-section-edit,.h18-v0811-edit-child,.h18-ud-auto-box-tile,.h18-ud-box-child-chip,.h18-navigator-select', function () { scheduleRefresh(55); });

    const observer = new MutationObserver(function (mutations) {
        const relevant = mutations.some(function (m) { return m.type === 'childList' || (m.type === 'attributes' && (m.attributeName === 'class' || m.attributeName === 'data-canvas-device' || m.attributeName === 'data-canvas-state')); });
        if (relevant) { scheduleRefresh(60); }
    });
    observer.observe($sections.get(0), { childList:true, subtree:true, attributes:true, attributeFilter:['class'] });
    if ($inspectorTarget.length) { observer.observe($inspectorTarget.get(0), { childList:true, subtree:true }); }
    if ($canvas.length) { observer.observe($canvas.get(0), { attributes:true, attributeFilter:['data-canvas-device','data-canvas-state'] }); }

    activeRows().each(function () { hydrateRow($(this)); });
    applyAllPreview();
    renderPanel();
    document.documentElement.setAttribute('data-h18-lego-responsive-design-runtime','0.8.33');
    window.__h18LegoResponsiveDesignV0833 = {
        version:'0.8.33',
        stateForKey:function (key) { const $row=activeRows().filter(function(){return rowKey($(this))===String(key||'');}).first(); return $row.length?stateForRow($row):null; },
        effectiveForKey:function (key,device) { const $row=activeRows().filter(function(){return rowKey($(this))===String(key||'');}).first(); if(!$row.length){return null;} return effectiveFor($row,stateForRow($row),['Desktop','Tablet','Mobile'].indexOf(String(device))!==-1?String(device):'Desktop'); },
        hasCanonicalField:function (key) { const $row=activeRows().filter(function(){return rowKey($(this))===String(key||'');}).first(); return $row.length?canonicalField($row).length===1:false; }
    };
});
