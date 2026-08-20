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
        $historyPath = $pluginDir . '/assets/ultimate-designer-history-preload-v0821.js';
        $postRestorePath = $pluginDir . '/assets/ultimate-designer-history-post-restore-v0822.js';
        $contentHistoryPath = $pluginDir . '/assets/ultimate-designer-history-content-v0823.js';

        /*
         * v0.8.21 remains the header-level history owner: it fixes snapshot
         * cloning so live SELECT/INPUT/TEXTAREA state survives Undo/Redo.
         */
        wp_enqueue_script(
            'hangar18-ultimate-designer-history-preload-v0821',
            $pluginUrl . 'assets/ultimate-designer-history-preload-v0821.js',
            ['jquery'],
            is_file($historyPath) ? (string) filemtime($historyPath) : '0.8.21',
            false
        );

        /*
         * v0.8.22 closes the post-Redo race for structural editor gestures.
         */
        wp_enqueue_script(
            'hangar18-ultimate-designer-history-post-restore-v0822',
            $pluginUrl . 'assets/ultimate-designer-history-post-restore-v0822.js',
            ['jquery', 'hangar18-ultimate-designer-history-preload-v0821'],
            is_file($postRestorePath) ? (string) filemtime($postRestorePath) : '0.8.22',
            false
        );

        /*
         * v0.8.23 applies the same post-restore guarantee to edits inside an
         * element: text/field input, direct design colors/ranges and image media
         * controls. It preserves the first new content checkpoint after Undo/Redo
         * without introducing a second history stack or persistence path.
         */
        wp_enqueue_script(
            'hangar18-ultimate-designer-history-content-v0823',
            $pluginUrl . 'assets/ultimate-designer-history-content-v0823.js',
            [
                'jquery',
                'hangar18-ultimate-designer-history-preload-v0821',
                'hangar18-ultimate-designer-history-post-restore-v0822',
            ],
            is_file($contentHistoryPath) ? (string) filemtime($contentHistoryPath) : '0.8.23',
            false
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-element-library',
            $pluginUrl . 'assets/ultimate-designer-element-library.js',
            [
                'jquery',
                'hangar18-manager-admin',
                'hangar18-ultimate-designer-history-preload-v0821',
                'hangar18-ultimate-designer-history-post-restore-v0822',
                'hangar18-ultimate-designer-history-content-v0823',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-element-library',
            $pluginUrl . 'assets/ultimate-designer-element-library.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.7'
        );

        // v0.8.17-v0.8.20 history implementations remain rollback archaeology.
        // v0.8.21 is the owner; v0.8.22/v0.8.23 are narrow post-restore bridges.
    }
}
