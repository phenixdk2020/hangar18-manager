<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Editor;

/**
 * Canonical renderer-neutral LEGO column-span state.
 *
 * Span 0 means Auto and is resolved by the editor from the sibling count.
 * Explicit spans are 1..12. Tablet/Mobile inherit Desktop in LEGO-032;
 * explicit responsive overrides are reserved for LEGO-033.
 *
 * This model owns no drag/drop, parent relation, history stack or public render.
 */
final class LegoLayoutSpanModel
{
    public const SCHEMA_VERSION = 1;
    public const COLUMN_COUNT = 12;

    /**
     * @param array<string,mixed> $raw
     * @return array<string,mixed>
     */
    public static function normalize(array $raw): array
    {
        $desktopRaw = isset($raw['Desktop']) && is_array($raw['Desktop']) ? $raw['Desktop'] : [];
        $tabletRaw = isset($raw['Tablet']) && is_array($raw['Tablet']) ? $raw['Tablet'] : [];
        $mobileRaw = isset($raw['Mobile']) && is_array($raw['Mobile']) ? $raw['Mobile'] : [];

        $desktopSpan = self::span($desktopRaw['Span'] ?? 0);

        return [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Desktop' => [
                'Span' => $desktopSpan,
            ],
            'Tablet' => [
                'InheritDesktop' => true,
                'Span' => self::span($tabletRaw['Span'] ?? 0),
            ],
            'Mobile' => [
                'InheritDesktop' => true,
                'Span' => self::span($mobileRaw['Span'] ?? 0),
            ],
        ];
    }

    /** @return array<string,mixed> */
    public static function defaults(): array
    {
        return self::normalize([]);
    }

    /**
     * Return the effective explicit span for a device. Zero still means Auto;
     * sibling-aware Auto distribution belongs to the editor runtime.
     *
     * @param array<string,mixed> $raw
     */
    public static function effectiveSpan(array $raw, string $device): int
    {
        $state = self::normalize($raw);
        $device = ucfirst(strtolower($device));
        if ($device === 'Tablet' || $device === 'Mobile') {
            return (int) $state['Desktop']['Span'];
        }
        return (int) $state['Desktop']['Span'];
    }

    /** @param mixed $value */
    private static function span($value): int
    {
        if (!is_numeric($value)) {
            return 0;
        }
        $span = (int) $value;
        if ($span <= 0) {
            return 0;
        }
        return max(1, min(self::COLUMN_COUNT, $span));
    }
}
