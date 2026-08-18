from pathlib import Path

php_path = Path('hangar18-manager.php')
readme_path = Path('readme.txt')
php = php_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')

for old,new,label in [
    (' * Version: 0.7.0',' * Version: 0.7.1','plugin header'),
    ("const VERSION = '0.7.0';","const VERSION = '0.7.1';",'version constant'),
]:
    if php.count(old) != 1:
        raise SystemExit(f'{label}: expected one anchor, found {php.count(old)}')
    php = php.replace(old,new,1)

if readme.count('Version: 0.7.0') != 1:
    raise SystemExit('readme version anchor missing/duplicated')
readme = readme.replace('Version: 0.7.0','Version: 0.7.1',1)

entry = '''\n\n== Version 0.7.1 – Automatisk gemmeresumé ==\n\nNyt:\n- Håndskrevet ændringsbeskrivelse er ikke længere obligatorisk ved Gem eller Ctrl/Cmd+S.\n- Editor sammenligner indlæst og aktuel side og laver automatisk et kort resumé af titel, tilføjede/fjernede/flyttede elementer samt indhold, typografi, design, layout, responsive og dynamic-data ændringer.\n- Det automatiske resumé vises før gemning og genberegnes ved submit.\n- Serveren laver fallback-resumé, hvis browserresuméet mangler.\n- Versionshistorikken gemmer AutoChangeSummary og UserChangeNote separat og bevarer kombineret ChangeNote for bagudkompatibilitet.\n- Egen kommentar er valgfri og bruges til fx begrundelse eller oplysninger som ikke kan udledes af side-state.\n- Save-summary QA er grøn på PHP 8.0, 8.2 og 8.3, og Vehicle/Event/Gallery-kontrakten er uændret.\n'''
pos = readme.find('\n\n== Version 0.7.0')
if pos < 0:
    raise SystemExit('readme changelog anchor missing')
readme = readme[:pos] + entry + readme[pos:]

php_path.write_text(php,encoding='utf-8')
readme_path.write_text(readme,encoding='utf-8')
