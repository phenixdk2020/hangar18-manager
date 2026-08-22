(function ($) {
    'use strict';

    const ROW_SELECTOR = '#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)';
    const INSPECTOR_SELECTOR = '#h18-page-inspector-target';
    const PARENT_TYPES = ['container', 'flex', 'grid'];
    const AUTO_LABEL = 'Auto-kasser';
    const RECONCILE_DELAYS = [80, 180, 360, 700, 1100, 1700];
    let reconcileToken = 0;

    function controls($row, selector) {
        if (!$row || !$row.length) { return $(); }
        let $result = $row.find(selector);
        if ($row.hasClass('is-selected')) {
            $result = $result.add($(INSPECTOR_SELECTOR).find(selector));
        }
        return $result;
    }

    function rowKey($row) {
        return String(controls($row, '.h18-page-section-key').first().val() || '');
    }

    function parentKey($row) {
        return String(controls($row, '.h18-layout-parent-key').first().val() || '');
    }

    function rowLabel($row) {
        return String(controls($row, '.h18-section-navigator-label').first().val() || '').trim();
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
        const navigator = rowLabel($parent);
        if (navigator) { return navigator; }
        const summary = String($parent.find('.h18-page-section-title-summary').first().text() || '').trim();
        if (summary) { return summary; }
        const type = String($parent.attr('data-section-type') || '').trim();
        return type === 'grid' ? AUTO_LABEL : (type === 'container' ? 'Kasse' : (type || 'Layout-parent'));
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
        const parentKeyValue = String(value || '');
        if (!$row || !$row.length || !parentKeyValue) { return false; }

        const $parent = rowByKey(parentKeyValue);
        if (!$parent.length || !PARENT_TYPES.includes(String($parent.attr('data-section-type') || ''))) {
            return false;
        }

        const label = parentLabel($parent);
        controls($row, '.h18-layout-parent-select').each(function () {
            ensureOption($(this), parentKeyValue, label);
        });
        return true;
    }

    function activeRows() {
        return $(ROW_SELECTOR);
    }

    function directChildCount($auto) {
        const key = rowKey($auto);
        if (!key) { return 0; }
        let count = 0;
        activeRows().each(function () {
            if (parentKey($(this)) === key) { count += 1; }
        });
        return count;
    }

    function visualChildCount($auto) {
        const $preview = $auto.children('.h18-canvas-preview').first();
        if (!$preview.length) { return 0; }
        return $preview.find('.h18-ud-auto-box-grid .h18-v0811-auto-box').length;
    }

    function autoRows() {
        return activeRows().filter(function () {
            const $row = $(this);
            return String($row.attr('data-section-type') || '') === 'grid' && rowLabel($row) === AUTO_LABEL;
        });
    }

    function needsVisualReconcile() {
        let mismatch = false;
        autoRows().each(function () {
            const $auto = $(this);
            const expected = directChildCount($auto);
            const actual = visualChildCount($auto);
            if (expected !== actual) {
                mismatch = true;
                return false;
            }
        });
        return mismatch;
    }

    function reconcileNow() {
        if (!needsVisualReconcile()) { return false; }
        const nesting = window.__h18NestingToolsV0840;
        if (!nesting || typeof nesting.refresh !== 'function') { return false; }
        nesting.refresh();
        return true;
    }

    function armVisualReconcile() {
        reconcileToken += 1;
        const token = reconcileToken;
        RECONCILE_DELAYS.forEach(function (delay) {
            window.setTimeout(function () {
                if (token !== reconcileToken) { return; }
                reconcileNow();
            }, delay);
        });
    }

    // The canonical nesting motor writes LayoutParentKey first and then mirrors
    // it to the human-facing select. In the full WordPress editor the select's
    // normal change handler writes its value back to LayoutParentKey. If the
    // newly created Auto-kasser row has not yet been added to that select, a
    // .val(newKey) becomes null and the normal handler erases the valid parent.
    // Guard only the control handoff: it never chooses a parent or moves a row.
    // Selected rows keep their structural fields in Inspector, so parent lookup
    // and label/select synchronization must use the same Inspector-aware view.
    $(document).on('change.h18V0845ParentKeyGuard', '.h18-layout-parent-key', function () {
        const value = String($(this).val() || '');
        if (value) {
            ensureParentOption(rowForControl(this), value);
        }
        armVisualReconcile();
    });

    // Live WordPress can perform one more canvas/Inspector repaint after the
    // canonical side-drop has already committed the correct LayoutParentKey
    // model. That late repaint can leave an existing Auto-kasse preview at
    // "0 stk." even though the two rows already point at the Auto-kasse. Undo
    // followed by Redo fixes it because history performs a full render. These
    // bounded post-gesture checkpoints perform only that missing visual
    // reconciliation. They never create/move rows, write parents or touch
    // history/persistence; nesting-tools remains the single placement authority.
    document.addEventListener('drop', armVisualReconcile, true);
    document.addEventListener('dragend', armVisualReconcile, true);

    document.documentElement.setAttribute('data-h18-lego-parent-key-guard', '0.8.45');
    document.documentElement.setAttribute('data-h18-lego-live-reconcile', '0.8.45');
    window.__h18LegoParentKeyGuardV0845 = {
        version: '0.8.45',
        ensureParentOption: function (rowKeyValue, parentKeyValue) {
            return ensureParentOption(rowByKey(rowKeyValue), parentKeyValue);
        },
        reconcileNow: reconcileNow,
        needsVisualReconcile: needsVisualReconcile,
        armVisualReconcile: armVisualReconcile
    };
}(jQuery));
