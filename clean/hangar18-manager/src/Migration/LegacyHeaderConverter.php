<?php

declare(strict_types=1);

namespace Hangar18\Clean\Migration;

use Hangar18\Clean\Model\LayoutModel;
use Hangar18\Clean\Model\TemplateLayoutModel;

/**
 * Non-destructive one-time conversion of the historical Hangar18 Manager
 * HeaderDesign into the canonical Visual Designer Header template.
 *
 * The legacy Manager kept the design in an option and rendered the Header
 * inside managed page content. Visual Designer keeps the converted result in
 * Header – Standard and preserves any previous Visual Designer state through
 * the normal template version history.
 */
final class LegacyHeaderConverter
{
    public const MIGRATION_OPTION = 'h18_vd_legacy_header_converted_v0141';

    private const LEGACY_DESIGN_OPTION = 'hangar18_manager_header_design_v25';
    private const LEGACY_ACTIVE_MENU_OPTION = 'hangar18_manager_active_menu';
    private const TARGET_TEMPLATE_ID = 'header-standard-v1';
    private const HEADER_START = '<!-- HANGAR18-HEADER-START -->';
    private const HEADER_END = '<!-- HANGAR18-HEADER-END -->';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'maybeMigrate'], 4);
    }

    public static function maybeMigrate(): void
    {
        if (!current_user_can('edit_theme_options') || get_option(self::MIGRATION_OPTION, false)) {
            return;
        }

        $stored = get_option(self::LEGACY_DESIGN_OPTION, []);
        $stored = is_array($stored) ? $stored : [];
        $shell = self::legacyShellHeader();

        // Do not manufacture a migration on sites that never had the legacy
        // Hangar18 Header. If the source appears later, a later admin request
        // can still perform the conversion because no marker is written here.
        if (!$stored && $shell === '') {
            return;
        }

        $design = array_merge(self::defaultLegacyDesign(), $stored);
        if ($shell !== '') {
            $design = array_merge($design, self::parseShellHeader($shell));
        }

        TemplateLayoutModel::ensureMigrated();
        $targetId = TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID, 'header')
            ? self::TARGET_TEMPLATE_ID
            : TemplateLayoutModel::defaultId('header');
        if ($targetId === '') {
            $targetId = TemplateLayoutModel::create('header', 'Header – Standard');
        }

        $menuId = self::legacyMenuId();
        $model = self::buildModelFromLegacyDesign($design, $menuId);
        $settings = self::templateSettings($design);

        // saveVersion is deliberately used instead of replacing the option
        // directly: any Header the user already saved remains restorable.
        $version = TemplateLayoutModel::saveVersion(
            $targetId,
            $model,
            $settings,
            get_current_user_id(),
            'Automatisk 1:1-konvertering fra legacy Header · v0.1.41'
        );
        TemplateLayoutModel::rename($targetId, 'Header – Standard');
        TemplateLayoutModel::setActive($targetId, true);
        TemplateLayoutModel::setDefault('header', $targetId);

        update_option(self::MIGRATION_OPTION, [
            'convertedUtc' => gmdate('c'),
            'templateId' => $targetId,
            'templateVersion' => $version,
            'menuId' => $menuId,
            'sourceOption' => (bool) $stored,
            'sourceShell' => $shell !== '',
            'digest' => LayoutModel::structuralDigest($model),
        ], false);
    }

    /**
     * Pure conversion entry used by CI and by the migration itself.
     *
     * @param array<string,mixed> $rawDesign
     * @return array<string,mixed>
     */
    public static function buildModelFromLegacyDesign(array $rawDesign, int $menuId): array
    {
        $d = array_merge(self::defaultLegacyDesign(), $rawDesign);

        $desktopPct = self::clampInt($d['DesktopContentWidthPercent'] ?? 90, 40, 100, 90);
        $laptopPct = self::clampInt($d['LaptopContentWidthPercent'] ?? 90, 50, 100, 90);
        $widthMode = (string) ($d['WidthMode'] ?? 'Contained');
        if ($widthMode === 'Full') {
            $desktopPct = 100;
            $laptopPct = 100;
        } elseif ($widthMode === 'Narrow') {
            $desktopPct = min($desktopPct, 72);
            $laptopPct = min($laptopPct, 84);
        }

        [$desktopX, $desktopW] = self::centredUnits($desktopPct);
        [$laptopX, $laptopW] = self::centredUnits($laptopPct);

        $scale = self::clampInt($d['VisualBaseScalePercent'] ?? 90, 50, 120, 90) / 100;
        $brandPx = max(12, (int) round(self::clampInt($d['BrandFontSize'] ?? 22, 12, 60, 22)
            * self::clampInt($d['BrandSizePercent'] ?? 100, 50, 180, 100) / 100 * $scale));
        $menuPx = max(10, (int) round(self::clampInt($d['MenuFontSize'] ?? 15, 10, 40, 15)
            * self::clampInt($d['MenuSizePercent'] ?? 100, 50, 180, 100) / 100 * $scale));
        $logoPx = max(24, (int) round(self::clampInt($d['LogoWidthPx'] ?? 52, 24, 300, 52)
            * self::clampInt($d['LogoSizePercent'] ?? 100, 50, 180, 100) / 100 * $scale));

        $showBrand = self::boolValue($d['ShowBrand'] ?? true, true)
            && trim((string) ($d['BrandText'] ?? '')) !== '';
        $showLogo = self::boolValue($d['ShowLogo'] ?? false, false)
            && trim((string) ($d['LogoUrl'] ?? '')) !== '';
        $hasIdentity = $showBrand || $showLogo;

        $heightPx = max(56, $menuPx * 3, $brandPx * 2 + 12, $showLogo ? $logoPx + 16 : 0);
        $rows = max(7, min(20, (int) ceil($heightPx / LayoutModel::ROW_PX)));

        $primary = self::color($d['PrimaryColor'] ?? '#30382a', '#30382a');
        $surface = self::color($d['SurfaceColor'] ?? '#f2f0e8', '#f2f0e8');
        $text = self::color($d['TextColor'] ?? '#30382a', '#30382a');
        $light = self::color($d['LightTextColor'] ?? '#ffffff', '#ffffff');
        $accent = self::color($d['AccentColor'] ?? '#c3ae83', '#c3ae83');
        $backgroundMode = (string) ($d['BackgroundMode'] ?? 'None');
        $darkBackground = in_array($backgroundMode, ['Bar', 'Box'], true);
        $foreground = $darkBackground ? $light : $text;

        $sectionBackground = $backgroundMode === 'Bar' ? $primary : '';
        $innerBackground = $backgroundMode === 'Box' ? $primary : ($backgroundMode === 'Glass' ? $surface : '');

        $menuAlign = self::alignment($d['MenuAlignment'] ?? 'Right', 'right');
        $identityAlign = self::alignment($d['IdentityAlignment'] ?? 'Center', 'center');
        $fontFamily = self::fontToken($d['BodyFontFamily'] ?? 'Segoe UI');
        $menuFontFamily = self::fontToken($d['MenuFontFamily'] ?? 'Segoe UI');
        // The current Menu element uses the common font token only indirectly;
        // keep the source token available by mapping the visual properties that
        // are canonical today. Segoe UI maps to system, which is the old site's
        // effective Windows/browser font stack.
        unset($menuFontFamily);

        $desktopIdentityW = $hasIdentity ? 50 : 0;
        $desktopMenuX = $desktopIdentityW;
        $desktopMenuW = 120 - $desktopMenuX;
        $mobileIdentityW = $hasIdentity ? 90 : 0;
        $mobileMenuX = $hasIdentity ? 90 : 0;
        $mobileMenuW = $hasIdentity ? 30 : 120;

        $nodes = [];
        $nodes[] = self::node(
            'section-legacy-header-v0141',
            'section',
            '',
            10,
            self::geometry(
                [$desktopX, 0, $desktopW, $rows],
                [$laptopX, 0, $laptopW, $rows],
                [0, 0, 120, $rows]
            ),
            [
                'background' => $sectionBackground,
                'radius' => 0,
                'padding' => 0,
                'minHeightRows' => $rows,
                'borderWidth' => 0,
                'borderColor' => '#000000',
                'gapX' => 0,
                'gapY' => 0,
            ]
        );
        $nodes[] = self::node(
            'container-legacy-header-inner-v0141',
            'container',
            'section-legacy-header-v0141',
            10,
            self::geometry([0, 0, 120, $rows], [0, 0, 120, $rows], [0, 0, 120, $rows]),
            [
                'background' => $innerBackground,
                'radius' => $backgroundMode === 'Glass' ? 7 : 0,
                'padding' => 0,
                'minHeightRows' => $rows,
                'borderWidth' => 0,
                'borderColor' => '#000000',
                'gapX' => 0,
                'gapY' => 0,
            ]
        );

        $order = 10;
        $desktopCursor = 0;
        $mobileCursor = 0;

        if ($showLogo) {
            $desktopLogoW = $showBrand ? 12 : min(20, $desktopIdentityW);
            $mobileLogoW = $showBrand ? 18 : min(30, $mobileIdentityW);
            $nodes[] = self::node(
                'image-legacy-header-logo-v0141',
                'image',
                'container-legacy-header-inner-v0141',
                $order,
                self::geometry(
                    [$desktopCursor, 0, max(1, $desktopLogoW), $rows],
                    [$desktopCursor, 0, max(1, $desktopLogoW), $rows],
                    [$mobileCursor, 0, max(1, $mobileLogoW), $rows]
                ),
                [
                    'mediaId' => max(0, (int) ($d['LogoMediaId'] ?? 0)),
                    'url' => esc_url_raw((string) ($d['LogoUrl'] ?? '')),
                    'alt' => sanitize_text_field((string) ($d['BrandText'] ?? '')),
                    'fit' => 'contain',
                    'imageAlignX' => $identityAlign,
                    'imageAlignY' => 'center',
                    'boxBackground' => '#ffffff',
                    'boxTransparent' => true,
                    'focalX' => 50,
                    'focalY' => 50,
                    'borderWidth' => 0,
                    'borderColor' => '#000000',
                    'gapX' => 0,
                    'gapY' => 0,
                ]
            );
            $order += 10;
            $desktopCursor += $desktopLogoW;
            $mobileCursor += $mobileLogoW;
        }

        if ($showBrand) {
            $desktopBrandW = max(1, $desktopIdentityW - $desktopCursor);
            $mobileBrandW = max(1, $mobileIdentityW - $mobileCursor);
            $nodes[] = self::node(
                'text-legacy-header-brand-v0141',
                'text',
                'container-legacy-header-inner-v0141',
                $order,
                self::geometry(
                    [$desktopCursor, 0, $desktopBrandW, $rows],
                    [$desktopCursor, 0, $desktopBrandW, $rows],
                    [$mobileCursor, 0, $mobileBrandW, $rows]
                ),
                [
                    'heading' => '',
                    'headingLevel' => 'h2',
                    'text' => sanitize_text_field((string) ($d['BrandText'] ?? '')),
                    'align' => $identityAlign,
                    'background' => '#ffffff',
                    'backgroundTransparent' => true,
                    'textColor' => $foreground,
                    'headingColor' => $foreground,
                    'padding' => 0,
                    'radius' => 0,
                    'fontFamily' => $fontFamily,
                    'fontSize' => $brandPx,
                    'fontWeight' => 600,
                    'lineHeight' => 1.2,
                    'letterSpacing' => 0,
                    'borderWidth' => 0,
                    'borderColor' => '#000000',
                    'gapX' => 0,
                    'gapY' => 0,
                ]
            );
            $order += 10;
        }

        $nodes[] = self::node(
            'menu-legacy-header-primary-v0141',
            'menu',
            'container-legacy-header-inner-v0141',
            $order,
            self::geometry(
                [$desktopMenuX, 0, $desktopMenuW, $rows],
                [$desktopMenuX, 0, $desktopMenuW, $rows],
                [$mobileMenuX, 0, $mobileMenuW, $rows]
            ),
            [
                'menuId' => max(0, $menuId),
                'orientation' => 'horizontal',
                'align' => $menuAlign,
                'mobileMode' => 'hamburger',
                'textColor' => $foreground,
                'hoverTextColor' => $accent,
                'activeTextColor' => $accent,
                'background' => $primary,
                'backgroundTransparent' => true,
                'fontSize' => $menuPx,
                'fontWeight' => self::fontWeight($d['MenuFontWeight'] ?? 'Semibold'),
                'menuGap' => 18,
                'paddingX' => 8,
                'paddingY' => 8,
                'radius' => 0,
                'borderWidth' => 0,
                'borderColor' => '#000000',
                'gapX' => 0,
                'gapY' => 0,
            ]
        );

        return LayoutModel::normalize([
            'schemaVersion' => LayoutModel::SCHEMA,
            'units' => LayoutModel::UNITS,
            'rowPx' => LayoutModel::ROW_PX,
            'nodes' => $nodes,
        ]);
    }

    /** @param array<string,mixed> $design @return array<string,mixed> */
    private static function templateSettings(array $design): array
    {
        $position = strtolower((string) ($design['PositionMode'] ?? 'Normal'));
        $sticky = self::boolValue($design['StickyOnScroll'] ?? false, false) || $position === 'sticky';
        $overlay = $position === 'overlay';
        $max = $design['ContentMaxWidth'] ?? 'None';
        $contentWidth = is_numeric($max) ? (int) $max : 2400;
        return [
            'sticky' => $sticky,
            'overlay' => $overlay,
            'contentWidth' => max(320, min(2400, $contentWidth)),
        ];
    }

    /** @return array<string,mixed> */
    private static function defaultLegacyDesign(): array
    {
        return [
            'PrimaryColor' => '#30382a',
            'SecondaryColor' => '#525a5f',
            'AccentColor' => '#c3ae83',
            'SurfaceColor' => '#f2f0e8',
            'BackgroundColor' => '#ffffff',
            'TextColor' => '#30382a',
            'LightTextColor' => '#ffffff',
            'ActionColor' => '#8b4a2b',
            'BodyFontFamily' => 'Segoe UI',
            'MenuAlignment' => 'Right',
            'PositionMode' => 'Normal',
            'StickyOnScroll' => false,
            'BackgroundMode' => 'None',
            'WidthMode' => 'Contained',
            'ShowBrand' => true,
            'BrandText' => 'Aalborg Kaserners Veteran Panser- og Køretøjsforening',
            'IdentityAlignment' => 'Center',
            'BrandFontSize' => 22,
            'BrandSizePercent' => 100,
            'ShowLogo' => false,
            'LogoMediaId' => 0,
            'LogoUrl' => '',
            'LogoWidthPx' => 52,
            'LogoSizePercent' => 100,
            'MobileStyle' => 'Dark',
            'MenuFontSize' => 15,
            'MenuSizePercent' => 100,
            'MenuFontFamily' => 'Segoe UI',
            'MenuFontWeight' => 'Semibold',
            'MenuFontItalic' => false,
            'MenuUppercase' => false,
            'VisualBaseScalePercent' => 90,
            'ResponsiveScaleEnabled' => true,
            'DesktopContentWidthPercent' => 90,
            'LaptopContentWidthPercent' => 90,
            'MaximumDesktopContentWidthPercent' => 90,
            'ContentMaxWidth' => 'None',
        ];
    }

    private static function legacyMenuId(): int
    {
        $saved = absint(get_option(self::LEGACY_ACTIVE_MENU_OPTION, 0));
        if ($saved > 0 && wp_get_nav_menu_object($saved)) {
            return $saved;
        }

        $locations = get_nav_menu_locations();
        if (is_array($locations) && !empty($locations['primary']) && wp_get_nav_menu_object((int) $locations['primary'])) {
            return (int) $locations['primary'];
        }

        $menus = wp_get_nav_menus();
        if (is_array($menus) && $menus) {
            return (int) ($menus[0]->term_id ?? 0);
        }
        return 0;
    }

    private static function legacyShellHeader(): string
    {
        $pages = [];
        $home = get_page_by_path('hjem', OBJECT, 'page');
        if ($home instanceof \WP_Post) {
            $pages[] = $home;
        }
        foreach (get_pages([
            'sort_column' => 'menu_order,post_title',
            'sort_order' => 'ASC',
            'post_status' => ['publish', 'draft', 'pending', 'private', 'future'],
        ]) as $page) {
            if ($page instanceof \WP_Post && (!isset($pages[0]) || (int) $pages[0]->ID !== (int) $page->ID)) {
                $pages[] = $page;
            }
        }

        foreach ($pages as $page) {
            $content = (string) $page->post_content;
            $start = strpos($content, self::HEADER_START);
            $end = strpos($content, self::HEADER_END);
            if ($start === false || $end === false || $end <= $start) {
                continue;
            }
            $end += strlen(self::HEADER_END);
            return trim(substr($content, $start, $end - $start));
        }
        return '';
    }

    /** @return array<string,mixed> */
    private static function parseShellHeader(string $header): array
    {
        $out = [];
        if (preg_match('/<header\s+class="([^"]*\bh18-site-header\b[^"]*)"[^>]*>/i', $header, $m)) {
            $classes = preg_split('/\s+/', trim((string) $m[1])) ?: [];
            foreach ($classes as $class) {
                if (str_starts_with($class, 'h18-align-')) { $out['MenuAlignment'] = ucfirst(substr($class, 10)); }
                elseif (str_starts_with($class, 'h18-identity-align-')) { $out['IdentityAlignment'] = ucfirst(substr($class, 19)); }
                elseif (str_starts_with($class, 'h18-pos-')) { $out['PositionMode'] = ucfirst(substr($class, 8)); }
                elseif (str_starts_with($class, 'h18-bg-')) { $out['BackgroundMode'] = ucfirst(substr($class, 7)); }
                elseif (str_starts_with($class, 'h18-width-')) { $out['WidthMode'] = ucfirst(substr($class, 10)); }
                elseif ($class === 'h18-scroll-sticky') { $out['StickyOnScroll'] = true; }
                elseif ($class === 'h18-scroll-normal') { $out['StickyOnScroll'] = false; }
                elseif ($class === 'h18-brandtext-visible') { $out['ShowBrand'] = true; }
                elseif ($class === 'h18-brandtext-hidden') { $out['ShowBrand'] = false; }
                elseif ($class === 'h18-logo-visible') { $out['ShowLogo'] = true; }
                elseif ($class === 'h18-logo-hidden') { $out['ShowLogo'] = false; }
            }
        }
        if (preg_match('/<span\s+class="h18-site-brand-text"[^>]*>(.*?)<\/span>/s', $header, $m)) {
            $brand = trim(wp_strip_all_tags((string) $m[1]));
            if ($brand !== '') { $out['BrandText'] = $brand; }
        }
        if (preg_match('/<img\s+class="h18-site-logo"[^>]*\ssrc="([^"]+)"/i', $header, $m)) {
            $url = esc_url_raw(html_entity_decode((string) $m[1], ENT_QUOTES));
            if ($url !== '') {
                $out['LogoUrl'] = $url;
                $out['ShowLogo'] = true;
                $attachment = attachment_url_to_postid($url);
                if ($attachment) { $out['LogoMediaId'] = (int) $attachment; }
            }
        }
        return $out;
    }

    /** @param array<int,int> $desktop @param array<int,int> $laptop @param array<int,int> $mobile */
    private static function geometry(array $desktop, array $laptop, array $mobile): array
    {
        return [
            'desktop' => ['x' => $desktop[0], 'y' => $desktop[1], 'w' => $desktop[2], 'h' => $desktop[3]],
            'laptop' => ['x' => $laptop[0], 'y' => $laptop[1], 'w' => $laptop[2], 'h' => $laptop[3], 'inheritDesktop' => false],
            'tablet' => ['x' => $laptop[0], 'y' => $laptop[1], 'w' => $laptop[2], 'h' => $laptop[3], 'inheritDesktop' => false],
            'mobile' => ['x' => $mobile[0], 'y' => $mobile[1], 'w' => $mobile[2], 'h' => $mobile[3], 'inheritDesktop' => false],
        ];
    }

    /** @param array<string,mixed> $geometry @param array<string,mixed> $props @return array<string,mixed> */
    private static function node(string $id, string $type, string $parentId, int $order, array $geometry, array $props): array
    {
        return compact('id', 'type', 'parentId', 'order', 'geometry', 'props');
    }

    /** @return array{0:int,1:int} */
    private static function centredUnits(int $percent): array
    {
        $w = max(1, min(120, (int) round(120 * $percent / 100)));
        return [(int) floor((120 - $w) / 2), $w];
    }

    private static function alignment($value, string $fallback): string
    {
        $value = strtolower((string) $value);
        return in_array($value, ['left', 'center', 'right'], true) ? $value : $fallback;
    }

    private static function color($value, string $fallback): string
    {
        $value = strtolower((string) $value);
        return preg_match('/^#[0-9a-f]{6}$/', $value) ? $value : $fallback;
    }

    private static function boolValue($value, bool $fallback): bool
    {
        if (is_bool($value)) { return $value; }
        if (is_numeric($value)) { return (int) $value !== 0; }
        $value = strtolower(trim((string) $value));
        if (in_array($value, ['1', 'true', 'yes', 'on'], true)) { return true; }
        if (in_array($value, ['0', 'false', 'no', 'off', ''], true)) { return false; }
        return $fallback;
    }

    private static function clampInt($value, int $min, int $max, int $fallback): int
    {
        if (!is_numeric($value)) { return $fallback; }
        return max($min, min($max, (int) $value));
    }

    private static function fontToken($value): string
    {
        $value = strtolower(trim((string) $value));
        if (str_contains($value, 'arial')) { return 'arial'; }
        if (str_contains($value, 'verdana')) { return 'verdana'; }
        if (str_contains($value, 'tahoma')) { return 'tahoma'; }
        if (str_contains($value, 'trebuchet')) { return 'trebuchet'; }
        if (str_contains($value, 'georgia')) { return 'georgia'; }
        if (str_contains($value, 'times')) { return 'times'; }
        if (str_contains($value, 'courier')) { return 'courier'; }
        return 'system';
    }

    private static function fontWeight($value): int
    {
        if (is_numeric($value)) { return max(100, min(900, (int) $value)); }
        return match (strtolower(trim((string) $value))) {
            'light' => 300,
            'medium' => 500,
            'semibold', 'semi-bold' => 600,
            'bold' => 700,
            'extrabold', 'extra-bold' => 800,
            default => 400,
        };
    }

    private function __construct()
    {
    }
}
