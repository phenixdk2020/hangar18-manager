from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.24'
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


# Alpha.23 release uses the corrected builder so the Alpha.22 working menu
# class remains .h18-clean-front-menu-summary.
subprocess.run(['python3', '.github/scripts/build_v3_alpha23_corrected.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.23', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.23');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.23');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.24 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# Page settings: distance after Header becomes independently editable/versioned.
replace_once(
    'src/Model/LayoutModel.php',
    "        $defaults = [\n            'sectionGap' => ['desktop' => 32, 'laptop' => 32, 'tablet' => 24, 'mobile' => 24],",
    "        $defaults = [\n            'headerGap' => ['desktop' => 32, 'laptop' => 32, 'tablet' => 24, 'mobile' => 24],\n            'sectionGap' => ['desktop' => 32, 'laptop' => 32, 'tablet' => 24, 'mobile' => 24],",
    'Alpha.24 LayoutModel Header gap'
)
replace_once(
    'src/Admin/EditorController.php',
    "$spacingLabels = ['sectionGap' => 'Afstand mellem sektioner', 'elementGap' => 'Standard afstand mellem elementer', 'footerGap' => 'Afstand til Footer'];",
    "$spacingLabels = ['headerGap' => 'Afstand efter Header', 'sectionGap' => 'Afstand mellem sektioner', 'elementGap' => 'Standard afstand mellem elementer', 'footerGap' => 'Afstand til Footer'];",
    'Alpha.24 Designer Header gap'
)
replace_once(
    'assets/editor-v018-core.js',
    "        const defaults = {\n            sectionGap:{desktop:32,laptop:32,tablet:24,mobile:24},",
    "        const defaults = {\n            headerGap:{desktop:32,laptop:32,tablet:24,mobile:24},\n            sectionGap:{desktop:32,laptop:32,tablet:24,mobile:24},",
    'Alpha.24 JS Header gap default'
)
replace_once(
    'assets/editor-v018-core.js',
    "if (!['sectionGap','elementGap','footerGap'].includes(key)",
    "if (!['headerGap','sectionGap','elementGap','footerGap'].includes(key)",
    'Alpha.24 JS Header gap binding'
)

# Responsive runtime: eliminate the conflicting multi-layer mobile cascade.
rr = read('src/Frontend/ResponsiveRenderer.php')
old = "self::pageSpacingCss($pageModel, ThemeShell::enabled() ? '.h18-vd-live-shell-page' : '.h18-clean-page', is_array($templateModels['footer']))"
new = "self::pageSpacingCss($pageModel, ThemeShell::enabled() ? '.h18-vd-live-shell-page' : '.h18-clean-page', is_array($templateModels['header']), is_array($templateModels['footer']))"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 pageSpacingCss call anchor mismatch')
rr = rr.replace(old, new, 1)

old = "private static function pageSpacingCss(array $model, string $pageSelector, bool $hasFooter): array"
new = "private static function pageSpacingCss(array $model, string $pageSelector, bool $hasHeader, bool $hasFooter): array"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 pageSpacingCss signature anchor mismatch')
rr = rr.replace(old, new, 1)

old = "        $defaults = [\n            'sectionGap' => ['desktop'=>32,'laptop'=>32,'tablet'=>24,'mobile'=>24],"
new = "        $defaults = [\n            'headerGap' => ['desktop'=>32,'laptop'=>32,'tablet'=>24,'mobile'=>24],\n            'sectionGap' => ['desktop'=>32,'laptop'=>32,'tablet'=>24,'mobile'=>24],"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 responsive Header gap default anchor mismatch')
rr = rr.replace(old, new, 1)

old = """        foreach (['desktop','laptop','tablet','mobile'] as $device) {
            $footer = $hasFooter ? $value('footerGap', $device) : 0;
            $out[$device] = $pageSelector . '{--h18-vdm-page-section-gap:' . $value('sectionGap',$device) . 'px;--h18-vdm-page-element-gap:' . $value('elementGap',$device) . 'px;--h18-vdm-page-footer-gap:' . $footer . 'px;margin-bottom:' . $footer . 'px!important;}';
        }
"""
new = """        foreach (['desktop','laptop','tablet','mobile'] as $device) {
            $header = $hasHeader ? $value('headerGap', $device) : 0;
            $footer = $hasFooter ? $value('footerGap', $device) : 0;
            $out[$device] = $pageSelector . '{--h18-vdm-page-header-gap:' . $header . 'px;--h18-vdm-page-section-gap:' . $value('sectionGap',$device) . 'px;--h18-vdm-page-element-gap:' . $value('elementGap',$device) . 'px;--h18-vdm-page-footer-gap:' . $footer . 'px;padding-top:' . $header . 'px!important;margin-bottom:' . $footer . 'px!important;}';
        }
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 responsive page spacing output anchor mismatch')
rr = rr.replace(old, new, 1)

# V1 converted pages: Section/Container owns internal flex gap, not old geometry
# margins. Semantic bands below own their outer section gap and inner padding.
old = """        $css = $surface . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;}'
            . $section . ',' . $container . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;padding-top:min(var(--h18-vdm-pad-top,0px),38px)!important;padding-right:min(var(--h18-vdm-pad-right,0px),18px)!important;padding-bottom:min(var(--h18-vdm-pad-bottom,0px),38px)!important;padding-left:min(var(--h18-vdm-pad-left,0px),18px)!important;}'
            . $scope . '.h18-clean-front-event-list,' . $scope . '.h18-clean-front-gallery-list,' . $scope . '.h18-clean-front-gallery-images,' . $scope . '.h18-clean-front-event-facts{grid-template-columns:1fr!important;width:100%!important;max-width:100%!important;}'
"""
new = """        $css = $surface . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;gap:0!important;}'
            . $section . ',' . $container . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;padding:0!important;gap:var(--h18-vdm-page-element-gap,14px)!important;}'
            . $scope . '.h18-clean-front-event-list,' . $scope . '.h18-clean-front-gallery-list,' . $scope . '.h18-clean-front-gallery-images,' . $scope . '.h18-clean-front-event-facts{grid-template-columns:1fr!important;width:100%!important;max-width:100%!important;gap:16px!important;}'
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 mobile flow ownership anchor mismatch')
rr = rr.replace(old, new, 1)

if rr.count("$gapPx = min(24, $gapRows * LayoutModel::ROW_PX);") != 1:
    raise SystemExit('Alpha.24 old child geometry gap anchor mismatch')
rr = rr.replace("$gapPx = min(24, $gapRows * LayoutModel::ROW_PX);", "$gapPx = 0;", 1)

if rr.count('margin-bottom:min(var(--h18-vdm-gap-y,0px),24px)!important;') != 1:
    raise SystemExit('Alpha.24 old child margin-bottom anchor mismatch')
rr = rr.replace('margin-bottom:min(var(--h18-vdm-gap-y,0px),24px)!important;', 'margin-bottom:0!important;', 1)

# Mobile typography and buttons use the measured V1 reference rather than the
# interim Alpha.16/23 values.
old = """        $css .= $pageScope . '.h18-clean-front-text{font-size:16px!important;line-height:1.5!important;}'
            . $pageScope . 'h1.h18-clean-front-text-heading{font-size:32px!important;line-height:1.2!important;}'
            . $pageScope . 'h2.h18-clean-front-text-heading{font-size:24.8px!important;line-height:1.2!important;}'
            . $pageScope . 'h3.h18-clean-front-text-heading{font-size:19.2px!important;line-height:1.2!important;}'
            . $pageScope . 'h4.h18-clean-front-text-heading,' . $pageScope . 'h5.h18-clean-front-text-heading,' . $pageScope . 'h6.h18-clean-front-text-heading{font-size:18px!important;line-height:1.2!important;}'
            . $pageScope . '.h18-clean-front-section,' . $pageScope . '.h18-clean-front-container{padding-left:max(var(--h18-vdm-pad-left,0px),18px)!important;padding-right:max(var(--h18-vdm-pad-right,0px),18px)!important;}'
            . $pageScope . '.h18-clean-front-button-link{min-height:52px!important;padding:13px 24px!important;border-radius:29px!important;font-size:16px!important;line-height:1.2!important;}'
"""
new = """        $css .= $pageScope . '.h18-clean-front-text{font-family:\"Inter\",Arial,sans-serif!important;font-size:16px!important;line-height:1.5!important;}'
            . $pageScope . 'h1.h18-clean-front-text-heading{font-size:32px!important;line-height:1.2!important;}'
            . $pageScope . 'h2.h18-clean-front-text-heading{font-size:25px!important;line-height:1.18!important;}'
            . $pageScope . 'h3.h18-clean-front-text-heading{font-size:19.2px!important;line-height:1.2!important;}'
            . $pageScope . 'h4.h18-clean-front-text-heading,' . $pageScope . 'h5.h18-clean-front-text-heading,' . $pageScope . 'h6.h18-clean-front-text-heading{font-size:18px!important;line-height:1.2!important;}'
            . $pageScope . '.h18-clean-front-button-link{width:100%!important;height:auto!important;min-height:0!important;padding:14px 18px!important;font-size:16px!important;line-height:1.2!important;box-sizing:border-box!important;}'
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 mobile type/button anchor mismatch')
rr = rr.replace(old, new, 1)

old = 'padding:13px 18px!important;border-radius:0!important;width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;font-size:18px!important;font-weight:700!important;line-height:1.35!important;'
new = 'padding:12px 15px!important;border-radius:0!important;width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;font-family:\"Inter\",Arial,sans-serif!important;font-size:16px!important;font-weight:650!important;line-height:1.35!important;'
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 tagline visual anchor mismatch')
rr = rr.replace(old, new, 1)

old = "$css .= $selector . '{width:calc(100% - 20px)!important;max-width:calc(100% - 20px)!important;margin-left:10px!important;margin-right:10px!important;padding:20px!important;border-radius:7px!important;background:' . $bg . '!important;color:' . $fg . '!important;font-size:16px!important;line-height:1.5!important;}'"
new = "$css .= $selector . '{width:100%!important;max-width:100%!important;margin:0!important;padding:0!important;border-radius:0!important;background:transparent!important;color:' . $fg . '!important;font-size:16px!important;line-height:1.5!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 duplicate feature card anchor mismatch')
rr = rr.replace(old, new, 1)

for old, new, label in [
    ('height:220px!important;min-height:220px!important;overflow:hidden!important;margin-bottom:24px!important;', 'height:155px!important;min-height:155px!important;overflow:hidden!important;margin-bottom:0!important;', 'hero outer'),
    ("height:220px!important;min-height:220px!important;}'", "height:155px!important;min-height:155px!important;}'", 'hero inner'),
    ('height:220px!important;object-fit:cover!important;object-position:50% 50%!important;', 'height:155px!important;object-fit:cover!important;object-position:50% 50%!important;', 'hero image'),
]:
    if rr.count(old) != 1:
        raise SystemExit(f'Alpha.24 {label} anchor mismatch: {rr.count(old)}')
    rr = rr.replace(old, new, 1)

# Header: exact V1 mobile reference and ID-specific resets so generated desktop
# min-heights cannot out-specificity the mobile class rules.
old = """        $css = $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section{display:block!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-surface{padding:0!important;}'
            . $scope . '.h18-clean-front-section{padding:0!important;margin:0!important;}'
            . $scope . '.h18-clean-front-container{display:grid!important;grid-template-columns:64px minmax(0,1fr) 48px!important;align-items:center!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;padding:12px 12px!important;margin:0!important;column-gap:10px!important;overflow:visible!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-node{grid-column:auto!important;grid-row:auto!important;position:relative!important;left:auto!important;right:auto!important;top:auto!important;transform:none!important;margin:0!important;min-height:0!important;box-sizing:border-box!important;}';
"""
new = """        $css = $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section{display:block!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;grid-auto-rows:auto!important;grid-template-rows:none!important;}'
            . $scope . '.h18-clean-front-surface{padding:0!important;}'
            . $scope . '.h18-clean-front-section{padding:0!important;margin:0!important;}'
            . $scope . '.h18-clean-front-container{display:grid!important;grid-template-columns:70px minmax(0,1fr) 44px!important;grid-template-rows:auto!important;grid-auto-rows:auto!important;align-items:center!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;padding:7px 11px!important;margin:0!important;column-gap:10px!important;overflow:visible!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-node{grid-column:auto!important;grid-row:auto!important;position:relative!important;left:auto!important;right:auto!important;top:auto!important;transform:none!important;margin:0!important;height:auto!important;min-height:0!important;box-sizing:border-box!important;}';
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 Header structural anchor mismatch')
rr = rr.replace(old, new, 1)

header_start = rr.find('private static function v1HeaderMobileCss')
needle = """            $props = is_array($node['props'] ?? null) ? $node['props'] : [];
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            if ($type === 'image') {
"""
header_pos = rr.find(needle, header_start)
if header_start < 0 or header_pos < 0:
    raise SystemExit('Alpha.24 Header per-ID reset anchor missing')
replacement = """            $props = is_array($node['props'] ?? null) ? $node['props'] : [];
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            $css .= $selector . '{height:auto!important;min-height:0!important;margin:0!important;}';
            if (in_array($type, ['section','container'], true)) {
                $css .= $selector . '{grid-auto-rows:auto!important;grid-template-rows:none!important;padding:0!important;}';
            }
            if ($type === 'image') {
"""
rr = rr[:header_pos] + replacement + rr[header_pos + len(needle):]

old = "$css .= $selector . '{grid-column:1!important;grid-row:1!important;width:64px!important;max-width:64px!important;height:64px!important;}'\n                    . $selector . ' .h18-clean-front-image,' . $selector . ' .h18-clean-front-image img{width:100%!important;height:100%!important;max-width:100%!important;object-fit:contain!important;}'"
new = "$css .= $selector . '{grid-column:1!important;grid-row:1!important;width:70px!important;max-width:70px!important;height:auto!important;}'\n                    . $selector . ' .h18-clean-front-image,' . $selector . ' .h18-clean-front-image img{width:70px!important;height:auto!important;max-width:70px!important;object-fit:contain!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 Header logo anchor mismatch')
rr = rr.replace(old, new, 1)

old = 'font-size:16px!important;font-weight:700!important;line-height:1.16!important;text-align:left!important;'
new = 'font-family:\"Inter\",Arial,sans-serif!important;font-size:17px!important;font-weight:750!important;line-height:1.15!important;text-align:left!important;'
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 Header title anchor mismatch')
rr = rr.replace(old, new, 1)

old = "$css .= $selector . '{grid-column:3!important;grid-row:1!important;width:48px!important;max-width:48px!important;height:48px!important;margin:0!important;padding:0!important;background:transparent!important;justify-self:end!important;}'\n                    . $selector . ' .h18-clean-front-menu-summary{width:48px!important;height:48px!important;}'"
new = "$css .= $selector . '{grid-column:3!important;grid-row:1!important;width:44px!important;max-width:44px!important;height:44px!important;margin:0!important;padding:0!important;background:transparent!important;justify-self:end!important;}'\n                    . $selector . ' .h18-clean-front-menu-summary{width:44px!important;height:44px!important;border-width:1px!important;border-radius:6px!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 Header hamburger anchor mismatch')
rr = rr.replace(old, new, 1)

# Footer: one outer padding owner; reset every node at ID specificity to remove
# the measured 656px minimum-height leak from responsive geometry.
old = """        $css = $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section,' . $scope . '.h18-clean-front-container{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section{padding:0!important;margin:0!important;}'
            . $scope . '.h18-clean-front-container{padding:28px 16px 24px!important;margin:0!important;}'
"""
new = """        $css = $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section,' . $scope . '.h18-clean-front-container{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;grid-auto-rows:auto!important;grid-template-rows:none!important;}'
            . $scope . '.h18-clean-front-surface{padding:32px 15px 20px!important;margin:0!important;}'
            . $scope . '.h18-clean-front-section,' . $scope . '.h18-clean-front-container{padding:0!important;margin:0!important;}'
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 Footer outer padding anchor mismatch')
rr = rr.replace(old, new, 1)

old = """        if ($legacy !== null) { $css .= self::v1PaintCss($model, $legacy, $scope); }

        foreach ($byParent as $children) {
"""
new = """        if ($legacy !== null) { $css .= self::v1PaintCss($model, $legacy, $scope); }

        // Responsive geometry is emitted as ID rules before this pass. Reset each
        // footer node with the same specificity so stale 656px/desktop heights cannot win.
        foreach ($byId as $id => $node) {
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            $css .= $selector . '{grid-column:auto!important;grid-row:auto!important;position:relative!important;left:auto!important;right:auto!important;top:auto!important;transform:none!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;margin-right:0!important;margin-bottom:0!important;box-sizing:border-box!important;}';
            if (in_array((string) ($node['type'] ?? ''), ['section','container'], true)) {
                $css .= $selector . '{display:flex!important;flex-direction:column!important;grid-auto-rows:auto!important;grid-template-rows:none!important;padding:0!important;}';
            }
        }

        foreach ($byParent as $children) {
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 Footer ID reset anchor mismatch')
rr = rr.replace(old, new, 1)

# Root/nested full-width ownership: use 100% of a deliberately full-width
# parent. Remove stacked 100vw/negative-margin breakout layers.
old = "$css .= $selector . '{width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;box-sizing:border-box!important;}'"
new = "$css .= $selector . '{width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;box-sizing:border-box!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 root 100vw breakout anchor mismatch')
rr = rr.replace(old, new, 1)

old = "$css .= $selector . '{padding-left:18px!important;padding-right:18px!important;border-radius:0!important;}'"
new = "$css .= $selector . '{padding-left:0!important;padding-right:0!important;border-radius:0!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 root inherited side-padding anchor mismatch')
rr = rr.replace(old, new, 1)

if rr.count("$featureIds[$id] = true;") != 1:
    raise SystemExit('Alpha.24 feature ID map anchor mismatch')
rr = rr.replace("$featureIds[$id] = true;", "$featureIds[$id] = $heading;", 1)

old = 'padding:0!important;overflow:visible!important;}\';'
new = 'padding:0!important;gap:0!important;overflow:visible!important;}\';'
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 hero/tagline path wrapper anchor mismatch')
rr = rr.replace(old, new, 1)

old = "$css .= $selector . '{width:100vw!important;max-width:100vw!important;height:160px!important;min-height:160px!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;margin-top:0!important;margin-bottom:0!important;padding:0!important;border-radius:0!important;overflow:hidden!important;}'\n                . $selector . ' .h18-clean-front-image{width:100%!important;max-width:100%!important;height:160px!important;min-height:160px!important;margin:0!important;padding:0!important;border-radius:0!important;}'\n                . $selector . ' .h18-clean-front-image img{display:block!important;width:100%!important;max-width:100%!important;height:160px!important;object-fit:cover!important;border-radius:0!important;}'"
new = "$css .= $selector . '{width:100%!important;max-width:100%!important;height:155px!important;min-height:155px!important;margin-left:0!important;margin-right:0!important;margin-top:0!important;margin-bottom:0!important;padding:0!important;border-radius:0!important;overflow:hidden!important;}'\n                . $selector . ' .h18-clean-front-image{width:100%!important;max-width:100%!important;height:155px!important;min-height:155px!important;margin:0!important;padding:0!important;border-radius:0!important;}'\n                . $selector . ' .h18-clean-front-image img{display:block!important;width:100%!important;max-width:100%!important;height:155px!important;object-fit:cover!important;object-position:50% 50%!important;border-radius:0!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 nested Hero anchor mismatch')
rr = rr.replace(old, new, 1)

old = "$css .= $selector . '{width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;margin-top:var(--h18-vdm-page-section-gap,24px)!important;margin-bottom:0!important;padding:13px 18px!important;border-radius:0!important;background:#c3ae83!important;color:#30382a!important;text-align:center!important;box-sizing:border-box!important;}'"
new = "$css .= $selector . '{width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;margin-top:var(--h18-vdm-page-section-gap,24px)!important;margin-bottom:0!important;padding:12px 15px!important;border-radius:0!important;background:#c3ae83!important;color:#30382a!important;font-family:\"Inter\",Arial,sans-serif!important;font-size:16px!important;font-weight:650!important;line-height:1.35!important;text-align:center!important;box-sizing:border-box!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 nested Tagline anchor mismatch')
rr = rr.replace(old, new, 1)

old = "$css .= $selector . '{width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;margin-top:var(--h18-vdm-page-section-gap,24px)!important;margin-bottom:0!important;padding-left:18px!important;padding-right:18px!important;box-sizing:border-box!important;border-radius:0!important;overflow:visible!important;}'"
new = "$css .= $selector . '{width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;margin-top:var(--h18-vdm-page-section-gap,24px)!important;margin-bottom:0!important;padding:30px 15px!important;box-sizing:border-box!important;border-radius:0!important;overflow:visible!important;gap:var(--h18-vdm-page-element-gap,14px)!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 major band padding anchor mismatch')
rr = rr.replace(old, new, 1)

old = """        foreach (array_keys($majorIds) as $semanticId) {
            $bandId = $nearestBand($semanticId);
            $majorWrapperIds[$bandId] = true;
            foreach ($ancestorChain($bandId) as $ancestorId) {
                $majorWrapperIds[$ancestorId] = true;
            }
        }
"""
new = """        foreach (array_keys($majorIds) as $semanticId) {
            $bandId = $nearestBand($semanticId);
            foreach ($ancestorChain($bandId) as $ancestorId) {
                $majorWrapperIds[$ancestorId] = true;
            }
        }
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 major wrapper ownership anchor mismatch')
rr = rr.replace(old, new, 1)

old = "$css .= $selector . '{max-width:100%!important;padding-left:0!important;padding-right:0!important;overflow:visible!important;}';"
new = "$css .= $selector . '{width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;margin-top:0!important;margin-bottom:0!important;padding:0!important;gap:0!important;overflow:visible!important;}';"
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 major wrapper reset anchor mismatch')
rr = rr.replace(old, new, 1)

old = """        foreach (array_keys($featureIds) as $id) {
            $selector = $scope . '#h18-clean-' . self::cssId($id);
            $css .= $selector . '{width:calc(100% - 20px)!important;max-width:calc(100% - 20px)!important;margin-left:10px!important;margin-right:10px!important;margin-top:var(--h18-vdm-page-element-gap,14px)!important;margin-bottom:0!important;}';
        }
"""
new = """        foreach ($featureIds as $id => $heading) {
            $bandId = $nearestBand($id);
            $bandSelector = $scope . '#h18-clean-' . self::cssId($bandId);
            $textSelector = $scope . '#h18-clean-' . self::cssId($id);
            $bg = $heading === 'Bevaring' ? '#f2f0e8' : ($heading === 'Formidling' ? '#c3ae83' : '#525a5f');
            $fg = $heading === 'Fællesskab' ? '#ffffff' : '#30382a';
            $css .= $bandSelector . '{width:calc(100% - 20px)!important;max-width:calc(100% - 20px)!important;margin-left:10px!important;margin-right:10px!important;margin-top:0!important;margin-bottom:0!important;padding:18px!important;border-radius:8px!important;background:' . $bg . '!important;color:' . $fg . '!important;box-sizing:border-box!important;}'
                . $textSelector . '{width:100%!important;max-width:100%!important;margin:0!important;padding:0!important;border-radius:0!important;background:transparent!important;color:' . $fg . '!important;}'
                . $textSelector . ' .h18-clean-front-text-heading{color:' . $fg . '!important;margin-bottom:12px!important;}';
        }
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.24 feature card single-surface anchor mismatch')
rr = rr.replace(old, new, 1)

write('src/Frontend/ResponsiveRenderer.php', rr)

# Renderer: match V1 hamburger geometry and strip only redundant leading line
# breaks immediately after a separate heading element.
renderer = read('src/Frontend/Renderer.php')
old = 'width:48px;height:48px;box-sizing:border-box;padding:0;border:1.5px solid var(--h18-menu-color);border-radius:8px;'
new = 'width:44px;height:44px;box-sizing:border-box;padding:0;border:1px solid var(--h18-menu-color);border-radius:6px;'
if renderer.count(old) != 1:
    raise SystemExit('Alpha.24 Renderer hamburger CSS anchor mismatch')
renderer = renderer.replace(old, new, 1)

old = """            $rawText = (string) ($props['text'] ?? '');
            $bodyHtml = self::renderStoredRichText($rawText);
"""
new = """            $rawText = (string) ($props['text'] ?? '');
            if ($heading !== '') {
                $rawText = preg_replace('/^(?:(?:\\r\\n|\\r|\\n)|\\s*<br\\s*\\/?\\s*>\\s*)+/i', '', $rawText) ?? $rawText;
            }
            $bodyHtml = self::renderStoredRichText($rawText);
"""
if renderer.count(old) != 1:
    raise SystemExit('Alpha.24 redundant heading BR anchor mismatch')
renderer = renderer.replace(old, new, 1)
write('src/Frontend/Renderer.php', renderer)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.23':
    raise SystemExit('Expected Alpha.23 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-08',
    'items': [
        'V1 mobile cascade cleanup: Header/Footer node-ID geometry resettes med samme specificitet, så gamle desktop-minimumshøjder ikke kan overleve på telefon.',
        'Header følger de målte V1-referenceværdier: 7/11 px padding, 70 px logo, 17 px/750 titel og 44 px hamburger med 1 px kant og 6 px radius.',
        'Mobil sideflow har én spacing-ejer: 24 px sektionsafstand, 30/15 px indholdssektion-padding, 16 px Event/Galleri-gap og 24 px før Footer som standard.',
        'Hero/tagline følger V1 CSS-reference: 155 px hero, 16 px/650 tagline og 12/15 px tagline-padding; nested 100vw/negative-margin breakouts fjernes.',
        'Bevaring/Formidling/Fællesskab bruger én 18 px/8 px kortflade i stedet for en ekstra indrammet overskriftsboks; redundant indledende BR efter overskrift fjernes ved rendering.',
        'Sider → Sideindstillinger får Afstand efter Header, responsive og versioneret sammen med sektion/element/Footer-afstande; Alpha.22 Website-menu er bevaret.'
    ],
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Deterministic contract checks.
checks = {
    'visual-designer-manager.php': ['Version: 3.0.0-alpha.24'],
    'src/Model/LayoutModel.php': ["'headerGap' =>", "'sectionGap' =>", "'footerGap' =>"],
    'src/Admin/EditorController.php': ['Afstand efter Header', 'Afstand mellem sektioner', 'Afstand til Footer'],
    'assets/editor-v018-core.js': ['headerGap:{desktop:32,laptop:32,tablet:24,mobile:24}', "['headerGap','sectionGap','elementGap','footerGap']"],
    'src/Frontend/ResponsiveRenderer.php': [
        '--h18-vdm-page-header-gap:',
        'grid-template-columns:70px minmax(0,1fr) 44px',
        'padding:7px 11px!important',
        'font-size:17px!important;font-weight:750!important;line-height:1.15!important',
        'height:155px!important',
        'padding:12px 15px!important',
        'font-size:16px!important;font-weight:650!important;line-height:1.35!important',
        'padding:30px 15px!important',
        'gap:16px!important',
        'padding:32px 15px 20px!important',
        'stale 656px/desktop heights cannot win',
        'padding:18px!important;border-radius:8px!important',
    ],
    'src/Frontend/Renderer.php': [
        'width:44px;height:44px;box-sizing:border-box;padding:0;border:1px solid var(--h18-menu-color);border-radius:6px',
        "preg_replace('/^(?:(?:\\r\\n|\\r|\\n)|\\s*<br\\s*\\/?\\s*>\\s*)+/i'",
        'h18-clean-front-menu-summary',
        'is-open',
    ],
}
for rel, tokens in checks.items():
    value = read(rel)
    for token in tokens:
        if token not in value:
            raise SystemExit(f'Alpha.24 contract token missing in {rel}: {token}')

responsive = read('src/Frontend/ResponsiveRenderer.php')
for forbidden in [
    'calc(50% - 50vw)',
    'width:100vw!important',
    'height:160px!important',
    'padding:28px 16px 24px!important',
    'padding-top:min(var(--h18-vdm-pad-top,0px),38px)',
    'padding:20px!important;border-radius:7px!important',
]:
    if forbidden in responsive:
        raise SystemExit(f'Alpha.24 forbidden stale mobile cascade token remains: {forbidden}')

if '<details class="h18-clean-front-menu-details">' in read('src/Frontend/Renderer.php'):
    raise SystemExit('Alpha.24 must retain Alpha.22 normal-DOM menu wrapper')

print(f'Built {VERSION}')
print('V1 mobile cascade ownership cleanup: PASS')
print('Header/footer ID specificity reset: PASS')
print('V1 measured mobile CSS reference values: PASS')
print('Per-page Header/section/element/Footer spacing: PASS')
