<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Admin;

use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionAiProposalRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionAiSettingsRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionArtifactRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionAssetMetadataRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionAcceptanceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionConversionWorkspaceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionCutoverPreflightRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionDesignLockRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionManualQaEvidenceRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionMenuRepository;
use Hangar18\UltimateDesigner\Infrastructure\WordPress\WordPressOptionSiteTemplateRepository;
use Hangar18\UltimateDesigner\Migration\ConversionAcceptanceValidator;
use Hangar18\UltimateDesigner\Permissions\CapabilityCatalog;
use Hangar18\UltimateDesigner\QA\ManualEvidenceValidator;
use Hangar18\UltimateDesigner\QA\ReleaseReadiness;

/** Safe admin-only bridge from the legacy plugin shell to extracted Ultimate Designer services. */
final class IntegrationAdminBootstrap
{
    public const PAGE_SLUG='hangar18-ultimate-designer';
    private static bool $registered=false;

    public static function register(): void
    {
        if(self::$registered){return;}
        self::$registered=true;
        add_action('admin_menu',[self::class,'registerMenu'],30);
        LegacyShellShadowAdminController::register();
        SiteTemplateAdminController::register();
        MenuAdminController::register();
        MenuPageChooserAdminController::register();
        SideHealthAdminController::register();
        EditorLayoutToolsAdminController::register();
        EditorElementLibraryAdminController::register();
        BackupRestoreAdminController::register();
        AssetManagerAdminController::register();
        PortabilityAdminController::register();
        PermissionsAdminController::register();
        AiAdminController::register();
        QaDashboardAdminController::register();
        ConversionAdminController::register();
        CutoverPreflightAdminController::register();
    }

    public static function registerMenu(): void
    {
        if(!class_exists('Hangar18_Manager')){return;}
        add_submenu_page(\Hangar18_Manager::MENU_SLUG,'Ultimate Designer','Ultimate Designer','edit_pages',self::PAGE_SLUG,[self::class,'render']);
    }

    public static function render(): void
    {
        if(!current_user_can('edit_pages')){wp_die(esc_html__('Du har ikke rettigheder til denne side.','hangar18-manager'));}
        $templates=new WordPressOptionSiteTemplateRepository();$menus=new WordPressOptionMenuRepository();$assets=new WordPressOptionAssetMetadataRepository();$readiness=new ReleaseReadiness();$workspace=new WordPressOptionArtifactRepository();$designLock=(new WordPressOptionDesignLockRepository())->get();$aiSettings=(new WordPressOptionAiSettingsRepository())->get();$aiProposals=(new WordPressOptionAiProposalRepository())->all();$qaRecords=(new WordPressOptionManualQaEvidenceRepository())->all();$conversionWorkspace=(new WordPressOptionConversionWorkspaceRepository())->all();$conversionAcceptance=(new WordPressOptionConversionAcceptanceRepository())->all();$cutoverPreflights=(new WordPressOptionCutoverPreflightRepository())->all();
        $allTemplates=$templates->all();$headerCount=0;$footerCount=0;foreach($allTemplates as $template){if(($template['Kind']??'')==='header'){$headerCount++;}elseif(($template['Kind']??'')==='footer'){$footerCount++;}}
        $manual=(new ManualEvidenceValidator())->statusMap($qaRecords);$manualPending=array_keys(array_filter($manual,static fn(bool $passed):bool=>!$passed));$manualPassed=count($manual)-count($manualPending);
        $capabilities=(new CapabilityCatalog())->all();$currentCapabilities=[];foreach($capabilities as $capability){if(current_user_can($capability)){$currentCapabilities[]=$capability;}}
        $assetCount=count($assets->all());$menuCount=count($menus->all());$globalHeader=$templates->globalAssignment('header');$globalFooter=$templates->globalAssignment('footer');$workspaceCount=0;foreach($workspace->snapshot() as $items){$workspaceCount+=count($items);}$pendingAi=count(array_filter($aiProposals,static fn(array $p): bool => ($p['Status']??'')==='pending'));
        $acceptanceValidator=new ConversionAcceptanceValidator();$acceptedShadowCount=0;foreach($conversionWorkspace as $slug=>$record){if($acceptanceValidator->isAccepted($conversionAcceptance[$slug]??null,(string)($record['SourceHash']??''))){$acceptedShadowCount++;}}
        echo '<div class="wrap h18-admin h18-ud-integration-admin"><h1>Ultimate Designer</h1><p class="description">Integrationsoverblik i shadow mode. Den nuværende Hangar18-frontend og Vehicle/Event/Gallery er stadig autoritative.</p><div class="notice notice-info inline"><p><strong>Ingen sidekonvertering:</strong> Denne skærm aktiverer ikke nye renderere, ændrer ikke URLs og overskriver ikke eksisterende sider.</p></div>';
        self::renderStatusNotice();echo '<div class="h18-ud-status-grid">';
        self::card('Site Builder',sprintf('%d Header · %d Footer · %d Menu',$headerCount,$footerCount,$menuCount),'Header/Footer og menu-data kan redigeres visuelt i shadow mode; frontend-cutover er fortsat deaktiveret.');
        self::card('Menuvalg','Tilvalg/fravalg pr. side','Sider eksisterer uafhængigt af menuen. Kun markerede sider bliver menupunkter.');
        self::card('Editor layout+','Auto-kasser · Tabel','Auto-kasser bruger den eksisterende Grid/Container-motor; Tabel bruger det sanitiserede HTML-element.');
        self::card('Elementbibliotek','Søgning · Kategorier · Favoritter','Admin-only palette UX oven på eksisterende drag/drop. Favoritter er browser-lokale og ændrer ikke side-schema.');
        self::card('Global assignment (shadow)','Header: '.($globalHeader?:'ingen').' · Footer: '.($globalFooter?:'ingen'),'Assignments påvirker ikke legacy header/footer endnu.');
        self::card('Asset metadata',(string)$assetCount.' registreret','Metadata-lag oven på native WordPress Media IDs.');
        self::card('Portability Workspace',(string)$workspaceCount.' artifact(s)','I6-imports går kun til isoleret workspace med dry-run og backup.');
        self::card('Permissions',sprintf('%d/%d capabilities på aktuel bruger',count($currentCapabilities),count($capabilities)),'I7 kan installere navngivne roller additivt; edit_pages fjernes ikke.');
        self::card('Design Lock',!empty($designLock['Enabled'])?'Policy aktiv (shadow)':'Policy inaktiv','Policy håndhæves først i den nye runtime efter kontrolleret cutover.');
        self::card('AI forslag',(!empty($aiSettings['Enabled'])?'Aktiv':'Inaktiv').' · '.$pendingAi.' pending','Provider-neutral I8 sandbox. Accept giver kun Apply/Undo-plan; ingen page-write.');
        self::card('Manual QA',$manualPassed.'/'.count($manual).' PASS',count($manualPending).' manuelle gates blokerer fortsat public I10 cutover. Automatisk preflight kan ikke godkende dem.');
        self::card('I10 conversion',count($conversionWorkspace).' shadow · '.$acceptedShadowCount.' accepted','Acceptance er manuelt/hash-bundet. Ingen activate/cutover-handler er registreret i denne fase.');
        self::card('I10 signed preflight',count($cutoverPreflights).' snapshot(s)','Preflight er source-drift/hash-bundet og altid non-executable; den giver ingen public mutation.');
        self::card('Side Health','Live panel på Sider','I4 analyserer den aktuelle editor-state read-only og linker issues til konkrete elementer.');
        self::card('Manual release gates',(string)count($manualPending).' pending','Offentlig konvertering forbliver blokeret indtil de manuelle/live gates er gennemført.');echo '</div>';
        LegacyShellShadowAdminController::renderPanel();SiteTemplateAdminController::renderPanel();MenuAdminController::renderPanel();BackupRestoreAdminController::renderPanel();AssetManagerAdminController::renderPanel();PortabilityAdminController::renderPanel();PermissionsAdminController::renderPanel();AiAdminController::renderPanel();QaDashboardAdminController::renderPanel();ConversionAdminController::renderPanel();CutoverPreflightAdminController::renderPanel();
        echo '<h2>Integration backlog</h2><table class="widefat striped h18-ud-backlog"><thead><tr><th>Fase</th><th>Status</th><th>Næste leverance</th></tr></thead><tbody>';
        self::backlogRow('I1','Færdig','Admin integration og overblik.');self::backlogRow('I2','Færdig','Visual Header/Footer Builder i shadow mode.');self::backlogRow('I2A','Aktiv · read-only baseline','Legacy Header/Footer source-hash og shell-markører er koblet til Designer-overblikket uden writes; næste trin er kontrolleret shadow-import.');self::backlogRow('I3','Færdig','Menu UI v2 med presets, nested editor, keyboard-preview og eksplicit side-tilvalg/fravalg.');self::backlogRow('I4','Færdig','Live Side Health i eksisterende sideeditor med element-links.');self::backlogRow('UX-1','Færdig','Auto-kasser med automatisk lige bredde samt visuelt Tabel-element i Sider-editoren.');self::backlogRow('UX-2','Færdig','Søgbart elementbibliotek med kategorifiltre og browser-lokale favoritter; eksisterende drag/drop genbruges.');self::backlogRow('I5','Færdig','Asset Manager: collections/tags/usage/focal point/duplicates/derivatives.');self::backlogRow('I6','Færdig','Import/Export UI med dry-run, signeret plan, isoleret workspace og restore-point.');self::backlogRow('I7','Færdig','Permissions/Design Lock UI og additive role-installation med migration preview.');self::backlogRow('I8','Færdig','Provider-neutral AI settings, pending forslag og signeret accept til Apply/Undo-plan.');self::backlogRow('I9','Færdig','Manual QA evidence dashboard og copy-only rollback preflight; evidens udføres separat.');self::backlogRow('I10','Aktiv · signed preflight','Conversion plan + shadow-copy + hash-bundet manual acceptance + source-drift preflight. Public cutover er fortsat låst.');self::backlogRow('B1','Draft-kandidat','Sidebackup kan erstattes på original med automatisk sikkerhedsbackup eller oprettes som separat draft-kopi.');
        echo '</tbody></table><h2>Manuelle gates før public I10 cutover</h2><ul class="ul-disc">';foreach($manualPending as $item){echo '<li><code>'.esc_html($item).'</code></li>';}echo '</ul></div>';
    }
    private static function renderStatusNotice(): void{$status=isset($_GET['ud_status'])?sanitize_key((string)wp_unslash($_GET['ud_status'])):'';$message=isset($_GET['ud_message'])?sanitize_text_field((string)wp_unslash($_GET['ud_message'])):'';if($status===''||$message===''){return;}$class=$status==='error'?'notice notice-error inline':'notice notice-success inline';echo '<div class="'.esc_attr($class).'"><p>'.esc_html($message).'</p></div>';}
    private static function card(string $title,string $value,string $description): void{echo '<section class="h18-ud-status-card"><h3>'.esc_html($title).'</h3><strong>'.esc_html($value).'</strong><p>'.esc_html($description).'</p></section>';}
    private static function backlogRow(string $phase,string $status,string $description): void{echo '<tr><td><strong>'.esc_html($phase).'</strong></td><td>'.esc_html($status).'</td><td>'.esc_html($description).'</td></tr>';}
}
