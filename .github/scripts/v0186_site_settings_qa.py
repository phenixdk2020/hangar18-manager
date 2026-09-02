from pathlib import Path
import json
import re

root = Path('.')
plugin = (root / 'clean/hangar18-manager/hangar18-manager.php').read_text(encoding='utf-8')
controller = (root / 'clean/hangar18-manager/src/Admin/SiteSettingsController.php').read_text(encoding='utf-8')
transfer = (root / 'clean/hangar18-manager/src/Admin/PortableTransferController.php').read_text(encoding='utf-8')

for needle in [
    'Version: 0.1.86',
    "define('VDM_VERSION', '0.1.86');",
    "src/Admin/SiteSettingsController.php",
    r'\VisualDesignerManager\Admin\SiteSettingsController::register();',
]:
    if needle not in plugin:
        raise SystemExit(f'Missing v0.1.86 bootstrap requirement: {needle}')

for needle in [
    "private const PAGE = 'vdm-site-settings';",
    "private const SAVE_ACTION = 'vdm_save_site_settings';",
    "get_option('blogname'",
    "get_option('blogdescription'",
    "update_option('blogname'",
    "update_option('blogdescription'",
    "OPTION_ORGANIZATION = 'vdm_organization_name'",
    "OPTION_CONTACT_EMAIL = 'vdm_contact_email'",
    "OPTION_CONTACT_PHONE = 'vdm_contact_phone'",
    "wp_enqueue_media();",
    "set_theme_mod('custom_logo'",
    "update_option('site_icon'",
    'My new WordPress installation',
]:
    if needle not in controller:
        raise SystemExit(f'Missing SiteSettings requirement: {needle}')

if re.search(r'(?i)(h18|hangar18|clean[_-]|\bclean\b)', controller):
    raise SystemExit('Legacy/site-specific naming leaked into new SiteSettingsController')

for needle in [
    "'siteIdentity' => [",
    "'siteTitle' => (string) get_option('blogname', '')",
    "'tagline' => (string) get_option('blogdescription', '')",
    "'customLogoSourceId' => (int) get_theme_mod('custom_logo', 0)",
    "'siteIconSourceId' => (int) get_option('site_icon', 0)",
    'self::applySiteSettings($site, $pageMap, $mediaMap);',
    'private static function applySiteSettings(array $site, array $pageMap, array $mediaMap): void',
    "isset($settings['siteIdentity'])",
    "set_theme_mod('custom_logo', (int) $mediaMap[$sourceLogo])",
    "update_option('site_icon', (int) $mediaMap[$sourceIcon])",
    'Pakken har ikke eksplicit site-identitet',
]:
    if needle not in transfer:
        raise SystemExit(f'Missing portable identity requirement: {needle}')

apply_start = transfer.find('    private static function applySiteSettings(')
apply_end = transfer.find('    private static function remapValue(', apply_start)
apply_block = transfer[apply_start:apply_end]
if "['source']['name']" in apply_block or "['source'][\"name\"]" in apply_block:
    raise SystemExit('Legacy package source.name must not be used as implicit identity fallback')

history = json.loads((root / 'clean/hangar18-manager/release-history.json').read_text(encoding='utf-8'))
if not history.get('versions') or history['versions'][0].get('version') != '0.1.86':
    raise SystemExit('release-history.json is not headed by v0.1.86')
if 'data-version="0.1.86"' not in (root / 'clean-release-notes.html').read_text(encoding='utf-8'):
    raise SystemExit('v0.1.86 release notes missing')
if not (root / 'docs/v0186-status.md').is_file():
    raise SystemExit('v0.1.86 status document missing')

updater = json.loads((root / 'clean-update.json').read_text(encoding='utf-8'))
if tuple(map(int, updater['version'].split('.'))) < (0, 1, 85):
    raise SystemExit('Updater regressed below v0.1.85')
if tuple(map(int, updater['version'].split('.'))) > (0, 1, 86):
    raise SystemExit('Updater is unexpectedly ahead of candidate')

print('Visual Designer Manager v0.1.86 SITE SETTINGS QA: PASS')
