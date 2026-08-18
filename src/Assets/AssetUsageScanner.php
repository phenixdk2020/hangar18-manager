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
            if (in_array($keyString, $this->mediaKeys, true) && (is_int($child) || ctype_digit((string) $child))) {
                $mediaId = (int) $child;
                if ($mediaId > 0) {
                    $usage[$mediaId] ??= [];
                    $reference = ['Resource'=>$resource,'Path'=>$childPath];
                    if (!in_array($reference, $usage[$mediaId], true)) { $usage[$mediaId][] = $reference; }
                }
            }
            $this->walk($child, $resource, $childPath, $usage);
        }
    }
}
