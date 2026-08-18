<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Portability;

use Hangar18\UltimateDesigner\Contracts\SchemaValidator;
use Hangar18\UltimateDesigner\Core\Version;
use RuntimeException;

/** UD-108 deterministic page + global styles package. */
final class PagePackageService
{
    public const PACKAGE_SCHEMA = '1.0';
    private SchemaValidator $validator;
    private CanonicalJson $json;

    public function __construct(SchemaValidator $validator, ?CanonicalJson $json = null)
    {
        $this->validator = $validator;
        $this->json = $json ?? new CanonicalJson();
    }

    /** @param array<string,mixed> $page @param array<string,mixed> $globalStyles */
    public function export(array $page, array $globalStyles): string
    {
        $this->validator->assertValid($page);
        $payload = [
            'PackageSchemaVersion'=>self::PACKAGE_SCHEMA,
            'Kind'=>'page',
            'PageSchemaVersion'=>Version::PAGE_SCHEMA,
            'Page'=>$page,
            'GlobalStyles'=>$globalStyles,
        ];
        $payload['Checksums'] = [
            'Page'=>$this->json->hash($page),
            'GlobalStyles'=>$this->json->hash($globalStyles),
        ];
        return $this->json->encode($payload);
    }

    /** @return array{Page:array<string,mixed>,GlobalStyles:array<string,mixed>,Checksums:array<string,string>} */
    public function import(string $json): array
    {
        $decoded = json_decode($json, true);
        if (!is_array($decoded)) { throw new RuntimeException('Import package is not valid JSON.'); }
        if (($decoded['PackageSchemaVersion'] ?? '') !== self::PACKAGE_SCHEMA || ($decoded['Kind'] ?? '') !== 'page') {
            throw new RuntimeException('Unsupported page package schema/kind.');
        }
        if (($decoded['PageSchemaVersion'] ?? '') !== Version::PAGE_SCHEMA) {
            throw new RuntimeException('Unsupported page schema version.');
        }
        $page = is_array($decoded['Page'] ?? null) ? $decoded['Page'] : [];
        $styles = is_array($decoded['GlobalStyles'] ?? null) ? $decoded['GlobalStyles'] : [];
        $this->validator->assertValid($page);
        $checksums = is_array($decoded['Checksums'] ?? null) ? $decoded['Checksums'] : [];
        if (($checksums['Page'] ?? '') !== $this->json->hash($page) || ($checksums['GlobalStyles'] ?? '') !== $this->json->hash($styles)) {
            throw new RuntimeException('Page package checksum validation failed.');
        }
        return ['Page'=>$page,'GlobalStyles'=>$styles,'Checksums'=>['Page'=>(string) $checksums['Page'],'GlobalStyles'=>(string) $checksums['GlobalStyles']]];
    }
}
