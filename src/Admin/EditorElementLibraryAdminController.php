<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only UX enhancers for the existing Sider element palette/workspace.
 *
 * Search, categories, favorites and collapsible workspace widgets operate
 * entirely on the rendered editor. Browser-local state introduces no page
 * storage, public renderer, schema migration or cutover path.
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
        $workspaceJsPath = $pluginDir . '/assets/ultimate-designer-workspace-widgets.js';
        $workspaceCssPath = $pluginDir . '/assets/ultimate-designer-workspace-widgets.css';

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

        /* v0.8.22 closes the post-Redo race for structural editor gestures. */
        wp_enqueue_script(
            'hangar18-ultimate-designer-history-post-restore-v0822',
            $pluginUrl . 'assets/ultimate-designer-history-post-restore-v0822.js',
            ['jquery', 'hangar18-ultimate-designer-history-preload-v0821'],
            is_file($postRestorePath) ? (string) filemtime($postRestorePath) : '0.8.22',
            false
        );

        /*
         * v0.8.23 applies the same post-restore guarantee to edits inside an
         * element without introducing a second history stack.
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

        /*
         * UX-3/v0.8.24 is browser-local workspace chrome only. It is loaded
         * after the stable history stack and cannot mutate page/schema state.
         */
        wp_enqueue_script(
            'hangar18-ultimate-designer-workspace-widgets',
            $pluginUrl . 'assets/ultimate-designer-workspace-widgets.js',
            [
                'jquery',
                'hangar18-manager-admin',
                'hangar18-ultimate-designer-element-library',
                'hangar18-ultimate-designer-history-content-v0823',
            ],
            is_file($workspaceJsPath) ? (string) filemtime($workspaceJsPath) : '0.8.24',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-workspace-widgets',
            $pluginUrl . 'assets/ultimate-designer-workspace-widgets.css',
            ['hangar18-ultimate-designer-element-library'],
            is_file($workspaceCssPath) ? (string) filemtime($workspaceCssPath) : '0.8.24'
        );

        // v0.8.17-v0.8.20 history implementations remain rollback archaeology.
        // v0.8.21 is the owner; v0.8.22/v0.8.23 are narrow post-restore bridges.
    }
}
