<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Editor;

/**
 * Additive responsive overlay for the v0.8.32 common LEGO design model.
 *
 * Desktop is never duplicated here: it remains the canonical legacy-backed
 * LegoDesignModel state. Tablet/Mobile keep reversible override snapshots and
 * may inherit the current Desktop state without deleting those snapshots.
 */
final class LegoResponsiveDesignModel
{
    public const SCHEMA_VERSION = 1;

    /**
     * @param array<string,mixed> $raw
     * @param array<string,mixed> $desktop
     * @return array<string,mixed>
     */
    public static function normalize(array $raw, array $desktop): array
    {
        $desktop = LegoDesignModel::normalizeState($desktop);
        $tablet = isset($raw['Tablet']) && is_array($raw['Tablet']) ? $raw['Tablet'] : [];
        $mobile = isset($raw['Mobile']) && is_array($raw['Mobile']) ? $raw['Mobile'] : [];

        return [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Tablet' => self::normalizeDevice($tablet, $desktop),
            'Mobile' => self::normalizeDevice($mobile, $desktop),
        ];
    }

    /**
     * @param array<string,mixed> $desktop
     * @return array<string,mixed>
     */
    public static function defaults(array $desktop): array
    {
        return self::normalize([], $desktop);
    }

    /**
     * Return the effective design for one device. Inherited devices are always
     * a live view of the current Desktop state; stored override snapshots remain
     * untouched until inheritance is disabled again.
     *
     * @param array<string,mixed> $responsive
     * @param array<string,mixed> $desktop
     * @return array{Design:array<string,mixed>,Inherited:bool,HasOverride:bool}
     */
    public static function effective(array $responsive, array $desktop, string $device): array
    {
        $desktop = LegoDesignModel::normalizeState($desktop);
        $responsive = self::normalize($responsive, $desktop);
        $device = in_array($device, ['Desktop', 'Tablet', 'Mobile'], true) ? $device : 'Desktop';

        if ($device === 'Desktop') {
            return ['Design'=>$desktop, 'Inherited'=>false, 'HasOverride'=>false];
        }

        $entry = $responsive[$device];
        if (!empty($entry['InheritDesktop'])) {
            return [
                'Design'=>$desktop,
                'Inherited'=>true,
                'HasOverride'=>!empty($entry['HasOverride']),
            ];
        }

        return [
            'Design'=>LegoDesignModel::normalizeState((array)($entry['Design'] ?? [])),
            'Inherited'=>false,
            'HasOverride'=>!empty($entry['HasOverride']),
        ];
    }

    /**
     * Produce the state transition used when inheritance is toggled. If a device
     * has never owned an override, its first transition away from Desktop is
     * seeded from the *current* Desktop state. Existing overrides are preserved.
     *
     * @param array<string,mixed> $responsive
     * @param array<string,mixed> $desktop
     * @return array<string,mixed>
     */
    public static function setInheritance(array $responsive, array $desktop, string $device, bool $inherit): array
    {
        $desktop = LegoDesignModel::normalizeState($desktop);
        $responsive = self::normalize($responsive, $desktop);
        if (!in_array($device, ['Tablet', 'Mobile'], true)) {
            return $responsive;
        }

        if (!$inherit && empty($responsive[$device]['HasOverride'])) {
            $responsive[$device]['Design'] = $desktop;
            $responsive[$device]['HasOverride'] = true;
        }
        $responsive[$device]['InheritDesktop'] = $inherit;
        return $responsive;
    }

    /**
     * @param array<string,mixed> $raw
     * @param array<string,mixed> $desktop
     * @return array<string,mixed>
     */
    private static function normalizeDevice(array $raw, array $desktop): array
    {
        $inherit = array_key_exists('InheritDesktop', $raw)
            ? self::boolValue($raw['InheritDesktop'], true)
            : true;
        $hasDesign = isset($raw['Design']) && is_array($raw['Design']);
        $hasOverride = array_key_exists('HasOverride', $raw)
            ? self::boolValue($raw['HasOverride'], $hasDesign && !$inherit)
            : ($hasDesign && !$inherit);
        $design = $hasDesign
            ? LegoDesignModel::normalizeState($raw['Design'])
            : $desktop;

        return [
            'InheritDesktop' => $inherit,
            'HasOverride' => $hasOverride,
            'Design' => $design,
        ];
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
            return ((int)$value) !== 0;
        }
        return in_array(strtolower(trim((string)$value)), ['1','true','yes','on'], true);
    }
}
