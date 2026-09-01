<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class HybridModulePageMigration
{
    public const META = '_h18_vd_hybrid_module_slots_v0178';
    private const BACKUP_META = '_h18_vd_hybrid_module_backup_v0178';
    private const DETAIL_META = '_h18_vd_module_detail_template_v0178';

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
