<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only layout bridge for v0.8.37.
 *
 * Existing legacy page-section fields remain the persisted/public-renderer source.
 * This controller only adds a canonical row-state mirror so Direct Design,
 * Inspector and the existing history owner see the same layout transaction.
 */
final class EditorLegoLayoutPrimaryAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        // v0.8.38 is visual targeting only and deliberately registers after
        // the canonical layout/design stack. Placement remains nesting-tools.
        EditorLegoDropZonesAdminController::register();
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-layout-primary-v0837.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-layout-primary-v0837.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-layout-primary-v0837',
            $pluginUrl . 'assets/ultimate-designer-lego-layout-primary-v0837.js',
            [
                'jquery',
                'hangar18-ultimate-designer-history-content-v0823',
                'hangar18-ultimate-designer-lego-primary-view-v0836',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.37',
            false
        );

        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-layout-primary-v0837',
            $pluginUrl . 'assets/ultimate-designer-lego-layout-primary-v0837.css',
            ['hangar18-ultimate-designer-lego-primary-view-v0836'],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.37'
        );
    }
}
