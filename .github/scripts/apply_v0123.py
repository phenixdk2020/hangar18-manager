#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding='utf-8')
    if new in text:
        return
    if old not in text:
        raise SystemExit(f'{path}: expected source snippet not found')
    path.write_text(text.replace(old, new, 1), encoding='utf-8')
    print(f'patched {path.relative_to(ROOT)}')


# 1) Larger, useful starting sizes for all four current Designer element types.
core = ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js'
replace_once(
    core,
    """        const defaultH = (type === 'text' || type === 'image') ? Math.max(1, Math.ceil(80 / ROW_PX)) : 0;\n        const desktop = normalizeDevice({ x: p.x, y: p.y, w: p.w || defaultW, h: defaultH }, false);\n        state.nodes.push({\n""",
    """        const defaultRows = { section: 20, container: 16, text: 14, image: 20 };\n        const defaultH = Math.max(MIN_SPLIT_H, parseInt(defaultRows[type] || MIN_SPLIT_H, 10) || MIN_SPLIT_H);\n        const newProps = normalizeProps(type, {});\n        if (PARENT_TYPES.includes(type)) { newProps.minHeightRows = defaultH; }\n        const desktop = normalizeDevice({ x: p.x, y: p.y, w: p.w || defaultW, h: defaultH }, false);\n        state.nodes.push({\n"""
)
replace_once(
    core,
    """            props: normalizeProps(type, {})\n        });\n""",
    """            props: newProps\n        });\n"""
)

# 2) Load the 0.1.23 Designer UX overlay and bump visible/runtime version.
bootstrap = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
replace_once(bootstrap, ' * Version: 0.1.22\n', ' * Version: 0.1.23\n')
replace_once(bootstrap, "define('H18_CLEAN_VERSION', '0.1.22');", "define('H18_CLEAN_VERSION', '0.1.23');")
replace_once(
    bootstrap,
    """    wp_enqueue_style(\n        'h18-clean-editor-v0122-hierarchy',\n        H18_CLEAN_URL . 'assets/editor-v0122-hierarchy.css',\n        ['h18-clean-editor-v0121'],\n        H18_CLEAN_VERSION\n    );\n\n""",
    """    wp_enqueue_style(\n        'h18-clean-editor-v0122-hierarchy',\n        H18_CLEAN_URL . 'assets/editor-v0122-hierarchy.css',\n        ['h18-clean-editor-v0121'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_style(\n        'h18-clean-editor-v0123-ux',\n        H18_CLEAN_URL . 'assets/editor-v0123-ux.css',\n        ['h18-clean-editor-v0122-hierarchy'],\n        H18_CLEAN_VERSION\n    );\n\n"""
)
replace_once(
    bootstrap,
    """    wp_enqueue_script(\n        'h18-clean-editor-v0122-hierarchy',\n        H18_CLEAN_URL . 'assets/editor-v0122-hierarchy.js',\n        ['h18-clean-editor-v0121-panels'],\n        H18_CLEAN_VERSION,\n        true\n    );\n""",
    """    wp_enqueue_script(\n        'h18-clean-editor-v0122-hierarchy',\n        H18_CLEAN_URL . 'assets/editor-v0122-hierarchy.js',\n        ['h18-clean-editor-v0121-panels'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    wp_enqueue_script(\n        'h18-clean-editor-v0123-ux',\n        H18_CLEAN_URL . 'assets/editor-v0123-ux.js',\n        ['h18-clean-editor-v0122-hierarchy'],\n        H18_CLEAN_VERSION,\n        true\n    );\n"""
)

# 3) Load Manager status markers and simplified Menu UX on Manager pages.
admin = ROOT / 'clean/hangar18-manager/src/Admin/AdminController.php'
replace_once(
    admin,
    """        wp_enqueue_style('h18-clean-manager-admin', H18_CLEAN_URL . 'assets/admin-v019.css', [], H18_CLEAN_VERSION);\n""",
    """        wp_enqueue_style('h18-clean-manager-admin', H18_CLEAN_URL . 'assets/admin-v019.css', [], H18_CLEAN_VERSION);\n        wp_enqueue_style('h18-clean-manager-v0123', H18_CLEAN_URL . 'assets/admin-v0123.css', ['h18-clean-manager-admin'], H18_CLEAN_VERSION);\n        wp_enqueue_script('h18-clean-manager-v0123', H18_CLEAN_URL . 'assets/admin-v0123.js', [], H18_CLEAN_VERSION, true);\n"""
)

# 4) Current plugin readme version and 0.1.23 change summary.
readme = ROOT / 'clean/hangar18-manager/readme.txt'
text = readme.read_text(encoding='utf-8')
text = text.replace('Version: 0.1.15', 'Version: 0.1.23', 1)
section = """\n== 0.1.23 ==\n* Manager-menuen viser modulstatus visuelt: grøn = klar, gul = under udvikling/ikke færdig.\n* Menu / Navigation er forenklet i standardvisningen; tekniske felter, theme locations og versionshistorik er sekundære/avancerede.\n* Nye Sektion/Kasse/Tekst/Billede starter med større, mere anvendelige højder.\n* Grøn selection-outline er gjort tykkere.\n* Ændringsbeskrivelsen ved Gem er valgfri; hvis feltet er tomt, genereres en kort ændringsbeskrivelse automatisk.\n* Tekst-preview i Designer bevarer linjeskift og tomme linjer.\n* Manuel billedredigering er gjort tydeligere, og reset til Vis hele billedet rydder den sandfarvede billedindholdsramme og manuelle styles.\n\n"""
if '== 0.1.23 ==' not in text:
    marker = 'Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.\n'
    if marker not in text:
        raise SystemExit('readme.txt: description marker missing')
    text = text.replace(marker, marker + section, 1)
readme.write_text(text, encoding='utf-8')

# 5) Keep living documentation current.
def append_section(rel: str, title: str, body: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    if title in text:
        return
    text = text.rstrip() + '\n\n' + title + '\n\n' + body.strip() + '\n'
    path.write_text(text, encoding='utf-8')
    print(f'updated docs: {rel}')

append_section(
    'CLEAN-USER-MANUAL.md',
    '## 0.1.23 – UX, Menu-status og lettere billedredigering',
    '''- Managerens undermenu viser nu status: **Klar** (grøn) eller **Under udvikling / Ikke færdig** (gul).\n- Menu / Navigation viser den normale arbejdsgang først; tekniske indstillinger og versionshistorik ligger under Avanceret.\n- Nye Sektioner, Kasser, Tekst- og Billede-elementer starter større.\n- Den grønne markering af valgt element er tykkere.\n- Feltet **Ændringer** ved Gem er valgfrit. Tomt felt giver en automatisk ændringsbeskrivelse i versionshistorikken.\n- Tekst i Designer bevarer linjeskift/tomme linjer.\n- Under Billede er **Billedindhold** tydeliggjort som separat fra den grønne billedboks. Reset til **Vis hele billedet** rydder manuel billedgeometri visuelt.'''
)
append_section(
    'CLEAN-DESIGN-MANUAL.md',
    '## 0.1.23 – UX-regler og modulstatus',
    '''- Manager-moduler skal vise tydelig modenhedsstatus. Grøn betyder klar/brugbart modul; gul betyder delvist implementeret eller planlagt modul.\n- Teknisk/avanceret Menu-funktionalitet må ikke dominere standardarbejdsgangen. Normal navigation skal kunne redigeres uden kendskab til parent-ID, positionstal eller theme-location-begreber.\n- Selection-markering skal være tydelig uden at ændre canonical geometri.\n- Tekst-preview skal bevare forfatterens linjeskift.\n- Billedboks og billedindhold skal fremstå som to eksplicitte redigeringslag.\n- Versionsnote er valgfri; manglende bruger-note erstattes af systemgenereret ændringsbeskrivelse.'''
)
append_section(
    'docs/CLEAN-HANDOVER.md',
    '## 0.1.23 – Godkendt UX-retning',
    '''0.1.23 samler brugerfeedback fra 0.1.22-testen: større element-defaults, tykkere grøn selection, valgfri/automatisk versionsnote, korrekt tekst-preview med linjeskift, tydelig separat billedindholdsredigering/reset samt visuelle modulstatusser i Manageren. Menu / Navigation følger princippet **simpel først, avanceret sekundært**. Gul status betyder, at modulet ikke skal opfattes som færdigt.'''
)

# 6) Hard QA assertions for the intended source state.
checks = {
    'clean/hangar18-manager/hangar18-manager.php': ["Version: 0.1.23", "H18_CLEAN_VERSION', '0.1.23", 'editor-v0123-ux.js', 'editor-v0123-ux.css'],
    'clean/hangar18-manager/src/Admin/AdminController.php': ['admin-v0123.css', 'admin-v0123.js'],
    'clean/hangar18-manager/assets/editor-v018-core.js': ['const defaultRows = { section: 20, container: 16, text: 14, image: 20 };', 'props: newProps'],
    'clean/hangar18-manager/assets/editor-v0123-ux.js': ['automaticChangeNote', 'Tilbage til Vis hele billedet'],
    'clean/hangar18-manager/assets/admin-v0123.js': ['Under udvikling', 'simplifyNavigationPage'],
}
for rel, needles in checks.items():
    data = (ROOT / rel).read_text(encoding='utf-8')
    for needle in needles:
        if needle not in data:
            raise SystemExit(f'{rel}: missing expected 0.1.23 marker: {needle}')

print('Visual Designer Manager 0.1.23 patch QA PASS')
