<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

/** v0.9.0 canonical editor layout state and compatibility projection. */
final class EditorLayoutEngineAdminController
{
    public const VERSION = '0.9.0';
    public const SCHEMA = 1;
    public const OPTION = 'hangar18_ultimate_designer_layout_model_v0900';
    private static bool $registered = false;

    public static function register(): void
    {
        if (self::$registered) { return; }
        self::$registered = true;
        add_action('admin_post_h18_save_page_editor', [self::class, 'captureSave'], 4);
        add_action('admin_enqueue_scripts', [self::class, 'enqueue'], 140);
    }

    public static function enqueue(): void
    {
        $page = isset($_GET['page']) ? sanitize_key((string) wp_unslash($_GET['page'])) : '';
        if ($page !== 'hangar18-pages' || !current_user_can('edit_pages')) { return; }

        $dir = dirname(__DIR__, 2);
        $url = plugin_dir_url($dir . '/hangar18-manager.php');
        $js = $dir . '/assets/ultimate-designer-layout-engine-v0900.js';
        $css = $dir . '/assets/ultimate-designer-layout-engine-v0900.css';

        wp_enqueue_script(
            'hangar18-ultimate-designer-layout-engine-v0900',
            $url . 'assets/ultimate-designer-layout-engine-v0900.js',
            [
                'jquery',
                'hangar18-ultimate-designer-lego-resize-v0841',
                'hangar18-ultimate-designer-lego-fixes-v0851',
                'hangar18-ultimate-designer-lego-placement-stability-v0862',
                'hangar18-ultimate-designer-lego-inspector-only-v0847',
            ],
            is_file($js) ? (string) filemtime($js) : self::VERSION,
            false
        );
        wp_enqueue_style(
            'hangar18-ultimate-designer-layout-engine-v0900',
            $url . 'assets/ultimate-designer-layout-engine-v0900.css',
            ['hangar18-ultimate-designer-lego-fixes-v0851'],
            is_file($css) ? (string) filemtime($css) : self::VERSION
        );

        $store = get_option(self::OPTION, []);
        wp_localize_script('hangar18-ultimate-designer-layout-engine-v0900', 'H18LayoutEngineV0900', [
            'version' => self::VERSION,
            'schemaVersion' => self::SCHEMA,
            'pages' => is_array($store) ? $store : [],
        ]);
    }

    public static function captureSave(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        if (!isset($_POST['_wpnonce']) || !wp_verify_nonce(sanitize_text_field((string) wp_unslash($_POST['_wpnonce'])), 'h18_save_page_editor')) { return; }
        if (!isset($_POST['h18_layout_model_v0900']) || !is_string($_POST['h18_layout_model_v0900'])) { return; }

        $slug = isset($_POST['page_slug']) ? sanitize_title((string) wp_unslash($_POST['page_slug'])) : '';
        $raw = json_decode((string) wp_unslash($_POST['h18_layout_model_v0900']), true);
        if ($slug === '' || !is_array($raw)) { return; }
        $model = self::normalizeModel($raw, $slug);
        if ($model === null) { return; }

        $posted = isset($_POST['sections']) && is_array($_POST['sections']) ? wp_unslash($_POST['sections']) : [];
        if (!self::sameKeySet($model['Sections'], $posted)) { return; }

        self::projectSections($model['Sections'], $posted);
        self::projectLegacyState($model['Sections']);

        $store = get_option(self::OPTION, []);
        $store = is_array($store) ? $store : [];
        $store[$slug] = [
            'SchemaVersion' => self::SCHEMA,
            'EngineVersion' => self::VERSION,
            'SavedUtc' => gmdate('c'),
            'Sections' => $model['Sections'],
        ];
        update_option(self::OPTION, $store, false);
    }

    private static function normalizeModel(array $raw, string $slug): ?array
    {
        if ((int) ($raw['schemaVersion'] ?? 0) !== self::SCHEMA || sanitize_title((string) ($raw['pageSlug'] ?? '')) !== $slug) { return null; }
        if (!isset($raw['sections']) || !is_array($raw['sections']) || count($raw['sections']) > 25) { return null; }

        $sections = [];
        foreach ($raw['sections'] as $i => $item) {
            if (!is_array($item)) { return null; }
            $key = sanitize_key((string) ($item['key'] ?? ''));
            if ($key === '' || isset($sections[$key])) { return null; }
            $sections[$key] = [
                'Key' => $key,
                'Type' => sanitize_key((string) ($item['type'] ?? 'text')),
                'ParentKey' => sanitize_key((string) ($item['parentKey'] ?? '')),
                'Order' => self::clamp($item['order'] ?? (($i + 1) * 10), 1, 10000, ($i + 1) * 10),
                'Removed' => !empty($item['removed']),
                'Span' => self::span(is_array($item['span'] ?? null) ? $item['span'] : []),
                'Stack' => self::stack(is_array($item['stack'] ?? null) ? $item['stack'] : [], $key),
            ];
        }
        self::validateHierarchy($sections);
        return ['Sections' => $sections];
    }

    private static function validateHierarchy(array &$sections): void
    {
        $parents = ['container', 'flex', 'grid'];
        foreach ($sections as $key => &$section) {
            $parent = $section['ParentKey'];
            if ($parent === '' || $parent === $key || !isset($sections[$parent]) || !in_array($sections[$parent]['Type'], $parents, true) || $sections[$parent]['Removed']) {
                $section['ParentKey'] = '';
            }
        }
        unset($section);

        foreach (array_keys($sections) as $start) {
            $seen = [];
            $cursor = $start;
            while ($cursor !== '' && isset($sections[$cursor])) {
                if (isset($seen[$cursor])) { $sections[$cursor]['ParentKey'] = ''; break; }
                $seen[$cursor] = true;
                $cursor = (string) $sections[$cursor]['ParentKey'];
            }
        }

        foreach ($sections as $key => &$section) {
            $root = (string) $section['Stack']['StackRootKey'];
            if ($root === '' || $root === $key || !isset($sections[$root]) || $sections[$root]['Removed'] || $sections[$root]['ParentKey'] !== $section['ParentKey']) {
                $section['Stack']['StackRootKey'] = '';
                $section['Stack']['StackOrder'] = 0;
            }
        }
        unset($section);
    }

    private static function sameKeySet(array $model, array $posted): bool
    {
        $keys = [];
        foreach (array_slice($posted, 0, 25) as $row) {
            if (!is_array($row)) { return false; }
            $key = sanitize_key((string) ($row['Key'] ?? ''));
            if ($key === '' || isset($keys[$key])) { return false; }
            $keys[$key] = true;
        }
        $modelKeys = array_fill_keys(array_keys($model), true);
        ksort($keys); ksort($modelKeys);
        return $keys === $modelKeys;
    }

    private static function projectSections(array $model, array $posted): void
    {
        foreach ($posted as $index => $row) {
            if (!is_array($row)) { continue; }
            $key = sanitize_key((string) ($row['Key'] ?? ''));
            if (!isset($model[$key])) { continue; }
            $state = $model[$key];
            $_POST['sections'][$index]['Remove'] = $state['Removed'] ? '1' : '0';
            $_POST['sections'][$index]['LayoutParentKey'] = $state['ParentKey'];
            $_POST['sections'][$index]['Order'] = (string) $state['Order'];
        }
    }

    private static function projectLegacyState(array $model): void
    {
        $_POST['h18_lego_layout_span'] = [];
        $_POST['h18_lego_stack_v0851'] = [];
        $i = 0;
        foreach ($model as $key => $state) {
            if ($state['Removed']) { continue; }
            $_POST['h18_lego_layout_span'][$i] = ['SectionKey' => $key, 'StateJson' => wp_json_encode($state['Span'])];
            $_POST['h18_lego_stack_v0851'][$i] = ['SectionKey' => $key, 'StateJson' => wp_json_encode($state['Stack'])];
            $i++;
        }
    }

    private static function span(array $raw): array
    {
        $desktop = is_array($raw['Desktop'] ?? null) ? $raw['Desktop'] : [];
        $tablet = is_array($raw['Tablet'] ?? null) ? $raw['Tablet'] : [];
        $mobile = is_array($raw['Mobile'] ?? null) ? $raw['Mobile'] : [];
        return [
            'SchemaVersion' => 2,
            'Desktop' => ['Span' => self::clamp($desktop['Span'] ?? 0, 0, 12, 0)],
            'Tablet' => self::responsiveSpan($tablet),
            'Mobile' => self::responsiveSpan($mobile),
        ];
    }

    private static function responsiveSpan(array $raw): array
    {
        $inherit = array_key_exists('InheritDesktop', $raw) ? self::bool($raw['InheritDesktop'], true) : true;
        $span = self::clamp($raw['Span'] ?? 0, 0, 12, 0);
        return [
            'InheritDesktop' => $inherit,
            'HasOverride' => array_key_exists('HasOverride', $raw) ? self::bool($raw['HasOverride'], !$inherit) : (!$inherit || $span > 0),
            'Span' => $span,
        ];
    }

    private static function stack(array $raw, string $key): array
    {
        $root = sanitize_key((string) ($raw['StackRootKey'] ?? ''));
        if ($root === $key) { $root = ''; }
        return [
            'SchemaVersion' => 1,
            'StackRootKey' => $root,
            'StackOrder' => max(0, (int) ($raw['StackOrder'] ?? 0)),
            'DesktopPercent' => self::percent($raw['DesktopPercent'] ?? 0),
            'TabletPercent' => self::percent($raw['TabletPercent'] ?? 0),
            'MobilePercent' => self::percent($raw['MobilePercent'] ?? 0),
        ];
    }

    private static function percent($value): int
    {
        if (!is_numeric($value) || (int) $value <= 0) { return 0; }
        return max(10, min(90, (int) $value));
    }

    private static function bool($value, bool $fallback): bool
    {
        if (is_bool($value)) { return $value; }
        if ($value === null || $value === '') { return $fallback; }
        return in_array(strtolower(trim((string) $value)), ['1', 'true', 'yes', 'on'], true);
    }

    private static function clamp($value, int $min, int $max, int $fallback): int
    {
        if (!is_numeric($value)) { return $fallback; }
        return max($min, min($max, (int) $value));
    }
}
