<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Assets;

/** UD-090 recursively indexes native MediaId references across pages/components/data entries. */
final class AssetUsageScanner
{
    /** @var list<string> */
    private array $mediaKeys = [
        'MediaId','ImageMediaId','BackgroundMediaId','LogoMediaId','IconMediaId','PosterMediaId','ThumbnailMediaId','MainMediaId'
    ];

    /**
     * @param array<string,array<string,mixed>> $resources keyed by e.g. page:hjem, component:42, data:event:12
     * @return array<int,list<array{Resource:string,Path:string}>>
     */
    public function scan(array $resources): array
    {
        $usage = [];
        foreach ($resources as $resourceKey => $state) {
            if (!is_array($state)) { continue; }
            $this->walk($state, (string) $resourceKey, '$', $usage);
        }
        ksort($usage, SORT_NUMERIC);
        foreach ($usage as &$references) {
            usort($references, static fn(array $a, array $b): int => [$a['Resource'],$a['Path']] <=> [$b['Resource'],$b['Path']]);
        }
        unset($references);
        return $usage;
    }

    /**
     * @param mixed $value
     * @param array<int,list<array{Resource:string,Path:string}>> $usage
     */
    private function walk($value, string $resource, string $path, array &$usage): void
    {
        if (!is_array($value)) { return; }
        foreach ($value as $key => $child) {
            $keyString = (string) $key;
            $childPath = $path . '.' . $keyString;
            if (in_array($keyString, $this->mediaKeys, true)) {
                $mediaId = $this->mediaId($child);
                if ($mediaId > 0) {
                    $usage[$mediaId] ??= [];
                    $reference = ['Resource'=>$resource,'Path'=>$childPath];
                    if (!in_array($reference, $usage[$mediaId], true)) { $usage[$mediaId][] = $reference; }
                }
            }
            $this->walk($child, $resource, $childPath, $usage);
        }
    }

    /** @param mixed $value */
    private function mediaId($value): int
    {
        if (is_int($value) || (is_string($value) && ctype_digit($value))) { return (int) $value; }
        // WordPress get_post_meta($id) commonly exposes scalar meta as ['123'].
        if (is_array($value) && count($value) === 1) {
            $first = reset($value);
            if (is_int($first) || (is_string($first) && ctype_digit($first))) { return (int) $first; }
        }
        return 0;
    }
}
