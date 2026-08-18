<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();
require_once __DIR__ . '/InMemoryRevisionRepository.php';
require_once __DIR__ . '/InMemoryStagingRepository.php';
require_once __DIR__ . '/InMemorySiteBuilderRepositories.php';

use Hangar18\UltimateDesigner\Core\Version;
use Hangar18\UltimateDesigner\Interaction\FormDefinitionValidator;
use Hangar18\UltimateDesigner\Interaction\FormRenderer;
use Hangar18\UltimateDesigner\Portability\PagePackageService;
use Hangar18\UltimateDesigner\QA\ReleaseReadiness;
use Hangar18\UltimateDesigner\Quality\SideHealthService;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use Hangar18\UltimateDesigner\SiteBuilder\ClassicMenuRenderer;
use Hangar18\UltimateDesigner\SiteBuilder\FooterTemplateService;
use Hangar18\UltimateDesigner\SiteBuilder\HeaderTemplateService;
use Hangar18\UltimateDesigner\SiteBuilder\MenuService;
use Hangar18\UltimateDesigner\SiteBuilder\MenuTreeValidator;
use Hangar18\UltimateDesigner\SiteBuilder\SiteTemplateService;
use Hangar18\UltimateDesigner\SiteBuilder\SiteTemplateValidator;
use Hangar18\UltimateDesigner\Workflow\PreviewService;
use Hangar18\UltimateDesigner\Workflow\PreviewTokenService;
use Hangar18\UltimateDesigner\Workflow\RevisionService;
use Hangar18\UltimateDesigner\Workflow\StagingService;
use RuntimeException;

function e14E2eAssert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

// UD-118 MVP E2E: create -> design/responsive -> validate -> save -> preview -> publish -> restore/export.
$page = [
    'Version'=>Version::PAGE_SCHEMA,
    'PageSlug'=>'e2e-page',
    'PageTitle'=>'E2E side',
    'ContentVersion'=>1,
    'DataContextType'=>'',
    'DataContextEntryId'=>0,
    'Sections'=>[
        ['Key'=>'title','Type'=>'heading','HeadingTag'=>'h1','LayoutParentKey'=>'','Title'=>'E2E side'],
        ['Key'=>'intro','Type'=>'text','LayoutParentKey'=>'','Content'=>'Introduktion','MobileFontSizePx'=>16],
        ['Key'=>'photo','Type'=>'image','LayoutParentKey'=>'','MediaId'=>100,'AltText'=>'Historisk køretøj'],
        ['Key'=>'dynamic','Type'=>'query_list','LayoutParentKey'=>'','QueryListType'=>'event','QueryListLimit'=>3],
    ],
];
$schema = new PageSchemaValidator();
e14E2eAssert($schema->validate($page) === [], 'MVP page state must pass canonical schema.');

$revisionRepo = new InMemoryRevisionRepository();
$revisions = new RevisionService($revisionRepo);
$resource='page:e2e-page';
$revisions->autosave($resource,$page,7);
e14E2eAssert(count($revisions->history($resource))===0, 'Autosave must not create permanent revision.');
$manual = $revisions->save($resource,$page,7,'E2E manual save');
e14E2eAssert((int) ($manual['Sequence'] ?? 0)===1, 'Manual save must create permanent revision.');

$stagingRepo = new InMemoryStagingRepository();
$staging = new StagingService($stagingRepo,$revisionRepo);
$staging->saveWorking($resource,$page);
$tokens = new PreviewTokenService(str_repeat('e2e-secret-',4));
$previewToken = $tokens->issue($resource,'mobile',600);
$preview = (new PreviewService($tokens,$stagingRepo))->resolve($previewToken['token']);
e14E2eAssert(is_array($preview) && ($preview['device'] ?? '')==='mobile' && ($preview['state']['PageSlug'] ?? '')==='e2e-page', 'Unpublished working page must preview on requested device.');
$published = $staging->publish($resource,7,'E2E publish');
e14E2eAssert(($published['State']['PageSlug'] ?? '')==='e2e-page', 'Working state must publish atomically.');

$health = (new SideHealthService())->analyze($page,[
    'Title'=>'E2E side',
    'MetaDescription'=>'E2E side med gyldig metadata og responsive komponenter.',
    'CanonicalUrl'=>'https://example.test/e2e-page/',
    'Index'=>true,'Follow'=>true,
    'SocialTitle'=>'E2E side','SocialDescription'=>'E2E beskrivelse','SocialImageMediaId'=>100,
],[100=>120000]);
e14E2eAssert((int) $health['HardFailureCount']===0, 'MVP published fixture must have no hard Side Health failures.');

$package = new PagePackageService($schema);
$globalStyles=['Colors'=>['Primary'=>'#30382a'],'Typography'=>['Body'=>'Global']];
$exported=$package->export($page,$globalStyles);
$roundtrip=$package->import($exported);
e14E2eAssert($roundtrip['Page']===$page && $roundtrip['GlobalStyles']===$globalStyles, 'MVP export must re-import identically.');
$restored=$revisions->restore($resource,(string) $manual['Id'],8,'E2E restore');
e14E2eAssert(($restored['State']['PageSlug'] ?? '')==='e2e-page' && count($revisions->history($resource))===2, 'Restore must append history and recover saved page.');

// UD-119 v1 E2E: Site Builder + menu + interaction + workflow/quality/portability coexist.
$templateRepo=new InMemorySiteTemplateRepository();
$templateService=new SiteTemplateService($templateRepo,new SiteTemplateValidator($schema));
$headers=new HeaderTemplateService($templateService);
$footers=new FooterTemplateService($templateService);
$header=$headers->create('Global header',[
    ['Key'=>'header-root','Type'=>'container','LayoutParentKey'=>''],
    ['Key'=>'header-title','Type'=>'text','LayoutParentKey'=>'header-root','Content'=>'Hangar18'],
],'header-main');
$footer=$footers->create('Global footer',[
    ['Key'=>'footer-text','Type'=>'text','LayoutParentKey'=>'','Content'=>'Kontakt'],
],'footer-main');
$headers->assignGlobal((string) $header['Id']);
$footers->assignGlobal((string) $footer['Id']);
e14E2eAssert(($headers->globalHeader()['Id'] ?? '')==='header-main' && ($footers->globalFooter()['Id'] ?? '')==='footer-main', 'Header/footer must use shared element tree and global assignment.');

$menuService=new MenuService(new InMemoryMenuRepository(),new MenuTreeValidator());
$menu=$menuService->create('Hovedmenu',[
    ['Id'=>'home','ParentId'=>'','Order'=>10,'Type'=>'url','Label'=>'Hjem','Url'=>'/'],
    ['Id'=>'about','ParentId'=>'','Order'=>20,'Type'=>'url','Label'=>'Om','Url'=>'/om/'],
    ['Id'=>'contact','ParentId'=>'about','Order'=>10,'Type'=>'url','Label'=>'Kontakt','Url'=>'/kontakt/'],
],'main');
$menuHtml=(new ClassicMenuRenderer())->render($menu,'/om/');
e14E2eAssert(strpos($menuHtml,'aria-current="page"')!==false && strpos($menuHtml,'h18-submenu-toggle')!==false, 'Site Builder menu must render active state and accessible submenu controls.');

$form=[
    'SchemaVersion'=>'1.0','Id'=>'e2e-form','SubmitLabel'=>'Send','Fields'=>[
        ['Key'=>'email','Type'=>'email','Label'=>'E-mail','Validation'=>['Required'=>true]],
    ],'Actions'=>[['Type'=>'redirect','Config'=>['Url'=>'/tak']]],
];
$formHtml=(new FormRenderer(new FormDefinitionValidator()))->render($form,'/submit');
e14E2eAssert(strpos($formHtml,'aria-required="true"')!==false && strpos($formHtml,'aria-live="polite"')!==false, 'v1 E2E form must render accessible validation/status semantics.');

// Release readiness must remain false until real/manual evidence is supplied.
$readiness=new ReleaseReadiness();
$automated=[
    'php-8.0'=>true,'php-8.2'=>true,'php-8.3'=>true,'browser-engine-matrix'=>true,
    'security-audit'=>true,'performance-budget'=>true,'migration-rollback'=>true,'mvp-e2e'=>true,'v1-e2e'=>true,
];
$manual=$readiness->requiredManualEvidence();
$pending=$readiness->evaluate($automated,$manual);
e14E2eAssert($pending['Ready']===false && count($pending['PendingManual'])>0, 'Automated E2E must not falsely satisfy manual/live release evidence.');
foreach($manual as $key=>$_){$manual[$key]=true;}
$ready=$readiness->evaluate($automated,$manual);
e14E2eAssert($ready['Ready']===true, 'Release gate must become ready only after automated and manual evidence are all true.');

fwrite(STDOUT,"E14 MVP/v1 end-to-end UD-118/119 + release gate: PASS\n");
