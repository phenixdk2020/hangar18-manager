<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only Navigator/Move UI for the existing Hangar18 Page Editor.
 *
 * This module introduces no parallel page schema and no placement owner.
 * Structural mutations write the existing LayoutParentKey/LayoutParentSelect
 * fields, update the existing flat order fields and ask nesting-tools to refresh.
 */
final class EditorNavigatorAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 120);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-navigator-v0880.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-navigator-v0880.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-navigator-v0880',
            $pluginUrl . 'assets/ultimate-designer-navigator-v0880.js',
            [
                'jquery',
                'hangar18-manager-admin',
                'hangar18-ultimate-designer-nesting-tools',
                'hangar18-ultimate-designer-lego-inspector-only-v0847',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.80',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-navigator-v0880',
            $pluginUrl . 'assets/ultimate-designer-navigator-v0880.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.80'
        );

        wp_localize_script(
            'hangar18-ultimate-designer-navigator-v0880',
            'H18NavigatorV0880',
            [
                'version' => '0.8.80',
                'workspaceKey' => 'h18.ultimate-designer.navigator.v0880',
                'outlineKey' => 'h18.ultimate-designer.container-outlines.v0880',
            ]
        );
    }
}
