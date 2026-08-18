<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Assets;

/** UD-093 SHA-256 duplicate detection. Detection never deletes or merges assets. */
final class DuplicateAssetDetector
{
    /**
     * @param array<int,string> $mediaFiles media ID => local file path
     * @return list<array{Hash:string,MediaIds:list<int>,Paths:list<string>}>
     */
    public function detect(array $mediaFiles): array
    {
        $groups = [];
        foreach ($mediaFiles as $mediaId => $path) {
            $mediaId = (int) $mediaId;
            $path = trim((string) $path);
            if ($mediaId <= 0 || $path === '' || !is_file($path) || !is_readable($path)) { continue; }
            $hash = hash_file('sha256', $path);
            if (!is_string($hash) || $hash === '') { continue; }
            $groups[$hash] ??= ['Hash'=>$hash,'MediaIds'=>[],'Paths'=>[]];
            $groups[$hash]['MediaIds'][] = $mediaId;
            $groups[$hash]['Paths'][] = $path;
        }
        $duplicates = [];
        foreach ($groups as $group) {
            if (count($group['MediaIds']) < 2) { continue; }
            array_multisort($group['MediaIds'], SORT_ASC, SORT_NUMERIC, $group['Paths'], SORT_ASC, SORT_STRING);
            $duplicates[] = $group;
        }
        usort($duplicates, static fn(array $a, array $b): int => $a['Hash'] <=> $b['Hash']);
        return $duplicates;
    }
}
