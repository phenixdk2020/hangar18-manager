from pathlib import Path
import json
import re

ROOT = Path('clean/hangar18-manager')
PLUGIN = ROOT / 'hangar18-manager.php'
ADMIN = ROOT / 'src/Admin/AdminController.php'
NAV = ROOT / 'src/Admin/NavigationController.php'
EDITOR = ROOT / 'src/Admin/EditorController.php'
MODEL = ROOT / 'src/Model/LayoutModel.php'
RENDERER = ROOT / 'src/Frontend/Renderer.php'
CORE = ROOT / 'assets/editor-v018-core.js'
HISTORY = ROOT / 'release-history.json'
NOTES = Path('clean-release-notes.html')
TECH = Path('CLEAN-TECHNICAL-MANUAL.md')
STATUS = Path('docs/v0154-status.md')
MENU_CSS = ROOT / 'assets/editor-v0154-menu.css'
ADMIN_MENU_CSS = ROOT / 'assets/admin-v0154-menu.css'
ADMIN_MENU_JS = ROOT / 'assets/admin-v0154-menu.js'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)


def regex_once(text: str, pattern: str, repl: str, label: str) -> str:
    out, count = re.subn(pattern, repl, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one regex match, found {count}')
    return out

# -----------------------------------------------------------------------------
# Plugin bootstrap: version, Designer menu-admin link and 0.1.54 Designer CSS.
# -----------------------------------------------------------------------------
plugin = PLUGIN.read_text(encoding='utf-8')
plugin = replace_once(plugin, 'Version: 0.1.53', 'Version: 0.1.54', 'plugin header version')
plugin = replace_once(plugin, "H18_CLEAN_VERSION', '0.1.53'", "H18_CLEAN_VERSION', '0.1.54'", 'plugin constant version')
plugin = replace_once(
    plugin,
    "        'menus' => $menuPayload,\n        'ajaxUrl' => admin_url('admin-ajax.php'),",
    "        'menus' => $menuPayload,\n        'menuAdminUrl' => admin_url('admin.php?page=h18-clean-menu'),\n        'ajaxUrl' => admin_url('admin-ajax.php'),",
    'localize menu admin url'
)
css_anchor = """    wp_enqueue_style(
        'h18-clean-editor-v0153-transparent',
        H18_CLEAN_URL . 'assets/editor-v0153-transparent.css',
        ['h18-clean-editor-v0148-layers'],
        H18_CLEAN_VERSION
    );
"""
css_insert = css_anchor + """    wp_enqueue_style(
        'h18-clean-editor-v0154-menu',
        H18_CLEAN_URL . 'assets/editor-v0154-menu.css',
        ['h18-clean-editor-v0153-transparent'],
        H18_CLEAN_VERSION
    );
"""
plugin = replace_once(plugin, css_anchor, css_insert, 'enqueue v0154 menu css')
PLUGIN.write_text(plugin, encoding='utf-8')

# -----------------------------------------------------------------------------
# Manager -> Menu: keep WordPress nav_menu canonical, but make the existing
# NavigationController UI sortable and easier to understand.
# -----------------------------------------------------------------------------
nav = NAV.read_text(encoding='utf-8')
nav = replace_once(
    nav,
    "        add_action('admin_menu', [self::class, 'menu'], 8);\n",
    "        add_action('admin_menu', [self::class, 'menu'], 8);\n        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);\n",
    'navigation enqueue hook'
)
menu_method_anchor = """    public static function menu(): void
    {
        remove_submenu_page(AdminController::MENU, 'h18-clean-menu');
        add_submenu_page(
            AdminController::MENU,
            'Menu / Navigation',
            'Menu',
            'edit_theme_options',
            'h18-clean-menu',
            [self::class, 'render']
        );
    }

"""
menu_method_insert = menu_method_anchor + """    public static function enqueue(string $hook): void
    {
        if (!current_user_can('edit_theme_options') || sanitize_key((string) ($_GET['page'] ?? '')) !== 'h18-clean-menu') {
            return;
        }
        wp_enqueue_style('h18-clean-menu-v0154', H18_CLEAN_URL . 'assets/admin-v0154-menu.css', [], H18_CLEAN_VERSION);
        wp_enqueue_script('h18-clean-menu-v0154', H18_CLEAN_URL . 'assets/admin-v0154-menu.js', [], H18_CLEAN_VERSION, true);
    }

"""
nav = replace_once(nav, menu_method_anchor, menu_method_insert, 'navigation enqueue method')
nav = replace_once(
    nav,
    "        echo '<p class=\"h18-manager-description\">Administrér navigationens struktur uafhængigt af Visual Designer. Menuens udseende, responsive hamburger-menu og placering hører senere til Menu-elementet i Header/Footer Designer.</p>';",
    "        echo '<p class=\"h18-manager-description\">Administrér menupunkter her med samme WordPress-menu som datakilde på frontend. Visual Designer styrer kun udseende og responsive visning — der oprettes aldrig en parallel menustruktur.</p>';",
    'navigation description'
)
nav = replace_once(
    nav,
    "            echo '<table class=\"widefat striped h18-manager-table\"><thead><tr><th>Titel</th><th>Type</th><th>Parent</th><th>Position</th><th>URL</th></tr></thead><tbody>';",
    "            echo '<p class=\"description\">Træk punkterne med ☰ for at ændre rækkefølgen. Piletasterne ved hvert punkt er et tastaturvenligt alternativ. Vælg \"Undermenu under\" for at lave et underpunkt.</p>';\n            echo '<table class=\"widefat striped h18-manager-table h18-menu-sort-table\"><thead><tr><th>Flyt</th><th>Menutekst</th><th>Type</th><th>Undermenu under</th><th>Rækkefølge</th><th>Destination</th></tr></thead><tbody id=\"h18-menu-sort-list\">';",
    'sortable table header'
)
nav = replace_once(
    nav,
    "                echo '<tr><td><input name=\"item_title[' . esc_attr((string) $id) . ']\" value=\"' . esc_attr((string) $item->title) . '\"></td><td><code>' . esc_html((string) $item->type) . '</code></td>';",
    "                echo '<tr class=\"h18-menu-sort-row\" draggable=\"true\" data-menu-item-id=\"' . esc_attr((string) $id) . '\"><td class=\"h18-menu-drag-cell\"><span class=\"h18-menu-drag-handle\" title=\"Træk for at flytte\" aria-hidden=\"true\">☰</span><span class=\"h18-menu-order-buttons\"><button type=\"button\" class=\"button button-small\" data-menu-move=\"up\" aria-label=\"Flyt op\">↑</button><button type=\"button\" class=\"button button-small\" data-menu-move=\"down\" aria-label=\"Flyt ned\">↓</button></span></td><td><input class=\"regular-text\" name=\"item_title[' . esc_attr((string) $id) . ']\" value=\"' . esc_attr((string) $item->title) . '\"><small class=\"description\">Kan ændres uden at ændre sidens titel.</small></td><td><code>' . esc_html((string) $item->type) . '</code></td>';",
    'sortable row start'
)
nav = replace_once(nav, '<option value=\"0\">— root —</option>', '<option value=\"0\">Topniveau</option>', 'parent root label')
nav = replace_once(
    nav,
    "                echo '</select></td><td><input type=\"number\" min=\"1\" style=\"width:75px\" name=\"item_order[' . esc_attr((string) $id) . ']\" value=\"' . esc_attr((string) $item->menu_order) . '\"></td><td><small>' . esc_html((string) $item->url) . '</small></td></tr>';",
    "                echo '</select></td><td><input class=\"h18-menu-order-input\" type=\"hidden\" name=\"item_order[' . esc_attr((string) $id) . ']\" value=\"' . esc_attr((string) $item->menu_order) . '\"><strong class=\"h18-menu-order-label\">' . esc_html((string) $item->menu_order) . '</strong></td><td><small>' . esc_html((string) $item->url) . '</small></td></tr>';",
    'sortable position field'
)
nav = replace_once(
    nav,
    "        echo '<p><button class=\"button button-primary\" type=\"submit\">Gem menu</button> <a class=\"button\" href=\"' . esc_url(admin_url('nav-menus.php?action=edit&menu=' . $menuId)) . '\">Åbn WordPress Menu-editor</a></p></form>';",
    "        echo '<p><button class=\"button button-primary\" type=\"submit\">Gem menu og rækkefølge</button> <a class=\"button\" href=\"' . esc_url(admin_url('nav-menus.php?action=edit&menu=' . $menuId)) . '\">Avanceret WordPress Menu-editor</a></p></form>';",
    'menu save label'
)
NAV.write_text(nav, encoding='utf-8')

ADMIN_MENU_JS.write_text(r"""(function () {
    'use strict';
    function rows(list) { return Array.from(list ? list.querySelectorAll(':scope > .h18-menu-sort-row') : []); }
    function renumber(list) {
        rows(list).forEach(function (row, index) {
            var input = row.querySelector('.h18-menu-order-input');
            var label = row.querySelector('.h18-menu-order-label');
            if (input) { input.value = String(index + 1); }
            if (label) { label.textContent = String(index + 1); }
        });
    }
    function install() {
        var list = document.getElementById('h18-menu-sort-list');
        if (!list) { return; }
        var dragging = null;
        rows(list).forEach(function (row) {
            row.addEventListener('dragstart', function (event) {
                dragging = row;
                row.classList.add('is-dragging');
                if (event.dataTransfer) { event.dataTransfer.effectAllowed = 'move'; event.dataTransfer.setData('text/plain', row.dataset.menuItemId || ''); }
            });
            row.addEventListener('dragend', function () { row.classList.remove('is-dragging'); dragging = null; renumber(list); });
        });
        list.addEventListener('dragover', function (event) {
            if (!dragging) { return; }
            event.preventDefault();
            var target = event.target && event.target.closest ? event.target.closest('.h18-menu-sort-row') : null;
            if (!target || target === dragging || target.parentNode !== list) { return; }
            var rect = target.getBoundingClientRect();
            var before = event.clientY < rect.top + rect.height / 2;
            list.insertBefore(dragging, before ? target : target.nextSibling);
            renumber(list);
        });
        list.addEventListener('click', function (event) {
            var button = event.target && event.target.closest ? event.target.closest('[data-menu-move]') : null;
            if (!button) { return; }
            var row = button.closest('.h18-menu-sort-row');
            if (!row) { return; }
            var direction = button.getAttribute('data-menu-move');
            if (direction === 'up' && row.previousElementSibling) { list.insertBefore(row, row.previousElementSibling); }
            if (direction === 'down' && row.nextElementSibling) { list.insertBefore(row.nextElementSibling, row); }
            renumber(list);
        });
        renumber(list);
    }
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
""", encoding='utf-8')

ADMIN_MENU_CSS.write_text("""/* Visual Designer Manager 0.1.54 · Manager Menu UX */
.h18-menu-sort-row{transition:box-shadow .12s ease,opacity .12s ease}
.h18-menu-sort-row.is-dragging{opacity:.55;box-shadow:inset 0 0 0 2px #2271b1}
.h18-menu-drag-cell{width:112px;white-space:nowrap}
.h18-menu-drag-handle{display:inline-flex;align-items:center;justify-content:center;width:30px;height:30px;margin-right:6px;border:1px solid #c3c4c7;border-radius:4px;background:#fff;cursor:grab;font-size:18px;font-weight:700;vertical-align:middle}
.h18-menu-drag-handle:active{cursor:grabbing}
.h18-menu-order-buttons{display:inline-flex;gap:3px;vertical-align:middle}
.h18-menu-sort-table td{vertical-align:middle}
.h18-menu-sort-table input.regular-text{width:min(100%,320px);display:block}
.h18-menu-sort-table td small.description{display:block;margin-top:4px}
@media(max-width:782px){.h18-menu-sort-table{display:block;overflow-x:auto}.h18-menu-drag-cell{min-width:112px}}
""", encoding='utf-8')

# Dashboard copy no longer says menu is merely upcoming.
admin = ADMIN.read_text(encoding='utf-8')
admin = admin.replace(
    "self::card('Menu · næste arbejdsspor', 'Menu-redesignet er næste UX-opgave. Eksisterende WordPress-menuer forbliver datakilden, mens vi gør valg, struktur og mobiladfærd mere brugervenlig.', self::url('h18-clean-menu'), 'Forbered Menu');",
    "self::card('Menu', 'Redigér WordPress-menuens punkter og rækkefølge i en brugervenlig VDM-visning. Samme menu bruges direkte af Visual Designer.', self::url('h18-clean-menu'), 'Redigér Menu');"
)
ADMIN.write_text(admin, encoding='utf-8')

# -----------------------------------------------------------------------------
# Canonical Menu properties: mobile presentation + close behavior.
# -----------------------------------------------------------------------------
model = MODEL.read_text(encoding='utf-8')
model = replace_once(
    model,
    "                    'mobileMode' => in_array((string) ($props['mobileMode'] ?? 'hamburger'), ['hamburger', 'vertical', 'wrap'], true) ? (string) $props['mobileMode'] : 'hamburger',\n                    'menuId' => max(0, (int) ($props['menuId'] ?? 0)),",
    "                    'mobileMode' => in_array((string) ($props['mobileMode'] ?? 'hamburger'), ['hamburger', 'vertical', 'wrap'], true) ? (string) $props['mobileMode'] : 'hamburger',\n                    'mobilePresentation' => in_array((string) ($props['mobilePresentation'] ?? 'dropdown'), ['dropdown', 'panel-right', 'panel-left'], true) ? (string) $props['mobilePresentation'] : 'dropdown',\n                    'mobileCloseOnSelect' => !array_key_exists('mobileCloseOnSelect', $props) || !empty($props['mobileCloseOnSelect']),\n                    'mobileCloseOutside' => !array_key_exists('mobileCloseOutside', $props) || !empty($props['mobileCloseOutside']),\n                    'menuId' => max(0, (int) ($props['menuId'] ?? 0)),",
    'php menu mobile props'
)
MODEL.write_text(model, encoding='utf-8')

# -----------------------------------------------------------------------------
# Designer Menu Inspector and mobile canvas preview.
# -----------------------------------------------------------------------------
core = CORE.read_text(encoding='utf-8')
core = replace_once(
    core,
    "orientation:'menuretning',mobileMode:'mobilmenu',activeTextColor:'aktiv menufarve'",
    "orientation:'menuretning',mobileMode:'mobilmenu',mobilePresentation:'mobilmenu-visning',mobileCloseOnSelect:'luk efter valg',mobileCloseOutside:'luk ved klik udenfor',activeTextColor:'aktiv menufarve'",
    'menu field labels'
)
core = replace_once(
    core,
    "                mobileMode: ['hamburger', 'vertical', 'wrap'].includes(String(raw.mobileMode || '').toLowerCase()) ? String(raw.mobileMode).toLowerCase() : 'hamburger',\n                textColor:",
    "                mobileMode: ['hamburger', 'vertical', 'wrap'].includes(String(raw.mobileMode || '').toLowerCase()) ? String(raw.mobileMode).toLowerCase() : 'hamburger',\n                mobilePresentation: ['dropdown', 'panel-right', 'panel-left'].includes(String(raw.mobilePresentation || '').toLowerCase()) ? String(raw.mobilePresentation).toLowerCase() : 'dropdown',\n                mobileCloseOnSelect: raw.mobileCloseOnSelect !== false,\n                mobileCloseOutside: raw.mobileCloseOutside !== false,\n                textColor:",
    'js normalize menu props'
)
core = replace_once(
    core,
    "                else if (field === 'mobileMode') { current.props.mobileMode = ['hamburger', 'vertical', 'wrap'].includes(control.value) ? control.value : 'hamburger'; }\n                else if (field === 'activeTextColor')",
    "                else if (field === 'mobileMode') { current.props.mobileMode = ['hamburger', 'vertical', 'wrap'].includes(control.value) ? control.value : 'hamburger'; }\n                else if (field === 'mobilePresentation') { current.props.mobilePresentation = ['dropdown', 'panel-right', 'panel-left'].includes(control.value) ? control.value : 'dropdown'; }\n                else if (field === 'mobileCloseOnSelect') { current.props.mobileCloseOnSelect = !!control.checked; }\n                else if (field === 'mobileCloseOutside') { current.props.mobileCloseOutside = !!control.checked; }\n                else if (field === 'activeTextColor')",
    'js input menu props'
)

menu_inspector_pattern = r"        } else if \(node\.type === 'menu'\) \{\n            html \+= '<label>WordPress-menu<select data-field=\\\"menuId\\\">.*?            html \+= '<p class=\\\"description\\\">Menuen henter sine punkter fra WordPress\. Visual Designer gemmer kun valgt menu og designindstillinger\.</p>';\n"
menu_inspector_repl = """        } else if (node.type === 'menu') {
            html += '<div class=\"h18-vd-menu-group\"><h3>Indhold</h3><label>Menu<select data-field=\"menuId\"><option value=\"0\">Vælg menu…</option>' + (Array.isArray(CFG.menus) ? CFG.menus.map(function (menu) { const id = parseInt(menu.id || 0, 10) || 0; return '<option value=\"' + id + '\"' + (parseInt(node.props.menuId || 0, 10) === id ? ' selected' : '') + '>' + escapeHtml(String(menu.name || ('Menu ' + id))) + '</option>'; }).join('') : '') + '</select></label>';
            if (CFG.menuAdminUrl) { html += '<p><a class=\"button\" href=\"' + escapeAttr(String(CFG.menuAdminUrl)) + '\">Redigér menupunkter</a></p>'; }
            html += '<p class=\"description\">Menupunkterne ligger ét sted i WordPress/Manager. Visual Designer gemmer kun valg og udseende.</p></div>';
            html += '<div class=\"h18-vd-menu-group\"><h3>Layout</h3><div class=\"h18-clean-field-grid\"><label>Retning<select data-field=\"orientation\"><option value=\"horizontal\"' + (node.props.orientation !== 'vertical' ? ' selected' : '') + '>Vandret</option><option value=\"vertical\"' + (node.props.orientation === 'vertical' ? ' selected' : '') + '>Lodret</option></select></label><label>Justering<select data-field=\"align\"><option value=\"left\"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value=\"center\"' + (node.props.align === 'center' ? ' selected' : '') + '>Center</option><option value=\"right\"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label><label>Afstand px<input data-field=\"menuGap\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.menuGap || 24) + '\"></label><label>Padding X<input data-field=\"paddingX\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingX || 8) + '\"></label><label>Padding Y<input data-field=\"paddingY\" type=\"number\" min=\"0\" max=\"120\" value=\"' + (node.props.paddingY || 8) + '\"></label><label>Hjørner px<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"100\" value=\"' + (node.props.radius || 0) + '\"></label></div></div>';
            html += '<div class=\"h18-vd-menu-group\"><h3>Tekst</h3><div class=\"h18-clean-field-grid\"><label>Størrelse px<input data-field=\"fontSize\" type=\"number\" min=\"8\" max=\"64\" value=\"' + (node.props.fontSize || 16) + '\"></label><label>Tykkelse<select data-field=\"fontWeight\">' + [300,400,500,600,700,800,900].map(function (v) { return '<option value=\"' + v + '\"' + (parseInt(node.props.fontWeight || 600, 10) === v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label></div></div>';
            html += '<div class=\"h18-vd-menu-group\"><h3>Farver</h3><label class=\"h18-clean-checkbox\"><input data-field=\"backgroundTransparent\" type=\"checkbox\"' + (node.props.backgroundTransparent !== false ? ' checked' : '') + '> Gennemsigtig baggrund</label><div class=\"h18-clean-field-grid\"><label>Baggrund<input data-field=\"background\" type=\"color\" value=\"' + escapeAttr(node.props.background || '#30382a') + '\"></label><label>Normal<input data-field=\"textColor\" type=\"color\" value=\"' + escapeAttr(node.props.textColor || '#ffffff') + '\"></label><label>Hover<input data-field=\"hoverTextColor\" type=\"color\" value=\"' + escapeAttr(node.props.hoverTextColor || '#c3ae83') + '\"></label><label>Aktiv side<input data-field=\"activeTextColor\" type=\"color\" value=\"' + escapeAttr(node.props.activeTextColor || '#c3ae83') + '\"></label></div></div>';
            html += '<div class=\"h18-vd-menu-group\"><h3>Mobil</h3><label>Mobilvisning<select data-field=\"mobileMode\"><option value=\"hamburger\"' + (node.props.mobileMode === 'hamburger' ? ' selected' : '') + '>Hamburger</option><option value=\"vertical\"' + (node.props.mobileMode === 'vertical' ? ' selected' : '') + '>Lodret menu</option><option value=\"wrap\"' + (node.props.mobileMode === 'wrap' ? ' selected' : '') + '>Ombryd menupunkter</option></select></label>';
            if (node.props.mobileMode === 'hamburger') { html += '<label>Åbn som<select data-field=\"mobilePresentation\"><option value=\"dropdown\"' + (node.props.mobilePresentation === 'dropdown' ? ' selected' : '') + '>Dropdown</option><option value=\"panel-right\"' + (node.props.mobilePresentation === 'panel-right' ? ' selected' : '') + '>Panel fra højre</option><option value=\"panel-left\"' + (node.props.mobilePresentation === 'panel-left' ? ' selected' : '') + '>Panel fra venstre</option></select></label><label class=\"h18-clean-checkbox\"><input data-field=\"mobileCloseOnSelect\" type=\"checkbox\"' + (node.props.mobileCloseOnSelect !== false ? ' checked' : '') + '> Luk efter valg</label><label class=\"h18-clean-checkbox\"><input data-field=\"mobileCloseOutside\" type=\"checkbox\"' + (node.props.mobileCloseOutside !== false ? ' checked' : '') + '> Luk ved klik udenfor</label>'; }
            html += '<p class=\"description\">Mobil bruger de samme menupunkter som Desktop; kun præsentationen ændres.</p></div>';
"""
core = regex_once(core, menu_inspector_pattern, lambda m: menu_inspector_repl, 'menu inspector UX')

# Canvas menu preview: show an actual hamburger control on the Mobile breakpoint.
old_preview = """                const nav = document.createElement('div');
                nav.className = 'h18-clean-menu-preview';
                nav.style.display = 'flex';
                nav.style.width = '100%';
                nav.style.flexDirection = node.props.orientation === 'vertical' ? 'column' : 'row';
                nav.style.flexWrap = node.props.mobileMode === 'wrap' ? 'wrap' : 'nowrap';
                nav.style.justifyContent = ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-end';
                nav.style.alignItems = node.props.orientation === 'vertical' ? ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-start' : 'center';
                nav.style.gap = String(node.props.menuGap || 24) + 'px';
                nav.style.fontSize = String(node.props.fontSize || 16) + 'px';
                nav.style.fontWeight = String(node.props.fontWeight || 600);
                const items = Array.isArray(menuDef.items) ? menuDef.items.filter(function (item) { return parseInt(item.parent || 0, 10) === 0; }) : [];
                if (!items.length) {
                    nav.textContent = menuDef.name || 'Tom menu';
                } else {
                    items.forEach(function (item) {
                        const label = document.createElement('span');
                        label.textContent = String(item.title || 'Menupunkt');
                        label.style.color = node.props.textColor || '#ffffff';
                        label.style.whiteSpace = 'nowrap';
                        nav.appendChild(label);
                    });
                }
                wrap.appendChild(nav);
"""
new_preview = """                const nav = document.createElement('div');
                nav.className = 'h18-clean-menu-preview';
                nav.style.display = 'flex';
                nav.style.width = '100%';
                nav.style.flexDirection = node.props.orientation === 'vertical' ? 'column' : 'row';
                nav.style.flexWrap = node.props.mobileMode === 'wrap' ? 'wrap' : 'nowrap';
                nav.style.justifyContent = ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-end';
                nav.style.alignItems = node.props.orientation === 'vertical' ? ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-start' : 'center';
                nav.style.gap = String(node.props.menuGap || 24) + 'px';
                nav.style.fontSize = String(node.props.fontSize || 16) + 'px';
                nav.style.fontWeight = String(node.props.fontWeight || 600);
                const items = Array.isArray(menuDef.items) ? menuDef.items.filter(function (item) { return parseInt(item.parent || 0, 10) === 0; }) : [];
                const previewDevice = document.body ? String(document.body.getAttribute('data-h18-clean-device') || 'desktop') : 'desktop';
                if (previewDevice === 'mobile' && node.props.mobileMode === 'hamburger') {
                    nav.classList.add('is-mobile-hamburger-preview');
                    nav.style.justifyContent = node.props.align === 'left' ? 'flex-start' : 'flex-end';
                    const toggle = document.createElement('button');
                    toggle.type = 'button';
                    toggle.className = 'h18-vd-menu-preview-toggle';
                    toggle.textContent = '☰ Menu';
                    toggle.style.color = node.props.textColor || '#ffffff';
                    toggle.addEventListener('click', function (event) {
                        event.preventDefault(); event.stopPropagation();
                        nav.classList.toggle('is-open');
                        toggle.textContent = nav.classList.contains('is-open') ? '✕ Luk' : '☰ Menu';
                    });
                    nav.appendChild(toggle);
                    const previewList = document.createElement('div');
                    previewList.className = 'h18-vd-menu-preview-mobile-list is-' + (node.props.mobilePresentation || 'dropdown');
                    items.forEach(function (item) { const label = document.createElement('span'); label.textContent = String(item.title || 'Menupunkt'); label.style.color = node.props.textColor || '#ffffff'; previewList.appendChild(label); });
                    nav.appendChild(previewList);
                } else if (!items.length) {
                    nav.textContent = menuDef.name || 'Tom menu';
                } else {
                    items.forEach(function (item) {
                        const label = document.createElement('span');
                        label.textContent = String(item.title || 'Menupunkt');
                        label.style.color = node.props.textColor || '#ffffff';
                        label.style.whiteSpace = 'nowrap';
                        nav.appendChild(label);
                    });
                }
                wrap.appendChild(nav);
"""
core = replace_once(core, old_preview, new_preview, 'mobile menu canvas preview')
CORE.write_text(core, encoding='utf-8')

MENU_CSS.write_text("""/* Visual Designer Manager 0.1.54 · Menu Inspector / mobile canvas preview */
.h18-vd-menu-group{margin:0 0 14px;padding:12px;border:1px solid #dcdcde;border-radius:6px;background:#fff}
.h18-vd-menu-group h3{margin:0 0 10px;font-size:13px;text-transform:uppercase;letter-spacing:.04em;color:#50575e}
.h18-vd-menu-preview-toggle{appearance:none;border:1px solid currentColor;border-radius:4px;background:transparent;padding:6px 10px;font:inherit;cursor:pointer}
.h18-clean-menu-preview.is-mobile-hamburger-preview{position:relative;align-items:center}
.h18-vd-menu-preview-mobile-list{display:none;position:absolute;z-index:50;top:calc(100% + 6px);right:0;min-width:220px;flex-direction:column;gap:10px;padding:16px;background:#30382a;box-shadow:0 10px 28px rgba(0,0,0,.22)}
.h18-clean-menu-preview.is-open .h18-vd-menu-preview-mobile-list{display:flex}
.h18-vd-menu-preview-mobile-list.is-panel-left,.h18-vd-menu-preview-mobile-list.is-panel-right{top:40px;min-width:min(300px,82vw);max-height:70vh;overflow:auto}
.h18-vd-menu-preview-mobile-list.is-panel-left{left:0;right:auto}
.h18-vd-menu-preview-mobile-list.is-panel-right{left:auto;right:0}
""", encoding='utf-8')

# -----------------------------------------------------------------------------
# Frontend / composite Preview: robust hamburger, dropdown/side-panel, Esc,
# outside-click and close-after-selection.
# -----------------------------------------------------------------------------
renderer = RENDERER.read_text(encoding='utf-8')
renderer = replace_once(
    renderer,
    "            $mobileMode = in_array((string) ($props['mobileMode'] ?? 'hamburger'), ['hamburger', 'vertical', 'wrap'], true) ? (string) $props['mobileMode'] : 'hamburger';\n            $textColor =",
    "            $mobileMode = in_array((string) ($props['mobileMode'] ?? 'hamburger'), ['hamburger', 'vertical', 'wrap'], true) ? (string) $props['mobileMode'] : 'hamburger';\n            $mobilePresentation = in_array((string) ($props['mobilePresentation'] ?? 'dropdown'), ['dropdown', 'panel-right', 'panel-left'], true) ? (string) $props['mobilePresentation'] : 'dropdown';\n            $mobileCloseOnSelect = !array_key_exists('mobileCloseOnSelect', $props) || !empty($props['mobileCloseOnSelect']);\n            $mobileCloseOutside = !array_key_exists('mobileCloseOutside', $props) || !empty($props['mobileCloseOutside']);\n            $textColor =",
    'renderer menu mobile props'
)
renderer = replace_once(
    renderer,
    "            $background = !empty($props['backgroundTransparent']) ? 'transparent' : (sanitize_hex_color((string) ($props['background'] ?? '#30382a')) ?: '#30382a');",
    "            $baseBackground = sanitize_hex_color((string) ($props['background'] ?? '#30382a')) ?: '#30382a';\n            $background = !empty($props['backgroundTransparent']) ? 'transparent' : $baseBackground;",
    'renderer menu base background'
)
renderer = replace_once(
    renderer,
    "                    'menu_class' => 'h18-clean-front-menu-list',\n                    'depth' => 2,",
    "                    'menu_class' => 'h18-clean-front-menu-list',\n                    'menu_id' => 'h18-clean-menu-list-' . $id,\n                    'depth' => 2,",
    'renderer menu id'
)
renderer = replace_once(
    renderer,
    "                . '--h18-menu-size:' . $fontSize . 'px;--h18-menu-weight:' . $fontWeight . ';--h18-menu-justify:' . $justify . ';--h18-menu-items-align:' . $itemsAlign . ';';",
    "                . '--h18-menu-size:' . $fontSize . 'px;--h18-menu-weight:' . $fontWeight . ';--h18-menu-justify:' . $justify . ';--h18-menu-items-align:' . $itemsAlign . ';--h18-menu-panel-bg:' . $baseBackground . ';';",
    'renderer menu panel variable'
)
renderer = replace_once(
    renderer,
    "            return '<nav id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-menu h18-clean-front-menu--' . esc_attr($orientation) . '\" data-mobile-mode=\"' . esc_attr($mobileMode) . '\" aria-label=\"Navigation\" style=\"' . esc_attr($menuStyle) . '\"><button type=\"button\" class=\"h18-clean-front-menu-toggle\" aria-expanded=\"false\">☰ Menu</button>' . $rendered . '</nav>';",
    "            return '<nav id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-menu h18-clean-front-menu--' . esc_attr($orientation) . '\" data-mobile-mode=\"' . esc_attr($mobileMode) . '\" data-mobile-presentation=\"' . esc_attr($mobilePresentation) . '\" data-close-on-select=\"' . ($mobileCloseOnSelect ? '1' : '0') . '\" data-close-outside=\"' . ($mobileCloseOutside ? '1' : '0') . '\" aria-label=\"Navigation\" style=\"' . esc_attr($menuStyle) . '\"><button type=\"button\" class=\"h18-clean-front-menu-toggle\" aria-expanded=\"false\" aria-controls=\"h18-clean-menu-list-' . $id . '\">☰ Menu</button>' . $rendered . '</nav>';",
    'renderer nav attrs'
)

# Append panel/mobile overrides immediately after the existing menu CSS echo.
menu_css_marker = "        echo '.h18-clean-front-text-heading{margin:0 0 8px;line-height:1.2}';"
menu_css_extra = """        echo '@media(max-width:782px){.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="dropdown"].is-open .h18-clean-front-menu-list{background:var(--h18-menu-panel-bg);padding:12px;box-sizing:border-box}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"]{position:relative}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"].is-open:before{content:"";position:fixed;inset:0;background:rgba(0,0,0,.38);z-index:99990}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"].is-open .h18-clean-front-menu-list{display:flex;position:fixed;top:0;bottom:0;width:min(340px,88vw);max-width:88vw;z-index:99991;overflow:auto;box-sizing:border-box;background:var(--h18-menu-panel-bg);padding:68px 24px 24px;gap:18px;align-items:flex-start;justify-content:flex-start}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="panel-right"].is-open .h18-clean-front-menu-list{right:0;left:auto}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="panel-left"].is-open .h18-clean-front-menu-list{left:0;right:auto}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"].is-open .h18-clean-front-menu-toggle{position:fixed;top:16px;z-index:99992;background:var(--h18-menu-panel-bg)}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="panel-right"].is-open .h18-clean-front-menu-toggle{right:16px}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation="panel-left"].is-open .h18-clean-front-menu-toggle{left:16px;margin-left:0}.h18-clean-front-menu[data-mobile-mode="hamburger"][data-mobile-presentation^="panel-"] .sub-menu{display:block!important;position:static!important;background:transparent!important;padding:8px 0 0 16px!important}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list a{white-space:normal}}';
""" + menu_css_marker
renderer = replace_once(renderer, menu_css_marker, menu_css_extra, 'renderer mobile panel css')

behavior = r'''(function(){function setOpen(n,o){if(!n)return;n.classList.toggle("is-open",o);var b=n.querySelector(".h18-clean-front-menu-toggle");if(b){b.setAttribute("aria-expanded",o?"true":"false");b.textContent=o?"✕ Luk":"☰ Menu";if(o){window.setTimeout(function(){var first=n.querySelector(".h18-clean-front-menu-list a");if(first)first.focus();},0);}}}document.addEventListener("click",function(e){var b=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu-toggle"):null;if(b){var n=b.closest(".h18-clean-front-menu");if(n){setOpen(n,!n.classList.contains("is-open"));}return;}var link=e.target&&e.target.closest?e.target.closest(".h18-clean-front-menu.is-open .h18-clean-front-menu-list a"):null;if(link){var nav=link.closest(".h18-clean-front-menu");if(nav&&nav.getAttribute("data-close-on-select")!=="0"){setOpen(nav,false);}return;}document.querySelectorAll(".h18-clean-front-menu.is-open[data-close-outside=\"1\"]").forEach(function(nav){if(!nav.contains(e.target)){setOpen(nav,false);}});});document.addEventListener("keydown",function(e){if(e.key!=="Escape")return;document.querySelectorAll(".h18-clean-front-menu.is-open").forEach(function(nav){setOpen(nav,false);var b=nav.querySelector(".h18-clean-front-menu-toggle");if(b)b.focus();});});})();'''
renderer = regex_once(
    renderer,
    r"            \. '<script>document\.addEventListener\(\\\"click\\\",function\(e\)\{var b=e\.target\.closest\(\\\"\.h18-clean-front-menu-toggle\\\"\);if\(!b\)return;var n=b\.closest\(\\\"\.h18-clean-front-menu\\\"\);if\(!n\)return;var open=!n\.classList\.contains\(\\\"is-open\\\"\);n\.classList\.toggle\(\\\"is-open\\\",open\);b\.setAttribute\(\\\"aria-expanded\\\",open\?\\\"true\\\":\\\"false\\\"\);\}\);</script></body></html>';",
    "            . '<script>" + behavior.replace("'", "\\'") + "</script></body></html>';",
    'standalone menu behavior'
)
renderer = regex_once(
    renderer,
    r"        echo '<script id=\\\"h18-clean-menu-js\\\">document\.addEventListener\(\\\"click\\\",function\(e\)\{var b=e\.target\.closest\(\\\"\.h18-clean-front-menu-toggle\\\"\);if\(!b\)return;var n=b\.closest\(\\\"\.h18-clean-front-menu\\\"\);if\(!n\)return;var open=!n\.classList\.contains\(\\\"is-open\\\"\);n\.classList\.toggle\(\\\"is-open\\\",open\);b\.setAttribute\(\\\"aria-expanded\\\",open\?\\\"true\\\":\\\"false\\\"\);\}\);</script>';",
    "        echo '<script id=\"h18-clean-menu-js\">" + behavior.replace("'", "\\'") + "</script>';",
    'frontend menu behavior'
)
RENDERER.write_text(renderer, encoding='utf-8')

# -----------------------------------------------------------------------------
# Page Designer: one real WordPress post-status control inside the existing Save
# form, so Publish/Draft also saves current Visual Designer changes atomically.
# -----------------------------------------------------------------------------
editor = EDITOR.read_text(encoding='utf-8')
status_ui_anchor = """        echo '<div class=\"h18-clean-toolbar\">';
        echo '<button type=\"button\" class=\"button\" id=\"h18-clean-undo\" disabled>↶ Fortryd</button>';
"""
status_ui = """        echo '<div class=\"h18-clean-toolbar\">';
        $isPublished = (string) $post->post_status === 'publish';
        $statusLabel = $isPublished ? 'Publiceret' : 'Kladde';
        echo '<span class=\"h18-vd-page-status ' . ($isPublished ? 'is-published' : 'is-draft') . '\"><strong>Status:</strong> ' . esc_html($statusLabel) . '</span>';
        if ($isPublished) {
            echo '<button type=\"submit\" class=\"button h18-vd-status-action\" name=\"post_status_action\" value=\"draft\" onclick=\"return confirm(\\'Gør siden til kladde? Den fjernes fra offentlig visning, og aktuelle Designer-ændringer gemmes samtidig.\\');\">Gem &amp; gør til kladde</button>';
        } elseif (current_user_can('publish_pages')) {
            echo '<button type=\"submit\" class=\"button button-primary h18-vd-status-action\" name=\"post_status_action\" value=\"publish\">Gem &amp; publicér</button>';
        }
        echo '<button type=\"button\" class=\"button\" id=\"h18-clean-undo\" disabled>↶ Fortryd</button>';
"""
editor = replace_once(editor, status_ui_anchor, status_ui, 'page status toolbar')

old_save_state = """            $currentVersion = max(0, (int) get_post_meta($postId, LayoutModel::VERSION_META, true));
            $sameModel = hash_equals(LayoutModel::structuralDigest(LayoutModel::get($postId)), LayoutModel::structuralDigest($normalized));
            $sameShell = TemplateLayoutModel::pageChoice($postId, 'header') === ($headerChoice !== '' ? $headerChoice : 'auto')
                && TemplateLayoutModel::pageChoice($postId, 'footer') === ($footerChoice !== '' ? $footerChoice : 'auto');
            if ($currentVersion > 0 && $sameModel && $sameShell) {
                DiagnosticStore::append($postId, 'save_noop', ['version' => $currentVersion, 'reason' => 'canonical-model-and-shell-unchanged']);
                self::redirect($postId, 'success', 'Ingen ændringer siden seneste gemte version. Der blev ikke oprettet en ny version.');
            }
            $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : 'Gemt Visual Designer-layout');
            TemplateLayoutModel::setPageChoice($postId, 'header', $headerChoice);
            TemplateLayoutModel::setPageChoice($postId, 'footer', $footerChoice);
"""
new_save_state = """            $currentVersion = max(0, (int) get_post_meta($postId, LayoutModel::VERSION_META, true));
            $sameModel = hash_equals(LayoutModel::structuralDigest(LayoutModel::get($postId)), LayoutModel::structuralDigest($normalized));
            $sameShell = TemplateLayoutModel::pageChoice($postId, 'header') === ($headerChoice !== '' ? $headerChoice : 'auto')
                && TemplateLayoutModel::pageChoice($postId, 'footer') === ($footerChoice !== '' ? $footerChoice : 'auto');
            $statusAction = sanitize_key((string) wp_unslash($_POST['post_status_action'] ?? ''));
            $desiredStatus = in_array($statusAction, ['publish', 'draft'], true) ? $statusAction : '';
            $currentPostStatus = (string) get_post_status($postId);
            $statusChanged = $desiredStatus !== '' && $desiredStatus !== $currentPostStatus;
            if ($desiredStatus === 'publish' && !current_user_can('publish_pages')) {
                throw new \\RuntimeException('Du har ikke rettighed til at publicere sider.');
            }
            if ($currentVersion > 0 && $sameModel && $sameShell && !$statusChanged) {
                DiagnosticStore::append($postId, 'save_noop', ['version' => $currentVersion, 'reason' => 'canonical-model-shell-and-status-unchanged']);
                self::redirect($postId, 'success', 'Ingen ændringer siden seneste gemte version. Der blev ikke oprettet en ny version.');
            }
            if ($currentVersion > 0 && $sameModel && $sameShell) {
                $version = $currentVersion;
            } else {
                $version = LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), $note !== '' ? $note : 'Gemt Visual Designer-layout');
                TemplateLayoutModel::setPageChoice($postId, 'header', $headerChoice);
                TemplateLayoutModel::setPageChoice($postId, 'footer', $footerChoice);
            }
            if ($statusChanged) {
                $updatedPost = wp_update_post(['ID' => $postId, 'post_status' => $desiredStatus], true);
                if (is_wp_error($updatedPost)) {
                    throw new \\RuntimeException($updatedPost->get_error_message());
                }
                DiagnosticStore::append($postId, 'page_status_changed', ['from' => $currentPostStatus, 'to' => $desiredStatus, 'version' => $version]);
            }
"""
editor = replace_once(editor, old_save_state, new_save_state, 'save plus page status')
old_redirect = "            self::redirect($postId, 'success', 'Visual Designer-layout gemt og verificeret som version v' . $version . '.');"
new_redirect = "            $statusMessage = $statusChanged ? ($desiredStatus === 'publish' ? ' Siden er publiceret.' : ' Siden er nu kladde og ikke længere offentligt publiceret.') : '';\n            self::redirect($postId, 'success', 'Visual Designer-layout gemt og verificeret som version v' . $version . '.' . $statusMessage);"
editor = replace_once(editor, old_redirect, new_redirect, 'status save message')
EDITOR.write_text(editor, encoding='utf-8')

# -----------------------------------------------------------------------------
# Documentation / release metadata.
# -----------------------------------------------------------------------------
history = json.loads(HISTORY.read_text(encoding='utf-8'))
versions = history.setdefault('versions', [])
if not any(str(v.get('version')) == '0.1.54' for v in versions):
    versions.insert(0, {
        'version': '0.1.54',
        'date': '2026-08-29',
        'items': [
            'VD-MENU-UX-002: Manager → Menu bruger WordPress-menuen som eneste datakilde og giver drag-and-drop/pilebaseret rækkefølge samt tydelig undermenu-parent.',
            'Menu Inspector er opdelt i Indhold, Layout, Tekst, Farver og Mobil med direkte link til Redigér menupunkter.',
            'Hamburger-menu kan vises som dropdown, panel fra højre eller panel fra venstre og kan lukke efter valg, ved klik udenfor og med Esc.',
            'Mobilmenuens åbne/lukkede tilstand bruger aria-expanded/aria-controls og bevarer aktiv-side styling.',
            'VD-PAGE-STATUS-001: Side-Designer viser rigtig WordPress-status og kan Gem & publicér eller Gem & gør til kladde i samme sikre Save-flow.'
        ]
    })
HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

old_notes = NOTES.read_text(encoding='utf-8').strip() if NOTES.exists() else ''
head = """<h4>0.1.54 – Menu UX og Kladde/Publicér</h4><ul><li><strong>VD-MENU-UX-002:</strong> Manager → Menu får drag-and-drop/pilebaseret rækkefølge, tydelig undermenu-parent og beholder WordPress-menuen som eneste datakilde.</li><li>Menu Inspector er opdelt i Indhold, Layout, Tekst, Farver og Mobil og linker direkte til menupunkterne.</li><li>Mobil Hamburger kan åbne som Dropdown, Panel fra højre eller Panel fra venstre; Esc, klik udenfor og luk efter valg understøttes.</li><li><strong>VD-PAGE-STATUS-001:</strong> Side-Designer viser WordPress-status og har Gem &amp; publicér / Gem &amp; gør til kladde uden en separat VDM-status.</li></ul>"""
NOTES.write_text(head + ('\n' + old_notes if old_notes else '') + '\n', encoding='utf-8')

tech = TECH.read_text(encoding='utf-8') if TECH.exists() else ''
contract = """

## 0.1.54 – Menu UX og sidestatus

### VD-MENU-UX-002
- WordPress `nav_menu`/`nav_menu_item` er fortsat canonical datakilde for navigation. VDM må ikke oprette en parallel menustruktur i Header/Footer.
- Manager → Menu er den primære brugervenlige redigering: rækkefølge kan ændres med drag-and-drop og tastaturvenlige pile; undermenu vælges eksplicit via parent.
- Menu-elementet gemmer kun menu-reference og design/responsive egenskaber.
- Desktop/Laptop/Mobil bruger samme menupunkter. Breakpointet ændrer præsentationen, ikke datasættet.
- Hamburger understøtter Dropdown, Panel fra højre og Panel fra venstre. `aria-expanded`, `aria-controls`, Esc, klik udenfor og valgfri luk-efter-valg er faste accessibility/UX-kontrakter.

### VD-PAGE-STATUS-001
- Side-Designer viser og ændrer WordPress' rigtige `post_status`; der oprettes ingen separat Visual Designer-publiceringsstatus.
- Kladde kan publiceres fra Designer, hvis brugeren har `publish_pages`.
- En publiceret side kan gøres til kladde med eksplicit bekræftelse.
- Statusændringen går gennem samme Save-submit som canonical layoutet, så aktuelle Designer-ændringer ikke tabes ved publicering/afpublicering.
- Header/Footer templates har ikke denne kontrol; den gælder almindelige WordPress-sider.
"""
if '### VD-MENU-UX-002' not in tech:
    TECH.write_text(tech.rstrip() + contract + '\n', encoding='utf-8')

STATUS.write_text("""# Visual Designer Manager 0.1.54 status

## VD-MENU-UX-002
- WordPress-menuen er eneste navigation-datakilde.
- Manager → Menu: drag-and-drop + op/ned-knapper, menutekst og tydelig parent/undermenu.
- Menu Inspector: Indhold, Layout, Tekst, Farver, Mobil samt link til Manager-menuen.
- Hamburger: dropdown, panel højre, panel venstre; Esc, outside click, close-on-select og ARIA.
- Mobil canvas viser en rigtig hamburger-preview på Mobil-breakpoint.

## VD-PAGE-STATUS-001
- Side-Designer viser Kladde/Publiceret fra WordPress `post_status`.
- Gem & publicér gemmer canonical layout og publicerer i samme submit.
- Gem & gør til kladde kræver bekræftelse og gemmer layout samtidig.
- Header/Footer påvirkes ikke.
""", encoding='utf-8')

print('Applied Visual Designer Manager 0.1.54 Menu UX + publish/draft patch')
