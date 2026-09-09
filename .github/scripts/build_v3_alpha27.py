from pathlib import Path
import json
import subprocess

VERSION='3.0.0-alpha.27'
DEST=Path('build/visual-designer-manager')

subprocess.run(['python3','.github/scripts/build_v3_alpha26.py'],check=True)

def read(rel): return (DEST/rel).read_text(encoding='utf-8')
def write(rel,s):
    p=DEST/rel
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(s,encoding='utf-8')

main=read('visual-designer-manager.php')
for old,new in [
    (' * Version: 3.0.0-alpha.26',' * Version: 3.0.0-alpha.27'),
    ("define('VDM_VERSION', '3.0.0-alpha.26');","define('VDM_VERSION', '3.0.0-alpha.27');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.26');","define('H18_CLEAN_VERSION', '3.0.0-alpha.27');"),
]:
    if main.count(old)!=1: raise SystemExit(f'version anchor {old}: {main.count(old)}')
    main=main.replace(old,new,1)
req="require_once VDM_DIR . 'src/Migration/V1MobileGeometryRecovery.php';\n"
if main.count(req)!=1: raise SystemExit('require anchor')
main=main.replace(req,req+"require_once VDM_DIR . 'src/Migration/ResponsivePaintUnifier.php';\n",1)
reg="    \\VisualDesignerManager\\Migration\\V1MobileGeometryRecovery::register();\n"
if main.count(reg)!=1: raise SystemExit('register anchor')
main=main.replace(reg,reg+"    \\VisualDesignerManager\\Migration\\ResponsivePaintUnifier::register();\n",1)
write('visual-designer-manager.php',main)

migration=r'''<?php

declare(strict_types=1);

namespace VisualDesignerManager\Migration;

use VisualDesignerManager\Model\LayoutModel;

final class ResponsivePaintUnifier
{
    private const VERSION = '3.0.0-alpha.27';
    private const DONE_META = '_vdm_alpha27_responsive_paint_unified_v1';
    private const BACKUP_META = '_vdm_alpha27_responsive_paint_backup_v1';
    private const LEGACY_META = '_h18_clean_layout_v1';
    private const OLIVE = '#30382a';
    private const SAND = '#c3ae83';

    public static function register(): void
    {
        add_action('init', [self::class, 'run'], 7);
    }

    public static function run(): void
    {
        global $wpdb;
        $postIds = $wpdb->get_col($wpdb->prepare(
            "SELECT DISTINCT post_id FROM {$wpdb->postmeta} WHERE meta_key = %s ORDER BY post_id",
            self::LEGACY_META
        ));
        foreach ((array) $postIds as $postIdRaw) {
            $postId = (int) $postIdRaw;
            if ($postId <= 0 || get_post_type($postId) !== 'page') { continue; }
            if ((string) get_post_meta($postId, self::DONE_META, true) === self::VERSION) { continue; }
            if (!metadata_exists('post', $postId, LayoutModel::META)) { continue; }
            $before = LayoutModel::get($postId);
            $after = self::unifyModel($before);
            if (LayoutModel::structuralDigest($after) !== LayoutModel::structuralDigest($before)) {
                if (!metadata_exists('post', $postId, self::BACKUP_META)) {
                    add_post_meta($postId, self::BACKUP_META, [
                        'version' => self::VERSION,
                        'savedUtc' => gmdate('c'),
                        'model' => $before,
                    ], true);
                }
                LayoutModel::saveVersion($postId, $after, 0, 'Alpha.27: fælles responsive farver og kasser');
            }
            update_post_meta($postId, self::DONE_META, self::VERSION);
        }
    }

    /** @param array<string,mixed> $model @return array<string,mixed> */
    public static function unifyModel(array $model): array
    {
        $nodes = isset($model['nodes']) && is_array($model['nodes']) ? $model['nodes'] : [];
        $byId = [];
        foreach ($nodes as $index => $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $byId[(string) $node['id']] = $index;
        }

        $taglineId = '';
        $heroId = '';
        $heroY = PHP_INT_MAX;
        foreach ($nodes as $node) {
            if (!is_array($node) || empty($node['id'])) { continue; }
            $id = (string) $node['id'];
            $type = (string) ($node['type'] ?? '');
            $props = is_array($node['props'] ?? null) ? $node['props'] : [];
            $heading = strtolower(trim(wp_strip_all_tags((string) ($props['heading'] ?? ''))));
            $text = strtolower(trim(wp_strip_all_tags((string) ($props['text'] ?? ''))));
            $hay = $heading . ' ' . $text;
            if ($type === 'text' && str_contains($hay, 'bevaring, restaurering og levende') && str_contains($hay, 'militærhistorie')) {
                $taglineId = $id;
            }
            if ($type === 'image') {
                $geometry = isset($node['geometry']['desktop']) && is_array($node['geometry']['desktop']) ? $node['geometry']['desktop'] : [];
                $w = (int) ($geometry['w'] ?? 0);
                $y = (int) ($geometry['y'] ?? PHP_INT_MAX);
                if ($w >= 100 && $y < $heroY) { $heroId = $id; $heroY = $y; }
            }
        }

        $nearestSection = static function (string $id) use (&$nodes, $byId): string {
            $guard = 0;
            $current = $id;
            while ($current !== '' && isset($byId[$current]) && $guard++ < 32) {
                $node = $nodes[$byId[$current]];
                $parent = (string) ($node['parentId'] ?? '');
                if ($parent === '' || !isset($byId[$parent])) { return ''; }
                $parentNode = $nodes[$byId[$parent]];
                if ((string) ($parentNode['type'] ?? '') === 'section') { return $parent; }
                $current = $parent;
            }
            return '';
        };

        $paintSection = static function (string $id, string $color) use (&$nodes, $byId): void {
            if ($id === '' || !isset($byId[$id])) { return; }
            $index = $byId[$id];
            $props = is_array($nodes[$index]['props'] ?? null) ? $nodes[$index]['props'] : [];
            $props['background'] = $color;
            $props['backgroundTransparent'] = false;
            $nodes[$index]['props'] = $props;
        };

        $heroSection = $taglineId !== '' ? $nearestSection($heroId) : '';
        $taglineSection = $nearestSection($taglineId);
        if ($taglineId !== '') {
            $paintSection($heroSection, self::OLIVE);
            $paintSection($taglineSection, self::SAND);
        }

        if ($taglineId !== '' && isset($byId[$taglineId])) {
            $index = $byId[$taglineId];
            $props = is_array($nodes[$index]['props'] ?? null) ? $nodes[$index]['props'] : [];
            $props['background'] = self::SAND;
            $props['backgroundTransparent'] = true;
            $props['textColor'] = self::OLIVE;
            $props['headingColor'] = self::OLIVE;
            $nodes[$index]['props'] = $props;
        }

        $model['nodes'] = $nodes;
        return $model;
    }

    private function __construct() {}
}
'''
write('src/Migration/ResponsivePaintUnifier.php',migration)

rr=read('src/Frontend/ResponsiveRenderer.php')
old="""        // Paint (background/text/border/radius) comes from the retained V1
        // model where a node id/type still matches. Geometry remains V3/Alpha.15.
        $css .= self::v1PaintCss($pageModel, $legacyPageModel, $pageScope);

"""
new="""        // Paint is owned by the canonical model for every breakpoint.
        // Alpha.27 removes the old mobile-only V1 paint layer so Designer color,
        // border and box edits render identically on desktop and mobile.

"""
if rr.count(old)!=1: raise SystemExit(f'page paint anchor {rr.count(old)}')
rr=rr.replace(old,new,1)
old="""                $css .= $selector . '{background:#c3ae83!important;color:#30382a!important;text-align:center!important;padding:12px 15px!important;border-radius:0!important;width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;font-family:\"Inter\",Arial,sans-serif!important;font-size:16px!important;font-weight:650!important;line-height:1.35!important;}'
                    . $selector . ' .h18-clean-front-text-heading{color:#30382a!important;}';
"""
new="""                $css .= $selector . '{text-align:center!important;padding:12px 15px!important;border-radius:0!important;width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;font-family:\"Inter\",Arial,sans-serif!important;font-size:16px!important;font-weight:650!important;line-height:1.35!important;}';
"""
if rr.count(old)!=1: raise SystemExit(f'tagline mobile paint anchor {rr.count(old)}')
rr=rr.replace(old,new,1)
old="        foreach ([$legacy, $model] as $candidate) {\n"
new="""        // Canonical Designer paint wins. Legacy is fallback only for templates
        // that have not yet stored an explicit surface color.
        foreach ([$model, $legacy] as $candidate) {
"""
if rr.count(old)!=1: raise SystemExit(f'template source order {rr.count(old)}')
rr=rr.replace(old,new,1)
old="        if ($legacy !== null) { $css .= self::v1PaintCss($model, $legacy, $scope); }\n\n"
if rr.count(old)!=2: raise SystemExit(f'header/footer paint anchors {rr.count(old)}')
rr=rr.replace(old,"",2)
old="""            $css .= $selector . '{width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;margin-top:var(--h18-vdm-page-section-gap,24px)!important;margin-bottom:0!important;padding:12px 15px!important;border-radius:0!important;background:#c3ae83!important;color:#30382a!important;font-family:\"Inter\",Arial,sans-serif!important;font-size:16px!important;font-weight:650!important;line-height:1.35!important;text-align:center!important;box-sizing:border-box!important;}';
"""
new="""            $css .= $selector . '{width:100%!important;max-width:100%!important;margin-left:0!important;margin-right:0!important;margin-top:var(--h18-vdm-page-section-gap,24px)!important;margin-bottom:0!important;padding:12px 15px!important;border-radius:0!important;font-family:\"Inter\",Arial,sans-serif!important;font-size:16px!important;font-weight:650!important;line-height:1.35!important;text-align:center!important;box-sizing:border-box!important;}';
"""
if rr.count(old)!=1: raise SystemExit(f'nested tagline paint anchor {rr.count(old)}')
rr=rr.replace(old,new,1)
write('src/Frontend/ResponsiveRenderer.php',rr)

vc=read('src/Migration/VisualBlockConversionService.php')
old="""        $sectionId = 'section-hero-' . $suffix . '-' . $order;
        $nodes[] = self::sectionNode($sectionId, $order, $desktopY, $mobileY, $desktopH, $mobileH, '#ffffff');
"""
new="""        $sectionId = 'section-hero-' . $suffix . '-' . $order;
        // Shared paint source: exposed hero separator is canonical olive on all breakpoints.
        $nodes[] = self::sectionNode($sectionId, $order, $desktopY, $mobileY, $desktopH, $mobileH, self::OLIVE);
"""
if vc.count(old)!=1: raise SystemExit(f'hero conversion anchor {vc.count(old)}')
vc=vc.replace(old,new,1)
write('src/Migration/VisualBlockConversionService.php',vc)

hp=DEST/'release-history.json'
h=json.loads(hp.read_text(encoding='utf-8'))
rows=h.get('versions',[]) if isinstance(h,dict) else []
if not isinstance(rows,list) or not rows or rows[0].get('version')!='3.0.0-alpha.26': raise SystemExit('history baseline')
rows.insert(0,{
    'version':VERSION,
    'date':'2026-09-09',
    'items':[
        'Responsive Paint Unification: farver, baggrunde, kanter og kasser ejes igen af den kanoniske Designer-model i stedet for separate mobil-overrides.',
        'Engangs paint-migrering retter Hjems hero-sektion til mørk oliven og tagline-sektion til sand i selve modellen; geometri, hierarki og tekst ændres ikke.',
        'Mobilens gamle v1PaintCss-lag fjernes fra side, Header og Footer, så senere Designer-farveændringer vises ens på desktop, laptop, tablet og mobil.',
        'Template-baggrund læser nu den kanoniske model først og bruger legacy kun som fallback.',
        'Fremtidige V1-konverteringer opretter hero-båndets eksponerede separator i oliven direkte i modellen; tagline forbliver sand.',
        'Alpha.26 Header/Footer parity, dynamiske Footer-genveje og Alpha.25 natural-flow bevares.'
    ]
})
hp.write_text(json.dumps({'versions':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

main=read('visual-designer-manager.php')
rr=read('src/Frontend/ResponsiveRenderer.php')
vc=read('src/Migration/VisualBlockConversionService.php')
mig=read('src/Migration/ResponsivePaintUnifier.php')
history=read('release-history.json')
for token in ['Version: 3.0.0-alpha.27',"define('VDM_VERSION', '3.0.0-alpha.27');",'ResponsivePaintUnifier.php','ResponsivePaintUnifier::register()']:
    if token not in main: raise SystemExit(f'main token {token}')
for token in ["foreach ([$model, $legacy] as $candidate)",'Paint is owned by the canonical model for every breakpoint.']:
    if token not in rr: raise SystemExit(f'responsive token {token}')
if 'self::v1PaintCss($pageModel, $legacyPageModel, $pageScope)' in rr: raise SystemExit('page legacy paint remains')
if 'if ($legacy !== null) { $css .= self::v1PaintCss($model, $legacy, $scope); }' in rr: raise SystemExit('template legacy paint remains')
for token in ["private const OLIVE = '#30382a';","private const SAND = '#c3ae83';",'Alpha.27: fælles responsive farver og kasser',"$props['backgroundTransparent'] = true;"]:
    if token not in mig: raise SystemExit(f'migration token {token}')
if "self::sectionNode($sectionId, $order, $desktopY, $mobileY, $desktopH, $mobileH, self::OLIVE)" not in vc: raise SystemExit('future hero paint')
if '3.0.0-alpha.27' not in history: raise SystemExit('history token')
print('PASS')
