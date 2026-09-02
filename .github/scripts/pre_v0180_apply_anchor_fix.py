from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
p = ROOT / '.github/scripts/apply_v0180_composable.py'
s = p.read_text(encoding='utf-8')

helper = r'''

def insert_before_nth(rel: str, anchor: str, payload: str, marker: str, occurrence: int) -> None:
    value = read(rel)
    if marker in value:
        return
    positions = []
    start = 0
    while True:
        pos = value.find(anchor, start)
        if pos < 0:
            break
        positions.append(pos)
        start = pos + len(anchor)
    if occurrence < 1 or occurrence > len(positions):
        raise SystemExit(f'{rel}: insertion anchor occurrence {occurrence} missing; found {len(positions)}: {anchor[:180]!r}')
    pos = positions[occurrence - 1]
    write(rel, value[:pos] + payload + value[pos:])
'''

if 'def insert_before_nth(' not in s:
    marker = '\n\n# Runtime version.'
    if marker not in s:
        raise SystemExit('Runtime-version marker not found in apply script')
    s = s.replace(marker, helper + marker, 1)

old_preview = 'insert_before(p, "        } else if (node.type === \'eventfield\') {", EVENT_JS_PREVIEW, "node.type === \'eventvalue\'")'
new_preview = 'insert_before_nth(p, "        } else if (node.type === \'eventfield\') {", EVENT_JS_PREVIEW, "node.type === \'eventvalue\'", 1)'
old_inspector = 'insert_before(p, "        } else if (node.type === \'eventfield\') {", EVENT_JS_INSPECTOR, "<h3>Eventværdi</h3>")'
new_inspector = 'insert_before_nth(p, "        } else if (node.type === \'eventfield\') {", EVENT_JS_INSPECTOR, "<h3>Eventværdi</h3>", 2)'

if old_preview in s:
    s = s.replace(old_preview, new_preview, 1)
elif new_preview not in s:
    raise SystemExit('Preview insert call not found in apply script')

if old_inspector in s:
    s = s.replace(old_inspector, new_inspector, 1)
elif new_inspector not in s:
    raise SystemExit('Inspector insert call not found in apply script')

p.write_text(s, encoding='utf-8')
print('v0.1.80 apply script anchors disambiguated: preview=1, inspector=2.')
