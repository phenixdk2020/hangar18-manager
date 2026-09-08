from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.25'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha24.py'], check=True)

def read(rel: str) -> str:
    return (DEST / rel).read_text(encoding='utf-8')
def write(rel: str, s: str) -> None:
    path = DEST / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(s, encoding='utf-8')
main=read('visual-designer-manager.php')
for old,new in [
(' * Version: 3.0.0-alpha.24',f' * Version: {VERSION}'),
("define('VDM_VERSION', '3.0.0-alpha.24');",f"define('VDM_VERSION', '{VERSION}');"),
("define('H18_CLEAN_VERSION', '3.0.0-alpha.24');",f"define('H18_CLEAN_VERSION', '{VERSION}');"),]:
    if main.count(old)!=1: raise SystemExit(f'version {old}: {main.count(old)}')
    main=main.replace(old,new,1)
anchor="""add_action('plugins_loaded', static function (): void {
"""
insert="""add_action('wp_head', static function (): void {
    if (is_admin()) { return; }
    echo '<meta name="theme-color" content="#30382a">' . "\\n";
}, 2000);

"""
if main.count(anchor)!=1: raise SystemExit('main hook anchor')
main=main.replace(anchor,insert+anchor,1)
write('visual-designer-manager.php',main)

rr=read('src/Frontend/ResponsiveRenderer.php')
old="""        $css = $surface . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;gap:0!important;}'
            . $section . ',' . $container . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;padding:0!important;gap:var(--h18-vdm-page-element-gap,14px)!important;}'
"""
new="""        $css = $surface . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;gap:0!important;grid-template-rows:none!important;grid-auto-rows:auto!important;}'
            . $section . ',' . $container . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;padding:0!important;gap:var(--h18-vdm-page-element-gap,14px)!important;grid-template-columns:1fr!important;grid-template-rows:none!important;grid-auto-rows:auto!important;}'
"""
if rr.count(old)!=1: raise SystemExit(f'flow class {rr.count(old)}')
rr=rr.replace(old,new,1)
old=". $scope . '.h18-clean-front-spacer{height:24px!important;min-height:24px!important;flex:0 0 24px!important;}';"
new=". $scope . '.h18-clean-front-spacer{display:none!important;height:0!important;min-height:0!important;flex:0 0 0!important;margin:0!important;padding:0!important;}';"
if rr.count(old)!=1: raise SystemExit(f'spacer {rr.count(old)}')
rr=rr.replace(old,new,1)
old="""                if (!in_array($type, ['image', 'eventimage', 'spacer'], true)) {
                    $css .= $selector . '{min-height:0!important;}';
                }
"""
new="""                if (!in_array($type, ['image', 'eventimage', 'spacer'], true)) {
                    $css .= $selector . '{height:auto!important;min-height:0!important;}';
                }
                if (in_array($type, ['section', 'container'], true)) {
                    $css .= $selector . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;grid-template-columns:1fr!important;grid-template-rows:none!important;grid-auto-rows:auto!important;height:auto!important;min-height:0!important;padding:0!important;gap:var(--h18-vdm-page-element-gap,14px)!important;overflow:visible!important;}';
                }
"""
if rr.count(old)!=1: raise SystemExit(f'per id natural {rr.count(old)}')
rr=rr.replace(old,new,1)
old="""        $css = $scope . '.h18-clean-front-surface,' . $scope . '.h18-clean-front-section{display:block!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;overflow:visible!important;box-sizing:border-box!important;grid-auto-rows:auto!important;grid-template-rows:none!important;}'
            . $scope . '.h18-clean-front-surface{padding:0!important;}'
            . $scope . '.h18-clean-front-section{padding:0!important;margin:0!important;}'
            . $scope . '.h18-clean-front-container{display:grid!important;grid-template-columns:70px minmax(0,1fr) 44px!important;grid-template-rows:auto!important;grid-auto-rows:auto!important;align-items:center!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;padding:7px 11px!important;margin:0!important;column-gap:10px!important;overflow:visible!important;box-sizing:border-box!important;}'
            . $scope . '.h18-clean-front-node{grid-column:auto!important;grid-row:auto!important;position:relative!important;left:auto!important;right:auto!important;top:auto!important;transform:none!important;margin:0!important;height:auto!important;min-height:0!important;box-sizing:border-box!important;}';
"""
new="""        $css = $scope . '.h18-clean-front-surface{display:flex!important;flex-direction:row!important;align-items:center!important;width:100%!important;max-width:100%!important;height:auto!important;min-height:0!important;padding:7px 11px!important;margin:0!important;gap:10px!important;overflow:visible!important;box-sizing:border-box!important;grid-template-columns:none!important;grid-template-rows:none!important;grid-auto-rows:auto!important;}'
            . $scope . '.h18-clean-front-section,' . $scope . '.h18-clean-front-container{display:contents!important;width:auto!important;max-width:none!important;height:auto!important;min-height:0!important;padding:0!important;margin:0!important;}'
            . $scope . '.h18-clean-front-node{grid-column:auto!important;grid-row:auto!important;position:relative!important;left:auto!important;right:auto!important;top:auto!important;transform:none!important;margin:0!important;height:auto!important;min-height:0!important;box-sizing:border-box!important;}';
"""
if rr.count(old)!=1: raise SystemExit(f'header base {rr.count(old)}')
rr=rr.replace(old,new,1)
old="""            if (in_array($type, ['section','container'], true)) {
                $css .= $selector . '{grid-auto-rows:auto!important;grid-template-rows:none!important;padding:0!important;}';
            }
"""
new="""            if (in_array($type, ['section','container'], true)) {
                $css .= $selector . '{display:contents!important;grid-template-columns:none!important;grid-auto-rows:auto!important;grid-template-rows:none!important;width:auto!important;max-width:none!important;height:auto!important;min-height:0!important;padding:0!important;margin:0!important;}';
            }
"""
if rr.count(old)!=1: raise SystemExit(f'header id wrappers {rr.count(old)}')
rr=rr.replace(old,new,1)
old="$css .= $selector . '{grid-column:1!important;grid-row:1!important;width:70px!important;max-width:70px!important;height:auto!important;}'"
new="$css .= $selector . '{flex:0 0 70px!important;width:70px!important;max-width:70px!important;height:auto!important;align-self:center!important;}'"
if rr.count(old)!=1: raise SystemExit(f'header image rule {rr.count(old)}')
rr=rr.replace(old,new,1)
old="$css .= $selector . '{grid-column:2!important;grid-row:1!important;width:100%!important;max-width:none!important;height:auto!important;padding:0!important;background:transparent!important;color:#f2f0e8!important;"
new="$css .= $selector . '{flex:1 1 0!important;width:auto!important;min-width:0!important;max-width:none!important;height:auto!important;padding:0!important;background:transparent!important;color:#f2f0e8!important;"
if rr.count(old)!=1: raise SystemExit(f'header text rule {rr.count(old)}')
rr=rr.replace(old,new,1)
old="$css .= $selector . '{grid-column:3!important;grid-row:1!important;width:44px!important;max-width:44px!important;height:44px!important;margin:0!important;padding:0!important;background:transparent!important;justify-self:end!important;}'"
new="$css .= $selector . '{flex:0 0 44px!important;width:44px!important;max-width:44px!important;height:44px!important;margin:0 0 0 auto!important;padding:0!important;background:transparent!important;align-self:center!important;}'"
if rr.count(old)!=1: raise SystemExit(f'header menu rule {rr.count(old)}')
rr=rr.replace(old,new,1)
old="$css .= $selector . '{display:flex!important;flex-direction:column!important;grid-auto-rows:auto!important;grid-template-rows:none!important;padding:0!important;}';"
new="$css .= $selector . '{display:flex!important;flex-direction:column!important;align-items:stretch!important;grid-template-columns:1fr!important;grid-auto-rows:auto!important;grid-template-rows:none!important;height:auto!important;min-height:0!important;padding:0!important;}';"
if rr.count(old)!=1: raise SystemExit(f'footer wrapper reset {rr.count(old)}')
rr=rr.replace(old,new,1)
write('src/Frontend/ResponsiveRenderer.php',rr)

hp=DEST/'release-history.json'; h=json.loads(hp.read_text(encoding='utf-8')); rows=h['versions']
if not rows or rows[0].get('version')!='3.0.0-alpha.24': raise SystemExit('history baseline')
rows.insert(0,{'version':VERSION,'date':'2026-09-08','items':[
'Mobile Natural Flow Reset: alle V1-konverterede Section/Container-ID’er nulstiller desktop-grid, grid-rækker, faste/minimumshøjder og bruger naturligt flex-column-flow på telefon.',
'Headerens nested wrappers flades ud med display:contents, mens Header-surface ejer én flex-række med vertikal centrering af 70 px logo, titel og 44 px hamburger.',
'Spacers er ikke længere en skjult ekstra spacing-kilde på mobil; side-/sektion-/element-/footer-afstande er fortsat de autoritative Designer-indstillinger.',
'Footerens Section/Container-ID’er nulstiller også grid-template-columns/rows og faste højder på mobil.',
'iPhone/browser theme-color sættes til Hangar18 mørkegrøn #30382a, så browser/status-området følger V1-referencefarven.',
'Alpha.24 V1 referencepadding, hero/tagline, single-surface feature cards og Alpha.22 Website-menu bevares.'
]})
hp.write_text(json.dumps({'versions':rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

for rel,toks in {
'visual-designer-manager.php':['Version: 3.0.0-alpha.25','<meta name="theme-color" content="#30382a">'],
'src/Frontend/ResponsiveRenderer.php':['display:contents!important','flex:0 0 70px!important','flex:1 1 0!important','grid-template-columns:1fr!important;grid-template-rows:none!important;grid-auto-rows:auto!important','display:none!important;height:0!important;min-height:0!important;flex:0 0 0!important'],
'release-history.json':['3.0.0-alpha.25']}.items():
    s=read(rel)
    for t in toks:
        if t not in s: raise SystemExit(f'missing {rel} {t}')
print('PASS')
