from __future__ import annotations

from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[2]

def text(rel:str)->str:
    p=ROOT/rel
    if not p.is_file(): raise SystemExit('FAIL missing '+rel)
    return p.read_text(encoding='utf-8')

def req(cond:bool,msg:str)->None:
    if not cond: raise SystemExit('FAIL: '+msg)
    print('PASS:',msg)

def version_tuple(value:str)->tuple[int,...]:
    return tuple(int(part) for part in value.split('.'))

plugin=text('clean/hangar18-manager/hangar18-manager.php')
layout=text('clean/hangar18-manager/src/Model/LayoutModel.php')
renderer=text('clean/hangar18-manager/src/Frontend/Renderer.php')
collection=text('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php')
slots=text('clean/hangar18-manager/src/Frontend/HybridModuleSlots.php')
migration=text('clean/hangar18-manager/src/Migration/HybridModulePageMigration.php')
events=text('clean/hangar18-manager/src/Admin/EventAdminController.php')
registry=text('clean/hangar18-manager/src/Modules/EventFieldRegistry.php')
editor=text('clean/hangar18-manager/src/Admin/EditorController.php')
core=text('clean/hangar18-manager/assets/editor-v018-core.js')
admin=text('clean/hangar18-manager/src/Admin/AdminController.php')
notes=text('clean-release-notes.html')
backlog=text('docs/clean-backlog-v0100.md')
history=json.loads(text('clean/hangar18-manager/release-history.json'))

h=re.search(r'\* Version:\s*([0-9.]+)',plugin); c=re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'",plugin)
current = h.group(1) if h is not None else ''
req(h is not None and c is not None and h.group(1)==c.group(1) and version_tuple(current)>=version_tuple('0.1.78'),'runtime version is v0.1.78 or newer')
req('EventFieldRegistry.php' in plugin and 'HybridModulePageMigration.php' in plugin and 'HybridModuleSlots.php' in plugin,'new v0.1.78 runtime classes are bootstrapped')
req('HybridModulePageMigration::register()' in plugin,'hybrid migration is registered')
req("'eventfield'" in layout and 'moduleSlot' in layout,'LayoutModel supports Eventfelt and module slots')
slot_contract = slots.replace(' ', '')
req(all(token in slot_contract for token in ["'before'", "'between'", "'after'"]) and 'in_array($slot' in slots,'hybrid slot contract exists')
req('Renderer::renderFragment' in slots and 'public static function renderFragment' in renderer,'hybrid slots render through canonical Renderer')
req("HybridModuleSlots::render($postId, 'before')" in collection and "HybridModuleSlots::render($postId, 'between')" in collection and "HybridModuleSlots::render($postId, 'after')" in collection,'collection pages expose before/between/after Designer slots')
req("detailPageId('events')" in collection and "detailPageId('galleries')" in collection and "detailPageId('vehicles')" in collection,'collection cards route to Designer detail pages')
req('event-detalje' in migration and 'album-detalje' in migration and 'koeretoej-detalje' in migration,'three reusable detail template pages are provisioned')
req('BACKUP_META' in migration and 'LayoutModel::saveVersion' in migration,'hybrid migration backs up and versions layout')
req('Om arrangementet' in registry and 'Program' in registry and 'Praktiske oplysninger' in registry,'default Event fields are present')
req('showCard' in registry and 'showDetail' in registry and 'required' in registry,'Event field visibility and required flags are canonical')
req('Eventfelter' in events and 'saveFields' in events and 'event_custom' in events,'Event Manager edits definitions and values')
req("'attributes'=>$attributes" in events or "'attributes' => $attributes" in events,'Event custom values persist as ModuleRecord attributes')
req('h18-clean-event-fields' in admin,'Eventfelter is available from Manager menu')
req("'eventfield' => 'Eventfelt'" in editor,'Designer palette exposes Eventfelt')
req("eventfield:'Eventfelt'" in core and "type === 'eventfield'" in core,'editor runtime supports Eventfelt')
req('eventFieldDefinitions' in plugin and "'attributes' => isset($record['attributes'])" in plugin,'editor receives Event field definitions and attributes')
req('h18_collection_mode' in editor and 'Indholdselementer' in editor and 'Moduldesign' in editor,'collection Designer has content/module-design modes')
req("collectionMode === 'module'" in editor,'collection page defaults to normal content canvas and only special-cases module design mode')
req('EventFieldRegistry::byId' in renderer and 'h18-clean-front-event-field' in renderer,'frontend renders standalone Eventfelt nodes')
req('showCard' in collection and 'showDetail' in collection,'collection/direct detail rendering honors Event field visibility')
req(current != '0.1.78' or ('0.1.78' in notes and 'Hybrid modulsider' in notes),'v0.1.78 release notes are required while v0.1.78 is current')
req('v0.1.78 – Hybrid modulsider + Eventfelter — FÆRDIG' in backlog,'canonical backlog retains completed v0.1.78 milestone')
versions=history.get('versions',[]) if isinstance(history,dict) else []
req(any(isinstance(row,dict) and row.get('version')=='0.1.78' for row in versions),'release history contains v0.1.78')
req((ROOT/'docs/v0178-status.md').is_file(),'v0.1.78 status document exists')
print('v0.1.78 hybrid module pages + Event fields QA: PASS (forward-compatible)')
