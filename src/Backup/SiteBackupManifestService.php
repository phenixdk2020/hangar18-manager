<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;

/**
 * Pure manifest builder for B2 versioned full-site backup packages.
 *
 * This slice does not write files/options and cannot restore anything. It
 * defines immutable IDs, canonical payload checksums and source-site identity
 * so a later package/catalog layer can persist and export them safely.
 */
final class SiteBackupManifestService
{
    public const SCHEMA_VERSION = '1.0';
    public const BACKUP_ID_PATTERN = '/^H18-BACKUP-(\d{6})$/';

    /** @param array<int,string> $existingIds */
    public function nextBackupId(array $existingIds): string
    {
        $max = 0;
        foreach ($existingIds as $id) {
            if (preg_match(self::BACKUP_ID_PATTERN, trim((string) $id), $match)) {
                $max = max($max, (int) $match[1]);
            }
        }
        if ($max >= 999999) {
            throw new RuntimeException('Backup-ID serien er opbrugt.');
        }
        return sprintf('H18-BACKUP-%06d', $max + 1);
    }

    /**
     * @param array<string,mixed> $sourceSite
     * @param array<string,mixed> $payloads
     * @param array<int,array<string,mixed>> $media
     * @return array<string,mixed>
     */
    public function build(
        string $backupId,
        string $createdUtc,
        string $pluginVersion,
        array $sourceSite,
        array $payloads,
        array $media = []
    ): array {
        $backupId = trim($backupId);
        if (!preg_match(self::BACKUP_ID_PATTERN, $backupId)) {
            throw new RuntimeException('Backup-ID skal have formatet H18-BACKUP-000001.');
        }
        if (!$this->isUtcTimestamp($createdUtc)) {
            throw new RuntimeException('CreatedUtc skal være en gyldig UTC ISO-8601 timestamp.');
        }
        if (!preg_match('/^\d+\.\d+\.\d+$/', trim($pluginVersion))) {
            throw new RuntimeException('PluginVersion skal være et semantisk versionsnummer.');
        }

        $homeUrl = $this->normalizeUrl((string) ($sourceSite['HomeUrl'] ?? ''));
        $siteUrl = $this->normalizeUrl((string) ($sourceSite['SiteUrl'] ?? ''));
        if ($homeUrl === '' || $siteUrl === '') {
            throw new RuntimeException('SourceSite kræver HomeUrl og SiteUrl.');
        }

        $payloadManifest = [];
        foreach ($payloads as $name => $payload) {
            $name = $this->safeLogicalName((string) $name);
            if ($name === '') {
                throw new RuntimeException('Payload-navn er ugyldigt.');
            }
            $canonical = $this->canonicalJson($payload);
            $payloadManifest[] = [
                'Name' => $name,
                'Encoding' => 'json-utf8',
                'Bytes' => strlen($canonical),
                'Sha256' => hash('sha256', $canonical),
                'ItemCount' => $this->itemCount($payload),
            ];
        }
        usort($payloadManifest, static fn(array $a, array $b): int => strcmp((string) $a['Name'], (string) $b['Name']));

        $mediaManifest = [];
        foreach ($media as $entry) {
            if (!is_array($entry)) {
                throw new RuntimeException('Media manifest entry skal være et objekt.');
            }
            $relativePath = $this->safeRelativePath((string) ($entry['RelativePath'] ?? ''));
            $sha = strtolower(trim((string) ($entry['Sha256'] ?? '')));
            if ($relativePath === '' || !preg_match('/^[a-f0-9]{64}$/', $sha)) {
                throw new RuntimeException('Media entry kræver sikker RelativePath og SHA-256.');
            }
            $derivatives = [];
            foreach ((array) ($entry['Derivatives'] ?? []) as $derivative) {
                if (!is_array($derivative)) {
                    continue;
                }
                $derivativePath = $this->safeRelativePath((string) ($derivative['RelativePath'] ?? ''));
                $derivativeSha = strtolower(trim((string) ($derivative['Sha256'] ?? '')));
                if ($derivativePath === '' || !preg_match('/^[a-f0-9]{64}$/', $derivativeSha)) {
                    throw new RuntimeException('Media derivative kræver sikker RelativePath og SHA-256.');
                }
                $derivatives[] = [
                    'RelativePath' => $derivativePath,
                    'Bytes' => max(0, (int) ($derivative['Bytes'] ?? 0)),
                    'Sha256' => $derivativeSha,
                    'MimeType' => trim((string) ($derivative['MimeType'] ?? '')),
                ];
            }
            usort($derivatives, static fn(array $a, array $b): int => strcmp((string) $a['RelativePath'], (string) $b['RelativePath']));
            $mediaManifest[] = [
                'MediaId' => max(0, (int) ($entry['MediaId'] ?? 0)),
                'RelativePath' => $relativePath,
                'Bytes' => max(0, (int) ($entry['Bytes'] ?? 0)),
                'Sha256' => $sha,
                'MimeType' => trim((string) ($entry['MimeType'] ?? '')),
                'Role' => trim((string) ($entry['Role'] ?? 'original')) ?: 'original',
                'Derivatives' => $derivatives,
            ];
        }
        usort($mediaManifest, static fn(array $a, array $b): int => strcmp((string) $a['RelativePath'], (string) $b['RelativePath']));
        $this->assertUniqueMediaPaths($mediaManifest);

        $sourceIdentity = [
            'HomeUrl' => $homeUrl,
            'SiteUrl' => $siteUrl,
            'Host' => (string) (parse_url($homeUrl, PHP_URL_HOST) ?: ''),
        ];
        $sourceIdentity['IdentitySha256'] = hash('sha256', $this->canonicalJson($sourceIdentity));

        $manifest = [
            'SchemaVersion' => self::SCHEMA_VERSION,
            'BackupId' => $backupId,
            'CreatedUtc' => $createdUtc,
            'PluginVersion' => trim($pluginVersion),
            'SourceSite' => $sourceIdentity,
            'Payloads' => $payloadManifest,
            'Media' => $mediaManifest,
            'Capabilities' => [
                'FullRestore' => false,
                'SelectiveRestore' => false,
                'ZipExport' => false,
                'DryRunValidation' => true,
            ],
        ];
        $manifest['ManifestSha256'] = hash('sha256', $this->canonicalJson($manifest));
        return $manifest;
    }

    /** @param mixed $value */
    public function canonicalJson($value): string
    {
        $normalized = $this->canonicalize($value);
        $json = json_encode($normalized, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES | JSON_PRESERVE_ZERO_FRACTION);
        if (!is_string($json)) {
            throw new RuntimeException('Data kunne ikke serialiseres deterministisk.');
        }
        return $json;
    }

    /** @param mixed $value @return mixed */
    private function canonicalize($value)
    {
        if (!is_array($value)) {
            return $value;
        }
        if ($this->isList($value)) {
            return array_map(fn($item) => $this->canonicalize($item), $value);
        }
        ksort($value, SORT_STRING);
        foreach ($value as $key => $item) {
            $value[$key] = $this->canonicalize($item);
        }
        return $value;
    }

    /** PHP 8.0-compatible equivalent of array_is_list(). */
    private function isList(array $value): bool
    {
        $expected = 0;
        foreach ($value as $key => $_item) {
            if ($key !== $expected) {
                return false;
            }
            $expected++;
        }
        return true;
    }

    /** @param mixed $payload */
    private function itemCount($payload): int
    {
        return is_array($payload) ? count($payload) : 1;
    }

    private function safeLogicalName(string $name): string
    {
        $name = strtolower(trim($name));
        return preg_match('/^[a-z0-9][a-z0-9._-]{0,79}$/', $name) ? $name : '';
    }

    private function safeRelativePath(string $path): string
    {
        $path = str_replace('\\', '/', trim($path));
        $path = ltrim($path, '/');
        if ($path === '' || str_contains($path, "\0") || preg_match('#(^|/)\.\.(/|$)#', $path)) {
            return '';
        }
        return preg_match('#^[A-Za-z0-9._/ -]+$#u', $path) ? $path : '';
    }

    private function normalizeUrl(string $url): string
    {
        $url = trim($url);
        if (!preg_match('#^https?://#i', $url) || filter_var($url, FILTER_VALIDATE_URL) === false) {
            return '';
        }
        return rtrim($url, '/');
    }

    private function isUtcTimestamp(string $value): bool
    {
        if (!preg_match('/Z$/', $value)) {
            return false;
        }
        try {
            $date = new \DateTimeImmutable($value);
            return $date->getOffset() === 0;
        } catch (\Throwable $error) {
            return false;
        }
    }

    /** @param array<int,array<string,mixed>> $media */
    private function assertUniqueMediaPaths(array $media): void
    {
        $seen = [];
        foreach ($media as $entry) {
            $paths = [(string) ($entry['RelativePath'] ?? '')];
            foreach ((array) ($entry['Derivatives'] ?? []) as $derivative) {
                if (is_array($derivative)) {
                    $paths[] = (string) ($derivative['RelativePath'] ?? '');
                }
            }
            foreach ($paths as $path) {
                $key = strtolower($path);
                if (isset($seen[$key])) {
                    throw new RuntimeException('Media manifest indeholder dubletsti: ' . $path);
                }
                $seen[$key] = true;
            }
        }
    }
}
