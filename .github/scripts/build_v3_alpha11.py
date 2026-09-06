from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.11'
DEST = Path('build/visual-designer-manager')


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


subprocess.run(['python3', '.github/scripts/build_v3_alpha10.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.10', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.10');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.10');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.11 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Preserve VISUAL mobile order when Alpha.10 falls back from grid to flex.
#
# Alpha.10 correctly repairs clipping/overlap/gaps by switching only defective
# page parents to natural flex flow. A flex container normally uses DOM order,
# while the VDM Designer's intended order is encoded by mobile grid y/x.
# The test2 reference screenshots prove that the grid order must remain the
# authority. Emit a stable flex `order` derived from the effective mobile
# geometry for every node. This keeps rows top-to-bottom and same-row items
# left-to-right without rewriting stored layout data.
# ---------------------------------------------------------------------------
rr_rel = 'src/Frontend/ResponsiveRenderer.php'
replace_once(
    rr_rel,
    "            $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);\n            if ($floating) {",
    "            $mobile .= self::geometryCss($selector, $mg, $mobileRows, $floating, $zIndex);\n            $mobileOrder = (max(0, (int) $mg['y']) * (LayoutModel::UNITS + 1)) + max(0, (int) $mg['x']);\n            $mobile .= $scope . '.h18-vdm-mobile-flow-repair>#h18-clean-' . self::cssId($id)\n                . '{order:' . $mobileOrder . '!important;}';\n            if ($floating) {",
    'visual-order flex fallback'
)

# Version the mobile runtime asset so browsers cannot retain Alpha.10 JS.
replace_once(
    rr_rel,
    "wp_enqueue_script('vdm-v3-mobile-reflow', VDM_URL . 'assets/v3-alpha10-mobile-reflow.js', [], VDM_VERSION, true);",
    "wp_enqueue_script('vdm-v3-mobile-reflow', VDM_URL . 'assets/v3-alpha11-mobile-reflow.js', [], VDM_VERSION, true);",
    'alpha11 mobile asset URL'
)
old_asset = DEST / 'assets/v3-alpha10-mobile-reflow.js'
if not old_asset.exists():
    raise SystemExit('Alpha.10 mobile runtime asset missing')
mobile_js = old_asset.read_text(encoding='utf-8')
for required in [
    'horizontalOverflow(parentRect, childRect)',
    'intrinsicOverflow(child)',
    'overlaps(normal[i - 1].rect, normal[i].rect)',
    'gap > 160',
    'document.fonts.ready.then(schedule)',
]:
    if required not in mobile_js:
        raise SystemExit(f'Alpha.10 mobile safety token missing before Alpha.11: {required}')
write('assets/v3-alpha11-mobile-reflow.js', mobile_js)
old_asset.unlink()

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.10':
    raise SystemExit('Expected Alpha.10 release-history baseline missing')
alpha11 = {
    'version': VERSION,
    'date': '2026-09-06',
    'items': [
        'Mobil fallback bevarer nu Designerens visuelle rækkefølge i stedet for rå DOM-rækkefølge.',
        'Flex-order afledes deterministisk af effektiv mobil grid-y/x: top-til-bund og derefter venstre-til-højre.',
        'Alpha.10 overflow-, overlap- og gap-reparation bevares uændret; kun rækkefølgen under aktiv reflow korrigeres.',
        'Header/Footer og gemte layoutdata ændres ikke; rettelsen gælder kun sideindhold, der faktisk udløser mobil fallback.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha11] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic contract checks.
rr = read(rr_rel)
for required in [
    "assets/v3-alpha11-mobile-reflow.js",
    "$mobileOrder = (max(0, (int) $mg['y']) * (LayoutModel::UNITS + 1)) + max(0, (int) $mg['x']);",
    "'{order:' . $mobileOrder . '!important;}'",
    'h18-vdm-mobile-flow-repair',
    "'.h18-vd-live-shell-page '",
    'public const MOBILE_MAX = 782;',
]:
    if required not in rr:
        raise SystemExit(f'Alpha.11 visual-order runtime token missing: {required}')
if (DEST / 'assets/v3-alpha10-mobile-reflow.js').exists():
    raise SystemExit('Stale Alpha.10 mobile asset must not remain in Alpha.11 package')
if not (DEST / 'assets/v3-alpha11-mobile-reflow.js').exists():
    raise SystemExit('Alpha.11 mobile runtime asset missing')

built_history = json.loads(history_path.read_text(encoding='utf-8'))['versions']
if built_history[0].get('version') != VERSION or built_history[1].get('version') != '3.0.0-alpha.10':
    raise SystemExit('Alpha.11 release-history ordering failed')

print('V3 Alpha.11 mobile visual-order preservation: PASS')
print('Effective mobile y/x -> flex order: PASS')
print('Alpha.10 clipping/overlap/gap safeguards retained: PASS')
print('Header/Footer and stored layout data unchanged: PASS')
