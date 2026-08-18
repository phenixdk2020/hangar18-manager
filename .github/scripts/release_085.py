from pathlib import Path

php_path = Path('hangar18-manager.php')
readme_path = Path('readme.txt')
php = php_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')

replacements = [
    (' * Version: 0.8.4', ' * Version: 0.8.5', 'plugin header'),
    ("const VERSION = '0.8.4';", "const VERSION = '0.8.5';", 'runtime constant'),
]
for old, new, label in replacements:
    if php.count(old) != 1:
        raise SystemExit(f'{label} anchor count: {php.count(old)}')
    php = php.replace(old, new, 1)

if readme.count('Version: 0.8.4') != 1:
    raise SystemExit('readme version anchor mismatch')
readme = readme.replace('Version: 0.8.4', 'Version: 0.8.5', 1)

entry = '''\n\n== Version 0.8.5 – Auto-kasser, Tabel og kompakt Side Health ==\n\nNyt:\n- Auto-kasser genbruger eksisterende Grid/Container: 1 kasse = 100 %, 2 = 50/50, 3 = tre lige kolonner osv. op til 6.\n- Antallet af desktop-kolonner følger automatisk direkte under-kasser; mobil starter på én kolonne.\n- Afstand mellem kasser styres med eksisterende desktop/mobile LayoutGap-indstillinger.\n- Hver Kasse er et normalt Container-element og har derfor egne farver, typografi, fontstørrelser, padding, border, shadow og responsive overrides.\n- Nyt visuelt Tabel-værktøj med rækker/kolonner, header-række, zebra, farver, fontstørrelse, celle-padding og direkte celle-redigering.\n- Tabel kan bruge vandret scroll på mobil og gemmes gennem det eksisterende sanitiserede HTML-element.\n- Side Health starter sammenklappet i Inspector og viser kompakt score + fejl/advarsler, så Indhold/Typografi/Design/Avanceret ikke overskygges.\n- Layout-værktøjerne følger Inspectorens valgte element korrekt, også når element-body flyttes ind i Inspector.\n- Ingen public cutover eller ny frontend-renderer aktiveres; Vehicle/Event/Gallery forbliver på legacy runtime.\n'''
anchor = '\n\n== Version 0.8.4'
pos = readme.find(anchor)
if pos < 0:
    raise SystemExit('changelog anchor missing')
readme = readme[:pos] + entry + readme[pos:]

php_path.write_text(php, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
