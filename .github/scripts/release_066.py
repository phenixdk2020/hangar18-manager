from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.6.5',' * Version: 0.6.6','header'),("const VERSION = '0.6.5';","const VERSION = '0.6.6';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.6.5')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.6.5','Version: 0.6.6',1)
entry='''\n\n== Version 0.6.6 – E10 Permissions ==\n\nNyt:\n- Named least-privilege capabilities for settings, design, components, templates, data schemas, content, assets, publish, custom code, events og galleries.\n- Rolleopskrifter for Administrator, Designer, Editor, Eventansvarlig og Gallery Manager.\n- Design/structure lock beskytter layout og styling men kan frigive konkrete content fields.\n- Component editable inputs begrænser content-only roller til eksplicit frigivne felter.\n- Domain scope kan begrænse roller til fx Event eller Gallery data.\n- WordPress role installer er eksplicit/passiv og overtager ikke nuværende legacy permissions endnu.\n- PHP 8.0/8.2/8.3 QA og Vehicle/Event/Gallery-kontrakten er grøn.\n'''
pos=readme.find('\n\n== Version 0.6.5')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
