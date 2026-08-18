from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.7.9',' * Version: 0.8.0','header'),("const VERSION = '0.7.9';","const VERSION = '0.8.0';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.7.9')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.7.9','Version: 0.8.0',1)
entry='''\n\n== Version 0.8.0 – I7 Permissions & Design Lock ==\n\nNyt:\n- Role/capability migration preview viser præcist hvad der vil blive oprettet og tilføjet før installation.\n- Rolle-installation er additive-only: ingen eksisterende capability eller rolle fjernes.\n- Installation kræver manage_options, nonce og eksplicit confirmation.\n- UD Administrator/Designer/Editor/Event/Gallery roller kan oprettes/opdateres via den eksisterende WordPress role API.\n- WordPress Administrator beholder sin eksisterende rolle og får kun manglende UD capabilities tilføjet.\n- Design Lock policy kan konfigurere struktur/design-lås og frigivne content-properties.\n- Design Lock håndhæves ikke i legacy Sider-editoren før I10; edit_pages fallback bevares.\n- Ingen bruger får automatisk ændret rolle. Frontend og Vehicle/Event/Gallery ændres ikke.\n'''
pos=readme.find('\n\n== Version 0.7.9')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
