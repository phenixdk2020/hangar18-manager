from pathlib import Path
import runpy

runpy.run_path('.github/scripts/fix_v0154_apply_anchors.py', run_name='__main__')
p = Path('.github/scripts/apply_v0154_menu_ux_publish.py')
s = p.read_text(encoding='utf-8')
old = "core = regex_once(core, menu_inspector_pattern, lambda m: menu_inspector_repl, 'menu inspector UX')"
new = '''menu_inspector_start = "        } else if (node.type === 'menu') {\\n            html += '<label>WordPress-menu<select data-field=\\\"menuId\\\">"
menu_inspector_end = "            html += '<p class=\\\"description\\\">Menuen henter sine punkter fra WordPress. Visual Designer gemmer kun valgt menu og designindstillinger.</p>';\\n"
menu_inspector_pos = core.find(menu_inspector_start)
menu_inspector_end_pos = core.find(menu_inspector_end, menu_inspector_pos)
if menu_inspector_pos < 0 or menu_inspector_end_pos < 0:
    raise SystemExit('menu inspector UX: source anchors not found')
menu_inspector_end_pos += len(menu_inspector_end)
core = core[:menu_inspector_pos] + menu_inspector_repl + core[menu_inspector_end_pos:]'''
if old not in s:
    raise SystemExit('menu inspector regex call not found')
p.write_text(s.replace(old, new, 1), encoding='utf-8')
print('0.1.54 Menu Inspector anchor repaired')
