from pathlib import Path

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
css_path = Path('assets/admin.css')

php = php_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

# 1) Put a clearly visible manual save control in the top editor toolbar.
anchor = '''                        <button type="button" class="button h18-command-palette-open" id="h18-command-palette-open" aria-haspopup="dialog" aria-controls="h18-command-palette" aria-expanded="false" title="Åbn kommandopaletten (Ctrl/Cmd+K)">⌘K Kommandoer</button>'''
insert = '''                        <div class="h18-editor-save-controls">
                            <button type="submit" class="button button-primary" id="h18-editor-save-top" title="Gem som permanent version (Ctrl/Cmd+S)">Gem</button>
                            <span id="h18-editor-save-status" class="h18-editor-save-status" aria-live="polite">Gemt</span>
                        </div>
                        <button type="button" class="button h18-command-palette-open" id="h18-command-palette-open" aria-haspopup="dialog" aria-controls="h18-command-palette" aria-expanded="false" title="Åbn kommandopaletten (Ctrl/Cmd+K)">⌘K Kommandoer</button>'''
if php.count(anchor) != 1:
    raise SystemExit(f'Expected one command palette toolbar anchor, found {php.count(anchor)}')
php = php.replace(anchor, insert, 1)
php_path.write_text(php, encoding='utf-8')

# 2) Dirty/save status, Ctrl/Cmd+S and leave-page warning.
marker = '''\n});\n'''
pos = js.rfind(marker)
if pos < 0:
    raise SystemExit('Could not find final jQuery closure')
block = r'''

    // v0.6.4 workflow UX: prominent manual Save, Ctrl/Cmd+S and unsaved-change guard.
    const $h18PageEditorFormV064 = $('#h18-page-editor-form');
    const $h18EditorSaveTopV064 = $('#h18-editor-save-top');
    const $h18EditorSaveStatusV064 = $('#h18-editor-save-status');
    let h18EditorDirtyV064 = false;
    let h18EditorSubmittingV064 = false;

    function h18EditorSetSaveStatusV064(text, state) {
        if (!$h18EditorSaveStatusV064.length) { return; }
        $h18EditorSaveStatusV064.text(text).attr('data-save-state', state || 'saved');
    }

    function h18EditorMarkDirtyV064() {
        if (!$h18PageEditorFormV064.length || h18EditorSubmittingV064) { return; }
        h18EditorDirtyV064 = true;
        h18EditorSetSaveStatusV064('Ikke gemt', 'dirty');
    }

    if ($h18PageEditorFormV064.length) {
        $h18PageEditorFormV064.on('input change', ':input', function () {
            h18EditorMarkDirtyV064();
        });

        $h18PageEditorFormV064.on('submit', function (event) {
            const whatIf = $h18PageEditorFormV064.find('[name="whatif"]').is(':checked');
            const $note = $h18PageEditorFormV064.find('[name="page_change_note"]');
            if (!whatIf && $note.length && !String($note.val() || '').trim()) {
                event.preventDefault();
                h18EditorSetSaveStatusV064('Beskriv ændringen før Gem', 'error');
                $note.trigger('focus');
                return;
            }
            h18EditorSubmittingV064 = true;
            h18EditorDirtyV064 = false;
            h18EditorSetSaveStatusV064(whatIf ? 'Simulerer…' : 'Gemmer…', 'saving');
            $h18EditorSaveTopV064.prop('disabled', true);
        });

        $(document).on('keydown.h18SaveV064', function (event) {
            const key = String(event.key || '').toLowerCase();
            if ((event.ctrlKey || event.metaKey) && !event.altKey && key === 's') {
                event.preventDefault();
                if (h18EditorSubmittingV064) { return; }
                const form = $h18PageEditorFormV064.get(0);
                const button = $h18EditorSaveTopV064.get(0);
                if (form && typeof form.requestSubmit === 'function') {
                    form.requestSubmit(button || undefined);
                } else if (form) {
                    $h18PageEditorFormV064.trigger('submit');
                }
            }
        });

        $(window).on('beforeunload.h18SaveV064', function (event) {
            if (!h18EditorDirtyV064 || h18EditorSubmittingV064) { return; }
            event.preventDefault();
            event.returnValue = '';
            return '';
        });
    }
'''
if 'h18EditorSetSaveStatusV064' in js:
    raise SystemExit('Save toolbar JS already present')
js = js[:pos] + block + js[pos:]
js_path.write_text(js, encoding='utf-8')

# 3) Toolbar layout and visible state feedback.
css_marker = '/* v0.6.4 – synlig Gem-knap og save-status */'
if css_marker in css:
    raise SystemExit('Save toolbar CSS already present')
css += r'''

/* v0.6.4 – synlig Gem-knap og save-status */
.h18-page-preview-toolbar .h18-editor-save-controls{display:flex;align-items:center;gap:8px;margin-left:auto;padding-left:8px}
.h18-page-preview-toolbar .h18-editor-save-controls #h18-editor-save-top{min-width:92px;font-weight:700}
.h18-page-preview-toolbar .h18-editor-save-controls .h18-editor-save-status{margin-left:0;font-size:12px;font-weight:600;color:#2271b1;white-space:nowrap}
.h18-page-preview-toolbar .h18-editor-save-controls .h18-editor-save-status[data-save-state="dirty"]{color:#996800}
.h18-page-preview-toolbar .h18-editor-save-controls .h18-editor-save-status[data-save-state="saving"]{color:#135e96}
.h18-page-preview-toolbar .h18-editor-save-controls .h18-editor-save-status[data-save-state="error"]{color:#b32d2e}
@media(max-width:782px){
    .h18-page-preview-toolbar .h18-editor-save-controls{order:20;width:100%;margin-left:0;padding-left:0;justify-content:flex-end}
}
'''
css_path.write_text(css, encoding='utf-8')
