from pathlib import Path

path = Path(__file__).with_name('apply_v0172_gallery_design.py')
value = path.read_text(encoding='utf-8')

# Inspector anchor compatibility: the current image Inspector starts directly
# with the media button, not the older Billede group heading.
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

# GALLERY_RECORDS is a raw Python string. It must contain one PHP namespace
# separator, not two literal backslashes, otherwise hangar18-manager.php is
# generated with an invalid \\VisualDesignerManager namespace token.
old_ns = r"}, \\VisualDesignerManager\\Modules\\ModuleStore::listRecords('galleries'"
new_ns = r"}, \VisualDesignerManager\Modules\ModuleStore::listRecords('galleries'"
if new_ns not in value:
    if old_ns not in value:
        raise SystemExit('v0.1.72 Gallery ModuleStore namespace anchor not found')
    value = value.replace(old_ns, new_ns, 1)

path.write_text(value, encoding='utf-8')
print('v0.1.72 apply anchor/escaping fixes: ready')
