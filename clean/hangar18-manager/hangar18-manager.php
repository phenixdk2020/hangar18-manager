<?php
/**
 * Plugin Name: Hangar18 Manager Clean
 * Plugin URI: https://hangar18.dk/
 * Update URI: https://github.com/phenixdk2020/hangar18-manager
 * Description: Ren Hangar18 120-unit sidebygger uden legacy editor-runtime.
 * Version: 0.1.0
 * Author: Hangar18
 * Requires at least: 6.4
 * Requires PHP: 8.0
 * Text Domain: hangar18-manager-clean
 */

if (!defined('ABSPATH')) {
    exit;
}

define('H18_CLEAN_VERSION', '0.1.0');
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
require_once H18_CLEAN_DIR . 'src/Frontend/Renderer.php';
require_once H18_CLEAN_DIR . 'src/Update/GitHubUpdater.php';

add_action('plugins_loaded', static function (): void {
    \Hangar18\Clean\Diagnostics\DiagnosticStore::register();
    \Hangar18\Clean\Admin\EditorController::register();
    \Hangar18\Clean\Frontend\Renderer::register();
    \Hangar18\Clean\Update\GitHubUpdater::register();
});
