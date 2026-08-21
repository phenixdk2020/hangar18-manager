<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only bridge that makes legacy Direct Design a thin view over the
 * canonical LEGO design/state controls. It owns no persistence, placement,
 * public rendering or history state.
 */
final class EditorLegoPrimaryViewAdminController
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
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-primary-view-v0836.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-primary-view-v0836.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-primary-view-v0836',
            $pluginUrl . 'assets/ultimate-designer-lego-primary-view-v0836.js',
            [
                'jquery',
                'hangar18-ultimate-designer-history-content-v0823',
                'hangar18-ultimate-designer-lego-design-responsive-v0833',
                'hangar18-ultimate-designer-lego-interaction-states-v0834',
                'hangar18-ultimate-designer-lego-interaction-snapshot-v0834',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.36',
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-primary-view-v0836',
            $pluginUrl . 'assets/ultimate-designer-lego-primary-view-v0836.css',
            [
                'hangar18-ultimate-designer-lego-design-responsive-v0833',
                'hangar18-ultimate-designer-lego-interaction-states-v0834',
            ],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.36'
        );
    }
}
