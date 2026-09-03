from pathlib import Path
import json
import re

root=Path('.')
plugin=(root/'clean/hangar18-manager/hangar18-manager.php').read_text(encoding='utf-8')
js=(root/'clean/hangar18-manager/assets/editor-v0181-color-picker.js').read_text(encoding='utf-8')
css=(root/'clean/hangar18-manager/assets/editor-v0181.css').read_text(encoding='utf-8')
notes=(root/'clean-release-notes.html').read_text(encoding='utf-8')
history=json.loads((root/'clean/hangar18-manager/release-history.json').read_text(encoding='utf-8'))
updater=json.loads((root/'clean-update.json').read_text(encoding='utf-8'))

def need(text, needle, label):
    if needle not in text:
        raise SystemExit(f'Missing {label}: {needle}')
    print(f'PASS: {label}')

need(plugin,'Version: 0.1.88','runtime version')
need(plugin,"define('VDM_VERSION', '0.1.88');",'VDM_VERSION')
if "wp_enqueue_style('wp-color-picker')" in plugin:
    raise SystemExit('WordPress color picker stylesheet is still enqueued')
if "'wp-color-picker'" in re.search(r"wp_enqueue_script\(\s*'h18-clean-editor-v0181-color-picker'.*?\);",plugin,re.S).group(0):
    raise SystemExit('Popup picker still depends on wp-color-picker')
print('PASS: WordPress/Iris picker retired from runtime dependency chain')

for needle,label in [
    ('const COLOR_SELECTOR = \'input[type="color"]\';','all color inputs selector'),
    ("input.type='hidden';",'native color input hidden'),
    ("panel.hidden=true",'popup hidden by default'),
    ("document.body.appendChild(picker.panel)",'popup only mounted on open'),
    ("themeToggle.textContent = picker.mode === 'theme' ? 'Farvevælger' : 'Tema';",'Tema/Farvevælger toggle label'),
    ("picker.colorView.hidden = picker.mode !== 'color';",'normal picker mode switch'),
    ("picker.themeView.hidden = picker.mode !== 'theme';",'theme mode switch'),
    ("cancel.textContent='Annuller'",'cancel action'),
    ("apply.textContent='Anvend'",'apply action'),
    ("themeTitle.textContent='Temafarver'",'theme palette'),
    ("recentTitle.textContent='Senest brugt'",'recent colors'),
    ("input.setAttribute('data-h18-vd-color-commit','1')",'canonical commit marker'),
    ("new MutationObserver",'dynamic Inspector coverage'),
    ("window.VDMColorPicker=api",'canonical picker refresh API'),
    ("event.key==='Escape'",'Escape cancels'),
    ("cancelPicker(openPicker)",'outside-click cancel path'),
]:
    need(js,needle,label)

if 'wpColorPicker' in js:
    raise SystemExit('Old WordPress/Iris picker call leaked into v0.1.88 JavaScript')
print('PASS: no wpColorPicker call in custom popup runtime')

for needle,label in [
    ('.vdm-color-panel{position:fixed','fixed popup geometry'),
    ('.vdm-color-panel[hidden]','hidden popup CSS'),
    ('.vdm-color-actions{display:flex','three-action footer'),
    ('.vdm-color-theme-toggle[aria-pressed="true"]','theme toggle active state'),
]:
    need(css,needle,label)

if not history.get('versions') or history['versions'][0].get('version')!='0.1.88':
    raise SystemExit('release-history.json is not headed by v0.1.88')
print('PASS: release history headed by v0.1.88')
need(notes,'data-version="0.1.88"','v0.1.88 release notes')
if not (root/'docs/v0188-status.md').is_file():
    raise SystemExit('v0.1.88 status document missing')
print('PASS: v0.1.88 status document')
if updater.get('version')!='0.1.87':
    raise SystemExit(f"Updater must remain 0.1.87 before release, got {updater.get('version')}")
print('PASS: updater remains v0.1.87 before release')

print('Visual Designer Manager v0.1.88 POPUP COLOR PICKER QA: PASS')
