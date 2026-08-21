jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $canvas = $('.h18-builder-canvas').first();
    const $inspector = $('#h18-page-inspector');
    if (!$sections.length || !$canvas.length || !$inspector.length) { return; }

    const DESIGN_PANEL = '#h18-ud-lego-responsive-design-panel';
    const INTERACTION_PANEL = '#h18-ud-lego-interaction-states-panel';
    const DESIGN_STATE = '.h18-lego-responsive-design-state-json';
    const INTERACTION_STATE = '.h18-lego-interaction-states-state-json';
    const layoutFieldPattern = /^(?:Desktop|Tablet|Mobile)?(?:PaddingPx|HorizontalPaddingPx|TopSpacingPx|BottomSpacingPx|WidthPercent|MinHeightPx)$|^(?:Columns|MobileColumns|ColumnGapPx|MobileColumnGapPx)$/;
    let refreshTimer = null;
    let routing = false;

    function selectedRow() {
        return $sections.find('.h18-page-section-row:not(.h18-page-section-removed).is-selected').first();
    }
    function rowBody($row) {
        const $body = $row.children('.h18-page-section-body').first();
        return $body.length ? $body : $row.find('.h18-page-section-body').first();
    }
    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || $row.attr('data-key') || '');
    }
    function device() {
        const raw = String($canvas.attr('data-canvas-device') || 'desktop').toLowerCase();
        return raw === 'tablet' ? 'Tablet' : (raw === 'mobile' ? 'Mobile' : 'Desktop');
    }
    function canvasState() {
        return String($canvas.attr('data-canvas-state') || 'normal').toLowerCase();
    }
    function clone(value) {
        return JSON.parse(JSON.stringify(value || {}));
    }
    function stateField($row, selector) {
        return rowBody($row).find(selector).first();
    }
    function parseState($field) {
        try { return JSON.parse(String($field.val() || '{}')); }
        catch (error) { return {}; }
    }
    function activateTab(panel, attr, requested) {
        const $panel = $(panel);
        if (!$panel.length) { return; }
        const $current = $panel.find('[' + attr + '].is-active').first();
        if (String($current.attr(attr) || '') === requested) { return; }
        const $button = $panel.find('[' + attr + '="' + requested + '"]').first();
        if ($button.length) { $button.trigger('click'); }
    }

    function seedResponsiveOverride($row, requested) {
        if (requested === 'Desktop') { return; }
        const $field = stateField($row, DESIGN_STATE);
        if (!$field.length) { return; }
        const state = parseState($field);
        if (!state[requested] || typeof state[requested] !== 'object') { state[requested] = {}; }
        if (!state[requested].InheritDesktop) { return; }
        if (!state[requested].HasOverride) {
            const bridge = window.__h18LegoResponsiveDesignV0833;
            const effective = bridge && typeof bridge.effectiveForKey === 'function'
                ? bridge.effectiveForKey(rowKey($row), 'Desktop')
                : null;
            if (effective && effective.Design) { state[requested].Design = clone(effective.Design); }
            state[requested].HasOverride = true;
        }
        state[requested].InheritDesktop = false;
        // Silent seed: the following canonical control event owns the one history checkpoint.
        $field.val(JSON.stringify(state));
    }

    function seedInteractionOverride($row, requested) {
        if (requested === 'Desktop') { return; }
        const $field = stateField($row, INTERACTION_STATE);
        if (!$field.length) { return; }
        const state = parseState($field);
        if (!state[requested] || typeof state[requested] !== 'object') { state[requested] = {}; }
        if (state[requested].HasOverride) { return; }
        const bridge = window.__h18LegoInteractionStatesV0834;
        const effective = bridge && typeof bridge.effectiveForKey === 'function'
            ? bridge.effectiveForKey(rowKey($row), 'Desktop')
            : null;
        if (effective && effective.Interaction) { state[requested].Interaction = clone(effective.Interaction); }
        state[requested].HasOverride = true;
        $field.val(JSON.stringify(state));
        $row.attr('data-h18-interaction-' + requested.toLowerCase() + '-snapshot', '1');
    }

    function designPathForDirect(target) {
        const $target = $(target);
        if ($target.is('[data-canvas-color-role]')) {
            const role = String($target.attr('data-canvas-color-role') || 'background');
            const suffix = role === 'text' ? 'Text' : (role === 'heading' ? 'Heading' : 'Background');
            return canvasState() === 'hover' ? 'States.Hover.' + suffix : 'Colors.' + suffix;
        }
        const field = String($target.attr('data-canvas-quick-field') || '');
        if (field === 'RadiusPx') { return 'Radius.All'; }
        if (field === 'HoverOpacityPercent') { return 'States.Hover.Opacity'; }
        if (field === 'SectionOpacityPercent') { return 'Effects.Opacity'; }
        return '';
    }

    function routeDesign($row, path, value) {
        const requested = device();
        activateTab(DESIGN_PANEL, 'data-h18-rd-tab', requested);
        seedResponsiveOverride($row, requested);
        const $input = $(DESIGN_PANEL + ' [data-h18-rd-device-panel="' + requested + '"] [data-h18-rd-path="' + path + '"]').first();
        if (!$input.length) { return false; }
        $input.prop('disabled', false).val(String(value));
        const eventName = $input.is('select') ? 'change' : 'input';
        $input.trigger(eventName);
        return true;
    }

    function routeInteraction($row, path, value) {
        const requested = device();
        activateTab(INTERACTION_PANEL, 'data-h18-i-tab', requested);
        seedInteractionOverride($row, requested);
        const $input = $(INTERACTION_PANEL + ' [data-h18-i-device-panel="' + requested + '"] [data-h18-i-path="' + path + '"]').first();
        if (!$input.length) { return false; }
        $input.prop('disabled', false).val(String(value));
        const eventName = $input.is('select') ? 'change' : 'input';
        $input.trigger(eventName);
        return true;
    }

    function directBarFor(target) {
        const $target = $(target);
        const $bar = $target.closest('.h18-canvas-direct-controls');
        if (!$bar.length || !$bar.closest('.h18-canvas-preview').length) { return $(); }
        return $bar;
    }

    function markBar($bar) {
        if (!$bar || !$bar.length) { return; }
        $bar.attr('data-h18-v0836-primary-view', '1');
        $bar.find('.h18-canvas-direct-title').first().text('Direkte design · LEGO');
        if (!$bar.children('.h18-v0836-view-badge').length) {
            $bar.prepend($('<span>', { class:'h18-v0836-view-badge', text:'Samme state som Inspector' }));
        }
        $bar.find('[data-canvas-color-role]').attr('data-h18-v0836-proxy', 'design');
        $bar.find('[data-canvas-quick-field]').each(function () {
            const $input = $(this);
            const field = String($input.attr('data-canvas-quick-field') || '');
            if (field === 'RadiusPx' || field === 'SectionOpacityPercent' || field === 'HoverOpacityPercent') {
                $input.attr('data-h18-v0836-proxy', canvasState() === 'disabled' && field === 'SectionOpacityPercent' ? 'interaction' : 'design');
            } else if (layoutFieldPattern.test(field)) {
                $input.attr('data-h18-v0836-layout-control', '1');
            }
        });
        const $layout = $bar.find('[data-h18-v0836-layout-control="1"]').closest('.h18-canvas-quick-range');
        $layout.attr('data-h18-v0836-layout-only', '1');
        const $canonical = $bar.find('[data-h18-v0836-proxy]').closest('.h18-canvas-quick-range,.h18-canvas-quick-color');
        $canonical.attr('data-h18-v0836-canonical-view', '1');
    }

    function refreshBars() {
        $('.h18-page-section-row.is-selected > .h18-canvas-preview > .h18-canvas-direct-controls').each(function () { markBar($(this)); });
    }
    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(refreshBars, typeof delay === 'number' ? delay : 20);
    }

    // Native capture runs before legacy jQuery delegated handlers. Canonical LEGO
    // controls receive the edit, so legacy fields are updated only by the one
    // existing LEGO transaction and no duplicate history checkpoint is emitted.
    document.addEventListener('input', function (event) {
        if (routing) { return; }
        const target = event.target;
        if (!target || typeof target.matches !== 'function') { return; }
        const $bar = directBarFor(target);
        if (!$bar.length) { return; }
        const proxy = String(target.getAttribute('data-h18-v0836-proxy') || '');
        if (!proxy) { return; }
        const $row = $(target).closest('.h18-page-section-row');
        if (!$row.length) { return; }

        const field = String(target.getAttribute('data-canvas-quick-field') || '');
        const isDisabledOpacity = proxy === 'interaction' || (canvasState() === 'disabled' && field === 'SectionOpacityPercent');
        const path = isDisabledOpacity ? 'Disabled.Opacity' : designPathForDirect(target);
        if (!path) { return; }

        event.stopImmediatePropagation();
        routing = true;
        try {
            if (isDisabledOpacity) { routeInteraction($row, path, target.value); }
            else { routeDesign($row, path, target.value); }
        } finally {
            routing = false;
            scheduleRefresh(45);
        }
    }, true);

    const observer = new MutationObserver(function (mutations) {
        if (mutations.some(function (mutation) {
            return mutation.type === 'childList' || (mutation.type === 'attributes' && ['class','data-canvas-device','data-canvas-state'].indexOf(mutation.attributeName) !== -1);
        })) { scheduleRefresh(25); }
    });
    observer.observe($sections.get(0), { childList:true, subtree:true, attributes:true, attributeFilter:['class'] });
    observer.observe($canvas.get(0), { attributes:true, attributeFilter:['data-canvas-device','data-canvas-state'] });

    refreshBars();
    document.documentElement.setAttribute('data-h18-lego-primary-view-runtime', '0.8.36');
    window.__h18LegoPrimaryViewV0836 = {
        version:'0.8.36',
        refresh:refreshBars,
        device:device,
        state:canvasState
    };
});
