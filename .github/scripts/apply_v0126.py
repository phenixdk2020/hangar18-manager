from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel, text):
    (ROOT / rel).write_text(text, encoding='utf-8')


def replace_exact(rel, old, new, expected=1):
    text = read(rel)
    count = text.count(old)
    if count != expected:
        raise SystemExit(f'{rel}: expected {expected} occurrences, found {count}: {old[:120]!r}')
    text = text.replace(old, new)
    write(rel, text)
    print(f'patched {rel}: {count} replacement(s)')


def replace_regex(rel, pattern, repl, expected=1, flags=0):
    text = read(rel)
    text2, count = re.subn(pattern, repl, text, flags=flags)
    if count != expected:
        raise SystemExit(f'{rel}: expected {expected} regex matches, found {count}: {pattern[:120]!r}')
    write(rel, text2)
    print(f'patched {rel}: {count} regex replacement(s)')


CORE = 'clean/hangar18-manager/assets/editor-v018-core.js'
RICH = 'clean/hangar18-manager/assets/editor-v0125.js'
RICH_CSS = 'clean/hangar18-manager/assets/editor-v0125.css'
UX_CSS = 'clean/hangar18-manager/assets/editor-v0123-ux.css'
IMG = 'clean/hangar18-manager/assets/editor-v0120.js'
MODEL = 'clean/hangar18-manager/src/Model/LayoutModel.php'
RENDERER = 'clean/hangar18-manager/src/Frontend/Renderer.php'

# ---------------------------------------------------------------------------
# Core editor: canonical typography, manual image persistence and button auto-fit
# ---------------------------------------------------------------------------
replace_exact(
    CORE,
    "    function normalizeColor(value) { return /^#[0-9a-f]{6}$/i.test(String(value || '')) ? String(value).toLowerCase() : '#000000'; }\n",
    "    function normalizeColor(value) { return /^#[0-9a-f]{6}$/i.test(String(value || '')) ? String(value).toLowerCase() : '#000000'; }\n"
    "    const FONT_TOKENS = ['system','arial','verdana','tahoma','trebuchet','georgia','times','courier'];\n"
    "    function normalizeFontToken(value, heading) {\n"
    "        const token = String(value || '').toLowerCase();\n"
    "        if (heading && token === 'body') { return 'body'; }\n"
    "        return FONT_TOKENS.includes(token) ? token : 'system';\n"
    "    }\n"
    "    function fontCss(token, bodyToken) {\n"
    "        token = normalizeFontToken(token, true);\n"
    "        if (token === 'body') { token = normalizeFontToken(bodyToken, false); }\n"
    "        return ({system:'system-ui,-apple-system,\\\"Segoe UI\\\",sans-serif',arial:'Arial,sans-serif',verdana:'Verdana,sans-serif',tahoma:'Tahoma,sans-serif',trebuchet:'\\\"Trebuchet MS\\\",sans-serif',georgia:'Georgia,serif',times:'\\\"Times New Roman\\\",serif',courier:'\\\"Courier New\\\",monospace'})[token] || 'system-ui,-apple-system,\\\"Segoe UI\\\",sans-serif';\n"
    "    }\n"
    "    function fontOptions(selected, allowBody) {\n"
    "        const options = [];\n"
    "        if (allowBody) { options.push(['body','Samme som brødtekst']); }\n"
    "        options.push(['system','System / Segoe UI'],['arial','Arial'],['verdana','Verdana'],['tahoma','Tahoma'],['trebuchet','Trebuchet MS'],['georgia','Georgia'],['times','Times New Roman'],['courier','Courier New']);\n"
    "        return options.map(function (item) { return '<option value=\\\"' + item[0] + '\\\"' + (selected === item[0] ? ' selected' : '') + '>' + item[1] + '</option>'; }).join('');\n"
    "    }\n"
    "    function headingPx(props) {\n"
    "        const explicit = clamp(parseInt(props.headingFontSize || 0, 10) || 0, 0, 160);\n"
    "        if (explicit > 0) { return explicit; }\n"
    "        return ({h2:32,h3:28,h4:24,h5:20,h6:18})[String(props.headingLevel || 'h2')] || 32;\n"
    "    }\n"
)

replace_exact(
    CORE,
    "    function fieldLabel(field) { return ({gx:'X-position',gw:'bredde',gy:'Y-position',gh:'højde',heading:'overskrift',headingLevel:'overskrifttype',text:'tekstindhold',align:'tekstjustering',fit:'billedtilpasning',imageAlignX:'vandret billedplacering',imageAlignY:'lodret billedplacering',boxTransparent:'boksbaggrund',boxBackground:'boksbaggrundsfarve',focalX:'billedfokus X',focalY:'billedfokus Y',alt:'alt-tekst',background:'baggrund',radius:'hjørner',padding:'padding',borderWidth:'ramme',borderColor:'rammefarve',gapX:'Afstand X',gapY:'Afstand Y',buttonText:'knaptekst',linkType:'linktype',pageId:'intern side',url:'linkdestination',targetBlank:'ny fane',textColor:'tekstfarve',hoverBackground:'hover-baggrund',hoverTextColor:'hover-tekstfarve',focusColor:'focus-farve',paddingX:'vandret padding',paddingY:'lodret padding'})[String(field || '')] || String(field || 'felt'); }\n",
    "    function fieldLabel(field) { return ({gx:'X-position',gw:'bredde',gy:'Y-position',gh:'højde',heading:'overskrift',headingLevel:'overskrifttype',text:'tekstindhold',align:'tekstjustering',fontFamily:'skrifttype',fontSize:'skriftstørrelse',fontWeight:'skrifttykkelse',lineHeight:'linjeafstand',letterSpacing:'bogstavafstand',headingFontFamily:'overskriftsskrifttype',headingFontSize:'overskriftsstørrelse',headingFontWeight:'overskriftstykkelse',headingLineHeight:'overskriftens linjeafstand',headingLetterSpacing:'overskriftens bogstavafstand',fit:'billedtilpasning',imageAlignX:'vandret billedplacering',imageAlignY:'lodret billedplacering',boxTransparent:'boksbaggrund',boxBackground:'boksbaggrundsfarve',focalX:'billedfokus X',focalY:'billedfokus Y',alt:'alt-tekst',background:'baggrund',radius:'hjørner',padding:'padding',borderWidth:'ramme',borderColor:'rammefarve',gapX:'Afstand X',gapY:'Afstand Y',buttonText:'knaptekst',linkType:'linktype',pageId:'intern side',url:'linkdestination',targetBlank:'ny fane',textColor:'tekstfarve',hoverBackground:'hover-baggrund',hoverTextColor:'hover-tekstfarve',focusColor:'focus-farve',paddingX:'vandret padding',paddingY:'lodret padding',autoSize:'automatisk størrelse'})[String(field || '')] || String(field || 'felt'); }\n"
)

replace_exact(
    CORE,
    "        if (type === 'text') {\n            return Object.assign(common, {\n                heading: String(raw.heading || ''),\n                headingLevel: ['h2', 'h3', 'h4', 'h5', 'h6'].includes(String(raw.headingLevel || '').toLowerCase()) ? String(raw.headingLevel).toLowerCase() : 'h2',\n                text: String(raw.text || 'Ny tekst'),\n                align: ['left', 'center', 'right'].includes(raw.align) ? raw.align : 'left'\n            });\n        }\n",
    "        if (type === 'text') {\n            return Object.assign(common, {\n                heading: String(raw.heading || ''),\n                headingLevel: ['h2', 'h3', 'h4', 'h5', 'h6'].includes(String(raw.headingLevel || '').toLowerCase()) ? String(raw.headingLevel).toLowerCase() : 'h2',\n                text: String(raw.text || 'Ny tekst'),\n                align: ['left', 'center', 'right'].includes(raw.align) ? raw.align : 'left',\n                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#ffffff',\n                backgroundTransparent: raw.backgroundTransparent !== false,\n                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#000000',\n                headingColor: /^#[0-9a-f]{6}$/i.test(String(raw.headingColor || '')) ? String(raw.headingColor).toLowerCase() : '#000000',\n                padding: clamp(parseInt(raw.padding || 0, 10) || 0, 0, 120),\n                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),\n                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),\n                fontSize: clamp(parseInt(raw.fontSize || 16, 10) || 16, 8, 120),\n                fontWeight: clamp(parseInt(raw.fontWeight || 400, 10) || 400, 100, 900),\n                lineHeight: Math.max(0.8, Math.min(3, parseFloat(raw.lineHeight || 1.5) || 1.5)),\n                letterSpacing: Math.max(-10, Math.min(30, parseFloat(raw.letterSpacing || 0) || 0)),\n                headingFontFamily: normalizeFontToken(raw.headingFontFamily || 'body', true),\n                headingFontSize: clamp(parseInt(raw.headingFontSize || 0, 10) || 0, 0, 160),\n                headingFontWeight: clamp(parseInt(raw.headingFontWeight || 700, 10) || 700, 100, 900),\n                headingLineHeight: Math.max(0.8, Math.min(3, parseFloat(raw.headingLineHeight || 1.2) || 1.2)),\n                headingLetterSpacing: Math.max(-10, Math.min(30, parseFloat(raw.headingLetterSpacing || 0) || 0))\n            });\n        }\n"
)

replace_exact(
    CORE,
    "                paddingY: clamp(parseInt(raw.paddingY || 10, 10) || 10, 0, 120),\n                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100)\n",
    "                paddingY: clamp(parseInt(raw.paddingY || 10, 10) || 10, 0, 120),\n                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),\n                autoSize: raw.autoSize !== false\n"
)

replace_exact(
    CORE,
    "            const fit = ['cover', 'contain', 'original', 'stretch'].includes(String(raw.fit || '').toLowerCase()) ? String(raw.fit).toLowerCase() : 'contain';\n",
    "            const fit = ['cover', 'contain', 'original', 'stretch', 'manual'].includes(String(raw.fit || '').toLowerCase()) ? String(raw.fit).toLowerCase() : 'contain';\n"
)
replace_exact(
    CORE,
    "                focalY: clamp(parseInt(raw.focalY || 50, 10) || 50, 0, 100)\n",
    "                focalY: clamp(parseInt(raw.focalY || 50, 10) || 50, 0, 100),\n                manualX: clamp(parseInt(raw.manualX || 0, 10) || 0, -4000, 4000),\n                manualY: clamp(parseInt(raw.manualY || 0, 10) || 0, -4000, 4000),\n                manualW: clamp(parseInt(raw.manualW || 320, 10) || 320, 1, 4000),\n                manualH: clamp(parseInt(raw.manualH || 240, 10) || 240, 1, 4000),\n                lockAspect: raw.lockAspect !== false\n"
)

replace_exact(
    CORE,
    "            wrap.classList.add('h18-clean-node-preview--text');\n            wrap.style.textAlign = node.props.align || 'left';\n",
    "            wrap.classList.add('h18-clean-node-preview--text');\n            wrap.style.textAlign = node.props.align || 'left';\n            wrap.style.fontFamily = fontCss(node.props.fontFamily || 'system');\n            wrap.style.fontSize = String(node.props.fontSize || 16) + 'px';\n            wrap.style.fontWeight = String(node.props.fontWeight || 400);\n            wrap.style.lineHeight = String(node.props.lineHeight || 1.5);\n            wrap.style.letterSpacing = String(node.props.letterSpacing || 0) + 'px';\n"
)
replace_exact(
    CORE,
    "                title.className = 'h18-clean-text-heading';\n                title.textContent = heading;\n",
    "                title.className = 'h18-clean-text-heading';\n                title.textContent = heading;\n                title.style.fontFamily = fontCss(node.props.headingFontFamily || 'body', node.props.fontFamily || 'system');\n                title.style.fontSize = headingPx(node.props) + 'px';\n                title.style.fontWeight = String(node.props.headingFontWeight || 700);\n                title.style.lineHeight = String(node.props.headingLineHeight || 1.2);\n                title.style.letterSpacing = String(node.props.headingLetterSpacing || 0) + 'px';\n"
)
replace_exact(
    CORE,
    "            button.style.width = '100%';\n            button.style.height = '100%';\n",
    "            button.style.width = node.props.autoSize === false ? '100%' : 'max-content';\n            button.style.height = node.props.autoSize === false ? '100%' : 'auto';\n"
)

# Add auto-fit reconciliation for buttons.
replace_exact(
    CORE,
    "    function reconcileLayoutAfterRender(canvas) {\n        const materialized = materializeNaturalLeafHeights();\n",
    "    function autoFitButtons() {\n        const changed = new Set();\n        document.querySelectorAll('.h18-clean-node--button[data-node-id]').forEach(function (card) {\n            const node = nodeById(card.getAttribute('data-node-id') || '');\n            if (!node || node.type !== 'button' || node.props.autoSize === false) { return; }\n            const button = card.querySelector(':scope > .h18-clean-node-preview--button .h18-clean-button-preview');\n            const surface = card.parentElement;\n            if (!button || !surface) { return; }\n            const surfaceWidth = Math.max(1, surface.getBoundingClientRect().width);\n            const unitPx = Math.max(0.1, surfaceWidth / UNITS);\n            const rect = button.getBoundingClientRect();\n            const nextW = clamp(Math.ceil(Math.max(1, rect.width) / unitPx), 1, UNITS - node.geometry.desktop.x);\n            const nextH = clamp(Math.ceil(Math.max(1, rect.height) / ROW_PX), 1, 4000);\n            if (node.geometry.desktop.w !== nextW || node.geometry.desktop.h !== nextH) {\n                node.geometry.desktop.w = nextW;\n                node.geometry.desktop.h = nextH;\n                changed.add(node.id);\n            }\n        });\n        return changed;\n    }\n\n    function reconcileLayoutAfterRender(canvas) {\n        const autoButtons = autoFitButtons();\n        const materialized = materializeNaturalLeafHeights();\n        autoButtons.forEach(function (id) { materialized.add(id); });\n"
)

# Manual resize disables button auto-size.
replace_exact(
    CORE,
    "        if (resizedNode && PARENT_TYPES.includes(resizedNode.type)) {\n            resizedNode.props.minHeightRows = resizedNode.geometry.desktop.h;\n        }\n",
    "        if (resizedNode && PARENT_TYPES.includes(resizedNode.type)) {\n            resizedNode.props.minHeightRows = resizedNode.geometry.desktop.h;\n        }\n        if (resizedNode && resizedNode.type === 'button') { resizedNode.props.autoSize = false; }\n"
)

# Typography controls and button auto-size control in Inspector.
replace_exact(
    CORE,
    "            html += '<label>Justering<select data-field=\"align\"><option value=\"left\"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value=\"center\"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value=\"right\"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label>';\n",
    "            html += '<label>Justering<select data-field=\"align\"><option value=\"left\"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value=\"center\"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value=\"right\"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label>';\n"
    "            html += '<div class=\"h18-vd-typography\"><strong>Typografi · brødtekst</strong><div class=\"h18-clean-field-grid\"><label>Skrifttype<select data-field=\"fontFamily\">' + fontOptions(node.props.fontFamily || 'system', false) + '</select></label><label>Størrelse px<input data-field=\"fontSize\" type=\"number\" min=\"8\" max=\"120\" value=\"' + (node.props.fontSize || 16) + '\"></label><label>Tykkelse<select data-field=\"fontWeight\">' + [300,400,500,600,700,800,900].map(function (v) { return '<option value=\"' + v + '\"' + (parseInt(node.props.fontWeight || 400, 10) === v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label><label>Linjeafstand<input data-field=\"lineHeight\" type=\"number\" step=\"0.1\" min=\"0.8\" max=\"3\" value=\"' + (node.props.lineHeight || 1.5) + '\"></label><label>Bogstavafstand px<input data-field=\"letterSpacing\" type=\"number\" step=\"0.1\" min=\"-10\" max=\"30\" value=\"' + (node.props.letterSpacing || 0) + '\"></label></div><strong>Typografi · overskrift</strong><div class=\"h18-clean-field-grid\"><label>Skrifttype<select data-field=\"headingFontFamily\">' + fontOptions(node.props.headingFontFamily || 'body', true) + '</select></label><label>Størrelse px <span class=\"description\">(0 = automatisk)</span><input data-field=\"headingFontSize\" type=\"number\" min=\"0\" max=\"160\" value=\"' + (node.props.headingFontSize || 0) + '\"></label><label>Tykkelse<select data-field=\"headingFontWeight\">' + [300,400,500,600,700,800,900].map(function (v) { return '<option value=\"' + v + '\"' + (parseInt(node.props.headingFontWeight || 700, 10) === v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label><label>Linjeafstand<input data-field=\"headingLineHeight\" type=\"number\" step=\"0.1\" min=\"0.8\" max=\"3\" value=\"' + (node.props.headingLineHeight || 1.2) + '\"></label><label>Bogstavafstand px<input data-field=\"headingLetterSpacing\" type=\"number\" step=\"0.1\" min=\"-10\" max=\"30\" value=\"' + (node.props.headingLetterSpacing || 0) + '\"></label></div></div>';\n"
)
replace_exact(
    CORE,
    "            html += '<div class=\"h18-clean-field-grid\"><label>Baggrund<input data-field=\"background\" type=\"color\" value=\"' + escapeAttr(node.props.background || '#30382a') + '\"></label><label>Tekstfarve<input data-field=\"textColor\" type=\"color\" value=\"' + escapeAttr(node.props.textColor || '#ffffff') + '\"></label><label>Hover baggrund<input data-field=\"hoverBackground\" type=\"color\" value=\"' + escapeAttr(node.props.hoverBackground || '#525a5f') + '\"></label><label>Hover tekst<input data-field=\"hoverTextColor\" type=\"color\" value=\"' + escapeAttr(node.props.hoverTextColor || '#ffffff') + '\"></label><label>Focus-farve<input data-field=\"focusColor\" type=\"color\" value=\"' + escapeAttr(node.props.focusColor || '#c3ae83') + '\"></label><label>Hjørner px<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"100\" value=\"' + (node.props.radius || 0) + '\"></label><label>Padding X<input data-field=\"paddingX\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingX || 20) + '\"></label><label>Padding Y<input data-field=\"paddingY\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingY || 10) + '\"></label></div>';\n",
    "            html += '<label class=\"h18-clean-checkbox\"><input data-field=\"autoSize\" type=\"checkbox\"' + (node.props.autoSize !== false ? ' checked' : '') + '> Automatisk størrelse efter tekst og padding</label>';\n"
    "            html += '<div class=\"h18-clean-field-grid\"><label>Baggrund<input data-field=\"background\" type=\"color\" value=\"' + escapeAttr(node.props.background || '#30382a') + '\"></label><label>Tekstfarve<input data-field=\"textColor\" type=\"color\" value=\"' + escapeAttr(node.props.textColor || '#ffffff') + '\"></label><label>Hover baggrund<input data-field=\"hoverBackground\" type=\"color\" value=\"' + escapeAttr(node.props.hoverBackground || '#525a5f') + '\"></label><label>Hover tekst<input data-field=\"hoverTextColor\" type=\"color\" value=\"' + escapeAttr(node.props.hoverTextColor || '#ffffff') + '\"></label><label>Focus-farve<input data-field=\"focusColor\" type=\"color\" value=\"' + escapeAttr(node.props.focusColor || '#c3ae83') + '\"></label><label>Hjørner px<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"100\" value=\"' + (node.props.radius || 0) + '\"></label><label>Padding X<input data-field=\"paddingX\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingX || 20) + '\"></label><label>Padding Y<input data-field=\"paddingY\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingY || 10) + '\"></label></div>';\n"
)

replace_exact(
    CORE,
    "                else if (field === 'align') { current.props.align = ['left', 'center', 'right'].includes(control.value) ? control.value : 'left'; }\n",
    "                else if (field === 'align') { current.props.align = ['left', 'center', 'right'].includes(control.value) ? control.value : 'left'; }\n"
    "                else if (field === 'fontFamily') { current.props.fontFamily = normalizeFontToken(control.value, false); }\n"
    "                else if (field === 'fontSize') { current.props.fontSize = clamp(parseInt(control.value || 16, 10) || 16, 8, 120); }\n"
    "                else if (field === 'fontWeight') { current.props.fontWeight = clamp(parseInt(control.value || 400, 10) || 400, 100, 900); }\n"
    "                else if (field === 'lineHeight') { current.props.lineHeight = Math.max(0.8, Math.min(3, parseFloat(control.value || 1.5) || 1.5)); }\n"
    "                else if (field === 'letterSpacing') { current.props.letterSpacing = Math.max(-10, Math.min(30, parseFloat(control.value || 0) || 0)); }\n"
    "                else if (field === 'headingFontFamily') { current.props.headingFontFamily = normalizeFontToken(control.value, true); }\n"
    "                else if (field === 'headingFontSize') { current.props.headingFontSize = clamp(parseInt(control.value || 0, 10) || 0, 0, 160); }\n"
    "                else if (field === 'headingFontWeight') { current.props.headingFontWeight = clamp(parseInt(control.value || 700, 10) || 700, 100, 900); }\n"
    "                else if (field === 'headingLineHeight') { current.props.headingLineHeight = Math.max(0.8, Math.min(3, parseFloat(control.value || 1.2) || 1.2)); }\n"
    "                else if (field === 'headingLetterSpacing') { current.props.headingLetterSpacing = Math.max(-10, Math.min(30, parseFloat(control.value || 0) || 0)); }\n"
)
replace_exact(
    CORE,
    "                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\n",
    "                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }\n                else if (field === 'autoSize') { current.props.autoSize = !!control.checked; }\n"
)

# Better automatic save note: use the actual Undo transaction labels.
replace_exact(
    CORE,
    "                if (note && !note.value) { note.value = lastAction || 'Gem clean layout'; }\n",
    "                if (note && !note.value) {\n                    const labels = window.H18CleanHistory && typeof window.H18CleanHistory.labels === 'function' ? window.H18CleanHistory.labels() : [];\n                    const compact = Array.isArray(labels) ? labels.filter(function (value, index, all) { return value && all.indexOf(value) === index; }).slice(-6) : [];\n                    note.value = compact.length ? compact.join(' · ') : (lastAction || 'Gemt Visual Designer-layout');\n                }\n"
)

# ---------------------------------------------------------------------------
# Rich text: preserve DOM Range selection, block line breaks and submit ordering
# ---------------------------------------------------------------------------
replace_exact(
    RICH,
    "        Array.prototype.slice.call(tpl.content.querySelectorAll('*')).forEach(function (el) {\n            if (allowed.indexOf(el.tagName) === -1) {\n                el.replaceWith.apply(el, Array.prototype.slice.call(el.childNodes));\n                return;\n            }\n",
    "        Array.prototype.slice.call(tpl.content.querySelectorAll('div')).forEach(function (el) {\n            var p = document.createElement('p');\n            while (el.firstChild) { p.appendChild(el.firstChild); }\n            el.replaceWith(p);\n        });\n        Array.prototype.slice.call(tpl.content.querySelectorAll('*')).forEach(function (el) {\n            if (allowed.indexOf(el.tagName) === -1) {\n                el.replaceWith.apply(el, Array.prototype.slice.call(el.childNodes));\n                return;\n            }\n"
)

replace_exact(
    RICH,
    "    function command(name, value) {\n        if (!active || !active.editor) { return; }\n        active.editor.focus();\n        try { document.execCommand(name, false, value || null); } catch (ignore) {}\n        active.dirty = true;\n        active.textarea.value = cleanHtml(active.editor.innerHTML);\n        updateCanvasPreview(active.textarea.value);\n    }\n",
    "    function rememberSelection() {\n        if (!active || !active.editor) { return; }\n        var selection = window.getSelection && window.getSelection();\n        if (!selection || !selection.rangeCount) { return; }\n        var range = selection.getRangeAt(0);\n        var container = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentNode;\n        if (container && active.editor.contains(container)) { active.savedRange = range.cloneRange(); }\n    }\n\n    function restoreSelection() {\n        if (!active || !active.editor) { return; }\n        active.editor.focus({ preventScroll: true });\n        if (!active.savedRange || !window.getSelection) { return; }\n        var selection = window.getSelection();\n        selection.removeAllRanges();\n        selection.addRange(active.savedRange);\n    }\n\n    function command(name, value) {\n        if (!active || !active.editor) { return; }\n        restoreSelection();\n        try { document.execCommand(name, false, value || null); } catch (ignore) {}\n        rememberSelection();\n        active.dirty = true;\n        active.textarea.value = cleanHtml(active.editor.innerHTML);\n        updateCanvasPreview(active.textarea.value);\n    }\n"
)
replace_exact(
    RICH,
    "        button.addEventListener('mousedown', function (event) { event.preventDefault(); });\n",
    "        button.addEventListener('mousedown', function (event) { rememberSelection(); event.preventDefault(); });\n"
)
replace_exact(
    RICH,
    "        active = { textarea: textarea, editor: editor, dirty: false };\n",
    "        active = { textarea: textarea, editor: editor, dirty: false, savedRange: null };\n"
)
replace_exact(
    RICH,
    "        editor.addEventListener('input', function () {\n            if (!active || active.editor !== editor) { return; }\n            active.dirty = true;\n            textarea.value = cleanHtml(editor.innerHTML);\n            updateCanvasPreview(textarea.value);\n        });\n        editor.addEventListener('blur', function () { sync(); });\n",
    "        ['mouseup','keyup','focus'].forEach(function (eventName) { editor.addEventListener(eventName, rememberSelection); });\n        editor.addEventListener('input', function () {\n            if (!active || active.editor !== editor) { return; }\n            active.dirty = true;\n            textarea.value = cleanHtml(editor.innerHTML);\n            updateCanvasPreview(textarea.value);\n            rememberSelection();\n        });\n        editor.addEventListener('blur', function () { sync(); });\n"
)

# Automatic note should begin with actual core transaction labels.
replace_exact(
    RICH,
    "        if (Array.isArray(coreLabels) && coreLabels.length) {\n            var responsiveCount = responsiveChangedCount();\n",
    "        if (Array.isArray(coreLabels) && coreLabels.length) {\n            var seen = Object.create(null);\n            var compactLabels = coreLabels.filter(function (label) { label = String(label || '').trim(); if (!label || seen[label]) { return false; } seen[label] = true; return true; }).slice(-6);\n            if (!String(input.value || '').trim() && compactLabels.length) { input.value = compactLabels.join(' · '); }\n            var responsiveCount = responsiveChangedCount();\n"
)

# Submit sync must run at document-capture level, before the core form capture handler.
replace_exact(
    RICH,
    "        var form = document.getElementById('h18-clean-save-form');\n        if (form) {\n            form.addEventListener('submit', function () {\n                sync();\n                augmentAutomaticNote();\n            }, true);\n        }\n",
    "        var form = document.getElementById('h18-clean-save-form');\n        if (form) {\n            document.addEventListener('submit', function (event) {\n                if (event.target !== form) { return; }\n                sync();\n                augmentAutomaticNote();\n            }, true);\n        }\n"
)

# ---------------------------------------------------------------------------
# Image reset: reset canonical fit and remove stale manual overlay immediately.
# ---------------------------------------------------------------------------
replace_exact(
    IMG,
    "                reset.addEventListener('click', function () {\n                    e.manual = false;\n                    e.fitOverride = 'contain';\n                    syncHidden();\n                    applyAll();\n                    panel.remove();\n                    injectInspector();\n                });\n",
    "                reset.addEventListener('click', function () {\n                    e.manual = false;\n                    e.fitOverride = 'contain';\n                    var staleFrame = card.querySelector('.h18-clean-image-edit-frame');\n                    if (staleFrame) { staleFrame.remove(); }\n                    var fitSelect = host.querySelector('[data-field=\"fit\"]');\n                    if (fitSelect) {\n                        fitSelect.value = 'contain';\n                        fitSelect.dispatchEvent(new Event('change', { bubbles: true }));\n                    } else {\n                        syncHidden();\n                        applyAll();\n                    }\n                    if (panel.isConnected) { panel.remove(); }\n                    injectInspector();\n                });\n"
)
replace_exact(
    IMG,
    "                help.textContent = 'Den grønne ramme styrer billedboksen. Den sandfarvede ramme styrer selve billedet. Billedets pixelmål ændres ikke, når du bagefter gør boksen større.';\n",
    "                help.textContent = 'Grøn ramme = billedboks. Sand ramme = selve billedindholdet.';\n"
)
replace_exact(
    IMG,
    "                hint.textContent = 'Dobbeltklik på billedet eller brug knappen for at få et separat sandfarvet resize-lag til selve billedindholdet.';\n",
    "                hint.textContent = 'Brug knappen for at flytte eller skalere billedet inde i billedboksen.';\n"
)

# ---------------------------------------------------------------------------
# Server canonical model: persist typography, text radius, manual image and auto-size.
# ---------------------------------------------------------------------------
replace_exact(
    MODEL,
    "                'headingColor' => sanitize_hex_color((string) ($raw['headingColor'] ?? '#000000')) ?: '#000000',\n                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),\n",
    "                'headingColor' => sanitize_hex_color((string) ($raw['headingColor'] ?? '#000000')) ?: '#000000',\n                'padding' => self::clamp($raw['padding'] ?? 0, 0, 120, 0),\n                'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),\n                'fontFamily' => self::fontToken($raw['fontFamily'] ?? 'system', false),\n                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 120, 16),\n                'fontWeight' => self::clamp($raw['fontWeight'] ?? 400, 100, 900, 400),\n                'lineHeight' => self::clampFloat($raw['lineHeight'] ?? 1.5, 0.8, 3.0, 1.5),\n                'letterSpacing' => self::clampFloat($raw['letterSpacing'] ?? 0, -10.0, 30.0, 0.0),\n                'headingFontFamily' => self::fontToken($raw['headingFontFamily'] ?? 'body', true),\n                'headingFontSize' => self::clamp($raw['headingFontSize'] ?? 0, 0, 160, 0),\n                'headingFontWeight' => self::clamp($raw['headingFontWeight'] ?? 700, 100, 900, 700),\n                'headingLineHeight' => self::clampFloat($raw['headingLineHeight'] ?? 1.2, 0.8, 3.0, 1.2),\n                'headingLetterSpacing' => self::clampFloat($raw['headingLetterSpacing'] ?? 0, -10.0, 30.0, 0.0),\n"
)
replace_exact(
    MODEL,
    "                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),\n",
    "                'paddingY' => self::clamp($raw['paddingY'] ?? 10, 0, 120, 10),\n                'autoSize' => array_key_exists('autoSize', $raw) ? (bool) $raw['autoSize'] : true,\n"
)
replace_exact(
    MODEL,
    "    /** @param mixed $value */\n    private static function clamp($value, int $min, int $max, int $fallback): int\n",
    "    /** @param mixed $value */\n    private static function fontToken($value, bool $heading): string\n    {\n        $token = sanitize_key((string) $value);\n        if ($heading && $token === 'body') {\n            return 'body';\n        }\n        return in_array($token, ['system', 'arial', 'verdana', 'tahoma', 'trebuchet', 'georgia', 'times', 'courier'], true) ? $token : 'system';\n    }\n\n    /** @param mixed $value */\n    private static function clampFloat($value, float $min, float $max, float $fallback): float\n    {\n        if (!is_numeric($value)) {\n            return $fallback;\n        }\n        return max($min, min($max, (float) $value));\n    }\n\n    /** @param mixed $value */\n    private static function clamp($value, int $min, int $max, int $fallback): int\n"
)

# ---------------------------------------------------------------------------
# Frontend renderer: exact same typography and line-break semantics as Designer.
# ---------------------------------------------------------------------------
replace_exact(
    RENDERER,
    "            $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));\n            $headingHtml = $heading !== ''\n                ? '<' . $headingLevel . ' class=\"h18-clean-front-text-heading\" style=\"color:' . esc_attr($headingColor) . '\">' . esc_html($heading) . '</' . $headingLevel . '>'\n                : '';\n            $textStyle = $style . $borderStyle . $spacingStyle . $radiusStyle\n                . 'background:' . $background . ';padding:' . $padding . 'px;color:' . $textColor . ';text-align:' . (string) ($props['align'] ?? 'left') . ';';\n            return '<div id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-text\" style=\"' . esc_attr($textStyle) . '\">' . $headingHtml . wpautop(wp_kses_post((string) ($props['text'] ?? ''))) . '</div>';\n",
    "            $padding = max(0, min(120, (int) ($props['padding'] ?? 0)));\n            $bodyFamily = self::fontCss((string) ($props['fontFamily'] ?? 'system'));\n            $headingFamilyToken = (string) ($props['headingFontFamily'] ?? 'body');\n            $headingFamily = $headingFamilyToken === 'body' ? $bodyFamily : self::fontCss($headingFamilyToken);\n            $fontSize = max(8, min(120, (int) ($props['fontSize'] ?? 16)));\n            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 400)));\n            $lineHeight = max(0.8, min(3.0, (float) ($props['lineHeight'] ?? 1.5)));\n            $letterSpacing = max(-10.0, min(30.0, (float) ($props['letterSpacing'] ?? 0)));\n            $headingSize = max(0, min(160, (int) ($props['headingFontSize'] ?? 0)));\n            if ($headingSize === 0) { $headingSize = ['h2' => 32, 'h3' => 28, 'h4' => 24, 'h5' => 20, 'h6' => 18][$headingLevel] ?? 32; }\n            $headingWeight = max(100, min(900, (int) ($props['headingFontWeight'] ?? 700)));\n            $headingLineHeight = max(0.8, min(3.0, (float) ($props['headingLineHeight'] ?? 1.2)));\n            $headingLetterSpacing = max(-10.0, min(30.0, (float) ($props['headingLetterSpacing'] ?? 0)));\n            $headingHtml = $heading !== ''\n                ? '<' . $headingLevel . ' class=\"h18-clean-front-text-heading\" style=\"color:' . esc_attr($headingColor) . ';font-family:' . esc_attr($headingFamily) . ';font-size:' . esc_attr((string) $headingSize) . 'px;font-weight:' . esc_attr((string) $headingWeight) . ';line-height:' . esc_attr((string) $headingLineHeight) . ';letter-spacing:' . esc_attr((string) $headingLetterSpacing) . 'px\">' . esc_html($heading) . '</' . $headingLevel . '>'\n                : '';\n            $textStyle = $style . $borderStyle . $spacingStyle . $radiusStyle\n                . 'background:' . $background . ';padding:' . $padding . 'px;color:' . $textColor . ';text-align:' . (string) ($props['align'] ?? 'left') . ';font-family:' . $bodyFamily . ';font-size:' . $fontSize . 'px;font-weight:' . $fontWeight . ';line-height:' . $lineHeight . ';letter-spacing:' . $letterSpacing . 'px;';\n            $rawText = (string) ($props['text'] ?? '');\n            $bodyHtml = strpos($rawText, '<') === false ? nl2br(esc_html($rawText), false) : wp_kses_post($rawText);\n            return '<div id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-text\" style=\"' . esc_attr($textStyle) . '\">' . $headingHtml . $bodyHtml . '</div>';\n"
)
replace_exact(
    RENDERER,
    "    /** @param array<string,mixed> $props */\n    private static function borderStyle(array $props): string\n",
    "    private static function fontCss(string $token): string\n    {\n        return [\n            'arial' => 'Arial,sans-serif',\n            'verdana' => 'Verdana,sans-serif',\n            'tahoma' => 'Tahoma,sans-serif',\n            'trebuchet' => '\"Trebuchet MS\",sans-serif',\n            'georgia' => 'Georgia,serif',\n            'times' => '\"Times New Roman\",serif',\n            'courier' => '\"Courier New\",monospace',\n            'system' => 'system-ui,-apple-system,\"Segoe UI\",sans-serif',\n        ][$token] ?? 'system-ui,-apple-system,\"Segoe UI\",sans-serif';\n    }\n\n    /** @param array<string,mixed> $props */\n    private static function borderStyle(array $props): string\n"
)

# ---------------------------------------------------------------------------
# CSS: editor chrome must not change physical layout; Inspector scrolls itself.
# ---------------------------------------------------------------------------
with open(ROOT / UX_CSS, 'a', encoding='utf-8') as f:
    f.write("\n\n/* 0.1.26 WYSIWYG: editor labels are chrome, never layout geometry. */\n")
    f.write(".h18-clean-node-header{position:absolute!important;top:2px!important;left:2px!important;right:auto!important;z-index:72!important;height:23px!important;max-width:calc(100% - 4px);padding:0 5px!important;border:1px solid rgba(140,143,148,.65)!important;border-radius:4px!important;background:rgba(246,247,247,.94)!important;box-shadow:0 1px 2px rgba(0,0,0,.08);pointer-events:none}\n")
    f.write(".h18-clean-node-header .h18-clean-move{pointer-events:auto}\n")
    f.write(".h18-clean-node-preview--text,.h18-clean-node-preview--button,.h18-clean-node-preview--image{height:100%!important;min-height:0!important;padding:0!important}\n")
    f.write(".h18-clean-node-preview--image{height:100%!important}\n")
    f.write(".h18-clean-text-heading{margin:0 0 8px!important}\n")
    f.write(".h18-clean-text-body p{margin:0 0 1em}.h18-clean-text-body p:last-child{margin-bottom:0}.h18-clean-text-body ul,.h18-clean-text-body ol{margin:.5em 0 1em;padding-left:1.5em}\n")
    f.write(".h18-vd-typography{margin:12px 0;padding:10px;border:1px solid #dcdcde;border-radius:6px;background:#f9f9f9}.h18-vd-typography>strong{display:block;margin:4px 0 6px}.h18-vd-typography>strong:not(:first-child){margin-top:12px;padding-top:10px;border-top:1px solid #dcdcde}\n")
    f.write("@media(min-width:783px){.h18-clean-inspector{overflow-y:auto!important;overscroll-behavior:contain;scrollbar-gutter:stable;max-height:calc(100vh - 104px)!important}.h18-clean-inspector:not(.is-collapsed){min-height:0}}\n")

# Rich editor canonical paragraph/list appearance.
with open(ROOT / RICH_CSS, 'a', encoding='utf-8') as f:
    f.write("\n.h18-vd-rich-editor p{margin:0 0 1em}.h18-vd-rich-editor p:last-child{margin-bottom:0}.h18-vd-rich-editor ul,.h18-vd-rich-editor ol{margin:.5em 0 1em;padding-left:1.5em}\n")

print('0.1.26 deterministic patch complete')
