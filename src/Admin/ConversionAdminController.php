<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionWorkspaceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionManualQaEvidenceRepository;
use Hangar18\UltimateDesigner\Migration\ConversionPlanService;
use Hangar18\UltimateDesigner\Migration\ConversionTargetCatalog;
use Hangar18\UltimateDesigner\QA\ManualEvidenceValidator;
use RuntimeException;

/** I10 planner/shadow-copy UI. This slice intentionally has no public activation handler. */
final class ConversionAdminController
{
    private const NONCE_ACTION='h18_ud_conversion_planner_v1';

    public static function register(): void
    {
        add_action('admin_enqueue_scripts',[self::class,'enqueueAssets']);
        add_action('admin_post_h18_ud_create_conversion_shadow',[self::class,'createShadow']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page=isset($_GET['page'])?sanitize_key((string)wp_unslash($_GET['page'])):'';
        if($page!==IntegrationAdminBootstrap::PAGE_SLUG&&strpos((string)$hook,IntegrationAdminBootstrap::PAGE_SLUG)===false){return;}
        $pluginFile=dirname(__DIR__,2).'/hangar18-manager.php';$version=class_exists('Hangar18_Manager')?(string)\Hangar18_Manager::VERSION:'0';$cssPath=dirname(__DIR__,2).'/assets/ultimate-designer-conversion.css';
        wp_enqueue_style('hangar18-ultimate-designer-conversion',plugins_url('assets/ultimate-designer-conversion.css',$pluginFile),[],$version.'-'.(string)(@filemtime($cssPath)?:0));
    }

    public static function renderPanel(): void
    {
        $records=(new WordPressOptionManualQaEvidenceRepository())->all();$manual=(new ManualEvidenceValidator())->statusMap($records);$pages=self::wordpressPages();$workspaceRepo=new WordPressOptionConversionWorkspaceRepository();$workspace=$workspaceRepo->all();$accepted=[];foreach($workspace as $slug=>$record){if(!empty($record['Accepted'])){$accepted[]=$slug;}}
        $plan=(new ConversionPlanService())->plan($pages,$manual,$accepted);$legacy=get_option('hangar18_manager_pages_v1',[]);if(!is_array($legacy)){$legacy=[];}$targets=new ConversionTargetCatalog();$manualPassed=count(array_filter($manual));$manualTotal=count($manual);
        echo '<section class="h18-ud-conversion-panel"><div class="h18-ud-builder-panel-head"><div><h2>I10 · Controlled conversion planner</h2><p>Planlægning og shadow-copy er tilgængelig. <strong>Public cutover findes ikke i denne version.</strong> I9-gates og rækkefølgen kan derfor ikke omgås fra UI.</p></div><span class="h18-ud-shadow-badge">PLANNER ONLY · CUTOVER LOCKED</span></div>';
        echo '<div class="h18-ud-conversion-summary"><strong>'.$manualPassed.'/'.$manualTotal.' manual gates PASS</strong><span>PublicMutationAvailable: '.(!empty($plan['PublicMutationAvailable'])?'YES':'NO').'</span><span>Comparison: '.esc_html((string)($plan['ComparisonSlug']?:'ingen')).'</span><span>'.count($workspace).' shadow copy/copies</span></div>';
        if($manualPassed<$manualTotal){echo '<div class="notice notice-warning inline"><p><strong>I10 er blokeret:</strong> '.($manualTotal-$manualPassed).' manuelle I9-gates mangler. Shadow-copy kan bruges til forberedelse, men ingen offentlig aktivering er implementeret.</p></div>';}
        echo '<table class="widefat striped h18-ud-conversion-table"><thead><tr><th>Trin</th><th>Target</th><th>Fremtidig cutover-status</th><th>Shadow-copy</th></tr></thead><tbody>';
        foreach((array)$plan['Stages'] as $stage){if(!is_array($stage)){continue;}$slug=(string)($stage['Slug']??'');$kind=(string)($stage['Kind']??'');$exists=!empty($stage['Exists']);$eligible=!empty($stage['EligibleForFutureCutover']);$blockers=(array)($stage['Blockers']??[]);$protected=$slug!==''&&$targets->isProtected($slug);$hasLegacy=$slug!==''&&isset($legacy[$slug])&&is_array($legacy[$slug]);$shadow=$workspace[$slug]??null;
            echo '<tr><td><strong>'.(int)($stage['Stage']??0).'</strong><br>'.esc_html($kind).'</td><td><strong>'.esc_html((string)($stage['Title']??$slug)).'</strong><br><code>'.esc_html($slug?:'—').'</code>'.(!$exists?'<br><span class="h18-ud-conversion-bad">WP-side mangler</span>':'').($protected?'<br><span class="h18-ud-conversion-protected">PROTECTED LEGACY</span>':'').'</td><td><strong>'.($eligible?'ELIGIBLE IF ACTIVATION LATER EXISTS':'BLOCKED').'</strong>';
            if($blockers){echo '<ul>';foreach($blockers as $blocker){echo '<li><code>'.esc_html((string)$blocker).'</code></li>';}echo '</ul>';}echo '</td><td>';
            if(is_array($shadow)){echo '<p><strong>Shadow eksisterer</strong><br><code>'.esc_html((string)($shadow['SourceHash']??'')).'</code><br>'.esc_html((string)($shadow['CreatedUtc']??'')).'</p>';}
            if(!$protected&&$exists&&$hasLegacy&&current_user_can('manage_options')){echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_create_conversion_shadow"><input type="hidden" name="slug" value="'.esc_attr($slug).'"><button class="button" type="submit">'.(is_array($shadow)?'Genskab shadow-copy':'Opret shadow-copy').'</button></form>';}
            elseif($protected){echo '<p>Shadow-konvertering er låst for beskyttet domæne.</p>';}elseif(!$hasLegacy&&$slug!==''){echo '<p>Ingen legacy editor-state fundet under denne slug.</p>';}else{echo '<p>—</p>';}echo '</td></tr>';}
        echo '</tbody></table>';
        echo '<div class="notice notice-info inline"><p><strong>Rækkefølge:</strong> sammenligningsside → Hjem → Om → Kontakt → Bliv medlem → Vehicle/Event/Gallery. Beskyttede domæner forbliver desuden låst af CompatibilityPolicy, indtil en separat, eksplicit compatibility-accept ændrer den politik.</p></div>';
        echo '<div class="notice notice-error inline"><p><strong>Ingen Activate-knap:</strong> v0.8.3-planneren registrerer kun <code>h18_ud_create_conversion_shadow</code>. Den registrerer ingen cutover/activate/publish-handler og ændrer ikke WordPress-posts, URLs eller <code>hangar18_manager_pages_v1</code>.</p></div></section>';
    }

    public static function createShadow(): void
    {
        self::guard();$slug=sanitize_title((string)wp_unslash($_POST['slug']??''));$targets=new ConversionTargetCatalog();if($slug===''||$targets->isProtected($slug)){self::redirect('error','Shadow-copy må ikke oprettes for et tomt eller beskyttet Vehicle/Event/Gallery-target.');}
        $pages=self::wordpressPages();$exists=false;foreach($pages as $page){if((string)($page['Slug']??'')===$slug){$exists=true;break;}}if(!$exists){self::redirect('error','WordPress-siden findes ikke længere.');}
        $legacy=get_option('hangar18_manager_pages_v1',[]);if(!is_array($legacy)||!is_array($legacy[$slug]??null)){self::redirect('error','Der findes ingen legacy editor-state for den valgte slug.');}
        try{$record=(new WordPressOptionConversionWorkspaceRepository())->createShadow($slug,$legacy[$slug],function_exists('get_current_user_id')?get_current_user_id():0);self::redirect('conversion-shadow-created','Shadow-copy oprettet for '.$slug.' med hash '.substr((string)$record['SourceHash'],0,12).'. Public side er uændret.');}
        catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    /** @return list<array{Slug:string,Title:string,Id:int}> */
    private static function wordpressPages(): array
    {
        if(!function_exists('get_posts')){return [];}$posts=get_posts(['post_type'=>'page','post_status'=>['publish','draft','private','pending'],'numberposts'=>-1,'orderby'=>'title','order'=>'ASC']);$out=[];
        foreach((array)$posts as $post){if(is_object($post)){$slug=(string)($post->post_name??'');$title=(string)($post->post_title??$slug);$id=(int)($post->ID??0);}elseif(is_array($post)){$slug=(string)($post['post_name']??$post['Slug']??'');$title=(string)($post['post_title']??$post['Title']??$slug);$id=(int)($post['ID']??$post['Id']??0);}else{continue;}$slug=sanitize_title($slug);if($slug!==''){$out[]=['Slug'=>$slug,'Title'=>$title,'Id'=>$id];}}
        usort($out,static fn(array $a,array $b): int=>strcmp($a['Slug'],$b['Slug']));return $out;
    }

    private static function guard(): void{if(!current_user_can('manage_options')){wp_die(esc_html__('Kun administratorer kan oprette conversion shadow-copies.','hangar18-manager'));}check_admin_referer(self::NONCE_ACTION);}
    private static function redirect(string $status,string $message): void{wp_safe_redirect(add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>mb_substr($message,0,700)],admin_url('admin.php')));exit;}
}
