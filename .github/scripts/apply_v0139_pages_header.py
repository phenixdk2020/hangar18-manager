from pathlib import Path
import json
import re

ROOT = Path('.')


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


def write(path, text):
    (ROOT / path).write_text(text, encoding='utf-8')


def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    return text.replace(old, new, 1)


# 1) Version + WordPress menu payload for the shared editor runtime.
path = 'clean/hangar18-manager/hangar18-manager.php'
s = read(path)
s = s.replace(' * Version: 0.1.38', ' * Version: 0.1.39', 1)
s = s.replace("define('H18_CLEAN_VERSION', '0.1.38');", "define('H18_CLEAN_VERSION', '0.1.39');", 1)
menu_payload = r'''    $menuPayload = array_values(array_map(static function ($menu): array {
        $items = wp_get_nav_menu_items((int) $menu->term_id);
        $items = is_array($items) ? $items : [];
        return [
            'id' => (int) $menu->term_id,
            'name' => (string) $menu->name,
            'items' => array_values(array_map(static function ($item): array {
                return [
                    'id' => (int) $item->ID,
                    'title' => wp_strip_all_tags((string) $item->title),
                    'url' => esc_url_raw((string) $item->url),
                    'parent' => (int) $item->menu_item_parent,
                ];
            }, $items)),
        ];
    }, wp_get_nav_menus()));

'''
s = replace_once(s, "    wp_enqueue_script(\n        'h18-clean-editor-v018-core',", menu_payload + "    wp_enqueue_script(\n        'h18-clean-editor-v018-core',", 'menu payload insertion')
s = replace_once(s, "        'pages' => array_values(array_map(static function ($page): array { return ['id' => (int) $page->ID, 'title' => (string) $page->post_title]; }, get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC']))),\n", "        'pages' => array_values(array_map(static function ($page): array { return ['id' => (int) $page->ID, 'title' => (string) $page->post_title]; }, get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC']))),\n        'menus' => $menuPayload,\n", 'localized menu payload')
write(path, s)

# 2) Native page creation in Manager -> Sider.
path = 'clean/hangar18-manager/src/Admin/AdminController.php'
s = read(path)
s = replace_once(s, "    private const CLEAR_LOG_ACTION = 'h18_clean_clear_diagnostics';\n", "    private const CLEAR_LOG_ACTION = 'h18_clean_clear_diagnostics';\n    private const CREATE_PAGE_ACTION = 'h18_clean_create_page';\n", 'create page action const')
s = replace_once(s, "    private const CLEAR_LOG_NONCE = 'h18_clean_clear_diagnostics';\n", "    private const CLEAR_LOG_NONCE = 'h18_clean_clear_diagnostics';\n    private const CREATE_PAGE_NONCE = 'h18_clean_create_page';\n", 'create page nonce const')
s = replace_once(s, "        add_action('admin_post_' . self::CLEAR_LOG_ACTION, [self::class, 'clearDiagnostics']);\n", "        add_action('admin_post_' . self::CLEAR_LOG_ACTION, [self::class, 'clearDiagnostics']);\n        add_action('admin_post_' . self::CREATE_PAGE_ACTION, [self::class, 'createPage']);\n", 'create page action register')
old_pages = """        self::open('Sider', 'Alle WordPress-sider med Visual Designer-status');
        echo '<div class=\"h18-manager-toolbar\"><a class=\"button button-primary\" href=\"' . esc_url(admin_url('post-new.php?post_type=page')) . '\">+ Ny WordPress-side</a><a class=\"button\" href=\"' . esc_url(self::designerUrl()) . '\">Åbn Designer</a></div>';
"""
new_pages = """        $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));
        self::open('Sider', 'Alle WordPress-sider med Visual Designer-status');
        if ($message !== '') { echo '<div class=\"notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible\"><p>' . esc_html($message) . '</p></div>'; }
        echo '<div class=\"h18-manager-card h18-manager-create-page\"><h2>Ny side</h2><p class=\"description\">Opret siden direkte i Visual Designer Manager. Efter oprettelse åbnes den i Designer.</p>';
        echo '<form method=\"post\" action=\"' . esc_url(admin_url('admin-post.php')) . '\" class=\"h18-manager-page-create-form\">';
        wp_nonce_field(self::CREATE_PAGE_NONCE);
        echo '<input type=\"hidden\" name=\"action\" value=\"' . esc_attr(self::CREATE_PAGE_ACTION) . '\">';
        echo '<label><strong>Titel</strong><input type=\"text\" name=\"page_title\" required placeholder=\"Ny side\"></label>';
        echo '<label><strong>Slug</strong><input type=\"text\" name=\"page_slug\" placeholder=\"automatisk-fra-titel\"></label>';
        echo '<label><strong>Overordnet side</strong><select name=\"page_parent\"><option value=\"0\">Ingen · topniveau</option>';
        foreach ($pages as $parentPage) { echo '<option value=\"' . esc_attr((string) $parentPage->ID) . '\">' . esc_html((string) $parentPage->post_title) . '</option>'; }
        echo '</select></label>';
        echo '<label><strong>Status</strong><select name=\"page_status\"><option value=\"draft\">Kladde</option>' . (current_user_can('publish_pages') ? '<option value=\"publish\">Publiceret</option>' : '') . '</select></label>';
        echo '<button class=\"button button-primary\" type=\"submit\">Opret og åbn Designer</button></form></div>';
        echo '<div class=\"h18-manager-toolbar\"><a class=\"button\" href=\"' . esc_url(admin_url('post-new.php?post_type=page')) . '\">WordPress-editor</a><a class=\"button\" href=\"' . esc_url(self::designerUrl()) . '\">Åbn Designer</a></div>';
"""
s = replace_once(s, old_pages, new_pages, 'pages create UI')
create_method = r'''
    public static function createPage(): void
    {
        self::guard();
        check_admin_referer(self::CREATE_PAGE_NONCE);

        $title = sanitize_text_field((string) wp_unslash($_POST['page_title'] ?? ''));
        if ($title === '') {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Sidetitel mangler.']));
            exit;
        }

        $slug = sanitize_title((string) wp_unslash($_POST['page_slug'] ?? ''));
        $parent = absint($_POST['page_parent'] ?? 0);
        if ($parent > 0 && get_post_type($parent) !== 'page') { $parent = 0; }

        $status = sanitize_key((string) ($_POST['page_status'] ?? 'draft'));
        if ($status !== 'publish' || !current_user_can('publish_pages')) { $status = 'draft'; }

        $postId = wp_insert_post([
            'post_type' => 'page',
            'post_title' => $title,
            'post_name' => $slug,
            'post_parent' => $parent,
            'post_status' => $status,
            'post_content' => '',
        ], true);

        if (is_wp_error($postId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kunne ikke oprettes: ' . $postId->get_error_message()]));
            exit;
        }

        $postId = (int) $postId;
        if ($postId <= 0) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'WordPress returnerede ikke et gyldigt side-ID.']));
            exit;
        }

        wp_safe_redirect(self::designerUrl($postId));
        exit;
    }

'''
s = replace_once(s, "    public static function exportBackup(): void\n", create_method + "    public static function exportBackup(): void\n", 'create page method')
write(path, s)

# 3) Canonical Menu element.
path = 'clean/hangar18-manager/src/Model/LayoutModel.php'
s = read(path)
s = replace_once(s, "['section', 'container', 'text', 'image', 'button']", "['section', 'container', 'text', 'image', 'button', 'menu']", 'LayoutModel allowed menu type')
menu_props_php = r'''        if ($type === 'menu') {
            $orientation = strtolower((string) ($raw['orientation'] ?? 'horizontal'));
            if (!in_array($orientation, ['horizontal', 'vertical'], true)) { $orientation = 'horizontal'; }
            $align = strtolower((string) ($raw['align'] ?? 'right'));
            if (!in_array($align, ['left', 'center', 'right'], true)) { $align = 'right'; }
            $mobileMode = strtolower((string) ($raw['mobileMode'] ?? 'hamburger'));
            if (!in_array($mobileMode, ['hamburger', 'vertical', 'wrap'], true)) { $mobileMode = 'hamburger'; }
            return array_merge([
                'menuId' => absint($raw['menuId'] ?? 0),
                'orientation' => $orientation,
                'align' => $align,
                'mobileMode' => $mobileMode,
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#ffffff')) ?: '#ffffff',
                'hoverTextColor' => sanitize_hex_color((string) ($raw['hoverTextColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'activeTextColor' => sanitize_hex_color((string) ($raw['activeTextColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'background' => sanitize_hex_color((string) ($raw['background'] ?? '#30382a')) ?: '#30382a',
                'backgroundTransparent' => array_key_exists('backgroundTransparent', $raw) ? (bool) $raw['backgroundTransparent'] : true,
                'fontSize' => self::clamp($raw['fontSize'] ?? 16, 8, 64, 16),
                'fontWeight' => self::clamp($raw['fontWeight'] ?? 600, 100, 900, 600),
                'menuGap' => self::clamp($raw['menuGap'] ?? 24, 0, 120, 24),
                'paddingX' => self::clamp($raw['paddingX'] ?? 8, 0, 120, 8),
                'paddingY' => self::clamp($raw['paddingY'] ?? 8, 0, 120, 8),
                'radius' => self::clamp($raw['radius'] ?? 0, 0, 100, 0),
            ], $border);
        }
'''
s = replace_once(s, "        if ($type === 'image') {\n            $fit = strtolower((string) ($raw['fit'] ?? 'contain'));\n", menu_props_php + "        if ($type === 'image') {\n            $fit = strtolower((string) ($raw['fit'] ?? 'contain'));\n", 'LayoutModel menu props')
write(path, s)

# 4) Shared editor core Menu UX.
path = 'clean/hangar18-manager/assets/editor-v018-core.js'
s = read(path)
s = replace_once(s, "const TYPES = ['section', 'container', 'text', 'image', 'button'];", "const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu'];", 'editor TYPES menu')
s = replace_once(s, "function typeLabel(type) { return ({section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap'})", "function typeLabel(type) { return ({section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap',menu:'Menu'})", 'editor type label menu')
s = replace_once(s, "zIndex:'lag'})[String(field || '')]", "zIndex:'lag',menuId:'WordPress-menu',orientation:'menuretning',mobileMode:'mobilmenu',activeTextColor:'aktiv menufarve',backgroundTransparent:'gennemsigtig baggrund',menuGap:'menuafstand'})[String(field || '')]", 'editor field labels menu')
menu_props_js = r'''        if (type === 'menu') {
            return Object.assign(common, {
                menuId: parseInt(raw.menuId || 0, 10) || 0,
                orientation: ['horizontal', 'vertical'].includes(String(raw.orientation || '').toLowerCase()) ? String(raw.orientation).toLowerCase() : 'horizontal',
                align: ['left', 'center', 'right'].includes(String(raw.align || '').toLowerCase()) ? String(raw.align).toLowerCase() : 'right',
                mobileMode: ['hamburger', 'vertical', 'wrap'].includes(String(raw.mobileMode || '').toLowerCase()) ? String(raw.mobileMode).toLowerCase() : 'hamburger',
                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#ffffff',
                hoverTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.hoverTextColor || '')) ? String(raw.hoverTextColor).toLowerCase() : '#c3ae83',
                activeTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.activeTextColor || '')) ? String(raw.activeTextColor).toLowerCase() : '#c3ae83',
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#30382a',
                backgroundTransparent: raw.backgroundTransparent !== false,
                fontSize: clamp(parseInt(raw.fontSize || 16, 10) || 16, 8, 64),
                fontWeight: clamp(parseInt(raw.fontWeight || 600, 10) || 600, 100, 900),
                menuGap: clamp(parseInt(raw.menuGap || 24, 10) || 24, 0, 120),
                paddingX: clamp(parseInt(raw.paddingX || 8, 10) || 8, 0, 120),
                paddingY: clamp(parseInt(raw.paddingY || 8, 10) || 8, 0, 120),
                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100)
            });
        }
'''
s = replace_once(s, "        if (type === 'image') {\n            const fit =", menu_props_js + "        if (type === 'image') {\n            const fit =", 'editor normalize menu props')
s = replace_once(s, "const defaultRows = { section: 20, container: 16, text: 14, image: 20, button: 8 };", "const defaultRows = { section: 20, container: 16, text: 14, image: 20, button: 8, menu: 10 };", 'editor default menu rows')
menu_card = r'''        } else if (node.type === 'menu') {
            wrap.classList.add('h18-clean-node-preview--menu');
            const menus = Array.isArray(CFG.menus) ? CFG.menus : [];
            const menuDef = menus.find(function (entry) { return parseInt(entry.id || 0, 10) === parseInt(node.props.menuId || 0, 10); }) || null;
            wrap.style.display = 'flex';
            wrap.style.alignItems = 'center';
            wrap.style.boxSizing = 'border-box';
            wrap.style.padding = String(node.props.paddingY || 8) + 'px ' + String(node.props.paddingX || 8) + 'px';
            wrap.style.borderRadius = String(node.props.radius || 0) + 'px';
            wrap.style.background = node.props.backgroundTransparent === false ? (node.props.background || '#30382a') : 'transparent';
            if (!menuDef) {
                wrap.textContent = 'Vælg WordPress-menu i Inspector';
            } else {
                const nav = document.createElement('div');
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
            }
'''
# Only replace the cardContent occurrence (before renderInspector).
card_pos = s.find('    function cardContent(node)')
if card_pos < 0:
    raise SystemExit('Missing cardContent')
image_pos = s.find("        } else if (node.type === 'image') {", card_pos)
if image_pos < 0:
    raise SystemExit('Missing image branch in cardContent')
s = s[:image_pos] + menu_card + s[image_pos + len("        } else if (node.type === 'image') {"):]
# Fix duplicated closing fragment: menu_card deliberately ends before image body; restore image branch header.
s = s[:image_pos + len(menu_card)] + "        } else if (node.type === 'image') {" + s[image_pos + len(menu_card):]
# Add MENU to both visual type maps.
s = s.replace("{section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP'}", "{section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP',menu:'MENU'}")
# Insert Menu Inspector branch immediately before the image branch within renderInspector.
inspector_pos = s.find('    function renderInspector()')
if inspector_pos < 0:
    raise SystemExit('Missing renderInspector')
image_inspector_pos = s.find("        } else if (node.type === 'image') {", inspector_pos)
if image_inspector_pos < 0:
    raise SystemExit('Missing image branch in Inspector')
menu_inspector = r'''        } else if (node.type === 'menu') {
            html += '<label>WordPress-menu<select data-field="menuId"><option value="0">Vælg menu…</option>' + (Array.isArray(CFG.menus) ? CFG.menus.map(function (menu) { const id = parseInt(menu.id || 0, 10) || 0; return '<option value="' + id + '"' + (parseInt(node.props.menuId || 0, 10) === id ? ' selected' : '') + '>' + escapeHtml(String(menu.name || ('Menu ' + id))) + '</option>'; }).join('') : '') + '</select></label>';
            html += '<div class="h18-clean-field-grid"><label>Retning<select data-field="orientation"><option value="horizontal"' + (node.props.orientation !== 'vertical' ? ' selected' : '') + '>Vandret</option><option value="vertical"' + (node.props.orientation === 'vertical' ? ' selected' : '') + '>Lodret</option></select></label><label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Center</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label></div>';
            html += '<label>Mobilvisning<select data-field="mobileMode"><option value="hamburger"' + (node.props.mobileMode === 'hamburger' ? ' selected' : '') + '>Hamburger</option><option value="vertical"' + (node.props.mobileMode === 'vertical' ? ' selected' : '') + '>Lodret menu</option><option value="wrap"' + (node.props.mobileMode === 'wrap' ? ' selected' : '') + '>Ombryd menupunkter</option></select></label>';
            html += '<label class="h18-clean-checkbox"><input data-field="backgroundTransparent" type="checkbox"' + (node.props.backgroundTransparent !== false ? ' checked' : '') + '> Gennemsigtig baggrund</label>';
            html += '<div class="h18-clean-field-grid"><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#30382a') + '"></label><label>Tekst<input data-field="textColor" type="color" value="' + escapeAttr(node.props.textColor || '#ffffff') + '"></label><label>Hover<input data-field="hoverTextColor" type="color" value="' + escapeAttr(node.props.hoverTextColor || '#c3ae83') + '"></label><label>Aktiv side<input data-field="activeTextColor" type="color" value="' + escapeAttr(node.props.activeTextColor || '#c3ae83') + '"></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="64" value="' + (node.props.fontSize || 16) + '"></label><label>Tykkelse<select data-field="fontWeight">' + [300,400,500,600,700,800,900].map(function (v) { return '<option value="' + v + '"' + (parseInt(node.props.fontWeight || 600, 10) === v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label><label>Afstand px<input data-field="menuGap" type="number" min="0" max="120" value="' + (node.props.menuGap || 24) + '"></label><label>Padding X<input data-field="paddingX" type="number" min="0" max="120" value="' + (node.props.paddingX || 8) + '"></label><label>Padding Y<input data-field="paddingY" type="number" min="0" max="120" value="' + (node.props.paddingY || 8) + '"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 0) + '"></label></div>';
            html += '<p class="description">Menuen henter sine punkter fra WordPress. Visual Designer gemmer kun valgt menu og designindstillinger.</p>';
'''
s = s[:image_inspector_pos] + menu_inspector + s[image_inspector_pos:]
# Add menu-specific field handlers before image fit handler.
field_anchor = "                else if (field === 'fit') { current.props.fit ="
field_pos = s.find(field_anchor, inspector_pos)
if field_pos < 0:
    raise SystemExit('Missing inspector field handler anchor')
menu_fields = r'''                else if (field === 'menuId') { current.props.menuId = parseInt(control.value || 0, 10) || 0; }
                else if (field === 'orientation') { current.props.orientation = control.value === 'vertical' ? 'vertical' : 'horizontal'; }
                else if (field === 'mobileMode') { current.props.mobileMode = ['hamburger', 'vertical', 'wrap'].includes(control.value) ? control.value : 'hamburger'; }
                else if (field === 'activeTextColor') { current.props.activeTextColor = normalizeColor(control.value || '#c3ae83'); }
                else if (field === 'backgroundTransparent') { current.props.backgroundTransparent = !!control.checked; }
                else if (field === 'menuGap') { current.props.menuGap = clamp(parseInt(control.value || 24, 10) || 24, 0, 120); }
'''
s = s[:field_pos] + menu_fields + s[field_pos:]
write(path, s)

# 5) Header/Footer palette exposes Menu.
path = 'clean/hangar18-manager/src/Admin/GlobalDesignerController.php'
s = read(path)
s = replace_once(s, "foreach (['section' => 'Sektion', 'container' => 'Kasse', 'text' => 'Tekst', 'image' => 'Billede', 'button' => 'Knap'] as $type => $elementLabel)", "foreach (['section' => 'Sektion', 'container' => 'Kasse', 'text' => 'Tekst', 'image' => 'Billede', 'button' => 'Knap', 'menu' => 'Menu'] as $type => $elementLabel)", 'global designer menu palette')
s = s.replace("Logo kan laves som Billede. Menu-elementet kommer efter template-/Header-layoutet er accepteret.", "Logo laves som Billede. Menu-elementet henter en eksisterende WordPress-menu som datakilde; Visual Designer styrer placering, farver, afstand og mobilvisning.")
write(path, s)

# 6) Frontend renderer supports Menu as a canonical leaf, ready for later Header cutover.
path = 'clean/hangar18-manager/src/Frontend/Renderer.php'
s = read(path)
s = replace_once(s, "        add_action('wp_footer', [self::class, 'previewBadge'], 1000);\n", "        add_action('wp_footer', [self::class, 'previewBadge'], 1000);\n        add_action('wp_footer', [self::class, 'menuScript'], 1001);\n", 'renderer menu script register')
css_anchor = "        echo '.h18-clean-front-button-link:focus-visible{outline:3px solid var(--h18-btn-focus);outline-offset:2px}';\n"
menu_css = r'''        echo '.h18-clean-front-menu{display:flex;align-items:center;box-sizing:border-box}.h18-clean-front-menu-list{list-style:none;margin:0;padding:0;display:flex;align-items:center;gap:var(--h18-menu-gap);font-size:var(--h18-menu-size);font-weight:var(--h18-menu-weight);justify-content:var(--h18-menu-justify);width:100%}.h18-clean-front-menu--vertical .h18-clean-front-menu-list{flex-direction:column;align-items:var(--h18-menu-items-align)}.h18-clean-front-menu-list li{margin:0;padding:0}.h18-clean-front-menu-list a{color:var(--h18-menu-color);text-decoration:none;white-space:nowrap}.h18-clean-front-menu-list a:hover,.h18-clean-front-menu-list a:focus-visible{color:var(--h18-menu-hover)}.h18-clean-front-menu-list .current-menu-item>a,.h18-clean-front-menu-list .current_page_item>a{color:var(--h18-menu-active)}.h18-clean-front-menu-toggle{display:none;margin-left:auto;background:transparent;color:var(--h18-menu-color);border:1px solid currentColor;border-radius:4px;padding:6px 10px;font:inherit}.h18-clean-front-menu .sub-menu{list-style:none;margin:4px 0 0;padding:0 0 0 14px}.h18-clean-front-menu--horizontal .sub-menu{display:none;position:absolute;background:inherit;padding:8px}.h18-clean-front-menu--horizontal li:hover>.sub-menu,.h18-clean-front-menu--horizontal li:focus-within>.sub-menu{display:block}@media(max-width:782px){.h18-clean-front-menu[data-mobile-mode="vertical"] .h18-clean-front-menu-list{flex-direction:column;align-items:flex-start}.h18-clean-front-menu[data-mobile-mode="wrap"] .h18-clean-front-menu-list{flex-wrap:wrap}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-toggle{display:block}.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-list{display:none;flex-direction:column;align-items:flex-start;padding-top:8px}.h18-clean-front-menu[data-mobile-mode="hamburger"].is-open{flex-wrap:wrap}.h18-clean-front-menu[data-mobile-mode="hamburger"].is-open .h18-clean-front-menu-list{display:flex;flex-basis:100%}}';
'''
s = replace_once(s, css_anchor, css_anchor + menu_css, 'renderer menu css')
menu_script = r'''
    public static function menuScript(): void
    {
        if (!is_singular('page')) { return; }
        echo '<script id="h18-clean-menu-js">document.addEventListener("click",function(e){var b=e.target.closest(".h18-clean-front-menu-toggle");if(!b)return;var n=b.closest(".h18-clean-front-menu");if(!n)return;var open=!n.classList.contains("is-open");n.classList.toggle("is-open",open);b.setAttribute("aria-expanded",open?"true":"false");});</script>';
    }

'''
s = replace_once(s, "    public static function previewKey(int $userId, int $postId, string $token): string\n", menu_script + "    public static function previewKey(int $userId, int $postId, string $token): string\n", 'renderer menu script')
menu_branch = r'''        if ($type === 'menu') {
            $menuId = absint($props['menuId'] ?? 0);
            $orientation = (string) ($props['orientation'] ?? 'horizontal') === 'vertical' ? 'vertical' : 'horizontal';
            $align = in_array((string) ($props['align'] ?? 'right'), ['left', 'center', 'right'], true) ? (string) $props['align'] : 'right';
            $mobileMode = in_array((string) ($props['mobileMode'] ?? 'hamburger'), ['hamburger', 'vertical', 'wrap'], true) ? (string) $props['mobileMode'] : 'hamburger';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#ffffff')) ?: '#ffffff';
            $hoverColor = sanitize_hex_color((string) ($props['hoverTextColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $activeColor = sanitize_hex_color((string) ($props['activeTextColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $background = !empty($props['backgroundTransparent']) ? 'transparent' : (sanitize_hex_color((string) ($props['background'] ?? '#30382a')) ?: '#30382a');
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
                    'depth' => 2,
                ]);
                $rendered = is_string($candidate) ? $candidate : '';
            }
            if ($rendered === '') {
                $rendered = '<ul class="h18-clean-front-menu-list"><li><span>Vælg menu i Visual Designer</span></li></ul>';
            }
            $menuStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';padding:' . $paddingY . 'px ' . $paddingX . 'px;'
                . '--h18-menu-color:' . $textColor . ';--h18-menu-hover:' . $hoverColor . ';--h18-menu-active:' . $activeColor . ';--h18-menu-gap:' . $gap . 'px;'
                . '--h18-menu-size:' . $fontSize . 'px;--h18-menu-weight:' . $fontWeight . ';--h18-menu-justify:' . $justify . ';--h18-menu-items-align:' . $itemsAlign . ';';
            return '<nav id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-menu h18-clean-front-menu--' . esc_attr($orientation) . '" data-mobile-mode="' . esc_attr($mobileMode) . '" aria-label="Navigation" style="' . esc_attr($menuStyle) . '"><button type="button" class="h18-clean-front-menu-toggle" aria-expanded="false">☰ Menu</button>' . $rendered . '</nav>';
        }

'''
s = replace_once(s, "        if ($type === 'button') {\n", menu_branch + "        if ($type === 'button') {\n", 'renderer menu node')
write(path, s)

# 7) Model QA includes Menu contract.
path = '.github/scripts/v0125_model_qa.php'
s = read(path)
menu_qa = r'''
/* Menu is a canonical leaf whose content comes from a WordPress menu reference. */
$menuModel = LayoutModel::normalize([
    'nodes' => [
        [
            'id' => 'section-menu', 'type' => 'section', 'parentId' => '', 'order' => 10,
            'geometry' => vdGeometry(0, 0, 120, 12),
            'props' => ['background' => '#30382a', 'padding' => 0, 'minHeightRows' => 12],
        ],
        [
            'id' => 'menu-a', 'type' => 'menu', 'parentId' => 'section-menu', 'order' => 10,
            'geometry' => vdGeometry(40, 1, 80, 10),
            'props' => ['menuId' => 6, 'orientation' => 'horizontal', 'align' => 'right', 'mobileMode' => 'hamburger', 'textColor' => '#FFFFFF', 'menuGap' => 28],
        ],
    ],
]);
$menuNode = null;
foreach ($menuModel['nodes'] as $node) { if (($node['id'] ?? '') === 'menu-a') { $menuNode = $node; break; } }
vdAssert(is_array($menuNode), 'Menu disappeared during canonical normalization.');
vdAssert(($menuNode['type'] ?? '') === 'menu', 'Menu canonical type was not retained.');
vdAssert((int) ($menuNode['props']['menuId'] ?? 0) === 6, 'Menu WordPress source ID was not retained.');
vdAssert(($menuNode['props']['mobileMode'] ?? '') === 'hamburger', 'Menu mobile mode was not retained.');
vdAssert(($menuNode['props']['textColor'] ?? '') === '#ffffff', 'Menu text color was not normalized.');

'''
s = replace_once(s, "/* Seed phase-1 single Header/Footer storage exactly as an existing 0.1.23 site could have it. */\n", menu_qa + "/* Seed phase-1 single Header/Footer storage exactly as an existing 0.1.23 site could have it. */\n", 'menu model QA')
write(path, s)

# 8) Release history and notes.
path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(path))
history = [row for row in history if row.get('version') != '0.1.39']
history.insert(0, {
    'version': '0.1.39',
    'date': '2026-08-28',
    'items': [
        'Sider kan nu oprettes direkte i Visual Designer Manager med titel, slug, overordnet side og kladde/publiceret status; den nye side åbnes direkte i Designer.',
        'Header/Footer Designer får et canonical Menu-element med WordPress-menu som datakilde.',
        'Menu Inspector styrer retning, alignment, mobilvisning, farver, typografi, afstand, padding og baggrund uden at kopiere menupunkterne ind i layoutmodellen.',
        'Menu understøtter Hamburger, Lodret og Ombryd som mobilstrategier; frontend-rendereren er klar til senere Theme Shell-cutover.',
        'BUG-02 rich-text selection er PASS i bruger-QA på 0.1.38 og regressionskontrakten bevares i 0.1.39.',
        'Theme Shell-cutover forbliver deaktiveret; eksisterende tema er fortsat sikker fallback indtil Header-parity er godkendt.'
    ]
})
write(path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')
write('clean-release-notes.html', '<h4>0.1.39</h4><ul><li><strong>Ny side:</strong> opret WordPress-sider direkte fra Visual Designer Manager og åbn dem straks i Designer.</li><li><strong>Header Menu:</strong> nyt canonical Menu-element med eksisterende WordPress-menu som datakilde.</li><li><strong>Menu design:</strong> retning, alignment, mobilvisning, farver, typografi, afstand, padding og baggrund styres i Inspector.</li><li><strong>Mobil:</strong> Hamburger, Lodret og Ombryd er tilgængelige menu-strategier.</li><li><strong>BUG-02:</strong> rich-text selection er bruger-QA PASS på 0.1.38; cold-start/single-owner-kontrakten bevares.</li><li><strong>Sikkerhed:</strong> Theme Shell-cutover forbliver slået fra indtil 1:1 Header-parity er godkendt.</li></ul>')

# 9) Technical + user documentation.
path = 'CLEAN-TECHNICAL-MANUAL.md'
s = read(path)
s = s.replace('## 21. Kontraktstatus for 0.1.37', '## 21. Kontraktstatus for 0.1.39', 1)
pattern = re.compile(r"### VD-TEXT-SEL-001 – Rich-text selection\n\n.*?(?=### VD-BUTTON-TYPE-001)", re.S)
replacement = '''### VD-TEXT-SEL-001 – Rich-text selection\n\n**PASS i bruger-QA på 0.1.38 / regressionsbeskyttet i 0.1.39.** Cold-start selection-sessionen etableres ved afsluttet tekstmarkering, før første toolbar-klik. `v0125` er eneste autoritative selection-ejer, og legacy-lag må ikke aktivere egne restore-loops. Bruger-QA bekræftede, at Fed/Kursiv/Understregning nu bevarer markeringen som krævet.\n\n**FAST owner-regel:** Legacy rich-text-filer må aldrig afgøre delegation ud fra et konkret release-nummer. Hvis `H18RichTextV0125.selectionOwner` er sat, er v0125 den eneste selection-ejer.\n\n### VD-PAGES-001 – Opret side fra Manager\n\n**IMPLEMENTERET i 0.1.39.** Sider kan oprettes direkte fra Managerens Sider-modul med titel, valgfri slug, overordnet side og status. Efter oprettelse åbnes siden direkte i Visual Designer. Oprettelse af en side opretter ikke automatisk en Visual Designer-version; første rigtige Gem opretter v1.\n\n### VD-MENU-001 – WordPress-menu som visuelt element\n\n**IMPLEMENTERET i 0.1.39 for Header/Footer Designer.** Canonical `type=menu` gemmer reference til en eksisterende WordPress-menu og designindstillinger, men ikke en kopi af menupunkterne. Menu Inspector styrer retning, alignment, mobilstrategi, farver, typografi, afstand, padding og baggrund. Mobilstrategier er Hamburger, Lodret og Ombryd. Theme Shell-cutover er fortsat separat og OFF, indtil parity er godkendt.\n\n'''
if not pattern.search(s):
    raise SystemExit('Missing technical rich-text status section')
s = pattern.sub(replacement, s, count=1)
write(path, s)

path = 'CLEAN-USER-MANUAL.md'
s = read(path)
s = s.replace('Gælder for: Visual Designer Manager 0.1.35 og nyere;', 'Gælder for: Visual Designer Manager 0.1.39 og nyere;', 1)
intro_anchor = 'Visual Designer gemmer siden i sin egen model og ændrer først den offentlige Visual Designer-side, når du vælger **Gem som ny version**.\n\n'
page_manual = '''### 1.1 Opret en ny side direkte i Manageren\n\nÅbn **Visual Designer Manager → Sider**. Under **Ny side** kan du angive titel, valgfri slug, overordnet side og om siden skal starte som Kladde eller Publiceret. Vælg **Opret og åbn Designer**; WordPress-siden oprettes, og Visual Designer åbner den med et tomt layout. Første **Gem som ny version** opretter Visual Designer-version v1.\n\nDu kan gentage dette for alle de sider, du skal bygge. Eksisterende WordPress-sider bliver fortsat vist i samme Sider-oversigt og kan åbnes i Designer.\n\n'''
s = replace_once(s, intro_anchor, intro_anchor + page_manual, 'user manual page creation')
old_menu = '''### 2.4 Menu\n\nMenu skal være et selvstændigt visuelt element, som kan bruge en WordPress-menu som datakilde, mens Visual Designer styrer fx skrifttype, størrelse, farve, afstand, hover, aktiv side og mobil/hamburger-visning.\n\n**Status: Planlagt som native Visual Designer-element.** WordPress-menuadministration findes allerede separat i Manageren.\n'''
new_menu = '''### 2.4 Menu\n\nMenu er fra 0.1.39 et selvstændigt visuelt element i Header/Footer Designer. Vælg **+ Menu**, placer elementet i en Sektion/Kasse og vælg derefter en eksisterende WordPress-menu i Inspector. Menupunkterne vedligeholdes fortsat centralt i WordPress; Visual Designer gemmer kun menuens ID og præsentationen.\n\nI Inspector kan du styre vandret/lodret retning, venstre/center/højre alignment, tekst-, hover- og aktiv-farve, baggrund, typografi, afstand mellem punkter, padding og mobilvisning. Mobilvisning kan være **Hamburger**, **Lodret menu** eller **Ombryd menupunkter**.\n\nHeader/Footer-preview kan bruges uden at Theme Shell overtager den offentlige side. Live cutover sker først, når Headeren er godkendt 1:1 på Desktop, Laptop og Mobil.\n'''
s = replace_once(s, old_menu, new_menu, 'user manual menu section')
write(path, s)

write('docs/v0139-status.md', '''# Visual Designer Manager 0.1.39 – implementation status\n\n- BUG-02: PASS confirmed by user on 0.1.38; regression contract retained.\n- VD-PAGES-001: native page creation from Manager implemented.\n- VD-MENU-001: canonical Menu element implemented for Header/Footer Designer with WordPress menu source.\n- Menu mobile strategies: hamburger, vertical, wrap.\n- Header/Footer templates, Sticky, Overlay, per-template history and page resolution remain intact.\n- Theme Shell cutover remains OFF; no automatic live Header/Footer replacement in 0.1.39.\n''')

print('0.1.39 pages + header patch applied')
