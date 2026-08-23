<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Removes the legacy WhatIf/simulation controls from Hangar18 admin screens.
 *
 * This is deliberately UI-only. Existing backend compatibility checks remain
 * untouched, while normal forms no longer expose or submit a WhatIf field.
 */
final class NoWhatIfAdminController
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
        if ($page === '' || strpos($page, 'hangar18-') !== 0) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $cssPath = $pluginDir . '/assets/hangar18-no-whatif-v0858.css';
        $jsPath = $pluginDir . '/assets/hangar18-no-whatif-v0858.js';

        wp_enqueue_style(
            'hangar18-no-whatif-v0858',
            $pluginUrl . 'assets/hangar18-no-whatif-v0858.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.58'
        );

        wp_enqueue_script(
            'hangar18-no-whatif-v0858',
            $pluginUrl . 'assets/hangar18-no-whatif-v0858.js',
            [],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.58',
            true
        );
    }
}
