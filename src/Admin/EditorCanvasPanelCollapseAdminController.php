<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Browser-local collapse controls for floating canvas tool panels.
 *
 * This controller only enqueues admin assets. It owns no page state,
 * persistence, history, placement or public rendering.
 */
final class EditorCanvasPanelCollapseAdminController
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
        $jsPath = $pluginDir . '/assets/ultimate-designer-canvas-panel-collapse-v0839.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-canvas-panel-collapse-v0839.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-canvas-panel-collapse-v0839',
            $pluginUrl . 'assets/ultimate-designer-canvas-panel-collapse-v0839.js',
            ['jquery', 'hangar18-manager-admin'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.39',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-canvas-panel-collapse-v0839',
            $pluginUrl . 'assets/ultimate-designer-canvas-panel-collapse-v0839.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.39'
        );
    }
}
