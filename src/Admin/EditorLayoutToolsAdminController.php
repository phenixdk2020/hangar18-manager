<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Additive tools for the existing Sider editor.
 *
 * Auto Boxes reuses the existing Grid + Container storage/runtime. Table reuses
 * the existing sanitized HTML element so this slice does not create a new public
 * renderer, schema migration, URL change or cutover path. Generic nesting also
 * reuses LayoutParentKey so normal elements can be placed inside a Box without a
 * parallel storage model.
 */
final class EditorLayoutToolsAdminController
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
        $jsPath = $pluginDir . '/assets/ultimate-designer-layout-tools.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-layout-tools.css';
        $boxJsPath = $pluginDir . '/assets/ultimate-designer-box-tools.js';
        $boxCssPath = $pluginDir . '/assets/ultimate-designer-box-tools.css';
        $nestingJsPath = $pluginDir . '/assets/ultimate-designer-nesting-tools.js';
        $nestingCssPath = $pluginDir . '/assets/ultimate-designer-nesting-tools.css';
        $boxContentJsPath = $pluginDir . '/assets/ultimate-designer-box-content-layout.js';
        $boxContentCssPath = $pluginDir . '/assets/ultimate-designer-box-content-layout.css';
        $tableAppearanceJsPath = $pluginDir . '/assets/ultimate-designer-table-appearance.js';
        $tableAppearanceCssPath = $pluginDir . '/assets/ultimate-designer-table-appearance.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-layout-tools',
            $pluginUrl . 'assets/ultimate-designer-layout-tools.js',
            ['jquery', 'jquery-ui-sortable', 'hangar18-manager-admin'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-layout-tools',
            $pluginUrl . 'assets/ultimate-designer-layout-tools.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.7'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-box-tools',
            $pluginUrl . 'assets/ultimate-designer-box-tools.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools'],
            is_file($boxJsPath) ? (string) filemtime($boxJsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-box-tools',
            $pluginUrl . 'assets/ultimate-designer-box-tools.css',
            ['hangar18-ultimate-designer-layout-tools'],
            is_file($boxCssPath) ? (string) filemtime($boxCssPath) : '0.8.7'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-nesting-tools',
            $pluginUrl . 'assets/ultimate-designer-nesting-tools.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools', 'hangar18-ultimate-designer-box-tools'],
            is_file($nestingJsPath) ? (string) filemtime($nestingJsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-nesting-tools',
            $pluginUrl . 'assets/ultimate-designer-nesting-tools.css',
            ['hangar18-ultimate-designer-box-tools'],
            is_file($nestingCssPath) ? (string) filemtime($nestingCssPath) : '0.8.7'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-box-content-layout',
            $pluginUrl . 'assets/ultimate-designer-box-content-layout.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-nesting-tools'],
            is_file($boxContentJsPath) ? (string) filemtime($boxContentJsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-box-content-layout',
            $pluginUrl . 'assets/ultimate-designer-box-content-layout.css',
            ['hangar18-ultimate-designer-nesting-tools'],
            is_file($boxContentCssPath) ? (string) filemtime($boxContentCssPath) : '0.8.7'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-table-appearance',
            $pluginUrl . 'assets/ultimate-designer-table-appearance.js',
            ['jquery', 'hangar18-manager-admin', 'hangar18-ultimate-designer-layout-tools'],
            is_file($tableAppearanceJsPath) ? (string) filemtime($tableAppearanceJsPath) : '0.8.7',
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-table-appearance',
            $pluginUrl . 'assets/ultimate-designer-table-appearance.css',
            ['hangar18-ultimate-designer-layout-tools'],
            is_file($tableAppearanceCssPath) ? (string) filemtime($tableAppearanceCssPath) : '0.8.7'
        );
    }
}
