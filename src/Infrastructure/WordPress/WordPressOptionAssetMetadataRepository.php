<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Infrastructure\WordPress;

use Hangar18\UltimateDesigner\Contracts\AssetMetadataRepository;
use RuntimeException;

/** Stores Ultimate Designer organization metadata separately from native attachment records. */
final class WordPressOptionAssetMetadataRepository implements AssetMetadataRepository
{
    public const OPTION = 'hangar18_ud_asset_metadata_v1';

    public function get(int $mediaId): array
    {
        if ($mediaId <= 0) { return []; }
        $all = $this->all();
        return is_array($all[$mediaId] ?? null) ? $all[$mediaId] : [];
    }

    public function save(int $mediaId, array $metadata): array
    {
        if ($mediaId <= 0) { throw new RuntimeException('Invalid media ID.'); }
        $metadata['MediaId'] = $mediaId;
        $all = $this->all();
        $all[$mediaId] = $metadata;
        ksort($all, SORT_NUMERIC);
        if (!update_option(self::OPTION, $all, false)) {
            $current = get_option(self::OPTION, []);
            if ($current !== $all) { throw new RuntimeException('Asset metadata could not be saved.'); }
        }
        return $metadata;
    }

    public function all(): array
    {
        $raw = get_option(self::OPTION, []);
        if (!is_array($raw)) { return []; }
        $result = [];
        foreach ($raw as $mediaId => $metadata) {
            $mediaId = (int) $mediaId;
            if ($mediaId > 0 && is_array($metadata)) { $result[$mediaId] = $metadata; }
        }
        ksort($result, SORT_NUMERIC);
        return $result;
    }

    public function delete(int $mediaId): void
    {
        if ($mediaId <= 0) { return; }
        $all = $this->all();
        unset($all[$mediaId]);
        update_option(self::OPTION, $all, false);
    }
}
