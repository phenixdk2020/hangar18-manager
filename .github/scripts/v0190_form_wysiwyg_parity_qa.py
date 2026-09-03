from pathlib import Path
import json

ROOT = Path('.')

def text(path):
    p = ROOT / path
    if not p.is_file():
        raise SystemExit('Missing ' + path)
    return p.read_text(encoding='utf-8')

def req(condition, label):
    if not condition:
        raise SystemExit('FAIL: ' + label)
    print('PASS:', label)

plugin = text('clean/hangar18-manager/hangar18-manager.php')
editor = text('clean/hangar18-manager/assets/editor-v018-core.js')
css = text('clean/hangar18-manager/assets/editor-v0181.css')
forms = text('clean/hangar18-manager/src/Forms/FormService.php')
layout = text('clean/hangar18-manager/src/Model/LayoutModel.php')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
updater = json.loads(text('clean-update.json'))
notes = text('clean-release-notes.html')

req('Version: 0.1.90' in plugin and "define('VDM_VERSION', '0.1.90');" in plugin, 'runtime version is 0.1.90')
req('contactform: 76, membershipform: 87' in editor, 'new forms reserve canonical minimum rows')
req('.h18-vd-form-preview-field textarea{height:168px;min-height:168px;resize:none}' in css, 'Designer textarea is canonical 168px')
req('height:112px' not in css, 'old 112px Designer textarea geometry is gone')
req('.h18-vd-form textarea{height:168px;min-height:168px;resize:vertical}' in forms, 'frontend textarea is canonical 168px')
req('font:400 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif' in css, 'Designer controls use explicit canonical typography')
req('font:400 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif' in forms, 'frontend controls use same canonical typography')
req('.h18-vd-form-preview-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0;font-size:14px;font-weight:400;line-height:1.4' in css, 'Designer consent geometry contract')
req('.h18-vd-form-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0;font-size:14px;font-weight:400;line-height:1.4' in forms, 'frontend consent geometry matches Designer')
req('padding:11px 20px;font:700 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif' in css, 'Designer submit geometry contract')
req('padding:11px 20px;font:700 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif' in forms, 'frontend submit geometry matches Designer')
req("$formMinRows = $type === 'membershipform' ? 87 : 76;" in layout, 'existing form nodes receive minimum row normalization')
req("$currentRows > 0 && $currentRows < $formMinRows" in layout, 'normalizer only expands undersized explicit forms')
req('FORM-WYSIWYG-002' in layout, 'form parity migration marker present')
req(history.get('versions', [{}])[0].get('version') == '0.1.90', 'release history headed by 0.1.90')
req('data-version="0.1.90"' in notes, '0.1.90 release notes present')
req((ROOT / 'docs/v0190-status.md').is_file(), '0.1.90 status document present')
req(updater.get('version') == '0.1.89', 'updater remains 0.1.89 before release')

print('Visual Designer Manager v0.1.90 FORM WYSIWYG PARITY QA: PASS')
