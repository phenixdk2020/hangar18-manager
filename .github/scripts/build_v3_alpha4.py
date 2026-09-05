from pathlib import Path
import hashlib
import re
import subprocess

VERSION = '3.0.0-alpha.4'
DEST = Path('build/visual-designer-manager')

ROUTE_MAP = {
    'h18-clean-manager': 'vdm-manager',
    'h18-clean-editor': 'vdm-editor',
    'h18-clean-vehicles': 'vdm-vehicles',
    'h18-clean-vehicle-fields': 'vdm-vehicle-fields',
    'h18-clean-events': 'vdm-events',
    'h18-clean-event-fields': 'vdm-event-fields',
    'h18-clean-gallery': 'vdm-gallery',
    'h18-clean-data': 'vdm-data',
    'h18-clean-pages': 'vdm-pages',
    'h18-clean-conversion': 'vdm-conversion',
    'h18-clean-menu': 'vdm-menu',
    'h18-clean-header-footer': 'vdm-header-footer',
    'h18-clean-backup': 'vdm-backup',
    'h18-clean-updates': 'vdm-updates',
    'h18-clean-log': 'vdm-log',
    'h18-clean-manual': 'vdm-manual',
    'h18-clean-export': 'vdm-export',
    'h18-clean-theme': 'vdm-theme',
}

COMPAT_PHP = r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Compatibility;

/**
 * Temporary V3 compatibility layer for pre-Alpha.4 WordPress admin URLs.
 *
 * Canonical runtime links use vdm-* page slugs. Historical h18-clean-* URLs
 * remain accepted as redirects only so bookmarks and old diagnostic links do
 * not break during the staged V3 cutover.
 */
final class AdminRouteCompatibility
{
    /** @var array<string,string> */
    private const LEGACY_TO_CANONICAL = [
        'h18-clean-manager' => 'vdm-manager',
        'h18-clean-editor' => 'vdm-editor',
        'h18-clean-vehicles' => 'vdm-vehicles',
        'h18-clean-vehicle-fields' => 'vdm-vehicle-fields',
        'h18-clean-events' => 'vdm-events',
        'h18-clean-event-fields' => 'vdm-event-fields',
        'h18-clean-gallery' => 'vdm-gallery',
        'h18-clean-data' => 'vdm-data',
        'h18-clean-pages' => 'vdm-pages',
        'h18-clean-conversion' => 'vdm-conversion',
        'h18-clean-menu' => 'vdm-menu',
        'h18-clean-header-footer' => 'vdm-header-footer',
        'h18-clean-backup' => 'vdm-backup',
        'h18-clean-updates' => 'vdm-updates',
        'h18-clean-log' => 'vdm-log',
        'h18-clean-manual' => 'vdm-manual',
        'h18-clean-export' => 'vdm-export',
        'h18-clean-theme' => 'vdm-theme',
    ];

    public static function register(): void
    {
        add_action('admin_init', [self::class, 'redirectLegacyRoute'], 0);
    }

    public static function redirectLegacyRoute(): void
    {
        global $pagenow;
        if (!is_admin() || $pagenow !== 'admin.php') {
            return;
        }

        $legacy = sanitize_key((string) wp_unslash($_GET['page'] ?? ''));
        $canonical = self::LEGACY_TO_CANONICAL[$legacy] ?? '';
        if ($canonical === '') {
            return;
        }

        $args = ['page' => $canonical];
        foreach ($_GET as $key => $value) {
            if ((string) $key === 'page' || !is_scalar($value)) {
                continue;
            }
            $cleanKey = sanitize_key((string) $key);
            if ($cleanKey === '') {
                continue;
            }
            $args[$cleanKey] = sanitize_text_field((string) wp_unslash((string) $value));
        }

        wp_safe_redirect(add_query_arg($args, admin_url('admin.php')), 302, 'Visual Designer Manager V3');
        exit;
    }

    public static function canonical(string $legacy): string
    {
        $legacy = sanitize_key($legacy);
        return self::LEGACY_TO_CANONICAL[$legacy] ?? $legacy;
    }

    private function __construct() {}
}
'''


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def route_pattern(token: str) -> re.Pattern[str]:
    # Do not rewrite CSS/DOM/asset identifiers such as h18-clean-menu-preview
    # or h18-clean-editor-v018-core. Only standalone route/handle tokens move.
    return re.compile(r'(?<![A-Za-z0-9-])' + re.escape(token) + r'(?![A-Za-z0-9-])')


# Alpha.4 is layered on the already verified Alpha.3 deterministic build.
subprocess.run(['python3', '.github/scripts/build_v3_alpha3.py'], check=True)

protected = [
    'assets/editor-v018-core.js',
    'assets/editor.css',
    'assets/frontend.css',
    'src/Frontend/Renderer.php',
    'src/Frontend/ResponsiveRenderer.php',
    'src/Model/LayoutModel.php',
    'src/Migration/V3StorageMigration.php',
]
protected_before = {rel: sha(DEST / rel) for rel in protected}

# Rewrite standalone WordPress admin page slugs in PHP and admin JS only.
changed = []
for path in sorted(DEST.rglob('*')):
    if not path.is_file() or path.suffix.lower() not in {'.php', '.js'}:
        continue
    text = path.read_text(encoding='utf-8')
    transformed = text
    for old, new in ROUTE_MAP.items():
        transformed = route_pattern(old).sub(new, transformed)
    if transformed != text:
        path.write_text(transformed, encoding='utf-8')
        changed.append(path.relative_to(DEST).as_posix())

main = DEST / 'visual-designer-manager.php'
main_text = main.read_text(encoding='utf-8')
for old, new in [
    (' * Version: 3.0.0-alpha.3', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.3');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.3');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main_text.count(old) != 1:
        raise SystemExit(f'Alpha.4 version token mismatch: {old!r} count={main_text.count(old)}')
    main_text = main_text.replace(old, new)

require_anchor = "require_once VDM_DIR . 'src/Compatibility/LegacyStorageBridge.php';"
if main_text.count(require_anchor) != 1:
    raise SystemExit('AdminRouteCompatibility require anchor mismatch')
main_text = main_text.replace(
    require_anchor,
    require_anchor + "\nrequire_once VDM_DIR . 'src/Compatibility/AdminRouteCompatibility.php';",
)
register_anchor = "add_action('plugins_loaded', static function (): void {"
if main_text.count(register_anchor) != 1:
    raise SystemExit('AdminRouteCompatibility register anchor mismatch')
main_text = main_text.replace(
    register_anchor,
    register_anchor + "\n    \\VisualDesignerManager\\Compatibility\\AdminRouteCompatibility::register();",
)
main.write_text(main_text, encoding='utf-8')

compat = DEST / 'src/Compatibility/AdminRouteCompatibility.php'
compat.write_text(COMPAT_PHP, encoding='utf-8')

# Every canonical page slug must now occur in active runtime.
runtime_text = ''
for path in sorted(DEST.rglob('*')):
    if path.is_file() and path.suffix.lower() in {'.php', '.js'} and path != compat:
        runtime_text += '\n' + path.read_text(encoding='utf-8')
for old, new in ROUTE_MAP.items():
    if new not in runtime_text:
        raise SystemExit(f'Canonical admin route missing after Alpha.4 transform: {new}')
    if route_pattern(old).search(runtime_text):
        raise SystemExit(f'Legacy standalone admin route remains outside compatibility layer: {old}')

# Compatibility bridge must contain every historical route and no destructive behavior.
compat_text = compat.read_text(encoding='utf-8')
for old, new in ROUTE_MAP.items():
    if f"'{old}' => '{new}'" not in compat_text:
        raise SystemExit(f'Compatibility route missing: {old} -> {new}')
for forbidden in ('delete_option(', 'delete_post_meta(', 'wp_delete_post(', 'remove_menu_page('):
    if forbidden in compat_text:
        raise SystemExit(f'Destructive/unwanted compatibility operation found: {forbidden}')
if "wp_safe_redirect" not in compat_text or "302" not in compat_text:
    raise SystemExit('Legacy route redirect contract missing')

# The V1 Designer, renderer, layout and Alpha.3 storage migration are protected.
for rel, before in protected_before.items():
    after = sha(DEST / rel)
    if before != after:
        raise SystemExit(f'Protected V1/Alpha.3 runtime changed during route cutover: {rel}')

if 'src/Admin/AdminController.php' not in changed or 'src/Admin/EditorController.php' not in changed:
    raise SystemExit('Expected core admin route files were not transformed')

print('V3 Alpha.4 admin route cutover: PASS')
print('Canonical vdm-* WordPress admin routes: PASS')
print('Legacy h18-clean-* URL redirect compatibility: PASS')
print('V1 Designer/renderer/layout and Alpha.3 storage migration preserved: PASS')
