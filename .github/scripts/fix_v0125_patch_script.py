from pathlib import Path

path = Path(__file__).resolve().parent / 'apply_v0125.py'
text = path.read_text(encoding='utf-8')
old = "text = replace_once(text, \"        } else if (node.type === 'image') {\\n\", button_card + \"        } else if (node.type === 'image') {\\n\", 'core button card')"
new = "text = replace_once(text, \"            wrap.appendChild(body);\\n        } else if (node.type === 'image') {\\n\", \"            wrap.appendChild(body);\\n\" + button_card + \"        } else if (node.type === 'image') {\\n\", 'core button card')"
if old not in text:
    raise RuntimeError('Expected ambiguous core button-card patch line was not found.')
path.write_text(text.replace(old, new, 1), encoding='utf-8')
print('0.1.25 patch targeting repaired.')
