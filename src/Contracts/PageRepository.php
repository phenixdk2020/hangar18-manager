<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

/**
 * Storage boundary for versioned designer page state.
 *
 * The v0.5.30 editor store is keyed by page slug. Keeping the repository key
 * as a string allows the compatibility adapter to read/write the existing
 * option without changing IDs, slugs or stored data structure.
 */
interface PageRepository
{
    /** @return array<string,mixed>|null */
    public function load(string $pageKey): ?array;

    /** @param array<string,mixed> $state */
    public function save(string $pageKey, array $state): void;

    public function exists(string $pageKey): bool;
}
