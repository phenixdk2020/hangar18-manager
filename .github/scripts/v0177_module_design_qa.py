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
    try:
        return tuple(int(part) for part in value.split('.'))
    except ValueError:
        return (0,)


plugin = text('clean/hangar18-manager/hangar18-manager.php')
model = text('clean/hangar18-manager/src/Model/ModuleDesignModel.php')
collection = text('clean/hangar18-manager/src/Frontend/CollectionPageRenderer.php')
editor = text('clean/hangar18-manager/src/Admin/EditorController.php')
js = text('clean/hangar18-manager/assets/module-design-v0177.js')
css = text('clean/hangar18-manager/assets/module-design-v0177.css')
notes = text('clean-release-notes.html')
backlog = text('docs/clean-backlog-v0100.md')
status = text('docs/v0177-status.md')
history = json.loads(text('clean/hangar18-manager/release-history.json'))
manifest = json.loads(text('clean-update.json'))

header = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
runtime = header.group(1) if header is not None else ''
require(
    header is not None and const is not None
    and runtime == const.group(1)
    and version_tuple(runtime) >= version_tuple('0.1.77'),
    'plugin/runtime version is v0.1.77 or newer',
)
require("src/Model/ModuleDesignModel.php" in plugin, 'ModuleDesignModel is bootstrapped')

require("META = '_h18_vd_module_design_v1'" in model and "HISTORY_META = '_h18_vd_module_design_history_v1'" in model, 'module design uses dedicated canonical current/history meta')
for key, value in [('pageWidth', '90'), ('columnsDesktop', '3'), ('columnsTablet', '2'), ('columnsMobile', '1'), ('cardGap', '22')]:
    require(f"'{key}' => {value}" in model, f'default {key} preserves _old/v0.1.76 parity')
require("'cardBackground' => '#eee8dc'" in model and "'imageRatio' => '16/9'" in model, 'default beige card body and 16:9 cover are preserved')
require("current_user_can('edit_pages')" in model and "h18_vd_module_design" in model, 'preview override is editor-only and explicit')
require('public static function save' in model and 'public static function historyDesign' in model, 'module design supports version-linked snapshots and restore')
require('sanitize_hex_color' in model and 'self::clamp' in model, 'module design input is normalized server-side')

require('ModuleDesignModel::forRender($postId)' in collection, 'canonical CollectionPageRenderer reads saved/preview module design')
require('private static function style(array $design)' in collection, 'collection CSS is generated from canonical design state')
require('--h18-module-page-width:' in collection and '--h18-module-columns-desktop:' in collection, 'page width and desktop grid are dynamic CSS variables')
require('--h18-module-card-gap:' in collection and '--h18-module-card-max:' in collection, 'card gap and max width are dynamic')
require('--h18-module-card-bg:' in collection and '--h18-module-card-text:' in collection and '--h18-module-accent:' in collection, 'card/text/accent colors are dynamic')
require('--h18-module-card-pad-x:' in collection and '--h18-module-card-pad-y:' in collection and '--h18-module-card-radius:' in collection, 'card padding and radius are dynamic')
require('--h18-module-image-ratio:' in collection and '--h18-module-h1:' in collection and '--h18-module-h2:' in collection and '--h18-module-h3:' in collection and '--h18-module-body:' in collection, 'image ratio and typography are dynamic')
require('width:90%;max-width:none' in collection and 'repeat(3,minmax(0,1fr))' in collection and 'repeat(2,minmax(0,1fr))' in collection and 'grid-template-columns:1fr' in collection, 'v0.1.76 static fallback declarations remain as safe parity fallbacks')
require('aspect-ratio:16/9' in collection and '.h18-module-card-body{background:#eee8dc' in collection, 'v0.1.76 image/background fallbacks remain intact')

require('use VisualDesignerManager\\Model\\ModuleDesignModel;' in editor, 'Designer imports canonical module design model')
require('h18-module-design-json' in editor and 'module_design_json' in editor, 'Designer persists module design through a hidden canonical JSON field')
require('h18-vd-module-design-panel' in editor and 'Moduldesign' in editor, 'collection pages expose the Moduldesign panel')
for key in ['pageWidth', 'columnsDesktop', 'columnsTablet', 'columnsMobile', 'cardGap', 'cardMaxWidth', 'cardBackground', 'cardTextColor', 'cardPaddingX', 'cardPaddingY', 'cardRadius', 'imageRatio', 'h1Size', 'h2Size', 'h3Size', 'bodySize', 'accentColor', 'sectionGap']:
    require(key in editor, f'Designer exposes {key}')
require('Nulstil til _old-standard' in editor, 'Designer exposes explicit _old reset')
require('data-base-url' in editor and "'h18_vd_module_design' =>" in editor, 'canonical iframe carries design preview state')
require('sameModuleDesign' in editor and 'ModuleDesignModel::digest' in editor, 'Designer save detects module-design changes canonically')
require('ModuleDesignModel::save($postId, $moduleDesign, $version)' in editor, 'module design is snapshotted with Designer version')
require('ModuleDesignModel::historyDesign($postId, $targetVersion)' in editor, 'versions restore module design together with layout')
require('module-design-v0177.js' in editor and 'module-design-v0177.css' in editor, 'module-design assets are enqueued by Designer')

require("url.searchParams.set('h18_vd_module_design', JSON.stringify(state))" in js, 'live preview forwards current design into canonical same-origin renderer')
require("hidden.value = JSON.stringify(state)" in js, 'live controls keep save payload synchronized')
require('data-module-design-reset' in js and 'defaults' in js, 'live controls support reset to defaults')
require('.h18-vd-module-designer-layout' in css and '.h18-vd-module-design-panel' in css, 'module design panel has dedicated responsive admin layout')

versions = history.get('versions', []) if isinstance(history, dict) else []
require(any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.77' for row in versions), 'release history retains v0.1.77')
require('VD-MODULE-DESIGN-001 — FÆRDIG I v0.1.77' in backlog, 'canonical backlog retains completed v0.1.77 module design milestone')
require('Release candidate' in status and 'central ZIP/manifest-build' in status, 'v0.1.77 status preserves central release gate')

# The original v0.1.77 gate also verified its pre-release boundary. Preserve that
# behavior when testing a 0.1.77 candidate, but make the regression forward-
# compatible once a later version is under development.
manifest_version = str(manifest.get('version', ''))
if runtime == '0.1.77':
    require(version_tuple(manifest_version) in {version_tuple('0.1.76'), version_tuple('0.1.77')}, 'v0.1.77 updater boundary is valid')
    if manifest_version == '0.1.76':
        require(not (ROOT / 'dist/visual-designer-manager-v0.1.77.zip').is_file(), 'pre-release source does not contain a v0.1.77 ZIP yet')
    else:
        require((ROOT / 'dist/visual-designer-manager-v0.1.77.zip').is_file(), 'released v0.1.77 ZIP exists')
else:
    require(version_tuple(manifest_version) >= version_tuple('0.1.77'), 'later source retains at least the verified v0.1.77 updater baseline')
    require((ROOT / 'dist/visual-designer-manager-v0.1.77.zip').is_file(), 'later source retains the verified v0.1.77 ZIP')

print('Visual Designer Manager v0.1.77 module design QA: PASS (forward-compatible)')
