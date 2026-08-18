<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

use RuntimeException;

/** UD-110 portable asset manifest and deterministic target matching. */
final class AssetManifestService
{
    private CanonicalJson $json;

    public function __construct(?CanonicalJson $json = null)
    {
        $this->json = $json ?? new CanonicalJson();
    }

    /**
     * @param list<array{MediaId:int,Hash:string,Filename:string,Mime?:string,Bytes?:int}> $assets
     * @return array<string,mixed>
     */
    public function manifest(array $assets): array
    {
        $items = [];
        $seen = [];
        foreach ($assets as $asset) {
            $mediaId = (int) ($asset['MediaId'] ?? 0);
            $hash = strtolower(trim((string) ($asset['Hash'] ?? '')));
            $filename = trim((string) ($asset['Filename'] ?? ''));
            if ($mediaId <= 0 || !preg_match('/^[a-f0-9]{64}$/',$hash) || $filename === '') { throw new RuntimeException('Invalid asset manifest entry.'); }
            $packageId = 'asset:' . $mediaId;
            if (isset($seen[$packageId])) { throw new RuntimeException('Duplicate package asset ID.'); }
            $seen[$packageId] = true;
            $items[] = [
                'PackageAssetId'=>$packageId,
                'SourceMediaId'=>$mediaId,
                'Hash'=>$hash,
                'Filename'=>mb_substr($filename,0,240),
                'Mime'=>mb_substr(trim((string) ($asset['Mime'] ?? '')),0,120),
                'Bytes'=>max(0,(int) ($asset['Bytes'] ?? 0)),
            ];
        }
        usort($items,static fn(array $a,array $b): int => $a['PackageAssetId'] <=> $b['PackageAssetId']);
        return ['SchemaVersion'=>'1.0','Assets'=>$items,'Checksum'=>$this->json->hash($items)];
    }

    /**
     * @param array<string,mixed> $manifest
     * @param list<array{MediaId:int,Hash:string,Filename?:string}> $targetAssets
     * @return array{Mappings:array<string,int>,Broken:list<array<string,mixed>>,Matches:list<array<string,mixed>>}
     */
    public function match(array $manifest, array $targetAssets): array
    {
        $assets = is_array($manifest['Assets'] ?? null) ? array_values($manifest['Assets']) : [];
        if (($manifest['SchemaVersion'] ?? '') !== '1.0' || ($manifest['Checksum'] ?? '') !== $this->json->hash($assets)) {
            throw new RuntimeException('Asset manifest checksum/schema validation failed.');
        }
        $byHash = [];
        foreach ($targetAssets as $target) {
            $id = (int) ($target['MediaId'] ?? 0);
            $hash = strtolower(trim((string) ($target['Hash'] ?? '')));
            if ($id > 0 && preg_match('/^[a-f0-9]{64}$/',$hash)) {
                $byHash[$hash] ??= [];
                $byHash[$hash][] = $id;
            }
        }
        foreach ($byHash as &$ids) { sort($ids,SORT_NUMERIC); }
        unset($ids);

        $mappings = []; $broken = []; $matches = [];
        foreach ($assets as $asset) {
            if (!is_array($asset)) { continue; }
            $packageId = (string) ($asset['PackageAssetId'] ?? '');
            $hash = strtolower((string) ($asset['Hash'] ?? ''));
            $ids = $byHash[$hash] ?? [];
            if ($packageId === '' || $ids === []) {
                $broken[] = ['PackageAssetId'=>$packageId,'Reason'=>'no-hash-match','Filename'=>(string) ($asset['Filename'] ?? '')];
                continue;
            }
            $targetId = (int) $ids[0];
            $mappings[$packageId] = $targetId;
            $matches[] = ['PackageAssetId'=>$packageId,'TargetMediaId'=>$targetId,'Method'=>'sha256'];
        }
        return ['Mappings'=>$mappings,'Broken'=>$broken,'Matches'=>$matches];
    }
}
