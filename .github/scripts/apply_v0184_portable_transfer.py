from pathlib import Path
import json

plugin = Path('clean/hangar18-manager/hangar18-manager.php')
s = plugin.read_text(encoding='utf-8')
if 'Version: 0.1.84' not in s:
    s = s.replace(' * Version: 0.1.83', ' * Version: 0.1.84', 1)
old = """define('H18_CLEAN_VERSION', '0.1.83');
define('H18_CLEAN_FILE', __FILE__);
define('H18_CLEAN_DIR', plugin_dir_path(__FILE__));
define('H18_CLEAN_URL', plugin_dir_url(__FILE__));
"""
new = """define('VDM_VERSION', '0.1.84');
define('VDM_FILE', __FILE__);
define('VDM_DIR', plugin_dir_path(__FILE__));
define('VDM_URL', plugin_dir_url(__FILE__));

/* Deprecated compatibility aliases. New code must use VDM_* constants. */
define('H18_CLEAN_VERSION', '0.1.84');
define('H18_CLEAN_FILE', VDM_FILE);
define('H18_CLEAN_DIR', VDM_DIR);
define('H18_CLEAN_URL', VDM_URL);
"""
if "define('VDM_VERSION', '0.1.84');" not in s:
    if old not in s:
        raise SystemExit('Expected v0.1.83 constant block not found')
    s = s.replace(old, new, 1)

compat_req = "require_once VDM_DIR . 'src/Compatibility/LegacyStorageBridge.php';\n"
if compat_req not in s:
    needle = "require_once H18_CLEAN_DIR . 'src/Icons/IconRegistry.php';\n"
    if needle not in s:
        raise SystemExit('Bootstrap IconRegistry require anchor missing')
    s = s.replace(needle, compat_req + needle, 1)

transfer_req = "require_once VDM_DIR . 'src/Admin/PortableTransferController.php';\n"
if transfer_req not in s:
    needle = "require_once H18_CLEAN_DIR . 'src/Admin/ExportController.php';\n"
    if needle not in s:
        raise SystemExit('Bootstrap ExportController require anchor missing')
    s = s.replace(needle, needle + transfer_req, 1)

transfer_register = "    \\VisualDesignerManager\\Admin\\PortableTransferController::register();\n"
if transfer_register not in s:
    needle = "    \\VisualDesignerManager\\Admin\\ExportController::register();\n"
    if needle not in s:
        raise SystemExit('Bootstrap ExportController register anchor missing')
    s = s.replace(needle, needle + transfer_register, 1)
plugin.write_text(s, encoding='utf-8')

history_path = Path('clean/hangar18-manager/release-history.json')
history = json.loads(history_path.read_text(encoding='utf-8'))
versions = history.setdefault('versions', [])
if not any(str(row.get('version')) == '0.1.84' for row in versions if isinstance(row, dict)):
    versions.insert(0, {
        'version': '0.1.84',
        'date': '2026-09-02',
        'items': [
            'VD-PORTABLE-TRANSFER-001: komplet portabel siteeksport og verificeret ZIP-import med schema 1.0.',
            'Eksporten indeholder sider/layouts og historik, Header/Footer-templates, modulrecords, køretøjs-/eventfelter, navigation og originale mediefiler.',
            'Import har read-only forhåndskontrol, SHA-256-verifikation, ZIP path-traversal-beskyttelse og ID/URL-remapping mellem sites.',
            'Nye runtime-identifikatorer bruger VDM-navngivning; historiske H18/Clean storage-nøgler er isoleret i Compatibility-laget.',
            'VDM_VERSION/VDM_FILE/VDM_DIR/VDM_URL er nye kanoniske konstanter; H18_CLEAN_* bevares midlertidigt som deprecated compatibility-aliases.'
        ]
    })
history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

notes_path = Path('clean-release-notes.html')
notes = notes_path.read_text(encoding='utf-8') if notes_path.exists() else ''
section = ('<section data-version="0.1.84"><h2>0.1.84</h2><ul>'
           '<li>Ny komplet <strong>Eksport / import</strong> for en portabel Visual Designer Manager sitepakke.</li>'
           '<li>ZIP-pakken indeholder sider og layouts med historik, Header/Footer-templates, moduldata, feltdefinitioner, navigation og originale mediefiler.</li>'
           '<li>Import starter med read-only forhåndskontrol og verificerer schema, sikre ZIP-stier og SHA-256 før data kan importeres.</li>'
           '<li>Side-, menu-, template- og mediereferencer remappes ved import til et andet site.</li>'
           '<li>Nye kanoniske runtime-konstanter hedder VDM_*; gamle H18/Clean-storageidentifikatorer er kun compatibility/migrationslag.</li>'
           '</ul></section>\n')
if 'data-version="0.1.84"' not in notes:
    notes = section + notes
notes_path.write_text(notes, encoding='utf-8')

status_path = Path('docs/v0184-status.md')
status_path.write_text('''# Visual Designer Manager v0.1.84 – Portable site transfer

Status: release candidate

## Leverance

- Portabel siteeksport i ZIP med schema 1.0.
- Read-only import-preflight før ændringer.
- SHA-256-verifikation af alle manifest-filer.
- ZIP path-traversal- og størrelsesgrænser.
- Sider/layouts + versionshistorik.
- Header/Footer-templates + historik og standardvalg.
- Modulrecords samt køretøjs- og eventfelter.
- Navigation og menuplaceringer.
- Originale mediefiler med attachment-ID/URL-remapping.
- Nye VDM_* runtime-konstanter med deprecated compatibility-aliases.
- Legacy-storage er isoleret i `src/Compatibility/LegacyStorageBridge.php`.

## Ikke inkluderet i den portable pakke

WordPress core, brugerkonti/adgangskoder, database-login, API-hemmeligheder og andre plugins' filer.
''', encoding='utf-8')
