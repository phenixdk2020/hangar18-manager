<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Editor;

/**
 * Canonical, renderer-neutral design view over the existing page section schema.
 *
 * The legacy section fields remain the save/public-renderer source. v0.8.34
 * extends the same model with transition/focus/active/disabled interaction state
 * values already present in that schema; no new base-design persistence store is
 * introduced.
 */
final class LegoDesignModel
{
    public const SCHEMA_VERSION = 2;

    /** @return array<int,string> */
    public static function fonts(): array
    {
        return ['Global', 'System', 'Segoe UI', 'Arial', 'Verdana', 'Tahoma', 'Trebuchet MS', 'Georgia', 'Times New Roman', 'Courier New'];
    }

    /** @return array<int,string> */
    public static function shadows(): array
    {
        return ['None', 'Soft', 'Medium', 'Strong'];
    }

    /** @return array<int,string> */
    public static function hoverEffects(): array
    {
        return ['None', 'Lift', 'Scale', 'Shadow'];
    }

    /** @return array<int,string> */
    public static function transitionPresets(): array
    {
        return ['Inherit', 'Fast', 'Normal', 'Slow', 'Custom'];
    }

    /** @return array<int,string> */
    public static function focusStyles(): array
    {
        return ['Global', 'Custom', 'None'];
    }

    /** @return array<int,string> */
    public static function activeEffects(): array
    {
        return ['None', 'Press', 'ScaleDown'];
    }

    /**
     * Map canonical state paths to the already-persisted page section fields.
     *
     * @return array<string,string>
     */
    public static function legacyFieldMap(): array
    {
        return [
            'Mode' => 'DesignMode',
            'Colors.Background' => 'CustomBackgroundColor',
            'Colors.Text' => 'CustomTextColor',
            'Colors.Heading' => 'CustomHeadingColor',
            'Border.Width' => 'BorderWidthPx',
            'Border.Color' => 'CustomBorderColor',
            'Radius.All' => 'RadiusPx',
            'Radius.TopLeft' => 'RadiusTopLeftPx',
            'Radius.TopRight' => 'RadiusTopRightPx',
            'Radius.BottomRight' => 'RadiusBottomRightPx',
            'Radius.BottomLeft' => 'RadiusBottomLeftPx',
            'Typography.BodyFont' => 'SectionBodyFontFamily',
            'Typography.HeadingFont' => 'SectionHeadingFontFamily',
            'Typography.BodySize' => 'BodyFontSizePx',
            'Typography.H1Size' => 'H1FontSizePx',
            'Typography.H2Size' => 'H2FontSizePx',
            'Typography.H3Size' => 'H3FontSizePx',
            'Effects.Opacity' => 'SectionOpacityPercent',
            'Effects.Shadow' => 'ShadowStyle',
            'Motion.Transition' => 'TransitionPreset',
            'States.Hover.Mode' => 'HoverStyleMode',
            'States.Hover.Background' => 'HoverBackgroundColor',
            'States.Hover.Text' => 'HoverTextColor',
            'States.Hover.Heading' => 'HoverHeadingColor',
            'States.Hover.Border' => 'HoverBorderColor',
            'States.Hover.Opacity' => 'HoverOpacityPercent',
            'States.Hover.Effect' => 'HoverEffect',
            'States.Hover.TransitionMs' => 'HoverTransitionMs',
            'States.Focus.Style' => 'FocusRingStyle',
            'States.Focus.Color' => 'FocusRingColor',
            'States.Focus.Width' => 'FocusRingWidthPx',
            'States.Focus.Offset' => 'FocusRingOffsetPx',
            'States.Active.Effect' => 'ActiveEffect',
            'States.Disabled.Opacity' => 'DisabledOpacityPercent',
        ];
    }

    /**
     * Normalize existing page-section values into the shared canonical model.
     *
     * @param array<string,mixed> $legacy
     * @return array<string,mixed>
     */
    public static function fromLegacy(array $legacy): array
    {
        $mode = self::enum($legacy['DesignMode'] ?? 'Global', ['Global', 'Custom'], 'Global');
        $hoverMode = self::enum($legacy['HoverStyleMode'] ?? 'Inherit', ['Inherit', 'Custom'], 'Inherit');

        return [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Mode' => $mode,
            'Colors' => [
                'Background' => self::color($legacy['CustomBackgroundColor'] ?? '#ffffff', '#ffffff'),
                'Text' => self::color($legacy['CustomTextColor'] ?? '#30382a', '#30382a'),
                'Heading' => self::color($legacy['CustomHeadingColor'] ?? '#30382a', '#30382a'),
            ],
            'Border' => [
                'Width' => self::clamp($legacy['BorderWidthPx'] ?? 0, 0, 12, 0),
                'Color' => self::color($legacy['CustomBorderColor'] ?? '#c3ae83', '#c3ae83'),
            ],
            'Radius' => [
                'All' => self::clamp($legacy['RadiusPx'] ?? 7, 0, 30, 7),
                'TopLeft' => self::clamp($legacy['RadiusTopLeftPx'] ?? -1, -1, 60, -1),
                'TopRight' => self::clamp($legacy['RadiusTopRightPx'] ?? -1, -1, 60, -1),
                'BottomRight' => self::clamp($legacy['RadiusBottomRightPx'] ?? -1, -1, 60, -1),
                'BottomLeft' => self::clamp($legacy['RadiusBottomLeftPx'] ?? -1, -1, 60, -1),
            ],
            'Typography' => [
                'BodyFont' => self::enum($legacy['SectionBodyFontFamily'] ?? 'Global', self::fonts(), 'Global'),
                'HeadingFont' => self::enum($legacy['SectionHeadingFontFamily'] ?? 'Global', self::fonts(), 'Global'),
                'BodySize' => self::clamp($legacy['BodyFontSizePx'] ?? 0, 0, 32, 0),
                'H1Size' => self::clamp($legacy['H1FontSizePx'] ?? 0, 0, 96, 0),
                'H2Size' => self::clamp($legacy['H2FontSizePx'] ?? 0, 0, 80, 0),
                'H3Size' => self::clamp($legacy['H3FontSizePx'] ?? 0, 0, 64, 0),
            ],
            'Effects' => [
                'Opacity' => self::clamp($legacy['SectionOpacityPercent'] ?? 100, 0, 100, 100),
                'Shadow' => self::enum($legacy['ShadowStyle'] ?? 'None', self::shadows(), 'None'),
            ],
            'Motion' => [
                'Transition' => self::enum($legacy['TransitionPreset'] ?? 'Inherit', self::transitionPresets(), 'Inherit'),
            ],
            'States' => [
                'Hover' => [
                    'Mode' => $hoverMode,
                    'Background' => self::color($legacy['HoverBackgroundColor'] ?? '#ffffff', '#ffffff'),
                    'Text' => self::color($legacy['HoverTextColor'] ?? '#30382a', '#30382a'),
                    'Heading' => self::color($legacy['HoverHeadingColor'] ?? '#30382a', '#30382a'),
                    'Border' => self::color($legacy['HoverBorderColor'] ?? '#c3ae83', '#c3ae83'),
                    'Opacity' => self::clamp($legacy['HoverOpacityPercent'] ?? 100, 0, 100, 100),
                    'Effect' => self::enum($legacy['HoverEffect'] ?? 'None', self::hoverEffects(), 'None'),
                    'TransitionMs' => self::clamp($legacy['HoverTransitionMs'] ?? 220, 0, 1000, 220),
                ],
                'Focus' => [
                    'Style' => self::enum($legacy['FocusRingStyle'] ?? 'Global', self::focusStyles(), 'Global'),
                    'Color' => self::color($legacy['FocusRingColor'] ?? '#8b4a2b', '#8b4a2b'),
                    'Width' => self::clamp($legacy['FocusRingWidthPx'] ?? 3, 1, 8, 3),
                    'Offset' => self::clamp($legacy['FocusRingOffsetPx'] ?? 2, 0, 12, 2),
                ],
                'Active' => [
                    'Effect' => self::enum($legacy['ActiveEffect'] ?? 'None', self::activeEffects(), 'None'),
                ],
                'Disabled' => [
                    'Opacity' => self::clamp($legacy['DisabledOpacityPercent'] ?? 55, 10, 100, 55),
                ],
            ],
        ];
    }

    /** @return array<string,mixed> */
    public static function defaults(): array
    {
        return self::fromLegacy([]);
    }

    /**
     * Flatten canonical model values back to the existing page section field names.
     *
     * @param array<string,mixed> $state
     * @return array<string,mixed>
     */
    public static function toLegacy(array $state): array
    {
        $normalized = self::normalizeState($state);
        $result = [];
        foreach (self::legacyFieldMap() as $path => $field) {
            $result[$field] = self::valueAt($normalized, $path);
        }
        return $result;
    }

    /**
     * Normalize a canonical/partial state through the legacy contract.
     *
     * @param array<string,mixed> $state
     * @return array<string,mixed>
     */
    public static function normalizeState(array $state): array
    {
        $legacy = [];
        foreach (self::legacyFieldMap() as $path => $field) {
            $value = self::valueAt($state, $path, null);
            if ($value !== null) {
                $legacy[$field] = $value;
            }
        }
        return self::fromLegacy($legacy);
    }

    /** @param mixed $value */
    private static function clamp($value, int $min, int $max, int $fallback): int
    {
        if (!is_numeric($value)) {
            return $fallback;
        }
        return max($min, min($max, (int) $value));
    }

    /** @param mixed $value @param array<int,string> $allowed */
    private static function enum($value, array $allowed, string $fallback): string
    {
        $value = trim((string) $value);
        return in_array($value, $allowed, true) ? $value : $fallback;
    }

    /** @param mixed $value */
    private static function color($value, string $fallback): string
    {
        $value = strtolower(trim((string) $value));
        return preg_match('/^#[0-9a-f]{6}$/', $value) ? $value : $fallback;
    }

    /**
     * @param array<string,mixed> $value
     * @param mixed $fallback
     * @return mixed
     */
    private static function valueAt(array $value, string $path, $fallback = null)
    {
        $current = $value;
        foreach (explode('.', $path) as $part) {
            if (!is_array($current) || !array_key_exists($part, $current)) {
                return $fallback;
            }
            $current = $current[$part];
        }
        return $current;
    }
}
