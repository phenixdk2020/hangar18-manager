<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/**
 * v0.9.1 physical canvas interaction/persistence bridge.
 *
 * The v0.9.0 layout engine remains the canonical owner for SectionKey,
 * ParentKey, Order, Removed, Span and Stack. This controller merges physical
 * geometry into the same per-page layout option after the base save projection
 * has completed, and loads the interaction runtime after the canonical engine.
 */
final class EditorPhysicalCanvasAdminController
{
    public const VERSION = '0.9.1';
    public const GEOMETRY_SCHEMA = 1;
    public const LAYOUT_OPTION = 'hangar18_ultimate_designer_layout_model_v0900';
    public const FIELD = 'h18_layout_geometry_v0901';
    public const HORIZONTAL_UNITS = 120;
    public const ROW_PX = 8;

    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) {
            return;
        }
        self::$registered = true;

        // Base v0.9.0 model writes at priority 4. Geometry is merged into that
        // same option immediately afterwards, before the legacy page saver.
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 5);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 145);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) {
            return;
        }

        $dir = dirname(__DIR__, 2);
        $url = plugin_dir_url($dir . '/hangar18-manager.php');
        $js = $dir . '/assets/ultimate-designer-physical-canvas-v0901.js';
        $css = $dir . '/assets/ultimate-designer-physical-canvas-v0901.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-physical-canvas-v0901',
            $url . 'assets/ultimate-designer-physical-canvas-v0901.js',
            ['jquery', 'hangar18-ultimate-designer-layout-engine-v0900'],
            is_file($js) ? (string) filemtime($js) : self::VERSION,
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-physical-canvas-v0901',
            $url . 'assets/ultimate-designer-physical-canvas-v0901.css',
            ['hangar18-ultimate-designer-layout-engine-v0900'],
            is_file($css) ? (string) filemtime($css) : self::VERSION
        );

        $store = get_option(self::LAYOUT_OPTION, []);
        $pages = [];
        if (is_array($store)) {
            foreach ($store as $slug => $pageState) {
                if (!is_array($pageState) || !isset($pageState['Sections']) || !is_array($pageState['Sections'])) {
                    continue;
                }
                $pageGeometry = [];
                foreach ($pageState['Sections'] as $key => $section) {
                    if (!is_array($section) || !isset($section['Geometry']) || !is_array($section['Geometry'])) {
                        continue;
                    }
                    $safeKey = sanitize_key((string) $key);
                    if ($safeKey !== '') {
                        $pageGeometry[$safeKey] = $section['Geometry'];
                    }
                }
                if ($pageGeometry) {
                    $pages[sanitize_title((string) $slug)] = $pageGeometry;
                }
            }
        }

        wp_localize_script(
            'hangar18-ultimate-designer-physical-canvas-v0901',
            'H18PhysicalCanvasV0901',
            [
                'version' => self::VERSION,
                'schemaVersion' => self::GEOMETRY_SCHEMA,
                'horizontalUnits' => self::HORIZONTAL_UNITS,
                'rowPx' => self::ROW_PX,
                'pages' => $pages,
            ]
        );
    }

    public static function captureSave(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        if (
            !isset($_POST['_wpnonce']) ||
            !wp_verify_nonce(
                sanitize_text_field((string) wp_unslash($_POST['_wpnonce'])),
                'h18_save_page_editor'
            )
        ) {
            return;
        }
        if (!isset($_POST[self::FIELD]) || !is_string($_POST[self::FIELD])) {
            return;
        }

        $slug = isset($_POST['page_slug'])
            ? sanitize_title((string) wp_unslash($_POST['page_slug']))
            : '';
        if ($slug === '') {
            return;
        }

        $decoded = json_decode((string) wp_unslash($_POST[self::FIELD]), true);
        if (!is_array($decoded)) {
            return;
        }
        if ((int) ($decoded['schemaVersion'] ?? 0) !== self::GEOMETRY_SCHEMA) {
            return;
        }
        if (sanitize_title((string) ($decoded['pageSlug'] ?? '')) !== $slug) {
            return;
        }
        if (!isset($decoded['sections']) || !is_array($decoded['sections']) || count($decoded['sections']) > 100) {
            return;
        }

        $store = get_option(self::LAYOUT_OPTION, []);
        if (!is_array($store) || !isset($store[$slug]) || !is_array($store[$slug])) {
            return;
        }
        if (!isset($store[$slug]['Sections']) || !is_array($store[$slug]['Sections'])) {
            return;
        }

        foreach ($decoded['sections'] as $rawKey => $rawGeometry) {
            $key = sanitize_key((string) $rawKey);
            if ($key === '' || !isset($store[$slug]['Sections'][$key]) || !is_array($rawGeometry)) {
                continue;
            }
            $store[$slug]['Sections'][$key]['Geometry'] = self::normalizeGeometry($rawGeometry);
        }

        $store[$slug]['GeometrySchemaVersion'] = self::GEOMETRY_SCHEMA;
        $store[$slug]['CanvasHorizontalUnits'] = self::HORIZONTAL_UNITS;
        $store[$slug]['CanvasRowPx'] = self::ROW_PX;
        $store[$slug]['GeometrySavedUtc'] = gmdate('c');
        update_option(self::LAYOUT_OPTION, $store, false);
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function normalizeGeometry(array $raw): array
    {
        return [
            'SchemaVersion' => self::GEOMETRY_SCHEMA,
            'Desktop' => self::normalizeDevice(
                isset($raw['Desktop']) && is_array($raw['Desktop']) ? $raw['Desktop'] : [],
                false
            ),
            'Tablet' => self::normalizeDevice(
                isset($raw['Tablet']) && is_array($raw['Tablet']) ? $raw['Tablet'] : [],
                true
            ),
            'Mobile' => self::normalizeDevice(
                isset($raw['Mobile']) && is_array($raw['Mobile']) ? $raw['Mobile'] : [],
                true
            ),
        ];
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function normalizeDevice(array $raw, bool $responsive): array
    {
        $x = self::clamp($raw['X'] ?? 0, 0, self::HORIZONTAL_UNITS - 1, 0);
        $width = self::clamp($raw['W'] ?? self::HORIZONTAL_UNITS, 1, self::HORIZONTAL_UNITS, self::HORIZONTAL_UNITS);
        if ($x + $width > self::HORIZONTAL_UNITS) {
            $width = self::HORIZONTAL_UNITS - $x;
        }

        $device = [
            'Explicit' => self::boolValue($raw['Explicit'] ?? false, false),
            'X' => $x,
            'Y' => self::clamp($raw['Y'] ?? 0, 0, 10000, 0),
            'W' => max(1, $width),
            // H=0 means natural/auto height until the user performs a vertical resize.
            'H' => self::clamp($raw['H'] ?? 0, 0, 4000, 0),
        ];

        if ($responsive) {
            $device['InheritDesktop'] = self::boolValue($raw['InheritDesktop'] ?? true, true);
            $device['HasOverride'] = self::boolValue($raw['HasOverride'] ?? false, false);
        }
        return $device;
    }

    /** @param mixed $value */
    private static function boolValue($value, bool $fallback): bool
    {
        if (is_bool($value)) {
            return $value;
        }
        if ($value === null || $value === '') {
            return $fallback;
        }
        if (is_numeric($value)) {
            return ((int) $value) !== 0;
        }
        return in_array(strtolower(trim((string) $value)), ['1', 'true', 'yes', 'on'], true);
    }

    /** @param mixed $value */
    private static function clamp($value, int $min, int $max, int $fallback): int
    {
        if (!is_numeric($value)) {
            return $fallback;
        }
        return max($min, min($max, (int) $value));
    }
}
