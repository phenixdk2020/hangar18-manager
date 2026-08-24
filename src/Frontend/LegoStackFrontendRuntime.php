<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Frontend;

/**
 * Frontend parity bridge for LEGO vertical stack metadata.
 *
 * A Grid stack is represented canonically as multiple page sections with the
 * same LayoutParentKey plus additive StackRootKey metadata. The editor folds
 * those sections into one horizontal tile. This runtime mirrors that contract
 * on public/live-preview DOM so stack members do not consume extra 12-column
 * spans. Natural content height is authoritative until a vertical split has
 * explicitly been set by the editor.
 */
final class LegoStackFrontendRuntime
{
    private const PAGE_OPTION = 'hangar18_manager_pages_v1';
    private const SPAN_OPTION = 'hangar18_ultimate_designer_lego_layout_span_v1';
    private const STACK_OPTION = 'hangar18_ultimate_designer_lego_stack_v0851';
    private const PREVIEW_PREFIX = 'h18_live_preview_';
    private const COLUMN_COUNT = 12;

    public static function register(): void
    {
        add_action('wp_head', [self::class, 'render'], 1002);
    }

    public static function render(): void
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
        $stackSections = self::stackSections($slug);
        $sections = isset($pageData['Sections']) && is_array($pageData['Sections']) ? $pageData['Sections'] : [];
        if (!$sections || !$stackSections) {
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
        $config = ['parents' => []];

        foreach ($childrenByParent as $parentKey => $childKeys) {
            if (!isset($byKey[$parentKey])) {
                continue;
            }
            if (sanitize_key((string) ($byKey[$parentKey]['Type'] ?? '')) !== 'grid') {
                continue;
            }

            $childSet = array_fill_keys($childKeys, true);
            $rootFor = [];
            $hasStack = false;
            foreach ($childKeys as $key) {
                $state = isset($stackSections[$key]) && is_array($stackSections[$key]) ? $stackSections[$key] : [];
                $root = sanitize_key((string) ($state['StackRootKey'] ?? ''));
                if ($root !== '' && $root !== $key && isset($childSet[$root])) {
                    $rootFor[$key] = $root;
                    $hasStack = true;
                } else {
                    $rootFor[$key] = '';
                }
            }
            if (!$hasStack) {
                continue;
            }

            $rootKeys = [];
            foreach ($childKeys as $key) {
                if (($rootFor[$key] ?? '') === '') {
                    $rootKeys[] = $key;
                }
            }
            if (!$rootKeys) {
                continue;
            }

            $desktop = self::resolveSpans($rootKeys, $spanSections, 'Desktop');
            $tablet = self::resolveSpans($rootKeys, $spanSections, 'Tablet');
            $mobile = self::resolveSpans($rootKeys, $spanSections, 'Mobile');

            $parentSelector = '#h18-section-' . sanitize_html_class($parentKey) . '>.h18-layout-children';
            $parentRule = $parentSelector . '{grid-template-columns:repeat(12,minmax(0,1fr))!important;align-items:stretch!important}';
            $desktopRules[] = $parentRule;
            $tabletRules[] = $parentRule;
            $mobileRules[] = $parentRule;

            $parentConfig = ['key' => $parentKey, 'groups' => []];
            foreach ($rootKeys as $index => $rootKey) {
                $members = [];
                foreach ($childKeys as $candidate) {
                    if (($rootFor[$candidate] ?? '') === $rootKey) {
                        $members[] = $candidate;
                    }
                }
                usort($members, static function (string $a, string $b) use ($stackSections, $childKeys): int {
                    $ao = isset($stackSections[$a]['StackOrder']) ? (int) $stackSections[$a]['StackOrder'] : 0;
                    $bo = isset($stackSections[$b]['StackOrder']) ? (int) $stackSections[$b]['StackOrder'] : 0;
                    if ($ao === $bo) {
                        return array_search($a, $childKeys, true) <=> array_search($b, $childKeys, true);
                    }
                    return $ao <=> $bo;
                });
                $groupMembers = array_merge([$rootKey], $members);

                $desktopSpan = isset($desktop[$index]) ? max(1, min(self::COLUMN_COUNT, (int) $desktop[$index])) : self::COLUMN_COUNT;
                $tabletSpan = isset($tablet[$index]) ? max(1, min(self::COLUMN_COUNT, (int) $tablet[$index])) : $desktopSpan;
                $mobileSpan = isset($mobile[$index]) ? max(1, min(self::COLUMN_COUNT, (int) $mobile[$index])) : $tabletSpan;

                if (count($groupMembers) > 1) {
                    $wrapperSelector = '.h18-lego-stack-column-v0886[data-h18-stack-root="' . esc_attr($rootKey) . '"]';
                    $desktopRules[] = $wrapperSelector . '{grid-column:span ' . $desktopSpan . '!important}';
                    $tabletRules[] = $wrapperSelector . '{grid-column:span ' . $tabletSpan . '!important}';
                    $mobileRules[] = $wrapperSelector . '{grid-column:span ' . $mobileSpan . '!important}';
                    self::appendStackHeightRules($desktopRules, $wrapperSelector, $groupMembers, $stackSections, 'Desktop');
                    self::appendStackHeightRules($tabletRules, $wrapperSelector, $groupMembers, $stackSections, 'Tablet');
                    self::appendStackHeightRules($mobileRules, $wrapperSelector, $groupMembers, $stackSections, 'Mobile');
                    $parentConfig['groups'][] = [
                        'root' => $rootKey,
                        'members' => $groupMembers,
                    ];
                } else {
                    $selector = '#h18-section-' . sanitize_html_class($rootKey);
                    $desktopRules[] = $selector . '{grid-column:span ' . $desktopSpan . '!important;align-self:stretch!important}';
                    $tabletRules[] = $selector . '{grid-column:span ' . $tabletSpan . '!important;align-self:stretch!important}';
                    $mobileRules[] = $selector . '{grid-column:span ' . $mobileSpan . '!important;align-self:stretch!important}';
                }
            }

            if ($parentConfig['groups']) {
                $config['parents'][] = $parentConfig;
            }
        }

        if (!$config['parents']) {
            return;
        }

        $baseRules = [
            '.h18-lego-stack-column-v0886{display:flex;flex-direction:column;align-self:stretch;min-width:0;width:100%;box-sizing:border-box}',
            '.h18-lego-stack-column-v0886>.h18-editor-section{min-width:0;box-sizing:border-box;flex:0 0 auto}',
            '.h18-lego-stack-column-v0886>.h18-editor-section .h18-editor-media img,.h18-lego-stack-column-v0886>.h18-editor-section .h18-editor-image img{max-width:100%}',
        ];

        echo "\n<style id=\"h18-lego-stack-parity-v0886\">\n";
        echo implode("\n", array_merge($baseRules, $desktopRules));
        if ($tabletRules) {
            echo "\n@media (max-width:1100px) and (min-width:783px){\n" . implode("\n", $tabletRules) . "\n}";
        }
        if ($mobileRules) {
            echo "\n@media (max-width:782px){\n" . implode("\n", $mobileRules) . "\n}";
        }
        echo "\n</style>\n";

        $json = wp_json_encode($config, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE);
        if (!is_string($json) || $json === '') {
            return;
        }
        echo '<script id="h18-lego-stack-parity-runtime-v0886">(function(){"use strict";var cfg=' . $json . ';function run(){(cfg.parents||[]).forEach(function(p){var section=document.getElementById("h18-section-"+p.key);var parent=section?section.querySelector(":scope>.h18-layout-children"):null;if(!parent){return;}(p.groups||[]).forEach(function(g){var existing=Array.from(parent.children).find(function(n){return n.classList&&n.classList.contains("h18-lego-stack-column-v0886")&&n.getAttribute("data-h18-stack-root")===g.root;});if(existing){return;}var nodes=(g.members||[]).map(function(k){return document.getElementById("h18-section-"+k);}).filter(function(n){return n&&n.parentNode===parent;});if(nodes.length<2){return;}var wrap=document.createElement("div");wrap.className="h18-lego-stack-column-v0886";wrap.setAttribute("data-h18-stack-root",g.root);parent.insertBefore(wrap,nodes[0]);nodes.forEach(function(n){wrap.appendChild(n);});});});}if(document.readyState==="loading"){document.addEventListener("DOMContentLoaded",run,{once:true});}else{run();}}());</script>' . "\n";
    }

    /** @return array<string,mixed> */
    private static function stackSections(string $slug): array
    {
        $token = isset($_GET['h18_live_preview'])
            ? preg_replace('/[^a-f0-9]/i', '', (string) wp_unslash($_GET['h18_live_preview']))
            : '';
        if ($token !== '' && is_user_logged_in() && current_user_can('edit_pages')) {
            $payload = get_transient(self::PREVIEW_PREFIX . $token);
            if (is_array($payload) && isset($payload['StackSections']) && is_array($payload['StackSections'])) {
                return $payload['StackSections'];
            }
        }
        $store = get_option(self::STACK_OPTION, []);
        return is_array($store) && isset($store[$slug]['Sections']) && is_array($store[$slug]['Sections'])
            ? $store[$slug]['Sections']
            : [];
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

    /** @param array<int,string> $keys @param array<string,mixed> $states @return array<int,int> */
    private static function effectiveStackPercents(array $keys, array $states, string $device): array
    {
        $raw = [];
        foreach ($keys as $key) {
            $state = isset($states[$key]) && is_array($states[$key]) ? $states[$key] : [];
            $desktop = self::percent($state['DesktopPercent'] ?? 0);
            if ($device === 'Desktop') {
                $raw[] = $desktop;
                continue;
            }
            $ownField = $device === 'Mobile' ? 'MobilePercent' : 'TabletPercent';
            $own = self::percent($state[$ownField] ?? 0);
            $raw[] = $own > 0 ? $own : $desktop;
        }
        if (!$raw || count(array_filter($raw, static fn(int $value): bool => $value > 0)) === 0) {
            return [];
        }
        $filled = array_map(static fn(int $value): int => $value > 0 ? $value : 10, $raw);
        $sum = max(1, array_sum($filled));
        $normalized = array_map(static fn(int $value): int => max(10, (int) round(($value / $sum) * 100)), $filled);
        $total = array_sum($normalized);
        while ($total > 100) {
            $index = -1;
            foreach ($normalized as $candidate => $value) {
                if ($value > 10) {
                    $index = $candidate;
                    break;
                }
            }
            if ($index < 0) {
                break;
            }
            $normalized[$index]--;
            $total--;
        }
        while ($total < 100 && $normalized) {
            $normalized[count($normalized) - 1]++;
            $total++;
        }
        return $normalized;
    }

    /** @param array<int,string> $keys @param array<string,mixed> $states @param array<int,string> $rules */
    private static function appendStackHeightRules(array &$rules, string $wrapperSelector, array $keys, array $states, string $device): void
    {
        $percents = self::effectiveStackPercents($keys, $states, $device);
        if (!$percents) {
            return;
        }
        foreach ($keys as $index => $key) {
            $value = isset($percents[$index]) ? max(10, min(90, (int) $percents[$index])) : 0;
            if ($value <= 0) {
                continue;
            }
            $rules[] = $wrapperSelector . '>#h18-section-' . sanitize_html_class($key) . '{flex:0 0 ' . $value . '%!important;min-height:0!important}';
        }
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
    private static function percent($value): int
    {
        if (!is_numeric($value)) {
            return 0;
        }
        $percent = (int) $value;
        return $percent > 0 ? max(10, min(90, $percent)) : 0;
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
}
