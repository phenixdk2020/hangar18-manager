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
notes = text('clean-release-notes.html')
backlog = text('docs/clean-backlog-v0100.md')
status = text('docs/vd-module-visual-parity-002-status.md')
release_status = text('docs/v0176-status.md')
editor = text('clean/hangar18-manager/src/Admin/EditorController.php')
collection = text('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php')
admin_css = text('clean/hangar18-manager/assets/admin-v0175.css')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
manifest = json.loads(text('clean-update.json'))

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
require(header is not None and const is not None and header.group(1) == '0.1.76' and const.group(1) == '0.1.76', 'plugin/runtime version is exactly 0.1.76')

versions = history.get('versions', []) if isinstance(history, dict) else []
require(bool(versions) and str(versions[0].get('version', '')) == '0.1.76', 'release history starts with v0.1.76')
require('0.1.76' in notes and 'CollectionPageRenderer' in notes and '_old' in notes, 'release notes describe canonical module preview and _old parity')
require('**Aktuel release:** v0.1.76' in backlog, 'canonical backlog points at v0.1.76')
require('VD-MODULE-VISUAL-PARITY-002 — FÆRDIG I v0.1.76' in backlog, 'parity task is closed in v0.1.76')
require('Inkluderet i Visual Designer Manager v0.1.76' in status, 'parity status records v0.1.76 inclusion')
require('Release candidate' in release_status and 'central ZIP/manifest-build' in release_status, 'v0.1.76 status preserves central release gate')

require('CollectionPageRenderer::supports($postId)' in editor, 'Designer detects canonical collection pages')
require('h18-vd-module-canonical-frame' in editor and '<iframe' in editor, 'Designer collection preview uses frontend iframe')
require('hideModulePreviewAdminBar' in editor, 'module iframe suppresses editor admin-bar geometry')
require('h18-module-page-style-parity-002' in collection, 'collection renderer retains parity CSS marker')
require('width:90%;max-width:none' in collection, 'collection page uses 90-percent frame without max-width ceiling')
require('repeat(3,minmax(0,1fr))' in collection and 'repeat(2,minmax(0,1fr))' in collection and 'grid-template-columns:1fr' in collection, 'collection page uses 3/2/1 responsive grid')
require('aspect-ratio:16/9' in collection and '.h18-module-card-body{background:#eee8dc' in collection, 'collection cards retain 16:9 cover and beige body')
require('VD-MODULE-VISUAL-PARITY-002' in admin_css and '.h18-vd-module-canonical-frame' in admin_css, 'Designer canonical preview CSS remains present')

# Until the central release workflow runs, the public updater must still point to the last verified release.
require(str(manifest.get('version', '')) == '0.1.75', 'pre-release updater manifest remains on verified v0.1.75')
require(not (ROOT / 'dist/visual-designer-manager-v0.1.76.zip').is_file(), 'pre-release source does not contain a v0.1.76 ZIP yet')

print('Visual Designer Manager v0.1.76 release-candidate QA: PASS')
