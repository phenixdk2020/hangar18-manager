from pathlib import Path
p=Path('assets/admin.js')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1: raise SystemExit(f'{label}: expected 1, found {n}')
    s=s.replace(old,new,1)

old="""    function editorHistoryUndo() {
        if (editorHistoryIndex <= 0) { return; }
        editorHistoryIndex -= 1;
        editorHistoryRestore(editorHistoryEntries[editorHistoryIndex]);
    }

    function editorHistoryRedo() {
        if (editorHistoryIndex < 0 || editorHistoryIndex >= editorHistoryEntries.length - 1) { return; }
        editorHistoryIndex += 1;
        editorHistoryRestore(editorHistoryEntries[editorHistoryIndex]);
    }
"""
new="""    function editorHistoryFlushPending() {
        if (!editorHistoryTimer) { return; }
        window.clearTimeout(editorHistoryTimer);
        editorHistoryTimer = null;
        editorHistoryRecordNow();
    }

    function editorHistoryUndo() {
        editorHistoryFlushPending();
        if (editorHistoryIndex <= 0) { return; }
        editorHistoryIndex -= 1;
        editorHistoryRestore(editorHistoryEntries[editorHistoryIndex]);
    }

    function editorHistoryRedo() {
        editorHistoryFlushPending();
        if (editorHistoryIndex < 0 || editorHistoryIndex >= editorHistoryEntries.length - 1) { return; }
        editorHistoryIndex += 1;
        editorHistoryRestore(editorHistoryEntries[editorHistoryIndex]);
    }
"""
once(old,new,'flush pending history')

once("        if (window.MutationObserver && $pageSections.get(0)) {\n", "        if (window.MutationObserver && $pageEditorForm.get(0)) {\n", 'observer guard')
once("            observer.observe($pageSections.get(0), { childList: true, subtree: true, attributes: true, attributeOldValue: true, attributeFilter: ['class'] });\n", "            observer.observe($pageEditorForm.get(0), { childList: true, subtree: true, attributes: true, attributeOldValue: true, attributeFilter: ['class'] });\n", 'observer target')

old_unload="""    $(window).on('beforeunload.h18EditorHistory', function (event) {
        if (!editorHistoryReady || editorHistorySubmitting || editorHistoryIndex < 0) { return; }
        const current = editorHistoryEntries[editorHistoryIndex];
        if (!current || current.signature === editorHistorySavedSignature) { return; }
        event.preventDefault();
        event.returnValue = '';
        return '';
    });
"""
new_unload="""    $(window).on('beforeunload.h18EditorHistory', function (event) {
        if (!editorHistoryReady || editorHistorySubmitting || editorHistoryIndex < 0) { return; }
        editorHistoryFlushPending();
        const live = editorHistorySnapshot();
        if (!live || live.signature === editorHistorySavedSignature) { return; }
        event.preventDefault();
        event.returnValue = '';
        return '';
    });
"""
once(old_unload,new_unload,'beforeunload live snapshot')

p.write_text(s,encoding='utf-8')
print('v0.5.12 history hardening applied')
