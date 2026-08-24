<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only compatibility renderer for persisted generic Grid/Flex parents.
 *
 * v0.8.90 rebuilds generic Grid/Flex compositions from canonical parent/span/
 * stack state after reload. It does not own drag/drop. Implicit multi-column
 * layouts are materialized through the established v0.8.41 span API so Gem can
 * persist the same layout the editor shows.
 *
 * v0.8.91 adds a narrowly-scoped save integrity guard. It snapshots the active
 * rows at the user's Save activation and only restores that snapshot if the
 * same submit transaction has catastrophically marked every active row removed
 * before the normal serializer runs. Normal section deletion remains untouched.
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
        $saveGuardPath = $pluginDir . '/assets/ultimate-designer-save-integrity-guard-v0891.js';
        $jsPath = $pluginDir . '/assets/ultimate-designer-saved-layout-rebuild-v0890.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-saved-layout-rebuild-v0890.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-save-integrity-guard-v0891',
            $pluginUrl . 'assets/ultimate-designer-save-integrity-guard-v0891.js',
            [],
            is_file($saveGuardPath) ? (string) filemtime($saveGuardPath) : '0.8.91',
            false
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-saved-layout-rebuild-v0890',
            $pluginUrl . 'assets/ultimate-designer-saved-layout-rebuild-v0890.js',
            [
                'jquery',
                'hangar18-ultimate-designer-lego-resize-v0841',
                'hangar18-ultimate-designer-lego-fixes-v0851',
                'hangar18-ultimate-designer-lego-placement-stability-v0862',
                'hangar18-ultimate-designer-lego-inspector-only-v0847',
                'hangar18-ultimate-designer-save-integrity-guard-v0891',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.90',
            false
        );

        wp_enqueue_style(
            'hangar18-ultimate-designer-saved-layout-rebuild-v0890',
            $pluginUrl . 'assets/ultimate-designer-saved-layout-rebuild-v0890.css',
            ['hangar18-ultimate-designer-lego-fixes-v0851'],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.90'
        );

        if (
            class_exists(UltimateDesignerTraceAdminController::class) &&
            UltimateDesignerTraceAdminController::enabled()
        ) {
            $diagPath = $pluginDir . '/assets/ultimate-designer-live-diagnostics-reload-v0889.js';
            wp_enqueue_script(
                'hangar18-ultimate-designer-live-diagnostics-reload-v0889',
                $pluginUrl . 'assets/ultimate-designer-live-diagnostics-reload-v0889.js',
                [
                    'hangar18-ultimate-designer-live-diagnostics-v0888',
                    'hangar18-ultimate-designer-saved-layout-rebuild-v0890',
                ],
                is_file($diagPath) ? (string) filemtime($diagPath) : '0.8.89',
                true
            );
        }
    }
}
