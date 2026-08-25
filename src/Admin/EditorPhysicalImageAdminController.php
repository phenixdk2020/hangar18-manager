<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * v0.9.3 physical image-box bridge.
 *
 * Pure Image elements use the v0.9.1 physical geometry as their authoritative
 * box. This controller persists only image fitting metadata in the same
 * canonical per-page layout option; it does not own geometry or page content.
 */
final class EditorPhysicalImageAdminController
{
    public const VERSION = '0.9.3';
    public const SCHEMA = 1;
    public const LAYOUT_OPTION = 'hangar18_ultimate_designer_layout_model_v0900';

    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        // v0.9.0 canonical state = 4, v0.9.1 geometry = 5,
        // v0.9.2 projected diagnostics = 6. Image metadata is merged at 7.
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 7);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 155);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $dir = dirname(__DIR__, 2);
        $url = plugin_dir_url($dir . '/hangar18-manager.php');
        $js = $dir . '/assets/ultimate-designer-physical-image-v0903.js';
        $css = $dir . '/assets/ultimate-designer-physical-image-v0903.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-physical-image-v0903',
            $url . 'assets/ultimate-designer-physical-image-v0903.js',
            ['jquery', 'hangar18-ultimate-designer-physical-canvas-v0901'],
            is_file($js) ? (string) filemtime($js) : self::VERSION,
            true
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-physical-image-v0903',
            $url . 'assets/ultimate-designer-physical-image-v0903.css',
            ['hangar18-ultimate-designer-physical-canvas-v0901'],
            is_file($css) ? (string) filemtime($css) : self::VERSION
        );

        $pages = [];
        $store = get_option(self::LAYOUT_OPTION, []);
        if (is_array($store)) {
            foreach ($store as $slug => $pageState) {
                if (!is_array($pageState) || !isset($pageState['Sections']) || !is_array($pageState['Sections'])) {
                    continue;
                }
                $imageState = [];
                foreach ($pageState['Sections'] as $rawKey => $section) {
                    if (!is_array($section) || sanitize_key((string) ($section['Type'] ?? '')) !== 'image') {
                        continue;
                    }
                    $key = sanitize_key((string) ($section['Key'] ?? $rawKey));
                    if ($key === '') {
                        continue;
                    }
                    if (isset($section['PhysicalImage']) && is_array($section['PhysicalImage'])) {
                        $imageState[$key] = self::normalizeImage($section['PhysicalImage']);
                    }
                }
                if ($imageState) {
                    $pages[sanitize_title((string) $slug)] = $imageState;
                }
            }
        }

        wp_localize_script(
            'hangar18-ultimate-designer-physical-image-v0903',
            'H18PhysicalImageV0903',
            [
                'version' => self::VERSION,
                'schemaVersion' => self::SCHEMA,
                'defaultMode' => 'Cover',
                'pages' => $pages,
            ]
        );
    }

    public static function captureSave(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        $nonce = isset($_POST['_wpnonce'])
            ? sanitize_text_field((string) wp_unslash($_POST['_wpnonce']))
            : '';
        if ($nonce === '' || !wp_verify_nonce($nonce, 'h18_save_page_editor')) {
            return;
        }

        $slug = isset($_POST['page_slug'])
            ? sanitize_title((string) wp_unslash($_POST['page_slug']))
            : '';
        $posted = isset($_POST['sections']) && is_array($_POST['sections'])
            ? wp_unslash($_POST['sections'])
            : [];
        if ($slug === '' || !$posted || count($posted) > 200) {
            return;
        }

        $store = get_option(self::LAYOUT_OPTION, []);
        if (!is_array($store) || !isset($store[$slug]) || !is_array($store[$slug])) {
            return;
        }
        if (!isset($store[$slug]['Sections']) || !is_array($store[$slug]['Sections'])) {
            return;
        }

        foreach ($posted as $row) {
            if (!is_array($row)) {
                continue;
            }
            $key = sanitize_key((string) ($row['Key'] ?? ''));
            $type = sanitize_key((string) ($row['Type'] ?? ''));
            if ($key === '' || $type !== 'image' || !isset($store[$slug]['Sections'][$key])) {
                continue;
            }

            // Read the raw posted value before the legacy section normalizer.
            // Stretch is intentionally a v0.9.3 physical-box mode and is kept
            // outside the legacy Page Editor ImageFit enum.
            $mode = self::mode($row['ImageFit'] ?? 'Cover');
            $store[$slug]['Sections'][$key]['PhysicalImage'] = self::normalizeImage([
                'Mode' => $mode,
                'FocalX' => $row['ImageFocalXPercent'] ?? 50,
                'FocalY' => $row['ImageFocalYPercent'] ?? 50,
            ]);
        }

        $store[$slug]['PhysicalImageSchemaVersion'] = self::SCHEMA;
        $store[$slug]['PhysicalImageEngineVersion'] = self::VERSION;
        $store[$slug]['PhysicalImageSavedUtc'] = gmdate('c');
        update_option(self::LAYOUT_OPTION, $store, false);
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function normalizeImage(array $raw): array
    {
        return [
            'SchemaVersion' => self::SCHEMA,
            'Mode' => self::mode($raw['Mode'] ?? 'Cover'),
            'FocalX' => self::percent($raw['FocalX'] ?? 50),
            'FocalY' => self::percent($raw['FocalY'] ?? 50),
        ];
    }

    /** @param mixed $value */
    private static function mode($value): string
    {
        $mode = ucfirst(strtolower(trim((string) $value)));
        return in_array($mode, ['Cover', 'Contain', 'Stretch'], true) ? $mode : 'Cover';
    }

    /** @param mixed $value */
    private static function percent($value): int
    {
        if (!is_numeric($value)) {
            return 50;
        }
        return max(0, min(100, (int) $value));
    }
}
