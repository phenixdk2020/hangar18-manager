<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Assets\AssetManagerService;
use Hangar18\UltimateDesigner\Assets\AssetUsageScanner;
use Hangar18\UltimateDesigner\Assets\DuplicateAssetDetector;
use Hangar18\UltimateDesigner\Assets\FocalPointResolver;
use Hangar18\UltimateDesigner\Assets\ImageOptimizationService;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressImageOptimizer;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionAssetMetadataRepository;
use RuntimeException;

/**
 * I5 Asset Manager UI over native WordPress attachments.
 * Metadata is an overlay; original attachments/Media IDs are never replaced/deleted.
 */
final class AssetManagerAdminController
{
    private const NONCE_ACTION='h18_ud_asset_manager_v1';
    private const MAX_LIBRARY=250;
    private const MAX_USAGE_DATA_POSTS=250;

    public static function register(): void
    {
        add_action('admin_post_h18_ud_save_asset_metadata',[self::class,'saveMetadata']);
        add_action('admin_post_h18_ud_generate_asset_derivatives',[self::class,'generateDerivatives']);
        add_action('wp_ajax_h18_ud_asset_duplicates',[self::class,'scanDuplicates']);
        add_action('admin_enqueue_scripts',[self::class,'enqueueAssets']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page=isset($_GET['page'])?sanitize_key((string)wp_unslash($_GET['page'])):'';
        if($page!==IntegrationAdminBootstrap::PAGE_SLUG && strpos((string)$hook,IntegrationAdminBootstrap::PAGE_SLUG)===false){return;}
        $pluginFile=dirname(__DIR__,2).'/hangar18-manager.php';
        $version=class_exists('Hangar18_Manager')?(string)\Hangar18_Manager::VERSION:'0';
        $jsPath=dirname(__DIR__,2).'/assets/ultimate-designer-asset-admin.js';
        $cssPath=dirname(__DIR__,2).'/assets/ultimate-designer-asset-admin.css';
        wp_enqueue_style('hangar18-ultimate-designer-asset-admin',plugins_url('assets/ultimate-designer-asset-admin.css',$pluginFile),[],$version.'-'.(string)(@filemtime($cssPath)?:0));
        wp_enqueue_script('hangar18-ultimate-designer-asset-admin',plugins_url('assets/ultimate-designer-asset-admin.js',$pluginFile),[],$version.'-'.(string)(@filemtime($jsPath)?:0),true);
        wp_localize_script('hangar18-ultimate-designer-asset-admin','Hangar18AssetManager',[
            'ajaxUrl'=>admin_url('admin-ajax.php'),
            'duplicateNonce'=>wp_create_nonce('h18_ud_asset_duplicates_v1'),
        ]);
    }

    public static function renderPanel(): void
    {
        $service=self::service();
        $taxonomy=$service->taxonomy();
        $query=isset($_GET['ud_asset_q'])?sanitize_text_field((string)wp_unslash($_GET['ud_asset_q'])):'';
        $folder=isset($_GET['ud_asset_folder'])?sanitize_text_field((string)wp_unslash($_GET['ud_asset_folder'])):'';
        $collection=isset($_GET['ud_asset_collection'])?sanitize_text_field((string)wp_unslash($_GET['ud_asset_collection'])):'';
        $tag=isset($_GET['ud_asset_tag'])?sanitize_text_field((string)wp_unslash($_GET['ud_asset_tag'])):'';
        $selectedId=isset($_GET['ud_media'])?max(0,(int)$_GET['ud_media']):0;
        $attachments=self::attachments($query,$folder,$collection,$tag);
        if($selectedId<=0 && $attachments!==[]){$selectedId=(int)$attachments[0]->ID;}
        $selected=$selectedId>0?get_post($selectedId):null;
        if(!($selected instanceof \WP_Post) || $selected->post_type!=='attachment'){$selected=null;$selectedId=0;}

        echo '<section class="h18-ud-assets-panel">';
        echo '<div class="h18-ud-builder-panel-head"><div><h2>I5 · Asset Manager</h2><p>Metadata og analyse oven på native WordPress Media IDs. Originalfiler slettes eller erstattes aldrig her.</p></div><span class="h18-ud-shadow-badge">NATIVE MEDIA IDs · ORIGINAL BEVARES</span></div>';
        self::renderFilters($query,$folder,$collection,$tag,$taxonomy);
        echo '<div class="h18-ud-assets-workspace"><div class="h18-ud-assets-library">';
        self::renderLibrary($attachments,$selectedId);
        echo '</div><aside class="h18-ud-asset-inspector">';
        if($selected){self::renderInspector($selected,$service);}else{echo '<div class="h18-ud-empty-editor"><strong>Ingen billed-attachments fundet.</strong></div>';}
        echo '</aside></div>';
        echo '<div class="h18-ud-duplicate-section"><div><h3>Dubletkontrol</h3><p class="description">SHA-256 scan er read-only. Ingen filer bliver slettet eller flettet automatisk.</p></div><button type="button" class="button" id="h18-ud-scan-duplicates">Scan dubletter</button><div id="h18-ud-duplicate-results" aria-live="polite"></div></div>';
        echo '</section>';
    }

    public static function saveMetadata(): void
    {
        self::guard();
        $mediaId=max(0,(int)($_POST['media_id']??0));
        try{
            self::assertAttachment($mediaId);
            $raw=isset($_POST['asset'])&&is_array($_POST['asset'])?wp_unslash($_POST['asset']):[];
            $metadata=[
                'Folder'=>(string)($raw['Folder']??''),
                'Collections'=>(string)($raw['Collections']??''),
                'Tags'=>(string)($raw['Tags']??''),
                'Copyright'=>sanitize_text_field((string)($raw['Copyright']??'')),
                'SourceUrl'=>(string)($raw['SourceUrl']??''),
                'FocalPoint'=>[
                    'desktop'=>['X'=>(float)($raw['FocalDesktopX']??50),'Y'=>(float)($raw['FocalDesktopY']??50)],
                    'tablet'=>['X'=>(float)($raw['FocalTabletX']??50),'Y'=>(float)($raw['FocalTabletY']??50)],
                    'mobile'=>['X'=>(float)($raw['FocalMobileX']??50),'Y'=>(float)($raw['FocalMobileY']??50)],
                ],
            ];
            self::service()->save($mediaId,$metadata);
            self::redirect($mediaId,'saved','Asset metadata og focal points er gemt. Media ID/original er uændret.');
        }catch(\Throwable $e){self::redirect($mediaId,'error',$e->getMessage());}
    }

    public static function generateDerivatives(): void
    {
        self::guard();
        $mediaId=max(0,(int)($_POST['media_id']??0));
        try{
            self::assertAttachment($mediaId);
            $source=(string)get_attached_file($mediaId);
            $mime=(string)get_post_mime_type($mediaId);
            if($source===''||!is_file($source)){throw new RuntimeException('Original billedfil kunne ikke findes.');}
            $quality=max(1,min(100,(int)($_POST['quality']??82)));
            $maxWidth=max(0,min(8000,(int)($_POST['max_width']??0)));
            $maxHeight=max(0,min(8000,(int)($_POST['max_height']??0)));
            $result=(new ImageOptimizationService(new WordPressImageOptimizer()))->optimize($source,$mime,['Quality'=>$quality,'MaxWidth'=>$maxWidth,'MaxHeight'=>$maxHeight]);
            if(empty($result['preserved'])||!is_file($source)){throw new RuntimeException('Sikkerhedscheck fejlede: originalen er ikke bevaret.');}
            $success=0;$messages=[];
            foreach((array)($result['derivatives']??[]) as $derivative){if(!empty($derivative['Success'])){$success++;}$messages[]=strtoupper((string)($derivative['Format']??'' )).': '.((!empty($derivative['Success']))?'OK':(string)($derivative['Message']??'sprunget over'));}
            foreach((array)($result['skipped']??[]) as $skipped){$messages[]='Sprunget over: '.(string)$skipped;}
            self::redirect($mediaId,'optimized',$success.' derivat(er) genereret. Originalen er bevaret. '.implode(' · ',$messages));
        }catch(\Throwable $e){self::redirect($mediaId,'error',$e->getMessage());}
    }

    public static function scanDuplicates(): void
    {
        if(!current_user_can('edit_pages')){wp_send_json_error(['message'=>'Manglende rettighed.'],403);return;}
        check_ajax_referer('h18_ud_asset_duplicates_v1','nonce');
        try{
            $files=[];
            foreach(self::attachmentIds(self::MAX_LIBRARY) as $mediaId){$path=(string)get_attached_file($mediaId);if($path!==''&&is_file($path)&&is_readable($path)){$files[$mediaId]=$path;}}
            $groups=(new DuplicateAssetDetector())->detect($files);
            $response=[];
            foreach($groups as $group){$response[]=['Hash'=>(string)$group['Hash'],'MediaIds'=>array_values(array_map('intval',(array)$group['MediaIds'])),'Count'=>count((array)$group['MediaIds'])];}
        }catch(\Throwable $e){wp_send_json_error(['message'=>mb_substr($e->getMessage(),0,500)],400);return;}
        wp_send_json_success(['groups'=>$response,'scanned'=>count($files)]);
    }

    /** @return list<\WP_Post> */
    private static function attachments(string $query,string $folder,string $collection,string $tag): array
    {
        $args=['post_type'=>'attachment','post_status'=>'inherit','post_mime_type'=>'image','posts_per_page'=>self::MAX_LIBRARY,'orderby'=>'date','order'=>'DESC'];
        if($query!==''){$args['s']=$query;}
        $posts=get_posts($args);if(!is_array($posts)){$posts=[];}
        if($folder===''&&$collection===''&&$tag===''){return array_values(array_filter($posts,static fn($p):bool=>$p instanceof \WP_Post));}
        $allowed=array_flip(self::service()->filter($folder,$collection,$tag));
        return array_values(array_filter($posts,static fn($p):bool=>$p instanceof \WP_Post&&isset($allowed[(int)$p->ID])));
    }

    /** @return list<int> */
    private static function attachmentIds(int $limit): array
    {
        $ids=get_posts(['post_type'=>'attachment','post_status'=>'inherit','post_mime_type'=>'image','posts_per_page'=>$limit,'fields'=>'ids','orderby'=>'ID','order'=>'ASC']);
        return array_values(array_filter(array_map('intval',is_array($ids)?$ids:[]),static fn(int $id):bool=>$id>0));
    }

    private static function renderFilters(string $query,string $folder,string $collection,string $tag,array $taxonomy): void
    {
        echo '<form class="h18-ud-asset-filters" method="get"><input type="hidden" name="page" value="'.esc_attr(IntegrationAdminBootstrap::PAGE_SLUG).'">';
        echo '<label>Søg<input type="search" name="ud_asset_q" value="'.esc_attr($query).'" placeholder="Filnavn/titel"></label>';
        self::filterSelect('ud_asset_folder','Mappe',$folder,(array)($taxonomy['folders']??[]));self::filterSelect('ud_asset_collection','Collection',$collection,(array)($taxonomy['collections']??[]));self::filterSelect('ud_asset_tag','Tag',$tag,(array)($taxonomy['tags']??[]));
        echo '<button class="button" type="submit">Filtrér</button><a class="button-link" href="'.esc_url(add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG],admin_url('admin.php'))).'">Nulstil</a></form>';
    }
    private static function filterSelect(string $name,string $label,string $value,array $options): void{echo '<label>'.esc_html($label).'<select name="'.esc_attr($name).'"><option value="">Alle</option>';foreach($options as $option){echo '<option value="'.esc_attr((string)$option).'"'.selected($value,(string)$option,false).'>'.esc_html((string)$option).'</option>';}echo '</select></label>';}

    /** @param list<\WP_Post> $attachments */
    private static function renderLibrary(array $attachments,int $selectedId): void
    {
        echo '<div class="h18-ud-assets-library-head"><h3>Mediebibliotek</h3><span>'.count($attachments).' billeder</span></div><div class="h18-ud-asset-grid">';
        foreach($attachments as $post){$id=(int)$post->ID;$thumb=wp_get_attachment_image_url($id,'thumbnail');$url=add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_media'=>$id],admin_url('admin.php'));echo '<a class="h18-ud-asset-card'.($selectedId===$id?' is-active':'').'" href="'.esc_url($url).'">';if($thumb){echo '<img src="'.esc_url($thumb).'" alt="">';}else{echo '<span class="dashicons dashicons-format-image"></span>';}echo '<span><strong>'.esc_html(get_the_title($id)?:basename((string)get_attached_file($id))).'</strong><small>Media ID '.$id.'</small></span></a>';}
        if($attachments===[]){echo '<p class="description">Ingen billeder matcher filteret.</p>';}echo '</div>';
    }

    private static function renderInspector(\WP_Post $post,AssetManagerService $service): void
    {
        $id=(int)$post->ID;$metadata=$service->get($id);$resolved=(new FocalPointResolver())->resolve(is_array($metadata['FocalPoint']??null)?$metadata['FocalPoint']:[]);$full=wp_get_attachment_image_url($id,'large')?:wp_get_attachment_url($id);$file=(string)get_attached_file($id);$mime=(string)get_post_mime_type($id);$usage=self::usageFor($id);$derivatives=self::derivativeState($file);
        echo '<div class="h18-ud-asset-inspector-head"><div><h3>'.esc_html(get_the_title($id)?:'Asset').'</h3><code>Media ID '.$id.'</code></div><a class="button-link" href="'.esc_url(get_edit_post_link($id,'')).'">Åbn i Medier</a></div>';
        if($full){echo '<div class="h18-ud-focal-preview"><img id="h18-ud-focal-image" src="'.esc_url($full).'" alt=""><span class="h18-ud-focal-marker" aria-hidden="true"></span></div>';}
        echo '<dl class="h18-ud-asset-native"><dt>MIME</dt><dd>'.esc_html($mime).'</dd><dt>Original</dt><dd><code>'.esc_html(basename($file)).'</code></dd><dt>Størrelse</dt><dd>'.esc_html(self::bytes($file)).'</dd></dl>';
        echo '<form class="h18-ud-asset-metadata-form" method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_save_asset_metadata"><input type="hidden" name="media_id" value="'.$id.'">';
        self::textField('Folder','Mappe',(string)($metadata['Folder']??''),'Fx Historie/Køretøjer');self::textField('Collections','Collections',implode(', ',(array)($metadata['Collections']??[])),'Komma-separeret');self::textField('Tags','Tags',implode(', ',(array)($metadata['Tags']??[])),'Komma-separeret');self::textField('Copyright','Copyright',(string)($metadata['Copyright']??''),'');self::textField('SourceUrl','Kilde-URL',(string)($metadata['SourceUrl']??''),'Kun HTTPS');
        echo '<fieldset class="h18-ud-focal-fields"><legend>Focal point (%)</legend>';foreach(['desktop'=>'Desktop','tablet'=>'Tablet','mobile'=>'Mobil'] as $device=>$label){echo '<div data-focal-device="'.esc_attr($device).'"><strong>'.esc_html($label).'</strong><label>X <input type="range" min="0" max="100" step="1" name="asset[Focal'.ucfirst($device).'X]" value="'.esc_attr((string)$resolved[$device]['X']).'"><output>'.esc_html((string)$resolved[$device]['X']).'</output></label><label>Y <input type="range" min="0" max="100" step="1" name="asset[Focal'.ucfirst($device).'Y]" value="'.esc_attr((string)$resolved[$device]['Y']).'"><output>'.esc_html((string)$resolved[$device]['Y']).'</output></label></div>';}echo '</fieldset><button class="button button-primary" type="submit">Gem asset metadata</button></form>';
        echo '<section class="h18-ud-asset-usage"><h4>Usage</h4>';if($usage===[]){echo '<p class="description">Ingen MediaId-referencer fundet i kendte Hangar18 resources.</p>';}else{echo '<ul>';foreach($usage as $ref){echo '<li><code>'.esc_html((string)$ref['Resource']).'</code><small>'.esc_html((string)$ref['Path']).'</small></li>';}echo '</ul>';}echo '</section>';
        echo '<section class="h18-ud-asset-derivatives"><h4>Optimeringsderivater</h4><div class="h18-ud-derivative-state"><span>WebP: <strong>'.($derivatives['webp']?'findes':'mangler').'</strong></span><span>AVIF: <strong>'.($derivatives['avif']?'findes':'mangler').'</strong></span></div><form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_generate_asset_derivatives"><input type="hidden" name="media_id" value="'.$id.'"><label>Kvalitet <input type="number" min="1" max="100" name="quality" value="82"></label><label>Max bredde <input type="number" min="0" max="8000" name="max_width" value="0"><small>0 = behold</small></label><label>Max højde <input type="number" min="0" max="8000" name="max_height" value="0"><small>0 = behold</small></label><button class="button" type="submit">Generér WebP/AVIF derivater</button><p class="description"><strong>Originalen bevares altid.</strong> Der oprettes kun nye derivatfiler ved siden af originalen.</p></form></section>';
    }

    private static function textField(string $key,string $label,string $value,string $help): void{echo '<label>'.esc_html($label).'<input type="text" name="asset['.esc_attr($key).']" value="'.esc_attr($value).'">';if($help!==''){echo '<small>'.esc_html($help).'</small>';}echo '</label>';}

    /** @return list<array{Resource:string,Path:string}> */
    private static function usageFor(int $mediaId): array
    {
        $resources=[];
        $optionMap=['page'=>'hangar18_manager_pages_v1','component'=>'hangar18_manager_page_components_v1','page-template'=>'hangar18_manager_page_templates_v1','site-template'=>'hangar18_manager_site_templates_v1'];
        foreach($optionMap as $prefix=>$option){$states=get_option($option,[]);if(!is_array($states))continue;foreach($states as $key=>$state){if(is_array($state)){$resources[$prefix.':'.(string)$key]=$state;}}}
        $dataIds=get_posts(['post_type'=>'h18_data_entry','post_status'=>['publish','draft','private'],'posts_per_page'=>self::MAX_USAGE_DATA_POSTS,'fields'=>'ids']);
        foreach(is_array($dataIds)?$dataIds:[] as $dataId){$meta=get_post_meta((int)$dataId);if(is_array($meta)){$resources['data:'.(int)$dataId]=$meta;}}
        $usage=(new AssetUsageScanner())->scan($resources);
        return array_values($usage[$mediaId]??[]);
    }

    /** @return array{webp:bool,avif:bool} */
    private static function derivativeState(string $source): array
    {
        if($source===''){return ['webp'=>false,'avif'=>false];}$dir=dirname($source);$name=pathinfo($source,PATHINFO_FILENAME);return ['webp'=>is_file($dir.DIRECTORY_SEPARATOR.$name.'.h18.webp'),'avif'=>is_file($dir.DIRECTORY_SEPARATOR.$name.'.h18.avif')];
    }

    private static function bytes(string $file): string
    {
        if($file===''||!is_file($file)){return 'ukendt';}$bytes=max(0,(int)filesize($file));if($bytes>=1048576)return number_format($bytes/1048576,1,',','.').' MB';if($bytes>=1024)return number_format($bytes/1024,0,',','.').' KB';return $bytes.' B';
    }

    private static function service(): AssetManagerService{return new AssetManagerService(new WordPressOptionAssetMetadataRepository());}
    private static function assertAttachment(int $mediaId): void{$post=$mediaId>0?get_post($mediaId):null;if(!($post instanceof \WP_Post)||$post->post_type!=='attachment'){throw new RuntimeException('Ugyldigt WordPress Media ID.');}}
    private static function guard(): void{if(!current_user_can('edit_pages')){wp_die(esc_html__('Du har ikke rettigheder til denne handling.','hangar18-manager'));}check_admin_referer(self::NONCE_ACTION);}
    private static function redirect(int $mediaId,string $status,string $message): void{$args=['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>mb_substr($message,0,700)];if($mediaId>0)$args['ud_media']=$mediaId;wp_safe_redirect(add_query_arg($args,admin_url('admin.php')));exit;}
}
