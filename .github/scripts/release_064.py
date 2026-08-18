from pathlib import Path

php_path = Path('hangar18-manager.php')
readme_path = Path('readme.txt')

php = php_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')

for old, new, label in [
    (' * Version: 0.6.3', ' * Version: 0.6.4', 'plugin header'),
    ("const VERSION = '0.6.3';", "const VERSION = '0.6.4';", 'version constant'),
]:
    if php.count(old) != 1:
        raise SystemExit(f'{label}: expected one anchor, found {php.count(old)}')
    php = php.replace(old, new, 1)

if readme.count('Version: 0.6.3') != 1:
    raise SystemExit('readme version anchor not found exactly once')
readme = readme.replace('Version: 0.6.3', 'Version: 0.6.4', 1)
entry = '''

== Version 0.6.4 – Gem-toolbar og E8 Workflow ==

Nyt og rettet:
- Tydelig Gem-knap i toppen af sideeditoren samt Ctrl/Cmd+S.
- Save-status viser Gemt, Ikke gemt, Gemmer eller valideringsfejl, og browseren advarer ved ugemte ændringer.
- E8 Workflow core: autosave snapshots uden revisionsspam og permanente revisioner med bruger, tidspunkt, note og state hash.
- Restore opretter en ny revision i stedet for at overskrive historikken.
- Structured revision diff for added/removed/moved/property changes.
- Expiring/revocable HMAC-signerede preview tokens for desktop/tablet/mobile working-state preview.
- Working/public staging model med atomisk publish og pre-publish backup.
- PHP 8.0/8.2/8.3 QA er grøn; Vehicle/Event/Gallery legacy-runtime er uændret.
'''
insert_at = readme.find('\n\n== Version 0.6.1')
if insert_at < 0:
    raise SystemExit('readme changelog insertion anchor not found')
readme = readme[:insert_at] + entry + readme[insert_at:]

php_path.write_text(php, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
