from pathlib import Path

path = Path('assets/admin.js')
text = path.read_text(encoding='utf-8')

old_a = "        const originalText = $button.text();\n        $button.prop('disabled', true).text('Opretter…');"
new_a = "        const originalHtml = $button.html();\n        $button.prop('disabled', true).text('Opretter…');"
if text.count(old_a) != 1:
    raise SystemExit(f'Expected one button loading-state match, found {text.count(old_a)}')
text = text.replace(old_a, new_a, 1)

old_b = "            $button.prop('disabled', false).text(originalText);"
new_b = "            $button.prop('disabled', false).html(originalHtml);"
if text.count(old_b) != 1:
    raise SystemExit(f'Expected one button restore-state match, found {text.count(old_b)}')
text = text.replace(old_b, new_b, 1)

path.write_text(text, encoding='utf-8')
