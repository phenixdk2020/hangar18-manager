<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Contracts;

interface AssetMetadataRepository
{
    /** @return array<string,mixed> */
    public function get(int $mediaId): array;

    /** @param array<string,mixed> $metadata @return array<string,mixed> */
    public function save(int $mediaId, array $metadata): array;

    /** @return array<int,array<string,mixed>> */
    public function all(): array;

    public function delete(int $mediaId): void;
}
