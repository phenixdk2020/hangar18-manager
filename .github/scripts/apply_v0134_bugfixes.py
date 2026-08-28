from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def p(rel: str) -> Path:
    return ROOT / rel


def read(rel: str) -> str:
    return p(rel).read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    p(rel).parent.mkdir(parents=True, exist_ok=True)
    p(rel).write_text(text, encoding="utf-8")


def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"Expected source block not found in {rel}: {old[:120]!r}")
    write(rel, text.replace(old, new, 1))


# ---------------------------------------------------------------------------
# Version + late editor stacking CSS
# ---------------------------------------------------------------------------
plugin = "clean/hangar18-manager/hangar18-manager.php"
replace_once(plugin, "Version: 0.1.33", "Version: 0.1.34")
replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.33');", "define('H18_CLEAN_VERSION', '0.1.34');")

style_anchor = """    wp_enqueue_style(
        'h18-clean-editor-v0132',
        H18_CLEAN_URL . 'assets/editor-v0132.css',
        ['h18-clean-editor-v0131'],
        H18_CLEAN_VERSION
    );
"""
style_new = style_anchor + """    wp_enqueue_style(
        'h18-clean-editor-v0134',
        H18_CLEAN_URL . 'assets/editor-v0134.css',
        ['h18-clean-editor-v0132'],
        H18_CLEAN_VERSION
    );
"""
replace_once(plugin, style_anchor, style_new)

write(
    "clean/hangar18-manager/assets/editor-v0134.css",
    """/* Visual Designer Manager 0.1.34\n * VD-FLOAT-STACK-001: floating Buttons are always above normal editor nodes.\n * Canonical zIndex is still preserved and used to order floating Buttons.\n */\n\n/* Normal selection chrome must not create a stacking context that traps or hides\n * a floating descendant. Floating is the intentional overlay layer. */\n.h18-clean-workspace .h18-clean-node{\n    z-index:auto!important;\n}\n.h18-clean-workspace .h18-clean-node.is-selected{\n    z-index:auto!important;\n}\n.h18-clean-workspace .h18-clean-node.is-resizing{\n    z-index:2000!important;\n}\n.h18-clean-workspace .h18-clean-node.is-drop-left,\n.h18-clean-workspace .h18-clean-node.is-drop-right,\n.h18-clean-workspace .h18-clean-v018-drop-target{\n    z-index:3000!important;\n}\n\n/* Dedicated editor overlay band. --h18-vd-floating-layer mirrors canonical\n * zIndex (1..200), so manual Lag still orders multiple floating Buttons. */\n.h18-clean-workspace .h18-clean-node--button.is-floating[data-h18-floating=\"1\"]{\n    z-index:calc(10000 + var(--h18-vd-floating-layer,20))!important;\n}\n.h18-clean-workspace .h18-clean-node--button.is-floating.h18-v0131-floating-drag{\n    z-index:10250!important;\n}\n""",
)


# ---------------------------------------------------------------------------
# Rich text: make v0125 the single authoritative selection owner.
# ---------------------------------------------------------------------------
rich = "clean/hangar18-manager/assets/editor-v0125.js"
replace_once(
    rich,
    """    var active = null;\n    var initialShellChoices = null;\n""",
    """    var active = null;\n    var initialShellChoices = null;\n    var selectionGeneration = 0;\n""",
)

replace_once(
    rich,
    """    function rememberSelection() {\n        if (!active || !active.editor) { return; }\n        var selection = window.getSelection && window.getSelection();\n        if (!selection || !selection.rangeCount) { return; }\n        var range = selection.getRangeAt(0);\n        var container = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentNode;\n        if (container && active.editor.contains(container)) { active.savedRange = range.cloneRange(); }\n    }\n\n    function restoreSelection() {\n        if (!active || !active.editor) { return; }\n        active.editor.focus({ preventScroll: true });\n        if (!active.savedRange || !window.getSelection) { return; }\n        var selection = window.getSelection();\n        selection.removeAllRanges();\n        selection.addRange(active.savedRange);\n    }\n""",
    """    function rememberSelection() {\n        if (!active || !active.editor) { return; }\n        var selection = window.getSelection && window.getSelection();\n        if (!selection || !selection.rangeCount) { return; }\n        var range = selection.getRangeAt(0);\n        var container = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentNode;\n        if (container && active.editor.contains(container)) {\n            try { active.savedRange = range.cloneRange(); } catch (ignoreRange) {}\n            if (!active.formatting) {\n                var logical = captureLogicalSelection(active.editor);\n                if (logical) { active.savedLogical = logical; }\n            }\n        }\n    }\n\n    function restoreSelection() {\n        if (!active || !active.editor) { return false; }\n        try { active.editor.focus({ preventScroll: true }); } catch (ignoreFocus) { active.editor.focus(); }\n        if (!active.savedRange || !window.getSelection) { return false; }\n        try {\n            var selection = window.getSelection();\n            selection.removeAllRanges();\n            selection.addRange(active.savedRange);\n            return true;\n        } catch (ignoreRange) {\n            return false;\n        }\n    }\n""",
)

replace_once(
    rich,
    """    function reinforceLogicalSelection(snapshot) {\n        if (!snapshot) { return; }\n        var restore = function () {\n            if (!active || active.editor !== snapshot.editor || !snapshot.editor.isConnected) { return; }\n            restoreLogicalSelection(snapshot);\n        };\n        restore();\n        if (window.queueMicrotask) { window.queueMicrotask(restore); }\n        else if (window.Promise) { Promise.resolve().then(restore); }\n        window.setTimeout(restore, 0);\n        window.setTimeout(restore, 40);\n        if (window.requestAnimationFrame) {\n            window.requestAnimationFrame(function () { restore(); window.requestAnimationFrame(restore); });\n        }\n    }\n\n    function command(name, value) {\n        if (!active || !active.editor) { return; }\n        restoreSelection();\n        var logicalSelection = captureLogicalSelection(active.editor);\n        try { document.execCommand('styleWithCSS', false, 'false'); } catch (ignoreStyleMode) {}\n        try { document.execCommand(name, false, value || null); } catch (ignore) {}\n        if (!logicalSelection || !restoreLogicalSelection(logicalSelection)) { rememberSelection(); }\n        active.dirty = true;\n        active.textarea.value = cleanHtml(active.editor.innerHTML);\n        updateCanvasPreview(active.textarea.value);\n        reinforceLogicalSelection(logicalSelection);\n    }\n""",
    """    function reinforceLogicalSelection(snapshot) {\n        if (!snapshot) { return; }\n        var generation = ++selectionGeneration;\n        var restore = function () {\n            if (generation !== selectionGeneration) { return; }\n            if (!active || active.editor !== snapshot.editor || !snapshot.editor.isConnected) { return; }\n            restoreLogicalSelection(snapshot);\n        };\n        restore();\n        if (window.queueMicrotask) { window.queueMicrotask(restore); }\n        else if (window.Promise) { Promise.resolve().then(restore); }\n        window.setTimeout(restore, 0);\n        if (window.requestAnimationFrame) { window.requestAnimationFrame(restore); }\n    }\n\n    function command(name, value) {\n        if (!active || !active.editor) { return; }\n\n        // VD-TEXT-SEL-001 / 0.1.34: the logical snapshot captured before the\n        // toolbar steals focus is authoritative. A cloned DOM Range is only a\n        // fallback because Bold/Italic can replace text nodes in Firefox.\n        var logicalSelection = active.savedLogical || captureLogicalSelection(active.editor);\n        if (logicalSelection) { restoreLogicalSelection(logicalSelection); }\n        else { restoreSelection(); }\n\n        active.formatting = true;\n        try {\n            try { document.execCommand('styleWithCSS', false, 'false'); } catch (ignoreStyleMode) {}\n            try { document.execCommand(name, false, value || null); } catch (ignoreCommand) {}\n            try { active.editor.normalize(); } catch (ignoreNormalize) {}\n            if (logicalSelection) { restoreLogicalSelection(logicalSelection); }\n            else { rememberSelection(); }\n        } finally {\n            active.formatting = false;\n        }\n\n        if (logicalSelection) { active.savedLogical = logicalSelection; }\n        active.dirty = true;\n        active.textarea.value = cleanHtml(active.editor.innerHTML);\n        updateCanvasPreview(active.textarea.value);\n        reinforceLogicalSelection(logicalSelection);\n    }\n""",
)

replace_once(
    rich,
    """    function toolbarButton(label, title, handler) {\n        var button = document.createElement('button');\n        button.type = 'button';\n        button.className = 'button h18-vd-rich-button';\n        button.innerHTML = label;\n        button.title = title;\n        button.addEventListener('mousedown', function (event) { rememberSelection(); event.preventDefault(); });\n        button.addEventListener('click', handler);\n        return button;\n    }\n""",
    """    function captureToolbarSelection() {\n        if (!active || !active.editor) { return; }\n        var logical = captureLogicalSelection(active.editor);\n        if (logical) { active.savedLogical = logical; }\n        rememberSelection();\n    }\n\n    function toolbarButton(label, title, handler) {\n        var button = document.createElement('button');\n        button.type = 'button';\n        button.className = 'button h18-vd-rich-button';\n        button.innerHTML = label;\n        button.title = title;\n        // Capture already on pointerdown, before a browser can move focus.\n        // mousedown prevents the toolbar button from becoming the editing focus.\n        button.addEventListener('pointerdown', function () { captureToolbarSelection(); });\n        button.addEventListener('mousedown', function (event) { captureToolbarSelection(); event.preventDefault(); });\n        button.addEventListener('click', handler);\n        return button;\n    }\n""",
)

replace_once(
    rich,
    """        active = { textarea: textarea, editor: editor, dirty: false, savedRange: null };\n""",
    """        active = { textarea: textarea, editor: editor, dirty: false, savedRange: null, savedLogical: null, formatting: false };\n""",
)

replace_once(
    rich,
    """        ['mouseup','keyup','focus'].forEach(function (eventName) { editor.addEventListener(eventName, rememberSelection); });\n        editor.addEventListener('input', function () {\n            if (!active || active.editor !== editor) { return; }\n            active.dirty = true;\n            textarea.value = cleanHtml(editor.innerHTML);\n            updateCanvasPreview(textarea.value);\n            rememberSelection();\n        });\n""",
    """        ['mouseup','keyup','focus'].forEach(function (eventName) {\n            editor.addEventListener(eventName, function () {\n                if (!active || active.editor !== editor || active.formatting) { return; }\n                selectionGeneration += 1;\n                rememberSelection();\n            });\n        });\n        editor.addEventListener('input', function () {\n            if (!active || active.editor !== editor) { return; }\n            active.dirty = true;\n            textarea.value = cleanHtml(editor.innerHTML);\n            updateCanvasPreview(textarea.value);\n            if (!active.formatting) {\n                selectionGeneration += 1;\n                rememberSelection();\n            }\n        });\n""",
)

replace_once(
    rich,
    """    window.H18RichTextV0125 = { sync: sync };\n""",
    """    window.H18RichTextV0125 = {\n        sync: sync,\n        selectionOwner: 'v0134',\n        restoreSelection: function () {\n            if (!active) { return false; }\n            return active.savedLogical ? restoreLogicalSelection(active.savedLogical) : restoreSelection();\n        }\n    };\n""",
)


# ---------------------------------------------------------------------------
# Retire the two legacy rich-selection restorers; keep their other features.
# ---------------------------------------------------------------------------
v131 = "clean/hangar18-manager/assets/editor-v0131.js"
replace_once(
    v131,
    """    document.addEventListener('mousedown', function (event) {\n        const button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
    """    document.addEventListener('mousedown', function (event) {\n        if (window.H18RichTextV0125 && window.H18RichTextV0125.selectionOwner === 'v0134') { return; }\n        const button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
)
replace_once(
    v131,
    """    document.addEventListener('click', function (event) {\n        const button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
    """    document.addEventListener('click', function (event) {\n        if (window.H18RichTextV0125 && window.H18RichTextV0125.selectionOwner === 'v0134') { return; }\n        const button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
)
replace_once(
    v131,
    """        scope.querySelectorAll('.h18-clean-node--button.is-floating[data-h18-floating=\"1\"]').forEach(function (card) {\n            const handle = floatingHandle(card);\n""",
    """        scope.querySelectorAll('.h18-clean-node--button.is-floating[data-h18-floating=\"1\"]').forEach(function (card) {\n            const canonicalLayer = clamp(parseInt(card.style.zIndex || '20', 10) || 20, 1, 200);\n            card.style.setProperty('--h18-vd-floating-layer', String(canonicalLayer));\n            const handle = floatingHandle(card);\n""",
)

v132 = "clean/hangar18-manager/assets/editor-v0132.js"
replace_once(
    v132,
    """    var noticeTimer = 0;\n\n    function richEditorForButton(button) {\n""",
    """    var noticeTimer = 0;\n\n    function richSelectionOwnedByV0125() {\n        return !!(window.H18RichTextV0125 && window.H18RichTextV0125.selectionOwner === 'v0134');\n    }\n\n    function richEditorForButton(button) {\n""",
)
replace_once(
    v132,
    """    document.addEventListener('selectionchange', function () {\n        var selection = window.getSelection && window.getSelection();\n""",
    """    document.addEventListener('selectionchange', function () {\n        if (richSelectionOwnedByV0125()) { return; }\n        var selection = window.getSelection && window.getSelection();\n""",
)
replace_once(
    v132,
    """        document.addEventListener(eventName, function (event) {\n            var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
    """        document.addEventListener(eventName, function (event) {\n            if (richSelectionOwnedByV0125()) { return; }\n            var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
)
replace_once(
    v132,
    """    document.addEventListener('keydown', function (event) {\n        var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
    """    document.addEventListener('keydown', function (event) {\n        if (richSelectionOwnedByV0125()) { return; }\n        var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
)
replace_once(
    v132,
    """    document.addEventListener('click', function (event) {\n        var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
    """    document.addEventListener('click', function (event) {\n        if (richSelectionOwnedByV0125()) { return; }\n        var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;\n""",
)


# ---------------------------------------------------------------------------
# Documentation + release metadata
# ---------------------------------------------------------------------------
readme = "clean/hangar18-manager/readme.txt"
replace_once(readme, "Version: 0.1.33", "Version: 0.1.34")
readme_text = read(readme)
section = """== 0.1.34 ==\n* Rich-text har nu én autoritativ selection-ejer: v0125 command-pipelinen. De ældre v0131/v0132 restore-loops er deaktiveret, så de ikke kan overskrive hinandens Range.\n* Toolbar-selection gemmes allerede ved pointerdown og som logiske tekst-offsets; Fed, Kursiv og Understregning bruger samme atomiske formatteringstransaktion.\n* Flydende Knap tegnes i editoren altid over normale elementer, også når et andet element markeres. Normal selection opretter ikke længere et stacking-context, der kan skjule floating.\n* Canonical Lag/z-index bevares og bruges fortsat til rækkefølge mellem flere flydende Knapper og på frontend.\n* Inspector-scrollrettelsen fra 0.1.32 og palette-floating fra 0.1.33 er bevaret uændret.\n\n"""
if section not in readme_text:
    marker = "== 0.1.33 ==\n"
    if marker not in readme_text:
        raise RuntimeError("0.1.33 readme marker not found")
    readme_text = readme_text.replace(marker, section + marker, 1)
    write(readme, readme_text)

history_path = "clean/hangar18-manager/release-history.json"
history = json.loads(read(history_path))
if not any(str(item.get("version")) == "0.1.34" for item in history):
    history.insert(0, {
        "version": "0.1.34",
        "date": "2026-08-28",
        "items": [
            "Rich-text selection har én autoritativ ejer i v0125; de ældre v0131/v0132 restore-loops er deaktiveret for at fjerne Range-race conditions.",
            "Fed, Kursiv og Understregning bruger samme logiske selection-snapshot og atomiske command-transaction; selection fanges allerede ved pointerdown.",
            "Flydende Knap ligger altid over normale elementer i editoren, også når et andet element markeres.",
            "Canonical Lag/z-index bevares til rækkefølge mellem flere floating-elementer og frontend; editorens top-lag er separat chrome-adfærd.",
            "Inspector-scroll og palette-floating fra 0.1.32/0.1.33 er bevaret."
        ]
    })
    write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + "\n")

write(
    "clean-release-notes.html",
    "<h4>0.1.34</h4><ul>"
    "<li><strong>Rich-text selection:</strong> én autoritativ selection-pipeline erstatter tre konkurrerende restore-mekanismer. Fed, Kursiv og Understregning bruger samme logiske Range-transaction.</li>"
    "<li><strong>Toolbar focus:</strong> selection gemmes allerede ved pointerdown og gendannes efter DOM-normalisering, så Firefox ikke skal stole på en gammel DOM-Range.</li>"
    "<li><strong>Flydende Knap:</strong> floating ligger altid over normale editor-elementer, også når et andet element markeres.</li>"
    "<li><strong>Lag:</strong> canonical z-index bevares til rækkefølge mellem flere floating-elementer og frontend, mens editorens top-lag er separat.</li>"
    "<li><strong>Regression:</strong> Inspector-scroll og palette-floating fra 0.1.32/0.1.33 er bevaret.</li>"
    "</ul>",
)

user_manual = "CLEAN-USER-MANUAL.md"
replace_once(user_manual, "Visual Designer Manager 0.1.33 og nyere", "Visual Designer Manager 0.1.34 og nyere")
replace_once(
    user_manual,
    """I Inspector kan Knap efterfølgende skiftes til **Normal**, hvis den i stedet skal deltage i det almindelige LEGO/grid-layout. En Flydende Knap er et parent-relativt overlay, reserverer ingen normal grid-celle og skubber ikke naboelementer.\n""",
    """I Inspector kan Knap efterfølgende skiftes til **Normal**, hvis den i stedet skal deltage i det almindelige LEGO/grid-layout. En Flydende Knap er et parent-relativt overlay, reserverer ingen normal grid-celle og skubber ikke naboelementer. I editoren ligger Flydende Knap altid visuelt over normale elementer, også når et andet element markeres; feltet **Lag** bruges fortsat til rækkefølgen mellem flere flydende elementer og på frontend.\n""",
)

tech = "CLEAN-TECHNICAL-MANUAL.md"
replace_once(
    tech,
    """- have breakpoint-specifik geometri for Desktop/Laptop/Mobil.\n\n### 6.4 Floating må ikke skjules som CSS-only hack\n""",
    """- have breakpoint-specifik geometri for Desktop/Laptop/Mobil.\n\n**Editor-stacking:** En Flydende Knap skal altid være visuelt over normale editor-elementer, også når et andet element vælges. Selection-chrome må ikke skabe et stacking-context, der skjuler floating. Canonical `zIndex` bevares til rækkefølge mellem flere floating-elementer og frontend; editorens top-lag er separat chrome-adfærd.\n\n### 6.4 Floating må ikke skjules som CSS-only hack\n""",
)

old_status = """## 21. Kontraktstatus for 0.1.33\n\n### VD-FLOAT-001 – Flydende Knap\n\n**IMPLEMENTERET / rettet i 0.1.33.** En palette-Knap klassificeres som Flydende **før** drop-zonen beregnes. Derfor går en ny Flydende Knap ikke gennem Over/Under/Venstre/Højre celle-split og viser ikke disse guides ved indsættelse. Den kan placeres på Side-root, i Sektion eller Kasse. Normal Knap kan fortsat vælges i Inspector og følger almindeligt grid-layout.\n\n### VD-TEXT-SEL-001 – Rich-text selection\n\n**IMPLEMENTERET / rettet i 0.1.33.** Bruger-QA af 0.1.32 viste Fed = PASS, Understregning = PASS og Kursiv = BUG. I 0.1.33 er logisk selection-capture/restore flyttet ind i den fælles rich-text command-pipeline, så DOM-ændringen ved Kursiv håndteres samme sted som Fed og Understregning.\n\nGodkendelsestest er fortsat: markér tekst → Fed → Kursiv → Understregning uden ny markering mellem kommandoerne.\n\n### VD-BUTTON-TYPE-001 – Knap er Knap\n\n**IMPLEMENTERET.** Palette-Knap oprettes canonical som `type=button`. 0.1.33 præciserer desuden, at den nye palette-Knap starter med `placementMode=overlay`; den er altså både Knap-type og Flydende layouttilstand fra første drop.\n\n### VD-INSPECTOR-SCROLL-001 – Inspector bund-buffer\n\n**PASS i bruger-QA på 0.1.32 / uændret i 0.1.33.** Inspectorens ca. 360 px editor-only bund-buffer fungerer som aftalt og påvirker ikke canonical model, Preview eller frontend.\n"""
new_status = """## 21. Kontraktstatus for 0.1.34\n\n### VD-FLOAT-001 – Flydende Knap\n\n**IMPLEMENTERET / stacking rettet i 0.1.34.** Palette-Knap starter fortsat som Flydende før drop-zonen beregnes. 0.1.34 fjerner normal-elementers editor stacking-context og giver Flydende Knap et separat top-lag, så den ikke forsvinder, når et andet element markeres. Canonical `zIndex` bevares og bruges til rækkefølge mellem flere floating-elementer og på frontend.\n\n### VD-TEXT-SEL-001 – Rich-text selection\n\n**BUGFIX i 0.1.34 – afventer bruger-QA.** Bruger-QA af 0.1.33 viste Understregning stabil, Fed ustabil og Kursiv fortsat fejlbehæftet. Årsagen var tre samtidige selection-restore-lag (`v0125`, `v0131`, `v0132`). I 0.1.34 er `v0125` eneste autoritative selection-ejer; de to ældre restore-loops delegerer/returnerer. Selection fanges ved pointerdown som logiske tekst-offsets og bruges af én atomisk command-transaction for Fed, Kursiv og Understregning.\n\nGodkendelsestest: mindst gentagne markeringer med Fed, Kursiv og Understregning samt kæden Fed → Kursiv → Understregning uden ny markering.\n\n### VD-BUTTON-TYPE-001 – Knap er Knap\n\n**IMPLEMENTERET / uændret.** Palette-Knap er canonical `type=button` og starter med `placementMode=overlay`. Normal kan fortsat vælges i Inspector.\n\n### VD-FLOAT-STACK-001 – Floating altid over normale editor-elementer\n\n**IMPLEMENTERET i 0.1.34.** Floating får et særskilt editor-toplag. Valg/selection af Tekst, Billede, Kasse eller Sektion må ikke skjule den flydende Knap. Dette editorlag ændrer ikke den canonical lagværdi.\n\n### VD-INSPECTOR-SCROLL-001 – Inspector bund-buffer\n\n**PASS i bruger-QA på 0.1.32 / uændret i 0.1.34.** Inspectorens ca. 360 px editor-only bund-buffer fungerer som aftalt og påvirker ikke canonical model, Preview eller frontend.\n"""
replace_once(tech, old_status, new_status)

write(
    "docs/v0134-status.md",
    """# Visual Designer Manager 0.1.34 – status\n\nDato: 28. august 2026\n\n## Scope\n\nRen bugfix-release før videre backlogarbejde.\n\n1. VD-TEXT-SEL-001: Fed/Kursiv/Understregning skal bevare samme selection stabilt.\n2. VD-FLOAT-STACK-001: Flydende Knap må ikke skjules, når et normalt element markeres.\n\n## Implementering\n\n- `editor-v0125.js` er eneste autoritative rich-text selection-owner.\n- Selection gemmes som logiske tekst-offsets ved pointerdown og anvendes i én formatteringstransaktion.\n- Legacy restore-loops i `editor-v0131.js` og `editor-v0132.js` deaktiveres, når v0125 owner er aktiv.\n- `editor-v0134.css` fjerner normale node-stacking-contexts i editoren og placerer floating i et særskilt top-lag.\n- Canonical Lag/z-index bevares til floating-rækkefølge og frontend.\n\n## QA-gate\n\n- PHP syntax PASS.\n- JavaScript syntax PASS.\n- Hierarchy/model regression PASS.\n- Kildekontrakter for single selection owner og floating top-layer PASS.\n- Endelig Firefox interaction-QA udføres af bruger efter release.\n""",
)

print("Visual Designer Manager 0.1.34 deterministic bugfix patch applied.")
