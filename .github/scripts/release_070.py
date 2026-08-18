from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.6.9',' * Version: 0.7.0','header'),("const VERSION = '0.6.9';","const VERSION = '0.7.0';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.6.9')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.6.9','Version: 0.7.0',1)
entry='''\n\n== Version 0.7.0 – E14 Automated QA baseline ==\n\nNyt:\n- Automated browser-engine matrix på Chromium, Firefox og WebKit for menu-keyboard, modal focus trap, formularfokus og reduced motion.\n- Security gate for den nye arkitektur samt eksplicit capability/preview/import safety checks.\n- Performance budgets for public runtime, portability flow og Side Health.\n- Migration/rollback fixture med checksum-protected backup og exact restore.\n- MVP/v1 end-to-end tests for save/preview/publish/restore, Site Builder, menu, form, quality og portability.\n- ReleaseReadiness adskiller automated evidence fra manual/live evidence; grøn CI kan ikke markere live acceptance som færdig.\n- Administrator/designer onboarding og endelig migration-rækkefølge er dokumenteret.\n- Manual Chrome/Edge/Firefox/Safari brand-test, screen-reader, test2 live E2E, Vehicle/Event/Gallery regression og live-copy migration er stadig pending.\n- Ingen eksisterende sider er konverteret.\n'''
pos=readme.find('\n\n== Version 0.6.9')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
