jQuery(function ($) {
    'use strict';

    const config = window.H18LegoInteractionStatesV0834 || {};
    const $form = $('#h18-page-editor-form');
    const $sections = $('#h18-page-sections-sortable');
    const $inspector = $('#h18-page-inspector');
    const $inspectorTarget = $('#h18-page-inspector-target');
    const $canvas = $('.h18-builder-canvas').first();
    if (!$form.length || !$sections.length || !$inspector.length) { return; }

    const PANEL_ID = 'h18-ud-lego-interaction-states-panel';
    const STATE_CLASS = 'h18-lego-interaction-states-state-json';
    const SUBMIT_ATTR = 'data-h18-lego-interaction-submit';
    const transitionPresets = Array.isArray(config.transitionPresets) ? config.transitionPresets : ['Inherit','Fast','Normal','Slow','Custom'];
    const focusStyles = Array.isArray(config.focusStyles) ? config.focusStyles : ['Global','Custom','None'];
    const activeEffects = Array.isArray(config.activeEffects) ? config.activeEffects : ['None','Press','ScaleDown'];
    let panelDevice = '';
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
    function legacyValue($row, name, fallback) {
        const $field = rowField($row, name);
        return $field.length ? $field.val() : fallback;
    }
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

    function desktopInteraction($row) {
        return {
            SchemaVersion: 1,
            Motion: {
                Transition: enumValue(legacyValue($row, 'TransitionPreset', 'Inherit'), transitionPresets, 'Inherit')
            },
            Focus: {
                Style: enumValue(legacyValue($row, 'FocusRingStyle', 'Global'), focusStyles, 'Global'),
                Color: colorValue(legacyValue($row, 'FocusRingColor', '#8b4a2b'), '#8b4a2b'),
                Width: clamp(legacyValue($row, 'FocusRingWidthPx', 3), 1, 8, 3),
                Offset: clamp(legacyValue($row, 'FocusRingOffsetPx', 2), 0, 12, 2)
            },
            Active: {
                Effect: enumValue(legacyValue($row, 'ActiveEffect', 'None'), activeEffects, 'None')
            },
            Disabled: {
                Opacity: clamp(legacyValue($row, 'DisabledOpacityPercent', 55), 10, 100, 55)
            }
        };
    }

    function normalizeInteraction(raw, fallback) {
        raw = raw && typeof raw === 'object' ? raw : {};
        fallback = fallback && typeof fallback === 'object' ? fallback : desktopInteraction($());
        const motion = raw.Motion && typeof raw.Motion === 'object' ? raw.Motion : {};
        const focus = raw.Focus && typeof raw.Focus === 'object' ? raw.Focus : {};
        const active = raw.Active && typeof raw.Active === 'object' ? raw.Active : {};
        const disabled = raw.Disabled && typeof raw.Disabled === 'object' ? raw.Disabled : {};
        return {
            SchemaVersion: 1,
            Motion: {
                Transition: enumValue(motion.Transition, transitionPresets, enumValue(fallback.Motion && fallback.Motion.Transition, transitionPresets, 'Inherit'))
            },
            Focus: {
                Style: enumValue(focus.Style, focusStyles, enumValue(fallback.Focus && fallback.Focus.Style, focusStyles, 'Global')),
                Color: colorValue(focus.Color, colorValue(fallback.Focus && fallback.Focus.Color, '#8b4a2b')),
                Width: clamp(focus.Width, 1, 8, clamp(fallback.Focus && fallback.Focus.Width, 1, 8, 3)),
                Offset: clamp(focus.Offset, 0, 12, clamp(fallback.Focus && fallback.Focus.Offset, 0, 12, 2))
            },
            Active: {
                Effect: enumValue(active.Effect, activeEffects, enumValue(fallback.Active && fallback.Active.Effect, activeEffects, 'None'))
            },
            Disabled: {
                Opacity: clamp(disabled.Opacity, 10, 100, clamp(fallback.Disabled && fallback.Disabled.Opacity, 10, 100, 55))
            }
        };
    }

    function interactionFromDesign(design, fallback) {
        design = design && typeof design === 'object' ? design : {};
        const states = design.States && typeof design.States === 'object' ? design.States : {};
        return normalizeInteraction({
            Motion: design.Motion,
            Focus: states.Focus,
            Active: states.Active,
            Disabled: states.Disabled
        }, fallback);
    }

    function storedSections() {
        const pages = config.pages && typeof config.pages === 'object' ? config.pages : {};
        const page = pages[pageSlug()] && typeof pages[pageSlug()] === 'object' ? pages[pageSlug()] : {};
        return page.Sections && typeof page.Sections === 'object' ? page.Sections : {};
    }

    function initialState($row) {
        const desktop = desktopInteraction($row);
        const stored = storedSections();
        const section = stored[rowKey($row)] && typeof stored[rowKey($row)] === 'object' ? stored[rowKey($row)] : {};
        function device(name) {
            const value = section[name] && typeof section[name] === 'object' ? section[name] : {};
            const design = value.Design && typeof value.Design === 'object' ? value.Design : {};
            return {
                HasOverride: Object.prototype.hasOwnProperty.call(value, 'InteractionHasOverride') ? boolValue(value.InteractionHasOverride, false) : false,
                Interaction: interactionFromDesign(design, desktop)
            };
        }
        return { SchemaVersion: 1, Tablet: device('Tablet'), Mobile: device('Mobile') };
    }

    function canonicalField($row) { return rowBody($row).find('.' + STATE_CLASS).first(); }
    function normalizeState($row, raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        const desktop = desktopInteraction($row);
        function device(name) {
            const value = raw[name] && typeof raw[name] === 'object' ? raw[name] : {};
            return {
                HasOverride: boolValue(value.HasOverride, false),
                Interaction: normalizeInteraction(value.Interaction, desktop)
            };
        }
        return { SchemaVersion: 1, Tablet: device('Tablet'), Mobile: device('Mobile') };
    }
    function stateForRow($row) {
        const $field = canonicalField($row);
        if ($field.length) {
            try { return normalizeState($row, JSON.parse(String($field.val() || '{}'))); }
            catch (error) { return normalizeState($row, initialState($row)); }
        }
        return normalizeState($row, initialState($row));
    }
    function ensureCanonicalField($row, state) {
        let $field = canonicalField($row);
        if ($field.length) { return $field; }
        $field = $('<input>', {
            type: 'hidden',
            class: STATE_CLASS,
            value: JSON.stringify(normalizeState($row, state)),
            'data-h18-lego-interaction-canonical': '1'
        });
        rowBody($row).append($field);
        return $field;
    }
    function writeState($row, state, captureHistory) {
        state = normalizeState($row, state);
        const $field = ensureCanonicalField($row, state);
        $field.val(JSON.stringify(state));
        $row.attr('data-h18-interaction-states', '1')
            .attr('data-h18-interaction-tablet-override', state.Tablet.HasOverride ? '1' : '0')
            .attr('data-h18-interaction-mobile-override', state.Mobile.HasOverride ? '1' : '0');
        applyPreview($row);
        if (captureHistory) { $field.trigger('input'); }
        return state;
    }
    function hydrateRow($row) {
        if (canonicalField($row).length) { writeState($row, stateForRow($row), false); return; }
        writeState($row, initialState($row), false);
    }

    function activeCanvasDevice() {
        const raw = String($canvas.attr('data-canvas-device') || 'desktop').toLowerCase();
        return raw === 'tablet' ? 'Tablet' : (raw === 'mobile' ? 'Mobile' : 'Desktop');
    }
    function activeCanvasState() { return String($canvas.attr('data-canvas-state') || 'normal').toLowerCase(); }
    function effectiveInteraction($row, state, device) {
        const desktop = desktopInteraction($row);
        if (device === 'Desktop') { return { Interaction: desktop, Inherited: false, HasOverride: false }; }
        const entry = state[device];
        return entry && entry.HasOverride
            ? { Interaction: normalizeInteraction(entry.Interaction, desktop), Inherited: false, HasOverride: true }
            : { Interaction: desktop, Inherited: true, HasOverride: false };
    }

    function responsiveDesignFor($row, device) {
        const bridge = window.__h18LegoResponsiveDesignV0833;
        const key = rowKey($row);
        if (bridge && typeof bridge.effectiveForKey === 'function' && key) {
            const result = bridge.effectiveForKey(key, device);
            if (result && result.Design) { return result.Design; }
        }
        return {
            Effects: { Opacity: clamp(legacyValue($row, 'SectionOpacityPercent', 100), 0, 100, 100), Shadow: String(legacyValue($row, 'ShadowStyle', 'None')) },
            States: { Hover: { Mode: String(legacyValue($row, 'HoverStyleMode', 'Inherit')), Opacity: clamp(legacyValue($row, 'HoverOpacityPercent', 100), 0, 100, 100), TransitionMs: clamp(legacyValue($row, 'HoverTransitionMs', 220), 0, 1000, 220) } }
        };
    }
    function shadowCss(value) {
        return { None:'none', Soft:'0 4px 14px rgba(0,0,0,.12)', Medium:'0 8px 24px rgba(0,0,0,.18)', Strong:'0 12px 36px rgba(0,0,0,.26)' }[String(value || 'None')] || 'none';
    }
    function transitionMs(interaction, design) {
        const preset = interaction.Motion.Transition;
        if (preset === 'Fast') { return 120; }
        if (preset === 'Slow') { return 420; }
        if (preset === 'Custom') { return clamp(design && design.States && design.States.Hover && design.States.Hover.TransitionMs, 0, 1000, 220); }
        return 220;
    }
    function deviceTransform($row, device, activeEffect) {
        const prefix = device === 'Tablet' ? 'Tablet' : (device === 'Mobile' ? 'Mobile' : 'Desktop');
        let x = clamp(legacyValue($row, prefix + 'TranslateXPx', 0), -2000, 2000, 0);
        let y = clamp(legacyValue($row, prefix + 'TranslateYPx', 0), -2000, 2000, 0);
        let scale = clamp(legacyValue($row, prefix + 'ScalePercent', 100), 10, 300, 100) / 100;
        const rotate = clamp(legacyValue($row, prefix + 'RotateDeg', 0), -360, 360, 0);
        if (activeEffect === 'Press') { y += 1; }
        if (activeEffect === 'ScaleDown') { scale *= 0.97; }
        return 'translate(' + x + 'px,' + y + 'px) scale(' + scale + ') rotate(' + rotate + 'deg)';
    }

    function applyPreview($row) {
        if (!$row || !$row.length) { return; }
        const $preview = $row.find('.h18-canvas-preview').first();
        if (!$preview.length) { return; }
        const device = activeCanvasDevice();
        const canvasState = activeCanvasState();
        const effective = effectiveInteraction($row, stateForRow($row), device);
        const interaction = effective.Interaction;
        const design = responsiveDesignFor($row, device) || {};
        const effects = design.Effects || {};
        const hover = design.States && design.States.Hover ? design.States.Hover : {};
        const baseShadow = shadowCss(effects.Shadow || legacyValue($row, 'ShadowStyle', 'None'));
        const baseOpacity = clamp(effects.Opacity, 0, 100, clamp(legacyValue($row, 'SectionOpacityPercent', 100), 0, 100, 100));
        const hoverOpacity = String(hover.Mode || 'Inherit') === 'Custom' ? clamp(hover.Opacity, 0, 100, baseOpacity) : baseOpacity;
        const duration = transitionMs(interaction, design);

        $row.attr('data-h18-interaction-active-device', device.toLowerCase())
            .attr('data-h18-interaction-inherited', effective.Inherited ? '1' : '0')
            .attr('data-h18-interaction-preview-state', canvasState);
        $preview.css('transition-duration', duration + 'ms');

        if (canvasState === 'focus') {
            const focus = interaction.Focus;
            if (focus.Style === 'None') {
                $preview.css('box-shadow', baseShadow);
            } else {
                const color = focus.Style === 'Custom' ? focus.Color : '#8b4a2b';
                const width = focus.Style === 'Custom' ? focus.Width : 3;
                const offset = focus.Style === 'Custom' ? focus.Offset : 2;
                const ring = '0 0 0 ' + offset + 'px transparent,0 0 0 ' + (offset + width) + 'px ' + color;
                $preview.css('box-shadow', baseShadow === 'none' ? ring : (baseShadow + ',' + ring));
            }
        }

        if (canvasState === 'active') {
            $preview.css('transform', deviceTransform($row, device, interaction.Active.Effect));
        }

        if (canvasState === 'disabled') {
            $preview.css('opacity', String((baseOpacity / 100) * (interaction.Disabled.Opacity / 100)));
        } else if (canvasState === 'hover') {
            $preview.css('opacity', String(hoverOpacity / 100));
        } else {
            $preview.css('opacity', String(baseOpacity / 100));
        }
    }
    function applyAllPreview() { activeRows().each(function () { hydrateRow($(this)); applyPreview($(this)); }); }

    const desktopFieldMap = {
        'Motion.Transition':'TransitionPreset',
        'Focus.Style':'FocusRingStyle',
        'Focus.Color':'FocusRingColor',
        'Focus.Width':'FocusRingWidthPx',
        'Focus.Offset':'FocusRingOffsetPx',
        'Active.Effect':'ActiveEffect',
        'Disabled.Opacity':'DisabledOpacityPercent'
    };
    function getAt(value, path) {
        return String(path || '').split('.').reduce(function (current, key) { return current && typeof current === 'object' ? current[key] : undefined; }, value);
    }
    function setAt(value, path, next) {
        const parts = String(path || '').split('.');
        let current = value;
        parts.slice(0,-1).forEach(function (key) {
            if (!current[key] || typeof current[key] !== 'object') { current[key] = {}; }
            current = current[key];
        });
        current[parts[parts.length - 1]] = next;
    }
    function normalizeInput(path, raw) {
        if (path === 'Motion.Transition') { return enumValue(raw, transitionPresets, 'Inherit'); }
        if (path === 'Focus.Style') { return enumValue(raw, focusStyles, 'Global'); }
        if (path === 'Focus.Color') { return colorValue(raw, '#8b4a2b'); }
        if (path === 'Focus.Width') { return clamp(raw, 1, 8, 3); }
        if (path === 'Focus.Offset') { return clamp(raw, 0, 12, 2); }
        if (path === 'Active.Effect') { return enumValue(raw, activeEffects, 'None'); }
        if (path === 'Disabled.Opacity') { return clamp(raw, 10, 100, 55); }
        return raw;
    }
    function setLegacySilently($row, fieldName, value) {
        const $field = rowField($row, fieldName);
        if (!$field.length) { return false; }
        $field.val(String(value));
        mirrorFields($row, fieldName).val(String(value));
        return true;
    }
    function writeDesktop($row, path, value, eventType) {
        const fieldName = desktopFieldMap[path] || '';
        const $field = rowField($row, fieldName);
        if (!$field.length) { return false; }
        setLegacySilently($row, fieldName, value);
        $field.trigger(eventType === 'change' ? 'change' : 'input');
        applyPreview($row);
        return true;
    }

    function control(label, path, value, options, disabled, suffix) {
        const $label = $('<label>', { class:'h18-i-control' }).append($('<strong>', { text:label }));
        let $input;
        if (Array.isArray(options)) {
            $input = $('<select>', { 'data-h18-i-path':path, disabled:Boolean(disabled) });
            options.forEach(function (option) {
                const raw = typeof option === 'string' ? option : option.value;
                const text = typeof option === 'string' ? option : option.label;
                $input.append($('<option>', { value:raw, text:text, selected:String(raw) === String(value) }));
            });
        } else if (path === 'Focus.Color') {
            $input = $('<input>', { type:'color', value:value, disabled:Boolean(disabled), 'data-h18-i-path':path });
        } else {
            const bounds = path === 'Focus.Width' ? [1,8] : (path === 'Focus.Offset' ? [0,12] : [10,100]);
            $input = $('<input>', { type:'number', min:bounds[0], max:bounds[1], step:1, value:value, disabled:Boolean(disabled), 'data-h18-i-path':path });
        }
        const $wrap = $('<span>', { class:'h18-i-input' }).append($input);
        if (suffix) { $wrap.append($('<em>', { text:suffix })); }
        return $label.append($wrap);
    }

    function renderDevicePanel($row, state, device) {
        const effective = effectiveInteraction($row, state, device);
        const interaction = effective.Interaction;
        const inherited = device !== 'Desktop' && !state[device].HasOverride;
        const focusCustom = interaction.Focus.Style === 'Custom';
        const $root = $('<div>', { class:'h18-i-device-panel', 'data-h18-i-device-panel':device, hidden:panelDevice !== device });
        if (device !== 'Desktop') {
            $root.append(
                $('<label>', { class:'h18-i-inherit' }).append(
                    $('<input>', { type:'checkbox', checked:inherited, 'data-h18-i-inherit':device }),
                    $('<span>', { text:'Arv interaktions-states fra Desktop' })
                ),
                $('<p>', { class:'description', text: inherited ? 'Focus, Active, Disabled og transition følger Desktop. Tidligere override bevares.' : 'Egne interaktions-states er aktive på ' + (device === 'Mobile' ? 'mobil' : 'tablet') + '.' })
            );
        }
        const disabled = inherited;
        const $grid = $('<div>', { class:'h18-i-grid' }).append(
            control('Transition','Motion.Transition',interaction.Motion.Transition,[
                {value:'Inherit',label:'Global normal'}, {value:'Fast',label:'Fast'}, {value:'Normal',label:'Normal'}, {value:'Slow',label:'Slow'}, {value:'Custom',label:'Hover-transition'}
            ],disabled),
            control('Focus ring','Focus.Style',interaction.Focus.Style,[
                {value:'Global',label:'Global'}, {value:'Custom',label:'Tilpasset'}, {value:'None',label:'Ingen'}
            ],disabled),
            control('Focus farve','Focus.Color',interaction.Focus.Color,null,disabled || !focusCustom),
            control('Focus bredde','Focus.Width',interaction.Focus.Width,null,disabled || !focusCustom,'px'),
            control('Focus offset','Focus.Offset',interaction.Focus.Offset,null,disabled || !focusCustom,'px'),
            control('Active-effekt','Active.Effect',interaction.Active.Effect,[
                {value:'None',label:'Ingen'}, {value:'Press',label:'Tryk 1 px'}, {value:'ScaleDown',label:'Scale 97%'}
            ],disabled),
            control('Disabled opacity','Disabled.Opacity',interaction.Disabled.Opacity,null,disabled,'%')
        );
        return $root.append($grid);
    }

    function renderPanel() {
        $('#' + PANEL_ID).remove();
        const $row = selectedRow();
        if (!$row.length) { return; }
        hydrateRow($row);
        const state = stateForRow($row);
        if (['Desktop','Tablet','Mobile'].indexOf(panelDevice) === -1) { panelDevice = activeCanvasDevice(); }
        const $panel = $('<section>', { id:PANEL_ID, class:'h18-section-module-box h18-i-panel', 'data-h18-i-role':isKasse($row)?'kasse':'element' });
        $panel.append(
            $('<div>', { class:'h18-i-heading' }).append(
                $('<div>').append($('<h4>', { text:'LEGO-design · States' }), $('<p>', { class:'description', text:'Focus, Active, Disabled og transition bruger samme responsive designmodel.' })),
                $('<span>', { class:'h18-i-badge', text:'0.8.34' })
            ),
            $('<div>', { class:'h18-i-tabs', role:'tablist' }).append(
                ['Desktop','Tablet','Mobile'].map(function (device) {
                    return $('<button>', { type:'button', class:'button h18-i-tab' + (panelDevice===device?' is-active':''), text:device==='Mobile'?'Mobil':device, 'data-h18-i-tab':device });
                })
            ),
            renderDevicePanel($row,state,'Desktop'), renderDevicePanel($row,state,'Tablet'), renderDevicePanel($row,state,'Mobile'),
            $('<p>', { class:'description h18-i-note', text:'Ét state-greb = ét eksisterende Undo/Redo-checkpoint. Ingen separat state-database eller history-stack.' })
        );
        $inspector.append($panel);
    }

    $(document).on('click', '#' + PANEL_ID + ' [data-h18-i-tab]', function () {
        panelDevice = String($(this).attr('data-h18-i-tab') || 'Desktop');
        renderPanel();
    });
    $(document).on('change', '#' + PANEL_ID + ' [data-h18-i-inherit]', function () {
        const $row = selectedRow();
        if (!$row.length) { return; }
        const device = String($(this).attr('data-h18-i-inherit') || '');
        if (device !== 'Tablet' && device !== 'Mobile') { return; }
        const state = stateForRow($row);
        const inherit = $(this).is(':checked');
        if (!inherit && !state[device].HasOverride) {
            state[device].Interaction = desktopInteraction($row);
        }
        state[device].HasOverride = !inherit;
        writeState($row,state,true);
        renderPanel();
    });
    $(document).on('input', '#' + PANEL_ID + ' input[data-h18-i-path]', function () {
        const $row = selectedRow();
        if (!$row.length) { return; }
        const path = String($(this).attr('data-h18-i-path') || '');
        const value = normalizeInput(path,$(this).val());
        if (panelDevice === 'Desktop') {
            writeDesktop($row,path,value,'input');
        } else {
            const state = stateForRow($row);
            if (!state[panelDevice].HasOverride) { return; }
            setAt(state[panelDevice].Interaction,path,value);
            writeState($row,state,true);
        }
        scheduleRefresh(30);
    });
    $(document).on('change', '#' + PANEL_ID + ' select[data-h18-i-path]', function () {
        const $row = selectedRow();
        if (!$row.length) { return; }
        const path = String($(this).attr('data-h18-i-path') || '');
        const value = normalizeInput(path,$(this).val());
        if (panelDevice === 'Desktop') {
            writeDesktop($row,path,value,'change');
        } else {
            const state = stateForRow($row);
            if (!state[panelDevice].HasOverride) { return; }
            setAt(state[panelDevice].Interaction,path,value);
            writeState($row,state,true);
        }
        scheduleRefresh(30);
    });

    function appendSavePayload() {
        $form.find('[' + SUBMIT_ATTR + '="1"]').remove();
        let index = 0;
        activeRows().each(function () {
            const $row = $(this);
            const key = rowKey($row);
            if (!key) { return; }
            hydrateRow($row);
            const values = { SectionKey:key, StateJson:JSON.stringify(stateForRow($row)) };
            Object.keys(values).forEach(function (name) {
                $('<input>', { type:'hidden', name:'h18_lego_interaction_states[' + index + '][' + name + ']', value:values[name] }).attr(SUBMIT_ATTR,'1').appendTo($form);
            });
            index += 1;
        });
    }
    $form.on('submit.h18InteractionStatesV0834', appendSavePayload);

    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(function () { applyAllPreview(); renderPanel(); }, typeof delay === 'number' ? delay : 45);
    }
    $(document).on('click', '.h18-page-section-header,.h18-page-section-edit,.h18-v0811-edit-child,.h18-ud-auto-box-tile,.h18-ud-box-child-chip,.h18-navigator-select,.h18-preview-state,.h18-preview-device', function () { scheduleRefresh(45); });

    const observer = new MutationObserver(function (mutations) {
        let relevant = false;
        mutations.forEach(function (mutation) {
            if (mutation.type === 'childList') { relevant = true; }
            if (mutation.type === 'attributes' && ['class','data-canvas-device','data-canvas-state'].indexOf(mutation.attributeName) !== -1) { relevant = true; }
        });
        if (relevant) {
            panelDevice = activeCanvasDevice();
            scheduleRefresh(55);
        }
    });
    observer.observe($sections.get(0), { childList:true, subtree:true, attributes:true, attributeFilter:['class'] });
    if ($inspectorTarget.length) { observer.observe($inspectorTarget.get(0), { childList:true, subtree:true }); }
    if ($canvas.length) { observer.observe($canvas.get(0), { attributes:true, attributeFilter:['data-canvas-device','data-canvas-state'] }); }

    activeRows().each(function () { hydrateRow($(this)); });
    applyAllPreview();
    renderPanel();
    document.documentElement.setAttribute('data-h18-lego-interaction-states-runtime','0.8.34');
    window.__h18LegoInteractionStatesV0834 = {
        version:'0.8.34',
        stateForKey:function (key) {
            const $row=activeRows().filter(function(){return rowKey($(this))===String(key||'');}).first();
            return $row.length?stateForRow($row):null;
        },
        effectiveForKey:function (key,device) {
            const $row=activeRows().filter(function(){return rowKey($(this))===String(key||'');}).first();
            if(!$row.length){return null;}
            return effectiveInteraction($row,stateForRow($row),['Desktop','Tablet','Mobile'].indexOf(String(device))!==-1?String(device):'Desktop');
        },
        hasCanonicalField:function (key) {
            const $row=activeRows().filter(function(){return rowKey($(this))===String(key||'');}).first();
            return $row.length?canonicalField($row).length===1:false;
        }
    };
});
