<?php

declare(strict_types=1);

namespace VisualDesignerManager\Admin;

use VisualDesignerManager\Diagnostics\DiagnosticStore;
use VisualDesignerManager\Frontend\ThemeShell;
use VisualDesignerManager\Model\LayoutModel;
use VisualDesignerManager\Model\TemplateLayoutModel;
use VisualDesignerManager\Update\GitHubUpdater;

final class AdminController
{
    public const MENU = 'h18-clean-manager';

    private const EXPORT_ACTION = 'h18_clean_export_backup';
    private const CLEAR_LOG_ACTION = 'h18_clean_clear_diagnostics';
    private const CREATE_PAGE_ACTION = 'h18_clean_create_page';
    private const DUPLICATE_PAGE_ACTION = 'h18_clean_duplicate_page';
    private const SET_HOME_PAGE_ACTION = 'h18_clean_set_home_page';
    private const PAGE_STATUS_ACTION = 'h18_clean_page_status';
    private const TRASH_PAGE_ACTION = 'h18_clean_trash_page';
    private const EXPORT_NONCE = 'h18_clean_export_backup';
    private const CLEAR_LOG_NONCE = 'h18_clean_clear_diagnostics';
    private const CREATE_PAGE_NONCE = 'h18_clean_create_page';
    private const DUPLICATE_PAGE_NONCE = 'h18_clean_duplicate_page';
    private const SET_HOME_PAGE_NONCE = 'h18_clean_set_home_page';
    private const PAGE_STATUS_NONCE = 'h18_clean_page_status';
    private const TRASH_PAGE_NONCE = 'h18_clean_trash_page';
    private const BLANK_SLUG_REPAIR_OPTION = 'h18_vd_blank_page_slugs_repaired_v0141';
    private const LANDING_PAGE_OPTION = 'h18_vd_landing_page_v0147';
    private const LANDING_PAGE_META = '_h18_vd_landing_page_v0147';

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
        add_action('admin_post_' . self::CREATE_PAGE_ACTION, [self::class, 'createPage']);
        add_action('admin_post_' . self::DUPLICATE_PAGE_ACTION, [self::class, 'duplicatePage']);
        add_action('admin_post_' . self::SET_HOME_PAGE_ACTION, [self::class, 'setHomePage']);
        add_action('admin_post_' . self::PAGE_STATUS_ACTION, [self::class, 'updatePageStatus']);
        add_action('admin_post_' . self::TRASH_PAGE_ACTION, [self::class, 'trashPage']);
        add_action('admin_init', [self::class, 'repairBlankPageSlugs'], 20);
        add_action('admin_init', [self::class, 'ensureLandingPage'], 25);
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
        add_submenu_page(self::MENU, 'Konvertering af sider', 'Konvertering', $cap, 'h18-clean-conversion', [ConversionController::class, 'render']);
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
        wp_enqueue_style('h18-clean-manager-v0123', H18_CLEAN_URL . 'assets/admin-v0123.css', ['h18-clean-manager-admin'], H18_CLEAN_VERSION);
        wp_enqueue_script('h18-clean-manager-v0123', H18_CLEAN_URL . 'assets/admin-v0123.js', [], H18_CLEAN_VERSION, true);
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
        self::card('Konvertering', 'Forbered eksisterende WordPress-sider som ikke-destruktive Visual Designer-kandidater, QA dem og aktivér én side ad gangen.', self::url('h18-clean-conversion'), 'Konvertér sider');
        self::card('Backup', 'Download én samlet JSON-backup af alle Visual Designer-layouts og deres versionshistorik.', self::url('h18-clean-backup'), 'Åbn Backup');
        self::card('Log / diagnostics', 'Læs de strukturelle Visual Designer-logs pr. side og kopiér diagnose-link.', self::url('h18-clean-log'), 'Åbn Log');
        self::card('Opdateringer', 'Brug den SHA-256-verificerede GitHub-opdateringskanal.', self::url('h18-clean-updates'), 'Tjek version');
        self::card('Menu', 'Redigér WordPress-menuens punkter og rækkefølge i en brugervenlig VDM-visning. Samme menu bruges direkte af Visual Designer.', self::url('h18-clean-menu'), 'Redigér Menu');
        echo '</div>';
        self::close();
    }

    public static function vehicles(): void { self::renderCollection('vehicles'); }
    public static function events(): void { self::renderCollection('events'); }
    public static function gallery(): void { self::renderCollection('gallery'); }

    public static function vehicleFields(): void
    {
        self::guard();
        self::open('Køretøjsfelter', 'Adminpladsen svarer til den gamle Manager, men legacy-feltmotoren er ikke indlæst i Visual Designer Manager.');
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
        self::moduleNotice('Visual Designer Data-modul', 'Den gamle Managers custom data types bliver ikke automatisk aktiveret. Denne side er administrationsindgangen til den kommende modeldrevne Visual Designer-datafunktion.');
        self::close();
    }

    public static function pages(): void
    {
        self::guard();
        $pages = self::allPages();
        $status = sanitize_key((string) ($_GET['vd_status'] ?? ''));
        $message = sanitize_text_field((string) wp_unslash($_GET['vd_message'] ?? ''));
        self::open('Sider', 'Alle WordPress-sider med Visual Designer-status');
        if ($message !== '') { echo '<div class="notice ' . ($status === 'error' ? 'notice-error' : 'notice-success') . ' is-dismissible"><p>' . esc_html($message) . '</p></div>'; }

        $frontId = get_option('show_on_front', 'posts') === 'page' ? absint(get_option('page_on_front', 0)) : 0;
        $frontPage = $frontId > 0 ? get_post($frontId) : null;
        echo '<div class="h18-manager-card"><h2>Hjemmeside</h2>';
        if ($frontPage instanceof \WP_Post && $frontPage->post_type === 'page') {
            echo '<p>WordPress-forsiden er <strong>' . esc_html((string) $frontPage->post_title) . '</strong> <span class="h18-manager-badge is-ok">Hjemmeside</span></p>';
            if (metadata_exists('post', $frontId, LayoutModel::META)) {
                echo '<p><a class="button button-primary" href="' . esc_url(self::designerUrl($frontId)) . '">Åbn hjemmesiden i Designer</a></p>';
            } else {
                echo '<p class="description">Den aktuelle forside er endnu ikke en Visual Designer-side. Vælg “Sæt som Hjem” på en Visual Designer-side nedenfor for at skifte sikkert.</p>';
            }
        } else {
            echo '<p>WordPress viser aktuelt de seneste indlæg. Vælg <strong>Sæt som Hjem</strong> på en Visual Designer-side nedenfor.</p>';
        }
        echo '</div>';

        $landingId = absint(get_option(self::LANDING_PAGE_OPTION, 0));
        if ($landingId > 0 && get_post_type($landingId) === 'page') {
            echo '<div class="h18-manager-card"><h2>Hjem – Visual Designer</h2><p>Den separate Visual Designer-landingsside er klar til Header + indhold + Footer. Når du vælger den som Hjem, publiceres den automatisk hvis nødvendigt.</p><div class="h18-manager-toolbar"><a class="button button-primary" href="' . esc_url(self::designerUrl($landingId)) . '">Åbn Hjem – Visual Designer</a>';
            if ($frontId === $landingId) {
                echo '<span class="h18-manager-badge is-ok">Aktiv hjemmeside</span>';
            } elseif (metadata_exists('post', $landingId, LayoutModel::META)) {
                $landingPost = get_post($landingId);
                if ($landingPost instanceof \WP_Post && (string) $landingPost->post_status === 'publish') {
                    echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
                    wp_nonce_field(self::SET_HOME_PAGE_NONCE);
                    echo '<input type="hidden" name="action" value="' . esc_attr(self::SET_HOME_PAGE_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $landingId) . '"><button class="button" type="submit">Sæt som Hjem</button></form>';
                } elseif ($landingPost instanceof \WP_Post && current_user_can('publish_pages')) {
                    echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
                    wp_nonce_field(self::PAGE_STATUS_NONCE);
                    echo '<input type="hidden" name="action" value="' . esc_attr(self::PAGE_STATUS_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $landingId) . '"><input type="hidden" name="page_status" value="publish"><button class="button" type="submit">Publicér</button></form>';
                    echo '<span class="description">Publicér først; vælg derefter siden som Hjem.</span>';
                }
            }
            echo '</div></div>';
        }
        echo '<div class="h18-manager-card h18-manager-create-page"><h2>Ny side</h2><p class="description">Opret siden direkte i Visual Designer Manager. Efter oprettelse åbnes den i Designer.</p>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-manager-page-create-form">';
        wp_nonce_field(self::CREATE_PAGE_NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::CREATE_PAGE_ACTION) . '">';
        echo '<label><strong>Titel</strong><input type="text" name="page_title" required placeholder="Ny side"></label>';
        echo '<label><strong>Slug</strong><input type="text" name="page_slug" placeholder="automatisk-fra-titel"></label>';
        echo '<label><strong>Overordnet side</strong><select name="page_parent"><option value="0">Ingen · topniveau</option>';
        foreach ($pages as $parentPage) { echo '<option value="' . esc_attr((string) $parentPage->ID) . '">' . esc_html((string) $parentPage->post_title) . '</option>'; }
        echo '</select></label>';
        echo '<label><strong>Status</strong><select name="page_status"><option value="draft">Kladde</option>' . (current_user_can('publish_pages') ? '<option value="publish">Publiceret</option>' : '') . '</select></label>';
        echo '<button class="button button-primary" type="submit">Opret og åbn Designer</button></form></div>';
        echo '<div class="h18-manager-toolbar"><a class="button" href="' . esc_url(admin_url('post-new.php?post_type=page')) . '">WordPress-editor</a><a class="button" href="' . esc_url(self::designerUrl()) . '">Åbn Designer</a></div>';
        echo '<table class="widefat striped h18-manager-table"><thead><tr><th>Side</th><th>Slug</th><th>Status</th><th>Nodes</th><th>Senest gemt</th><th>Handlinger</th></tr></thead><tbody>';
        foreach ($pages as $page) {
            $version = (int) get_post_meta($page->ID, LayoutModel::VERSION_META, true);
            $model = LayoutModel::get($page->ID);
            $history = LayoutModel::history($page->ID);
            $last = $history ? $history[count($history) - 1] : [];
            $designerStatus = $version > 0 ? '<span class="h18-manager-badge is-ok">Designer v' . esc_html((string) $version) . '</span>' : '<span class="h18-manager-badge">Ikke Visual Designer</span>';
            $wpStatusObject = get_post_status_object((string) $page->post_status);
            $wpStatusLabel = $wpStatusObject ? (string) $wpStatusObject->label : (string) $page->post_status;
            $homeBadge = $frontId === (int) $page->ID ? ' <span class="h18-manager-badge is-ok">Hjemmeside</span>' : '';
            echo '<tr><td><strong>' . esc_html((string) $page->post_title) . '</strong>' . $homeBadge . '<br><small>ID ' . esc_html((string) $page->ID) . '</small></td>';
            echo '<td><code>' . esc_html((string) $page->post_name) . '</code></td><td><strong>' . esc_html($wpStatusLabel) . '</strong><br>' . $designerStatus . '</td><td>' . esc_html((string) count($model['nodes'])) . '</td><td>' . esc_html(self::prettyDate((string) ($last['savedUtc'] ?? ''))) . '</td><td class="h18-manager-actions">';
            echo '<a class="button button-primary" href="' . esc_url(self::designerUrl($page->ID)) . '">Designer</a>';
            echo '<a class="button" href="' . esc_url(get_edit_post_link($page->ID, 'raw') ?: '#') . '">WordPress</a>';
            $permalink = get_permalink($page->ID);
            if ($permalink) { echo '<a class="button" target="_blank" rel="noopener" href="' . esc_url($permalink) . '">Vis</a>'; }
            $isFrontPage = $frontId === (int) $page->ID;
            $isPublished = (string) $page->post_status === 'publish';
            if (!$isPublished && current_user_can('publish_pages') && current_user_can('edit_post', $page->ID)) {
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">';
                wp_nonce_field(self::PAGE_STATUS_NONCE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::PAGE_STATUS_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $page->ID) . '"><input type="hidden" name="page_status" value="publish"><button class="button" type="submit">Publicér</button></form>';
            } elseif ($isPublished && !$isFrontPage && current_user_can('edit_post', $page->ID)) {
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">';
                wp_nonce_field(self::PAGE_STATUS_NONCE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::PAGE_STATUS_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $page->ID) . '"><input type="hidden" name="page_status" value="draft"><button class="button" type="submit" onclick="return confirm(\'Gør denne side til kladde? Den fjernes fra offentlig visning.\');">Gør til kladde</button></form>';
            }
            if (!$isFrontPage && $isPublished && metadata_exists('post', $page->ID, LayoutModel::META)) {
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">';
                wp_nonce_field(self::SET_HOME_PAGE_NONCE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::SET_HOME_PAGE_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $page->ID) . '"><button class="button" type="submit">Sæt som Hjem</button></form>';
            }
            if (current_user_can('edit_post', $page->ID)) {
                echo '<details class="h18-manager-copy-page"><summary class="button">Kopiér</summary>';
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" class="h18-manager-copy-page-form">';
                wp_nonce_field(self::DUPLICATE_PAGE_NONCE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::DUPLICATE_PAGE_ACTION) . '"><input type="hidden" name="source_post_id" value="' . esc_attr((string) $page->ID) . '">';
                echo '<label><span class="screen-reader-text">Nyt sidenavn</span><input type="text" name="new_page_title" required value="' . esc_attr((string) $page->post_title . ' – kopi') . '" aria-label="Nyt sidenavn"></label>';
                echo '<button class="button button-primary" type="submit">Kopiér side</button></form></details>';
            }
            if (!$isFrontPage && current_user_can('delete_post', $page->ID)) {
                $confirmTitle = esc_js((string) $page->post_title);
                echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '" style="display:inline">';
                wp_nonce_field(self::TRASH_PAGE_NONCE);
                echo '<input type="hidden" name="action" value="' . esc_attr(self::TRASH_PAGE_ACTION) . '"><input type="hidden" name="post_id" value="' . esc_attr((string) $page->ID) . '"><button class="button button-link-delete" type="submit" onclick="return confirm(\'Flyt “' . $confirmTitle . '” til papirkurven? Siden kan gendannes fra WordPress-papirkurven.\');">Slet</button></form>';
            } elseif ($isFrontPage) {
                echo '<span class="description" title="Vælg en anden hjemmeside før denne side kan afpubliceres eller slettes.">Hjemmesiden er beskyttet</span>';
            }
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
        TemplateLayoutModel::ensureMigrated();
        $headerId = TemplateLayoutModel::defaultId('header');
        $footerId = TemplateLayoutModel::defaultId('footer');
        $headerMeta = $headerId !== '' ? TemplateLayoutModel::meta($headerId) : null;
        $footerMeta = $footerId !== '' ? TemplateLayoutModel::meta($footerId) : null;

        self::open('Header / Footer', 'Tema og global shell');
        echo '<div class="h18-manager-two-col"><div class="h18-manager-card"><h2>Aktivt tema</h2><dl class="h18-manager-dl">';
        echo '<dt>Navn</dt><dd>' . esc_html($theme->get('Name')) . '</dd><dt>Version</dt><dd>' . esc_html($theme->get('Version')) . '</dd><dt>Stylesheet</dt><dd><code>' . esc_html($theme->get_stylesheet()) . '</code></dd></dl>';
        echo '<p><a class="button" href="' . esc_url(admin_url('themes.php')) . '">Temaer</a>';
        if (current_user_can('edit_theme_options')) { echo ' <a class="button" href="' . esc_url(admin_url('customize.php')) . '">Tilpas</a>'; }
        echo '</p></div>';

        echo '<div class="h18-manager-card"><h2>Shell integration</h2>';
        echo ThemeShell::enabled() ? '<p><span class="h18-manager-badge is-ok">Status: Aktiv</span></p>' : '<p><span class="h18-manager-badge">Status: Inaktiv</span></p>';
        echo '<p>På offentlige <strong>Visual Designer-sider</strong> renderer Manageren nu Header → sideindhold → Footer med den samme canonical renderer som Preview.</p>';
        echo '<dl class="h18-manager-dl"><dt>Standard Header</dt><dd>' . esc_html((string) ($headerMeta['name'] ?? 'Ingen aktiv')) . '</dd><dt>Standard Footer</dt><dd>' . esc_html((string) ($footerMeta['name'] ?? 'Ingen aktiv')) . '</dd></dl>';
        echo '<p class="description">Sider uden Visual Designer-model ændres ikke. Hvis en Header/Footer mangler eller er inaktiv, vises selve siden stadig uden den pågældende del.</p></div></div>';
        self::close();
    }

    public static function backup(): void
    {
        self::guard();
        $clean = self::cleanPages();
        self::open('Backup', 'Eksport af Visual Designer-layout og versionshistorik');
        echo '<div class="h18-manager-card"><h2>Fuld Visual Designer-backup</h2><p>Downloader én JSON-fil med alle sider, der har Visual Designer-data, inklusive nuværende canonical model og gemt versionshistorik.</p>';
        echo '<p><strong>' . esc_html((string) count($clean)) . '</strong> Visual Designer-sider medtages.</p>';
        echo '<form method="post" action="' . esc_url(admin_url('admin-post.php')) . '">';
        wp_nonce_field(self::EXPORT_NONCE);
        echo '<input type="hidden" name="action" value="' . esc_attr(self::EXPORT_ACTION) . '"><button class="button button-primary" type="submit">Download fuld Visual Designer-backup</button></form></div>';
        echo '<div class="h18-manager-card"><h2>Hvad backupen indeholder</h2><ul class="h18-manager-list"><li>Side-ID, titel og slug</li><li>Aktuel Designer-version</li><li>Canonical layoutmodel</li><li>Versionshistorik med model og digest</li><li>Plugin/schema/grid-version</li></ul><p class="description">Diagnostics/logs, nonces, tokens og credentials eksporteres ikke.</p></div>';
        self::close();
    }

    public static function updates(): void
    {
        self::guard();
        $status = GitHubUpdater::status();
        $backups = GitHubUpdater::programBackups();
        $versions = GitHubUpdater::releaseHistory();
        self::open('Opdateringer', 'Tjek, installer og se update-checkpoints for Visual Designer Manager');
        echo '<div class="h18-manager-card"><h2>Version</h2><p class="h18-manager-big-version">' . esc_html(H18_CLEAN_VERSION) . '</p>';
        if ($status['ok']) {
            echo '<p>Seneste GitHub-version: <strong>' . esc_html($status['latest']) . '</strong></p>';
            echo $status['available'] ? '<p><span class="h18-manager-badge is-progress">Opdatering tilgængelig</span></p>' : '<p><span class="h18-manager-badge is-ok">Du er opdateret</span></p>';
        } else {
            echo '<p><span class="h18-manager-badge">Manifest kunne ikke læses</span></p>';
        }
        echo '<p>Downloadpakken SHA-256-verificeres. Før installation gemmes både program-ZIP og et Designer-data-checkpoint; opdateringen stoppes hvis checkpointet fejler.</p><div class="h18-manager-toolbar">';
        echo GitHubUpdater::checkButtonHtml();
        echo GitHubUpdater::installButtonHtml();
        echo '</div></div>';

        echo '<div class="h18-manager-card"><h2>Update-checkpoints</h2><p>De seneste automatiske checkpoints før plugin-opdateringer. Der beholdes op til 12.</p>';
        if (!$backups) {
            echo '<p>Ingen lokale update-checkpoints er registreret endnu.</p>';
        } else {
            echo '<table class="widefat striped"><thead><tr><th>Fra</th><th>Til</th><th>Dato</th><th>Program</th><th>Designer-data</th></tr></thead><tbody>';
            foreach ($backups as $backup) {
                $created = (string) ($backup['createdUtc'] ?? '');
                $programSize = isset($backup['size']) ? size_format((int) $backup['size']) : '—';
                $dataSize = isset($backup['dataSize']) && (int) $backup['dataSize'] > 0 ? size_format((int) $backup['dataSize']) : '—';
                echo '<tr><td><strong>' . esc_html((string) ($backup['version'] ?? '—')) . '</strong></td><td>' . esc_html((string) ($backup['targetVersion'] ?? '—')) . '</td><td>' . esc_html(self::prettyDate($created)) . '</td>';
                echo '<td><code>' . esc_html((string) ($backup['file'] ?? '—')) . '</code><br><small>' . esc_html($programSize) . '</small></td>';
                echo '<td>';
                if (!empty($backup['dataFile'])) {
                    echo '<code>' . esc_html((string) $backup['dataFile']) . '</code><br><small>' . esc_html($dataSize) . '</small>';
                } else {
                    echo '<span class="description">Ældre checkpoint · kun program-ZIP</span>';
                }
                echo '</td></tr>';
            }
            echo '</tbody></table>';
        }
        echo '</div>';

        echo '<div class="h18-manager-card"><h2>Versionshistorik</h2><p>Hvad de enkelte Visual Designer Manager-versioner indeholder.</p>';
        if (!$versions) {
            echo '<p>Versionshistorikken kunne ikke læses.</p>';
        } else {
            foreach ($versions as $row) {
                $version = (string) ($row['version'] ?? '');
                $current = $version === H18_CLEAN_VERSION ? ' <span class="h18-manager-badge is-ok">Installeret</span>' : '';
                echo '<details' . ($version === H18_CLEAN_VERSION ? ' open' : '') . '><summary><strong>v' . esc_html($version) . '</strong>' . $current . ' <span class="description">' . esc_html((string) ($row['date'] ?? '')) . '</span></summary>';
                echo '<ul class="h18-manager-list">';
                foreach (is_array($row['items'] ?? null) ? $row['items'] : [] as $item) {
                    echo '<li>' . esc_html((string) $item) . '</li>';
                }
                echo '</ul></details>';
            }
        }
        echo '</div>';
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
        self::open('Log', 'Visual Designer-diagnostics pr. side');
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


    public static function createPage(): void
    {
        self::guard();
        check_admin_referer(self::CREATE_PAGE_NONCE);

        $title = sanitize_text_field((string) wp_unslash($_POST['page_title'] ?? ''));
        if ($title === '') {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Sidetitel mangler.']));
            exit;
        }

        $requestedSlug = sanitize_title((string) wp_unslash($_POST['page_slug'] ?? ''));
        $slugBase = $requestedSlug !== '' ? $requestedSlug : sanitize_title($title);
        $slug = self::uniquePageSlug($slugBase);
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


    public static function duplicatePage(): void
    {
        self::guard();
        check_admin_referer(self::DUPLICATE_PAGE_NONCE);

        $sourceId = absint($_POST['source_post_id'] ?? 0);
        $newTitle = sanitize_text_field((string) wp_unslash($_POST['new_page_title'] ?? ''));
        if ($sourceId <= 0 || get_post_type($sourceId) !== 'page' || !current_user_can('edit_post', $sourceId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Kildesiden er ikke gyldig eller du mangler rettighed.']));
            exit;
        }
        if ($newTitle === '') {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Nyt sidenavn mangler.']));
            exit;
        }

        $source = get_post($sourceId);
        if (!$source instanceof \WP_Post) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Kildesiden kunne ikke læses.']));
            exit;
        }

        $newSlug = self::uniquePageSlug(sanitize_title($newTitle));
        $newPostId = wp_insert_post([
            'post_type' => 'page',
            'post_title' => $newTitle,
            'post_name' => $newSlug,
            'post_parent' => (int) $source->post_parent,
            'post_status' => 'draft',
            'post_content' => (string) $source->post_content,
            'post_excerpt' => (string) $source->post_excerpt,
            'menu_order' => (int) $source->menu_order,
            'comment_status' => (string) $source->comment_status,
            'ping_status' => (string) $source->ping_status,
            'post_author' => get_current_user_id(),
        ], true);

        if (is_wp_error($newPostId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kunne ikke kopieres: ' . $newPostId->get_error_message()]));
            exit;
        }
        $newPostId = (int) $newPostId;
        if ($newPostId <= 0) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'WordPress returnerede ikke et gyldigt ID til kopien.']));
            exit;
        }

        try {
            $pageTemplate = sanitize_text_field((string) get_post_meta($sourceId, '_wp_page_template', true));
            if ($pageTemplate !== '') {
                update_post_meta($newPostId, '_wp_page_template', $pageTemplate);
            }
            $thumbnailId = absint(get_post_thumbnail_id($sourceId));
            if ($thumbnailId > 0) {
                set_post_thumbnail($newPostId, $thumbnailId);
            }

            TemplateLayoutModel::ensureMigrated();
            TemplateLayoutModel::setPageChoice($newPostId, 'header', TemplateLayoutModel::pageChoice($sourceId, 'header'));
            TemplateLayoutModel::setPageChoice($newPostId, 'footer', TemplateLayoutModel::pageChoice($sourceId, 'footer'));

            $sourceHasDesigner = metadata_exists('post', $sourceId, LayoutModel::META)
                || (int) get_post_meta($sourceId, LayoutModel::VERSION_META, true) > 0;
            if ($sourceHasDesigner) {
                $sourceModel = LayoutModel::get($sourceId);
                $newVersion = LayoutModel::saveVersion(
                    $newPostId,
                    $sourceModel,
                    get_current_user_id(),
                    'Kopieret fra side ID ' . $sourceId . ' · ' . (string) $source->post_title
                );
                if ($newVersion !== 1) {
                    throw new \RuntimeException('Den kopierede Designer-side startede ikke med sin egen v1-historik.');
                }
                if (!hash_equals(LayoutModel::structuralDigest($sourceModel), LayoutModel::structuralDigest(LayoutModel::get($newPostId)))) {
                    throw new \RuntimeException('Designer-layoutet på kopien matcher ikke kildesiden.');
                }
            }

            clean_post_cache($newPostId);
        } catch (\Throwable $error) {
            wp_trash_post($newPostId);
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Kopien blev rullet tilbage: ' . $error->getMessage()]));
            exit;
        }

        wp_safe_redirect(self::url('h18-clean-pages', [
            'vd_status' => 'ok',
            'vd_message' => '“' . (string) $source->post_title . '” er kopieret som “' . $newTitle . '” (kladde).',
        ]));
        exit;
    }

    public static function updatePageStatus(): void
    {
        self::guard();
        check_admin_referer(self::PAGE_STATUS_NONCE);

        $postId = absint($_POST['post_id'] ?? 0);
        $desired = sanitize_key((string) ($_POST['page_status'] ?? ''));
        if ($postId <= 0 || get_post_type($postId) !== 'page' || !current_user_can('edit_post', $postId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den valgte side er ikke gyldig.']));
            exit;
        }
        if (!in_array($desired, ['publish', 'draft'], true)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den ønskede sidestatus er ikke gyldig.']));
            exit;
        }
        if ($desired === 'publish' && !current_user_can('publish_pages')) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Du har ikke rettighed til at publicere sider.']));
            exit;
        }

        $frontId = get_option('show_on_front', 'posts') === 'page' ? absint(get_option('page_on_front', 0)) : 0;
        if ($desired === 'draft' && $frontId === $postId) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den aktive hjemmeside kan ikke gøres til kladde. Vælg først en anden side som Hjem.']));
            exit;
        }

        $result = wp_update_post(['ID' => $postId, 'post_status' => $desired], true);
        if (is_wp_error($result) || (int) $result <= 0) {
            $detail = is_wp_error($result) ? $result->get_error_message() : 'Ukendt WordPress-fejl';
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Sidestatus kunne ikke ændres: ' . $detail]));
            exit;
        }
        clean_post_cache($postId);
        $message = $desired === 'publish'
            ? '“' . get_the_title($postId) . '” er nu publiceret.'
            : '“' . get_the_title($postId) . '” er nu kladde og ikke længere offentligt publiceret.';
        wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'ok', 'vd_message' => $message]));
        exit;
    }

    public static function trashPage(): void
    {
        self::guard();
        check_admin_referer(self::TRASH_PAGE_NONCE);

        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page' || !current_user_can('delete_post', $postId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kan ikke slettes eller du mangler rettighed.']));
            exit;
        }
        $frontId = get_option('show_on_front', 'posts') === 'page' ? absint(get_option('page_on_front', 0)) : 0;
        if ($frontId === $postId) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den aktive hjemmeside kan ikke slettes. Vælg først en anden side som Hjem.']));
            exit;
        }

        $title = (string) get_the_title($postId);
        $trashed = wp_trash_post($postId);
        if (!$trashed instanceof \WP_Post) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kunne ikke flyttes til papirkurven.']));
            exit;
        }
        wp_safe_redirect(self::url('h18-clean-pages', [
            'vd_status' => 'ok',
            'vd_message' => '“' . $title . '” er flyttet til WordPress-papirkurven og kan gendannes derfra.',
        ]));
        exit;
    }


    public static function setHomePage(): void
    {
        self::guard();
        check_admin_referer(self::SET_HOME_PAGE_NONCE);

        $postId = absint($_POST['post_id'] ?? 0);
        if ($postId <= 0 || get_post_type($postId) !== 'page' || !current_user_can('edit_post', $postId)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Den valgte side er ikke gyldig.']));
            exit;
        }
        if (!metadata_exists('post', $postId, LayoutModel::META)) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Kun en side med Visual Designer-layout kan vælges som ny hjemmeside her.']));
            exit;
        }

        $page = get_post($postId);
        if (!$page instanceof \WP_Post) {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Siden kunne ikke læses.']));
            exit;
        }

        if ((string) $page->post_status !== 'publish') {
            wp_safe_redirect(self::url('h18-clean-pages', ['vd_status' => 'error', 'vd_message' => 'Publicér siden først. “Sæt som Hjem” ændrer kun hjemmesidevalget og publicerer aldrig automatisk.']));
            exit;
        }

        if (absint(get_option('page_for_posts', 0)) === $postId) {
            update_option('page_for_posts', 0);
        }
        update_option('show_on_front', 'page');
        update_option('page_on_front', $postId);
        clean_post_cache($postId);

        wp_safe_redirect(self::url('h18-clean-pages', [
            'vd_status' => 'ok',
            'vd_message' => '“' . get_the_title($postId) . '” er nu valgt som hjemmeside.',
        ]));
        exit;
    }

    public static function ensureLandingPage(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        $stored = absint(get_option(self::LANDING_PAGE_OPTION, 0));
        if ($stored > 0 && get_post_type($stored) === 'page') { return; }

        $existing = get_posts([
            'post_type' => 'page', 'post_status' => ['publish','draft','pending','private','future'],
            'meta_key' => self::LANDING_PAGE_META, 'meta_value' => '1', 'fields' => 'ids',
            'posts_per_page' => 1, 'no_found_rows' => true, 'suppress_filters' => true,
        ]);
        if (is_array($existing) && !empty($existing)) {
            update_option(self::LANDING_PAGE_OPTION, (int) $existing[0], false);
            return;
        }

        $postId = wp_insert_post([
            'post_type' => 'page',
            'post_title' => 'Hjem – Visual Designer',
            'post_name' => self::uniquePageSlug('hjem-visual-designer'),
            'post_status' => 'draft',
            'post_content' => '',
            'post_author' => get_current_user_id(),
        ], true);
        if (is_wp_error($postId) || (int) $postId <= 0) { return; }
        $postId = (int) $postId;
        update_post_meta($postId, self::LANDING_PAGE_META, '1');
        LayoutModel::saveVersion($postId, self::landingPageModel(), get_current_user_id(), 'Oprettet ny Visual Designer-landingsside · gammel Hjem-side urørt');
        TemplateLayoutModel::ensureMigrated();
        TemplateLayoutModel::setPageChoice($postId, 'header', 'auto');
        TemplateLayoutModel::setPageChoice($postId, 'footer', 'auto');
        update_option(self::LANDING_PAGE_OPTION, $postId, false);
    }

    /** @return array<string,mixed> */
    private static function landingPageModel(): array
    {
        $g = static function (int $x,int $y,int $w,int $h): array {
            return [
                'desktop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h],
                'laptop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
                'tablet'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
                'mobile'=>['x'=>0,'y'=>$y,'w'=>120,'h'=>$h,'inheritDesktop'=>false],
            ];
        };
        return LayoutModel::normalize(['nodes'=>[
            ['id'=>'section-landing-v0147','type'=>'section','parentId'=>'','order'=>10,'geometry'=>$g(6,0,108,42),'props'=>['background'=>'#ffffff','padding'=>0,'minHeightRows'=>42,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]],
            ['id'=>'container-landing-v0147','type'=>'container','parentId'=>'section-landing-v0147','order'=>10,'geometry'=>$g(0,0,120,42),'props'=>['background'=>'#ffffff','padding'=>0,'minHeightRows'=>42,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]],
            ['id'=>'text-landing-v0147','type'=>'text','parentId'=>'container-landing-v0147','order'=>10,'geometry'=>$g(6,10,108,14),'props'=>['heading'=>'Ny Visual Designer-landingsside','headingLevel'=>'h2','text'=>'Denne kladde er oprettet som et rent udgangspunkt. Header og Footer vises i Samlet preview. Den gamle Hjem-side konverteres først senere.','align'=>'center','verticalAlign'=>'center','background'=>'#ffffff','backgroundTransparent'=>true,'textColor'=>'#30382a','headingColor'=>'#30382a','fontFamily'=>'system','fontSize'=>18,'fontWeight'=>400,'lineHeight'=>1.5,'letterSpacing'=>0,'headingFontFamily'=>'body','headingFontSize'=>36,'headingFontWeight'=>700,'headingLineHeight'=>1.2,'headingLetterSpacing'=>0,'padding'=>16,'radius'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]],
        ]]);
    }

    public static function repairBlankPageSlugs(): void
    {
        if (!current_user_can('edit_pages') || get_option(self::BLANK_SLUG_REPAIR_OPTION, false)) {
            return;
        }

        $repaired = 0;
        foreach (self::allPages() as $page) {
            if (!$page instanceof \WP_Post || trim((string) $page->post_name) !== '') {
                continue;
            }
            if (!current_user_can('edit_post', $page->ID)) {
                continue;
            }

            $base = sanitize_title((string) $page->post_title);
            $slug = self::uniquePageSlug($base !== '' ? $base : 'side');
            $result = wp_update_post([
                'ID' => (int) $page->ID,
                'post_name' => $slug,
            ], true);
            if (!is_wp_error($result) && (int) $result > 0) {
                $repaired++;
            }
        }

        update_option(self::BLANK_SLUG_REPAIR_OPTION, [
            'repairedUtc' => gmdate('c'),
            'count' => $repaired,
        ], false);
    }

    private static function uniquePageSlug(string $base): string
    {
        $base = sanitize_title($base);
        if ($base === '') {
            $base = 'side';
        }

        $candidate = $base;
        $suffix = 2;
        while (self::pageSlugExists($candidate)) {
            $candidate = $base . '-' . $suffix;
            $suffix++;
            if ($suffix > 10000) {
                throw new \RuntimeException('Kunne ikke finde en ledig side-slug.');
            }
        }
        return $candidate;
    }

    private static function pageSlugExists(string $slug): bool
    {
        $ids = get_posts([
            'post_type' => 'page',
            'post_status' => ['publish', 'draft', 'pending', 'private', 'future'],
            'name' => sanitize_title($slug),
            'fields' => 'ids',
            'posts_per_page' => 1,
            'no_found_rows' => true,
            'suppress_filters' => true,
        ]);
        return is_array($ids) && !empty($ids);
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
        self::open($cfg['title'], 'Indholdsoversigt med direkte adgang til WordPress og Visual Designer');
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
        echo '<table class="widefat striped"><thead><tr><th>Side</th><th>Designer</th><th>Nodes</th><th>Handlinger</th></tr></thead><tbody>';
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
        return array_values(array_filter(get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC', 'post_status' => ['publish', 'draft', 'pending', 'private', 'future']]), static fn($page): bool => $page instanceof \WP_Post));
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
            wp_die(esc_html__('Ingen adgang.', 'visual-designer-manager'));
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
        echo '<div class="h18-manager-card h18-manager-module"><h2>' . esc_html($title) . '</h2><p>' . esc_html($text) . '</p><span class="h18-manager-badge is-progress">Admin-grundlag klar</span></div>';
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
