from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.6.8',' * Version: 0.6.9','header'),("const VERSION = '0.6.8';","const VERSION = '0.6.9';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.6.8')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.6.8','Version: 0.6.9',1)
entry='''\n\n== Version 0.6.9 – E13 Portability ==\n\nNyt:\n- Page + global styles JSON med package/page schema og SHA-256 checksum samt identisk roundtrip.\n- Components/templates/menus/forms kan pakkes med stabile ExportId-referencer.\n- Dry-run er standard; collisions vises før write og kan remappes, skips eller blokeres eksplicit.\n- artifact:// og asset:// references remappes kun via validerede mapping-tabeller.\n- Asset manifest matcher target Media IDs via SHA-256 og rapporterer Broken references i stedet for silent drop.\n- Bekræftet import tager automatisk pre-import backup og kører mutationsdelen atomisk med rollback ved referencefejl.\n- E8 pre-publish backup regressionstestes fortsat. Ingen eksisterende sider konverteres endnu.\n'''
pos=readme.find('\n\n== Version 0.6.8')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
