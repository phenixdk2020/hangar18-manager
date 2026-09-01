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


def version_tuple(value: str) -> tuple[int, ...]:
    return tuple(int(part) for part in value.split('.'))


plugin = text('clean/hangar18-manager/hangar18-manager.php')
collection = text('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php')
renderer = text('clean/hangar18-manager/src/Frontend/Renderer.php')
updater = text('clean/hangar18-manager/src/Update/GitHubUpdater.php')
editor = text('clean/hangar18-manager/src/Admin/EditorController.php')
notes = text('clean-release-notes.html')
backlog = text('docs/clean-backlog-v0100.md')
history = json.loads(text('clean/hangar18-manager/release-history.json'))

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
require(header is not None and const is not None and header.group(1) == const.group(1) and version_tuple(header.group(1)) >= version_tuple('0.1.74'), 'plugin/runtime version is v0.1.74 or newer')
require("src/Frontend/CollectionPageRenderer.php" in plugin, 'collection-page renderer is bootstrapped')
require('CollectionPageRenderer::render($postId)' in renderer, 'frontend content delegates known module pages to collection renderer')

for slug in ('events', 'billedgalleri', 'koeretoejer-og-materiel'):
    require(slug in collection, f'collection renderer recognizes {slug}')
require('Kommende arrangementer' in collection and 'Tidligere arrangementer' in collection, 'Events page renders upcoming and past groups')
require("current_time('timestamp')" in collection, 'event grouping uses WordPress-local current time')
require('Læs mere →' in collection, 'event cards expose old-site read-more action')
require('Køretøjer' in collection and 'h18-module-gallery-grid' in collection, 'gallery page keeps old-site category/card layout')
require('billeder' in collection and "fields['imageIds']" in collection, 'gallery cards show album image counts from module data')
require('Historisk materiel' in collection, 'vehicle page keeps old-site subheading')
require('Her finder du foreningens dokumenterede køretøjer og øvrige militærhistoriske materiel.' in collection, 'vehicle page keeps original intro text')
require('h18-module-spec-table' in collection and 'Se køretøjet →' in collection, 'vehicle cards render technical table and detail link')
require('width:90%' in collection, 'module page uses the 90-percent site frame from the original pages')
require('grid-auto-rows' not in collection, 'collection pages are content-flow modules rather than fixed 8px canvas rows')

require("isset($decoded['versions'])" in updater and "$decoded['versions']" in updater, 'release-history loader accepts the actual {versions:[...]} JSON envelope')
require("'Ingen ændringer at gemme.'" in editor, 'no-op save reports no changes clearly')
require("'Siden er gemt." in editor, 'successful page save reports a clear confirmation')
require("'Siden kunne ikke gemmes:" in editor, 'failed page save reports a clear failure')
require("$status === 'info' ? 'notice-info'" in editor, 'no-change feedback is informational rather than success/error')
require('isNoopDesignerSave' in updater, 'change-note guard lets canonical no-op saves reach no-change feedback')

versions = history.get('versions', []) if isinstance(history, dict) else []
require(any(str(item.get('version', '')) == '0.1.74' for item in versions if isinstance(item, dict)), 'release history retains v0.1.74')
require('0.1.74' in notes or version_tuple(header.group(1)) > version_tuple('0.1.74'), 'release notes are current or still describe v0.1.74')
require('**Aktuel release:** v' in backlog, 'canonical backlog carries an active-release marker')
require((ROOT / 'docs/v0174-status.md').is_file(), 'v0.1.74 status document exists')

print('v0.1.74 module cutover + UX fixes QA: PASS')
