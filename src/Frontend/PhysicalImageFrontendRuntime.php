<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Frontend;

/** Public parity for v0.9.3 physical Image box fitting. */
final class PhysicalImageFrontendRuntime
{
    private const LAYOUT_OPTION = 'hangar18_ultimate_designer_layout_model_v0900';

    public static function register(): void
    {
        add_action('wp_head', [self::class, 'renderCss'], 1006);
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

        $common = [];
        $desktopHeight = [];
        $tabletHeight = [];
        $mobileHeight = [];

        foreach ($sections as $rawKey => $section) {
            if (!is_array($section) || !empty($section['Removed'])) {
                continue;
            }
            if (sanitize_key((string) ($section['Type'] ?? '')) !== 'image') {
                continue;
            }
            if (!isset($section['PhysicalImage']) || !is_array($section['PhysicalImage'])) {
                continue;
            }

            $key = sanitize_key((string) ($section['Key'] ?? $rawKey));
            if ($key === '') {
                continue;
            }
            $image = self::normalizeImage($section['PhysicalImage']);
            $selector = '#h18-section-' . sanitize_html_class($key);
            $figure = $selector . ' .h18-editor-image';
            $img = $selector . ' .h18-editor-image img,' . $selector . ' img';
            $fit = $image['Mode'] === 'Contain' ? 'contain' : ($image['Mode'] === 'Stretch' ? 'fill' : 'cover');
            $position = (int) $image['FocalX'] . '% ' . (int) $image['FocalY'] . '%';

            $common[] = $figure . '{box-sizing:border-box!important;width:100%!important;max-width:none!important;margin:0!important;overflow:hidden!important;}';
            $common[] = $img . '{box-sizing:border-box!important;display:block!important;width:100%!important;max-width:none!important;margin:0!important;aspect-ratio:auto!important;object-fit:' . $fit . '!important;object-position:' . $position . '!important;}';

            $geometry = isset($section['Geometry']) && is_array($section['Geometry']) ? $section['Geometry'] : [];
            if (self::hasExplicitHeight($geometry, 'Desktop')) {
                $desktopHeight[] = $figure . ',' . $img . '{height:100%!important;}';
            }
            if (self::hasExplicitHeight($geometry, 'Tablet')) {
                $tabletHeight[] = $figure . ',' . $img . '{height:100%!important;}';
            }
            if (self::hasExplicitHeight($geometry, 'Mobile')) {
                $mobileHeight[] = $figure . ',' . $img . '{height:100%!important;}';
            }
        }

        if (!$common && !$desktopHeight && !$tabletHeight && !$mobileHeight) {
            return;
        }

        echo "\n<style id=\"h18-physical-image-parity-v0903\">\n";
        echo implode("\n", array_merge($common, $desktopHeight));
        if ($tabletHeight) {
            echo "\n@media (max-width:1100px) and (min-width:783px){\n" . implode("\n", $tabletHeight) . "\n}";
        }
        if ($mobileHeight) {
            echo "\n@media (max-width:782px){\n" . implode("\n", $mobileHeight) . "\n}";
        }
        echo "\n</style>\n";
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function normalizeImage(array $raw): array
    {
        $mode = ucfirst(strtolower(trim((string) ($raw['Mode'] ?? 'Cover'))));
        if (!in_array($mode, ['Cover', 'Contain', 'Stretch'], true)) {
            $mode = 'Cover';
        }
        return [
            'Mode' => $mode,
            'FocalX' => self::percent($raw['FocalX'] ?? 50),
            'FocalY' => self::percent($raw['FocalY'] ?? 50),
        ];
    }

    /** @param array<string,mixed> $geometry */
    private static function hasExplicitHeight(array $geometry, string $device): bool
    {
        $desktop = isset($geometry['Desktop']) && is_array($geometry['Desktop']) ? $geometry['Desktop'] : [];
        $branch = $desktop;
        if ($device !== 'Desktop') {
            $candidate = isset($geometry[$device]) && is_array($geometry[$device]) ? $geometry[$device] : [];
            $inherit = array_key_exists('InheritDesktop', $candidate)
                ? self::boolValue($candidate['InheritDesktop'], true)
                : true;
            $branch = $inherit ? $desktop : $candidate;
        }
        return !empty($branch['Explicit']) && is_numeric($branch['H'] ?? null) && (int) $branch['H'] > 0;
    }

    /** @param mixed $value */
    private static function percent($value): int
    {
        return is_numeric($value) ? max(0, min(100, (int) $value)) : 50;
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
