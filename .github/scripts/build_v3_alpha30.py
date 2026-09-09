from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.30'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha29.py'], check=True)


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
    (' * Version: 3.0.0-alpha.29', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.29');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.29');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.30 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Footer-only visual parity pass.
#
# Alpha.29 fixed semantic mobile grouping, but its intentionally generous group
# margins made the V3 footer taller and looser than the approved V1 reference.
# Keep the canonical node order and live Website-menu contract, while tightening
# only Footer mobile rhythm. Header and page flow are deliberately untouched.
# ---------------------------------------------------------------------------
rr_rel = 'src/Frontend/ResponsiveRenderer.php'
rr = read(rr_rel)
old = """        $footerStack = [
            'text-footer-brand-v0147' => [10, 0],
            'text-footer-description-v0147' => [20, 12],
            'text-footer-shortcuts-heading-v0147' => [30, 24],
            'menu-footer-shortcuts-v3' => [40, 8],
            'text-footer-association-heading-v0147' => [50, 24],
            'button-footer-join-v0147' => [60, 12],
            'button-footer-contact-v0147' => [70, 12],
            'container-footer-divider-v0147' => [80, 24],
            'text-footer-copyright-v0147' => [90, 16],
        ];
        foreach ($footerStack as $footerId => $stack) {
            if (!isset($byId[$footerId])) { continue; }
            $css .= $scope . '#h18-clean-' . self::cssId($footerId)
                . '{order:' . $stack[0] . '!important;margin-top:' . $stack[1] . 'px!important;}';
        }
        return $css;
"""
new = """        $footerStack = [
            'text-footer-brand-v0147' => [10, 0],
            'text-footer-description-v0147' => [20, 8],
            'text-footer-shortcuts-heading-v0147' => [30, 20],
            'menu-footer-shortcuts-v3' => [40, 6],
            'text-footer-association-heading-v0147' => [50, 20],
            'button-footer-join-v0147' => [60, 10],
            'button-footer-contact-v0147' => [70, 8],
            'container-footer-divider-v0147' => [80, 20],
            'text-footer-copyright-v0147' => [90, 12],
        ];
        foreach ($footerStack as $footerId => $stack) {
            if (!isset($byId[$footerId])) { continue; }
            $css .= $scope . '#h18-clean-' . self::cssId($footerId)
                . '{order:' . $stack[0] . '!important;margin-top:' . $stack[1] . 'px!important;}';
        }

        // Alpha.30: V1 footer rhythm. Alpha.24/26 already established the
        // measured 32/15/20 outer padding and V1 typography, so retain those
        // values and remove only the extra inner whitespace introduced by the
        // grouped Alpha.29 stack.
        $css .= $scope . '.h18-clean-front-surface{gap:0!important;}'
            . $scope . '#h18-clean-text-footer-brand-v0147 .h18-clean-front-text-heading,'
            . $scope . '#h18-clean-text-footer-brand-v0147 .h18-clean-front-text-body,'
            . $scope . '#h18-clean-text-footer-description-v0147 .h18-clean-front-text-heading,'
            . $scope . '#h18-clean-text-footer-description-v0147 .h18-clean-front-text-body,'
            . $scope . '#h18-clean-text-footer-shortcuts-heading-v0147 .h18-clean-front-text-heading,'
            . $scope . '#h18-clean-text-footer-shortcuts-heading-v0147 .h18-clean-front-text-body,'
            . $scope . '#h18-clean-text-footer-association-heading-v0147 .h18-clean-front-text-heading,'
            . $scope . '#h18-clean-text-footer-association-heading-v0147 .h18-clean-front-text-body,'
            . $scope . '#h18-clean-text-footer-copyright-v0147 .h18-clean-front-text-heading,'
            . $scope . '#h18-clean-text-footer-copyright-v0147 .h18-clean-front-text-body{margin-top:0!important;margin-bottom:0!important;}'
            . $scope . '#h18-clean-text-footer-description-v0147 p,'
            . $scope . '#h18-clean-text-footer-copyright-v0147 p{margin-top:0!important;margin-bottom:0!important;}'
            . $scope . '#h18-clean-menu-footer-shortcuts-v3 .h18-clean-front-menu-list{gap:6px!important;line-height:1.35!important;margin:0!important;padding:0!important;}'
            . $scope . '#h18-clean-menu-footer-shortcuts-v3 .h18-clean-front-menu-list a{padding-top:0!important;padding-bottom:0!important;line-height:1.35!important;}'
            . $scope . '#h18-clean-button-footer-join-v0147,'
            . $scope . '#h18-clean-button-footer-contact-v0147{width:100%!important;max-width:100%!important;}'
            . $scope . '#h18-clean-button-footer-join-v0147 .h18-clean-front-button-link,'
            . $scope . '#h18-clean-button-footer-contact-v0147 .h18-clean-front-button-link{width:100%!important;min-height:44px!important;padding:11px 16px!important;font-size:14px!important;line-height:1.25!important;box-sizing:border-box!important;}'
            . $scope . '#h18-clean-container-footer-divider-v0147{width:100%!important;max-width:100%!important;padding:0!important;}'
            . $scope . '#h18-clean-text-footer-copyright-v0147{padding:0!important;}';
        return $css;
"""
if rr.count(old) != 1:
    raise SystemExit(f'Alpha.30 footer parity anchor mismatch: {rr.count(old)}')
rr = rr.replace(old, new, 1)
write(rr_rel, rr)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.29':
    raise SystemExit('Expected Alpha.29 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-09',
    'items': [
        'Footer-only V1 parity: Alpha.29 gruppestruktur bevares, mens de ekstra mobile gruppemargener strammes til V1-lignende rytme.',
        'Footerens målte 32/15/20 px ydre padding fra Alpha.24 og V1-typografien fra Alpha.26 bevares uændret.',
        'Indre tekst-/paragraph-margener nulstilles i Footeren, så der ikke opstår skjulte ekstra vertikale mellemrum.',
        'Genveje-menuen bruger 6 px link-gap og kompakt 1.35 line-height; indhold og rækkefølge følger fortsat den valgte Website-menu dynamisk.',
        'Footer CTA-knapper normaliseres til fuld bredde, 44 px minimumshøjde og 11/16 px padding for samme visuelle tyngde som V1.',
        'Header, side-sektioner, Desktop-master Mobile layout, Event-fixes og øvrig Alpha.29 runtime er urørt.'
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
rr = read(rr_rel)
renderer = read('src/Frontend/Renderer.php')
layout = read('src/Model/LayoutModel.php')
history_text = read('release-history.json')

for token in ['Version: 3.0.0-alpha.30', "define('VDM_VERSION', '3.0.0-alpha.30');"]:
    if token not in main:
        raise SystemExit(f'Alpha.30 main token missing: {token}')
for token in [
    "'text-footer-description-v0147' => [20, 8]",
    "'text-footer-shortcuts-heading-v0147' => [30, 20]",
    "'menu-footer-shortcuts-v3' => [40, 6]",
    "'text-footer-copyright-v0147' => [90, 12]",
    '#h18-clean-menu-footer-shortcuts-v3 .h18-clean-front-menu-list{gap:6px!important',
    'min-height:44px!important;padding:11px 16px!important;font-size:14px!important',
    'Alpha.30: V1 footer rhythm.',
]:
    if token not in rr:
        raise SystemExit(f'Alpha.30 responsive token missing: {token}')

# Regression locks: these are explicitly outside Alpha.30 scope.
for token in [
    "if ($id === 'menu-footer-shortcuts-v3')",
    "$props['menuSource'] = 'website';",
    'private static function renderEventProgramText(',
    'private static function eventGalleryButton(',
    'h18-clean-front-menu-summary',
    'is-open',
]:
    if token not in renderer:
        raise SystemExit(f'Alpha.30 retained renderer token missing: {token}')
for token in ['$mobile = $desktop;', "$mobile['inheritDesktop'] = true;"]:
    if token not in layout:
        raise SystemExit(f'Alpha.30 Desktop-master token missing: {token}')
if 'self::v1PaintCss($pageModel, $legacyPageModel, $pageScope)' in rr:
    raise SystemExit('Alpha.30 mobile-only paint regression')
if '3.0.0-alpha.30' not in history_text:
    raise SystemExit('Alpha.30 history token missing')

print('PASS')
