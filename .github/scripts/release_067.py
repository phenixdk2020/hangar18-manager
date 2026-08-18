from pathlib import Path
php_path=Path('hangar18-manager.php'); readme_path=Path('readme.txt')
php=php_path.read_text(encoding='utf-8'); readme=readme_path.read_text(encoding='utf-8')
for old,new,label in [(' * Version: 0.6.6',' * Version: 0.6.7','header'),("const VERSION = '0.6.6';","const VERSION = '0.6.7';",'constant')]:
    if php.count(old)!=1: raise SystemExit(f'{label} anchor count {php.count(old)}')
    php=php.replace(old,new,1)
if readme.count('Version: 0.6.6')!=1: raise SystemExit('readme version anchor')
readme=readme.replace('Version: 0.6.6','Version: 0.6.7',1)
entry='''\n\n== Version 0.6.7 – E11 Side Health ==\n\nNyt:\n- Accessibility analyzer for heading order, alt text, labels, focus og målbar kontrast med elementreference.\n- Responsive analyzer finder fixed-width overflow, små touch targets, lille tekst og kritisk skjult mobilindhold.\n- Design consistency analyzer finder off-token farver, lokale font overrides og spacing/radius outliers.\n- SEO metadata-model/analyzer for title, description, H1, canonical/index/follow og social metadata.\n- Performance analyzer finder store assets, dyb DOM/layout nesting og unødvendige feature-moduler.\n- Side Health samler Design, Mobile, Accessibility, Performance og SEO score og viser HardFailures separat.\n- Analyzer-laget er read-only og omskriver aldrig sider automatisk.\n'''
pos=readme.find('\n\n== Version 0.6.6')
if pos<0: raise SystemExit('changelog anchor')
readme=readme[:pos]+entry+readme[pos:]
php_path.write_text(php,encoding='utf-8'); readme_path.write_text(readme,encoding='utf-8')
