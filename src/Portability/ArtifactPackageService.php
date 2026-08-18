<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

use RuntimeException;

/** UD-109 portable package for components/templates/menus/forms. */
final class ArtifactPackageService
{
    public const PACKAGE_SCHEMA = '1.0';
    private const TYPES = ['component','template','menu','form'];
    private CanonicalJson $json;

    public function __construct(?CanonicalJson $json = null)
    {
        $this->json = $json ?? new CanonicalJson();
    }

    /**
     * @param list<array{Type:string,Id:string,Name?:string,Data:array<string,mixed>}> $artifacts
     */
    public function export(array $artifacts): string
    {
        $normalized = [];
        $seen = [];
        foreach ($artifacts as $artifact) {
            $type = strtolower(trim((string) ($artifact['Type'] ?? '')));
            $id = trim((string) ($artifact['Id'] ?? ''));
            if (!in_array($type,self::TYPES,true) || $id === '') { throw new RuntimeException('Invalid portable artifact type/id.'); }
            $exportId = $type . ':' . $id;
            if (isset($seen[$exportId])) { throw new RuntimeException('Duplicate artifact export ID: '.$exportId); }
            $seen[$exportId] = true;
            $normalized[] = [
                'ExportId'=>$exportId,
                'Type'=>$type,
                'SourceId'=>$id,
                'Name'=>mb_substr(trim((string) ($artifact['Name'] ?? $id)),0,160),
                'Data'=>is_array($artifact['Data'] ?? null) ? $artifact['Data'] : [],
            ];
        }
        usort($normalized, static fn(array $a,array $b): int => $a['ExportId'] <=> $b['ExportId']);
        $payload = ['PackageSchemaVersion'=>self::PACKAGE_SCHEMA,'Kind'=>'artifacts','Artifacts'=>$normalized];
        $payload['Checksum'] = $this->json->hash($normalized);
        return $this->json->encode($payload);
    }

    /** @return array{Artifacts:list<array<string,mixed>>,Checksum:string} */
    public function import(string $json): array
    {
        $decoded = json_decode($json,true);
        if (!is_array($decoded) || ($decoded['PackageSchemaVersion'] ?? '') !== self::PACKAGE_SCHEMA || ($decoded['Kind'] ?? '') !== 'artifacts') {
            throw new RuntimeException('Unsupported artifact package.');
        }
        $artifacts = is_array($decoded['Artifacts'] ?? null) ? array_values($decoded['Artifacts']) : [];
        $seen = [];
        foreach ($artifacts as $artifact) {
            if (!is_array($artifact)) { throw new RuntimeException('Artifact entry is invalid.'); }
            $type = strtolower(trim((string) ($artifact['Type'] ?? '')));
            $sourceId = trim((string) ($artifact['SourceId'] ?? ''));
            $exportId = trim((string) ($artifact['ExportId'] ?? ''));
            if (!in_array($type,self::TYPES,true) || $sourceId === '' || $exportId !== $type.':'.$sourceId || isset($seen[$exportId])) {
                throw new RuntimeException('Artifact entry identity is invalid or duplicated.');
            }
            if (!is_array($artifact['Data'] ?? null)) { throw new RuntimeException('Artifact Data must be an object/array.'); }
            $seen[$exportId] = true;
        }
        $checksum = (string) ($decoded['Checksum'] ?? '');
        if ($checksum === '' || $checksum !== $this->json->hash($artifacts)) { throw new RuntimeException('Artifact package checksum validation failed.'); }
        return ['Artifacts'=>$artifacts,'Checksum'=>$checksum];
    }
}
