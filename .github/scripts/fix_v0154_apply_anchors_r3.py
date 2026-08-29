from pathlib import Path
import runpy

runpy.run_path('.github/scripts/fix_v0154_apply_anchors_r2.py', run_name='__main__')
p = Path('.github/scripts/apply_v0154_menu_ux_publish.py')
s = p.read_text(encoding='utf-8')
start = s.find("renderer = regex_once(\n    renderer,\n    r\"            \\\\. '<script>document")
end_marker = "    'frontend menu behavior'\n)\n"
end = s.find(end_marker, start)
if start < 0 or end < 0:
    raise SystemExit('renderer behavior patch block not found')
end += len(end_marker)
replacement = r'''standalone_old = ''' + "\"\"\"" + r'''            . '<script>document.addEventListener("click",function(e){var b=e.target.closest(".h18-clean-front-menu-toggle");if(!b)return;var n=b.closest(".h18-clean-front-menu");if(!n)return;var open=!n.classList.contains("is-open");n.classList.toggle("is-open",open);b.setAttribute("aria-expanded",open?"true":"false");});</script></body></html>';''' + "\"\"\"" + r'''
standalone_new = "            . '<script>" + behavior.replace("'", "\\'") + "</script></body></html>';"
renderer = replace_once(renderer, standalone_old, standalone_new, 'standalone menu behavior')
frontend_old = ''' + "\"\"\"" + r'''        echo '<script id="h18-clean-menu-js">document.addEventListener("click",function(e){var b=e.target.closest(".h18-clean-front-menu-toggle");if(!b)return;var n=b.closest(".h18-clean-front-menu");if(!n)return;var open=!n.classList.contains("is-open");n.classList.toggle("is-open",open);b.setAttribute("aria-expanded",open?"true":"false");});</script>';''' + "\"\"\"" + r'''
frontend_new = "        echo '<script id=\"h18-clean-menu-js\">" + behavior.replace("'", "\\'") + "</script>';"
renderer = replace_once(renderer, frontend_old, frontend_new, 'frontend menu behavior')
'''
p.write_text(s[:start] + replacement + s[end:], encoding='utf-8')
print('0.1.54 Renderer behavior anchors repaired')
