from pathlib import Path
import json

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(path, old, new):
    text = read(path)
    if old not in text:
        raise SystemExit(f'Missing expected text in {path}: {old[:120]!r}')
    text = text.replace(old, new, 1)
    write(path, text)


def replace_block(path, start, end, new_block):
    text = read(path)
    a = text.find(start)
    if a < 0:
        raise SystemExit(f'Missing start marker in {path}: {start!r}')
    b = text.find(end, a)
    if b < 0:
        raise SystemExit(f'Missing end marker in {path}: {end!r}')
    text = text[:a] + new_block + text[b:]
    write(path, text)


# ---------------------------------------------------------------------------
# Version / visible backup naming
# ---------------------------------------------------------------------------
replace_once('clean/hangar18-manager/hangar18-manager.php', 'Version: 0.1.35', 'Version: 0.1.36')
replace_once("clean/hangar18-manager/hangar18-manager.php", "define('H18_CLEAN_VERSION', '0.1.35');", "define('H18_CLEAN_VERSION', '0.1.36');")
replace_once(
    'clean/hangar18-manager/src/Update/GitHubUpdater.php',
    "$filename = 'hangar18-manager-clean-v' . $safeCurrent . '-before-v' . $safeTarget . '-' . gmdate('Ymd-His') . '.zip';",
    "$filename = 'visual-designer-manager-v' . $safeCurrent . '-before-v' . $safeTarget . '-' . gmdate('Ymd-His') . '.zip';"
)

# ---------------------------------------------------------------------------
# BUG-02: persistent selection boundary markers
# ---------------------------------------------------------------------------
rich_path = 'clean/hangar18-manager/assets/editor-v0125.js'
marker_code = r'''    /*
     * VD-TEXT-SEL-001 / 0.1.36
     *
     * Firefox may replace or split text nodes differently for STRONG and EM.
     * Logical offsets remain useful as a fallback, but toolbar chaining now
     * owns two persistent empty boundary elements around the selected content.
     * Formatting happens between those boundaries and the native Range is
     * rebuilt from the same DOM anchors after every command.
     */
    function markerSelectionValid() {
        return !!(active && active.editor && active.markerStart && active.markerEnd &&
            active.markerStart.isConnected && active.markerEnd.isConnected &&
            active.editor.contains(active.markerStart) && active.editor.contains(active.markerEnd));
    }

    function clearSelectionMarkers() {
        if (!active) { return; }
        [active.markerStart, active.markerEnd].forEach(function (marker) {
            if (marker && marker.parentNode) { marker.parentNode.removeChild(marker); }
        });
        active.markerStart = null;
        active.markerEnd = null;
    }

    function boundaryMarker(kind) {
        var marker = document.createElement('span');
        marker.setAttribute('data-vd-selection-boundary', kind);
        marker.setAttribute('aria-hidden', 'true');
        marker.contentEditable = 'false';
        marker.style.fontSize = '0';
        marker.style.lineHeight = '0';
        marker.style.pointerEvents = 'none';
        return marker;
    }

    function restoreMarkerSelection() {
        if (!markerSelectionValid() || !window.getSelection) { return false; }
        try {
            var range = document.createRange();
            range.setStartAfter(active.markerStart);
            range.setEndBefore(active.markerEnd);
            if (range.collapsed) { return false; }
            try { active.editor.focus({ preventScroll: true }); } catch (ignoreFocus) { active.editor.focus(); }
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            active.savedRange = range.cloneRange();
            return true;
        } catch (ignore) { return false; }
    }

    function installSelectionMarkers() {
        if (!active || !active.editor || !window.getSelection) { return false; }
        var logical = captureLogicalSelection(active.editor) || active.savedLogical;
        if (!logical) { return false; }
        clearSelectionMarkers();
        if (!restoreLogicalSelection(logical)) { return false; }
        var selection = window.getSelection();
        if (!selection || !selection.rangeCount || selection.getRangeAt(0).collapsed) { return false; }
        var range = selection.getRangeAt(0);
        try {
            var end = boundaryMarker('end');
            var endRange = range.cloneRange();
            endRange.collapse(false);
            endRange.insertNode(end);
            var start = boundaryMarker('start');
            var startRange = range.cloneRange();
            startRange.collapse(true);
            startRange.insertNode(start);
            active.markerStart = start;
            active.markerEnd = end;
            active.savedLogical = logical;
            return restoreMarkerSelection();
        } catch (ignore) {
            clearSelectionMarkers();
            return false;
        }
    }

    function reinforceMarkerSelection() {
        if (!markerSelectionValid()) { return; }
        var generation = ++selectionGeneration;
        var restore = function () {
            if (generation !== selectionGeneration || !markerSelectionValid()) { return; }
            restoreMarkerSelection();
        };
        restore();
        if (window.queueMicrotask) { window.queueMicrotask(restore); }
        else if (window.Promise) { Promise.resolve().then(restore); }
        window.setTimeout(restore, 0);
        window.setTimeout(restore, 24);
        if (window.requestAnimationFrame) { window.requestAnimationFrame(restore); }
    }

'''
replace_once(rich_path, "    var INLINE_FORMAT_TAGS = { bold: 'STRONG', italic: 'EM', underline: 'U' };\n", marker_code + "    var INLINE_FORMAT_TAGS = { bold: 'STRONG', italic: 'EM', underline: 'U' };\n")
replace_once(
    rich_path,
    "        if (!tagName || !snapshot || !restoreLogicalSelection(snapshot) || !window.getSelection) { return false; }",
    "        if (!tagName || !snapshot || !window.getSelection) { return false; }\n        if (markerSelectionValid()) { restoreMarkerSelection(); }\n        else if (!restoreLogicalSelection(snapshot)) { return false; }"
)
replace_once(
    rich_path,
    "        removeMarker(marker);\n        try { snapshot.editor.normalize(); } catch (ignoreNormalize) {}\n        restoreLogicalSelection(snapshot);\n        return true;",
    "        removeMarker(marker);\n        try { snapshot.editor.normalize(); } catch (ignoreNormalize) {}\n        if (markerSelectionValid()) { restoreMarkerSelection(); }\n        else { restoreLogicalSelection(snapshot); }\n        return true;"
)

new_command = r'''    function command(name, value) {
        if (!active || !active.editor) { return; }
        var logicalSelection = active.savedLogical || captureLogicalSelection(active.editor);
        if (markerSelectionValid()) { restoreMarkerSelection(); }
        else if (logicalSelection) { restoreLogicalSelection(logicalSelection); }
        else { restoreSelection(); }

        active.formatting = true;
        try {
            if (INLINE_FORMAT_TAGS[String(name || '').toLowerCase()] && logicalSelection) {
                applyInlineFormat(name, logicalSelection);
            } else {
                try { document.execCommand('styleWithCSS', false, 'false'); } catch (ignoreStyleMode) {}
                try { document.execCommand(name, false, value || null); } catch (ignoreCommand) {}
                try { active.editor.normalize(); } catch (ignoreNormalize) {}
                if (markerSelectionValid()) { restoreMarkerSelection(); }
                else if (logicalSelection) { restoreLogicalSelection(logicalSelection); }
                else { rememberSelection(); }
            }
        } finally { active.formatting = false; }

        if (logicalSelection) { active.savedLogical = captureLogicalSelection(active.editor) || logicalSelection; }
        active.dirty = true;
        active.textarea.value = cleanHtml(active.editor.innerHTML);
        updateCanvasPreview(active.textarea.value);
        if (markerSelectionValid()) { reinforceMarkerSelection(); }
        else { reinforceLogicalSelection(logicalSelection); }
    }

'''
replace_block(rich_path, '    function command(name, value) {', '    function updateCanvasPreview(html) {', new_command)

new_capture = r'''    function captureToolbarSelection() {
        if (!active || !active.editor) { return; }
        if (markerSelectionValid()) {
            restoreMarkerSelection();
            return;
        }
        var logical = captureLogicalSelection(active.editor);
        if (logical) { active.savedLogical = logical; }
        rememberSelection();
        installSelectionMarkers();
    }

'''
replace_block(rich_path, '    function captureToolbarSelection() {', '    function toolbarButton(label, title, handler) {', new_capture)

new_toolbar = r'''    function toolbarButton(label, title, handler) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'button h18-vd-rich-button';
        button.innerHTML = label;
        button.title = title;
        button.addEventListener('pointerdown', function (event) {
            captureToolbarSelection();
            event.preventDefault();
        });
        button.addEventListener('mousedown', function (event) { event.preventDefault(); });
        button.addEventListener('click', function (event) {
            event.preventDefault();
            handler(event);
        });
        return button;
    }

'''
replace_block(rich_path, '    function toolbarButton(label, title, handler) {', '    function enhance() {', new_toolbar)

replace_once(
    rich_path,
    "        active = { textarea: textarea, editor: editor, dirty: false, savedRange: null, savedLogical: null, formatting: false };",
    "        active = { textarea: textarea, editor: editor, dirty: false, savedRange: null, savedLogical: null, formatting: false, markerStart: null, markerEnd: null };"
)

old_events = r'''        ['mouseup','keyup','focus'].forEach(function (eventName) {
            editor.addEventListener(eventName, function () {
                if (!active || active.editor !== editor || active.formatting) { return; }
                selectionGeneration += 1;
                rememberSelection();
            });
        });
        editor.addEventListener('input', function () {
            if (!active || active.editor !== editor) { return; }
            active.dirty = true;
            textarea.value = cleanHtml(editor.innerHTML);
            updateCanvasPreview(textarea.value);
            if (!active.formatting) {
                selectionGeneration += 1;
                rememberSelection();
            }
        });
'''
new_events = r'''        ['mouseup','keyup'].forEach(function (eventName) {
            editor.addEventListener(eventName, function () {
                if (!active || active.editor !== editor || active.formatting) { return; }
                clearSelectionMarkers();
                selectionGeneration += 1;
                rememberSelection();
            });
        });
        editor.addEventListener('focus', function () {
            if (!active || active.editor !== editor || active.formatting || markerSelectionValid()) { return; }
            rememberSelection();
        });
        editor.addEventListener('input', function () {
            if (!active || active.editor !== editor) { return; }
            active.dirty = true;
            textarea.value = cleanHtml(editor.innerHTML);
            updateCanvasPreview(textarea.value);
            if (!active.formatting) {
                clearSelectionMarkers();
                selectionGeneration += 1;
                rememberSelection();
            }
        });
'''
replace_once(rich_path, old_events, new_events)
replace_once(
    rich_path,
    "        restoreSelection: function () {\n            if (!active) { return false; }\n            return active.savedLogical ? restoreLogicalSelection(active.savedLogical) : restoreSelection();\n        }",
    "        selectionMode: 'boundary-markers-v0136',\n        restoreSelection: function () {\n            if (!active) { return false; }\n            if (markerSelectionValid()) { return restoreMarkerSelection(); }\n            return active.savedLogical ? restoreLogicalSelection(active.savedLogical) : restoreSelection();\n        }"
)

# ---------------------------------------------------------------------------
# BUG-07: body-level, viewport-aware color popover for every Inspector color
# ---------------------------------------------------------------------------
color_path = 'clean/hangar18-manager/assets/editor-v0135.js'
old_close = r'''    function close(p) {
        if (!p) { return; }
        p.panel.hidden = true;
        p.button.setAttribute('aria-expanded', 'false');
        if (openPicker === p) { openPicker = null; }
    }
'''
new_close = r'''    function close(p) {
        if (!p) { return; }
        p.panel.hidden = true;
        p.button.setAttribute('aria-expanded', 'false');
        if (p.control && p.control.isConnected) { p.control.appendChild(p.panel); }
        else if (p.panel && p.panel.parentNode) { p.panel.parentNode.removeChild(p.panel); }
        if (openPicker === p) { openPicker = null; }
    }

    function positionPanel(p) {
        if (!p || !p.panel || p.panel.hidden || !p.button || !p.button.isConnected) { return; }
        var margin = 8, gap = 6;
        var vw = Math.max(document.documentElement.clientWidth || 0, window.innerWidth || 0);
        var vh = Math.max(document.documentElement.clientHeight || 0, window.innerHeight || 0);
        var buttonRect = p.button.getBoundingClientRect();
        var inspectorRect = inspector && inspector.getBoundingClientRect ? inspector.getBoundingClientRect() : { left: margin, right: vw - margin, width: vw - (margin * 2) };
        p.panel.style.left = '0px';
        p.panel.style.top = '0px';
        var panelRect = p.panel.getBoundingClientRect();
        var width = Math.min(panelRect.width, Math.max(1, vw - (margin * 2)));
        var height = Math.min(panelRect.height, Math.max(1, vh - (margin * 2)));

        var inspectorMin = Math.max(margin, inspectorRect.left + 4);
        var inspectorMax = Math.min(vw - margin - width, inspectorRect.right - width - 4);
        var x;
        if (inspectorMax >= inspectorMin) {
            x = clamp(buttonRect.left, inspectorMin, inspectorMax);
        } else if (buttonRect.right + gap + width <= vw - margin) {
            x = buttonRect.right + gap;
        } else if (buttonRect.left - gap - width >= margin) {
            x = buttonRect.left - gap - width;
        } else {
            x = clamp(buttonRect.left, margin, Math.max(margin, vw - margin - width));
        }

        var y;
        if (buttonRect.bottom + gap + height <= vh - margin) {
            y = buttonRect.bottom + gap;
        } else if (buttonRect.top - gap - height >= margin) {
            y = buttonRect.top - gap - height;
        } else {
            y = clamp(buttonRect.top, margin, Math.max(margin, vh - margin - height));
        }
        p.panel.style.left = Math.round(x) + 'px';
        p.panel.style.top = Math.round(y) + 'px';
    }
'''
replace_once(color_path, old_close, new_close)
replace_once(
    color_path,
    "        control.appendChild(button); control.appendChild(panel); input.parentNode.insertBefore(control, input.nextSibling);",
    "        control.appendChild(button); input.parentNode.insertBefore(control, input.nextSibling);"
)
old_open = r'''            setHex(p, input.value || initial); panel.hidden = false; button.setAttribute('aria-expanded', 'true'); openPicker = p;
'''
new_open = r'''            setHex(p, input.value || initial);
            document.body.appendChild(panel);
            panel.hidden = false;
            button.setAttribute('aria-expanded', 'true');
            openPicker = p;
            positionPanel(p);
'''
replace_once(color_path, old_open, new_open)
replace_once(
    color_path,
    "        if (!inspector) { return; }\n        inspector.querySelectorAll('input[type=\"color\"][data-field]').forEach(enhance);",
    "        if (!inspector) { return; }\n        if (openPicker && (!openPicker.control || !openPicker.control.isConnected)) { close(openPicker); }\n        inspector.querySelectorAll('input[type=\"color\"][data-field]').forEach(enhance);"
)
replace_once(
    color_path,
    "        document.addEventListener('pointerdown', function (e) { if (openPicker && !openPicker.control.contains(e.target)) { close(openPicker); } });\n        document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && openPicker) { close(openPicker); } });",
    "        document.addEventListener('pointerdown', function (e) { if (openPicker && !openPicker.control.contains(e.target) && !openPicker.panel.contains(e.target)) { close(openPicker); } });\n        document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && openPicker) { close(openPicker); } });\n        window.addEventListener('resize', function () { if (openPicker) { positionPanel(openPicker); } });\n        window.addEventListener('scroll', function () { if (openPicker) { positionPanel(openPicker); } }, true);"
)
replace_once(
    color_path,
    "    window.H18ColorPickerV0135 = { enhance: enhanceAll, normalizeHex: hex, rgbToHsv: rgbToHsv, hsvToRgb: hsvToRgb };",
    "    window.H18ColorPickerV0135 = { enhance: enhanceAll, normalizeHex: hex, rgbToHsv: rgbToHsv, hsvToRgb: hsvToRgb, positionOpenPicker: function () { if (openPicker) { positionPanel(openPicker); } } };"
)

css_path = 'clean/hangar18-manager/assets/editor-v0135.css'
css = read(css_path)
old_panel_css = ".h18-vd-color-panel{position:absolute;z-index:120000;right:0;top:calc(100% + 5px);box-sizing:border-box;width:286px;max-width:min(286px,calc(100vw - 32px));padding:12px;border:1px solid #8c8f94;border-radius:8px;background:#fff;box-shadow:0 10px 34px rgba(0,0,0,.24)}"
new_panel_css = ".h18-vd-color-panel{position:fixed;z-index:120000;left:0;top:0;box-sizing:border-box;width:286px;max-width:calc(100vw - 16px);max-height:calc(100vh - 16px);overflow:auto;padding:12px;border:1px solid #8c8f94;border-radius:8px;background:#fff;box-shadow:0 10px 34px rgba(0,0,0,.24)}"
if old_panel_css not in css:
    raise SystemExit('Missing 0.1.35 panel CSS')
css = css.replace(old_panel_css, new_panel_css, 1)
css = css.replace("\n@media(max-width:1100px){.h18-vd-color-panel{left:0;right:auto}}\n", "\n")
write(css_path, css)

# ---------------------------------------------------------------------------
# Documentation and release metadata
# ---------------------------------------------------------------------------
# Design manual: explicit public naming contract.
design_path = 'CLEAN-DESIGN-MANUAL.md'
design = read(design_path)
design = design.replace('Senest opdateret: 27. august 2026', 'Senest opdateret: 28. august 2026', 1)
if '### 24.2 Produktnavn og synlige filnavne' not in design:
    anchor = "Dokumentationen skal derfor forklare både **hvad et element er**, **hvor det kan ligge**, **hvordan det kombineres med andre elementer**, og **hvordan resultatet ser ud i en rigtig sideopbygning**.\n\n"
    naming = r'''### 24.2 Produktnavn og synlige filnavne

Det officielle produktnavn er **Visual Designer Manager**. Den tidligere udviklingsbetegnelse **Clean** må ikke bruges i nye brugersynlige navne.

Følgende er en FAST navngivningsregel:

- nye releasepakker navngives `visual-designer-manager-v<version>.zip`;
- automatiske programbackups navngives `visual-designer-manager-v<fra-version>-before-v<til-version>-YYYYMMDD-HHMMSS.zip`;
- nye brugersynlige eksport-, backup-, checkpoint-, dokument- og downloadnavne skal bruge **Visual Designer Manager** eller `visual-designer-manager`;
- `Clean`, `hangar18-manager-clean` og tilsvarende gamle produktbetegnelser må ikke introduceres i nye brugersynlige filnavne, UI-tekster eller dokumenttitler;
- historiske filer/releases omdøbes ikke automatisk;
- interne kompatibilitetsidentifikatorer som eksisterende PHP namespace, `h18_clean_*`, WordPress pluginmappe/slug og text-domain må bevares midlertidigt, når en ændring ellers kan bryde opdatering, data eller WordPress-kompatibilitet. De må ikke præsenteres som produktnavn for brugeren.

En senere intern namespace/slug-migration skal behandles som en særskilt kompatibilitetsændring og må ikke blandes sammen med den brugersynlige navngivning.

'''
    if anchor not in design:
        raise SystemExit('Design manual naming anchor missing')
    design = design.replace(anchor, anchor + naming, 1)
design = design.replace('indtil de relevante regler er migreret til Clean.', 'indtil de relevante regler er migreret til Visual Designer Manager.')
write(design_path, design)

user_path = 'CLEAN-USER-MANUAL.md'
user = read(user_path)
user = user.replace('Gælder for: Visual Designer Manager 0.1.34 og nyere', 'Gælder for: Visual Designer Manager 0.1.36 og nyere', 1)
write(user_path, user)

tech_path = 'CLEAN-TECHNICAL-MANUAL.md'
tech = read(tech_path)
tech = tech.replace('## 21. Kontraktstatus for 0.1.34', '## 21. Kontraktstatus for 0.1.36', 1)
old_rich = "**BUGFIX i 0.1.34 – afventer bruger-QA.** Bruger-QA af 0.1.33 viste Understregning stabil, Fed ustabil og Kursiv fortsat fejlbehæftet. Årsagen var tre samtidige selection-restore-lag (`v0125`, `v0131`, `v0132`). I 0.1.34 er `v0125` eneste autoritative selection-ejer; de to ældre restore-loops delegerer/returnerer. Selection fanges ved pointerdown som logiske tekst-offsets og bruges af én atomisk command-transaction for Fed, Kursiv og Understregning."
new_rich = "**BUGFIX i 0.1.36 – afventer bruger-QA.** Bruger-QA af 0.1.35 viste fortsat, at Understregning bevarer selection, mens Fed/Kursiv kan miste den. 0.1.36 gør derfor selection uafhængig af Firefox' genopbygning af `STRONG`/`EM`: to vedvarende, tomme editor-boundary-markører placeres omkring den valgte tekst ved toolbar-pointerdown. Fed, Kursiv og Understregning formatterer mellem de samme markører, og Range rekonstrueres fra markørerne efter hver kommando. Logiske tekst-offsets er kun fallback."
if old_rich in tech:
    tech = tech.replace(old_rich, new_rich, 1)
else:
    raise SystemExit('Technical manual rich text status anchor missing')
color_contract = r'''
### VD-COLOR-POPOVER-001 – Global farvevælgerplacering

**BUGFIX i 0.1.36 – afventer bruger-QA.** Farvevælgeren er én fælles Inspector-popover for alle elementtyper og alle `type=color`-felter. Mens den er åben, flyttes panelet til `document.body`, positioneres som viewport-relativ editor-chrome og clamped til den synlige viewport. Den forsøger først at holde hele panelet inden for Inspectorens vandrette område og vælger derefter en viewport-fallback. Inspector `overflow` må aldrig klippe farvevælgeren. Scroll og resize genberegner placeringen.

'''
anchor = '### VD-INSPECTOR-SCROLL-001 – Inspector bund-buffer\n'
if color_contract.strip() not in tech:
    if anchor not in tech:
        raise SystemExit('Technical manual color contract anchor missing')
    tech = tech.replace(anchor, color_contract + anchor, 1)
write(tech_path, tech)

# Release history.
history_path = Path('clean/hangar18-manager/release-history.json')
history = json.loads(history_path.read_text(encoding='utf-8'))
if not history or history[0].get('version') != '0.1.36':
    history.insert(0, {
        'version': '0.1.36',
        'date': '2026-08-28',
        'items': [
            'Rich-text selection bruger vedvarende start/slut-boundary-markører, så Fed, Kursiv og Understregning kan genvælge præcis samme tekst efter DOM-ændringer.',
            'Toolbar-click forhindrer default fokusflytning; logiske tekst-offsets er fallback frem for primær selection-ejer.',
            'Farvevælgeren er en global body-level popover for alle Inspector-farvefelter og kan ikke længere klippes af Inspector overflow.',
            'Farvepopover positioneres efter Inspector/viewport og genplaceres ved scroll/resize.',
            'Brugersynlige backupnavne skifter til visual-designer-manager; Clean bevares kun i nødvendige interne kompatibilitets-id’er.'
        ]
    })
history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

readme_path = 'clean/hangar18-manager/readme.txt'
readme = read(readme_path)
readme = readme.replace('Version: 0.1.35', 'Version: 0.1.36', 1)
if '== 0.1.36 ==' not in readme:
    insert_at = readme.find('\n== 0.1.35 ==')
    if insert_at < 0:
        raise SystemExit('README 0.1.35 anchor missing')
    block = "\n== 0.1.36 ==\n* Rich-text selection er boundary-marker-baseret: samme markerede tekst fastholdes mellem stabile start/slut-markører gennem Fed, Kursiv og Understregning.\n* Toolbar-knapper flytter ikke fokus som default; logiske offsets er fallback.\n* Visual Designer-farvevælgeren flyttes til body, mens den er åben, og positioneres/clampes til Inspector og viewport for alle elementtyper.\n* Farvepopover genplaceres ved scroll/resize og klippes ikke af Inspectorens overflow.\n* Nye programbackups bruger synligt filnavn visual-designer-manager-v... i stedet for hangar18-manager-clean-v....\n"
    readme = readme[:insert_at] + block + readme[insert_at:]
write(readme_path, readme)

Path('docs/v0136-status.md').write_text('''# Visual Designer Manager 0.1.36 – status\n\nDato: 28. august 2026\n\n## Scope\n- BUG-02 / VD-TEXT-SEL-001: persistent boundary-marker selection for Fed/Kursiv/Understregning.\n- BUG-07 / VD-COLOR-POPOVER-001: global viewport-aware color popover for all Inspector color fields.\n- Public naming: new backups/releases use visual-designer-manager naming; legacy internal identifiers remain for compatibility.\n\n## QA gate\n- PHP syntax.\n- JavaScript syntax.\n- Hierarchy/model regression.\n- Source contracts for marker selection, body-level color popover and public backup naming.\n- Final Firefox interaction QA is performed by the user after release.\n''', encoding='utf-8')

Path('clean-release-notes.html').write_text(
    '<h4>0.1.36</h4><ul>'
    '<li><strong>Rich text:</strong> Fed, Kursiv og Understregning fastholder selection mellem permanente start/slut-boundary-markører.</li>'
    '<li><strong>Firefox:</strong> selection afhænger ikke længere primært af tekstnoderne i STRONG/EM efter DOM-ændringer.</li>'
    '<li><strong>Farvevælger:</strong> fælles body-level popover for alle Inspector-farvefelter; viewport-aware placering og ingen clipping.</li>'
    '<li><strong>Navngivning:</strong> nye synlige backup/release-navne bruger visual-designer-manager.</li>'
    '<li><strong>Regression:</strong> Floating top-layer og Inspector-scroll bevares.</li>'
    '</ul>\n',
    encoding='utf-8'
)

print('0.1.36 patch applied')
