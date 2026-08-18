from pathlib import Path
p=Path('.github/scripts/patch_v0529.py')
t=p.read_text()
old="<?php foreach ($selected['Fields'] as $field) :\n"
new="<?php foreach ($selected['Fields'] as $field) : $value = $entry ? ($entry_values[$field['Key']] ?? '') : ''; ?>\n"
count=t.count(old)
if count != 2:
    raise SystemExit(f'entry-tag patch-definition anchors: expected 2, found {count}')
t=t.replace(old,new)
p.write_text(t)
print('v0.5.29 entry tag UI anchor prepared')
