<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * Admin-only LEGO spacing foundation.
 *
 * The legacy page schema/public renderer remain authoritative. LEGO-specific
 * X/Y spacing is stored in a separate option keyed by page slug + section key,
 * so the feature can be proven in the editor before any public cutover.
 */
final class EditorLegoSpacingAdminController
{
    private const OPTION = 'hangar18_ultimate_designer_lego_spacing_v1';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        add_action('admin_enqueue_scripts', [self::class, 'enqueue']);
        // Run before the legacy save handler (default priority 10), which redirects.
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
        $jsPath = $pluginDir . '/assets/ultimate-designer-lego-spacing.js';
        $cssPath = $pluginDir . '/assets/ultimate-designer-lego-spacing.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-lego-spacing',
            $pluginUrl . 'assets/ultimate-designer-lego-spacing.js',
            ['jquery'],
            is_file($jsPath) ? (string) filemtime($jsPath) : '0.8.24',
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-lego-spacing',
            $pluginUrl . 'assets/ultimate-designer-lego-spacing.css',
            [],
            is_file($cssPath) ? (string) filemtime($cssPath) : '0.8.24'
        );

        $store = get_option(self::OPTION, []);
        wp_localize_script(
            'hangar18-ultimate-designer-lego-spacing',
            'H18LegoSpacing',
            [
                'version' => '0.8.24',
                'pages' => is_array($store) ? $store : [],
                'limits' => [
                    'desktop' => 160,
                    'mobile' => 120,
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

            $sections[$sectionKey] = [
                'MarginXPx' => self::clampInt($rawEntry['MarginXPx'] ?? 0, 0, 160),
                'MarginYPx' => self::clampInt($rawEntry['MarginYPx'] ?? 0, 0, 160),
                'MobileMarginXPx' => self::clampInt($rawEntry['MobileMarginXPx'] ?? 0, 0, 120),
                'MobileMarginYPx' => self::clampInt($rawEntry['MobileMarginYPx'] ?? 0, 0, 120),
                'GapXPx' => self::clampInt($rawEntry['GapXPx'] ?? 16, 0, 160),
                'GapYPx' => self::clampInt($rawEntry['GapYPx'] ?? 16, 0, 160),
                'MobileGapXPx' => self::clampInt($rawEntry['MobileGapXPx'] ?? 12, 0, 120),
                'MobileGapYPx' => self::clampInt($rawEntry['MobileGapYPx'] ?? 12, 0, 120),
            ];
        }

        $store = get_option(self::OPTION, []);
        if (!is_array($store)) {
            $store = [];
        }
        $store[$slug] = [
            'Version' => 1,
            'SavedUtc' => gmdate('c'),
            'Sections' => $sections,
        ];
        update_option(self::OPTION, $store, false);
    }

    private static function clampInt($value, int $min, int $max): int
    {
        $value = is_numeric($value) ? (int) $value : $min;
        return max($min, min($max, $value));
    }
}
