from pathlib import Path

p = Path('.github/scripts/v0180_composable_qa.py')
s = p.read_text(encoding='utf-8')

old = "req(header is not None and const is not None and header.group(1) == const.group(1) == '0.1.80', 'runtime version is exactly v0.1.80')"
new = "req(header is not None and const is not None and header.group(1) == const.group(1) and tuple(map(int, header.group(1).split('.'))) >= (0,1,80), 'runtime version is v0.1.80 or newer')"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('v0.1.80 runtime QA anchor not found')

old = "req(bool(versions) and str(versions[0].get('version','')) == '0.1.80', 'release history starts with v0.1.80')"
new = "req(any(isinstance(row, dict) and str(row.get('version','')) == '0.1.80' for row in versions), 'release history retains v0.1.80')"
if old in s:
    s = s.replace(old, new, 1)
elif new not in s:
    raise SystemExit('v0.1.80 history QA anchor not found')

old = "# Until central release runs, updater must remain on verified v0.1.79.\nreq(str(manifest.get('version','')) == '0.1.79', 'pre-release updater manifest remains on verified v0.1.79')\nreq((ROOT / 'dist/visual-designer-manager-v0.1.79.zip').is_file(), 'verified v0.1.79 ZIP remains present before release')"
new = "# Historical gate is forward-compatible: the updater must be at least the verified v0.1.80 release.\nreq(tuple(map(int, str(manifest.get('version','0.0.0')).split('.'))) >= (0,1,80), 'updater manifest is v0.1.80 or newer')\nreq((ROOT / 'dist/visual-designer-manager-v0.1.80.zip').is_file(), 'verified v0.1.80 ZIP remains present')"
if old in s:
    s = s.replace(old, new, 1)
elif "updater manifest is v0.1.80 or newer" not in s:
    raise SystemExit('v0.1.80 manifest QA anchor not found')

p.write_text(s, encoding='utf-8')
print('Made v0.1.80 historical QA forward-compatible for v0.1.81+.')
