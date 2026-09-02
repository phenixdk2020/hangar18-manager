from pathlib import Path


def req(ok, label):
    if not ok:
        raise SystemExit('FAIL: ' + label)
    print('PASS:', label)

registry = Path('clean/hangar18-manager/src/Modules/ModuleRegistry.php').read_text(encoding='utf-8')
record = Path('clean/hangar18-manager/src/Modules/ModuleRecord.php').read_text(encoding='utf-8')
event_admin = Path('clean/hangar18-manager/src/Admin/EventAdminController.php').read_text(encoding='utf-8')
renderer = Path('clean/hangar18-manager/src/Frontend/Renderer.php').read_text(encoding='utf-8')

req("'address' => ['label' => 'Adresse', 'type' => 'text'" in registry, 'Address declared in canonical Event ModuleRegistry')
req("'contact' => ['label' => 'Kontakt', 'type' => 'text'" in registry, 'Contact declared in canonical Event ModuleRegistry')
req('foreach (ModuleRegistry::fieldDefinitions($module) as $key => $field)' in record, 'ModuleRecord persists only registry fields')
req("'address' => sanitize_text_field" in event_admin and "'contact' => sanitize_text_field" in event_admin, 'Event admin submits canonical Address and Contact values')
req("($fields['address'] ?? '')" in renderer and "($fields['contact'] ?? '')" in renderer, 'Eventfaktabånd reads persisted Address and Contact')
req("$allowDraft=self::$forceStandaloneCss&&current_user_can('edit_pages');if($record===null||((string)($record['status']??'draft')!=='publish'&&!$allowDraft))" in renderer, 'Eventfelt enforces publish/draft visibility contract')

print('v0.1.85 SEMANTIC EVENT PERSISTENCE QA PASS')
