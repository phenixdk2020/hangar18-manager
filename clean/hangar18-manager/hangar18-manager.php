<?php
/**
 * Plugin Name: Hangar18 Manager Clean
 * Plugin URI: https://hangar18.dk/
 * Update URI: https://github.com/phenixdk2020/hangar18-manager
 * Description: Ren Hangar18 120-unit sidebygger uden legacy editor-runtime.
 * Version: 0.1.12
 * Author: Hangar18
 * Requires at least: 6.4
 * Requires PHP: 8.0
 * Text Domain: hangar18-manager-clean
 */

if (!defined('ABSPATH')) {
    exit;
}

define('H18_CLEAN_VERSION', '0.1.12');
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

require_once H18_CLEAN_DIR . 'src/Model/LayoutModel.php';
require_once H18_CLEAN_DIR . 'src/Diagnostics/DiagnosticStore.php';
require_once H18_CLEAN_DIR . 'src/Admin/EditorController.php';
require_once H18_CLEAN_DIR . 'src/Admin/AdminController.php';
require_once H18_CLEAN_DIR . 'src/Admin/AdminMenuBridge.php';
require_once H18_CLEAN_DIR . 'src/Frontend/Renderer.php';
require_once H18_CLEAN_DIR . 'src/Update/GitHubUpdater.php';

add_action('plugins_loaded', static function (): void {
    \Hangar18\Clean\Diagnostics\DiagnosticStore::register();
    \Hangar18\Clean\Admin\EditorController::register();
    \Hangar18\Clean\Admin\AdminController::register();
    \Hangar18\Clean\Admin\AdminMenuBridge::register();
    \Hangar18\Clean\Frontend\Renderer::register();
    \Hangar18\Clean\Update\GitHubUpdater::register();
});

add_action('admin_enqueue_scripts', static function (string $hook): void {
    if (strpos($hook, 'h18-clean-editor') === false || !current_user_can('edit_pages')) {
        return;
    }

    /*
     * 0.1.12 separates selection from overlap diagnostics, localises editor
     * labels and keeps editor chrome outside canonical element geometry.
     */
    wp_dequeue_script('h18-clean-editor');

    $postId = isset($_GET['post']) ? absint($_GET['post']) : 0;
    $model = $postId > 0 && get_post_type($postId) === 'page'
        ? \Hangar18\Clean\Model\LayoutModel::get($postId)
        : \Hangar18\Clean\Model\LayoutModel::empty();

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
    /* v0.1.6 border/autogrow JS is retired; current Clean core handles these natively. */
}, 20);
