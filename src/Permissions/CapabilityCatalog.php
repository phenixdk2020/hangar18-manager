<?php

declare(strict_types=1);

namespace Hangar18\UltimateDesigner\Permissions;

use RuntimeException;

/** UD-094 named least-privilege capability matrix for Ultimate Designer features. */
final class CapabilityCatalog
{
    public const MANAGE_SETTINGS = 'hangar18_manage_settings';
    public const MANAGE_DESIGN = 'hangar18_manage_design';
    public const MANAGE_COMPONENTS = 'hangar18_manage_components';
    public const MANAGE_TEMPLATES = 'hangar18_manage_templates';
    public const MANAGE_DATA_SCHEMAS = 'hangar18_manage_data_schemas';
    public const EDIT_CONTENT = 'hangar18_edit_content';
    public const MANAGE_ASSETS = 'hangar18_manage_assets';
    public const PUBLISH = 'hangar18_publish';
    public const USE_CUSTOM_CODE = 'hangar18_use_custom_code';
    public const MANAGE_EVENTS = 'hangar18_manage_events';
    public const MANAGE_GALLERIES = 'hangar18_manage_galleries';

    /** @return list<string> */
    public function all(): array
    {
        return [
            self::MANAGE_SETTINGS,self::MANAGE_DESIGN,self::MANAGE_COMPONENTS,self::MANAGE_TEMPLATES,
            self::MANAGE_DATA_SCHEMAS,self::EDIT_CONTENT,self::MANAGE_ASSETS,self::PUBLISH,
            self::USE_CUSTOM_CODE,self::MANAGE_EVENTS,self::MANAGE_GALLERIES,
        ];
    }

    public function forAction(string $action): string
    {
        $map = [
            'settings.read'=>self::MANAGE_SETTINGS,'settings.write'=>self::MANAGE_SETTINGS,
            'design.edit'=>self::MANAGE_DESIGN,'design.tokens'=>self::MANAGE_DESIGN,
            'component.create'=>self::MANAGE_COMPONENTS,'component.update'=>self::MANAGE_COMPONENTS,'component.delete'=>self::MANAGE_COMPONENTS,
            'template.create'=>self::MANAGE_TEMPLATES,'template.update'=>self::MANAGE_TEMPLATES,'template.assign'=>self::MANAGE_TEMPLATES,
            'schema.create'=>self::MANAGE_DATA_SCHEMAS,'schema.update'=>self::MANAGE_DATA_SCHEMAS,'schema.delete'=>self::MANAGE_DATA_SCHEMAS,
            'content.edit'=>self::EDIT_CONTENT,'asset.manage'=>self::MANAGE_ASSETS,
            'publish'=>self::PUBLISH,'custom_code.edit'=>self::USE_CUSTOM_CODE,
            'event.manage'=>self::MANAGE_EVENTS,'gallery.manage'=>self::MANAGE_GALLERIES,
        ];
        $action = strtolower(trim($action));
        if (!isset($map[$action])) { throw new RuntimeException('Unknown protected action: ' . $action); }
        return $map[$action];
    }
}
