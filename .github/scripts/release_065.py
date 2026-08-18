from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.6.4',' * Version: 0.6.5','header'),("const VERSION = '0.6.4';","const VERSION = '0.6.5';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.6.4')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.6.4','Version: 0.6.5',1)
entry='''\n\n== Version 0.6.5 – E9 Asset Manager ==\n\nNyt:\n- Asset metadata-overlay med mapper, collections og tags uden at ændre native WordPress Media IDs.\n- Usage inspector scanner sider, komponenter og data entries for MediaId-referencer før senere sletning.\n- Responsive focal points omsættes til object-position for desktop/tablet/mobile.\n- WebP/AVIF-optimeringspipeline opretter kun understøttede derivater og bevarer altid originalen.\n- SHA-256 dubletdetektion er read-only og sletter/fletter aldrig automatisk.\n- PHP 8.0/8.2/8.3 QA og Vehicle/Event/Gallery-kontrakten er grøn.\n'''
pos=readme.find('\n\n== Version 0.6.4')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
