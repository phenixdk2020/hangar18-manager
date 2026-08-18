<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\DynamicData;

/**
 * Validates UD-060 presets against the field capabilities already delivered by
 * the generic UD-051/UD-054 data motor. No WordPress functions are required.
 */
final class StarterSchemaPresetValidator
{
    /** @var list<string> */
    private const FIELD_TYPES = ['text', 'number', 'bool', 'date', 'media', 'relation', 'group', 'repeater'];

    /** @var list<string> */
    private const NESTED_FIELD_TYPES = ['text', 'number', 'bool', 'date', 'media'];

    /** @param array<string,array<string,mixed>> $presets @return list<string> */
    public function validateCatalog(array $presets): array
    {
        $errors = [];

        if (array_keys($presets) !== StarterSchemaPresetCatalog::PRESET_KEYS) {
            $errors[] = 'Starter catalog must contain exactly vehicle, event and gallery in canonical order.';
        }

        foreach ($presets as $presetKey => $preset) {
            foreach ($this->validatePreset((string) $presetKey, $preset, array_keys($presets)) as $error) {
                $errors[] = $error;
            }
        }

        return array_values(array_unique($errors));
    }

    /** @param array<string,mixed> $preset @param list<string> $catalogKeys @return list<string> */
    public function validatePreset(string $presetKey, array $preset, array $catalogKeys = StarterSchemaPresetCatalog::PRESET_KEYS): array
    {
        $errors = [];
        $domain = (string) ($preset['Domain'] ?? '');
        $schema = $preset['Schema'] ?? null;

        if (($preset['PresetVersion'] ?? null) !== StarterSchemaPresetCatalog::PRESET_VERSION) {
            $errors[] = "Preset '{$presetKey}' has wrong PresetVersion.";
        }
        if ($domain !== $presetKey) {
            $errors[] = "Preset '{$presetKey}' Domain must match its key.";
        }
        if (!is_array($schema)) {
            $errors[] = "Preset '{$presetKey}' has no Schema.";
            return $errors;
        }
        if (($schema['Key'] ?? null) !== $presetKey) {
            $errors[] = "Preset '{$presetKey}' schema Key must match preset key.";
        }
        if (($schema['SchemaVersion'] ?? null) !== StarterSchemaPresetCatalog::GENERIC_SCHEMA_VERSION) {
            $errors[] = "Preset '{$presetKey}' must use generic SchemaVersion " . StarterSchemaPresetCatalog::GENERIC_SCHEMA_VERSION . '.';
        }
        if (!is_string($schema['SingularLabel'] ?? null) || trim((string) $schema['SingularLabel']) === '') {
            $errors[] = "Preset '{$presetKey}' needs SingularLabel.";
        }
        if (!is_string($schema['PluralLabel'] ?? null) || trim((string) $schema['PluralLabel']) === '') {
            $errors[] = "Preset '{$presetKey}' needs PluralLabel.";
        }
        if (!isset($preset['EntryTitle']['Required']) || $preset['EntryTitle']['Required'] !== true) {
            $errors[] = "Preset '{$presetKey}' must require the generic entry title.";
        }

        $fields = $schema['Fields'] ?? null;
        if (!is_array($fields) || $fields === []) {
            $errors[] = "Preset '{$presetKey}' must contain fields.";
            return $errors;
        }

        $used = [];
        foreach (array_values($fields) as $index => $field) {
            if (!is_array($field)) {
                $errors[] = "Preset '{$presetKey}' field {$index} is invalid.";
                continue;
            }

            $key = (string) ($field['Key'] ?? '');
            $label = (string) ($field['Label'] ?? '');
            $type = (string) ($field['Type'] ?? '');

            if ($key === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{1,47}$/', $key)) {
                $errors[] = "Preset '{$presetKey}' field {$index} has invalid Key.";
            } elseif (isset($used[$key])) {
                $errors[] = "Preset '{$presetKey}' duplicates field '{$key}'.";
            }
            $used[$key] = true;

            if ($label === '') {
                $errors[] = "Preset '{$presetKey}' field '{$key}' has no Label.";
            }
            if (!in_array($type, self::FIELD_TYPES, true)) {
                $errors[] = "Preset '{$presetKey}' field '{$key}' uses unsupported Type '{$type}'.";
                continue;
            }

            if ($type === 'relation') {
                $target = (string) ($field['RelationTargetType'] ?? '');
                if ($target === '' || !in_array($target, $catalogKeys, true)) {
                    $errors[] = "Preset '{$presetKey}' relation '{$key}' targets unknown preset '{$target}'.";
                }
            }

            if (in_array($type, ['group', 'repeater'], true)) {
                $nested = $field['NestedFields'] ?? null;
                if (!is_array($nested) || $nested === []) {
                    $errors[] = "Preset '{$presetKey}' field '{$key}' needs NestedFields.";
                } else {
                    $nestedUsed = [];
                    foreach (array_values($nested) as $nestedIndex => $nestedField) {
                        if (!is_array($nestedField)) {
                            $errors[] = "Preset '{$presetKey}' field '{$key}' nested field {$nestedIndex} is invalid.";
                            continue;
                        }
                        $nestedKey = (string) ($nestedField['Key'] ?? '');
                        $nestedType = (string) ($nestedField['Type'] ?? '');
                        if ($nestedKey === '' || isset($nestedUsed[$nestedKey])) {
                            $errors[] = "Preset '{$presetKey}' field '{$key}' has invalid/duplicate nested key '{$nestedKey}'.";
                        }
                        $nestedUsed[$nestedKey] = true;
                        if (!in_array($nestedType, self::NESTED_FIELD_TYPES, true)) {
                            $errors[] = "Preset '{$presetKey}' field '{$key}' nested field '{$nestedKey}' uses unsupported Type '{$nestedType}'.";
                        }
                    }
                }
            }

            if ($type === 'repeater') {
                $max = (int) ($field['RepeaterMaxItems'] ?? 0);
                if ($max < 1 || $max > 20) {
                    $errors[] = "Preset '{$presetKey}' repeater '{$key}' must allow 1-20 items.";
                }
            }
        }

        $legacy = $preset['LegacyCompatibility'] ?? null;
        if (!is_array($legacy) || trim((string) ($legacy['ParentSlug'] ?? '')) === '' || trim((string) ($legacy['Marker'] ?? '')) === '') {
            $errors[] = "Preset '{$presetKey}' must declare legacy ParentSlug and Marker.";
        }

        return $errors;
    }

    /** @param array<string,array<string,mixed>> $presets */
    public function assertCatalogValid(array $presets): void
    {
        $errors = $this->validateCatalog($presets);
        if ($errors !== []) {
            throw new \RuntimeException('Invalid starter schema catalog: ' . implode(' ', $errors));
        }
    }
}
