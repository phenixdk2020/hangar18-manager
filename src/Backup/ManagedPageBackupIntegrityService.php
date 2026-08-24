<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;

/**
 * Integrity gate for the historical B1 managed-page JSON format.
 *
 * Old Hangar18 JSON backups predate embedded checksums. This service therefore
 * validates path, size and payload structure and computes a SHA-256 fingerprint.
 * Mutation forms bind to that fingerprint; restore/copy refuses the request if
 * the file changed after the user reviewed it.
 */
final class ManagedPageBackupIntegrityService
{
    private const FILE_PATTERN = '/^Hangar18-Web-(?:Full-Backup|Backup)-\d{8}-\d{6}(?:-Post-\d+)?\.json$/';
    private const MAX_BYTES = 134217728; // 128 MiB defensive ceiling for legacy JSON.

    /** @return array<string,mixed> */
    public function inspect(string $filename): array
    {
        [$safeName, $path] = $this->resolve($filename);
        $size = filesize($path);
        if ($size === false || $size <= 0) {
            throw new RuntimeException('Backup-filen er tom eller størrelsen kunne ikke læses.');
        }
        if ($size > self::MAX_BYTES) {
            throw new RuntimeException('Backup-filen overskrider den tilladte størrelse for B1 JSON.');
        }

        $sha = strtolower((string) hash_file('sha256', $path));
        if (!preg_match('/^[a-f0-9]{64}$/', $sha)) {
            throw new RuntimeException('SHA-256 af backup-filen kunne ikke beregnes.');
        }

        $json = file_get_contents($path);
        if ($json === false) {
            throw new RuntimeException('Backup-filen kunne ikke læses.');
        }
        try {
            $payload = json_decode($json, true, 512, JSON_THROW_ON_ERROR);
        } catch (\JsonException $error) {
            throw new RuntimeException('Backup-filen indeholder ikke gyldig JSON: ' . $error->getMessage(), 0, $error);
        }
        if (!is_array($payload)) {
            throw new RuntimeException('Backup-filen har ikke et gyldigt JSON top-level objekt.');
        }

        $pages = $this->pages($payload);
        if ($pages === []) {
            throw new RuntimeException('Backup-filen indeholder ingen gyldig WordPress-side.');
        }
        if (isset($payload['page_editor']) && !is_array($payload['page_editor'])) {
            throw new RuntimeException('Backup-filen har ugyldig page_editor state.');
        }

        return [
            'Valid' => true,
            'Filename' => $safeName,
            'Sha256' => $sha,
            'Bytes' => (int) $size,
            'PageCount' => count($pages),
            'HasPageEditorStore' => isset($payload['page_editor']) && is_array($payload['page_editor']),
            'Payload' => $payload,
        ];
    }

    /** @return array<string,mixed> */
    public function assertUnchanged(string $filename, string $expectedSha256): array
    {
        $expected = strtolower(trim($expectedSha256));
        if (!preg_match('/^[a-f0-9]{64}$/', $expected)) {
            throw new RuntimeException('Restore-requesten mangler en gyldig backup SHA-256. Genindlæs backup-panelet.');
        }
        $report = $this->inspect($filename);
        $actual = strtolower((string) ($report['Sha256'] ?? ''));
        if (!hash_equals($expected, $actual)) {
            throw new RuntimeException('Backup-filen er ændret siden den blev vist. Genindlæs og kontrollér backupen igen.');
        }
        return $report;
    }

    /** @return array{0:string,1:string} */
    private function resolve(string $filename): array
    {
        $filename = sanitize_file_name($filename);
        if ($filename === '' || !preg_match(self::FILE_PATTERN, $filename)) {
            throw new RuntimeException('Ugyldigt backup-filnavn.');
        }
        $uploads = wp_upload_dir();
        if (!empty($uploads['error']) || empty($uploads['basedir'])) {
            throw new RuntimeException('WordPress uploads-mappen er ikke tilgængelig.');
        }
        $dir = trailingslashit((string) $uploads['basedir']) . 'hangar18-manager-backups';
        $realDir = realpath($dir);
        $realPath = realpath(trailingslashit($dir) . $filename);
        if ($realDir === false || $realPath === false) {
            throw new RuntimeException('Backup-filen blev ikke fundet.');
        }
        $prefix = rtrim($realDir, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR;
        if (strpos($realPath, $prefix) !== 0 || !is_file($realPath) || !is_readable($realPath)) {
            throw new RuntimeException('Backup-filen ligger uden for den administrerede backup-mappe eller kan ikke læses.');
        }
        return [$filename, $realPath];
    }

    /** @return array<int,array<string,mixed>> */
    private function pages(array $payload): array
    {
        $candidates = [];
        if (isset($payload['posts']) && is_array($payload['posts'])) {
            $candidates = $payload['posts'];
        } elseif (isset($payload['post']) && is_array($payload['post'])) {
            $candidates = [$payload['post']];
        }

        $valid = [];
        foreach ($candidates as $post) {
            if (!is_array($post)) {
                continue;
            }
            $slug = sanitize_title((string) ($post['post_name'] ?? ''));
            $id = absint($post['ID'] ?? 0);
            if ($slug === '' && $id <= 0) {
                continue;
            }
            if (array_key_exists('post_content', $post) && !is_scalar($post['post_content']) && $post['post_content'] !== null) {
                throw new RuntimeException('Backup-siden har ugyldigt post_content-format.');
            }
            $valid[] = $post;
        }
        return $valid;
    }
}
