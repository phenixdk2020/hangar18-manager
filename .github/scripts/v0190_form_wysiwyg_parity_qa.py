from pathlib import Path
import json
import re

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


def version_tuple(value):
    parts = [int(p) for p in re.findall(r'\d+', str(value))[:3]]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


plugin = text('clean/hangar18-manager/hangar18-manager.php')
editor = text('clean/hangar18-manager/assets/editor-v018-core.js')
css = text('clean/hangar18-manager/assets/editor-v0181.css')
forms = text('clean/hangar18-manager/src/Forms/FormService.php')
layout = text('clean/hangar18-manager/src/Model/LayoutModel.php')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
updater = json.loads(text('clean-update.json'))
notes = text('clean-release-notes.html')

m = re.search(r"define\('VDM_VERSION',\s*'([^']+)'\);", plugin)
req(bool(m) and version_tuple(m.group(1)) >= (0, 1, 90), 'runtime version is >= 0.1.90')
req('contactform: 76, membershipform: 87' in editor, 'new forms reserve canonical minimum rows')

# v0.1.90 used literal geometry. Newer versions may expose the same defaults
# through canonical CSS variables while retaining 168/18/20/11 as fallbacks.
preview_textarea = (
    '.h18-vd-form-preview-field textarea{height:168px;min-height:168px;resize:none}' in css
    or 'var(--vdm-form-textarea-height,168px)' in css
)
front_textarea = (
    '.h18-vd-form textarea{height:168px;min-height:168px;resize:vertical}' in forms
    or 'var(--vdm-form-textarea-height,168px)' in forms
)
req(preview_textarea, 'Designer textarea preserves canonical 168px default')
req('height:112px' not in css, 'old 112px Designer textarea geometry is gone')
req(front_textarea, 'frontend textarea preserves canonical 168px default')
req('font:400 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif' in css, 'Designer controls use explicit canonical typography')
req('font:400 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif' in forms, 'frontend controls use same canonical typography')

preview_consent = (
    '.h18-vd-form-preview-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0;font-size:14px;font-weight:400;line-height:1.4' in css
    or 'margin:var(--vdm-form-consent-margin,18px) 0' in css
)
front_consent = (
    '.h18-vd-form-consent{display:flex;gap:9px;align-items:flex-start;margin:18px 0;font-size:14px;font-weight:400;line-height:1.4' in forms
    or 'margin:var(--vdm-form-consent-margin,18px) 0' in forms
)
req(preview_consent, 'Designer consent preserves canonical 18px default')
req(front_consent, 'frontend consent preserves same canonical default')

preview_submit = (
    'padding:11px 20px;font:700 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif' in css
    or 'padding:var(--vdm-form-button-padding-y,11px) var(--vdm-form-button-padding-x,20px)' in css
)
front_submit = (
    'padding:11px 20px;font:700 16px/1.35 system-ui,-apple-system,"Segoe UI",sans-serif' in forms
    or 'padding:var(--vdm-form-button-padding-y,11px) var(--vdm-form-button-padding-x,20px)' in forms
)
req(preview_submit, 'Designer submit preserves canonical 11/20px default')
req(front_submit, 'frontend submit preserves same canonical default')

req("$formMinRows = $type === 'membershipform' ? 87 : 76;" in layout, 'existing form nodes receive minimum row normalization')
req("$currentRows > 0 && $currentRows < $formMinRows" in layout, 'normalizer only expands undersized explicit forms')
req('FORM-WYSIWYG-002' in layout, 'form parity migration marker present')
req(any(str(row.get('version')) == '0.1.90' for row in history.get('versions', [])), '0.1.90 remains in release history')
req('data-version="0.1.90"' in notes, '0.1.90 release notes remain present')
req((ROOT / 'docs/v0190-status.md').is_file(), '0.1.90 status document present')
req(version_tuple(updater.get('version', '0')) >= (0, 1, 89), 'updater is not older than v0.1.89 baseline')

print('Visual Designer Manager v0.1.90 FORM WYSIWYG PARITY QA: PASS')
