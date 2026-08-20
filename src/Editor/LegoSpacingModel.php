<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Editor;

/**
 * Canonical, renderer-neutral responsive X/Y spacing model for Ultimate Designer LEGO elements.
 *
 * The model owns only normalized editor state. It deliberately does not own drag/drop,
 * parent/child placement, history or public rendering. Tablet/Mobile can inherit the
 * effective Desktop spacing without deleting their stored override values.
 */
final class LegoSpacingModel
{
    public const SCHEMA_VERSION = 2;
    public const DESKTOP_MAX = 160;
    public const TABLET_MAX = 160;
    public const MOBILE_MAX = 120;

    /**
     * Normalize v0.8.30 schema-1 and v0.8.31 schema-2 data into one schema-2 state.
     *
     * Migration rules:
     * - Desktop is always explicit.
     * - Tablet defaults to inheritance from Desktop.
     * - Existing schema-1 Mobile values remain explicit overrides (no visual drift).
     * - Mobile without stored state keeps the legacy MobileLayoutGapPx fallback.
     *
     * @param array<string,mixed> $raw
     * @param array<string,mixed> $legacy
     * @return array<string,mixed>
     */
    public static function normalize(array $raw, array $legacy = []): array
    {
        $desktopLegacyGap = self::clamp($legacy['LayoutGapPx'] ?? 16, 0, self::DESKTOP_MAX, 16);
        $mobileLegacyGap = self::clamp($legacy['MobileLayoutGapPx'] ?? 12, 0, self::MOBILE_MAX, 12);

        $desktopRaw = isset($raw['Desktop']) && is_array($raw['Desktop']) ? $raw['Desktop'] : [];
        $tabletRaw = isset($raw['Tablet']) && is_array($raw['Tablet']) ? $raw['Tablet'] : [];
        $mobileRaw = isset($raw['Mobile']) && is_array($raw['Mobile']) ? $raw['Mobile'] : [];

        $desktop = [
            'Margin' => self::axisPair($desktopRaw['Margin'] ?? [], 0, self::DESKTOP_MAX, 0, 0),
            'Gap' => self::axisPair($desktopRaw['Gap'] ?? [], 0, self::DESKTOP_MAX, $desktopLegacyGap, $desktopLegacyGap),
        ];

        $tablet = [
            'InheritDesktop' => array_key_exists('InheritDesktop', $tabletRaw)
                ? self::toBool($tabletRaw['InheritDesktop'])
                : true,
            'Margin' => self::axisPair(
                $tabletRaw['Margin'] ?? [],
                0,
                self::TABLET_MAX,
                (int) $desktop['Margin']['X'],
                (int) $desktop['Margin']['Y']
            ),
            'Gap' => self::axisPair(
                $tabletRaw['Gap'] ?? [],
                0,
                self::TABLET_MAX,
                (int) $desktop['Gap']['X'],
                (int) $desktop['Gap']['Y']
            ),
        ];

        $mobile = [
            // Schema-1 had explicit Mobile values. Missing inheritance therefore means override.
            'InheritDesktop' => array_key_exists('InheritDesktop', $mobileRaw)
                ? self::toBool($mobileRaw['InheritDesktop'])
                : false,
            'Margin' => self::axisPair($mobileRaw['Margin'] ?? [], 0, self::MOBILE_MAX, 0, 0),
            'Gap' => self::axisPair($mobileRaw['Gap'] ?? [], 0, self::MOBILE_MAX, $mobileLegacyGap, $mobileLegacyGap),
        ];

        return [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Desktop' => $desktop,
            'Tablet' => $tablet,
            'Mobile' => $mobile,
        ];
    }

    /**
     * @param array<string,mixed> $legacy
     * @return array<string,mixed>
     */
    public static function defaults(array $legacy = []): array
    {
        return self::normalize([], $legacy);
    }

    /**
     * Return the effective Margin/Gap pair for one device after inheritance.
     *
     * @param array<string,mixed> $raw
     * @return array{Margin:array{X:int,Y:int},Gap:array{X:int,Y:int},Inherited:bool}
     */
    public static function effective(array $raw, string $device): array
    {
        $state = self::normalize($raw);
        $device = ucfirst(strtolower($device));
        if (!in_array($device, ['Desktop', 'Tablet', 'Mobile'], true)) {
            $device = 'Desktop';
        }

        if ($device === 'Desktop') {
            return [
                'Margin' => $state['Desktop']['Margin'],
                'Gap' => $state['Desktop']['Gap'],
                'Inherited' => false,
            ];
        }

        $requested = $state[$device];
        if (!empty($requested['InheritDesktop'])) {
            return [
                'Margin' => $state['Desktop']['Margin'],
                'Gap' => $state['Desktop']['Gap'],
                'Inherited' => true,
            ];
        }

        return [
            'Margin' => $requested['Margin'],
            'Gap' => $requested['Gap'],
            'Inherited' => false,
        ];
    }

    /**
     * @param mixed $raw
     * @return array{X:int,Y:int}
     */
    private static function axisPair($raw, int $min, int $max, int $fallbackX, int $fallbackY): array
    {
        $raw = is_array($raw) ? $raw : [];
        return [
            'X' => self::clamp($raw['X'] ?? $fallbackX, $min, $max, $fallbackX),
            'Y' => self::clamp($raw['Y'] ?? $fallbackY, $min, $max, $fallbackY),
        ];
    }

    /** @param mixed $value */
    private static function clamp($value, int $min, int $max, int $fallback): int
    {
        if (!is_numeric($value)) {
            return $fallback;
        }
        return max($min, min($max, (int) $value));
    }

    /** @param mixed $value */
    private static function toBool($value): bool
    {
        if (is_bool($value)) {
            return $value;
        }
        if (is_int($value) || is_float($value)) {
            return (int) $value !== 0;
        }
        return in_array(strtolower(trim((string) $value)), ['1', 'true', 'yes', 'on'], true);
    }
}
