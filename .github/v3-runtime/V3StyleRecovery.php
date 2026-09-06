<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

/**
 * V3 Alpha.7 surgical recovery for the duplicated historical v0.1.72
 * SiteDesignHarmonizer pass that occurred after portable V1 -> V3 import.
 *
 * Safety contract:
 * - detects a duplicated harmonizer history note; never guesses by colour;
 * - restores only props changed by the duplicated pass;
 * - restores a prop only when its current value still equals the bad pass,
 *   so later user styling is preserved;
 * - never changes geometry, hierarchy, content identity or node order;
 * - writes a normal Designer version for rollback and keeps all history.
 */
final class V3StyleRecovery
{
    private const LEGACY_NOTE = 'Design harmoniseret med Hjem (v0.1.72)';
    private const RECOVERY_NOTE = 'V3 Alpha.7: gendan V1-styling efter dobbelt v0.1.72-harmonisering';
    private const DONE_META = '_vdm_v3_alpha7_style_recovery';
    private const BACKUP_META = '_vdm_v3_alpha7_style_recovery_backup';
    private const TARGET_SLUGS = ['om-foreningen', 'koeretoejer-og-materiel', 'events', 'billedgalleri', 'bliv-medlem', 'kontakt'];

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'run'], 35);
    }

    public static function run(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        foreach (self::TARGET_SLUGS as $slug) {
            $page = get_page_by_path($slug, OBJECT, 'page');
            if (!$page instanceof \WP_Post) {
                continue;
            }
            $postId = (int) $page->ID;
            if ($postId <= 0 || !metadata_exists('post', $postId, LayoutModel::META)) {
                continue;
            }
            $done = get_post_meta($postId, self::DONE_META, true);
            if (is_array($done) && ($done['status'] ?? '') === 'complete') {
                continue;
            }
            self::repairPage($postId, $slug);
        }
    }

    private static function repairPage(int $postId, string $slug): void
    {
        $history = LayoutModel::history($postId);
        $harmonized = [];
        foreach ($history as $index => $entry) {
            if ((string) ($entry['note'] ?? '') === self::LEGACY_NOTE) {
                $harmonized[] = (int) $index;
            }
        }

        // A legitimate V1 page has one historical pass. The V3 import bug is
        // proven only when the same harmonizer note occurs at least twice.
        if (count($harmonized) < 2) {
            update_post_meta($postId, self::DONE_META, [
                'version' => VDM_VERSION,
                'status' => 'not-needed',
                'slug' => $slug,
                'harmonizerPasses' => count($harmonized),
                'checkedUtc' => gmdate('c'),
            ]);
            return;
        }

        $badIndex = (int) end($harmonized);
        if ($badIndex <= 0 || !isset($history[$badIndex - 1], $history[$badIndex])) {
            return;
        }
        $beforeEntry = $history[$badIndex - 1];
        $badEntry = $history[$badIndex];
        if (!isset($beforeEntry['model'], $badEntry['model']) || !is_array($beforeEntry['model']) || !is_array($badEntry['model'])) {
            return;
        }

        $before = LayoutModel::normalize($beforeEntry['model']);
        $bad = LayoutModel::normalize($badEntry['model']);
        $current = LayoutModel::get($postId);
        $currentFingerprint = self::layoutFingerprint($current);
        [$repaired, $restored] = self::restoreChangedProps($current, $before, $bad);
        $repaired = LayoutModel::normalize($repaired);

        if (self::layoutFingerprint($repaired) !== $currentFingerprint) {
            update_post_meta($postId, self::DONE_META, [
                'version' => VDM_VERSION,
                'status' => 'blocked-fingerprint',
                'slug' => $slug,
                'checkedUtc' => gmdate('c'),
            ]);
            return;
        }

        if ($restored <= 0 || LayoutModel::structuralDigest($repaired) === LayoutModel::structuralDigest($current)) {
            update_post_meta($postId, self::DONE_META, [
                'version' => VDM_VERSION,
                'status' => 'complete',
                'slug' => $slug,
                'restoredProps' => 0,
                'badVersion' => (int) ($badEntry['version'] ?? 0),
                'sourceVersion' => (int) ($beforeEntry['version'] ?? 0),
                'completedUtc' => gmdate('c'),
            ]);
            return;
        }

        if (!metadata_exists('post', $postId, self::BACKUP_META)) {
            update_post_meta($postId, self::BACKUP_META, [
                'savedUtc' => gmdate('c'),
                'version' => (int) get_post_meta($postId, LayoutModel::VERSION_META, true),
                'digest' => LayoutModel::structuralDigest($current),
                'model' => $current,
            ]);
        }

        $newVersion = LayoutModel::saveVersion($postId, $repaired, get_current_user_id(), self::RECOVERY_NOTE);
        $stored = LayoutModel::get($postId);
        if (self::layoutFingerprint($stored) !== $currentFingerprint || LayoutModel::structuralDigest($stored) !== LayoutModel::structuralDigest($repaired)) {
            update_post_meta($postId, self::DONE_META, [
                'version' => VDM_VERSION,
                'status' => 'attention',
                'slug' => $slug,
                'restoredProps' => $restored,
                'checkedUtc' => gmdate('c'),
            ]);
            return;
        }

        update_post_meta($postId, self::DONE_META, [
            'version' => VDM_VERSION,
            'status' => 'complete',
            'slug' => $slug,
            'restoredProps' => $restored,
            'badVersion' => (int) ($badEntry['version'] ?? 0),
            'sourceVersion' => (int) ($beforeEntry['version'] ?? 0),
            'recoveryVersion' => $newVersion,
            'completedUtc' => gmdate('c'),
        ]);
    }

    /**
     * @param array<string,mixed> $current
     * @param array<string,mixed> $before
     * @param array<string,mixed> $bad
     * @return array{0:array<string,mixed>,1:int}
     */
    private static function restoreChangedProps(array $current, array $before, array $bad): array
    {
        $beforeNodes = self::nodesById($before);
        $badNodes = self::nodesById($bad);
        $nodes = isset($current['nodes']) && is_array($current['nodes']) ? array_values($current['nodes']) : [];
        $restored = 0;

        foreach ($nodes as &$node) {
            if (!is_array($node)) {
                continue;
            }
            $id = (string) ($node['id'] ?? '');
            if ($id === '' || !isset($beforeNodes[$id], $badNodes[$id])) {
                continue;
            }
            $beforeNode = $beforeNodes[$id];
            $badNode = $badNodes[$id];
            if ((string) ($node['type'] ?? '') !== (string) ($beforeNode['type'] ?? '') || (string) ($node['type'] ?? '') !== (string) ($badNode['type'] ?? '')) {
                continue;
            }

            $beforeProps = isset($beforeNode['props']) && is_array($beforeNode['props']) ? $beforeNode['props'] : [];
            $badProps = isset($badNode['props']) && is_array($badNode['props']) ? $badNode['props'] : [];
            $currentProps = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            $keys = array_unique(array_merge(array_keys($beforeProps), array_keys($badProps)));

            foreach ($keys as $key) {
                $key = (string) $key;
                $beforeExists = array_key_exists($key, $beforeProps);
                $badExists = array_key_exists($key, $badProps);
                $beforeValue = $beforeExists ? $beforeProps[$key] : null;
                $badValue = $badExists ? $badProps[$key] : null;
                if ($beforeExists === $badExists && $beforeValue === $badValue) {
                    continue;
                }

                // Preserve any explicit post-bug user change.
                $currentExists = array_key_exists($key, $currentProps);
                $currentValue = $currentExists ? $currentProps[$key] : null;
                if ($currentExists !== $badExists || $currentValue !== $badValue) {
                    continue;
                }

                if ($beforeExists) {
                    $currentProps[$key] = $beforeValue;
                } else {
                    unset($currentProps[$key]);
                }
                $restored++;
            }
            $node['props'] = $currentProps;
        }
        unset($node);
        $current['nodes'] = $nodes;
        return [$current, $restored];
    }

    /** @param array<string,mixed> $model @return array<string,array<string,mixed>> */
    private static function nodesById(array $model): array
    {
        $result = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node)) {
                continue;
            }
            $id = (string) ($node['id'] ?? '');
            if ($id !== '') {
                $result[$id] = $node;
            }
        }
        return $result;
    }

    /** @param array<string,mixed> $model */
    private static function layoutFingerprint(array $model): string
    {
        $rows = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node)) {
                continue;
            }
            $rows[] = [
                'id' => (string) ($node['id'] ?? ''),
                'type' => (string) ($node['type'] ?? ''),
                'parentId' => (string) ($node['parentId'] ?? ''),
                'order' => (int) ($node['order'] ?? 0),
                'geometry' => $node['geometry'] ?? [],
            ];
        }
        return hash('sha256', (string) wp_json_encode($rows, JSON_UNESCAPED_SLASHES | JSON_UNESCAPED_UNICODE));
    }

    private function __construct() {}
}
