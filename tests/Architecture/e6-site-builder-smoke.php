<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Contracts\MenuRepository;
use Hangar18\UltimateDesigner\Contracts\SiteTemplateRepository;
use Hangar18\UltimateDesigner\Contracts\TemplateAssignmentRepository;
use Hangar18\UltimateDesigner\Schema\PageSchemaValidator;
use Hangar18\UltimateDesigner\SiteBuilder\ClassicMenuRenderer;
use Hangar18\UltimateDesigner\SiteBuilder\FooterTemplateService;
use Hangar18\UltimateDesigner\SiteBuilder\HeaderTemplateService;
use Hangar18\UltimateDesigner\SiteBuilder\MenuService;
use Hangar18\UltimateDesigner\SiteBuilder\MenuTreeValidator;
use Hangar18\UltimateDesigner\SiteBuilder\SiteBuilderPresetCatalog;
use Hangar18\UltimateDesigner\SiteBuilder\SiteTemplateService;
use Hangar18\UltimateDesigner\SiteBuilder\SiteTemplateValidator;
use Hangar18\UltimateDesigner\SiteBuilder\TemplateAssignmentService;
use RuntimeException;

function e6Assert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$siteRepo = new class implements SiteTemplateRepository {
    public array $templates = [];
    public array $assignments = [];
    public function all(): array { return $this->templates; }
    public function get(string $templateId): ?array { return $this->templates[$templateId] ?? null; }
    public function save(array $template): array { $this->templates[$template['Id']] = $template; return $template; }
    public function delete(string $templateId): void { unset($this->templates[$templateId]); }
    public function assignGlobal(string $kind, ?string $templateId): void { if ($templateId === null) unset($this->assignments[$kind]); else $this->assignments[$kind] = $templateId; }
    public function globalAssignment(string $kind): ?string { return $this->assignments[$kind] ?? null; }
};

$siteValidator = new SiteTemplateValidator(new PageSchemaValidator());
$shared = new SiteTemplateService($siteRepo, $siteValidator);
$headers = new HeaderTemplateService($shared);
$footers = new FooterTemplateService($shared);
$sections = [
    ['Key'=>'root','Type'=>'container','LayoutParentKey'=>''],
    ['Key'=>'logo','Type'=>'text','LayoutParentKey'=>'root','Title'=>'Logo'],
];
$header = $headers->create('Global Header', $sections, 'header-main');
$footer = $footers->create('Global Footer', $sections, 'footer-main');
e6Assert($header['Kind'] === 'header' && $footer['Kind'] === 'footer', 'Header/footer template kinds must be preserved.');
$headers->assignGlobal('header-main');
$footers->assignGlobal('footer-main');
e6Assert(($headers->globalHeader()['Id'] ?? '') === 'header-main', 'Global header assignment must resolve.');
e6Assert(($footers->globalFooter()['Id'] ?? '') === 'footer-main', 'Global footer assignment must resolve.');

$menuRepo = new class implements MenuRepository {
    public array $menus = [];
    public function all(): array { return $this->menus; }
    public function get(string $menuId): ?array { return $this->menus[$menuId] ?? null; }
    public function save(array $menu): array { $this->menus[$menu['Id']] = $menu; return $menu; }
    public function delete(string $menuId): void { unset($this->menus[$menuId]); }
};
$menuService = new MenuService($menuRepo, new MenuTreeValidator());
$menu = $menuService->create('Main menu', [
    ['Id'=>'home','Type'=>'url','Label'=>'Hjem','Url'=>'/','Order'=>10],
    ['Id'=>'about','Type'=>'url','Label'=>'Om','Url'=>'/om','Order'=>20],
    ['Id'=>'history','ParentId'=>'about','Type'=>'url','Label'=>'Historie','Url'=>'/om/historie','Order'=>10],
], 'main-menu');
e6Assert($menu['Revision'] === 1 && count($menu['Items']) === 3, 'Menu must save versioned nested items.');
$html = (new ClassicMenuRenderer())->render($menu, '/om');
e6Assert(str_contains($html, 'aria-current="page"'), 'Classic menu must expose active item semantics.');
e6Assert(str_contains($html, 'h18-submenu-toggle'), 'Nested menu must render a keyboard-operable submenu control.');
e6Assert(str_contains($html, 'h18-menu-mobile-toggle'), 'Classic menu must render mobile fallback control.');

$cycleRejected = false;
try {
    $menuService->create('Bad', [
        ['Id'=>'a','ParentId'=>'b','Type'=>'url','Label'=>'A','Url'=>'/a','Order'=>10],
        ['Id'=>'b','ParentId'=>'a','Type'=>'url','Label'=>'B','Url'=>'/b','Order'=>20],
    ], 'bad-menu');
} catch (RuntimeException $exception) { $cycleRejected = true; }
e6Assert($cycleRejected, 'Menu cycles must be rejected.');

$assignmentRepo = new class implements TemplateAssignmentRepository {
    public array $items = [];
    public function all(): array { return array_values($this->items); }
    public function save(array $assignment): array { $this->items[$assignment['Id']] = $assignment; return $assignment; }
    public function delete(string $assignmentId): void { unset($this->items[$assignmentId]); }
};
$assignments = new TemplateAssignmentService($assignmentRepo);
$assignments->assign('tpl-global', 'single', 'global', '*', 10, 'global-single');
$assignments->assign('tpl-vehicle', 'single', 'datatype', 'vehicle', 50, 'vehicle-single');
$resolved = $assignments->resolve('single', ['datatype'=>'vehicle']);
e6Assert(($resolved['TemplateId'] ?? '') === 'tpl-vehicle', 'Higher-priority datatype assignment must win.');
$resolvedOther = $assignments->resolve('single', ['datatype'=>'event']);
e6Assert(($resolvedOther['TemplateId'] ?? '') === 'tpl-global', 'Global assignment must remain fallback.');

$presets = SiteBuilderPresetCatalog::all();
foreach (['transparent-scrolled','sticky-shrink','floating-pill','mega-menu','off-canvas-mobile','fullscreen-overlay','side-rail','bottom-mobile','motion-underline','motion-pill','motion-slide','motion-icon'] as $key) {
    e6Assert(isset($presets[$key]), "Missing E6 preset {$key}.");
}
e6Assert(($presets['transparent-scrolled']['Config']['ReducedMotion'] ?? '') === 'instant', 'Header transition preset must define reduced-motion behavior.');
e6Assert(!empty($presets['off-canvas-mobile']['Config']['FocusTrap']), 'Off-canvas preset must require focus trap.');
e6Assert(!empty($presets['fullscreen-overlay']['Config']['EscapeCloses']), 'Fullscreen preset must close on Escape.');

fwrite(STDOUT, "E6 Site Builder core UD-061..073: PASS\n");
