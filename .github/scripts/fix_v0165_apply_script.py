from pathlib import Path

# Rerun trigger after making the v0.1.64 clipboard QA forward-compatible.
p = Path('.github/scripts/apply_v0165_general_elements.py')
s = p.read_text(encoding='utf-8')

old_preview = '''insert_before_once(editor, "        } else if (node.type === 'image') {\\n", preview_branches, "node.type === 'datalist'")'''
new_preview = '''insert_before_once(editor, "        } else if (node.type === 'image') {\\n            wrap.classList.add('h18-clean-node-preview--image');\\n", preview_branches, "node.type === 'datalist'")'''
if old_preview in s:
    s = s.replace(old_preview, new_preview, 1)
elif new_preview not in s:
    raise SystemExit('preview insertion call not found')

old_inspector = '''insert_before_once(editor, "        } else if (node.type === 'image') {\\n", inspector_branches, "Statisk Tabel · test")'''
new_inspector = '''insert_before_once(editor, "        } else if (node.type === 'image') {\\n            html += '<button type=\\"button\\" class=\\"button\\" id=\\"h18-clean-pick-image\\">Vælg / skift billede</button><p class=\\"description\\">PNG, JPG/JPEG, WebP, GIF og andre image/*-formater som WordPress tillader. PNG-transparens bevares.</p>';\\n", inspector_branches, "Statisk Tabel · test")'''
if old_inspector in s:
    s = s.replace(old_inspector, new_inspector, 1)
elif new_inspector not in s:
    raise SystemExit('inspector insertion call not found')

old_border = "cellBorderWidth: clamp(parseInt(raw.cellBorderWidth || 1, 10) || 0, 0, 10),"
new_border = "cellBorderWidth: clamp(parseInt(raw.cellBorderWidth != null ? raw.cellBorderWidth : 1, 10) || 0, 0, 10),"
if old_border in s:
    s = s.replace(old_border, new_border, 1)
elif new_border not in s:
    raise SystemExit('table border normalization anchor not found')

p.write_text(s, encoding='utf-8')
print('Hardened v0.1.65 apply script')
