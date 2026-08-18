from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.7.8',' * Version: 0.7.9','header'),("const VERSION = '0.7.8';","const VERSION = '0.7.9';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.7.8')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.7.8','Version: 0.7.9',1)
entry='''\n\n== Version 0.7.9 – I6 Import / Export ==\n\nNyt:\n- Sidepakker kan eksporteres med schema/checksum og valideres/previewes ved import uden side-write.\n- Artifact packages kan eksporteres fra shadow templates/menuer/components og Portability Workspace.\n- Artifact import starter altid med dry-run og viser actions, conflicts og ID-remaps.\n- Confirmation er bundet til et tidsbegrænset HMAC-signeret dry-run token for præcis package/strategi/plan.\n- Uløste asset/artifact references blokerer mutation.\n- Bekræftet import går kun til isoleret Portability Workspace og tager automatisk pre-import backup.\n- Workspace kan gendannes fra backup; eksisterende sider, frontend og Vehicle/Event/Gallery ændres ikke.\n'''
pos=readme.find('\n\n== Version 0.7.8')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
