<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Editor\LegoDesignModel;

/**
 * Admin-only bridge for the v0.8.32 common element/Kasse design model.
 *
 * There is intentionally no save hook and no new option. The runtime reads and
 * writes the already-persisted page section fields, so legacy save/public render
 * remains authoritative while the editor gains one canonical design vocabulary.
 */
final class EditorLegoDesignAdminController
{
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;
        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        EditorLegoResponsiveDesignAdminController::register();
        // v0.8.36 is a view/proxy only. It registers after the complete
        // responsive + interaction stack and owns no save/history domain.
        EditorLegoPrimaryViewAdminController::register();
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $pluginDir = dirname(__DIR__, 2);
        $pluginUrl = plugin_dir_url($pluginDir . '/hangar18-manager.php');
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-design-v0832.js';
        $guardPath = $pluginDir . '/assets/ultimate-designer-lego-design-event-guard-v0832.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-design-v0832.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-design-v0832',
            $pluginUrl . 'assets/ultimate-designer-lego-design-v0832.js',
            [
                'jquery',
                'hangar18-ultimate-designer-history-content-v0823',
                'hangar18-ultimate-designer-lego-spacing-v0831',
            ],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.32',
            false
        );
        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-design-event-guard-v0832',
            $pluginUrl . 'assets/ultimate-designer-lego-design-event-guard-v0832.js',
            ['hangar18-ultimate-designer-lego-design-v0832'],
            is_file($guardPath) ? (string) filemtime($guardPath) : '0.8.32',
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-design-v0832',
            $pluginUrl . 'assets/ultimate-designer-lego-design-v0832.css',
            ['hangar18-ultimate-designer-lego-spacing-v0831'],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.32'
        );

        wp_localize_script(
            'hangar18-ultimate-designer-lego-design-v0832',
            'H18LegoDesignV0832',
            [
                'version' => '0.8.32',
                'schemaVersion' => LegoDesignModel::SCHEMA_VERSION,
                'fieldMap' => LegoDesignModel::legacyFieldMap(),
                'fonts' => LegoDesignModel::fonts(),
                'shadows' => LegoDesignModel::shadows(),
                'hoverEffects' => LegoDesignModel::hoverEffects(),
            ]
        );
    }
}
