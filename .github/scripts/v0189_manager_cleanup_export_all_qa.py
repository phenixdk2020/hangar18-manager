from pathlib import Path
import json
import re

root = Path('.')
plugin = (root/'clean/hangar18-manager/hangar18-manager.php').read_text(encoding='utf-8')
admin = (root/'clean/hangar18-manager/src/Admin/AdminController.php').read_text(encoding='utf-8')
export = (root/'clean/hangar18-manager/src/Admin/ExportController.php').read_text(encoding='utf-8')
transfer = (root/'clean/hangar18-manager/src/Admin/PortableTransferController.php').read_text(encoding='utf-8')
status_js = (root/'clean/hangar18-manager/assets/admin-v0123.js').read_text(encoding='utf-8')
color_js = (root/'clean/hangar18-manager/assets/editor-v0181-color-picker.js').read_text(encoding='utf-8')
history = json.loads((root/'clean/hangar18-manager/release-history.json').read_text(encoding='utf-8'))
notes = (root/'clean-release-notes.html').read_text(encoding='utf-8')
updater = json.loads((root/'clean-update.json').read_text(encoding='utf-8'))


def ok(cond, label):
    if not cond:
        raise SystemExit('FAIL: ' + label)
    print('PASS:', label)


def version_tuple(value):
    parts = [int(p) for p in re.findall(r'\d+', str(value))[:3]]
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts)


m = re.search(r"define\('VDM_VERSION',\s*'([^']+)'\);", plugin)
ok(bool(m) and version_tuple(m.group(1)) >= (0, 1, 89), 'runtime version >= 0.1.89')

# Conversion remains available only as hidden recovery route.
ok("add_submenu_page(null, 'Konvertering (intern)'" in admin, 'conversion route is hidden')
ok("add_submenu_page(self::MENU, 'Konvertering af sider'" not in admin, 'visible conversion submenu removed')
ok("self::card('Konvertering'" not in admin, 'conversion dashboard card removed')

# Development statuses disappear from the UI, while the old asset may remain as historical source.
ok("wp_enqueue_script('h18-clean-manager-v0123'" not in admin, 'status badge runtime no longer enqueued')
ok('development-status badges are no longer rendered' in admin, 'status retirement documented in runtime')
ok('Under udvikling' in status_js and 'Klar' in status_js, 'historical status asset retained without runtime activation')

# Old combined transfer screen is hidden but import/preflight engine remains functional.
ok("add_submenu_page(\n            null,\n            'Import / recovery'" in transfer, 'old Export/import menu hidden as recovery route')
ok("add_action('admin_post_' . self::PREFLIGHT_ACTION" in transfer, 'import preflight action retained')
ok("add_action('admin_post_' . self::IMPORT_ACTION" in transfer, 'import action retained')
ok('public static function buildPortablePackage(string $targetPath): array' in transfer, 'portable package builder is reusable')
ok("self::addJson($zip, 'site.json'" in transfer, 'portable package includes site settings')
ok("self::addJson($zip, 'pages/pages.json'" in transfer, 'portable package includes pages/layouts/history')
ok("self::addJson($zip, 'templates/templates.json'" in transfer, 'portable package includes Header/Footer templates')
ok("self::addJson($zip, 'modules/modules.json'" in transfer, 'portable package includes module records')
ok("self::addJson($zip, 'modules/custom-fields.json'" in transfer, 'portable package includes custom fields')
ok("self::addJson($zip, 'navigation/navigation.json'" in transfer, 'portable package includes navigation')
ok("self::addJson($zip, 'media/media-index.json'" in transfer, 'portable package includes media')

# Unified Export page and complete bundle.
ok("'all' => 'Alt'" in export, 'Export supports All kind')
ok("self::card('all', 'Eksporter alt'" in export, 'Export All card is active')
ok('Kommer senere' not in export, 'disabled whole-site placeholder removed')
ok("case 'all':" in export, 'Export All execution path exists')
ok("PortableTransferController::buildPortablePackage($portableTmp)" in export, 'Export All reuses canonical portable builder')
ok("'portable-site/' . sanitize_file_name" in export, 'directly importable portable ZIP is nested in total bundle')
ok("'includes' => ['plugin', 'active-theme', 'parent-theme-when-used', 'portable-site']" in export, 'total bundle declares full scope')
ok("H18_CLEAN_DIR" in export and "self::addTheme($zip, $files)" in export, 'total bundle includes plugin and theme')
ok("@unlink($portableTmp)" in export, 'temporary portable ZIP is cleaned up')

# Existing popup color picker must survive this manager cleanup unchanged.
ok("themeToggle.textContent = picker.mode === 'theme' ? 'Farvevælger' : 'Tema';" in color_js, 'v0.1.88 popup color toggle retained')
ok("cancel.textContent='Annuller'" in color_js and "apply.textContent='Anvend'" in color_js, 'popup color actions retained')

ok(any(str(row.get('version')) == '0.1.89' for row in history.get('versions', [])), '0.1.89 remains in release history')
ok('data-version="0.1.89"' in notes, '0.1.89 release notes remain present')
ok((root/'docs/v0189-status.md').is_file(), '0.1.89 status document present')
ok(version_tuple(updater.get('version', '0')) >= (0, 1, 88), 'updater is not older than v0.1.88 baseline')

print('Visual Designer Manager v0.1.89 MANAGER CLEANUP + EXPORT ALL QA: PASS')
