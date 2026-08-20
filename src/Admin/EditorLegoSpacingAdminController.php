<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Editor\LegoSpacingModel;

/**
 * Admin-only persistence bridge for the LEGO X/Y spacing foundation.
 *
 * Inspector controls edit one canonical hidden state field inside the existing
 * section row. The existing page-history engine therefore remains the only
 * Undo/Redo owner. Public rendering and legacy page schema are untouched.
 */
final class EditorLegoSpacingAdminController
{
    public const OPTION = 'hangar18_ultimate_designer_lego_spacing_v2';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        // Persist the additive overlay before the legacy page-save handler redirects.
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
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-spacing-v0830.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-spacing-v0830.css';

        /*
         * Header load is intentional. Its jQuery-ready callback is registered
         * before legacy admin.js takes the initial history snapshot, so the
         * canonical hidden state field is part of that single history model.
         */
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-spacing-v0830',
            $pluginUrl . 'assets/ultimate-designer-lego-spacing-v0830.js',
            ['jquery', 'hangar18-ultimate-designer-history-content-v0823'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.30',
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-spacing-v0830',
            $pluginUrl . 'assets/ultimate-designer-lego-spacing-v0830.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.30'
        );

        $store = get_option(self::OPTION, []);
        wp_localize_script(
            'hangar18-ultimate-designer-lego-spacing-v0830',
            'H18LegoSpacingV0830',
            [
                'version' => '0.8.30',
                'schemaVersion' => LegoSpacingModel::SCHEMA_VERSION,
                'pages' => is_array($store) ? $store : [],
                'limits' => [
                    'desktop' => LegoSpacingModel::DESKTOP_MAX,
                    'mobile' => LegoSpacingModel::MOBILE_MAX,
                ],
            ]
        );
    }

    public static function captureSave(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        check_admin_referer('h18_save_page_editor');

        if (!isset($_POST['h18_lego_spacing']) || !is_array($_POST['h18_lego_spacing'])) {
            return;
        }

        $slug = isset($_POST['page_slug'])
            ? sanitize_title((string) wp_unslash($_POST['page_slug']))
            : '';
        if ($slug === '') {
            return;
        }

        $rawEntries = wp_unslash($_POST['h18_lego_spacing']);
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
            $decoded = is_array($decoded) ? $decoded : [];
            $legacy = [
                'LayoutGapPx' => $rawEntry['LegacyLayoutGapPx'] ?? 16,
                'MobileLayoutGapPx' => $rawEntry['LegacyMobileLayoutGapPx'] ?? 12,
            ];
            $sections[$sectionKey] = LegoSpacingModel::normalize($decoded, $legacy);
        }

        $store = get_option(self::OPTION, []);
        $store = is_array($store) ? $store : [];
        $store[$slug] = [
            'SchemaVersion' => LegoSpacingModel::SCHEMA_VERSION,
            'SavedUtc' => gmdate('c'),
            'Sections' => $sections,
        ];
        update_option(self::OPTION, $store, false);
    }
}
