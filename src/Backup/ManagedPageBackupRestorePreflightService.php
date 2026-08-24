<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Backup;

use RuntimeException;

/**
 * Read-only safety gate for B1 replacement restores.
 *
 * Legacy single-page backups may contain an embedded Page Editor marker but no
 * central page_editor store entry. Replacing a live editor page from such a
 * backup would be ambiguous because the newer central store can override the
 * restored marker. Copy-mode is intentionally not blocked by this editor-state
 * rule, but both modes use ManagedPageBackupIntegrityService before mutation.
 */
final class ManagedPageBackupRestorePreflightService
{
    /** @return array<string,mixed> */
    public function analyzeReplace(string $filename, string $sourceKey): array
    {
        $integrity = (new ManagedPageBackupIntegrityService())->inspect($filename);
        $payload = is_array($integrity['Payload'] ?? null) ? $integrity['Payload'] : [];
        $source = $this->findSourcePage($payload, $sourceKey);
        $slug = sanitize_title((string) ($source['post_name'] ?? ''));
        if ($slug === '') {
            throw new RuntimeException('Backup-siden har ingen gyldig slug.');
        }

        $content = (string) ($source['post_content'] ?? '');
        $usesPageEditor = strpos($content, 'HANGAR18-PAGE-EDITOR-DATA') !== false ||
            stripos($content, '[hangar18_page_editor') !== false;
        $editorData = $payload['page_editor'][$slug] ?? null;
        $hasEditorStore = is_array($editorData);
        $allowed = !$usesPageEditor || $hasEditorStore;

        return [
            'Allowed' => $allowed,
            'SourceSlug' => $slug,
            'UsesPageEditor' => $usesPageEditor,
            'HasPageEditorStoreEntry' => $hasEditorStore,
            'EditorDataSource' => $hasEditorStore ? 'page-editor-store' : ($usesPageEditor ? 'embedded-marker-only' : 'not-required'),
            'BackupSha256' => (string) ($integrity['Sha256'] ?? ''),
            'BackupBytes' => (int) ($integrity['Bytes'] ?? 0),
            'BackupPageCount' => (int) ($integrity['PageCount'] ?? 0),
            'IntegrityValid' => !empty($integrity['Valid']),
            'Reason' => $allowed
                ? 'Backup-kilden har gyldig JSON/SHA-integritet og tilstrækkelig state til replace-original.'
                : 'Replace-original er låst: backup-siden bruger Page Editor, men backupfilen mangler den centrale page_editor state. Brug Opret som kopi eller en full-backup med editor-data.',
        ];
    }

    /** @return array<string,mixed> */
    private function findSourcePage(array $payload, string $sourceKey): array
    {
        $sourceKey = trim($sourceKey);
        $sourceId = absint($sourceKey);
        $sourceSlug = sanitize_title($sourceKey);
        $posts = [];
        if (isset($payload['posts']) && is_array($payload['posts'])) {
            $posts = $payload['posts'];
        } elseif (isset($payload['post']) && is_array($payload['post'])) {
            $posts = [$payload['post']];
        }
        foreach ($posts as $post) {
            if (!is_array($post)) {
                continue;
            }
            $id = absint($post['ID'] ?? 0);
            $slug = sanitize_title((string) ($post['post_name'] ?? ''));
            if (($sourceId > 0 && $sourceId === $id) || ($sourceSlug !== '' && $sourceSlug === $slug)) {
                return $post;
            }
        }
        throw new RuntimeException('Den valgte side findes ikke i backup-filen.');
    }
}
