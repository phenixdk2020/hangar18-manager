<?php

declare(strict_types=1);

namespace Hangar18\Clean\Admin;

use Hangar18\Clean\Diagnostics\DiagnosticStore;
use Hangar18\Clean\Model\LayoutModel;
use Hangar18\Clean\Update\GitHubUpdater;

final class AdminController
{
    public const MENU = 'h18-clean-manager';

    private const EXPORT_ACTION = 'h18_clean_export_backup';
    private const CLEAR_LOG_ACTION = 'h18_clean_clear_diagnostics';
    private const EXPORT_NONCE = 'h18_clean_export_backup';
    private const CLEAR_LOG_NONCE = 'h18_clean_clear_diagnostics';

    /** @var array<string,array{title:string,slug:string}> */
    private const COLLECTIONS = [
        'vehicles' => ['title' => 'Køretøjer', 'slug' => 'koeretoejer-og-materiel'],
        'events' => ['title' => 'Events', 'slug' => 'events'],
        'gallery' => ['title' => 'Billedgalleri', 'slug' => 'billedgalleri'],
    ];

    public static function register(): void
    {
        add_action('admin_menu', [self::class, 'menu'], 5);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        add_action('admin_post_' . self::EXPORT_ACTION, [self::class, 'exportBackup']);
        add_action('admin_post_' . self::CLEAR_LOG_ACTION, [self::class, 'clearDiagnostics']);
    }

    public static function menu(): void
    {
        $cap = 'edit_pages';
        add_menu_page(
            'Visual Designer Manager',
            'Visual Designer Manager',
            $cap,
            self::MENU,
            [self::class, 'dashboard'],
            'dashicons-admin-tools',
            3
        );

        add_submenu_page(self::MENU, 'Dashboard', 'Dashboard', $cap, self::MENU, [self::class, 'dashboard']);
        add_submenu_page(self::MENU, 'Køretøjer', 'Køretøjer', $cap, 'h18-clean-vehicles', [self::class, 'vehicles']);
        add_submenu_page(self::MENU, 'Køretøjsfelter', 'Køretøjsfelter', $cap, 'h18-clean-vehicle-fields', [self::class, 'vehicleFields']);
        add_submenu_page(self::MENU, 'Events', 'Events', $cap, 'h18-clean-events', [self::class, 'events']);
        add_submenu_page(self::MENU, 'Billedgalleri', 'Billedgalleri', $cap, 'h18-clean-gallery', [self::class, 'gallery']);
        add_submenu_page(self::MENU, 'Data', 'Data', $cap, 'h18-clean-data', [self::class, 'data']);
        add_submenu_page(self::MENU, 'Sider', 'Sider', $cap, 'h18-clean-pages', [self::class, 'pages']);
        add_submenu_page(self::MENU, 'Menu', 'Menu', $cap, 'h18-clean-menu', [self::class, 'menus']);
        add_submenu_page(self::MENU, 'Header / Footer og design', 'Header / Footer', $cap, 'h18-clean-header-footer', [self::class, 'headerFooter']);
        add_submenu_page(self::MENU, 'Backup', 'Backup', $cap, 'h18-clean-backup', [self::class, 'backup']);
        add_submenu_page(self::MENU, 'Opdateringer', 'Opdateringer', $cap, 'h18-clean-updates', [self::class, 'updates']);
        add_submenu_page(self::MENU, 'Log', 'Log', $cap, 'h18-clean-log', [self::class, 'log']);
    }

    public static function enqueue(string $hook): void
    {
        if (!current_user_can('edit_pages') || strpos($hook, 'h18-clean-') === false) {
            return;
        }
        wp_enqueue_style('h18-clean-manager-admin', H18_CLEAN_URL . 'assets/admin-v019.css', [], H18_CLEAN_VERSION);
    }

    public static function dashboard(): void
    {
        self::guard();
        $pages = self::allPages();
        $cleanPages = 0;
        $nodes = 0;
        $versions = 0;
        foreach ($pages as $page) {
            $version = (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true);
            if ($version > 0 || metadata_exists('post', $page->ID, LayoutModel::META)) {
                $cleanPages++;
                $nodes += count(LayoutModel::get($page->ID)['nodes']);
                $versions += count(LayoutModel::history($page->ID));
            }
        }

        self::open('Visual Designer Manager', 'Administration · v' . H18_CLEAN_VERSION);
        echo '<section class="h18-manager-hero"><div><span class="h18-manager-kicker">Visual Designer Manager v' . esc_html(H18_CLEAN_VERSION) . '</span>';
        echo '<h2>' . esc_html((string) get_bloginfo('name')) . '</h2>';
        echo '<p>Samlet administration af sider, designer, indholdsoversigter, navigation, backup, opdateringer og diagnostics. Visual Designer bruger den canonical layoutmodel.</p></div>';
        echo '<div class="h18-manager-hero-actions"><a class="button button-primary button-hero" href="' . esc_url(self::designerUrl()) . '">Åbn Designer</a><a class="button" href="' . esc_url(self::url('h18-clean-pages')) . '">Administrer sider</a></div></section>';

        echo '<div class="h18-manager-stats">';
        self::stat('WordPress-sider', count($pages), 'Alle registrerede sider');
        self::stat('Visual Designer-sider', $cleanPages, 'Sider med Visual Designer-layout');
        self::stat('Elementer', $nodes, 'Canonical nodes i alt');
        self::stat('Gemte versioner', $versions, 'Versionshistorik i alt');
        echo '</div>';

        echo '<div class="h18-manager-card-grid">';
        self::card('Designer', 'Byg sider med 120-unit / 8-px grid, Undo/Redo og versionshistorik.', self::designerUrl(), 'Åbn Designer');
        self::card('Sider', 'Se Visual Designer-status, nodeantal og seneste version for alle WordPress-sider.', self::url('h18-clean-pages'), 'Vis sider');
        self::card('Backup', 'Download én samlet JSON-backup af alle Visual Designer-layouts og deres versionshistorik.', self::url('h18-clean-backup'), 'Åbn Backup');
        self::card('Log / diagnostics', 'Læs de strukturelle Visual Designer-logs pr. side og kopiér diagnose-link.', self::url('h18-clean-log'), 'Åbn Log');
        self::card('Opdateringer', 'Brug den SHA-256-verificerede GitHub-opdateringskanal.', self::url('h18-clean-updates'), 'Tjek version');
        self::card('Menu', 'Se WordPress-navigation og aktive menulocations uden at ændre Visual Designer-layoutdata.', self::url('h18-clean-menu'), 'Vis menu');
        echo '</div>';
        self::close();
    }

    public static function vehicles(): void { self::renderCollection('vehicles'); }
    public static function events(): void { self::renderCollection('events'); }
    public static function gallery(): void { self::renderCollection('gallery'); }

    public static function vehicleFields(): void
    {
        self::guard();
        self::open('Køretøjsfelter', 'Adminpladsen svarer til den gamle Manager, men legacy-feltmotoren er ikke indlæst i Clean.');
        self::moduleNotice('Køretøjsfelter', 'Visual Designer Manager-administrationen er klar. Selve dynamiske køretøjsfelter porteres som et selvstændigt Visual Designer-datamodul, så vi ikke blander 0.9.x-runtime ind i den nye editor.');
        echo '<p><a class="button" href="' . esc_url(self::url('h18-clean-vehicles')) . '">← Køretøjer</a></p>';
        self::close();
    }

    public static function data(): void
    {
        self::guard();
        self::open('Data', 'WordPress-data og Visual Designer-modelstatus');
        $postTypes = get_post_types(['public' => true], 'objects');
        echo '<div class="h18-manager-card"><h2>Offentlige indholdstyper</h2><table class="widefat striped"><thead><tr><th>Type</th><th>Slug</th><th>Antal</th><th></th></tr></thead><tbody>';
        foreach ($postTypes as $type) {
            if (!$type instanceof \WP_Post_Type) { continue; }
            $counts = wp_count_posts($type->name);
            $published = is_object($counts) ? (int) ($counts->publish ?? 0) : 0;
            echo '<tr><td><strong>' . esc_html((string) $type->labels->name) . '</strong></td><td><code>' . esc_html($type->name) . '</code></td><td>' . esc_html((string) $published) . '</td><td>';
            if (current_user_can($type->cap->edit_posts)) {
                $href = $type->name === 'post' ? admin_url('edit.php') : admin_url('edit.php?post_type=' . $type->name);
                echo '<a class="button" href="' . esc_url($href) . '">Åbn</a>';
            }
            echo '</td></tr>';
        }
        echo '</tbody></table></div>';
        self::moduleNotice('Visual Designer Data-modul', 'Den gamle Managers custom data types bliver ikke automatisk aktiveret. Denne side er administrationsindgangen til den kommende modeldrevne Clean-datafunktion.');
        self::close();
    }

    public static function pages(): void
    {
        self::guard();
        $pages = self::allPages();
        self::open('Sider', 'Alle WordPress-sider med Visual Designer-status');
        echo '<div class="h18-manager-toolbar"><a class="button button-primary" href="' . esc_url(admin_url('post-new.php?post_type=page')) . '">+ Ny WordPress-side</a><a class="button" href="' . esc_url(self::designerUrl()) . '">Åbn Designer</a></div>';
        echo '<table class="widefat striped h18-manager-table"><thead><tr><th>Side</th><th>Slug</th><th>Status</th><th>Nodes</th><th>Senest gemt</th><th>Handlinger</th></tr></thead><tbody>';
        foreach ($pages as $page) {
            $version = (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true);
            $model = LayoutModel::get($page->ID);
            $history = LayoutModel::history($page->ID);
            $last = $history ? $history[count($history) - 1] : [];
            $status = $version > 0 ? '<span class="h18-manager-badge is-ok">Designer v' . esc_html((string) $version) . '</span>' : '<span class="h18-manager-badge">Ikke Visual Designer</span>';
            echo '<tr><td><strong>' . esc_html((string) $page->post_title) . '</strong><br><small>ID ' . esc_html((string) $page->ID) . '</small></td>';
            echo '<td><code>' . esc_html((string) $page->post_name) . '</code></td><td>' . $status . '</td><td>' . esc_html((string) count($model['nodes'])) . '</td><td>' . esc_html(self::prettyDate((string) ($last['savedUtc'] ?? ''))) . '</td><td class="h18-manager-actions">';
            echo '<a class="button button-primary" href="' . esc_url(self::designerUrl($page->ID)) . '">Designer</a>';
            echo '<a class="button" href="' . esc_url(get_edit_post_link($page->ID, 'raw') ?: '#') . '">WordPress</a>';
            $permalink = get_permalink($page->ID);
            if ($permalink) { echo '<a class="button" target="_blank" rel="noopener" href="' . esc_url($permalink) . '">Vis</a>'; }
            echo '</td></tr>';
        }
        echo '</tbody></table>';
        self::close();
    }

    public static function menus(): void
    {
        self::guard();
        self::open('Menu', 'WordPress-navigation og locations');
        $menus = wp_get_nav_menus();
        $locations = get_nav_menu_locations();
        $registered = get_registered_nav_menus();
        echo '<div class="h18-manager-toolbar"><a class="button button-primary" href="' . esc_url(admin_url('nav-menus.php')) . '">Åbn WordPress Menu-editor</a></div>';
        echo '<div class="h18-manager-two-col"><div class="h18-manager-card"><h2>Menuer</h2>';
        if (!$menus) { echo '<p>Ingen klassiske WordPress-menuer fundet.</p>'; }
        else {
            echo '<table class="widefat striped"><thead><tr><th>Navn</th><th>Elementer</th></tr></thead><tbody>';
            foreach ($menus as $menu) {
                $items = wp_get_nav_menu_items((int) $menu->term_id);
                echo '<tr><td><strong>' . esc_html((string) $menu->name) . '</strong></td><td>' . esc_html((string) count(is_array($items) ? $items : [])) . '</td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</div><div class="h18-manager-card"><h2>Menu-locations</h2>';
        if (!$registered) { echo '<p>Temaet registrerer ingen klassiske menu-locations.</p>'; }
        else {
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

    public static function headerFooter(): void
    {
        self::guard();
        $theme = wp_get_theme();
        self::open('Header / Footer', 'Tema og global shell');
        echo '<div class="h18-manager-two-col"><div class="h18-manager-card"><h2>Aktivt tema</h2><dl class="h18-manager-dl">';
        echo '<dt>Navn</dt><dd>' . esc_html($theme->get('Name')) . '</dd><dt>Version</dt><dd>' . esc_html($theme->get('Version')) . '</dd><dt>Stylesheet</dt><dd><code>' . esc_html($theme->get_stylesheet()) . '</code></dd></dl>';
        echo '<p><a class="button" href="' . esc_url(admin_url('themes.php')) . '">Temaer</a>';
        if (current_user_can('edit_theme_options')) { echo ' <a class="button" href="' . esc_url(admin_url('customize.php')) . '">Tilpas</a>'; }
        echo '</p></div>';
        echo '<div class="h18-manager-card"><h2>Visual Designer-princip</h2><p>Visual Designer styrer sideindholdets canonical layout. Header, footer og global navigation holdes adskilt fra side-layoutet, så en sideversion ikke utilsigtet ændrer hele sitet.</p><p class="description">Når den globale design-editor porteres, placeres den her frem for at genaktivere den gamle 0.9.x shell-runtime.</p></div></div>';
        self::close();
    }

    public static function backup(): void
    {
        self::guard();
        $clean = self::cleanPages();
        self::open('Backup', 'Eksport af Clean-layout og versionshistorik');
        echo '<div class="h18-manager-card"><h2>Fuld Visual Designer-backup</h2><p>Downloader én JSON-fil med alle sider, der har Clean-state, inklusive nuværende canonical model og gemt versionshistorik.</p>';
        echo '<p><strong>' . esc_html((string) count($clean)) . '</strong> Visual Designer-sider medtages.</p>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::EXPORT_NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::EXPORT_ACTION) . '"><button class="button button-primary" type="submit">Download fuld Visual Designer-backup</button></form></div>';
        echo '<div class="h18-manager-card"><h2>Hvad backupen indeholder</h2><ul class="h18-manager-list"><li>Side-ID, titel og slug</li><li>Aktuel Clean-version</li><li>Canonical layoutmodel</li><li>Versionshistorik med model og digest</li><li>Plugin/schema/grid-version</li></ul><p class="description">Diagnostics/logs, nonces, tokens og credentials eksporteres ikke.</p></div>';
        self::close();
    }

    public static function updates(): void
    {
        self::guard();
        $status = GitHubUpdater::status();
        self::open('Opdateringer', 'Tjek og installer Visual Designer Manager direkte herfra');
        echo '<div class="h18-manager-card"><h2>Version</h2><p class="h18-manager-big-version">' . esc_html(H18_CLEAN_VERSION) . '</p>';
        if ($status['ok']) {
            echo '<p>Seneste GitHub-version: <strong>' . esc_html($status['latest']) . '</strong></p>';
            echo $status['available'] ? '<p><span class="h18-manager-badge is-progress">Opdatering tilgængelig</span></p>' : '<p><span class="h18-manager-badge is-ok">Du er opdateret</span></p>';
        } else {
            echo '<p><span class="h18-manager-badge">Manifest kunne ikke læses</span></p>';
        }
        echo '<p>Downloadpakken SHA-256-verificeres før WordPress installerer den. Du behøver ikke åbne Plugins-siden.</p><div class="h18-manager-toolbar">';
        echo GitHubUpdater::checkButtonHtml();
        echo GitHubUpdater::installButtonHtml();
        echo '</div></div>';
        self::close();
    }

    public static function log(): void
    {
        self::guard();
        $pages = self::allPages();
        $postId = isset($_GET['post']) ? absint($_GET['post']) : 0;
        if ($postId <= 0 && $pages) {
            foreach ($pages as $candidate) {
                if (metadata_exists('post', $candidate->ID, LayoutModel::META)) { $postId = $candidate->ID; break; }
            }
        }
        self::open('Log', 'Clean diagnostics pr. side');
        echo '<form method="get" class="h18-manager-toolbar"><input type="hidden" name="page" value="h18-clean-log"><label for="h18-log-post"><strong>Side:</strong></label><select id="h18-log-post" name="post">';
        foreach ($pages as $page) {
            echo '<option value="' . esc_attr((string) $page->ID) . '"' . selected($postId, $page->ID, false) . '>' . esc_html((string) $page->post_title) . ' · ' . esc_html((string) $page->post_name) . '</option>';
        }
        echo '</select><button class="button" type="submit">Vis log</button></form>';

        if ($postId > 0 && get_post_type($postId) === 'page') {
            $entries = array_reverse(DiagnosticStore::entries($postId));
            echo '<div class="h18-manager-toolbar"><a class="button" target="_blank" rel="noopener" href="' . esc_url(DiagnosticStore::supportUrl($postId)) . '">Åbn diagnose-link</a>';
            if ($entries) {
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
                wp_nonce_field(self::CLEAR_LOG_NONCE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::CLEAR_LOG_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $postId) . '"><button class="button" type="submit" onclick="return confirm(\'Ryd diagnostics for denne side?\');">Ryd log</button></form>';
            }
            echo '</div>';
            echo '<div class="h18-manager-card"><h2>Seneste diagnostics</h2>';
            if (!$entries) { echo '<p>Ingen diagnostics på den valgte side.</p>'; }
            else {
                echo '<table class="widefat striped h18-manager-log"><thead><tr><th>Tid</th><th>Type</th><th>Bruger</th><th>Detaljer</th></tr></thead><tbody>';
                foreach (array_slice($entries, 0, 150) as $entry) {
                    $detail = wp_json_encode($entry['detail'] ?? [], JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
                    echo '<tr><td>' . esc_html(self::prettyDate((string) ($entry['time'] ?? ''))) . '</td><td><code>' . esc_html((string) ($entry['type'] ?? '')) . '</code></td><td>' . esc_html((string) ((int) ($entry['userId'] ?? 0))) . '</td><td><code class="h18-manager-json">' . esc_html((string) $detail) . '</code></td></tr>';
                }
                echo '</tbody></table>';
            }
            echo '</div>';
        }
        self::close();
    }

    public static function exportBackup(): void
    {
        self::guard();
        check_admin_referer(self::EXPORT_NONCE);
        $payload = [
            'product' => 'Visual Designer Manager backup',
            'pluginVersion' => H18_CLEAN_VERSION,
            'schemaVersion' => LayoutModel::SCHEMA,
            'units' => LayoutModel::UNITS,
            'rowPx' => LayoutModel::ROW_PX,
            'generatedUtc' => gmdate('c'),
            'pages' => [],
        ];
        foreach (self::cleanPages() as $page) {
            $payload['pages'][] = [
                'postId' => $page->ID,
                'title' => (string) $page->post_title,
                'slug' => (string) $page->post_name,
                'version' => (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true),
                'model' => LayoutModel::get($page->ID),
                'history' => LayoutModel::history($page->ID),
            ];
        }
        $json = wp_json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($json)) { wp_die('Backup kunne ikke serialiseres.'); }
        nocache_headers();
        header('Content-Type: application/json; charset=utf-8');
        header('Content-Disposition: attachment; filename="hangar18-clean-backup-' . gmdate('Ymd-His') . '.json"');
        header('Content-Length: ' . strlen($json));
        echo $json;
        exit;
    }

    public static function clearDiagnostics(): void
    {
        self::guard();
        check_admin_referer(self::CLEAR_LOG_NONCE);
        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId > 0 && get_post_type($postId) === 'page') {
            DiagnosticStore::clear($postId);
        }
        wp_safe_redirect(self::url('h18-clean-log', ['post' => $postId]));
        exit;
    }

    private static function renderCollection(string $key): void
    {
        self::guard();
        $cfg = self::COLLECTIONS[$key] ?? null;
        if (!$cfg) { return; }
        $parent = get_page_by_path($cfg['slug'], OBJECT, 'page');
        self::open($cfg['title'], 'Indholdsoversigt med direkte adgang til WordPress og Clean Designer');
        echo '<div class="h18-manager-toolbar"><a class="button button-primary" href="' . esc_url(admin_url('post-new.php?post_type=page')) . '">+ Ny side</a>';
        if ($parent instanceof \WP_Post) { echo '<a class="button" href="' . esc_url(self::designerUrl($parent->ID)) . '">Designer: ' . esc_html((string) $parent->post_title) . '</a>'; }
        echo '</div>';
        if (!$parent instanceof \WP_Post) {
            self::moduleNotice($cfg['title'], 'Hovedsiden /' . $cfg['slug'] . '/ blev ikke fundet. Opret eller vælg siden under Sider.');
            self::close();
            return;
        }
        $children = get_pages(['parent' => $parent->ID, 'sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC']);
        echo '<div class="h18-manager-card"><h2>' . esc_html((string) $parent->post_title) . '</h2><p><code>/' . esc_html((string) $parent->post_name) . '/</code> · ' . esc_html((string) count($children)) . ' undersider</p>';
        echo '<table class="widefat striped"><thead><tr><th>Side</th><th>Clean</th><th>Nodes</th><th>Handlinger</th></tr></thead><tbody>';
        if (!$children) { echo '<tr><td colspan="4">Ingen undersider fundet.</td></tr>'; }
        foreach ($children as $child) {
            if (!$child instanceof \WP_Post) { continue; }
            $version = (int) get_post_meta($child->ID, LayoutModel::VERSION_META, true);
            echo '<tr><td><strong>' . esc_html((string) $child->post_title) . '</strong><br><code>' . esc_html((string) $child->post_name) . '</code></td><td>' . esc_html($version > 0 ? 'v' . $version : 'Ikke Visual Designer') . '</td><td>' . esc_html((string) count(LayoutModel::get($child->ID)['nodes'])) . '</td><td class="h18-manager-actions"><a class="button button-primary" href="' . esc_url(self::designerUrl($child->ID)) . '">Designer</a><a class="button" href="' . esc_url(get_edit_post_link($child->ID, 'raw') ?: '#') . '">WordPress</a></td></tr>';
        }
        echo '</tbody></table></div>';
        self::close();
    }

    /** @return array<int,\WP_Post> */
    private static function allPages(): array
    {
        return array_values(array_filter(get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC']), static fn($page): bool => $page instanceof \WP_Post));
    }

    /** @return array<int,\WP_Post> */
    private static function cleanPages(): array
    {
        return array_values(array_filter(self::allPages(), static function (\WP_Post $page): bool {
            return metadata_exists('post', $page->ID, LayoutModel::META) || (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true) > 0;
        }));
    }

    private static function guard(): void
    {
        if (!current_user_can('edit_pages')) {
            wp_die(esc_html__('Ingen adgang.', 'hangar18-manager-clean'));
        }
    }

    private static function open(string $title, string $description): void
    {
        echo '<div class="wrap h18-manager-admin"><h1>' . esc_html($title) . '</h1><p class="description h18-manager-description">' . esc_html($description) . '</p>';
    }

    private static function close(): void { echo '</div>'; }

    private static function stat(string $label, int $value, string $text): void
    {
        echo '<div class="h18-manager-stat"><span>' . esc_html($label) . '</span><strong>' . esc_html((string) $value) . '</strong><small>' . esc_html($text) . '</small></div>';
    }

    private static function card(string $title, string $text, string $url, string $button): void
    {
        echo '<div class="h18-manager-card"><h2>' . esc_html($title) . '</h2><p>' . esc_html($text) . '</p><p><a class="button" href="' . esc_url($url) . '">' . esc_html($button) . '</a></p></div>';
    }

    private static function moduleNotice(string $title, string $text): void
    {
        echo '<div class="h18-manager-card h18-manager-module"><h2>' . esc_html($title) . '</h2><p>' . esc_html($text) . '</p><span class="h18-manager-badge is-progress">Clean admin klar</span></div>';
    }

    private static function url(string $page, array $args = []): string
    {
        return add_query_arg(array_merge(['page' => $page], $args), admin_url('admin.php'));
    }

    private static function designerUrl(int $postId = 0): string
    {
        return self::url('h18-clean-editor', $postId > 0 ? ['post' => $postId] : []);
    }

    private static function prettyDate(string $utc): string
    {
        if ($utc === '') { return '—'; }
        $time = strtotime($utc);
        if ($time === false) { return $utc; }
        return wp_date('Y-m-d H:i:s', $time);
    }
}
