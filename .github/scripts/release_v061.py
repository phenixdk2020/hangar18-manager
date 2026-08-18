from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected exactly 1 match, found {count}")
    return text.replace(old, new, 1)

php_path = Path('hangar18-manager.php')
readme_path = Path('readme.txt')

php = php_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')

php = replace_once(php, ' * Version: 0.6.0', ' * Version: 0.6.1', 'plugin header version')
php = replace_once(php, "const VERSION = '0.6.0';", "const VERSION = '0.6.1';", 'plugin version constant')
readme = replace_once(readme, 'Version: 0.6.0', 'Version: 0.6.1', 'readme version')

intro = 'Webbaseret management-værktøj til Aalborg Kaserners Veteran Panser- og Køretøjsforening.\n'
release_notes = '''\n\n== Version 0.6.1 – Inspector layout hotfix ==\n\nRettet:\n- Sider-editorens Inspector-faner og settings kan ikke længere overlappe hinanden i den smalle højre sidebar.\n- Inspector-fanerne bruger et responsivt wrapping grid med tydelig afstand til indstillingerne nedenunder.\n- Inputs, selects og tekstfelter holdes inden for Inspector-panelets bredde.\n- Vehicle/Event/Gallery runtime, data, markup og CSS hooks er uændret.\n'''
if '== Version 0.6.1 ' in readme:
    raise SystemExit('readme already contains v0.6.1 section')
readme = replace_once(readme, intro, intro + release_notes, 'readme release insertion')

php_path.write_text(php, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
print('v0.6.1 source metadata prepared')
