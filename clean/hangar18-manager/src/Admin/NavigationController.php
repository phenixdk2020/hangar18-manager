<?php

declare(strict_types=1);

namespace Hangar18\Clean\Admin;

final class NavigationController
{
    private const HISTORY_OPTION = 'h18_clean_navigation_history_v1';
    private const MAX_HISTORY = 30;
    private const ACTION_CREATE = 'h18_clean_nav_create';
    private const ACTION_ADD = 'h18_clean_nav_add';
    private const ACTION_SAVE = 'h18_clean_nav_save';
    private const ACTION_DELETE_ITEM = 'h18_clean_nav_delete_item';
    private const ACTION_LOCATIONS = 'h18_clean_nav_locations';

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 8);
        add_action('admin_post_' . self::ACTION_CREATE, [self::class, 'createMenu']);
        add_action('admin_post_' . self::ACTION_ADD, [self::class, 'addItem']);
        add_action('admin_post_' . self::ACTION_SAVE, [self::class, 'saveMenu']);
        add_action('admin_post_' . self::ACTION_DELETE_ITEM, [self::class, 'deleteItem']);
        add_action('admin_post_' . self::ACTION_LOCATIONS, [self::class, 'saveLocations']);
    }

    public static function menu(): void
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

    public static function render(): void
    {
        self::guard();
        $menus = wp_get_nav_menus();
        $selectedId = absint($_GET['menu_id'] ?? 0);
        if ($selectedId === 0 && !empty($menus)) {
            $selectedId = (int) $menus[0]->term_id;
        }
        $selected = $selectedId > 0 ? wp_get_nav_menu_object($selectedId) : false;
        $history = get_option(self::HISTORY_OPTION, []);
        $historyCount = is_array($history) ? count($history) : 0;

        echo '<div class="wrap h18-manager-admin">';
        echo '<h1>Menu / Navigation</h1>';
        echo '<p class="h18-manager-description">Administrér navigationens struktur uafhængigt af Visual Designer. Udseende, responsiv hamburger-menu og placering styres senere af Menu-elementet i Header/Footer Designer.</p>';

        if (isset($_GET['h18_nav_notice'])) {
            $notice = sanitize_text_field((string) wp_unslash($_GET['h18_nav_notice']));
            echo '<div class="notice notice-success is-dismissible"><p>' . esc_html($notice) . '</p></div>';
        }

        echo '<div class="h18-manager-two-col">';
        echo '<section class="h18-manager-card"><h2>Menuer</h2>';
        if (!$menus) {
            echo '<p>Der er endnu ingen klassiske WordPress-menuer.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Navn</th><th>Elementer</th><th></th></tr></thead><tbody>';
            foreach ($menus as $menu) {
                $items = wp_get_nav_menu_items((int) $menu->term_id);
                echo '<tr><td><strong>' . esc_html((string) $menu->name) . '</strong></td><td>' . esc_html((string) count(is_array($items) ? $items : [])) . '</td><td><a class="button' . ((int) $menu->term_id === $selectedId ? ' button-primary' : '') . '" href="' . esc_url(self::url((int) $menu->term_id)) . '">Redigér</a></td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '<h3>Ny menu</h3>';
        self::formStart(self::ACTION_CREATE, 'create');
        echo '<label><strong>Navn</strong><br><input class="regular-text" name="menu_name" required></label> ';
        echo '<button class="button button-primary" type="submit">Opret menu</button>';
        echo '</form></section>';

        echo '<section class="h18-manager-card"><h2>Theme locations</h2>';
        self::renderLocations($menus);
        echo '<p class="description">Theme-location er kun koblingen mellem en navigation og temaets runtime. Det visuelle menu-design skal ikke ligge i temaet.</p>';
        echo '</section></div>';

        if ($selected) {
            self::renderSelectedMenu($selectedId, (string) $selected->name);
        }

        echo '<section class="h18-manager-card"><h2>Versionssikkerhed</h2><p>Før Manageren ændrer navigation eller theme-location, gemmes automatisk et strukturelt snapshot. Der er aktuelt <strong>' . esc_html((string) $historyCount) . '</strong> snapshots; maksimalt ' . esc_html((string) self::MAX_HISTORY) . ' bevares.</p><p class="description">Restore-UI til disse snapshots tilføjes som næste navigationstrin. Den eksisterende WordPress Menu-editor kan fortsat bruges parallelt, men ændringer foretaget direkte dér bliver ikke automatisk snapshot'et af Visual Designer Manager.</p></section>';
        echo '</div>';
    }

    public static function createMenu(): void
    {
        self::guard();
        check_admin_referer('h18_clean_nav_create');
        $name = sanitize_text_field((string) wp_unslash($_POST['menu_name'] ?? ''));
        if ($name === '') {
            self::redirect(0, 'Menunavn mangler.');
        }
        self::snapshot('Før oprettelse af menu');
        $result = wp_create_nav_menu($name);
        if (is_wp_error($result)) {
            wp_die(esc_html($result->get_error_message()));
        }
        self::redirect((int) $result, 'Menu oprettet.');
    }

    public static function addItem(): void
    {
        self::guard();
        $menuId = absint($_POST['menu_id'] ?? 0);
        check_admin_referer('h18_clean_nav_add_' . $menuId);
        self::requireMenu($menuId);
        $kind = sanitize_key((string) ($_POST['item_kind'] ?? 'page'));
        self::snapshot('Før tilføjelse af menupunkt');

        if ($kind === 'page') {
            $pageId = absint($_POST['page_id'] ?? 0);
            $page = get_post($pageId);
            if (!$page instanceof \WP_Post || $page->post_type !== 'page') {
                wp_die(esc_html__('Ugyldig side.', 'hangar18-manager-clean'));
            }
            $result = wp_update_nav_menu_item($menuId, 0, [
                'menu-item-object-id' => $pageId,
                'menu-item-object' => 'page',
                'menu-item-type' => 'post_type',
                'menu-item-status' => 'publish',
            ]);
        } else {
            $title = sanitize_text_field((string) wp_unslash($_POST['custom_title'] ?? ''));
            $url = esc_url_raw((string) wp_unslash($_POST['custom_url'] ?? ''));
            if ($title === '' || $url === '') {
                wp_die(esc_html__('Titel og URL er påkrævet.', 'hangar18-manager-clean'));
            }
            $result = wp_update_nav_menu_item($menuId, 0, [
                'menu-item-title' => $title,
                'menu-item-url' => $url,
                'menu-item-type' => 'custom',
                'menu-item-status' => 'publish',
            ]);
        }
        if (is_wp_error($result)) {
            wp_die(esc_html($result->get_error_message()));
        }
        self::redirect($menuId, 'Menupunkt tilføjet.');
    }

    public static function saveMenu(): void
    {
        self::guard();
        $menuId = absint($_POST['menu_id'] ?? 0);
        check_admin_referer('h18_clean_nav_save_' . $menuId);
        $menu = self::requireMenu($menuId);
        self::snapshot('Før ændring af menu ' . (string) $menu->name);

        $newName = sanitize_text_field((string) wp_unslash($_POST['menu_name'] ?? ''));
        if ($newName !== '' && $newName !== (string) $menu->name) {
            $renamed = wp_update_nav_menu_object($menuId, ['menu-name' => $newName]);
            if (is_wp_error($renamed)) {
                wp_die(esc_html($renamed->get_error_message()));
            }
        }

        $items = wp_get_nav_menu_items($menuId, ['post_status' => 'any']);
        $titles = isset($_POST['item_title']) && is_array($_POST['item_title']) ? $_POST['item_title'] : [];
        $parents = isset($_POST['item_parent']) && is_array($_POST['item_parent']) ? $_POST['item_parent'] : [];
        $orders = isset($_POST['item_order']) && is_array($_POST['item_order']) ? $_POST['item_order'] : [];
        foreach (is_array($items) ? $items : [] as $item) {
            $id = (int) $item->ID;
            $title = sanitize_text_field((string) wp_unslash($titles[$id] ?? $item->title));
            $parent = absint($parents[$id] ?? $item->menu_item_parent);
            if ($parent === $id) {
                $parent = 0;
            }
            $position = max(1, absint($orders[$id] ?? $item->menu_order));
            $args = [
                'menu-item-title' => $title,
                'menu-item-parent-id' => $parent,
                'menu-item-position' => $position,
                'menu-item-status' => 'publish',
                'menu-item-type' => (string) $item->type,
                'menu-item-object' => (string) $item->object,
                'menu-item-object-id' => (int) $item->object_id,
                'menu-item-target' => (string) $item->target,
                'menu-item-classes' => is_array($item->classes) ? $item->classes : [],
            ];
            if ((string) $item->type === 'custom') {
                $args['menu-item-url'] = esc_url_raw((string) $item->url);
            }
            $result = wp_update_nav_menu_item($menuId, $id, $args);
            if (is_wp_error($result)) {
                wp_die(esc_html($result->get_error_message()));
            }
        }
        self::redirect($menuId, 'Menu gemt.');
    }

    public static function deleteItem(): void
    {
        self::guard();
        $menuId = absint($_POST['menu_id'] ?? 0);
        $itemId = absint($_POST['item_id'] ?? 0);
        check_admin_referer('h18_clean_nav_delete_' . $menuId . '_' . $itemId);
        self::requireMenu($menuId);
        if ($itemId <= 0 || get_post_type($itemId) !== 'nav_menu_item') {
            wp_die(esc_html__('Ugyldigt menupunkt.', 'hangar18-manager-clean'));
        }
        self::snapshot('Før sletning af menupunkt');
        wp_delete_post($itemId, true);
        self::redirect($menuId, 'Menupunkt slettet.');
    }

    public static function saveLocations(): void
    {
        self::guard();
        check_admin_referer('h18_clean_nav_locations');
        self::snapshot('Før ændring af theme locations');
        $registered = get_registered_nav_menus();
        $posted = isset($_POST['locations']) && is_array($_POST['locations']) ? $_POST['locations'] : [];
        $locations = get_nav_menu_locations();
        foreach ($registered as $key => $label) {
            $locations[$key] = absint($posted[$key] ?? 0);
        }
        set_theme_mod('nav_menu_locations', $locations);
        self::redirect(0, 'Theme locations gemt.');
    }

    private static function renderSelectedMenu(int $menuId, string $menuName): void
    {
        $items = wp_get_nav_menu_items($menuId, ['post_status' => 'any']);
        $items = is_array($items) ? $items : [];
        echo '<section class="h18-manager-card"><h2>Redigér: ' . esc_html($menuName) . '</h2>';
        self::formStart(self::ACTION_SAVE, 'save_' . $menuId);
        echo '<input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '">';
        wp_nonce_field('h18_clean_nav_save_' . $menuId);
        echo '<p><label><strong>Menunavn</strong><br><input class="regular-text" name="menu_name" value="' . esc_attr($menuName) . '"></label></p>';
        if (!$items) {
            echo '<p>Menuen har ingen punkter endnu.</p>';
        } else {
            echo '<table class="widefat striped h18-manager-table"><thead><tr><th>Titel</th><th>Type</th><th>Parent</th><th>Position</th><th>URL</th><th></th></tr></thead><tbody>';
            foreach ($items as $item) {
                $id = (int) $item->ID;
                echo '<tr><td><input name="item_title[' . esc_attr((string) $id) . ']" value="' . esc_attr((string) $item->title) . '"></td>';
                echo '<td><code>' . esc_html((string) $item->type) . '</code></td><td><select name="item_parent[' . esc_attr((string) $id) . ']"><option value="0">— root —</option>';
                foreach ($items as $parent) {
                    if ((int) $parent->ID === $id) { continue; }
                    echo '<option value="' . esc_attr((string) $parent->ID) . '"' . selected((int) $item->menu_item_parent, (int) $parent->ID, false) . '>' . esc_html((string) $parent->title) . '</option>';
                }
                echo '</select></td><td><input type="number" min="1" style="width:75px" name="item_order[' . esc_attr((string) $id) . ']" value="' . esc_attr((string) $item->menu_order) . '"></td>';
                echo '<td><small>' . esc_html((string) $item->url) . '</small></td><td></td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '<p><button class="button button-primary" type="submit">Gem menu</button> <a class="button" href="' . esc_url(admin_url('nav-menus.php?action=edit&menu=' . $menuId)) . '">Åbn WordPress Menu-editor</a></p></form>';

        if ($items) {
            echo '<h3>Slet menupunkt</h3><div class="h18-manager-actions">';
            foreach ($items as $item) {
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" onsubmit="return confirm(\'Slet dette menupunkt?\');"><input type="hidden" name="action" value="' . esc_attr(self::ACTION_DELETE_ITEM) . '"><input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '"><input type="hidden" name="item_id" value="' . esc_attr((string) $item->ID) . '">';
                wp_nonce_field('h18_clean_nav_delete_' . $menuId . '_' . (int) $item->ID);
                echo '<button class="button" type="submit">Slet ' . esc_html((string) $item->title) . '</button></form>';
            }
            echo '</div>';
        }

        echo '<hr><h3>Tilføj menupunkt</h3><div class="h18-manager-two-col">';
        echo '<div><h4>WordPress-side</h4>';
        self::formStart(self::ACTION_ADD, 'add_page_' . $menuId);
        echo '<input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '"><input type="hidden" name="item_kind" value="page">';
        wp_nonce_field('h18_clean_nav_add_' . $menuId);
        echo '<select name="page_id" required><option value="">Vælg side…</option>';
        foreach (get_pages(['sort_column' => 'post_title', 'post_status' => ['publish', 'draft', 'private']]) as $page) {
            echo '<option value="' . esc_attr((string) $page->ID) . '">' . esc_html((string) $page->post_title) . '</option>';
        }
        echo '</select> <button class="button" type="submit">Tilføj side</button></form></div>';

        echo '<div><h4>Custom link</h4>';
        self::formStart(self::ACTION_ADD, 'add_custom_' . $menuId);
        echo '<input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '"><input type="hidden" name="item_kind" value="custom">';
        wp_nonce_field('h18_clean_nav_add_' . $menuId);
        echo '<p><input name="custom_title" placeholder="Titel" required></p><p><input class="regular-text" type="url" name="custom_url" placeholder="https://…" required></p><button class="button" type="submit">Tilføj link</button></form></div>';
        echo '</div></section>';
    }

    /** @param array<int,\WP_Term> $menus */
    private static function renderLocations(array $menus): void
    {
        $registered = get_registered_nav_menus();
        $locations = get_nav_menu_locations();
        if (!$registered) {
            echo '<p>Det aktive tema registrerer ingen klassiske menu-locations. Det forhindrer ikke senere brug af et Visual Designer Menu-element, som kan vælge en menu direkte.</p>';
            return;
        }
        self::formStart(self::ACTION_LOCATIONS, 'locations');
        wp_nonce_field('h18_clean_nav_locations');
        echo '<table class="widefat striped"><thead><tr><th>Location</th><th>Menu</th></tr></thead><tbody>';
        foreach ($registered as $key => $label) {
            echo '<tr><td><strong>' . esc_html((string) $label) . '</strong><br><code>' . esc_html((string) $key) . '</code></td><td><select name="locations[' . esc_attr((string) $key) . ']"><option value="0">Ikke tildelt</option>';
            foreach ($menus as $menu) {
                echo '<option value="' . esc_attr((string) $menu->term_id) . '"' . selected((int) ($locations[$key] ?? 0), (int) $menu->term_id, false) . '>' . esc_html((string) $menu->name) . '</option>';
            }
            echo '</select></td></tr>';
        }
        echo '</tbody></table><p><button class="button button-primary" type="submit">Gem locations</button></p></form>';
    }

    private static function snapshot(string $reason): void
    {
        $history = get_option(self::HISTORY_OPTION, []);
        $history = is_array($history) ? array_values(array_filter($history, 'is_array')) : [];
        $menusOut = [];
        foreach (wp_get_nav_menus() as $menu) {
            $itemsOut = [];
            $items = wp_get_nav_menu_items((int) $menu->term_id, ['post_status' => 'any']);
            foreach (is_array($items) ? $items : [] as $item) {
                $itemsOut[] = [
                    'sourceId' => (int) $item->ID,
                    'title' => (string) $item->title,
                    'url' => (string) $item->url,
                    'type' => (string) $item->type,
                    'object' => (string) $item->object,
                    'objectId' => (int) $item->object_id,
                    'parentSourceId' => (int) $item->menu_item_parent,
                    'order' => (int) $item->menu_order,
                    'target' => (string) $item->target,
                    'classes' => is_array($item->classes) ? array_values($item->classes) : [],
                ];
            }
            $menusOut[] = [
                'sourceId' => (int) $menu->term_id,
                'name' => (string) $menu->name,
                'slug' => (string) $menu->slug,
                'items' => $itemsOut,
            ];
        }
        $history[] = [
            'savedUtc' => gmdate('c'),
            'userId' => get_current_user_id(),
            'reason' => sanitize_text_field($reason),
            'locations' => get_nav_menu_locations(),
            'menus' => $menusOut,
        ];
        if (count($history) > self::MAX_HISTORY) {
            $history = array_slice($history, -self::MAX_HISTORY);
        }
        update_option(self::HISTORY_OPTION, $history, false);
    }

    /** @return \WP_Term */
    private static function requireMenu(int $menuId)
    {
        $menu = wp_get_nav_menu_object($menuId);
        if (!$menu instanceof \WP_Term) {
            wp_die(esc_html__('Menuen findes ikke.', 'hangar18-manager-clean'));
        }
        return $menu;
    }

    private static function formStart(string $action, string $suffix): void
    {
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr($action) . '">';
    }

    private static function url(int $menuId = 0): string
    {
        $url = admin_url('admin.php?page=h18-clean-menu');
        return $menuId > 0 ? add_query_arg('menu_id', $menuId, $url) : $url;
    }

    private static function redirect(int $menuId, string $notice): void
    {
        $url = self::url($menuId);
        wp_safe_redirect(add_query_arg('h18_nav_notice', rawurlencode($notice), $url));
        exit;
    }

    private static function guard(): void
    {
        if (!current_user_can('edit_theme_options')) {
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
        }
    }
}
