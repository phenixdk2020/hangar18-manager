<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\AI\AiProposalTokenService;
use Hangar18\UltimateDesigner\AI\SuggestionGuard;
use Hangar18\UltimateDesigner\AI\TextAssistant;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressAiProviderRegistryFactory;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionAiProposalRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionAiSettingsRepository;
use Hangar18\UltimateDesigner\Permissions\CapabilityCatalog;
use RuntimeException;

/** I8 provider-neutral AI settings + isolated suggestion review flow. */
final class AiAdminController
{
    private const NONCE_ACTION='h18_ud_ai_v1';

    public static function register(): void
    {
        add_action('admin_enqueue_scripts',[self::class,'enqueueAssets']);
        add_action('admin_post_h18_ud_save_ai_settings',[self::class,'saveSettings']);
        add_action('admin_post_h18_ud_ai_text_suggest',[self::class,'suggestText']);
        add_action('admin_post_h18_ud_ai_decide',[self::class,'decide']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page=isset($_GET['page'])?sanitize_key((string)wp_unslash($_GET['page'])):'';
        if($page!==IntegrationAdminBootstrap::PAGE_SLUG&&strpos((string)$hook,IntegrationAdminBootstrap::PAGE_SLUG)===false){return;}
        $pluginFile=dirname(__DIR__,2).'/hangar18-manager.php';$version=class_exists('Hangar18_Manager')?(string)\Hangar18_Manager::VERSION:'0';$cssPath=dirname(__DIR__,2).'/assets/ultimate-designer-ai.css';
        wp_enqueue_style('hangar18-ultimate-designer-ai',plugins_url('assets/ultimate-designer-ai.css',$pluginFile),[],$version.'-'.(string)(@filemtime($cssPath)?:0));
    }

    public static function renderPanel(): void
    {
        $settingsRepo=new WordPressOptionAiSettingsRepository();$settings=$settingsRepo->get();$registry=(new WordPressAiProviderRegistryFactory())->create();$labels=$registry->labels();$proposals=(new WordPressOptionAiProposalRepository())->all();$canConfigure=current_user_can('manage_options');$canUse=self::canUseAi();
        $providerId=(string)($settings['ProviderId']??'');$providerReady=$providerId!==''&&$registry->has($providerId);$enabled=!empty($settings['Enabled'])&&$providerReady;
        echo '<section class="h18-ud-ai-panel"><div class="h18-ud-builder-panel-head"><div><h2>I8 · AI forslag</h2><p>Provider-neutral AI i shadow mode. AI kan kun oprette forslag; den får ingen repository/page-write adgang.</p></div><span class="h18-ud-shadow-badge">SUGGEST ONLY · APPLY/UNDO PLAN</span></div>';
        echo '<div class="h18-ud-ai-grid"><section class="h18-ud-ai-card"><h3>Provider settings</h3><p class="description">Credentials gemmes ikke i WordPress options. En provider-adapter registreres via <code>hangar18_ud_ai_providers</code> og håndterer selv secrets uden for dette settings-lag.</p>';
        echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_save_ai_settings"><label>Provider<select name="provider_id"'.($canConfigure?'':' disabled').'><option value="">Ingen provider</option>';
        foreach($labels as $id=>$label){echo '<option value="'.esc_attr($id).'"'.selected($providerId,$id,false).'>'.esc_html($label).' · '.esc_html($id).'</option>';}
        $checked=!empty($settings['Enabled'])?' checked="checked"':'';
        echo '</select></label><label class="h18-ud-ai-check"><input type="checkbox" name="enabled" value="1"'.$checked.($canConfigure?'':' disabled').'> Aktivér AI-forslag</label>';
        if($canConfigure){echo '<button class="button" type="submit">Gem AI settings</button>';}echo '</form>';
        echo '<div class="h18-ud-ai-state"><strong>Status</strong><span>'.($enabled?'Aktiv':'Inaktiv').'</span><span>'.($providerReady?'Provider registreret':'Provider ikke registreret').'</span><span>'.count($labels).' provider(e) tilgængelig(e)</span></div></section>';
        echo '<section class="h18-ud-ai-card"><h3>Tekstforslag sandbox</h3><p class="description">Sandboxen ændrer ingen side. Den bruger kun den tekst du indsætter og producerer et pending forslag.</p>';
        if(!$enabled){echo '<div class="notice notice-warning inline"><p>AI er ikke klar. Vælg en registreret provider og aktivér AI.</p></div>';}elseif(!$canUse){echo '<div class="notice notice-warning inline"><p>Din bruger mangler <code>'.esc_html(CapabilityCatalog::USE_AI).'</code>.</p></div>';}else{
            echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_ai_text_suggest"><label>Element key<input name="element_key" maxlength="100" required placeholder="intro"></label><label>Property<input name="property" maxlength="100" required value="Content"></label><label>Nuværende tekst<textarea name="current_text" rows="5" maxlength="12000" required></textarea></label><label>Instruktion<textarea name="instruction" rows="3" maxlength="2000" required placeholder="Gør teksten kortere og tydeligere"></textarea></label><button class="button button-primary" type="submit">Lav AI-forslag</button></form>';
        }echo '</section></div>';
        echo '<section class="h18-ud-ai-card h18-ud-ai-queue"><h3>Forslagskø</h3><p class="description">Accept opretter kun en reversibel Apply/Undo-plan. Planen bliver ikke skrevet til en side i I8.</p>';
        if($proposals===[]){echo '<p>Ingen AI-forslag endnu.</p>';}else{echo '<table class="widefat striped"><thead><tr><th>Status</th><th>Mål</th><th>Før</th><th>Efter</th><th>Begrundelse</th><th>Handling</th></tr></thead><tbody>';
            foreach($proposals as $proposal){$status=(string)($proposal['Status']??'');echo '<tr><td><strong>'.esc_html($status).'</strong></td><td><code>'.esc_html((string)($proposal['ElementKey']??'')).'.'.esc_html((string)($proposal['Property']??'')).'</code></td><td>'.esc_html(self::clip($proposal['Before']??'')).'</td><td>'.esc_html(self::clip($proposal['After']??'')).'</td><td>'.esc_html(self::clip($proposal['Reason']??'')).'</td><td>';
                if($status==='pending'&&$canUse){foreach(['accept'=>'Acceptér','reject'=>'Afvis'] as $decision=>$label){echo '<form class="h18-ud-ai-inline" method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_ai_decide"><input type="hidden" name="proposal_id" value="'.esc_attr((string)$proposal['Id']).'"><input type="hidden" name="proposal_token" value="'.esc_attr((string)($proposal['Token']??'')).'"><input type="hidden" name="decision" value="'.esc_attr($decision).'"><button class="button" type="submit">'.esc_html($label).'</button></form>';}}
                elseif($status==='accepted'){echo '<details><summary>Apply / Undo</summary><pre>'.esc_html(wp_json_encode(['Apply'=>$proposal['Apply']??null,'Undo'=>$proposal['Undo']??null])).'</pre></details>';}
                else{echo '—';}echo '</td></tr>';}
            echo '</tbody></table>';}
        echo '</section><div class="notice notice-info inline"><p><strong>I8 safety:</strong> Ingen API-key felter, ingen direkte page writes, ingen automatisk accept. Provider-output bliver altid et pending forslag, og Accept genererer kun Apply/Undo-data.</p></div></section>';
    }

    public static function saveSettings(): void
    {
        if(!current_user_can('manage_options')){wp_die(esc_html__('Kun administratorer kan ændre AI settings.','hangar18-manager'));}check_admin_referer(self::NONCE_ACTION);
        $providerId=sanitize_key((string)wp_unslash($_POST['provider_id']??''));$enabled=isset($_POST['enabled']);$registry=(new WordPressAiProviderRegistryFactory())->create();
        if($enabled&&($providerId===''||!$registry->has($providerId))){self::redirect('error','AI kan kun aktiveres med en provider, der er registreret i provider-registry.');}
        (new WordPressOptionAiSettingsRepository())->save(['ProviderId'=>$providerId,'Enabled'=>$enabled]);self::redirect('ai-settings-saved','AI settings gemt. Credentials er ikke gemt i WordPress options.');
    }

    public static function suggestText(): void
    {
        self::guardUse();$settings=(new WordPressOptionAiSettingsRepository())->get();$registry=(new WordPressAiProviderRegistryFactory())->create();$providerId=(string)($settings['ProviderId']??'');
        if(empty($settings['Enabled'])||$providerId===''||!$registry->has($providerId)){self::redirect('error','AI provider er ikke aktiv eller registreret.');}
        $elementKey=sanitize_key((string)wp_unslash($_POST['element_key']??''));$property=sanitize_key((string)wp_unslash($_POST['property']??''));$current=mb_substr((string)wp_unslash($_POST['current_text']??''),0,12000);$instruction=mb_substr(sanitize_textarea_field((string)wp_unslash($_POST['instruction']??'')),0,2000);
        if($elementKey===''||$property===''||trim($current)===''||trim($instruction)===''){self::redirect('error','Element, property, nuværende tekst og instruktion er påkrævet.');}
        try{$proposal=(new TextAssistant($registry->get($providerId)))->suggest($elementKey,$property,$current,$instruction,['Source'=>'I8 sandbox']);$issued=self::tokenService()->issue($proposal);$proposal['Token']=$issued['token'];$proposal['TokenExpires']=$issued['expires'];(new WordPressOptionAiProposalRepository())->save($proposal);self::redirect('ai-proposal-created','AI-forslag oprettet som pending. Ingen side er ændret.');}
        catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    public static function decide(): void
    {
        self::guardUse();$id=sanitize_text_field((string)wp_unslash($_POST['proposal_id']??''));$token=(string)wp_unslash($_POST['proposal_token']??'');$decision=sanitize_key((string)wp_unslash($_POST['decision']??''));$repo=new WordPressOptionAiProposalRepository();$proposal=$repo->get($id);
        if($proposal===null||($proposal['Status']??'')!=='pending'){self::redirect('error','Forslaget findes ikke eller er ikke længere pending.');}
        $base=$proposal;unset($base['Token'],$base['TokenExpires']);if(!self::tokenService()->verify($token,$base)){self::redirect('error','AI-forslagets signatur er ugyldig eller udløbet.');}
        $guard=new SuggestionGuard();try{if($decision==='accept'){$proposal=$guard->accept($base,true);$proposal['DecisionBy']=function_exists('get_current_user_id')?get_current_user_id():0;$repo->save($proposal);self::redirect('ai-proposal-accepted','Forslaget er accepteret som Apply/Undo-plan. Ingen side er ændret.');}if($decision==='reject'){$proposal=$guard->reject($base);$proposal['DecisionBy']=function_exists('get_current_user_id')?get_current_user_id():0;$repo->save($proposal);self::redirect('ai-proposal-rejected','Forslaget er afvist.');}throw new RuntimeException('Ukendt AI decision.');}catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    private static function canUseAi(): bool{return current_user_can(CapabilityCatalog::USE_AI)||current_user_can('manage_options');}
    private static function guardUse(): void{if(!self::canUseAi()){wp_die(esc_html__('Du har ikke rettighed til at bruge AI.','hangar18-manager'));}check_admin_referer(self::NONCE_ACTION);}
    private static function tokenService(): AiProposalTokenService{$secret=function_exists('wp_salt')?(string)wp_salt('auth'):'';if(strlen($secret)<32){throw new RuntimeException('WordPress auth salt er ikke tilgængelig til AI proposal-signering.');}return new AiProposalTokenService($secret);}
    /** @param mixed $value */
    private static function clip($value): string{$text=is_scalar($value)?(string)$value:wp_json_encode($value);$text=preg_replace('/\s+/u',' ',trim($text))??'';return mb_strlen($text)>120?mb_substr($text,0,117).'...':$text;}
    private static function redirect(string $status,string $message): void{wp_safe_redirect(add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>mb_substr($message,0,700)],admin_url('admin.php')));exit;}
}
