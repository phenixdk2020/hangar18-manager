from pathlib import Path
p=Path('.github/scripts/patch_v0521.py')
t=p.read_text()
# The patch file itself contains literal quotes inside Python triple-quoted anchors.
needle='<template id="h18-page-section-template">\n"""'
actual='<template id="h18-page-section-template"><?php $this->render_page_editor_section_admin($page, $this->default_page_section(\'text\', 10), \'__INDEX__\', true); ?></template>\n"""'
if needle not in t:
    raise SystemExit('Component-data template patch-definition anchor missing')
t=t.replace(needle,actual)
p.write_text(t)
print('v0.5.21 patch anchors prepared')
