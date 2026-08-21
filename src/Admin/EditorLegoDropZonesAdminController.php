<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only visual target layer for LEGO placement.
 *
 * The asset does not own placement. Over/Under stay passive over jQuery
 * sortable, while Venstre/Højre reuse the existing nesting motor's
 * .h18-v0811-side-zone data contract.
 */
final class EditorLegoDropZonesAdminController
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
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-drop-zones-v0838.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-drop-zones-v0838.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-drop-zones-v0838',
            $pluginUrl . 'assets/ultimate-designer-lego-drop-zones-v0838.js',
            [
                'jquery',
                'hangar18-ultimate-designer-nesting-tools',
                'hangar18-ultimate-designer-lego-layout-primary-v0837',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.38',
            false
        );

        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-drop-zones-v0838',
            $pluginUrl . 'assets/ultimate-designer-lego-drop-zones-v0838.css',
            ['hangar18-ultimate-designer-nesting-tools'],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.38'
        );
    }
}
