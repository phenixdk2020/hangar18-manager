<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\SiteBuilder;

use RuntimeException;

final class MenuTreeValidator
{
    public const SCHEMA_VERSION = '1.0';
    private const MAX_ITEMS = 200;
    private const MAX_DEPTH = 6;
    /** @var list<string> */
    private const TYPES = ['page', 'url', 'taxonomy', 'dynamic', 'anchor', 'action'];

    /** @param array<string,mixed> $menu @return list<string> */
    public function validate(array $menu): array
    {
        $errors = [];
        $id = trim((string) ($menu['Id'] ?? ''));
        $name = trim((string) ($menu['Name'] ?? ''));
        $revision = $menu['Revision'] ?? null;
        $items = $menu['Items'] ?? null;

        if (($menu['SchemaVersion'] ?? null) !== self::SCHEMA_VERSION) {
            $errors[] = 'SchemaVersion must be ' . self::SCHEMA_VERSION . '.';
        }
        if ($id === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{2,79}$/', $id)) {
            $errors[] = 'Id must be a stable lowercase menu key.';
        }
        if ($name === '' || mb_strlen($name) > 120) {
            $errors[] = 'Name must be 1-120 characters.';
        }
        if (!is_int($revision) || $revision < 1) {
            $errors[] = 'Revision must be a positive integer.';
        }
        if (!is_array($items)) {
            $errors[] = 'Items must be an array.';
            return $errors;
        }
        if (count($items) > self::MAX_ITEMS) {
            $errors[] = 'Menu exceeds maximum item count.';
        }

        $byId = [];
        foreach (array_values($items) as $index => $item) {
            if (!is_array($item)) {
                $errors[] = "Item {$index} must be an object/array.";
                continue;
            }
            $itemId = trim((string) ($item['Id'] ?? ''));
            $type = trim((string) ($item['Type'] ?? ''));
            $label = trim((string) ($item['Label'] ?? ''));
            $order = $item['Order'] ?? null;
            if ($itemId === '' || !preg_match('/^[a-z0-9][a-z0-9_-]{1,79}$/', $itemId)) {
                $errors[] = "Item {$index} has an invalid Id.";
                continue;
            }
            if (isset($byId[$itemId])) {
                $errors[] = "Menu item Id '{$itemId}' is duplicated.";
                continue;
            }
            if (!in_array($type, self::TYPES, true)) {
                $errors[] = "Menu item '{$itemId}' has unsupported Type.";
            }
            if ($label === '' || mb_strlen($label) > 120) {
                $errors[] = "Menu item '{$itemId}' must have a 1-120 character Label.";
            }
            if (!is_int($order) || $order < 0) {
                $errors[] = "Menu item '{$itemId}' must have a non-negative integer Order.";
            }
            foreach (['Icon', 'Badge', 'Description'] as $field) {
                if (isset($item[$field]) && !is_string($item[$field])) {
                    $errors[] = "Menu item '{$itemId}' {$field} must be a string.";
                }
            }
            $byId[$itemId] = $item;
        }

        foreach ($byId as $itemId => $item) {
            $parentId = trim((string) ($item['ParentId'] ?? ''));
            if ($parentId === '') {
                continue;
            }
            if ($parentId === $itemId) {
                $errors[] = "Menu item '{$itemId}' cannot be its own parent.";
                continue;
            }
            if (!isset($byId[$parentId])) {
                $errors[] = "Menu item '{$itemId}' references missing parent '{$parentId}'.";
                continue;
            }

            $seen = [$itemId => true];
            $cursor = $parentId;
            $depth = 1;
            while ($cursor !== '') {
                if (isset($seen[$cursor])) {
                    $errors[] = "Menu cycle detected at '{$itemId}'.";
                    break;
                }
                $seen[$cursor] = true;
                if ($depth >= self::MAX_DEPTH) {
                    $errors[] = "Menu item '{$itemId}' exceeds maximum depth " . self::MAX_DEPTH . '.';
                    break;
                }
                if (!isset($byId[$cursor])) {
                    break;
                }
                $cursor = trim((string) ($byId[$cursor]['ParentId'] ?? ''));
                $depth++;
            }
        }

        return array_values(array_unique($errors));
    }

    /** @param array<string,mixed> $menu */
    public function assertValid(array $menu): void
    {
        $errors = $this->validate($menu);
        if ($errors !== []) {
            throw new RuntimeException('Invalid menu tree: ' . implode(' ', $errors));
        }
    }
}
