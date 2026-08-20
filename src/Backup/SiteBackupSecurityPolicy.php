<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;
use ZipArchive;

/** Security boundary for B2 package storage, import and restorable media. */
final class SiteBackupSecurityPolicy
{
    public const MAX_ZIP_BYTES = 536870912; // 512 MiB compressed upload.
    public const MAX_ENTRY_BYTES = 536870912; // 512 MiB per unpacked entry.
    public const MAX_UNPACKED_BYTES = 2147483648; // 2 GiB total unpacked.
    public const MAX_ZIP_ENTRIES = 5000;

    /** Extensions that must never be installed into a public uploads tree. */
    private const BLOCKED_EXTENSIONS = [
        'php','php3','php4','php5','php7','php8','phtml','pht','phar',
        'cgi','pl','py','rb','sh','bash','zsh','exe','dll','com','bat','cmd','ps1',
    ];

    /** @param array<string,mixed> $manifest */
    public static function assertManifestSafe(array $manifest): void
    {
        foreach ((array) ($manifest['Media'] ?? []) as $entry) {
            if (!is_array($entry)) {
                throw new RuntimeException('Media-manifest indeholder en ugyldig entry.');
            }
            self::assertSafeMediaPath((string) ($entry['RelativePath'] ?? ''));
            foreach ((array) ($entry['Derivatives'] ?? []) as $derivative) {
                if (is_array($derivative)) {
                    self::assertSafeMediaPath((string) ($derivative['RelativePath'] ?? ''));
                }
            }
        }
    }

    public static function assertSafeMediaPath(string $path): void
    {
        $path = str_replace('\\', '/', trim($path));
        if (
            $path === '' || str_contains($path, "\0") || str_starts_with($path, '/') ||
            preg_match('/^[A-Za-z]:\//', $path) || preg_match('#(^|/)\.\.(/|$)#', $path)
        ) {
            throw new RuntimeException('Usikker media-sti i B2-package: ' . $path);
        }
        $basename = strtolower(basename($path));
        if (in_array($basename, ['.htaccess','.user.ini','web.config'], true)) {
            throw new RuntimeException('Aktiv serverkonfiguration er ikke tilladt i B2 media: ' . $path);
        }
        $extension = strtolower((string) pathinfo($basename, PATHINFO_EXTENSION));
        if ($extension !== '' && in_array($extension, self::BLOCKED_EXTENSIONS, true)) {
            throw new RuntimeException('Eksekverbar filtype er ikke tilladt i B2 media: ' . $path);
        }
    }

    /** Read-only ZIP preflight before SiteBackupPackageService extracts anything. */
    public static function inspectZip(string $path): array
    {
        if (!class_exists(ZipArchive::class)) {
            throw new RuntimeException('PHP ZipArchive er påkrævet for B2 import.');
        }
        if (!is_file($path) || !is_readable($path)) {
            throw new RuntimeException('Den uploadede B2 ZIP-fil blev ikke fundet.');
        }
        $compressedBytes = (int) filesize($path);
        if ($compressedBytes <= 0 || $compressedBytes > self::MAX_ZIP_BYTES) {
            throw new RuntimeException('B2 ZIP-filen overskrider den tilladte uploadstørrelse.');
        }

        $zip = new ZipArchive();
        if ($zip->open($path) !== true) {
            throw new RuntimeException('B2 ZIP-filen kunne ikke åbnes.');
        }
        $entryCount = (int) $zip->numFiles;
        $unpacked = 0;
        try {
            if ($entryCount < 1 || $entryCount > self::MAX_ZIP_ENTRIES) {
                throw new RuntimeException('B2 ZIP-filen har et ugyldigt antal entries.');
            }
            for ($i = 0; $i < $entryCount; $i++) {
                $name = str_replace('\\', '/', (string) $zip->getNameIndex($i));
                if ($name === '' || str_contains($name, "\0") || str_starts_with($name, '/') || preg_match('/^[A-Za-z]:\//', $name) || preg_match('#(^|/)\.\.(/|$)#', $name)) {
                    throw new RuntimeException('ZIP indeholder en usikker sti: ' . $name);
                }
                if (str_ends_with($name, '/')) {
                    continue;
                }
                $stat = $zip->statIndex($i);
                $bytes = is_array($stat) ? max(0, (int) ($stat['size'] ?? 0)) : 0;
                $packed = is_array($stat) ? max(0, (int) ($stat['comp_size'] ?? 0)) : 0;
                if ($bytes > self::MAX_ENTRY_BYTES) {
                    throw new RuntimeException('ZIP-entry er for stor: ' . $name);
                }
                $unpacked += $bytes;
                if ($unpacked > self::MAX_UNPACKED_BYTES) {
                    throw new RuntimeException('B2 ZIP-filen er for stor efter udpakning.');
                }
                if ($bytes > 50 * 1024 * 1024 && $packed > 0 && ($bytes / $packed) > 250) {
                    throw new RuntimeException('ZIP-entry har mistænkelig kompressionsratio: ' . $name);
                }
                if (preg_match('#(^|/)media/(.+)$#i', $name, $match)) {
                    self::assertSafeMediaPath((string) $match[2]);
                }
                $base = strtolower(basename($name));
                if (in_array($base, ['.htaccess','.user.ini','web.config'], true)) {
                    throw new RuntimeException('ZIP indeholder aktiv serverkonfiguration: ' . $name);
                }
                $ext = strtolower((string) pathinfo($base, PATHINFO_EXTENSION));
                if ($ext !== '' && in_array($ext, self::BLOCKED_EXTENSIONS, true)) {
                    throw new RuntimeException('ZIP indeholder en eksekverbar filtype: ' . $name);
                }
            }
        } finally {
            $zip->close();
        }
        return ['Entries'=>$entryCount, 'CompressedBytes'=>$compressedBytes, 'UnpackedBytes'=>$unpacked];
    }

    /** Best-effort web-server guards around the immutable package catalog. */
    public static function hardenStorage(): void
    {
        if (!function_exists('wp_upload_dir')) {
            return;
        }
        $uploads = wp_upload_dir();
        if (!empty($uploads['error']) || empty($uploads['basedir'])) {
            throw new RuntimeException('WordPress uploads-mappen er ikke tilgængelig.');
        }
        $root = rtrim((string) $uploads['basedir'], '/\\') . DIRECTORY_SEPARATOR . 'hangar18-manager-site-backups';
        $ok = is_dir($root) || (function_exists('wp_mkdir_p') ? wp_mkdir_p($root) : mkdir($root, 0775, true));
        if (!$ok && !is_dir($root)) {
            throw new RuntimeException('B2 backup-kataloget kunne ikke oprettes.');
        }
        $guards = [
            'index.php' => "<?php\nhttp_response_code(404);\nexit;\n",
            '.htaccess' => "<IfModule mod_authz_core.c>\nRequire all denied\n</IfModule>\n<IfModule !mod_authz_core.c>\nDeny from all\n</IfModule>\n",
            'web.config' => "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<configuration><system.webServer><security><authorization><remove users=\"*\" roles=\"\" verbs=\"\"/><add accessType=\"Deny\" users=\"*\"/></authorization></security></system.webServer></configuration>\n",
        ];
        foreach ($guards as $name => $content) {
            $target = $root . DIRECTORY_SEPARATOR . $name;
            if (!is_file($target) && file_put_contents($target, $content, LOCK_EX) === false) {
                throw new RuntimeException('Kunne ikke beskytte B2 backup-kataloget med ' . $name . '.');
            }
        }
    }
}
