from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.6.7',' * Version: 0.6.8','header'),("const VERSION = '0.6.7';","const VERSION = '0.6.8';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.6.7')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.6.7','Version: 0.6.8',1)
entry='''\n\n== Version 0.6.8 – E12 AI suggestion layer ==\n\nNyt:\n- Provider-neutral AI integration point uden repository/write-adgang.\n- AI tekstforslag ændrer aldrig content uden eksplicit accept og indeholder reversible Apply/Undo-data.\n- Prompt-to-layout kandidat skal bestå den normale Page Schema-validering før preview/insert.\n- AI design review må kun foreslå ændringer på eksisterende element/property-referencer.\n- AI accessibility-forslag begrænses til konkrete alt/label-fund og kan afvises individuelt.\n- Dedikeret hangar18_use_ai capability; ingen provider/API credentials konfigureres i denne release.\n- PHP 8.0/8.2/8.3 QA og Vehicle/Event/Gallery-kontrakten er grøn.\n'''
pos=readme.find('\n\n== Version 0.6.7')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
