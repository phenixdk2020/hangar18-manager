from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.31'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha30.py'], check=True)


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
    (' * Version: 3.0.0-alpha.30', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.30');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.30');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.31 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Module Design: shared Footer gap for collection + detail pages.
# ---------------------------------------------------------------------------
replace_once(
    'src/Model/ModuleDesignModel.php',
    "            'sectionGap' => 44,\n",
    "            'sectionGap' => 44,\n            'footerGap' => 64,\n",
    'Alpha.31 ModuleDesign footerGap default'
)
replace_once(
    'src/Model/ModuleDesignModel.php',
    "            'sectionGap' => self::clamp($raw['sectionGap'] ?? $defaults['sectionGap'], 12, 100, 44),\n",
    "            'sectionGap' => self::clamp($raw['sectionGap'] ?? $defaults['sectionGap'], 12, 100, 44),\n            'footerGap' => self::clamp($raw['footerGap'] ?? $defaults['footerGap'], 0, 200, 64),\n",
    'Alpha.31 ModuleDesign footerGap normalize'
)

replace_once(
    'src/Admin/EditorController.php',
    "            echo '<h2>Moduldesign</h2><p>Ændringer vises direkte i den samme renderer som den offentlige side.</p>';\n",
    "            echo '<h2>Moduldesign</h2><p>Ændringer vises direkte i den samme renderer som den offentlige side. Afstand til Footer gælder både moduloversigten og modulets detaljesider.</p>';\n",
    'Alpha.31 ModuleDesign Footer help'
)
replace_once(
    'src/Admin/EditorController.php',
    "                'sectionGap' => ['Afstand mellem sektioner (px)', 12, 100, 1],\n",
    "                'sectionGap' => ['Afstand mellem sektioner (px)', 12, 100, 1],\n                'footerGap' => ['Afstand til Footer (px)', 0, 200, 1],\n",
    'Alpha.31 ModuleDesign Footer field'
)

# ---------------------------------------------------------------------------
# Canonical collection renderer: use the same setting in preview + frontend.
# Existing 58 px hard-coded bottom padding becomes a versioned module value.
# ---------------------------------------------------------------------------
replace_once(
    'src/Frontend/CollectionPageRenderer.php',
    "        $sectionGap = (int) ($design['sectionGap'] ?? 44);\n        $maxWidth = $cardMax > 0 ? $cardMax . 'px' : 'none';\n",
    "        $sectionGap = (int) ($design['sectionGap'] ?? 44);\n        $footerGap = max(0, min(200, (int) ($design['footerGap'] ?? 64)));\n        $maxWidth = $cardMax > 0 ? $cardMax . 'px' : 'none';\n",
    'Alpha.31 collection Footer variable'
)
replace_once(
    'src/Frontend/CollectionPageRenderer.php',
    ";--h18-module-section-gap:' . $sectionGap . 'px;width:90%;max-width:none;width:var(--h18-module-page-width);margin:0 auto;padding:36px 0 58px;color:#30382a",
    ";--h18-module-section-gap:' . $sectionGap . 'px;--h18-module-footer-gap:' . $footerGap . 'px;width:90%;max-width:none;width:var(--h18-module-page-width);margin:0 auto;padding:36px 0 var(--h18-module-footer-gap);color:#30382a",
    'Alpha.31 collection Footer CSS'
)

# ---------------------------------------------------------------------------
# V3 detail pages are separate Visual Designer pages. Resolve their owner
# collection and let the collection's Module Design control the Footer gap.
# Use shell padding for these detail pages so dynamic Event content (including
# the optional gallery CTA) gets a real flow reserve before the Footer.
# Ordinary pages keep their existing responsive pageSettings.footerGap.
# ---------------------------------------------------------------------------
replace_once(
    'src/Frontend/ResponsiveRenderer.php',
    "use VisualDesignerManager\\Model\\LayoutModel;\nuse VisualDesignerManager\\Model\\TemplateLayoutModel;\n",
    "use VisualDesignerManager\\Model\\LayoutModel;\nuse VisualDesignerManager\\Model\\ModuleDesignModel;\nuse VisualDesignerManager\\Model\\TemplateLayoutModel;\n",
    'Alpha.31 Responsive ModuleDesign import'
)
replace_once(
    'src/Frontend/ResponsiveRenderer.php',
    "        $pageSpacing = self::pageSpacingCss($pageModel, ThemeShell::enabled() ? '.h18-vd-live-shell-page' : '.h18-clean-page', is_array($templateModels['header']), is_array($templateModels['footer']));\n",
    "        $moduleFooterGap = self::detailModuleFooterGap($postId);\n        $pageSpacing = self::pageSpacingCss($pageModel, ThemeShell::enabled() ? '.h18-vd-live-shell-page' : '.h18-clean-page', is_array($templateModels['header']), is_array($templateModels['footer']), $moduleFooterGap);\n",
    'Alpha.31 pageSpacing module Footer call'
)
replace_once(
    'src/Frontend/ResponsiveRenderer.php',
    "    private static function pageSpacingCss(array $model, string $pageSelector, bool $hasHeader, bool $hasFooter): array\n",
    "    private static function pageSpacingCss(array $model, string $pageSelector, bool $hasHeader, bool $hasFooter, ?int $moduleFooterGap = null): array\n",
    'Alpha.31 pageSpacing signature'
)

old_spacing = """        foreach (['desktop','laptop','tablet','mobile'] as $device) {
            $header = $hasHeader ? $value('headerGap', $device) : 0;
            $footer = $hasFooter ? $value('footerGap', $device) : 0;
            $out[$device] = $pageSelector . '{--h18-vdm-page-header-gap:' . $header . 'px;--h18-vdm-page-section-gap:' . $value('sectionGap',$device) . 'px;--h18-vdm-page-element-gap:' . $value('elementGap',$device) . 'px;--h18-vdm-page-footer-gap:' . $footer . 'px;padding-top:' . $header . 'px!important;margin-bottom:' . $footer . 'px!important;}';
        }
        return $out;
    }
"""
new_spacing = """        foreach (['desktop','laptop','tablet','mobile'] as $device) {
            $header = $hasHeader ? $value('headerGap', $device) : 0;
            $footer = $hasFooter ? ($moduleFooterGap !== null ? max(0, min(200, $moduleFooterGap)) : $value('footerGap', $device)) : 0;
            $footerCss = $moduleFooterGap !== null
                ? 'margin-bottom:0!important;padding-bottom:' . $footer . 'px!important;'
                : 'margin-bottom:' . $footer . 'px!important;';
            $out[$device] = $pageSelector . '{--h18-vdm-page-header-gap:' . $header . 'px;--h18-vdm-page-section-gap:' . $value('sectionGap',$device) . 'px;--h18-vdm-page-element-gap:' . $value('elementGap',$device) . 'px;--h18-vdm-page-footer-gap:' . $footer . 'px;padding-top:' . $header . 'px!important;' . $footerCss . '}';
        }
        return $out;
    }

    private static function detailModuleFooterGap(int $postId): ?int
    {
        $slug = sanitize_title((string) get_post_field('post_name', $postId));
        $collectionSlug = [
            'event-detalje' => 'events',
            'album-detalje' => 'billedgalleri',
            'koeretoej-detalje' => 'koeretoejer-og-materiel',
        ][$slug] ?? '';
        if ($collectionSlug === '') { return null; }
        $collection = get_page_by_path($collectionSlug, OBJECT, 'page');
        if (!$collection instanceof \\WP_Post) { return null; }
        $design = ModuleDesignModel::get((int) $collection->ID);
        return max(0, min(200, (int) ($design['footerGap'] ?? 64)));
    }
"""
replace_once(
    'src/Frontend/ResponsiveRenderer.php',
    old_spacing,
    new_spacing,
    'Alpha.31 module detail Footer spacing body'
)

# ---------------------------------------------------------------------------
# Release history.
# ---------------------------------------------------------------------------
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.30':
    raise SystemExit('Expected Alpha.30 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-09',
    'items': [
        'Moduldesign får Afstand til Footer (0–200 px), som gælder både oversigt og detaljeside for Events, Billedgalleri og Køretøjer.',
        'Standard er 64 px; eksisterende moduldesign normaliseres automatisk med den nye indstilling uden datatab.',
        'CollectionPageRenderer bruger samme footerGap i den kanoniske preview og på den offentlige moduloversigt.',
        'Event-/album-/køretøjsdetaljesider læser footerGap fra deres tilhørende modulside og reserverer plads inde i side-shellen før Footeren, så dynamisk indhold ikke falder sammen med Footer.',
        'Almindelige sider beholder deres eksisterende responsive Sideindstillinger → Afstand til Footer. Footer-template, Header og Alpha.30 footer-paritet ændres ikke.',
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# ---------------------------------------------------------------------------
# Deterministic contracts + regression locks.
# ---------------------------------------------------------------------------
main = read('visual-designer-manager.php')
module_design = read('src/Model/ModuleDesignModel.php')
editor = read('src/Admin/EditorController.php')
collection = read('src/Frontend/CollectionPageRenderer.php')
responsive = read('src/Frontend/ResponsiveRenderer.php')
renderer = read('src/Frontend/Renderer.php')
history_text = read('release-history.json')

for token in ['Version: 3.0.0-alpha.31', "define('VDM_VERSION', '3.0.0-alpha.31');"]:
    if token not in main:
        raise SystemExit(f'Alpha.31 main token missing: {token}')
for token in ["'footerGap' => 64", "'footerGap' => self::clamp("]:
    if token not in module_design:
        raise SystemExit(f'Alpha.31 ModuleDesign token missing: {token}')
for token in ['Afstand til Footer (px)', 'gælder både moduloversigten og modulets detaljesider']:
    if token not in editor:
        raise SystemExit(f'Alpha.31 Editor token missing: {token}')
for token in ["$footerGap = max(0, min(200", '--h18-module-footer-gap:', 'padding:36px 0 var(--h18-module-footer-gap)']:
    if token not in collection:
        raise SystemExit(f'Alpha.31 Collection token missing: {token}')
for token in [
    'use VisualDesignerManager\\Model\\ModuleDesignModel;',
    '$moduleFooterGap = self::detailModuleFooterGap($postId);',
    'private static function detailModuleFooterGap(',
    "'event-detalje' => 'events'",
    "'album-detalje' => 'billedgalleri'",
    "'koeretoej-detalje' => 'koeretoejer-og-materiel'",
    "padding-bottom:' . $footer . 'px!important",
]:
    if token not in responsive:
        raise SystemExit(f'Alpha.31 Responsive token missing: {token}')

# Existing event/gallery and Footer contracts must remain intact.
for token in [
    'private static function renderEventProgramText(',
    'private static function eventGalleryButton(',
    'Se billeder fra arrangementet',
    "if ($id === 'menu-footer-shortcuts-v3')",
    "$props['menuSource'] = 'website';",
    'h18-clean-front-menu-summary',
    'is-open',
]:
    if token not in renderer:
        raise SystemExit(f'Alpha.31 retained Renderer token missing: {token}')
for token in [
    "'menu-footer-shortcuts-v3' => [40, 6]",
    'Alpha.30: V1 footer rhythm.',
]:
    if token not in responsive:
        raise SystemExit(f'Alpha.31 Alpha.30 Footer token missing: {token}')
if '3.0.0-alpha.31' not in history_text:
    raise SystemExit('Alpha.31 history token missing')

print('PASS')
