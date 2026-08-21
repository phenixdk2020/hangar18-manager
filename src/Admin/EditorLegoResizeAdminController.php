<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Editor\LegoLayoutSpanModel;

/**
 * LEGO-032/033 admin-only visual resize bridge.
 *
 * Owns only renderer-neutral per-section span state. Existing Auto-kasser /
 * LayoutParentKey owns placement, the existing history engine owns Undo/Redo,
 * and public rendering remains unchanged until controlled conversion.
 */
final class EditorLegoResizeAdminController
{
    public const OPTION = 'hangar18_ultimate_designer_lego_layout_span_v1';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 5);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-resize-v0841.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-resize-v0841.css';
        $responsiveJsPath = $pluginDir . '/assets/ultimate-designer-lego-responsive-layout-v0842.js';
        $responsiveCssPath = $pluginDir . '/assets/ultimate-designer-lego-responsive-layout-v0842.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-resize-v0841',
            $pluginUrl . 'assets/ultimate-designer-lego-resize-v0841.js',
            [
                'jquery',
                'hangar18-ultimate-designer-nesting-tools',
                'hangar18-ultimate-designer-lego-drop-zones-v0838',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.41',
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-resize-v0841',
            $pluginUrl . 'assets/ultimate-designer-lego-resize-v0841.css',
            ['hangar18-ultimate-designer-nesting-tools'],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.41'
        );

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-responsive-layout-v0842',
            $pluginUrl . 'assets/ultimate-designer-lego-responsive-layout-v0842.js',
            [
                'jquery',
                'hangar18-ultimate-designer-lego-resize-v0841',
            ],
            is_file($responsiveJsPath) ? (string) filemtime($responsiveJsPath) : '0.8.42',
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-responsive-layout-v0842',
            $pluginUrl . 'assets/ultimate-designer-lego-responsive-layout-v0842.css',
            ['hangar18-ultimate-designer-lego-resize-v0841'],
            is_file($responsiveCssPath) ? (string) filemtime($responsiveCssPath) : '0.8.42'
        );

        $store = get_option(self::OPTION, []);
        wp_localize_script(
            'hangar18-ultimate-designer-lego-resize-v0841',
            'H18LegoResizeV0841',
            [
                'version' => '0.8.42',
                'schemaVersion' => LegoLayoutSpanModel::SCHEMA_VERSION,
                'columns' => LegoLayoutSpanModel::COLUMN_COUNT,
                'pages' => is_array($store) ? $store : [],
            ]
        );
    }

    public static function captureSave(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        check_admin_referer('h18_save_page_editor');
        if (!isset($_POST['h18_lego_layout_span']) || !is_array($_POST['h18_lego_layout_span'])) {
            return;
        }

        $slug = isset($_POST['page_slug'])
            ? sanitize_title((string) wp_unslash($_POST['page_slug']))
            : '';
        if ($slug === '') {
            return;
        }

        $rawEntries = wp_unslash($_POST['h18_lego_layout_span']);
        $sections = [];
        foreach ($rawEntries as $rawEntry) {
            if (!is_array($rawEntry)) {
                continue;
            }
            $sectionKey = isset($rawEntry['SectionKey'])
                ? sanitize_text_field((string) $rawEntry['SectionKey'])
                : '';
            if ($sectionKey === '') {
                continue;
            }
            $json = isset($rawEntry['StateJson']) ? (string) $rawEntry['StateJson'] : '';
            $decoded = json_decode($json, true);
            $sections[$sectionKey] = LegoLayoutSpanModel::normalize(is_array($decoded) ? $decoded : []);
        }

        $store = get_option(self::OPTION, []);
        $store = is_array($store) ? $store : [];
        $store[$slug] = [
            'SchemaVersion' => LegoLayoutSpanModel::SCHEMA_VERSION,
            'SavedUtc' => gmdate('c'),
            'Sections' => $sections,
        ];
        update_option(self::OPTION, $store, false);
    }
}
