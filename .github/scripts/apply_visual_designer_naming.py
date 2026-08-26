#!/usr/bin/env python3
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]


def edit(path, replacements=(), regex_replacements=()):
    p = ROOT / path
    text = p.read_text(encoding='utf-8')
    original = text
    for old, new in replacements:
        text = text.replace(old, new)
    for pattern, repl in regex_replacements:
        text = re.sub(pattern, repl, text)
    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f'updated {path}')
    else:
        print(f'unchanged {path}')


# Plugin metadata: public/product-facing only. Internal slug, namespace, constants,
# actions, metadata keys and filesystem paths intentionally remain unchanged.
edit('clean/hangar18-manager/hangar18-manager.php', [
    ('Plugin Name: Hangar18 Manager Clean', 'Plugin Name: Visual Designer Manager'),
    ('Plugin URI: https://hangar18.dk/', 'Plugin URI: https://github.com/phenixdk2020/hangar18-manager'),
    ('Description: Ren Hangar18 120-unit sidebygger uden legacy editor-runtime.', 'Description: Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.'),
    ('Author: Hangar18', 'Author: Visual Designer Manager'),
])

# Visual Designer UI.
edit('clean/hangar18-manager/src/Admin/EditorController.php', [
    ('Hangar18 Designer', 'Visual Designer'),
    ('Clean editor ', 'Visual Designer '),
    ('Ingen gemte clean-versioner endnu.', 'Ingen gemte Visual Designer-versioner endnu.'),
    ('Gem fra clean editor', 'Gem fra Visual Designer'),
    ('Clean layout gemt og verificeret som version v', 'Visual Designer-layout gemt og verificeret som version v'),
    ('Clean-version', 'Visual Designer-version'),
    ('clean-version', 'Visual Designer-version'),
])

# Manager UI. Site name is runtime data, not product branding.
edit('clean/hangar18-manager/src/Admin/AdminController.php', [
    ('Hangar18 Manager Clean', 'Visual Designer Manager'),
    ("'Hangar18 Manager',\n            'Hangar18 Manager',", "'Visual Designer Manager',\n            'Visual Designer Manager',"),
    ("self::open('Hangar18 Manager', 'Clean administration · v'", "self::open('Visual Designer Manager', 'Administration · v'"),
    ('<span class="h18-manager-kicker">Clean Manager v', '<span class="h18-manager-kicker">Visual Designer Manager v'),
    ("echo '<h2>Aalborg Kaserners Veteran Panser- og Køretøjsforening</h2>';", "echo '<h2>' . esc_html((string) get_bloginfo('name')) . '</h2>';"),
    ('Clean bruger kun den nye canonical layoutmodel.', 'Visual Designer bruger den canonical layoutmodel.'),
    ('Clean-sider', 'Visual Designer-sider'),
    ('Sider med Clean-state', 'Sider med Visual Designer-layout'),
    ('Se Clean-status, nodeantal og seneste version', 'Se Visual Designer-status, nodeantal og seneste version'),
    ('Clean-layouts', 'Visual Designer-layouts'),
    ('Clean-logs', 'Visual Designer-logs'),
    ('Clean-layoutdata', 'Visual Designer-layoutdata'),
    ('Clean-adminstrukturen', 'Visual Designer Manager-administrationen'),
    ('Clean-datamodul', 'Visual Designer-datamodul'),
    ('Clean Data-modul', 'Visual Designer Data-modul'),
    ('Clean-modelstatus', 'Visual Designer-modelstatus'),
    ('Clean-status', 'Visual Designer-status'),
    ('>Clean v', '>Designer v'),
    ('Ikke Clean', 'Ikke Visual Designer'),
    ('Clean-princip', 'Visual Designer-princip'),
    ('Clean Designer styrer', 'Visual Designer styrer'),
    ('Clean-backup', 'Visual Designer-backup'),
    ('Hangar18 Manager', 'Visual Designer Manager'),
])

edit('clean/hangar18-manager/src/Admin/AdminMenuBridge.php', [
    ("'Designer',\n            'Designer',", "'Visual Designer',\n            'Visual Designer',"),
])

# Diagnostics may identify the product in support payload headings, but its
# internal keys and namespace remain unchanged.
edit('clean/hangar18-manager/src/Diagnostics/DiagnosticStore.php', [
    ('Hangar18 Manager Clean', 'Visual Designer Manager'),
    ('Hangar18 Designer', 'Visual Designer'),
])

# Updater/plugin-information visible metadata and messages.
edit('clean/hangar18-manager/src/Update/GitHubUpdater.php', [
    ('Hangar18 Manager Clean', 'Visual Designer Manager'),
    ('<a href="https://hangar18.dk/">Hangar18</a>', '<a href="https://github.com/phenixdk2020/hangar18-manager">Visual Designer Manager</a>'),
    ('https://hangar18.dk/', 'https://github.com/phenixdk2020/hangar18-manager'),
    ('Hangar18 Clean Designer.', 'Visual Designer Manager.'),
    ('Hangar18 update-pakken', 'Visual Designer Manager-updatepakken'),
    ('Hangar18-opdateringen', 'Visual Designer Manager-opdateringen'),
])

# Current workflow display text and next-release manifest metadata.
edit('.github/workflows/clean-artifact-release.yml', [
    ('name: Clean Plugin Download Artifact', 'name: Visual Designer Manager Dev Artifact'),
    ('Verify clean source', 'Verify Visual Designer Manager source'),
    ('Legacy editor dependency found in clean plugin.', 'Legacy editor dependency found in Visual Designer Manager.'),
])

edit('.github/workflows/clean-release.yml', [
    ('name: Clean GitHub Release', 'name: Visual Designer Manager Release'),
    ('echo "Clean version: $VERSION"', 'echo "Visual Designer Manager version: $VERSION"'),
    ('Verify clean source', 'Verify Visual Designer Manager source'),
    ("f'<h4>{version}</h4><p>Hangar18 Manager Clean release.</p>'", "f'<h4>{version}</h4><p>Visual Designer Manager release.</p>'"),
    ("'name': 'Hangar18 Manager Clean'", "'name': 'Visual Designer Manager'"),
    ("'homepage': 'https://hangar18.dk/'", "'homepage': 'https://github.com/phenixdk2020/hangar18-manager'"),
    ("'description': 'Ren Hangar18 120-unit sidebygger uden legacy editor-runtime.'", "'description': 'Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.'"),
    ('git commit -m "Release clean v${VERSION}"', 'git commit -m "Release Visual Designer Manager v${VERSION}"'),
    ("echo 'Unable to publish clean release after three attempts.'", "echo 'Unable to publish Visual Designer Manager release after three attempts.'"),
])

# Older 0.1.x release workflows may still be visible in Actions. Rebrand their
# display/product metadata without changing package paths or technical slugs.
for workflow in [
    '.github/workflows/clean-v012-release.yml',
    '.github/workflows/clean-v013-release.yml',
]:
    p = ROOT / workflow
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    original = text
    text = text.replace('Hangar18 Manager Clean', 'Visual Designer Manager')
    text = text.replace('Hangar18 Clean Designer', 'Visual Designer')
    text = text.replace('Ren Hangar18 120-unit sidebygger uden legacy editor-runtime.', 'Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.')
    text = text.replace('https://hangar18.dk/', 'https://github.com/phenixdk2020/hangar18-manager')
    text = text.replace('Clean GitHub Release', 'Visual Designer Manager Release')
    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f'updated {workflow}')

# Current authoritative/user-facing documentation. Filenames and CLEAN-* task IDs
# are intentionally retained as stable technical references.
for doc in [
    'CLEAN-DESIGN-MANUAL.md',
    'CLEAN-USER-MANUAL.md',
    'docs/CLEAN-HANDOVER.md',
    'docs/clean-backlog-v0120.md',
    'docs/HEADER-FOOTER-SPEC.md',
    'docs/PARALLEL-MANAGER-WORK.md',
    'docs/EXPORT-SPEC.md',
]:
    p = ROOT / doc
    if not p.exists():
        continue
    text = p.read_text(encoding='utf-8')
    original = text
    text = text.replace('Hangar18 Manager Clean', 'Visual Designer Manager')
    text = text.replace('Hangar18 Designer', 'Visual Designer')
    text = text.replace('Clean Designer', 'Visual Designer')
    text = text.replace('Clean Manager', 'Visual Designer Manager')
    text = text.replace('Hangar18 Manager', 'Visual Designer Manager')
    # Clean is still permitted in stable file names, identifiers, task IDs and
    # explicit internal naming explanations. In ordinary prose it is replaced.
    lines = []
    for line in text.splitlines(keepends=True):
        if ('`' in line and ('clean/' in line.lower() or 'CLEAN-' in line or '_h18_clean' in line or 'H18_CLEAN' in line)):
            lines.append(line)
            continue
        line = re.sub(r'\bClean\b', 'Visual Designer', line)
        line = re.sub(r'\bclean\b', 'Visual Designer', line)
        lines.append(line)
    text = ''.join(lines)
    if doc == 'CLEAN-DESIGN-MANUAL.md':
        text = text.replace('HANGAR18 DESIGN', 'VISUAL DESIGNER')
    if text != original:
        p.write_text(text, encoding='utf-8')
        print(f'updated {doc}')

# Naming policy now records that the public rename is implemented in the
# 0.1.22 forward source while internal compatibility identifiers remain.
p = ROOT / 'docs/PRODUCT-NAMING.md'
text = p.read_text(encoding='utf-8')
text = text.replace('**Status:** Godkendt navnestandard fra og med planlagt release 0.1.22', '**Status:** Implementeret i 0.1.22 forward-development; offentlig release følger QA-gaten')
marker = '## Clean er kun intern teknisk generationsbetegnelse\n'
if marker in text and '### Implementationsstatus 0.1.22' not in text:
    insert = ('### Implementationsstatus 0.1.22\n\n'
              'Fra 0.1.22 forward-development bruger plugin-header, WordPress-menuer, editor, Manager, updater-info, release-workflow og aktuelle brugerrettede dokumenter navnene **Visual Designer** / **Visual Designer Manager**.\n\n'
              'Interne kompatibilitetsidentifiers med `Hangar18`/`Clean` er bevidst ikke omdøbt endnu.\n\n')
    text = text.replace(marker, insert + marker)
p.write_text(text, encoding='utf-8')
print('updated docs/PRODUCT-NAMING.md')

# Guard: these specific obsolete public labels must not survive in active source.
public_roots = [ROOT / 'clean/hangar18-manager', ROOT / '.github/workflows']
forbidden = [
    'Hangar18 Manager Clean',
    'Hangar18 Designer',
    'Clean Manager v',
    'Clean editor ',
    'Clean layout gemt',
    'Clean-sider',
    'Ikke Clean',
]
errors = []
for base in public_roots:
    for path in base.rglob('*'):
        if not path.is_file() or path.suffix.lower() not in {'.php', '.js', '.css', '.yml', '.yaml', '.html', '.json'}:
            continue
        content = path.read_text(encoding='utf-8', errors='ignore')
        for token in forbidden:
            if token in content:
                errors.append(f'{path.relative_to(ROOT)}: obsolete public label: {token}')
if errors:
    raise SystemExit('\n'.join(errors))

print('Visual Designer naming migration PASS')
