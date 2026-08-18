<?php

declare(strict_types=1);

use Hangar18\UltimateDesigner\Contracts\AssetMetadataRepository;

final class InMemoryAssetMetadataRepository implements AssetMetadataRepository
{
    /** @var array<int,array<string,mixed>> */
    private array $items = [];

    public function get(int $mediaId): array
    {
        return $this->items[$mediaId] ?? [];
    }

    public function save(int $mediaId, array $metadata): array
    {
        $this->items[$mediaId] = $metadata;
        ksort($this->items, SORT_NUMERIC);
        return $metadata;
    }

    public function all(): array
    {
        return $this->items;
    }

    public function delete(int $mediaId): void
    {
        unset($this->items[$mediaId]);
    }
}
