from pathlib import Path
import runpy

runpy.run_path('.github/scripts/fix_v0154_apply_anchors_r2.py', run_name='__main__')
p = Path('.github/scripts/apply_v0154_menu_ux_publish.py')
s = p.read_text(encoding='utf-8')
label1 = s.find("'standalone menu behavior'")
label2 = s.find("'frontend menu behavior'", label1 + 1)
if label1 < 0 or label2 < 0:
    raise SystemExit('renderer behavior labels not found')
start = s.rfind('renderer = regex_once(', 0, label1)
end = s.find('\n)', label2)
if start < 0 or end < 0:
    raise SystemExit('renderer behavior labelled block bounds not found')
end += 2
replacement = '''standalone_old = """            . '<script>document.addEventListener("click",function(e){var b=e.target.closest(".h18-clean-front-menu-toggle");if(!b)return;var n=b.closest(".h18-clean-front-menu");if(!n)return;var open=!n.classList.contains("is-open");n.classList.toggle("is-open",open);b.setAttribute("aria-expanded",open?"true":"false");});</script></body></html>';"""
standalone_new = "            . '<script>" + behavior.replace("'", "\\\\'") + "</script></body></html>';"
renderer = replace_once(renderer, standalone_old, standalone_new, 'standalone menu behavior')
frontend_old = """        echo '<script id="h18-clean-menu-js">document.addEventListener("click",function(e){var b=e.target.closest(".h18-clean-front-menu-toggle");if(!b)return;var n=b.closest(".h18-clean-front-menu");if(!n)return;var open=!n.classList.contains("is-open");n.classList.toggle("is-open",open);b.setAttribute("aria-expanded",open?"true":"false");});</script>';"""
frontend_new = "        echo '<script id=\\\"h18-clean-menu-js\\\">" + behavior.replace("'", "\\\\'") + "</script>';"
renderer = replace_once(renderer, frontend_old, frontend_new, 'frontend menu behavior')'''
p.write_text(s[:start] + replacement + s[end:], encoding='utf-8')
print('0.1.54 Renderer label-based anchors repaired')
