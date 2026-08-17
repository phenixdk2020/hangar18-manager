from pathlib import Path


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 anchor, found {count}")
    return text.replace(old, new, 1)

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
css_path = Path('assets/admin.css')
readme_path = Path('readme.txt')

php = php_path.read_text(encoding='utf-8')
php = replace_once(php, ' * Version: 0.5.12', ' * Version: 0.5.13', 'plugin header version')
php = replace_once(php, "    const VERSION = '0.5.12';", "    const VERSION = '0.5.13';", 'class version')

toolbar_anchor = '''                            <span id="h18-editor-history-status" class="h18-editor-history-status" aria-live="polite">Ingen ugemte ændringer</span>\n                        </span>'''
toolbar_new = '''                            <span id="h18-editor-history-status" class="h18-editor-history-status" aria-live="polite">Ingen ugemte ændringer</span>\n                        </span>\n                        <span class="h18-editor-draft-controls">\n                            <span id="h18-editor-autosave-status" class="h18-editor-autosave-status" aria-live="polite">Lokal kladde: klar</span>\n                            <span id="h18-editor-recovery-actions" class="h18-editor-recovery-actions" hidden>\n                                <button type="button" class="button button-small button-primary" id="h18-editor-restore-draft">Gendan kladde</button>\n                                <button type="button" class="button button-small" id="h18-editor-discard-draft">Kassér kladde</button>\n                            </span>\n                        </span>'''
php = replace_once(php, toolbar_anchor, toolbar_new, 'draft toolbar controls')
php_path.write_text(php, encoding='utf-8')

js = js_path.read_text(encoding='utf-8')
vars_anchor = "    let editorHistorySavedSignature = '';\n"
draft_block = r'''    const editorDraftVersion = '1.0';
    const editorDraftStoragePrefix = 'hangar18PageDraftV0513:';
    const editorDraftMaxChars = 4000000;
    const editorDraftSubmitSuccessWindowMs = 10 * 60 * 1000;
    let editorDraftTimer = null;
    let editorDraftCandidate = null;
    let editorDraftServerSignature = '';
    let editorDraftRecoveryPending = false;

    function editorDraftPageSlug() {
        const raw = String($('#h18-page-editor-form [name="page_slug"]').val() || '').trim().toLowerCase();
        return raw.replace(/[^a-z0-9_-]+/g, '-').replace(/^-+|-+$/g, '') || 'unknown';
    }

    function editorDraftStorageKey() {
        return editorDraftStoragePrefix + editorDraftPageSlug();
    }

    function editorDraftSetStatus(text, state) {
        const $status = $('#h18-editor-autosave-status');
        if (!$status.length) { return; }
        $status.removeClass('is-saved is-warning is-error');
        if (state) { $status.addClass('is-' + state); }
        $status.text(String(text || 'Lokal kladde: klar'));
    }

    function editorDraftFormatTime(iso) {
        if (!iso) { return ''; }
        const value = new Date(iso);
        if (Number.isNaN(value.getTime())) { return ''; }
        return value.toLocaleTimeString('da-DK', { hour: '2-digit', minute: '2-digit' });
    }

    function editorDraftHideRecovery() {
        $('#h18-editor-recovery-actions').prop('hidden', true);
    }

    function editorDraftShowRecovery() {
        $('#h18-editor-recovery-actions').prop('hidden', false);
    }

    function editorDraftRead() {
        try {
            if (!window.localStorage) { return null; }
            const raw = window.localStorage.getItem(editorDraftStorageKey());
            if (!raw) { return null; }
            const value = JSON.parse(raw);
            if (!value || value.Version !== editorDraftVersion || value.PageSlug !== editorDraftPageSlug()) { return null; }
            if (!value.Snapshot || typeof value.Snapshot !== 'object' || !value.Snapshot.html || !value.Snapshot.signature) { return null; }
            return value;
        } catch (error) {
            editorDraftSetStatus('Lokal kladde kunne ikke læses', 'error');
            return null;
        }
    }

    function editorDraftRemove(updateStatus) {
        try {
            if (window.localStorage) { window.localStorage.removeItem(editorDraftStorageKey()); }
            if (updateStatus !== false) { editorDraftSetStatus('Lokal kladde: ingen ændringer', ''); }
            return true;
        } catch (error) {
            editorDraftSetStatus('Lokal kladde kunne ikke slettes', 'error');
            return false;
        }
    }

    function editorDraftSaveNow(markSubmitted) {
        window.clearTimeout(editorDraftTimer);
        editorDraftTimer = null;
        if (!editorHistoryReady || editorHistoryApplying) { return false; }
        if (editorDraftRecoveryPending && !markSubmitted) { return false; }
        const snapshot = editorHistorySnapshot();
        if (!snapshot) { return false; }
        if (snapshot.signature === editorDraftServerSignature) {
            editorDraftRemove(false);
            editorDraftSetStatus('Lokal kladde: ingen ændringer', '');
            return true;
        }
        const now = new Date().toISOString();
        const payload = {
            Version: editorDraftVersion,
            PluginVersion: '0.5.13',
            PageSlug: editorDraftPageSlug(),
            BaseSignature: editorDraftServerSignature,
            SavedAtUtc: now,
            SubmittedAtUtc: markSubmitted ? now : '',
            Snapshot: snapshot
        };
        let raw = '';
        try {
            raw = JSON.stringify(payload);
            if (raw.length > editorDraftMaxChars) {
                editorDraftSetStatus('Lokal kladde er for stor til browserlager', 'error');
                return false;
            }
            if (!window.localStorage) { throw new Error('localStorage unavailable'); }
            window.localStorage.setItem(editorDraftStorageKey(), raw);
            editorDraftSetStatus('Lokal kladde gemt ' + editorDraftFormatTime(now), 'saved');
            return true;
        } catch (error) {
            editorDraftSetStatus('Lokal kladde kunne ikke gemmes', 'error');
            return false;
        }
    }

    function editorDraftScheduleSave(delay) {
        if (!editorHistoryReady || editorHistoryApplying || editorDraftRecoveryPending) { return; }
        window.clearTimeout(editorDraftTimer);
        editorDraftTimer = window.setTimeout(function () { editorDraftSaveNow(false); }, Math.max(150, Number(delay) || 1200));
    }

    function editorDraftInitializeRecovery(initial) {
        if (!initial) { return; }
        editorDraftServerSignature = initial.signature;
        editorDraftHideRecovery();
        const draft = editorDraftRead();
        if (!draft) {
            editorDraftSetStatus('Lokal kladde: klar', '');
            return;
        }
        if (draft.Snapshot.signature === initial.signature) {
            editorDraftRemove(false);
            editorDraftSetStatus('Lokal kladde er allerede gemt', 'saved');
            return;
        }
        const submittedAt = draft.SubmittedAtUtc ? new Date(draft.SubmittedAtUtc).getTime() : 0;
        const recentlySubmitted = submittedAt > 0 && (Date.now() - submittedAt) >= 0 && (Date.now() - submittedAt) <= editorDraftSubmitSuccessWindowMs;
        if (recentlySubmitted && draft.BaseSignature && draft.BaseSignature !== initial.signature) {
            editorDraftRemove(false);
            editorDraftSetStatus('Sidste lokale kladde er gemt i WordPress', 'saved');
            return;
        }
        editorDraftCandidate = draft;
        editorDraftRecoveryPending = true;
        editorDraftShowRecovery();
        const time = editorDraftFormatTime(draft.SavedAtUtc);
        const stale = Boolean(draft.BaseSignature && draft.BaseSignature !== initial.signature);
        editorDraftSetStatus(
            'Kladde fundet' + (time ? ' ' + time : '') + (stale ? ' · ældre sideversion' : ' · kan gendannes'),
            'warning'
        );
    }

    function editorDraftRestoreCandidate() {
        if (!editorDraftCandidate || !editorDraftCandidate.Snapshot || !editorHistoryReady) { return; }
        const draft = editorDraftCandidate;
        const serverEntry = editorHistoryEntries.find(function (entry) { return entry.signature === editorDraftServerSignature; }) || editorHistoryEntries[0];
        editorDraftRecoveryPending = false;
        editorDraftCandidate = null;
        editorDraftHideRecovery();
        editorHistoryEntries.splice(0, editorHistoryEntries.length);
        if (serverEntry) { editorHistoryEntries.push(serverEntry); }
        if (!serverEntry || draft.Snapshot.signature !== serverEntry.signature) { editorHistoryEntries.push(draft.Snapshot); }
        editorHistoryIndex = editorHistoryEntries.length - 1;
        editorHistoryRestore(draft.Snapshot);
        editorDraftSaveNow(false);
        editorHistoryUpdateUi();
    }

    function editorDraftDiscardCandidate() {
        editorDraftRecoveryPending = false;
        editorDraftCandidate = null;
        editorDraftHideRecovery();
        editorDraftRemove(false);
        editorDraftSetStatus('Lokal kladde kasseret', '');
        editorDraftScheduleSave(250);
    }
'''
js = replace_once(js, vars_anchor, vars_anchor + draft_block, 'draft state/functions')

record_anchor = '''        editorHistoryIndex = editorHistoryEntries.length - 1;\n        editorHistoryUpdateUi();\n    }'''.replace('\\n', '\n')
record_new = '''        editorHistoryIndex = editorHistoryEntries.length - 1;\n        editorHistoryUpdateUi();\n        editorDraftScheduleSave();\n    }'''.replace('\\n', '\n')
js = replace_once(js, record_anchor, record_new, 'history autosave hook')

restore_anchor = '''        } finally {\n            editorHistoryApplying = false;\n            editorHistoryUpdateUi();\n        }\n    }'''.replace('\\n', '\n')
restore_new = '''        } finally {\n            editorHistoryApplying = false;\n            editorHistoryUpdateUi();\n            if (editorHistoryReady) { editorDraftScheduleSave(250); }\n        }\n    }'''.replace('\\n', '\n')
js = replace_once(js, restore_anchor, restore_new, 'restore autosave hook')

init_anchor = '''        editorHistorySavedSignature = initial.signature;\n        editorHistoryReady = true;\n        editorHistoryUpdateUi();'''.replace('\\n', '\n')
init_new = '''        editorHistorySavedSignature = initial.signature;\n        editorDraftServerSignature = initial.signature;\n        editorHistoryReady = true;\n        editorHistoryUpdateUi();\n        editorDraftInitializeRecovery(initial);'''.replace('\\n', '\n')
js = replace_once(js, init_anchor, init_new, 'history recovery initialization')

submit_anchor = "        $pageEditorForm.on('submit', function () { editorHistorySubmitting = true; });"
submit_new = '''        $pageEditorForm.on('submit', function () {
            editorHistoryFlushPending();
            window.clearTimeout(editorDraftTimer);
            editorDraftTimer = null;
            editorDraftSaveNow(!$pageWhatIf.is(':checked'));
            editorHistorySubmitting = true;
        });'''
js = replace_once(js, submit_anchor, submit_new, 'submit draft handling')

unload_anchor = '''        editorHistoryFlushPending();\n        const live = editorHistorySnapshot();'''.replace('\\n', '\n')
unload_new = '''        editorHistoryFlushPending();\n        editorDraftSaveNow(false);\n        const live = editorHistorySnapshot();'''.replace('\\n', '\n')
js = replace_once(js, unload_anchor, unload_new, 'beforeunload draft flush')

end_anchor = '\n});\n'
if not js.endswith(end_anchor):
    raise SystemExit('jQuery wrapper ending not found')
end_events = r'''

    $(document).on('click', '#h18-editor-restore-draft', function (event) {
        event.preventDefault();
        editorHistoryFlushPending();
        editorDraftRestoreCandidate();
    });

    $(document).on('click', '#h18-editor-discard-draft', function (event) {
        event.preventDefault();
        editorDraftDiscardCandidate();
    });

    $(window).on('pagehide.h18EditorDraft', function () {
        if (!editorHistoryReady || editorHistorySubmitting) { return; }
        editorHistoryFlushPending();
        editorDraftSaveNow(false);
    });

    if (document && document.addEventListener) {
        document.addEventListener('visibilitychange', function () {
            if (document.visibilityState !== 'hidden' || !editorHistoryReady || editorHistorySubmitting) { return; }
            editorHistoryFlushPending();
            editorDraftSaveNow(false);
        });
    }
'''
js = js[:-len(end_anchor)] + end_events + end_anchor
js_path.write_text(js, encoding='utf-8')

css = css_path.read_text(encoding='utf-8')
css_add = '''\n/* v0.5.13 local autosave / recovery */\n.h18-editor-draft-controls{display:inline-flex;align-items:center;gap:6px;flex-wrap:wrap;margin-left:6px}\n.h18-editor-recovery-actions{display:inline-flex;align-items:center;gap:4px}\n.h18-editor-recovery-actions[hidden]{display:none!important}\n.h18-editor-autosave-status{white-space:nowrap}\n.h18-editor-autosave-status.is-saved{font-weight:600}\n.h18-editor-autosave-status.is-warning,.h18-editor-autosave-status.is-error{font-weight:700}\n'''
if '/* v0.5.13 local autosave / recovery */' in css:
    raise SystemExit('v0.5.13 css already present')
css_path.write_text(css.rstrip() + css_add + '\n', encoding='utf-8')

readme = readme_path.read_text(encoding='utf-8')
readme = replace_once(readme, 'Version: 0.5.11', 'Version: 0.5.13', 'readme top version')
intro_anchor = 'Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.\n\n\n'
intro_new = '''Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.\n\n\n== Version 0.5.13 – Lokal autosave og crash recovery ==\n\nNyt:\n- lokal browser-autosave af sideeditorens aktuelle recovery-state\n- kladden gemmes pr. side og indeholder sideopbygning, Card Grid, design og aktuelle feltværdier\n- Gendan kladde / Kassér kladde vises kun, når der faktisk findes en relevant recovery-state\n- ældre kladder markeres tydeligt, hvis WordPress-siden er ændret siden kladden blev oprettet\n- ingen kladde gendannes automatisk; restore kræver altid et aktivt klik\n- autosave flusher ved skjult fane/pagehide og før browserens ugemte-ændringer-advarsel\n- permanent Gem, WhatIf, WordPress-revisioner og JSON-backups er uændrede\n- page-editor schema forbliver 1.12; ingen datamigrering er nødvendig\n\n== Version 0.5.12 – Undo / Redo og sikker redigeringshistorik ==\n\nNyt:\n- lokal Undo/Redo-historik med op til 50 trin\n- Fortryd/Gendan-knapper og Ctrl/Cmd+Z samt Ctrl/Cmd+Shift+Z uden at overtage normal tekst-undo i inputfelter\n- historikken dækker live canvas, sektioner, Card Grid og rækkefølge\n- status for ugemte ændringer og browseradvarsel ved navigation\n- hurtige ændringer flusher før Undo/Redo, og Card Grid i Inspector indgår i historikken\n- page-editor schema forbliver 1.12; permanente revisioner og backups er uændrede\n\n\n'''
readme = replace_once(readme, intro_anchor, intro_new, 'readme release sections')
readme_path.write_text(readme, encoding='utf-8')

print('v0.5.13 patch applied')
