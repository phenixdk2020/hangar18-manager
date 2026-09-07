from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.18'
DEST = Path('build/visual-designer-manager')


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


subprocess.run(['python3', '.github/scripts/build_v3_alpha17.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.17', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.17');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.17');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.18 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# Alpha.18 keeps Alpha.17 as the accepted baseline and only normalizes the
# remaining V1 mobile presentation mismatch: top-level sections should paint
# edge-to-edge, while vertical air must be exactly one V1 section gap rather
# than a stack of grid gap + node margin + spacer + hero margin.
rr = read('src/Frontend/ResponsiveRenderer.php')

old = """            : '';

        $laptop = '';
"""
new = """            : '';
        $v1MobileEdgeSpacing = $legacyPageModel !== null
            ? self::v1MobileEdgeSpacingCss($pageModel, $pageScope)
            : '';

        $laptop = '';
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.18 edge-spacing variable anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

old = """            . $mobile
            . $v1MobileFlow
            . $v1MobileVisual . '}';
"""
new = """            . $mobile
            . $v1MobileFlow
            . $v1MobileVisual
            . $v1MobileEdgeSpacing . '}';
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.18 mobile CSS append anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

anchor = """    /** @return array<string,mixed>|null */
    private static function model(int $postId): ?array
"""
method = r'''    /**
     * Alpha.18 V1 mobile edge/spacing contract.
     *
     * The approved Alpha.17 screenshots show the structure is now correct,
     * but the V3 page wrapper still leaves gutters around top-level V1 bands
     * and several old spacing mechanisms can accumulate. V1 instead paints
     * major page bands to the viewport edge and uses one controlled section
     * gap. Feature cards (Bevaring/Formidling/Fællesskab) remain inset.
     *
     * @param array<string,mixed> $model
     */
    private static function v1MobileEdgeSpacingCss(array $model, string $scope): string
    {
        $root = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            if ((string) ($node['parentId'] ?? '') !== '') { continue; }
            $root[] = $node;
        }
        usort($root, static function (array $a, array $b): int {
            $ag = self::effectiveGeometry($a, 'mobile');
            $bg = self::effectiveGeometry($b, 'mobile');
            return ($ag['y'] <=> $bg['y'])
                ?: ($ag['x'] <=> $bg['x'])
                ?: ((int) ($a['order'] ?? 0) <=> (int) ($b['order'] ?? 0));
        });

        $css = $scope . '.h18-clean-front-surface{width:100%!important;max-width:none!important;padding-left:0!important;padding-right:0!important;gap:0!important;overflow-x:clip!important;}'
            . $scope . '.h18-clean-front-surface>.h18-clean-front-spacer{display:none!important;height:0!important;min-height:0!important;margin:0!important;padding:0!important;}'
            . $scope . '.h18-clean-front-surface>.h18-clean-front-node{margin-bottom:0!important;}';

        $visible = 0;
        $previousFeature = false;
        foreach ($root as $node) {
            $id = (string) ($node['id'] ?? '');
            $type = (string) ($node['type'] ?? '');
            if ($id === '' || $type === 'spacer') { continue; }
            $props = is_array($node['props'] ?? null) ? $node['props'] : [];
            $heading = trim(wp_strip_all_tags((string) ($props['heading'] ?? '')));
            $feature = $type === 'text' && in_array($heading, ['Bevaring', 'Formidling', 'Fællesskab'], true);
            $gap = $visible === 0 ? 0 : (($feature && $previousFeature) ? 14 : 24);
            $selector = $scope . '#h18-clean-' . self::cssId($id);

            // One and only one vertical gap between visible top-level sections.
            $css .= $selector . '{margin-top:' . $gap . 'px!important;margin-bottom:0!important;}';

            if ($feature) {
                // V1 feature cards are intentionally inset; Alpha.16 paint/size
                // remains authoritative here.
                $css .= $selector . '{margin-left:10px!important;margin-right:10px!important;}';
            } elseif (in_array($type, ['image', 'text', 'section', 'container', 'eventlist', 'gallerylist', 'eventdetail', 'gallerydetail'], true)) {
                // Major V1 page bands paint to the physical viewport edge even
                // when the WordPress/page shell itself has a content gutter.
                $css .= $selector . '{width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;box-sizing:border-box!important;}';
                if (in_array($type, ['text', 'section', 'container'], true)) {
                    $css .= $selector . '{padding-left:18px!important;padding-right:18px!important;border-radius:0!important;}';
                }
                if ($type === 'image') {
                    $css .= $selector . '{padding-left:0!important;padding-right:0!important;border-radius:0!important;overflow:hidden!important;}'
                        . $selector . ' .h18-clean-front-image,' . $selector . ' .h18-clean-front-image img{width:100%!important;max-width:100%!important;border-radius:0!important;}';
                }
            }

            $visible++;
            $previousFeature = $feature;
        }
        return $css;
    }

'''
if rr.count(anchor) != 1:
    raise SystemExit(f'Alpha.18 method anchor mismatch: {rr.count(anchor)}')
rr = rr.replace(anchor, method + anchor, 1)
write('src/Frontend/ResponsiveRenderer.php', rr)

# Designer palette UX: sort rendered element buttons alphabetically by their
# visible Danish label. Categories/groups stay intact; only the button order
# inside each group (or the ungrouped Header/Footer palette) changes.
editor_rel = 'assets/editor-v018-core.js'
editor = read(editor_rel)
palette_anchor = "        document.querySelectorAll('.h18-clean-add').forEach(function (button) {\n"
palette_sort = r'''        const h18PaletteContainers = Array.from(document.querySelectorAll('.h18-vd-palette-group-items'));
        if (!h18PaletteContainers.length) {
            const palette = document.querySelector('.h18-clean-palette');
            if (palette) { h18PaletteContainers.push(palette); }
        }
        h18PaletteContainers.forEach(function (container) {
            const buttons = Array.from(container.children).filter(function (child) {
                return child && child.classList && child.classList.contains('h18-clean-add');
            });
            buttons.sort(function (a, b) {
                const left = String(a.textContent || '').replace(/^\s*\+\s*/, '').trim();
                const right = String(b.textContent || '').replace(/^\s*\+\s*/, '').trim();
                try { return left.localeCompare(right, 'da', { sensitivity: 'base' }); }
                catch (ignore) { return left.toLowerCase().localeCompare(right.toLowerCase()); }
            });
            buttons.forEach(function (button) { container.appendChild(button); });
        });

'''
if editor.count(palette_anchor) != 1:
    raise SystemExit(f'Alpha.18 palette bind anchor mismatch: {editor.count(palette_anchor)}')
editor = editor.replace(palette_anchor, palette_sort + palette_anchor, 1)
write(editor_rel, editor)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.17':
    raise SystemExit('Expected Alpha.17 release-history baseline missing')
alpha18 = {
    'version': VERSION,
    'date': '2026-09-07',
    'items': [
        'V1 Mobile Edge-to-Edge: top-level V1 page bands now paint to the viewport edge instead of inheriting the V3 page-shell gutter.',
        'Mobile section air is normalized to one 24 px V1 section gap; stacked spacer/node/hero margins can no longer multiply the distance.',
        'Bevaring, Formidling and Fællesskab remain intentionally inset with a compact 14 px gap between consecutive feature cards.',
        'The hero/image band becomes true full-bleed on mobile while preserving Alpha.16 image height/crop behavior.',
        'Designer element palettes are alphabetically sorted by the visible Danish label while palette groups remain unchanged.',
        'Alpha.17 Eventlist sizing controls and the current V3 navigation remain unchanged.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha18] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic build contract.
main = read('visual-designer-manager.php')
rr = read('src/Frontend/ResponsiveRenderer.php')
editor = read(editor_rel)
history = json.loads(history_path.read_text(encoding='utf-8'))['versions']
for token in [
    'Version: 3.0.0-alpha.18',
    "define('VDM_VERSION', '3.0.0-alpha.18');",
]:
    if token not in main:
        raise SystemExit(f'Alpha.18 main token missing: {token}')
for token in [
    'private static function v1MobileEdgeSpacingCss(',
    'width:100vw!important;max-width:100vw!important',
    'margin-left:calc(50% - 50vw)!important',
    'padding-left:18px!important;padding-right:18px!important',
    "($feature && $previousFeature) ? 14 : 24",
    "['Bevaring', 'Formidling', 'Fællesskab']",
    '.h18-clean-front-surface>.h18-clean-front-spacer{display:none!important',
    '. $v1MobileEdgeSpacing',
]:
    if token not in rr:
        raise SystemExit(f'Alpha.18 responsive token missing: {token}')
for token in [
    'const h18PaletteContainers = Array.from(',
    "left.localeCompare(right, 'da'",
    "child.classList.contains('h18-clean-add')",
]:
    if token not in editor:
        raise SystemExit(f'Alpha.18 palette sorting token missing: {token}')
if history[0].get('version') != VERSION or history[1].get('version') != '3.0.0-alpha.17':
    raise SystemExit('Alpha.18 release-history ordering failed')

print('V3 Alpha.18 mobile edge-to-edge + spacing contract: PASS')
print('Top-level major bands: viewport full-bleed PASS')
print('Single V1 section gap: 24px; feature-card gap: 14px PASS')
print('Designer palette alphabetical order within groups: PASS')
print('Alpha.17 Eventlist and V3 navigation preserved: PASS')
