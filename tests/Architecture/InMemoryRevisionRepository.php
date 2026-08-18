<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Contracts\RevisionRepository;

final class InMemoryRevisionRepository implements RevisionRepository
{
    /** @var array<string,list<array<string,mixed>>> */
    private array $history = [];
    /** @var array<string,array<string,mixed>|null> */
    private array $autosaves = [];

    public function append(string $resourceKey, array $revision): array
    {
        $this->history[$resourceKey] ??= [];
        $this->history[$resourceKey][] = $revision;
        return $revision;
    }

    public function history(string $resourceKey): array
    {
        return $this->history[$resourceKey] ?? [];
    }

    public function get(string $resourceKey, string $revisionId): ?array
    {
        foreach ($this->history($resourceKey) as $revision) {
            if ((string) ($revision['Id'] ?? '') === $revisionId) {
                return $revision;
            }
        }
        return null;
    }

    public function saveAutosave(string $resourceKey, ?array $snapshot): void
    {
        $this->autosaves[$resourceKey] = $snapshot;
    }

    public function autosave(string $resourceKey): ?array
    {
        return $this->autosaves[$resourceKey] ?? null;
    }
}
