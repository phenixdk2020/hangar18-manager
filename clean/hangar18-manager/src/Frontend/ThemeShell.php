<?php

declare(strict_types=1);

namespace Hangar18\Clean\Frontend;

use Hangar18\Clean\Model\TemplateLayoutModel;

/**
 * Theme-shell coordination for the Visual Designer runtime.
 *
 * 0.1.31 deliberately prepares the cutover contract without replacing the
 * current Hangar18 Base Theme rendering. Header/Footer activation remains an
 * explicit later step after visual parity has passed on Desktop/Laptop/Mobile.
 */
final class ThemeShell
{
    public const CUTOVER_OPTION = 'h18_visual_designer_theme_shell_cutover_v1';

    public static function register(): void
    {
        add_filter('body_class', [self::class, 'bodyClasses'], 50);
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
