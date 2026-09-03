from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def text(rel):
    p = ROOT / rel
    if not p.is_file():
        raise SystemExit('FAIL missing ' + rel)
    return p.read_text(encoding='utf-8')


def req(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)
    print('PASS:', message)


plugin = text('clean/hangar18-manager/hangar18-manager.php')
admin_js = text('clean/hangar18-manager/assets/admin-v0123.js')
editor = text('clean/hangar18-manager/assets/editor-v018-core.js')
color_js = text('clean/hangar18-manager/assets/editor-v0181-color-picker.js')
color_css = text('clean/hangar18-manager/assets/editor-v0181.css')
forms = text('clean/hangar18-manager/src/Forms/FormService.php')
user_manual = text('CLEAN-USER-MANUAL.md')
design_manual = text('CLEAN-DESIGN-MANUAL.md')
plan = text('docs/v0181-plan.md')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
manifest = json.loads(text('clean-update.json'))

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
req(header is not None and const is not None and header.group(1) == const.group(1) and tuple(map(int, header.group(1).split('.'))) >= (0, 1, 81), 'runtime version is v0.1.81 or newer')

req("'h18-clean-pages': ['Klar', 'ready']" in admin_js, 'Sider status is Klar')
req("'h18-clean-event-fields': ['Klar', 'ready']" in admin_js, 'Eventfelter status is Klar')

req("'themePalette' => $themePalette" in plugin, 'Designer receives dynamic theme palette')
req("wp_get_global_settings(['color', 'palette', $origin])" in plugin, 'theme.json/global palette is collected dynamically')
req("get_theme_mods()" in plugin, 'active theme mods can contribute palette colors')

# Forward-compatible color-picker contract.
# v0.1.81 originally used WordPress/Iris. v0.1.88 intentionally restores the
# compact VDM popup while preserving the same canonical color/theme/recent
# behavior and broad dynamic input coverage.
req("editor-v0181-color-picker.js" in plugin and "editor-v0181.css" in plugin, 'shared color picker assets are enqueued')
wordpress_picker = "wpColorPicker" in color_js and "input.type = 'text'" in color_js
vdm_popup_picker = "window.VDMColorPicker=api" in color_js and "input.type='hidden'" in color_js and "vdm-color-panel" in color_css
req(wordpress_picker or vdm_popup_picker, 'native color input is replaced by a web-based Designer picker')
req("themePalette" in color_js and ("hexInput" in color_js or "HEX-koden" in color_js), 'picker exposes theme shortcuts and free HEX entry')
req("RECENT_KEY" in color_js and "Senest brugt" in color_js, 'picker stores and shows recent colors')
req("data-h18-vd-color-managed" in editor and "data-h18-vd-color-commit" in editor, 'core commits picker values only through explicit picker Apply path')
req(
    ("h18-vd-color-shortcut" in color_css and "wp-picker-input-wrap" in color_css)
    or ("vdm-color-panel" in color_css and "vdm-color-chip" in color_css and "vdm-color-actions" in color_css),
    'unified picker has Visual Designer styling'
)

# Form preview parity.
req("document.createElement('input')" in editor and "document.createElement('textarea')" in editor, 'Designer form preview uses real input/textarea controls')
req("h18-vd-form-preview-field" in editor and "h18-vd-form-preview-consent" in editor and "h18-vd-form-preview-submit" in editor, 'Designer form preview includes fields, consent and submit button')
req("membership || node.props.showPhone !== false" in editor, 'Kontakt preview respects showPhone while membership keeps phone')
req("addField('Kommentar', 'textarea', true)" in editor and "addField('Besked *', 'textarea', true)" in editor, 'membership/contact wide textarea structure is represented')
req("fields.forEach(function(label){const f=document.createElement('span')" not in editor, 'legacy simplified form label-box mockup is removed')

# v0.1.81 established 2-column/16px parity. Newer versions may expose the
# 16px value as a canonical CSS variable while retaining 16px as the fallback.
designer_grid = (
    "grid-template-columns:repeat(2,minmax(0,1fr));gap:16px" in color_css
    or "grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--vdm-form-field-gap,16px)" in color_css
)
frontend_grid = (
    "grid-template-columns:repeat(2,minmax(0,1fr));gap:16px" in forms
    or "grid-template-columns:repeat(2,minmax(0,1fr));gap:var(--vdm-form-field-gap,16px)" in forms
)
req(designer_grid, 'Designer form grid preserves 2-column 16px default contract')
req(frontend_grid, 'frontend form preserves matching 2-column 16px default contract')
req("@media(max-width:782px)" in color_css and "@media(max-width:782px)" in forms, 'Designer and frontend both switch forms at mobile breakpoint')

for asset in ['v0181-designer-overview.svg', 'v0181-color-picker.svg', 'v0181-form-wysiwyg.svg']:
    req((ROOT / 'docs/user-manual-assets' / asset).is_file(), 'manual graphic exists: ' + asset)
req('## Visual Designer v0.1.81 – sådan arbejder du visuelt' in user_manual, 'user manual contains v0.1.81 visual workflow section')
req('| Element | Hvad bruges det til?' in user_manual, 'user manual contains element purpose table')
req('v0181-form-wysiwyg.svg' in user_manual and 'v0181-color-picker.svg' in user_manual, 'user manual embeds form and color illustrations')
req('## v0.1.81 – visuelle Designer-regler' in design_manual, 'design manual contains v0.1.81 design rules')
req('Paritetskontrakt' in design_manual and 'Canonical værdi' in design_manual, 'design manual documents form parity and canonical color contract')
req('FORM-WYSIWYG-001' in plan and 'DOC-VISUAL-001' in plan, 'v0.1.81 plan records form parity and visual docs scope')

versions = history.get('versions', []) if isinstance(history, dict) else []
req(any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.81' for row in versions), 'release history contains v0.1.81 candidate')
req((ROOT / 'docs/v0181-status.md').is_file(), 'v0.1.81 status document exists')

# Historical gate: v0.1.81 is now a verified published baseline.
req(tuple(map(int, str(manifest.get('version', '0.0.0')).split('.'))) >= (0, 1, 81), 'updater manifest is v0.1.81 or newer')
req((ROOT / 'dist/visual-designer-manager-v0.1.81.zip').is_file(), 'verified v0.1.81 ZIP remains present')

print('Visual Designer Manager v0.1.81 complete QA: PASS')
