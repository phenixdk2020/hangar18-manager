jQuery(function ($) {
    'use strict';

    const config = window.H18LegoInteractionStatesV0834 || {};
    const $form = $('#h18-page-editor-form');
    const $sections = $('#h18-page-sections-sortable');
    if (!$form.length || !$sections.length) { return; }

    function activeRows() { return $sections.find('.h18-page-section-row:not(.h18-page-section-removed)'); }
    function selectedRow() { return activeRows().filter('.is-selected').first(); }
    function rowBody($row) {
        const $direct = $row.children('.h18-page-section-body').first();
        return $direct.length ? $direct : $row.find('.h18-page-section-body').first();
    }
    function rowKey($row) {
        return String($row.find('.h18-page-section-key').first().val() || $row.attr('data-key') || '');
    }
    function pageSlug() { return String($form.find('[name="page_slug"]').first().val() || '').trim(); }
    function stateField($row) { return rowBody($row).find('.h18-lego-interaction-states-state-json').first(); }
    function snapshotAttr(device) { return 'data-h18-interaction-' + device.toLowerCase() + '-snapshot'; }

    function storedSections() {
        const pages = config.pages && typeof config.pages === 'object' ? config.pages : {};
        const page = pages[pageSlug()] && typeof pages[pageSlug()] === 'object' ? pages[pageSlug()] : {};
        return page.Sections && typeof page.Sections === 'object' ? page.Sections : {};
    }

    function markStoredSnapshots() {
        const stored = storedSections();
        activeRows().each(function () {
            const $row = $(this);
            const section = stored[rowKey($row)] && typeof stored[rowKey($row)] === 'object' ? stored[rowKey($row)] : {};
            ['Tablet','Mobile'].forEach(function (device) {
                const entry = section[device] && typeof section[device] === 'object' ? section[device] : {};
                const exists = Boolean(entry.InteractionHasSnapshot || entry.InteractionHasOverride);
                if (exists) { $row.attr(snapshotAttr(device), '1'); }
                else if (!$row.is('[' + snapshotAttr(device) + ']')) { $row.attr(snapshotAttr(device), '0'); }
            });
        });
    }

    // Run before the delegated v0.8.34 change handler. If an inactive snapshot
    // exists, temporarily expose it as an override so the main runtime does not
    // reseed from Desktop when inheritance is disabled again.
    document.addEventListener('change', function (event) {
        const target = event.target;
        if (!target || typeof target.matches !== 'function' || !target.matches('#h18-ud-lego-interaction-states-panel [data-h18-i-inherit]')) { return; }
        const device = String(target.getAttribute('data-h18-i-inherit') || '');
        if (device !== 'Tablet' && device !== 'Mobile') { return; }
        const $row = selectedRow();
        if (!$row.length || target.checked) { return; }
        const hasSnapshot = String($row.attr(snapshotAttr(device)) || '0') === '1';
        if (!hasSnapshot) { return; }
        const $field = stateField($row);
        if (!$field.length) { return; }
        try {
            const state = JSON.parse(String($field.val() || '{}'));
            if (state[device] && typeof state[device] === 'object') {
                state[device].HasOverride = true;
                $field.val(JSON.stringify(state));
            }
        } catch (error) {
            // Main runtime will fall back to current Desktop if state is invalid.
        }
    }, true);

    $(document).on('change', '#h18-ud-lego-interaction-states-panel [data-h18-i-inherit]', function () {
        const device = String($(this).attr('data-h18-i-inherit') || '');
        const $row = selectedRow();
        if ($row.length && (device === 'Tablet' || device === 'Mobile') && !$(this).is(':checked')) {
            $row.attr(snapshotAttr(device), '1');
        }
    });

    $(document).on('input change', '#h18-ud-lego-interaction-states-panel [data-h18-i-path]', function () {
        const device = String($('#h18-ud-lego-interaction-states-panel [data-h18-i-tab].is-active').attr('data-h18-i-tab') || 'Desktop');
        const $row = selectedRow();
        if ($row.length && (device === 'Tablet' || device === 'Mobile')) {
            $row.attr(snapshotAttr(device), '1');
        }
    });

    // The main runtime appends the save payload first. This later submit handler
    // enriches that payload with HasSnapshot without adding a second persistence
    // domain or producing another history event.
    $form.on('submit.h18InteractionSnapshotV0834', function () {
        $form.find('input[name^="h18_lego_interaction_states"][name$="[StateJson]"]').each(function () {
            const $json = $(this);
            const name = String($json.attr('name') || '');
            const prefix = name.replace(/\[StateJson\]$/, '');
            let key = '';
            $form.find('input[name^="h18_lego_interaction_states"][name$="[SectionKey]"]').each(function () {
                if (String($(this).attr('name') || '').replace(/\[SectionKey\]$/, '') === prefix) { key = String($(this).val() || ''); }
            });
            if (!key) { return; }
            const $row = activeRows().filter(function () { return rowKey($(this)) === key; }).first();
            if (!$row.length) { return; }
            try {
                const state = JSON.parse(String($json.val() || '{}'));
                ['Tablet','Mobile'].forEach(function (device) {
                    if (!state[device] || typeof state[device] !== 'object') { state[device] = {}; }
                    state[device].HasSnapshot = String($row.attr(snapshotAttr(device)) || '0') === '1';
                });
                $json.val(JSON.stringify(state));
            } catch (error) {
                // Server-side normalization rejects malformed payloads safely.
            }
        });
    });

    markStoredSnapshots();
    const observer = new MutationObserver(function (mutations) {
        if (mutations.some(function (mutation) { return mutation.type === 'childList'; })) {
            window.setTimeout(markStoredSnapshots, 0);
        }
    });
    observer.observe($sections.get(0), { childList:true, subtree:false });

    document.documentElement.setAttribute('data-h18-lego-interaction-snapshot-runtime', '0.8.34');
}());
