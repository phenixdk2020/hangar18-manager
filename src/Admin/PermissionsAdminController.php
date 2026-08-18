<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionDesignLockRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressRoleInstaller;
use Hangar18\UltimateDesigner\Permissions\RoleDefinitionCatalog;
use Hangar18\UltimateDesigner\Permissions\RoleInstallationPlanner;

/** I7 additive permissions rollout + Design Lock policy UI. */
final class PermissionsAdminController
{
    private const NONCE_ACTION='h18_ud_permissions_v1';
    private const AUDIT_OPTION='hangar18_ud_role_install_audit_v1';

    public static function register(): void
    {
        add_action('admin_enqueue_scripts',[self::class,'enqueueAssets']);
        add_action('admin_post_h18_ud_install_roles',[self::class,'installRoles']);
        add_action('admin_post_h18_ud_save_design_lock',[self::class,'saveDesignLock']);
    }

    /** @param mixed $hook */
    public static function enqueueAssets($hook): void
    {
        $page=isset($_GET['page'])?sanitize_key((string)wp_unslash($_GET['page'])):'';
        if($page!==IntegrationAdminBootstrap::PAGE_SLUG&&strpos((string)$hook,IntegrationAdminBootstrap::PAGE_SLUG)===false){return;}
        $pluginFile=dirname(__DIR__,2).'/hangar18-manager.php';$version=class_exists('Hangar18_Manager')?(string)\Hangar18_Manager::VERSION:'0';$cssPath=dirname(__DIR__,2).'/assets/ultimate-designer-permissions.css';
        wp_enqueue_style('hangar18-ultimate-designer-permissions',plugins_url('assets/ultimate-designer-permissions.css',$pluginFile),[],$version.'-'.(string)(@filemtime($cssPath)?:0));
    }

    public static function renderPanel(): void
    {
        $plan=(new RoleInstallationPlanner())->plan(self::currentRoleCapabilities());$settings=(new WordPressOptionDesignLockRepository())->get();$canManage=current_user_can('manage_options');
        echo '<section class="h18-ud-permissions-panel"><div class="h18-ud-builder-panel-head"><div><h2>I7 · Permissions & Design Lock</h2><p>Roller installeres additivt. Ingen eksisterende capability fjernes, og legacy <code>edit_pages</code> forbliver adgangsgate indtil I10.</p></div><span class="h18-ud-shadow-badge">ADDITIVE ONLY · NO LOCKOUT</span></div>';
        echo '<div class="h18-ud-permission-grid"><section class="h18-ud-permission-card"><h3>Role migration preview</h3><p class="description">Dette er den præcise plan før installation. <strong>Removals: '.(int)$plan['Removals'].'</strong>.</p><table class="widefat striped"><thead><tr><th>Rolle</th><th>Status</th><th>Capabilities der tilføjes</th><th>Domæne</th></tr></thead><tbody>';
        foreach($plan['Roles'] as $slug=>$role){$add=(array)$role['Add'];echo '<tr><td><strong>'.esc_html((string)$role['Label']).'</strong><br><code>'.esc_html((string)$slug).'</code></td><td>'.(!empty($role['Create'])?'Opret':'Findes').'</td><td>'.($add?'<code>'.esc_html(implode(', ',$add)).'</code>':'Ingen ændring').'</td><td><code>'.esc_html(implode(', ',(array)$role['Domains'])).'</code></td></tr>';}
        $adminAdd=(array)$plan['Administrator']['Add'];echo '<tr><td><strong>WordPress Administrator</strong></td><td>Bevares</td><td>'.($adminAdd?'<code>'.esc_html(implode(', ',$adminAdd)).'</code>':'Ingen ændring').'</td><td><code>*</code></td></tr></tbody></table><p><strong>'.(int)$plan['TotalCapabilitiesToAdd'].'</strong> capability-grants mangler i den nuværende installation.</p>';
        if($canManage){echo '<form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_install_roles"><label class="h18-ud-permission-confirm"><input type="checkbox" name="confirm_install" value="yes" required> Jeg har gennemgået previewet. Opret/opdatér roller additivt; fjern intet.</label><button class="button button-primary" type="submit">Installer / opdatér UD roller</button></form>';}else{echo '<p class="description">Kun en bruger med <code>manage_options</code> kan installere roller.</p>';}
        echo '</section><section class="h18-ud-permission-card"><h3>Design Lock policy</h3><p class="description">Policyen er klar til den nye editor/runtime. Den håndhæves ikke mod legacy Sider-editoren før den kontrollerede cutover.</p><form method="post" action="'.esc_url(admin_url('admin-post.php')).'">';wp_nonce_field(self::NONCE_ACTION);echo '<input type="hidden" name="action" value="h18_ud_save_design_lock">';
        self::checkbox('Enabled','Aktivér Design Lock policy',!empty($settings['Enabled']),$canManage);self::checkbox('LockStructure','Lås struktur for content editors',!empty($settings['LockStructure']),$canManage);self::checkbox('LockDesign','Lås design/typografi/responsive for content editors',!empty($settings['LockDesign']),$canManage);echo '<label>Frigivne content-properties<textarea name="released_properties" rows="5"'.($canManage?'':' disabled').'>'.esc_textarea(implode("\n",(array)$settings['ReleasedProperties'])).'</textarea><small>Én property pr. linje. Disse kan redigeres selv når Design Lock er aktiv.</small></label><div class="h18-ud-lock-summary"><strong>Aktuel policy</strong><span>Structure: '.(!empty($settings['LockStructure'])?'låst':'åben').'</span><span>Design: '.(!empty($settings['LockDesign'])?'låst':'åben').'</span><span>'.count((array)$settings['ReleasedProperties']).' frigivne properties</span></div>';
        if($canManage){echo '<button class="button" type="submit">Gem Design Lock policy</button>';}echo '</form></section></div>';
        echo '<div class="notice notice-info inline"><p><strong>Migration-sikkerhed:</strong> I7 ændrer ikke brugerroller på eksisterende brugere, fjerner ikke <code>edit_pages</code>, ændrer ikke frontend og aktiverer ikke Design Lock i legacy-editoren.</p></div></section>';
    }

    public static function installRoles(): void
    {
        self::guard();if((string)($_POST['confirm_install']??'')!=='yes'){self::redirect('error','Role installation kræver eksplicit confirmation efter preview.');}
        try{$plan=(new RoleInstallationPlanner())->plan(self::currentRoleCapabilities());$audit=['CreatedUtc'=>gmdate('c'),'UserId'=>get_current_user_id(),'Mode'=>'additive-only','Plan'=>$plan];update_option(self::AUDIT_OPTION,$audit,false);$result=(new WordPressRoleInstaller())->install();self::redirect('permissions-installed',count((array)$result['roles']).' UD roller installeret/opdateret additivt. Ingen capabilities blev fjernet.');}
        catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    public static function saveDesignLock(): void
    {
        self::guard();try{$raw=['Enabled'=>isset($_POST['Enabled']),'LockStructure'=>isset($_POST['LockStructure']),'LockDesign'=>isset($_POST['LockDesign']),'ReleasedProperties'=>(string)($_POST['released_properties']??'')];$saved=(new WordPressOptionDesignLockRepository())->save($raw);self::redirect('design-lock-saved','Design Lock policy gemt. '.count((array)$saved['ReleasedProperties']).' properties er frigivet. Legacy editor er stadig ikke låst.');}
        catch(\Throwable $e){self::redirect('error',$e->getMessage());}
    }

    /** @return array<string,list<string>> */
    private static function currentRoleCapabilities(): array
    {
        $slugs=array_keys((new RoleDefinitionCatalog())->definitions());$slugs[]='administrator';$out=[];
        foreach($slugs as $slug){$role=get_role($slug);if($role===null){continue;}$caps=[];foreach((array)$role->capabilities as $cap=>$granted){if($granted){$caps[]=(string)$cap;}}sort($caps,SORT_STRING);$out[$slug]=$caps;}return $out;
    }
    private static function checkbox(string $name,string $label,bool $checked,bool $enabled): void{echo '<label class="h18-ud-permission-check"><input type="checkbox" name="'.esc_attr($name).'" value="1"'.checked($checked,true,false).($enabled?'':' disabled').'> '.esc_html($label).'</label>';}
    private static function guard(): void{if(!current_user_can('manage_options')){wp_die(esc_html__('Kun administratorer kan ændre permissions.','hangar18-manager'));}check_admin_referer(self::NONCE_ACTION);}
    private static function redirect(string $status,string $message): void{wp_safe_redirect(add_query_arg(['page'=>IntegrationAdminBootstrap::PAGE_SLUG,'ud_status'=>$status,'ud_message'=>mb_substr($message,0,700)],admin_url('admin.php')));exit;}
}
