<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class EventDetailFactsMigration
{
    private const META = '_h18_vd_event_detail_facts_v0185';
    private const BACKUP_META = '_h18_vd_event_detail_facts_backup_v0185';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'ensure'], 28);
    }

    public static function ensure(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        $page = get_page_by_path('event-detalje', OBJECT, 'page');
        if (!$page instanceof \WP_Post) { return; }
        $postId = (int) $page->ID;
        if (get_post_meta($postId, self::META, true)) { return; }

        $before = LayoutModel::get($postId);
        $nodes = isset($before['nodes']) && is_array($before['nodes']) ? array_values($before['nodes']) : [];
        $ids = [];
        foreach ($nodes as $node) {
            if (is_array($node)) { $ids[(string) ($node['id'] ?? '')] = true; }
        }
        // Only replace the known v0.1.80 composable pair. Custom detail pages are left untouched.
        if (empty($ids['event-date']) || empty($ids['event-location']) || empty($ids['event-title']) || empty($ids['detail-section'])) {
            update_post_meta($postId, self::META, ['status' => 'skipped-custom-layout', 'checkedUtc' => gmdate('c')]);
            return;
        }

        update_post_meta($postId, self::BACKUP_META, $before);
        $next = [];
        foreach ($nodes as $node) {
            if (!is_array($node)) { continue; }
            $id = (string) ($node['id'] ?? '');
            if ($id === 'event-date' || $id === 'event-location') { continue; }
            if (in_array($id, ['eventfield-about', 'eventfield-program', 'eventfield-practical'], true)) {
                if (!isset($node['props']) || !is_array($node['props'])) { $node['props'] = []; }
                $node['props']['showHeading'] = true;
                $node['props']['showWhenEmpty'] = true;
                if (!array_key_exists('headingFontSize', $node['props'])) { $node['props']['headingFontSize'] = 40; }
                if (!array_key_exists('headingFontWeight', $node['props'])) { $node['props']['headingFontWeight'] = 400; }
                if (!array_key_exists('headingLineHeight', $node['props'])) { $node['props']['headingLineHeight'] = 1.15; }
                if (!array_key_exists('headingGap', $node['props'])) { $node['props']['headingGap'] = 12; }
                if (!array_key_exists('fontSize', $node['props'])) { $node['props']['fontSize'] = 16; }
                if (!array_key_exists('fontWeight', $node['props'])) { $node['props']['fontWeight'] = 400; }
                if (!array_key_exists('lineHeight', $node['props'])) { $node['props']['lineHeight'] = 1.5; }
            }
            $next[] = $node;
        }
        $next[] = [
            'id' => 'event-facts',
            'type' => 'eventfacts',
            'parentId' => 'detail-section',
            'order' => 30,
            'geometry' => self::geometry(3, 22, 114, 12),
            'props' => [
                'recordId' => '',
                'showDate' => true,
                'showTime' => true,
                'showLocation' => true,
                'showAddress' => true,
                'showContact' => true,
                'gap' => 12,
                'minCardWidth' => 150,
                'cardBackground' => '#f4f1e8',
                'accentColor' => '#c3ae83',
                'labelColor' => '#30382a',
                'valueColor' => '#30382a',
                'paddingX' => 16,
                'paddingY' => 16,
                'radius' => 0,
                'labelFontFamily' => 'system',
                'labelFontSize' => 16,
                'labelFontWeight' => 700,
                'valueFontFamily' => 'system',
                'valueFontSize' => 16,
                'valueFontWeight' => 400,
                'lineHeight' => 1.35,
            ],
        ];
        $model = $before;
        $model['nodes'] = $next;
        $version = LayoutModel::saveVersion($postId, $model, get_current_user_id(), 'v0.1.85: Eventfaktabånd + justerbar Eventfelt-typografi');
        update_post_meta($postId, self::META, ['status' => 'migrated', 'version' => $version, 'migratedUtc' => gmdate('c')]);
    }

    /** @return array<string,mixed> */
    private static function geometry(int $x, int $y, int $w, int $h): array
    {
        return [
            'desktop' => ['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h],
            'laptop' => ['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
            'tablet' => ['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],
            'mobile' => ['x'=>0,'y'=>$y,'w'=>120,'h'=>$h,'inheritDesktop'=>false],
        ];
    }

    private function __construct() {}
}
