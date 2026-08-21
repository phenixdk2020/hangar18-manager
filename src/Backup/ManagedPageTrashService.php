<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;
use WP_Post;

/**
 * Safe WordPress Trash flow for managed pages.
 *
 * PAGE-DELETE-001 deliberately uses the existing B1 JSON backup shape before
 * the first mutation. Page-editor/LEGO option stores are not removed when the
 * post is moved to Trash, so a B1 restore can reactivate the same page safely.
 */
final class ManagedPageTrashService
{
    public const AUDIT_OPTION = 'hangar18_manager_page_trash_audit_v1';

    /** @var array<int,string> */
    private const PROTECTED_SLUGS = [
        'hjem',
        'koeretoejer-og-materiel',
        'events',
        'billedgalleri',
    ];

    /** @return array<string,mixed> */
    public function trashBySlug(string $slug, string $confirmedTitle, int $userId): array
    {
        $slug = sanitize_title($slug);
        if ($slug === '') {
            throw new RuntimeException('Siden har ingen gyldig slug.');
        }
        if (in_array($slug, self::PROTECTED_SLUGS, true)) {
            throw new RuntimeException('Denne beskyttede kerneside kan ikke slettes fra Ultimate Designer.');
        }

        $post = get_page_by_path($slug, OBJECT, 'page');
        if (!$post instanceof WP_Post || $post->post_type !== 'page') {
            throw new RuntimeException('Siden kunne ikke findes sikkert.');
        }
        if ((string) $post->post_status === 'trash') {
            throw new RuntimeException('Siden ligger allerede i papirkurven.');
        }

        $confirmedTitle = trim($confirmedTitle);
        if ($confirmedTitle === '' || $confirmedTitle !== (string) $post->post_title) {
            throw new RuntimeException('Bekræftelsen matcher ikke sidens aktuelle titel.');
        }

        // Safety backup MUST exist before WordPress Trash is invoked.
        $safetyFile = $this->createSafetyBackup($post);
        $previousStatus = (string) $post->post_status;

        $trashed = wp_trash_post((int) $post->ID);
        if (!$trashed instanceof WP_Post) {
            throw new RuntimeException('WordPress kunne ikke flytte siden til papirkurven. Sikkerhedsbackupen er bevaret.');
        }

        $audit = [
            'Utc' => gmdate('c'),
            'Mode' => 'trash-page',
            'PageId' => (int) $post->ID,
            'Slug' => $slug,
            'Title' => (string) $post->post_title,
            'PreviousStatus' => $previousStatus,
            'SafetyBackup' => basename($safetyFile),
            'UserId' => max(0, $userId),
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

    private function createSafetyBackup(WP_Post $post): string
    {
        $uploads = wp_upload_dir();
        if (!empty($uploads['error']) || empty($uploads['basedir'])) {
            throw new RuntimeException('WordPress uploads-mappen er ikke tilgængelig.');
        }

        $dir = trailingslashit((string) $uploads['basedir']) . 'hangar18-manager-backups';
        if (!is_dir($dir) && !wp_mkdir_p($dir)) {
            throw new RuntimeException('Hangar18 backup-mappen kunne ikke oprettes.');
        }

        $slug = sanitize_title((string) $post->post_name);
        $pageEditorStore = get_option(\Hangar18_Manager::PAGE_EDITOR_OPTION, []);
        $pageEditor = [];
        if (is_array($pageEditorStore) && $slug !== '' && isset($pageEditorStore[$slug]) && is_array($pageEditorStore[$slug])) {
            $pageEditor[$slug] = $pageEditorStore[$slug];
        }

        // Same payload shape as ManagedPageBackupRestoreService/B1.
        $payload = [
            'created_utc' => gmdate('c'),
            'reason' => 'PAGE-DELETE-001 sikkerhedsbackup før WordPress Trash',
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

        $json = wp_json_encode($payload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES);
        if (!is_string($json) || $json === '') {
            throw new RuntimeException('Sikkerhedsbackupen kunne ikke serialiseres.');
        }
        $written = file_put_contents($path, $json, LOCK_EX);
        if ($written === false || $written !== strlen($json)) {
            @unlink($path);
            throw new RuntimeException('Sikkerhedsbackupen kunne ikke skrives fuldstændigt.');
        }

        return $path;
    }

    /** @param array<string,mixed> $entry */
    private function appendAudit(array $entry): void
    {
        $items = get_option(self::AUDIT_OPTION, []);
        $items = is_array($items) ? array_values($items) : [];
        array_unshift($items, $entry);
        update_option(self::AUDIT_OPTION, array_slice($items, 0, 100), false);
    }
}
