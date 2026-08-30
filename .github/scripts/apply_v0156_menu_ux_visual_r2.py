from pathlib import Path
import runpy

path = Path('.github/scripts/apply_v0156_menu_ux_visual.py')
text = path.read_text(encoding='utf-8')
old = "new, count = re.subn(pattern, replacement.rstrip() + '\\n', text, count=1, flags=re.S)"
new = "new, count = re.subn(pattern, lambda _match: replacement.rstrip() + '\\n', text, count=1, flags=re.S)"
if old not in text:
    raise SystemExit('0.1.56 replacement-engine anchor not found')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
runpy.run_path(str(path), run_name='__main__')
