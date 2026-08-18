<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\LegacyOptionPageRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionArtifactRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionMenuRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionRevisionRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionSiteTemplateRepository;
use Hangar18\UltimateDesigner\Portability\ArtifactPackageService;
use Hangar18\UltimateDesigner\Portability\BackupService;
use Hangar18\UltimateDesigner\Portability\ImportExecutor;
use Hangar18\UltimateDesigner\Portability\ImportPlanTokenService;
use Hangar18\UltimateDesigner\Portability\ImportPlanner;
use Hangar18\UltimateDesigner\Portability\PagePackageService;
use Hangar18\UltimateDesigner\Portability\PortableReferenceInspector;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use RuntimeException;

/** I6 Portability UI. Page import stays preview-only until I10; artifact import targets an isolated workspace. */
final class PortabilityAdminController
{
    private const NONCE_ACTION='h18_ud_portability_v1';
    private const PLAN_NONCE='h18_ud_portability_plan_v1';
    private const BACKUP_RESOURCE='portability:artifact-import';
    private const MAX_JSON=1048576;

    public static function register(): void
    {
        add_action('admin_enqueue_scripts',[self::class,'enqueueAssets']);
        add_action('admin_post_h18_ud_export_page_package',[self::class,'exportPage']);
        add_action('admin_post_h18_ud_export_artifact_package',[self::class,'exportArtifacts']);
        add_action('wp_ajax_h18_ud_preview_page_import',[self::class,'previewPageImport']);
        add_action('wp_ajax_h18_ud_plan_artifact_import',[self::class,'planArtifactImport']);
        add_action('admin_post_h18_ud_confirm_artifact_import',[self::class,'confirmArtifactImport']);
        add_action('admin_post_h18_ud_restore_portability_backup',[self::class,'restoreBackup']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page=isset($_GET['page'])?sanitize_key((string)wp_unslash($_GET['page'])):'';
        if($page!==IntegrationAdminBootstrap::PAGE_SLUG&&strpos((string)$hook,IntegrationAdminBootstrap::PAGE_SLUG)===false){return;}
        $pluginFile=dirname(__DIR__,2).'/hangar18-manager.php';$version=class_exists('Hangar18_Manager')?(string)\Hangar18_Manager::VERSION:'0';
        $jsPath=dirname(__DIR__,2).'/assets/ultimate-designer-portability.js';$cssPath=dirname(__DIR__,2).'/assets/ultimate-designer-portability.css';
        wp_enqueue_style('hangar18-ultimate-designer-portability',plugins_url('assets/ultimate-designer-portability.css',$pluginFile),[],$version.'-'.(string)(@filemtime($cssPath)?:0));
        wp_enqueue_script('hangar18-ultimate-designer-portability',plugins_url('assets/ultimate-designer-portability.js',$pluginFile),[],$version.'-'.(string)(@filemtime($jsPath)?:0),true);
        wp_localize_script('hangar18-ultimate-designer-portability','Hangar18Portability',['ajaxUrl'=>admin_url('admin-ajax.php'),'nonce'=>wp_create_nonce(self::PLAN_NONCE),'maxJson'=>self::MAX_JSON]);
    }

    public static function renderPanel(): void
    {
        $pages=self::pages();$sources=self::artifactSources();$workspace=(new WordPressOptionArtifactRepository())->snapshot();$history=(new WordPressOptionRevisionRepository())->history(self::BACKUP_RESOURCE);
        echo '<section class="h18-ud-portability-panel"><div class="h18-ud-builder-panel-head"><div><h2>I6 · Import / Export</h2><p>Dry-run først. Sidepakker er preview-only indtil I10; artifact-import går kun til en isoleret workspace.</p></div><span class="h18-ud-shadow-badge">DRY-RUN FIRST · BACKUP · ROLLBACK</span></div>';
        echo '<div class="h18-ud-portability-grid"><section class="h18-ud-port-card"><h3>Sidepakke</h3><p class="description">Eksportér eksisterende editor-state + globale UD styles. Import kan kun valideres nu — den skriver ikke siden.</p>';
        echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_export_page_package"><label>Side<select name="page_key" required><option value="">Vælg side</option>';foreach($pages as $key=>$page){echo '<option value="'.esc_attr($key).'">'.esc_html((string)($page['PageTitle']??$key)).' · '.esc_html($key).'</option>';}echo '</select></label><button class="button" type="submit">Download side JSON</button></form>';
        echo '<div class="h18-ud-page-import-preview"><label>Valider sidepakke<textarea id="h18-ud-page-package-json" rows="7" placeholder="Indsæt eksporteret page JSON"></textarea></label><button class="button" type="button" id="h18-ud-preview-page-package">Valider / preview</button><div id="h18-ud-page-package-result" aria-live="polite"></div></div></section>';

        echo '<section class="h18-ud-port-card"><h3>Artifact eksport</h3><p class="description">Components, Header/Footer templates, shadow-menuer og workspace artifacts. Eksport ændrer intet.</p><form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_export_artifact_package"><div class="h18-ud-artifact-source-list">';
        foreach($sources as $selection=>$artifact){echo '<label><input type="checkbox" name="artifacts[]" value="'.esc_attr($selection).'"><span><strong>'.esc_html((string)$artifact['Name']).'</strong><small>'.esc_html((string)$artifact['Type']).' · '.esc_html((string)$artifact['Id']).' · '.esc_html((string)$artifact['Source']).'</small></span></label>';}
        if($sources===[]){echo '<p class="description">Ingen artifacts fundet endnu.</p>';}echo '</div><button class="button" type="submit">Download valgte artifacts</button></form></section>';

        echo '<section class="h18-ud-port-card h18-ud-port-import"><h3>Artifact import workspace</h3><p class="description"><strong>1.</strong> Indsæt package · <strong>2.</strong> Kør dry-run · <strong>3.</strong> Gennemgå conflicts/remaps · <strong>4.</strong> Bekræft. Ændringer går aldrig direkte til aktive sider/menu/templates.</p>';
        echo '<form id="h18-ud-artifact-import-form" method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_confirm_artifact_import"><input type="hidden" name="plan_token" id="h18-ud-import-plan-token" value=""><label>Conflict-strategi<select name="strategy" id="h18-ud-import-strategy"><option value="remap">Remap ID ved collision</option><option value="skip">Skip eksisterende</option><option value="reject">Blokér ved collision</option></select></label><label>Artifact package JSON<textarea name="package_json" id="h18-ud-artifact-package-json" rows="11" required></textarea></label><button class="button" type="button" id="h18-ud-run-import-dry-run">Kør dry-run</button><div id="h18-ud-import-plan-result" aria-live="polite"></div><label class="h18-ud-import-confirm"><input type="checkbox" name="confirm_import" value="yes" id="h18-ud-confirm-import" disabled> Jeg har gennemgået dry-run-planen og vil importere til Portability Workspace.</label><button class="button button-primary" type="submit" id="h18-ud-confirm-import-button" disabled>Bekræft workspace-import</button></form></section>';

        echo '<section class="h18-ud-port-card"><h3>Workspace & restore points</h3>';self::renderWorkspace($workspace);echo '<h4>Automatiske pre-import backups</h4>';
        if($history===[]){echo '<p class="description">Ingen import-backups endnu.</p>';}else{echo '<div class="h18-ud-backup-list">';foreach(array_reverse(array_slice($history,-10)) as $revision){$id=(string)($revision['Id']??'');echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'" onsubmit="return confirm(\'Gendan workspace til denne backup?\');">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_restore_portability_backup"><input type="hidden" name="backup_id" value="'.esc_attr($id).'"><input type="hidden" name="confirm_restore" value="yes"><span><strong>'.esc_html($id).'</strong><small>'.esc_html((string)($revision['CreatedUtc']??'')).' · hash '.esc_html(substr((string)($revision['StateHash']??''),0,12)).'…</small></span><button class="button-link" type="submit">Gendan</button></form>';}echo '</div>';}
        echo '</section></div></section>';
    }

    public static function exportPage(): void
    {
        self::guard();$key=isset($_POST['page_key'])?sanitize_key((string)wp_unslash($_POST['page_key'])):'';if($key===''){self::fail('Vælg en side.');}
        $page=(new LegacyOptionPageRepository())->load($key);if(!is_array($page)){self::fail('Siden blev ikke fundet i editor-store.');}
        $json=(new PagePackageService(new PageSchemaValidator()))->export($page,self::globalStyles());self::download($key.'-page-package.json',$json);
    }

    public static function exportArtifacts(): void
    {
        self::guard();$selected=isset($_POST['artifacts'])&&is_array($_POST['artifacts'])?array_values(array_unique(array_map('sanitize_text_field',wp_unslash($_POST['artifacts'])))):[];$sources=self::artifactSources();$artifacts=[];
        foreach($selected as $selection){if(isset($sources[$selection])){$artifact=$sources[$selection];$artifacts[]=['Type'=>$artifact['Type'],'Id'=>$artifact['Id'],'Name'=>$artifact['Name'],'Data'=>$artifact['Data']];}}
        if($artifacts===[]){self::fail('Vælg mindst ét artifact.');}$json=(new ArtifactPackageService())->export($artifacts);self::download('hangar18-artifacts-'.gmdate('Ymd-His').'.json',$json);
    }

    public static function previewPageImport(): void
    {
        self::ajaxGuard();$json=self::postedJson('package_json');
        try{$package=(new PagePackageService(new PageSchemaValidator()))->import($json);$page=$package['Page'];$result=['valid'=>true,'PageSlug'=>(string)($page['PageSlug']??''),'PageTitle'=>(string)($page['PageTitle']??''),'Sections'=>count((array)($page['Sections']??[])),'PageChecksum'=>(string)($package['Checksums']['Page']??''),'WriteAllowed'=>false,'Message'=>'Pakken er gyldig. Side-write er låst indtil I10.'];}
        catch(\Throwable $e){wp_send_json_error(['message'=>mb_substr($e->getMessage(),0,700)],400);return;}wp_send_json_success($result);
    }

    public static function planArtifactImport(): void
    {
        self::ajaxGuard();$json=self::postedJson('package_json');$strategy=self::strategy((string)($_POST['strategy']??'remap'));
        try{$package=(new ArtifactPackageService())->import($json);$repository=new WordPressOptionArtifactRepository();$plan=(new ImportPlanner($repository))->plan($package['Artifacts'],$strategy,true);$refs=(new PortableReferenceInspector())->inspect($package['Artifacts']);$brokenArtifacts=array_values(array_filter($refs['Artifacts'],static fn(string $id):bool=>!array_key_exists($id,$plan['Mappings'])));$assetRefs=$refs['Assets'];$ready=!empty($plan['Valid'])&&$brokenArtifacts===[]&&$assetRefs===[];$token='';$expires=0;if($ready){$issued=self::tokens()->issue($package['Checksum'],$strategy,$plan,900);$token=$issued['token'];$expires=(int)$issued['expires'];}
            wp_send_json_success(['plan'=>$plan,'ReadyForImport'=>$ready,'BrokenArtifactRefs'=>$brokenArtifacts,'UnresolvedAssetRefs'=>$assetRefs,'planToken'=>$token,'expires'=>$expires,'message'=>$assetRefs!==[]?'Asset-referencer skal remappes før import kan bekræftes.':($brokenArtifacts!==[]?'Pakken indeholder ukendte artifact-referencer.':($ready?'Dry-run er gyldig. Gennemgå planen før bekræftelse.':'Dry-run har blokerende conflicts.'))]);
        }catch(\Throwable $e){wp_send_json_error(['message'=>mb_substr($e->getMessage(),0,700)],400);}
    }

    public static function confirmArtifactImport(): void
    {
        self::guard();if((string)($_POST['confirm_import']??'')!=='yes'){self::redirect('error','Import kræver eksplicit bekræftelse efter dry-run.');}
        try{$json=self::postedJson('package_json');$strategy=self::strategy((string)($_POST['strategy']??'remap'));$token=(string)($_POST['plan_token']??'');$package=(new ArtifactPackageService())->import($json);$repository=new WordPressOptionArtifactRepository();$planner=new ImportPlanner($repository);$dryPlan=$planner->plan($package['Artifacts'],$strategy,true);$refs=(new PortableReferenceInspector())->inspect($package['Artifacts']);$brokenArtifacts=array_values(array_filter($refs['Artifacts'],static fn(string $id):bool=>!array_key_exists($id,$dryPlan['Mappings'])));if($refs['Assets']!==[]||$brokenArtifacts!==[]){throw new RuntimeException('Import har uløste portable referencer og kan ikke bekræftes.');}if(!self::tokens()->verify($token,$package['Checksum'],$strategy,$dryPlan)){throw new RuntimeException('Dry-run token er udløbet eller matcher ikke den aktuelle package/plan. Kør dry-run igen.');}$writePlan=$planner->plan($package['Artifacts'],$strategy,false);$executor=new ImportExecutor($repository,new BackupService(new WordPressOptionRevisionRepository()));$result=$executor->execute($writePlan,[],get_current_user_id(),true);self::redirect('imported',count((array)$result['Written']).' artifact(s) importeret til workspace. Backup: '.(string)$result['BackupId']);}
        catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    public static function restoreBackup(): void
    {
        self::guard();if((string)($_POST['confirm_restore']??'')!=='yes'){self::redirect('error','Restore kræver eksplicit bekræftelse.');}$id=sanitize_text_field((string)($_POST['backup_id']??''));
        try{$backup=new BackupService(new WordPressOptionRevisionRepository());$state=$backup->restoreState(self::BACKUP_RESOURCE,$id);$repository=new WordPressOptionArtifactRepository();$repository->restoreSnapshot($state);self::redirect('restored','Portability Workspace gendannet fra backup '.$id.'.');}
        catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    /** @return array<string,array<string,mixed>> */
    private static function pages(): array{$raw=get_option(LegacyOptionPageRepository::DEFAULT_OPTION,[]);if(!is_array($raw)){return [];}$pages=[];foreach($raw as $key=>$state){if(is_array($state)){$pages[(string)$key]=$state;}}ksort($pages,SORT_NATURAL|SORT_FLAG_CASE);return $pages;}
    private static function globalStyles(): array{$raw=get_option('hangar18_ud_global_styles_v1',[]);return is_array($raw)?$raw:[];}

    /** @return array<string,array{Type:string,Id:string,Name:string,Data:array<string,mixed>,Source:string}> */
    private static function artifactSources(): array
    {
        $out=[];$add=static function(array &$out,string $type,string $id,string $name,array $data,string $source):void{$identity=$type.':'.$id;if(isset($out[$identity])){return;}$out[$identity]=['Type'=>$type,'Id'=>$id,'Name'=>$name!==''?$name:$id,'Data'=>$data,'Source'=>$source];};
        foreach((new WordPressOptionSiteTemplateRepository())->all() as $id=>$data){if(is_array($data)){$add($out,'template',(string)$id,(string)($data['Name']??$id),$data,'shadow site template');}}
        foreach((new WordPressOptionMenuRepository())->all() as $id=>$data){if(is_array($data)){$add($out,'menu',(string)$id,(string)($data['Name']??$id),$data,'shadow menu');}}
        $components=get_option('hangar18_manager_page_components_v1',[]);if(is_array($components)){foreach($components as $id=>$data){if(is_array($data)){$add($out,'component',(string)$id,(string)($data['Name']??$data['Title']??$id),$data,'page component');}}}
        $pageTemplates=get_option('hangar18_manager_page_templates_v1',[]);if(is_array($pageTemplates)){foreach($pageTemplates as $id=>$data){if(is_array($data)){$add($out,'template',(string)$id,(string)($data['Name']??$data['Title']??$id),$data,'page template');}}}
        foreach((new WordPressOptionArtifactRepository())->snapshot() as $type=>$items){foreach($items as $id=>$data){$add($out,(string)$type,(string)$id,(string)($data['Name']??$data['Title']??$id),$data,'portability workspace');}}
        ksort($out,SORT_NATURAL|SORT_FLAG_CASE);return $out;
    }

    private static function renderWorkspace(array $workspace): void
    {
        $count=0;foreach($workspace as $items){$count+=count($items);}echo '<p><strong>'.$count.'</strong> artifact(s) i isoleret workspace.</p>';
        if($count===0){echo '<p class="description">Workspace er tom. En import her påvirker ikke aktive sider/menu/templates.</p>';return;}echo '<ul class="h18-ud-workspace-list">';foreach($workspace as $type=>$items){foreach($items as $id=>$data){echo '<li><code>'.esc_html((string)$type).':'.esc_html((string)$id).'</code><span>'.esc_html((string)($data['Name']??$data['Title']??'')).'</span></li>';}}echo '</ul>';
    }

    private static function postedJson(string $field): string{$json=isset($_POST[$field])?(string)wp_unslash($_POST[$field]):'';if($json===''||strlen($json)>self::MAX_JSON){throw new RuntimeException('JSON package mangler eller overskrider 1 MB.');}return $json;}
    private static function strategy(string $strategy): string{$strategy=sanitize_key($strategy);if(!in_array($strategy,['remap','skip','reject'],true)){throw new RuntimeException('Ugyldig conflict-strategi.');}return $strategy;}
    private static function tokens(): ImportPlanTokenService{$secret=wp_salt('auth');if(!is_string($secret)||strlen($secret)<32){throw new RuntimeException('WordPress auth salt er ikke stærk nok til import-plan tokens.');}return new ImportPlanTokenService($secret);}
    private static function guard(): void{if(!current_user_can('edit_pages')){wp_die(esc_html__('Du har ikke rettigheder til denne handling.','hangar18-manager'));}check_admin_referer(self::NONCE_ACTION);}
    private static function ajaxGuard(): void{if(!current_user_can('edit_pages')){wp_send_json_error(['message'=>'Manglende rettighed.'],403);exit;}check_ajax_referer(self::PLAN_NONCE,'nonce');}
    private static function download(string $filename,string $content): void{nocache_headers();header('Content-Type: application/json; charset=utf-8');header('Content-Disposition: attachment; filename="'.sanitize_file_name($filename).'"');header('Content-Length: '.strlen($content));echo $content;exit;}
    private static function fail(string $message): void{self::redirect('error',$message);}
    private static function redirect(string $status,string $message): void{wp_safe_redirect(add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>mb_substr($message,0,700)],admin_url('admin.php')));exit;}
}
