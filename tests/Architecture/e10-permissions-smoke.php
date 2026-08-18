<?php

declare(strict_types=1);

require_once dirname(__DIR__, 2) . '/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Contracts\SecurityGate;
use Hangar18\UltimateDesigner\Permissions\AuthorizationService;
use Hangar18\UltimateDesigner\Permissions\CapabilityCatalog;
use Hangar18\UltimateDesigner\Permissions\ComponentEditableInputPolicy;
use Hangar18\UltimateDesigner\Permissions\DesignLockGuard;
use Hangar18\UltimateDesigner\Permissions\DomainScopePolicy;
use Hangar18\UltimateDesigner\Permissions\RoleDefinitionCatalog;
use RuntimeException;

function e10Assert(bool $condition, string $message): void
{
    if (!$condition) { throw new RuntimeException($message); }
}

$caps = new CapabilityCatalog();
e10Assert(count($caps->all()) >= 11, 'Capability matrix must expose named plugin capabilities.');
e10Assert($caps->forAction('component.update') === CapabilityCatalog::MANAGE_COMPONENTS, 'Component writes must resolve to named component capability.');
e10Assert($caps->forAction('publish') === CapabilityCatalog::PUBLISH, 'Publish must use a dedicated capability.');

$roles = (new RoleDefinitionCatalog())->definitions();
e10Assert(isset($roles['hangar18_designer'],$roles['hangar18_editor'],$roles['hangar18_event_manager'],$roles['hangar18_gallery_manager']), 'Required role recipes must exist.');
e10Assert(in_array(CapabilityCatalog::MANAGE_DESIGN,$roles['hangar18_designer']['Capabilities'],true), 'Designer must be able to manage design.');
e10Assert(!in_array(CapabilityCatalog::MANAGE_DESIGN,$roles['hangar18_editor']['Capabilities'],true), 'Content editor must not get design capability.');

$domain = new DomainScopePolicy();
e10Assert($domain->canRoleAccess($roles['hangar18_event_manager'],'event'), 'Event role must access Event data.');
e10Assert(!$domain->canRoleAccess($roles['hangar18_event_manager'],'gallery'), 'Event role must not access Gallery data.');
e10Assert($domain->canRoleAccess($roles['hangar18_designer'],'vehicle'), 'Wildcard role must access generic data domains.');

$component = ['Inputs'=>[
    ['SectionKey'=>'card-1','Field'=>'Title'],
    ['SectionKey'=>'card-1','Field'=>'MediaId'],
]];
$inputPolicy = new ComponentEditableInputPolicy();
$filtered = $inputPolicy->filter([
    'card-1.Title'=>'Ny titel',
    'card-1.MediaId'=>123,
    'card-1.BackgroundColor'=>'#000000',
], $component);
e10Assert(array_keys($filtered) === ['card-1.MediaId','card-1.Title'], 'Only explicitly released component inputs may be overridden.');

$before = ['Key'=>'card-1','Type'=>'card','LayoutParentKey'=>'','Title'=>'A','CustomBackgroundColor'=>'#fff','DesktopAlignment'=>'Left'];
$afterContent = $before; $afterContent['Title'] = 'B';
$afterDesign = $before; $afterDesign['CustomBackgroundColor'] = '#000';
$afterStructure = $before; $afterStructure['LayoutParentKey'] = 'container-1';
$guard = new DesignLockGuard();
e10Assert($guard->violations($before,$afterContent,['Structure'=>true,'Design'=>true],['Title'=>true]) === [], 'Released content property must remain editable under design lock.');
e10Assert($guard->violations($before,$afterDesign,['Structure'=>true,'Design'=>true],[]) === ['design:CustomBackgroundColor'], 'Locked design property change must be rejected.');
e10Assert($guard->violations($before,$afterStructure,['Structure'=>true,'Design'=>true],[]) === ['structure:LayoutParentKey'], 'Locked structure move must be rejected.');

$gate = new class implements SecurityGate {
    public array $grants = [];
    public function can(string $capability): bool { return !empty($this->grants[$capability]); }
    public function validateWriteToken(string $action, string $token): bool { return $token === 'ok'; }
};
$gate->grants[CapabilityCatalog::MANAGE_EVENTS] = true;
$authorization = new AuthorizationService($gate);
e10Assert($authorization->can('event.manage','event',$roles['hangar18_event_manager']), 'Named capability plus domain scope must authorize matching event operation.');
e10Assert(!$authorization->can('event.manage','gallery',$roles['hangar18_event_manager']), 'Domain scope must deny cross-domain operation even when capability is granted.');

e10Assert($gate->validateWriteToken('event.save','ok'), 'Security gate write-token contract remains usable with named capabilities.');

fwrite(STDOUT, "E10 Permissions core UD-094..097: PASS\n");
