from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.14'
DEST = Path('build/visual-designer-manager')


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


subprocess.run(['python3', '.github/scripts/build_v3_alpha13.py'], check=True)

main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.13', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.13');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.13');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.14 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

renderer = read('src/Frontend/Renderer.php')
css_start = "        echo '.h18-clean-front-menu{"
css_end = "        echo '.h18-clean-front-text-heading{"
css = r'''        echo '.h18-clean-front-menu{display:flex;align-items:center;box-sizing:border-box;overflow:visible!important;z-index:10020}.h18-clean-front-menu-details{display:block;width:100%;min-width:0;position:relative}.h18-clean-front-menu-summary{display:none}.h18-clean-front-menu-panel{display:block!important;width:100%;min-width:0}.h18-clean-front-menu-list{list-style:none;margin:0;padding:0;display:flex;align-items:center;gap:var(--h18-menu-gap);font-size:var(--h18-menu-size);font-weight:var(--h18-menu-weight);justify-content:var(--h18-menu-justify);width:100%}.h18-clean-front-menu--vertical .h18-clean-front-menu-list{flex-direction:column;align-items:var(--h18-menu-items-align)}.h18-clean-front-menu-list li{margin:0;padding:0;position:relative}.h18-clean-front-menu-list a{color:var(--h18-menu-color);text-decoration:none;white-space:nowrap}.h18-clean-front-menu-list a:hover,.h18-clean-front-menu-list a:focus-visible{color:var(--h18-menu-hover)}.h18-clean-front-menu-list .current-menu-item>a,.h18-clean-front-menu-list .current_page_item>a{color:var(--h18-menu-active)}.h18-clean-front-menu .sub-menu{list-style:none;margin:4px 0 0;padding:0 0 0 14px}.h18-clean-front-menu--horizontal .sub-menu{display:none;position:absolute;background:var(--h18-menu-panel-bg);padding:8px;z-index:10030}.h18-clean-front-menu--horizontal li:hover>.sub-menu,.h18-clean-front-menu--horizontal li:focus-within>.sub-menu{display:block}';
        echo '@media(max-width:782px){.h18-clean-front-menu[data-mobile-mode="hamburger"]{justify-content:flex-end;overflow:visible!important}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-details{width:auto;margin-left:auto;overflow:visible!important}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-summary{display:grid;place-items:center;width:48px;height:48px;box-sizing:border-box;padding:0;border:1.5px solid var(--h18-menu-color);border-radius:8px;background:transparent;color:var(--h18-menu-color);cursor:pointer;list-style:none;-webkit-tap-highlight-color:transparent}.h18-clean-front-menu-summary::-webkit-details-marker{display:none}.h18-clean-front-menu-summary::marker{content:""}.h18-clean-front-hamburger{display:block;position:relative;width:24px;height:2px;border-radius:2px;background:currentColor}.h18-clean-front-hamburger:before,.h18-clean-front-hamburger:after{content:"";position:absolute;left:0;width:24px;height:2px;border-radius:2px;background:currentColor}.h18-clean-front-hamburger:before{top:-8px}.h18-clean-front-hamburger:after{top:8px}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-panel{display:none!important;position:absolute;top:calc(100% + 12px);right:0;left:auto;width:min(730px,calc(100vw - 32px));max-width:calc(100vw - 32px);max-height:calc(100vh - 120px);overflow:auto;box-sizing:border-box;padding:22px 24px;background:var(--h18-menu-mobile-panel-bg,#f2f0e8);color:var(--h18-menu-mobile-color,#30382a);border:1px solid rgba(48,56,42,.18);border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.20);z-index:2147482000}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-details[open]>.h18-clean-front-menu-panel{display:block!important}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list{display:flex!important;flex-direction:column!important;align-items:stretch!important;justify-content:flex-start!important;width:100%;gap:14px;font-size:max(var(--h18-menu-size),20px);font-weight:max(var(--h18-menu-weight),600)}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list li{width:100%}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list a{display:flex;align-items:center;width:100%;min-height:44px;box-sizing:border-box;padding:4px 10px;color:var(--h18-menu-mobile-color,#30382a)!important;white-space:normal;text-decoration:none}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list a:hover,.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list a:focus-visible,.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list .current-menu-item>a,.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list .current_page_item>a{color:var(--h18-menu-mobile-active,#30382a)!important;background:rgba(195,174,131,.20);border-radius:6px}.h18-clean-front-menu[data-mobile-mode="hamburger"] .sub-menu{display:block!important;position:static!important;margin:4px 0 4px 14px!important;padding:0 0 0 12px!important;border-left:2px solid rgba(195,174,131,.55)!important;background:transparent!important}.h18-clean-front-menu[data-mobile-mode="vertical"] .h18-clean-front-menu-details,.h18-clean-front-menu[data-mobile-mode="wrap"] .h18-clean-front-menu-details{width:100%}.h18-clean-front-menu[data-mobile-mode="vertical"] .h18-clean-front-menu-summary,.h18-clean-front-menu[data-mobile-mode="wrap"] .h18-clean-front-menu-summary{display:none}.h18-clean-front-menu[data-mobile-mode="vertical"] .h18-clean-front-menu-panel,.h18-clean-front-menu[data-mobile-mode="wrap"] .h18-clean-front-menu-panel{display:block!important;position:static;background:transparent;border:0;box-shadow:none;padding:0}.h18-clean-front-menu[data-mobile-mode="vertical"] .h18-clean-front-menu-list{flex-direction:column;align-items:flex-start}.h18-clean-front-menu[data-mobile-mode="wrap"] .h18-clean-front-menu-list{flex-wrap:wrap}}';
'''
start = renderer.find(css_start)
end = renderer.find(css_end, start)
if start < 0 or end < 0:
    raise SystemExit('Alpha.14 menu CSS anchors missing')
renderer = renderer[:start] + css + renderer[end:]

menu_start = "        if ($type === 'menu') {"
menu_end = "        if ($type === 'button') {"
menu_block = r'''        if ($type === 'menu') {
            $menuId = absint($props['menuId'] ?? 0);
            $orientation = (string) ($props['orientation'] ?? 'horizontal') === 'vertical' ? 'vertical' : 'horizontal';
            $align = in_array((string) ($props['align'] ?? 'right'), ['left', 'center', 'right'], true) ? (string) $props['align'] : 'right';
            $mobileMode = in_array((string) ($props['mobileMode'] ?? 'hamburger'), ['hamburger', 'vertical', 'wrap'], true) ? (string) $props['mobileMode'] : 'hamburger';
            $mobilePresentation = in_array((string) ($props['mobilePresentation'] ?? 'dropdown'), ['dropdown', 'panel-right', 'panel-left'], true) ? (string) $props['mobilePresentation'] : 'dropdown';
            $mobileCloseOnSelect = !array_key_exists('mobileCloseOnSelect', $props) || !empty($props['mobileCloseOnSelect']);
            $mobileCloseOutside = !array_key_exists('mobileCloseOutside', $props) || !empty($props['mobileCloseOutside']);
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#ffffff')) ?: '#ffffff';
            $hoverColor = sanitize_hex_color((string) ($props['hoverTextColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $activeColor = sanitize_hex_color((string) ($props['activeTextColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $baseBackground = sanitize_hex_color((string) ($props['background'] ?? '#30382a')) ?: '#30382a';
            $background = !empty($props['backgroundTransparent']) ? 'transparent' : $baseBackground;
            $fontSize = max(8, min(64, (int) ($props['fontSize'] ?? 16)));
            $fontWeight = max(100, min(900, (int) ($props['fontWeight'] ?? 600)));
            $gap = max(0, min(120, (int) ($props['menuGap'] ?? 24)));
            $paddingX = max(0, min(120, (int) ($props['paddingX'] ?? 8)));
            $paddingY = max(0, min(120, (int) ($props['paddingY'] ?? 8)));
            $justify = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $itemsAlign = ['left' => 'flex-start', 'center' => 'center', 'right' => 'flex-end'][$align];
            $rendered = '';
            if ($menuId > 0) {
                $candidate = wp_nav_menu([
                    'menu' => $menuId,
                    'container' => false,
                    'echo' => false,
                    'fallback_cb' => false,
                    'menu_class' => 'h18-clean-front-menu-list',
                    'menu_id' => 'h18-clean-menu-list-' . $id,
                    'depth' => 2,
                ]);
                $rendered = is_string($candidate) ? $candidate : '';
            }
            if ($rendered === '') {
                $rendered = '<ul class="h18-clean-front-menu-list"><li><span>Vælg menu i Visual Designer</span></li></ul>';
            }
            $menuStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';padding:' . $paddingY . 'px ' . $paddingX . 'px;'
                . '--h18-menu-color:' . $textColor . ';--h18-menu-hover:' . $hoverColor . ';--h18-menu-active:' . $activeColor . ';--h18-menu-gap:' . $gap . 'px;'
                . '--h18-menu-size:' . $fontSize . 'px;--h18-menu-weight:' . $fontWeight . ';--h18-menu-justify:' . $justify . ';--h18-menu-items-align:' . $itemsAlign . ';--h18-menu-panel-bg:' . $baseBackground . ';'
                . '--h18-menu-mobile-panel-bg:#f2f0e8;--h18-menu-mobile-color:#30382a;--h18-menu-mobile-active:#30382a;';
            $summaryLabel = esc_attr__('Åbn menu', 'visual-designer-manager');
            return '<nav id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-menu h18-clean-front-menu--' . esc_attr($orientation) . '" data-mobile-mode="' . esc_attr($mobileMode) . '" data-mobile-presentation="' . esc_attr($mobilePresentation) . '" data-close-on-select="' . ($mobileCloseOnSelect ? '1' : '0') . '" data-close-outside="' . ($mobileCloseOutside ? '1' : '0') . '" aria-label="Navigation" style="' . esc_attr($menuStyle) . '"><details class="h18-clean-front-menu-details"><summary class="h18-clean-front-menu-summary" aria-label="' . $summaryLabel . '"><span class="h18-clean-front-hamburger" aria-hidden="true"></span></summary><div class="h18-clean-front-menu-panel">' . $rendered . '</div></details></nav>';
        }

'''
start = renderer.find(menu_start)
end = renderer.find(menu_end, start)
if start < 0 or end < 0:
    raise SystemExit('Alpha.14 menu node anchors missing')
renderer = renderer[:start] + menu_block + renderer[end:]

old_inline_start = "            . '<script>(function(){function setOpen(n,o)"
old_inline_end = "</script></body></html>';"
pos = renderer.find(old_inline_start)
end = renderer.find(old_inline_end, pos)
if pos < 0 or end < 0:
    raise SystemExit('Alpha.14 standalone old menu runtime anchor missing')
end += len('</script>')
new_inline = "            . '<script>(function(){document.addEventListener(\"click\",function(e){document.querySelectorAll(\".h18-clean-front-menu-details[open]\").forEach(function(d){var nav=d.closest(\".h18-clean-front-menu\");if(!nav)return;var link=e.target&&e.target.closest?e.target.closest(\".h18-clean-front-menu-list a\"):null;if(link&&d.contains(link)&&nav.getAttribute(\"data-close-on-select\")!==\"0\"){d.open=false;return;}if(nav.getAttribute(\"data-close-outside\")===\"1\"&&!d.contains(e.target)){d.open=false;}});});document.addEventListener(\"keydown\",function(e){if(e.key!==\"Escape\")return;document.querySelectorAll(\".h18-clean-front-menu-details[open]\").forEach(function(d){d.open=false;var s=d.querySelector(\"summary\");if(s)s.focus();});});})();</script>"
renderer = renderer[:pos] + new_inline + renderer[end:]

script_start = "    public static function menuScript(): void\n    {"
script_end = "    public static function previewKey("
pos = renderer.find(script_start)
end = renderer.find(script_end, pos)
if pos < 0 or end < 0:
    raise SystemExit('Alpha.14 menuScript anchors missing')
menu_script = r'''    public static function menuScript(): void
    {
        if (!is_singular('page')) { return; }
        echo '<script id="h18-clean-menu-js">(function(){document.addEventListener("click",function(e){document.querySelectorAll(".h18-clean-front-menu-details[open]").forEach(function(d){var nav=d.closest(".h18-clean-front-menu");if(!nav)return;var link=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu-list a"):null;if(link&&d.contains(link)&&nav.getAttribute("data-close-on-select")!=="0"){d.open=false;return;}if(nav.getAttribute("data-close-outside")==="1"&&!d.contains(e.target)){d.open=false;}});});document.addEventListener("keydown",function(e){if(e.key!=="Escape")return;document.querySelectorAll(".h18-clean-front-menu-details[open]").forEach(function(d){d.open=false;var s=d.querySelector("summary");if(s)s.focus();});});})();</script>';
    }

'''
renderer = renderer[:pos] + menu_script + renderer[end:]
write('src/Frontend/Renderer.php', renderer)

editor = read('assets/editor-v018-core.js')
preview_start = "                if (previewDevice === 'mobile' && node.props.mobileMode === 'hamburger') {"
preview_end = "                } else if (!items.length) {"
pos = editor.find(preview_start)
end = editor.find(preview_end, pos)
if pos < 0 or end < 0:
    raise SystemExit('Alpha.14 Designer menu preview anchors missing')
preview = r'''                if (previewDevice === 'mobile' && node.props.mobileMode === 'hamburger') {
                    nav.classList.add('is-mobile-hamburger-preview');
                    nav.style.justifyContent = node.props.align === 'left' ? 'flex-start' : 'flex-end';
                    const details = document.createElement('details');
                    details.className = 'h18-vd-menu-preview-details';
                    details.style.position = 'relative';
                    details.style.marginLeft = node.props.align === 'left' ? '0' : 'auto';
                    const summary = document.createElement('summary');
                    summary.className = 'h18-vd-menu-preview-summary';
                    summary.setAttribute('aria-label', 'Åbn menu');
                    summary.textContent = '☰';
                    summary.style.display = 'grid'; summary.style.placeItems = 'center'; summary.style.width = '48px'; summary.style.height = '48px'; summary.style.boxSizing = 'border-box'; summary.style.border = '1.5px solid currentColor'; summary.style.borderRadius = '8px'; summary.style.cursor = 'pointer'; summary.style.listStyle = 'none'; summary.style.color = node.props.textColor || '#ffffff';
                    details.appendChild(summary);
                    const previewList = document.createElement('div');
                    previewList.className = 'h18-vd-menu-preview-mobile-list is-v1-dropdown';
                    previewList.style.position = 'absolute'; previewList.style.zIndex = '500'; previewList.style.top = '60px'; previewList.style.right = '0'; previewList.style.width = 'min(330px, calc(100vw - 32px))'; previewList.style.boxSizing = 'border-box'; previewList.style.padding = '22px 24px'; previewList.style.borderRadius = '8px'; previewList.style.background = '#f2f0e8'; previewList.style.boxShadow = '0 10px 30px rgba(0,0,0,.20)'; previewList.style.flexDirection = 'column'; previewList.style.gap = '14px';
                    items.forEach(function (item) { const label = document.createElement('span'); label.textContent = String(item.title || 'Menupunkt'); label.style.color = '#30382a'; label.style.fontSize = '20px'; label.style.fontWeight = '600'; label.style.padding = '7px 10px'; previewList.appendChild(label); });
                    details.appendChild(previewList);
                    nav.appendChild(details);
'''
editor = editor[:pos] + preview + editor[end:]
write('assets/editor-v018-core.js', editor)

menu_css = read('assets/editor-v0154-menu.css')
menu_css += r'''
/* Alpha.14: V1-style native mobile menu preview. */
.h18-vd-menu-preview-details:not([open])>.h18-vd-menu-preview-mobile-list.is-v1-dropdown{display:none!important}
.h18-vd-menu-preview-details[open]>.h18-vd-menu-preview-mobile-list.is-v1-dropdown{display:flex!important}
.h18-vd-menu-preview-summary::-webkit-details-marker{display:none}
.h18-vd-menu-preview-summary::marker{content:""}
'''
write('assets/editor-v0154-menu.css', menu_css)

history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.13':
    raise SystemExit('Expected Alpha.13 release-history baseline missing')
alpha14 = {
    'version': VERSION,
    'date': '2026-09-06',
    'items': [
        'V1 Mobile Menu Parity: hamburger-menuen bruger nu native details/summary som den fungerende V1-reference i stedet for V3 is-open/grid-toggle runtime.',
        'Mobilmenuen åbner som et lyst dropdown-panel over sideindholdet og ændrer ikke Headerens gemte gridhøjde eller sidegeometri.',
        'Menulinks er almindelige WordPress-links og bliver ikke preventDefault-behandlet; valg navigerer normalt og lukker menuen.',
        'Klik udenfor og Escape lukker det åbne details-panel som progressiv enhancement uden at eje selve toggle-adfærden.',
        'Designerens mobil-preview bruger samme details/summary-model og V1-lignende lyse dropdown som live frontend.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha14] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

renderer = read('src/Frontend/Renderer.php')
editor = read('assets/editor-v018-core.js')
main = read('visual-designer-manager.php')
for token in ['Version: 3.0.0-alpha.14', "define('VDM_VERSION', '3.0.0-alpha.14');"]:
    if token not in main:
        raise SystemExit(f'Alpha.14 version token missing: {token}')
for token in [
    '<details class="h18-clean-front-menu-details">',
    'h18-clean-front-menu-summary',
    'h18-clean-front-hamburger',
    'h18-clean-front-menu-details[open]>.h18-clean-front-menu-panel',
    '--h18-menu-mobile-panel-bg:#f2f0e8',
    'data-close-on-select',
    'data-close-outside',
]:
    if token not in renderer:
        raise SystemExit(f'Alpha.14 Renderer parity token missing: {token}')
for forbidden in ['class="h18-clean-front-menu-toggle"', 'classList.toggle("is-open"', 'textContent=o?"✕ Luk":"☰ Menu"']:
    if forbidden in renderer:
        raise SystemExit(f'Alpha.14 obsolete V3 menu runtime still present: {forbidden}')
for token in ['h18-vd-menu-preview-details', "summary.setAttribute('aria-label', 'Åbn menu')", "previewList.style.background = '#f2f0e8'"]:
    if token not in editor:
        raise SystemExit(f'Alpha.14 Designer V1 menu token missing: {token}')

print('V3 Alpha.14 V1 native mobile menu parity: PASS')
print('Grid-bound is-open toggle removed: PASS')
print('Designer/live native details contract: PASS')
