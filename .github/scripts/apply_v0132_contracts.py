from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
JS = ROOT / 'clean/hangar18-manager/assets/editor-v0132.js'
CSS = ROOT / 'clean/hangar18-manager/assets/editor-v0132.css'
README = ROOT / 'clean/hangar18-manager/readme.txt'
HISTORY = ROOT / 'clean/hangar18-manager/release-history.json'
NOTES = ROOT / 'clean-release-notes.html'
USER_MANUAL = ROOT / 'CLEAN-USER-MANUAL.md'
TECH_MANUAL = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
STATUS = ROOT / 'docs/v0132-status.md'

js = r'''(function () {
    'use strict';

    /*
     * Visual Designer Manager 0.1.32 contract hardening.
     *
     * VD-TEXT-SEL-001:
     * A rich-text selection must survive Bold/Italic/Underline and chained
     * toolbar commands, even when the browser rewrites text nodes.
     *
     * VD-BUTTON-TYPE-001:
     * A palette Button is always canonical type=button. When hierarchy rules
     * reject a root-level Button drop, make the rejection explicit so the
     * previously selected Text node cannot be mistaken for a newly created Button.
     */

    var richSnapshot = null;
    var richRestoreUntil = 0;
    var richRestoreScheduled = false;
    var paletteDrag = null;
    var noticeTimer = 0;

    function richEditorForButton(button) {
        var shell = button && button.closest ? button.closest('.h18-vd-rich-shell') : null;
        return shell ? shell.querySelector('.h18-vd-rich-editor') : null;
    }

    function selectionBelongsToEditor(editor, range) {
        if (!editor || !range) { return false; }
        var common = range.commonAncestorContainer;
        if (common && common.nodeType !== 1) { common = common.parentNode; }
        return !!(common && (common === editor || editor.contains(common)));
    }

    function captureRichSelection(editor) {
        if (!editor || !editor.isConnected || !window.getSelection) { return null; }
        var selection = window.getSelection();
        if (!selection || !selection.rangeCount) { return null; }
        var range = selection.getRangeAt(0);
        if (!selectionBelongsToEditor(editor, range) || range.collapsed) { return null; }
        try {
            var startProbe = document.createRange();
            startProbe.selectNodeContents(editor);
            startProbe.setEnd(range.startContainer, range.startOffset);
            var endProbe = document.createRange();
            endProbe.selectNodeContents(editor);
            endProbe.setEnd(range.endContainer, range.endOffset);
            var start = startProbe.toString().length;
            var end = endProbe.toString().length;
            if (end <= start) { return null; }
            return { editor: editor, start: start, end: end };
        } catch (ignore) {
            return null;
        }
    }

    function pointAtOffset(editor, requestedOffset) {
        var remaining = Math.max(0, parseInt(requestedOffset || 0, 10) || 0);
        var walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT);
        var node = walker.nextNode();
        var last = null;
        while (node) {
            last = node;
            var length = String(node.nodeValue || '').length;
            if (remaining <= length) { return { node: node, offset: remaining }; }
            remaining -= length;
            node = walker.nextNode();
        }
        if (last) { return { node: last, offset: String(last.nodeValue || '').length }; }
        return { node: editor, offset: 0 };
    }

    function restoreRichSelection(snapshot) {
        if (!snapshot || !snapshot.editor || !snapshot.editor.isConnected || !window.getSelection) { return false; }
        var editor = snapshot.editor;
        var start = pointAtOffset(editor, snapshot.start);
        var end = pointAtOffset(editor, Math.max(snapshot.start, snapshot.end));
        try {
            var range = document.createRange();
            range.setStart(start.node, start.offset);
            range.setEnd(end.node, end.offset);
            if (range.collapsed && snapshot.end > snapshot.start) { return false; }
            try { editor.focus({ preventScroll: true }); } catch (ignoreFocus) { editor.focus(); }
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            return true;
        } catch (ignore) {
            return false;
        }
    }

    function restoreBurst(snapshot) {
        if (!snapshot || !snapshot.editor) { return; }
        richRestoreUntil = Date.now() + 320;
        var restore = function () {
            if (!snapshot.editor.isConnected) { return; }
            if (restoreRichSelection(snapshot)) { richSnapshot = snapshot; }
        };

        if (window.queueMicrotask) { window.queueMicrotask(restore); }
        else if (window.Promise) { Promise.resolve().then(restore); }
        window.setTimeout(restore, 0);
        window.setTimeout(restore, 24);
        window.setTimeout(restore, 80);
        window.setTimeout(restore, 180);
        if (window.requestAnimationFrame) {
            window.requestAnimationFrame(function () {
                restore();
                window.requestAnimationFrame(restore);
            });
        }
    }

    function armRichSelection(button) {
        var editor = richEditorForButton(button);
        if (!editor) { return null; }
        var fresh = captureRichSelection(editor);
        if (fresh) { richSnapshot = fresh; }
        if (richSnapshot && richSnapshot.editor === editor) { return richSnapshot; }
        return null;
    }

    document.addEventListener('selectionchange', function () {
        var selection = window.getSelection && window.getSelection();
        if (selection && selection.rangeCount) {
            var range = selection.getRangeAt(0);
            var common = range.commonAncestorContainer;
            if (common && common.nodeType !== 1) { common = common.parentNode; }
            var editor = common && common.closest ? common.closest('.h18-vd-rich-editor') : null;
            if (editor && !range.collapsed) {
                var fresh = captureRichSelection(editor);
                if (fresh) { richSnapshot = fresh; }
                return;
            }
        }

        if (richSnapshot && Date.now() < richRestoreUntil && !richRestoreScheduled) {
            richRestoreScheduled = true;
            var run = function () {
                richRestoreScheduled = false;
                if (Date.now() < richRestoreUntil) { restoreRichSelection(richSnapshot); }
            };
            if (window.requestAnimationFrame) { window.requestAnimationFrame(run); }
            else { window.setTimeout(run, 0); }
        }
    });

    ['pointerdown', 'mousedown'].forEach(function (eventName) {
        document.addEventListener(eventName, function (event) {
            var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;
            if (!button) { return; }
            armRichSelection(button);
        }, true);
    });

    document.addEventListener('keydown', function (event) {
        var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;
        if (!button || (event.key !== 'Enter' && event.key !== ' ')) { return; }
        armRichSelection(button);
    }, true);

    document.addEventListener('click', function (event) {
        var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;
        if (!button) { return; }
        var snapshot = armRichSelection(button);
        if (!snapshot) { return; }
        restoreBurst({ editor: snapshot.editor, start: snapshot.start, end: snapshot.end });
    }, false);

    function modelTypes() {
        var field = document.getElementById('h18-clean-model-json');
        var result = Object.create(null);
        if (!field) { return result; }
        try {
            var model = JSON.parse(field.value || '{}');
            (Array.isArray(model && model.nodes) ? model.nodes : []).forEach(function (node) {
                if (node && node.id) { result[String(node.id)] = String(node.type || '').toLowerCase(); }
            });
        } catch (ignore) {}
        return result;
    }

    function showNotice(message, error) {
        var el = document.getElementById('h18-v0132-contract-notice');
        if (!el) {
            el = document.createElement('div');
            el.id = 'h18-v0132-contract-notice';
            el.setAttribute('role', 'status');
            el.setAttribute('aria-live', 'polite');
            document.body.appendChild(el);
        }
        el.className = 'h18-v0132-contract-notice' + (error ? ' is-error' : '');
        el.textContent = String(message || '');
        el.classList.add('is-visible');
        window.clearTimeout(noticeTimer);
        noticeTimer = window.setTimeout(function () { el.classList.remove('is-visible'); }, 4200);
    }

    function dragBadge(show) {
        var el = document.getElementById('h18-v0132-button-drag-badge');
        if (!show) {
            if (el) { el.remove(); }
            document.body.removeAttribute('data-h18-v0132-palette-type');
            return;
        }
        if (!el) {
            el = document.createElement('div');
            el.id = 'h18-v0132-button-drag-badge';
            el.className = 'h18-v0132-button-drag-badge';
            el.textContent = 'TRÆKKER KNAP · slip i Sektion eller Kasse';
            document.body.appendChild(el);
        }
        document.body.setAttribute('data-h18-v0132-palette-type', 'button');
    }

    function paletteType(target) {
        var button = target && target.closest ? target.closest('.h18-clean-add[data-type]') : null;
        return button ? String(button.getAttribute('data-type') || '').toLowerCase() : '';
    }

    window.addEventListener('dragstart', function (event) {
        var type = paletteType(event.target);
        if (!type) { return; }
        paletteDrag = { type: type, before: modelTypes() };
        if (type === 'button') { dragBadge(true); }
    }, true);

    window.addEventListener('drop', function () {
        if (!paletteDrag) { return; }
        var attempt = { type: paletteDrag.type, before: paletteDrag.before };
        window.setTimeout(function () {
            var after = modelTypes();
            var added = Object.keys(after).filter(function (id) { return !Object.prototype.hasOwnProperty.call(attempt.before, id); });
            if (attempt.type !== 'button') { return; }
            if (!added.length) {
                showNotice('Knap blev ikke oprettet. Træk Knap ind i en Sektion eller Kasse – det valgte TEKST-element er stadig det gamle element.', true);
                return;
            }
            var buttonIds = added.filter(function (id) { return after[id] === 'button'; });
            if (!buttonIds.length) {
                showNotice('Typekontrol fejlede: palette-elementet KNAP må kun oprettes som canonical type button.', true);
                return;
            }
            showNotice('Knap oprettet som KNAP.', false);
        }, 40);
    }, true);

    window.addEventListener('dragend', function () {
        paletteDrag = null;
        dragBadge(false);
    }, true);

    window.H18VisualDesignerV0132 = {
        captureRichSelection: captureRichSelection,
        restoreRichSelection: restoreRichSelection,
        verifyButtonType: function () {
            var types = modelTypes();
            return Object.keys(types).filter(function (id) { return types[id] === 'button'; });
        }
    };
}());
'''

css = r'''/* Visual Designer Manager 0.1.32 */

/* UI-04 / VD-INSPECTOR-SCROLL-001: editor-only breathing room after the last control. */
.h18-clean-inspector:not(.is-collapsed)::after{
    content:"";
    display:block;
    width:100%;
    height:360px;
    min-height:360px;
    clear:both;
    pointer-events:none;
}

.h18-v0132-button-drag-badge,
.h18-v0132-contract-notice{
    position:fixed;
    right:24px;
    z-index:100000;
    box-sizing:border-box;
    max-width:440px;
    padding:10px 14px;
    border:2px solid #2271b1;
    border-radius:8px;
    background:#ffffff;
    color:#1d2327;
    font-size:13px;
    font-weight:600;
    line-height:1.35;
    box-shadow:0 6px 24px rgba(0,0,0,.18);
    pointer-events:none;
}

.h18-v0132-button-drag-badge{ top:64px; }

.h18-v0132-contract-notice{
    top:112px;
    opacity:0;
    transform:translateY(-6px);
    transition:opacity .14s ease, transform .14s ease;
}

.h18-v0132-contract-notice.is-visible{
    opacity:1;
    transform:translateY(0);
}

.h18-v0132-contract-notice.is-error{
    border-color:#d63638;
}
'''

JS.write_text(js, encoding='utf-8')
CSS.write_text(css, encoding='utf-8')

plugin = PLUGIN.read_text(encoding='utf-8')
if 'Version: 0.1.32' not in plugin:
    if 'Version: 0.1.31' not in plugin or "H18_CLEAN_VERSION', '0.1.31'" not in plugin:
        raise SystemExit('Expected 0.1.31 plugin version not found')
    plugin = plugin.replace('Version: 0.1.31', 'Version: 0.1.32', 1)
    plugin = plugin.replace("H18_CLEAN_VERSION', '0.1.31'", "H18_CLEAN_VERSION', '0.1.32'", 1)

css_anchor = """    wp_enqueue_style(\n        'h18-clean-editor-v0131',\n        H18_CLEAN_URL . 'assets/editor-v0131.css',\n        ['h18-clean-editor-v0125'],\n        H18_CLEAN_VERSION\n    );\n"""
css_add = css_anchor + """    wp_enqueue_style(\n        'h18-clean-editor-v0132',\n        H18_CLEAN_URL . 'assets/editor-v0132.css',\n        ['h18-clean-editor-v0131'],\n        H18_CLEAN_VERSION\n    );\n"""
if "'h18-clean-editor-v0132'" not in plugin:
    if css_anchor not in plugin:
        raise SystemExit('0.1.31 CSS enqueue anchor not found')
    plugin = plugin.replace(css_anchor, css_add, 1)

js_anchor = """    wp_enqueue_script(\n        'h18-clean-editor-v0131',\n        H18_CLEAN_URL . 'assets/editor-v0131.js',\n        ['h18-clean-editor-v0125'],\n        H18_CLEAN_VERSION,\n        true\n    );\n"""
js_add = js_anchor + """    wp_enqueue_script(\n        'h18-clean-editor-v0132',\n        H18_CLEAN_URL . 'assets/editor-v0132.js',\n        ['h18-clean-editor-v0131'],\n        H18_CLEAN_VERSION,\n        true\n    );\n"""
if "H18_CLEAN_URL . 'assets/editor-v0132.js'" not in plugin:
    if js_anchor not in plugin:
        raise SystemExit('0.1.31 JS enqueue anchor not found')
    plugin = plugin.replace(js_anchor, js_add, 1)
PLUGIN.write_text(plugin, encoding='utf-8')

readme = README.read_text(encoding='utf-8')
readme = readme.replace('Version: 0.1.31', 'Version: 0.1.32', 1)
section = '''== 0.1.32 ==
* Rich-text selection er hardenet: samme markerede tekst gendannes efter Fed, Kursiv og Understregning og bevares til kædede toolbar-kommandoer.
* Knap-typekontrakten er synliggjort: palette-Knap er canonical type=button; hvis hierarchy-reglen afviser et root-drop, vises tydeligt at Knap ikke blev oprettet og skal slippes i en Sektion eller Kasse.
* Inspector har 360 px ekstra usynlig scroll-buffer efter sidste kontrol, så nederste felter kan rulles fri af viewport-kanten.
* Flydende Knap bevarer parent-relativ overlay-adfærd, springer normal celle-split/autogrow over og er fortsat aldrig position:fixed.
* Teknisk manual og brugermanual er synkroniseret med 0.1.32-kontrakterne.

'''
if '== 0.1.32 ==' not in readme:
    marker = '== 0.1.31 ==\n'
    if marker not in readme:
        raise SystemExit('0.1.31 readme section not found')
    readme = readme.replace(marker, section + marker, 1)
README.write_text(readme, encoding='utf-8')

history = json.loads(HISTORY.read_text(encoding='utf-8'))
if not isinstance(history, list):
    raise SystemExit('release-history.json must be a list')
if not any(str(row.get('version', '')) == '0.1.32' for row in history if isinstance(row, dict)):
    history.insert(0, {
        'version': '0.1.32',
        'date': '2026-08-27',
        'items': [
            'Rich-text selection gendannes robust efter Fed, Kursiv og Understregning, så samme markering kan bruges til flere formatteringer i træk.',
            'Knap fra paletten forbliver canonical type=button; afviste root-drops forklares tydeligt, så en eksisterende valgt Tekst ikke kan forveksles med en ny Knap.',
            'Inspector har en 360 px editor-only scroll-buffer efter sidste kontrol, så nederste felter kan rulles komfortabelt op i viewporten.',
            'Flydende Knap-reglerne regression-sikres: parent-relativ overlay, ingen normal grid-række/celle-split, ingen autogrow alene pga. floating-position.',
            'Bruger- og teknisk dokumentation er synkroniseret med 0.1.32.'
        ]
    })
HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

NOTES.write_text(
    '<h4>0.1.32</h4><ul>'
    '<li><strong>Rich text selection:</strong> markeringen gendannes efter Fed, Kursiv og Understregning og bevares til flere formatteringer i træk.</li>'
    '<li><strong>Knap-type og drop-feedback:</strong> Knap er fortsat canonical type <code>button</code>. Hvis hierarchy-reglen afviser et drop på root, får brugeren nu tydelig besked om, at Knap ikke blev oprettet og skal placeres i en Sektion eller Kasse.</li>'
    '<li><strong>Inspector:</strong> 360 px ekstra usynlig scroll-buffer efter sidste kontrol gør de nederste felter lettere at arbejde med.</li>'
    '<li><strong>Floating regression:</strong> Flydende Knap forbliver parent-relativ overlay, reserverer ingen normal grid-række og påvirker ikke autogrow alene på grund af sin position.</li>'
    '<li><strong>Dokumentation:</strong> teknisk manual og brugermanual er opdateret til 0.1.32-kontrakterne.</li>'
    '</ul>',
    encoding='utf-8'
)

user = USER_MANUAL.read_text(encoding='utf-8')
user = user.replace('Gælder for: Visual Designer Manager 0.1.31 og nyere', 'Gælder for: Visual Designer Manager 0.1.32 og nyere', 1)
if '| 1.2 |' not in user:
    user = user.replace(
        '| 1.1 | Nyt kapitel om websides anatomi, Header/Footer kontra Hero, elementoversigt samt grafiske illustrationer og tydelig markering af planlagt funktionalitet. |',
        '| 1.1 | Nyt kapitel om websides anatomi, Header/Footer kontra Hero, elementoversigt samt grafiske illustrationer og tydelig markering af planlagt funktionalitet. |\n| 1.2 | Opdateret til Visual Designer Manager 0.1.32 med rich-text selection-kontrakt, tydelig Knap-drop-feedback og ekstra Inspector-scrollplads. |',
        1
    )
release_doc = '''\n## 0.1.32 – Rich text, Knap-drop og Inspector\n\n- Markeret rich text skal forblive markeret efter **Fed**, **Kursiv** og **Understregning**, så flere formatteringer kan anvendes uden ny markering.\n- **Knap** er et selvstændigt canonical element. Hvis Knap forsøges sluppet direkte på root, oprettes den ikke; Designer viser tydeligt, at den skal trækkes ind i en **Sektion eller Kasse**.\n- Inspector har ekstra tom scrollplads nederst, så sidste kontrol kan rulles komfortabelt op fra vinduets nederste kant.\n- Flydende Knap forbliver et parent-relativt overlay og påvirker ikke normal grid-autogrow alene på grund af floating-position.\n'''
if '## 0.1.32 – Rich text, Knap-drop og Inspector' not in user:
    user = user.rstrip() + '\n' + release_doc + '\n'
USER_MANUAL.write_text(user, encoding='utf-8')

tech = TECH_MANUAL.read_text(encoding='utf-8')
tech = tech.replace('Senest opdateret: 27. august 2026', 'Senest opdateret: 27. august 2026', 1)
status_section = '''## 21. Kontraktstatus for 0.1.32\n\n### VD-FLOAT-001 – Flydende Knap\n\n**IMPLEMENTERET / regressionstestet.** 0.1.31 indførte det parent-relative overlay-flow. 0.1.32 fastholder kontrakten: ingen normal grid-række/celle-split, ingen parent auto-grow alene på grund af floating-position og aldrig `position:fixed`.\n\n### VD-TEXT-SEL-001 – Rich-text selection\n\n**IMPLEMENTERET i 0.1.32.** Selection gendannes ud fra logiske tekst-offsets i flere browser-tidspunkter efter toolbar-kommandoen, så Fed, Kursiv og Understregning kan kædes på samme markering.\n\nHvis browser-/DOM-adfærd senere igen bryder markeringen, genåbnes dette som BUG mod samme FAST-kontrakt.\n\n### VD-BUTTON-TYPE-001 – Knap er Knap\n\n**IMPLEMENTERET / præciseret i 0.1.32.** Core opretter palette-elementet Knap som canonical `type=button`. Den observerede `TEKST`-situation kunne opstå, når hierarchy-reglen afviste et root-drop, hvorefter det tidligere valgte Tekst-element fortsat stod markeret. 0.1.32 gør den afvisning eksplicit og verificerer efter palette-drop, at en ny Knap enten er oprettet som `button`, eller at brugeren får besked om, at den ikke blev oprettet.\n\nHierarkireglen ændres ikke: leaf-elementer som Knap skal ligge i Sektion eller Kasse.\n\n### VD-INSPECTOR-SCROLL-001 – Inspector bund-buffer\n\n**IMPLEMENTERET i 0.1.32.** Inspector får ca. 360 px editor-only scroll-buffer efter sidste kontrol. Bufferen påvirker ikke canonical model, Preview eller frontend.\n\n---\n\n'''
tech = re.sub(
    r'## 21\. Aktuelle kendte kontraktbrud / fejl til næste release\n.*?\n---\n\n(?=## 22\.)',
    status_section,
    tech,
    flags=re.S
)
TECH_MANUAL.write_text(tech, encoding='utf-8')

STATUS.parent.mkdir(parents=True, exist_ok=True)
STATUS.write_text('''# Visual Designer Manager 0.1.32 – Status\n\nDato: 27. august 2026\n\n## Scope\n\n- VD-TEXT-SEL-001: robust selection efter Fed/Kursiv/Understregning.\n- VD-BUTTON-TYPE-001: canonical Button-type + tydelig feedback ved hierarchy-afvist root-drop.\n- VD-INSPECTOR-SCROLL-001: 360 px editor-only bund-buffer.\n- VD-FLOAT-001: regression-gate for parent-relativ floating.\n\n## Bevidst ikke med i denne patch\n\nTabel, Divider, Spacer, Icon, Hero/Topbanner, Menu og øvrige større nye elementtyper forbliver planlagte featurepakker. 0.1.32 er en kontrakt-/fejlrettelsesrelease.\n\n## QA-gates\n\n- PHP syntax på hele pluginet.\n- JavaScript syntax på alle aktive editor-assets.\n- HierarchyNormalizer + LayoutModel regression-QA.\n- v0.1.32 asset/enqueue/version checks.\n- Selection-hærdning og Button-type/drop-feedback findes i aktiv late patch.\n- Inspector 360 px buffer findes kun som editor CSS.\n- Floating-kontrakten findes fortsat i core/responsive/frontend.\n''', encoding='utf-8')

print('Applied Visual Designer Manager 0.1.32 contract fixes.')
