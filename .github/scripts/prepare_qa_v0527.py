from pathlib import Path
p=Path('.github/scripts/qa_v0527.py')
t=p.read_text()
old='''# Editor must never hide/remove the actual editable row; it only applies preview class/badge.\nif ".remove()" in js[js.index('function evaluateConditionPreviewV0527'):js.index("$(document).on('click','.h18-condition-add'",js.index('function evaluateConditionPreviewV0527'))]:\n    raise SystemExit('Condition preview removes editor DOM')\n'''
new='''# Editor must never remove the actual editable row/preview; removing the old badge is expected.\npreview=js[js.index('function evaluateConditionPreviewV0527'):js.index("$(document).on('click','.h18-condition-add'",js.index('function evaluateConditionPreviewV0527'))]\nfor forbidden in ['$row.remove(', '$preview.remove(', ".closest('.h18-page-section-row').remove("]:\n    if forbidden in preview: raise SystemExit('Condition preview removes editor DOM: '+forbidden)\nif ".h18-condition-preview-badge').remove()" not in preview:\n    raise SystemExit('Condition preview does not clean up stale badge')\n'''
if old not in t:
    raise SystemExit('QA editor DOM assertion anchor missing')
p.write_text(t.replace(old,new,1))
print('v0.5.27 QA DOM assertion refined')
