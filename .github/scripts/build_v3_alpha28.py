from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.28'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha27.py'], check=True)


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
    (' * Version: 3.0.0-alpha.27', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.27');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.27');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.28 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Canonical model rule: mobile geometry is derived directly from Desktop.
# Laptop/tablet keep their current responsive contract; phone layout no longer
# reads the historical V1 mobile geometry copied by Alpha.13.
# ---------------------------------------------------------------------------
replace_once(
    'src/Model/LayoutModel.php',
    """        $desktop = self::device(isset($raw['desktop']) && is_array($raw['desktop']) ? $raw['desktop'] : [], false);\n        $laptop = self::device(isset($raw['laptop']) && is_array($raw['laptop']) ? $raw['laptop'] : [], true);\n        $tablet = self::device(isset($raw['tablet']) && is_array($raw['tablet']) ? $raw['tablet'] : [], true);\n        $mobile = self::device(isset($raw['mobile']) && is_array($raw['mobile']) ? $raw['mobile'] : [], true);\n        return ['desktop' => $desktop, 'laptop' => $laptop, 'tablet' => $tablet, 'mobile' => $mobile];\n""",
    """        $desktop = self::device(isset($raw['desktop']) && is_array($raw['desktop']) ? $raw['desktop'] : [], false);\n        $laptop = self::device(isset($raw['laptop']) && is_array($raw['laptop']) ? $raw['laptop'] : [], true);\n        $tablet = self::device(isset($raw['tablet']) && is_array($raw['tablet']) ? $raw['tablet'] : [], true);\n        // Alpha.28: Desktop is the mobile master layout. Historical phone x/y/w/h\n        // values are intentionally ignored; the mobile renderer may still stack\n        // the shared Desktop structure, but it must not own a second layout.\n        $mobile = $desktop;\n        $mobile['inheritDesktop'] = true;\n        return ['desktop' => $desktop, 'laptop' => $laptop, 'tablet' => $tablet, 'mobile' => $mobile];\n""",
    'Alpha.28 LayoutModel mobile inheritance'
)

# ---------------------------------------------------------------------------
# Designer rule: every normalize/save pass synchronizes mobile geometry to the
# current Desktop geometry. Moving/resizing/reordering Desktop therefore updates
# the phone preview/model automatically without separate mobile coordinates.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v018-core.js',
    """            const added = nodes[nodes.length - 1];\n            if (PARENT_TYPES.includes(type) && (!item.props || !Object.prototype.hasOwnProperty.call(item.props, 'minHeightRows'))) {\n""",
    """            const added = nodes[nodes.length - 1];\n            // Alpha.28: Desktop is the master layout for Mobile. Keep one node\n            // tree and one placement source; phone-specific presentation is CSS.\n            added.geometry.mobile = Object.assign({}, added.geometry.desktop, { inheritDesktop: true });\n            if (PARENT_TYPES.includes(type) && (!item.props || !Object.prototype.hasOwnProperty.call(item.props, 'minHeightRows'))) {\n""",
    'Alpha.28 Designer normalize mobile inheritance'
)

replace_once(
    'assets/editor-v018-core.js',
    """                mobile: { x: 0, y: 0, w: 120, h: defaultH, inheritDesktop: true }\n""",
    """                mobile: Object.assign({}, desktop, { inheritDesktop: true })\n""",
    'Alpha.28 new node mobile inheritance'
)

# ---------------------------------------------------------------------------
# Runtime rule: Mobile resolves geometry directly from Desktop, not through the
# old Laptop -> Tablet -> Mobile chain. Mobile flow then stacks that shared
# Desktop structure in visual Desktop y/x order.
# ---------------------------------------------------------------------------
rr_rel = 'src/Frontend/ResponsiveRenderer.php'
rr = read(rr_rel)
old = """        $mobileRaw = is_array($geometry['mobile'] ?? null) ? $geometry['mobile'] : [];\n        // Responsive inheritance is cascading: Mobile inherits Tablet, Tablet\n        // inherits Laptop, and Laptop may inherit Desktop.\n        return !empty($mobileRaw['inheritDesktop']) ? $tablet : self::geometry($mobileRaw, $tablet);\n"""
new = """        // Alpha.28: Desktop is the canonical phone layout source. Mobile\n        // presentation can stack/resize through generated CSS, but placement and\n        // ordering never come from a second mobile geometry model.\n        return $desktop;\n"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.28 effectiveGeometry mobile anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

old = """            usort($children, static function (array $a, array $b): int {\n                $ag = self::effectiveGeometry($a, 'mobile');\n                $bg = self::effectiveGeometry($b, 'mobile');\n                return ($ag['y'] <=> $bg['y'])\n                    ?: ($ag['x'] <=> $bg['x'])\n                    ?: ((int) ($a['order'] ?? 0) <=> (int) ($b['order'] ?? 0));\n            });\n\n            $previousBottom = 0;\n            foreach (array_values($children) as $index => $node) {\n                $id = (string) ($node['id'] ?? '');\n                if ($id === '') { continue; }\n                $g = self::effectiveGeometry($node, 'mobile');\n                $rows = self::effectiveRows($id, 'mobile', $byId, $byParent, []);\n"""
new = """            usort($children, static function (array $a, array $b): int {\n                // Stack phone content in the same visual order as Desktop.\n                $ag = self::effectiveGeometry($a, 'desktop');\n                $bg = self::effectiveGeometry($b, 'desktop');\n                return ($ag['y'] <=> $bg['y'])\n                    ?: ($ag['x'] <=> $bg['x'])\n                    ?: ((int) ($a['order'] ?? 0) <=> (int) ($b['order'] ?? 0));\n            });\n\n            $previousBottom = 0;\n            foreach (array_values($children) as $index => $node) {\n                $id = (string) ($node['id'] ?? '');\n                if ($id === '') { continue; }\n                $g = self::effectiveGeometry($node, 'desktop');\n                $rows = self::effectiveRows($id, 'desktop', $byId, $byParent, []);\n"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.28 page mobile order anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

# Update the contract comment so future work does not reintroduce a second
# mobile layout source.
old = """     * Recreate the mobile flow semantics used by the working V1 page runtime.\n     * V1 does not keep desktop-style columns on phones: content sections stack,\n     * text/image compositions become one column and direct children follow the\n     * visual mobile y/x order. This is intentionally page-only; Header/Footer\n     * retain their independent responsive template geometry.\n"""
new = """     * Mobile is a responsive projection of the Desktop Designer layout.\n     * Desktop visual y/x order is canonical; phone presentation stacks that same\n     * node tree to one column without maintaining independent phone placement.\n     * Header/Footer may still change presentation (for example hamburger menu),\n     * but they use the same canonical nodes, paint and Desktop ordering source.\n"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.28 mobile flow comment anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)
write(rr_rel, rr)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.27':
    raise SystemExit('Expected Alpha.27 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-09',
    'items': [
        'Desktop Master Mobile Layout: Mobile bruger samme node-træ, placering og visuelle rækkefølge som Desktop-designeren i stedet for en separat mobilgeometri.',
        'LayoutModel ignorerer historiske geometry.mobile x/y/w/h og normaliserer Mobile direkte fra Desktop med inheritDesktop=true.',
        'Designeren synkroniserer Mobile-geometri ved hver normalize/save, så flytning og resize på Desktop automatisk følger med på telefon.',
        'Mobilens one-column flow sorterer efter Desktop y/x/order; responsive CSS må stacke og ændre størrelse, men må ikke ændre den kanoniske layout-rækkefølge.',
        'Laptop/Tablet-kontrakten, responsive sideafstande, hamburger-præsentation og andre eksplicit responsive præsentationsregler bevares.',
        'Alpha.27 fælles paint source og Alpha.26 Header/Footer/Website-menu-adfærd bevares.'
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contract checks.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
layout = read('src/Model/LayoutModel.php')
rr = read('src/Frontend/ResponsiveRenderer.php')
editor = read('assets/editor-v018-core.js')
history_text = read('release-history.json')

for token in ['Version: 3.0.0-alpha.28', "define('VDM_VERSION', '3.0.0-alpha.28');"]:
    if token not in main:
        raise SystemExit(f'Alpha.28 main token missing: {token}')
for token in [
    '$mobile = $desktop;',
    "$mobile['inheritDesktop'] = true;",
    'Desktop is the mobile master layout',
]:
    if token not in layout:
        raise SystemExit(f'Alpha.28 LayoutModel token missing: {token}')
for token in [
    'added.geometry.mobile = Object.assign({}, added.geometry.desktop, { inheritDesktop: true });',
    'mobile: Object.assign({}, desktop, { inheritDesktop: true })',
]:
    if token not in editor:
        raise SystemExit(f'Alpha.28 editor token missing: {token}')
for token in [
    'return $desktop;',
    "self::effectiveGeometry($a, 'desktop')",
    "self::effectiveRows($id, 'desktop', $byId, $byParent, [])",
    'Mobile is a responsive projection of the Desktop Designer layout.',
]:
    if token not in rr:
        raise SystemExit(f'Alpha.28 responsive token missing: {token}')
if "return !empty($mobileRaw['inheritDesktop']) ? $tablet : self::geometry($mobileRaw, $tablet);" in rr:
    raise SystemExit('Alpha.28 old mobile geometry cascade still present')
if '3.0.0-alpha.28' not in history_text:
    raise SystemExit('Alpha.28 history token missing')

# Retain the paint/menu contracts fixed by Alpha.27/26.
if 'self::v1PaintCss($pageModel, $legacyPageModel, $pageScope)' in rr:
    raise SystemExit('Alpha.27 mobile-only paint regression')
renderer = read('src/Frontend/Renderer.php')
if "if ($id === 'menu-footer-shortcuts-v3')" not in renderer or "$props['menuSource'] = 'website';" not in renderer:
    raise SystemExit('Alpha.26 Footer Website-menu contract missing')
if 'h18-clean-front-menu-summary' not in renderer or 'is-open' not in renderer:
    raise SystemExit('Alpha.22 menu controller regression')

print('PASS')
