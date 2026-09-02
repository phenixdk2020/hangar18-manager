from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js'
s = p.read_text(encoding='utf-8')
old = "['h2', 'h3', 'h4', 'h5', 'h6'].includes"
new = "['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes"
count = s.count(old)
if count not in (0, 3):
    raise SystemExit(f'Unexpected H1 whitelist anchor count: {count}')
if count:
    s = s.replace(old, new)
    p.write_text(s, encoding='utf-8')
print(f'H1 whitelist pre-fix complete; replaced {count} anchors.')
