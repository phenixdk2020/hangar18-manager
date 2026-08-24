<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only compatibility renderer for persisted generic Grid/Flex parents.
 *
 * The legacy nesting composer intentionally owns only Kasse (container) and
 * Auto-kasser (labelled grid). Generic grid/flex parents still persist via
 * LayoutParentKey, but need a read-only canvas proxy after reload. This layer
 * never owns drag/drop or persistence; it only renders canonical saved state.
 */
final class EditorGenericLayoutRebuildAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 130);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-saved-layout-rebuild-v0889.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-saved-layout-rebuild-v0889.css';
        $refreshPath = $pluginDir . '/assets/ultimate-designer-saved-layout-refresh-v0889.js';

        wp_enqueue_script(
            'hangar18-ultimate-designer-saved-layout-rebuild-v0889',
            $pluginUrl . 'assets/ultimate-designer-saved-layout-rebuild-v0889.js',
            ['jquery'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.89',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-saved-layout-refresh-v0889',
            $pluginUrl . 'assets/ultimate-designer-saved-layout-refresh-v0889.js',
            ['hangar18-ultimate-designer-saved-layout-rebuild-v0889'],
            is_file($refreshPath) ? (string) filemtime($refreshPath) : '0.8.89',
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-saved-layout-rebuild-v0889',
            $pluginUrl . 'assets/ultimate-designer-saved-layout-rebuild-v0889.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.89'
        );

        if (
            class_exists(UltimateDesignerTraceAdminController::class) &&
            UltimateDesignerTraceAdminController::enabled()
        ) {
            $diagPath = $pluginDir . '/assets/ultimate-designer-live-diagnostics-reload-v0889.js';
            wp_enqueue_script(
                'hangar18-ultimate-designer-live-diagnostics-reload-v0889',
                $pluginUrl . 'assets/ultimate-designer-live-diagnostics-reload-v0889.js',
                ['hangar18-ultimate-designer-live-diagnostics-v0888'],
                is_file($diagPath) ? (string) filemtime($diagPath) : '0.8.89',
                true
            );
        }
    }
}
