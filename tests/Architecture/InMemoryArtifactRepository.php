<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Contracts\ArtifactRepository;

final class InMemoryArtifactRepository implements ArtifactRepository
{
    /** @var array<string,array<string,array<string,mixed>>> */
    private array $items = [];

    /** @param array<string,array<string,array<string,mixed>>> $seed */
    public function __construct(array $seed = [])
    {
        $this->items = $seed;
    }

    public function exists(string $type, string $id): bool
    {
        return isset($this->items[$type][$id]);
    }

    public function ids(string $type): array
    {
        $ids = array_keys($this->items[$type] ?? []);
        sort($ids,SORT_STRING);
        return array_values($ids);
    }

    public function save(string $type, string $id, array $data): void
    {
        $this->items[$type] ??= [];
        $this->items[$type][$id] = $data;
        ksort($this->items[$type],SORT_STRING);
        ksort($this->items,SORT_STRING);
    }

    public function snapshot(): array
    {
        return $this->items;
    }

    public function transaction(callable $callback)
    {
        $before = $this->items;
        try { return $callback(); }
        catch (Throwable $e) { $this->items = $before; throw $e; }
    }
}
