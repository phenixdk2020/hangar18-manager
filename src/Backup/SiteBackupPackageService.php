<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;
use ZipArchive;

/** Persists, validates, exports and imports immutable B2 application-aware packages. */
final class SiteBackupPackageService
{
    public const CATALOG_OPTION = 'hangar18_manager_site_backup_catalog_v1';
    private const ROOT_DIR = 'hangar18-manager-site-backups';

    private SiteBackupManifestService $manifest;
    private SiteBackupManifestValidator $validator;
    private SiteBackupSnapshotCollector $collector;

    public function __construct(
        ?SiteBackupManifestService $manifest = null,
        ?SiteBackupManifestValidator $validator = null,
        ?SiteBackupSnapshotCollector $collector = null
    ) {
        $this->manifest = $manifest ?? new SiteBackupManifestService();
        $this->validator = $validator ?? new SiteBackupManifestValidator();
        $this->collector = $collector ?? new SiteBackupSnapshotCollector();
    }

    /** @return array<string,mixed> */
    public function create(string $note = ''): array
    {
        $catalog = $this->catalog();
        $backupId = $this->manifest->nextBackupId(array_keys($catalog));
        $created = gmdate('c');
        $pluginVersion = defined('Hangar18_Manager::VERSION') ? (string)\Hangar18_Manager::VERSION : '0.0.0';
        $snapshot = $this->collector->collect();
        $payloads = (array)($snapshot['Payloads'] ?? []);
        $media = (array)($snapshot['Media'] ?? []);
        $mediaFiles = (array)($snapshot['MediaFiles'] ?? []);
        $sourceSite = [
            'HomeUrl'=>function_exists('home_url') ? (string)home_url('/') : 'https://unknown.invalid',
            'SiteUrl'=>function_exists('site_url') ? (string)site_url('/') : 'https://unknown.invalid',
        ];

        $manifest = $this->manifest->build($backupId, $created, $pluginVersion, $sourceSite, $payloads, $media);
        $manifest['Capabilities'] = [
            'FullRestore'=>true,
            'SelectiveRestore'=>true,
            'ZipExport'=>class_exists(ZipArchive::class),
            'DryRunValidation'=>true,
            'Import'=>class_exists(ZipArchive::class),
        ];
        unset($manifest['ManifestSha256']);
        $manifest['ManifestSha256'] = hash('sha256', $this->manifest->canonicalJson($manifest));

        $root = $this->root(true);
        $final = $root . DIRECTORY_SEPARATOR . $backupId;
        $building = $root . DIRECTORY_SEPARATOR . '.building-' . $backupId . '-' . bin2hex(random_bytes(4));
        if (file_exists($final)) {
            throw new RuntimeException('Backup-ID findes allerede på disk: ' . $backupId);
        }

        try {
            $this->mkdir($building);
            $this->mkdir($building . DIRECTORY_SEPARATOR . 'payloads');
            $this->mkdir($building . DIRECTORY_SEPARATOR . 'media');

            foreach ($payloads as $name=>$payload) {
                $safeName = (string)$name;
                if (!preg_match('/^[a-z0-9][a-z0-9._-]{0,79}$/', $safeName)) {
                    throw new RuntimeException('Ugyldigt payload-navn: ' . $safeName);
                }
                $this->write($building . DIRECTORY_SEPARATOR . 'payloads' . DIRECTORY_SEPARATOR . $safeName . '.json', $this->manifest->canonicalJson($payload));
            }
            foreach ($mediaFiles as $relative=>$source) {
                $relative = $this->safeRelativePath((string)$relative);
                $source = (string)$source;
                if ($relative === '' || !is_file($source)) {
                    throw new RuntimeException('Referenced mediafil mangler: ' . (string)$relative);
                }
                $destination = $building . DIRECTORY_SEPARATOR . 'media' . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $relative);
                $this->mkdir(dirname($destination));
                if (!copy($source, $destination)) {
                    throw new RuntimeException('Kunne ikke kopiere media til backuppakken: ' . $relative);
                }
            }
            $this->write($building . DIRECTORY_SEPARATOR . 'manifest.json', $this->manifest->canonicalJson($manifest));
            $report = $this->validateDirectory($building);
            if (empty($report['Valid'])) {
                throw new RuntimeException('Backuppakken fejlede egen validering: ' . implode(' | ', (array)($report['Errors'] ?? [])));
            }
            if (!rename($building, $final)) {
                throw new RuntimeException('Backuppakken kunne ikke flyttes til immutable katalog.');
            }

            $zipName = '';
            if (class_exists(ZipArchive::class)) {
                $zipName = $backupId . '.zip';
                $this->writeZip($final, $root . DIRECTORY_SEPARATOR . $zipName);
            }

            $entry = [
                'BackupId'=>$backupId,
                'CreatedUtc'=>$created,
                'PluginVersion'=>$pluginVersion,
                'Note'=>mb_substr(trim($note), 0, 500),
                'Directory'=>$backupId,
                'Zip'=>$zipName,
                'ManifestSha256'=>(string)$manifest['ManifestSha256'],
                'PayloadCount'=>count($payloads),
                'MediaCount'=>count($media),
                'SourceHost'=>(string)($manifest['SourceSite']['Host'] ?? ''),
                'Imported'=>false,
            ];
            $catalog[$backupId] = $entry;
            $this->saveCatalog($catalog);
            return $entry + ['Validation'=>$report];
        } catch (\Throwable $error) {
            $this->removeTree($building);
            throw $error;
        }
    }

    /** @return array<int,array<string,mixed>> */
    public function listBackups(): array
    {
        $items = array_values($this->catalog());
        usort($items, static fn(array $a,array $b): int => strcmp((string)($b['BackupId'] ?? ''), (string)($a['BackupId'] ?? '')));
        return $items;
    }

    /** @return array<string,mixed> */
    public function validate(string $backupId): array
    {
        return $this->validateDirectory($this->directory($backupId));
    }

    /** @return array{Manifest:array<string,mixed>,Payloads:array<string,mixed>,Directory:string} */
    public function read(string $backupId): array
    {
        $dir = $this->directory($backupId);
        $manifest = $this->jsonFile($dir . DIRECTORY_SEPARATOR . 'manifest.json');
        $payloads = [];
        foreach ((array)($manifest['Payloads'] ?? []) as $entry) {
            if (!is_array($entry)) {
                continue;
            }
            $name = (string)($entry['Name'] ?? '');
            if ($name === '') {
                continue;
            }
            $payloads[$name] = $this->jsonFile($dir . DIRECTORY_SEPARATOR . 'payloads' . DIRECTORY_SEPARATOR . $name . '.json');
        }
        return ['Manifest'=>$manifest,'Payloads'=>$payloads,'Directory'=>$dir];
    }

    public function zipPath(string $backupId): string
    {
        $catalog = $this->catalog();
        if (!isset($catalog[$backupId])) {
            throw new RuntimeException('Backup-ID findes ikke i kataloget.');
        }
        $zip = basename((string)($catalog[$backupId]['Zip'] ?? ''));
        if ($zip === '') {
            if (!class_exists(ZipArchive::class)) {
                throw new RuntimeException('PHP ZipArchive er ikke installeret på serveren.');
            }
            $dir = $this->directory($backupId);
            $zip = $backupId . '.zip';
            $this->writeZip($dir, $this->root(true) . DIRECTORY_SEPARATOR . $zip);
            $catalog[$backupId]['Zip'] = $zip;
            $this->saveCatalog($catalog);
        }
        $path = $this->root(false) . DIRECTORY_SEPARATOR . $zip;
        if (!is_file($path)) {
            throw new RuntimeException('ZIP-filen blev ikke fundet.');
        }
        return $path;
    }

    /** @return array<string,mixed> */
    public function importZip(string $uploadedPath, bool $assignNewIdOnCollision = false): array
    {
        if (!class_exists(ZipArchive::class)) {
            throw new RuntimeException('PHP ZipArchive er påkrævet for import.');
        }
        if (!is_file($uploadedPath)) {
            throw new RuntimeException('Den uploadede ZIP-fil blev ikke fundet.');
        }
        $zip = new ZipArchive();
        if ($zip->open($uploadedPath) !== true) {
            throw new RuntimeException('ZIP-filen kunne ikke åbnes.');
        }
        for ($i=0; $i<$zip->numFiles; $i++) {
            $name = (string)$zip->getNameIndex($i);
            if ($this->safeRelativePath($name) === '' || str_ends_with($name, '/') && $this->safeRelativePath(rtrim($name, '/')) === '') {
                $zip->close();
                throw new RuntimeException('ZIP indeholder en usikker sti: ' . $name);
            }
        }
        $root = $this->root(true);
        $stage = $root . DIRECTORY_SEPARATOR . '.import-' . bin2hex(random_bytes(6));
        $this->mkdir($stage);
        try {
            if (!$zip->extractTo($stage)) {
                throw new RuntimeException('ZIP-filen kunne ikke udpakkes.');
            }
        } finally {
            $zip->close();
        }

        try {
            $manifestPath = $stage . DIRECTORY_SEPARATOR . 'manifest.json';
            if (!is_file($manifestPath)) {
                $children = glob($stage . DIRECTORY_SEPARATOR . '*' . DIRECTORY_SEPARATOR . 'manifest.json') ?: [];
                if (count($children) === 1) {
                    $nested = dirname($children[0]);
                    $normalized = $root . DIRECTORY_SEPARATOR . '.import-normalized-' . bin2hex(random_bytes(4));
                    if (!rename($nested, $normalized)) {
                        throw new RuntimeException('Importpakken kunne ikke normaliseres.');
                    }
                    $this->removeTree($stage);
                    $stage = $normalized;
                    $manifestPath = $stage . DIRECTORY_SEPARATOR . 'manifest.json';
                }
            }
            $manifest = $this->jsonFile($manifestPath);
            $sourceId = (string)($manifest['BackupId'] ?? '');
            if (!preg_match(SiteBackupManifestService::BACKUP_ID_PATTERN, $sourceId)) {
                throw new RuntimeException('Importpakken har intet gyldigt BackupId.');
            }
            $catalog = $this->catalog();
            $backupId = $sourceId;
            if (isset($catalog[$backupId]) || is_dir($root . DIRECTORY_SEPARATOR . $backupId)) {
                if (!$assignNewIdOnCollision) {
                    throw new RuntimeException('Backup-ID findes allerede. Vælg import som nyt lokalt ID for at bevare begge pakker.');
                }
                $backupId = $this->manifest->nextBackupId(array_keys($catalog));
                $manifest['ImportedFromBackupId'] = $sourceId;
                $manifest['BackupId'] = $backupId;
                unset($manifest['ManifestSha256']);
                $manifest['ManifestSha256'] = hash('sha256', $this->manifest->canonicalJson($manifest));
                $this->write($manifestPath, $this->manifest->canonicalJson($manifest));
            }
            $report = $this->validateDirectory($stage);
            if (empty($report['Valid'])) {
                throw new RuntimeException('Importpakken er ugyldig: ' . implode(' | ', (array)($report['Errors'] ?? [])));
            }
            $final = $root . DIRECTORY_SEPARATOR . $backupId;
            if (!rename($stage, $final)) {
                throw new RuntimeException('Importpakken kunne ikke installeres i backupkataloget.');
            }
            $zipName = $backupId . '.zip';
            $this->writeZip($final, $root . DIRECTORY_SEPARATOR . $zipName);
            $entry = [
                'BackupId'=>$backupId,
                'CreatedUtc'=>(string)($manifest['CreatedUtc'] ?? gmdate('c')),
                'PluginVersion'=>(string)($manifest['PluginVersion'] ?? ''),
                'Note'=>'Importeret package' . ($sourceId !== $backupId ? ' fra ' . $sourceId : ''),
                'Directory'=>$backupId,
                'Zip'=>$zipName,
                'ManifestSha256'=>(string)($manifest['ManifestSha256'] ?? ''),
                'PayloadCount'=>count((array)($manifest['Payloads'] ?? [])),
                'MediaCount'=>count((array)($manifest['Media'] ?? [])),
                'SourceHost'=>(string)($manifest['SourceSite']['Host'] ?? ''),
                'Imported'=>true,
            ];
            $catalog[$backupId] = $entry;
            $this->saveCatalog($catalog);
            return $entry + ['Validation'=>$report];
        } catch (\Throwable $error) {
            $this->removeTree($stage);
            throw $error;
        }
    }

    /** @return array<string,mixed> */
    private function validateDirectory(string $dir): array
    {
        if (!is_dir($dir)) {
            return ['Valid'=>false,'Errors'=>['Backupmappen findes ikke.'],'Warnings'=>[]];
        }
        try {
            $manifest = $this->jsonFile($dir . DIRECTORY_SEPARATOR . 'manifest.json');
            $payloads = [];
            foreach ((array)($manifest['Payloads'] ?? []) as $entry) {
                if (!is_array($entry)) {
                    continue;
                }
                $name = (string)($entry['Name'] ?? '');
                if ($name !== '') {
                    $payloads[$name] = $this->jsonFile($dir . DIRECTORY_SEPARATOR . 'payloads' . DIRECTORY_SEPARATOR . $name . '.json');
                }
            }
            $report = $this->validator->validate($manifest, $payloads);
            $errors = (array)($report['Errors'] ?? []);
            foreach ((array)($manifest['Media'] ?? []) as $entry) {
                if (!is_array($entry)) {
                    continue;
                }
                $checks = [$entry];
                foreach ((array)($entry['Derivatives'] ?? []) as $derivative) {
                    if (is_array($derivative)) {
                        $checks[] = $derivative;
                    }
                }
                foreach ($checks as $fileEntry) {
                    $relative = $this->safeRelativePath((string)($fileEntry['RelativePath'] ?? ''));
                    $expected = strtolower((string)($fileEntry['Sha256'] ?? ''));
                    $path = $dir . DIRECTORY_SEPARATOR . 'media' . DIRECTORY_SEPARATOR . str_replace('/', DIRECTORY_SEPARATOR, $relative);
                    if ($relative === '' || !is_file($path)) {
                        $errors[] = 'Mediafil mangler: ' . $relative;
                        continue;
                    }
                    $actual = hash_file('sha256', $path);
                    if (!is_string($actual) || !hash_equals($expected, strtolower($actual))) {
                        $errors[] = 'Media SHA-256 mismatch: ' . $relative;
                    }
                }
            }
            $report['Errors'] = array_values(array_unique($errors));
            $report['Valid'] = $report['Errors'] === [];
            $report['DryRunOnly'] = false;
            return $report;
        } catch (\Throwable $error) {
            return ['Valid'=>false,'Errors'=>[$error->getMessage()],'Warnings'=>[],'DryRunOnly'=>false];
        }
    }

    /** @return array<string,array<string,mixed>> */
    private function catalog(): array
    {
        if (!function_exists('get_option')) {
            return [];
        }
        $value = get_option(self::CATALOG_OPTION, []);
        return is_array($value) ? $value : [];
    }

    /** @param array<string,array<string,mixed>> $catalog */
    private function saveCatalog(array $catalog): void
    {
        if (!function_exists('update_option') || !update_option(self::CATALOG_OPTION, $catalog, false)) {
            throw new RuntimeException('Backupkataloget kunne ikke gemmes.');
        }
    }

    private function root(bool $create): string
    {
        if (!function_exists('wp_upload_dir')) {
            if ($create) {
                throw new RuntimeException('WordPress uploads API er ikke tilgængelig.');
            }
            return '';
        }
        $uploads = wp_upload_dir();
        if (!empty($uploads['error']) || empty($uploads['basedir'])) {
            throw new RuntimeException('WordPress uploads-mappen er ikke tilgængelig.');
        }
        $root = rtrim((string)$uploads['basedir'], '/\\') . DIRECTORY_SEPARATOR . self::ROOT_DIR;
        if ($create) {
            $this->mkdir($root);
            $guard = $root . DIRECTORY_SEPARATOR . 'index.php';
            if (!is_file($guard)) {
                $this->write($guard, "<?php\n// Silence is golden.\n");
            }
        }
        return $root;
    }

    private function directory(string $backupId): string
    {
        $backupId = trim($backupId);
        if (!preg_match(SiteBackupManifestService::BACKUP_ID_PATTERN, $backupId)) {
            throw new RuntimeException('Ugyldigt BackupId.');
        }
        $catalog = $this->catalog();
        if (!isset($catalog[$backupId])) {
            throw new RuntimeException('Backup-ID findes ikke i kataloget.');
        }
        $root = $this->root(false);
        $dir = $root . DIRECTORY_SEPARATOR . $backupId;
        $realRoot = realpath($root);
        $realDir = realpath($dir);
        if ($realRoot === false || $realDir === false || strpos($realDir, rtrim($realRoot, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR) !== 0) {
            throw new RuntimeException('Backupmappen ligger uden for det administrerede katalog.');
        }
        return $realDir;
    }

    private function writeZip(string $dir, string $zipPath): void
    {
        if (!class_exists(ZipArchive::class)) {
            throw new RuntimeException('PHP ZipArchive er ikke installeret.');
        }
        $tmp = $zipPath . '.tmp-' . bin2hex(random_bytes(4));
        $zip = new ZipArchive();
        if ($zip->open($tmp, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== true) {
            throw new RuntimeException('ZIP-filen kunne ikke oprettes.');
        }
        $baseLength = strlen(rtrim($dir, DIRECTORY_SEPARATOR)) + 1;
        $iterator = new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($dir, \FilesystemIterator::SKIP_DOTS));
        foreach ($iterator as $file) {
            if (!$file->isFile()) {
                continue;
            }
            $path = $file->getPathname();
            $local = str_replace(DIRECTORY_SEPARATOR, '/', substr($path, $baseLength));
            if (!$zip->addFile($path, $local)) {
                $zip->close();
                @unlink($tmp);
                throw new RuntimeException('Kunne ikke tilføje fil til ZIP: ' . $local);
            }
        }
        if (!$zip->close()) {
            @unlink($tmp);
            throw new RuntimeException('ZIP-filen kunne ikke færdiggøres.');
        }
        if (!rename($tmp, $zipPath)) {
            @unlink($tmp);
            throw new RuntimeException('ZIP-filen kunne ikke installeres.');
        }
    }

    /** @return array<string,mixed> */
    private function jsonFile(string $path): array
    {
        if (!is_file($path) || !is_readable($path)) {
            throw new RuntimeException('Package-fil mangler: ' . basename($path));
        }
        $raw = file_get_contents($path);
        $value = is_string($raw) ? json_decode($raw, true) : null;
        if (!is_array($value)) {
            throw new RuntimeException('Package-fil indeholder ugyldig JSON: ' . basename($path));
        }
        return $value;
    }

    private function safeRelativePath(string $path): string
    {
        $path = str_replace('\\', '/', trim($path));
        if ($path === '' || str_starts_with($path, '/') || preg_match('/^[A-Za-z]:\//', $path) || str_contains($path, "\0") || preg_match('#(^|/)\.\.(/|$)#', $path)) {
            return '';
        }
        $path = trim($path, '/');
        return preg_match('#^[A-Za-z0-9._/ -]+$#u', $path) ? $path : '';
    }

    private function mkdir(string $dir): void
    {
        if (is_dir($dir)) {
            return;
        }
        $ok = function_exists('wp_mkdir_p') ? wp_mkdir_p($dir) : mkdir($dir, 0775, true);
        if (!$ok && !is_dir($dir)) {
            throw new RuntimeException('Mappe kunne ikke oprettes: ' . $dir);
        }
    }

    private function write(string $path, string $content): void
    {
        $this->mkdir(dirname($path));
        if (file_put_contents($path, $content, LOCK_EX) === false) {
            throw new RuntimeException('Fil kunne ikke skrives: ' . basename($path));
        }
    }

    private function removeTree(string $path): void
    {
        if ($path === '' || !file_exists($path)) {
            return;
        }
        if (is_file($path) || is_link($path)) {
            @unlink($path);
            return;
        }
        foreach (array_diff(scandir($path) ?: [], ['.','..']) as $item) {
            $this->removeTree($path . DIRECTORY_SEPARATOR . $item);
        }
        @rmdir($path);
    }
}
