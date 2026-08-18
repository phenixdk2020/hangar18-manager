<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\PageRepository;
use InvalidArgumentException;
use RuntimeException;

/**
 * Compatibility adapter for the existing v0.5.30 page editor option store.
 *
 * It deliberately preserves the current option name and slug-keyed map:
 *   hangar18_manager_pages_v1[<page-slug>] = <page-state>
 */
final class LegacyOptionPageRepository implements PageRepository
{
    public const DEFAULT_OPTION = 'hangar18_manager_pages_v1';

    private string $optionName;

    public function __construct(string $optionName = self::DEFAULT_OPTION)
    {
        $optionName = trim($optionName);
        if ($optionName === '') {
            throw new InvalidArgumentException('Page repository option name cannot be empty.');
        }
        $this->optionName = $optionName;
    }

    public function load(string $pageKey): ?array
    {
        $key = $this->normalizeKey($pageKey);
        $store = $this->readStore();
        $state = $store[$key] ?? null;

        return is_array($state) ? $state : null;
    }

    public function save(string $pageKey, array $state): void
    {
        $key = $this->normalizeKey($pageKey);
        $store = $this->readStore();
        $store[$key] = $state;

        $result = update_option($this->optionName, $store, false);
        if ($result === false) {
            $after = get_option($this->optionName, []);
            if (!is_array($after) || !array_key_exists($key, $after) || $after[$key] !== $state) {
                throw new RuntimeException("Unable to persist designer page '{$key}'.");
            }
        }
    }

    public function exists(string $pageKey): bool
    {
        $key = $this->normalizeKey($pageKey);
        return array_key_exists($key, $this->readStore());
    }

    /** @return array<string,mixed> */
    private function readStore(): array
    {
        $stored = get_option($this->optionName, []);
        return is_array($stored) ? $stored : [];
    }

    private function normalizeKey(string $pageKey): string
    {
        $key = trim($pageKey);
        if ($key === '') {
            throw new InvalidArgumentException('Page repository key cannot be empty.');
        }
        return $key;
    }
}
