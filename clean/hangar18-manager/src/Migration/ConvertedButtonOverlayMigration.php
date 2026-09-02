<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

/**
 * v0.1.82 one-time repair for buttons created by VisualBlockConversionService.
 *
 * Converted button IDs contain an 8-character source suffix derived from the
 * page ID plus the immutable external source snapshot. That provenance lets us
 * repair only converter-owned buttons and leave ordinary Designer buttons
 * untouched.
 */
final class ConvertedButtonOverlayMigration
{
    public const MARKER_META = '_h18_vd_converted_button_overlay_v0182';
    public const BACKUP_META = '_h18_vd_converted_button_overlay_backup_v0182';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'migrateAll'], 20);
    }

    public static function migrateAll(): void
    {
        if (!current_user_can('edit_pages')) {
            return;
        }

        $ids = get_posts([
            'post_type' => 'page',
            'post_status' => 'any',
            'numberposts' => -1,
            'fields' => 'ids',
            'orderby' => 'ID',
            'order' => 'ASC',
            'meta_key' => PageConversionService::STATE_META,
        ]);
        if (!is_array($ids)) {
            return;
        }

        foreach ($ids as $id) {
            self::migratePage(absint($id));
        }
    }

    private static function migratePage(int $postId): void
    {
        if ($postId <= 0 || metadata_exists('post', $postId, self::MARKER_META)) {
            return;
        }

        $source = get_post_meta($postId, PageConversionService::SOURCE_META, true);
        $source = is_array($source) ? $source : [];
        $sourceType = sanitize_key((string) ($source['sourceType'] ?? ''));
        $sourceHtml = isset($source['sourceHtml']) && is_string($source['sourceHtml']) ? $source['sourceHtml'] : '';
        if ($sourceType !== 'external' || $sourceHtml === '') {
            self::mark($postId, 'not-applicable', 0, 0);
            return;
        }

        $suffix = substr(hash('sha256', (string) $postId . '|' . $sourceHtml), 0, 8);
        $activeChanged = 0;
        $candidateChanged = 0;

        if (metadata_exists('post', $postId, LayoutModel::META)) {
            $raw = get_post_meta($postId, LayoutModel::META, true);
            if (is_array($raw)) {
                $current = LayoutModel::normalize($raw);
                [$next, $activeChanged] = self::upgradeModelForConverter($current, $suffix);
                if ($activeChanged > 0) {
                    if (!metadata_exists('post', $postId, self::BACKUP_META)) {
                        update_post_meta($postId, self::BACKUP_META, $raw);
                    }
                    LayoutModel::saveVersion(
                        $postId,
                        $next,
                        max(0, get_current_user_id()),
                        'v0.1.82: konverterede knapper ændret til flydende Designer-knapper'
                    );
                }
            }
        }

        $candidate = get_post_meta($postId, PageConversionService::CANDIDATE_META, true);
        if (is_array($candidate)) {
            [$candidateNext, $candidateChanged] = self::upgradeModelForConverter(LayoutModel::normalize($candidate), $suffix);
            if ($candidateChanged > 0) {
                update_post_meta($postId, PageConversionService::CANDIDATE_META, LayoutModel::normalize($candidateNext));
            }
        }

        self::mark(
            $postId,
            ($activeChanged + $candidateChanged) > 0 ? 'migrated' : 'checked',
            $activeChanged,
            $candidateChanged
        );
    }

    /**
     * Pure migration kernel used by release QA as well as the WordPress pass.
     *
     * @param array<string,mixed> $model
     * @return array{0:array<string,mixed>,1:int}
     */
    public static function upgradeModelForConverter(array $model, string $suffix): array
    {
        if (!preg_match('/^[a-f0-9]{8}$/', $suffix)) {
            return [$model, 0];
        }
        if (!isset($model['nodes']) || !is_array($model['nodes'])) {
            return [$model, 0];
        }

        $prefix = 'button-' . $suffix . '-';
        $changed = 0;
        foreach ($model['nodes'] as &$node) {
            if (!is_array($node)
                || (string) ($node['type'] ?? '') !== 'button'
                || !str_starts_with((string) ($node['id'] ?? ''), $prefix)
                || !isset($node['props'])
                || !is_array($node['props'])
                || (string) ($node['props']['placementMode'] ?? 'normal') !== 'normal') {
                continue;
            }
            $node['props']['placementMode'] = 'overlay';
            $changed++;
        }
        unset($node);

        return [$model, $changed];
    }

    private static function mark(int $postId, string $status, int $activeChanged, int $candidateChanged): void
    {
        update_post_meta($postId, self::MARKER_META, [
            'version' => '0.1.82',
            'status' => sanitize_key($status),
            'activeChanged' => max(0, $activeChanged),
            'candidateChanged' => max(0, $candidateChanged),
            'migratedUtc' => gmdate('c'),
        ]);
    }

    private function __construct()
    {
    }
}
