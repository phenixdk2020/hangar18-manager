from pathlib import Path

ROOT = Path('.')
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
CORE = ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js'
NOTES = ROOT / 'clean-release-notes.html'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
STATUS = ROOT / 'docs/v0164-status.md'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 match, got {count}')
    return text.replace(old, new, 1)


plugin = PLUGIN.read_text(encoding='utf-8')
if 'Version: 0.1.63' in plugin:
    plugin = replace_once(plugin, 'Version: 0.1.63', 'Version: 0.1.64', 'plugin header version')
    plugin = replace_once(plugin, "H18_CLEAN_VERSION', '0.1.63'", "H18_CLEAN_VERSION', '0.1.64'", 'runtime version')
elif 'Version: 0.1.64' not in plugin or "H18_CLEAN_VERSION', '0.1.64'" not in plugin:
    raise SystemExit('unexpected plugin version; expected 0.1.63 or already-applied 0.1.64')
PLUGIN.write_text(plugin, encoding='utf-8')

core = CORE.read_text(encoding='utf-8')

# Preserve the complete canonical responsive geometry in the client model.
old_geometry = """                geometry: {
                    desktop: normalizeDevice(item.geometry && item.geometry.desktop, false),
                    tablet: normalizeDevice(item.geometry && item.geometry.tablet, true),
                    mobile: normalizeDevice(item.geometry && item.geometry.mobile, true)
                },"""
new_geometry = """                geometry: {
                    desktop: normalizeDevice(item.geometry && item.geometry.desktop, false),
                    laptop: normalizeDevice(item.geometry && item.geometry.laptop, true),
                    tablet: normalizeDevice(item.geometry && item.geometry.tablet, true),
                    mobile: normalizeDevice(item.geometry && item.geometry.mobile, true)
                },"""
if old_geometry in core:
    core = replace_once(core, old_geometry, new_geometry, 'normalizeModel laptop geometry')
elif new_geometry not in core:
    raise SystemExit('normalizeModel geometry shape not recognized')

old_add_geometry = """            geometry: {
                desktop: desktop,
                tablet: Object.assign({}, desktop, { inheritDesktop: true }),
                mobile: { x: 0, y: 0, w: 120, h: defaultH, inheritDesktop: true }
            },"""
new_add_geometry = """            geometry: {
                desktop: desktop,
                laptop: Object.assign({}, desktop, { inheritDesktop: true }),
                tablet: Object.assign({}, desktop, { inheritDesktop: true }),
                mobile: { x: 0, y: 0, w: 120, h: defaultH, inheritDesktop: true }
            },"""
if old_add_geometry in core:
    core = replace_once(core, old_add_geometry, new_add_geometry, 'new node laptop geometry')
elif new_add_geometry not in core:
    raise SystemExit('addNode geometry shape not recognized')

# Keep a small transient status channel for copy/paste feedback.
old_vars = """    let nudgeSession = null;
    let memoryClipboard = null;
"""
new_vars = """    let nudgeSession = null;
    let memoryClipboard = null;
    let productivityNoticeTimer = 0;
"""
if old_vars in core:
    core = replace_once(core, old_vars, new_vars, 'productivity notice timer')
elif 'let productivityNoticeTimer = 0;' not in core:
    raise SystemExit('clipboard state variables not recognized')

old_editable = """    function isEditableTarget(target) {
        if (!target || typeof target.closest !== 'function') { return false; }
        return !!target.closest('input,textarea,select,[contenteditable=\"true\"],.wp-editor-area,.mce-content-body');
    }

    function clipboardPayloadFor(id) {"""
new_editable = """    function isEditableTarget(target) {
        if (!target || typeof target.closest !== 'function') { return false; }
        return !!target.closest('input,textarea,select,[contenteditable=\"true\"],.wp-editor-area,.mce-content-body');
    }

    function selectedNodeForProductivity() {
        const direct = nodeById(selectedId);
        if (direct) { return direct; }
        const card = document.querySelector('#h18-clean-canvas .h18-clean-node.is-selected[data-node-id]');
        if (!card) { return null; }
        const recovered = nodeById(card.getAttribute('data-node-id') || '');
        if (recovered) { selectedId = recovered.id; }
        return recovered;
    }

    function productivityNotice(message) {
        const status = document.getElementById('h18-vd-clipboard-status');
        if (!status) { return; }
        if (productivityNoticeTimer) { window.clearTimeout(productivityNoticeTimer); }
        status.textContent = String(message || '');
        productivityNoticeTimer = window.setTimeout(function () {
            productivityNoticeTimer = 0;
            updateProductivityToolbar();
        }, 2200);
    }

    function revealSelected(message) {
        const id = cleanId(selectedId);
        const reveal = function () {
            const card = id ? document.querySelector('#h18-clean-canvas .h18-clean-node[data-node-id=\"' + CSS.escape(id) + '\"]') : null;
            if (card) {
                try { card.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'smooth' }); }
                catch (ignore) { try { card.scrollIntoView(); } catch (ignoreFallback) {} }
            }
            productivityNotice(message);
        };
        if (window.requestAnimationFrame) { window.requestAnimationFrame(reveal); }
        else { window.setTimeout(reveal, 0); }
    }

    function clipboardPayloadFor(id) {"""
if old_editable in core:
    core = replace_once(core, old_editable, new_editable, 'clipboard selection fallback')
elif 'function selectedNodeForProductivity()' not in core:
    raise SystemExit('clipboard helper insertion point not recognized')

old_copy = """    function copySelected() {
        const payload = clipboardPayloadFor(selectedId);
        if (!payload) { return false; }
        writeClipboard(payload);
        lastAction = 'Kopiér ' + typeLabel(payload.rootType);
        diag('clipboard_copy', { rootId: payload.rootId, rootType: payload.rootType, nodeCount: payload.nodes.length, sourcePostId: POST_ID });
        return true;
    }

    function resolvePasteParent(payload) {
        const selected = nodeById(selectedId);"""
new_copy = """    function copySelected() {
        const selected = selectedNodeForProductivity();
        const payload = selected ? clipboardPayloadFor(selected.id) : null;
        if (!payload) { productivityNotice('Vælg først et element'); return false; }
        writeClipboard(payload);
        lastAction = 'Kopiér ' + typeLabel(payload.rootType);
        productivityNotice('Kopieret: ' + typeLabel(payload.rootType) + (payload.nodes.length > 1 ? ' + indhold' : '') + ' · brug Indsæt eller Ctrl+V');
        diag('clipboard_copy', { rootId: payload.rootId, rootType: payload.rootType, nodeCount: payload.nodes.length, sourcePostId: POST_ID });
        return true;
    }

    function resolvePasteParent(payload) {
        const selected = selectedNodeForProductivity();"""
if old_copy in core:
    core = replace_once(core, old_copy, new_copy, 'copy selected fallback and feedback')
elif "productivityNotice('Kopieret:" not in core:
    raise SystemExit('copySelected shape not recognized')

old_paste_tail = """        commit(before, label);
        render();
        diag(duplicateMode ? 'clipboard_duplicate' : 'clipboard_paste', { sourceRootId: payload.rootId, newRootId: selectedId, nodeCount: payload.nodes.length, targetParentId: parentId, sourcePostId: parseInt(payload.sourcePostId || 0, 10) || 0, targetPostId: POST_ID });
        return true;
    }

    function pasteClipboard() { return pastePayload(readClipboard(), false); }
    function duplicateSelected() {
        const payload = clipboardPayloadFor(selectedId);
        return payload ? pastePayload(payload, true) : false;
    }
"""
new_paste_tail = """        commit(before, label);
        render();
        revealSelected((duplicateMode ? 'Duplikeret: ' : 'Indsat: ') + typeLabel(sourceRoot.type) + (payload.nodes.length > 1 ? ' + indhold' : ''));
        diag(duplicateMode ? 'clipboard_duplicate' : 'clipboard_paste', { sourceRootId: payload.rootId, newRootId: selectedId, nodeCount: payload.nodes.length, targetParentId: parentId, sourcePostId: parseInt(payload.sourcePostId || 0, 10) || 0, targetPostId: POST_ID });
        return true;
    }

    function pasteClipboard() {
        const payload = readClipboard();
        if (!payload) { productivityNotice('Clipboard er tomt'); return false; }
        return pastePayload(payload, false);
    }
    function duplicateSelected() {
        const selected = selectedNodeForProductivity();
        const payload = selected ? clipboardPayloadFor(selected.id) : null;
        if (!payload) { productivityNotice('Vælg først et element'); return false; }
        return pastePayload(payload, true);
    }
"""
if old_paste_tail in core:
    core = replace_once(core, old_paste_tail, new_paste_tail, 'paste reveal and duplicate fallback')
elif "revealSelected((duplicateMode ? 'Duplikeret:" not in core:
    raise SystemExit('pastePayload tail not recognized')

old_toolbar_state = """        if (copyButton) { copyButton.disabled = !nodeById(selectedId); }
        if (duplicateButton) { duplicateButton.disabled = !nodeById(selectedId); }
"""
new_toolbar_state = """        const selected = selectedNodeForProductivity();
        if (copyButton) { copyButton.disabled = !selected; }
        if (duplicateButton) { duplicateButton.disabled = !selected; }
"""
if old_toolbar_state in core:
    core = replace_once(core, old_toolbar_state, new_toolbar_state, 'toolbar selected fallback')
elif 'const selected = selectedNodeForProductivity();' not in core:
    raise SystemExit('productivity toolbar state not recognized')

old_keys = """                else if (key === 'c' && nodeById(selectedId)) { event.preventDefault(); finalizeNudge(); copySelected(); }
                else if (key === 'v' && readClipboard()) { event.preventDefault(); finalizeNudge(); pasteClipboard(); }
                else if (key === 'd' && nodeById(selectedId)) { event.preventDefault(); finalizeNudge(); duplicateSelected(); }
"""
new_keys = """                else if (key === 'c' && selectedNodeForProductivity()) { event.preventDefault(); finalizeNudge(); copySelected(); }
                else if (key === 'v') { event.preventDefault(); finalizeNudge(); pasteClipboard(); }
                else if (key === 'd' && selectedNodeForProductivity()) { event.preventDefault(); finalizeNudge(); duplicateSelected(); }
"""
if old_keys in core:
    core = replace_once(core, old_keys, new_keys, 'keyboard clipboard fallback')
elif "else if (key === 'c' && selectedNodeForProductivity())" not in core:
    raise SystemExit('keyboard clipboard handlers not recognized')

# Expose a tiny diagnostic API so live QA can invoke exactly the same production functions.
old_expose_anchor = """    function structuralSummary() {
"""
new_expose_anchor = """    window.H18VDProductivity = {
        copySelected: copySelected,
        pasteClipboard: pasteClipboard,
        duplicateSelected: duplicateSelected,
        selectedId: function () { const node = selectedNodeForProductivity(); return node ? node.id : ''; },
        clipboard: function () { return clone(readClipboard()); }
    };

    function structuralSummary() {
"""
if old_expose_anchor in core and 'window.H18VDProductivity = {' not in core:
    core = replace_once(core, old_expose_anchor, new_expose_anchor, 'productivity diagnostic API')
elif 'window.H18VDProductivity = {' not in core:
    raise SystemExit('structuralSummary anchor not recognized')

CORE.write_text(core, encoding='utf-8')

notes = NOTES.read_text(encoding='utf-8')
entry = '<h4>0.1.64 – Designer clipboard og duplikering</h4><ul><li><strong>BUG-23 / VD-CLIPBOARD-002:</strong> Kopiér, Indsæt og Duplikér bruger nu både core-selection og den synlige markerede node som fallback.</li><li>Efter Indsæt/Duplikér vælges kopien og scrolles automatisk ind i view med tydelig clipboard-status.</li><li>Ctrl/Cmd+V viser også feedback hvis clipboard er tomt, i stedet for at fejle lydløst.</li><li>Client-normalisering bevarer nu også canonical laptop-geometri; nye elementer får laptop inheritance fra Desktop.</li><li>Samme rettelse gælder Side Designer og Header/Footer, fordi begge bruger den fælles editor-v018-core runtime.</li></ul>\n'
if not notes.startswith('<h4>0.1.64'):
    notes = entry + notes
NOTES.write_text(notes, encoding='utf-8')

tech = TECH.read_text(encoding='utf-8')
contract = """

## 0.1.64 – Designer clipboard reliability

### BUG-23 / VD-CLIPBOARD-002
- Kopiér/Duplikér må ikke afhænge af kun én intern selection-variabel. Hvis core-selection mangler, må den synligt markerede `.is-selected` node bruges som sikker fallback.
- `Ctrl/Cmd+C`, `Ctrl/Cmd+V`, `Ctrl/Cmd+D` og toolbar-knapperne skal kalde samme produktionsfunktioner.
- Efter Indsæt/Duplikér skal den nye root-node være markeret og automatisk scrolles ind i canvas-view, så en korrekt indsættelse ikke kan ligne en no-op.
- Clipboard-status skal give synlig feedback ved Kopiér, Indsæt, Duplikér og tomt clipboard.
- Clientens canonical model skal bevare `desktop`, `laptop`, `tablet` og `mobile` geometry ved normalisering og clipboard roundtrip.
- `window.H18VDProductivity` eksponerer de samme produktionsfunktioner til live QA/diagnostik; den er ikke en separat implementering.
- Side Designer og Header/Footer skal fortsat bruge den samme `editor-v018-core.js`, så Designer-rettelser gælder begge steder.
"""
if '### BUG-23 / VD-CLIPBOARD-002' not in tech:
    tech = tech.rstrip() + contract + '\n'
TECH.write_text(tech, encoding='utf-8')

STATUS.parent.mkdir(parents=True, exist_ok=True)
STATUS.write_text("""# Visual Designer Manager v0.1.64 status

- BUG-23 / VD-CLIPBOARD-002: Designer clipboard reliability.
- Copy/Duplicate recovers the visibly selected node if the internal selectedId is stale.
- Paste/Duplicate reveals the inserted copy and reports status instead of looking like a no-op.
- Ctrl/Cmd+V reports an empty clipboard explicitly.
- Client normalization preserves desktop/laptop/tablet/mobile geometry.
- The shared editor-v018-core runtime keeps the fix common to Page Designer and Header/Footer.
""", encoding='utf-8')
