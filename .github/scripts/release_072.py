from pathlib import Path

# Controlled v0.7.2 release trigger.
php_path=Path('hangar18-manager.php')
readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8')
readme=readme_path.read_text(encoding='utf-8')

for old,new,label in [
    (' * Version: 0.7.1',' * Version: 0.7.2','plugin header'),
    ("const VERSION = '0.7.1';","const VERSION = '0.7.2';",'version constant'),
]:
    if php.count(old)!=1:
        raise SystemExit(f'{label}: expected one anchor, found {php.count(old)}')
    php=php.replace(old,new,1)

if readme.count('Version: 0.7.1')!=1:
    raise SystemExit('readme version anchor missing/duplicated')
readme=readme.replace('Version: 0.7.1','Version: 0.7.2',1)

entry='''\n\n== Version 0.7.2 – Gem og Typografi rettet ==\n\nRettet:\n- Egen kommentar ved Gem er eksplicit valgfri i markup og JavaScript; stale/custom browser-validity ryddes før submit.\n- Admin CSS/JS cache-bustes med pluginversion + filemtime, så en gammel admin.js ikke bliver hængende efter opdatering.\n- Editor viser aktiv version direkte i sideeditorens header.\n- Typografi-fanen var tom fordi CSS skjulte parent-containeren til typography-panelet. Nesting-reglen er rettet.\n- Typografi viser nu de eksisterende funktionelle indstillinger: brødtekst-font, overskrift-font, brødtekst-størrelse samt H1/H2/H3-størrelser.\n- PHP 8.0/8.2/8.3 QA, workflow regression og Vehicle/Event/Gallery-kontrakten er grøn.\n'''
pos=readme.find('\n\n== Version 0.7.1')
if pos<0:
    raise SystemExit('readme changelog anchor missing')
readme=readme[:pos]+entry+readme[pos:]

php_path.write_text(php,encoding='utf-8')
readme_path.write_text(readme,encoding='utf-8')
