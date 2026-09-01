from __future__ import annotations

from pathlib import Path
import json

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
    if new and new in value:
        return
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{rel}: expected one replacement anchor, found {count}: {old[:120]}')
    write(rel, value.replace(old, new, 1))


def append_once(rel: str, marker: str, block: str) -> None:
    value = read(rel)
    if marker in value:
        return
    write(rel, value.rstrip() + '\n\n' + block.strip() + '\n')


PLUGIN = 'clean/hangar18-manager/hangar18-manager.php'
PARITY_CSS = 'clean/hangar18-manager/assets/editor-v0166-foundation.css'
HISTORY = 'clean/hangar18-manager/release-history.json'
BACKLOG = 'docs/clean-backlog-v0100.md'
V0172_QA = '.github/scripts/v0172_gallery_design_qa.py'

# ---------------------------------------------------------------------------
# v0.1.73 runtime version
# ---------------------------------------------------------------------------
replace_once(PLUGIN, ' * Version: 0.1.72', ' * Version: 0.1.73')
replace_once(PLUGIN,
             "define('H18_CLEAN_VERSION', '0.1.72');",
             "define('H18_CLEAN_VERSION', '0.1.73');")

# ---------------------------------------------------------------------------
# VD-EDITOR-FRONTEND-PARITY-001
# Editor-only chrome must not consume canonical node geometry. The frontend
# renderer remains untouched; this makes the canvas represent the same saved
# box dimensions instead of adding 28px headers, preview padding and guide
# borders/margins inside the layout flow.
# ---------------------------------------------------------------------------
append_once(PARITY_CSS, 'VD-EDITOR-FRONTEND-PARITY-001', r'''
/* Visual Designer Manager 0.1.73 · VD-EDITOR-FRONTEND-PARITY-001
 * Editor chrome is an overlay and must never participate in canonical geometry.
 */
.h18-clean-surface{align-items:stretch}
.h18-clean-node-header{position:absolute;top:0;left:0;right:0;z-index:80;height:28px;margin:0;opacity:0;pointer-events:none;transform:translateY(-100%);transition:opacity .12s ease,transform .12s ease}
.h18-clean-node:hover>.h18-clean-node-header,.h18-clean-node.is-selected>.h18-clean-node-header,.h18-clean-node.is-dragging>.h18-clean-node-header,.h18-clean-node.is-resizing>.h18-clean-node-header{opacity:.96;pointer-events:auto;transform:translateY(0)}
.h18-clean-node-preview{min-height:0;padding:0}
.h18-clean-node[data-h18-explicit-grid="1"]>.h18-clean-node-preview{height:100%}
.h18-clean-node-preview--image{min-height:0;height:100%}
.h18-clean-inner-surface{margin-top:0;min-height:0;border:0;outline:1px dashed #a7aaad;outline-offset:-1px}
''')

# ---------------------------------------------------------------------------
# Make the v0.1.72 feature QA forward-compatible. It must continue checking
# Gallery/Site Design contracts without pinning the *current* product release.
# ---------------------------------------------------------------------------
replace_once(V0172_QA,
'''require('clean/hangar18-manager/hangar18-manager.php',
        ' * Version: 0.1.72',
        "define('H18_CLEAN_VERSION', '0.1.72');",
        "src/Admin/GalleryAdminController.php",''',
'''require('clean/hangar18-manager/hangar18-manager.php',
        "src/Admin/GalleryAdminController.php",''')
replace_once(V0172_QA,
'''require('docs/clean-backlog-v0100.md',
        '**Aktuel release:** v0.1.72',
        'VD-GALLERY-MODULE-001 — FÆRDIG I v0.1.72',
        'VD-SITE-DESIGN-HARMONY-001 — FÆRDIG I v0.1.72',
        'v0.1.73 – Modul-cutover/migrering — NÆSTE')''',
'''require('docs/clean-backlog-v0100.md',
        'VD-GALLERY-MODULE-001 — FÆRDIG I v0.1.72',
        'VD-SITE-DESIGN-HARMONY-001 — FÆRDIG I v0.1.72')''')
replace_once(V0172_QA,
"require('clean-release-notes.html', '0.1.72 – Billedgalleri + Site Design Harmony')\n",
"")

# ---------------------------------------------------------------------------
# Release history + concise canonical status/backlog.
# ---------------------------------------------------------------------------
history = json.loads(read(HISTORY))
versions = history.get('versions', []) if isinstance(history, dict) else []
if not any(isinstance(row, dict) and str(row.get('version', '')) == '0.1.73' for row in versions):
    versions.insert(0, {
        'version': '0.1.73',
        'date': '2026-09-01',
        'items': [
            'VD-EDITOR-FRONTEND-PARITY-001: editorens værktøjsheader er nu overlay og optager ikke canonical højde.',
            'Generisk editor-preview padding/min-height er fjernet, så gemte node-mål svarer til frontendens renderede bokse.',
            'Sektion/Kasse-hjælperammen bruger outline uden margin/border og ændrer derfor ikke child-grid geometri.',
            'Rettelsen gælder samme fælles canvas-runtime for sider, Header og Footer og ændrer ikke gemte layouts.'
        ],
    })
history['versions'] = versions
write(HISTORY, json.dumps(history, ensure_ascii=False, indent=2) + '\n')

backlog = read(BACKLOG)
backlog = backlog.replace('**Aktuel release:** v0.1.72', '**Aktuel release:** v0.1.73', 1)
backlog = backlog.replace('## Aktuel milepælsstatus · v0.1.72', '## Aktuel milepælsstatus · v0.1.73', 1)
anchor = '- **VD-SITE-DESIGN-HARMONY-001 — IMPLEMENTERET I v0.1.72:** de seks øvrige hovedsider harmoniseres sikkert med Hjem med backup og versionering.\n'
parity_line = '- **VD-EDITOR-FRONTEND-PARITY-001 — IMPLEMENTERET I v0.1.73:** editor-chrome ligger som overlay og påvirker ikke længere den visuelle nodegeometri for sider, Header eller Footer.\n'
if parity_line not in backlog:
    first = backlog.find(anchor)
    if first < 0:
        raise SystemExit(f'{BACKLOG}: parity insertion anchor missing')
    insert_at = first + len(anchor)
    backlog = backlog[:insert_at] + parity_line + backlog[insert_at:]
roadmap_old = '5. **v0.1.73 – Modul-cutover/migrering — NÆSTE:** samlet legacy data-/module-migrering med side-by-side QA før cutover.'
roadmap_new = '5. **v0.1.73 – Editor/frontend visuel paritet — FÆRDIG:** editorens hjælpe-UI er overlay og ændrer ikke canonical mål.\n6. **v0.1.74 – Modul-cutover/migrering — NÆSTE:** samlet legacy data-/module-migrering med side-by-side QA før cutover.'
if roadmap_new not in backlog:
    if roadmap_old not in backlog:
        raise SystemExit(f'{BACKLOG}: roadmap anchor missing')
    backlog = backlog.replace(roadmap_old, roadmap_new, 1)
write(BACKLOG, backlog)

write('clean-release-notes.html', '''<h2>0.1.73 – Editor/frontend visuel paritet</h2>\n<ul>\n<li><strong>VD-EDITOR-FRONTEND-PARITY-001:</strong> editorens elementheader er nu et overlay og optager ikke layoutplads.</li>\n<li>Standard-preview padding og minimumshøjde er fjernet, så gemte bredder/højder vises uden editor-tillæg.</li>\n<li>Sektion/Kasse-hjælperammer bruger outline i stedet for margin/border og forskyder ikke indhold.</li>\n<li>Rettelsen gælder den fælles canvas-runtime for almindelige sider, Header og Footer og ændrer ikke eksisterende gemte layouts.</li>\n<li>Canonical PHP-preview/frontend-renderer er fortsat reference for den endelige visning.</li>\n</ul>\n''')

write('docs/v0173-status.md', '''# Visual Designer Manager v0.1.73\n\nStatus: release candidate\n\n## VD-EDITOR-FRONTEND-PARITY-001\n\n- Editorens 28 px elementheader er flyttet ud af layoutflowet og vises som overlay ved hover/selection/drag/resize.\n- Generisk `.h18-clean-node-preview` har ikke længere 8 px editor-padding eller 48 px editor-minimum.\n- Billedpreview bruger hele den canonical elementhøjde i stedet for `calc(100% - 28px)`.\n- Sektion/Kasse-surface har ingen editor-margin eller border, kun en ikke-pladsforbrugende outline.\n- Canvas bruger stretch som frontend-grid, så eksplícitte gridområder udfyldes efter den gemte geometri.\n- Ingen layout-JSON, node-IDer, hierarchy, Desktop/Laptop/Tablet/Mobil-geometri eller frontend Renderer ændres af denne release.\n\n## QA-gate\n\n1. PHP- og JavaScript-syntax skal være grøn.\n2. Historiske Header/Footer-, hierarchy-, clipboard-, element-, module- og canvas-regressionstests skal fortsat bestå.\n3. Statisk parity-QA skal bekræfte, at editor-chrome ikke længere kan optage canonical layoutplads.\n4. Release bygges fortsat af den centrale Visual Designer Manager Release-workflow med ZIP + SHA-256 manifest.\n''')

print('Applied Visual Designer Manager v0.1.73 editor/frontend parity')
