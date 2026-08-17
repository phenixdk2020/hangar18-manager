from pathlib import Path

root = Path('.')
php_path = root / 'hangar18-manager.php'
js_path = root / 'assets/admin.js'
css_path = root / 'assets/admin.css'
readme_path = root / 'readme.txt'

php = php_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')


def once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {n}')
    return text.replace(old, new, 1)

php = once(php, ' * Version: 0.5.11', ' * Version: 0.5.12', 'header version')
php = once(php, "    const VERSION = '0.5.11';", "    const VERSION = '0.5.12';", 'const version')

toolbar_old = '''                        <button type="button" class="button h18-preview-device" data-device="mobile">Mobil</button>
                        <span>Visningen gør arbejdsområdet smallere. Den offentlige side åbnes med knappen ovenfor.</span>'''
toolbar_new = '''                        <button type="button" class="button h18-preview-device" data-device="mobile">Mobil</button>
                        <span class="h18-editor-history-controls">
                            <button type="button" class="button" id="h18-editor-undo" disabled title="Fortryd sidste ændring (Ctrl/Cmd+Z)">↶ Fortryd</button>
                            <button type="button" class="button" id="h18-editor-redo" disabled title="Gendan ændring (Ctrl/Cmd+Shift+Z)">↷ Gendan</button>
                            <span id="h18-editor-history-status" class="h18-editor-history-status" aria-live="polite">Ingen ugemte ændringer</span>
                        </span>
                        <span>Visningen gør arbejdsområdet smallere. Den offentlige side åbnes med knappen ovenfor.</span>'''
php = once(php, toolbar_old, toolbar_new, 'history toolbar')

anchor = "    const $pageEditorForm = $('#h18-page-editor-form');\n"
history = r'''    const editorHistoryLimit = 50;
    const editorHistoryEntries = [];
    let editorHistoryIndex = -1;
    let editorHistoryTimer = null;
    let editorHistoryReady = false;
    let editorHistoryApplying = false;
    let editorHistorySubmitting = false;
    let editorHistorySavedSignature = '';

    function editorHistoryNormalizeClone($root) {
        $root.find('.h18-canvas-preview, .ui-sortable-placeholder, .ui-sortable-helper').remove();
        $root.find('.is-selected, .is-card-selected, .is-direct-dragging, .is-focal-dragging').removeClass('is-selected is-card-selected is-direct-dragging is-focal-dragging');
        $root.find('.ui-sortable').removeClass('ui-sortable');
        $root.find('input').each(function () {
            const $input = $(this);
            if ($input.is(':checkbox, :radio')) {
                if ($input.prop('checked')) { $input.attr('checked', 'checked'); }
                else { $input.removeAttr('checked'); }
            } else {
                $input.attr('value', String($input.val() == null ? '' : $input.val()));
            }
        });
        $root.find('textarea').each(function () { $(this).text(String($(this).val() == null ? '' : $(this).val())); });
        $root.find('select').each(function () {
            const $select = $(this);
            const values = Array.isArray($select.val()) ? $select.val().map(String) : [String($select.val() == null ? '' : $select.val())];
            $select.find('option').each(function () {
                if (values.includes(String($(this).val()))) { $(this).attr('selected', 'selected'); }
                else { $(this).removeAttr('selected'); }
            });
        });
    }

    function editorHistorySnapshot() {
        if (!$pageSections.length) { return null; }
        const selectedKey = $inspectedSection.length ? String($inspectedSection.find('.h18-page-section-key').val() || '') : '';
        const inspectedIndex = $inspectedSection.length ? String($inspectedSection.attr('data-section-index') || '') : '';
        const $clone = $pageSections.clone(false, false);
        if (inspectedIndex) {
            const $body = $pageInspectorTarget.children('.h18-page-section-body').first();
            if ($body.length) {
                const $cloneRow = $clone.children('.h18-page-section-row[data-section-index="' + inspectedIndex + '"]').first();
                if ($cloneRow.length) {
                    $cloneRow.children('.h18-page-section-body').remove();
                    $cloneRow.children('.h18-page-section-header').after($body.clone(false, false));
                }
            }
        }
        editorHistoryNormalizeClone($clone);
        const html = String($clone.html() || '');
        return {
            html: html,
            signature: html,
            selectedKey: selectedKey,
            selectedCardKey: String(selectedCanvasCardKey || ''),
            device: String(currentCanvasDevice || 'desktop'),
            state: String(currentCanvasState || 'normal')
        };
    }

    function editorHistoryUpdateUi() {
        const canUndo = editorHistoryIndex > 0;
        const canRedo = editorHistoryIndex >= 0 && editorHistoryIndex < editorHistoryEntries.length - 1;
        $('#h18-editor-undo').prop('disabled', !canUndo);
        $('#h18-editor-redo').prop('disabled', !canRedo);
        const current = editorHistoryIndex >= 0 ? editorHistoryEntries[editorHistoryIndex] : null;
        const dirty = Boolean(current && current.signature !== editorHistorySavedSignature);
        $('#h18-editor-history-status')
            .toggleClass('is-dirty', dirty)
            .text(dirty ? 'Ugemte ændringer · trin ' + editorHistoryIndex : 'Ingen ugemte ændringer');
    }

    function editorHistoryRecordNow() {
        if (!editorHistoryReady || editorHistoryApplying) { return; }
        const snapshot = editorHistorySnapshot();
        if (!snapshot) { return; }
        const current = editorHistoryIndex >= 0 ? editorHistoryEntries[editorHistoryIndex] : null;
        if (current && current.signature === snapshot.signature) { editorHistoryUpdateUi(); return; }
        if (editorHistoryIndex < editorHistoryEntries.length - 1) { editorHistoryEntries.splice(editorHistoryIndex + 1); }
        editorHistoryEntries.push(snapshot);
        if (editorHistoryEntries.length > editorHistoryLimit) {
            editorHistoryEntries.shift();
            if (editorHistorySavedSignature && !editorHistoryEntries.some(entry => entry.signature === editorHistorySavedSignature)) {
                editorHistorySavedSignature = '__saved_state_outside_history__';
            }
        }
        editorHistoryIndex = editorHistoryEntries.length - 1;
        editorHistoryUpdateUi();
    }

    function scheduleEditorHistoryCapture(delay) {
        if (!editorHistoryReady || editorHistoryApplying) { return; }
        window.clearTimeout(editorHistoryTimer);
        editorHistoryTimer = window.setTimeout(editorHistoryRecordNow, typeof delay === 'number' ? delay : 280);
    }

    function editorHistoryFindRowByKey(key) {
        let $match = $();
        if (!key) { return $match; }
        $pageSections.children('.h18-page-section-row').each(function () {
            const $row = $(this);
            if (String($row.find('.h18-page-section-key').val() || '') === String(key)) { $match = $row; return false; }
        });
        return $match;
    }

    function editorHistoryRestore(entry) {
        if (!entry || !entry.html || !$pageSections.length) { return; }
        editorHistoryApplying = true;
        window.clearTimeout(editorHistoryTimer);
        try {
            restoreInspectedSection();
            selectedCanvasCardKey = String(entry.selectedCardKey || '');
            $pageSections.html(entry.html);
            $pageSections.children('.h18-page-section-row').each(function () {
                const $row = $(this);
                refreshPageSectionType($row);
                initializePageCardSortables($row);
            });
            syncPageSectionOrder(true);
            rebuildPageNavigator();
            currentCanvasDevice = ['desktop','tablet','mobile'].includes(String(entry.device)) ? String(entry.device) : 'desktop';
            currentCanvasState = String(entry.state) === 'hover' ? 'hover' : 'normal';
            $('.h18-preview-device').removeClass('is-active').filter('[data-device="' + currentCanvasDevice + '"]').addClass('is-active');
            $('.h18-preview-state').removeClass('is-active').filter('[data-state="' + currentCanvasState + '"]').addClass('is-active');
            $pageSections.removeClass('h18-preview-desktop h18-preview-tablet h18-preview-mobile').addClass('h18-preview-' + currentCanvasDevice);
            const $target = editorHistoryFindRowByKey(entry.selectedKey);
            if ($target.length && !$target.hasClass('h18-page-section-removed')) { inspectPageSection($target); }
            refreshAllCanvasPreviews();
        } finally {
            editorHistoryApplying = false;
            editorHistoryUpdateUi();
        }
    }

    function editorHistoryUndo() {
        if (editorHistoryIndex <= 0) { return; }
        editorHistoryIndex -= 1;
        editorHistoryRestore(editorHistoryEntries[editorHistoryIndex]);
    }

    function editorHistoryRedo() {
        if (editorHistoryIndex < 0 || editorHistoryIndex >= editorHistoryEntries.length - 1) { return; }
        editorHistoryIndex += 1;
        editorHistoryRestore(editorHistoryEntries[editorHistoryIndex]);
    }

    function initializeEditorHistory() {
        if (!$pageSections.length || editorHistoryReady) { return; }
        const initial = editorHistorySnapshot();
        if (!initial) { return; }
        editorHistoryEntries.push(initial);
        editorHistoryIndex = 0;
        editorHistorySavedSignature = initial.signature;
        editorHistoryReady = true;
        editorHistoryUpdateUi();

        const originalCanvasSetField = canvasSetField;
        canvasSetField = function ($row, fieldName, value) {
            const result = originalCanvasSetField($row, fieldName, value);
            if (result) { scheduleEditorHistoryCapture(); }
            return result;
        };
        const originalCanvasCardSetField = canvasCardSetField;
        canvasCardSetField = function ($card, fieldName, value) {
            const result = originalCanvasCardSetField($card, fieldName, value);
            if (result) { scheduleEditorHistoryCapture(); }
            return result;
        };

        $('#h18-page-editor-form').on('input change', '.h18-page-section-body :input, .h18-page-card-row :input', function () {
            scheduleEditorHistoryCapture();
        });

        if (window.MutationObserver && $pageSections.get(0)) {
            const observer = new MutationObserver(function (mutations) {
                if (editorHistoryApplying) { return; }
                let meaningful = false;
                mutations.forEach(function (mutation) {
                    if (meaningful) { return; }
                    if (mutation.type === 'childList') {
                        const nodes = Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || []));
                        meaningful = nodes.some(function (node) {
                            return node && node.nodeType === 1 && ($(node).is('.h18-page-section-row, .h18-page-card-row') || $(node).find('.h18-page-section-row, .h18-page-card-row').length);
                        });
                    } else if (mutation.type === 'attributes' && mutation.attributeName === 'class') {
                        const $target = $(mutation.target);
                        if ($target.is('.h18-page-section-row, .h18-page-card-row')) {
                            const before = String(mutation.oldValue || '').includes('h18-page-section-removed') || String(mutation.oldValue || '').includes('h18-page-card-removed');
                            const after = $target.hasClass('h18-page-section-removed') || $target.hasClass('h18-page-card-removed');
                            meaningful = before !== after;
                        }
                    }
                });
                if (meaningful) { scheduleEditorHistoryCapture(120); }
            });
            observer.observe($pageSections.get(0), { childList: true, subtree: true, attributes: true, attributeOldValue: true, attributeFilter: ['class'] });
        }
    }

    $(document).on('click', '#h18-editor-undo', function (event) { event.preventDefault(); editorHistoryUndo(); });
    $(document).on('click', '#h18-editor-redo', function (event) { event.preventDefault(); editorHistoryRedo(); });
    $(document).on('keydown.h18EditorHistory', function (event) {
        if (!(event.ctrlKey || event.metaKey) || String(event.key || '').toLowerCase() !== 'z') { return; }
        const $target = $(event.target);
        if ($target.is('input, textarea, select') || $target.closest('[contenteditable="true"]').length) { return; }
        event.preventDefault();
        if (event.shiftKey) { editorHistoryRedo(); } else { editorHistoryUndo(); }
    });

'''
js = once(js, anchor, history + anchor, 'history system insertion')

# Mark submit as safe navigation and initialize history after normal form setup.
submit_anchor = "    if ($pageEditorForm.length) {\n        $pageWhatIf.on('change', syncPageChangeNoteRequirement);\n        syncPageChangeNoteRequirement();\n    }\n"
submit_new = "    if ($pageEditorForm.length) {\n        $pageWhatIf.on('change', syncPageChangeNoteRequirement);\n        syncPageChangeNoteRequirement();\n        $pageEditorForm.on('submit', function () { editorHistorySubmitting = true; });\n        window.setTimeout(initializeEditorHistory, 0);\n    }\n\n    $(window).on('beforeunload.h18EditorHistory', function (event) {\n        if (!editorHistoryReady || editorHistorySubmitting || editorHistoryIndex < 0) { return; }\n        const current = editorHistoryEntries[editorHistoryIndex];\n        if (!current || current.signature === editorHistorySavedSignature) { return; }\n        event.preventDefault();\n        event.returnValue = '';\n        return '';\n    });\n"
js = once(js, submit_anchor, submit_new, 'history initialization')

css += '''\n/* v0.5.12 - lokal Undo/Redo-historik i den visuelle editor */\n.h18-editor-history-controls{display:inline-flex;align-items:center;gap:6px;margin-left:8px;padding-left:8px;border-left:1px solid #dcdcde;vertical-align:middle}.h18-editor-history-status{display:inline-flex;align-items:center;min-height:30px;padding:0 8px;border-radius:4px;background:#f0f0f1;color:#50575e;font-size:12px;font-weight:600;white-space:nowrap}.h18-editor-history-status.is-dirty{background:#fff8e5;color:#7a4b00}.h18-page-preview-toolbar #h18-editor-undo:disabled,.h18-page-preview-toolbar #h18-editor-redo:disabled{opacity:.5}@media(max-width:900px){.h18-editor-history-controls{margin:6px 0 0;padding:6px 0 0;border-left:0;border-top:1px solid #dcdcde;flex-wrap:wrap;width:100%}}\n'''

if '== 0.5.12 ==' in readme:
    raise SystemExit('readme already contains v0.5.12')
readme += '''\n\n== 0.5.12 ==\n* Lokal Undo/Redo-historik med op til 50 redigeringstrin i den visuelle editor.\n* Fortryd/Gendan-knapper samt Ctrl/Cmd+Z og Ctrl/Cmd+Shift+Z uden at overtage tekstfelters native undo.\n* Historikken dækker feltændringer, live-canvas, sektioner, kort og rækkefølge.\n* Status viser ugemte ændringer, og browseren advarer ved navigation væk fra en ændret side.\n* Ingen page-editor schemaændring; permanente WordPress-revisioner/backups er uændrede.\n'''

php_path.write_text(php, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
print('v0.5.12 undo/redo patch applied')
