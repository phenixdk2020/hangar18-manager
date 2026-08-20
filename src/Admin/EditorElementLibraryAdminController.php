<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only UX enhancer for the existing Sider element palette.
 *
 * Search, categories and favorites operate entirely on the rendered palette.
 * Favorites are browser-local and this controller introduces no page storage,
 * public renderer, schema migration or cutover path.
 */
final class EditorElementLibraryAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-element-library.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-element-library.css';
        $historyPath = $pluginDir . '/assets/ultimate-designer-history-preload-v0820.js';

        /*
         * v0.8.20: the history owner is a real header asset instead of inline
         * code attached to hangar18-manager-admin. The integration controller is
         * registered before Hangar18_Manager::instance(), so v0.8.19 could call
         * wp_add_inline_script() before that target handle was queued; WordPress
         * then discarded the inline runtime. A dedicated in-header asset has no
         * dependency on that registration order and necessarily executes before
         * the legacy assets/admin.js footer runtime initializes editor history.
         */
        wp_enqueue_script(
            'hangar18-ultimate-designer-history-preload-v0820',
            $pluginUrl . 'assets/ultimate-designer-history-preload-v0820.js',
            ['jquery'],
            is_file($historyPath) ? (string) filemtime($historyPath) : '0.8.20',
            false
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-element-library',
            $pluginUrl . 'assets/ultimate-designer-element-library.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-history-preload-v0820'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-element-library',
            $pluginUrl . 'assets/ultimate-designer-element-library.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.7'
        );

        // v0.8.17-v0.8.19 history implementations remain rollback archaeology
        // only and are deliberately not enqueued beside the v0.8.20 preloader.
    }
}
