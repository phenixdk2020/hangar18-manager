<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionAcceptanceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionWorkspaceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionManualQaEvidenceRepository;
use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceChecklist;
use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceValidator;
use Hangar18\UltimateDesigner\Migration\ConversionPlanService;
use Hangar18\UltimateDesigner\Migration\ConversionTargetCatalog;
use Hangar18\UltimateDesigner\QA\ManualEvidenceValidator;

/** I10 planner/shadow-copy + manual acceptance UI. This slice intentionally has no public activation handler. */
final class ConversionAdminController
{
    private const NONCE_ACTION='h18_ud_conversion_planner_v1';

    public static function register(): void
    {
        add_action('admin_enqueue_scripts',[self::class,'enqueueAssets']);
        add_action('admin_post_h18_ud_create_conversion_shadow',[self::class,'createShadow']);
        add_action('admin_post_h18_ud_save_conversion_acceptance',[self::class,'saveAcceptance']);
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
        $records=(new WordPressOptionManualQaEvidenceRepository())->all();$manual=(new ManualEvidenceValidator())->statusMap($records);$pages=self::wordpressPages();
        $workspaceRepo=new WordPressOptionConversionWorkspaceRepository();$workspace=$workspaceRepo->all();$acceptanceRepo=new WordPressOptionConversionAcceptanceRepository();$acceptance=$acceptanceRepo->all();$acceptanceValidator=new ConversionAcceptanceValidator();$checklist=new ConversionAcceptanceChecklist();
        $accepted=[];foreach($workspace as $slug=>$record){$hash=(string)($record['SourceHash']??'');if($acceptanceValidator->isAccepted($acceptance[$slug]??null,$hash)){$accepted[]=$slug;}}
        $plan=(new ConversionPlanService())->plan($pages,$manual,$accepted);$legacy=get_option('hangar18_manager_pages_v1',[]);if(!is_array($legacy)){$legacy=[];}$targets=new ConversionTargetCatalog();$manualPassed=count(array_filter($manual));$manualTotal=count($manual);
        echo '<section class="h18-ud-conversion-panel"><div class="h18-ud-builder-panel-head"><div><h2>I10 · Controlled conversion planner</h2><p>Planlægning, shadow-copy og manuel shadow-acceptance er tilgængelig. <strong>Public cutover findes ikke i denne version.</strong> I9-gates og rækkefølgen kan derfor ikke omgås fra UI.</p></div><span class="h18-ud-shadow-badge">SHADOW ACCEPTANCE · CUTOVER LOCKED</span></div>';
        echo '<div class="h18-ud-conversion-summary"><strong>'.$manualPassed.'/'.$manualTotal.' manual gates PASS</strong><span>PublicMutationAvailable: '.(!empty($plan['PublicMutationAvailable'])?'YES':'NO').'</span><span>Comparison: '.esc_html((string)($plan['ComparisonSlug']?:'ingen')).'</span><span>'.count($workspace).' shadow copy/copies</span><span>'.count($accepted).' accepted shadow(s)</span></div>';
        if($manualPassed<$manualTotal){echo '<div class="notice notice-warning inline"><p><strong>I10 er globalt blokeret:</strong> '.($manualTotal-$manualPassed).' manuelle I9-gates mangler. Side-specifik acceptance må gerne dokumenteres i shadow mode, men kan ikke lukke de globale I9-gates eller aktivere en offentlig side.</p></div>';}
        echo '<table class="widefat striped h18-ud-conversion-table"><thead><tr><th>Trin</th><th>Target</th><th>Fremtidig cutover-status</th><th>Shadow-copy</th><th>Shadow acceptance</th></tr></thead><tbody>';
        foreach((array)$plan['Stages'] as $stage){if(!is_array($stage)){continue;}$slug=(string)($stage['Slug']??'');$kind=(string)($stage['Kind']??'');$exists=!empty($stage['Exists']);$eligible=!empty($stage['EligibleForFutureCutover']);$blockers=(array)($stage['Blockers']??[]);$protected=$slug!==''&&$targets->isProtected($slug);$hasLegacy=$slug!==''&&isset($legacy[$slug])&&is_array($legacy[$slug]);$shadow=$workspace[$slug]??null;$acceptanceRecord=$acceptance[$slug]??null;$sourceHash=is_array($shadow)?(string)($shadow['SourceHash']??''):'';$acceptedNow=$sourceHash!==''&&$acceptanceValidator->isAccepted(is_array($acceptanceRecord)?$acceptanceRecord:null,$sourceHash);$acceptanceBlockers=$sourceHash!==''?$acceptanceValidator->blockers(is_array($acceptanceRecord)?$acceptanceRecord:null,$sourceHash):['shadow-copy-missing'];
            echo '<tr><td><strong>'.(int)($stage['Stage']??0).'</strong><br>'.esc_html($kind).'</td><td><strong>'.esc_html((string)($stage['Title']??$slug)).'</strong><br><code>'.esc_html($slug?:'—').'</code>'.(!$exists?'<br><span class="h18-ud-conversion-bad">WP-side mangler</span>':'').($protected?'<br><span class="h18-ud-conversion-protected">PROTECTED LEGACY</span>':'').'</td><td><strong>'.($eligible?'ELIGIBLE IF ACTIVATION LATER EXISTS':'BLOCKED').'</strong>';
            if($blockers){echo '<ul>';foreach($blockers as $blocker){echo '<li><code>'.esc_html((string)$blocker).'</code></li>';}echo '</ul>';}echo '</td><td>';
            if(is_array($shadow)){echo '<p><strong>Shadow eksisterer</strong><br><code>'.esc_html($sourceHash).'</code><br>'.esc_html((string)($shadow['CreatedUtc']??'')).'</p>';}
            if(!$protected&&$exists&&$hasLegacy&&current_user_can('manage_options')){echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_create_conversion_shadow"><input type="hidden" name="slug" value="'.esc_attr($slug).'"><button class="button" type="submit">'.(is_array($shadow)?'Genskab shadow-copy':'Opret shadow-copy').'</button></form>';}
            elseif($protected){echo '<p>Shadow-konvertering er låst for beskyttet domæne.</p>';}elseif(!$hasLegacy&&$slug!==''){echo '<p>Ingen legacy editor-state fundet under denne slug.</p>';}else{echo '<p>—</p>';}echo '</td><td>';
            if($protected){echo '<p>Acceptance er låst sammen med den beskyttede legacy-runtime.</p>';}elseif(!is_array($shadow)){echo '<p>Opret først en shadow-copy.</p>';}else{
                echo '<p><strong>'.($acceptedNow?'ACCEPTED FOR SEQUENCE':'NOT ACCEPTED').'</strong></p>';
                if(is_array($acceptanceRecord)){echo '<p><small>Evidence: '.esc_html((string)($acceptanceRecord['EvidenceRef']??'—')).'<br>Captured: '.esc_html((string)($acceptanceRecord['CapturedUtc']??'—')).'</small></p>';}
                if(!$acceptedNow&&$acceptanceBlockers){echo '<ul class="h18-ud-conversion-acceptance-blockers">';foreach($acceptanceBlockers as $blocker){echo '<li><code>'.esc_html((string)$blocker).'</code></li>';}echo '</ul>';}
                if(current_user_can('manage_options')){self::renderAcceptanceForm($slug,$sourceHash,is_array($acceptanceRecord)?$acceptanceRecord:[],$checklist);}
            }echo '</td></tr>';}
        echo '</tbody></table>';
        echo '<div class="notice notice-info inline"><p><strong>Acceptance-regel:</strong> desktop, tablet, mobile, save, preview, revision og rollback skal alle være manuelt verificeret med miljø og evidensreference. Acceptance bindes til shadow-copyens SourceHash; genskabes shadow-copyen, bliver gammel acceptance automatisk stale.</p></div>';
        echo '<div class="notice notice-info inline"><p><strong>Rækkefølge:</strong> sammenligningsside → Hjem → Om → Kontakt → Bliv medlem → Vehicle/Event/Gallery. Beskyttede domæner forbliver desuden låst af CompatibilityPolicy, indtil en separat, eksplicit compatibility-accept ændrer den politik.</p></div>';
        echo '<div class="notice notice-error inline"><p><strong>Ingen Activate-knap:</strong> planneren registrerer kun shadow-copy og shadow-acceptance handlers. Den registrerer ingen cutover/activate/publish-handler og ændrer ikke WordPress-posts, URLs eller <code>hangar18_manager_pages_v1</code>.</p></div></section>';
    }

    /** @param array<string,mixed> $record */
    private static function renderAcceptanceForm(string $slug,string $sourceHash,array $record,ConversionAcceptanceChecklist $checklist): void
    {
        $checks=is_array($record['Checks']??null)?$record['Checks']:[];
        echo '<form class="h18-ud-conversion-acceptance-form" method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);
        echo '<input type="hidden" name="action" value="h18_ud_save_conversion_acceptance"><input type="hidden" name="slug" value="'.esc_attr($slug).'"><input type="hidden" name="source_hash" value="'.esc_attr($sourceHash).'">';
        foreach($checklist->required() as $key=>$label){echo '<label><input type="checkbox" name="checks['.esc_attr($key).']" value="1" '.checked(!empty($checks[$key]),true,false).'> '.esc_html($label).'</label>';}
        echo '<label>Miljø/browser/device<input type="text" name="environment" value="'.esc_attr((string)($record['Environment']??'')).'" maxlength="240"></label>';
        echo '<label>Evidensreference<input type="text" name="evidence_ref" value="'.esc_attr((string)($record['EvidenceRef']??'')).'" maxlength="700" placeholder="URL, ticket, fil/reference eller test-ID"></label>';
        echo '<label>Noter<textarea name="notes" rows="3" maxlength="4000">'.esc_textarea((string)($record['Notes']??'')).'</textarea></label>';
        echo '<label><input type="checkbox" name="confirmed_manual" value="1" '.checked(!empty($record['ConfirmedManual']),true,false).'> Jeg bekræfter, at kontrollerne er udført manuelt på denne shadow-copy.</label>';
        echo '<button class="button button-secondary" type="submit">Gem acceptance evidence</button></form>';
    }

    public static function createShadow(): void
    {
        self::guard();$slug=sanitize_title((string)wp_unslash($_POST['slug']??''));$targets=new ConversionTargetCatalog();if($slug===''||$targets->isProtected($slug)){self::redirect('error','Shadow-copy må ikke oprettes for et tomt eller beskyttet Vehicle/Event/Gallery-target.');}
        $pages=self::wordpressPages();$exists=false;foreach($pages as $page){if((string)($page['Slug']??'')===$slug){$exists=true;break;}}if(!$exists){self::redirect('error','WordPress-siden findes ikke længere.');}
        $legacy=get_option('hangar18_manager_pages_v1',[]);if(!is_array($legacy)||!is_array($legacy[$slug]??null)){self::redirect('error','Der findes ingen legacy editor-state for den valgte slug.');}
        try{$record=(new WordPressOptionConversionWorkspaceRepository())->createShadow($slug,$legacy[$slug],function_exists('get_current_user_id')?get_current_user_id():0);self::redirect('conversion-shadow-created','Shadow-copy oprettet for '.$slug.' med hash '.substr((string)$record['SourceHash'],0,12).'. Public side er uændret; tidligere acceptance er nu stale hvis hash er ændret.');}
        catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    public static function saveAcceptance(): void
    {
        self::guard();$slug=sanitize_title((string)wp_unslash($_POST['slug']??''));$targets=new ConversionTargetCatalog();if($slug===''||$targets->isProtected($slug)){self::redirect('error','Acceptance må ikke gemmes for et tomt eller beskyttet Vehicle/Event/Gallery-target.');}
        $workspace=(new WordPressOptionConversionWorkspaceRepository())->all();$shadow=$workspace[$slug]??null;if(!is_array($shadow)){self::redirect('error','Der findes ingen shadow-copy for target.');}
        $currentHash=strtolower((string)($shadow['SourceHash']??''));$postedHash=strtolower(trim((string)wp_unslash($_POST['source_hash']??'')));if($postedHash===''||!hash_equals($currentHash,$postedHash)){self::redirect('error','Shadow-copy er ændret siden formularen blev vist. Genindlæs siden og verificer den aktuelle kopi.');}
        $rawChecks=[];$postedChecks=isset($_POST['checks'])&&is_array($_POST['checks'])?wp_unslash($_POST['checks']):[];foreach(array_keys((new ConversionAcceptanceChecklist())->required()) as $key){$rawChecks[$key]=!empty($postedChecks[$key]);}
        $raw=['Checks'=>$rawChecks,'Environment'=>sanitize_text_field((string)wp_unslash($_POST['environment']??'')),'EvidenceRef'=>sanitize_text_field((string)wp_unslash($_POST['evidence_ref']??'')),'Notes'=>sanitize_textarea_field((string)wp_unslash($_POST['notes']??'')),'ConfirmedManual'=>!empty($_POST['confirmed_manual'])];
        try{$validator=new ConversionAcceptanceValidator();$record=$validator->normalize($slug,$currentHash,$raw,function_exists('get_current_user_id')?get_current_user_id():0);(new WordPressOptionConversionAcceptanceRepository())->save($slug,$record);$accepted=$validator->isAccepted($record,$currentHash);self::redirect('conversion-acceptance-saved',$accepted?'Shadow acceptance er dokumenteret for '.$slug.'. Dette aktiverer ikke public cutover.':'Acceptance evidence er gemt for '.$slug.', men alle krav er endnu ikke opfyldt.');}
        catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    /** @return list<array{Slug:string,Title:string,Id:int}> */
    private static function wordpressPages(): array
    {
        if(!function_exists('get_posts')){return [];}$posts=get_posts(['post_type'=>'page','post_status'=>['publish','draft','private','pending'],'numberposts'=>-1,'orderby'=>'title','order'=>'ASC']);$out=[];
        foreach((array)$posts as $post){if(is_object($post)){$slug=(string)($post->post_name??'');$title=(string)($post->post_title??$slug);$id=(int)($post->ID??0);}elseif(is_array($post)){$slug=(string)($post['post_name']??$post['Slug']??'');$title=(string)($post['post_title']??$post['Title']??$slug);$id=(int)($post['ID']??$post['Id']??0);}else{continue;}$slug=sanitize_title($slug);if($slug!==''){$out[]=['Slug'=>$slug,'Title'=>$title,'Id'=>$id];}}
        usort($out,static fn(array $a,array $b): int=>strcmp($a['Slug'],$b['Slug']));return $out;
    }

    private static function guard(): void{if(!current_user_can('manage_options')){wp_die(esc_html__('Kun administratorer kan bruge conversion plannerens shadow-funktioner.','hangar18-manager'));}check_admin_referer(self::NONCE_ACTION);}
    private static function redirect(string $status,string $message): void{wp_safe_redirect(add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>mb_substr($message,0,700)],admin_url('admin.php')));exit;}
}
