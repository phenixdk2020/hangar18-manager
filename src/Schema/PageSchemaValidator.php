<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Schema;

use Hangar18\UltimateDesigner\Contracts\SchemaValidator;
use Hangar18\UltimateDesigner\Core\Version;
use RuntimeException;

/**
 * Structural validator for the normalized v0.5.30 page editor state.
 *
 * This validates the compatibility envelope and layout tree only. Element
 * property validation belongs to the element/property registries and can be
 * added incrementally without changing the stored v0.5.30 format.
 */
final class PageSchemaValidator implements SchemaValidator
{
    private const MAX_SECTIONS = 25;
    private const MAX_LAYOUT_DEPTH = 3;
    private const LAYOUT_PARENT_TYPES = ['container', 'flex', 'grid'];

    public function validate(array $state): array
    {
        $errors = [];

        if (($state['Version'] ?? null) !== Version::PAGE_SCHEMA) {
            $errors[] = 'Version must be ' . Version::PAGE_SCHEMA . '.';
        }
        if (!is_string($state['PageSlug'] ?? null) || trim((string) $state['PageSlug']) === '') {
            $errors[] = 'PageSlug must be a non-empty string.';
        }
        if (!is_string($state['PageTitle'] ?? null)) {
            $errors[] = 'PageTitle must be a string.';
        }
        if (!is_int($state['ContentVersion'] ?? null) || (int) $state['ContentVersion'] < 0) {
            $errors[] = 'ContentVersion must be a non-negative integer.';
        }
        if (!is_string($state['DataContextType'] ?? null)) {
            $errors[] = 'DataContextType must be a string.';
        }
        if (!is_int($state['DataContextEntryId'] ?? null) || (int) $state['DataContextEntryId'] < 0) {
            $errors[] = 'DataContextEntryId must be a non-negative integer.';
        }
        if (!isset($state['Sections']) || !is_array($state['Sections'])) {
            $errors[] = 'Sections must be an array.';
            return $errors;
        }

        $sections = array_values($state['Sections']);
        if (count($sections) > self::MAX_SECTIONS) {
            $errors[] = 'Sections exceeds the v0.5.30 limit of ' . self::MAX_SECTIONS . '.';
        }

        $byKey = [];
        foreach ($sections as $index => $section) {
            if (!is_array($section)) {
                $errors[] = "Section {$index} must be an object/array.";
                continue;
            }

            $key = trim((string) ($section['Key'] ?? ''));
            $type = trim((string) ($section['Type'] ?? ''));
            if ($key === '') {
                $errors[] = "Section {$index} has no Key.";
                continue;
            }
            if (isset($byKey[$key])) {
                $errors[] = "Section Key '{$key}' is duplicated.";
                continue;
            }
            if ($type === '') {
                $errors[] = "Section '{$key}' has no Type.";
            }

            $byKey[$key] = $section;
        }

        foreach ($byKey as $key => $section) {
            $parent = trim((string) ($section['LayoutParentKey'] ?? ''));
            if ($parent === '') {
                continue;
            }
            if ($parent === $key) {
                $errors[] = "Section '{$key}' cannot be its own layout parent.";
                continue;
            }
            if (!isset($byKey[$parent])) {
                $errors[] = "Section '{$key}' references missing layout parent '{$parent}'.";
                continue;
            }
            if (!in_array((string) ($byKey[$parent]['Type'] ?? ''), self::LAYOUT_PARENT_TYPES, true)) {
                $errors[] = "Section '{$key}' uses non-layout parent '{$parent}'.";
            }

            $seen = [$key => true];
            $cursor = $parent;
            $depth = 1;
            while ($cursor !== '') {
                if (isset($seen[$cursor])) {
                    $errors[] = "Layout cycle detected at section '{$key}'.";
                    break;
                }
                $seen[$cursor] = true;
                if ($depth >= self::MAX_LAYOUT_DEPTH) {
                    $errors[] = "Section '{$key}' exceeds maximum layout depth " . self::MAX_LAYOUT_DEPTH . '.';
                    break;
                }
                if (!isset($byKey[$cursor])) {
                    break;
                }
                $cursor = trim((string) ($byKey[$cursor]['LayoutParentKey'] ?? ''));
                $depth++;
            }
        }

        return array_values(array_unique($errors));
    }

    public function assertValid(array $state): void
    {
        $errors = $this->validate($state);
        if ($errors !== []) {
            throw new RuntimeException('Invalid page schema: ' . implode(' ', $errors));
        }
    }
}
