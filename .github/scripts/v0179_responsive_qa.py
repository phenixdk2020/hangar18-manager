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
editor = text('clean/hangar18-manager/assets/editor-v0121.js')
viewport = text('clean/hangar18-manager/assets/editor-v0144-viewport.js')
editor_css = text('clean/hangar18-manager/assets/editor-v0121.css')
viewport_css = text('clean/hangar18-manager/assets/editor-v0144.css')
frontend = text('clean/hangar18-manager/src/Frontend/ResponsiveRenderer.php')
layout = text('clean/hangar18-manager/src/Model/LayoutModel.php')
notes = text('clean-release-notes.html')
backlog = text('docs/clean-backlog-v0100.md')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
manifest = json.loads(text('clean-update.json'))
legacy_v0178_qa = text('.github/scripts/v0178_hybrid_event_fields_qa.py')

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
req(header is not None and const is not None and header.group(1) == const.group(1) and tuple(map(int, header.group(1).split('.'))) >= (0,1,79), 'runtime version is v0.1.79 or newer')
req('v0.1.78 or newer' in legacy_v0178_qa, 'historical v0.1.78 gate is forward-compatible')

# Canonical model already has all four geometries; v0.1.79 closes runtime parity.
req("'desktop' => $desktop, 'laptop' => $laptop, 'tablet' => $tablet, 'mobile' => $mobile" in layout, 'LayoutModel canonical geometry contains Desktop/Laptop/Tablet/Mobile')
req("var DEVICES = ['desktop', 'laptop', 'tablet', 'mobile'];" in editor, 'active responsive toolbar contains all four breakpoints')
req('var tabletRaw = source.geometry && source.geometry.tablet;' in editor and 'tablet: normalizeGeometry(tabletRaw, desktop, true)' in editor, 'responsive editor loads a canonical Tablet geometry state')
req('node.geometry.tablet = clone(responsive[id].tablet);' in editor, 'responsive save path persists Tablet without replacing Desktop')
req("if (device === 'tablet') { return effectiveTablet; }" in editor, 'editor resolves Tablet explicitly')
req('mobile.inheritDesktop !== false ? effectiveTablet' in editor, 'Mobile inheritance cascades through effective Tablet')
req("tablet.inheritDesktop !== false ? effectiveLaptop" in editor, 'Tablet inheritance cascades through effective Laptop')
req("tablet: 'Tablet'" in editor, 'responsive toolbar labels Tablet explicitly')
req("button.setAttribute('aria-pressed', isActive ? 'true' : 'false')" in editor and "button.setAttribute('aria-label', 'Redigér '" in editor, 'breakpoint toolbar exposes accessible active state and labels')
req("activeDevice === 'tablet' ? 'Laptop/Desktop'" in editor, 'Tablet Inspector explains its immediate inheritance chain')
req('commitResponsive(before' in editor and 'undo.push({ before: before, after: after' in editor and 'responsive = clone(entry.before)' in editor and 'responsive = clone(entry.after)' in editor, 'responsive breakpoint edits remain snapshot-based Undo/Redo')

req("var WIDTHS = { desktop: 1920, laptop: 1180, tablet: 980, mobile: 390 };" in viewport, 'viewport runtime has explicit Tablet 980 px width')
req("tablet: 'Tablet'" in viewport, 'viewport status labels Tablet')
req('data-h18-device="tablet"' in editor_css and 'data-h18-clean-device="tablet"' in editor_css, 'responsive editor CSS treats Tablet as first-class device')
req('data-h18-device="tablet"' in viewport_css, 'viewport CSS accepts Tablet canvas')

req('public const LAPTOP_MAX = 1180;' in frontend and 'public const TABLET_MAX = 980;' in frontend and 'public const MOBILE_MAX = 782;' in frontend, 'frontend breakpoints are Laptop 1180 / Tablet 980 / Mobile 782')
req("$tg = self::effectiveGeometry($node, 'tablet');" in frontend and "$tabletRows = self::effectiveRows($id, 'tablet'" in frontend, 'frontend computes Tablet geometry and auto-height')
req("self::TABLET_MAX" in frontend and "'px){' . $tablet . '}'" in frontend, 'frontend emits a dedicated Tablet media query')
req("$tabletRaw = is_array($geometry['tablet']" in frontend and "if ($device === 'tablet')" in frontend, 'frontend reads canonical Tablet geometry')
req("return !empty($mobileRaw['inheritDesktop']) ? $tablet" in frontend, 'frontend Mobile inheritance cascades through Tablet')

versions = history.get('versions', []) if isinstance(history, dict) else []
req(any(isinstance(row, dict) and str(row.get('version','')) == '0.1.79' for row in versions), 'release history retains v0.1.79')
req(any(isinstance(row, dict) and str(row.get('version','')) == '0.1.79' and any('Tablet' in str(item) for item in row.get('items', [])) for row in versions), 'release history documents responsive Tablet completion')
req('CLEAN-RESPONSIVE-009 — FÆRDIG I v0.1.79' in backlog, 'canonical backlog closes CLEAN-RESPONSIVE-009 in v0.1.79')
req((ROOT / 'docs/v0179-status.md').is_file(), 'v0.1.79 status document exists')

# Until central release runs, updater must stay on the last verified release.
req(tuple(map(int, str(manifest.get('version','0.0.0')).split('.'))) >= (0,1,79), 'updater manifest is v0.1.79 or newer')
req((ROOT / 'dist/visual-designer-manager-v0.1.79.zip').is_file(), 'verified v0.1.79 ZIP remains present')

print('Visual Designer Manager v0.1.79 responsive QA: PASS')
