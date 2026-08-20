<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Editor;

/**
 * Canonical, renderer-neutral X/Y spacing model for Ultimate Designer LEGO elements.
 *
 * This model deliberately does not own drag/drop, history or public rendering.
 * It is an additive editor-state overlay that can be persisted, backed up and
 * restored independently while legacy LayoutGapPx remains the compatibility
 * fallback until a later controlled public cutover.
 */
final class LegoSpacingModel
{
    public const SCHEMA_VERSION = 1;
    public const DESKTOP_MAX = 160;
    public const MOBILE_MAX = 120;

    /**
     * @param array<string,mixed> $raw
     * @param array<string,mixed> $legacy
     * @return array<string,mixed>
     */
    public static function normalize(array $raw, array $legacy = []): array
    {
        $desktopLegacyGap = self::clamp($legacy['LayoutGapPx'] ?? 16, 0, self::DESKTOP_MAX, 16);
        $mobileLegacyGap = self::clamp($legacy['MobileLayoutGapPx'] ?? 12, 0, self::MOBILE_MAX, 12);

        $desktop = isset($raw['Desktop']) && is_array($raw['Desktop']) ? $raw['Desktop'] : [];
        $mobile = isset($raw['Mobile']) && is_array($raw['Mobile']) ? $raw['Mobile'] : [];

        return [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Desktop' => [
                'Margin' => self::axisPair($desktop['Margin'] ?? [], 0, self::DESKTOP_MAX, 0, 0),
                'Gap' => self::axisPair($desktop['Gap'] ?? [], 0, self::DESKTOP_MAX, $desktopLegacyGap, $desktopLegacyGap),
            ],
            'Mobile' => [
                'Margin' => self::axisPair($mobile['Margin'] ?? [], 0, self::MOBILE_MAX, 0, 0),
                'Gap' => self::axisPair($mobile['Gap'] ?? [], 0, self::MOBILE_MAX, $mobileLegacyGap, $mobileLegacyGap),
            ],
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
}
