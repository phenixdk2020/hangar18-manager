from __future__ import annotations

# Authenticated re-trigger after VehicleFieldRegistry generator repair.
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def text(path: str) -> str:
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f'Missing required file: {path}')
    return p.read_text(encoding='utf-8')


def require(path: str, *needles: str) -> None:
    value = text(path)
    for needle in needles:
        if needle not in value:
            raise SystemExit(f'{path}: missing contract marker: {needle}')


# Version/bootstrap and concrete module classes.
require('clean/hangar18-manager/hangar18-manager.php',
        ' * Version: 0.1.70',
        "define('H18_CLEAN_VERSION', '0.1.70');",
        "src/Modules/VehicleFieldRegistry.php",
        "src/Admin/VehicleAdminController.php",
        'VehicleAdminController::register()',
        "'vehicleRecords' => $vehicleRecords",
        "'vehicleAdminUrl' => admin_url('admin.php?page=h18-clean-vehicles')")
require('clean/hangar18-manager/src/Modules/VehicleFieldRegistry.php',
        'final class VehicleFieldRegistry',
        "public const OPTION = 'h18_vehicle_fields_v1'",
        "'manufacturer'", "'engine'", "'weight'", "'crew'")
require('clean/hangar18-manager/src/Admin/VehicleAdminController.php',
        'final class VehicleAdminController',
        "public const PAGE = 'h18-clean-vehicles'",
        "public const FIELDS_PAGE = 'h18-clean-vehicle-fields'",
        'function saveVehicle', 'function deleteVehicle', 'function saveFields',
        "ModuleStore::save('vehicles'", 'VehicleFieldRegistry::all()')

# Admin routes and UI must be real, not placeholders.
require('clean/hangar18-manager/src/Admin/AdminController.php',
        "[VehicleAdminController::class, 'render']",
        "[VehicleAdminController::class, 'renderFields']")
require('clean/hangar18-manager/assets/admin-v0123.js',
        "'h18-clean-vehicles': ['Klar', 'ready']",
        "'h18-clean-vehicle-fields': ['Klar', 'ready']")
require('clean/hangar18-manager/assets/admin-v0170-vehicles.js',
        'Vælg galleribilleder', 'Vælg primært billede', 'h18-vd-add-vehicle-field')
require('clean/hangar18-manager/assets/admin-v0170-vehicles.css', 'h18-vd-vehicle-layout', 'h18-vd-field-row')

# Shared datastore and schema contracts.
require('clean/hangar18-manager/src/Modules/ModuleRegistry.php',
        "'imageIds' => ['label' => 'Galleri', 'type' => 'media_list'")
require('clean/hangar18-manager/src/Modules/ModuleStore.php',
        "public const META_RECORD_ID = '_h18_module_record_id'",
        'function findByRecordId',
        'META_RECORD_ID')

# Canonical Designer elements and dynamic binding.
require('clean/hangar18-manager/src/Model/LayoutModel.php',
        'use VisualDesignerManager\\Modules\\ModuleBinding;',
        "'vehiclelist'", "'vehicledetail'",
        "'module' => 'vehicles'",
        "'view' => 'list'",
        "'view' => 'detail'")
require('clean/hangar18-manager/src/Admin/EditorController.php',
        "'vehiclelist' => 'Køretøjsliste'",
        "'vehicledetail' => 'Køretøjsdetalje'")
require('clean/hangar18-manager/assets/editor-v018-core.js',
        "'vehiclelist'", "'vehicledetail'",
        'Køretøjsliste', 'Køretøjsdetalje',
        'vehicleRecords()', 'vehicleRecordById',
        'vehicleDetailPageId', 'vehicleRecordId',
        'h18_vehicle=record-id')
require('clean/hangar18-manager/assets/editor-v0166-foundation.css',
        'h18-vd-vehicle-list-preview', 'h18-vd-vehicle-detail-preview')

# Frontend: list is publish-only; detail resolves stable record IDs and blocks drafts publicly.
require('clean/hangar18-manager/src/Frontend/Renderer.php',
        'use VisualDesignerManager\\Modules\\ModuleStore;',
        "if ($type === 'vehiclelist')",
        "if ($type === 'vehicledetail')",
        "ModuleStore::listRecords('vehicles'",
        "ModuleStore::findByRecordId('vehicles'",
        "$_GET['h18_vehicle']",
        "(string) ($record['status'] ?? 'draft') !== 'publish'",
        'h18-clean-front-vehicle-list',
        'h18-clean-front-vehicle-detail')

# Manuals/backlog/release traceability explicitly requested by the user.
for manual in ('CLEAN-DESIGN-MANUAL.md', 'CLEAN-USER-MANUAL.md', 'CLEAN-TECHNICAL-MANUAL.md'):
    require(manual, 'Køretøj')
require('CLEAN-TECHNICAL-MANUAL.md', 'VD-VEHICLE-MODULE-001')
require('CLEAN-DESIGN-MANUAL.md', 'Køretøjsmodul – designprincip')
require('CLEAN-USER-MANUAL.md', 'Sådan bruger du Køretøjsmodulet')
require('docs/clean-backlog-v0100.md',
        'Aktuel release:** v0.1.70',
        'VD-VEHICLE-MODULE-001',
        'v0.1.71 – Events',
        'v0.1.72 – Billedgalleri')
require('docs/v0170-status.md', 'VD-VEHICLE-MODULE-001', 'release candidate')
require('clean-release-notes.html', '0.1.70 – Køretøjsmodul')

history = json.loads(text('clean/hangar18-manager/release-history.json'))
versions = history.get('versions', []) if isinstance(history, dict) else []
if not any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.70' for row in versions):
    raise SystemExit('release-history.json: v0.1.70 missing')

# Permanent central release gate and package-presence checks must be wired before release.
require('.github/workflows/visual-designer-release.yml',
        'v0170_vehicle_module_qa.py',
        'VD-VEHICLE-MODULE-001',
        'docs/v0170-status.md',
        'src/Admin/VehicleAdminController.php',
        'src/Modules/VehicleFieldRegistry.php')

# Prevent accidental regression back to placeholder routes/statuses.
admin = text('clean/hangar18-manager/src/Admin/AdminController.php')
if re.search(r"h18-clean-vehicles'.*\[self::class,\s*'vehicles'\]", admin):
    raise SystemExit('Vehicle submenu still points at placeholder AdminController::vehicles')

print('v0.1.70 vehicle module QA: PASS')
