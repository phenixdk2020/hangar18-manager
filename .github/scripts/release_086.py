from pathlib import Path

php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [
    (' * Version: 0.8.5',' * Version: 0.8.6','plugin header'),
    ("const VERSION = '0.8.5';","const VERSION = '0.8.6';",'runtime constant'),
]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.8.5')!=1: raise SystemExit('readme version anchor mismatch')
readme=readme.replace('Version: 0.8.5','Version: 0.8.6',1)
entry='''\n\n== Version 0.8.6 – I10 Signed Cutover Preflight ==\n\nNyt:\n- Source-drift detection sammenligner shadow-copyens SourceHash med den aktuelle legacy editor-state før fremtidig cutover kan godkendes.\n- Cutover preflight kræver komplette manuelle I9-gates, korrekt I10-rækkefølge, gyldig shadow acceptance samt WordPress page ID og permalink.\n- Eligible preflight snapshots signeres med HMAC og bindes til præcis target-identitet, source hashes og blockers.\n- Signerede preflight-records er tidsbegrænsede og bliver stale/ugyldige ved source-drift eller ændret preflight-state.\n- Preflight har altid Executable=false og PublicMutationAvailable=false; den giver ingen aktiveringsret.\n- Admin-UI viser blockers, source hashes og om et gemt signeret preflight stadig er current.\n- Der findes stadig ingen activate/cutover/publish-handler, og WordPress-posts, URLs samt hangar18_manager_pages_v1 ændres ikke.\n- Vehicle/Event/Gallery forbliver blokeret af CompatibilityPolicy på legacy runtime.\n'''
anchor='\n\n== Version 0.8.5'
pos=readme.find(anchor)
if pos<0: raise SystemExit('changelog anchor missing')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
