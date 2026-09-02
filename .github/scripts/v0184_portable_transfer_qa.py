from pathlib import Path
import json
import re

root = Path('.')
plugin = (root / 'clean/hangar18-manager/hangar18-manager.php').read_text(encoding='utf-8')
controller_path = root / 'clean/hangar18-manager/src/Admin/PortableTransferController.php'
bridge_path = root / 'clean/hangar18-manager/src/Compatibility/LegacyStorageBridge.php'
controller = controller_path.read_text(encoding='utf-8')
bridge = bridge_path.read_text(encoding='utf-8')


def version_tuple(value: str):
    parts = value.split('.')
    return tuple(int(part) for part in parts)


header_match = re.search(r'^\s*\*\s*Version:\s*([0-9]+(?:\.[0-9]+){2})\s*$', plugin, re.MULTILINE)
vdm_match = re.search(r"define\('VDM_VERSION',\s*'([0-9]+(?:\.[0-9]+){2})'\);", plugin)
legacy_match = re.search(r"define\('H18_CLEAN_VERSION',\s*'([0-9]+(?:\.[0-9]+){2})'\);", plugin)
if not header_match or not vdm_match or not legacy_match:
    raise SystemExit('Plugin version declarations are incomplete')

runtime_version = header_match.group(1)
if version_tuple(runtime_version) < (0, 1, 84):
    raise SystemExit(f'Portable transfer requires runtime >= 0.1.84, got {runtime_version}')
if vdm_match.group(1) != runtime_version:
    raise SystemExit('VDM_VERSION does not match plugin header version')
if legacy_match.group(1) != runtime_version:
    raise SystemExit('Deprecated H18_CLEAN_VERSION alias does not match runtime version')

required_plugin = [
    "define('VDM_FILE', __FILE__);",
    "define('VDM_DIR', plugin_dir_path(__FILE__));",
    "define('VDM_URL', plugin_dir_url(__FILE__));",
    "src/Compatibility/LegacyStorageBridge.php",
    "src/Admin/PortableTransferController.php",
    r'\VisualDesignerManager\Admin\PortableTransferController::register();',
]
for needle in required_plugin:
    if needle not in plugin:
        raise SystemExit(f'Missing bootstrap requirement: {needle}')

required_controller = [
    "private const PAGE = 'vdm-transfer';",
    "private const EXPORT_ACTION = 'vdm_export_portable_site';",
    "private const PREFLIGHT_ACTION = 'vdm_import_preflight';",
    "private const IMPORT_ACTION = 'vdm_import_portable_site';",
    "private const FORMAT = 'Visual Designer Manager Portable Site';",
    "private const SCHEMA = '1.0';",
    "manifest.json",
    "pages/pages.json",
    "templates/templates.json",
    "modules/modules.json",
    "modules/custom-fields.json",
    "navigation/navigation.json",
    "media/media-index.json",
    "migration/legacy-map.json",
    "hash_equals",
    "hashZipEntry",
    "safeArchivePath",
    "MAX_UNCOMPRESSED_BYTES",
    "LegacyStorageBridge::importTemplateSnapshot",
    "ModuleStore::findByRecordId",
    "VehicleFieldRegistry::save",
    "EventFieldRegistry::save",
    "wp_generate_attachment_metadata",
    "$sameSite",
]
for needle in required_controller:
    if needle not in controller:
        raise SystemExit(f'Missing portable transfer requirement: {needle}')

start = controller.find('    private static function legacyMap(): array')
end = controller.find('    private static function manifest(', start)
if start < 0 or end < 0:
    raise SystemExit('legacyMap boundary not found')
active_controller = controller[:start] + controller[end:]
if re.search(r'(?i)(h18|hangar18|clean[_-]|\bclean\b)', active_controller):
    matches = sorted(set(m.group(0) for m in re.finditer(r'(?i)(h18|hangar18|clean[_-]|\bclean\b)', active_controller)))
    raise SystemExit('Legacy naming leaked into new controller outside migration metadata: ' + ', '.join(matches))

if 'namespace VisualDesignerManager\\Compatibility;' not in bridge:
    raise SystemExit('Compatibility bridge namespace missing')
for needle in [
    'h18_clean_global_template_registry_v1',
    'h18_clean_global_template_defaults_v1',
    "return 'h18_clean_tpl_'",
    'importTemplateSnapshot',
    'importTemplateDefaults',
]:
    if needle not in bridge:
        raise SystemExit(f'Missing legacy bridge requirement: {needle}')

history = json.loads((root / 'clean/hangar18-manager/release-history.json').read_text(encoding='utf-8'))
versions = [str(item.get('version', '')) for item in history.get('versions', [])]
if '0.1.84' not in versions:
    raise SystemExit('release-history.json no longer contains the v0.1.84 portable-transfer release')
if not versions or version_tuple(versions[0]) < (0, 1, 84):
    raise SystemExit('release-history.json is older than v0.1.84')

notes = (root / 'clean-release-notes.html').read_text(encoding='utf-8')
if 'data-version="0.1.84"' not in notes:
    raise SystemExit('v0.1.84 release notes missing')
if not (root / 'docs/v0184-status.md').is_file():
    raise SystemExit('v0.1.84 status document missing')

print(f'v0.1.84 portable transfer static QA: OK on runtime {runtime_version}')
