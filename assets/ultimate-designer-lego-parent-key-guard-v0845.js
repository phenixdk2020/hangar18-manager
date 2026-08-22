(function ($) {
    'use strict';

    const ROW_SELECTOR = '#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)';
    const PARENT_TYPES = ['container', 'flex', 'grid'];

    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || '');
    }

    function rowByKey(key) {
        const requested = String(key || '');
        if (!requested) { return $(); }
        return $(ROW_SELECTOR).filter(function () {
            return rowKey($(this)) === requested;
        }).first();
    }

    function rowForControl(control) {
        const $direct = $(control).closest('.h18-page-section-row');
        if ($direct.length) { return $direct; }
        return $(ROW_SELECTOR + '.is-selected').first();
    }

    function parentLabel($parent) {
        if (!$parent || !$parent.length) { return 'Layout-parent'; }
        const navigator = String($parent.find('.h18-section-navigator-label').first().val() || '').trim();
        if (navigator) { return navigator; }
        const summary = String($parent.find('.h18-page-section-title-summary').first().text() || '').trim();
        if (summary) { return summary; }
        const type = String($parent.attr('data-section-type') || '').trim();
        return type === 'grid' ? 'Auto-kasser' : (type === 'container' ? 'Kasse' : (type || 'Layout-parent'));
    }

    function hasOption($select, value) {
        let found = false;
        $select.find('option').each(function () {
            if (String(this.value || '') === String(value || '')) {
                found = true;
                return false;
            }
        });
        return found;
    }

    function ensureOption($select, value, label) {
        if (!$select || !$select.length || !value || hasOption($select, value)) { return; }
        $select.append($('<option>', {
            value: String(value),
            text: String(label || value)
        }));
    }

    function ensureParentOption($row, value) {
        const parentKey = String(value || '');
        if (!$row || !$row.length || !parentKey) { return false; }

        const $parent = rowByKey(parentKey);
        if (!$parent.length || !PARENT_TYPES.includes(String($parent.attr('data-section-type') || ''))) {
            return false;
        }

        const label = parentLabel($parent);
        $row.find('.h18-layout-parent-select').each(function () {
            ensureOption($(this), parentKey, label);
        });

        if ($row.hasClass('is-selected')) {
            $('#h18-page-inspector-target .h18-layout-parent-select').each(function () {
                ensureOption($(this), parentKey, label);
            });
        }
        return true;
    }

    // The canonical nesting motor writes LayoutParentKey first and then mirrors
    // it to the human-facing select. In the full WordPress editor the select's
    // normal change handler writes its value back to LayoutParentKey. If the
    // newly created Auto-kasser row has not yet been added to that select, a
    // .val(newKey) becomes null and the normal handler erases the valid parent.
    // Guard only the control handoff: it never chooses a parent or moves a row.
    $(document).on('change.h18V0845ParentKeyGuard', '.h18-layout-parent-key', function () {
        const value = String($(this).val() || '');
        if (!value) { return; }
        ensureParentOption(rowForControl(this), value);
    });

    document.documentElement.setAttribute('data-h18-lego-parent-key-guard', '0.8.45');
    window.__h18LegoParentKeyGuardV0845 = {
        version: '0.8.45',
        ensureParentOption: function (rowKeyValue, parentKeyValue) {
            return ensureParentOption(rowByKey(rowKeyValue), parentKeyValue);
        }
    };
}(jQuery));
