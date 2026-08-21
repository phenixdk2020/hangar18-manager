<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Editor;

/**
 * Canonical interaction-state subset of LegoDesignModel.
 *
 * This is not a separate persistence domain. It is the Focus/Active/Disabled
 * and transition slice of the same design contract and is merged back into the
 * v0.8.33 responsive device Design snapshots on save.
 */
final class LegoInteractionStateModel
{
    public const SCHEMA_VERSION = 1;

    /**
     * @param array<string,mixed> $design
     * @return array<string,mixed>
     */
    public static function fromDesign(array $design): array
    {
        $design = LegoDesignModel::normalizeState($design);
        return [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Motion' => [
                'Transition' => (string)($design['Motion']['Transition'] ?? 'Inherit'),
            ],
            'Focus' => [
                'Style' => (string)($design['States']['Focus']['Style'] ?? 'Global'),
                'Color' => (string)($design['States']['Focus']['Color'] ?? '#8b4a2b'),
                'Width' => (int)($design['States']['Focus']['Width'] ?? 3),
                'Offset' => (int)($design['States']['Focus']['Offset'] ?? 2),
            ],
            'Active' => [
                'Effect' => (string)($design['States']['Active']['Effect'] ?? 'None'),
            ],
            'Disabled' => [
                'Opacity' => (int)($design['States']['Disabled']['Opacity'] ?? 55),
            ],
        ];
    }

    /**
     * @param array<string,mixed> $raw
     * @param array<string,mixed> $fallbackDesign
     * @return array<string,mixed>
     */
    public static function normalize(array $raw, array $fallbackDesign): array
    {
        $fallback = self::fromDesign($fallbackDesign);
        $motion = isset($raw['Motion']) && is_array($raw['Motion']) ? $raw['Motion'] : [];
        $focus = isset($raw['Focus']) && is_array($raw['Focus']) ? $raw['Focus'] : [];
        $active = isset($raw['Active']) && is_array($raw['Active']) ? $raw['Active'] : [];
        $disabled = isset($raw['Disabled']) && is_array($raw['Disabled']) ? $raw['Disabled'] : [];

        return [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'Motion' => [
                'Transition' => self::enum(
                    $motion['Transition'] ?? $fallback['Motion']['Transition'],
                    LegoDesignModel::transitionPresets(),
                    (string)$fallback['Motion']['Transition']
                ),
            ],
            'Focus' => [
                'Style' => self::enum($focus['Style'] ?? $fallback['Focus']['Style'], LegoDesignModel::focusStyles(), (string)$fallback['Focus']['Style']),
                'Color' => self::color($focus['Color'] ?? $fallback['Focus']['Color'], (string)$fallback['Focus']['Color']),
                'Width' => self::clamp($focus['Width'] ?? $fallback['Focus']['Width'], 1, 8, (int)$fallback['Focus']['Width']),
                'Offset' => self::clamp($focus['Offset'] ?? $fallback['Focus']['Offset'], 0, 12, (int)$fallback['Focus']['Offset']),
            ],
            'Active' => [
                'Effect' => self::enum($active['Effect'] ?? $fallback['Active']['Effect'], LegoDesignModel::activeEffects(), (string)$fallback['Active']['Effect']),
            ],
            'Disabled' => [
                'Opacity' => self::clamp($disabled['Opacity'] ?? $fallback['Disabled']['Opacity'], 10, 100, (int)$fallback['Disabled']['Opacity']),
            ],
        ];
    }

    /**
     * Merge only this sub-contract into an existing common design snapshot.
     *
     * @param array<string,mixed> $design
     * @param array<string,mixed> $interaction
     * @return array<string,mixed>
     */
    public static function mergeIntoDesign(array $design, array $interaction): array
    {
        $design = LegoDesignModel::normalizeState($design);
        $interaction = self::normalize($interaction, $design);
        $design['Motion']['Transition'] = $interaction['Motion']['Transition'];
        $design['States']['Focus'] = $interaction['Focus'];
        $design['States']['Active'] = $interaction['Active'];
        $design['States']['Disabled'] = $interaction['Disabled'];
        return LegoDesignModel::normalizeState($design);
    }

    /** @param mixed $value @param array<int,string> $allowed */
    private static function enum($value, array $allowed, string $fallback): string
    {
        $value = trim((string)$value);
        return in_array($value, $allowed, true) ? $value : $fallback;
    }

    /** @param mixed $value */
    private static function color($value, string $fallback): string
    {
        $value = strtolower(trim((string)$value));
        return preg_match('/^#[0-9a-f]{6}$/', $value) ? $value : $fallback;
    }

    /** @param mixed $value */
    private static function clamp($value, int $min, int $max, int $fallback): int
    {
        if (!is_numeric($value)) {
            return $fallback;
        }
        return max($min, min($max, (int)$value));
    }
}
