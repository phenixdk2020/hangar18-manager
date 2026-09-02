from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor, found {count}')
    return text.replace(old, new, 1)

# Address and Contact must be canonical module fields; ModuleRecord intentionally
# discards fields that are not declared in ModuleRegistry.
registry_path = Path('clean/hangar18-manager/src/Modules/ModuleRegistry.php')
registry = registry_path.read_text(encoding='utf-8')
if "'address' => ['label' => 'Adresse'" not in registry:
    old = """                    'location' => ['label' => 'Sted', 'type' => 'text', 'required' => false],
                    'description' => ['label' => 'Beskrivelse', 'type' => 'richtext', 'required' => false],
"""
    new = """                    'location' => ['label' => 'Sted', 'type' => 'text', 'required' => false],
                    'address' => ['label' => 'Adresse', 'type' => 'text', 'required' => false],
                    'contact' => ['label' => 'Kontakt', 'type' => 'text', 'required' => false],
                    'description' => ['label' => 'Beskrivelse', 'type' => 'richtext', 'required' => false],
"""
    registry = replace_once(registry, old, new, 'ModuleRegistry event address/contact')
registry_path.write_text(registry, encoding='utf-8')

# Eventfield must follow the same publish/draft visibility contract as the other
# event detail elements. Drafts remain available inside authorized Designer preview.
renderer_path = Path('clean/hangar18-manager/src/Frontend/Renderer.php')
renderer = renderer_path.read_text(encoding='utf-8')
if "$allowDraft=self::$forceStandaloneCss&&current_user_can('edit_pages');if($record===null||((string)($record['status']??'draft')!=='publish'&&!$allowDraft))" not in renderer:
    old = """            $fieldKey=sanitize_key((string)($props['fieldKey']??'about')); $found=$recordId!==''?ModuleStore::findByRecordId('events',$recordId):null; $record=is_array($found)&&isset($found['record'])&&is_array($found['record'])?$found['record']:null;
            if($record===null){$message=self::$forceStandaloneCss?'Eventfelt · vælg record via ?h18_event=record-id.':'';return '<div id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-field" style="'.esc_attr($style.$borderStyle.$spacingStyle).'">'.esc_html($message).'</div>';}
"""
    new = """            $fieldKey=sanitize_key((string)($props['fieldKey']??'about')); $found=$recordId!==''?ModuleStore::findByRecordId('events',$recordId):null; $record=is_array($found)&&isset($found['record'])&&is_array($found['record'])?$found['record']:null;
            $allowDraft=self::$forceStandaloneCss&&current_user_can('edit_pages');if($record===null||((string)($record['status']??'draft')!=='publish'&&!$allowDraft)){$message=self::$forceStandaloneCss?'Eventfelt · vælg record via ?h18_event=record-id.':'';return '<div id="h18-clean-'.$id.'" class="h18-clean-front-node h18-clean-front-event-field" style="'.esc_attr($style.$borderStyle.$spacingStyle).'">'.esc_html($message).'</div>';}
"""
    renderer = replace_once(renderer, old, new, 'Renderer eventfield publish contract')
renderer_path.write_text(renderer, encoding='utf-8')
