<?php
/**
 * Plugin Name: Visual Designer Manager
 * Plugin URI: https://github.com/phenixdk2020/hangar18-manager
 * Update URI: https://github.com/phenixdk2020/hangar18-manager
 * Description: Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.
 * Version: 0.1.41
 * Author: Visual Designer Manager
 * Requires at least: 6.4
 * Requires PHP: 8.0
 * Text Domain: hangar18-manager-clean
 */

if (!defined('ABSPATH')) {
    exit;
}

define('H18_CLEAN_VERSION', '0.1.41');
define('H18_CLEAN_FILE', __FILE__);
define('H18_CLEAN_DIR', plugin_dir_path(__FILE__));
define('H18_CLEAN_URL', plugin_dir_url(__FILE__));

/**
 * Compatibility marker for Hangar18 Base Theme 1.2.x.
 *
 * The theme only checks whether the historical Hangar18_Manager class exists
 * to decide if a Manager is active. Clean deliberately does not load the
 * legacy manager runtime, but exposing this empty marker keeps the theme's
 * status detection correct while the clean architecture remains isolated.
 */
if (!class_exists('Hangar18_Manager', false)) {
    final class Hangar18_Manager
    {
        public const CLEAN_COMPATIBILITY_MARKER = true;

        private function __construct()
        {
        }
    }
}

require_once H18_CLEAN_DIR . 'src/Model/HierarchyNormalizer.php';
require_once H18_CLEAN_DIR . 'src/Model/LayoutModel.php';
require_once H18_CLEAN_DIR . 'src/Model/GlobalLayoutModel.php';
require_once H18_CLEAN_DIR . 'src/Model/TemplateLayoutModel.php';
require_once H18_CLEAN_DIR . 'src/Migration/LegacyHeaderConverter.php';
require_once H18_CLEAN_DIR . 'src/Diagnostics/DiagnosticStore.php';
require_once H18_CLEAN_DIR . 'src/Admin/EditorController.php';
require_once H18_CLEAN_DIR . 'src/Admin/AdminController.php';
require_once H18_CLEAN_DIR . 'src/Admin/AdminMenuBridge.php';
require_once H18_CLEAN_DIR . 'src/Admin/ExportController.php';
require_once H18_CLEAN_DIR . 'src/Admin/NavigationController.php';
require_once H18_CLEAN_DIR . 'src/Admin/ThemeController.php';
require_once H18_CLEAN_DIR . 'src/Admin/GlobalDesignerController.php';
require_once H18_CLEAN_DIR . 'src/Frontend/Renderer.php';
require_once H18_CLEAN_DIR . 'src/Frontend/ResponsiveRenderer.php';
require_once H18_CLEAN_DIR . 'src/Frontend/ThemeShell.php';
require_once H18_CLEAN_DIR . 'src/Update/GitHubUpdater.php';

add_action('plugins_loaded', static function (): void {
    \Hangar18\Clean\Migration\LegacyHeaderConverter::register();
    \Hangar18\Clean\Diagnostics\DiagnosticStore::register();
    \Hangar18\Clean\Admin\EditorController::register();
    \Hangar18\Clean\Admin\AdminController::register();
    \Hangar18\Clean\Admin\AdminMenuBridge::register();
    \Hangar18\Clean\Admin\ExportController::register();
    \Hangar18\Clean\Admin\NavigationController::register();
    \Hangar18\Clean\Admin\ThemeController::register();
    \Hangar18\Clean\Admin\GlobalDesignerController::register();
    \Hangar18\Clean\Frontend\Renderer::register();
    \Hangar18\Clean\Frontend\ResponsiveRenderer::register();
    \Hangar18\Clean\Frontend\ThemeShell::register();
    \Hangar18\Clean\Update\GitHubUpdater::register();
});

add_action('admin_enqueue_scripts', static function (string $hook): void {
    $isPageDesigner = strpos($hook, 'h18-clean-editor') !== false;
    $isGlobalDesigner = strpos($hook, 'h18-clean-header-footer') !== false;
    if ((!$isPageDesigner && !$isGlobalDesigner) || !current_user_can('edit_pages')) {
        return;
    }

    /*
     * Current Clean core provides theme-accurate preview, canonical grid layout,
     * verified Save, independent image-box rendering and responsive layout editing.
     */
    wp_dequeue_script('h18-clean-editor');

    $postId = isset($_GET['post']) ? absint($_GET['post']) : 0;
    if ($isGlobalDesigner) {
        $part = isset($_GET['part']) && sanitize_key((string) $_GET['part']) === 'footer' ? 'footer' : 'header';
        $postId = 0;
        \Hangar18\Clean\Model\TemplateLayoutModel::ensureMigrated();
        $templateId = isset($_GET['template']) ? sanitize_key((string) $_GET['template']) : '';
        if ($templateId === '' || !\Hangar18\Clean\Model\TemplateLayoutModel::exists($templateId, $part)) { $templateId = \Hangar18\Clean\Model\TemplateLayoutModel::defaultId($part); }
        $model = $templateId !== '' ? \Hangar18\Clean\Model\TemplateLayoutModel::model($templateId) : \Hangar18\Clean\Model\LayoutModel::empty();
    } else {
        $model = $postId > 0 && get_post_type($postId) === 'page'
            ? \Hangar18\Clean\Model\LayoutModel::get($postId)
            : \Hangar18\Clean\Model\LayoutModel::empty();
    }

    $menuPayload = array_values(array_map(static function ($menu): array {
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

    wp_enqueue_script(
        'h18-clean-editor-v018-core',
        H18_CLEAN_URL . 'assets/editor-v018-core.js',
        ['jquery'],
        H18_CLEAN_VERSION,
        true
    );
    wp_localize_script('h18-clean-editor-v018-core', 'H18CleanEditor', [
        'version' => H18_CLEAN_VERSION,
        'schemaVersion' => \Hangar18\Clean\Model\LayoutModel::SCHEMA,
        'units' => \Hangar18\Clean\Model\LayoutModel::UNITS,
        'rowPx' => \Hangar18\Clean\Model\LayoutModel::ROW_PX,
        'postId' => $postId,
        'initialModel' => $model,
        'pages' => array_values(array_map(static function ($page): array { return ['id' => (int) $page->ID, 'title' => (string) $page->post_title]; }, get_pages(['sort_column' => 'menu_order,post_title', 'sort_order' => 'ASC', 'post_status' => ['publish', 'draft', 'pending', 'private', 'future']]))),
        'menus' => $menuPayload,
        'ajaxUrl' => admin_url('admin-ajax.php'),
        'diagAction' => 'h18_clean_diag_append',
        'diagNonce' => wp_create_nonce('h18_clean_diag_append'),
    ]);

    wp_enqueue_style(
        'h18-clean-editor-v016',
        H18_CLEAN_URL . 'assets/editor-v016.css',
        ['h18-clean-editor'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v018',
        H18_CLEAN_URL . 'assets/editor-v018.css',
        ['h18-clean-editor-v016'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0110',
        H18_CLEAN_URL . 'assets/editor-v0110.css',
        ['h18-clean-editor-v018'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0112',
        H18_CLEAN_URL . 'assets/editor-v0112.css',
        ['h18-clean-editor-v0110'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0114',
        H18_CLEAN_URL . 'assets/editor-v0114.css',
        ['h18-clean-editor-v0112'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0117',
        H18_CLEAN_URL . 'assets/editor-v0117.css',
        ['h18-clean-editor-v0114'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0118',
        H18_CLEAN_URL . 'assets/editor-v0118.css',
        ['h18-clean-editor-v0117'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0120',
        H18_CLEAN_URL . 'assets/editor-v0120.css',
        ['h18-clean-editor-v0118'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0121',
        H18_CLEAN_URL . 'assets/editor-v0121.css',
        ['h18-clean-editor-v0120'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0122-hierarchy',
        H18_CLEAN_URL . 'assets/editor-v0122-hierarchy.css',
        ['h18-clean-editor-v0121'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0123-ux',
        H18_CLEAN_URL . 'assets/editor-v0123-ux.css',
        ['h18-clean-editor-v0122-hierarchy'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0125',
        H18_CLEAN_URL . 'assets/editor-v0125.css',
        ['h18-clean-editor-v0123-ux'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0131',
        H18_CLEAN_URL . 'assets/editor-v0131.css',
        ['h18-clean-editor-v0125'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0132',
        H18_CLEAN_URL . 'assets/editor-v0132.css',
        ['h18-clean-editor-v0131'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0134',
        H18_CLEAN_URL . 'assets/editor-v0134.css',
        ['h18-clean-editor-v0132'],
        H18_CLEAN_VERSION
    );
    wp_enqueue_style(
        'h18-clean-editor-v0135',
        H18_CLEAN_URL . 'assets/editor-v0135.css',
        ['h18-clean-editor-v0134'],
        H18_CLEAN_VERSION
    );

    wp_enqueue_script(
        'h18-clean-editor-v0114',
        H18_CLEAN_URL . 'assets/editor-v0114.js',
        ['h18-clean-editor-v018-core'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0120',
        H18_CLEAN_URL . 'assets/editor-v0120.js',
        ['h18-clean-editor-v0114'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0121',
        H18_CLEAN_URL . 'assets/editor-v0121.js',
        ['h18-clean-editor-v0120'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0121-panels',
        H18_CLEAN_URL . 'assets/editor-v0121-panels.js',
        ['h18-clean-editor-v0121'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0122-hierarchy',
        H18_CLEAN_URL . 'assets/editor-v0122-hierarchy.js',
        ['h18-clean-editor-v0121-panels'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0123-ux',
        H18_CLEAN_URL . 'assets/editor-v0123-ux.js',
        ['h18-clean-editor-v0122-hierarchy'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0125',
        H18_CLEAN_URL . 'assets/editor-v0125.js',
        ['h18-clean-editor-v0123-ux'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0131',
        H18_CLEAN_URL . 'assets/editor-v0131.js',
        ['h18-clean-editor-v0125'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0132',
        H18_CLEAN_URL . 'assets/editor-v0132.js',
        ['h18-clean-editor-v0131'],
        H18_CLEAN_VERSION,
        true
    );
    wp_enqueue_script(
        'h18-clean-editor-v0135',
        H18_CLEAN_URL . 'assets/editor-v0135.js',
        ['h18-clean-editor-v0132'],
        H18_CLEAN_VERSION,
        true
    );
    /* v0.1.6 border/autogrow JS is retired; current Clean core handles these natively. */
}, 20);
