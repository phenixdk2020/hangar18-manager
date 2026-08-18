<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionManualQaEvidenceRepository;
use Hangar18\UltimateDesigner\QA\ManualEvidenceValidator;
use Hangar18\UltimateDesigner\QA\ReleaseReadiness;
use Hangar18\UltimateDesigner\QA\RollbackPreflightService;

/** I9 manual evidence dashboard. Automated preflight never marks a manual gate as passed. */
final class QaDashboardAdminController
{
    private const NONCE_ACTION='h18_ud_qa_dashboard_v1';
    private const PREFLIGHT_OPTION='hangar18_ud_rollback_preflight_v1';

    public static function register(): void
    {
        add_action('admin_enqueue_scripts',[self::class,'enqueueAssets']);
        add_action('admin_post_h18_ud_save_qa_evidence',[self::class,'saveEvidence']);
        add_action('admin_post_h18_ud_run_rollback_preflight',[self::class,'runRollbackPreflight']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page=isset($_GET['page'])?sanitize_key((string)wp_unslash($_GET['page'])):'';
        if($page!==IntegrationAdminBootstrap::PAGE_SLUG&&strpos((string)$hook,IntegrationAdminBootstrap::PAGE_SLUG)===false){return;}
        $pluginFile=dirname(__DIR__,2).'/hangar18-manager.php';$version=class_exists('Hangar18_Manager')?(string)\Hangar18_Manager::VERSION:'0';$cssPath=dirname(__DIR__,2).'/assets/ultimate-designer-qa.css';
        wp_enqueue_style('hangar18-ultimate-designer-qa',plugins_url('assets/ultimate-designer-qa.css',$pluginFile),[],$version.'-'.(string)(@filemtime($cssPath)?:0));
    }

    public static function renderPanel(): void
    {
        $repo=new WordPressOptionManualQaEvidenceRepository();$records=$repo->all();$validator=new ManualEvidenceValidator();$manual=$validator->statusMap($records);$readiness=(new ReleaseReadiness())->evaluate([],$manual);$canManage=current_user_can('manage_options');$preflight=get_option(self::PREFLIGHT_OPTION,[]);if(!is_array($preflight)){$preflight=[];}
        echo '<section class="h18-ud-qa-panel"><div class="h18-ud-builder-panel-head"><div><h2>I9 · Manual QA & rollback rehearsal</h2><p>Manuel evidens kan ikke erstattes af automatiske tests. I10 forbliver blokeret indtil alle krævede manuelle gates er dokumenteret som PASS.</p></div><span class="h18-ud-shadow-badge">'.(int)$readiness['ManualPassed'].'/'.(int)$readiness['ManualTotal'].' MANUAL PASS</span></div>';
        echo '<div class="h18-ud-qa-summary"><strong>'.(!empty($readiness['Ready'])?'MANUAL GATES COMPLETE':'I10 BLOCKED').'</strong><span>'.count((array)$readiness['PendingManual']).' pending</span><span>Automated evidence kan ikke auto-godkende</span></div>';
        echo '<table class="widefat striped h18-ud-qa-table"><thead><tr><th>Gate</th><th>Status / evidens</th><th>Registrér manuel evidens</th></tr></thead><tbody>';
        foreach($manual as $gate=>$passed){$record=$records[$gate]??[];$status=(string)($record['Status']??'pending');echo '<tr><td><strong>'.esc_html(self::label($gate)).'</strong><br><code>'.esc_html($gate).'</code></td><td><span class="h18-ud-qa-status h18-ud-qa-status-'.esc_attr($status).'">'.esc_html(strtoupper($status)).'</span>';
            if($record){echo '<dl><dt>Miljø</dt><dd>'.esc_html((string)($record['Environment']??'')).'</dd><dt>Evidens</dt><dd>'.esc_html((string)($record['EvidenceRef']??'')).'</dd><dt>Tid</dt><dd>'.esc_html((string)($record['CapturedUtc']??'')).'</dd><dt>Bruger-ID</dt><dd>'.(int)($record['UserId']??0).'</dd></dl>';if(trim((string)($record['Notes']??''))!==''){echo '<p>'.esc_html((string)$record['Notes']).'</p>';}}echo '</td><td>';
            if($canManage){echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_save_qa_evidence"><input type="hidden" name="gate" value="'.esc_attr($gate).'"><label>Status<select name="status"><option value="pending"'.selected($status,'pending',false).'>Pending</option><option value="pass"'.selected($status,'pass',false).'>Pass</option><option value="fail"'.selected($status,'fail',false).'>Fail</option></select></label><label>Miljø / browser / device<input name="environment" maxlength="240" value="'.esc_attr((string)($record['Environment']??'')).'" placeholder="test2 · Safari · iPhone"></label><label>Evidens-reference<input name="evidence_ref" maxlength="500" value="'.esc_attr((string)($record['EvidenceRef']??'')).'" placeholder="URL, ticket, screenshot-id eller testlog"></label><label>Noter<textarea name="notes" rows="3" maxlength="3000">'.esc_textarea((string)($record['Notes']??'')).'</textarea></label><label class="h18-ud-qa-confirm"><input type="checkbox" name="confirmed_manual" value="1"> Jeg bekræfter, at PASS er manuelt verificeret i det angivne miljø.</label><button class="button" type="submit">Gem evidens</button></form>';}else{echo '<p>Kun administratorer kan registrere evidens.</p>';}echo '</td></tr>';}
        echo '</tbody></table>';
        echo '<section class="h18-ud-qa-preflight"><h3>Rollback preflight på kopi</h3><p>Preflight kopierer den aktuelle legacy page-store til memory, simulerer en ændring og verificerer byte-semantisk restore. Den skriver <strong>ikke</strong> tilbage til page-store og kan ikke lukke <code>migration-rollback-live-copy</code>.</p>';
        if($preflight){echo '<div class="h18-ud-qa-preflight-result"><strong>'.(!empty($preflight['Pass'])?'PASS':'FAIL').'</strong><span>Mode: '.esc_html((string)($preflight['Mode']??'')).'</span><span>Items: '.(int)($preflight['SourceItems']??0).'</span><span>Ran: '.esc_html((string)($preflight['RanUtc']??'')).'</span><code>'.esc_html((string)($preflight['BeforeHash']??'')).'</code></div>';}
        if($canManage){echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_run_rollback_preflight"><button class="button" type="submit">Kør rollback preflight på kopi</button></form>';}echo '</section>';
        echo '<div class="notice notice-warning inline"><p><strong>I10-gate:</strong> Selv en grøn automatisk preflight tæller ikke som live-copy evidence. Den krævede live-copy rollback skal stadig udføres og registreres manuelt.</p></div></section>';
    }

    public static function saveEvidence(): void
    {
        self::guard();$gate=sanitize_key((string)wp_unslash($_POST['gate']??''));$status=sanitize_key((string)wp_unslash($_POST['status']??'pending'));
        try{(new WordPressOptionManualQaEvidenceRepository())->save($gate,['Status'=>$status,'Environment'=>sanitize_text_field((string)wp_unslash($_POST['environment']??'')),'EvidenceRef'=>sanitize_text_field((string)wp_unslash($_POST['evidence_ref']??'')),'Notes'=>sanitize_textarea_field((string)wp_unslash($_POST['notes']??'')),'ConfirmedManual'=>isset($_POST['confirmed_manual'])],function_exists('get_current_user_id')?get_current_user_id():0);self::redirect('qa-evidence-saved','Manuel QA evidens gemt for '.$gate.'.');}
        catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    public static function runRollbackPreflight(): void
    {
        self::guard();$snapshot=get_option('hangar18_manager_pages_v1',[]);if(!is_array($snapshot)){$snapshot=[];}$result=(new RollbackPreflightService())->rehearse($snapshot);$result['UserId']=function_exists('get_current_user_id')?get_current_user_id():0;update_option(self::PREFLIGHT_OPTION,$result,false);self::redirect(!empty($result['Pass'])?'qa-preflight-pass':'error',!empty($result['Pass'])?'Rollback preflight på kopi bestod. Live-copy gate er stadig manuel.':'Rollback preflight fejlede.');
    }

    private static function guard(): void{if(!current_user_can('manage_options')){wp_die(esc_html__('Kun administratorer kan registrere QA evidens.','hangar18-manager'));}check_admin_referer(self::NONCE_ACTION);}
    private static function label(string $gate): string{$labels=['latest-chrome-brand'=>'Chrome brand/layout','latest-edge-brand'=>'Edge brand/layout','latest-firefox-brand'=>'Firefox brand/layout','latest-safari-brand'=>'Safari brand/layout','screen-reader-core-flow'=>'Screen reader core flow','test2-live-site-e2e'=>'test2 live-site E2E','vehicle-event-gallery-visual-regression'=>'Vehicle/Event/Gallery visual regression','migration-rollback-live-copy'=>'Migration rollback på live-copy'];return $labels[$gate]??$gate;}
    private static function redirect(string $status,string $message): void{wp_safe_redirect(add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>mb_substr($message,0,700)],admin_url('admin.php')));exit;}
}
