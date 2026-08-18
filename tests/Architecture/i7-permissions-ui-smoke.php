<?php

declare(strict_types=1);

require_once dirname(__DIR__,2).'/src/Autoload.php';
\Hangar18\UltimateDesigner\Autoload::register();

use Hangar18\UltimateDesigner\Permissions\CapabilityCatalog;
use Hangar18\UltimateDesigner\Permissions\DesignLockGuard;
use Hangar18\UltimateDesigner\Permissions\DesignLockSettings;
use Hangar18\UltimateDesigner\Permissions\RoleInstallationPlanner;
use RuntimeException;

function i7Assert(bool $condition,string $message): void{if(!$condition){throw new RuntimeException($message);}}

$current=[
    'hangar18_designer'=>['read',CapabilityCatalog::EDIT_CONTENT],
    'administrator'=>['read','edit_pages'],
];
$plan=(new RoleInstallationPlanner())->plan($current);
i7Assert($plan['Mode']==='additive-only','Role migration must be additive-only.');
i7Assert((int)$plan['Removals']===0,'Role migration preview must never remove capabilities.');
i7Assert(($plan['Roles']['hangar18_designer']['Create']??true)===false,'Existing designer role must be detected.');
i7Assert(in_array(CapabilityCatalog::MANAGE_DESIGN,$plan['Roles']['hangar18_designer']['Add'],true),'Designer preview must include missing design capability.');
i7Assert(($plan['Roles']['hangar18_event_manager']['Create']??false)===true,'Missing domain role must be planned for creation.');
i7Assert(in_array(CapabilityCatalog::MANAGE_SETTINGS,$plan['Administrator']['Add'],true),'Administrator preview must include missing UD capabilities.');
foreach($plan['Roles'] as $role){i7Assert(($role['Remove']??['unexpected'])===[],'No role may contain removal plan.');}

$settings=(new DesignLockSettings())->normalize([
    'Enabled'=>true,'LockStructure'=>true,'LockDesign'=>true,
    'ReleasedProperties'=>"Content\nTitle\nAltText\nContent\n<script>\nBad Property",
]);
i7Assert($settings['Enabled']===true&&$settings['LockStructure']===true&&$settings['LockDesign']===true,'Design Lock booleans must normalize.');
i7Assert($settings['ReleasedProperties']===['AltText','Content','Title'],'Released properties must be safe, unique and sorted.');
$released=(new DesignLockSettings())->releasedMap($settings);
$before=['Key'=>'x','Type'=>'text','LayoutParentKey'=>'','Content'=>'A','CustomTextColor'=>'#111111'];
$after=['Key'=>'x','Type'=>'text','LayoutParentKey'=>'new-parent','Content'=>'B','CustomTextColor'=>'#ffffff'];
$violations=(new DesignLockGuard())->violations($before,$after,['Structure'=>true,'Design'=>true],$released);
i7Assert(!in_array('design:Content',$violations,true),'Released content property must remain editable.');
i7Assert(in_array('structure:LayoutParentKey',$violations,true),'Structure lock must block parent change.');
i7Assert(in_array('design:CustomTextColor',$violations,true),'Design lock must block color change.');

fwrite(STDOUT,"I7 Permissions preview + Design Lock: PASS\n");
