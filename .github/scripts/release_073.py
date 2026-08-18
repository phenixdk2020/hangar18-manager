from pathlib import Path

# Second branch commit intentionally triggers the release workflow now that it exists on this branch.
php_path = Path('hangar18-manager.php')
readme_path = Path('readme.txt')

php = php_path.read_text(encoding='utf-8')
readme = readme_path.read_text(encoding='utf-8')

replacements = [
    (' * Version: 0.7.2', ' * Version: 0.7.3', 'plugin header'),
    ("const VERSION = '0.7.2';", "const VERSION = '0.7.3';", 'VERSION constant'),
]
for old, new, label in replacements:
    if php.count(old) != 1:
        raise SystemExit(f'{label} anchor count: {php.count(old)}')
    php = php.replace(old, new, 1)

if readme.count('Version: 0.7.2') != 1:
    raise SystemExit('readme version anchor is not unique')
readme = readme.replace('Version: 0.7.2', 'Version: 0.7.3', 1)

entry = '''\n\n== Version 0.7.3 – Valgfri overskrift og linjeskift ==\n\nRettet:\n- Overskrift på almindelige sideelementer er eksplicit valgfri; elementet kan bestå af ren tekst uden overskrift.\n- Afstemning beholder sin semantiske Spørgsmål-overskrift.\n- Enter i tekstfeltet bevares som synligt linjeskift i canvas-preview; tom linje giver nyt afsnit på frontend via wpautop.\n- Den ældre WhatIf-baserede JavaScript-regel kan ikke længere gøre Gem-kommentaren required igen.\n- Egen Gem-kommentar forbliver valgfri og automatisk ændringsresumé bruges som standard.\n- PHP 8.0/8.2/8.3 QA, workflow/quality E2E og Vehicle/Event/Gallery-kontrakten er grøn.\n'''
anchor = '\n\n== Version 0.7.2'
pos = readme.find(anchor)
if pos < 0:
    raise SystemExit('readme changelog anchor missing')
readme = readme[:pos] + entry + readme[pos:]

php_path.write_text(php, encoding='utf-8')
readme_path.write_text(readme, encoding='utf-8')
