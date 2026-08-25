<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Frontend;

/** Public parity for persisted v0.9.1 physical 120-unit geometry. */
final class PhysicalCanvasFrontendRuntime
{
    private const LAYOUT_OPTION = 'hangar18_ultimate_designer_layout_model_v0900';
    private const UNITS = 120;
    private const ROW_PX = 8;

    public static function register(): void
    {
        add_action('wp_head', [self::class, 'renderCss'], 1004);
    }

    public static function renderCss(): void
    {
        if (!is_singular('page')) {
            return;
        }
        $page = get_queried_object();
        if (!$page instanceof \WP_Post) {
            return;
        }
        $slug = sanitize_title((string) $page->post_name);
        if ($slug === '') {
            return;
        }

        $store = get_option(self::LAYOUT_OPTION, []);
        $pageState = is_array($store) && isset($store[$slug]) && is_array($store[$slug])
            ? $store[$slug]
            : [];
        $sections = isset($pageState['Sections']) && is_array($pageState['Sections'])
            ? $pageState['Sections']
            : [];
        if (!$sections) {
            return;
        }

        $byKey = [];
        $children = [];
        foreach ($sections as $rawKey => $section) {
            if (!is_array($section) || !empty($section['Removed'])) {
                continue;
            }
            $key = sanitize_key((string) ($section['Key'] ?? $rawKey));
            if ($key === '') {
                continue;
            }
            $byKey[$key] = $section;
            $parent = sanitize_key((string) ($section['ParentKey'] ?? $section['LayoutParentKey'] ?? ''));
            $children[$parent][] = $key;
        }

        $desktop = [];
        $tablet = [];
        $mobile = [];
        self::appendDeviceRules($desktop, $byKey, $children, 'Desktop');
        self::appendDeviceRules($tablet, $byKey, $children, 'Tablet');
        self::appendDeviceRules($mobile, $byKey, $children, 'Mobile');
        if (!$desktop && !$tablet && !$mobile) {
            return;
        }

        echo "\n<style id=\"h18-physical-canvas-parity-v0901\">\n";
        echo implode("\n", $desktop);
        if ($tablet) {
            echo "\n@media (max-width:1100px) and (min-width:783px){\n" . implode("\n", $tablet) . "\n}";
        }
        if ($mobile) {
            echo "\n@media (max-width:782px){\n" . implode("\n", $mobile) . "\n}";
        }
        echo "\n</style>\n";
    }

    /**
     * @param array<int,string> $rules
     * @param array<string,array<string,mixed>> $byKey
     * @param array<string,array<int,string>> $children
     */
    private static function appendDeviceRules(array &$rules, array $byKey, array $children, string $device): void
    {
        foreach ($children as $parentKey => $childKeys) {
            $explicit = [];
            foreach ($childKeys as $key) {
                if (!isset($byKey[$key])) {
                    continue;
                }
                $geo = self::deviceGeometry($byKey[$key]['Geometry'] ?? [], $device);
                if ($geo !== null && !empty($geo['Explicit'])) {
                    $explicit[$key] = $geo;
                }
            }
            if (!$explicit) {
                continue;
            }

            if ($parentKey !== '' && isset($byKey[$parentKey])) {
                $parentType = sanitize_key((string) ($byKey[$parentKey]['Type'] ?? ''));
                if (in_array($parentType, ['container', 'grid', 'flex'], true)) {
                    $parentSelector = '#h18-section-' . sanitize_html_class($parentKey) . '>.h18-layout-children';
                    $rules[] = $parentSelector . '{display:grid!important;grid-template-columns:repeat(' . self::UNITS . ',minmax(0,1fr))!important;column-gap:0!important;align-items:start!important}';
                }
            }

            foreach ($explicit as $key => $geo) {
                $selector = '#h18-section-' . sanitize_html_class($key);
                $x = max(0, min(self::UNITS - 1, (int) $geo['X']));
                $w = max(1, min(self::UNITS - $x, (int) $geo['W']));
                $y = max(-4000, min(10000, (int) $geo['Y']));
                $h = max(0, min(4000, (int) $geo['H']));

                if ($parentKey === '') {
                    $percent = round(($w / self::UNITS) * 100, 6);
                    $left = round(($x / self::UNITS) * 100, 6);
                    $rule = $selector . '{box-sizing:border-box!important;width:' . $percent . '%!important;max-width:none!important;margin-left:' . $left . '%!important;margin-right:0!important;';
                } else {
                    $rule = $selector . '{box-sizing:border-box!important;grid-column:' . ($x + 1) . '/span ' . $w . '!important;width:auto!important;max-width:none!important;';
                }
                if ($y !== 0) {
                    $rule .= 'margin-top:' . ($y * self::ROW_PX) . 'px!important;';
                }
                if ($h > 0) {
                    $rule .= 'height:' . ($h * self::ROW_PX) . 'px!important;min-height:' . ($h * self::ROW_PX) . 'px!important;';
                }
                $rule .= '}';
                $rules[] = $rule;
            }
        }
    }

    /** @param mixed $raw @return array<string,mixed>|null */
    private static function deviceGeometry($raw, string $device): ?array
    {
        if (!is_array($raw)) {
            return null;
        }
        $desktop = isset($raw['Desktop']) && is_array($raw['Desktop']) ? $raw['Desktop'] : null;
        if ($desktop === null) {
            return null;
        }
        if ($device === 'Desktop') {
            return $desktop;
        }
        $branch = isset($raw[$device]) && is_array($raw[$device]) ? $raw[$device] : [];
        $inherit = array_key_exists('InheritDesktop', $branch)
            ? self::boolValue($branch['InheritDesktop'], true)
            : true;
        return $inherit ? $desktop : $branch;
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
}
