<?php

declare(strict_types=1);

namespace VisualDesignerManager\Frontend;

use VisualDesignerManager\Model\TemplateLayoutModel;

/**
 * Theme-shell coordination for the Visual Designer runtime.
 *
 * 0.1.49 activates the approved cutover for Visual Designer pages.
 * Non-Visual-Designer WordPress pages remain untouched as a safe fallback.
 */
final class ThemeShell
{
    public const CUTOVER_OPTION = 'h18_visual_designer_theme_shell_cutover_v1';
    private const V0149_ACTIVATED_OPTION = 'h18_visual_designer_theme_shell_cutover_v0149_activated';

    public static function register(): void
    {
        add_action('init', [self::class, 'activateApprovedCutover'], 1);
        add_filter('body_class', [self::class, 'bodyClasses'], 50);
    }

    /**
     * 0.1.49 is the explicit, user-approved cutover point. This runs once.
     * A rollback to an older plugin stays safe because older Renderers ignore
     * the flag, while non-Visual-Designer pages are never wrapped by 0.1.49.
     */
    public static function activateApprovedCutover(): void
    {
        if (get_option(self::V0149_ACTIVATED_OPTION, false)) {
            return;
        }
        update_option(self::CUTOVER_OPTION, '1', false);
        update_option(self::V0149_ACTIVATED_OPTION, [
            'activatedUtc' => gmdate('c'),
            'version' => defined('H18_CLEAN_VERSION') ? H18_CLEAN_VERSION : '0.1.49',
            'scope' => 'visual-designer-pages-only',
        ], false);
    }

    public static function enabled(): bool
    {
        return get_option(self::CUTOVER_OPTION, '0') === '1';
    }

    /** @param array<int,string> $classes @return array<int,string> */
    public static function bodyClasses(array $classes): array
    {
        $classes[] = 'h18-vd-theme-shell-ready';
        if (self::enabled()) {
            $classes[] = 'h18-vd-theme-shell-active';
        }
        return array_values(array_unique($classes));
    }

    public static function resolvedTemplateId(int $postId, string $part): string
    {
        $part = sanitize_key($part) === 'footer' ? 'footer' : 'header';
        if ($postId <= 0) {
            return '';
        }
        TemplateLayoutModel::ensureMigrated();
        return TemplateLayoutModel::resolveId($postId, $part);
    }

    /** @return array{enabled:bool,header:string,footer:string} */
    public static function status(int $postId): array
    {
        return [
            'enabled' => self::enabled(),
            'header' => self::resolvedTemplateId($postId, 'header'),
            'footer' => self::resolvedTemplateId($postId, 'footer'),
        ];
    }

    private function __construct()
    {
    }
}
