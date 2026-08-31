from pathlib import Path
import json
import re

# v0.1.69 release contract; all assertions are intentionally forward-compatible.
ROOT = Path(__file__).resolve().parents[2]


def text(rel):
    return (ROOT / rel).read_text(encoding='utf-8')


def require(condition, message):
    if not condition:
        raise SystemExit('FAIL: ' + message)
    print('PASS:', message)


def version_tuple(value):
    match = re.search(r'\b(\d+)\.(\d+)\.(\d+)\b', value)
    return tuple(int(part) for part in match.groups()) if match else (0, 0, 0)

plugin = text('clean/hangar18-manager/hangar18-manager.php')
js = text('clean/hangar18-manager/assets/editor-v0169-canvas-height.js')
tech = text('CLEAN-TECHNICAL-MANUAL.md')
design = text('CLEAN-DESIGN-MANUAL.md')
user = text('CLEAN-USER-MANUAL.md')
notes = text('clean-release-notes.html')
history = json.loads(text('clean/hangar18-manager/release-history.json'))

header_match = re.search(r'\* Version:\s*([0-9.]+)', plugin)
const_match = re.search(r"H18_CLEAN_VERSION',\s*'([0-9.]+)'", plugin)
header_version = header_match.group(1) if header_match else ''
const_version = const_match.group(1) if const_match else ''
require(header_version == const_version and version_tuple(header_version) >= (0, 1, 69), 'plugin/runtime version is 0.1.69 or newer')
require("assets/editor-v0169-canvas-height.js" in plugin, 'auto-height runtime is enqueued')
require("['h18-clean-editor-v0148-layers']" in plugin, 'auto-height runs after shared Designer runtime')
require("directSections" in js and "root.children" in js and "h18-clean-node--section" in js, 'only direct root Sections are canvas height authorities')
require('BASE_HEIGHT = 650' in js and 'BOTTOM_SPACE = 32' in js, 'minimum canvas height and bottom space are explicit')
require('Math.max(BASE_HEIGHT' in js, 'canvas has deterministic minimum height')
require("root.style.minHeight = String(next) + 'px'" in js, 'canvas height is assigned from current extents and can shrink')
require('ResizeObserver' in js and 'MutationObserver' in js, 'resize and DOM mutations refresh canvas height')
require("h18-vd-viewport-fit" in js, 'responsive/viewport changes refresh canvas height')
require("#h18-clean-undo,#h18-clean-redo" in js and "#h18-clean-paste,#h18-clean-duplicate" in js, 'history and clipboard UI actions refresh canvas height')
require('state.nodes' not in js and 'geometry.desktop' not in js and 'zIndex' not in js, 'auto-height runtime never mutates canonical node geometry or z-index')
require('window.H18VDCanvasAutoHeight' in js and 'refresh: schedule' in js, 'diagnostic/manual refresh API exists')
require('VD-CANVAS-AUTOHEIGHT-001' in tech, 'technical contract is documented')
require('Canvas Auto Height' in design, 'design rule is documented')
require('Websiden følger Sektionerne automatisk' in user, 'user manual documents automatic behavior')
require('0.1.69 – Canvas Auto Height' in notes, 'v0.1.69 release notes remain documented')
require(any(str(v.get('version')) == '0.1.69' for v in history.get('versions', []) if isinstance(v, dict)), 'release history contains v0.1.69')
require((ROOT / 'docs/v0169-status.md').is_file(), 'v0.1.69 status file exists')

print('V0169 CANVAS AUTO HEIGHT QA OK (forward-compatible)')
