from pathlib import Path
import json

ROOT = Path('.')
PLUGIN_ROOT = ROOT / 'clean/hangar18-manager'
PLUGIN = PLUGIN_ROOT / 'hangar18-manager.php'
LAYOUT = PLUGIN_ROOT / 'src/Model/LayoutModel.php'
TECH = ROOT / 'CLEAN-TECHNICAL-MANUAL.md'
NOTES = ROOT / 'clean-release-notes.html'
HISTORY = PLUGIN_ROOT / 'release-history.json'
STATUS = ROOT / 'docs/v0159-status.md'
TRIGGER = ROOT / 'visual-designer-release-now.txt'


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly 1 match, got {count}')
    return text.replace(old, new, 1)


# BUG-21 / VD-TEXT-BG-INHERIT-001
# The runtime fix itself is merged before this release patch. Verify that the
# canonical Text model always paints transparent so its nearest Kasse/Sektion
# background is visible instead of a stale legacy white Text background.
layout = LAYOUT.read_text(encoding='utf-8')
required = "'backgroundTransparent' => true,"
if required not in layout:
    raise SystemExit('BUG-21 fix missing: Text backgroundTransparent is not canonical true')

# Version bump.
plugin = PLUGIN.read_text(encoding='utf-8')
plugin = replace_once(plugin, ' * Version: 0.1.58', ' * Version: 0.1.59', 'plugin header version')
plugin = replace_once(plugin, "define('H18_CLEAN_VERSION', '0.1.58');", "define('H18_CLEAN_VERSION', '0.1.59');", 'runtime version')
PLUGIN.write_text(plugin, encoding='utf-8')

# Release notes.
notes = NOTES.read_text(encoding='utf-8')
release_notes = '''<h4>0.1.59 – Tekstbaggrund arver Kasse/Sektion</h4><ul><li><strong>BUG-21:</strong> Tekst-elementer normaliseres nu altid med transparent elementbaggrund.</li><li>Tekst i en Kasse viser derfor Kassens baggrund; Tekst direkte i en Sektion viser Sektionens baggrund.</li><li>Hvis Kassen selv er transparent, ses Sektionens baggrund videre igennem.</li><li>Eksisterende ældre modeller med <code>backgroundTransparent=false</code> kan ikke længere blokere forælderens baggrund med en hvid Tekst-flade.</li><li>Menu, Billede, Knap, geometri og hierarchy-normalisering er ikke ændret i denne release.</li></ul>\n'''
if not notes.startswith('<h4>0.1.59'):
    notes = release_notes + notes
NOTES.write_text(notes, encoding='utf-8')

# Structured release history.
history_data = json.loads(HISTORY.read_text(encoding='utf-8'))
if not isinstance(history_data, dict):
    raise SystemExit('release-history.json has unexpected top-level format')
versions = history_data.setdefault('versions', [])
if not versions or versions[0].get('version') != '0.1.59':
    versions.insert(0, {
        'version': '0.1.59',
        'date': '2026-08-30',
        'items': [
            'BUG-21: Tekst-elementets canonical backgroundTransparent er nu altid true.',
            'Paint-kæden er Tekst → nærmeste Kasse → Sektion.',
            'Legacy Text-state med backgroundTransparent=false kan ikke længere give hvid elementbaggrund.',
            'Transparent Kasse lader fortsat Sektionens baggrund skinne igennem.',
            'Menu, Billede, Knap, geometri og hierarchy-normalisering er uændret.'
        ],
    })
HISTORY.write_text(json.dumps(history_data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Technical contract.
tech = TECH.read_text(encoding='utf-8')
contract = r'''

## 0.1.59 – Tekstbaggrund arver Kasse/Sektion

### VD-TEXT-BG-INHERIT-001
- Tekst-elementer har ikke en selvstændig synlig baggrundskontrakt i den aktuelle Inspector og normaliseres derfor canonical med `backgroundTransparent=true`.
- Paint-kæden er **Tekst → nærmeste Kasse → Sektion**.
- Ligger Tekst direkte under en Sektion, er Sektionens baggrund den synlige baggrund bag teksten.
- Ligger Tekst under en Kasse, er Kassens baggrund den synlige baggrund; er Kassen transparent, fortsætter paint-kæden til Sektionen.
- Ældre persisted Text-state med `backgroundTransparent=false` må ikke genindføre en hvid leaf-baggrund.
- Menu, Billede og Knap beholder deres egne eksisterende background-kontrakter.
'''
if '## 0.1.59 – Tekstbaggrund arver Kasse/Sektion' not in tech:
    tech += contract
TECH.write_text(tech, encoding='utf-8')

STATUS.parent.mkdir(parents=True, exist_ok=True)
STATUS.write_text('''# Visual Designer Manager 0.1.59 status\n\n- BUG-21 / VD-TEXT-BG-INHERIT-001 implementeret.\n- Text normaliseres canonical med `backgroundTransparent=true`.\n- Synlig baggrund følger Text → nærmeste Kasse → Sektion.\n- Legacy `backgroundTransparent=false` på Text kan ikke længere male en hvid leaf-flade.\n- Menu, Billede, Knap, geometri og hierarchy-normalisering er ikke ændret.\n- Release bygges gennem den eksisterende Visual Designer Manager release-workflow med versionslåst ZIP og SHA-256-manifest.\n''', encoding='utf-8')

TRIGGER.write_text('''Release Visual Designer Manager v0.1.59\nTrigger: text-background-inheritance 2026-08-30\n''', encoding='utf-8')

print('Applied Visual Designer Manager 0.1.59 Text background inheritance release patch.')
