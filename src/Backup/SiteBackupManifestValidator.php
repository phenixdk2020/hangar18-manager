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
            if (!preg_match('/^[a-f0-9]{64}$/', $expectedManifestSha) || !hash_equals($calculatedManifestSha, $expectedManifestSha)) {
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
                $expectedSha = strtolower((string) ($entry['Sha256'] ?? ''));
                if (!preg_match('/^[a-f0-9]{64}$/', $expectedSha) || !hash_equals($sha, $expectedSha)) {
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
                $warnings[] = 'B2 full-site scope mangler payload: ' . $required;
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
            $checks = [$entry];
            foreach ((array) ($entry['Derivatives'] ?? []) as $derivative) {
                if (is_array($derivative)) {
                    $checks[] = $derivative;
                }
            }
            foreach ($checks as $fileEntry) {
                $path = str_replace('\\', '/', (string) ($fileEntry['RelativePath'] ?? ''));
                $normalized = strtolower($path);
                $sha = strtolower((string) ($fileEntry['Sha256'] ?? ''));
                if ($path === '' || str_contains($path, "\0") || str_contains($path, '..') || str_starts_with($path, '/') || preg_match('/^[A-Za-z]:\//', $path)) {
                    $errors[] = 'Usikker eller tom media-sti: ' . $path;
                    continue;
                }
                if (!preg_match('/^[a-f0-9]{64}$/', $sha)) {
                    $errors[] = 'Media-entry mangler gyldig SHA-256: ' . $path;
                }
                if (isset($seenPaths[$normalized])) {
                    $errors[] = 'Dublet media-sti: ' . $path;
                }
                $seenPaths[$normalized] = true;
            }
        }

        $capabilities = $manifest['Capabilities'] ?? null;
        if (!is_array($capabilities)) {
            $errors[] = 'Capabilities mangler eller er ugyldig.';
        } else {
            foreach (['FullRestore','SelectiveRestore','ZipExport','DryRunValidation'] as $capability) {
                if (!array_key_exists($capability, $capabilities) || !is_bool($capabilities[$capability])) {
                    $errors[] = 'Capability skal være eksplicit boolean: ' . $capability;
                }
            }
            if (empty($capabilities['DryRunValidation'])) {
                $errors[] = 'B2-package skal understøtte dry-run validation.';
            }
            if (array_key_exists('Import', $capabilities) && !is_bool($capabilities['Import'])) {
                $errors[] = 'Capability skal være eksplicit boolean: Import';
            }
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
