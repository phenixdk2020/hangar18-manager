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
        $workspaceJsPath = $pluginDir . '/assets/ultimate-designer-workspace-widgets.js';
        $workspaceCssPath = $pluginDir . '/assets/ultimate-designer-workspace-widgets.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-element-library',
            $pluginUrl . 'assets/ultimate-designer-element-library.js',
            ['jquery', 'hangar18-manager-admin'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-element-library',
            $pluginUrl . 'assets/ultimate-designer-element-library.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.7'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-workspace-widgets',
            $pluginUrl . 'assets/ultimate-designer-workspace-widgets.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-element-library'],
            is_file($workspaceJsPath) ? (string) filemtime($workspaceJsPath) : '0.8.14',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-workspace-widgets',
            $pluginUrl . 'assets/ultimate-designer-workspace-widgets.css',
            ['hangar18-ultimate-designer-element-library'],
            is_file($workspaceCssPath) ? (string) filemtime($workspaceCssPath) : '0.8.14'
        );
    }
}
