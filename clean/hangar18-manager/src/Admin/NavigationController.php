<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

final class NavigationController
{
    private const HISTORY_OPTION = 'h18_clean_navigation_history_v1';
    private const MAX_HISTORY = 30;
    private const ACTION_CREATE = 'h18_clean_nav_create';
    private const ACTION_ADD = 'h18_clean_nav_add';
    private const ACTION_SAVE = 'h18_clean_nav_save';
    private const ACTION_DELETE_ITEM = 'h18_clean_nav_delete_item';
    private const ACTION_LOCATIONS = 'h18_clean_nav_locations';
    private const ACTION_RESTORE = 'h18_clean_nav_restore';

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 8);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        add_action('admin_post_' . self::ACTION_CREATE, [self::class, 'createMenu']);
        add_action('admin_post_' . self::ACTION_ADD, [self::class, 'addItem']);
        add_action('admin_post_' . self::ACTION_SAVE, [self::class, 'saveMenu']);
        add_action('admin_post_' . self::ACTION_DELETE_ITEM, [self::class, 'deleteItem']);
        add_action('admin_post_' . self::ACTION_LOCATIONS, [self::class, 'saveLocations']);
        add_action('admin_post_' . self::ACTION_RESTORE, [self::class, 'restoreSnapshot']);
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

    public static function enqueue(string $hook): void
    {
        if (!current_user_can('edit_theme_options') || sanitize_key((string) ($_GET['page'] ?? '')) !== 'h18-clean-menu') {
            return;
        }
        wp_enqueue_style('h18-clean-menu-v0156', H18_CLEAN_URL . 'assets/admin-v0156-menu.css', [], H18_CLEAN_VERSION);
        wp_enqueue_script('h18-clean-menu-v0156', H18_CLEAN_URL . 'assets/admin-v0156-menu.js', [], H18_CLEAN_VERSION, true);
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
        if (!$selected instanceof \WP_Term && !empty($menus)) {
            $selectedId = (int) $menus[0]->term_id;
            $selected = wp_get_nav_menu_object($selectedId);
        }
        $history = self::history();
        $selectedSnapshot = sanitize_text_field((string) wp_unslash($_GET['snapshot'] ?? ''));

        echo '<div class="wrap h18-manager-admin h18-menu-visual-admin" data-vd-menu-root>';
        echo '<h1>Menu</h1>';
        echo '<p class="h18-manager-description">Byg sidens navigation ved at flytte og redigere de menupunkter, besøgende faktisk ser. Visual Designer styrer udseendet; WordPress-menuen er fortsat den eneste datakilde.</p>';
        self::notice();

        if (!$menus) {
            echo '<section class="h18-manager-card h18-menu-empty"><h2>Opret din første menu</h2><p>Start med én hovedmenu. Når den er oprettet, kan du vælge publicerede sider med få klik og trække dem i den ønskede rækkefølge.</p>';
            echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::ACTION_CREATE) . '">';
            wp_nonce_field('h18_clean_nav_create');
            echo '<label><strong>Navn</strong><input class="regular-text" name="menu_name" value="Hovedmenu" required></label> <button class="button button-primary" type="submit">Opret Hovedmenu</button></form></section>';
            echo '</div>';
            return;
        }

        echo '<section class="h18-manager-card h18-menu-picker"><div><span class="h18-menu-kicker">Aktuel menu</span><h2>' . esc_html($selected instanceof \WP_Term ? (string) $selected->name : 'Menu') . '</h2></div>';
        if (count($menus) > 1) {
            echo '<form method="get"><input type="hidden" name="page" value="h18-clean-menu"><label><span class="screen-reader-text">Skift menu</span><select name="menu_id" onchange="this.form.submit()">';
            foreach ($menus as $menu) {
                echo '<option value="' . esc_attr((string) $menu->term_id) . '"' . selected($selectedId, (int) $menu->term_id, false) . '>' . esc_html((string) $menu->name) . '</option>';
            }
            echo '</select></label></form>';
        } else {
            echo '<span class="h18-manager-badge is-ok">Hovedmenu</span>';
        }
        echo '</section>';

        if ($selected instanceof \WP_Term) {
            self::renderSelectedMenu((int) $selected->term_id, (string) $selected->name);
        }

        echo '<details class="h18-manager-card h18-menu-advanced"' . ($selectedSnapshot !== '' ? ' open' : '') . '><summary><strong>⚙ Avancerede indstillinger</strong><span>Flere menuer, theme-locations og versionshistorik</span></summary><div class="h18-menu-advanced-body">';
        echo '<div class="h18-manager-two-col">';
        self::renderMenuList($menus, $selectedId);
        echo '<section class="h18-manager-card"><h2>Theme locations</h2>';
        self::renderLocations($menus);
        echo '<p class="description">Theme locations er en teknisk WordPress-kobling. Visual Designer Menu-elementet kan fortsat vælge menuen direkte.</p></section>';
        echo '</div>';
        self::renderHistory($history, $selectedSnapshot);
        echo '</div></details>';
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
        $kind = sanitize_key((string) ($_POST['item_kind'] ?? 'pages'));

        if ($kind === 'pages' || $kind === 'page') {
            $pageIds = $kind === 'page'
                ? [absint($_POST['page_id'] ?? 0)]
                : array_values(array_unique(array_filter(array_map('absint', self::postedArray('page_ids')))));
            if (!$pageIds) {
                self::redirect($menuId, 'Vælg mindst én publiceret side.');
            }

            $existing = wp_get_nav_menu_items($menuId, ['post_status' => 'any']);
            $usedPageIds = [];
            foreach (is_array($existing) ? $existing : [] as $item) {
                if ((string) $item->type === 'post_type' && (string) $item->object === 'page') {
                    $usedPageIds[(int) $item->object_id] = true;
                }
            }

            $valid = [];
            foreach (array_slice($pageIds, 0, 100) as $pageId) {
                $page = get_post($pageId);
                if (!$page instanceof \WP_Post || $page->post_type !== 'page' || $page->post_status !== 'publish' || isset($usedPageIds[$pageId])) {
                    continue;
                }
                $valid[] = $pageId;
            }
            if (!$valid) {
                self::redirect($menuId, 'De valgte sider er allerede i menuen eller er ikke publiceret.');
            }

            self::snapshot('Før tilføjelse af sider til menu');
            $added = 0;
            foreach ($valid as $pageId) {
                $result = wp_update_nav_menu_item($menuId, 0, [
                    'menu-item-object-id' => $pageId,
                    'menu-item-object' => 'page',
                    'menu-item-type' => 'post_type',
                    'menu-item-status' => 'publish',
                ]);
                if (is_wp_error($result)) {
                    wp_die(esc_html($result->get_error_message()));
                }
                $added++;
            }
            self::redirect($menuId, $added === 1 ? 'Siden er tilføjet til menuen.' : $added . ' sider er tilføjet til menuen.');
        }

        $title = sanitize_text_field((string) wp_unslash($_POST['custom_title'] ?? ''));
        if ($title === '') {
            self::redirect($menuId, 'Menutekst mangler.');
        }

        self::snapshot($kind === 'heading' ? 'Før tilføjelse af menuoverskrift' : 'Før tilføjelse af eksternt link');
        if ($kind === 'heading') {
            $result = wp_update_nav_menu_item($menuId, 0, [
                'menu-item-title' => $title,
                'menu-item-url' => '#',
                'menu-item-type' => 'custom',
                'menu-item-status' => 'publish',
                'menu-item-classes' => 'vd-menu-heading',
            ]);
        } else {
            $url = esc_url_raw((string) wp_unslash($_POST['custom_url'] ?? ''));
            if ($url === '') {
                self::redirect($menuId, 'URL mangler eller er ugyldig.');
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
        self::redirect($menuId, $kind === 'heading' ? 'Overskrift tilføjet.' : 'Link tilføjet.');
    }

    public static function saveMenu(): void
    {
        self::guard();
        $menuId = absint($_POST['menu_id'] ?? 0);
        check_admin_referer('h18_clean_nav_save_' . $menuId);
        $menu = self::requireMenu($menuId);

        $items = wp_get_nav_menu_items($menuId, ['post_status' => 'any']);
        $items = is_array($items) ? $items : [];
        $deleteItemId = absint($_POST['delete_item_id'] ?? 0);
        if ($deleteItemId > 0) {
            $belongs = false;
            foreach ($items as $item) {
                if ((int) $item->ID === $deleteItemId) {
                    $belongs = true;
                    break;
                }
            }
            if (!$belongs) {
                wp_die(esc_html__('Menupunktet tilhører ikke denne menu.', 'visual-designer-manager'));
            }
            self::snapshot('Før fjernelse af menupunkt');
            wp_delete_post($deleteItemId, true);
            self::redirect($menuId, 'Menupunkt fjernet fra menuen.');
        }

        $titles = self::postedArray('item_title');
        $parents = self::postedArray('item_parent');
        $orders = self::postedArray('item_order');
        $parentMap = [];
        foreach ($items as $item) {
            $id = (int) $item->ID;
            $parentMap[$id] = absint($parents[$id] ?? $item->menu_item_parent);
        }
        self::validateParentMap($parentMap);

        self::snapshot('Før ændring af menu ' . (string) $menu->name);
        $newName = sanitize_text_field((string) wp_unslash($_POST['menu_name'] ?? ''));
        if ($newName !== '' && $newName !== (string) $menu->name) {
            $renamed = wp_update_nav_menu_object($menuId, ['menu-name' => $newName]);
            if (is_wp_error($renamed)) {
                wp_die(esc_html($renamed->get_error_message()));
            }
        }

        foreach ($items as $item) {
            $id = (int) $item->ID;
            $args = [
                'menu-item-title' => sanitize_text_field((string) wp_unslash($titles[$id] ?? $item->title)),
                'menu-item-parent-id' => (int) ($parentMap[$id] ?? 0),
                'menu-item-position' => max(1, absint($orders[$id] ?? $item->menu_order)),
                'menu-item-status' => 'publish',
                'menu-item-type' => (string) $item->type,
                'menu-item-object' => (string) $item->object,
                'menu-item-object-id' => (int) $item->object_id,
                'menu-item-target' => (string) $item->target,
                'menu-item-classes' => self::menuItemClasses($item->classes),
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
            wp_die(esc_html__('Ugyldigt menupunkt.', 'visual-designer-manager'));
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
        $posted = self::postedArray('locations');
        $locations = get_nav_menu_locations();
        foreach ($registered as $key => $label) {
            $locations[$key] = absint($posted[$key] ?? 0);
        }
        set_theme_mod('nav_menu_locations', $locations);
        self::redirect(0, 'Theme locations gemt.');
    }

    public static function restoreSnapshot(): void
    {
        self::guard();
        $fingerprint = sanitize_text_field((string) wp_unslash($_POST['snapshot'] ?? ''));
        if ($fingerprint === '') {
            wp_die(esc_html__('Snapshot mangler.', 'visual-designer-manager'));
        }
        check_admin_referer('h18_clean_nav_restore_' . $fingerprint);
        $entry = self::findSnapshot($fingerprint);
        if ($entry === null) {
            wp_die(esc_html__('Snapshot findes ikke længere.', 'visual-designer-manager'));
        }

        self::validateSnapshot($entry);
        self::snapshot('Sikkerhedskopi før gendannelse af navigation');

        try {
            self::applySnapshot($entry);
        } catch (\Throwable $error) {
            wp_die(esc_html('Gendannelse fejlede: ' . $error->getMessage() . ' En sikkerhedskopi af navigationen før forsøget er gemt.'));
        }

        self::redirect(0, 'Navigation gendannet fra snapshot ' . self::formatSaved((string) ($entry['savedUtc'] ?? '')) . '.');
    }

    /** @param array<int,\WP_Term> $menus */
    private static function renderMenuList(array $menus, int $selectedId): void
    {
        echo '<section class="h18-manager-card"><h2>Menuer</h2>';
        if (!$menus) {
            echo '<p>Der er endnu ingen klassiske WordPress-menuer.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Navn</th><th>Elementer</th><th></th></tr></thead><tbody>';
            foreach ($menus as $menu) {
                $items = wp_get_nav_menu_items((int) $menu->term_id);
                $active = (int) $menu->term_id === $selectedId ? ' button-primary' : '';
                echo '<tr><td><strong>' . esc_html((string) $menu->name) . '</strong></td><td>' . esc_html((string) count(is_array($items) ? $items : [])) . '</td><td><a class="button' . esc_attr($active) . '" href="' . esc_url(self::url((int) $menu->term_id)) . '">Redigér</a></td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '<h3>Ny menu</h3><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        echo '<input type="hidden" name="action" value="' . esc_attr(self::ACTION_CREATE) . '">';
        wp_nonce_field('h18_clean_nav_create');
        echo '<label><strong>Navn</strong><br><input class="regular-text" name="menu_name" required></label> ';
        echo '<button class="button button-primary" type="submit">Opret menu</button></form></section>';
    }

    private static function renderSelectedMenu(int $menuId, string $menuName): void
    {
        $items = wp_get_nav_menu_items($menuId, ['post_status' => 'any']);
        $items = is_array($items) ? array_values($items) : [];
        $parentMap = [];
        foreach ($items as $item) {
            $parentMap[(int) $item->ID] = (int) $item->menu_item_parent;
        }
        $depthOf = static function (int $id) use ($parentMap): int {
            $depth = 0;
            $seen = [];
            $cursor = (int) ($parentMap[$id] ?? 0);
            while ($cursor > 0 && isset($parentMap[$cursor]) && !isset($seen[$cursor]) && $depth < 6) {
                $seen[$cursor] = true;
                $depth++;
                $cursor = (int) ($parentMap[$cursor] ?? 0);
            }
            return $depth;
        };

        echo '<section class="h18-manager-card h18-menu-editor-shell">';
        echo '<div class="h18-menu-editor-head"><div><span class="h18-menu-kicker">Menupunkter</span><h2>' . esc_html($menuName) . '</h2><p>Træk punkterne op eller ned. Brug <strong>↳</strong> til undermenu og <strong>←</strong> til at flytte et niveau ud. Klik Redigér hvis menuteksten skal ændres.</p></div><div class="h18-menu-primary-actions"><button class="button button-primary" type="button" data-menu-add-open>+ Tilføj menupunkt</button><button class="button button-primary" type="submit" form="h18-menu-main-form">Gem menu</button></div></div>';

        echo '<div class="h18-menu-workspace"><div class="h18-menu-structure">';
        echo '<form id="h18-menu-main-form" method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::ACTION_SAVE) . '"><input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '">';
        wp_nonce_field('h18_clean_nav_save_' . $menuId);
        echo '<input type="hidden" name="menu_name" value="' . esc_attr($menuName) . '">';

        if ($items) {
            echo '<ol id="h18-menu-sort-list" class="h18-menu-visual-list" aria-label="Menupunkter">';
            foreach ($items as $item) {
                $id = (int) $item->ID;
                $classes = is_array($item->classes) ? array_map('strval', $item->classes) : [];
                $isHeading = in_array('vd-menu-heading', $classes, true);
                $typeLabel = $isHeading ? 'Overskrift' : (((string) $item->type === 'post_type' && (string) $item->object === 'page') ? 'Side' : 'Link');
                $destination = $isHeading ? 'Ingen destination · bruges som gruppeoverskrift' : (string) $item->url;
                $depth = $depthOf($id);
                echo '<li class="h18-menu-sort-row" draggable="true" data-menu-item-id="' . esc_attr((string) $id) . '" data-parent-id="' . esc_attr((string) $item->menu_item_parent) . '" style="--vd-menu-depth:' . esc_attr((string) $depth) . '">';
                echo '<div class="h18-menu-item-main"><span class="h18-menu-drag-handle" title="Træk for at flytte" aria-label="Træk for at flytte" tabindex="0">☰</span><div class="h18-menu-item-copy"><strong class="h18-menu-item-title-preview">' . esc_html((string) $item->title) . '</strong><span><span class="h18-menu-type-badge">' . esc_html($typeLabel) . '</span> <small class="h18-menu-destination">' . esc_html($destination) . '</small></span></div>';
                echo '<div class="h18-menu-item-buttons"><button type="button" class="button button-small" data-menu-move="up" title="Flyt op" aria-label="Flyt op">↑</button><button type="button" class="button button-small" data-menu-move="down" title="Flyt ned" aria-label="Flyt ned">↓</button><button type="button" class="button button-small" data-menu-outdent title="Flyt et niveau ud" aria-label="Flyt et niveau ud">←</button><button type="button" class="button button-small" data-menu-indent title="Gør til undermenu under forrige punkt" aria-label="Gør til undermenu">↳</button><button type="button" class="button" data-menu-edit aria-expanded="false">Redigér</button></div></div>';
                echo '<div class="h18-menu-item-editor" hidden><label><strong>Menutekst</strong><input class="regular-text h18-menu-title-input" name="item_title[' . esc_attr((string) $id) . ']" value="' . esc_attr((string) $item->title) . '"></label><p class="description"><strong>Destination:</strong> ' . esc_html($destination) . '</p><button class="button h18-menu-remove" type="submit" name="delete_item_id" value="' . esc_attr((string) $id) . '" onclick="return confirm(\'Fjern dette punkt fra menuen? Selve siden slettes ikke.\');">Fjern fra menu</button></div>';
                echo '<input class="h18-menu-parent-input" type="hidden" name="item_parent[' . esc_attr((string) $id) . ']" value="' . esc_attr((string) $item->menu_item_parent) . '"><input class="h18-menu-order-input" type="hidden" name="item_order[' . esc_attr((string) $id) . ']" value="' . esc_attr((string) $item->menu_order) . '">';
                echo '</li>';
            }
            echo '</ol>';
        } else {
            echo '<div class="h18-menu-empty-list"><strong>Menuen er tom</strong><p>Tilføj de sider, der skal kunne vælges i navigationen.</p><button class="button button-primary" type="button" data-menu-add-open>+ Tilføj menupunkt</button></div>';
        }

        echo '<div class="h18-menu-form-footer"><button class="button button-primary" type="submit">Gem menu</button><span class="description">Rækkefølge og undermenuer gemmes først, når du trykker Gem menu.</span></div></form></div>';

        echo '<aside class="h18-menu-preview-panel"><h3>Struktur-preview</h3><p class="description">Preview viser rækkefølge og undermenuer. Farver og typografi styres fortsat i Visual Designer.</p><div class="h18-menu-preview-device"><strong>Desktop</strong><nav id="h18-menu-preview-desktop" aria-label="Desktop menu preview"></nav></div><div class="h18-menu-preview-device"><strong>Mobil</strong><div class="h18-menu-mobile-bar"><span>Menu</span><span>☰</span></div><nav id="h18-menu-preview-mobile" aria-label="Mobil menu preview"></nav></div></aside></div>';

        self::renderAddItems($menuId, $items);
        echo '</section>';
    }

    /** @param array<int,\WP_Post> $items */
    private static function renderAddItems(int $menuId, array $items = []): void
    {
        $usedPages = [];
        foreach ($items as $item) {
            if ((string) $item->type === 'post_type' && (string) $item->object === 'page') {
                $usedPages[(int) $item->object_id] = true;
            }
        }
        $pages = get_pages([
            'sort_column' => 'post_title',
            'sort_order' => 'ASC',
            'post_status' => 'publish',
        ]);

        echo '<div id="h18-menu-add-dialog" class="h18-menu-dialog" hidden><div class="h18-menu-dialog-backdrop" data-menu-add-close></div><section class="h18-menu-dialog-card" role="dialog" aria-modal="true" aria-labelledby="h18-menu-add-title"><div class="h18-menu-dialog-head"><div><span class="h18-menu-kicker">Menu</span><h2 id="h18-menu-add-title">Tilføj menupunkt</h2></div><button type="button" class="button" data-menu-add-close aria-label="Luk">✕</button></div>';
        echo '<div class="h18-menu-add-tabs" role="tablist"><button type="button" class="button button-primary" data-menu-add-tab="pages">Sider</button><button type="button" class="button" data-menu-add-tab="link">Eksternt link</button><button type="button" class="button" data-menu-add-tab="heading">Overskrift</button></div>';

        echo '<div class="h18-menu-add-panel" data-menu-add-panel="pages"><h3>Publicerede sider</h3><p class="description">Vælg én eller flere sider. Sider, der allerede er i menuen, kan ikke vælges igen.</p>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::ACTION_ADD) . '"><input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '"><input type="hidden" name="item_kind" value="pages">';
        wp_nonce_field('h18_clean_nav_add_' . $menuId);
        echo '<div class="h18-menu-page-picker">';
        $selectable = 0;
        foreach ($pages as $page) {
            if (!$page instanceof \WP_Post) { continue; }
            $used = isset($usedPages[(int) $page->ID]);
            if (!$used) { $selectable++; }
            echo '<label class="h18-menu-page-choice' . ($used ? ' is-used' : '') . '"><input type="checkbox" name="page_ids[]" value="' . esc_attr((string) $page->ID) . '"' . ($used ? ' disabled' : '') . '><span><strong>' . esc_html((string) $page->post_title) . '</strong><small>/' . esc_html((string) $page->post_name) . '/</small></span>' . ($used ? '<em>Allerede i menuen</em>' : '') . '</label>';
        }
        if (!$pages) {
            echo '<p>Der er ingen publicerede sider endnu.</p>';
        }
        echo '</div><p><button class="button button-primary" type="submit"' . ($selectable === 0 ? ' disabled' : '') . '>Tilføj valgte</button></p></form></div>';

        echo '<div class="h18-menu-add-panel" data-menu-add-panel="link" hidden><h3>Eksternt link</h3><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::ACTION_ADD) . '"><input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '"><input type="hidden" name="item_kind" value="custom">';
        wp_nonce_field('h18_clean_nav_add_' . $menuId);
        echo '<label><strong>Menutekst</strong><input class="regular-text" name="custom_title" required placeholder="Ekstern side"></label><label><strong>URL</strong><input class="regular-text" type="url" name="custom_url" placeholder="https://…" required></label><p><button class="button button-primary" type="submit">Tilføj link</button></p></form></div>';

        echo '<div class="h18-menu-add-panel" data-menu-add-panel="heading" hidden><h3>Overskrift / gruppe</h3><p class="description">Bruges som et ikke-sidemål, som andre punkter kan ligge under.</p><form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::ACTION_ADD) . '"><input type="hidden" name="menu_id" value="' . esc_attr((string) $menuId) . '"><input type="hidden" name="item_kind" value="heading">';
        wp_nonce_field('h18_clean_nav_add_' . $menuId);
        echo '<label><strong>Tekst</strong><input class="regular-text" name="custom_title" required placeholder="Køretøjer"></label><p><button class="button button-primary" type="submit">Tilføj overskrift</button></p></form></div>';
        echo '</section></div>';
    }

    /** @param array<int,\WP_Term> $menus */
    private static function renderLocations(array $menus): void
    {
        $registered = get_registered_nav_menus();
        $locations = get_nav_menu_locations();
        if (!$registered) {
            echo '<p>Det aktive tema registrerer ingen klassiske menu-locations. Et senere Visual Designer Menu-element kan stadig vælge en menu direkte.</p>';
            return;
        }
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '"><input type="hidden" name="action" value="' . esc_attr(self::ACTION_LOCATIONS) . '">';
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

    /** @param array<int,array<string,mixed>> $history */
    private static function renderHistory(array $history, string $selectedFingerprint): void
    {
        echo '<section class="h18-manager-card"><h2>Navigationens versionshistorik</h2>';
        echo '<p>Før Manageren ændrer navigation eller theme-location, gemmes et komplet snapshot. Gendannelse er ikke-destruktiv i historikken: den aktuelle navigation gemmes automatisk som et nyt sikkerhedssnapshot, før et ældre snapshot anvendes.</p>';

        if (!$history) {
            echo '<p>Der er endnu ingen snapshots.</p></section>';
            return;
        }

        echo '<table class="widefat striped h18-manager-table"><thead><tr><th>Dato</th><th>Årsag</th><th>Menuer</th><th>Punkter</th><th>Bruger</th><th></th></tr></thead><tbody>';
        foreach (array_reverse($history) as $entry) {
            $fingerprint = self::fingerprint($entry);
            $menuCount = isset($entry['menus']) && is_array($entry['menus']) ? count($entry['menus']) : 0;
            $itemCount = self::snapshotItemCount($entry);
            $user = get_userdata(absint($entry['userId'] ?? 0));
            echo '<tr><td>' . esc_html(self::formatSaved((string) ($entry['savedUtc'] ?? ''))) . '</td><td>' . esc_html((string) ($entry['reason'] ?? 'Snapshot')) . '</td>';
            echo '<td>' . esc_html((string) $menuCount) . '</td><td>' . esc_html((string) $itemCount) . '</td><td>' . esc_html($user ? (string) $user->display_name : '—') . '</td>';
            echo '<td><a class="button' . ($fingerprint === $selectedFingerprint ? ' button-primary' : '') . '" href="' . esc_url(add_query_arg('snapshot', $fingerprint, self::url())) . '">Detaljer</a></td></tr>';
        }
        echo '</tbody></table>';

        if ($selectedFingerprint !== '') {
            $entry = self::findSnapshot($selectedFingerprint);
            if ($entry !== null) {
                self::renderSnapshotDetails($entry, $selectedFingerprint);
            } else {
                echo '<div class="notice notice-warning inline"><p>Det valgte snapshot findes ikke længere i de seneste ' . esc_html((string) self::MAX_HISTORY) . ' versioner.</p></div>';
            }
        }
        echo '</section>';
    }

    /** @param array<string,mixed> $entry */
    private static function renderSnapshotDetails(array $entry, string $fingerprint): void
    {
        echo '<div class="h18-clean-update-details"><h3>Snapshot ' . esc_html(self::formatSaved((string) ($entry['savedUtc'] ?? ''))) . '</h3>';
        echo '<p><strong>Årsag:</strong> ' . esc_html((string) ($entry['reason'] ?? 'Snapshot')) . '<br><strong>Fingerprint:</strong> <code>' . esc_html($fingerprint) . '</code></p>';

        $menus = isset($entry['menus']) && is_array($entry['menus']) ? $entry['menus'] : [];
        if (!$menus) {
            echo '<p>Snapshot indeholder ingen menuer.</p>';
        } else {
            foreach ($menus as $menu) {
                if (!is_array($menu)) {
                    continue;
                }
                $items = isset($menu['items']) && is_array($menu['items']) ? $menu['items'] : [];
                echo '<details><summary><strong>' . esc_html((string) ($menu['name'] ?? 'Menu')) . '</strong> · ' . esc_html((string) count($items)) . ' punkter</summary>';
                if ($items) {
                    echo '<table class="widefat striped"><thead><tr><th>Position</th><th>Titel</th><th>Type</th><th>Parent-ID</th><th>URL</th></tr></thead><tbody>';
                    foreach ($items as $item) {
                        if (!is_array($item)) {
                            continue;
                        }
                        echo '<tr><td>' . esc_html((string) absint($item['order'] ?? 0)) . '</td><td>' . esc_html((string) ($item['title'] ?? '')) . '</td><td><code>' . esc_html((string) ($item['type'] ?? '')) . '</code></td><td>' . esc_html((string) absint($item['parentSourceId'] ?? 0)) . '</td><td><small>' . esc_html((string) ($item['url'] ?? '')) . '</small></td></tr>';
                    }
                    echo '</tbody></table>';
                }
                echo '</details>';
            }
        }

        $locations = isset($entry['locations']) && is_array($entry['locations']) ? $entry['locations'] : [];
        if ($locations) {
            echo '<h4>Theme locations</h4><table class="widefat striped"><thead><tr><th>Location</th><th>Menu source-ID</th></tr></thead><tbody>';
            foreach ($locations as $location => $menuId) {
                echo '<tr><td><code>' . esc_html((string) $location) . '</code></td><td>' . esc_html((string) absint($menuId)) . '</td></tr>';
            }
            echo '</tbody></table>';
        }

        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" onsubmit="return confirm(\'Gendan hele navigationen til dette snapshot? Nuværende menuer og theme-locations bliver først gemt som et nyt sikkerhedssnapshot.\');">';
        echo '<input type="hidden" name="action" value="' . esc_attr(self::ACTION_RESTORE) . '"><input type="hidden" name="snapshot" value="' . esc_attr($fingerprint) . '">';
        wp_nonce_field('h18_clean_nav_restore_' . $fingerprint);
        echo '<p><button class="button button-primary" type="submit">Gendan dette snapshot</button></p></form></div>';
    }

    private static function snapshot(string $reason): void
    {
        $history = self::history();
        $entry = self::captureSnapshot($reason);
        $history[] = $entry;
        if (count($history) > self::MAX_HISTORY) {
            $history = array_slice($history, -self::MAX_HISTORY);
        }
        update_option(self::HISTORY_OPTION, $history, false);
    }

    /** @return array<string,mixed> */
    private static function captureSnapshot(string $reason): array
    {
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
                    'attrTitle' => (string) $item->attr_title,
                    'description' => (string) $item->description,
                    'xfn' => (string) $item->xfn,
                ];
            }
            $menusOut[] = [
                'sourceId' => (int) $menu->term_id,
                'name' => (string) $menu->name,
                'slug' => (string) $menu->slug,
                'items' => $itemsOut,
            ];
        }

        return [
            'schemaVersion' => 1,
            'savedUtc' => gmdate('c'),
            'userId' => get_current_user_id(),
            'reason' => sanitize_text_field($reason),
            'locations' => get_nav_menu_locations(),
            'menus' => $menusOut,
        ];
    }

    /** @return array<int,array<string,mixed>> */
    private static function history(): array
    {
        $history = get_option(self::HISTORY_OPTION, []);
        return is_array($history) ? array_values(array_filter($history, 'is_array')) : [];
    }

    /** @param array<string,mixed> $entry */
    private static function fingerprint(array $entry): string
    {
        $payload = wp_json_encode([
            'savedUtc' => (string) ($entry['savedUtc'] ?? ''),
            'userId' => absint($entry['userId'] ?? 0),
            'reason' => (string) ($entry['reason'] ?? ''),
            'locations' => isset($entry['locations']) && is_array($entry['locations']) ? $entry['locations'] : [],
            'menus' => isset($entry['menus']) && is_array($entry['menus']) ? $entry['menus'] : [],
        ], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($payload)) {
            $payload = serialize($entry);
        }
        return substr(hash('sha256', $payload), 0, 24);
    }

    /** @return array<string,mixed>|null */
    private static function findSnapshot(string $fingerprint): ?array
    {
        foreach (self::history() as $entry) {
            if (hash_equals(self::fingerprint($entry), $fingerprint)) {
                return $entry;
            }
        }
        return null;
    }

    /** @param array<string,mixed> $entry */
    private static function validateSnapshot(array $entry): void
    {
        if (!isset($entry['menus']) || !is_array($entry['menus']) || !isset($entry['locations']) || !is_array($entry['locations'])) {
            throw new \RuntimeException('Snapshotformatet er ugyldigt.');
        }
        $menuIds = [];
        foreach ($entry['menus'] as $menu) {
            if (!is_array($menu)) {
                throw new \RuntimeException('Snapshot indeholder en ugyldig menu.');
            }
            $sourceId = absint($menu['sourceId'] ?? 0);
            if ($sourceId <= 0 || isset($menuIds[$sourceId])) {
                throw new \RuntimeException('Snapshot har manglende eller dublerede menu-IDer.');
            }
            $menuIds[$sourceId] = true;
            $items = isset($menu['items']) && is_array($menu['items']) ? $menu['items'] : [];
            $itemIds = [];
            foreach ($items as $item) {
                if (!is_array($item)) {
                    throw new \RuntimeException('Snapshot indeholder et ugyldigt menupunkt.');
                }
                $itemId = absint($item['sourceId'] ?? 0);
                if ($itemId <= 0 || isset($itemIds[$itemId])) {
                    throw new \RuntimeException('Snapshot har manglende eller dublerede menupunkt-IDer.');
                }
                $itemIds[$itemId] = true;
            }
        }
    }

    /** @param array<string,mixed> $entry */
    private static function applySnapshot(array $entry): void
    {
        $snapshotMenus = isset($entry['menus']) && is_array($entry['menus']) ? $entry['menus'] : [];
        $menuMap = [];
        $keepMenuIds = [];

        foreach ($snapshotMenus as $menuData) {
            if (!is_array($menuData)) {
                continue;
            }
            $sourceId = absint($menuData['sourceId'] ?? 0);
            $menu = $sourceId > 0 ? wp_get_nav_menu_object($sourceId) : false;
            if (!$menu instanceof \WP_Term) {
                $slug = sanitize_title((string) ($menuData['slug'] ?? ''));
                $menu = $slug !== '' ? get_term_by('slug', $slug, 'nav_menu') : false;
            }
            if (!$menu instanceof \WP_Term) {
                $name = sanitize_text_field((string) ($menuData['name'] ?? 'Gendannet menu'));
                $created = wp_create_nav_menu($name !== '' ? $name : 'Gendannet menu');
                if (is_wp_error($created)) {
                    throw new \RuntimeException($created->get_error_message());
                }
                $menu = wp_get_nav_menu_object((int) $created);
            }
            if (!$menu instanceof \WP_Term) {
                throw new \RuntimeException('En menu kunne ikke genskabes.');
            }

            $desiredName = sanitize_text_field((string) ($menuData['name'] ?? ''));
            if ($desiredName !== '' && $desiredName !== (string) $menu->name) {
                $renamed = wp_update_nav_menu_object((int) $menu->term_id, ['menu-name' => $desiredName]);
                if (is_wp_error($renamed)) {
                    throw new \RuntimeException($renamed->get_error_message());
                }
            }

            $menuMap[$sourceId] = (int) $menu->term_id;
            $keepMenuIds[(int) $menu->term_id] = true;
        }

        foreach (wp_get_nav_menus() as $currentMenu) {
            $currentId = (int) $currentMenu->term_id;
            if (!isset($keepMenuIds[$currentId])) {
                $deleted = wp_delete_nav_menu($currentId);
                if (is_wp_error($deleted)) {
                    throw new \RuntimeException($deleted->get_error_message());
                }
            }
        }

        foreach ($snapshotMenus as $menuData) {
            if (!is_array($menuData)) {
                continue;
            }
            $sourceMenuId = absint($menuData['sourceId'] ?? 0);
            $currentMenuId = (int) ($menuMap[$sourceMenuId] ?? 0);
            if ($currentMenuId <= 0) {
                continue;
            }

            $existingItems = wp_get_nav_menu_items($currentMenuId, ['post_status' => 'any']);
            foreach (is_array($existingItems) ? $existingItems : [] as $existingItem) {
                wp_delete_post((int) $existingItem->ID, true);
            }

            $items = isset($menuData['items']) && is_array($menuData['items']) ? array_values($menuData['items']) : [];
            usort($items, static function ($a, $b): int {
                $aOrder = is_array($a) ? absint($a['order'] ?? 0) : 0;
                $bOrder = is_array($b) ? absint($b['order'] ?? 0) : 0;
                return $aOrder <=> $bOrder;
            });

            $parentMap = [];
            foreach ($items as $itemData) {
                if (!is_array($itemData)) {
                    continue;
                }
                $sourceItemId = absint($itemData['sourceId'] ?? 0);
                $parentMap[$sourceItemId] = absint($itemData['parentSourceId'] ?? 0);
            }
            self::validateParentMap($parentMap);

            $itemMap = [];
            foreach ($items as $itemData) {
                if (!is_array($itemData)) {
                    continue;
                }
                $sourceItemId = absint($itemData['sourceId'] ?? 0);
                $created = wp_update_nav_menu_item($currentMenuId, 0, self::snapshotItemArgs($itemData, 0));
                if (is_wp_error($created)) {
                    $fallback = self::snapshotItemArgs($itemData, 0, true);
                    $created = wp_update_nav_menu_item($currentMenuId, 0, $fallback);
                }
                if (is_wp_error($created)) {
                    throw new \RuntimeException($created->get_error_message());
                }
                $itemMap[$sourceItemId] = (int) $created;
            }

            foreach ($items as $itemData) {
                if (!is_array($itemData)) {
                    continue;
                }
                $sourceItemId = absint($itemData['sourceId'] ?? 0);
                $currentItemId = (int) ($itemMap[$sourceItemId] ?? 0);
                if ($currentItemId <= 0) {
                    continue;
                }
                $sourceParentId = (int) ($parentMap[$sourceItemId] ?? 0);
                $currentParentId = $sourceParentId > 0 ? (int) ($itemMap[$sourceParentId] ?? 0) : 0;
                $updated = wp_update_nav_menu_item($currentMenuId, $currentItemId, self::snapshotItemArgs($itemData, $currentParentId));
                if (is_wp_error($updated)) {
                    $updated = wp_update_nav_menu_item($currentMenuId, $currentItemId, self::snapshotItemArgs($itemData, $currentParentId, true));
                }
                if (is_wp_error($updated)) {
                    throw new \RuntimeException($updated->get_error_message());
                }
            }
        }

        $registered = get_registered_nav_menus();
        $sourceLocations = isset($entry['locations']) && is_array($entry['locations']) ? $entry['locations'] : [];
        $restoredLocations = [];
        foreach ($registered as $location => $label) {
            $sourceMenuId = absint($sourceLocations[$location] ?? 0);
            $restoredLocations[$location] = $sourceMenuId > 0 ? (int) ($menuMap[$sourceMenuId] ?? 0) : 0;
        }
        set_theme_mod('nav_menu_locations', $restoredLocations);
    }

    /** @param array<string,mixed> $item */
    private static function snapshotItemArgs(array $item, int $parentId, bool $forceCustom = false): array
    {
        $type = sanitize_key((string) ($item['type'] ?? 'custom'));
        $url = esc_url_raw((string) ($item['url'] ?? ''));
        if ($forceCustom) {
            $type = 'custom';
        }

        $args = [
            'menu-item-title' => sanitize_text_field((string) ($item['title'] ?? '')),
            'menu-item-parent-id' => max(0, $parentId),
            'menu-item-position' => max(1, absint($item['order'] ?? 1)),
            'menu-item-status' => 'publish',
            'menu-item-target' => sanitize_key((string) ($item['target'] ?? '')),
            'menu-item-classes' => self::menuItemClasses($item['classes'] ?? []),
            'menu-item-attr-title' => sanitize_text_field((string) ($item['attrTitle'] ?? '')),
            'menu-item-description' => sanitize_textarea_field((string) ($item['description'] ?? '')),
            'menu-item-xfn' => sanitize_text_field((string) ($item['xfn'] ?? '')),
        ];

        if ($type === 'custom') {
            $args['menu-item-type'] = 'custom';
            $args['menu-item-url'] = $url !== '' ? $url : home_url('/');
            return $args;
        }

        $args['menu-item-type'] = $type;
        $args['menu-item-object'] = sanitize_key((string) ($item['object'] ?? ''));
        $args['menu-item-object-id'] = absint($item['objectId'] ?? 0);
        return $args;
    }

    /** @param array<string,mixed> $entry */
    private static function snapshotItemCount(array $entry): int
    {
        $count = 0;
        $menus = isset($entry['menus']) && is_array($entry['menus']) ? $entry['menus'] : [];
        foreach ($menus as $menu) {
            if (is_array($menu) && isset($menu['items']) && is_array($menu['items'])) {
                $count += count($menu['items']);
            }
        }
        return $count;
    }

    /** @param array<int,int> $parentMap */
    private static function validateParentMap(array &$parentMap): void
    {
        foreach ($parentMap as $id => &$parent) {
            if ($parent === $id || ($parent !== 0 && !isset($parentMap[$parent]))) {
                $parent = 0;
            }
        }
        unset($parent);
        foreach (array_keys($parentMap) as $start) {
            $seen = [];
            $cursor = $start;
            while ($cursor !== 0 && isset($parentMap[$cursor])) {
                if (isset($seen[$cursor])) {
                    $parentMap[$start] = 0;
                    break;
                }
                $seen[$cursor] = true;
                $cursor = (int) $parentMap[$cursor];
            }
        }
    }

    /** @param mixed $classes */
    private static function menuItemClasses($classes): string
    {
        if (is_string($classes)) {
            $classes = preg_split('/\s+/', trim($classes)) ?: [];
        }
        if (!is_array($classes)) {
            $classes = [];
        }

        $clean = [];
        foreach ($classes as $className) {
            $className = sanitize_html_class((string) $className);
            if ($className !== '') {
                $clean[] = $className;
            }
        }
        return implode(' ', array_values(array_unique($clean)));
    }

    /** @return array<mixed> */
    private static function postedArray(string $key): array
    {
        return isset($_POST[$key]) && is_array($_POST[$key]) ? wp_unslash($_POST[$key]) : [];
    }

    /** @return \WP_Term */
    private static function requireMenu(int $menuId)
    {
        $menu = wp_get_nav_menu_object($menuId);
        if (!$menu instanceof \WP_Term) {
            wp_die(esc_html__('Menuen findes ikke.', 'visual-designer-manager'));
        }
        return $menu;
    }

    private static function notice(): void
    {
        if (!isset($_GET['h18_nav_notice'])) {
            return;
        }
        $notice = sanitize_text_field((string) wp_unslash($_GET['h18_nav_notice']));
        echo '<div class="notice notice-success is-dismissible"><p>' . esc_html($notice) . '</p></div>';
    }

    private static function formatSaved(string $savedUtc): string
    {
        $timestamp = $savedUtc !== '' ? strtotime($savedUtc) : false;
        if ($timestamp === false) {
            return $savedUtc !== '' ? $savedUtc : 'Ukendt tidspunkt';
        }
        return wp_date('d-m-Y H:i', $timestamp);
    }

    private static function url(int $menuId = 0): string
    {
        $url = admin_url('admin.php?page=h18-clean-menu');
        return $menuId > 0 ? add_query_arg('menu_id', $menuId, $url) : $url;
    }

    private static function redirect(int $menuId, string $notice): void
    {
        wp_safe_redirect(add_query_arg('h18_nav_notice', rawurlencode($notice), self::url($menuId)));
        exit;
    }

    private static function guard(): void
    {
        if (!current_user_can('edit_theme_options')) {
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
        }
    }
}
