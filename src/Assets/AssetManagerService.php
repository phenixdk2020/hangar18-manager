<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Assets;

use Hangar18\UltimateDesigner\Contracts\AssetMetadataRepository;

/** UD-089 collections/folders/tags overlay keyed by immutable native media IDs. */
final class AssetManagerService
{
    private AssetMetadataRepository $repository;
    private AssetMetadataValidator $validator;

    public function __construct(AssetMetadataRepository $repository, ?AssetMetadataValidator $validator = null)
    {
        $this->repository = $repository;
        $this->validator = $validator ?? new AssetMetadataValidator();
    }

    /** @param array<string,mixed> $metadata @return array<string,mixed> */
    public function save(int $mediaId, array $metadata): array
    {
        return $this->repository->save($mediaId, $this->validator->normalize($mediaId, $metadata));
    }

    /** @return array<string,mixed> */
    public function get(int $mediaId): array
    {
        return $this->repository->get($mediaId);
    }

    /** @return array<string,list<string>> */
    public function taxonomy(): array
    {
        $folders = [];
        $collections = [];
        $tags = [];
        foreach ($this->repository->all() as $metadata) {
            $folder = trim((string) ($metadata['Folder'] ?? ''));
            if ($folder !== '') { $folders[$folder] = true; }
            foreach ((array) ($metadata['Collections'] ?? []) as $value) { $collections[(string) $value] = true; }
            foreach ((array) ($metadata['Tags'] ?? []) as $value) { $tags[(string) $value] = true; }
        }
        $sort = static function (array $map): array {
            $values = array_keys($map);
            natcasesort($values);
            return array_values($values);
        };
        return ['folders'=>$sort($folders),'collections'=>$sort($collections),'tags'=>$sort($tags)];
    }

    /** @return list<int> */
    public function filter(string $folder = '', string $collection = '', string $tag = ''): array
    {
        $ids = [];
        foreach ($this->repository->all() as $mediaId => $metadata) {
            if ($folder !== '' && (string) ($metadata['Folder'] ?? '') !== $folder) { continue; }
            if ($collection !== '' && !in_array($collection, (array) ($metadata['Collections'] ?? []), true)) { continue; }
            if ($tag !== '' && !in_array($tag, (array) ($metadata['Tags'] ?? []), true)) { continue; }
            $ids[] = (int) $mediaId;
        }
        sort($ids);
        return $ids;
    }
}
