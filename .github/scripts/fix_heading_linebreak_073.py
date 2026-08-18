from pathlib import Path
import re

php_path = Path('hangar18-manager.php')
js_path = Path('assets/admin.js')
css_path = Path('assets/admin.css')

php = php_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')

# 1) Remove the legacy save-note requirement. Keep the function/event hook so old code paths
# remain harmless, but it must always enforce OPTIONAL state.
legacy_required = re.compile(
    r"    function syncPageChangeNoteRequirement\(\) \{\n"
    r"        if \(!\$pageChangeNote\.length\) \{\n"
    r"            return;\n"
    r"        \}\n"
    r"        const required = !\$pageWhatIf\.is\(':checked'\);\n"
    r"        \$pageChangeNote\.prop\('required', required\)\.attr\('aria-required', required \? 'true' : 'false'\);\n"
    r"    \}"
)
matches = list(legacy_required.finditer(js))
if len(matches) != 1:
    raise SystemExit(f'legacy save-note requirement anchor count: {len(matches)}')
js = legacy_required.sub(
    "    function syncPageChangeNoteRequirement() {\n"
    "        if (!$pageChangeNote.length) { return; }\n"
    "        $pageChangeNote.prop('required', false).removeAttr('required').attr('aria-required', 'false').each(function () {\n"
    "            if (typeof this.setCustomValidity === 'function') { this.setCustomValidity(''); }\n"
    "        });\n"
    "    }",
    js,
    count=1,
)

# 2) Make the ordinary section heading explicitly optional in the UI.
old_label = "<?php echo $section['Type'] === 'poll' ? 'Spørgsmål' : 'Overskrift'; ?>"
new_label = "<?php echo $section['Type'] === 'poll' ? 'Spørgsmål' : 'Overskrift (valgfri)'; ?>"
if php.count(old_label) != 1:
    raise SystemExit(f'heading label anchor count: {php.count(old_label)}')
php = php.replace(old_label, new_label, 1)

old_title_input = "<input class=\"h18-section-title-input\" type=\"text\" name=\"<?php echo esc_attr($prefix); ?>[Title]\" value=\"<?php echo esc_attr($section['Title']); ?>\" />"
new_title_input = old_title_input + "\n                            <?php if ($section['Type'] !== 'poll') : ?><p class=\"description\">Valgfri. Lad feltet være tomt, hvis elementet kun skal vise tekst/indhold uden en overskrift.</p><?php endif; ?>"
if php.count(old_title_input) != 1:
    raise SystemExit(f'heading input anchor count: {php.count(old_title_input)}')
php = php.replace(old_title_input, new_title_input, 1)

# 3) Explain native newline behavior. Frontend already uses wpautop(); this makes the editor
# behavior discoverable and aligns the canvas with the rendered page.
old_help = "<p class=\"description h18-standard-content-help\">Almindelig tekst samt enkel formatering som fed, kursiv, links og lister er tilladt.</p>"
new_help = "<p class=\"description h18-standard-content-help\"><strong>Enter = linjeskift.</strong> En tom linje starter et nyt afsnit. Almindelig tekst samt enkel formatering som fed, kursiv, links og lister er tilladt.</p>"
if php.count(old_help) != 1:
    raise SystemExit(f'content help anchor count: {php.count(old_help)}')
php = php.replace(old_help, new_help, 1)

# 4) Canvas uses .html(raw textarea text); normal HTML whitespace collapses newlines.
# Preserve typed newlines visually without injecting <br> into stored content.
css_marker = "/* v0.7.3 – preserve natural textarea line breaks in canvas preview. */"
if css_marker not in css:
    css += "\n\n" + css_marker + "\n.h18-pages-admin .h18-canvas-preview-text{white-space:pre-line}\n"

# 5) Regression guard: normal section Title must not be HTML-required.
if re.search(r'class=\"h18-section-title-input\"[^>]*\brequired\b', php):
    raise SystemExit('ordinary section heading unexpectedly has required attribute')

php_path.write_text(php, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
