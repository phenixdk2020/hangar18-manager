from pathlib import Path
import base64
import gzip
import json
import subprocess
import tempfile

VERSION = '3.0.0-alpha.36'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha35.py'], check=True)

PATCH_B64 = r"""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"""
patch_bytes = gzip.decompress(base64.b64decode(PATCH_B64.encode('ascii')))
with tempfile.NamedTemporaryFile(prefix='alpha36-', suffix='.patch', delete=False) as handle:
    handle.write(patch_bytes)
    patch_path = handle.name
subprocess.run(['patch', '--batch', '--forward', '-p1', '-d', str(DEST), '-i', patch_path], check=True)
Path(patch_path).unlink(missing_ok=True)


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')

# Deterministic Alpha.36 contracts + regression locks.
main = read('visual-designer-manager.php')
viewport_js = read('assets/editor-v0144-viewport.js')
viewport_css = read('assets/editor-v0121.css')
preview_click = read('assets/editor-v0114.js')
canonical_preview = read('assets/editor-v0183-canonical-responsive-preview.js')
controller = read('src/Admin/EditorController.php')
responsive = read('src/Frontend/ResponsiveRenderer.php')
renderer = read('src/Frontend/Renderer.php')
updater = read('src/Update/GitHubUpdater.php')
module_design = read('src/Model/ModuleDesignModel.php')
collection = read('src/Frontend/CollectionPageRenderer.php')
history_text = read('release-history.json')

for token in [
    'Version: 3.0.0-alpha.36',
    "define('VDM_VERSION', '3.0.0-alpha.36');",
    "define('H18_CLEAN_VERSION', '3.0.0-alpha.36');",
]:
    if token not in main:
        raise SystemExit(f'Alpha.36 main version token missing: {token}')

if 'var WIDTHS = { desktop: 1920, laptop: 1100, tablet: 850, mobile: 390 };' not in viewport_js:
    raise SystemExit('Alpha.36 viewport toolbar width contract missing')
for token in ['max-width:1100px', 'max-width:850px']:
    if token not in viewport_css:
        raise SystemExit(f'Alpha.36 viewport CSS width missing: {token}')
if 'var WIDTHS = { laptop: 1100, tablet: 850, mobile: 390 };' not in canonical_preview:
    raise SystemExit('Alpha.36 canonical responsive preview width contract missing')

for token in ["hidden(form, 'preview_device', previewDevice);", 'data-h18-clean-device']:
    if token not in preview_click:
        raise SystemExit(f'Alpha.36 preview-device post contract missing: {token}')
for token in [
    'private static function devicePreviewDocument(',
    "'desktop' => 1920, 'laptop' => 1100, 'tablet' => 850, 'mobile' => 390",
    "$_POST['preview_device']",
    'echo self::devicePreviewDocument(',
]:
    if token not in controller:
        raise SystemExit(f'Alpha.36 exact-device preview shell missing: {token}')

for token in [
    '$v1LaptopFluid =', '$v1TabletFluid =', '$v1TabletHeader =',
    'private static function v1IntermediateFluidGridCss(',
    'grid-auto-rows:auto!important', 'object-fit:contain!important',
    "$device === 'tablet' ? '24px' : '32px'",
    '.h18-clean-front-menu[data-mobile-mode="hamburger"] .h18-clean-front-menu-summary{display:grid!important',
]:
    if token not in responsive:
        raise SystemExit(f'Alpha.36 responsive fluid contract missing: {token}')

if renderer.count('window.matchMedia("(max-width:980px)").matches') < 2:
    raise SystemExit('Alpha.36 tablet hamburger matchMedia contract missing')

for token in [
    'public const LAPTOP_MAX = 1180;', 'public const TABLET_MAX = 980;', 'public const MOBILE_MAX = 782;',
    'private static function v1MobileFlowCss(', 'private static function v1MobileVisualParityCss(', "return $desktop;",
]:
    if token not in responsive:
        raise SystemExit(f'Alpha.36 public responsive breakpoint contract missing: {token}')

stable_manifest = 'https://raw.githubusercontent.com/phenixdk2020/hangar18-manager/v3-clean-refactor/v3-update.json'
if stable_manifest not in updater:
    raise SystemExit('Alpha.36 stable updater manifest URL missing')
for token in ["'footerGap' => 64", "'footerGap' => self::clamp("]:
    if token not in module_design:
        raise SystemExit(f'Alpha.36 retained ModuleDesign token missing: {token}')
for token in ['--h18-module-footer-gap:', 'padding:36px 0 var(--h18-module-footer-gap)']:
    if token not in collection:
        raise SystemExit(f'Alpha.36 retained Collection token missing: {token}')
if '3.0.0-alpha.36' not in history_text:
    raise SystemExit('Alpha.36 release history token missing')

print('Alpha.36 exact-device preview + Laptop/Tablet fluid parity: PASS')
