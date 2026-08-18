<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface RevisionRepository
{
    /** @param array<string,mixed> $revision @return array<string,mixed> */
    public function append(string $resourceKey, array $revision): array;

    /** @return list<array<string,mixed>> */
    public function history(string $resourceKey): array;

    /** @return array<string,mixed>|null */
    public function get(string $resourceKey, string $revisionId): ?array;

    /** @param array<string,mixed>|null $snapshot */
    public function saveAutosave(string $resourceKey, ?array $snapshot): void;

    /** @return array<string,mixed>|null */
    public function autosave(string $resourceKey): ?array;
}
