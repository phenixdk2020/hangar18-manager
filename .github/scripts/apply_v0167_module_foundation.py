from __future__ import annotations

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[2]


def read(rel: str) -> str:
    return (ROOT / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = ROOT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str) -> None:
    text = read(rel)
    if new in text:
        return
    count = text.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected one replacement anchor, found {count}: {old[:120]!r}')
    write(rel, text.replace(old, new, 1))


def append_once(rel: str, marker: str, block: str) -> None:
    text = read(rel)
    if marker in text:
        return
    write(rel, text.rstrip() + '\n\n' + block.strip() + '\n')


# ---------------------------------------------------------------------------
# Runtime version + module bootstrap
# ---------------------------------------------------------------------------
plugin = 'clean/hangar18-manager/hangar18-manager.php'
text = read(plugin)
text2 = re.sub(r'Version:\s*0\.1\.66\b', 'Version: 0.1.67', text, count=1)
text2 = text2.replace("define('H18_CLEAN_VERSION', '0.1.66');", "define('H18_CLEAN_VERSION', '0.1.67');", 1)
if text2 == text and 'Version: 0.1.67' not in text:
    raise SystemExit('plugin version anchors not found')
write(plugin, text2)

replace_once(
    plugin,
    "require_once H18_CLEAN_DIR . 'src/Icons/IconRegistry.php';",
    "require_once H18_CLEAN_DIR . 'src/Icons/IconRegistry.php';\n"
    "require_once H18_CLEAN_DIR . 'src/Modules/ModuleRegistry.php';\n"
    "require_once H18_CLEAN_DIR . 'src/Modules/ModuleRecord.php';\n"
    "require_once H18_CLEAN_DIR . 'src/Modules/ModuleBinding.php';\n"
    "require_once H18_CLEAN_DIR . 'src/Modules/ModuleStore.php';",
)
replace_once(
    plugin,
    "add_action('plugins_loaded', static function (): void {\n    \\VisualDesignerManager\\Diagnostics\\DiagnosticStore::register();",
    "add_action('plugins_loaded', static function (): void {\n"
    "    \\VisualDesignerManager\\Modules\\ModuleStore::register();\n"
    "    \\VisualDesignerManager\\Diagnostics\\DiagnosticStore::register();",
)
replace_once(
    plugin,
    "        'iconLibrary' => \\VisualDesignerManager\\Icons\\IconRegistry::editorCatalog(),\n        'initialModel' => $model,",
    "        'iconLibrary' => \\VisualDesignerManager\\Icons\\IconRegistry::editorCatalog(),\n"
    "        'moduleCatalog' => \\VisualDesignerManager\\Modules\\ModuleRegistry::editorCatalog(),\n"
    "        'initialModel' => $model,",
)


# ---------------------------------------------------------------------------
# Forward compatibility for the old element model QA after IconRegistry
# ---------------------------------------------------------------------------
qa165 = '.github/scripts/v0165_elements_model_qa.php'
text = read(qa165)
icon_require = "require_once __DIR__ . '/../../clean/hangar18-manager/src/Icons/IconRegistry.php';\n"
if icon_require not in text:
    anchor = "require_once __DIR__ . '/../../clean/hangar18-manager/src/Model/HierarchyNormalizer.php';\n"
    if text.count(anchor) != 1:
        raise SystemExit('v0165 model QA require anchor missing')
    text = text.replace(anchor, icon_require + anchor, 1)
    write(qa165, text)


# ---------------------------------------------------------------------------
# Release history
# ---------------------------------------------------------------------------
history_path = 'clean/hangar18-manager/release-history.json'
history = json.loads(read(history_path))
if not isinstance(history, dict) or not isinstance(history.get('versions'), list):
    raise SystemExit('release-history.json must contain versions[]')
versions = history['versions']
if not any(isinstance(item, dict) and item.get('version') == '0.1.67' for item in versions):
    versions.insert(0, {
        'version': '0.1.67',
        'date': '2026-08-31',
        'items': [
            'VD-MODULE-DATA-001: fælles modulregistry for Køretøjer, Events og Billedgalleri.',
            'Canonical ModuleRecord v1 med stabile record-IDer, standardfelter, dynamiske attributter, media-referencer og SHA-256 digest.',
            'Privat WordPress-native ModuleStore på h18_module_item med canonical JSON og separate indeks-meta til modul, status og sortering.',
            'ModuleBinding v1 definerer statisk/modul, liste/detail, query og field-map uden endnu at aktivere dynamisk rendering.',
            'Den gamle v0.1.65 elementmodel-QA indlæser nu IconRegistry og er forward-kompatibel med 0.1.66+.',
        ],
    })
write(history_path, json.dumps(history, ensure_ascii=False, indent=2) + '\n')


# ---------------------------------------------------------------------------
# Canonical backlog sync
# ---------------------------------------------------------------------------
backlog = 'docs/clean-backlog-v0100.md'
text = read(backlog)
text = text.replace('**Statusdato:** 30. august 2026', '**Statusdato:** 31. august 2026', 1)
text = text.replace('## Aktuel milepælsstatus · v0.1.62', '## Aktuel milepælsstatus · v0.1.67', 1)
old_bullet = '- **Næste generelle elementpakke:** Spacer, Divider, Ikon og Tabel/Dataliste. Dynamiske Køretøjer/Events/Billedgalleri følger derefter den separate modularkitektur.'
new_bullets = (
    '- **VD-ELEMENTS-001 / VD-ICON-LIBRARY-001 / VD-TABLE-BORDERS-001 — IMPLEMENTERET:** generelle elementer, ikonbibliotek og Excel-lignende tabelkanter er nu canonical Designer-funktioner.\n'
    '- **VD-MODULE-DATA-001 — IMPLEMENTERET I v0.1.67:** fælles ModuleRegistry, ModuleRecord, ModuleBinding og privat ModuleStore er fundamentet for Køretøjer, Events og Billedgalleri.\n'
    '- **Næste modul:** Køretøjer bygges først oven på den fælles modularkitektur; derefter Events og Billedgalleri.'
)
if old_bullet in text:
    text = text.replace(old_bullet, new_bullets, 1)

roadmap_marker = '## Roadmap fra v0.1.67'
if roadmap_marker not in text:
    roadmap_block = '''## Roadmap fra v0.1.67

1. **v0.1.67 – Module/Data Foundation:** registry, canonical recordmodel, private datastore og binding-kontrakt.
2. **Næste – Køretøjsmodul:** Manager-CRUD, fleksible tekniske datafelter, billeder, sortering og Designer-modul-elementer til liste/detail.
3. **Derefter – Events:** samme data-/bindingarkitektur med dato, sted, status og eventvisninger.
4. **Derefter – Billedgalleri:** album/medier på samme modulstore og genbrugelige Designer-visninger.
5. Dynamisk binding aktiveres først i de konkrete modulelementer; v0.1.67 ændrer ikke eksisterende statiske Data List/Tabel-renderinger.
'''
    anchor = '## Næste backlog\n'
    if anchor not in text:
        raise SystemExit('clean backlog next-section anchor missing')
    text = text.replace(anchor, roadmap_block + '\n' + anchor, 1)
write(backlog, text)


# ---------------------------------------------------------------------------
# Documentation + release notes
# ---------------------------------------------------------------------------
append_once(
    'CLEAN-TECHNICAL-MANUAL.md',
    'VD-MODULE-DATA-001',
    '''## VD-MODULE-DATA-001 – Fælles modul- og dataarkitektur (v0.1.67)

- `ModuleRegistry` er den eneste registry for modulnøglerne `vehicles`, `events` og `galleries`.
- `ModuleRecord` schema 1 normaliserer den fælles record-envelope: stabilt ID, titel, slug, status, sortering, featured media, summary, module-specifikke standardfelter, dynamiske attributter samt created/updated timestamps.
- Dynamiske attributter er ordnede key/label/type/value-records. De er bevidst generiske, så Køretøjer kan få brugerdefinerede tekniske felter uden et nyt databaseformat.
- `ModuleStore` bruger det private WordPress post type `h18_module_item`. Canonical record gemmes som JSON i `_h18_module_record_v1`; modul, status og sortering har egne meta-indekser.
- Storage er `public=false`, `show_ui=false` og `show_in_rest=false`. Manager-UI skal altid gå gennem modulets egne kontrollerede actions/services.
- `ModuleBinding` schema 1 beskriver `static|module`, `list|detail`, record-ID, query og field-map. Kontrakten er foundation i v0.1.67; eksisterende statiske Designer-elementer skifter ikke datasource automatisk.
- Records har canonical SHA-256 digest, så senere import/migration og QA kan verificere strukturel identitet.
- Modulrækkefølge: Køretøjer først, derefter Events og Billedgalleri.
'''
)
append_once(
    'CLEAN-DESIGN-MANUAL.md',
    'Module/Data Foundation v0.1.67',
    '''## Module/Data Foundation v0.1.67

Visual Designer Manager skelner nu mellem **statiske elementdata** og **genbrugelige moduldata**. Køretøjer, Events og Billedgalleri skal ikke gemmes som kopier inde i hver side. De får en fælles central datastore og kan senere vises gennem dynamiske Designer-elementer.

Et modulrecord har fælles titel/status/billede/sortering samt modul-specifikke standardfelter. Derudover findes ordnede, brugerdefinerede attributter. Det er især grundlaget for Køretøjer, hvor tekniske datafelter skal kunne tilføjes, skjules og sorteres uden at ændre datamodellen.

v0.1.67 indeholder **ikke** den endelige Køretøjer-Manager eller dynamisk frontendbinding. Den etablerer den datakontrakt, som næste version bygger UI og visninger oven på.
'''
)

write('clean-release-notes.html', '''<h4>0.1.67 – Module/Data Foundation</h4>
<ul>
<li>Fælles ModuleRegistry for Køretøjer, Events og Billedgalleri.</li>
<li>Canonical ModuleRecord v1 med fleksible, ordnede attributter til bl.a. tekniske køretøjsdata.</li>
<li>Privat WordPress ModuleStore med canonical JSON, indeks-meta og SHA-256 digest.</li>
<li>ModuleBinding v1 for kommende liste/detail-elementer og dynamisk datasource.</li>
<li>Release-QA er forward-kompatibel med Icon Library fra v0.1.66.</li>
</ul>
''')

write('docs/v0167-status.md', '''# Visual Designer Manager v0.1.67 – teststatus

Status: TESTKANDIDAT

Scope:
- VD-MODULE-DATA-001 fælles Module/Data Foundation.
- ModuleRegistry: vehicles, events, galleries.
- ModuleRecord schema 1 med stabile IDs, standardfelter, fleksible attributter, media og digest.
- ModuleStore på privat WordPress post type med canonical JSON og indeks-meta.
- ModuleBinding schema 1 til kommende liste/detail-databinding.
- Canonical backlog synkroniseret til v0.1.67.
- v0.1.65 elementmodel-QA gjort forward-kompatibel med IconRegistry.

Ikke med i denne version:
- Manager-CRUD-skærm til Køretøjer.
- Aktiv dynamisk rendering i Data List/Tabel.
- Event- og Billedgalleri-UI.
- Custom icon upload/persistent storage.

Næste planlagte modul:
- Køretøjer: records, fleksible tekniske felter, billeder, sortering samt Designer liste/detail-elementer.
''')

print('Applied Visual Designer Manager v0.1.67 module/data foundation.')
