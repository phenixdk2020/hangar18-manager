from pathlib import Path
import json
import re

ROOT = Path('.')
NAV = ROOT / 'clean/hangar18-manager/src/Admin/NavigationController.php'
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
NOTES = ROOT / 'clean-release-notes.html'
HISTORY = ROOT / 'clean/hangar18-manager/release-history.json'
STATUS = ROOT / 'docs/v0156-status.md'
JS = ROOT / 'clean/hangar18-manager/assets/admin-v0156-menu.js'
CSS = ROOT / 'clean/hangar18-manager/assets/admin-v0156-menu.css'


def replace_block(text: str, pattern: str, replacement: str, label: str) -> str:
    new, count = re.subn(pattern, replacement.rstrip() + '\n', text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f'Could not replace {label}; matches={count}')
    return new

nav = NAV.read_text(encoding='utf-8')

nav = nav.replace(
    "wp_enqueue_style('h18-clean-menu-v0154', H18_CLEAN_URL . 'assets/admin-v0154-menu.css', [], H18_CLEAN_VERSION);\n        wp_enqueue_script('h18-clean-menu-v0154', H18_CLEAN_URL . 'assets/admin-v0154-menu.js', [], H18_CLEAN_VERSION, true);",
    "wp_enqueue_style('h18-clean-menu-v0156', H18_CLEAN_URL . 'assets/admin-v0156-menu.css', [], H18_CLEAN_VERSION);\n        wp_enqueue_script('h18-clean-menu-v0156', H18_CLEAN_URL . 'assets/admin-v0156-menu.js', [], H18_CLEAN_VERSION, true);"
)

render = r'''    public static function render(): void
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
'''
nav = replace_block(nav, r"    public static function render\(\): void\n    \{.*?(?=\n    public static function createMenu)", render, 'render')

add_item = r'''    public static function addItem(): void
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
                'menu-item-classes' => ['vd-menu-heading'],
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
'''
nav = replace_block(nav, r"    public static function addItem\(\): void\n    \{.*?(?=\n    public static function saveMenu)", add_item, 'addItem')

save_menu = r'''    public static function saveMenu(): void
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
                wp_die(esc_html__('Menupunktet tilhører ikke denne menu.', 'hangar18-manager-clean'));
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
'''
nav = replace_block(nav, r"    public static function saveMenu\(\): void\n    \{.*?(?=\n    public static function deleteItem)", save_menu, 'saveMenu')

selected_menu = r'''    private static function renderSelectedMenu(int $menuId, string $menuName): void
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
'''
nav = replace_block(nav, r"    private static function renderSelectedMenu\(int \$menuId, string \$menuName\): void\n    \{.*?(?=\n    private static function renderAddItems)", selected_menu, 'renderSelectedMenu')

add_items = r'''    /** @param array<int,\WP_Post> $items */
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
'''
nav = replace_block(nav, r"    private static function renderAddItems\(int \$menuId\): void\n    \{.*?(?=\n    /\*\* @param array<int,\\WP_Term> \$menus \*/\n    private static function renderLocations)", add_items, 'renderAddItems')

NAV.write_text(nav, encoding='utf-8')

js = r'''(function () {
    'use strict';

    function q(sel, root) { return (root || document).querySelector(sel); }
    function qa(sel, root) { return Array.from((root || document).querySelectorAll(sel)); }
    function rows(list) { return qa(':scope > .h18-menu-sort-row', list); }
    function itemId(row) { return parseInt(row && row.dataset.menuItemId || '0', 10) || 0; }
    function parentInput(row) { return q('.h18-menu-parent-input', row); }
    function parentId(row) { var input = parentInput(row); return parseInt(input && input.value || '0', 10) || 0; }
    function setParent(row, id) {
        var input = parentInput(row);
        if (input) { input.value = String(id || 0); }
        row.dataset.parentId = String(id || 0);
    }
    function rowById(list, id) { return rows(list).find(function (row) { return itemId(row) === id; }) || null; }
    function isDescendant(list, candidateId, ancestorId) {
        var cursor = candidateId, seen = {};
        while (cursor && !seen[cursor]) {
            if (cursor === ancestorId) { return true; }
            seen[cursor] = true;
            var row = rowById(list, cursor);
            cursor = row ? parentId(row) : 0;
        }
        return false;
    }
    function depth(list, row) {
        var d = 0, cursor = parentId(row), seen = {};
        while (cursor && !seen[cursor] && d < 6) {
            seen[cursor] = true;
            var parent = rowById(list, cursor);
            if (!parent) { break; }
            d += 1;
            cursor = parentId(parent);
        }
        return d;
    }
    function renumber(list) {
        rows(list).forEach(function (row, index) {
            var input = q('.h18-menu-order-input', row);
            if (input) { input.value = String(index + 1); }
            row.style.setProperty('--vd-menu-depth', String(depth(list, row)));
        });
        updatePreview(list);
    }
    function titleFor(row) {
        var input = q('.h18-menu-title-input', row);
        var preview = q('.h18-menu-item-title-preview', row);
        return (input && input.value || preview && preview.textContent || '').trim();
    }
    function buildTree(list) {
        var all = rows(list), map = {}, roots = [];
        all.forEach(function (row) { map[itemId(row)] = { row: row, children: [] }; });
        all.forEach(function (row) {
            var id = itemId(row), parent = parentId(row), node = map[id];
            if (parent && map[parent] && parent !== id) { map[parent].children.push(node); }
            else { roots.push(node); }
        });
        return roots;
    }
    function renderTree(nodes, mobile) {
        var ul = document.createElement('ul');
        ul.className = mobile ? 'h18-menu-preview-tree is-mobile' : 'h18-menu-preview-tree';
        nodes.forEach(function (node) {
            var li = document.createElement('li');
            var label = document.createElement('span');
            label.textContent = titleFor(node.row) || 'Uden navn';
            li.appendChild(label);
            if (node.children.length) { li.appendChild(renderTree(node.children, mobile)); }
            ul.appendChild(li);
        });
        return ul;
    }
    function updatePreview(list) {
        var tree = buildTree(list);
        var desktop = document.getElementById('h18-menu-preview-desktop');
        var mobile = document.getElementById('h18-menu-preview-mobile');
        if (desktop) { desktop.replaceChildren(renderTree(tree, false)); }
        if (mobile) { mobile.replaceChildren(renderTree(tree, true)); }
    }
    function moveRow(list, row, direction) {
        if (direction === 'up' && row.previousElementSibling) { list.insertBefore(row, row.previousElementSibling); }
        if (direction === 'down' && row.nextElementSibling) { list.insertBefore(row.nextElementSibling, row); }
        renumber(list);
    }
    function indentRow(list, row) {
        var previous = row.previousElementSibling;
        if (!previous) { return; }
        var newParent = itemId(previous);
        if (!newParent || isDescendant(list, newParent, itemId(row))) { return; }
        setParent(row, newParent);
        renumber(list);
    }
    function outdentRow(list, row) {
        var currentParent = parentId(row);
        if (!currentParent) { return; }
        var parentRow = rowById(list, currentParent);
        setParent(row, parentRow ? parentId(parentRow) : 0);
        renumber(list);
    }
    function installDialog() {
        var dialog = document.getElementById('h18-menu-add-dialog');
        if (!dialog) { return; }
        var lastFocus = null;
        function open() {
            lastFocus = document.activeElement;
            dialog.hidden = false;
            document.body.classList.add('h18-menu-dialog-open');
            var focus = q('input:not([disabled]),button:not([disabled])', dialog);
            if (focus) { setTimeout(function () { focus.focus(); }, 0); }
        }
        function close() {
            dialog.hidden = true;
            document.body.classList.remove('h18-menu-dialog-open');
            if (lastFocus && lastFocus.focus) { lastFocus.focus(); }
        }
        qa('[data-menu-add-open]').forEach(function (button) { button.addEventListener('click', open); });
        qa('[data-menu-add-close]', dialog).forEach(function (button) { button.addEventListener('click', close); });
        qa('[data-menu-add-tab]', dialog).forEach(function (button) {
            button.addEventListener('click', function () {
                var key = button.getAttribute('data-menu-add-tab');
                qa('[data-menu-add-tab]', dialog).forEach(function (b) { b.classList.toggle('button-primary', b === button); });
                qa('[data-menu-add-panel]', dialog).forEach(function (panel) { panel.hidden = panel.getAttribute('data-menu-add-panel') !== key; });
            });
        });
        document.addEventListener('keydown', function (event) { if (!dialog.hidden && event.key === 'Escape') { close(); } });
    }
    function install() {
        var list = document.getElementById('h18-menu-sort-list');
        installDialog();
        if (!list) { return; }
        var dragging = null;
        rows(list).forEach(function (row) {
            row.addEventListener('dragstart', function (event) {
                var handle = event.target && event.target.closest ? event.target.closest('.h18-menu-drag-handle') : null;
                if (!handle) { event.preventDefault(); return; }
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
            var wantsChild = event.clientX > rect.left + Math.min(150, rect.width * 0.28);
            if (wantsChild && !isDescendant(list, itemId(target), itemId(dragging))) { setParent(dragging, itemId(target)); }
            else { setParent(dragging, parentId(target)); }
            renumber(list);
        });
        list.addEventListener('click', function (event) {
            var row = event.target && event.target.closest ? event.target.closest('.h18-menu-sort-row') : null;
            if (!row) { return; }
            var move = event.target.closest('[data-menu-move]');
            if (move) { moveRow(list, row, move.getAttribute('data-menu-move')); return; }
            if (event.target.closest('[data-menu-indent]')) { indentRow(list, row); return; }
            if (event.target.closest('[data-menu-outdent]')) { outdentRow(list, row); return; }
            var edit = event.target.closest('[data-menu-edit]');
            if (edit) {
                var editor = q('.h18-menu-item-editor', row);
                var open = editor && editor.hidden;
                if (editor) { editor.hidden = !open; }
                edit.setAttribute('aria-expanded', open ? 'true' : 'false');
                edit.textContent = open ? 'Luk' : 'Redigér';
            }
        });
        list.addEventListener('input', function (event) {
            if (!event.target.classList.contains('h18-menu-title-input')) { return; }
            var row = event.target.closest('.h18-menu-sort-row');
            var title = row && q('.h18-menu-item-title-preview', row);
            if (title) { title.textContent = event.target.value || 'Uden navn'; }
            updatePreview(list);
        });
        renumber(list);
    }
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
'''
JS.write_text(js + '\n', encoding='utf-8')

css = r'''/* Visual Designer Manager 0.1.56 · visual Menu UX */
.h18-menu-visual-admin{max-width:1480px}
.h18-menu-kicker{display:block;margin-bottom:4px;text-transform:uppercase;letter-spacing:.08em;font-size:11px;font-weight:700;color:#646970}
.h18-menu-picker{display:flex;align-items:center;justify-content:space-between;gap:20px}.h18-menu-picker h2{margin:0}.h18-menu-picker select{min-width:240px}
.h18-menu-editor-shell{padding:22px!important}.h18-menu-editor-head{display:flex;align-items:flex-start;justify-content:space-between;gap:24px;margin-bottom:20px}.h18-menu-editor-head h2{margin:0 0 6px}.h18-menu-editor-head p{max-width:760px;margin:0;color:#50575e}.h18-menu-primary-actions{display:flex;gap:8px;flex-wrap:wrap}
.h18-menu-workspace{display:grid;grid-template-columns:minmax(520px,1fr) minmax(300px,420px);gap:24px;align-items:start}
.h18-menu-visual-list{list-style:none;margin:0;padding:0}.h18-menu-sort-row{--vd-menu-depth:0;margin:0 0 9px calc(var(--vd-menu-depth) * 30px);border:1px solid #c3c4c7;border-radius:8px;background:#fff;box-shadow:0 1px 2px rgba(0,0,0,.04);transition:margin .15s ease,box-shadow .12s ease,opacity .12s ease}.h18-menu-sort-row.is-dragging{opacity:.5;box-shadow:0 0 0 2px #2271b1}.h18-menu-sort-row[style*="--vd-menu-depth:1"],.h18-menu-sort-row[style*="--vd-menu-depth:2"],.h18-menu-sort-row[style*="--vd-menu-depth:3"]{border-left:4px solid #c8a96b}
.h18-menu-item-main{display:flex;align-items:center;gap:10px;padding:11px 12px}.h18-menu-drag-handle{display:inline-flex;align-items:center;justify-content:center;width:34px;height:34px;flex:0 0 34px;border:1px solid #c3c4c7;border-radius:5px;background:#f6f7f7;cursor:grab;font-size:19px}.h18-menu-drag-handle:active{cursor:grabbing}.h18-menu-item-copy{min-width:0;flex:1;display:flex;flex-direction:column;gap:4px}.h18-menu-item-title-preview{font-size:14px}.h18-menu-item-copy>span{display:flex;align-items:center;gap:7px;min-width:0}.h18-menu-type-badge{display:inline-block;padding:2px 6px;border-radius:999px;background:#f0f0f1;font-size:11px;font-weight:600}.h18-menu-destination{overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#646970}.h18-menu-item-buttons{display:flex;gap:4px;align-items:center;flex-wrap:wrap;justify-content:flex-end}.h18-menu-item-editor{padding:12px 16px 15px 56px;border-top:1px solid #e2e4e7;background:#f9f9f9}.h18-menu-item-editor label{display:flex;flex-direction:column;gap:5px}.h18-menu-item-editor input.regular-text{width:min(100%,520px)}.h18-menu-remove{color:#b32d2e!important;border-color:#d63638!important}
.h18-menu-form-footer{display:flex;align-items:center;gap:10px;margin-top:14px}.h18-menu-empty-list{padding:28px;border:2px dashed #c3c4c7;border-radius:8px;text-align:center;background:#f6f7f7}.h18-menu-empty-list p{margin:5px 0 14px}
.h18-menu-preview-panel{position:sticky;top:42px;padding:18px;border:1px solid #dcdcde;border-radius:8px;background:#f6f7f7}.h18-menu-preview-panel h3{margin-top:0}.h18-menu-preview-device{margin-top:16px;padding:12px;border:1px solid #dcdcde;border-radius:7px;background:#fff}.h18-menu-preview-tree{display:flex;gap:16px;align-items:flex-start;list-style:none;margin:10px 0 0;padding:0}.h18-menu-preview-tree li{position:relative;margin:0;padding:0;font-weight:600}.h18-menu-preview-tree li>ul{display:none;position:absolute;z-index:2;top:100%;left:0;min-width:160px;padding:8px;margin:4px 0 0;background:#fff;border:1px solid #dcdcde;border-radius:5px;box-shadow:0 4px 12px rgba(0,0,0,.08)}.h18-menu-preview-tree li:hover>ul{display:block}.h18-menu-preview-tree li>ul li{margin:5px 0}.h18-menu-mobile-bar{display:flex;justify-content:space-between;align-items:center;margin-top:8px;padding:8px 10px;border-radius:5px;background:#30382a;color:#fff;font-weight:700}.h18-menu-preview-tree.is-mobile{display:block;margin-top:7px}.h18-menu-preview-tree.is-mobile li{padding:5px 7px;border-bottom:1px solid #eee}.h18-menu-preview-tree.is-mobile li>ul{display:block;position:static;box-shadow:none;border:0;border-left:2px solid #c8a96b;border-radius:0;margin:5px 0 0 8px;padding:0 0 0 8px;background:transparent}
.h18-menu-dialog-open{overflow:hidden}.h18-menu-dialog{position:fixed;z-index:100100;inset:0;display:flex;align-items:center;justify-content:center;padding:24px}.h18-menu-dialog[hidden]{display:none!important}.h18-menu-dialog-backdrop{position:absolute;inset:0;background:rgba(0,0,0,.48)}.h18-menu-dialog-card{position:relative;width:min(760px,100%);max-height:min(780px,90vh);overflow:auto;padding:22px;border-radius:10px;background:#fff;box-shadow:0 18px 60px rgba(0,0,0,.3)}.h18-menu-dialog-head{display:flex;justify-content:space-between;align-items:flex-start;gap:20px}.h18-menu-dialog-head h2{margin:0}.h18-menu-add-tabs{display:flex;gap:6px;margin:18px 0}.h18-menu-add-panel label{display:flex;flex-direction:column;gap:5px;margin:12px 0}.h18-menu-page-picker{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin:14px 0;max-height:400px;overflow:auto}.h18-menu-page-choice{display:grid!important;grid-template-columns:auto 1fr auto;align-items:center;gap:10px;margin:0!important;padding:10px;border:1px solid #dcdcde;border-radius:7px;background:#fff}.h18-menu-page-choice span{display:flex;flex-direction:column;gap:2px}.h18-menu-page-choice small{color:#646970}.h18-menu-page-choice em{font-size:11px;color:#646970}.h18-menu-page-choice.is-used{opacity:.6;background:#f6f7f7}
.h18-menu-advanced{padding:0!important}.h18-menu-advanced>summary{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:17px 20px;cursor:pointer}.h18-menu-advanced>summary span{color:#646970;font-weight:400}.h18-menu-advanced-body{padding:0 20px 20px;border-top:1px solid #dcdcde}.h18-menu-advanced-body>.h18-manager-card{box-shadow:none}
@media(max-width:1100px){.h18-menu-workspace{grid-template-columns:1fr}.h18-menu-preview-panel{position:static}.h18-menu-editor-head{flex-direction:column}.h18-menu-primary-actions{width:100%}}
@media(max-width:782px){.h18-menu-picker{align-items:flex-start;flex-direction:column}.h18-menu-workspace{display:block}.h18-menu-item-main{align-items:flex-start;flex-wrap:wrap}.h18-menu-item-copy{min-width:180px}.h18-menu-item-buttons{width:100%;justify-content:flex-start;padding-left:44px}.h18-menu-sort-row{margin-left:min(calc(var(--vd-menu-depth) * 18px),54px)}.h18-menu-item-editor{padding-left:14px}.h18-menu-page-picker{grid-template-columns:1fr}.h18-menu-dialog{padding:10px}.h18-menu-form-footer{align-items:flex-start;flex-direction:column}}
'''
CSS.write_text(css + '\n', encoding='utf-8')

plugin = PLUGIN.read_text(encoding='utf-8')
plugin = plugin.replace('Version: 0.1.55', 'Version: 0.1.56', 1)
plugin = plugin.replace("H18_CLEAN_VERSION', '0.1.55'", "H18_CLEAN_VERSION', '0.1.56'", 1)
PLUGIN.write_text(plugin, encoding='utf-8')

contract = r'''

## 0.1.56 – Forenklet visuel Menu-administration

### VD-MENU-UX-003
- Manager → Menu viser som standard den valgte menus faktiske menupunkter; WordPress-tekniske felter, theme-locations, flere menuer og historik ligger under **Avancerede indstillinger**.
- Menupunkter kan flyttes visuelt med drag-and-drop samt tastaturvenlige op/ned-knapper. `↳` gør et punkt til undermenu under forrige punkt, og `←` flytter ét niveau ud. Backend validerer fortsat parent-grafen mod cycles og ugyldige parents.
- **+ Tilføj menupunkt** åbner en dialog med tre enkle valg: publicerede WordPress-sider, eksternt link eller overskrift/gruppe. Kladder vises ikke som valgbare sider, og en side der allerede er i menuen kan ikke tilføjes igen via standarddialogen.
- Menutekst kan ændres uden at ændre WordPress-sidens titel. **Fjern fra menu** sletter kun `nav_menu_item`; destinationssiden slettes aldrig.
- Struktur-preview opdateres i browseren ved ændret rækkefølge, nesting eller menutekst. Preview viser kun informationsarkitektur; typografi/farver/layout styres fortsat af Visual Designer Menu-elementet.
- WordPress `nav_menu` / `nav_menu_item` er fortsat den eneste canonical datakilde. Versionssnapshots og restore-kontrakten fra VD-MENU-UX-002 bevares.
'''
tech = TECH.read_text(encoding='utf-8')
if 'VD-MENU-UX-003' not in tech:
    TECH.write_text(tech.rstrip() + contract + '\n', encoding='utf-8')

notes = NOTES.read_text(encoding='utf-8')
new_notes = '<h4>0.1.56 – Forenklet visuel Menu</h4><ul><li><strong>VD-MENU-UX-003:</strong> Menuadministrationen viser nu menupunkterne som en visuel, trækbar liste i stedet for en teknisk WordPress-tabel.</li><li><strong>+ Tilføj menupunkt</strong> giver et enkelt valg mellem publicerede sider, eksternt link og overskrift/gruppe; kladder og dubletter filtreres fra standardflowet.</li><li>Undermenuer kan laves med ↳ / ← og drag-and-drop; menutekst redigeres direkte, og Fjern fra menu sletter aldrig destinationssiden.</li><li>Desktop/Mobil struktur-preview opdateres live, mens theme-locations, flere menuer og versionshistorik er flyttet under Avancerede indstillinger.</li></ul>\n'
if not notes.startswith('<h4>0.1.56'):
    NOTES.write_text(new_notes + notes, encoding='utf-8')

history = json.loads(HISTORY.read_text(encoding='utf-8'))
versions = history.get('versions', [])
if not versions or versions[0].get('version') != '0.1.56':
    versions.insert(0, {
        'version': '0.1.56',
        'date': '2026-08-30',
        'items': [
            'VD-MENU-UX-003: Manager → Menu viser en visuel drag-and-drop liste som standard og gemmer WordPress-tekniske indstillinger under Avanceret.',
            '+ Tilføj menupunkt viser publicerede sider, eksternt link og overskrift/gruppe i en enkel dialog; kladder og allerede valgte sider filtreres.',
            'Menutekst kan redigeres direkte; Fjern fra menu sletter kun menupunktet og aldrig destinationssiden.',
            'Undermenuer styres med ↳ / ← samt drag-and-drop, mens backend fortsat validerer parent-grafen.',
            'Desktop/Mobil struktur-preview opdateres live; farver og typografi ejes fortsat af Visual Designer Menu-elementet.'
        ]
    })
    history['versions'] = versions
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

STATUS.write_text('''# Visual Designer Manager 0.1.56 – status\n\n## Scope\n- VD-MENU-UX-003: forenklet visuel Menu-administration.\n- WordPress nav_menu/nav_menu_item forbliver canonical datakilde.\n- Eksisterende snapshots, restore og theme-location support bevares under Avanceret.\n\n## QA gates\n- PHP syntax for hele pluginet.\n- JavaScript syntax for alle assets.\n- HierarchyNormalizer + eksisterende LayoutModel QA.\n- Kontraktcheck for visual list, dialog, publicerede sider, nesting, preview og avanceret panel.\n- Regression-gates for rich-text selection, Fit og transparent leaf-paint.\n''', encoding='utf-8')

print('Applied Visual Designer Manager 0.1.56 visual Menu UX patch')
