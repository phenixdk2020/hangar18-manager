from pathlib import Path
import runpy

runpy.run_path('.github/scripts/fix_v0154_apply_anchors_r4.py', run_name='__main__')
p = Path('.github/scripts/apply_v0154_menu_ux_publish.py')
s = p.read_text(encoding='utf-8')
old = "'reason' => 'canonical-model-shell-and-status-unchanged'"
new = "'reason' => 'canonical-model-and-shell-unchanged'"
if s.count(old) != 1:
    raise SystemExit(f'no-op reason anchor expected once, found {s.count(old)}')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
print('0.1.54 preserved canonical no-op diagnostic marker')
