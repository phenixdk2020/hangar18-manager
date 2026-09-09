from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.26'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha25.py'], check=True)

def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')

def write(rel: str, value: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(value, encoding='utf-8')

# ---------------------------------------------------------------------------
# Version cutover.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.25', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.25');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.25');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.26 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Header/Footer mobile paint ownership.
# Alpha.25 flattened nested template wrappers with display:contents. That fixed
# height/grid inheritance but also removed the painted background from those
# wrappers. Re-apply the effective template background to the outer surface.
# ---------------------------------------------------------------------------
rr_rel = 'src/Frontend/ResponsiveRenderer.php'
rr = read(rr_rel)
helper_anchor = """    /** @param array<string,mixed> $model @param array<string,mixed>|null $legacy */
    private static function v1HeaderMobileCss(array $model, ?array $legacy, string $scope): string
"""
helper = r'''    /** @param array<string,mixed> $model @param array<string,mixed>|null $legacy */
    private static function templateSurfaceBackground(array $model, ?array $legacy, string $fallback = '#30382a'): string
    {
        foreach ([$legacy, $model] as $candidate) {
            if (!is_array($candidate)) { continue; }
            foreach ((array) ($candidate['nodes'] ?? []) as $node) {
                if (!is_array($node) || !in_array((string) ($node['type'] ?? ''), ['section', 'container'], true)) { continue; }
                $props = is_array($node['props'] ?? null) ? $node['props'] : [];
                if (!empty($props['backgroundTransparent'])) { continue; }
                $color = sanitize_hex_color((string) ($props['background'] ?? ''));
                if ($color) { return $color; }
            }
        }
        return sanitize_hex_color($fallback) ?: '#30382a';
    }

'''
if rr.count(helper_anchor) != 1:
    raise SystemExit(f'Alpha.26 surface helper anchor mismatch: {rr.count(helper_anchor)}')
rr = rr.replace(helper_anchor, helper + helper_anchor, 1)

old = """    private static function v1HeaderMobileCss(array $model, ?array $legacy, string $scope): string
    {
        $css = $scope . '.h18-clean-front-surface{display:flex!important;flex-direction:row!important;align-items:center!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;padding:7px 11px!important;margin:0!important;gap:10px!important;overflow:visible!important;box-sizing:border-box!important;grid-template-columns:none!important;grid-template-rows:none!important;grid-auto-rows:auto!important;}'
"""
new = """    private static function v1HeaderMobileCss(array $model, ?array $legacy, string $scope): string
    {
        $surfaceBackground = self::templateSurfaceBackground($model, $legacy, '#30382a');
        $css = $scope . '.h18-clean-front-surface{display:flex!important;flex-direction:row!important;align-items:center!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;padding:7px 11px!important;margin:0!important;gap:10px!important;overflow:visible!important;box-sizing:border-box!important;grid-template-columns:none!important;grid-template-rows:none!important;grid-auto-rows:auto!important;background:' . $surfaceBackground . '!important;}'
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.26 Header surface anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

old = """    private static function v1FooterMobileCss(array $model, ?array $legacy, string $scope): string
    {
        $byId = [];
"""
new = """    private static function v1FooterMobileCss(array $model, ?array $legacy, string $scope): string
    {
        $surfaceBackground = self::templateSurfaceBackground($model, $legacy, '#30382a');
        $byId = [];
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.26 Footer surface setup anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

old = """            . $scope . '.h18-clean-front-surface{padding:32px 15px 20px!important;margin:0!important;}'
"""
new = """            . $scope . '.h18-clean-front-surface{padding:32px 15px 20px!important;margin:0!important;background:' . $surfaceBackground . '!important;}'
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.26 Footer background anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)

old = """            . $scope . '.h18-clean-front-menu-list{display:flex!important;flex-direction:column!important;align-items:flex-start!important;gap:8px!important;font-size:14px!important;font-weight:400!important;}';
"""
new = """            . $scope . '.h18-clean-front-menu-list{display:flex!important;flex-direction:column!important;align-items:flex-start!important;gap:8px!important;font-size:14px!important;font-weight:400!important;}'
            . $scope . '#h18-clean-text-footer-brand-v0147{font-size:18px!important;font-weight:700!important;line-height:1.25!important;}'
            . $scope . '#h18-clean-text-footer-description-v0147{font-size:14px!important;font-weight:400!important;line-height:1.45!important;}'
            . $scope . '#h18-clean-text-footer-shortcuts-heading-v0147,' . $scope . '#h18-clean-text-footer-association-heading-v0147{font-size:14px!important;font-weight:600!important;line-height:1.2!important;}'
            . $scope . '#h18-clean-text-footer-copyright-v0147{font-size:11px!important;font-weight:400!important;line-height:1.3!important;text-align:center!important;white-space:nowrap!important;}';
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.26 Footer typography anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)
write(rr_rel, rr)

# ---------------------------------------------------------------------------
# Footer Genveje must always mirror the canonical Website-menu.
# This is intentionally stronger than a stored node property: even an old or
# manually changed Footer model cannot drift to a separate specific menu.
# ---------------------------------------------------------------------------
renderer_rel = 'src/Frontend/Renderer.php'
renderer = read(renderer_rel)
old = """        if ($type === 'menu') {
            $menuSource = strtolower((string) ($props['menuSource'] ?? 'website')) === 'specific' ? 'specific' : 'website';
            $menuId = self::resolveLiveMenuId($props);
"""
new = """        if ($type === 'menu') {
            if ($id === 'menu-footer-shortcuts-v3') {
                $props['menuSource'] = 'website';
            }
            $menuSource = strtolower((string) ($props['menuSource'] ?? 'website')) === 'specific' ? 'specific' : 'website';
            $menuId = self::resolveLiveMenuId($props);
"""
if renderer.count(old) != 1:
    raise SystemExit(f'Alpha.26 Footer Website-menu renderer anchor mismatch: {renderer.count(old)}')
renderer = renderer.replace(old, new, 1)
write(renderer_rel, renderer)

# SharedPrimaryMenu already resolves the canonical Website-menu at runtime.
shared = read('src/Migration/SharedPrimaryMenu.php')
for token in [
    "private const FOOTER_MENU_NODE = 'menu-footer-shortcuts-v3';",
    "add_filter('wp_nav_menu_args', [self::class, 'filterFooterMenuArgs'], 20);",
    "get_option('vdm_website_menu_id', null)",
    "'menuSource' => 'website'",
]:
    if token not in shared:
        raise SystemExit(f'Alpha.26 SharedPrimaryMenu contract missing: {token}')

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.25':
    raise SystemExit('Expected Alpha.25 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-09',
    'items': [
        'Header Mobile Paint Parity: den yderste Header-surface overtager den effektive template-baggrund, så Alpha.25 display:contents ikke længere gør Headeren hvid.',
        'Footer Mobile Full-Width Paint: Footer-surface maler template-baggrunden helt til viewport-kanten, mens 32/15/20 px fortsat er indvendig content-padding.',
        'Footer Genveje er låst til den kanoniske Website-menu og viser dens aktuelle menupunkter i samme WordPress-menu-rækkefølge.',
        'Footer mobiltypografi gendanner V1-reference for brand 18 px, beskrivelse/overskrifter 14 px og copyright 11 px uden unødigt linjeskift.',
        'Alpha.25 natural-flow reset, Alpha.24 page spacing og Alpha.22 menu-controller bevares uændret.'
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic contract checks.
main = read('visual-designer-manager.php')
rr = read('src/Frontend/ResponsiveRenderer.php')
renderer = read('src/Frontend/Renderer.php')
history_text = read('release-history.json')
for token in ['Version: 3.0.0-alpha.26', "define('VDM_VERSION', '3.0.0-alpha.26');"]:
    if token not in main: raise SystemExit(f'Alpha.26 main token missing: {token}')
for token in [
    'private static function templateSurfaceBackground(',
    "background:' . $surfaceBackground . '!important",
    '#h18-clean-text-footer-brand-v0147{font-size:18px!important',
    '#h18-clean-text-footer-copyright-v0147{font-size:11px!important',
    'white-space:nowrap!important',
]:
    if token not in rr: raise SystemExit(f'Alpha.26 responsive token missing: {token}')
for token in [
    "if ($id === 'menu-footer-shortcuts-v3')",
    "$props['menuSource'] = 'website';",
    'h18-clean-front-menu-summary',
    'is-open',
]:
    if token not in renderer: raise SystemExit(f'Alpha.26 renderer token missing: {token}')
if '3.0.0-alpha.26' not in history_text: raise SystemExit('Alpha.26 history token missing')
print('PASS')
