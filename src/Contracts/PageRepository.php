<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

/**
 * Storage boundary for versioned designer page state.
 * Implementations may use WordPress posts/meta/options, but domain/editor code
 * must not depend directly on those storage details.
 */
interface PageRepository
{
    /** @return array<string,mixed>|null */
    public function load(int $pageId): ?array;

    /** @param array<string,mixed> $state */
    public function save(int $pageId, array $state): void;

    public function exists(int $pageId): bool;
}
