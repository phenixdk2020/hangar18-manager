<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

use InvalidArgumentException;

/** UD-065..072 declarative Site Builder presentation presets. */
final class SiteBuilderPresetCatalog
{
    /** @return array<string,array<string,mixed>> */
    public static function all(): array
    {
        return [
            'transparent-scrolled' => [
                'Task' => 'UD-065', 'Kind' => 'header-state', 'Label' => 'Transparent → solid',
                'Config' => [
                    'Position' => 'overlay', 'InitialBackground' => 'transparent', 'ScrolledBackground' => 'surface',
                    'InitialHeightPx' => 96, 'ScrolledHeightPx' => 68, 'InitialLogoScalePercent' => 100,
                    'ScrolledLogoScalePercent' => 82, 'TransitionMs' => 260, 'ReducedMotion' => 'instant',
                ],
            ],
            'sticky-shrink' => [
                'Task' => 'UD-066', 'Kind' => 'header-state', 'Label' => 'Sticky shrink',
                'Config' => [
                    'Position' => 'sticky', 'InitialHeightPx' => 88, 'ScrolledHeightPx' => 64,
                    'InitialLogoScalePercent' => 100, 'ScrolledLogoScalePercent' => 84,
                    'TransitionMs' => 220, 'ReserveInitialHeight' => true, 'ReducedMotion' => 'instant',
                ],
            ],
            'floating-pill' => [
                'Task' => 'UD-067', 'Kind' => 'navigation', 'Label' => 'Floating pill',
                'Config' => [
                    'MaxWidthPx' => 1180, 'ViewportMarginPx' => 16, 'RadiusPx' => 999,
                    'BackdropBlurPx' => 12, 'Shadow' => 'medium', 'MobileMarginPx' => 12,
                ],
            ],
            'mega-menu' => [
                'Task' => 'UD-068', 'Kind' => 'navigation', 'Label' => 'Mega menu',
                'Config' => [
                    'PanelColumnsMin' => 3, 'PanelColumnsMax' => 5, 'ComponentPanels' => true,
                    'Animation' => 'fade-y', 'TranslateYPx' => 8, 'DurationMs' => 190,
                    'Keyboard' => true, 'ReducedMotion' => 'instant',
                ],
            ],
            'off-canvas-mobile' => [
                'Task' => 'UD-069', 'Kind' => 'navigation', 'Label' => 'Off-canvas mobile',
                'Config' => [
                    'Side' => 'right', 'WidthVw' => 90, 'OverlayOpacity' => 0.45,
                    'FocusTrap' => true, 'EscapeCloses' => true, 'ScrollLock' => true,
                    'ReducedMotion' => 'instant',
                ],
            ],
            'fullscreen-overlay' => [
                'Task' => 'UD-070', 'Kind' => 'navigation', 'Label' => 'Fullscreen overlay',
                'Config' => [
                    'Width' => '100vw', 'Height' => '100vh', 'FocusTrap' => true,
                    'EscapeCloses' => true, 'ScrollLock' => true, 'ItemStaggerMs' => 30,
                    'ReducedMotion' => 'no-stagger',
                ],
            ],
            'side-rail' => [
                'Task' => 'UD-071', 'Kind' => 'navigation', 'Label' => 'Side rail',
                'Config' => ['Placement' => 'side', 'DataSource' => 'same-menu', 'Collapsible' => true],
            ],
            'bottom-mobile' => [
                'Task' => 'UD-071', 'Kind' => 'navigation', 'Label' => 'Bottom mobile navigation',
                'Config' => ['Placement' => 'bottom', 'DataSource' => 'same-menu', 'MaxPrimaryItems' => 5, 'SafeAreaInset' => true],
            ],
            'motion-underline' => [
                'Task' => 'UD-072', 'Kind' => 'motion', 'Label' => 'Underline',
                'Config' => ['Effect' => 'underline', 'DurationMs' => 180, 'LayoutShift' => false, 'ReducedMotion' => 'instant'],
            ],
            'motion-pill' => [
                'Task' => 'UD-072', 'Kind' => 'motion', 'Label' => 'Pill',
                'Config' => ['Effect' => 'pill', 'DurationMs' => 180, 'LayoutShift' => false, 'ReducedMotion' => 'instant'],
            ],
            'motion-slide' => [
                'Task' => 'UD-072', 'Kind' => 'motion', 'Label' => 'Slide',
                'Config' => ['Effect' => 'slide', 'DurationMs' => 180, 'LayoutShift' => false, 'ReducedMotion' => 'instant'],
            ],
            'motion-icon' => [
                'Task' => 'UD-072', 'Kind' => 'motion', 'Label' => 'Icon',
                'Config' => ['Effect' => 'icon', 'DurationMs' => 180, 'LayoutShift' => false, 'ReducedMotion' => 'instant'],
            ],
        ];
    }

    /** @return array<string,mixed> */
    public static function get(string $key): array
    {
        $all = self::all();
        if (!isset($all[$key])) {
            throw new InvalidArgumentException("Unknown Site Builder preset '{$key}'.");
        }
        return $all[$key];
    }

    private function __construct() {}
}
