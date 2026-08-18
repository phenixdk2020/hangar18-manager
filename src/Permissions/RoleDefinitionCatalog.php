<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Permissions;

/** UD-094/097 role recipes; installation is explicit and not run during this passive slice. */
final class RoleDefinitionCatalog
{
    /** @return array<string,array{Label:string,Capabilities:list<string>,Domains:list<string>}> */
    public function definitions(): array
    {
        $c = new CapabilityCatalog();
        return [
            'hangar18_administrator'=>[
                'Label'=>'Hangar18 Administrator',
                'Capabilities'=>$c->all(),
                'Domains'=>['*'],
            ],
            'hangar18_designer'=>[
                'Label'=>'Hangar18 Designer',
                'Capabilities'=>[
                    CapabilityCatalog::MANAGE_DESIGN,CapabilityCatalog::MANAGE_COMPONENTS,
                    CapabilityCatalog::MANAGE_TEMPLATES,CapabilityCatalog::EDIT_CONTENT,
                    CapabilityCatalog::MANAGE_ASSETS,
                ],
                'Domains'=>['*'],
            ],
            'hangar18_editor'=>[
                'Label'=>'Hangar18 Editor',
                'Capabilities'=>[CapabilityCatalog::EDIT_CONTENT,CapabilityCatalog::MANAGE_ASSETS],
                'Domains'=>['*'],
            ],
            'hangar18_event_manager'=>[
                'Label'=>'Hangar18 Eventansvarlig',
                'Capabilities'=>[CapabilityCatalog::EDIT_CONTENT,CapabilityCatalog::MANAGE_ASSETS,CapabilityCatalog::MANAGE_EVENTS],
                'Domains'=>['event'],
            ],
            'hangar18_gallery_manager'=>[
                'Label'=>'Hangar18 Gallery Manager',
                'Capabilities'=>[CapabilityCatalog::EDIT_CONTENT,CapabilityCatalog::MANAGE_ASSETS,CapabilityCatalog::MANAGE_GALLERIES],
                'Domains'=>['gallery'],
            ],
        ];
    }
}
