<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\HierarchyNormalizer;
use VisualDesignerManager\Model\LayoutModel;

/**
 * v0.1.68 persistent migration for existing Visual Designer pages.
 *
 * LayoutModel::get() has long normalized legacy root elements in memory. This
 * migration makes that hierarchy permanent in post meta without asking the
 * editor to open and save every page manually.
 */
final class CanvasSectionMigration
{
    public const TARGET_VERSION = '0.1.68';
    public const OPTION = 'h18_vd_canvas_section_migration_v0168';
    public const BACKUP_META = '_h18_clean_layout_pre_section_v0168';
    public const NOTE = 'Automatisk migrering til Section-struktur (v0.1.68)';

    public static function register(): void
    {
        if (is_admin()) {
            add_action('admin_init', [self::class, 'maybeRun'], 5);
        }
    }

    public static function maybeRun(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }
        if (function_exists('wp_doing_ajax') && wp_doing_ajax()) {
            return;
        }

        $previous = get_option(self::OPTION, []);
        if (is_array($previous)
            && (string) ($previous['version'] ?? '') === self::TARGET_VERSION
            && empty($previous['failed'])) {
            return;
        }

        $postIds = get_posts([
            'post_type' => 'page',
            'post_status' => ['publish', 'draft', 'pending', 'private', 'future'],
            'posts_per_page' => -1,
            'fields' => 'ids',
            'orderby' => 'ID',
            'order' => 'ASC',
            'meta_key' => LayoutModel::META,
            'no_found_rows' => true,
            'suppress_filters' => false,
        ]);
        $postIds = is_array($postIds) ? array_values(array_map('absint', $postIds)) : [];

        $result = [
            'version' => self::TARGET_VERSION,
            'ranUtc' => gmdate('c'),
            'migrated' => 0,
            'skipped' => 0,
            'failed' => [],
        ];

        foreach ($postIds as $postId) {
            $raw = get_post_meta($postId, LayoutModel::META, true);
            if (!is_array($raw) || !self::needsMigration($raw)) {
                $result['skipped']++;
                continue;
            }

            $historyExists = metadata_exists('post', $postId, LayoutModel::HISTORY_META);
            $versionExists = metadata_exists('post', $postId, LayoutModel::VERSION_META);
            $historyBefore = get_post_meta($postId, LayoutModel::HISTORY_META, true);
            $versionBefore = get_post_meta($postId, LayoutModel::VERSION_META, true);
            $mutated = false;

            try {
                self::writeRawBackupOnce($postId, $raw);
                $originalIds = self::nodeIds($raw);
                $normalized = LayoutModel::normalize($raw);
                if (!HierarchyNormalizer::isCanonical((array) ($normalized['nodes'] ?? []))) {
                    throw new \RuntimeException('Canonical Section-struktur kunne ikke verificeres.');
                }
                self::assertIdsPreserved($originalIds, $normalized);

                $mutated = true;
                LayoutModel::saveVersion($postId, $normalized, get_current_user_id(), self::NOTE);

                $saved = get_post_meta($postId, LayoutModel::META, true);
                if (!is_array($saved) || !HierarchyNormalizer::isCanonical((array) ($saved['nodes'] ?? []))) {
                    throw new \RuntimeException('Gemte layoutdata bestod ikke Section-verifikation.');
                }
                self::assertIdsPreserved($originalIds, $saved);
                clean_post_cache($postId);
                $result['migrated']++;
            } catch (\Throwable $error) {
                if ($mutated) {
                    update_post_meta($postId, LayoutModel::META, $raw);
                    self::restoreMeta($postId, LayoutModel::HISTORY_META, $historyExists, $historyBefore);
                    self::restoreMeta($postId, LayoutModel::VERSION_META, $versionExists, $versionBefore);
                    clean_post_cache($postId);
                }
                $result['failed'][] = [
                    'postId' => $postId,
                    'message' => sanitize_text_field($error->getMessage()),
                ];
            }
        }

        update_option(self::OPTION, $result, false);
    }

    /** @param array<string,mixed> $model */
    public static function needsMigration(array $model): bool
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        if (!$nodes) {
            return false;
        }

        $map = [];
        foreach ($nodes as $node) {
            if (!is_array($node)) {
                return true;
            }
            $id = self::cleanId($node['id'] ?? '');
            if ($id === '' || isset($map[$id])) {
                return true;
            }
            $map[$id] = [
                'type' => sanitize_key((string) ($node['type'] ?? '')),
                'parentId' => self::cleanId($node['parentId'] ?? ''),
            ];
        }

        foreach ($map as $id => $node) {
            $type = (string) $node['type'];
            $parent = (string) $node['parentId'];
            if ($type === 'section') {
                if ($parent !== '') {
                    return true;
                }
                continue;
            }
            if ($parent === '') {
                return true;
            }
            if (!isset($map[$parent]) || !in_array((string) $map[$parent]['type'], ['section', 'container'], true)) {
                return true;
            }

            $seen = [];
            $cursor = $id;
            while ($cursor !== '') {
                if (isset($seen[$cursor]) || !isset($map[$cursor])) {
                    return true;
                }
                $seen[$cursor] = true;
                $cursor = (string) $map[$cursor]['parentId'];
            }
        }

        return false;
    }

    /** @param array<string,mixed> $raw */
    private static function writeRawBackupOnce(int $postId, array $raw): void
    {
        if (metadata_exists('post', $postId, self::BACKUP_META)) {
            return;
        }
        $json = wp_json_encode($raw, JSON_UNESCAPED_UNICODE | JSON_UNESCAPED_SLASHES);
        update_post_meta($postId, self::BACKUP_META, [
            'version' => self::TARGET_VERSION,
            'savedUtc' => gmdate('c'),
            'digest' => hash('sha256', is_string($json) ? $json : ''),
            'model' => $raw,
        ]);
    }

    /** @param array<string,mixed> $model @return array<int,string> */
    private static function nodeIds(array $model): array
    {
        $ids = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node)) {
                continue;
            }
            $id = self::cleanId($node['id'] ?? '');
            if ($id !== '') {
                $ids[$id] = true;
            }
        }
        return array_keys($ids);
    }

    /** @param array<int,string> $originalIds @param array<string,mixed> $model */
    private static function assertIdsPreserved(array $originalIds, array $model): void
    {
        $saved = array_fill_keys(self::nodeIds($model), true);
        foreach ($originalIds as $id) {
            if (!isset($saved[$id])) {
                throw new \RuntimeException('Migreringen ville miste element-ID: ' . $id);
            }
        }
    }

    /** @param mixed $value */
    private static function restoreMeta(int $postId, string $key, bool $existed, $value): void
    {
        if ($existed) {
            update_post_meta($postId, $key, $value);
        } else {
            delete_post_meta($postId, $key);
        }
    }

    /** @param mixed $value */
    private static function cleanId($value): string
    {
        return substr(strtolower((string) preg_replace('/[^a-z0-9._-]/i', '', (string) $value)), 0, 100);
    }
}
