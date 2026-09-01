from pathlib import Path

path = Path(__file__).with_name('apply_v0172_gallery_design.py')
value = path.read_text(encoding='utf-8')
old = '''replace_once(CORE,
             "        } else if (node.type === 'image') {\\n            html += '<div class=\\\"h18-vd-menu-group\\\"><h3>Billede</h3>',",
             GALLERY_INSPECTOR + "\\n        } else if (node.type === 'image') {\\n            html += '<div class=\\\"h18-vd-menu-group\\\"><h3>Billede</h3>',")'''
new = '''replace_once(CORE,
             "        } else if (node.type === 'image') {\\n            html += '<button type=\\\"button\\\" class=\\\"button\\\" id=\\\"h18-clean-pick-image\\\">Vælg / skift billede</button>',",
             GALLERY_INSPECTOR + "\\n        } else if (node.type === 'image') {\\n            html += '<button type=\\\"button\\\" class=\\\"button\\\" id=\\\"h18-clean-pick-image\\\">Vælg / skift billede</button>',")'''
if new not in value:
    if old not in value:
        raise SystemExit('v0.1.72 Gallery Inspector apply anchor not found')
    value = value.replace(old, new, 1)
path.write_text(value, encoding='utf-8')
print('v0.1.72 apply anchor fix: ready')
