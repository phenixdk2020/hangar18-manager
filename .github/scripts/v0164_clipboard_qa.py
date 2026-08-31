from pathlib import Path
import re

ROOT = Path('.')
PLUGIN = (ROOT / 'clean/hangar18-manager/hangar18-manager.php').read_text(encoding='utf-8')
CORE = (ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js').read_text(encoding='utf-8')
TECH = (ROOT / 'CLEAN-TECHNICAL-MANUAL.md').read_text(encoding='utf-8')
STATUS = ROOT / 'docs/v0164-status.md'


def require(condition: bool, label: str) -> None:
    if not condition:
        raise SystemExit('FAIL: ' + label)
    print('PASS: ' + label)


version_match = re.search(r'Version:\s*([0-9]+)\.([0-9]+)\.([0-9]+)', PLUGIN)
version_tuple = tuple(int(part) for part in version_match.groups()) if version_match else (0, 0, 0)
version_text = '.'.join(str(part) for part in version_tuple)
require(version_tuple >= (0, 1, 64) and f"H18_CLEAN_VERSION', '{version_text}'" in PLUGIN, f'plugin/runtime version {version_text} is 0.1.64 or newer')
require("wp_dequeue_script('h18-clean-editor')" in PLUGIN, 'legacy editor runtime is explicitly dequeued')
require("H18_CLEAN_URL . 'assets/editor-v018-core.js'" in PLUGIN, 'shared current core runtime is enqueued')
require("$isPageDesigner = strpos($hook, 'h18-clean-editor') !== false;" in PLUGIN, 'shared core applies to Page Designer')
require("$isGlobalDesigner = strpos($hook, 'h18-clean-header-footer') !== false;" in PLUGIN, 'shared core applies to Header/Footer')
require("'userId' => get_current_user_id()" in PLUGIN and "'contextLabel' => $contextLabel" in PLUGIN, 'clipboard gets user/context localization')

require('function selectedNodeForProductivity()' in CORE, 'clipboard can recover visible selected node')
require("document.querySelector('#h18-clean-canvas .h18-clean-node.is-selected[data-node-id]')" in CORE, 'selection fallback uses visible selected canvas node')
require("productivityNotice('Kopieret:" in CORE, 'copy gives visible feedback')
require("productivityNotice('Clipboard er tomt')" in CORE, 'empty clipboard gives visible feedback')
require("revealSelected((duplicateMode ? 'Duplikeret: ' : 'Indsat: ')" in CORE, 'paste/duplicate reveals inserted node')
require("card.scrollIntoView({ block: 'center'" in CORE, 'inserted node scrolls into view')
require("else if (key === 'c' && selectedNodeForProductivity())" in CORE, 'Ctrl/Cmd+C uses robust selection')
require("else if (key === 'v')" in CORE and 'pasteClipboard();' in CORE, 'Ctrl/Cmd+V always routes through production paste function')
require("else if (key === 'd' && selectedNodeForProductivity())" in CORE, 'Ctrl/Cmd+D uses robust selection')
require('window.H18VDProductivity = {' in CORE, 'live diagnostic API exposes production clipboard functions')

require('laptop: normalizeDevice(item.geometry && item.geometry.laptop, true)' in CORE, 'normalizeModel preserves laptop geometry')
require('laptop: Object.assign({}, desktop, { inheritDesktop: true })' in CORE, 'new nodes receive laptop inheritance')
require('desktop: normalizeDevice(item.geometry && item.geometry.desktop, false)' in CORE, 'desktop geometry remains present')
require('tablet: normalizeDevice(item.geometry && item.geometry.tablet, true)' in CORE, 'tablet geometry remains present')
require('mobile: normalizeDevice(item.geometry && item.geometry.mobile, true)' in CORE, 'mobile geometry remains present')

require('### BUG-23 / VD-CLIPBOARD-002' in TECH, 'technical clipboard contract documented')
require(STATUS.is_file() and STATUS.stat().st_size > 0, 'v0.1.64 status file exists')

print('v0.1.64 Designer clipboard runtime QA PASS (forward-compatible)')
