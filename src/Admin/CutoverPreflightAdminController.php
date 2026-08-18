<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionAcceptanceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionWorkspaceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionCutoverPreflightRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionManualQaEvidenceRepository;
use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceValidator;
use Hangar18\UltimateDesigner\Migration\ConversionCutoverPreflightService;
use Hangar18\UltimateDesigner\Migration\ConversionCutoverPreflightTokenService;
use Hangar18\UltimateDesigner\Migration\ConversionPlanService;
use Hangar18\UltimateDesigner\Migration\ConversionTargetCatalog;
use Hangar18\UltimateDesigner\QA\ManualEvidenceValidator;

/**
 * I10-C future-cutover preflight UI.
 *
 * This controller can only persist signed, non-executable snapshots. It has no
 * activate/cutover/publish handler and never mutates posts, URLs or legacy page data.
 */
final class CutoverPreflightAdminController
{
    private const NONCE_ACTION = 'h18_ud_cutover_preflight_v1';

    public static function register(): void
    {
        add_action('admin_post_h18_ud_create_cutover_preflight', [self::class, 'create']);
    }

    public static function renderPanel(): void
    {
        $workspace = (new WordPressOptionConversionWorkspaceRepository())->all();
        $acceptance = (new WordPressOptionConversionAcceptanceRepository())->all();
        $stored = (new WordPressOptionCutoverPreflightRepository())->all();
        $manual = (new ManualEvidenceValidator())->statusMap((new WordPressOptionManualQaEvidenceRepository())->all());
        $pages = self::wordpressPages();
        $accepted = self::acceptedSlugs($workspace, $acceptance);
        $plan = (new ConversionPlanService())->plan($pages, $manual, $accepted);
        $comparisonSlug = (string) ($plan['ComparisonSlug'] ?? '');
        $legacy = get_option('hangar18_manager_pages_v1', []);
        if (!is_array($legacy)) { $legacy = []; }
        $targets = new ConversionTargetCatalog();
        $service = new ConversionCutoverPreflightService();
        $tokens = new ConversionCutoverPreflightTokenService(self::secret());
        $pageMap = [];
        foreach ($pages as $page) { $pageMap[(string) $page['Slug']] = $page; }

        echo '<section class="h18-ud-conversion-panel h18-ud-cutover-preflight-panel">';
        echo '<div class="h18-ud-builder-panel-head"><div><h2>I10 · Cutover preflight</h2><p>Preflight verificerer global QA, rækkefølge, shadow acceptance, WordPress-identitet og source-drift. <strong>Et signeret preflight giver ingen aktiveringsret.</strong></p></div><span class="h18-ud-shadow-badge">SIGNED PREFLIGHT · NON-EXECUTABLE</span></div>';
        echo '<div class="notice notice-warning inline"><p><strong>Public cutover er stadig låst:</strong> Denne fase gemmer kun et tidsbegrænset, signeret snapshot med <code>Executable=false</code> og <code>PublicMutationAvailable=false</code>.</p></div>';

        if (!$workspace) {
            echo '<p>Ingen shadow-copies endnu. Opret og accepter først en shadow-copy i I10-planneren.</p></section>';
            return;
        }

        echo '<table class="widefat striped h18-ud-conversion-table"><thead><tr><th>Target</th><th>Aktuel preflight</th><th>Source</th><th>Signeret snapshot</th></tr></thead><tbody>';
        foreach ($workspace as $slug => $shadow) {
            if (!is_string($slug) || !is_array($shadow)) { continue; }
            $protected = $targets->isProtected($slug);
            $page = $pageMap[$slug] ?? ['Id'=>0,'Permalink'=>''];
            $legacyState = is_array($legacy[$slug] ?? null) ? $legacy[$slug] : [];
            $current = $service->build(
                $slug,
                (int) ($page['Id'] ?? 0),
                (string) ($page['Permalink'] ?? ''),
                $legacyState,
                $shadow,
                is_array($acceptance[$slug] ?? null) ? $acceptance[$slug] : null,
                $manual,
                $accepted,
                $comparisonSlug
            );
            $eligible = !empty($current['EligibleForFutureCutover']) && !$protected;
            $record = is_array($stored[$slug] ?? null) ? $stored[$slug] : null;
            $storedValid = false;
            if ($record && is_array($record['Preflight'] ?? null)) {
                $storedValid = $tokens->verify((string) ($record['Token'] ?? ''), $record['Preflight'])
                    && hash_equals((string) ($record['PreflightHash'] ?? ''), $tokens->preflightHash($current));
            }

            echo '<tr><td><strong>'.esc_html($slug).'</strong>'.($protected?'<br><span class="h18-ud-conversion-protected">PROTECTED LEGACY</span>':'').'</td>';
            echo '<td><strong>'.($eligible?'ELIGIBLE FOR SIGNED PREFLIGHT':'BLOCKED').'</strong>';
            $blockers = (array) ($current['Blockers'] ?? []);
            if ($blockers) { echo '<ul>'; foreach ($blockers as $blocker) { echo '<li><code>'.esc_html((string) $blocker).'</code></li>'; } echo '</ul>'; }
            echo '</td>';
            echo '<td><small>Shadow<br><code>'.esc_html(substr((string) ($current['ShadowSourceHash'] ?? ''),0,16)).'…</code><br>Current legacy<br><code>'.esc_html(substr((string) ($current['CurrentLegacyHash'] ?? ''),0,16)).'…</code><br>Drift: '.(!empty($current['SourceDriftFree'])?'NONE':'BLOCKED').'</small></td>';
            echo '<td>';
            if ($record) {
                echo '<p><strong>'.($storedValid?'CURRENT':'STALE/EXPIRED').'</strong><br><small>Hash: <code>'.esc_html(substr((string) ($record['PreflightHash'] ?? ''),0,16)).'…</code><br>Expires: '.esc_html(gmdate('c',(int) ($record['TokenExpires'] ?? 0))).'</small></p>';
            }
            if ($eligible && current_user_can('manage_options')) {
                echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';
                wp_nonce_field(self::NONCE_ACTION);
                echo '<input type="hidden" name="action" value="h18_ud_create_cutover_preflight"><input type="hidden" name="slug" value="'.esc_attr($slug).'">';
                echo '<button type="submit" class="button button-secondary">'.($record?'Forny signed preflight':'Opret signed preflight').'</button></form>';
            }
            echo '</td></tr>';
        }
        echo '</tbody></table>';
        echo '<p class="description">Hvis legacy editor-state ændres efter shadow/acceptance, bliver <code>CurrentLegacyHash</code> forskellig fra <code>ShadowSourceHash</code>, og preflight blokeres med <code>legacy-source-drift</code>.</p>';
        echo '</section>';
    }

    public static function create(): void
    {
        self::guard();
        $slug = sanitize_title((string) wp_unslash($_POST['slug'] ?? ''));
        $targets = new ConversionTargetCatalog();
        if ($slug === '' || $targets->isProtected($slug)) { self::redirect('error','Preflight må ikke oprettes for et tomt eller beskyttet Vehicle/Event/Gallery-target.'); }

        $workspace = (new WordPressOptionConversionWorkspaceRepository())->all();
        $shadow = is_array($workspace[$slug] ?? null) ? $workspace[$slug] : null;
        if (!$shadow) { self::redirect('error','Der findes ingen shadow-copy for target.'); }
        $acceptance = (new WordPressOptionConversionAcceptanceRepository())->all();
        $manual = (new ManualEvidenceValidator())->statusMap((new WordPressOptionManualQaEvidenceRepository())->all());
        $pages = self::wordpressPages();
        $accepted = self::acceptedSlugs($workspace,$acceptance);
        $plan = (new ConversionPlanService())->plan($pages,$manual,$accepted);
        $comparisonSlug = (string) ($plan['ComparisonSlug'] ?? '');
        $page = null;
        foreach ($pages as $candidate) { if ((string) $candidate['Slug'] === $slug) { $page = $candidate; break; } }
        if (!$page) { self::redirect('error','WordPress-siden findes ikke længere.'); }
        $legacy = get_option('hangar18_manager_pages_v1', []);
        if (!is_array($legacy) || !is_array($legacy[$slug] ?? null)) { self::redirect('error','Legacy editor-state mangler for target.'); }

        try {
            $preflight = (new ConversionCutoverPreflightService())->build(
                $slug,(int)$page['Id'],(string)$page['Permalink'],$legacy[$slug],$shadow,
                is_array($acceptance[$slug] ?? null)?$acceptance[$slug]:null,$manual,$accepted,$comparisonSlug
            );
            if (empty($preflight['EligibleForFutureCutover'])) {
                self::redirect('error','Preflight er blokeret: '.implode(', ',(array)($preflight['Blockers']??[])));
            }
            $tokens = new ConversionCutoverPreflightTokenService(self::secret());
            $signed = $tokens->issue($preflight,900);
            if (!$tokens->verify($signed['token'],$preflight)) { throw new \RuntimeException('Preflight-signaturen kunne ikke verificeres.'); }
            (new WordPressOptionCutoverPreflightRepository())->save($slug,$preflight,$signed,function_exists('get_current_user_id')?get_current_user_id():0);
            self::redirect('cutover-preflight-created','Signed preflight oprettet for '.$slug.'. Snapshot er ikke eksekverbart og aktiverer ingen offentlig side.');
        } catch (\Throwable $e) {
            self::redirect('error',$e->getMessage());
        }
    }

    /** @param array<string,array<string,mixed>> $workspace @param array<string,array<string,mixed>> $acceptance @return list<string> */
    private static function acceptedSlugs(array $workspace,array $acceptance): array
    {
        $validator = new ConversionAcceptanceValidator(); $out=[];
        foreach ($workspace as $slug=>$shadow) {
            if (is_string($slug) && is_array($shadow) && $validator->isAccepted(is_array($acceptance[$slug]??null)?$acceptance[$slug]:null,(string)($shadow['SourceHash']??''))) { $out[]=$slug; }
        }
        sort($out,SORT_STRING); return $out;
    }

    /** @return list<array{Slug:string,Title:string,Id:int,Permalink:string}> */
    private static function wordpressPages(): array
    {
        if (!function_exists('get_posts')) { return []; }
        $posts=get_posts(['post_type'=>'page','post_status'=>['publish','draft','private','pending'],'numberposts'=>-1,'orderby'=>'title','order'=>'ASC']); $out=[];
        foreach ((array)$posts as $post) {
            if (is_object($post)) { $slug=(string)($post->post_name??'');$title=(string)($post->post_title??$slug);$id=(int)($post->ID??0); }
            elseif (is_array($post)) { $slug=(string)($post['post_name']??$post['Slug']??'');$title=(string)($post['post_title']??$post['Title']??$slug);$id=(int)($post['ID']??$post['Id']??0); }
            else { continue; }
            $slug=sanitize_title($slug); if($slug===''){continue;}
            $permalink=$id>0&&function_exists('get_permalink')?(string)get_permalink($id):'';
            $out[]=['Slug'=>$slug,'Title'=>$title,'Id'=>$id,'Permalink'=>$permalink];
        }
        usort($out,static fn(array $a,array $b): int=>strcmp($a['Slug'],$b['Slug'])); return $out;
    }

    private static function secret(): string
    {
        $salt = function_exists('wp_salt') ? (string) wp_salt('auth') : '';
        return hash('sha256',$salt.'|hangar18-cutover-preflight-v1');
    }

    private static function guard(): void
    {
        if(!current_user_can('manage_options')){wp_die(esc_html__('Kun administratorer kan oprette cutover preflight.','hangar18-manager'));}
        check_admin_referer(self::NONCE_ACTION);
    }

    private static function redirect(string $status,string $message): void
    {
        $url=add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>rawurlencode(mb_substr($message,0,600))],admin_url('admin.php'));
        wp_safe_redirect($url);exit;
    }
}
