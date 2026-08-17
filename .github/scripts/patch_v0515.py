from pathlib import Path
import re

VERSION_OLD = '0.5.14'
VERSION_NEW = '0.5.15'


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 anchor, found {count}')
    return text.replace(old, new, 1)

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
css_path = Path('assets/admin.css')
readme_path = Path('readme.txt')

php = php_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')

php = replace_once(php, ' * Version: 0.5.14', ' * Version: 0.5.15', 'plugin header version')
php = replace_once(php, "    const VERSION = '0.5.14';", "    const VERSION = '0.5.15';", 'plugin const version')

state_old = """    let currentCanvasState = 'normal';
    let selectedCanvasCardKey = '';
    const sectionDesignClipboardStorageKey = 'hangar18SectionDesignClipboardV0511';
"""
state_new = """    let currentCanvasState = 'normal';
    let selectedCanvasCardKey = '';
    const multiSelectedSectionKeys = new Set();
    let canvasZoomPercentV0515 = 100;
    let canvasOutlineModeV0515 = false;
    let canvasGuideModeV0515 = false;
    const canvasWorkspaceStorageKeyV0515 = 'hangar18CanvasWorkspaceV0515';
    let contextMenuRowV0515 = $();
    let contextMenuReturnFocusV0515 = null;
    const sectionDesignClipboardStorageKey = 'hangar18SectionDesignClipboardV0511';
"""
js = replace_once(js, state_old, state_new, 'editor state anchor')

inspect_old = """    function inspectPageSection($row) {
        if (!$pageInspectorTarget.length || !$row.length || $row.hasClass('h18-page-section-removed')) {
            return;
        }
        if ($inspectedSection.length && $inspectedSection.get(0) === $row.get(0)) {
            return;
        }
"""
inspect_new = """    function inspectPageSection($row, preserveMultiSelection) {
        if (!$pageInspectorTarget.length || !$row.length || $row.hasClass('h18-page-section-removed')) {
            return;
        }
        if (preserveMultiSelection !== true) {
            multiSelectClearV0515(false);
        }
        if ($inspectedSection.length && $inspectedSection.get(0) === $row.get(0)) {
            syncMultiSelectUiV0515();
            return;
        }
"""
js = replace_once(js, inspect_old, inspect_new, 'inspectPageSection signature')

navigator_old = """    $(document).on('click', '.h18-navigator-select', function () {
        const index = String($(this).closest('.h18-navigator-item').attr('data-section-index') || '');
        const $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
        inspectPageSection($row);
    });
"""
navigator_new = """    $(document).on('click', '.h18-navigator-select', function (event) {
        const index = String($(this).closest('.h18-navigator-item').attr('data-section-index') || '');
        const $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
        if (event.ctrlKey || event.metaKey || event.shiftKey) {
            event.preventDefault();
            toggleMultiSelectRowV0515($row);
            return;
        }
        inspectPageSection($row);
    });
"""
js = replace_once(js, navigator_old, navigator_new, 'navigator select handler')

canvas_old = """    $(document).on('click keydown', '.h18-canvas-preview', function (event) {
        if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) { return; }
        if ($(event.target).closest('.h18-canvas-inline-edit.is-editing').length) { return; }
        event.preventDefault();
        inspectPageSection($(this).closest('.h18-page-section-row'));
    });
"""
canvas_new = """    $(document).on('click keydown', '.h18-canvas-preview', function (event) {
        if (event.type === 'keydown' && !['Enter', ' '].includes(event.key)) { return; }
        if ($(event.target).closest('.h18-canvas-inline-edit.is-editing').length) { return; }
        event.preventDefault();
        const $row = $(this).closest('.h18-page-section-row');
        if (event.type === 'click' && (event.ctrlKey || event.metaKey || event.shiftKey)) {
            toggleMultiSelectRowV0515($row);
            return;
        }
        inspectPageSection($row);
    });
"""
js = replace_once(js, canvas_old, canvas_new, 'canvas selection handler')

# Keep navigator selection state synchronized with multi-select after rebuilds.
nav_selected_old = """            const active = $row.find('.h18-section-active').is(':checked');
            const selected = $inspectedSection.length && $inspectedSection.get(0) === $row.get(0);
            const $item = $('<div>', { class: 'h18-navigator-item' + (selected ? ' is-selected' : ''), 'data-section-index': index });
"""
nav_selected_new = """            const active = $row.find('.h18-section-active').is(':checked');
            const selected = $inspectedSection.length && $inspectedSection.get(0) === $row.get(0);
            const sectionKeyV0515 = String($row.find('.h18-page-section-key').val() || '');
            const multiSelectedV0515 = sectionKeyV0515 && multiSelectedSectionKeys.has(sectionKeyV0515);
            const $item = $('<div>', { class: 'h18-navigator-item' + (selected ? ' is-selected' : '') + (multiSelectedV0515 ? ' is-multi-selected' : ''), 'data-section-index': index });
"""
js = replace_once(js, nav_selected_old, nav_selected_new, 'navigator multi-select class')

workspace_block = r'''

    /* ================================================================
       v0.5.15 – E1 Editor Shell completion
       UD-017 multi-select/common properties
       UD-018 zoom/guides/outline workspace
       UD-019 accessible context menu
       ================================================================ */

    function sectionKeyV0515($row) {
        return $row && $row.length ? String($row.find('.h18-page-section-key').val() || '') : '';
    }

    function multiSelectRowsV0515() {
        const rows = [];
        const validKeys = new Set();
        $pageSections.children('.h18-page-section-row:not(.h18-page-section-removed)').each(function () {
            const $row = $(this);
            const key = sectionKeyV0515($row);
            if (key && multiSelectedSectionKeys.has(key)) {
                rows.push($row);
                validKeys.add(key);
            }
        });
        Array.from(multiSelectedSectionKeys).forEach(function (key) {
            if (!validKeys.has(key)) { multiSelectedSectionKeys.delete(key); }
        });
        return rows;
    }

    function ensureMultiEditPanelV0515() {
        if (!$pageInspector.length || $('#h18-multi-edit-panel').length) { return; }
        const $panel = $('<section>', {
            id: 'h18-multi-edit-panel',
            class: 'h18-multi-edit-panel',
            'aria-live': 'polite',
            hidden: true
        });
        $panel.append(
            $('<div>', { class: 'h18-multi-edit-heading' }).append(
                $('<div>').append(
                    $('<strong>', { text: 'Flere elementer valgt' }),
                    $('<small>', { id: 'h18-multi-edit-count', text: '0 elementer' })
                ),
                $('<button>', { type: 'button', class: 'button-link', id: 'h18-multi-clear', text: 'Ryd markering' })
            )
        );
        const $grid = $('<div>', { class: 'h18-multi-edit-grid' });
        $grid.append(
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'Background' }).append(
                $('<span>', { text: 'Baggrund' }),
                $('<select>', { id: 'h18-multi-background' }).append(
                    $('<option>', { value: '', text: 'Behold hver værdi' }),
                    $('<option>', { value: 'White', text: 'Hvid' }),
                    $('<option>', { value: 'OffWhite', text: 'Off-white' }),
                    $('<option>', { value: 'Sand', text: 'Sand' }),
                    $('<option>', { value: 'Steel', text: 'Stål' }),
                    $('<option>', { value: 'Olive', text: 'Oliven' })
                )
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'DesktopAlignment' }).append(
                $('<span>', { text: 'Desktop-placering' }),
                $('<select>', { id: 'h18-multi-alignment' }).append(
                    $('<option>', { value: '', text: 'Behold hver værdi' }),
                    $('<option>', { value: 'Left', text: 'Venstre' }),
                    $('<option>', { value: 'Center', text: 'Midt' })
                )
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'PaddingPx' }).append(
                $('<span>', { text: 'Indvendig luft' }),
                $('<input>', { id: 'h18-multi-padding', type: 'number', min: 0, max: 160, step: 1, placeholder: 'Behold' })
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'RadiusPx' }).append(
                $('<span>', { text: 'Radius' }),
                $('<input>', { id: 'h18-multi-radius', type: 'number', min: 0, max: 160, step: 1, placeholder: 'Behold' })
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'SectionOpacityPercent' }).append(
                $('<span>', { text: 'Opacity %' }),
                $('<input>', { id: 'h18-multi-opacity', type: 'number', min: 0, max: 100, step: 1, placeholder: 'Behold' })
            ),
            $('<label>', { class: 'h18-multi-field', 'data-common-field': 'Active' }).append(
                $('<span>', { text: 'Synlighed' }),
                $('<select>', { id: 'h18-multi-active' }).append(
                    $('<option>', { value: '', text: 'Behold hver værdi' }),
                    $('<option>', { value: '1', text: 'Synlig' }),
                    $('<option>', { value: '0', text: 'Skjult' })
                )
            )
        );
        $panel.append($grid);
        $panel.append(
            $('<div>', { class: 'h18-multi-edit-actions' }).append(
                $('<button>', { type: 'button', class: 'button button-primary', id: 'h18-multi-apply', text: 'Anvend på valgte' }),
                $('<span>', { class: 'description', text: 'Kun felter, som alle valgte elementer understøtter, bliver vist.' })
            )
        );
        $panel.insertBefore($pageInspectorTarget);
    }

    function multiSelectCommonFieldV0515(rows, fieldName) {
        if (!rows.length) { return false; }
        return rows.every(function ($row) {
            return pageSectionControls($row, '[name$="[' + fieldName + ']"]').length > 0;
        });
    }

    function syncMultiSelectUiV0515() {
        const rows = multiSelectRowsV0515();
        $pageSections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            $row.toggleClass('is-multi-selected', multiSelectedSectionKeys.has(sectionKeyV0515($row)));
        });
        $pageNavigatorList.children('.h18-navigator-item').each(function () {
            const index = String($(this).attr('data-section-index') || '');
            const $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
            $(this).toggleClass('is-multi-selected', multiSelectedSectionKeys.has(sectionKeyV0515($row)));
        });
        ensureMultiEditPanelV0515();
        const visible = rows.length > 1;
        const $panel = $('#h18-multi-edit-panel');
        $panel.prop('hidden', !visible);
        $('#h18-multi-edit-count').text(rows.length + ' elementer');
        if (visible) {
            $panel.find('[data-common-field]').each(function () {
                const fieldName = String($(this).attr('data-common-field') || '');
                $(this).prop('hidden', !multiSelectCommonFieldV0515(rows, fieldName));
            });
        }
    }

    function multiSelectClearV0515(updateInspector) {
        if (!multiSelectedSectionKeys.size) {
            syncMultiSelectUiV0515();
            return;
        }
        multiSelectedSectionKeys.clear();
        syncMultiSelectUiV0515();
        if (updateInspector === true && $inspectedSection.length) {
            refreshInspectorMeta($inspectedSection);
        }
    }

    function toggleMultiSelectRowV0515($row) {
        if (!$row || !$row.length || $row.hasClass('h18-page-section-removed')) { return; }
        const key = sectionKeyV0515($row);
        if (!key) { return; }
        if (!multiSelectedSectionKeys.size && $inspectedSection.length) {
            const inspectedKey = sectionKeyV0515($inspectedSection);
            if (inspectedKey) { multiSelectedSectionKeys.add(inspectedKey); }
        }
        if (multiSelectedSectionKeys.has(key)) { multiSelectedSectionKeys.delete(key); }
        else { multiSelectedSectionKeys.add(key); }

        const rows = multiSelectRowsV0515();
        if (rows.length < 2) {
            const remaining = rows.length ? rows[0] : null;
            multiSelectedSectionKeys.clear();
            syncMultiSelectUiV0515();
            if (remaining && remaining.length) { inspectPageSection(remaining, true); }
            return;
        }
        inspectPageSection($row, true);
        syncMultiSelectUiV0515();
    }

    function multiSelectSetFieldV0515($row, fieldName, value) {
        const $control = pageSectionControls($row, '[name$="[' + fieldName + ']"]').first();
        if (!$control.length) { return false; }
        if ($control.is(':checkbox')) {
            $control.prop('checked', String(value) === '1' || value === true).trigger('change');
        } else {
            $control.val(value).trigger('input').trigger('change');
        }
        renderCanvasPreview($row);
        return true;
    }

    function multiSelectApplyV0515() {
        const rows = multiSelectRowsV0515();
        if (rows.length < 2) { return; }
        const changes = [
            ['Background', $('#h18-multi-background').val()],
            ['DesktopAlignment', $('#h18-multi-alignment').val()],
            ['PaddingPx', $('#h18-multi-padding').val()],
            ['RadiusPx', $('#h18-multi-radius').val()],
            ['SectionOpacityPercent', $('#h18-multi-opacity').val()],
            ['Active', $('#h18-multi-active').val()]
        ].filter(function (item) { return String(item[1] ?? '') !== ''; });
        if (!changes.length) {
            window.alert('Vælg mindst én fælles værdi, der skal ændres.');
            return;
        }
        rows.forEach(function ($row) {
            changes.forEach(function (item) {
                if (multiSelectCommonFieldV0515(rows, item[0])) {
                    multiSelectSetFieldV0515($row, item[0], item[1]);
                }
            });
        });
        syncPageSectionOrder(true);
        rebuildPageNavigator();
        refreshAllCanvasPreviews();
        syncMultiSelectUiV0515();
        scheduleEditorHistoryCapture(0);
        $('#h18-multi-edit-panel input').val('');
        $('#h18-multi-edit-panel select').val('');
        const $button = $('#h18-multi-apply').text('Anvendt ✓');
        window.setTimeout(function () { $button.text('Anvend på valgte'); }, 1000);
    }

    $(document).on('click', '#h18-multi-clear', function () { multiSelectClearV0515(true); });
    $(document).on('click', '#h18-multi-apply', multiSelectApplyV0515);
    $(document).on('click', '.h18-page-section-delete', function () {
        window.setTimeout(syncMultiSelectUiV0515, 0);
    });

    function loadCanvasWorkspaceV0515() {
        try {
            const raw = window.localStorage ? window.localStorage.getItem(canvasWorkspaceStorageKeyV0515) : '';
            const saved = raw ? JSON.parse(raw) : null;
            if (saved && typeof saved === 'object') {
                canvasZoomPercentV0515 = Math.max(50, Math.min(150, parseInt(saved.zoom, 10) || 100));
                canvasOutlineModeV0515 = saved.outline === true;
                canvasGuideModeV0515 = saved.guides === true;
            }
        } catch (error) {}
    }

    function saveCanvasWorkspaceV0515() {
        try {
            if (window.localStorage) {
                window.localStorage.setItem(canvasWorkspaceStorageKeyV0515, JSON.stringify({
                    zoom: canvasZoomPercentV0515,
                    outline: canvasOutlineModeV0515,
                    guides: canvasGuideModeV0515
                }));
            }
        } catch (error) {}
    }

    function applyCanvasWorkspaceV0515() {
        if (!$pageSections.length) { return; }
        const scale = Math.max(0.5, Math.min(1.5, canvasZoomPercentV0515 / 100));
        const supportsZoom = Boolean(window.CSS && CSS.supports && CSS.supports('zoom', '1'));
        if (supportsZoom) {
            $pageSections.css({ zoom: String(scale), transform: '', transformOrigin: '', width: '' });
        } else {
            $pageSections.css({
                zoom: '',
                transform: 'scale(' + scale + ')',
                transformOrigin: 'top center',
                width: (100 / scale) + '%'
            });
        }
        $pageSections.toggleClass('h18-canvas-outline-mode', canvasOutlineModeV0515);
        $pageSections.toggleClass('h18-canvas-guide-mode', canvasGuideModeV0515);
        $('#h18-canvas-zoom').val(canvasZoomPercentV0515);
        $('#h18-canvas-zoom-output').text(canvasZoomPercentV0515 + '%');
        $('#h18-canvas-outline-toggle').attr('aria-pressed', canvasOutlineModeV0515 ? 'true' : 'false').toggleClass('is-active', canvasOutlineModeV0515);
        $('#h18-canvas-guide-toggle').attr('aria-pressed', canvasGuideModeV0515 ? 'true' : 'false').toggleClass('is-active', canvasGuideModeV0515);
        saveCanvasWorkspaceV0515();
    }

    function ensureCanvasWorkspaceControlsV0515() {
        const $heading = $('.h18-builder-canvas-heading');
        if (!$heading.length || $('#h18-canvas-workspace-controls').length) { return; }
        const $controls = $('<div>', { id: 'h18-canvas-workspace-controls', class: 'h18-canvas-workspace-controls' });
        $controls.append(
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-zoom-out', text: '−', title: 'Zoom ud', 'aria-label': 'Zoom ud' }),
            $('<label>', { class: 'h18-canvas-zoom-label' }).append(
                $('<span>', { class: 'screen-reader-text', text: 'Canvas zoom' }),
                $('<input>', { id: 'h18-canvas-zoom', type: 'range', min: 50, max: 150, step: 5, value: canvasZoomPercentV0515 }),
                $('<output>', { id: 'h18-canvas-zoom-output', for: 'h18-canvas-zoom', text: canvasZoomPercentV0515 + '%' })
            ),
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-zoom-in', text: '+', title: 'Zoom ind', 'aria-label': 'Zoom ind' }),
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-zoom-reset', text: '100%', title: 'Nulstil zoom' }),
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-outline-toggle', text: 'Outline', 'aria-pressed': 'false' }),
            $('<button>', { type: 'button', class: 'button button-small', id: 'h18-canvas-guide-toggle', text: 'Guides', 'aria-pressed': 'false' })
        );
        $heading.append($controls);
        applyCanvasWorkspaceV0515();
    }

    $(document).on('input change', '#h18-canvas-zoom', function () {
        canvasZoomPercentV0515 = Math.max(50, Math.min(150, parseInt($(this).val(), 10) || 100));
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-zoom-out', function () {
        canvasZoomPercentV0515 = Math.max(50, canvasZoomPercentV0515 - 5);
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-zoom-in', function () {
        canvasZoomPercentV0515 = Math.min(150, canvasZoomPercentV0515 + 5);
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-zoom-reset', function () {
        canvasZoomPercentV0515 = 100;
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-outline-toggle', function () {
        canvasOutlineModeV0515 = !canvasOutlineModeV0515;
        applyCanvasWorkspaceV0515();
    });
    $(document).on('click', '#h18-canvas-guide-toggle', function () {
        canvasGuideModeV0515 = !canvasGuideModeV0515;
        applyCanvasWorkspaceV0515();
    });

    function contextMenuEnsureV0515() {
        if ($('#h18-editor-context-menu').length) { return; }
        const $menu = $('<div>', {
            id: 'h18-editor-context-menu',
            class: 'h18-editor-context-menu',
            role: 'menu',
            'aria-label': 'Elementhandlinger',
            hidden: true
        });
        $('body').append($menu);
    }

    function contextMenuItemsV0515($row) {
        const type = String($row.attr('data-section-type') || 'text');
        const active = pageSectionControls($row, '.h18-section-active').is(':checked');
        const key = sectionKeyV0515($row);
        return [
            { action: 'edit', label: 'Redigér element', hint: 'Enter' },
            { action: 'multi', label: multiSelectedSectionKeys.has(key) ? 'Fjern fra multivalg' : 'Tilføj til multivalg', hint: 'Ctrl/⌘/Shift+klik' },
            { separator: true },
            { action: 'duplicate', label: 'Duplikér element', disabled: type === 'legacy' },
            { action: 'copy-design', label: 'Kopiér design', disabled: type === 'legacy' },
            { action: 'paste-design', label: 'Indsæt design', disabled: type === 'legacy' || !sectionDesignClipboard },
            { action: 'component', label: 'Gem som komponent', disabled: type === 'legacy' },
            { separator: true },
            { action: 'toggle-active', label: active ? 'Skjul element' : 'Vis element' },
            { action: 'move-up', label: 'Flyt op' },
            { action: 'move-down', label: 'Flyt ned' },
            { separator: true },
            { action: 'delete', label: 'Fjern element', danger: true, disabled: type === 'legacy' }
        ];
    }

    function contextMenuCloseV0515(returnFocus) {
        const $menu = $('#h18-editor-context-menu');
        if (!$menu.length || $menu.prop('hidden')) { return; }
        $menu.prop('hidden', true).empty();
        contextMenuRowV0515 = $();
        if (returnFocus !== false && contextMenuReturnFocusV0515 && document.contains(contextMenuReturnFocusV0515)) {
            $(contextMenuReturnFocusV0515).trigger('focus');
        }
        contextMenuReturnFocusV0515 = null;
    }

    function contextMenuOpenV0515($row, x, y, focusSource) {
        if (!$row || !$row.length || $row.hasClass('h18-page-section-removed')) { return; }
        contextMenuEnsureV0515();
        const key = sectionKeyV0515($row);
        inspectPageSection($row, key && multiSelectedSectionKeys.has(key));
        contextMenuRowV0515 = $row;
        contextMenuReturnFocusV0515 = focusSource || document.activeElement;
        const $menu = $('#h18-editor-context-menu').empty();
        contextMenuItemsV0515($row).forEach(function (item) {
            if (item.separator) {
                $menu.append($('<div>', { class: 'h18-context-separator', role: 'separator' }));
                return;
            }
            const $button = $('<button>', {
                type: 'button',
                role: 'menuitem',
                class: 'h18-context-item' + (item.danger ? ' is-danger' : ''),
                'data-context-action': item.action,
                disabled: item.disabled === true
            });
            $button.append($('<span>', { text: item.label }));
            if (item.hint) { $button.append($('<small>', { text: item.hint })); }
            $menu.append($button);
        });
        $menu.prop('hidden', false).css({ left: 0, top: 0 });
        const node = $menu.get(0);
        const width = node ? node.offsetWidth : 240;
        const height = node ? node.offsetHeight : 300;
        const left = Math.max(8, Math.min(Number(x) || 8, window.innerWidth - width - 8));
        const top = Math.max(8, Math.min(Number(y) || 8, window.innerHeight - height - 8));
        $menu.css({ left: left + 'px', top: top + 'px' });
        $menu.find('.h18-context-item:not(:disabled)').first().trigger('focus');
    }

    function contextMenuMoveRowV0515($row, direction) {
        if (!$row || !$row.length) { return; }
        restoreInspectedSection();
        const $target = direction < 0
            ? $row.prevAll('.h18-page-section-row:not(.h18-page-section-removed)').first()
            : $row.nextAll('.h18-page-section-row:not(.h18-page-section-removed)').first();
        if (!$target.length) { inspectPageSection($row, true); return; }
        if (direction < 0) { $row.insertBefore($target); }
        else { $row.insertAfter($target); }
        syncPageSectionOrder(true);
        rebuildPageNavigator();
        inspectPageSection($row, multiSelectedSectionKeys.has(sectionKeyV0515($row)));
        scheduleEditorHistoryCapture(0);
    }

    function contextMenuExecuteV0515(action) {
        const $row = contextMenuRowV0515;
        if (!$row || !$row.length) { contextMenuCloseV0515(); return; }
        contextMenuCloseV0515(false);
        if (action === 'edit') { inspectPageSection($row, multiSelectedSectionKeys.has(sectionKeyV0515($row))); }
        else if (action === 'multi') { toggleMultiSelectRowV0515($row); }
        else if (action === 'duplicate') { inspectPageSection($row); $row.find('.h18-page-section-duplicate').first().trigger('click'); }
        else if (action === 'copy-design') { inspectPageSection($row); $('#h18-inspector-copy-design').trigger('click'); }
        else if (action === 'paste-design') { inspectPageSection($row); $('#h18-inspector-paste-design').trigger('click'); }
        else if (action === 'component') { inspectPageSection($row); $('#h18-save-section-preset').trigger('click'); }
        else if (action === 'toggle-active') {
            const $active = pageSectionControls($row, '.h18-section-active').first();
            if ($active.length) { $active.prop('checked', !$active.is(':checked')).trigger('change'); renderCanvasPreview($row); rebuildPageNavigator(); scheduleEditorHistoryCapture(0); }
        }
        else if (action === 'move-up') { contextMenuMoveRowV0515($row, -1); }
        else if (action === 'move-down') { contextMenuMoveRowV0515($row, 1); }
        else if (action === 'delete') { inspectPageSection($row); $row.find('.h18-page-section-delete').first().trigger('click'); }
    }

    $(document).on('contextmenu', '.h18-canvas-preview, .h18-navigator-item', function (event) {
        if ($(event.target).closest('input,textarea,select,[contenteditable="true"]').length) { return; }
        event.preventDefault();
        let $row = $(this).closest('.h18-page-section-row');
        if (!$row.length) {
            const index = String($(this).closest('.h18-navigator-item').attr('data-section-index') || '');
            $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
        }
        contextMenuOpenV0515($row, event.clientX, event.clientY, this);
    });

    $(document).on('keydown', '.h18-canvas-preview, .h18-navigator-select', function (event) {
        if (!(event.shiftKey && event.key === 'F10')) { return; }
        event.preventDefault();
        let $row = $(this).closest('.h18-page-section-row');
        if (!$row.length) {
            const index = String($(this).closest('.h18-navigator-item').attr('data-section-index') || '');
            $row = $pageSections.children('.h18-page-section-row[data-section-index="' + index + '"]');
        }
        const rect = this.getBoundingClientRect();
        contextMenuOpenV0515($row, rect.left + Math.min(rect.width / 2, 180), rect.top + Math.min(rect.height / 2, 120), this);
    });

    $(document).on('click', '.h18-context-item:not(:disabled)', function () {
        contextMenuExecuteV0515(String($(this).attr('data-context-action') || ''));
    });

    $(document).on('keydown', '#h18-editor-context-menu', function (event) {
        const $items = $(this).find('.h18-context-item:not(:disabled)');
        if (!$items.length) { return; }
        const index = Math.max(0, $items.index(document.activeElement));
        if (event.key === 'Escape') { event.preventDefault(); contextMenuCloseV0515(); }
        else if (event.key === 'ArrowDown') { event.preventDefault(); $items.eq((index + 1) % $items.length).trigger('focus'); }
        else if (event.key === 'ArrowUp') { event.preventDefault(); $items.eq((index - 1 + $items.length) % $items.length).trigger('focus'); }
        else if (event.key === 'Home') { event.preventDefault(); $items.first().trigger('focus'); }
        else if (event.key === 'End') { event.preventDefault(); $items.last().trigger('focus'); }
        else if (event.key === 'Enter' || event.key === ' ') { event.preventDefault(); $(document.activeElement).trigger('click'); }
        else if (event.key === 'Tab') { event.preventDefault(); $items.eq((index + (event.shiftKey ? -1 : 1) + $items.length) % $items.length).trigger('focus'); }
    });

    $(document).on('mousedown', function (event) {
        if (!$(event.target).closest('#h18-editor-context-menu').length) { contextMenuCloseV0515(false); }
    });
    $(window).on('blur scroll resize', function () { contextMenuCloseV0515(false); });

    loadCanvasWorkspaceV0515();
    if ($pageSections.length) {
        window.setTimeout(function () {
            ensureCanvasWorkspaceControlsV0515();
            syncMultiSelectUiV0515();
        }, 0);
    }
'''

js = replace_once(js, "\n    const editorHistoryLimit = 50;", workspace_block + "\n\n    const editorHistoryLimit = 50;", 'workspace block anchor')

css_block = r'''

/* v0.5.15 – multi-select, canvas workspace and context menu */
.h18-page-section-row.is-multi-selected > .h18-canvas-preview{box-shadow:0 0 0 3px rgba(34,113,177,.32),0 12px 28px rgba(0,0,0,.08)}
.h18-navigator-item.is-multi-selected{background:#eef6fc;box-shadow:inset 3px 0 0 #2271b1}
.h18-multi-edit-panel{margin:10px 0 14px;padding:12px;border:1px solid #b9d7ed;border-radius:8px;background:#f4f9fd}
.h18-multi-edit-panel[hidden]{display:none!important}
.h18-multi-edit-heading{display:flex;align-items:flex-start;justify-content:space-between;gap:10px;margin-bottom:10px}
.h18-multi-edit-heading strong,.h18-multi-edit-heading small{display:block}
.h18-multi-edit-heading small{margin-top:2px;color:#50575e}
.h18-multi-edit-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}
.h18-multi-field{display:grid;gap:4px;font-size:12px;font-weight:600}
.h18-multi-field[hidden]{display:none!important}
.h18-multi-field input,.h18-multi-field select{width:100%;font-weight:400}
.h18-multi-edit-actions{display:flex;align-items:center;gap:10px;margin-top:10px;flex-wrap:wrap}
.h18-canvas-workspace-controls{margin-left:auto;display:flex;align-items:center;gap:5px;flex-wrap:wrap;justify-content:flex-end}
.h18-canvas-workspace-controls .button.is-active{background:#2271b1;border-color:#2271b1;color:#fff}
.h18-canvas-zoom-label{display:inline-flex;align-items:center;gap:6px}
.h18-canvas-zoom-label input[type=range]{width:92px}
.h18-canvas-zoom-label output{min-width:42px;text-align:right;font-variant-numeric:tabular-nums;color:#50575e}
.h18-page-sections.h18-canvas-guide-mode{background-image:linear-gradient(rgba(34,113,177,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(34,113,177,.07) 1px,transparent 1px);background-size:16px 16px;background-position:center top;padding-top:1px}
.h18-page-sections.h18-canvas-outline-mode .h18-canvas-preview-inner,.h18-page-sections.h18-canvas-outline-mode .h18-canvas-preview-inner>*,.h18-page-sections.h18-canvas-outline-mode .h18-canvas-card,.h18-page-sections.h18-canvas-outline-mode .h18-canvas-editable-media{outline:1px dashed rgba(34,113,177,.48);outline-offset:-1px}
.h18-editor-context-menu{position:fixed;z-index:100100;min-width:238px;max-width:min(320px,calc(100vw - 16px));padding:6px;background:#fff;border:1px solid #c3c4c7;border-radius:8px;box-shadow:0 16px 45px rgba(0,0,0,.22)}
.h18-editor-context-menu[hidden]{display:none!important}
.h18-context-item{appearance:none;display:flex;width:100%;align-items:center;justify-content:space-between;gap:12px;border:0;background:transparent;border-radius:5px;padding:8px 9px;text-align:left;color:#1d2327;cursor:pointer}
.h18-context-item:hover,.h18-context-item:focus{background:#f0f6fc;outline:2px solid transparent}
.h18-context-item:focus-visible{box-shadow:0 0 0 2px #2271b1}
.h18-context-item small{color:#646970;font-size:11px}
.h18-context-item.is-danger{color:#b32d2e}
.h18-context-item:disabled{opacity:.42;cursor:not-allowed}
.h18-context-separator{height:1px;background:#dcdcde;margin:5px 3px}
@media(max-width:1100px){.h18-multi-edit-grid{grid-template-columns:1fr}.h18-canvas-workspace-controls{width:100%;justify-content:flex-start;margin-left:0}}
'''
if '/* v0.5.15 – multi-select, canvas workspace and context menu */' in css:
    raise SystemExit('v0.5.15 CSS already present')
css = css.rstrip() + css_block + '\n'

readme = replace_once(readme, 'Version: 0.5.14', 'Version: 0.5.15', 'readme version')
readme_anchor = """== Version 0.5.14 – Kommandopalette og hurtignavigation ==
"""
readme_insert = """== Version 0.5.15 – Multi-select, canvas workspace og context menu ==

Nyt:
- UD-017: Ctrl/Cmd/Shift+klik kan vælge flere sideelementer samtidig i canvas og Navigator
- fælles kompatible egenskaber kan batch-redigeres: baggrund, placering, padding, radius, opacity og synlighed
- Inspector viser tydeligt antal valgte elementer og skjuler batchfelter, som ikke understøttes af alle valgte elementer
- UD-018: canvas zoom 50-150%, 100%-reset, Outline mode og 16 px Guides-grid
- workspace-indstillinger gemmes lokalt i browseren og ændrer aldrig frontend-output
- UD-019: højreklik eller Shift+F10 åbner en keyboard-tilgængelig context menu på canvas/Navigator
- context menu indeholder redigér, multivalg, duplikér, design copy/paste, komponent, vis/skjul, flyt og fjern
- context menu understøtter piletaster, Home/End, Enter/Space, Tab-loop og Escape
- page-editor schema forbliver 1.12; alle funktioner er editor-only

""" + readme_anchor
readme = replace_once(readme, readme_anchor, readme_insert, 'readme v0.5.14 anchor')

php_path.write_text(php, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
print('v0.5.15 patch applied')
