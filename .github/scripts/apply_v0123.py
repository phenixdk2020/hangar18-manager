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


def append_section(rel: str, title: str, body: str) -> None:
    path = ROOT / rel
    text = path.read_text(encoding='utf-8')
    if title in text:
        return
    path.write_text(text.rstrip() + '\n\n' + title + '\n\n' + body.strip() + '\n', encoding='utf-8')
    print(f'updated docs: {rel}')


# 1) Designer UX defaults from 0.1.22 user testing.
core = ROOT / 'clean/hangar18-manager/assets/editor-v018-core.js'
replace_once(
    core,
    """        const defaultH = (type === 'text' || type === 'image') ? Math.max(1, Math.ceil(80 / ROW_PX)) : 0;\n        const desktop = normalizeDevice({ x: p.x, y: p.y, w: p.w || defaultW, h: defaultH }, false);\n        state.nodes.push({\n""",
    """        const defaultRows = { section: 20, container: 16, text: 14, image: 20 };\n        const defaultH = Math.max(MIN_SPLIT_H, parseInt(defaultRows[type] || MIN_SPLIT_H, 10) || MIN_SPLIT_H);\n        const newProps = normalizeProps(type, {});\n        if (PARENT_TYPES.includes(type)) { newProps.minHeightRows = defaultH; }\n        if (type === 'text') { newProps.padding = 12; }\n        const desktop = normalizeDevice({ x: p.x, y: p.y, w: p.w || defaultW, h: defaultH }, false);\n        state.nodes.push({\n"""
)
replace_once(core, """            props: normalizeProps(type, {})\n        });\n""", """            props: newProps\n        });\n""")
replace_once(
    core,
    """            body.textContent = String(node.props.text || 'Ny tekst').replace(/<[^>]+>/g, '').slice(0, 220) || 'Tekst';\n""",
    """            body.textContent = String(node.props.text || 'Ny tekst').replace(/<[^>]+>/g, '') || 'Tekst';\n"""
)

# 2) Bootstrap 0.1.23, global Header/Footer model/controller, and shared Designer assets.
bootstrap = ROOT / 'clean/hangar18-manager/hangar18-manager.php'
replace_once(bootstrap, ' * Version: 0.1.22\n', ' * Version: 0.1.23\n')
replace_once(bootstrap, "define('H18_CLEAN_VERSION', '0.1.22');", "define('H18_CLEAN_VERSION', '0.1.23');")
replace_once(
    bootstrap,
    "require_once H18_CLEAN_DIR . 'src/Model/LayoutModel.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Model/LayoutModel.php';\nrequire_once H18_CLEAN_DIR . 'src/Model/GlobalLayoutModel.php';\n"
)
replace_once(
    bootstrap,
    "require_once H18_CLEAN_DIR . 'src/Admin/ThemeController.php';\n",
    "require_once H18_CLEAN_DIR . 'src/Admin/ThemeController.php';\nrequire_once H18_CLEAN_DIR . 'src/Admin/GlobalDesignerController.php';\n"
)
replace_once(
    bootstrap,
    "    \\Hangar18\\Clean\\Admin\\ThemeController::register();\n",
    "    \\Hangar18\\Clean\\Admin\\ThemeController::register();\n    \\Hangar18\\Clean\\Admin\\GlobalDesignerController::register();\n"
)
replace_once(
    bootstrap,
    """add_action('admin_enqueue_scripts', static function (string $hook): void {\n    if (strpos($hook, 'h18-clean-editor') === false || !current_user_can('edit_pages')) {\n        return;\n    }\n""",
    """add_action('admin_enqueue_scripts', static function (string $hook): void {\n    $isPageDesigner = strpos($hook, 'h18-clean-editor') !== false;\n    $isGlobalDesigner = strpos($hook, 'h18-clean-header-footer') !== false;\n    if ((!$isPageDesigner && !$isGlobalDesigner) || !current_user_can('edit_pages')) {\n        return;\n    }\n"""
)
replace_once(
    bootstrap,
    """    $postId = isset($_GET['post']) ? absint($_GET['post']) : 0;\n    $model = $postId > 0 && get_post_type($postId) === 'page'\n        ? \\Hangar18\\Clean\\Model\\LayoutModel::get($postId)\n        : \\Hangar18\\Clean\\Model\\LayoutModel::empty();\n""",
    """    $postId = isset($_GET['post']) ? absint($_GET['post']) : 0;\n    if ($isGlobalDesigner) {\n        $part = isset($_GET['part']) && sanitize_key((string) $_GET['part']) === 'footer' ? 'footer' : 'header';\n        $postId = 0;\n        $model = \\Hangar18\\Clean\\Model\\GlobalLayoutModel::get($part);\n    } else {\n        $model = $postId > 0 && get_post_type($postId) === 'page'\n            ? \\Hangar18\\Clean\\Model\\LayoutModel::get($postId)\n            : \\Hangar18\\Clean\\Model\\LayoutModel::empty();\n    }\n"""
)
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

# 3) Manager status markers only. Menu redesign is deliberately deferred.
admin = ROOT / 'clean/hangar18-manager/src/Admin/AdminController.php'
replace_once(
    admin,
    "        wp_enqueue_style('h18-clean-manager-admin', H18_CLEAN_URL . 'assets/admin-v019.css', [], H18_CLEAN_VERSION);\n",
    "        wp_enqueue_style('h18-clean-manager-admin', H18_CLEAN_URL . 'assets/admin-v019.css', [], H18_CLEAN_VERSION);\n        wp_enqueue_style('h18-clean-manager-v0123', H18_CLEAN_URL . 'assets/admin-v0123.css', ['h18-clean-manager-admin'], H18_CLEAN_VERSION);\n        wp_enqueue_script('h18-clean-manager-v0123', H18_CLEAN_URL . 'assets/admin-v0123.js', [], H18_CLEAN_VERSION, true);\n"
)

# 4) Readme and living documentation.
readme = ROOT / 'clean/hangar18-manager/readme.txt'
text = readme.read_text(encoding='utf-8')
text = text.replace('Version: 0.1.15', 'Version: 0.1.23', 1)
section = """\n== 0.1.23 ==\n* Første globale Header/Footer Designer med separat canonical model og versionshistorik.\n* Header og Footer bruger samme 120-unit / 8-px layoutmotor og Desktop/Laptop/Mobil-model som Side Designer.\n* Manager-menuen viser modulstatus visuelt: grøn = klar, gul = under udvikling/ikke færdig.\n* Menu-redesign er bevidst udskudt, til Menu-elementet bygges ind i Header/Footer.\n* Nye Sektion/Kasse/Tekst/Billede starter større; ny Tekst får 12 px standard-padding.\n* Grøn selection-outline er tykkere.\n* Ændringsbeskrivelsen ved Gem er valgfri og genereres automatisk, hvis feltet er tomt.\n* Tekst-preview bevarer hele teksten, linjeskift og tomme linjer.\n* Manuel billedredigering er tydeligere, og reset til Vis hele billedet rydder manuel UI-state korrekt.\n\n"""
if '== 0.1.23 ==' not in text:
    marker = 'Modeldrevet visuel WordPress-designer med responsive layouts, versionshistorik og Manager-funktioner.\n'
    if marker not in text:
        raise SystemExit('readme.txt: description marker missing')
    text = text.replace(marker, marker + section, 1)
readme.write_text(text, encoding='utf-8')

append_section(
    'CLEAN-USER-MANUAL.md',
    '## 0.1.23 – Header/Footer Designer og UX-rettelser',
    '''- **Header / Footer** i Manager åbner nu en global Visual Designer med fanerne Header og Footer.\n- Header og Footer har hver sin canonical model, indstillinger og versionshistorik og ændrer ikke sideversionerne.\n- Fase 1 bruger Sektion, Kasse, Tekst og Billede samt Desktop/Laptop/Mobil. Menu/Knap/Ikon kommer efter layout-QA.\n- Manager-menuen viser **Klar** (grøn) og **Under udvikling / Ikke færdig** (gul).\n- Menu-redigeringen er ikke redesignet endnu; den afventer Header/Footer og det kommende Menu-element.\n- Nye elementer starter større; ny Tekst får 12 px padding.\n- Grøn selection er tykkere, Gem-note er valgfri/automatisk, tekst-preview bevarer linjeskift, og billed-reset rydder manuel billedramme korrekt.'''
)
append_section(
    'CLEAN-DESIGN-MANUAL.md',
    '## 0.1.23 – Global Header/Footer Designer',
    '''- Header og Footer er globale Visual Designer-modeller i separat storage og med separat ikke-destruktiv versionshistorik.\n- De genbruger Side Designer-layoutmotoren; der må ikke opstå en parallel Header/Footer-layoutmotor.\n- 0.1.23 overtager ikke endnu temaets runtime Header/Footer. Indstillingen kan klargøres, men frontend-aktivering venter på Theme-shell integration for at undgå dobbelt Header/Footer.\n- Menu-data bevares separat. Visuelt Menu-element bygges først efter Header/Footer-canvas og indsættes derefter som et normalt globalt element.\n- Manager-moduler viser modenhedsstatus; gul betyder ikke færdig.\n- Versionsnote er valgfri og kan systemgenereres.'''
)
append_section(
    'docs/CLEAN-HANDOVER.md',
    '## 0.1.23 – Header/Footer før Menu',
    '''Brugerbeslutning 26-08-2026: Visuelt Menu-arbejde skal vente, til Header/Footer Designer findes. 0.1.23 prioriterer derfor global Header/Footer-model, fælles Designer-canvas og versionering samt UX-rettelser fra 0.1.22-testen. Menu-data må fortsat eksistere, men Menu UI/element må ikke færdigdesignes før Header/Footer-layoutet er testet.'''
)

spec = ROOT / 'docs/HEADER-FOOTER-SPEC.md'
spec_text = spec.read_text(encoding='utf-8')
old_order = """1. 0.1.22 – hierarki og layout-QA;\n2. Global Design-model;\n3. Theme-shell-kontrakt;\n4. Menu-data-/Menu-element-kontrakt;\n5. Header Designer;\n6. Footer Designer;\n7. mobilmenu og accessibility-QA;\n8. parity-test mod eksisterende site;\n9. Export/Import integration.\n"""
new_order = """1. 0.1.22 – hierarki og layout-QA;\n2. 0.1.23 – global Header/Footer-model og fælles Designer-canvas;\n3. Header/Footer layout-QA med Sektion/Kasse/Tekst/Billede;\n4. Global Design-model og Theme-shell-kontrakt;\n5. Menu-element oven på eksisterende Menu-data;\n6. mobilmenu og accessibility-QA;\n7. parity-test mod eksisterende site;\n8. Export/Import integration.\n"""
if new_order not in spec_text:
    if old_order not in spec_text:
        raise SystemExit('HEADER-FOOTER-SPEC: implementation order not found')
    spec.write_text(spec_text.replace(old_order, new_order, 1), encoding='utf-8')

# 5) Hard QA assertions.
checks = {
    'clean/hangar18-manager/hangar18-manager.php': ['Version: 0.1.23', 'GlobalLayoutModel.php', 'GlobalDesignerController.php', 'editor-v0123-ux.js'],
    'clean/hangar18-manager/src/Admin/AdminController.php': ['admin-v0123.css', 'admin-v0123.js'],
    'clean/hangar18-manager/src/Model/GlobalLayoutModel.php': ['saveVersion', 'historyState'],
    'clean/hangar18-manager/src/Admin/GlobalDesignerController.php': ['Header / Footer Designer', 'h18_clean_global_layout_save'],
    'clean/hangar18-manager/assets/editor-v018-core.js': ['const defaultRows = { section: 20, container: 16, text: 14, image: 20 };', 'newProps.padding = 12'],
    'clean/hangar18-manager/assets/editor-v0123-ux.js': ['automaticChangeNote', 'Tilbage til Vis hele billedet'],
    'clean/hangar18-manager/assets/admin-v0123.js': ['Under udvikling'],
    'clean/hangar18-manager/assets/global-designer-v0123.js': ['previewLayout'],
}
for rel, needles in checks.items():
    data = (ROOT / rel).read_text(encoding='utf-8')
    for needle in needles:
        if needle not in data:
            raise SystemExit(f'{rel}: missing expected 0.1.23 marker: {needle}')
if 'simplifyNavigationPage' in (ROOT / 'clean/hangar18-manager/assets/admin-v0123.js').read_text(encoding='utf-8'):
    raise SystemExit('Menu redesign must remain deferred in 0.1.23')

print('Visual Designer Manager 0.1.23 Header/Footer + UX patch QA PASS')
