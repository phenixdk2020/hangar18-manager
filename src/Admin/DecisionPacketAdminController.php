<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionAcceptanceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionWorkspaceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionManualQaEvidenceRepository;
use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceValidator;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketFingerprintService;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketFormatter;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketReviewChainService;
use Hangar18\UltimateDesigner\Migration\ConversionDecisionPacketService;
use Hangar18\UltimateDesigner\QA\ManualEvidenceValidator;

/** Read-only operator view for the I10 decision packet. No actions or persistence. */
final class DecisionPacketAdminController
{
    public static function renderPanel(): void
    {
        $manualRecords=(new WordPressOptionManualQaEvidenceRepository())->all();
        $manual=(new ManualEvidenceValidator())->statusMap($manualRecords);
        $workspace=(new WordPressOptionConversionWorkspaceRepository())->all();
        $acceptance=(new WordPressOptionConversionAcceptanceRepository())->all();
        $acceptanceValidator=new ConversionAcceptanceValidator();
        $accepted=[];
        foreach($workspace as $slug=>$record){
            if(!is_array($record)){continue;}
            $hash=(string)($record['SourceHash']??'');
            if($hash!==''&&$acceptanceValidator->isAccepted(is_array($acceptance[$slug]??null)?$acceptance[$slug]:null,$hash)){$accepted[]=(string)$slug;}
        }

        $legacy=get_option('hangar18_manager_pages_v1',[]);
        if(!is_array($legacy)){$legacy=[];}
        $pages=self::wordpressPages();
        $targetInputs=[];
        foreach($pages as $page){
            $slug=(string)$page['Slug'];
            $targetInputs[$slug]=[
                'PageId'=>(int)$page['Id'],
                'Permalink'=>(string)$page['Permalink'],
                'CurrentLegacyState'=>is_array($legacy[$slug]??null)?$legacy[$slug]:[],
                'Shadow'=>is_array($workspace[$slug]??null)?$workspace[$slug]:null,
                'AcceptanceRecord'=>is_array($acceptance[$slug]??null)?$acceptance[$slug]:null,
            ];
        }

        $packet=(new ConversionDecisionPacketService())->build($pages,$manual,$accepted,$targetInputs);
        $fingerprint=(new ConversionDecisionPacketFingerprintService())->fingerprint($packet);
        $reviewChain=(new ConversionDecisionPacketReviewChainService())->inspect($packet,$fingerprint,null);
        $packetJson=(new ConversionDecisionPacketFormatter())->json($packet);
        $reviewable=(array)($packet['ReviewableTargets']??[]);
        $blocked=(array)($packet['BlockedTargets']??[]);

        echo '<section class="h18-ud-conversion-panel h18-ud-decision-packet-panel">';
        echo '<div class="h18-ud-builder-panel-head"><div><h2>I10 · Decision packet · read-only</h2><p>Samlet operatorvisning af plan, readiness, acceptance og preflight. Panelet har ingen formularer eller actions og kan ikke aktivere public cutover.</p></div><span class="h18-ud-shadow-badge">READ ONLY · CUTOVER LOCKED</span></div>';
        echo '<div class="h18-ud-conversion-summary"><strong>'.count($reviewable).' reviewable target(s)</strong><span>'.count($blocked).' blocked target(s)</span><span>Executable: NO</span><span>PublicMutationAvailable: NO</span><span>Packet SHA-256: <code>'.esc_html(substr((string)($fingerprint['Hash']??''),0,16)).'…</code></span></div>';
        echo '<div class="notice notice-info inline"><p><strong>Betydning:</strong> “Operator reviewable” betyder kun, at det aktuelle decision packet ikke har blockers for menneskelig gennemgang. Det er <em>ikke</em> tilladelse til publicering eller cutover.</p></div>';
        echo '<div class="notice notice-warning inline"><p><strong>Review chain:</strong> Human review receipt gemmes ikke af dette read-only panel. Status er derfor <code>ReviewChainValid='.(!empty($reviewChain['ReviewChainValid'])?'true':'false').'</code> og <code>FreshHumanReviewRequired='.(!empty($reviewChain['FreshHumanReviewRequired'])?'true':'false').'</code>. Dette panel kan ikke oprette eller godkende en receipt.</p></div>';
        echo '<table class="widefat striped h18-ud-conversion-table"><thead><tr><th>Trin</th><th>Target</th><th>Plan</th><th>Preflight</th><th>Operator review</th><th>Blockers</th></tr></thead><tbody>';
        foreach((array)($packet['Stages']??[]) as $row){
            if(!is_array($row)){continue;}
            $blockers=array_values(array_filter(array_map('strval',(array)($row['Blockers']??[])),static fn(string $v):bool=>$v!==''));
            echo '<tr>';
            echo '<td><strong>'.(int)($row['Stage']??0).'</strong><br>'.esc_html((string)($row['Kind']??'')).'</td>';
            echo '<td><strong>'.esc_html((string)($row['Title']??'')).'</strong><br><code>'.esc_html((string)($row['Slug']??'')).'</code></td>';
            echo '<td>'.(!empty($row['PlanEligible'])?'<strong>ELIGIBLE</strong>':'BLOCKED').'</td>';
            echo '<td>'.(!empty($row['PreflightAvailable'])?'AVAILABLE':'MISSING').'</td>';
            echo '<td>'.(!empty($row['EligibleForOperatorReview'])?'<strong>REVIEWABLE</strong>':'NOT REVIEWABLE').'</td>';
            echo '<td>';
            if($blockers===[]){echo '—';}else{echo '<ul>';foreach($blockers as $blocker){echo '<li><code>'.esc_html($blocker).'</code></li>';}echo '</ul>';}
            echo '</td></tr>';
        }
        echo '</tbody></table>';
        echo '<details class="h18-ud-decision-packet-evidence"><summary><strong>Vis decision packet JSON · read-only evidence snapshot</strong></summary><p><small>Fingerprint: <code>'.esc_html((string)($fingerprint['Hash']??'')).'</code>. Snapshotet genereres ved sidevisning og gemmes ikke af panelet.</small></p><pre>'.esc_html($packetJson).'</pre></details>';
        echo '<div class="notice notice-error inline"><p><strong>Permanent lås i denne slice:</strong> <code>AuthorizesCutover=false</code>, <code>Executable=false</code> og <code>PublicMutationAvailable=false</code>. Vehicle/Event/Gallery forbliver protected legacy-domæner.</p></div>';
        echo '</section>';
    }

    /** @return list<array{Slug:string,Title:string,Id:int,Permalink:string}> */
    private static function wordpressPages(): array
    {
        if(!function_exists('get_posts')){return [];}
        $posts=get_posts(['post_type'=>'page','post_status'=>['publish','draft','private','pending'],'numberposts'=>-1,'orderby'=>'title','order'=>'ASC']);
        $out=[];
        foreach((array)$posts as $post){
            if(is_object($post)){$slug=(string)($post->post_name??'');$title=(string)($post->post_title??$slug);$id=(int)($post->ID??0);}
            elseif(is_array($post)){$slug=(string)($post['post_name']??$post['Slug']??'');$title=(string)($post['post_title']??$post['Title']??$slug);$id=(int)($post['ID']??$post['Id']??0);}
            else{continue;}
            $slug=sanitize_title($slug);
            if($slug===''){continue;}
            $permalink=function_exists('get_permalink')?(string)get_permalink($id):'';
            $out[]=['Slug'=>$slug,'Title'=>$title,'Id'=>$id,'Permalink'=>$permalink];
        }
        usort($out,static fn(array $a,array $b):int=>strcmp($a['Slug'],$b['Slug']));
        return $out;
    }
}
