from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.7.7',' * Version: 0.7.8','header'),("const VERSION = '0.7.7';","const VERSION = '0.7.8';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.7.7')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.7.7','Version: 0.7.8',1)
entry='''\n\n== Version 0.7.8 – I5 Asset Manager + menuvalg ==\n\nNyt:\n- I5 Asset Manager UI oven på native WordPress Media IDs med mapper, collections, tags og metadata.\n- Responsive focal point for desktop/tablet/mobil med live preview.\n- Usage-inspector finder MediaId-referencer på sider, components, templates og data/meta.\n- SHA-256 dubletscan er read-only og sletter/fletter aldrig filer automatisk.\n- WebP/AVIF genereres som namespaced .h18.webp/.h18.avif derivater; original og eksisterende derivater overskrives aldrig.\n- Menu UI har eksplicit Tilgængelige sider med valg/fravalg; en side kan eksistere uden at være i menuen.\n- Frontend og Vehicle/Event/Gallery forbliver uændrede; ingen sider konverteres.\n'''
pos=readme.find('\n\n== Version 0.7.7')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
