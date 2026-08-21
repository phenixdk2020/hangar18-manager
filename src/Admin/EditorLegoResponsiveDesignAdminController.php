<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Editor\LegoDesignModel;
use Hangar18\UltimateDesigner\Editor\LegoResponsiveDesignModel;

/** Admin-only persistence bridge for Tablet/Mobile LEGO design overrides. */
final class EditorLegoResponsiveDesignAdminController
{
    public const OPTION = 'hangar18_ultimate_designer_lego_design_responsive_v1';
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
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-design-responsive-v0833.js';
        $guardPath = $pluginDir . '/assets/ultimate-designer-lego-design-responsive-event-guard-v0833.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-design-responsive-v0833.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-design-responsive-event-guard-v0833',
            $pluginUrl . 'assets/ultimate-designer-lego-design-responsive-event-guard-v0833.js',
            [
                'jquery',
                'hangar18-ultimate-designer-lego-design-event-guard-v0832',
            ],
            is_file($guardPath) ? (string) filemtime($guardPath) : '0.8.33',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-design-responsive-v0833',
            $pluginUrl . 'assets/ultimate-designer-lego-design-responsive-v0833.js',
            [
                'jquery',
                'hangar18-ultimate-designer-history-content-v0823',
                'hangar18-ultimate-designer-lego-spacing-v0831',
                'hangar18-ultimate-designer-lego-design-v0832',
                'hangar18-ultimate-designer-lego-design-responsive-event-guard-v0833',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.33',
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-design-responsive-v0833',
            $pluginUrl . 'assets/ultimate-designer-lego-design-responsive-v0833.css',
            ['hangar18-ultimate-designer-lego-design-v0832'],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.33'
        );

        $store = get_option(self::OPTION, []);
        wp_localize_script(
            'hangar18-ultimate-designer-lego-design-responsive-v0833',
            'H18LegoResponsiveDesignV0833',
            [
                'version' => '0.8.33',
                'schemaVersion' => LegoResponsiveDesignModel::SCHEMA_VERSION,
                'pages' => is_array($store) ? $store : [],
                'fieldMap' => LegoDesignModel::legacyFieldMap(),
                'fonts' => LegoDesignModel::fonts(),
                'shadows' => LegoDesignModel::shadows(),
                'hoverEffects' => LegoDesignModel::hoverEffects(),
            ]
        );
    }

    public static function captureSave(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        check_admin_referer('h18_save_page_editor');
        if (!isset($_POST['h18_lego_responsive_design']) || !is_array($_POST['h18_lego_responsive_design'])) {
            return;
        }

        $slug = isset($_POST['page_slug'])
            ? sanitize_title((string) wp_unslash($_POST['page_slug']))
            : '';
        if ($slug === '') {
            return;
        }

        $sections = [];
        foreach (wp_unslash($_POST['h18_lego_responsive_design']) as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $key = isset($entry['SectionKey']) ? sanitize_text_field((string)$entry['SectionKey']) : '';
            $json = isset($entry['StateJson']) ? (string)$entry['StateJson'] : '';
            if ($key === '' || $json === '') {
                continue;
            }
            $decoded = json_decode($json, true);
            if (!is_array($decoded)) {
                continue;
            }
            // Device payloads are self-contained normalized override snapshots.
            // Desktop remains legacy-backed and is therefore not duplicated here.
            $sections[$key] = LegoResponsiveDesignModel::normalize($decoded, LegoDesignModel::defaults());
        }

        $store = get_option(self::OPTION, []);
        $store = is_array($store) ? $store : [];
        $store[$slug] = [
            'SchemaVersion' => LegoResponsiveDesignModel::SCHEMA_VERSION,
            'SavedUtc' => gmdate('c'),
            'Sections' => $sections,
        ];
        update_option(self::OPTION, $store, false);
    }
}
