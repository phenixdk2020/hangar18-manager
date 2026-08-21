jQuery(function ($) {
    'use strict';

    const $sections = $('#h18-page-sections-sortable');
    const $canvas = $('.h18-builder-canvas').first();
    const $inspector = $('#h18-page-inspector');
    const $inspectorTarget = $('#h18-page-inspector-target');
    if (!$sections.length || !$canvas.length || !$inspector.length) { return; }

    const STATE_CLASS = 'h18-lego-layout-primary-state-json';
    const FIELD_PATTERN = /^(?:Tablet|Mobile)?(?:PaddingPx|HorizontalPaddingPx|TopSpacingPx|BottomSpacingPx|WidthPercent|MinHeightPx)$|^(?:Columns|MobileColumns|ColumnGapPx|MobileColumnGapPx)$/;
    let refreshTimer = null;

    function activeRows() {
        return $sections.children('.h18-page-section-row:not(.h18-page-section-removed)');
    }

    function selectedRow() {
        return activeRows().filter('.is-selected').first();
    }

    function rowBody($row) {
        const $body = $row.children('.h18-page-section-body').first();
        return $body.length ? $body : $row.find('.h18-page-section-body').first();
    }

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || $row.attr('data-key') || '');
    }

    function fieldNameFromElement(target) {
        if (!target || typeof target.getAttribute !== 'function') { return ''; }
        const quick = String(target.getAttribute('data-canvas-quick-field') || '');
        if (FIELD_PATTERN.test(quick)) { return quick; }
        const name = String(target.getAttribute('name') || '');
        const match = name.match(/\[([^\]]+)\]$/);
        const field = match ? String(match[1] || '') : '';
        return FIELD_PATTERN.test(field) ? field : '';
    }

    function normalizeValue(value) {
        const raw = String(value == null ? '' : value).trim();
        if (raw !== '' && /^-?\d+(?:\.\d+)?$/.test(raw)) {
            const numeric = Number(raw);
            return Number.isFinite(numeric) ? numeric : raw;
        }
        return raw;
    }

    function canonicalField($row) {
        return rowBody($row).find('.' + STATE_CLASS).first();
    }

    function stateFromLegacy($row) {
        const fields = {};
        rowBody($row).find('[name]').each(function () {
            const field = fieldNameFromElement(this);
            if (!field) { return; }
            fields[field] = normalizeValue($(this).val());
        });
        return { SchemaVersion: 1, Fields: fields };
    }

    function normalizeState(raw, $row) {
        raw = raw && typeof raw === 'object' ? raw : {};
        const fallback = stateFromLegacy($row);
        const source = raw.Fields && typeof raw.Fields === 'object' ? raw.Fields : {};
        const fields = Object.assign({}, fallback.Fields);
        Object.keys(source).forEach(function (field) {
            if (FIELD_PATTERN.test(field)) { fields[field] = normalizeValue(source[field]); }
        });
        return { SchemaVersion: 1, Fields: fields };
    }

    function ensureCanonicalField($row) {
        let $field = canonicalField($row);
        if ($field.length) { return $field; }
        $field = $('<input>', {
            type: 'hidden',
            class: STATE_CLASS,
            value: JSON.stringify(stateFromLegacy($row)),
            'data-h18-v0837-layout-state': '1'
        });
        rowBody($row).append($field);
        return $field;
    }

    function stateForRow($row) {
        const $field = ensureCanonicalField($row);
        try {
            return normalizeState(JSON.parse(String($field.val() || '{}')), $row);
        } catch (error) {
            return stateFromLegacy($row);
        }
    }

    function writeFieldState($row, field, value) {
        if (!$row || !$row.length || !FIELD_PATTERN.test(field)) { return; }
        const $state = ensureCanonicalField($row);
        const state = stateForRow($row);
        state.Fields[field] = normalizeValue(value);
        $state.val(JSON.stringify(state));
        $row.attr('data-h18-v0837-layout-canonical', '1');
    }

    function hydrateRow($row) {
        if (!$row || !$row.length) { return; }
        const $state = canonicalField($row);
        if (!$state.length) {
            ensureCanonicalField($row);
        } else {
            try {
                $state.val(JSON.stringify(normalizeState(JSON.parse(String($state.val() || '{}')), $row)));
            } catch (error) {
                $state.val(JSON.stringify(stateFromLegacy($row)));
            }
        }
        $row.attr('data-h18-v0837-layout-canonical', '1');
    }

    function rowForTarget(target) {
        const $target = $(target);
        const $row = $target.closest('.h18-page-section-row');
        if ($row.length) { return $row; }
        if ($target.closest($inspectorTarget).length) { return selectedRow(); }
        return $();
    }

    function markDirectBars() {
        $('.h18-page-section-row.is-selected > .h18-canvas-preview > .h18-canvas-direct-controls').each(function () {
            const $bar = $(this);
            $bar.find('[data-canvas-quick-field]').each(function () {
                const field = fieldNameFromElement(this);
                if (!field) { return; }
                $(this)
                    .attr('data-h18-v0837-layout-proxy', '1')
                    .attr('data-h18-v0837-layout-field', field);
                $(this).closest('.h18-canvas-quick-range')
                    .attr('data-h18-v0837-canonical-layout', '1');
            });
        });
    }

    function markInspector() {
        const $row = selectedRow();
        if (!$row.length || !$inspectorTarget.length) { return; }
        $inspectorTarget.find('[name]').each(function () {
            const field = fieldNameFromElement(this);
            if (!field) { return; }
            $(this)
                .attr('data-h18-v0837-layout-proxy', '1')
                .attr('data-h18-v0837-layout-field', field);
        });
    }

    function refresh() {
        activeRows().each(function () { hydrateRow($(this)); });
        markDirectBars();
        markInspector();
    }

    function scheduleRefresh(delay) {
        window.clearTimeout(refreshTimer);
        refreshTimer = window.setTimeout(refresh, typeof delay === 'number' ? delay : 25);
    }

    function captureLayoutValue(event) {
        const target = event.target;
        const field = fieldNameFromElement(target);
        if (!field) { return; }
        const $row = rowForTarget(target);
        if (!$row.length) { return; }

        // Mirror the value before the existing delegated history handler runs.
        // The original legacy/Inspector/direct event remains the single checkpoint;
        // this hidden canonical state deliberately emits no second input event.
        writeFieldState($row, field, target.value);
        if ($(target).closest('.h18-canvas-direct-controls').length) {
            $(target).attr('data-h18-v0837-layout-proxy', '1');
        }
    }

    document.addEventListener('input', captureLayoutValue, true);
    document.addEventListener('change', captureLayoutValue, true);

    const observer = new MutationObserver(function (mutations) {
        if (mutations.some(function (mutation) {
            return mutation.type === 'childList' || (mutation.type === 'attributes' && mutation.attributeName === 'class');
        })) {
            scheduleRefresh(30);
        }
    });
    observer.observe($sections.get(0), { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
    if ($inspectorTarget.length) {
        observer.observe($inspectorTarget.get(0), { childList: true, subtree: true });
    }

    refresh();
    document.documentElement.setAttribute('data-h18-lego-layout-primary-runtime', '0.8.37');
    window.__h18LegoLayoutPrimaryV0837 = {
        version: '0.8.37',
        fields: FIELD_PATTERN,
        refresh: refresh,
        stateForKey: function (key) {
            const requested = String(key || '');
            const $row = activeRows().filter(function () { return rowKey($(this)) === requested; }).first();
            return $row.length ? stateForRow($row) : null;
        }
    };
});
