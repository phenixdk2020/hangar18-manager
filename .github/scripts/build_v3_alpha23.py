from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.23'
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


subprocess.run(['python3', '.github/scripts/build_v3_alpha22.py'], check=True)

# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.22', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.22');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.22');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.23 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# Page-level responsive spacing becomes part of the canonical page model.
replace_once(
    'src/Model/LayoutModel.php',
    "            'rowPx' => self::ROW_PX,\n            'nodes' => [],\n",
    "            'rowPx' => self::ROW_PX,\n            'pageSettings' => self::pageSettings([]),\n            'nodes' => [],\n",
    'Alpha.23 empty page settings'
)
replace_once(
    'src/Model/LayoutModel.php',
    "            'rowPx' => self::ROW_PX,\n            'nodes' => array_values($nodes),\n",
    "            'rowPx' => self::ROW_PX,\n            'pageSettings' => self::pageSettings(isset($raw['pageSettings']) && is_array($raw['pageSettings']) ? $raw['pageSettings'] : []),\n            'nodes' => array_values($nodes),\n",
    'Alpha.23 normalized page settings'
)
layout = read('src/Model/LayoutModel.php')
anchor = "    /** @param array<string,mixed> $model */\n    public static function saveVersion"
helper = r'''    /** @param array<string,mixed> $raw @return array<string,mixed> */
    private static function pageSettings(array $raw): array
    {
        $defaults = [
            'sectionGap' => ['desktop' => 32, 'laptop' => 32, 'tablet' => 24, 'mobile' => 24],
            'elementGap' => ['desktop' => 16, 'laptop' => 16, 'tablet' => 14, 'mobile' => 14],
            'footerGap' => ['desktop' => 32, 'laptop' => 32, 'tablet' => 24, 'mobile' => 24],
        ];
        $out = [];
        foreach ($defaults as $key => $devices) {
            $source = isset($raw[$key]) && is_array($raw[$key]) ? $raw[$key] : [];
            foreach ($devices as $device => $fallback) {
                $out[$key][$device] = self::clamp($source[$device] ?? $fallback, 0, 200, $fallback);
            }
        }
        return $out;
    }

'''
if layout.count(anchor) != 1:
    raise SystemExit('Alpha.23 LayoutModel pageSettings helper anchor mismatch')
write('src/Model/LayoutModel.php', layout.replace(anchor, helper + anchor, 1))

# Sider -> Sideindstillinger -> Afstande.
editor = read('src/Admin/EditorController.php')
old = """        echo '</select></label><span class=\"description\">Header og Footer vælges uafhængigt. Theme-shell er aktiv på Visual Designer-sider; Automatisk bruger den aktive website-standard.</span></section>';

        echo '<div class=\"h18-clean-toolbar\">';
"""
new = """        echo '</select></label><span class=\"description\">Header og Footer vælges uafhængigt. Theme-shell er aktiv på Visual Designer-sider; Automatisk bruger den aktive website-standard.</span></section>';

        $pageSettings = isset($model['pageSettings']) && is_array($model['pageSettings']) ? $model['pageSettings'] : [];
        echo '<details class=\"h18-clean-page-shell h18-vd-page-settings\" open><summary><strong>Sideindstillinger · Afstande</strong></summary>';
        echo '<p class=\"description\">Styr den enkelte sides responsive luft. Afstand til Footer ligger efter sidste sideelement og før Footeren – ikke inde i Footeren.</p>';
        echo '<table class=\"widefat striped\"><thead><tr><th>Indstilling</th><th>Desktop</th><th>Laptop</th><th>Tablet</th><th>Mobil</th></tr></thead><tbody>';
        $spacingLabels = ['sectionGap' => 'Afstand mellem sektioner', 'elementGap' => 'Standard afstand mellem elementer', 'footerGap' => 'Afstand til Footer'];
        foreach ($spacingLabels as $spacingKey => $spacingLabel) {
            echo '<tr><th>' . esc_html($spacingLabel) . '</th>';
            foreach (['desktop' => 32, 'laptop' => 32, 'tablet' => 24, 'mobile' => 24] as $device => $fallback) {
                if ($spacingKey === 'elementGap') { $fallback = in_array($device, ['tablet','mobile'], true) ? 14 : 16; }
                $value = isset($pageSettings[$spacingKey][$device]) ? (int) $pageSettings[$spacingKey][$device] : $fallback;
                echo '<td><label><span class=\"screen-reader-text\">' . esc_html($spacingLabel . ' ' . $device) . '</span><input type=\"number\" min=\"0\" max=\"200\" step=\"1\" value=\"' . esc_attr((string) $value) . '\" data-page-spacing-key=\"' . esc_attr($spacingKey) . '\" data-page-spacing-device=\"' . esc_attr($device) . '\"> px</label></td>';
            }
            echo '</tr>';
        }
        echo '</tbody></table></details>';

        echo '<div class=\"h18-clean-toolbar\">';
"""
if editor.count(old) != 1:
    raise SystemExit('Alpha.23 Editor page settings anchor mismatch')
write('src/Admin/EditorController.php', editor.replace(old, new, 1))

# Keep pageSettings in client-side canonical state and bind the controls.
js = read('assets/editor-v018-core.js')
anchor = "    function normalizeModel(raw) {\n"
helper = r'''    function normalizePageSettings(raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        const defaults = {
            sectionGap:{desktop:32,laptop:32,tablet:24,mobile:24},
            elementGap:{desktop:16,laptop:16,tablet:14,mobile:14},
            footerGap:{desktop:32,laptop:32,tablet:24,mobile:24}
        };
        const out = {};
        Object.keys(defaults).forEach(function (key) {
            out[key] = {};
            Object.keys(defaults[key]).forEach(function (device) {
                const value = raw[key] && raw[key][device] != null ? parseInt(raw[key][device], 10) : defaults[key][device];
                out[key][device] = clamp(Number.isFinite(value) ? value : defaults[key][device], 0, 200);
            });
        });
        return out;
    }

'''
if js.count(anchor) != 1:
    raise SystemExit('Alpha.23 editor normalize helper anchor mismatch')
js = js.replace(anchor, helper + anchor, 1)
old = "        return { schemaVersion: 1, units: UNITS, rowPx: ROW_PX, nodes: nodes };\n"
new = "        return { schemaVersion: 1, units: UNITS, rowPx: ROW_PX, pageSettings: normalizePageSettings(raw.pageSettings), nodes: nodes };\n"
if js.count(old) != 1:
    raise SystemExit('Alpha.23 editor model return anchor mismatch')
js = js.replace(old, new, 1)
old = """    function install() {
        document.querySelectorAll('.h18-clean-add').forEach(function (button) {
"""
new = r'''    function install() {
        document.querySelectorAll('[data-page-spacing-key][data-page-spacing-device]').forEach(function (control) {
            control.addEventListener('change', function () {
                const key = String(control.getAttribute('data-page-spacing-key') || '');
                const device = String(control.getAttribute('data-page-spacing-device') || '');
                if (!['sectionGap','elementGap','footerGap'].includes(key) || !['desktop','laptop','tablet','mobile'].includes(device)) { return; }
                const before = clone(state);
                state.pageSettings = normalizePageSettings(state.pageSettings);
                state.pageSettings[key][device] = clamp(parseInt(control.value || '0', 10) || 0, 0, 200);
                control.value = String(state.pageSettings[key][device]);
                commit(before, 'Sideafstand · ' + key + ' · ' + device);
                updateHidden();
                if (window.H18VDViewport && typeof window.H18VDViewport.refresh === 'function') { window.H18VDViewport.refresh(); }
            });
        });
        document.querySelectorAll('.h18-clean-add').forEach(function (button) {
'''
if js.count(old) != 1:
    raise SystemExit('Alpha.23 page settings client binding anchor mismatch')
write('assets/editor-v018-core.js', js.replace(old, new, 1))

# Frontend responsive spacing variables + V1 mobile rhythm correction.
rr = read('src/Frontend/ResponsiveRenderer.php')
old = """        $v1NestedMobileEdgeParity = $legacyPageModel !== null
            ? self::v1NestedMobileEdgeParityCss($pageModel, $pageScope)
            : '';

        $laptop = '';
"""
new = """        $v1NestedMobileEdgeParity = $legacyPageModel !== null
            ? self::v1NestedMobileEdgeParityCss($pageModel, $pageScope)
            : '';
        $pageSpacing = self::pageSpacingCss($pageModel, ThemeShell::enabled() ? '.h18-vd-live-shell-page' : '.h18-clean-page', is_array($templateModels['footer']));

        $laptop = '';
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 page spacing setup anchor mismatch')
rr = rr.replace(old, new, 1)
old = """        echo '.h18-vd-live-shell,.h18-vd-live-shell-part,.h18-vd-live-shell-part>.h18-clean-page{width:100%;max-width:100%;min-width:0;box-sizing:border-box}';
        echo '@media(max-width:' . esc_attr((string) self::LAPTOP_MAX) . 'px){' . $laptop . '}';
        echo '@media(max-width:' . esc_attr((string) self::TABLET_MAX) . 'px){' . $tablet . '}';
"""
new = """        echo '.h18-vd-live-shell,.h18-vd-live-shell-part,.h18-vd-live-shell-part>.h18-clean-page{width:100%;max-width:100%;min-width:0;box-sizing:border-box}';
        echo $pageSpacing['desktop'];
        echo '@media(max-width:' . esc_attr((string) self::LAPTOP_MAX) . 'px){' . $laptop . $pageSpacing['laptop'] . '}';
        echo '@media(max-width:' . esc_attr((string) self::TABLET_MAX) . 'px){' . $tablet . $pageSpacing['tablet'] . '}';
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 desktop/tablet spacing output anchor mismatch')
rr = rr.replace(old, new, 1)
old = """            . $v1MobileVisual
            . $v1MobileEdgeSpacing
            . $v1NestedMobileEdgeParity . '}';
"""
new = """            . $v1MobileVisual
            . $v1MobileEdgeSpacing
            . $v1NestedMobileEdgeParity
            . $pageSpacing['mobile'] . '}';
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 mobile spacing output anchor mismatch')
rr = rr.replace(old, new, 1)
anchor = """    /**
     * Emit the same responsive geometry contract for one rendered model.
"""
helper = r'''    /** @param array<string,mixed> $model @return array{desktop:string,laptop:string,tablet:string,mobile:string} */
    private static function pageSpacingCss(array $model, string $pageSelector, bool $hasFooter): array
    {
        $raw = isset($model['pageSettings']) && is_array($model['pageSettings']) ? $model['pageSettings'] : [];
        $defaults = [
            'sectionGap' => ['desktop'=>32,'laptop'=>32,'tablet'=>24,'mobile'=>24],
            'elementGap' => ['desktop'=>16,'laptop'=>16,'tablet'=>14,'mobile'=>14],
            'footerGap' => ['desktop'=>32,'laptop'=>32,'tablet'=>24,'mobile'=>24],
        ];
        $value = static function (string $key, string $device) use ($raw, $defaults): int {
            $fallback = (int) $defaults[$key][$device];
            $candidate = isset($raw[$key][$device]) ? (int) $raw[$key][$device] : $fallback;
            return max(0, min(200, $candidate));
        };
        $out = [];
        foreach (['desktop','laptop','tablet','mobile'] as $device) {
            $footer = $hasFooter ? $value('footerGap', $device) : 0;
            $out[$device] = $pageSelector . '{--h18-vdm-page-section-gap:' . $value('sectionGap',$device) . 'px;--h18-vdm-page-element-gap:' . $value('elementGap',$device) . 'px;--h18-vdm-page-footer-gap:' . $footer . 'px;margin-bottom:' . $footer . 'px!important;}';
        }
        return $out;
    }

'''
if rr.count(anchor) != 1:
    raise SystemExit('Alpha.23 pageSpacingCss helper anchor mismatch')
rr = rr.replace(anchor, helper + anchor, 1)

# Alpha.18/19 hard-coded mobile gaps become page settings.
old = "$gap = $visible === 0 ? 0 : (($feature && $previousFeature) ? 14 : 24);"
new = "$gap = $visible === 0 ? '0px' : (($feature && $previousFeature) ? 'var(--h18-vdm-page-element-gap,14px)' : 'var(--h18-vdm-page-section-gap,24px)');"
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 root gap anchor mismatch')
rr = rr.replace(old, new, 1)
old = "'{margin-top:' . $gap . 'px!important;margin-bottom:0!important;}'"
new = "'{margin-top:' . $gap . '!important;margin-bottom:0!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 root gap unit anchor mismatch')
rr = rr.replace(old, new, 1)
for old, new, label in [
    ('margin-top:24px!important;margin-bottom:0!important;padding:13px 18px!important', 'margin-top:var(--h18-vdm-page-section-gap,24px)!important;margin-bottom:0!important;padding:13px 18px!important', 'tagline gap'),
    ('margin-top:24px!important;margin-bottom:0!important;padding-left:18px!important', 'margin-top:var(--h18-vdm-page-section-gap,24px)!important;margin-bottom:0!important;padding-left:18px!important', 'major gap'),
    ('margin-top:14px!important;margin-bottom:0!important;', 'margin-top:var(--h18-vdm-page-element-gap,14px)!important;margin-bottom:0!important;', 'feature gap'),
]:
    if rr.count(old) != 1:
        raise SystemExit(f'Alpha.23 {label} anchor mismatch: {rr.count(old)}')
    rr = rr.replace(old, new, 1)

# Hero/tagline structural wrappers contributed extra vertical padding. Clear it
# and let the page's sectionGap be the one authoritative gap.
old = "$css .= $selector . '{width:100%!important;max-width:100%!important;margin-top:0!important;margin-bottom:0!important;padding-left:0!important;padding-right:0!important;overflow:visible!important;}';"
new = "$css .= $selector . '{width:100%!important;max-width:100%!important;margin-top:0!important;margin-bottom:0!important;padding:0!important;overflow:visible!important;}';"
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 hero/tagline wrapper padding anchor mismatch')
rr = rr.replace(old, new, 1)

# V1 screenshot parity: phone hero is full bleed and compact, not the 220px
# Alpha.16 interim height. 160px matches the retained V1 phone composition.
old = "$selector . '{width:100vw!important;max-width:100vw!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;margin-top:0!important;margin-bottom:0!important;padding:0!important;border-radius:0!important;overflow:hidden!important;}'"
new = "$selector . '{width:100vw!important;max-width:100vw!important;height:160px!important;min-height:160px!important;margin-left:calc(50% - 50vw)!important;margin-right:calc(50% - 50vw)!important;margin-top:0!important;margin-bottom:0!important;padding:0!important;border-radius:0!important;overflow:hidden!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 hero node anchor mismatch')
rr = rr.replace(old, new, 1)
old = "$selector . ' .h18-clean-front-image{width:100%!important;max-width:100%!important;margin:0!important;padding:0!important;border-radius:0!important;}'"
new = "$selector . ' .h18-clean-front-image{width:100%!important;max-width:100%!important;height:160px!important;min-height:160px!important;margin:0!important;padding:0!important;border-radius:0!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 hero inner anchor mismatch')
rr = rr.replace(old, new, 1)
old = 'height:220px!important;object-fit:cover!important;border-radius:0!important;'
new = 'height:160px!important;object-fit:cover!important;border-radius:0!important;'
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 nested hero image height anchor mismatch')
rr = rr.replace(old, new, 1)

# V1 phone Header geometry: logo + two-line brand + hamburger in one compact row.
old = """        $css = $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section,' . $scope . '.h18-clean-front-container{display:flex!important;flex-direction:row!important;align-items:center!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-surface{padding:0!important;}'
            . $scope . '.h18-clean-front-section{padding:0!important;margin:0!important;}'
            . $scope . '.h18-clean-front-container{padding:12px 12px!important;margin:0!important;gap:10px!important;}'
"""
new = """        $css = $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section{display:block!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-surface{padding:0!important;}'
            . $scope . '.h18-clean-front-section{padding:0!important;margin:0!important;}'
            . $scope . '.h18-clean-front-container{display:grid!important;grid-template-columns:64px minmax(0,1fr) 48px!important;align-items:center!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;padding:12px 12px!important;margin:0!important;column-gap:10px!important;overflow:visible!important;box-sizing:border-box!important;}'
"""
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 mobile Header grid anchor mismatch')
rr = rr.replace(old, new, 1)
old = "$selector . '{order:10!important;flex:0 0 clamp(48px,15vw,60px)!important;width:clamp(48px,15vw,60px)!important;max-width:60px!important;height:clamp(48px,15vw,60px)!important;}'"
new = "$selector . '{grid-column:1!important;grid-row:1!important;width:64px!important;max-width:64px!important;height:64px!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 Header logo anchor mismatch')
rr = rr.replace(old, new, 1)
old = "$selector . '{order:20!important;flex:1 1 auto!important;width:auto!important;max-width:none!important;height:auto!important;padding:0!important;background:transparent!important;color:#f2f0e8!important;font-size:' . rtrim(rtrim(number_format($font, 1, '.', ''), '0'), '.') . 'px!important;font-weight:700!important;line-height:1.16!important;text-align:left!important;overflow-wrap:normal!important;word-break:normal!important;}'"
new = "$selector . '{grid-column:2!important;grid-row:1!important;width:100%!important;max-width:none!important;height:auto!important;padding:0!important;background:transparent!important;color:#f2f0e8!important;font-size:16px!important;font-weight:700!important;line-height:1.16!important;text-align:left!important;overflow-wrap:normal!important;word-break:normal!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 Header brand anchor mismatch')
rr = rr.replace(old, new, 1)
old = "$selector . '{order:30!important;flex:0 0 48px!important;width:48px!important;max-width:48px!important;height:48px!important;margin-left:auto!important;padding:0!important;background:transparent!important;}'\n                    . $selector . ' .h18-clean-front-menu-summary{width:48px!important;height:48px!important;}'"
new = "$selector . '{grid-column:3!important;grid-row:1!important;width:48px!important;max-width:48px!important;height:48px!important;margin:0!important;padding:0!important;background:transparent!important;justify-self:end!important;}'\n                    . $selector . ' .h18-clean-front-menu-toggle{width:48px!important;height:48px!important;}'"
if rr.count(old) != 1:
    raise SystemExit('Alpha.23 Header menu anchor mismatch')
rr = rr.replace(old, new, 1)
write('src/Frontend/ResponsiveRenderer.php', rr)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.22':
    raise SystemExit('Expected Alpha.22 release-history baseline missing')
rows.insert(0, {
    'version': VERSION,
    'date': '2026-09-07',
    'items': [
        'V1 mobilrytme: Header bruger kompakt trekolonne-layout, hero er full-bleed i V1-højde, og tagline/sektioner bruger én kontrolleret responsive afstand.',
        'Sider → Sideindstillinger → Afstande styrer Afstand mellem sektioner, Standard afstand mellem elementer og Afstand til Footer separat for Desktop/Laptop/Tablet/Mobil.',
        'Sideafstande gemmes i den enkelte sides canonical model og versionshistorik; V1-lignende standarder er 32/24 px sektion/footer og 16/14 px elementafstand.',
        'Alpha.22 Website-menu og desktop/mobil-menu-rendering bevares.'
    ]
})
history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

# Contract checks.
for rel, tokens in {
    'visual-designer-manager.php': ['Version: 3.0.0-alpha.23'],
    'src/Model/LayoutModel.php': ["'pageSettings' => self::pageSettings", "'sectionGap' =>", "'footerGap' =>"],
    'src/Admin/EditorController.php': ['Sideindstillinger · Afstande', 'data-page-spacing-key', 'Afstand til Footer'],
    'assets/editor-v018-core.js': ['function normalizePageSettings(', 'pageSettings: normalizePageSettings(raw.pageSettings)', 'data-page-spacing-device'],
    'src/Frontend/ResponsiveRenderer.php': ['private static function pageSpacingCss(', '--h18-vdm-page-section-gap:', '--h18-vdm-page-footer-gap:', 'grid-template-columns:64px minmax(0,1fr) 48px', 'height:160px!important', '.h18-clean-front-menu-toggle'],
}.items():
    value = read(rel)
    for token in tokens:
        if token not in value:
            raise SystemExit(f'Alpha.23 contract token missing in {rel}: {token}')

print('V3 Alpha.23 V1 mobile rhythm + per-page spacing controls: PASS')
