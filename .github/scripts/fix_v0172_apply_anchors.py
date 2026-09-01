from pathlib import Path

path = Path(__file__).with_name('apply_v0172_gallery_design.py')
value = path.read_text(encoding='utf-8')
original = '''replace_once(CORE,
             "        } else if (node.type === 'image') {\\n            html += '<div class=\\\"h18-vd-menu-group\\\"><h3>Billede</h3>',",
             GALLERY_INSPECTOR + "\\n        } else if (node.type === 'image') {\\n            html += '<div class=\\\"h18-vd-menu-group\\\"><h3>Billede</h3>',")'''
intermediate = '''replace_once(CORE,
             "        } else if (node.type === 'image') {\\n            html += '<button type=\\\"button\\\" class=\\\"button\\\" id=\\\"h18-clean-pick-image\\\">Vælg / skift billede</button>',",
             GALLERY_INSPECTOR + "\\n        } else if (node.type === 'image') {\\n            html += '<button type=\\\"button\\\" class=\\\"button\\\" id=\\\"h18-clean-pick-image\\\">Vælg / skift billede</button>',")'''
final = '''replace_once(CORE,
             "        } else if (node.type === 'image') {\\n            html += '<button type=\\\"button\\\" class=\\\"button\\\" id=\\\"h18-clean-pick-image\\\">",
             GALLERY_INSPECTOR + "\\n        } else if (node.type === 'image') {\\n            html += '<button type=\\\"button\\\" class=\\\"button\\\" id=\\\"h18-clean-pick-image\\\">")'''
if final not in value:
    if intermediate in value:
        value = value.replace(intermediate, final, 1)
    elif original in value:
        value = value.replace(original, final, 1)
    else:
        raise SystemExit('v0.1.72 Gallery Inspector apply anchor not found')
path.write_text(value, encoding='utf-8')
print('v0.1.72 apply anchor fix: ready')
