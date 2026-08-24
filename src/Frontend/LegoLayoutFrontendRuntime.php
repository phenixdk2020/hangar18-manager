<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Frontend;

/**
 * Public layout parity bridge for the LEGO 12-column state.
 *
 * The editor stores per-element spans independently of page-section data.
 * This runtime makes those spans authoritative for the public renderer too,
 * so editor, live preview and frontend use the same column geometry.
 * It owns no drag/drop, history or editor selection state.
 */
final class LegoLayoutFrontendRuntime
{
    private const PAGE_OPTION = 'hangar18_manager_pages_v1';
    private const SPAN_OPTION = 'hangar18_ultimate_designer_lego_layout_span_v1';
    private const PREVIEW_PREFIX = 'h18_live_preview_';
    private const COLUMN_COUNT = 12;

    /** @var array<string,mixed>|null */
    private static ?array $previewPayload = null;

    public static function register(): void
    {
        add_action('init', [self::class, 'bootstrapLivePreview'], 1);
        add_action('wp_head', [self::class, 'renderSpanCss'], 1001);
    }

    public static function bootstrapLivePreview(): void
    {
        $token = isset($_GET['h18_live_preview'])
            ? preg_replace('/[^a-f0-9]/i', '', (string) wp_unslash($_GET['h18_live_preview']))
            : '';
        if ($token === '' || !is_user_logged_in() || !current_user_can('edit_pages')) {
            return;
        }

        $payload = get_transient(self::PREVIEW_PREFIX . $token);
        if (!is_array($payload) || empty($payload['PageSlug']) || !isset($payload['PageData']) || !is_array($payload['PageData'])) {
            return;
        }
        self::$previewPayload = $payload;

        add_filter('pre_option_' . self::PAGE_OPTION, [self::class, 'previewPageStore'], 1, 3);
        add_filter('pre_option_' . self::SPAN_OPTION, [self::class, 'previewSpanStore'], 1, 3);
        add_action('send_headers', static function (): void {
            nocache_headers();
            header('X-Robots-Tag: noindex, nofollow, noarchive', true);
        }, 1);
    }

    /** @param mixed $pre @param mixed $default */
    public static function previewPageStore($pre, string $option, $default)
    {
        if (!is_array(self::$previewPayload)) {
            return $pre;
        }
        $slug = sanitize_title((string) self::$previewPayload['PageSlug']);
        return [$slug => (array) self::$previewPayload['PageData']];
    }

    /** @param mixed $pre @param mixed $default */
    public static function previewSpanStore($pre, string $option, $default)
    {
        if (!is_array(self::$previewPayload)) {
            return $pre;
        }
        $slug = sanitize_title((string) self::$previewPayload['PageSlug']);
        $sections = isset(self::$previewPayload['SpanSections']) && is_array(self::$previewPayload['SpanSections'])
            ? self::$previewPayload['SpanSections']
            : [];
        return [
            $slug => [
                'SchemaVersion' => 2,
                'SavedUtc' => gmdate('c'),
                'Sections' => $sections,
            ],
        ];
    }

    public static function renderSpanCss(): void
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

        $pageStore = get_option(self::PAGE_OPTION, []);
        $spanStore = get_option(self::SPAN_OPTION, []);
        $pageData = is_array($pageStore) && isset($pageStore[$slug]) && is_array($pageStore[$slug])
            ? $pageStore[$slug]
            : [];
        $spanSections = is_array($spanStore) && isset($spanStore[$slug]['Sections']) && is_array($spanStore[$slug]['Sections'])
            ? $spanStore[$slug]['Sections']
            : [];
        $sections = isset($pageData['Sections']) && is_array($pageData['Sections']) ? $pageData['Sections'] : [];
        if (!$sections || !$spanSections) {
            return;
        }

        $byKey = [];
        $childrenByParent = [];
        foreach ($sections as $section) {
            if (!is_array($section)) {
                continue;
            }
            $key = sanitize_key((string) ($section['Key'] ?? ''));
            if ($key === '') {
                continue;
            }
            $byKey[$key] = $section;
            $parent = sanitize_key((string) ($section['LayoutParentKey'] ?? ''));
            if ($parent !== '') {
                $childrenByParent[$parent][] = $key;
            }
        }

        $desktopRules = [];
        $tabletRules = [];
        $mobileRules = [];
        foreach ($childrenByParent as $parentKey => $childKeys) {
            if (!isset($byKey[$parentKey])) {
                continue;
            }
            $parentType = sanitize_key((string) ($byKey[$parentKey]['Type'] ?? ''));
            if (!in_array($parentType, ['grid', 'flex'], true)) {
                continue;
            }

            $desktop = self::resolveSpans($childKeys, $spanSections, 'Desktop');
            $tablet = self::resolveSpans($childKeys, $spanSections, 'Tablet');
            $mobile = self::resolveSpans($childKeys, $spanSections, 'Mobile');
            $parentSelector = '#h18-section-' . sanitize_html_class($parentKey) . '>.h18-layout-children';

            if ($parentType === 'grid') {
                $parentRule = $parentSelector . '{grid-template-columns:repeat(12,minmax(0,1fr))!important;align-items:stretch!important}';
                $desktopRules[] = $parentRule;
                $tabletRules[] = $parentRule;
                $mobileRules[] = $parentRule;
                self::appendGridChildRules($desktopRules, $childKeys, $desktop);
                self::appendGridChildRules($tabletRules, $childKeys, $tablet);
                self::appendGridChildRules($mobileRules, $childKeys, $mobile);
            } else {
                self::appendFlexChildRules($desktopRules, $childKeys, $desktop);
                self::appendFlexChildRules($tabletRules, $childKeys, $tablet);
                self::appendFlexChildRules($mobileRules, $childKeys, $mobile);
            }
        }

        if (!$desktopRules && !$tabletRules && !$mobileRules) {
            return;
        }

        echo "\n<style id=\"h18-lego-layout-parity-v0885\">\n";
        echo implode("\n", $desktopRules);
        if ($tabletRules) {
            echo "\n@media (max-width:1100px) and (min-width:783px){\n" . implode("\n", $tabletRules) . "\n}";
        }
        if ($mobileRules) {
            echo "\n@media (max-width:782px){\n" . implode("\n", $mobileRules) . "\n}";
        }
        echo "\n</style>\n";
    }

    /** @param array<int,string> $keys @param array<string,mixed> $states @return array<int,int> */
    private static function resolveSpans(array $keys, array $states, string $device): array
    {
        $explicit = [];
        foreach ($keys as $key) {
            $state = isset($states[$key]) && is_array($states[$key]) ? $states[$key] : [];
            $explicit[] = self::effectiveSpan($state, $device);
        }
        $count = count($explicit);
        if ($count === 0) {
            return [];
        }
        if ($count > self::COLUMN_COUNT) {
            return array_fill(0, $count, 1);
        }
        if (count(array_filter($explicit, static fn(int $span): bool => $span > 0)) === 0) {
            return self::distribute(self::COLUMN_COUNT, $count);
        }

        $autoIndexes = [];
        $explicitIndexes = [];
        foreach ($explicit as $index => $span) {
            if ($span > 0) {
                $explicitIndexes[] = $index;
            } else {
                $autoIndexes[] = $index;
            }
        }
        $result = array_fill(0, $count, 0);
        $explicitValues = array_map(static fn(int $index): int => $explicit[$index], $explicitIndexes);
        $explicitBudget = self::COLUMN_COUNT - count($autoIndexes);
        $explicitValues = self::reduceToBudget($explicitValues, max(count($explicitIndexes), $explicitBudget));
        foreach ($explicitIndexes as $valueIndex => $index) {
            $result[$index] = $explicitValues[$valueIndex];
        }

        $used = array_sum($result);
        if ($autoIndexes) {
            $autoValues = self::distribute(max(count($autoIndexes), self::COLUMN_COUNT - $used), count($autoIndexes));
            foreach ($autoIndexes as $valueIndex => $index) {
                $result[$index] = $autoValues[$valueIndex];
            }
        } elseif ($used < self::COLUMN_COUNT) {
            $remaining = self::COLUMN_COUNT - $used;
            $cursor = 0;
            while ($remaining > 0 && $count > 0) {
                $result[$cursor % $count]++;
                $cursor++;
                $remaining--;
            }
        }
        return array_sum($result) > self::COLUMN_COUNT
            ? self::reduceToBudget($result, self::COLUMN_COUNT)
            : $result;
    }

    /** @param array<string,mixed> $state */
    private static function effectiveSpan(array $state, string $device): int
    {
        $desktop = self::span($state['Desktop']['Span'] ?? 0);
        if ($device === 'Desktop') {
            return $desktop;
        }
        $deviceState = isset($state[$device]) && is_array($state[$device]) ? $state[$device] : [];
        $inherit = array_key_exists('InheritDesktop', $deviceState)
            ? self::boolValue($deviceState['InheritDesktop'], true)
            : true;
        return $inherit ? $desktop : self::span($deviceState['Span'] ?? 0);
    }

    /** @param mixed $value */
    private static function span($value): int
    {
        if (!is_numeric($value)) {
            return 0;
        }
        $span = (int) $value;
        return $span > 0 ? max(1, min(self::COLUMN_COUNT, $span)) : 0;
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

    /** @param array<int,int> $values @return array<int,int> */
    private static function reduceToBudget(array $values, int $budget): array
    {
        $result = array_values($values);
        while (array_sum($result) > $budget) {
            $best = -1;
            foreach ($result as $index => $value) {
                if ($value > 1 && ($best < 0 || $value > $result[$best])) {
                    $best = $index;
                }
            }
            if ($best < 0) {
                break;
            }
            $result[$best]--;
        }
        return $result;
    }

    /** @return array<int,int> */
    private static function distribute(int $total, int $count): array
    {
        if ($count <= 0) {
            return [];
        }
        $base = intdiv($total, $count);
        $remainder = $total - ($base * $count);
        $result = [];
        for ($index = 0; $index < $count; $index++) {
            $result[] = max(1, $base + ($remainder > 0 ? 1 : 0));
            if ($remainder > 0) {
                $remainder--;
            }
        }
        return $result;
    }

    /** @param array<int,string> $keys @param array<int,int> $spans @param array<int,string> $rules */
    private static function appendGridChildRules(array &$rules, array $keys, array $spans): void
    {
        foreach ($keys as $index => $key) {
            $span = isset($spans[$index]) ? max(1, min(self::COLUMN_COUNT, (int) $spans[$index])) : self::COLUMN_COUNT;
            $rules[] = '#h18-section-' . sanitize_html_class($key) . '{grid-column:span ' . $span . '!important;align-self:stretch!important}';
        }
    }

    /** @param array<int,string> $keys @param array<int,int> $spans @param array<int,string> $rules */
    private static function appendFlexChildRules(array &$rules, array $keys, array $spans): void
    {
        foreach ($keys as $index => $key) {
            $span = isset($spans[$index]) ? max(1, min(self::COLUMN_COUNT, (int) $spans[$index])) : self::COLUMN_COUNT;
            $percent = round(($span / self::COLUMN_COUNT) * 100, 6);
            $rules[] = '#h18-section-' . sanitize_html_class($key) . '{flex:0 0 ' . $percent . '%!important;align-self:stretch!important}';
        }
    }
}
