from pathlib import Path

path = Path(__file__).resolve().parent / 'apply_v0125.py'
text = path.read_text(encoding='utf-8')

old = "text = replace_once(text, \"        } else if (node.type === 'image') {\\n\", button_card + \"        } else if (node.type === 'image') {\\n\", 'core button card')"
new = "text = replace_once(text, \"            wrap.appendChild(body);\\n        } else if (node.type === 'image') {\\n\", \"            wrap.appendChild(body);\\n\" + button_card + \"        } else if (node.type === 'image') {\\n\", 'core button card')"
if old not in text:
    raise RuntimeError('Expected ambiguous core button-card patch line was not found.')
text = text.replace(old, new, 1)

old_heading = "text = replace_once(text, \"({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE'}[node.type]\", \"({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP'}[node.type]\", 'core inspector heading')"
new_heading = "old_map = \"({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE'}[node.type]\"\nnew_map = \"({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP'}[node.type]\"\nif text.count(old_map) != 2:\n    raise RuntimeError(f'core type-label mappings: expected exactly 2 matches, found {text.count(old_map)}')\ntext = text.replace(old_map, new_map)"
if old_heading not in text:
    raise RuntimeError('Expected core inspector-heading patch line was not found.')
text = text.replace(old_heading, new_heading, 1)

path.write_text(text, encoding='utf-8')
print('0.1.25 patch targeting repaired.')
