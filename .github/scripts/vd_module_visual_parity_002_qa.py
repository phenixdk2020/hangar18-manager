from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def text(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f'Missing required file: {rel}')
    return path.read_text(encoding='utf-8')


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit('FAIL: ' + message)
    print('PASS:', message)


plugin = text('clean/hangar18-manager/hangar18-manager.php')
manifest = json.loads(text('clean-update.json'))
editor = text('clean/hangar18-manager/src/Admin/EditorController.php')
collection = text('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php')
admin_css = text('clean/hangar18-manager/assets/admin-v0175.css')
backlog = text('docs/clean-backlog-v0100.md')
status = text('docs/vd-module-visual-parity-002-status.md')

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
require(header is not None and const is not None and header.group(1) == const.group(1) and tuple(map(int, header.group(1).split('.'))) >= (0, 1, 75), 'parity task remains present in v0.1.75 or newer runtime')
require(tuple(map(int, str(manifest.get('version', '0.0.0')).split('.'))) <= tuple(map(int, header.group(1).split('.'))), 'updater manifest never points beyond runtime version')

for slug in ('events', 'billedgalleri', 'koeretoejer-og-materiel'):
    require(slug in collection, f'collection renderer still owns {slug}')

require('use VisualDesignerManager\\Frontend\\CollectionPageRenderer;' in editor, 'Designer controller imports canonical collection renderer')
require('CollectionPageRenderer::supports($postId)' in editor, 'Designer detects the three collection pages through canonical support check')
require('h18-vd-module-canonical-preview' in editor, 'collection Designer renders dedicated canonical preview shell')
require('h18-vd-module-canonical-frame' in editor and '<iframe' in editor, 'Designer uses same-origin frontend iframe instead of a second module card implementation')
require("'h18_vd_module_preview' => '1'" in editor, 'iframe carries a dedicated preview marker')
require('hideModulePreviewAdminBar' in editor and "add_filter('show_admin_bar'" in editor, 'editor preview suppresses logged-in admin-bar geometry')
require("'h18-clean-events'" in editor and "'h18-clean-gallery'" in editor and "'h18-clean-vehicles'" in editor, 'canonical preview links to each module data manager')

require('h18-module-page-style-parity-002' in collection, 'frontend collection CSS carries parity task marker')
require('width:90%;max-width:none' in collection, 'old-site 90-percent page frame has no artificial 1440px ceiling')
require('repeat(3,minmax(0,1fr))' in collection and 'repeat(2,minmax(0,1fr))' in collection and 'grid-template-columns:1fr' in collection, 'collection cards use 3/2/1 responsive grid')
require('aspect-ratio:16/9' in collection, 'collection card covers use stable full-width 16:9 geometry')
require('.h18-module-card-body{background:#eee8dc' in collection, 'beige old-style card body is separated from the image')
require('.h18-module-card{background:transparent' in collection and 'box-shadow:none' in collection, 'cards do not add a modern shadow/background shell absent from old target')
require('h18-module-spec-table' in collection and 'Se køretøjet →' in collection, 'vehicle technical card structure remains intact')
require('Kommende arrangementer' in collection and 'Tidligere arrangementer' in collection, 'event old-site section structure remains intact')
require("<h2>Køretøjer</h2>" in collection, 'gallery old-site subheading remains intact')

require('VD-MODULE-VISUAL-PARITY-002' in admin_css, 'Designer iframe chrome has dedicated parity CSS')
require('.h18-vd-module-canonical-frame' in admin_css and 'min-height:680px' in admin_css, 'canonical module preview has usable desktop viewport')

require('VD-MODULE-VISUAL-PARITY-002' in backlog, 'backlog records parity implementation/release state')
require('1:1-visuel `_old`-paritet var ikke afsluttet' in backlog, 'backlog corrects the historical v0.1.74 overstatement')
require('v0.1.76' in status or 'Implementeret i source efter v0.1.75' in status, 'status document records parity completion/release state')
require('centrale release-workflow' in status or 'Ingen ZIP, manifest eller release-trigger ændres' in status, 'status document preserves central release boundary')

print('VD-MODULE-VISUAL-PARITY-002 QA: PASS')
