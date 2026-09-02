from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def text(rel: str) -> str:
    p = ROOT / rel
    if not p.is_file():
        raise SystemExit('FAIL missing ' + rel)
    return p.read_text(encoding='utf-8')


def req(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit('FAIL: ' + message)
    print('PASS:', message)


plugin = text('clean/hangar18-manager/hangar18-manager.php')
admin = text('clean/hangar18-manager/src/Admin/AdminController.php')
editor_controller = text('clean/hangar18-manager/src/Admin/EditorController.php')
layout = text('clean/hangar18-manager/src/Model/LayoutModel.php')
renderer = text('clean/hangar18-manager/src/Frontend/Renderer.php')
collection = text('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php')
migration = text('clean/hangar18-manager/src/Migration/HybridModulePageMigration.php')
editor = text('clean/hangar18-manager/assets/editor-v018-core.js')
legacy79 = text('.github/scripts/v0179_responsive_qa.py')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
manifest = json.loads(text('clean-update.json'))
notes = text('clean-release-notes.html')
backlog = text('docs/clean-backlog-v0100.md')

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
req(header is not None and const is not None and header.group(1) == const.group(1) and tuple(map(int, header.group(1).split('.'))) >= (0,1,80), 'runtime version is v0.1.80 or newer')
req('runtime version is v0.1.79 or newer' in legacy79, 'historical v0.1.79 gate is forward-compatible')

req("'eventvalue'" in layout and "'eventimage'" in layout, 'canonical LayoutModel supports Eventværdi and Eventbillede')
req("['h1', 'h2', 'h3', 'h4', 'h5', 'h6']" in layout, 'Text canonical model supports H1')
req("if ($type === 'eventvalue')" in renderer and "if ($type === 'eventimage')" in renderer, 'frontend renders independent event values and images')
req("['h1' => 44, 'h2' => 32" in renderer, 'frontend Text renderer has H1 typography default')
req("node.type === 'eventvalue'" in editor and "node.type === 'eventimage'" in editor, 'Designer previews Eventværdi and Eventbillede')
req("<h3>Eventværdi</h3>" in editor and "<h3>Eventbillede</h3>" in editor, 'Inspector exposes user-facing event controls')
req("eventvalue:'Eventværdi'" in editor and "eventimage:'Eventbillede'" in editor, 'Designer type labels include new event nodes')
req("'eventvalue' => 'Eventværdi', 'eventimage' => 'Eventbillede'" in editor_controller, 'palette exposes composable event pieces')
req("'eventdetail' => 'Eventdetalje'" not in editor_controller.split("'Moduler' => [",1)[1].split("'Formularer' => [",1)[0], 'old all-in-one Eventdetalje is hidden from new palette')

req("self::openPage('events', $title, false)" in collection, 'Events collection omits hardcoded H1')
req("self::openPage('galleries', $title, false)" in collection, 'Billedgalleri collection omits hardcoded H1')
req("self::openPage('vehicles', $title, false)" in collection, 'Køretøjer collection omits hardcoded H1')
req("bool $showTitle = true" in collection, 'legacy/detail openPage keeps optional title compatibility')

req("V0180_COLLECTION_META" in migration and "module-page-title" in migration, 'v0.1.80 migration provisions Designer collection headings')
req("'headingLevel'=>'h1'" in migration and "'headingFontSize'=>44" in migration, 'migrated collection title is a true H1 Designer text')
req("withComposableEventDetail" in migration, 'migration upgrades Eventdetalje composition')
for marker in ['event-title','event-date','event-location','event-summary','event-description','event-image']:
    req(marker in migration, 'migration contains ' + marker)
req("'eventfield-about'=>58" in migration and "'eventfield-program'=>72" in migration and "'eventfield-practical'=>86" in migration, 'default Eventfelter align on the same Designer content line')
req('V0180_COLLECTION_BACKUP' in migration and 'V0180_EVENT_DETAIL_BACKUP' in migration, 'migration stores pre-change layout backups')

visible_data = "add_submenu_page(self::MENU, 'Data', 'Data'"
req(visible_data not in admin, 'Data is removed from visible Manager submenu')
req("add_submenu_page(null, 'Data (intern)'" in admin, 'old Data URL remains as hidden compatibility/diagnostic route')
req('final class ModuleBinding' in text('clean/hangar18-manager/src/Modules/ModuleBinding.php'), 'internal ModuleBinding remains intact')
req('final class ModuleStore' in text('clean/hangar18-manager/src/Modules/ModuleStore.php'), 'internal ModuleStore remains intact')

versions = history.get('versions', []) if isinstance(history, dict) else []
req(any(isinstance(row, dict) and str(row.get('version','')) == '0.1.80' for row in versions), 'release history retains v0.1.80')
req('0.1.80' in notes and 'Eventværdi' in notes and 'Data' in notes, 'release notes describe composable detail and Data-menu cleanup')
req('VD-COMPOSABLE-MODULE-PAGES-002 — FÆRDIG I v0.1.80' in backlog, 'canonical backlog retains completed v0.1.80 milestone')
req((ROOT / 'docs/v0180-status.md').is_file(), 'v0.1.80 status document exists')

# Historical gate is forward-compatible: the updater must be at least the verified v0.1.80 release.
req(tuple(map(int, str(manifest.get('version','0.0.0')).split('.'))) >= (0,1,80), 'updater manifest is v0.1.80 or newer')
req((ROOT / 'dist/visual-designer-manager-v0.1.80.zip').is_file(), 'verified v0.1.80 ZIP remains present')

print('Visual Designer Manager v0.1.80 composable module QA: PASS')
