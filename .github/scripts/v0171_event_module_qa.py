from __future__ import annotations

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


require('clean/hangar18-manager/hangar18-manager.php',
        ' * Version: 0.1.71',
        "define('H18_CLEAN_VERSION', '0.1.71');",
        "src/Admin/EventAdminController.php",
        'EventAdminController::register()',
        "'eventRecords' => $eventRecords",
        "'eventAdminUrl' => admin_url('admin.php?page=h18-clean-events')")
require('clean/hangar18-manager/src/Admin/EventAdminController.php',
        'final class EventAdminController',
        "public const PAGE = 'h18-clean-events'",
        'function saveEvent', 'function deleteEvent',
        "ModuleStore::save('events'",
        "name=\"start\"", "name=\"end\"", "name=\"location\"",
        'featured_media_id')
require('clean/hangar18-manager/src/Admin/AdminController.php',
        "[EventAdminController::class, 'render']")
require('clean/hangar18-manager/assets/admin-v0123.js',
        "'h18-clean-events': ['Klar', 'ready']")

require('clean/hangar18-manager/src/Modules/ModuleRegistry.php',
        "'events' => [", "'start' =>", "'end' =>", "'location' =>", "'description' =>")
require('clean/hangar18-manager/src/Modules/ModuleStore.php',
        "['sortOrder', 'title', 'updatedAt', 'start']",
        "$orderBy === 'start'",
        "$leftFields['start']")

require('clean/hangar18-manager/src/Model/LayoutModel.php',
        "'eventlist'", "'eventdetail'",
        "'module' => 'events'",
        "'view' => 'list'", "'view' => 'detail'",
        "'dateFilter'", "['all', 'upcoming', 'past']")
require('clean/hangar18-manager/src/Admin/EditorController.php',
        "'eventlist' => 'Eventliste'", "'eventdetail' => 'Eventdetalje'")
require('clean/hangar18-manager/assets/editor-v018-core.js',
        "'eventlist'", "'eventdetail'", 'Eventliste', 'Eventdetalje',
        'eventRecords()', 'eventRecordById', 'eventDateLabel', 'eventDateFilter',
        'eventDetailPageId', 'eventRecordId', 'h18_event=record-id')
require('clean/hangar18-manager/assets/editor-v0166-foundation.css',
        'h18-vd-event-list-preview', 'h18-vd-event-detail-preview')

require('clean/hangar18-manager/src/Frontend/Renderer.php',
        "if ($type === 'eventlist')", "if ($type === 'eventdetail')",
        "ModuleStore::listRecords('events'", "ModuleStore::findByRecordId('events'",
        "$_GET['h18_event']", "(string) ($record['status'] ?? 'draft') !== 'publish'",
        "['all', 'upcoming', 'past']", 'h18-clean-front-event-list',
        'h18-clean-front-event-detail', 'eventDateLabel')

for manual in ('CLEAN-DESIGN-MANUAL.md', 'CLEAN-USER-MANUAL.md', 'CLEAN-TECHNICAL-MANUAL.md'):
    require(manual, 'Event')
require('CLEAN-TECHNICAL-MANUAL.md', 'VD-EVENT-MODULE-001')
require('CLEAN-DESIGN-MANUAL.md', 'Eventmodul – designprincip')
require('CLEAN-USER-MANUAL.md', 'Sådan bruger du Eventmodulet')
require('docs/clean-backlog-v0100.md',
        'Aktuel release:** v0.1.71', 'VD-EVENT-MODULE-001',
        'v0.1.71 – Events — FÆRDIG', 'v0.1.72 – Billedgalleri — NÆSTE')
require('docs/v0171-status.md', 'VD-EVENT-MODULE-001', 'release candidate')
require('clean-release-notes.html', '0.1.71 – Events')

history = json.loads(text('clean/hangar18-manager/release-history.json'))
versions = history.get('versions', []) if isinstance(history, dict) else []
if not any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.71' for row in versions):
    raise SystemExit('release-history.json: v0.1.71 missing')

admin = text('clean/hangar18-manager/src/Admin/AdminController.php')
if re.search(r"h18-clean-events'.*\[self::class,\s*'events'\]", admin):
    raise SystemExit('Events submenu still points at placeholder AdminController::events')

print('v0.1.71 event module QA: PASS')
