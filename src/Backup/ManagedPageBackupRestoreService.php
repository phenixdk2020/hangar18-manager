<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;
use WP_Post;

/**
 * Restore/copy service for the existing Hangar18 managed JSON backup format.
 *
 * The service intentionally reuses Hangar18-Web-Full-Backup / Hangar18-Web-Backup
 * files and the existing PAGE_EDITOR_OPTION store. No second backup format or
 * public cutover model is introduced.
 */
final class ManagedPageBackupRestoreService
{
    public const AUDIT_OPTION = 'hangar18_manager_backup_restore_audit_v1';
    private const FILE_PATTERN = '/^Hangar18-Web-(?:Full-Backup|Backup)-\d{8}-\d{6}(?:-Post-\d+)?\.json$/';

    /** @return array<int,array<string,mixed>> */
    public function listBackups(int $limit = 40): array
    {
        $dir = $this->backupDirectory(false);
        if ($dir === '' || !is_dir($dir)) {
            return [];
        }

        $paths = glob(trailingslashit($dir) . 'Hangar18-Web-*.json') ?: [];
        usort($paths, static function (string $a, string $b): int {
            return (int) @filemtime($b) <=> (int) @filemtime($a);
        });

        $items = [];
        foreach (array_slice($paths, 0, max(1, $limit)) as $path) {
            $filename = basename($path);
            try {
                $payload = $this->readBackup($filename);
                $pages = $this->pagesFromPayload($payload);
                if (!$pages) {
                    continue;
                }
                $items[] = [
                    'Filename' => $filename,
                    'CreatedUtc' => sanitize_text_field((string) ($payload['created_utc'] ?? '')),
                    'Reason' => sanitize_text_field((string) ($payload['reason'] ?? '')),
                    'PluginVersion' => sanitize_text_field((string) ($payload['plugin_version'] ?? '')),
                    'Pages' => $pages,
                    'HasPageEditorStore' => isset($payload['page_editor']) && is_array($payload['page_editor']),
                ];
            } catch (\Throwable $error) {
                // A corrupt/unreadable backup is omitted from mutation UI.
            }
        }

        return $items;
    }

    /** @return array<string,mixed> */
    public function inspect(string $filename): array
    {
        $payload = $this->readBackup($filename);
        return [
            'Filename' => basename($filename),
            'CreatedUtc' => sanitize_text_field((string) ($payload['created_utc'] ?? '')),
            'Reason' => sanitize_text_field((string) ($payload['reason'] ?? '')),
            'PluginVersion' => sanitize_text_field((string) ($payload['plugin_version'] ?? '')),
            'Pages' => $this->pagesFromPayload($payload),
            'HasPageEditorStore' => isset($payload['page_editor']) && is_array($payload['page_editor']),
        ];
    }

    /** @return array<string,mixed> */
    public function restoreOriginal(string $filename, string $sourceKey): array
    {
        $payload = $this->readBackup($filename);
        $source = $this->sourcePage($payload, $sourceKey);
        $sourceSlug = sanitize_title((string) ($source['post_name'] ?? ''));
        if ($sourceSlug === '') {
            throw new RuntimeException('Backup-siden har ingen gyldig slug.');
        }

        $target = $this->findOriginalPage($source);
        if (!$target instanceof WP_Post || $target->post_type !== 'page') {
            throw new RuntimeException('Originalsiden kunne ikke findes sikkert.');
        }

        $targetSlug = sanitize_title((string) $target->post_name);
        if ($targetSlug === '') {
            throw new RuntimeException('Originalsiden har ingen gyldig slug.');
        }

        // Must exist before the first mutation. It remains available even if restore later fails.
        $safetyFile = $this->createSafetyBackup($target, 'B1 sikkerhedsbackup før restore fra ' . basename($filename));

        $content = $this->rebindEditorContent(
            (string) ($source['post_content'] ?? ''),
            $sourceSlug,
            $targetSlug
        );

        $result = wp_update_post([
            'ID' => (int) $target->ID,
            'post_title' => sanitize_text_field((string) ($source['post_title'] ?? $target->post_title)),
            // Preserve the live original ID and slug by deliberately omitting post_name.
            'post_status' => $this->safePostStatus((string) ($source['post_status'] ?? $target->post_status)),
            'post_parent' => absint($source['post_parent'] ?? $target->post_parent),
            'post_excerpt' => (string) ($source['post_excerpt'] ?? ''),
            'post_content' => $content,
        ], true);
        if (is_wp_error($result)) {
            throw new RuntimeException('Restore af WordPress-siden fejlede: ' . $result->get_error_message());
        }

        $this->restoreFeaturedImage((int) $target->ID, absint($source['featured_id'] ?? 0));

        $editorData = $this->sourceEditorData($payload, $sourceSlug);
        if (is_array($editorData)) {
            $this->writeEditorStoreEntry($targetSlug, $editorData);
        }

        $audit = [
            'Utc' => gmdate('c'),
            'Mode' => 'replace-original',
            'SourceBackup' => basename($filename),
            'SourcePageId' => absint($source['ID'] ?? 0),
            'SourceSlug' => $sourceSlug,
            'TargetPageId' => (int) $target->ID,
            'TargetSlug' => $targetSlug,
            'SafetyBackup' => basename($safetyFile),
            'UserId' => get_current_user_id(),
        ];
        $this->appendAudit($audit);

        return $audit;
    }

    /** @return array<string,mixed> */
    public function createCopy(string $filename, string $sourceKey): array
    {
        $payload = $this->readBackup($filename);
        $source = $this->sourcePage($payload, $sourceKey);
        $sourceSlug = sanitize_title((string) ($source['post_name'] ?? ''));
        if ($sourceSlug === '') {
            throw new RuntimeException('Backup-siden har ingen gyldig slug.');
        }

        $copySlug = $this->collisionSafeCopySlug($sourceSlug);
        $copyTitle = trim(sanitize_text_field((string) ($source['post_title'] ?? 'Side'))) . ' - kopi';
        $parentId = absint($source['post_parent'] ?? 0);
        if ($parentId > 0) {
            $parent = get_post($parentId);
            if (!$parent instanceof WP_Post || $parent->post_type !== 'page') {
                $parentId = 0;
            }
        }

        $content = $this->rebindEditorContent(
            (string) ($source['post_content'] ?? ''),
            $sourceSlug,
            $copySlug
        );

        $newId = wp_insert_post([
            'post_type' => 'page',
            'post_status' => 'draft',
            'post_title' => $copyTitle,
            'post_name' => $copySlug,
            'post_parent' => $parentId,
            'post_excerpt' => (string) ($source['post_excerpt'] ?? ''),
            'post_content' => $content,
        ], true);
        if (is_wp_error($newId)) {
            throw new RuntimeException('Kopien kunne ikke oprettes: ' . $newId->get_error_message());
        }

        $newId = (int) $newId;
        try {
            $this->restoreFeaturedImage($newId, absint($source['featured_id'] ?? 0));
            $editorData = $this->sourceEditorData($payload, $sourceSlug);
            if (is_array($editorData)) {
                $this->writeEditorStoreEntry($copySlug, $editorData);
            }
        } catch (\Throwable $error) {
            wp_delete_post($newId, true);
            throw $error;
        }

        $audit = [
            'Utc' => gmdate('c'),
            'Mode' => 'create-copy',
            'SourceBackup' => basename($filename),
            'SourcePageId' => absint($source['ID'] ?? 0),
            'SourceSlug' => $sourceSlug,
            'TargetPageId' => $newId,
            'TargetSlug' => $copySlug,
            'SafetyBackup' => '',
            'UserId' => get_current_user_id(),
        ];
        $this->appendAudit($audit);

        return $audit;
    }

    /** @return array<int,array<string,mixed>> */
    public function audit(int $limit = 30): array
    {
        $items = get_option(self::AUDIT_OPTION, []);
        if (!is_array($items)) {
            return [];
        }
        return array_slice(array_values($items), 0, max(1, $limit));
    }

    /** @return array<string,mixed> */
    private function readBackup(string $filename): array
    {
        $filename = sanitize_file_name($filename);
        if ($filename === '' || !preg_match(self::FILE_PATTERN, $filename)) {
            throw new RuntimeException('Ugyldigt backup-filnavn.');
        }

        $dir = $this->backupDirectory(false);
        $realDir = $dir !== '' ? realpath($dir) : false;
        $path = $dir !== '' ? trailingslashit($dir) . $filename : '';
        $realPath = $path !== '' ? realpath($path) : false;
        if ($realDir === false || $realPath === false) {
            throw new RuntimeException('Backup-filen blev ikke fundet.');
        }

        $prefix = rtrim($realDir, DIRECTORY_SEPARATOR) . DIRECTORY_SEPARATOR;
        if (strpos($realPath, $prefix) !== 0 || !is_readable($realPath)) {
            throw new RuntimeException('Backup-filen ligger uden for den administrerede backup-mappe.');
        }

        $json = file_get_contents($realPath);
        if ($json === false) {
            throw new RuntimeException('Backup-filen kunne ikke læses.');
        }
        $payload = json_decode($json, true);
        if (!is_array($payload)) {
            throw new RuntimeException('Backup-filen indeholder ikke gyldig JSON.');
        }

        return $payload;
    }

    /** @return array<int,array<string,mixed>> */
    private function pagesFromPayload(array $payload): array
    {
        $pages = [];
        if (isset($payload['posts']) && is_array($payload['posts'])) {
            foreach ($payload['posts'] as $post) {
                if (is_array($post) && sanitize_title((string) ($post['post_name'] ?? '')) !== '') {
                    $pages[] = $this->pageSummary($post);
                }
            }
        } elseif (isset($payload['post']) && is_array($payload['post'])) {
            $pages[] = $this->pageSummary($payload['post']);
        }
        return $pages;
    }

    /** @return array<string,mixed> */
    private function pageSummary(array $post): array
    {
        return [
            'ID' => absint($post['ID'] ?? 0),
            'Title' => sanitize_text_field((string) ($post['post_title'] ?? '')),
            'Slug' => sanitize_title((string) ($post['post_name'] ?? '')),
            'Status' => sanitize_key((string) ($post['post_status'] ?? '')),
        ];
    }

    /** @return array<string,mixed> */
    private function sourcePage(array $payload, string $sourceKey): array
    {
        $sourceKey = trim($sourceKey);
        $sourceId = absint($sourceKey);
        $sourceSlug = sanitize_title($sourceKey);

        $candidates = [];
        if (isset($payload['posts']) && is_array($payload['posts'])) {
            $candidates = $payload['posts'];
        } elseif (isset($payload['post']) && is_array($payload['post'])) {
            $candidates = [$payload['post']];
        }

        foreach ($candidates as $post) {
            if (!is_array($post)) {
                continue;
            }
            $id = absint($post['ID'] ?? 0);
            $slug = sanitize_title((string) ($post['post_name'] ?? ''));
            if (($sourceId > 0 && $id === $sourceId) || ($sourceSlug !== '' && $slug === $sourceSlug)) {
                return $post;
            }
        }

        throw new RuntimeException('Den valgte side findes ikke i backup-filen.');
    }

    private function findOriginalPage(array $source): ?WP_Post
    {
        $sourceId = absint($source['ID'] ?? 0);
        if ($sourceId > 0) {
            $post = get_post($sourceId);
            if ($post instanceof WP_Post && $post->post_type === 'page') {
                return $post;
            }
        }

        $slug = sanitize_title((string) ($source['post_name'] ?? ''));
        if ($slug === '') {
            return null;
        }
        $post = get_page_by_path($slug, OBJECT, 'page');
        return $post instanceof WP_Post ? $post : null;
    }

    private function backupDirectory(bool $create): string
    {
        $uploads = wp_upload_dir();
        if (!empty($uploads['error']) || empty($uploads['basedir'])) {
            if ($create) {
                throw new RuntimeException('WordPress uploads-mappen er ikke tilgængelig.');
            }
            return '';
        }

        $dir = trailingslashit((string) $uploads['basedir']) . 'hangar18-manager-backups';
        if ($create && !is_dir($dir) && !wp_mkdir_p($dir)) {
            throw new RuntimeException('Hangar18 backup-mappen kunne ikke oprettes.');
        }
        return $dir;
    }

    private function createSafetyBackup(WP_Post $post, string $reason): string
    {
        $dir = $this->backupDirectory(true);
        $store = get_option(\Hangar18_Manager::PAGE_EDITOR_OPTION, []);
        $slug = sanitize_title((string) $post->post_name);
        $pageEditor = [];
        if (is_array($store) && $slug !== '' && isset($store[$slug]) && is_array($store[$slug])) {
            $pageEditor[$slug] = $store[$slug];
        }

        $payload = [
            'created_utc' => gmdate('c'),
            'reason' => $reason,
            'plugin_version' => \Hangar18_Manager::VERSION,
            'page_editor' => $pageEditor,
            'post' => [
                'ID' => (int) $post->ID,
                'post_title' => (string) $post->post_title,
                'post_name' => (string) $post->post_name,
                'post_status' => (string) $post->post_status,
                'post_parent' => (int) $post->post_parent,
                'post_excerpt' => (string) $post->post_excerpt,
                'post_content' => (string) $post->post_content,
                'featured_id' => (int) get_post_thumbnail_id($post->ID),
            ],
        ];

        $baseTime = time();
        $path = '';
        for ($offset = 0; $offset < 5; $offset++) {
            $candidate = trailingslashit($dir) . sprintf(
                'Hangar18-Web-Backup-%s-Post-%d.json',
                gmdate('Ymd-His', $baseTime + $offset),
                (int) $post->ID
            );
            if (!file_exists($candidate)) {
                $path = $candidate;
                break;
            }
        }
        if ($path === '') {
            throw new RuntimeException('Kunne ikke reservere et unikt sikkerhedsbackup-filnavn.');
        }

        $json = wp_json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        if (!is_string($json) || file_put_contents($path, $json) === false) {
            throw new RuntimeException('Sikkerhedsbackup kunne ikke skrives.');
        }
        return $path;
    }

    /** @return array<string,mixed>|null */
    private function sourceEditorData(array $payload, string $sourceSlug): ?array
    {
        if (!isset($payload['page_editor']) || !is_array($payload['page_editor'])) {
            return null;
        }
        $data = $payload['page_editor'][$sourceSlug] ?? null;
        return is_array($data) ? $data : null;
    }

    /** @param array<string,mixed> $data */
    private function writeEditorStoreEntry(string $slug, array $data): void
    {
        $store = get_option(\Hangar18_Manager::PAGE_EDITOR_OPTION, []);
        if (!is_array($store)) {
            $store = [];
        }
        $store[$slug] = $data;
        update_option(\Hangar18_Manager::PAGE_EDITOR_OPTION, $store, false);
    }

    private function rebindEditorContent(string $content, string $sourceSlug, string $targetSlug): string
    {
        if ($sourceSlug === $targetSlug || $content === '') {
            return $content;
        }

        $patterns = [
            '/(\[hangar18_page_editor\s+slug=["\'])' . preg_quote($sourceSlug, '/') . '(["\'])/i',
            '/(\[hangar18_page_editor\s+slug=)' . preg_quote($sourceSlug, '/') . '(\s|\])/i',
        ];
        $replacements = [
            '$1' . $targetSlug . '$2',
            '$1' . $targetSlug . '$2',
        ];
        return (string) preg_replace($patterns, $replacements, $content);
    }

    private function collisionSafeCopySlug(string $sourceSlug): string
    {
        $base = sanitize_title($sourceSlug . '-kopi');
        $candidate = $base;
        $suffix = 2;
        while (get_page_by_path($candidate, OBJECT, 'page') instanceof WP_Post) {
            $candidate = $base . '-' . $suffix;
            $suffix++;
            if ($suffix > 1000) {
                throw new RuntimeException('Kunne ikke finde en ledig kopi-slug.');
            }
        }
        return $candidate;
    }

    private function safePostStatus(string $status): string
    {
        $status = sanitize_key($status);
        return in_array($status, ['publish', 'draft', 'pending', 'private'], true) ? $status : 'draft';
    }

    private function restoreFeaturedImage(int $postId, int $attachmentId): void
    {
        if ($attachmentId > 0 && get_post($attachmentId) instanceof WP_Post) {
            set_post_thumbnail($postId, $attachmentId);
        } else {
            delete_post_thumbnail($postId);
        }
    }

    /** @param array<string,mixed> $entry */
    private function appendAudit(array $entry): void
    {
        $audit = get_option(self::AUDIT_OPTION, []);
        if (!is_array($audit)) {
            $audit = [];
        }
        array_unshift($audit, $entry);
        update_option(self::AUDIT_OPTION, array_slice($audit, 0, 200), false);
    }
}
