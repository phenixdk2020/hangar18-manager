<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface StagingRepository
{
    /** @return array<string,mixed>|null */
    public function working(string $resourceKey): ?array;

    /** @return array<string,mixed>|null */
    public function published(string $resourceKey): ?array;

    /** @param array<string,mixed> $state */
    public function saveWorking(string $resourceKey, array $state): void;

    /** @param array<string,mixed> $state */
    public function savePublished(string $resourceKey, array $state): void;

    /**
     * Execute an atomic mutation. Implementations must rollback when the callback throws.
     * @template T
     * @param callable():T $callback
     * @return T
     */
    public function transaction(callable $callback);
}
