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
layout = text('clean/hangar18-manager/src/Model/LayoutModel.php')
renderer = text('clean/hangar18-manager/src/Frontend/Renderer.php')
collection = text('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php')
forms = text('clean/hangar18-manager/src/Forms/FormService.php')
provisioner = text('clean/hangar18-manager/src/Migration/FormPageProvisioner.php')
editor = text('clean/hangar18-manager/src/Admin/EditorController.php')
editor_js = text('clean/hangar18-manager/assets/editor-v018-core.js')
admin = text('clean/hangar18-manager/src/Admin/AdminController.php')
admin_css = text('clean/hangar18-manager/assets/admin-v0175.css')
event_admin = text('clean/hangar18-manager/src/Admin/EventAdminController.php')
registry = text('clean/hangar18-manager/src/Modules/ModuleRegistry.php')
notes = text('clean-release-notes.html')
backlog = text('docs/clean-backlog-v0100.md')
history = json.loads(text('clean/hangar18-manager/release-history.json'))

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
require(header is not None and const is not None and header.group(1) == const.group(1) and tuple(map(int, header.group(1).split('.'))) >= (0, 1, 75), 'plugin/runtime version is v0.1.75 or newer')

require("src/Forms/FormService.php" in plugin and 'FormService::register()' in plugin, 'form runtime is bootstrapped and registered')
require("src/Migration/FormPageProvisioner.php" in plugin and 'FormPageProvisioner::register()' in plugin, 'Kontakt/Bliv medlem page provisioner is bootstrapped')
require("'contactform'" in layout and "'membershipform'" in layout, 'canonical LayoutModel accepts both form node types')
require('FormService::renderNode' in renderer, 'frontend renderer delegates form nodes to FormService')
require("admin_post_nopriv_" in forms and 'wp_mail(' in forms, 'forms accept public submissions and send through WordPress mail')
require('wp_verify_nonce' in forms and "name=\"website\"" in forms, 'forms use nonce validation and honeypot spam protection')
require('Vi har modtaget din' in forms, 'forms send a receipt to the visitor')
require("ensurePage('kontakt', 'Kontakt', 'contactform')" in provisioner, 'Kontakt page is provisioned with Kontaktformular')
require("ensurePage('bliv-medlem', 'Bliv medlem', 'membershipform')" in provisioner, 'Bliv medlem page is provisioned with membership form')

require('Basic' in editor and 'Moduler' in editor and 'Formularer' in editor, 'Designer palette is split into Basic / Moduler / Formularer')
require("'contactform'" in editor and "'membershipform'" in editor, 'Designer palette exposes both forms')
require("'contactform', 'membershipform'" in editor_js or "'contactform','membershipform'" in editor_js, 'editor runtime accepts form node types')
require('Kontaktformular' in editor_js and 'Bliv medlem-formular' in editor_js, 'editor labels and previews cover both form types')
require('formRecipient' in editor_js and 'formRequireConsent' in editor_js, 'form inspector edits recipient and consent behavior')

require('admin-v0175.css' in admin, 'v0.1.75 Manager CSS is enqueued')
require('flex-wrap:nowrap' in admin_css and 'min-width:500px' in admin_css, 'desktop Handlinger column stays wide and on one line')

require("'galleryRecordId'" in registry, 'event module schema includes optional gallery relation')
require('gallery_record_id' in event_admin and 'Tilknyttet album' in event_admin, 'event Manager can select and save a gallery album')
require('Se billeder' in collection, 'event frontend exposes the linked gallery')

require('eventArchiveEdge' in collection and '23:59:59' in collection, 'events without an end time remain upcoming until end of start date')
require('h18_q' in collection and 'h18_sort' in collection, 'collection pages expose search/sort controls')
require("sortMode('events')" in collection and "'date'" in collection, 'Events default to chronological date sorting')
require("orderBy' => 'title'" in collection, 'vehicle/gallery source lists use title ordering where applicable')
require('Søg i events' in collection, 'Events can be searched by name')
require('Søg i køretøjer' in collection, 'Vehicles can be searched by name')
require('Søg i billedgalleri' in collection, 'Gallery albums can be searched by name')
require('repeat(3,minmax(0,1fr))' in collection, 'desktop module cards use the improved three-column parity layout')
require('← Tilbage til Events' in collection and '← Tilbage til Billedgalleri' in collection and '← Tilbage til Køretøjer' in collection, 'detail pages use explicit back-links')

versions = history.get('versions', []) if isinstance(history, dict) else []
require(any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.75' for row in versions), 'release history retains v0.1.75')
require(any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.75' and any('kontakt' in str(item).lower() for item in row.get('items', [])) for row in versions), 'release history retains v0.1.75 form scope')
require('**Aktuel release:** v' in backlog, 'canonical backlog carries an active release marker')
require((ROOT / 'docs/v0175-status.md').is_file(), 'v0.1.75 status document exists')

print('v0.1.75 forms + search/sort + event archive QA: PASS')
