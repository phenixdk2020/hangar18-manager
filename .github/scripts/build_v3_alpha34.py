from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.34'
DEST = Path('build/visual-designer-manager')
ASSET_ROOT = Path('.github/release-assets/alpha34')

subprocess.run(['python3', '.github/scripts/build_v3_alpha33.py'], check=True)


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
    (' * Version: 3.0.0-alpha.33', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.33');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.33');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.34 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Retire Alpha.33's parallel mobile DOM/CSS renderer. The screenshot regression
# proved that flattening the editor DOM cannot be made safely equivalent to the
# frontend DOM: explicit-grid parent/child sizing still participates in the
# editor and causes collapsed/overlapping content.
#
# Alpha.34 instead uses the existing unsaved frontend preview endpoint as the
# canonical rendering surface for Laptop, Tablet and Mobile on converted V1
# pages. This means those tabs are literally Renderer + ResponsiveRenderer at
# the real breakpoint width, not a second approximation.
# ---------------------------------------------------------------------------
replace_once(
    'visual-designer-manager.php',
    """    wp_enqueue_style(
        'h18-clean-editor-v0182-v1-mobile-parity',
        H18_CLEAN_URL . 'assets/editor-v0182-v1-mobile-parity.css',
        ['h18-clean-editor-v0181'],
        H18_CLEAN_VERSION
    );
""",
    """    wp_enqueue_style(
        'h18-clean-editor-v0183-canonical-responsive-preview',
        H18_CLEAN_URL . 'assets/editor-v0183-canonical-responsive-preview.css',
        ['h18-clean-editor-v0181'],
        H18_CLEAN_VERSION
    );
""",
    'Alpha.34 canonical preview stylesheet enqueue'
)
replace_once(
    'visual-designer-manager.php',
    """    wp_enqueue_script(
        'h18-clean-editor-v0182-v1-mobile-parity',
        H18_CLEAN_URL . 'assets/editor-v0182-v1-mobile-parity.js',
        ['h18-clean-editor-v0181-color-picker', 'h18-clean-editor-v0121'],
        H18_CLEAN_VERSION,
        true
    );
""",
    """    wp_enqueue_script(
        'h18-clean-editor-v0183-canonical-responsive-preview',
        H18_CLEAN_URL . 'assets/editor-v0183-canonical-responsive-preview.js',
        ['h18-clean-editor-v0181-color-picker', 'h18-clean-editor-v0121'],
        H18_CLEAN_VERSION,
        true
    );
""",
    'Alpha.34 canonical preview script enqueue'
)

for name in ['editor-v0183-canonical-responsive-preview.js', 'editor-v0183-canonical-responsive-preview.css']:
    source = ASSET_ROOT / name
    if not source.is_file():
        raise SystemExit(f'Alpha.34 release asset missing: {source}')
    write('assets/' + name, source.read_text(encoding='utf-8'))

# The retired Alpha.33 projection must not remain in the installer and become a
# future accidental enqueue target.
for retired in ['assets/editor-v0182-v1-mobile-parity.js', 'assets/editor-v0182-v1-mobile-parity.css']:
    path = DEST / retired
    if path.exists():
        path.unlink()

# ---------------------------------------------------------------------------
# Tiny editor bridge: canonical iframe nodes can select their matching Designer
# node, and every normal render announces the current unsaved model. The iframe
# then refreshes via the already existing h18_clean_preview endpoint.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v018-core.js',
    """        renderInspector();
        updateHidden();
        updateHistoryUi();
        updateProductivityToolbar();
    }

    function install() {
""",
    """        renderInspector();
        updateHidden();
        updateHistoryUi();
        updateProductivityToolbar();
        try {
            document.dispatchEvent(new CustomEvent('h18-clean-model-changed', {
                detail: { selectedId: selectedId, modelJson: (document.getElementById('h18-clean-model-json') || {}).value || '{}' }
            }));
        } catch (ignoreModelChanged) {}
    }

    window.H18VDDesigner = Object.assign(window.H18VDDesigner || {}, {
        selectNode: function (id) {
            var node = nodeById(cleanId(id));
            if (!node) { return false; }
            selectedId = node.id;
            render();
            return true;
        },
        selectedId: function () { return selectedId || ''; }
    });

    function install() {
""",
    'Alpha.34 editor canonical selection bridge'
)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.33':
    raise SystemExit('Expected Alpha.33 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-09',
    'items': [
        'Fjerner Alpha.33 mobile flex-projektionen, som kunne kollapse explicit-grid sektioner og få tekst/knapper til at overlappe i Designer.',
        'V1-konverterede sider viser nu Laptop, Tablet og Mobil gennem den eksisterende usavede frontend-preview: samme Renderer, ResponsiveRenderer, Header/Footer, CSS og breakpoint som den virkelige side.',
        'Breakpointbredder er kanoniske: Laptop 1180 px, Tablet 980 px og Mobil 390 px; preview skaleres kun visuelt for at passe i Designer-kolonnen, mens iframe-layoutets CSS-pixelbredde forbliver uændret.',
        'Klik på et sideelement i den kanoniske responsive preview vælger samme node i Inspector. Inspector- og sideafstandsændringer opdaterer den usavede frontend-preview automatisk.',
        'Desktop forbliver den normale drag/drop Designer-master. Mobile X/Y/W/H markeres fortsat som ikke-separat layoutkilde, fordi Alpha.28 bruger Desktop som mobil master.',
        'Alpha.32 updater-kanal, Alpha.31 Footer-gap, Alpha.29 Event/Footer og den offentlige frontend-renderer ændres ikke.',
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts + regression locks.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
core = read('assets/editor-v018-core.js')
preview_js = read('assets/editor-v0183-canonical-responsive-preview.js')
preview_css = read('assets/editor-v0183-canonical-responsive-preview.css')
responsive = read('src/Frontend/ResponsiveRenderer.php')
updater = read('src/Update/GitHubUpdater.php')
module_design = read('src/Model/ModuleDesignModel.php')
collection = read('src/Frontend/CollectionPageRenderer.php')
history_text = read('release-history.json')

for token in [
    'Version: 3.0.0-alpha.34',
    "define('VDM_VERSION', '3.0.0-alpha.34');",
    "define('H18_CLEAN_VERSION', '3.0.0-alpha.34');",
    "'legacyMobileFlow' => metadata_exists('post', $postId, '_h18_clean_layout_v1'),",
    "'h18-clean-editor-v0183-canonical-responsive-preview'",
]:
    if token not in main:
        raise SystemExit(f'Alpha.34 main token missing: {token}')
for forbidden in ['h18-clean-editor-v0182-v1-mobile-parity']:
    if forbidden in main:
        raise SystemExit(f'Alpha.34 retired enqueue still present: {forbidden}')
for retired in ['assets/editor-v0182-v1-mobile-parity.js', 'assets/editor-v0182-v1-mobile-parity.css']:
    if (DEST / retired).exists():
        raise SystemExit(f'Alpha.34 retired asset still packaged: {retired}')

for token in [
    "document.dispatchEvent(new CustomEvent('h18-clean-model-changed'",
    'window.H18VDDesigner = Object.assign',
    'selectNode: function (id)',
    "selectedId: function () { return selectedId || ''; }",
]:
    if token not in core:
        raise SystemExit(f'Alpha.34 editor bridge token missing: {token}')

for token in [
    'var WIDTHS = { laptop: 1180, tablet: 980, mobile: 390 };',
    "hidden(form, 'action', 'h18_clean_preview');",
    "form.target = FRAME_NAME;",
    'window.H18CleanResponsive.sync()',
    "doc.getElementById('h18-clean-' + id)",
    "window.H18VDDesigner.selectNode(id)",
    "document.addEventListener('h18-clean-model-changed'",
]:
    if token not in preview_js:
        raise SystemExit(f'Alpha.34 canonical preview JS token missing: {token}')
for token in [
    'body.h18-vd-canonical-responsive-active .h18-vd-viewport-stage{display:none!important}',
    'body.h18-vd-canonical-responsive-active[data-h18-clean-device="mobile"]',
    'Mobil er en kanonisk frontend-projektion af Desktop-layoutet.',
]:
    if token not in preview_css:
        raise SystemExit(f'Alpha.34 canonical preview CSS token missing: {token}')

# Public frontend contracts are intentionally unchanged.
for token in [
    'public const LAPTOP_MAX = 1180;',
    'public const TABLET_MAX = 980;',
    'public const MOBILE_MAX = 782;',
    'private static function v1MobileFlowCss(',
    'private static function v1MobileVisualParityCss(',
    'private static function v1MobileEdgeSpacingCss(',
    'private static function v1NestedMobileEdgeParityCss(',
    "return $desktop;",
]:
    if token not in responsive:
        raise SystemExit(f'Alpha.34 retained frontend responsive token missing: {token}')

stable_manifest = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/v3-clean-refactor/v3-update.json'
if stable_manifest not in updater:
    raise SystemExit('Alpha.34 stable updater manifest URL missing')
for token in ["'footerGap' => 64", "'footerGap' => self::clamp("]:
    if token not in module_design:
        raise SystemExit(f'Alpha.34 retained ModuleDesign token missing: {token}')
for token in ['--h18-module-footer-gap:', 'padding:36px 0 var(--h18-module-footer-gap)']:
    if token not in collection:
        raise SystemExit(f'Alpha.34 retained Collection token missing: {token}')
if '3.0.0-alpha.34' not in history_text:
    raise SystemExit('Alpha.34 history token missing')

print('Alpha.34 canonical responsive frontend preview: PASS')
