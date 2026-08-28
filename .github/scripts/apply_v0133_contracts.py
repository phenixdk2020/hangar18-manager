from pathlib import Path
import json

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(path, old, new):
    text = read(path)
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{path}: expected exactly one match, found {count}: {old[:100]!r}')
    write(path, text.replace(old, new, 1))


# ---------------------------------------------------------------------------
# Version metadata
# ---------------------------------------------------------------------------
plugin = 'clean/hangar18-manager/hangar18-manager.php'
replace_once(plugin, ' * Version: 0.1.32', ' * Version: 0.1.33')
replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.32');", "define('H18_CLEAN_VERSION', '0.1.33');")

# ---------------------------------------------------------------------------
# VD-TEXT-SEL-001: preserve logical selection inside the shared command path.
# This deliberately fixes the command pipeline itself instead of adding an
# Italic-only UX workaround.
# ---------------------------------------------------------------------------
rich = 'clean/hangar18-manager/assets/editor-v0125.js'
old = """    function restoreSelection() {\n        if (!active || !active.editor) { return; }\n        active.editor.focus({ preventScroll: true });\n        if (!active.savedRange || !window.getSelection) { return; }\n        var selection = window.getSelection();\n        selection.removeAllRanges();\n        selection.addRange(active.savedRange);\n    }\n\n    function command(name, value) {\n        if (!active || !active.editor) { return; }\n        restoreSelection();\n        try { document.execCommand('styleWithCSS', false, false); } catch (ignoreStyleMode) {}\n        try { document.execCommand(name, false, value || null); } catch (ignore) {}\n        rememberSelection();\n        active.dirty = true;\n        active.textarea.value = cleanHtml(active.editor.innerHTML);\n        updateCanvasPreview(active.textarea.value);\n    }\n"""
new = """    function restoreSelection() {\n        if (!active || !active.editor) { return; }\n        active.editor.focus({ preventScroll: true });\n        if (!active.savedRange || !window.getSelection) { return; }\n        var selection = window.getSelection();\n        selection.removeAllRanges();\n        selection.addRange(active.savedRange);\n    }\n\n    function captureLogicalSelection(editor) {\n        if (!editor || !window.getSelection) { return null; }\n        var selection = window.getSelection();\n        if (!selection || !selection.rangeCount) { return null; }\n        var range = selection.getRangeAt(0);\n        var common = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentNode;\n        if (!common || !editor.contains(common) || range.collapsed) { return null; }\n        try {\n            var startProbe = document.createRange();\n            startProbe.selectNodeContents(editor);\n            startProbe.setEnd(range.startContainer, range.startOffset);\n            var endProbe = document.createRange();\n            endProbe.selectNodeContents(editor);\n            endProbe.setEnd(range.endContainer, range.endOffset);\n            var start = startProbe.toString().length;\n            var end = endProbe.toString().length;\n            return end > start ? { editor: editor, start: start, end: end } : null;\n        } catch (ignore) {\n            return null;\n        }\n    }\n\n    function logicalPoint(editor, requestedOffset) {\n        var remaining = Math.max(0, parseInt(requestedOffset || 0, 10) || 0);\n        var walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT);\n        var node = walker.nextNode();\n        var last = null;\n        while (node) {\n            last = node;\n            var length = String(node.nodeValue || '').length;\n            if (remaining <= length) { return { node: node, offset: remaining }; }\n            remaining -= length;\n            node = walker.nextNode();\n        }\n        if (last) { return { node: last, offset: String(last.nodeValue || '').length }; }\n        return { node: editor, offset: 0 };\n    }\n\n    function restoreLogicalSelection(snapshot) {\n        if (!snapshot || !snapshot.editor || !snapshot.editor.isConnected || !window.getSelection) { return false; }\n        var start = logicalPoint(snapshot.editor, snapshot.start);\n        var end = logicalPoint(snapshot.editor, snapshot.end);\n        try {\n            var range = document.createRange();\n            range.setStart(start.node, start.offset);\n            range.setEnd(end.node, end.offset);\n            if (range.collapsed && snapshot.end > snapshot.start) { return false; }\n            try { snapshot.editor.focus({ preventScroll: true }); } catch (ignoreFocus) { snapshot.editor.focus(); }\n            var selection = window.getSelection();\n            selection.removeAllRanges();\n            selection.addRange(range);\n            if (active && active.editor === snapshot.editor) { active.savedRange = range.cloneRange(); }\n            return true;\n        } catch (ignore) {\n            return false;\n        }\n    }\n\n    function reinforceLogicalSelection(snapshot) {\n        if (!snapshot) { return; }\n        var restore = function () {\n            if (!active || active.editor !== snapshot.editor || !snapshot.editor.isConnected) { return; }\n            restoreLogicalSelection(snapshot);\n        };\n        restore();\n        if (window.queueMicrotask) { window.queueMicrotask(restore); }\n        else if (window.Promise) { Promise.resolve().then(restore); }\n        window.setTimeout(restore, 0);\n        window.setTimeout(restore, 40);\n        if (window.requestAnimationFrame) {\n            window.requestAnimationFrame(function () { restore(); window.requestAnimationFrame(restore); });\n        }\n    }\n\n    function command(name, value) {\n        if (!active || !active.editor) { return; }\n        restoreSelection();\n        var logicalSelection = captureLogicalSelection(active.editor);\n        try { document.execCommand('styleWithCSS', false, 'false'); } catch (ignoreStyleMode) {}\n        try { document.execCommand(name, false, value || null); } catch (ignore) {}\n        if (!logicalSelection || !restoreLogicalSelection(logicalSelection)) { rememberSelection(); }\n        active.dirty = true;\n        active.textarea.value = cleanHtml(active.editor.innerHTML);\n        updateCanvasPreview(active.textarea.value);\n        reinforceLogicalSelection(logicalSelection);\n    }\n"""
replace_once(rich, old, new)

# ---------------------------------------------------------------------------
# VD-FLOAT-001 / BUG-04: a palette Button is floating before drop placement is
# calculated. That keeps it out of normal cell split from the first dragover.
# ---------------------------------------------------------------------------
core = 'clean/hangar18-manager/assets/editor-v018-core.js'
replace_once(
    core,
    "function dropPlacement(surface, event, parentId, width, movingId) {",
    "function dropPlacement(surface, event, parentId, width, movingId, paletteType) {"
)
replace_once(
    core,
    """        const movingNode = movingId ? nodeById(movingId) : null;\n        if (isFloatingButton(movingNode)) {\n            const pointerRow = clamp(Math.round((event.clientY - rect.top) / ROW_PX), 0, 10000);\n            const movingH = Math.max(1, movingNode.geometry.desktop.h || MIN_SPLIT_H);\n            placement.y = Math.max(0, pointerRow - Math.floor(movingH / 2));\n            placement.targetId = '';\n            placement.zone = 'overlay';\n            placement.bandIds = [];\n            placement.targetGeometry = null;\n            return placement;\n        }\n""",
    """        const movingNode = movingId ? nodeById(movingId) : null;\n        const paletteFloatingButton = String(paletteType || '').toLowerCase() === 'button';\n        if (isFloatingButton(movingNode) || paletteFloatingButton) {\n            const overlayWidth = paletteFloatingButton ? Math.min(30, UNITS) : width;\n            const pointerRow = clamp(Math.round((event.clientY - rect.top) / ROW_PX), 0, 10000);\n            const movingH = movingNode ? Math.max(1, movingNode.geometry.desktop.h || MIN_SPLIT_H) : MIN_SPLIT_H;\n            placement.w = clamp(overlayWidth, 1, UNITS);\n            placement.x = clamp(Math.round(pointerUnit - (placement.w / 2)), 0, UNITS - placement.w);\n            placement.y = Math.max(0, pointerRow - Math.floor(movingH / 2));\n            placement.targetId = '';\n            placement.zone = 'overlay';\n            placement.bandIds = [];\n            placement.targetGeometry = null;\n            return placement;\n        }\n"""
)
replace_once(
    core,
    """        const newProps = normalizeProps(type, {});\n        if (PARENT_TYPES.includes(type)) { newProps.minHeightRows = defaultH; }\n""",
    """        const newProps = normalizeProps(type, {});\n        if (type === 'button' && p.zone === 'overlay') { newProps.placementMode = 'overlay'; }\n        if (PARENT_TYPES.includes(type)) { newProps.minHeightRows = defaultH; }\n"""
)
replace_once(
    core,
    """            const placement = dropPlacement(surface, event, parentId, width, payload.kind === 'node' ? payload.id : '');\n""",
    """            const placement = dropPlacement(surface, event, parentId, width, payload.kind === 'node' ? payload.id : '', payload.kind === 'palette' ? payload.type : '');\n"""
)
replace_once(
    core,
    """                const placement = dropPlacement(surface, event, parentId, defaultWidth(payload.type, parentId), '');\n""",
    """                const placement = dropPlacement(surface, event, parentId, defaultWidth(payload.type, parentId), '', payload.type);\n"""
)
replace_once(
    core,
    """            const placement = dropPlacement(surface, event, parentId, movingNode.geometry.desktop.w, payload.id);\n""",
    """            const placement = dropPlacement(surface, event, parentId, movingNode.geometry.desktop.w, payload.id, '');\n"""
)

# ---------------------------------------------------------------------------
# Hierarchy: Floating Button is the explicit root-level leaf exception.
# Palette Knap starts floating; an existing Normal Knap still follows leaf rules.
# ---------------------------------------------------------------------------
hierarchy = 'clean/hangar18-manager/assets/editor-v0122-hierarchy.js'
replace_once(
    hierarchy,
    "function decision(event, surface, type) {",
    "function decision(event, surface, type, floating) {"
)
replace_once(
    hierarchy,
    """        if (effectiveParentId === '') {\n            return {\n                allowed: false,\n                message: (LABELS[type] || 'Elementet') + ' skal ligge inde i en Sektion eller Kasse.'\n            };\n        }\n""",
    """        if (effectiveParentId === '') {\n            if (type === 'button' && floating) { return { allowed: true, message: '' }; }\n            return {\n                allowed: false,\n                message: (LABELS[type] || 'Elementet') + ' skal ligge inde i en Sektion eller Kasse.'\n            };\n        }\n"""
)
replace_once(
    hierarchy,
    """            activeDrag = type ? { kind: 'palette', type: type } : null;\n""",
    """            activeDrag = type ? { kind: 'palette', type: type, floating: type === 'button' } : null;\n"""
)
replace_once(
    hierarchy,
    """        activeDrag = type ? { kind: 'node', type: type, id: nodeId(card) } : null;\n""",
    """        activeDrag = type ? { kind: 'node', type: type, id: nodeId(card), floating: !!(card && card.classList.contains('is-floating')) } : null;\n"""
)
replace_once(
    hierarchy,
    """        const result = decision(event, surface, activeDrag.type);\n""",
    """        const result = decision(event, surface, activeDrag.type, !!activeDrag.floating);\n"""
)
replace_once(
    hierarchy,
    """        toast((LABELS[type] || 'Elementet') + ' skal trækkes ind i en Sektion eller Kasse.', null);\n""",
    """        toast(type === 'button'\n            ? 'Knap skal trækkes til canvas, Sektion eller Kasse, så placeringen kan vælges som Flydende.'\n            : (LABELS[type] || 'Elementet') + ' skal trækkes ind i en Sektion eller Kasse.', null);\n"""
)
replace_once(
    hierarchy,
    """            } else if (type) {\n                button.title = 'Træk ' + (LABELS[type] || type) + ' ind i en Sektion eller Kasse';\n            }\n""",
    """            } else if (type === 'button') {\n                button.title = 'Træk Knap til canvas, Sektion eller Kasse · starter som Flydende';\n            } else if (type) {\n                button.title = 'Træk ' + (LABELS[type] || type) + ' ind i en Sektion eller Kasse';\n            }\n"""
)

# 0.1.32 diagnostic wording must match the now-explicit floating root exception.
v132 = 'clean/hangar18-manager/assets/editor-v0132.js'
replace_once(v132, "TRÆKKER KNAP · slip i Sektion eller Kasse", "TRÆKKER KNAP · slip på canvas, i Sektion eller Kasse")
replace_once(
    v132,
    "Knap blev ikke oprettet. Træk Knap ind i en Sektion eller Kasse – det valgte TEKST-element er stadig det gamle element.",
    "Knap blev ikke oprettet. Slip Knap på canvas eller i en Sektion/Kasse – det valgte element er stadig det gamle element."
)

# ---------------------------------------------------------------------------
# Release documentation
# ---------------------------------------------------------------------------
readme = 'clean/hangar18-manager/readme.txt'
text = read(readme)
text = text.replace('Version: 0.1.32', 'Version: 0.1.33', 1)
marker = '== 0.1.32 ==\n'
if marker not in text:
    raise SystemExit('readme: 0.1.32 marker missing')
entry = """== 0.1.33 ==\n* Kursiv bruger nu samme logiske selection-capture/restore inde i den fælles rich-text command-pipeline som Fed og Understregning.\n* Palette-Knap starter som Flydende før drop-zonen beregnes, så den ikke længere viser eller udfører Over/Under/Venstre/Højre cell-split.\n* Flydende Knap kan slippes på Side-root, i Sektion eller Kasse; Normal Knap følger fortsat almindelige leaf-/grid-regler.\n* Inspectorens 360 px bund-buffer fra 0.1.32 er uændret og regression-sikret.\n* Bruger- og teknisk dokumentation er synkroniseret med de to rettede interaction contracts.\n\n"""
text = text.replace(marker, entry + marker, 1)
write(readme, text)

history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
if history and history[0].get('version') == '0.1.33':
    raise SystemExit('release-history already contains 0.1.33')
history.insert(0, {
    'version': '0.1.33',
    'date': '2026-08-28',
    'items': [
        'Kursiv bevarer nu selection via logiske tekst-offsets inde i den fælles rich-text command-pipeline; Fed og Understregning bruger samme mekanisme.',
        'En Knap fra paletten klassificeres som Flydende før drop-beregning og går derfor ikke gennem Over/Under/Venstre/Højre celle-split.',
        'Flydende Knap kan placeres på Side-root, i Sektion eller Kasse; Normal Knap forbliver et almindeligt grid/leaf-element.',
        'Inspector-scroll fra 0.1.32 bevares uændret og er fortsat editor-only.',
        'Teknisk manual og brugermanual er opdateret, så hierarchy-undtagelsen for Flydende Knap er eksplicit.'
    ]
})
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

write('clean-release-notes.html', """<h4>0.1.33</h4><ul><li><strong>Kursiv selection:</strong> selection gemmes og gendannes nu som logiske tekst-offsets inde i den fælles rich-text command-pipeline, så Kursiv matcher Fed og Understregning.</li><li><strong>Flydende Knap fra palette:</strong> Knap klassificeres som Flydende før drop-zone beregnes. Derfor vises eller udføres almindelig Over/Under/Venstre/Højre celle-split ikke ved indsættelse.</li><li><strong>Hierarchy:</strong> Flydende Knap er den eksplicitte leaf-undtagelse og må placeres på Side-root, i Sektion eller Kasse. Normal Knap følger fortsat almindeligt grid-layout.</li><li><strong>Inspector:</strong> den fungerende 360 px bund-buffer fra 0.1.32 er bevaret uændret.</li><li><strong>Dokumentation:</strong> bruger- og teknisk manual er synkroniseret med de rettede kontrakter.</li></ul>""")

# User manual
user_manual = 'CLEAN-USER-MANUAL.md'
text = read(user_manual)
text = text.replace('Senest opdateret: 27. august 2026', 'Senest opdateret: 28. august 2026', 1)
text = text.replace('Gælder for: Visual Designer Manager 0.1.32 og nyere;', 'Gælder for: Visual Designer Manager 0.1.33 og nyere;', 1)
old_button = """### 2.9 Knap\n\nKnap er et selvstændigt element og skal ikke behandles som Tekst. En normal Knap deltager i LEGO-layoutet. En **Flydende Knap** er et parent-relativt overlay, som kan ligge over andet indhold uden at reservere en normal grid-celle.\n"""
new_button = """### 2.9 Knap\n\nKnap er et selvstændigt element og skal ikke behandles som Tekst. Når **Knap trækkes fra paletten**, starter den som **Flydende Knap**, så den kan placeres frit på Side-root, i en Sektion eller Kasse uden at dele den celle, den ligger oven på. Derfor bruges der ikke Over/Under/Venstre/Højre cell-split under selve indsættelsen.\n\nI Inspector kan Knap efterfølgende skiftes til **Normal**, hvis den i stedet skal deltage i det almindelige LEGO/grid-layout. En Flydende Knap er et parent-relativt overlay, reserverer ingen normal grid-celle og skubber ikke naboelementer.\n"""
if old_button not in text:
    raise SystemExit('user manual: button section did not match')
text = text.replace(old_button, new_button, 1)
write(user_manual, text)

# Technical manual
tech = 'CLEAN-TECHNICAL-MANUAL.md'
text = read(tech)
text = text.replace('Senest opdateret: 27. august 2026', 'Senest opdateret: 28. august 2026', 1)
old_hierarchy = """- Sektion: kun direkte på Side/root.\n- Kasse: i Sektion eller Kasse.\n- Leaf-elementer: i Sektion eller Kasse.\n- Kasse må indeholde Kasse.\n- Sektion må ikke nestes som almindelig Kasse.\n"""
new_hierarchy = """- Sektion: kun direkte på Side/root.\n- Kasse: i Sektion eller Kasse.\n- Normale leaf-elementer: i Sektion eller Kasse.\n- **Flydende Knap er den eksplicitte leaf-undtagelse** og må placeres på Side/root, i Sektion eller Kasse.\n- Kasse må indeholde Kasse.\n- Sektion må ikke nestes som almindelig Kasse.\n"""
if old_hierarchy not in text:
    raise SystemExit('technical manual: hierarchy section did not match')
text = text.replace(old_hierarchy, new_hierarchy, 1)
old_normal = """### 6.2 Normal Knap\n\nEn normal Knap deltager i almindeligt LEGO/grid-layout og kan placeres via Over/Under/Venstre/Højre.\n\n### 6.3 Flydende Knap\n"""
new_normal = """### 6.2 Normal Knap\n\nEn normal Knap deltager i almindeligt LEGO/grid-layout og kan placeres via Over/Under/Venstre/Højre. Normal er en bevidst tilstand, som kan vælges i Inspector.\n\nNår **Knap trækkes fra paletten**, er den godkendte standard derimod **Flydende**, så indsættelsen ikke først går gennem almindelig celle-split.\n\n### 6.3 Flydende Knap\n"""
if old_normal not in text:
    raise SystemExit('technical manual: normal button section did not match')
text = text.replace(old_normal, new_normal, 1)
start = text.index('## 21. Kontraktstatus for 0.1.32')
end = text.index('\n---\n\n## 22. Teknisk review', start)
status = """## 21. Kontraktstatus for 0.1.33\n\n### VD-FLOAT-001 – Flydende Knap\n\n**IMPLEMENTERET / rettet i 0.1.33.** En palette-Knap klassificeres som Flydende **før** drop-zonen beregnes. Derfor går en ny Flydende Knap ikke gennem Over/Under/Venstre/Højre celle-split og viser ikke disse guides ved indsættelse. Den kan placeres på Side-root, i Sektion eller Kasse. Normal Knap kan fortsat vælges i Inspector og følger almindeligt grid-layout.\n\n### VD-TEXT-SEL-001 – Rich-text selection\n\n**IMPLEMENTERET / rettet i 0.1.33.** Bruger-QA af 0.1.32 viste Fed = PASS, Understregning = PASS og Kursiv = BUG. I 0.1.33 er logisk selection-capture/restore flyttet ind i den fælles rich-text command-pipeline, så DOM-ændringen ved Kursiv håndteres samme sted som Fed og Understregning.\n\nGodkendelsestest er fortsat: markér tekst → Fed → Kursiv → Understregning uden ny markering mellem kommandoerne.\n\n### VD-BUTTON-TYPE-001 – Knap er Knap\n\n**IMPLEMENTERET.** Palette-Knap oprettes canonical som `type=button`. 0.1.33 præciserer desuden, at den nye palette-Knap starter med `placementMode=overlay`; den er altså både Knap-type og Flydende layouttilstand fra første drop.\n\n### VD-INSPECTOR-SCROLL-001 – Inspector bund-buffer\n\n**PASS i bruger-QA på 0.1.32 / uændret i 0.1.33.** Inspectorens ca. 360 px editor-only bund-buffer fungerer som aftalt og påvirker ikke canonical model, Preview eller frontend.\n"""
text = text[:start] + status + text[end:]
write(tech, text)

# Release status document
write('docs/v0133-status.md', """# Visual Designer Manager 0.1.33 – status\n\nDato: 28. august 2026\n\n## Scope\n\n0.1.33 er en fokuseret bugfix-release før næste backlog-featurepakke.\n\n1. VD-TEXT-SEL-001: Kursiv skal bevare samme tekstselection som Fed og Understregning.\n2. VD-FLOAT-001: En ny Flydende Knap fra paletten må ikke gå gennem normal celle-split.\n\n## Implementering\n\n- Rich-text command-pipelinen gemmer selection som logiske tekst-offsets før `execCommand` og rekonstruerer en frisk Range efter DOM-ændringen.\n- Palette-Knap klassificeres som floating før drop-placement beregnes.\n- Overlay-drop nulstiller target/cell-band og bruger fri parent-relativ X/Y.\n- `placementMode=overlay` sættes canonical ved oprettelsen.\n- Flydende Knap er eksplicit hierarchy-undtagelse og må ligge på Side-root, i Sektion eller Kasse.\n- Normal Knap følger fortsat almindelige leaf/grid-regler.\n- Inspector-scroll fra 0.1.32 ændres ikke.\n\n## QA gates\n\n- PHP syntax på hele pluginet.\n- JavaScript syntax på alle editor-assets.\n- Hierarchy normalizer QA.\n- v0.1.25 model QA.\n- Statisk kontraktcheck af logical selection pipeline.\n- Statisk kontraktcheck af palette-floating før dropPlacement og canonical `placementMode=overlay`.\n- Statisk hierarchy-check af floating root-undtagelsen.\n\nEfter release kræves bruger-QA af de to konkrete interaction flows, før backlog-featurearbejdet fortsættes.\n""")

print('Visual Designer Manager 0.1.33 deterministic patch applied.')
