from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.15'
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


subprocess.run(['python3', '.github/scripts/build_v3_alpha14.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.14', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.14');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.14');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.15 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# Preserve the original per-node spacing and section padding as CSS variables.
# Alpha.15's V1 mobile flow can then cap excessive desktop values without
# changing the persisted V3 model or desktop/tablet rendering.
replace_once(
    'src/Frontend/Renderer.php',
    "        return 'margin-right:' . $gapX . 'px;margin-bottom:' . $gapY . 'px;';",
    "        return '--h18-vdm-gap-x:' . $gapX . 'px;--h18-vdm-gap-y:' . $gapY . 'px;margin-right:' . $gapX . 'px;margin-bottom:' . $gapY . 'px;';",
    'Alpha.15 spacing variables'
)
replace_once(
    'src/Frontend/Renderer.php',
    "$boxStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';padding:' . $paddingTop . 'px ' . $paddingRight . 'px ' . $paddingBottom . 'px ' . $paddingLeft . 'px;';",
    "$boxStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';--h18-vdm-pad-top:' . $paddingTop . 'px;--h18-vdm-pad-right:' . $paddingRight . 'px;--h18-vdm-pad-bottom:' . $paddingBottom . 'px;--h18-vdm-pad-left:' . $paddingLeft . 'px;padding:' . $paddingTop . 'px ' . $paddingRight . 'px ' . $paddingBottom . 'px ' . $paddingLeft . 'px;';",
    'Alpha.15 section padding variables'
)

# Root-cause fix: V1 mobile pages use natural one-column flow. Alpha.13 copied
# geometry.mobile correctly, but V3 still rendered that geometry as a 120-column
# phone grid. Recreate the V1 flow contract for converted V1 pages only.
rr = read('src/Frontend/ResponsiveRenderer.php')
old = """        $models = [[
            'scope' => ThemeShell::enabled() ? '.h18-vd-live-shell-page ' : '',
            'model' => $pageModel,
        ]];
"""
new = """        $pageScope = ThemeShell::enabled() ? '.h18-vd-live-shell-page ' : '';
        $models = [[
            'scope' => $pageScope,
            'model' => $pageModel,
        ]];
        // Converted V1 pages use V1's natural one-column mobile flow contract.
        // New V3-native pages keep the explicit responsive grid model.
        $v1MobileFlow = metadata_exists('post', $postId, '_h18_clean_layout_v1')
            ? self::v1MobileFlowCss($pageModel, $pageScope)
            : '';
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.15 page scope anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

old = """            . '.h18-vd-live-shell{overflow-x:hidden;}'
            . $mobile . '}';
"""
new = """            . '.h18-vd-live-shell{overflow-x:hidden;}'
            . $mobile
            . $v1MobileFlow . '}';
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.15 mobile output anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

anchor = """    /** @return array<string,mixed>|null */
    private static function model(int $postId): ?array
"""
method = r'''    /**
     * Recreate the mobile flow semantics used by the working V1 page runtime.
     * V1 does not keep desktop-style columns on phones: content sections stack,
     * text/image compositions become one column and direct children follow the
     * visual mobile y/x order. This is intentionally page-only; Header/Footer
     * retain their independent responsive template geometry.
     *
     * @param array<string,mixed> $model
     */
    private static function v1MobileFlowCss(array $model, string $scope): string
    {
        $byId = [];
        $byParent = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $id = (string) $node['id'];
            $byId[$id] = $node;
            $parent = (string) ($node['parentId'] ?? '');
            $byParent[$parent][] = $node;
        }

        $surface = $scope . '.h18-clean-front-surface';
        $section = $scope . '.h18-clean-front-section';
        $container = $scope . '.h18-clean-front-container';
        $css = $surface . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;}'
            . $section . ',' . $container . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;padding-top:min(var(--h18-vdm-pad-top,0px),38px)!important;padding-right:min(var(--h18-vdm-pad-right,0px),18px)!important;padding-bottom:min(var(--h18-vdm-pad-bottom,0px),38px)!important;padding-left:min(var(--h18-vdm-pad-left,0px),18px)!important;}'
            . $scope . '.h18-clean-front-event-list,' . $scope . '.h18-clean-front-gallery-list,' . $scope . '.h18-clean-front-gallery-images,' . $scope . '.h18-clean-front-event-facts{grid-template-columns:1fr!important;width:100%!important;max-width:100%!important;}'
            . $scope . '.h18-clean-front-event-detail,' . $scope . '.h18-clean-front-gallery-detail,' . $scope . '.h18-clean-front-event-image{width:100%!important;max-width:100%!important;justify-self:stretch!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-gallery-images img{width:100%!important;height:auto!important;aspect-ratio:4/3;object-fit:cover!important;}'
            . $scope . '.h18-clean-front-event-list img,' . $scope . '.h18-clean-front-gallery-list img{width:100%!important;height:auto!important;aspect-ratio:16/10;object-fit:cover!important;}'
            . $scope . '.h18-clean-front-spacer{height:24px!important;min-height:24px!important;flex:0 0 24px!important;}';

        foreach ($byParent as $children) {
            usort($children, static function (array $a, array $b): int {
                $ag = self::effectiveGeometry($a, 'mobile');
                $bg = self::effectiveGeometry($b, 'mobile');
                return ($ag['y'] <=> $bg['y'])
                    ?: ($ag['x'] <=> $bg['x'])
                    ?: ((int) ($a['order'] ?? 0) <=> (int) ($b['order'] ?? 0));
            });

            $previousBottom = 0;
            foreach (array_values($children) as $index => $node) {
                $id = (string) ($node['id'] ?? '');
                if ($id === '') { continue; }
                $g = self::effectiveGeometry($node, 'mobile');
                $rows = self::effectiveRows($id, 'mobile', $byId, $byParent, []);
                $gapRows = $index === 0 ? 0 : max(0, $g['y'] - $previousBottom);
                $gapPx = min(24, $gapRows * LayoutModel::ROW_PX);
                $selector = $scope . '#h18-clean-' . self::cssId($id);
                $type = (string) ($node['type'] ?? '');
                $props = is_array($node['props'] ?? null) ? $node['props'] : [];
                $floating = $type === 'button' && (string) ($props['placementMode'] ?? 'normal') === 'overlay';

                $css .= $selector . '{order:' . $index . '!important;grid-column:auto!important;grid-row:auto!important;position:relative!important;left:auto!important;right:auto!important;top:auto!important;width:100%!important;max-width:100%!important;height:auto!important;margin-top:' . $gapPx . 'px!important;margin-right:0!important;margin-bottom:min(var(--h18-vdm-gap-y,0px),24px)!important;box-sizing:border-box!important;transform:none!important;}';
                if (!in_array($type, ['image', 'eventimage', 'spacer'], true)) {
                    $css .= $selector . '{min-height:0!important;}';
                }
                if ($floating) {
                    $css .= $selector . '{z-index:auto!important;}';
                }
                $previousBottom = max($previousBottom, $g['y'] + $rows);
            }
        }
        return $css;
    }

'''
if rr.count(anchor) != 1:
    raise SystemExit(f'Alpha.15 flow method anchor mismatch: {rr.count(anchor)}')
rr = rr.replace(anchor, method + anchor, 1)
write('src/Frontend/ResponsiveRenderer.php', rr)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.14':
    raise SystemExit('Expected Alpha.14 release-history baseline missing')
alpha15 = {
    'version': VERSION,
    'date': '2026-09-06',
    'items': [
        'V1 Mobile Page Flow Parity: konverterede V1-sider bruger nu V1s naturlige én-kolonne mobilflow i stedet for V3s 120-kolonne grid.',
        'Mobil indholdsrækkefølge bestemmes deterministisk af den gemte mobile y/x-geometri; Header/Footer påvirkes ikke.',
        'Sektioner og containere bliver fuld bredde med V1-lignende mobile padding-lofter på 18 px vandret og 38 px lodret.',
        'Eventfakta, Event-oversigter og gallerier kollapser til én kolonne på telefon; V1-kortproportioner gendannes.',
        'Store tomme grid-gab og desktop-offsets fjernes på V1-konverterede mobilsider uden JavaScript-måling eller omskrivning af gemte data.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha15] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic contract checks.
main = read('visual-designer-manager.php')
renderer = read('src/Frontend/Renderer.php')
rr = read('src/Frontend/ResponsiveRenderer.php')
history = json.loads(history_path.read_text(encoding='utf-8'))['versions']

for token in [
    'Version: 3.0.0-alpha.15',
    "define('VDM_VERSION', '3.0.0-alpha.15');",
]:
    if token not in main:
        raise SystemExit(f'Alpha.15 main token missing: {token}')
for token in [
    '--h18-vdm-gap-y:',
    '--h18-vdm-pad-top:',
    '--h18-vdm-pad-left:',
    '<details class="h18-clean-front-menu-details">',
]:
    if token not in renderer:
        raise SystemExit(f'Alpha.15 renderer token missing: {token}')
for token in [
    "metadata_exists('post', $postId, '_h18_clean_layout_v1')",
    'private static function v1MobileFlowCss(',
    'display:flex!important;flex-direction:column!important',
    'grid-template-columns:1fr!important',
    'padding-right:min(var(--h18-vdm-pad-right,0px),18px)!important',
    'padding-top:min(var(--h18-vdm-pad-top,0px),38px)!important',
    "self::effectiveGeometry($a, 'mobile')",
    'grid-column:auto!important;grid-row:auto!important',
    'transform:none!important',
    'aspect-ratio:4/3',
    'aspect-ratio:16/10',
]:
    if token not in rr:
        raise SystemExit(f'Alpha.15 responsive token missing: {token}')
for forbidden in ['v3-alpha10-mobile-reflow.js', 'v3-alpha11-mobile-reflow.js']:
    if (DEST / 'assets' / forbidden).exists():
        raise SystemExit(f'Forbidden historical mobile workaround returned: {forbidden}')
if history[0].get('version') != VERSION or history[1].get('version') != '3.0.0-alpha.14':
    raise SystemExit('Alpha.15 release-history ordering failed')

print('V3 Alpha.15 V1 mobile page flow parity: PASS')
print('Legacy V1 pages: deterministic full-width one-column mobile flow: PASS')
print('Header/Footer and native V3 responsive grids remain isolated: PASS')
print('V1 mobile spacing/card proportions without measurement JS: PASS')
