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
     * @param array<string,mixed> $responsive
     * @param array<string,mixed> $desktop
     * @return array{Design:array<string,mixed>,Inherited:bool}
     */
    public static function effective(array $responsive, array $desktop, string $device): array
    {
        $desktop = LegoDesignModel::normalizeState($desktop);
        $responsive = self::normalize($responsive, $desktop);
        $device = in_array($device, ['Desktop', 'Tablet', 'Mobile'], true) ? $device : 'Desktop';

        if ($device === 'Desktop') {
            return ['Design'=>$desktop, 'Inherited'=>false];
        }
        $entry = $responsive[$device];
        if (!empty($entry['InheritDesktop'])) {
            return ['Design'=>$desktop, 'Inherited'=>true];
        }
        return ['Design'=>LegoDesignModel::normalizeState((array)($entry['Design'] ?? [])), 'Inherited'=>false];
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
        $design = isset($raw['Design']) && is_array($raw['Design'])
            ? LegoDesignModel::normalizeState($raw['Design'])
            : $desktop;

        return [
            'InheritDesktop' => $inherit,
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
