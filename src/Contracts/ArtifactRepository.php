<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface ArtifactRepository
{
    public function exists(string $type, string $id): bool;

    /** @return list<string> */
    public function ids(string $type): array;

    /** @param array<string,mixed> $data */
    public function save(string $type, string $id, array $data): void;

    /** @return array<string,array<string,array<string,mixed>>> */
    public function snapshot(): array;

    /**
     * Execute all import mutations atomically where the backend supports it.
     * @template T
     * @param callable():T $callback
     * @return T
     */
    public function transaction(callable $callback);
}
