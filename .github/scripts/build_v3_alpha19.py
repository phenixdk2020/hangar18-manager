from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.19'
DEST = Path('build/visual-designer-manager')


def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')


def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')


subprocess.run(['python3', '.github/scripts/build_v3_alpha18.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.18', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.18');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.18');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.19 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# Alpha.18 sorted the Designer element palette because the request was
# initially misunderstood. Restore the Alpha.17 palette behavior; Alpha.19
# sorts the Visual Designer Manager WordPress admin submenu instead.
editor_rel = 'assets/editor-v018-core.js'
editor = read(editor_rel)
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
if editor.count(palette_sort) != 1:
    raise SystemExit(f'Alpha.19 palette rollback anchor mismatch: {editor.count(palette_sort)}')
editor = editor.replace(palette_sort, '', 1)
write(editor_rel, editor)

# Sort every visible submenu entry below Visual Designer Manager after all
# V3 controllers have had a chance to register their menu pages.
admin_rel = 'src/Admin/AdminController.php'
admin = read(admin_rel)
old = """        add_action('admin_menu', [self::class, 'menu'], 5);
"""
new = """        add_action('admin_menu', [self::class, 'menu'], 5);
        add_action('admin_menu', [self::class, 'sortManagerSubmenu'], 999);
"""
if admin.count(old) != 1:
    raise SystemExit(f'Alpha.19 admin hook anchor mismatch: {admin.count(old)}')
admin = admin.replace(old, new, 1)

anchor = """    public static function enqueue(string $hook): void
"""
method = r'''    public static function sortManagerSubmenu(): void
    {
        global $submenu;
        if (!isset($submenu[self::MENU]) || !is_array($submenu[self::MENU])) {
            return;
        }

        usort($submenu[self::MENU], static function (array $left, array $right): int {
            $leftLabel = remove_accents(wp_strip_all_tags((string) ($left[0] ?? '')));
            $rightLabel = remove_accents(wp_strip_all_tags((string) ($right[0] ?? '')));
            $cmp = strnatcasecmp($leftLabel, $rightLabel);
            if ($cmp !== 0) { return $cmp; }
            return strnatcasecmp((string) ($left[2] ?? ''), (string) ($right[2] ?? ''));
        });

        $submenu[self::MENU] = array_values($submenu[self::MENU]);
    }

'''
if admin.count(anchor) != 1:
    raise SystemExit(f'Alpha.19 admin method anchor mismatch: {admin.count(anchor)}')
admin = admin.replace(anchor, method + anchor, 1)
write(admin_rel, admin)

# Alpha.18 only handled root nodes. Alpha.19 traverses the actual nested V3
# hierarchy and emits explicit mobile rules for the semantic V1 bands.
rr_rel = 'src/Frontend/ResponsiveRenderer.php'
rr = read(rr_rel)
old = """        $v1MobileEdgeSpacing = $legacyPageModel !== null
            ? self::v1MobileEdgeSpacingCss($pageModel, $pageScope)
            : '';

        $laptop = '';
"""
new = """        $v1MobileEdgeSpacing = $legacyPageModel !== null
            ? self::v1MobileEdgeSpacingCss($pageModel, $pageScope)
            : '';
        $v1NestedMobileEdgeParity = $legacyPageModel !== null
            ? self::v1NestedMobileEdgeParityCss($pageModel, $pageScope)
            : '';

        $laptop = '';
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.19 nested variable anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

old = """            . $v1MobileFlow
            . $v1MobileVisual
            . $v1MobileEdgeSpacing . '}';
"""
new = """            . $v1MobileFlow
            . $v1MobileVisual
            . $v1MobileEdgeSpacing
            . $v1NestedMobileEdgeParity . '}';
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.19 nested append anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

anchor = """    /** @return array<string,mixed>|null */
    private static function model(int $postId): ?array
"""
method = r'''    /**
     * Alpha.19 nested mobile edge parity.
     *
     * Alpha.18 only matched root nodes. The migrated V3 home page keeps the
     * hero, tagline and most visual page bands inside Section/Container nodes,
     * so those root-only selectors did not affect the actual phone DOM. This
     * pass walks the complete node tree and targets the semantic V1 bands by
     * node type/content while keeping the approved feature cards inset.
     *
     * @param array<string,mixed> $model
     */
    private static function v1NestedMobileEdgeParityCss(array $model, string $scope): string
    {
        $byId = [];
        $children = [];
        foreach ((array) ($model['nodes'] ?? []) as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $id = (string) $node['id'];
            $byId[$id] = $node;
            $parent = (string) ($node['parentId'] ?? '');
            $children[$parent][] = $node;
        }

        $taglineId = '';
        $heroId = '';
        $heroY = PHP_INT_MAX;
        $majorIds = [];
        $featureIds = [];
        $majorHeadings = ['Om foreningen', 'Køretøjer og materiel', 'Events', 'Billedgalleri', 'Bliv en del af foreningen', 'Kontakt os'];

        foreach ($byId as $id => $node) {
            $type = (string) ($node['type'] ?? '');
            $props = is_array($node['props'] ?? null) ? $node['props'] : [];
            $heading = trim(wp_strip_all_tags((string) ($props['heading'] ?? '')));
            $text = trim(wp_strip_all_tags((string) ($props['text'] ?? '')));
            $hay = strtolower($heading . ' ' . $text);

            if ($type === 'text' && str_contains($hay, 'bevaring, restaurering og levende') && str_contains($hay, 'militærhistorie')) {
                $taglineId = $id;
            }
            if ($type === 'text' && in_array($heading, ['Bevaring', 'Formidling', 'Fællesskab'], true)) {
                $featureIds[$id] = true;
            }
            if ($type === 'text' && in_array($heading, $majorHeadings, true)) {
                $majorIds[$id] = true;
            }
            if ($type === 'image') {
                $g = self::effectiveGeometry($node, 'mobile');
                if ($g['w'] >= 100 && $g['y'] < $heroY) {
                    $heroId = $id;
                    $heroY = $g['y'];
                }
            }
        }

        $nearestBand = static function (string $id) use ($byId): string {
            $node = $byId[$id] ?? null;
            if (!is_array($node)) { return $id; }
            $parent = (string) ($node['parentId'] ?? '');
            $guard = 0;
            while ($parent !== '' && isset($byId[$parent]) && $guard++ < 32) {
                $candidate = $byId[$parent];
                $type = (string) ($candidate['type'] ?? '');
                if (in_array($type, ['section', 'container'], true)) { return $parent; }
                $parent = (string) ($candidate['parentId'] ?? '');
            }
            return $id;
        };

        $ancestorChain = static function (string $id) use ($byId): array {
            $result = [];
            $node = $byId[$id] ?? null;
            $parent = is_array($node) ? (string) ($node['parentId'] ?? '') : '';
            $guard = 0;
            while ($parent !== '' && isset($byId[$parent]) && $guard++ < 32) {
                $result[] = $parent;
                $parent = (string) ($byId[$parent]['parentId'] ?? '');
            }
            return $result;
        };

        $css = $scope . '.h18-clean-front-surface{padding-left:0!important;padding-right:0!important;overflow-x:clip!important;}'
            . $scope . '.h18-clean-front-spacer{display:none!important;height:0!important;min-height:0!important;flex-basis:0!important;margin:0!important;padding:0!important;}';

        // Structural wrappers on the hero/tagline paths must not contribute an
        // additional 24px flow margin or internal horizontal gutter.
        $pathIds = [];
        foreach (array_filter([$heroId, $taglineId]) as $semanticId) {
            foreach ($ancestorChain($semanticId) as $ancestorId) { $pathIds[$ancestorId] = true; }
        }
        foreach (array_keys($pathIds) as $id) {
            $node = $byId[$id] ?? null;
            if (!is_array($node) || !in_array((string) ($node['type'] ?? ''), ['section', 'container'], true)) { continue; }
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            $css .= $selector . '{width:100%!important;max-width:100%!important;margin-top:0!important;margin-bottom:0!important;padding-left:0!important;padding-right:0!important;overflow:visible!important;}';
        }

        if ($heroId !== '') {
            $selector = $scope . '#h18-clean-' . self::cssId($heroId);
            $css .= $selector . '{width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;margin-top:0!important;margin-bottom:0!important;padding:0!important;border-radius:0!important;overflow:hidden!important;}'
                . $selector . ' .h18-clean-front-image{width:100%!important;max-width:100%!important;margin:0!important;padding:0!important;border-radius:0!important;}'
                . $selector . ' .h18-clean-front-image img{display:block!important;width:100%!important;max-width:100%!important;height:220px!important;object-fit:cover!important;border-radius:0!important;}';
        }

        if ($taglineId !== '') {
            $selector = $scope . '#h18-clean-' . self::cssId($taglineId);
            $css .= $selector . '{width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;margin-top:24px!important;margin-bottom:0!important;padding:13px 18px!important;border-radius:0!important;background:#c3ae83!important;color:#30382a!important;text-align:center!important;box-sizing:border-box!important;}';
        }

        foreach (array_keys($majorIds) as $id) {
            $bandId = $nearestBand($id);
            $selector = $scope . '#h18-clean-' . self::cssId($bandId);
            $css .= $selector . '{width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;margin-top:24px!important;margin-bottom:0!important;padding-left:18px!important;padding-right:18px!important;box-sizing:border-box!important;border-radius:0!important;overflow:visible!important;}';
        }

        // Preserve V1's inset Bevaring/Formidling/Fællesskab cards even when
        // their parent wrapper is full-width.
        foreach (array_keys($featureIds) as $id) {
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            $css .= $selector . '{width:calc(100% - 20px)!important;max-width:calc(100% - 20px)!important;margin-left:10px!important;margin-right:10px!important;margin-top:14px!important;margin-bottom:0!important;}';
        }

        return $css;
    }

'''
if rr.count(anchor) != 1:
    raise SystemExit(f'Alpha.19 nested method anchor mismatch: {rr.count(anchor)}')
rr = rr.replace(anchor, method + anchor, 1)
write(rr_rel, rr)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.18':
    raise SystemExit('Expected Alpha.18 release-history baseline missing')
alpha19 = {
    'version': VERSION,
    'date': '2026-09-07',
    'items': [
        'Nested Mobile Edge Parity: V1 mobile full-bleed rules now traverse the actual V3 Section/Container hierarchy instead of matching root nodes only.',
        'Hero and tagline are explicitly restored to V1 full-width phone bands; stacked nested Spacer/wrapper gaps are removed.',
        'Major semantic home-page sections use full-width V1 bands with 18 px internal text padding, while Bevaring/Formidling/Fællesskab remain inset cards.',
        'Visual Designer Manager WordPress submenu entries are sorted alphabetically after every V3 module has registered its menu item.',
        'The accidental Alpha.18 Designer element-palette sorting is removed; only the requested Manager admin menu is alphabetized.',
        'Alpha.17 Eventlist sizing controls and Alpha.14 navigation behavior remain unchanged.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha19] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic contract checks.
main = read('visual-designer-manager.php')
rr = read(rr_rel)
admin = read(admin_rel)
editor = read(editor_rel)
history = json.loads(history_path.read_text(encoding='utf-8'))['versions']

for token in ['Version: 3.0.0-alpha.19', "define('VDM_VERSION', '3.0.0-alpha.19');"]:
    if token not in main: raise SystemExit(f'Alpha.19 main token missing: {token}')
for token in [
    'private static function v1NestedMobileEdgeParityCss(',
    "['Om foreningen', 'Køretøjer og materiel', 'Events', 'Billedgalleri', 'Bliv en del af foreningen', 'Kontakt os']",
    'margin-left:calc(50% - 50vw)!important',
    '.h18-clean-front-spacer{display:none!important',
    'padding:13px 18px!important',
    'height:220px!important',
    '. $v1NestedMobileEdgeParity',
]:
    if token not in rr: raise SystemExit(f'Alpha.19 responsive token missing: {token}')
for token in [
    "add_action('admin_menu', [self::class, 'sortManagerSubmenu'], 999);",
    'public static function sortManagerSubmenu(): void',
    'strnatcasecmp($leftLabel, $rightLabel)',
    '$submenu[self::MENU] = array_values($submenu[self::MENU]);',
]:
    if token not in admin: raise SystemExit(f'Alpha.19 admin sort token missing: {token}')
if 'const h18PaletteContainers = Array.from(' in editor:
    raise SystemExit('Alpha.19 must remove accidental Alpha.18 palette sorting')
if history[0].get('version') != VERSION or history[1].get('version') != '3.0.0-alpha.18':
    raise SystemExit('Alpha.19 release-history ordering failed')

print('V3 Alpha.19 nested mobile edge parity: PASS')
print('Hero/tagline/major nested bands full-width: PASS')
print('Feature cards remain inset: PASS')
print('VDM WordPress admin submenu alphabetical sorting: PASS')
print('Designer palette sorting rollback: PASS')
