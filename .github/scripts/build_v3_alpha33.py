from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.33'
DEST = Path('build/visual-designer-manager')
ASSET_ROOT = Path('.github/release-assets/alpha33')

subprocess.run(['python3', '.github/scripts/build_v3_alpha32.py'], check=True)


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


def replace_once(rel: str, old: str, new: str, label: str) -> None:
    value = read(rel)
    count = value.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected exactly one anchor in {rel}, found {count}')
    write(rel, value.replace(old, new, 1))


# ---------------------------------------------------------------------------
# Version cutover.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.32', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.32');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.32');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.33 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# V1-converted page marker for the editor. Frontend already detects this same
# post meta key in ResponsiveRenderer::legacyPageModel(). Alpha.33 exposes the
# contract to the Designer so phone preview can render the same flow.
# ---------------------------------------------------------------------------
replace_once(
    'visual-designer-manager.php',
    "        'postId' => $postId,\n        'userId' => get_current_user_id(),\n",
    "        'postId' => $postId,\n        'legacyMobileFlow' => metadata_exists('post', $postId, '_h18_clean_layout_v1'),\n        'userId' => get_current_user_id(),\n",
    'Alpha.33 editor legacy mobile flag'
)

replace_once(
    'visual-designer-manager.php',
    "    wp_enqueue_style(\n        'h18-clean-editor-v0181',\n        H18_CLEAN_URL . 'assets/editor-v0181.css',\n        ['h18-clean-editor-v0166-foundation'],\n        H18_CLEAN_VERSION\n    );\n\n    wp_enqueue_script(\n",
    "    wp_enqueue_style(\n        'h18-clean-editor-v0181',\n        H18_CLEAN_URL . 'assets/editor-v0181.css',\n        ['h18-clean-editor-v0166-foundation'],\n        H18_CLEAN_VERSION\n    );\n    wp_enqueue_style(\n        'h18-clean-editor-v0182-v1-mobile-parity',\n        H18_CLEAN_URL . 'assets/editor-v0182-v1-mobile-parity.css',\n        ['h18-clean-editor-v0181'],\n        H18_CLEAN_VERSION\n    );\n\n    wp_enqueue_script(\n",
    'Alpha.33 parity stylesheet enqueue'
)

replace_once(
    'visual-designer-manager.php',
    "    wp_enqueue_script(\n        'h18-clean-editor-v0181-color-picker',\n        H18_CLEAN_URL . 'assets/editor-v0181-color-picker.js',\n        ['h18-clean-editor-v0169-canvas-height'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    /* v0.1.6 border/autogrow JS is retired; current Clean core handles these natively. */\n",
    "    wp_enqueue_script(\n        'h18-clean-editor-v0181-color-picker',\n        H18_CLEAN_URL . 'assets/editor-v0181-color-picker.js',\n        ['h18-clean-editor-v0169-canvas-height'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    wp_enqueue_script(\n        'h18-clean-editor-v0182-v1-mobile-parity',\n        H18_CLEAN_URL . 'assets/editor-v0182-v1-mobile-parity.js',\n        ['h18-clean-editor-v0181-color-picker', 'h18-clean-editor-v0121'],\n        H18_CLEAN_VERSION,\n        true\n    );\n    /* v0.1.6 border/autogrow JS is retired; current Clean core handles these natively. */\n",
    'Alpha.33 parity script enqueue'
)

for name in ['editor-v0182-v1-mobile-parity.js', 'editor-v0182-v1-mobile-parity.css']:
    source = ASSET_ROOT / name
    if not source.is_file():
        raise SystemExit(f'Alpha.33 release asset missing: {source}')
    write('assets/' + name, source.read_text(encoding='utf-8'))

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.32':
    raise SystemExit('Expected Alpha.32 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-09',
    'items': [
        'Designerens mobilvisning for V1-konverterede sider bruger nu samme automatiske enkolonne-flow som frontend i stedet for gemt mobil X/Y/H-geometri.',
        'Hero, tagline, V1-sektionsafstande, mobiltypografi, skjulte spacere og semantiske V1-indholdsbånd projiceres efter samme kontrakt som den offentlige side.',
        'Mobilgeometri-kontroller og resize/move-håndtag markeres som inaktive i V1 mobilflow, fordi frontend bevidst bruger Desktop som kanonisk rækkefølge.',
        'Desktop, Laptop og Tablet beholder den eksisterende responsive Designer-adfærd. Alpha.32 updater-kanal og Alpha.31 Footer-gap-kontrakter bevares.',
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts + regression locks.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
parity_js = read('assets/editor-v0182-v1-mobile-parity.js')
parity_css = read('assets/editor-v0182-v1-mobile-parity.css')
responsive = read('src/Frontend/ResponsiveRenderer.php')
updater = read('src/Update/GitHubUpdater.php')
module_design = read('src/Model/ModuleDesignModel.php')
editor = read('src/Admin/EditorController.php')
collection = read('src/Frontend/CollectionPageRenderer.php')
history_text = read('release-history.json')

for token in [
    'Version: 3.0.0-alpha.33',
    "define('VDM_VERSION', '3.0.0-alpha.33');",
    "define('H18_CLEAN_VERSION', '3.0.0-alpha.33');",
    "'legacyMobileFlow' => metadata_exists('post', $postId, '_h18_clean_layout_v1'),",
    "'h18-clean-editor-v0182-v1-mobile-parity'",
]:
    if token not in main:
        raise SystemExit(f'Alpha.33 main token missing: {token}')

for token in [
    "activeDevice() !== 'mobile'",
    "g.w >= 100",
    "bevaring, restaurering og levende",
    "majorHeadings = ['Om foreningen'",
    "pageGap(model, 'sectionGap', 24)",
    "pageGap(model, 'elementGap', 14)",
    "h18-vd-parity-structural-path",
]:
    if token not in parity_js:
        raise SystemExit(f'Alpha.33 parity JS token missing: {token}')
for token in [
    'height:155px!important',
    'padding:12px 15px!important',
    'padding:30px 15px!important',
    'width:calc(100% - 20px)!important',
    'font-size:25px!important',
    'V1 mobilflow er aktivt',
]:
    if token not in parity_css:
        raise SystemExit(f'Alpha.33 parity CSS token missing: {token}')

for token in [
    'private static function v1MobileFlowCss(',
    'private static function v1MobileVisualParityCss(',
    'private static function v1MobileEdgeSpacingCss(',
    'private static function v1NestedMobileEdgeParityCss(',
    'return $desktop;',
    'height:155px!important',
    'padding:12px 15px!important',
    "['Bevaring', 'Formidling', 'Fællesskab']",
]:
    if token not in responsive:
        raise SystemExit(f'Alpha.33 retained frontend parity token missing: {token}')

stable_manifest = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/v3-clean-refactor/v3-update.json'
if stable_manifest not in updater:
    raise SystemExit('Alpha.33 stable updater manifest URL missing')

for token in ["'footerGap' => 64", "'footerGap' => self::clamp("]:
    if token not in module_design:
        raise SystemExit(f'Alpha.33 retained ModuleDesign token missing: {token}')
for token in ['Afstand til Footer (px)', 'gælder både moduloversigten og modulets detaljesider']:
    if token not in editor:
        raise SystemExit(f'Alpha.33 retained Editor token missing: {token}')
for token in ['--h18-module-footer-gap:', 'padding:36px 0 var(--h18-module-footer-gap)']:
    if token not in collection:
        raise SystemExit(f'Alpha.33 retained Collection token missing: {token}')

if '3.0.0-alpha.33' not in history_text:
    raise SystemExit('Alpha.33 history token missing')

print('PASS')
