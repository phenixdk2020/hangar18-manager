from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.37'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha36.py'], check=True)


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
    (' * Version: 3.0.0-alpha.36', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.36');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.36');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.37 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Designer responsive preview is PAGE-ONLY.
#
# Laptop/Tablet/Mobile use the real frontend renderer, but the Designer canvas
# should not also show global Header/Footer; a dedicated "Vis med Header + Footer"
# action already exists for that purpose. We keep the same canonical frontend
# DOM/CSS and hide only the shell parts inside the embedded Designer iframe.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0183-canonical-responsive-preview.js',
    """            style.textContent = '' +
                '#wpadminbar{display:none!important}html{margin-top:0!important}' +
                '[data-h18-vd-selectable=\"1\"]{cursor:pointer!important}' +
                '[data-h18-vd-selected=\"1\"]{outline:3px solid #2271b1!important;outline-offset:2px!important;position:relative!important;z-index:2147483000!important}';
""",
    """            style.textContent = '' +
                '#wpadminbar{display:none!important}html{margin-top:0!important}' +
                '.h18-vd-live-shell-header,.h18-vd-live-shell-footer{display:none!important}' +
                '.h18-vd-live-shell-page{padding-top:0!important;margin-bottom:0!important}' +
                '[data-h18-vd-selectable=\"1\"]{cursor:pointer!important}' +
                '[data-h18-vd-selected=\"1\"]{outline:3px solid #2271b1!important;outline-offset:2px!important;position:relative!important;z-index:2147483000!important}';
""",
    'Alpha.37 Designer page-only responsive shell'
)

replace_once(
    'assets/editor-v0183-canonical-responsive-preview.js',
    "status.textContent = label + ' · ' + width + ' px · frontend-renderer · ' + Math.round(scale * 100) + '% visning';",
    "status.textContent = label + ' · ' + width + ' px · frontend-renderer · side uden Header/Footer · ' + Math.round(scale * 100) + '% visning';",
    'Alpha.37 responsive status shell label'
)

# ---------------------------------------------------------------------------
# Laptop/Tablet converted V1 button parity.
#
# Alpha.36 changed vertical layout to content-sized rows, but retained the
# Desktop grid-column span as the physical button width. At 850/1100 px this
# could shrink CTA buttons into narrow vertical pills. Buttons on intermediate
# breakpoints therefore use content width with a sane minimum while preserving
# their grid-cell anchor/centering. Mobile keeps its already-approved contract.
# ---------------------------------------------------------------------------
replace_once(
    'src/Frontend/ResponsiveRenderer.php',
    """                if ($type === 'image') {
                    $css .= $selector . ' .h18-clean-front-image{height:auto!important;min-height:0!important;overflow:hidden!important;}'
                        . $selector . ' .h18-clean-front-image img{display:block!important;width:100%!important;height:auto!important;max-width:100%!important;max-height:none!important;object-fit:contain!important;}';
                }
                if (in_array($type, ['section', 'container'], true)) {
""",
    """                if ($type === 'image') {
                    $css .= $selector . ' .h18-clean-front-image{height:auto!important;min-height:0!important;overflow:hidden!important;}'
                        . $selector . ' .h18-clean-front-image img{display:block!important;width:100%!important;height:auto!important;max-width:100%!important;max-height:none!important;object-fit:contain!important;}';
                }
                if ($type === 'button') {
                    $css .= $selector . '{width:max-content!important;min-width:120px!important;max-width:min(280px,calc(100vw - 32px))!important;justify-self:center!important;align-self:start!important;}'
                        . $selector . ' .h18-clean-front-button-link{width:auto!important;height:auto!important;min-width:120px!important;min-height:44px!important;padding:10px 18px!important;white-space:normal!important;line-height:1.2!important;}';
                }
                if (in_array($type, ['section', 'container'], true)) {
""",
    'Alpha.37 Laptop/Tablet button parity'
)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.36':
    raise SystemExit('Expected Alpha.36 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-13',
    'items': [
        'Designerens indlejrede Laptop/Tablet/Mobil frontend-paritet viser nu kun selve siden; global Header og Footer skjules i Designer-previewet, fordi Vis med Header + Footer allerede er den eksplicitte samlede preview-funktion.',
        'Den responsive Designer-status angiver tydeligt side uden Header/Footer.',
        'Laptop/Tablet CTA-knapper bruger indholdsbaseret bredde med minimum 120 px og minimum 44 px højde, så de ikke længere kollapser til smalle lodrette piller ved 1100/850 px.',
        'Mobilknapper og mobilflow ændres ikke.',
        'Forhåndsvis fortsætter med at følge den valgte Desktop/Laptop/Tablet/Mobil-opløsning fra Alpha.36.',
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts + regression locks.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
preview_js = read('assets/editor-v0183-canonical-responsive-preview.js')
responsive = read('src/Frontend/ResponsiveRenderer.php')
history_text = read('release-history.json')

for token in [
    'Version: 3.0.0-alpha.37',
    "define('VDM_VERSION', '3.0.0-alpha.37');",
    "define('H18_CLEAN_VERSION', '3.0.0-alpha.37');",
]:
    if token not in main:
        raise SystemExit(f'Alpha.37 version token missing: {token}')

for token in [
    '.h18-vd-live-shell-header,.h18-vd-live-shell-footer{display:none!important}',
    '.h18-vd-live-shell-page{padding-top:0!important;margin-bottom:0!important}',
    'side uden Header/Footer',
    'var WIDTHS = { laptop: 1100, tablet: 850, mobile: 390 };',
]:
    if token not in preview_js:
        raise SystemExit(f'Alpha.37 preview token missing: {token}')

for token in [
    'width:max-content!important;min-width:120px!important;max-width:min(280px,calc(100vw - 32px))!important;justify-self:center!important',
    'min-width:120px!important;min-height:44px!important;padding:10px 18px!important',
    'public const LAPTOP_MAX = 1180;',
    'public const TABLET_MAX = 980;',
    'public const MOBILE_MAX = 782;',
]:
    if token not in responsive:
        raise SystemExit(f'Alpha.37 responsive token missing: {token}')

# Selected-device preview from Alpha.36 must remain intact.
editor = read('src/Admin/EditorController.php')
editor_js = read('assets/editor-v0114.js')
for token in [
    "$previewWidths = ['desktop' => 1920, 'laptop' => 1100, 'tablet' => 850, 'mobile' => 390];",
    'echo self::devicePreviewDocument($previewUrl, $previewDevice, (int) $previewWidths[$previewDevice]);',
]:
    if token not in editor:
        raise SystemExit(f'Alpha.37 selected-device preview token missing: {token}')
for token in [
    "hidden(form, 'preview_device', previewDevice);",
]:
    if token not in editor_js:
        raise SystemExit(f'Alpha.37 preview JS token missing: {token}')

if '3.0.0-alpha.37' not in history_text:
    raise SystemExit('Alpha.37 history token missing')

print('Alpha.37 Designer shell/button parity: PASS')
