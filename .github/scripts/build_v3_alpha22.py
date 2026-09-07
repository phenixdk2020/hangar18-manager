from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.22'
DEST = Path('build/visual-designer-manager')


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


subprocess.run(['python3', '.github/scripts/build_v3_alpha21.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.21', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.21');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.21');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.22 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# Desktop menu hardening.
# Alpha.21 still rendered navigation through a <details> disclosure wrapper.
# The mobile hamburger actively toggled that state, while desktop depended on
# CSS forcing content out of the closed disclosure state. Alpha.22 removes that
# dependency: desktop navigation is normal DOM/layout and mobile has its own
# explicit class controller.
renderer_rel = 'src/Frontend/Renderer.php'
renderer = read(renderer_rel)

old_markup = '<details class="h18-clean-front-menu-details"><summary class="h18-clean-front-menu-summary" aria-label="' + "' . $summaryLabel . '" + '"><span class="h18-clean-front-hamburger" aria-hidden="true"></span></summary><div class="h18-clean-front-menu-panel">' + "' . $rendered . '" + '</div></details>'
new_markup = '<div class="h18-clean-front-menu-details"><button type="button" class="h18-clean-front-menu-summary" aria-label="' + "' . $summaryLabel . '" + '" aria-expanded="false"><span class="h18-clean-front-hamburger" aria-hidden="true"></span></button><div class="h18-clean-front-menu-panel">' + "' . $rendered . '" + '</div></div>'
if renderer.count(old_markup) != 1:
    raise SystemExit(f'Alpha.22 menu markup anchor mismatch: {renderer.count(old_markup)}')
renderer = renderer.replace(old_markup, new_markup, 1)

old_open_selector = '.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-details[open]>.h18-clean-front-menu-panel{display:block!important}'
new_open_selector = '.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-details.is-open>.h18-clean-front-menu-panel{display:block!important}'
if renderer.count(old_open_selector) != 1:
    raise SystemExit(f'Alpha.22 mobile open selector mismatch: {renderer.count(old_open_selector)}')
renderer = renderer.replace(old_open_selector, new_open_selector, 1)

old_summary_css = '.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-summary{display:grid;place-items:center;width:48px;height:48px;box-sizing:border-box;padding:0;border:1.5px solid var(--h18-menu-color);border-radius:8px;background:transparent;color:var(--h18-menu-color);cursor:pointer;list-style:none;-webkit-tap-highlight-color:transparent}'
new_summary_css = '.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-summary{display:grid;place-items:center;width:48px;height:48px;box-sizing:border-box;padding:0;border:1.5px solid var(--h18-menu-color);border-radius:8px;background:transparent;color:var(--h18-menu-color);cursor:pointer;list-style:none;-webkit-tap-highlight-color:transparent;appearance:none;-webkit-appearance:none;font:inherit}'
if renderer.count(old_summary_css) != 1:
    raise SystemExit(f'Alpha.22 mobile summary CSS anchor mismatch: {renderer.count(old_summary_css)}')
renderer = renderer.replace(old_summary_css, new_summary_css, 1)

old_js = '(function(){document.addEventListener("click",function(e){document.querySelectorAll(".h18-clean-front-menu-details[open]").forEach(function(d){var nav=d.closest(".h18-clean-front-menu");if(!nav)return;var link=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu-list a"):null;if(link&&d.contains(link)&&nav.getAttribute("data-close-on-select")!=="0"){d.open=false;return;}if(nav.getAttribute("data-close-outside")==="1"&&!d.contains(e.target)){d.open=false;}});});document.addEventListener("keydown",function(e){if(e.key!=="Escape")return;document.querySelectorAll(".h18-clean-front-menu-details[open]").forEach(function(d){d.open=false;var s=d.querySelector("summary");if(s)s.focus();});});})();'
new_js = '(function(){function closeMenu(d,focus){if(!d)return;d.classList.remove("is-open");var s=d.querySelector(".h18-clean-front-menu-summary");if(s){s.setAttribute("aria-expanded","false");if(focus)s.focus();}}document.addEventListener("click",function(e){var trigger=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu-summary"):null;if(trigger){var details=trigger.closest(".h18-clean-front-menu-details");var triggerNav=trigger.closest(".h18-clean-front-menu");if(details&&triggerNav&&window.matchMedia("(max-width:782px)").matches&&triggerNav.getAttribute("data-mobile-mode")==="hamburger"){e.preventDefault();var opening=!details.classList.contains("is-open");document.querySelectorAll(".h18-clean-front-menu-details.is-open").forEach(function(other){if(other!==details)closeMenu(other,false);});details.classList.toggle("is-open",opening);trigger.setAttribute("aria-expanded",opening?"true":"false");return;}}document.querySelectorAll(".h18-clean-front-menu-details.is-open").forEach(function(d){var nav=d.closest(".h18-clean-front-menu");if(!nav)return;var link=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu-list a"):null;if(link&&d.contains(link)&&nav.getAttribute("data-close-on-select")!=="0"){closeMenu(d,false);return;}if(nav.getAttribute("data-close-outside")==="1"&&!d.contains(e.target)){closeMenu(d,false);}});});document.addEventListener("keydown",function(e){if(e.key!=="Escape")return;document.querySelectorAll(".h18-clean-front-menu-details.is-open").forEach(function(d){closeMenu(d,true);});});window.addEventListener("resize",function(){if(!window.matchMedia("(max-width:782px)").matches){document.querySelectorAll(".h18-clean-front-menu-details.is-open").forEach(function(d){closeMenu(d,false);});}});})();'
if renderer.count(old_js) != 2:
    raise SystemExit(f'Alpha.22 menu JS anchor mismatch: {renderer.count(old_js)}')
renderer = renderer.replace(old_js, new_js)

write(renderer_rel, renderer)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.21':
    raise SystemExit('Expected Alpha.21 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-07',
    'items': [
        'Desktop Header-menu: Menu-elementets wrapper er ikke længere et details-element; desktop-menuen ligger nu altid i normal DOM/layout.',
        'Mobil hamburger: eksplicit is-open-controller med aria-expanded, Escape, klik udenfor og luk ved menuvalg bevarer mobiladfærden.',
        'Website-menu binding fra Alpha.21, V1 0.1.93 baseline og øvrige responsive parity-fixes er bevaret.'
    ],
})
history['versions'] = rows
history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

print(f'Built {VERSION}')
