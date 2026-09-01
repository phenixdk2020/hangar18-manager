from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REL = 'clean/hangar18-manager/src/Admin/EditorController.php'
path = ROOT / REL
value = path.read_text(encoding='utf-8')
old = "'reason' => 'canonical-model-shell-and-module-design-unchanged'"
new = "'reason' => 'canonical-model-and-shell-unchanged; module-design-unchanged'"
if new not in value:
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{REL}: expected one v0.1.77 no-op marker, found {count}')
    path.write_text(value.replace(old, new, 1), encoding='utf-8')
print('Preserved permanent v0.1.25 no-op regression marker.')
