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
    public const MIGRATION_OPTION = 'h18_vd_legacy_header_converted_v0143';
    public const STATUS_OPTION = 'h18_vd_legacy_header_status_v0143';

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

        try {
            self::convert(false);
        } catch (\Throwable $error) {
            update_option(self::STATUS_OPTION, [
                'status' => 'error',
                'checkedUtc' => gmdate('c'),
                'message' => $error->getMessage(),
            ], false);
        }
    }

    /**
     * Run or re-run the Header conversion. The operation is non-destructive:
     * the target template is always saved through normal version history.
     *
     * @return array<string,mixed>
     */
    public static function convert(bool $force = true): array
    {
        if (!current_user_can('edit_theme_options')) {
            throw new \RuntimeException('Ingen adgang til Header-konvertering.');
        }
        if (!$force && get_option(self::MIGRATION_OPTION, false)) {
            return self::diagnosticStatus();
        }

        $stored = get_option(self::LEGACY_DESIGN_OPTION, []);
        $stored = is_array($stored) ? $stored : [];
        $shell = self::legacyShellHeader();
        $legacyFound = !empty($stored) || $shell !== '';

        $design = array_merge(self::defaultLegacyDesign(), $stored);
        if ($shell !== '') {
            $design = array_merge($design, self::parseShellHeader($shell));
        }

        $logo = self::resolveLogo($design);
        if ($logo['url'] !== '') {
            $design['ShowLogo'] = true;
            $design['LogoUrl'] = $logo['url'];
            $design['LogoMediaId'] = $logo['mediaId'];
        }

        $menuId = self::legacyMenuId();
        if ($menuId <= 0) {
            throw new \RuntimeException('Ingen WordPress-menu kunne findes til Headeren.');
        }

        if ($legacyFound) {
            $model = self::buildModelFromLegacyDesign($design, $menuId);
            $source = 'legacy';
            $note = 'Automatisk konvertering fra fundet legacy Header · v0.1.43';
        } else {
            $model = self::buildScreenshotReferenceModel($menuId, $logo['mediaId'], $logo['url']);
            $source = 'desktop-reference-2026-08-28';
            $note = 'Header-reference fra godkendt Desktop-screenshot · v0.1.43';
        }

        $counts = self::nodeCounts($model);
        if (($counts['section'] ?? 0) < 1 || ($counts['container'] ?? 0) < 1 || ($counts['menu'] ?? 0) < 1) {
            throw new \RuntimeException('Konverteringen gav ikke en gyldig Sektion/Kasse/Menu-struktur.');
        }
        if (($counts['text'] ?? 0) + ($counts['image'] ?? 0) < 1) {
            throw new \RuntimeException('Konverteringen mangler Header-identitet (Tekst/Billede).');
        }

        TemplateLayoutModel::ensureMigrated();
        $targetId = TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID, 'header')
            ? self::TARGET_TEMPLATE_ID
            : TemplateLayoutModel::defaultId('header');
        if ($targetId === '') {
            $targetId = TemplateLayoutModel::create('header', 'Header – Standard');
        }

        $settings = $legacyFound
            ? self::templateSettings($design)
            : ['sticky' => false, 'overlay' => false, 'contentWidth' => 1728];

        $version = TemplateLayoutModel::saveVersion(
            $targetId,
            $model,
            $settings,
            get_current_user_id(),
            $note
        );
        TemplateLayoutModel::rename($targetId, 'Header – Standard');
        TemplateLayoutModel::setActive($targetId, true);
        TemplateLayoutModel::setDefault('header', $targetId);

        $menu = wp_get_nav_menu_object($menuId);
        $items = $menu ? wp_get_nav_menu_items($menuId) : [];
        $result = [
            'status' => 'success',
            'convertedUtc' => gmdate('c'),
            'templateId' => $targetId,
            'templateVersion' => $version,
            'source' => $source,
            'legacyDesignFound' => !empty($stored),
            'legacyShellFound' => $shell !== '',
            'menuId' => $menuId,
            'menuName' => $menu ? (string) $menu->name : '',
            'menuItems' => is_array($items) ? count($items) : 0,
            'logoSource' => $logo['source'],
            'logoFound' => $logo['url'] !== '',
            'logoMediaId' => $logo['mediaId'],
            'logoUrl' => $logo['url'],
            'nodeCounts' => $counts,
            'digest' => LayoutModel::structuralDigest($model),
        ];
        update_option(self::STATUS_OPTION, $result, false);
        update_option(self::MIGRATION_OPTION, $result, false);
        return $result;
    }

    /** @return array<string,mixed> */
    public static function diagnosticStatus(): array
    {
        $stored = get_option(self::LEGACY_DESIGN_OPTION, []);
        $stored = is_array($stored) ? $stored : [];
        $shell = self::legacyShellHeader();
        $design = array_merge(self::defaultLegacyDesign(), $stored);
        if ($shell !== '') {
            $design = array_merge($design, self::parseShellHeader($shell));
        }
        $logo = self::resolveLogo($design);
        $menuId = self::legacyMenuId();
        $menu = $menuId > 0 ? wp_get_nav_menu_object($menuId) : false;
        $items = $menu ? wp_get_nav_menu_items($menuId) : [];

        TemplateLayoutModel::ensureMigrated();
        $targetId = TemplateLayoutModel::exists(self::TARGET_TEMPLATE_ID, 'header')
            ? self::TARGET_TEMPLATE_ID
            : TemplateLayoutModel::defaultId('header');
        $model = $targetId !== '' ? TemplateLayoutModel::model($targetId) : LayoutModel::empty();

        $last = get_option(self::STATUS_OPTION, []);
        $last = is_array($last) ? $last : [];
        return [
            'legacyDesignFound' => !empty($stored),
            'legacyShellFound' => $shell !== '',
            'fallbackAvailable' => true,
            'menuId' => $menuId,
            'menuName' => $menu ? (string) $menu->name : '',
            'menuItems' => is_array($items) ? count($items) : 0,
            'logoSource' => $logo['source'],
            'logoFound' => $logo['url'] !== '',
            'logoUrl' => $logo['url'],
            'targetTemplateId' => $targetId,
            'targetVersion' => $targetId !== '' ? TemplateLayoutModel::version($targetId) : 0,
            'targetNodeCounts' => self::nodeCounts($model),
            'lastConversion' => $last,
        ];
    }

    /**
     * Approved desktop fallback from the 2026-08-28 visual reference:
     * 90% centred Header, dark #30382a bar, logo/brand left, menu right.
     *
     * @return array<string,mixed>
     */
    public static function buildScreenshotReferenceModel(int $menuId, int $logoMediaId = 0, string $logoUrl = ''): array
    {
        $rowsDesktop = 15;
        $rowsMobile = 14;
        $brand = 'Aalborg Kaserners Veteran Panser- og Køretøjsforening';
        $nodes = [];
        $nodes[] = self::node('section-header-reference-v0143','section','',10,
            self::geometry([6,0,108,$rowsDesktop],[6,0,108,$rowsDesktop],[0,0,120,$rowsMobile]),
            ['background'=>'#30382a','radius'=>0,'padding'=>0,'minHeightRows'=>$rowsDesktop,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        $nodes[] = self::node('container-header-reference-v0143','container','section-header-reference-v0143',10,
            self::geometry([0,0,120,$rowsDesktop],[0,0,120,$rowsDesktop],[0,0,120,$rowsMobile]),
            ['background'=>'#30382a','radius'=>0,'padding'=>0,'minHeightRows'=>$rowsDesktop,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        $nodes[] = self::node('image-header-reference-logo-v0143','image','container-header-reference-v0143',10,
            self::geometry([0,1,7,13],[0,1,7,13],[0,1,20,12]),
            ['mediaId'=>max(0,$logoMediaId),'url'=>esc_url_raw($logoUrl),'alt'=>$brand,'fit'=>'contain','imageAlignX'=>'left','imageAlignY'=>'center','boxBackground'=>'#30382a','boxTransparent'=>true,'focalX'=>50,'focalY'=>50,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        $nodes[] = self::node('text-header-reference-brand-v0143','text','container-header-reference-v0143',20,
            self::geometry([8,4,28,7],[8,4,30,7],[20,3,72,8]),
            ['heading'=>'','headingLevel'=>'h2','text'=>$brand,'align'=>'left','verticalAlign'=>'center','background'=>'#30382a','backgroundTransparent'=>true,'textColor'=>'#f2f0e8','headingColor'=>'#f2f0e8','padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>19,'fontWeight'=>700,'lineHeight'=>1.18,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        $nodes[] = self::node('menu-header-reference-primary-v0143','menu','container-header-reference-v0143',30,
            self::geometry([72,4,48,7],[68,4,52,7],[95,3,25,8]),
            ['menuId'=>max(0,$menuId),'orientation'=>'horizontal','align'=>'right','mobileMode'=>'hamburger','textColor'=>'#f2f0e8','hoverTextColor'=>'#c3ae83','activeTextColor'=>'#c3ae83','background'=>'#30382a','backgroundTransparent'=>true,'fontSize'=>17,'fontWeight'=>600,'menuGap'=>22,'paddingX'=>6,'paddingY'=>8,'radius'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]);
        return LayoutModel::normalize(['schemaVersion'=>LayoutModel::SCHEMA,'units'=>LayoutModel::UNITS,'rowPx'=>LayoutModel::ROW_PX,'nodes'=>$nodes]);
    }

    /** @param array<string,mixed> $design @return array{mediaId:int,url:string,source:string} */
    private static function resolveLogo(array $design): array
    {
        $url = esc_url_raw((string) ($design['LogoUrl'] ?? ''));
        $mediaId = max(0, (int) ($design['LogoMediaId'] ?? 0));
        if ($url !== '') { return ['mediaId'=>$mediaId,'url'=>$url,'source'=>'legacy-header']; }
        if (function_exists('get_theme_mod')) {
            $id=absint(get_theme_mod('custom_logo',0)); $u=$id>0?wp_get_attachment_url($id):false;
            if ($u) return ['mediaId'=>$id,'url'=>esc_url_raw((string)$u),'source'=>'wordpress-custom-logo'];
        }
        $siteIconId=absint(get_option('site_icon',0)); $siteIconUrl=$siteIconId>0?wp_get_attachment_url($siteIconId):false;
        if ($siteIconUrl) return ['mediaId'=>$siteIconId,'url'=>esc_url_raw((string)$siteIconUrl),'source'=>'wordpress-site-icon'];

        $best=['score'=>0,'mediaId'=>0,'url'=>''];
        $attachments=get_posts(['post_type'=>'attachment','post_status'=>'inherit','post_mime_type'=>'image','posts_per_page'=>200,'orderby'=>'date','order'=>'DESC','suppress_filters'=>true]);
        foreach ((array)$attachments as $attachment) {
            if (!$attachment instanceof \WP_Post) continue;
            $file=(string)get_post_meta($attachment->ID,'_wp_attached_file',true);
            $hay=sanitize_title((string)$attachment->post_title.' '.basename($file).' '.(string)$attachment->guid);
            $score=0;
            foreach (['logo'=>70,'emblem'=>55,'veteran'=>25,'kaserne'=>25,'aalborg'=>20,'panser'=>15] as $needle=>$points) if (str_contains($hay,$needle)) $score+=$points;
            foreach (['banner'=>80,'hero'=>70,'topbanner'=>90,'header-billede'=>60] as $needle=>$points) if (str_contains($hay,$needle)) $score-=$points;
            $meta=wp_get_attachment_metadata($attachment->ID);
            if (is_array($meta) && !empty($meta['width']) && !empty($meta['height'])) {
                $ratio=(float)$meta['width']/max(1,(float)$meta['height']);
                if ($ratio>=0.75 && $ratio<=1.25) $score+=25;
                elseif ($ratio>2.0) $score-=25;
            }
            $u=wp_get_attachment_url($attachment->ID);
            if ($u && $score>$best['score']) $best=['score'=>$score,'mediaId'=>(int)$attachment->ID,'url'=>esc_url_raw((string)$u)];
        }
        if ($best['score']>=40) return ['mediaId'=>$best['mediaId'],'url'=>$best['url'],'source'=>'media-library-match'];
        if (function_exists('get_site_icon_url')) {
            $u=(string)get_site_icon_url(512,''); if ($u!=='') return ['mediaId'=>0,'url'=>esc_url_raw($u),'source'=>'wordpress-site-icon-url'];
        }
        return ['mediaId'=>0,'url'=>'','source'=>'not-found'];
    }

    /** @param array<string,mixed> $model @return array<string,int> */
    private static function nodeCounts(array $model): array
    {
        $counts = ['section' => 0, 'container' => 0, 'text' => 0, 'image' => 0, 'menu' => 0, 'button' => 0];
        foreach (($model['nodes'] ?? []) as $node) {
            if (!is_array($node)) { continue; }
            $type = sanitize_key((string) ($node['type'] ?? ''));
            if (array_key_exists($type, $counts)) { $counts[$type]++; }
        }
        return $counts;
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
        $defs = self::referenceMenuDefinitions();
        $saved = absint(get_option(self::LEGACY_ACTIVE_MENU_OPTION, 0));
        if ($saved > 0 && wp_get_nav_menu_object($saved)) {
            return $saved;
        }
        $locations = get_nav_menu_locations();
        $primary = is_array($locations) ? absint($locations['primary'] ?? 0) : 0;
        $bestId=0; $bestScore=-1;
        foreach ((array) wp_get_nav_menus() as $menu) {
            $id=(int)($menu->term_id ?? 0); if ($id<=0) continue;
            $items=wp_get_nav_menu_items($id); $items=is_array($items)?$items:[];
            $matched=[]; $score=0;
            foreach ($items as $item) {
                $titleSlug=sanitize_title(strip_tags((string)$item->title));
                $pageSlug='';
                if (($item->object ?? '')==='page' && !empty($item->object_id)) { $p=get_post((int)$item->object_id); if ($p instanceof \WP_Post) $pageSlug=sanitize_title((string)$p->post_name); }
                foreach ($defs as $def) {
                    if (isset($matched[$def['slug']])) continue;
                    if ($pageSlug===$def['slug'] || $titleSlug===sanitize_title($def['title']) || in_array($titleSlug,$def['aliases'],true)) { $matched[$def['slug']]=true; $score+=10; }
                }
            }
            if (count($items)===7) $score+=10;
            $name=sanitize_title((string)($menu->name ?? ''));
            if (str_contains($name,'hangar18') || str_contains($name,'hoved') || str_contains($name,'main')) $score+=5;
            if ($id===$saved) $score+=2; if ($id===$primary) $score+=3;
            if ($score>$bestScore) { $bestScore=$score; $bestId=$id; }
        }
        if ($bestId>0 && $bestScore>=45) return $bestId;
        return self::ensureReferenceMenu($defs);
    }

    /** @return array<int,array{slug:string,title:string,aliases:array<int,string>}> */
    private static function referenceMenuDefinitions(): array
    {
        return [
            ['slug'=>'hjem','title'=>'Hjem','aliases'=>['hjem','home']],
            ['slug'=>'events','title'=>'Events','aliases'=>['events','event']],
            ['slug'=>'koeretoejer-og-materiel','title'=>'Køretøjer','aliases'=>['koeretoejer','koeretoejer-og-materiel','koretojer']],
            ['slug'=>'billedgalleri','title'=>'Billedgalleri','aliases'=>['billedgalleri','galleri']],
            ['slug'=>'om-foreningen','title'=>'Om','aliases'=>['om','om-foreningen']],
            ['slug'=>'bliv-medlem','title'=>'Bliv medlem','aliases'=>['bliv-medlem']],
            ['slug'=>'kontakt','title'=>'Kontakt','aliases'=>['kontakt']],
        ];
    }

    private static function ensureReferenceMenu(array $defs): int
    {
        $menu=wp_get_nav_menu_object('Visual Designer Hovedmenu');
        if (!$menu) {
            $created=wp_create_nav_menu('Visual Designer Hovedmenu');
            if (is_wp_error($created)) throw new \RuntimeException('Kunne ikke oprette Visual Designer Hovedmenu: '.$created->get_error_message());
            $menu=wp_get_nav_menu_object((int)$created);
        }
        $menuId=(int)($menu->term_id ?? 0); if ($menuId<=0) throw new \RuntimeException('Visual Designer Hovedmenu fik ikke et gyldigt ID.');
        $items=wp_get_nav_menu_items($menuId); if (!is_array($items) || count($items)<count($defs)) {
            foreach ((array)$items as $item) wp_delete_post((int)$item->ID,true);
            $position=1;
            foreach ($defs as $def) {
                $page=get_page_by_path($def['slug'],OBJECT,'page');
                $args=['menu-item-title'=>$def['title'],'menu-item-position'=>$position++,'menu-item-status'=>'publish'];
                if ($page instanceof \WP_Post) $args += ['menu-item-object-id'=>(int)$page->ID,'menu-item-object'=>'page','menu-item-type'=>'post_type'];
                else $args += ['menu-item-type'=>'custom','menu-item-url'=>home_url('/'.$def['slug'].'/')];
                $result=wp_update_nav_menu_item($menuId,0,$args);
                if (is_wp_error($result)) throw new \RuntimeException('Kunne ikke opbygge Visual Designer Hovedmenu: '.$result->get_error_message());
            }
        }
        return $menuId;
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
