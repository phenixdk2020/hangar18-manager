from pathlib import Path

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


require(PLUGIN, ' * Version: 0.1.62', 'plugin header is 0.1.62')
require(PLUGIN, "H18_CLEAN_VERSION', '0.1.62'", 'runtime version is 0.1.62')
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
print('v0.1.62 page duplicate QA PASS')
