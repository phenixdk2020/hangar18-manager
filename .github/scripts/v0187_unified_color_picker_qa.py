from pathlib import Path
import json
import re


def text(path: str) -> str:
    return Path(path).read_text(encoding='utf-8')


def req(ok: bool, label: str) -> None:
    if not ok:
        raise SystemExit('FAIL: ' + label)
    print('PASS:', label)

plugin = text('clean/hangar18-manager/hangar18-manager.php')
core = text('clean/hangar18-manager/assets/editor-v018-core.js')
picker = text('clean/hangar18-manager/assets/editor-v0181-color-picker.js')
legacy_picker = text('clean/hangar18-manager/assets/editor-v0135.js')
manifest = json.loads(text('clean-update.json'))
history = json.loads(text('clean/hangar18-manager/release-history.json'))
notes = text('clean-release-notes.html')
status = text('docs/v0187-status.md')

req('Version: 0.1.87' in plugin and "define('VDM_VERSION', '0.1.87');" in plugin, 'runtime version 0.1.87')
req("wp_enqueue_style('wp-color-picker');" in plugin, 'WordPress web color picker stylesheet is loaded')
req("'wp-color-picker'" in plugin and "assets/editor-v0181-color-picker.js" in plugin, 'unified picker depends on WordPress color picker')

# The historical v0.1.35 picker converted inputs before v0.1.81 could enhance them.
req("assets/editor-v0135.js" not in plugin, 'legacy v0.1.35 color picker JavaScript is retired from runtime')
req("assets/editor-v0135.css" not in plugin, 'legacy v0.1.35 color picker CSS is retired from runtime')
req("input.type = 'text';" in legacy_picker and "input.readOnly = true;" in legacy_picker, 'QA documents why legacy picker conflicts with unified picker')
req("'h18-clean-editor-v0144'" in plugin and "['h18-clean-editor-v0134']" in plugin, 'stylesheet dependency chain bypasses legacy color picker')
req("'h18-clean-editor-v0148-layers'" in plugin and "['h18-clean-editor-v0132']" in plugin, 'script dependency chain bypasses legacy color picker')

# One picker must own every color input on Designer/Global Designer pages.
req("const COLOR_SELECTOR = 'input[type=\"color\"]';" in picker, 'unified picker scans every color input on Designer pages')
req('scope.matches && scope.matches(COLOR_SELECTOR)' in picker, 'newly inserted color input root is enhanced')
req('scope.querySelectorAll(COLOR_SELECTOR).forEach(enhance);' in picker, 'newly inserted color input descendants are enhanced')
req('window.VDMColorPicker = api;' in picker, 'canonical VDM color picker refresh API is exposed')
req("window.H18VDColorPicker = api;" in picker, 'temporary compatibility API remains available')
req("window.VDMColorPicker && typeof window.VDMColorPicker.refresh === 'function'" in core, 'Inspector explicitly refreshes unified color picker after render')
req('window.VDMColorPicker.refresh(host);' in core, 'Inspector refresh targets newly rendered controls')

# User-facing functionality promised in v0.1.81 must remain intact.
for token, label in [
    ('Temafarver', 'theme color shortcuts'),
    ('Senest brugt', 'recent color shortcuts'),
    ('Annuller', 'cancel action'),
    ('Anvend', 'explicit apply action'),
    ('themePalette()', 'dynamic theme palette'),
    ('remember(value)', 'recent color persistence'),
    ("input.setAttribute('data-h18-vd-color-commit', '1')", 'explicit commit marker'),
]:
    req(token in picker, label)

# Ensure the active core contains the reported fields and that they remain real color controls.
for field in ['background', 'textColor', 'headingColor', 'borderColor']:
    pattern = rf'data-field=\\?"{re.escape(field)}\\?" type=\\?"color\\?"'
    req(re.search(pattern, core) is not None, f'{field} is rendered as a color control')

color_inputs = len(re.findall(r'type=\\?"color\\?"', core))
req(color_inputs >= 20, f'active core exposes expected color controls ({color_inputs})')
req("querySelectorAll('input[type=\"color\"][data-field]" not in picker, 'unified picker is no longer limited to data-field controls')

versions = [str(row.get('version')) for row in history.get('versions', []) if isinstance(row, dict)]
req('0.1.87' in versions, 'release history includes v0.1.87 candidate')
req('data-version="0.1.87"' in notes and 'farvevælger' in notes.lower(), 'release notes document unified color picker')
req('v0.1.87' in status and 'farve' in status.lower(), 'v0.1.87 status document exists')
req(str(manifest.get('version')) == '0.1.86', 'central updater remains v0.1.86 before release')

print('Visual Designer Manager v0.1.87 UNIFIED COLOR PICKER QA: PASS')
