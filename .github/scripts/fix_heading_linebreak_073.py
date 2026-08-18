from pathlib import Path
import re

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
css_path = Path('assets/admin.css')

php = php_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

# 1) Neutralize the old WhatIf-driven save-note requirement.
old_required = """    function syncPageChangeNoteRequirement() {
        if (!$pageChangeNote.length) {
            return;
        }
        const required = !$pageWhatIf.is(':checked');
        $pageChangeNote.prop('required', required).attr('aria-required', required ? 'true' : 'false');
    }"""
new_optional = """    function syncPageChangeNoteRequirement() {
        if (!$pageChangeNote.length) { return; }
        $pageChangeNote.prop('required', false).removeAttr('required').attr('aria-required', 'false').each(function () {
            if (typeof this.setCustomValidity === 'function') { this.setCustomValidity(''); }
        });
    }"""
if old_required in js:
    if js.count(old_required) != 1:
        raise SystemExit('legacy save-note requirement is duplicated')
    js = js.replace(old_required, new_optional, 1)
elif new_optional not in js:
    raise SystemExit('save-note requirement anchor not found')

# 2) Ordinary headings are optional; poll question retains its semantic label.
old_label = "<?php echo $section['Type'] === 'poll' ? 'Spørgsmål' : 'Overskrift'; ?>"
new_label = "<?php echo $section['Type'] === 'poll' ? 'Spørgsmål' : 'Overskrift (valgfri)'; ?>"
if old_label in php:
    if php.count(old_label) != 1:
        raise SystemExit('heading label anchor duplicated')
    php = php.replace(old_label, new_label, 1)
elif new_label not in php:
    raise SystemExit('heading label anchor not found')

old_title_input = "<input class=\"h18-section-title-input\" type=\"text\" name=\"<?php echo esc_attr($prefix); ?>[Title]\" value=\"<?php echo esc_attr($section['Title']); ?>\" />"
optional_help = "<?php if ($section['Type'] !== 'poll') : ?><p class=\"description\">Valgfri. Lad feltet være tomt, hvis elementet kun skal vise tekst/indhold uden en overskrift.</p><?php endif; ?>"
if optional_help not in php:
    if php.count(old_title_input) != 1:
        raise SystemExit('heading input anchor not unique')
    php = php.replace(old_title_input, old_title_input + "\n                            " + optional_help, 1)

# 3) Make Enter/newline behavior explicit.
old_help = "<p class=\"description h18-standard-content-help\">Almindelig tekst samt enkel formatering som fed, kursiv, links og lister er tilladt.</p>"
new_help = "<p class=\"description h18-standard-content-help\"><strong>Enter = linjeskift.</strong> En tom linje starter et nyt afsnit. Almindelig tekst samt enkel formatering som fed, kursiv, links og lister er tilladt.</p>"
if old_help in php:
    if php.count(old_help) != 1:
        raise SystemExit('content help anchor duplicated')
    php = php.replace(old_help, new_help, 1)
elif new_help not in php:
    raise SystemExit('content help anchor not found')

# 4) Preserve raw textarea newlines visually in the canvas. Stored content remains unchanged;
# frontend still runs the content through wpautop().
css_marker = "/* v0.7.3 – preserve natural textarea line breaks in canvas preview. */"
css_rule = ".h18-pages-admin .h18-canvas-preview-text{white-space:pre-line}"
if css_marker not in css:
    css += "\n\n" + css_marker + "\n" + css_rule + "\n"
elif css_rule not in css:
    raise SystemExit('newline marker exists without CSS rule')

if re.search(r'class=\"h18-section-title-input\"[^>]*\brequired\b', php):
    raise SystemExit('ordinary section heading unexpectedly has required attribute')
if "const required = !$pageWhatIf.is(':checked');" in js:
    raise SystemExit('legacy save-note required toggle still present')

php_path.write_text(php, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
