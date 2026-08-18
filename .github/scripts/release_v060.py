from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)


php_path = Path('hangar18-manager.php')
readme_path = Path('readme.txt')
css_path = Path('assets/admin.css')
js_path = Path('assets/admin.js')
sync_path = Path('.github/workflows/sync-release-source.yml')

php = php_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')
css = css_path.read_text(encoding='utf-8')
js = js_path.read_text(encoding='utf-8')
sync = sync_path.read_text(encoding='utf-8')

php = replace_once(php, ' * Version: 0.5.30', ' * Version: 0.6.0', 'plugin header version')
php = replace_once(php, "const VERSION = '0.5.30';", "const VERSION = '0.6.0';", 'plugin version constant')

readme = replace_once(readme, 'Version: 0.5.30', 'Version: 0.6.0', 'readme version')
intro = 'Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.\n'
release_notes = '''\n\n== Version 0.6.0 – Architecture Foundation, UD-060 og større sideeditor ==\n\nNyt:\n- Ny ikke-invasiv Ultimate Designer architecture foundation med namespaces, registries, schema validation, repositories, security/logging contracts og passive WordPress adapters.\n- Runtime bridge kører fortsat i shadow mode og må ikke overtage eksisterende Vehicle/Event/Gallery handlers.\n- UD-060: generiske Vehicle, Event og Gallery starter schemas/presets oven på Dynamic CMS-motoren; ingen specialmotor og ingen automatisk datamigration.\n- Sider-modulet udnytter nu hele den tilgængelige WordPress-adminbredde, så sideopbygning/canvas får markant mere arbejdsplads.\n- Sider får en tydelig Ny tom side-funktion samt genvej til oprettelse fra Page Template.\n- Retter Page Template-oprettelse, så nye managed side-slugs bevares korrekt i stedet for at kunne falde tilbage til Hjem.\n- Vehicle/Event/Gallery beholder eksisterende v0.5.30 markup, CSS hooks, URLs, data og legacy runtime-kontrakt.\n- Releasepakken indeholder nu src/ med architecture foundation og validerer den ved build/installationspakke-QA.\n'''
if '== Version 0.6.0 ' in readme:
    raise SystemExit('readme already contains v0.6.0 section')
readme = replace_once(readme, intro, intro + release_notes, 'readme release insertion')

css = replace_once(css, '/* v0.5.31 – Sider: full-width workspace og tydelig sideoprettelse */', '/* v0.6.0 – Sider: full-width workspace og tydelig sideoprettelse */', 'admin css release comment')
js = replace_once(js, '/* v0.5.31 – tydelig oprettelse af sider */', '/* v0.6.0 – tydelig oprettelse af sider */', 'admin js release comment')

sync = replace_once(
    sync,
    "          node --check .build/hangar18-manager/assets/admin.js\n",
    "          node --check .build/hangar18-manager/assets/admin.js\n          test -f .build/hangar18-manager/src/Autoload.php\n          test -f .build/hangar18-manager/src/Core/RuntimeBridge.php\n          test -f .build/hangar18-manager/src/DynamicData/StarterSchemaPresetCatalog.php\n          find .build/hangar18-manager/src -name '*.php' -print0 | xargs -0 -n1 php -l\n",
    'sync package src validation'
)
sync = replace_once(
    sync,
    "          cp .build/hangar18-manager/assets/admin.js assets/admin.js\n          rm -rf .build\n",
    "          cp .build/hangar18-manager/assets/admin.js assets/admin.js\n          rm -rf src\n          cp -R .build/hangar18-manager/src ./src\n          rm -rf .build\n",
    'sync src copy'
)
sync = replace_once(
    sync,
    "          git add hangar18-manager.php readme.txt assets/admin.css assets/admin.js\n",
    "          git add hangar18-manager.php readme.txt assets/admin.css assets/admin.js src\n",
    'sync src git add'
)

php_path.write_text(php, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
css_path.write_text(css, encoding='utf-8')
js_path.write_text(js, encoding='utf-8')
sync_path.write_text(sync, encoding='utf-8')

print('v0.6.0 source metadata and release sync prepared')
