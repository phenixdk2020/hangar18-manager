<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Editor;

/**
 * Canonical renderer-neutral LEGO column-span state.
 *
 * Span 0 means Auto and is resolved by the editor from sibling count.
 * Explicit spans are 1..12. Tablet/Mobile keep reversible override snapshots:
 * inheritance may be enabled without deleting the stored device span.
 *
 * This model owns no drag/drop, parent relation, history stack or public render.
 */
final class LegoLayoutSpanModel
{
    public const SCHEMA_VERSION = 2;
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

        return [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Desktop' => [
                'Span' => self::span($desktopRaw['Span'] ?? 0),
            ],
            'Tablet' => self::normalizeDevice($tabletRaw),
            'Mobile' => self::normalizeDevice($mobileRaw),
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
        if (!in_array($device, ['Desktop', 'Tablet', 'Mobile'], true)) {
            $device = 'Desktop';
        }
        if ($device === 'Desktop') {
            return (int) $state['Desktop']['Span'];
        }
        if (!empty($state[$device]['InheritDesktop'])) {
            return (int) $state['Desktop']['Span'];
        }
        return (int) $state[$device]['Span'];
    }

    /**
     * Toggle responsive inheritance without deleting an existing override.
     * First transition away from Desktop may be seeded from the currently
     * resolved Desktop span supplied by the editor runtime.
     *
     * @param array<string,mixed> $raw
     * @return array<string,mixed>
     */
    public static function setInheritance(array $raw, string $device, bool $inherit, int $seedSpan = 0): array
    {
        $state = self::normalize($raw);
        $device = ucfirst(strtolower($device));
        if (!in_array($device, ['Tablet', 'Mobile'], true)) {
            return $state;
        }

        if (!$inherit && empty($state[$device]['HasOverride'])) {
            $state[$device]['Span'] = self::span($seedSpan);
            $state[$device]['HasOverride'] = true;
        }
        $state[$device]['InheritDesktop'] = $inherit;
        return self::normalize($state);
    }

    /**
     * Set one explicit span. Responsive writes automatically create/activate
     * an override while Desktop remains the canonical default.
     *
     * @param array<string,mixed> $raw
     * @return array<string,mixed>
     */
    public static function setSpan(array $raw, string $device, int $span): array
    {
        $state = self::normalize($raw);
        $device = ucfirst(strtolower($device));
        if ($device === 'Desktop') {
            $state['Desktop']['Span'] = self::span($span);
            return self::normalize($state);
        }
        if (!in_array($device, ['Tablet', 'Mobile'], true)) {
            return $state;
        }
        $state[$device]['Span'] = self::span($span);
        $state[$device]['InheritDesktop'] = false;
        $state[$device]['HasOverride'] = true;
        return self::normalize($state);
    }

    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function normalizeDevice(array $raw): array
    {
        $inherit = array_key_exists('InheritDesktop', $raw)
            ? self::boolValue($raw['InheritDesktop'], true)
            : true;
        $span = self::span($raw['Span'] ?? 0);
        $hasOverride = array_key_exists('HasOverride', $raw)
            ? self::boolValue($raw['HasOverride'], !$inherit)
            : (!$inherit || $span > 0);

        return [
            'InheritDesktop' => $inherit,
            'HasOverride' => $hasOverride,
            'Span' => $span,
        ];
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
