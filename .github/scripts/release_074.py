from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.7.3',' * Version: 0.7.4','header'),("const VERSION = '0.7.3';","const VERSION = '0.7.4';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.7.3')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.7.3','Version: 0.7.4',1)
entry='''\n\n== Version 0.7.4 – Ultimate Designer integration dashboard ==\n\nNyt:\n- Den namespacede Ultimate Designer-arkitektur autoloades nu fra pluginet i admin-kontekst.\n- Ny Hangar18 Manager → Ultimate Designer-side viser Site Builder templates/menuer, assets, permissions og QA-status.\n- I1–I10 integrationsbackloggen er synlig og dokumenteret.\n- Manual/live release gates vises separat fra automated QA.\n- Integrationen er admin-only: ingen frontend-renderer, side, URL eller Vehicle/Event/Gallery-domain skiftes.\n- PHP 8.0/8.2/8.3 integration QA og protected-domain regression er grøn.\n'''
pos=readme.find('\n\n== Version 0.7.3')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
