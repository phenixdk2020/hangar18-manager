from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.20'
DEST = Path('build/visual-designer-manager')


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


subprocess.run(['python3', '.github/scripts/build_v3_alpha19.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.19', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.19');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.19');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.20 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Menu CRUD in Visual Designer Manager.
# ---------------------------------------------------------------------------
admin_rel = 'src/Admin/AdminController.php'
admin = read(admin_rel)

hook_anchor = "        add_action('admin_menu', [self::class, 'sortManagerSubmenu'], 999);\n"
hook_add = hook_anchor + "        add_action('admin_post_vdm_create_nav_menu', [self::class, 'createNavigationMenu']);\n        add_action('admin_post_vdm_delete_nav_menu', [self::class, 'deleteNavigationMenu']);\n"
if admin.count(hook_anchor) != 1:
    raise SystemExit(f'Alpha.20 menu CRUD hook anchor mismatch: {admin.count(hook_anchor)}')
admin = admin.replace(hook_anchor, hook_add, 1)

menu_start = "    public static function menus(): void\n    {"
menu_end = "    public static function headerFooter(): void\n"
start = admin.find(menu_start)
end = admin.find(menu_end, start)
if start < 0 or end < 0:
    raise SystemExit('Alpha.20 menus() method anchors missing')

menu_methods = r'''    public static function menus(): void
    {
        self::guard();
        $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));
        self::open('Menu', 'Opret, redigér og slet WordPress-menuer. De samme menu-IDer bruges direkte af Visual Designerens Menu-element.');
        if ($message !== '') {
            echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>';
        }

        $canManage = current_user_can('edit_theme_options');
        $menus = wp_get_nav_menus();
        $locations = get_nav_menu_locations();
        $registered = get_registered_nav_menus();

        echo '<div class="h18-manager-toolbar">';
        if ($canManage) {
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">';
            wp_nonce_field('vdm_create_nav_menu');
            echo '<input type="hidden" name="action" value="vdm_create_nav_menu">';
            echo '<label><span class="screen-reader-text">Navn på ny menu</span><input type="text" name="menu_name" required placeholder="Navn på ny menu" aria-label="Navn på ny menu"></label>';
            echo '<button class="button button-primary" type="submit">+ Ny menu</button></form>';
        }
        echo '<a class="button" href="' . esc_url(admin_url('nav-menus.php')) . '">Åbn WordPress Menu-editor</a></div>';

        echo '<div class="h18-manager-two-col"><div class="h18-manager-card"><h2>Menuer</h2>';
        if (!$menus) {
            echo '<p>Ingen klassiske WordPress-menuer fundet. Opret den første menu ovenfor.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Navn</th><th>Elementer</th><th>Bruges i location</th><th>Handlinger</th></tr></thead><tbody>';
            foreach ($menus as $menu) {
                $menuId = (int) $menu->term_id;
                $items = wp_get_nav_menu_items($menuId);
                $locationLabels = [];
                foreach ($registered as $key => $label) {
                    if ((int) ($locations[$key] ?? 0) === $menuId) { $locationLabels[] = (string) $label; }
                }
                echo '<tr><td><strong>' . esc_html((string) $menu->name) . '</strong><br><code>ID ' . esc_html((string) $menuId) . '</code></td>';
                echo '<td>' . esc_html((string) count(is_array($items) ? $items : [])) . '</td>';
                echo '<td>' . esc_html($locationLabels ? implode(', ', $locationLabels) : '—') . '</td><td class="h18-manager-actions">';
                echo '<a class="button" href="' . esc_url(admin_url('nav-menus.php?action=edit&menu=' . $menuId)) . '">Redigér</a>';
                if ($canManage) {
                    echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">';
                    wp_nonce_field('vdm_delete_nav_menu');
                    echo '<input type="hidden" name="action" value="vdm_delete_nav_menu"><input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '">';
                    echo '<button class="button button-link-delete" type="submit" onclick="return confirm(\'Slet menuen “' . esc_js((string) $menu->name) . '”? Menupunkterne i denne menu slettes også.\');">Slet</button></form>';
                }
                echo '</td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</div><div class="h18-manager-card"><h2>Menu-locations</h2>';
        if (!$registered) {
            echo '<p>Temaet registrerer ingen klassiske menu-locations. Visual Designer kan stadig bruge en menu direkte via menu-ID.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Location</th><th>Menu</th></tr></thead><tbody>';
            foreach ($registered as $key => $label) {
                $menuId = (int) ($locations[$key] ?? 0);
                $menuObj = $menuId > 0 ? wp_get_nav_menu_object($menuId) : false;
                echo '<tr><td>' . esc_html((string) $label) . '<br><code>' . esc_html((string) $key) . '</code></td><td>' . esc_html($menuObj ? (string) $menuObj->name : 'Ikke tildelt') . '</td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</div></div>';
        self::close();
    }

    public static function createNavigationMenu(): void
    {
        if (!current_user_can('edit_theme_options')) {
            wp_die(esc_html__('Ingen adgang til at oprette menuer.', 'visual-designer-manager'));
        }
        check_admin_referer('vdm_create_nav_menu');
        $name = sanitize_text_field((string) wp_unslash($_POST['menu_name'] ?? ''));
        if ($name === '') {
            self::redirectMenu('error', 'Menuens navn mangler.');
        }
        $result = wp_create_nav_menu($name);
        if (is_wp_error($result)) {
            self::redirectMenu('error', 'Menuen kunne ikke oprettes: ' . $result->get_error_message());
        }
        self::redirectMenu('ok', 'Menuen “' . $name . '” er oprettet og kan nu vælges i Designerens Menu-element.');
    }

    public static function deleteNavigationMenu(): void
    {
        if (!current_user_can('edit_theme_options')) {
            wp_die(esc_html__('Ingen adgang til at slette menuer.', 'visual-designer-manager'));
        }
        check_admin_referer('vdm_delete_nav_menu');
        $menuId = absint($_POST['menu_id'] ?? 0);
        $menu = $menuId > 0 ? wp_get_nav_menu_object($menuId) : false;
        if (!$menu) {
            self::redirectMenu('error', 'Den valgte menu findes ikke længere.');
        }
        $name = (string) $menu->name;
        $result = wp_delete_nav_menu($menuId);
        if (is_wp_error($result)) {
            self::redirectMenu('error', 'Menuen kunne ikke slettes: ' . $result->get_error_message());
        }
        self::redirectMenu('ok', 'Menuen “' . $name . '” er slettet. Menu-elementer, der pegede på den, falder sikkert tilbage til en eksisterende menu eller en synlig placeholder.');
    }

    private static function redirectMenu(string $status, string $message): void
    {
        wp_safe_redirect(add_query_arg([
            'page' => 'vdm-menu',
            'vd_status' => sanitize_key($status),
            'vd_message' => $message,
        ], admin_url('admin.php')));
        exit;
    }

'''
admin = admin[:start] + menu_methods + admin[end:]
write(admin_rel, admin)

# ---------------------------------------------------------------------------
# Live Header menu parity.
# The Designer screenshot proves that the Menu node exists. Resolve a stale or
# deleted menu ID at render time and make the Header's navigation paint path
# explicitly visible on desktop without rewriting the stored template model.
# ---------------------------------------------------------------------------
renderer_rel = 'src/Frontend/Renderer.php'
renderer = read(renderer_rel)
menu_id_anchor = "            $menuId = absint($props['menuId'] ?? 0);\n"
menu_id_new = menu_id_anchor + "            $menuId = self::resolveLiveMenuId($menuId);\n"
if renderer.count(menu_id_anchor) != 1:
    raise SystemExit(f'Alpha.20 live menu ID anchor mismatch: {renderer.count(menu_id_anchor)}')
renderer = renderer.replace(menu_id_anchor, menu_id_new, 1)

method_anchor = "    public static function menuScript(): void\n"
resolver = r'''    private static function resolveLiveMenuId(int $requested): int
    {
        $hasItems = static function (int $menuId): bool {
            if ($menuId <= 0 || !wp_get_nav_menu_object($menuId)) { return false; }
            $items = wp_get_nav_menu_items($menuId);
            return is_array($items) && count($items) > 0;
        };

        if ($hasItems($requested)) { return $requested; }

        foreach ((array) get_nav_menu_locations() as $menuId) {
            $candidate = absint($menuId);
            if ($hasItems($candidate)) { return $candidate; }
        }

        foreach ((array) wp_get_nav_menus() as $menu) {
            $candidate = isset($menu->term_id) ? absint($menu->term_id) : 0;
            if ($hasItems($candidate)) { return $candidate; }
        }

        // Keep the requested ID when it still exists but is empty. Renderer.php
        // then shows its normal visible placeholder instead of silently losing
        // the entire Header Menu node.
        return $requested > 0 && wp_get_nav_menu_object($requested) ? $requested : 0;
    }

'''
if renderer.count(method_anchor) != 1:
    raise SystemExit(f'Alpha.20 menu resolver method anchor mismatch: {renderer.count(method_anchor)}')
renderer = renderer.replace(method_anchor, resolver + method_anchor, 1)

css_anchor = "        echo '.h18-clean-front-text-heading{margin:0 0 8px;line-height:1.2}';\n"
header_css = "        echo '@media(min-width:783px){.h18-vd-live-shell-header{overflow:visible!important}.h18-vd-live-shell-header .h18-clean-front-section,.h18-vd-live-shell-header .h18-clean-front-container{overflow:visible!important}.h18-vd-live-shell-header .h18-clean-front-menu{display:flex!important;visibility:visible!important;opacity:1!important;overflow:visible!important;z-index:10020!important}.h18-vd-live-shell-header .h18-clean-front-menu-details,.h18-vd-live-shell-header .h18-clean-front-menu-panel{display:block!important;visibility:visible!important;opacity:1!important}.h18-vd-live-shell-header .h18-clean-front-menu-list{display:flex!important;visibility:visible!important;opacity:1!important}}';\n"
if renderer.count(css_anchor) != 1:
    raise SystemExit(f'Alpha.20 Header live CSS anchor mismatch: {renderer.count(css_anchor)}')
renderer = renderer.replace(css_anchor, header_css + css_anchor, 1)
write(renderer_rel, renderer)

# ---------------------------------------------------------------------------
# Mobile 1:1 hardening.
# Alpha.19 correctly finds nested semantic bands, but a full-width band can
# still sit inside one or more wrappers with inherited horizontal padding.
# Neutralize those structural ancestors for the major V1 bands. Card nodes
# retain Alpha.16/19's explicit inset sizing, so Bevaring/Formidling/Fællesskab
# remain inset while hero/tagline/major bands can reach the phone edges.
# ---------------------------------------------------------------------------
rr_rel = 'src/Frontend/ResponsiveRenderer.php'
rr = read(rr_rel)
old = r'''        // Preserve V1's inset Bevaring/Formidling/Fællesskab cards even when
        // their parent wrapper is full-width.
        foreach (array_keys($featureIds) as $id) {
'''
new = r'''        // Full-width semantic bands must not remain trapped inside a
        // Section/Container with inherited horizontal padding. Alpha.19 fixed
        // the band itself; Alpha.20 also clears every structural ancestor on
        // that path. This is mobile-only generated CSS and does not mutate data.
        $majorWrapperIds = [];
        foreach (array_keys($majorIds) as $semanticId) {
            $bandId = $nearestBand($semanticId);
            $majorWrapperIds[$bandId] = true;
            foreach ($ancestorChain($bandId) as $ancestorId) {
                $majorWrapperIds[$ancestorId] = true;
            }
        }
        foreach (array_keys($majorWrapperIds) as $id) {
            $node = $byId[$id] ?? null;
            if (!is_array($node) || !in_array((string) ($node['type'] ?? ''), ['section', 'container'], true)) { continue; }
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            $css .= $selector . '{max-width:100%!important;padding-left:0!important;padding-right:0!important;overflow:visible!important;}';
        }

        // Preserve V1's inset Bevaring/Formidling/Fællesskab cards even when
        // their parent wrapper is full-width.
        foreach (array_keys($featureIds) as $id) {
'''
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.20 major ancestor parity anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)
write(rr_rel, rr)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.19':
    raise SystemExit('Expected Alpha.19 release-history baseline missing')
alpha20 = {
    'version': VERSION,
    'date': '2026-09-07',
    'items': [
        'Menuadministration: VDM Menu kan nu oprette og slette klassiske WordPress-menuer direkte med nonce- og capability-kontrol.',
        'Header live-paritet: et Menu-element, der findes i Designeren, resolver nu sikkert et slettet/tomt/stale menu-ID til en eksisterende ikke-tom menu ved rendering uden at omskrive template-data.',
        'Desktop Header-navigation har en eksplicit visibility/overflow-kontrakt, så Menu-noden ikke kan forsvinde bag shell/container styling.',
        'Mobil 1:1 hardening: nested major bands rydder nu også inherited horizontal padding på deres Section/Container-ancestor path.',
        'Alpha.19 nested edge parity, Alpha.17 Eventlist controls, Alpha.14 hamburger navigation og V1 0.1.93 regression baseline bevares.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha20] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic build contract.
main = read('visual-designer-manager.php')
admin = read(admin_rel)
renderer = read(renderer_rel)
rr = read(rr_rel)
history = json.loads(history_path.read_text(encoding='utf-8'))['versions']

for token in [
    'Version: 3.0.0-alpha.20',
    "define('VDM_VERSION', '3.0.0-alpha.20');",
]:
    if token not in main:
        raise SystemExit(f'Alpha.20 main token missing: {token}')

for token in [
    "add_action('admin_post_vdm_create_nav_menu', [self::class, 'createNavigationMenu']);",
    "add_action('admin_post_vdm_delete_nav_menu', [self::class, 'deleteNavigationMenu']);",
    'public static function createNavigationMenu(): void',
    'public static function deleteNavigationMenu(): void',
    'wp_create_nav_menu($name)',
    'wp_delete_nav_menu($menuId)',
    "check_admin_referer('vdm_create_nav_menu')",
    "check_admin_referer('vdm_delete_nav_menu')",
    "current_user_can('edit_theme_options')",
    '>+ Ny menu<',
    '>Slet</button>',
]:
    if token not in admin:
        raise SystemExit(f'Alpha.20 menu CRUD token missing: {token}')

for token in [
    '$menuId = self::resolveLiveMenuId($menuId);',
    'private static function resolveLiveMenuId(int $requested): int',
    'get_nav_menu_locations()',
    'wp_get_nav_menus()',
    '.h18-vd-live-shell-header .h18-clean-front-menu{display:flex!important;visibility:visible!important;opacity:1!important',
    '<details class="h18-clean-front-menu-details">',
]:
    if token not in renderer:
        raise SystemExit(f'Alpha.20 live menu parity token missing: {token}')

for token in [
    'private static function v1NestedMobileEdgeParityCss(',
    '$majorWrapperIds = [];',
    'foreach ($ancestorChain($bandId) as $ancestorId)',
    "padding-left:0!important;padding-right:0!important;overflow:visible!important;",
    "['Om foreningen', 'Køretøjer og materiel', 'Events', 'Billedgalleri', 'Bliv en del af foreningen', 'Kontakt os']",
]:
    if token not in rr:
        raise SystemExit(f'Alpha.20 mobile parity token missing: {token}')

if history[0].get('version') != VERSION or history[1].get('version') != '3.0.0-alpha.19':
    raise SystemExit('Alpha.20 release-history ordering failed')

print('V3 Alpha.20 menu CRUD: PASS')
print('V3 Alpha.20 live Header menu resolver/visibility parity: PASS')
print('V3 Alpha.20 nested mobile ancestor edge parity: PASS')
