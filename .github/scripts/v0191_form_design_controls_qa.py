from pathlib import Path

ROOT = Path('.')
plugin = (ROOT/'clean/hangar18-manager/hangar18-manager.php').read_text(encoding='utf-8')
model = (ROOT/'clean/hangar18-manager/src/Model/LayoutModel.php').read_text(encoding='utf-8')
form = (ROOT/'clean/hangar18-manager/src/Forms/FormService.php').read_text(encoding='utf-8')
editor = (ROOT/'clean/hangar18-manager/assets/editor-v018-core.js').read_text(encoding='utf-8')
css = (ROOT/'clean/hangar18-manager/assets/editor-v0181.css').read_text(encoding='utf-8')

assert 'Version: 0.1.91' in plugin
for token in ['fieldGap','textareaHeight','consentMargin','buttonPaddingX','buttonPaddingY']:
    assert token in model, token
    assert token in editor, token
for token in ['--vdm-form-field-gap','--vdm-form-textarea-height','--vdm-form-consent-margin','--vdm-form-button-padding-x','--vdm-form-button-padding-y']:
    assert token in form, token
    assert token in css or token in editor, token
assert 'fitOverflowingForms' in editor
assert "['contactform','membershipform'].includes(node.type)" in editor
assert "formsChanged = fitOverflowingForms()" in editor
assert 'formFieldGap' in editor and 'formTextareaHeight' in editor and 'formConsentMargin' in editor
assert 'formButtonPaddingX' in editor and 'formButtonPaddingY' in editor
# Defaults must preserve v0.1.90 visible geometry.
assert "?? 16" in model and "?? 168" in model and "?? 18" in model
assert "?? 20" in model and "?? 11" in model
assert 'var(--vdm-form-textarea-height,168px)' in form
assert 'var(--vdm-form-textarea-height,168px)' in css
print('v0.1.91 form design controls QA: PASS')
