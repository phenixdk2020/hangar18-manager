from pathlib import Path
p=Path('hangar18-manager.php'); r=Path('readme.txt')
php=p.read_text(encoding='utf-8'); readme=r.read_text(encoding='utf-8')
for old,new in [(' * Version: 0.7.6',' * Version: 0.7.7'),("const VERSION = '0.7.6';","const VERSION = '0.7.7';")]:
    if php.count(old)!=1: raise SystemExit(f'version anchor mismatch: {old}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.7.6')!=1: raise SystemExit('readme version anchor mismatch')
readme=readme.replace('Version: 0.7.6','Version: 0.7.7',1)
entry='''\n\n== Version 0.7.7 – I4 Live Side Health ==\n\nNyt:\n- Side Health vises direkte i den eksisterende Sider-editor uden at konvertere siden.\n- Analysen bruger den aktuelle DOM/form-state og medregner derfor også ugemte ændringer.\n- Samlet score samt Design, Mobile, Accessibility, Performance og SEO delscorer.\n- Filtrerbare issues med severity, code og konkrete ElementKey-links til Navigator.\n- Klik på et issue vælger/scroller til det konkrete element i den eksisterende editor.\n- Read-only AJAX bridge er capability/nonce-beskyttet og begrænser JSON-størrelse og antal elementer.\n- Side Health-controlleren indeholder ingen page-save/update/delete primitives.\n- Vehicle/Event/Gallery og frontend-rendering er fortsat uændret.\n'''
pos=readme.find('\n\n== Version 0.7.6')
if pos<0: raise SystemExit('changelog anchor missing')
readme=readme[:pos]+entry+readme[pos:]
p.write_text(php,encoding='utf-8'); r.write_text(readme,encoding='utf-8')
