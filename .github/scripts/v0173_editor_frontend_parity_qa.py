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


def version_tuple(value: str) -> tuple[int, int, int]:
    match = re.search(r'\b(\d+)\.(\d+)\.(\d+)\b', value)
    return tuple(int(part) for part in match.groups()) if match else (0, 0, 0)


plugin = text('clean/hangar18-manager/hangar18-manager.php')
css = text('clean/hangar18-manager/assets/editor-v0166-foundation.css')
renderer = text('clean/hangar18-manager/src/Frontend/Renderer.php')
controller = text('clean/hangar18-manager/src/Admin/EditorController.php')
backlog = text('docs/clean-backlog-v0100.md')
notes = text('clean-release-notes.html')
history = json.loads(text('clean/hangar18-manager/release-history.json'))

header_match = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const_match = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
header_version = header_match.group(1) if header_match else ''
const_version = const_match.group(1) if const_match else ''
require(header_version == const_version and version_tuple(header_version) >= (0, 1, 73), 'plugin/runtime version is 0.1.73 or newer')

require('VD-EDITOR-FRONTEND-PARITY-001' in css, 'parity contract marker exists in final editor stylesheet')
require('.h18-clean-surface{align-items:stretch}' in css, 'editor grid stretches canonical grid areas like frontend')
require('.h18-clean-node-header{position:absolute;' in css, 'editor element header is removed from normal layout flow')
require('pointer-events:none' in css and 'transform:translateY(-100%)' in css, 'hidden editor chrome cannot reserve content space')
require('.h18-clean-node-preview{min-height:0;padding:0}' in css, 'generic editor-only preview padding and minimum height are removed')
require('.h18-clean-node[data-h18-explicit-grid="1"]>.h18-clean-node-preview{height:100%}' in css, 'explicit canonical node geometry fills its saved box')
require('.h18-clean-node-preview--image{min-height:0;height:100%}' in css, 'image preview no longer subtracts the 28px editor header')
require('.h18-clean-inner-surface{margin-top:0;min-height:0;border:0;outline:1px dashed #a7aaad;outline-offset:-1px}' in css, 'Section/Container guide is non-layout outline without margin or border')

# Guard against reintroducing the known geometry drift in the parity block.
parity = css.split('VD-EDITOR-FRONTEND-PARITY-001', 1)[1]
require('height:calc(100% - 28px)' not in parity, 'parity block never subtracts editor header height from rendered content')
require('margin-top:8px' not in parity, 'parity block never adds editor-only top spacing to nested surfaces')

require('public static function standaloneDocument' in renderer, 'canonical PHP standalone preview remains available')
require('self::renderModel(LayoutModel::normalize($headerModel))' in renderer, 'canonical preview renders Header through frontend renderer')
require('self::renderModel(LayoutModel::normalize($pageModel))' in renderer, 'canonical preview renders page through frontend renderer')
require('self::renderModel(LayoutModel::normalize($footerModel))' in renderer, 'canonical preview renders Footer through frontend renderer')
require('Renderer::standaloneDocument($pageModel, $headerModel, $footerModel' in controller, 'composite preview still uses canonical renderer')

require('**Aktuel release:** v0.1.73' in backlog, 'canonical backlog points at v0.1.73')
require('VD-EDITOR-FRONTEND-PARITY-001 — IMPLEMENTERET I v0.1.73' in backlog, 'parity work is recorded as implemented')
require('v0.1.74 – Modul-cutover/migrering — NÆSTE' in backlog, 'module cutover is moved to the next release instead of being lost')
require('0.1.73 – Editor/frontend visuel paritet' in notes, 'release notes describe v0.1.73')
require((ROOT / 'docs/v0173-status.md').is_file(), 'v0.1.73 status document exists')
require(any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.73' for row in history.get('versions', [])), 'release history contains v0.1.73')

print('v0.1.73 Editor/frontend visual parity QA: PASS')
