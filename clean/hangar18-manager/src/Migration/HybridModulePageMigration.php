<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class HybridModulePageMigration
{
    public const META = '_h18_vd_hybrid_module_slots_v0178';
    private const BACKUP_META = '_h18_vd_hybrid_module_backup_v0178';
    private const DETAIL_META = '_h18_vd_module_detail_template_v0178';
    private const V0180_COLLECTION_META = '_h18_vd_collection_heading_v0180';
    private const V0180_COLLECTION_BACKUP = '_h18_vd_collection_heading_backup_v0180';
    private const V0180_EVENT_DETAIL_META = '_h18_vd_event_detail_composable_v0180';
    private const V0180_EVENT_DETAIL_BACKUP = '_h18_vd_event_detail_backup_v0180';

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'ensure'], 27);
    }

    public static function ensure(): void
    {
        if (!current_user_can('edit_pages')) { return; }
        foreach ([
            'events' => ['module'=>'events','detailSlug'=>'event-detalje','detailTitle'=>'Eventdetalje','detailType'=>'eventdetail','query'=>'h18_event'],
            'billedgalleri' => ['module'=>'galleries','detailSlug'=>'album-detalje','detailTitle'=>'Albumdetalje','detailType'=>'gallerydetail','query'=>'h18_gallery'],
            'koeretoejer-og-materiel' => ['module'=>'vehicles','detailSlug'=>'koeretoej-detalje','detailTitle'=>'Køretøjsdetalje','detailType'=>'vehicledetail','query'=>'h18_vehicle'],
        ] as $slug => $config) {
            $page = get_page_by_path($slug, OBJECT, 'page');
            if (!$page instanceof \WP_Post) { continue; }
            $postId = (int) $page->ID;
            $detailId = self::ensureDetailPage($postId, $config);
            if (get_post_meta($postId, self::META, true)) { continue; }
            $old = LayoutModel::get($postId);
            update_post_meta($postId, self::BACKUP_META, $old);
            $model = self::slotModel();
            LayoutModel::saveVersion($postId, $model, get_current_user_id(), 'v0.1.78 hybrid modulside: Designer-slots + dynamisk modul');
            update_post_meta($postId, self::META, ['module'=>$config['module'],'detailPageId'=>$detailId,'migratedUtc'=>gmdate('c')]);
        }
        self::upgradeV0180();
    }

    private static function upgradeV0180(): void
    {
        foreach ([
            'events' => 'Events',
            'billedgalleri' => 'Billedgalleri',
            'koeretoejer-og-materiel' => 'Køretøjer og materiel',
        ] as $slug => $fallbackTitle) {
            $page = get_page_by_path($slug, OBJECT, 'page');
            if (!$page instanceof \WP_Post) { continue; }
            $postId = (int) $page->ID;
            if (get_post_meta($postId, self::V0180_COLLECTION_META, true)) { continue; }
            $before = LayoutModel::get($postId);
            update_post_meta($postId, self::V0180_COLLECTION_BACKUP, $before);
            $title = trim((string) $page->post_title); if ($title === '') { $title = $fallbackTitle; }
            $next = self::withCollectionHeading($before, $title);
            $version = LayoutModel::saveVersion($postId, $next, get_current_user_id(), 'v0.1.80: sideoverskrift flyttet ind i Visual Designer');
            update_post_meta($postId, self::V0180_COLLECTION_META, ['version'=>$version,'migratedUtc'=>gmdate('c')]);
        }

        $detailId = self::detailPageId('events');
        if ($detailId <= 0 || get_post_meta($detailId, self::V0180_EVENT_DETAIL_META, true)) { return; }
        $before = LayoutModel::get($detailId);
        update_post_meta($detailId, self::V0180_EVENT_DETAIL_BACKUP, $before);
        $next = self::withComposableEventDetail($before);
        $version = LayoutModel::saveVersion($detailId, $next, get_current_user_id(), 'v0.1.80: Eventdetalje opdelt i flytbare dataelementer');
        update_post_meta($detailId, self::V0180_EVENT_DETAIL_META, ['version'=>$version,'migratedUtc'=>gmdate('c')]);
    }

    /** @param array<string,mixed> $model @return array<string,mixed> */
    private static function withCollectionHeading(array $model, string $title): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        foreach ($nodes as $node) {
            if (!is_array($node) || (string) ($node['type'] ?? '') !== 'text') { continue; }
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ((string) ($node['id'] ?? '') === 'module-page-title' || strcasecmp(trim((string) ($props['heading'] ?? '')), $title) === 0) { return $model; }
        }
        $beforeId = '';
        foreach ($nodes as $node) {
            if (!is_array($node) || (string) ($node['parentId'] ?? '') !== '' || (string) ($node['type'] ?? '') !== 'section') { continue; }
            $props = isset($node['props']) && is_array($node['props']) ? $node['props'] : [];
            if ((string) ($props['moduleSlot'] ?? '') === 'before') { $beforeId = (string) ($node['id'] ?? ''); break; }
        }
        if ($beforeId === '') {
            $beforeId = 'hybrid-before-v0180';
            $nodes[] = ['id'=>$beforeId,'type'=>'section','parentId'=>'','order'=>1,'geometry'=>self::geometry(0,0,120,22),'props'=>['background'=>'','padding'=>0,'radius'=>0,'minHeightRows'=>22,'moduleSlot'=>'before']];
        }
        foreach ($nodes as &$node) {
            if (!is_array($node)) { continue; }
            if ((string) ($node['parentId'] ?? '') === $beforeId) {
                foreach (['desktop','laptop','tablet','mobile'] as $device) {
                    if (isset($node['geometry'][$device]) && is_array($node['geometry'][$device])) { $node['geometry'][$device]['y'] = (int) ($node['geometry'][$device]['y'] ?? 0) + 10; }
                }
            }
            if ((string) ($node['id'] ?? '') === $beforeId) {
                $height = max(22, (int) ($node['geometry']['desktop']['h'] ?? 0) + 10);
                foreach (['desktop','laptop','tablet','mobile'] as $device) {
                    if (isset($node['geometry'][$device]) && is_array($node['geometry'][$device])) { $node['geometry'][$device]['h'] = max($height, (int) ($node['geometry'][$device]['h'] ?? 0)); }
                }
                if (!isset($node['props']) || !is_array($node['props'])) { $node['props'] = []; }
                $node['props']['minHeightRows'] = $height;
            }
        }
        unset($node);
        $nodes[] = [
            'id'=>'module-page-title','type'=>'text','parentId'=>$beforeId,'order'=>1,'geometry'=>self::geometry(0,0,120,8),
            'props'=>['heading'=>$title,'headingLevel'=>'h1','text'=>'','align'=>'left','verticalAlign'=>'top','background'=>'#ffffff','backgroundTransparent'=>true,'textColor'=>'#30382a','headingColor'=>'#30382a','padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>16,'fontWeight'=>400,'lineHeight'=>1.5,'letterSpacing'=>0,'headingFontFamily'=>'body','headingFontSize'=>44,'headingFontWeight'=>700,'headingLineHeight'=>1.08,'headingLetterSpacing'=>0],
        ];
        $model['nodes'] = $nodes;
        return $model;
    }

    /** @param array<string,mixed> $model @return array<string,mixed> */
    private static function withComposableEventDetail(array $model): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? array_values($model['nodes']) : [];
        $sectionId = 'detail-section';
        $hasSection = false; $already = false;
        foreach ($nodes as $node) {
            if (!is_array($node)) { continue; }
            if ((string) ($node['id'] ?? '') === $sectionId && (string) ($node['type'] ?? '') === 'section') { $hasSection = true; }
            if ((string) ($node['type'] ?? '') === 'eventvalue' || (string) ($node['id'] ?? '') === 'event-title') { $already = true; }
        }
        if ($already) { return $model; }
        if (!$hasSection) {
            $nodes[] = ['id'=>$sectionId,'type'=>'section','parentId'=>'','order'=>10,'geometry'=>self::geometry(0,0,120,145),'props'=>['background'=>'','padding'=>0,'radius'=>0,'minHeightRows'=>145]];
        }
        $nodes = array_values(array_filter($nodes, static fn($node): bool => !is_array($node) || (string) ($node['id'] ?? '') !== 'detail-module'));

        $eventNodes = [
            ['id'=>'event-title','type'=>'eventvalue','order'=>20,'geometry'=>self::geometry(3,12,114,8),'props'=>['valueKey'=>'title','recordId'=>'','tag'=>'h1','align'=>'left','fontFamily'=>'system','fontSize'=>44,'fontWeight'=>700,'lineHeight'=>1.08,'letterSpacing'=>0,'textColor'=>'#30382a','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-date','type'=>'eventvalue','order'=>30,'geometry'=>self::geometry(3,22,114,5),'props'=>['valueKey'=>'date','recordId'=>'','tag'=>'p','align'=>'left','fontFamily'=>'system','fontSize'=>16,'fontWeight'=>500,'lineHeight'=>1.4,'letterSpacing'=>0,'textColor'=>'#536243','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-location','type'=>'eventvalue','order'=>40,'geometry'=>self::geometry(3,28,114,5),'props'=>['valueKey'=>'location','recordId'=>'','tag'=>'p','align'=>'left','fontFamily'=>'system','fontSize'=>16,'fontWeight'=>400,'lineHeight'=>1.4,'letterSpacing'=>0,'textColor'=>'#30382a','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-summary','type'=>'eventvalue','order'=>50,'geometry'=>self::geometry(3,34,114,6),'props'=>['valueKey'=>'summary','recordId'=>'','tag'=>'p','align'=>'left','fontFamily'=>'system','fontSize'=>17,'fontWeight'=>700,'lineHeight'=>1.4,'letterSpacing'=>0,'textColor'=>'#30382a','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-description','type'=>'eventvalue','order'=>60,'geometry'=>self::geometry(3,42,114,14),'props'=>['valueKey'=>'description','recordId'=>'','tag'=>'div','align'=>'left','fontFamily'=>'system','fontSize'=>16,'fontWeight'=>400,'lineHeight'=>1.5,'letterSpacing'=>0,'textColor'=>'#30382a','background'=>'#ffffff','backgroundTransparent'=>true,'padding'=>0,'radius'=>0]],
            ['id'=>'event-image','type'=>'eventimage','order'=>100,'geometry'=>self::geometry(3,102,114,36),'props'=>['recordId'=>'','fit'=>'cover','imageHeight'=>360,'focalX'=>50,'focalY'=>50,'background'=>'#ffffff','radius'=>4]],
        ];
        foreach ($eventNodes as $row) { $row['parentId'] = $sectionId; $nodes[] = $row; }

        $fieldRows = ['eventfield-about'=>58,'eventfield-program'=>72,'eventfield-practical'=>86];
        $oldRows = ['eventfield-about'=>84,'eventfield-program'=>96,'eventfield-practical'=>108];
        foreach ($nodes as &$node) {
            if (!is_array($node)) { continue; }
            $id = (string) ($node['id'] ?? '');
            if ($id === $sectionId) {
                foreach (['desktop','laptop','tablet','mobile'] as $device) {
                    if (isset($node['geometry'][$device]) && is_array($node['geometry'][$device])) { $node['geometry'][$device]['h'] = max(145, (int) ($node['geometry'][$device]['h'] ?? 0)); }
                }
                if (!isset($node['props']) || !is_array($node['props'])) { $node['props'] = []; }
                $node['props']['minHeightRows'] = max(145, (int) ($node['props']['minHeightRows'] ?? 0));
                continue;
            }
            if (!isset($fieldRows[$id])) { continue; }
            foreach (['desktop','laptop','tablet','mobile'] as $device) {
                if (!isset($node['geometry'][$device]) || !is_array($node['geometry'][$device])) { continue; }
                if ((int) ($node['geometry'][$device]['y'] ?? -1) === $oldRows[$id]) { $node['geometry'][$device]['y'] = $fieldRows[$id]; }
                if ((int) ($node['geometry'][$device]['x'] ?? 3) === 3) { $node['geometry'][$device]['x'] = $device === 'mobile' ? 0 : 3; }
                if ((int) ($node['geometry'][$device]['w'] ?? 114) === 114) { $node['geometry'][$device]['w'] = $device === 'mobile' ? 120 : 114; }
            }
        }
        unset($node);
        $model['nodes'] = $nodes;
        return $model;
    }

    public static function detailPageId(string $module): int
    {
        $module = sanitize_key($module);
        $slug = ['events'=>'event-detalje','galleries'=>'album-detalje','vehicles'=>'koeretoej-detalje'][$module] ?? '';
        if ($slug === '') { return 0; }
        $page = get_page_by_path($slug, OBJECT, 'page');
        return $page instanceof \WP_Post ? (int) $page->ID : 0;
    }

    /** @param array<string,string> $config */
    private static function ensureDetailPage(int $collectionId, array $config): int
    {
        $page = get_page_by_path((string) $config['detailSlug'], OBJECT, 'page');
        if (!$page instanceof \WP_Post) {
            $id = wp_insert_post([
                'post_type'=>'page','post_title'=>(string) $config['detailTitle'],'post_name'=>(string) $config['detailSlug'],
                'post_status'=>current_user_can('publish_pages') ? 'publish' : 'draft','post_content'=>'',
            ], true);
            if (is_wp_error($id)) { return 0; }
            $page = get_post((int) $id);
        }
        if (!$page instanceof \WP_Post) { return 0; }
        $detailId = (int) $page->ID;
        if (!get_post_meta($detailId, self::DETAIL_META, true)) {
            $model = self::detailModel((string) $config['detailType'], $collectionId, (string) $config['module']);
            LayoutModel::saveVersion($detailId, $model, get_current_user_id(), 'v0.1.78 dynamisk detaljeskabelon');
            update_post_meta($detailId, self::DETAIL_META, ['module'=>$config['module'],'collectionPageId'=>$collectionId,'createdUtc'=>gmdate('c')]);
        }
        return $detailId;
    }

    /** @return array<string,mixed> */
    private static function slotModel(): array
    {
        $nodes = []; $order = 10; $y = 0;
        foreach ([['before',12],['between',12],['after',12]] as $item) {
            $slot = (string) $item[0]; $h = (int) $item[1];
            $nodes[] = [
                'id'=>'hybrid-'.$slot,'type'=>'section','parentId'=>'','order'=>$order,
                'geometry'=>self::geometry(0,$y,120,$h),
                'props'=>['background'=>'','padding'=>0,'radius'=>0,'minHeightRows'=>$h,'moduleSlot'=>$slot],
            ];
            $order += 10; $y += $h + 2;
        }
        return ['schemaVersion'=>1,'units'=>120,'rowPx'=>8,'nodes'=>$nodes];
    }

    /** @return array<string,mixed> */
    private static function detailModel(string $detailType, int $collectionId, string $module): array
    {
        $nodes = [[
            'id'=>'detail-section','type'=>'section','parentId'=>'','order'=>10,'geometry'=>self::geometry(0,0,120,120),
            'props'=>['background'=>'','padding'=>0,'radius'=>0,'minHeightRows'=>120],
        ],[
            'id'=>'detail-back','type'=>'button','parentId'=>'detail-section','order'=>10,'geometry'=>self::geometry(3,2,30,7),
            'props'=>['text'=>$module==='events'?'← Tilbage til Events':($module==='galleries'?'← Tilbage til Billedgalleri':'← Tilbage til Køretøjer'),'linkType'=>'page','pageId'=>$collectionId,'autoSize'=>true,'background'=>'#30382a','textColor'=>'#ffffff','paddingX'=>16,'paddingY'=>8,'radius'=>4],
        ],[
            'id'=>'detail-module','type'=>$detailType,'parentId'=>'detail-section','order'=>20,'geometry'=>self::geometry(3,12,114,70),
            'props'=>['recordId'=>'','showImage'=>true,'showDate'=>true,'showLocation'=>true,'showSummary'=>true,'showDescription'=>true,'showGallery'=>true,'showCategory'=>true,'showAttributes'=>true,'columns'=>4,'imageHeight'=>360,'background'=>'#ffffff','textColor'=>'#30382a','accentColor'=>'#536243','padding'=>16,'radius'=>4],
        ]];
        if ($module === 'events') {
            $row = 84; $order = 30;
            foreach (['about','program','practical'] as $key) {
                $nodes[] = ['id'=>'eventfield-'.$key,'type'=>'eventfield','parentId'=>'detail-section','order'=>$order,'geometry'=>self::geometry(3,$row,114,10),'props'=>['fieldKey'=>$key,'recordId'=>'','showHeading'=>true,'background'=>'','textColor'=>'#30382a','padding'=>0,'radius'=>0]];
                $row += 12; $order += 10;
            }
            $nodes[0]['geometry'] = self::geometry(0,0,120,124); $nodes[0]['props']['minHeightRows'] = 124;
        }
        return ['schemaVersion'=>1,'units'=>120,'rowPx'=>8,'nodes'=>$nodes];
    }

    /** @return array<string,mixed> */
    private static function geometry(int $x,int $y,int $w,int $h): array
    {
        return ['desktop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h],'laptop'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],'tablet'=>['x'=>$x,'y'=>$y,'w'=>$w,'h'=>$h,'inheritDesktop'=>true],'mobile'=>['x'=>0,'y'=>$y,'w'=>120,'h'=>$h,'inheritDesktop'=>false]];
    }

    private function __construct() {}
}
