<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

/** Read-only validation/dry-run report for B2 package manifests. */
final class SiteBackupManifestValidator
{
    public const REQUIRED_PAYLOADS = [
        'managed-site',
        'page-versions',
        'site-builder',
        'forms-polls-data',
        'plugin-metadata',
    ];

    /**
     * @param array<string,mixed> $manifest
     * @param array<string,mixed> $payloads
     * @return array<string,mixed>
     */
    public function validate(array $manifest, array $payloads): array
    {
        $errors = [];
        $warnings = [];

        if (($manifest['SchemaVersion'] ?? '') !== SiteBackupManifestService::SCHEMA_VERSION) {
            $errors[] = 'Ukendt eller manglende manifest schema-version.';
        }
        if (!preg_match(SiteBackupManifestService::BACKUP_ID_PATTERN, (string) ($manifest['BackupId'] ?? ''))) {
            $errors[] = 'BackupId har ugyldigt format.';
        }
        if (!preg_match('/^\d+\.\d+\.\d+$/', (string) ($manifest['PluginVersion'] ?? ''))) {
            $errors[] = 'PluginVersion mangler eller er ugyldig.';
        }

        $source = $manifest['SourceSite'] ?? null;
        if (!is_array($source) || empty($source['HomeUrl']) || empty($source['SiteUrl']) || !preg_match('/^[a-f0-9]{64}$/', (string) ($source['IdentitySha256'] ?? ''))) {
            $errors[] = 'SourceSite identity er ufuldstændig.';
        }

        $manifestForHash = $manifest;
        $expectedManifestSha = strtolower((string) ($manifestForHash['ManifestSha256'] ?? ''));
        unset($manifestForHash['ManifestSha256']);
        try {
            $calculatedManifestSha = hash('sha256', (new SiteBackupManifestService())->canonicalJson($manifestForHash));
            if (!hash_equals($calculatedManifestSha, $expectedManifestSha)) {
                $errors[] = 'ManifestSha256 matcher ikke manifestets indhold.';
            }
        } catch (\Throwable $error) {
            $errors[] = 'Manifestet kunne ikke canonicaliseres.';
        }

        $payloadEntries = $manifest['Payloads'] ?? [];
        if (!is_array($payloadEntries)) {
            $errors[] = 'Payloads skal være en liste.';
            $payloadEntries = [];
        }
        $seenPayloadNames = [];
        $service = new SiteBackupManifestService();
        foreach ($payloadEntries as $entry) {
            if (!is_array($entry)) {
                $errors[] = 'Payload-entry er ugyldig.';
                continue;
            }
            $name = (string) ($entry['Name'] ?? '');
            if ($name === '' || isset($seenPayloadNames[$name])) {
                $errors[] = 'Payload-navn mangler eller forekommer flere gange: ' . $name;
                continue;
            }
            $seenPayloadNames[$name] = true;
            if (!array_key_exists($name, $payloads)) {
                $errors[] = 'Payload mangler fra package input: ' . $name;
                continue;
            }
            try {
                $canonical = $service->canonicalJson($payloads[$name]);
                $sha = hash('sha256', $canonical);
                if (!hash_equals($sha, strtolower((string) ($entry['Sha256'] ?? '')))) {
                    $errors[] = 'SHA-256 mismatch for payload: ' . $name;
                }
                if (strlen($canonical) !== (int) ($entry['Bytes'] ?? -1)) {
                    $errors[] = 'Byte-længde mismatch for payload: ' . $name;
                }
            } catch (\Throwable $error) {
                $errors[] = 'Payload kunne ikke valideres: ' . $name;
            }
        }

        foreach (self::REQUIRED_PAYLOADS as $required) {
            if (!isset($seenPayloadNames[$required])) {
                $warnings[] = 'B2 full-site scope mangler endnu payload: ' . $required;
            }
        }

        $media = $manifest['Media'] ?? [];
        if (!is_array($media)) {
            $errors[] = 'Media skal være en liste.';
            $media = [];
        }
        $seenPaths = [];
        foreach ($media as $entry) {
            if (!is_array($entry)) {
                $errors[] = 'Media-entry er ugyldig.';
                continue;
            }
            $paths = [(string) ($entry['RelativePath'] ?? '')];
            foreach ((array) ($entry['Derivatives'] ?? []) as $derivative) {
                if (is_array($derivative)) {
                    $paths[] = (string) ($derivative['RelativePath'] ?? '');
                }
            }
            foreach ($paths as $path) {
                $normalized = strtolower($path);
                if ($path === '' || str_contains($path, '..') || str_starts_with($path, '/') || str_starts_with($path, '\\')) {
                    $errors[] = 'Usikker eller tom media-sti: ' . $path;
                    continue;
                }
                if (isset($seenPaths[$normalized])) {
                    $errors[] = 'Dublet media-sti: ' . $path;
                }
                $seenPaths[$normalized] = true;
            }
        }

        $capabilities = $manifest['Capabilities'] ?? [];
        if (!is_array($capabilities) || !empty($capabilities['FullRestore']) || !empty($capabilities['SelectiveRestore']) || !empty($capabilities['ZipExport'])) {
            $warnings[] = 'B2-A må ikke annoncere restore/ZIP som aktivt endnu.';
        }

        return [
            'Valid' => $errors === [],
            'Errors' => array_values(array_unique($errors)),
            'Warnings' => array_values(array_unique($warnings)),
            'PayloadCount' => count($payloadEntries),
            'MediaCount' => count($media),
            'DryRunOnly' => true,
        ];
    }
}
