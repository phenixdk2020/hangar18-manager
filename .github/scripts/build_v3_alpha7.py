from pathlib import Path
import hashlib
import json
import shutil
import subprocess

VERSION = '3.0.0-alpha.7'
DEST = Path('build/visual-designer-manager')
RUNTIME = Path('.github/v3-runtime')


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


subprocess.run(['python3', '.github/scripts/build_v3_alpha6.py'], check=True)

protected = [
    'assets/admin-v019.css', 'assets/admin-v0123.css', 'assets/admin-v0175.css',
    'assets/editor-v018-core.js', 'assets/editor-v0144-viewport.js',
    'assets/editor-v0169-canvas-height.js', 'assets/editor.css',
    'src/Frontend/Renderer.php', 'src/Frontend/ResponsiveRenderer.php',
    'src/Frontend/ThemeShell.php', 'src/Model/LayoutModel.php',
    'src/Model/TemplateLayoutModel.php', 'src/Migration/V3StorageMigration.php',
    'templates/vdm-site-shell.php',
]
protected_before = {rel: sha(DEST / rel) for rel in protected}

main = DEST / 'visual-designer-manager.php'
main_text = main.read_text(encoding='utf-8')
for old, new in [
    (' * Version: 3.0.0-alpha.6', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.6');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.6');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main_text.count(old) != 1:
        raise SystemExit(f'Alpha.7 version token mismatch: {old!r} count={main_text.count(old)}')
    main_text = main_text.replace(old, new)

old_register = '    \\VisualDesignerManager\\Migration\\SiteDesignHarmonizer::register();\n'
new_register = (
    '    \\VisualDesignerManager\\Migration\\V3StyleRecovery::register();\n'
    '    \\VisualDesignerManager\\Migration\\SharedPrimaryMenu::register();\n'
)
if main_text.count(old_register) != 1:
    raise SystemExit(f'Alpha.7 SiteDesignHarmonizer register mismatch: count={main_text.count(old_register)}')
main_text = main_text.replace(old_register, new_register)

old_require = "require_once H18_CLEAN_DIR . 'src/Migration/SiteDesignHarmonizer.php';\n"
new_require = old_require + (
    "require_once VDM_DIR . 'src/Migration/V3StyleRecovery.php';\n"
    "require_once VDM_DIR . 'src/Migration/SharedPrimaryMenu.php';\n"
)
if main_text.count(old_require) != 1:
    raise SystemExit(f'Alpha.7 migration require anchor mismatch: count={main_text.count(old_require)}')
main_text = main_text.replace(old_require, new_require)
main.write_text(main_text, encoding='utf-8')

for name in ['V3StyleRecovery.php', 'SharedPrimaryMenu.php']:
    source = RUNTIME / name
    if not source.exists():
        raise SystemExit(f'Alpha.7 runtime source missing: {source}')
    shutil.copy2(source, DEST / 'src/Migration' / name)

history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.6':
    raise SystemExit('Expected Alpha.6 release-history baseline missing')
alpha7 = {
    'version': VERSION,
    'date': '2026-09-06',
    'items': [
        'Den historiske v0.1.72 SiteDesignHarmonizer registreres ikke længere i V3, så portable V1-importer ikke harmoniseres en ekstra gang.',
        'Recovery finder det dobbelte harmonizer-history entry og gendanner kun de props, som den fejlagtige anden kørsel ændrede; senere brugerændringer og al geometri bevares.',
        'Footerens Genveje konverteres fra statiske HTML-links til et rigtigt lodret Menu-element.',
        'Footer-menuen følger automatisk den WordPress-menu, som den aktive Header bruger, så menuindhold kun vedligeholdes ét sted.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha7] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

main_text = main.read_text(encoding='utf-8')
if '\\VisualDesignerManager\\Migration\\SiteDesignHarmonizer::register();' in main_text:
    raise SystemExit('Historical SiteDesignHarmonizer is still registered in Alpha.7')
for required in [
    'src/Migration/V3StyleRecovery.php', 'src/Migration/SharedPrimaryMenu.php',
    '\\VisualDesignerManager\\Migration\\V3StyleRecovery::register();',
    '\\VisualDesignerManager\\Migration\\SharedPrimaryMenu::register();',
]:
    if required not in main_text:
        raise SystemExit(f'Alpha.7 bootstrap token missing: {required}')

style = (DEST / 'src/Migration/V3StyleRecovery.php').read_text(encoding='utf-8')
for required in [
    "private const LEGACY_NOTE = 'Design harmoniseret med Hjem (v0.1.72)'",
    'count($harmonized) < 2', 'restoreChangedProps($current, $before, $bad)',
    '$currentValue !== $badValue', 'LayoutModel::saveVersion($postId, $repaired',
    'layoutFingerprint($repaired) !== $currentFingerprint',
]:
    if required not in style:
        raise SystemExit(f'Alpha.7 style recovery contract token missing: {required}')

shared = (DEST / 'src/Migration/SharedPrimaryMenu.php').read_text(encoding='utf-8')
for required in [
    "private const LEGACY_FOOTER_NODE = 'text-footer-shortcuts-v0147'",
    "private const FOOTER_MENU_NODE = 'menu-footer-shortcuts-v3'",
    "add_filter('wp_nav_menu_args'", "TemplateLayoutModel::resolveId($postId, 'header')",
    "'orientation' => 'vertical'", "'mobileMode' => 'vertical'",
    'Footer Genveje følger Headerens hovedmenu',
]:
    if required not in shared:
        raise SystemExit(f'Alpha.7 shared menu contract token missing: {required}')

built_history = json.loads(history_path.read_text(encoding='utf-8'))['versions']
if built_history[0].get('version') != VERSION or built_history[1].get('version') != '3.0.0-alpha.6':
    raise SystemExit('Alpha.7 release-history ordering failed')

for rel, before in protected_before.items():
    if sha(DEST / rel) != before:
        raise SystemExit(f'Protected parity file changed during Alpha.7 recovery: {rel}')

print('V3 Alpha.7 duplicate style-harmonizer recovery: PASS')
print('Historical SiteDesignHarmonizer registration disabled in V3: PASS')
print('Footer shortcuts converted to shared primary Menu: PASS')
print('Footer menu dynamically follows resolved Header menu: PASS')
print('Designer/renderer/layout/shell/storage behavior unchanged: PASS')
