from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    path = ROOT / rel
    if not path.is_file():
        raise SystemExit(f'Missing required file: {rel}')
    return path.read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    value = read(rel)
    if new in value:
        return
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected one anchor, found {count}: {old[:140]!r}')
    write(rel, value.replace(old, new, 1))


PLUGIN = 'clean/hangar18-manager/hangar18-manager.php'
HISTORY = 'clean/hangar18-manager/release-history.json'
NOTES = 'clean-release-notes.html'
BACKLOG = 'docs/clean-backlog-v0100.md'
PARITY_STATUS = 'docs/vd-module-visual-parity-002-status.md'
V0175_QA = '.github/scripts/v0175_forms_search_archive_qa.py'
PARITY_QA = '.github/scripts/vd_module_visual_parity_002_qa.py'

# Runtime version.
replace_once(PLUGIN, ' * Version: 0.1.75', ' * Version: 0.1.76')
replace_once(PLUGIN, "define('H18_CLEAN_VERSION', '0.1.75');", "define('H18_CLEAN_VERSION', '0.1.76');")

# Release notes consumed by the central release workflow when it builds clean-update.json.
write(NOTES, '''<h2>0.1.76 – Modulvisning og _old-paritet</h2>
<ul>
<li><strong>Designer/frontend-paritet:</strong> Events, Billedgalleri og Køretøjer bruger nu den samme canonical <code>CollectionPageRenderer</code> i Designer-preview og på den offentlige side.</li>
<li>Designer viser de tre dynamiske samlingssider i en same-origin frontend-iframe i stedet for separate JS-efterligninger, så kort, typografi, søgning/sortering og responsive regler ikke kan drive fra frontend.</li>
<li><strong>Visuel _old-paritet:</strong> 90 % sideframe uden kunstigt max-width-loft, 3/2/1 responsive kolonner, fuldbredde 16:9 coverbilleder, beige kortkrop, kompakt spacing og ingen kunstig kortskygge.</li>
<li>WordPress admin-bar skjules kun i Designerens modul-preview, så preview-geometrien svarer til offentlig visning for redaktører.</li>
<li>Funktionerne fra v0.1.75 bevares: Kontakt/Bliv medlem-formularer, eventarkiv, event→album samt søgning/sortering på de tre modulsider.</li>
</ul>
''')

# Canonical release history.
history = json.loads(read(HISTORY))
versions = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(versions, list):
    raise SystemExit('release-history.json: versions must be a list')
if not any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.76' for row in versions):
    versions.insert(0, {
        'version': '0.1.76',
        'date': '2026-09-01',
        'items': [
            'VD-MODULE-VISUAL-PARITY-002: Events, Billedgalleri og Køretøjer bruger samme canonical CollectionPageRenderer i Designer-preview og frontend.',
            'Designerens samlingsside-preview bruger en same-origin frontend-iframe i stedet for separate JS-kortimplementeringer.',
            '_old-paritet er strammet med 90% frame uden max-width-loft, 3/2/1 grid, 16:9 coverbilleder, beige kortkrop og kompakt spacing.',
            'WordPress admin-bar skjules kun i modul-previewet, så redaktørpreviewet bevarer offentlig frontend-geometri.',
            'v0.1.75-funktionalitet for formularer, søgning/sortering, eventarkiv og event→album er bevaret og regressionstestet.'
        ],
    })
history['versions'] = versions
write(HISTORY, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

# Canonical backlog/status now records the parity work as part of v0.1.76.
backlog = read(BACKLOG)
replacements = [
    ('**Aktuel release:** v0.1.75', '**Aktuel release:** v0.1.76'),
    ('## Aktuel milepælsstatus · v0.1.75 + efterfølgende source-opgaver', '## Aktuel milepælsstatus · v0.1.76'),
    ('8. **VD-MODULE-VISUAL-PARITY-002 — IMPLEMENTERET EFTER v0.1.75 / AFVENTER NÆSTE RELEASE:**', '8. **v0.1.76 – VD-MODULE-VISUAL-PARITY-002 — FÆRDIG:**'),
    ('### VD-MODULE-VISUAL-PARITY-002 — IMPLEMENTERET EFTER v0.1.75 / AFVENTER NÆSTE RELEASE', '### VD-MODULE-VISUAL-PARITY-002 — FÆRDIG I v0.1.76'),
    ('- Opgaven ændrer ikke plugin-version eller updater-manifest; den skal med i næste eksplicit bestilte release.', '- Opgaven er inkluderet i v0.1.76; ZIP og updater-manifest bygges og verificeres af den centrale release-workflow.'),
]
for old, new in replacements:
    if old in backlog:
        backlog = backlog.replace(old, new, 1)
    elif new not in backlog:
        raise SystemExit(f'{BACKLOG}: missing release anchor: {old!r}')
write(BACKLOG, backlog)

write(PARITY_STATUS, '''# VD-MODULE-VISUAL-PARITY-002 – status

**Dato:** 1. september 2026  
**Status:** Inkluderet i Visual Designer Manager v0.1.76.

## Scope
- Events, Billedgalleri og Køretøjer og materiel.
- `_old` er visuel reference.
- Frontend beholder dynamisk flow-rendering og eksisterende søgning/sortering.
- Kortlayout er justeret mod `_old` med 90% frame, 3/2/1 grid, fuldbredde 16:9-billeder, beige kortkrop og kompakt spacing.
- Designer bruger den faktiske offentlige CollectionPageRenderer i en same-origin iframe i stedet for en separat JS-approximation.
- WordPress admin-bar skjules kun i iframe-previewet for redaktører, så preview-geometrien svarer til offentlig visning.

## Release
- Plugin header/runtime er `0.1.76` efter releaseforberedelsen.
- ZIP og `clean-update.json` genereres kun af den centrale release-workflow.
- Historiske v0.1.75-funktioner er fortsat regression-gates.
''')

write('docs/v0176-status.md', '''# Visual Designer Manager v0.1.76 – status

**Dato:** 1. september 2026  
**Status:** Release candidate; central ZIP/manifest-build kræves før frigivelsen er verificeret.

## Scope
- VD-MODULE-VISUAL-PARITY-002.
- Canonical Designer/frontend-rendering for Events, Billedgalleri og Køretøjer.
- `_old`-orienteret kortgeometri og responsive 3/2/1 layouts.
- Ingen ændring af moduldata eller v0.1.75-form/event/search-funktionalitet.

## Release-gate
- Plugin/runtime skal være præcis `0.1.76`.
- v0.1.73, v0.1.74, v0.1.75 og parity-QA skal være grønne.
- Før central release skal `clean-update.json` stadig være v0.1.75.
- Efter central release skal manifest og versioneret ZIP være v0.1.76 og SHA-256-verificeret.
''')

# Historical QA must remain valid after newer releases instead of pinning the latest version.
v175 = read(V0175_QA)
v175 = v175.replace("require(header is not None and const is not None and header.group(1) == '0.1.75' and const.group(1) == '0.1.75', 'plugin/runtime version is exactly 0.1.75')",
                    "require(header is not None and const is not None and header.group(1) == const.group(1) and tuple(map(int, header.group(1).split('.'))) >= (0, 1, 75), 'plugin/runtime version is v0.1.75 or newer')")
v175 = v175.replace("require(bool(versions) and str(versions[0].get('version', '')) == '0.1.75', 'release history starts with v0.1.75')",
                    "require(any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.75' for row in versions), 'release history retains v0.1.75')")
v175 = v175.replace("require('0.1.75' in notes and 'Kontakt' in notes and 'Bliv medlem' in notes, 'release notes describe v0.1.75 forms')",
                    "require(any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.75' and any('kontakt' in str(item).lower() for item in row.get('items', [])) for row in versions), 'release history retains v0.1.75 form scope')")
v175 = v175.replace("require('**Aktuel release:** v0.1.75' in backlog, 'canonical backlog points at v0.1.75')",
                    "require('**Aktuel release:** v' in backlog, 'canonical backlog carries an active release marker')")
write(V0175_QA, v175)

parity = read(PARITY_QA)
parity = parity.replace("require(header is not None and const is not None and header.group(1) == '0.1.75' and const.group(1) == '0.1.75', 'task does not bump plugin/runtime beyond released v0.1.75')",
                        "require(header is not None and const is not None and header.group(1) == const.group(1) and tuple(map(int, header.group(1).split('.'))) >= (0, 1, 75), 'parity task remains present in v0.1.75 or newer runtime')")
parity = parity.replace("require(str(manifest.get('version', '')) == '0.1.75', 'task does not mutate updater manifest/released version')",
                        "require(tuple(map(int, str(manifest.get('version', '0.0.0')).split('.'))) <= tuple(map(int, header.group(1).split('.'))), 'updater manifest never points beyond runtime version')")
parity = parity.replace("require('VD-MODULE-VISUAL-PARITY-002 — IMPLEMENTERET EFTER v0.1.75 / AFVENTER NÆSTE RELEASE' in backlog, 'backlog records parity implementation without pretending it is released')",
                        "require('VD-MODULE-VISUAL-PARITY-002' in backlog, 'backlog records parity implementation/release state')")
parity = parity.replace("require('Implementeret i source efter v0.1.75' in status, 'status document records source-only completion')",
                        "require('v0.1.76' in status or 'Implementeret i source efter v0.1.75' in status, 'status document records parity completion/release state')")
parity = parity.replace("require('Ingen ZIP, manifest eller release-trigger ændres' in status, 'status document preserves explicit release boundary')",
                        "require('centrale release-workflow' in status or 'Ingen ZIP, manifest eller release-trigger ændres' in status, 'status document preserves central release boundary')")
write(PARITY_QA, parity)

print('Prepared Visual Designer Manager v0.1.76 release candidate.')
