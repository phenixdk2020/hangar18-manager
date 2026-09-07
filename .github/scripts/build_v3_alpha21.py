from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.21'
DEST = Path('build/visual-designer-manager')


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str, label: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor in {rel}, found {count}')
    write(rel, value.replace(old, new, 1))


subprocess.run(['python3', '.github/scripts/build_v3_alpha20.py'], check=True)

# ---------------------------------------------------------------------------
# Version cutover.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.20', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.20');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.20');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.21 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Remove Alpha.20's duplicate Menu page callback/CRUD layer.
# NavigationController remains the single owner of VDM -> Menu.
# ---------------------------------------------------------------------------
admin_rel = 'src/Admin/AdminController.php'
admin = read(admin_rel)
for line in [
    "        add_action('admin_post_vdm_create_nav_menu', [self::class, 'createNavigationMenu']);\n",
    "        add_action('admin_post_vdm_delete_nav_menu', [self::class, 'deleteNavigationMenu']);\n",
    "        add_submenu_page(self::MENU, 'Menu', 'Menu', $cap, 'vdm-menu', [self::class, 'menus']);\n",
]:
    if admin.count(line) != 1:
        raise SystemExit(f'Alpha.21 duplicate Menu owner anchor mismatch: {line!r} count={admin.count(line)}')
    admin = admin.replace(line, '', 1)
start = admin.find("    public static function menus(): void\n    {")
end = admin.find("    public static function headerFooter(): void\n", start)
if start < 0 or end < 0:
    raise SystemExit('Alpha.21 could not remove Alpha.20 duplicate menus()/CRUD block')
admin = admin[:start] + admin[end:]
write(admin_rel, admin)

# ---------------------------------------------------------------------------
# Persistent Website-menu in the existing advanced NavigationController.
# ---------------------------------------------------------------------------
nav_rel = 'src/Admin/NavigationController.php'
nav = read(nav_rel)
nav = nav.replace(
    "    private const HISTORY_OPTION = 'vdm_navigation_history_v1';\n",
    "    private const HISTORY_OPTION = 'vdm_navigation_history_v1';\n    private const WEBSITE_MENU_OPTION = 'vdm_website_menu_id';\n",
    1,
)
nav = nav.replace(
    "    private const ACTION_RESTORE = 'h18_clean_nav_restore';\n",
    "    private const ACTION_RESTORE = 'h18_clean_nav_restore';\n    private const ACTION_SAVE_WEBSITE = 'h18_clean_nav_save_website';\n    private const ACTION_DELETE_MENU = 'h18_clean_nav_delete_menu';\n",
    1,
)
register_anchor = "        add_action('admin_post_' . self::ACTION_RESTORE, [self::class, 'restoreSnapshot']);\n"
register_add = register_anchor + "        add_action('admin_post_' . self::ACTION_SAVE_WEBSITE, [self::class, 'saveWebsiteMenu']);\n        add_action('admin_post_' . self::ACTION_DELETE_MENU, [self::class, 'deleteMenu']);\n        add_action('admin_init', [self::class, 'bootstrapWebsiteMenu'], 60);\n"
if nav.count(register_anchor) != 1:
    raise SystemExit('Alpha.21 NavigationController register anchor mismatch')
nav = nav.replace(register_anchor, register_add, 1)

old_selected = """        $menus = wp_get_nav_menus();
        $selectedId = absint($_GET['menu_id'] ?? 0);
        if ($selectedId === 0 && !empty($menus)) {
            $selectedId = (int) $menus[0]->term_id;
        }
        $selected = $selectedId > 0 ? wp_get_nav_menu_object($selectedId) : false;
        if (!$selected instanceof \\WP_Term && !empty($menus)) {
            $selectedId = (int) $menus[0]->term_id;
            $selected = wp_get_nav_menu_object($selectedId);
        }
"""
new_selected = """        $menus = wp_get_nav_menus();
        $websiteMenuId = self::websiteMenuId();
        $selectedId = absint($_GET['menu_id'] ?? 0);
        if ($selectedId === 0 && $websiteMenuId > 0) {
            $selectedId = $websiteMenuId;
        }
        if ($selectedId === 0 && !empty($menus)) {
            $selectedId = (int) $menus[0]->term_id;
        }
        $selected = $selectedId > 0 ? wp_get_nav_menu_object($selectedId) : false;
        if (!$selected instanceof \\WP_Term && !empty($menus)) {
            $selectedId = $websiteMenuId > 0 ? $websiteMenuId : (int) $menus[0]->term_id;
            $selected = wp_get_nav_menu_object($selectedId);
        }
"""
if nav.count(old_selected) != 1:
    raise SystemExit('Alpha.21 selected edit-menu anchor mismatch')
nav = nav.replace(old_selected, new_selected, 1)

old_picker = """        if (!$menus) {
            echo '<section class="h18-manager-card h18-menu-empty"><h2>Opret din første menu</h2><p>Start med én hovedmenu. Når den er oprettet, kan du vælge publicerede sider med få klik og trække dem i den ønskede rækkefølge.</p>';
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::ACTION_CREATE) . '">';
            wp_nonce_field('h18_clean_nav_create');
            echo '<label><strong>Navn</strong><input class="regular-text" name="menu_name" value="Hovedmenu" required></label> <button class="button button-primary" type="submit">Opret Hovedmenu</button></form></section>';
            echo '</div>';
            return;
        }

        echo '<section class="h18-manager-card h18-menu-picker"><div><span class="h18-menu-kicker">Aktuel menu</span><h2>' . esc_html($selected instanceof \\WP_Term ? (string) $selected->name : 'Menu') . '</h2></div>';
"""
new_picker = """        if (!$menus) {
            echo '<section class="h18-manager-card h18-menu-empty"><h2>Opret din første menu</h2><p>Start med én hovedmenu. Når den er oprettet, kan du vælge publicerede sider med få klik og trække dem i den ønskede rækkefølge.</p>';
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::ACTION_CREATE) . '">';
            wp_nonce_field('h18_clean_nav_create');
            echo '<label><strong>Navn</strong><input class="regular-text" name="menu_name" value="Hovedmenu" required></label> <button class="button button-primary" type="submit">Opret Hovedmenu</button></form></section>';
            echo '</div>';
            return;
        }

        self::renderWebsiteMenuSelector($menus, $websiteMenuId);

        echo '<section class="h18-manager-card h18-menu-picker"><div><span class="h18-menu-kicker">Redigér menu</span><h2>' . esc_html($selected instanceof \\WP_Term ? (string) $selected->name : 'Menu') . '</h2><p class="description">Dette valg bestemmer kun, hvilken menu du redigerer nedenfor. Det ændrer ikke website-menuen.</p></div>';
"""
if nav.count(old_picker) != 1:
    raise SystemExit('Alpha.21 Menu picker integration anchor mismatch')
nav = nav.replace(old_picker, new_picker, 1)
nav = nav.replace('<span class="screen-reader-text">Skift menu</span>', '<span class="screen-reader-text">Vælg menu der skal redigeres</span>', 1)
nav = nav.replace('<span>Flere menuer, theme-locations og versionshistorik</span>', '<span>Alle menuer, theme-locations og versionshistorik</span>', 1)

create_anchor = "    public static function createMenu(): void\n"
website_methods = r'''    public static function bootstrapWebsiteMenu(): void
    {
        // Migration-only bootstrap: once the option exists, never silently
        // replace it with another menu, even if WordPress later deletes it.
        if (get_option(self::WEBSITE_MENU_OPTION, null) !== null) {
            return;
        }
        $candidate = self::headerMenuCandidate();
        if ($candidate > 0) {
            update_option(self::WEBSITE_MENU_OPTION, $candidate, false);
        }
    }

    public static function saveWebsiteMenu(): void
    {
        self::guard();
        check_admin_referer('h18_clean_nav_save_website');
        $menuId = absint($_POST['website_menu_id'] ?? 0);
        self::requireMenu($menuId);
        self::snapshot('Før ændring af website-menu');
        update_option(self::WEBSITE_MENU_OPTION, $menuId, false);
        self::redirect($menuId, 'Website-menu gemt. Header og andre Menu-elementer med datakilden Website-menu bruger nu denne menu.');
    }

    public static function deleteMenu(): void
    {
        self::guard();
        $menuId = absint($_POST['menu_id'] ?? 0);
        check_admin_referer('h18_clean_nav_delete_menu_' . $menuId);
        $menu = self::requireMenu($menuId);
        if ($menuId === self::websiteMenuId()) {
            wp_die(esc_html__('Den aktive website-menu kan ikke slettes. Vælg og gem en anden website-menu først.', 'visual-designer-manager'));
        }
        self::snapshot('Før sletning af menu ' . (string) $menu->name);
        $result = wp_delete_nav_menu($menuId);
        if (is_wp_error($result)) {
            wp_die(esc_html($result->get_error_message()));
        }
        $menus = wp_get_nav_menus();
        $next = $menus ? (int) $menus[0]->term_id : 0;
        self::redirect($next, 'Menuen “' . (string) $menu->name . '” er slettet.');
    }

    /** @param array<int,\WP_Term> $menus */
    private static function renderWebsiteMenuSelector(array $menus, int $websiteMenuId): void
    {
        $website = $websiteMenuId > 0 ? wp_get_nav_menu_object($websiteMenuId) : false;
        echo '<section class="h18-manager-card h18-menu-picker h18-menu-website-picker"><div><span class="h18-menu-kicker">Website-menu</span><h2>' . esc_html($website instanceof \WP_Term ? (string) $website->name : 'Ikke valgt') . '</h2><p class="description">Dette er den menu, som Headerens Menu-element bruger som standard på Hjem og de øvrige sider.</p></div>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:flex;gap:8px;align-items:end;flex-wrap:wrap">';
        echo '<input type="hidden" name="action" value="' . esc_attr(self::ACTION_SAVE_WEBSITE) . '">';
        wp_nonce_field('h18_clean_nav_save_website');
        echo '<label><strong>Aktiv website-menu</strong><br><select name="website_menu_id" required>';
        foreach ($menus as $menu) {
            echo '<option value="' . esc_attr((string) $menu->term_id) . '"' . selected($websiteMenuId, (int) $menu->term_id, false) . '>' . esc_html((string) $menu->name) . '</option>';
        }
        echo '</select></label><button class="button button-primary" type="submit">Gem website-menu</button></form>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:flex;gap:8px;align-items:end;flex-wrap:wrap;margin-top:12px">';
        echo '<input type="hidden" name="action" value="' . esc_attr(self::ACTION_CREATE) . '">';
        wp_nonce_field('h18_clean_nav_create');
        echo '<label><strong>Ny menu</strong><br><input class="regular-text" name="menu_name" required placeholder="Navn på ny menu"></label><button class="button" type="submit">+ Ny menu</button></form>';
        echo '</section>';
    }

    private static function websiteMenuId(): int
    {
        $raw = get_option(self::WEBSITE_MENU_OPTION, null);
        if ($raw === null) {
            return self::headerMenuCandidate();
        }
        $menuId = absint($raw);
        return $menuId > 0 && wp_get_nav_menu_object($menuId) ? $menuId : 0;
    }

    private static function headerMenuCandidate(): int
    {
        try {
            \VisualDesignerManager\Model\TemplateLayoutModel::ensureMigrated();
            $headerId = \VisualDesignerManager\Model\TemplateLayoutModel::defaultId('header');
            if ($headerId !== '' && \VisualDesignerManager\Model\TemplateLayoutModel::exists($headerId, 'header')) {
                $nodes = (array) (\VisualDesignerManager\Model\TemplateLayoutModel::model($headerId)['nodes'] ?? []);
                foreach ($nodes as $node) {
                    if (!is_array($node) || (string) ($node['type'] ?? '') !== 'menu') { continue; }
                    $candidate = absint($node['props']['menuId'] ?? 0);
                    if ($candidate > 0 && wp_get_nav_menu_object($candidate)) { return $candidate; }
                }
            }
        } catch (\Throwable $error) {
            // Continue with migration-only name lookup.
        }
        foreach (wp_get_nav_menus() as $menu) {
            if (strcasecmp((string) $menu->name, 'Visual Designer Hovedmenu') === 0) {
                return (int) $menu->term_id;
            }
        }
        $menus = wp_get_nav_menus();
        return $menus ? (int) $menus[0]->term_id : 0;
    }

'''
if nav.count(create_anchor) != 1:
    raise SystemExit('Alpha.21 website menu methods anchor mismatch')
nav = nav.replace(create_anchor, website_methods + create_anchor, 1)

list_start = nav.find("    /** @param array<int,\\WP_Term> $menus */\n    private static function renderMenuList")
list_end = nav.find("    private static function renderSelectedMenu", list_start)
if list_start < 0 or list_end < 0:
    raise SystemExit('Alpha.21 renderMenuList region missing')
render_list = r'''    /** @param array<int,\WP_Term> $menus */
    private static function renderMenuList(array $menus, int $selectedId): void
    {
        $websiteMenuId = self::websiteMenuId();
        echo '<section class="h18-manager-card"><h2>Alle menuer</h2>';
        if (!$menus) {
            echo '<p>Der er endnu ingen klassiske WordPress-menuer.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Navn</th><th>Elementer</th><th>Status</th><th>Handlinger</th></tr></thead><tbody>';
            foreach ($menus as $menu) {
                $menuId = (int) $menu->term_id;
                $items = wp_get_nav_menu_items($menuId);
                $isWebsite = $menuId === $websiteMenuId;
                $active = $menuId === $selectedId ? ' button-primary' : '';
                echo '<tr><td><strong>' . esc_html((string) $menu->name) . '</strong><br><code>ID ' . esc_html((string) $menuId) . '</code></td><td>' . esc_html((string) count(is_array($items) ? $items : [])) . '</td><td>';
                echo $isWebsite ? '<span class="h18-manager-badge is-ok">Aktiv på website</span>' : '—';
                echo '</td><td><a class="button' . esc_attr($active) . '" href="' . esc_url(self::url($menuId)) . '">Redigér</a> ';
                if ($isWebsite) {
                    echo '<span class="description">Vælg en anden website-menu før sletning.</span>';
                } else {
                    echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">';
                    echo '<input type="hidden" name="action" value="' . esc_attr(self::ACTION_DELETE_MENU) . '"><input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '">';
                    wp_nonce_field('h18_clean_nav_delete_menu_' . $menuId);
                    echo '<button class="button button-link-delete" type="submit" onclick="return confirm(\'Slet menuen “' . esc_js((string) $menu->name) . '”? Menupunkterne i denne menu slettes også.\');">Slet</button></form>';
                }
                echo '</td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</section>';
    }

'''
nav = nav[:list_start] + render_list + nav[list_end:]

# Website-menu is part of navigation snapshots as well.
old = """            'locations' => get_nav_menu_locations(),
            'menus' => $menusOut,
"""
new = """            'websiteMenuId' => self::websiteMenuId(),
            'locations' => get_nav_menu_locations(),
            'menus' => $menusOut,
"""
if nav.count(old) != 1:
    raise SystemExit('Alpha.21 snapshot websiteMenuId anchor mismatch')
nav = nav.replace(old, new, 1)
old = """            'reason' => (string) ($entry['reason'] ?? ''),
            'locations' => isset($entry['locations']) && is_array($entry['locations']) ? $entry['locations'] : [],
"""
new = """            'reason' => (string) ($entry['reason'] ?? ''),
            'websiteMenuId' => absint($entry['websiteMenuId'] ?? 0),
            'locations' => isset($entry['locations']) && is_array($entry['locations']) ? $entry['locations'] : [],
"""
if nav.count(old) != 1:
    raise SystemExit('Alpha.21 snapshot fingerprint anchor mismatch')
nav = nav.replace(old, new, 1)
old = """        $registered = get_registered_nav_menus();
        $sourceLocations = isset($entry['locations']) && is_array($entry['locations']) ? $entry['locations'] : [];
"""
new = """        $sourceWebsiteMenuId = absint($entry['websiteMenuId'] ?? 0);
        if ($sourceWebsiteMenuId > 0 && isset($menuMap[$sourceWebsiteMenuId])) {
            update_option(self::WEBSITE_MENU_OPTION, (int) $menuMap[$sourceWebsiteMenuId], false);
        }

        $registered = get_registered_nav_menus();
        $sourceLocations = isset($entry['locations']) && is_array($entry['locations']) ? $entry['locations'] : [];
"""
if nav.count(old) != 1:
    raise SystemExit('Alpha.21 snapshot restore websiteMenuId anchor mismatch')
nav = nav.replace(old, new, 1)
write(nav_rel, nav)

# ---------------------------------------------------------------------------
# Menu nodes now explicitly distinguish Website-menu vs Specific menu.
# Existing nodes default to Website-menu when normalized.
# ---------------------------------------------------------------------------
replace_once(
    'src/Model/LayoutModel.php',
    """            return array_merge([\n                'menuId' => absint($raw['menuId'] ?? 0),\n""",
    """            $menuSource = strtolower((string) ($raw['menuSource'] ?? 'website')) === 'specific' ? 'specific' : 'website';\n            return array_merge([\n                'menuSource' => $menuSource,\n                'menuId' => absint($raw['menuId'] ?? 0),\n""",
    'Alpha.21 LayoutModel menu source',
)

renderer_rel = 'src/Frontend/Renderer.php'
renderer = read(renderer_rel)
call_old = "            $menuId = absint($props['menuId'] ?? 0);\n            $menuId = self::resolveLiveMenuId($menuId);\n"
call_new = "            $menuSource = strtolower((string) ($props['menuSource'] ?? 'website')) === 'specific' ? 'specific' : 'website';\n            $menuId = self::resolveLiveMenuId($props);\n"
if renderer.count(call_old) != 1:
    raise SystemExit('Alpha.21 Renderer menu call anchor mismatch')
renderer = renderer.replace(call_old, call_new, 1)
resolver_start = renderer.find('    private static function resolveLiveMenuId(')
resolver_end = renderer.find('    public static function menuScript(): void', resolver_start)
if resolver_start < 0 or resolver_end < 0:
    raise SystemExit('Alpha.21 Renderer resolver region missing')
resolver = r'''    /** @param array<string,mixed> $props */
    private static function resolveLiveMenuId(array $props): int
    {
        $requested = absint($props['menuId'] ?? 0);
        $source = strtolower((string) ($props['menuSource'] ?? 'website')) === 'specific' ? 'specific' : 'website';
        if ($source === 'specific') {
            return $requested > 0 && wp_get_nav_menu_object($requested) ? $requested : 0;
        }

        $saved = get_option('vdm_website_menu_id', null);
        if ($saved !== null) {
            $websiteMenuId = absint($saved);
            return $websiteMenuId > 0 && wp_get_nav_menu_object($websiteMenuId) ? $websiteMenuId : 0;
        }

        // Upgrade-only compatibility before Alpha.21 has created the option:
        // keep the explicit menu already stored in the template model.
        return $requested > 0 && wp_get_nav_menu_object($requested) ? $requested : 0;
    }

'''
renderer = renderer[:resolver_start] + resolver + renderer[resolver_end:]
nav_attr_old = "            return '<nav id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-menu h18-clean-front-menu--' . esc_attr($orientation) . '\" data-mobile-mode=\"' . esc_attr($mobileMode) . '\" "
nav_attr_new = "            return '<nav id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-menu h18-clean-front-menu--' . esc_attr($orientation) . '\" data-menu-source=\"' . esc_attr($menuSource) . '\" data-menu-id=\"' . esc_attr((string) $menuId) . '\" data-mobile-mode=\"' . esc_attr($mobileMode) . '\" "
if renderer.count(nav_attr_old) != 1:
    raise SystemExit('Alpha.21 Renderer diagnostic menu attributes anchor mismatch')
renderer = renderer.replace(nav_attr_old, nav_attr_new, 1)
write(renderer_rel, renderer)

# Footer shared-menu migration also follows the canonical Website-menu option.
shared_rel = 'src/Migration/SharedPrimaryMenu.php'
shared = read(shared_rel)
old = """    private static function headerMenuId(int $postId): int
    {
        TemplateLayoutModel::ensureMigrated();
"""
new = """    private static function headerMenuId(int $postId): int
    {
        $saved = get_option('vdm_website_menu_id', null);
        if ($saved !== null) {
            $websiteMenuId = absint($saved);
            if ($websiteMenuId > 0 && wp_get_nav_menu_object($websiteMenuId)) { return $websiteMenuId; }
            return 0;
        }
        TemplateLayoutModel::ensureMigrated();
"""
if shared.count(old) != 1:
    raise SystemExit('Alpha.21 SharedPrimaryMenu website option anchor mismatch')
shared = shared.replace(old, new, 1)
old = """                if (absint($props['menuId'] ?? 0) !== $menuId) {
                    $props['menuId'] = $menuId;
                    $node['props'] = $props;
                    $changed = true;
                }
"""
new = """                if ((string) ($props['menuSource'] ?? 'website') !== 'website' || absint($props['menuId'] ?? 0) !== $menuId) {
                    $props['menuSource'] = 'website';
                    $props['menuId'] = $menuId;
                    $node['props'] = $props;
                    $changed = true;
                }
"""
if shared.count(old) != 1:
    raise SystemExit('Alpha.21 SharedPrimaryMenu existing node anchor mismatch')
shared = shared.replace(old, new, 1)
old = """            $node['props'] = [
                'menuId' => $menuId,
"""
new = """            $node['props'] = [
                'menuSource' => 'website',
                'menuId' => $menuId,
"""
if shared.count(old) != 1:
    raise SystemExit('Alpha.21 SharedPrimaryMenu new node anchor mismatch')
shared = shared.replace(old, new, 1)
write(shared_rel, shared)

# ---------------------------------------------------------------------------
# Designer: Website-menu is the default source; Specific menu remains optional.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
old = """        'menus' => $menuPayload,
        'menuAdminUrl' => admin_url('admin.php?page=vdm-menu'),
"""
new = """        'menus' => $menuPayload,
        'websiteMenuId' => absint(get_option('vdm_website_menu_id', 0)),
        'menuAdminUrl' => admin_url('admin.php?page=vdm-menu'),
"""
if main.count(old) != 1:
    raise SystemExit('Alpha.21 Designer websiteMenuId localization anchor mismatch')
main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

js_rel = 'assets/editor-v018-core.js'
js = read(js_rel)
for old, new, label in [
    ("menuId:'WordPress-menu',orientation", "menuSource:'Menudatakilde',menuId:'WordPress-menu',orientation", 'field label'),
    ("""            return Object.assign(common, {\n                menuId: parseInt(raw.menuId || 0, 10) || 0,\n""", """            return Object.assign(common, {\n                menuSource: String(raw.menuSource || 'website').toLowerCase() === 'specific' ? 'specific' : 'website',\n                menuId: parseInt(raw.menuId || 0, 10) || 0,\n""", 'normalize'),
    ("""            const menus = Array.isArray(CFG.menus) ? CFG.menus : [];\n            const menuDef = menus.find(function (entry) { return parseInt(entry.id || 0, 10) === parseInt(node.props.menuId || 0, 10); }) || null;\n""", """            const menus = Array.isArray(CFG.menus) ? CFG.menus : [];\n            const previewMenuId = node.props.menuSource === 'specific'\n                ? (parseInt(node.props.menuId || 0, 10) || 0)\n                : ((parseInt(CFG.websiteMenuId || 0, 10) || 0) || (parseInt(node.props.menuId || 0, 10) || 0));\n            const menuDef = menus.find(function (entry) { return parseInt(entry.id || 0, 10) === previewMenuId; }) || null;\n""", 'preview'),
    ("""                else if (field === 'menuId') { current.props.menuId = parseInt(control.value || 0, 10) || 0; }\n                else if (field === 'orientation')""", """                else if (field === 'menuSource') { current.props.menuSource = control.value === 'specific' ? 'specific' : 'website'; }\n                else if (field === 'menuId') { current.props.menuId = parseInt(control.value || 0, 10) || 0; }\n                else if (field === 'orientation')""", 'change handler'),
]:
    if js.count(old) != 1:
        raise SystemExit(f'Alpha.21 Designer {label} anchor mismatch: {js.count(old)}')
    js = js.replace(old, new, 1)
old = """            html += '<div class="h18-vd-menu-group"><h3>Indhold</h3><label>Menu<select data-field="menuId"><option value="0">Vælg menu…</option>' + (Array.isArray(CFG.menus) ? CFG.menus.map(function (menu) { const id = parseInt(menu.id || 0, 10) || 0; return '<option value="' + id + '"' + (parseInt(node.props.menuId || 0, 10) === id ? ' selected' : '') + '>' + escapeHtml(String(menu.name || ('Menu ' + id))) + '</option>'; }).join('') : '') + '</select></label>';
"""
new = """            html += '<div class="h18-vd-menu-group"><h3>Indhold</h3><label>Datakilde<select data-field="menuSource"><option value="website"' + (node.props.menuSource !== 'specific' ? ' selected' : '') + '>Website-menu</option><option value="specific"' + (node.props.menuSource === 'specific' ? ' selected' : '') + '>Specifik menu</option></select></label>';
            if (node.props.menuSource === 'specific') {
                html += '<label>Menu<select data-field="menuId"><option value="0">Vælg menu…</option>' + (Array.isArray(CFG.menus) ? CFG.menus.map(function (menu) { const id = parseInt(menu.id || 0, 10) || 0; return '<option value="' + id + '"' + (parseInt(node.props.menuId || 0, 10) === id ? ' selected' : '') + '>' + escapeHtml(String(menu.name || ('Menu ' + id))) + '</option>'; }).join('') : '') + '</select></label>';
            } else {
                const websiteMenu = (Array.isArray(CFG.menus) ? CFG.menus : []).find(function (menu) { return (parseInt(menu.id || 0, 10) || 0) === (parseInt(CFG.websiteMenuId || 0, 10) || 0); });
                html += '<p class="description">Aktiv website-menu: <strong>' + escapeHtml(websiteMenu ? String(websiteMenu.name || '') : 'ikke gemt endnu') + '</strong>. <a href="' + escapeAttr(CFG.menuAdminUrl || '#') + '">Åbn Menu</a></p>';
            }
"""
if js.count(old) != 1:
    raise SystemExit(f'Alpha.21 Designer inspector anchor mismatch: {js.count(old)}')
js = js.replace(old, new, 1)
write(js_rel, js)

# ---------------------------------------------------------------------------
# Release history and deterministic contracts.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.20':
    raise SystemExit('Expected Alpha.20 release-history baseline missing')
alpha21 = {
    'version': VERSION,
    'date': '2026-09-07',
    'items': [
        'VDM Menu er igen ét samlet modul: Alpha.20s dobbelte Menu-callback/UI er fjernet, og NavigationController ejer hele siden.',
        'Ny persistent Website-menu med eksplicit Gem website-menu; Redigér menu er et separat, ikke-persistent redigeringsvalg.',
        'Header/Footer Menu-elementer bruger Website-menu som standarddatakilde; Specifik menu kan vælges eksplicit i Designerens Inspector.',
        'Aktiv website-menu kan ikke slettes før en anden website-menu er valgt og gemt; opret/slet er integreret i den eksisterende Menu-editor.',
        'Website-menu indgår i navigationens snapshots/gendannelse og frontenden gætter ikke en anden menu, når et allerede gemt website-menu-ID bliver ugyldigt.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha21] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

main = read('visual-designer-manager.php')
admin = read(admin_rel)
nav = read(nav_rel)
layout = read('src/Model/LayoutModel.php')
renderer = read(renderer_rel)
shared = read(shared_rel)
js = read(js_rel)
release_rows = json.loads(history_path.read_text(encoding='utf-8'))['versions']

for token in ['Version: 3.0.0-alpha.21', "define('VDM_VERSION', '3.0.0-alpha.21');", "'websiteMenuId' => absint(get_option('vdm_website_menu_id', 0))"]:
    if token not in main: raise SystemExit(f'Alpha.21 main token missing: {token}')
for forbidden in ["[self::class, 'menus']", 'public static function menus(): void', 'vdm_create_nav_menu', 'vdm_delete_nav_menu']:
    if forbidden in admin: raise SystemExit(f'Alpha.21 duplicate AdminController Menu owner remains: {forbidden}')
for token in [
    "private const WEBSITE_MENU_OPTION = 'vdm_website_menu_id';",
    'public static function saveWebsiteMenu(): void',
    'public static function deleteMenu(): void',
    '>Gem website-menu</button>',
    '>Redigér menu</span>',
    'Aktiv på website',
    'Den aktive website-menu kan ikke slettes',
    "'websiteMenuId' => self::websiteMenuId()",
]:
    if token not in nav: raise SystemExit(f'Alpha.21 Navigation token missing: {token}')
for token in ["'menuSource' => $menuSource", "($raw['menuSource'] ?? 'website')"]:
    if token not in layout: raise SystemExit(f'Alpha.21 LayoutModel token missing: {token}')
for token in ["get_option('vdm_website_menu_id', null)", "($props['menuSource'] ?? 'website')", 'data-menu-source=', 'data-menu-id=']:
    if token not in renderer: raise SystemExit(f'Alpha.21 Renderer token missing: {token}')
for token in ["menuSource:'Menudatakilde'", "data-field=\"menuSource\"", '>Website-menu</option>', '>Specifik menu</option>', 'CFG.websiteMenuId']:
    if token not in js: raise SystemExit(f'Alpha.21 Designer token missing: {token}')
if "get_option('vdm_website_menu_id', null)" not in shared: raise SystemExit('Alpha.21 shared Footer website-menu binding missing')
if release_rows[0].get('version') != VERSION or release_rows[1].get('version') != '3.0.0-alpha.20':
    raise SystemExit('Alpha.21 release-history ordering failed')

print('V3 Alpha.21 single integrated Menu module: PASS')
print('V3 Alpha.21 persistent Website-menu save/binding: PASS')
print('V3 Alpha.21 Header/Footer website-menu source contract: PASS')
print('V3 Alpha.21 Designer Website-menu/Specific-menu source control: PASS')
