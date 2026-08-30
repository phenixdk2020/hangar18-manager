from pathlib import Path
import re

ROOT = Path('.')
ADMIN = ROOT / 'clean/hangar18-manager/src/Admin/AdminController.php'
PLUGIN = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
GLOBAL = ROOT / 'clean/hangar18-manager/src/Admin/GlobalDesignerController.php'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
HF = ROOT / 'docs/HEADER-FOOTER-SPEC.md'
STATUS = ROOT / 'docs/v0162-status.md'


def require(path: Path, needle: str, label: str) -> None:
    text = path.read_text(encoding='utf-8')
    if needle not in text:
        raise SystemExit(f'FAIL: {label}')
    print(f'PASS: {label}')


def version_tuple(value: str) -> tuple[int, int, int]:
    parts = value.split('.')
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise SystemExit(f'FAIL: invalid plugin version {value!r}')
    return tuple(int(part) for part in parts)


plugin_text = PLUGIN.read_text(encoding='utf-8')
header_match = re.search(r'^ \* Version: ([0-9]+\.[0-9]+\.[0-9]+)$', plugin_text, re.MULTILINE)
runtime_match = re.search(r"define\('H18_CLEAN_VERSION', '([0-9]+\.[0-9]+\.[0-9]+)'\);", plugin_text)
if not header_match or not runtime_match:
    raise SystemExit('FAIL: plugin version markers are missing')
header_version = header_match.group(1)
runtime_version = runtime_match.group(1)
if version_tuple(header_version) < (0, 1, 62):
    raise SystemExit(f'FAIL: plugin version {header_version} is older than 0.1.62')
if runtime_version != header_version:
    raise SystemExit(f'FAIL: runtime version {runtime_version} does not match plugin header {header_version}')
print(f'PASS: plugin/runtime version {header_version} is 0.1.62 or newer')

require(ADMIN, "private const DUPLICATE_PAGE_ACTION = 'h18_clean_duplicate_page';", 'duplicate action constant exists')
require(ADMIN, "private const DUPLICATE_PAGE_NONCE = 'h18_clean_duplicate_page';", 'duplicate nonce exists')
require(ADMIN, "add_action('admin_post_' . self::DUPLICATE_PAGE_ACTION, [self::class, 'duplicatePage']);", 'duplicate handler is registered')
require(ADMIN, '<summary class="button">Kopiér</summary>', 'copy action is shown under Sider')
require(ADMIN, 'name="new_page_title" required', 'new page name is required')
require(ADMIN, 'public static function duplicatePage(): void', 'duplicate page handler exists')
require(ADMIN, "'post_status' => 'draft'", 'copies are always drafts')
require(ADMIN, "self::uniquePageSlug(sanitize_title($newTitle))", 'copy gets a unique slug')
require(ADMIN, "TemplateLayoutModel::setPageChoice($newPostId, 'header'", 'Header page choice is copied')
require(ADMIN, "TemplateLayoutModel::setPageChoice($newPostId, 'footer'", 'Footer page choice is copied')
require(ADMIN, 'LayoutModel::saveVersion(', 'Designer copy starts through saveVersion')
require(ADMIN, '$newVersion !== 1', 'Designer copy must start at v1')
require(ADMIN, 'LayoutModel::structuralDigest($sourceModel)', 'Designer source digest is verified')
require(ADMIN, "get_post_meta($sourceId, '_wp_page_template', true)", 'WordPress page template is copied')
require(ADMIN, 'get_post_thumbnail_id($sourceId)', 'featured image is copied')
require(ADMIN, 'wp_trash_post($newPostId);', 'failed copy is rolled back')
require(GLOBAL, 'h18-manager-badge is-ok">Klar', 'Header/Footer Admin status is Klar')
require(TECH, '### VD-PAGE-DUPLICATE-001', 'technical duplicate-page contract is documented')
require(HF, '## 16. Klar betyder vedligeholdt – fælles Designer-paritet', 'Header/Footer shared Designer maintenance rule is documented')
if not STATUS.is_file() or STATUS.stat().st_size == 0:
    raise SystemExit('FAIL: v0.1.62 status file exists')
print('PASS: v0.1.62 status file exists')
print('v0.1.62 page duplicate QA PASS (forward-compatible)')
