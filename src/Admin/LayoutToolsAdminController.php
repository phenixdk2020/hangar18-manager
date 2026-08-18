<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only enqueue bridge for the v0.8.5 Auto-kasser/Table editor tools.
 *
 * The controller does not save pages, register frontend hooks or alter the
 * public renderer. It only layers UI helpers on the existing Sider editor.
 */
final class LayoutToolsAdminController
{
    private const PAGE_SLUG = 'hangar18-pages';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
    }

    /** @param string $hookSuffix */
    public static function enqueue($hookSuffix = ''): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== self::PAGE_SLUG && strpos((string) $hookSuffix, self::PAGE_SLUG) === false) {
            return;
        }

        $pluginFile = dirname(__DIR__, 2) . '/hangar18-manager.php';
        $baseUrl = plugin_dir_url($pluginFile);
        $jsPath = dirname(__DIR__, 2) . '/assets/ultimate-designer-layout-tools.js';
        $cssPath = dirname(__DIR__, 2) . '/assets/ultimate-designer-layout-tools.css';
        $version = class_exists('Hangar18_Manager') ? (string) \Hangar18_Manager::VERSION : '0.8.5';

        wp_enqueue_style(
            'hangar18-ultimate-designer-layout-tools',
            $baseUrl . 'assets/ultimate-designer-layout-tools.css',
            [],
            $version . '-' . (is_file($cssPath) ? (string) filemtime($cssPath) : '0')
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-layout-tools',
            $baseUrl . 'assets/ultimate-designer-layout-tools.js',
            ['jquery', 'hangar18-manager-admin'],
            $version . '-' . (is_file($jsPath) ? (string) filemtime($jsPath) : '0'),
            true
        );
    }
}
