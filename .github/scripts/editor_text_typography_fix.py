from pathlib import Path

branch_marker = 'v0.6.2 – rich-text toggle og tydelig typografi-fane'

# --- PHP: add Typography inspector tab ---
php_path = Path('hangar18-manager.php')
php = php_path.read_text(encoding='utf-8')
old_tabs = '''                            <div class="h18-inspector-tabs" role="tablist" aria-label="Elementindstillinger">
                                <button type="button" class="h18-inspector-tab is-active" data-inspector-tab="content">Indhold</button>
                                <button type="button" class="h18-inspector-tab" data-inspector-tab="design">Design</button>
                                <button type="button" class="h18-inspector-tab" data-inspector-tab="advanced">Avanceret</button>
                            </div>'''
new_tabs = '''                            <div class="h18-inspector-tabs" role="tablist" aria-label="Elementindstillinger">
                                <button type="button" class="h18-inspector-tab is-active" data-inspector-tab="content">Indhold</button>
                                <button type="button" class="h18-inspector-tab" data-inspector-tab="typography">Typografi</button>
                                <button type="button" class="h18-inspector-tab" data-inspector-tab="design">Design</button>
                                <button type="button" class="h18-inspector-tab" data-inspector-tab="advanced">Avanceret</button>
                            </div>'''
if php.count(old_tabs) != 1:
    raise SystemExit(f'Expected exactly one inspector tab block, found {php.count(old_tabs)}')
php = php.replace(old_tabs, new_tabs, 1)
php_path.write_text(php, encoding='utf-8')

# --- JS: replace mini-format source wrapper with true toggle behavior ---
js_path = Path('assets/admin.js')
js = js_path.read_text(encoding='utf-8')
start_marker = "    $(document).on('click', '.h18-mini-format', function (event) {"
end_marker = "\n\n    $('.h18-preview-device').on('click'"
start = js.find(start_marker)
if start < 0:
    raise SystemExit('mini-format handler start not found')
end = js.find(end_marker, start)
if end < 0:
    raise SystemExit('mini-format handler end not found')

new_handler = r'''    function h18MiniEditorToggleTag(textarea, tagName, placeholder) {
        const openTag = '<' + tagName + '>';
        const closeTag = '</' + tagName + '>';
        const value = String(textarea.value || '');
        let start = Number.isInteger(textarea.selectionStart) ? textarea.selectionStart : 0;
        let end = Number.isInteger(textarea.selectionEnd) ? textarea.selectionEnd : start;
        let selected = value.slice(start, end);
        const lowerValue = value.toLowerCase();
        const lowerOpen = openTag.toLowerCase();
        const lowerClose = closeTag.toLowerCase();

        // Selection includes the complete wrapper: unwrap instead of nesting.
        if (selected.toLowerCase().startsWith(lowerOpen) && selected.toLowerCase().endsWith(lowerClose)) {
            const inner = selected.slice(openTag.length, selected.length - closeTag.length);
            textarea.setRangeText(inner, start, end, 'select');
            textarea.setSelectionRange(start, start + inner.length);
            return;
        }

        // Selection is exactly surrounded by the requested wrapper.
        const immediateOpenStart = start - openTag.length;
        const immediateCloseEnd = end + closeTag.length;
        if (immediateOpenStart >= 0 &&
            lowerValue.slice(immediateOpenStart, start) === lowerOpen &&
            lowerValue.slice(end, immediateCloseEnd) === lowerClose) {
            textarea.setRangeText(selected, immediateOpenStart, immediateCloseEnd, 'select');
            textarea.setSelectionRange(immediateOpenStart, immediateOpenStart + selected.length);
            return;
        }

        // Selection is a subsection inside one bold/italic span. Split the span so
        // only the selected text is toggled off, preserving formatting either side.
        const openPos = lowerValue.lastIndexOf(lowerOpen, start);
        const previousClose = lowerValue.lastIndexOf(lowerClose, start);
        const closePos = lowerValue.indexOf(lowerClose, end);
        const nextOpen = lowerValue.indexOf(lowerOpen, end);
        const insideSameSpan = openPos >= 0 && openPos > previousClose && closePos >= end && (nextOpen < 0 || closePos < nextOpen);
        if (insideSameSpan) {
            const left = value.slice(openPos + openTag.length, start);
            const middle = value.slice(start, end);
            const right = value.slice(end, closePos);
            let replacement = '';
            if (left) { replacement += openTag + left + closeTag; }
            const middleStart = openPos + replacement.length;
            replacement += middle;
            if (right) { replacement += openTag + right + closeTag; }
            textarea.setRangeText(replacement, openPos, closePos + closeTag.length, 'select');
            textarea.setSelectionRange(middleStart, middleStart + middle.length);
            return;
        }

        if (!selected) {
            selected = placeholder;
            const replacement = openTag + selected + closeTag;
            textarea.setRangeText(replacement, start, end, 'select');
            textarea.setSelectionRange(start + openTag.length, start + openTag.length + selected.length);
            return;
        }

        // Avoid same-tag nesting if the marked selection already contains wrappers.
        const sameTagPattern = new RegExp('</?' + tagName + '>', 'gi');
        selected = selected.replace(sameTagPattern, '');
        const replacement = openTag + selected + closeTag;
        textarea.setRangeText(replacement, start, end, 'select');
        textarea.setSelectionRange(start + openTag.length, start + openTag.length + selected.length);
    }

    $(document).on('click', '.h18-mini-format', function (event) {
        event.preventDefault();
        const textarea = $(this).closest('.h18-page-section-content').find('textarea').get(0);
        if (!textarea) { return; }

        const format = String($(this).data('format') || '');
        const start = Number.isInteger(textarea.selectionStart) ? textarea.selectionStart : 0;
        const end = Number.isInteger(textarea.selectionEnd) ? textarea.selectionEnd : start;
        const selected = textarea.value.slice(start, end);

        if (format === 'bold') {
            h18MiniEditorToggleTag(textarea, 'strong', 'fed tekst');
        } else if (format === 'italic') {
            h18MiniEditorToggleTag(textarea, 'em', 'kursiv tekst');
        } else if (format === 'link') {
            const url = window.prompt('Indtast linkadresse', 'https://');
            if (!url) { return; }
            const label = selected || 'linktekst';
            const replacement = '<a href="' + String(url).replace(/"/g, '&quot;') + '">' + label + '</a>';
            textarea.setRangeText(replacement, start, end, 'select');
            textarea.setSelectionRange(start + replacement.indexOf(label), start + replacement.indexOf(label) + label.length);
        } else if (format === 'list') {
            const source = selected || 'Punkt 1\nPunkt 2';
            const lines = source.split(/\r?\n/).map(function (line) { return line.trim(); }).filter(Boolean);
            const replacement = '<ul>\n' + lines.map(function (line) { return '<li>' + line.replace(/^<li>|<\/li>$/gi, '') + '</li>'; }).join('\n') + '\n</ul>';
            textarea.setRangeText(replacement, start, end, 'select');
        } else {
            return;
        }

        $(textarea).trigger('input');
        textarea.focus();
    });'''
js = js[:start] + new_handler + js[end:]

# JS: add typography as real inspector panel and force layout details open for Design/Typography.
set_start = js.find('    function setInspectorPanel(panel) {')
set_end = js.find('\n\n    function refreshInspectorMeta', set_start)
if set_start < 0 or set_end < 0:
    raise SystemExit('setInspectorPanel block not found')
new_set_panel = r'''    function setInspectorPanel(panel) {
        panel = ['content', 'typography', 'design', 'advanced'].includes(String(panel)) ? String(panel) : 'content';
        currentInspectorPanel = panel;
        $pageInspector.attr('data-inspector-panel', panel);
        $pageInspector.find('.h18-inspector-tab').removeClass('is-active').filter('[data-inspector-tab="' + panel + '"]').addClass('is-active');
        if (panel === 'typography' || panel === 'design') {
            $pageInspectorTarget.find('.h18-page-section-layout').prop('open', true);
        }
    }'''
js = js[:set_start] + new_set_panel + js[set_end:]
js_path.write_text(js, encoding='utf-8')

# --- CSS: isolate Typography from Design and keep all panels in normal flow ---
css_path = Path('assets/admin.css')
css = css_path.read_text(encoding='utf-8').rstrip()
if branch_marker in css:
    raise SystemExit('editor typography fix already applied')
css_patch = r'''

/* v0.6.2 – rich-text toggle og tydelig typografi-fane */
.h18-pages-admin .h18-inspector-tabs{grid-template-columns:repeat(2,minmax(0,1fr))}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>*{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout{display:block!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout>summary{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target>.h18-page-section-body>.h18-page-section-layout>*:not(.h18-element-typography-box):not(summary){display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] #h18-page-inspector-target .h18-element-typography-box{display:block!important;margin:0;padding:0;border-top:0}
.h18-builder-inspector[data-inspector-panel="design"] #h18-page-inspector-target .h18-element-typography-box{display:none!important}
.h18-builder-inspector[data-inspector-panel="typography"] .h18-module-fields-grid--four{grid-template-columns:1fr 1fr}
.h18-builder-inspector[data-inspector-panel="typography"] .h18-field{min-width:0}
@media(max-width:1180px){
    .h18-pages-admin .h18-inspector-tabs{grid-template-columns:repeat(4,minmax(0,1fr))}
}
@media(max-width:782px){
    .h18-pages-admin .h18-inspector-tabs{grid-template-columns:repeat(2,minmax(0,1fr))}
    .h18-builder-inspector[data-inspector-panel="typography"] .h18-module-fields-grid--four{grid-template-columns:1fr}
}
'''
css_path.write_text(css + css_patch.rstrip() + '\n', encoding='utf-8')

print('Editor text/typography fixes applied')
