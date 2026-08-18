<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Permissions;

/** Pure preview of the additive WordPress role installation performed by I7. */
final class RoleInstallationPlanner
{
    private RoleDefinitionCatalog $catalog;
    public function __construct(?RoleDefinitionCatalog $catalog=null){$this->catalog=$catalog??new RoleDefinitionCatalog();}

    /**
     * @param array<string,list<string>> $currentCapabilities role slug => granted capabilities
     * @return array<string,mixed>
     */
    public function plan(array $currentCapabilities): array
    {
        $roles=[];$totalAdd=0;
        foreach($this->catalog->definitions() as $slug=>$definition){$current=array_values(array_unique(array_map('strval',$currentCapabilities[$slug]??[])));sort($current,SORT_STRING);$required=array_values(array_unique(array_merge(['read'],$definition['Capabilities'])));sort($required,SORT_STRING);$add=array_values(array_diff($required,$current));sort($add,SORT_STRING);$totalAdd+=count($add);$roles[$slug]=['Label'=>$definition['Label'],'Create'=>!array_key_exists($slug,$currentCapabilities),'Current'=>$current,'Required'=>$required,'Add'=>$add,'Remove'=>[],'Domains'=>$definition['Domains']];}
        $adminCurrent=array_values(array_unique(array_map('strval',$currentCapabilities['administrator']??[])));sort($adminCurrent,SORT_STRING);$adminRequired=(new CapabilityCatalog())->all();sort($adminRequired,SORT_STRING);$adminAdd=array_values(array_diff($adminRequired,$adminCurrent));sort($adminAdd,SORT_STRING);$totalAdd+=count($adminAdd);
        return ['Mode'=>'additive-only','Roles'=>$roles,'Administrator'=>['Add'=>$adminAdd,'Remove'=>[],'Domains'=>['*']],'TotalCapabilitiesToAdd'=>$totalAdd,'Removals'=>0];
    }
}
