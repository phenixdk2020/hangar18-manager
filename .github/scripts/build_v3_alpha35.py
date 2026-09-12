from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.35'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha34.py'], check=True)


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
    (' * Version: 3.0.0-alpha.34', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.34');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.34');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.35 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Responsive Designer parity.
#
# Alpha.34 correctly moved Laptop/Tablet/Mobile to the real frontend renderer,
# but it rendered Laptop and Tablet exactly at their max-width breakpoint edges
# (1180 / 980). At those exact widths neighbouring max-width rules can meet at
# the boundary and the preview is a poor representative of a normal device in
# that range. Alpha.35 therefore keeps the same canonical frontend renderer but
# renders inside the interval: 1100 Laptop, 850 Tablet. Mobile remains 390 as
# the accepted regression reference. Public frontend breakpoints are unchanged.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0183-canonical-responsive-preview.js',
    'var WIDTHS = { laptop: 1180, tablet: 980, mobile: 390 };',
    'var WIDTHS = { laptop: 1100, tablet: 850, mobile: 390 };',
    'Alpha.35 representative responsive preview widths'
)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.34':
    raise SystemExit('Expected Alpha.34 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-12',
    'items': [
        'Laptop-preview bruger nu 1100 px i stedet for præcis 1180 px breakpoint-kanten, så visningen repræsenterer den normale Laptop-tilstand.',
        'Tablet-preview bruger nu 850 px i stedet for præcis 980 px breakpoint-kanten, så visningen repræsenterer den normale Tablet-tilstand.',
        'Mobil-preview forbliver 390 px som godkendt regression-reference.',
        'Laptop, Tablet og Mobil bruger fortsat Alpha.34s kanoniske usavede frontend-preview med samme Renderer, ResponsiveRenderer, Header/Footer og CSS som den offentlige side.',
        'De offentlige frontend-breakpoints ændres ikke: Laptop max 1180 px, Tablet max 980 px og Mobil max 782 px.',
        'Alpha.31 modulernes Afstand til Footer, Alpha.32 updater-kanalen og øvrige frontend-kontrakter bevares.',
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts + regression locks.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
preview_js = read('assets/editor-v0183-canonical-responsive-preview.js')
responsive = read('src/Frontend/ResponsiveRenderer.php')
updater = read('src/Update/GitHubUpdater.php')
module_design = read('src/Model/ModuleDesignModel.php')
collection = read('src/Frontend/CollectionPageRenderer.php')
history_text = read('release-history.json')

for token in [
    'Version: 3.0.0-alpha.35',
    "define('VDM_VERSION', '3.0.0-alpha.35');",
    "define('H18_CLEAN_VERSION', '3.0.0-alpha.35');",
]:
    if token not in main:
        raise SystemExit(f'Alpha.35 main token missing: {token}')

if 'var WIDTHS = { laptop: 1100, tablet: 850, mobile: 390 };' not in preview_js:
    raise SystemExit('Alpha.35 representative widths missing')
if 'var WIDTHS = { laptop: 1180, tablet: 980, mobile: 390 };' in preview_js:
    raise SystemExit('Alpha.35 old breakpoint-edge preview widths still present')

# Canonical Alpha.34 frontend preview behaviour remains intact.
for token in [
    "hidden(form, 'action', 'h18_clean_preview');",
    'form.target = FRAME_NAME;',
    'window.H18CleanResponsive.sync()',
    "doc.getElementById('h18-clean-' + id)",
    'window.H18VDDesigner.selectNode(id)',
    "document.addEventListener('h18-clean-model-changed'",
]:
    if token not in preview_js:
        raise SystemExit(f'Alpha.35 retained preview token missing: {token}')

# Public frontend breakpoint contract MUST NOT move with preview sample widths.
for token in [
    'public const LAPTOP_MAX = 1180;',
    'public const TABLET_MAX = 980;',
    'public const MOBILE_MAX = 782;',
    'private static function v1MobileFlowCss(',
    'private static function v1MobileVisualParityCss(',
    "return $desktop;",
]:
    if token not in responsive:
        raise SystemExit(f'Alpha.35 public responsive contract missing: {token}')

stable_manifest = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/v3-clean-refactor/v3-update.json'
if stable_manifest not in updater:
    raise SystemExit('Alpha.35 stable updater manifest URL missing')
for token in ["'footerGap' => 64", "'footerGap' => self::clamp("]:
    if token not in module_design:
        raise SystemExit(f'Alpha.35 retained ModuleDesign token missing: {token}')
for token in ['--h18-module-footer-gap:', 'padding:36px 0 var(--h18-module-footer-gap)']:
    if token not in collection:
        raise SystemExit(f'Alpha.35 retained Collection token missing: {token}')
if '3.0.0-alpha.35' not in history_text:
    raise SystemExit('Alpha.35 history token missing')

print('Alpha.35 Laptop/Tablet representative frontend preview: PASS')
