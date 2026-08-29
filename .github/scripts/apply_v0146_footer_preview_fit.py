from pathlib import Path
import json

ROOT = Path('.')

def read(path):
    return (ROOT / path).read_text(encoding='utf-8')

def write(path, text):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')

def replace_once(text, old, new, label):
    if old not in text:
        raise SystemExit(f'Missing anchor: {label}')
    return text.replace(old, new, 1)

# Version ---------------------------------------------------------------------
path='clean/hangar18-manager/hangar18-manager.php'
s=read(path)
s=replace_once(s,' * Version: 0.1.45',' * Version: 0.1.46','version header')
s=replace_once(s,"define('H18_CLEAN_VERSION', '0.1.45');","define('H18_CLEAN_VERSION', '0.1.46');",'version constant')
write(path,s)

# BUG-16 Footer Desktop reference fallback ------------------------------------
path='clean/hangar18-manager/src/Migration/LegacyFooterConverter.php'
s=read(path)
s=replace_once(s,"h18_vd_legacy_footer_converted_v0143","h18_vd_legacy_footer_converted_v0146",'migration option')
s=replace_once(s,"h18_vd_legacy_footer_status_v0143","h18_vd_legacy_footer_status_v0146",'status option')
s=replace_once(s,"""        if ($fallbackUsed) {
            $model=self::buildReferenceFooterModel($design);
            $kind='legacy-manager-standard-fallback';
            $note='Standardfallback fra gammel Manager · v0.1.45 · ikke 1:1-kilde';
        } else {
""","""        if ($fallbackUsed) {
            $model=self::buildDesktopReferenceFooterModel($design,self::referenceFooterLinks());
            $kind='desktop-reference-2026-08-29';
            $note='Footer-reference fra godkendt Desktop-screenshot · v0.1.46';
        } else {
""",'fallback convert')
s=replace_once(s,"'sourceKind'=>'legacy-manager-standard-fallback',","'sourceKind'=>'desktop-reference-2026-08-29',",'empty source kind')
old="""    /** @param array<string,mixed> $design */
    public static function buildReferenceFooterModel(array $design=[]): array {
        $pct=self::footerWidth($design); if ($pct>=100) $pct=90; [$x,$w]=self::centredUnits($pct);
        return self::model($x,$w,12,self::color($design['PrimaryColor']??'#30382a','#30382a'),self::color($design['LightTextColor']??'#f2f0e8','#f2f0e8'),'Aalborg Kaserners Veteran Panser- og Køretøjsforening');
    }
"""
new=r'''    /**
     * Deterministic no-legacy fallback based on the real Desktop Footer
     * reference supplied 2026-08-29. It is a visual reconstruction, not a
     * claim that the historical source was recovered.
     *
     * @param array<string,mixed> $design
     * @param array<string,string> $links
     */
    public static function buildDesktopReferenceFooterModel(array $design=[],array $links=[]): array {
        $pct=self::footerWidth($design); if ($pct>=100) $pct=90; [$x,$w]=self::centredUnits($pct);
        $bg=self::color($design['PrimaryColor']??'#30382a','#30382a');
        $fg=self::color($design['LightTextColor']??'#f2f0e8','#f2f0e8');
        $accent=self::color($design['AccentColor']??'#c3ae83','#c3ae83');
        $rows=40;
        $nodes=[
            self::node('section-footer-reference-v0146','section','',10,self::geometry([$x,0,$w,$rows],[3,0,114,44],[0,0,120,82]),['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('container-footer-reference-v0146','container','section-footer-reference-v0146',10,self::geometry([0,0,120,$rows],[0,0,120,44],[0,0,120,82]),['background'=>$bg,'radius'=>0,'padding'=>0,'minHeightRows'=>$rows,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-brand-v0146','text','container-footer-reference-v0146',20,self::geometry([2,5,42,4],[2,5,42,5],[4,4,112,5]),['heading'=>'','headingLevel'=>'h2','text'=>'Aalborg Kaserners Veteran Panser- og Køretøjsforening','align'=>'left','verticalAlign'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>18,'fontWeight'=>700,'lineHeight'=>1.25,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-description-v0146','text','container-footer-reference-v0146',30,self::geometry([2,10,36,7],[2,11,40,8],[4,10,112,10]),['heading'=>'','headingLevel'=>'h2','text'=>'Bevaring, restaurering og levende formidling af militærhistorisk materiel med særlig tilknytning til Aalborg Kaserner.','align'=>'left','verticalAlign'=>'top','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>400,'lineHeight'=>1.45,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-shortcuts-heading-v0146','text','container-footer-reference-v0146',40,self::geometry([49,5,18,3],[47,5,20,3],[4,23,112,3]),['heading'=>'','headingLevel'=>'h2','text'=>'Genveje','align'=>'left','verticalAlign'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$accent,'headingColor'=>$accent,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>600,'lineHeight'=>1.2,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-shortcuts-v0146','text','container-footer-reference-v0146',50,self::geometry([49,9,20,18],[47,9,22,19],[4,27,112,18]),['heading'=>'','headingLevel'=>'h2','text'=>self::referenceShortcutHtml($links),'align'=>'left','verticalAlign'=>'top','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>400,'lineHeight'=>2.05,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-association-heading-v0146','text','container-footer-reference-v0146',60,self::geometry([84,5,32,3],[80,5,38,3],[4,48,112,3]),['heading'=>'','headingLevel'=>'h2','text'=>'Foreningen','align'=>'left','verticalAlign'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$accent,'headingColor'=>$accent,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>14,'fontWeight'=>600,'lineHeight'=>1.2,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
            self::node('button-footer-join-v0146','button','container-footer-reference-v0146',70,self::geometry([84,8,32,6],[80,8,38,6],[4,52,112,6]),['text'=>'Bliv medlem','linkType'=>'url','url'=>self::referenceLink($links,'join','/bliv-medlem/'),'targetBlank'=>false,'autoSize'=>false,'placementMode'=>'normal','zIndex'=>20,'background'=>$accent,'textColor'=>'#1d2327','hoverBackground'=>$accent,'hoverTextColor'=>'#1d2327','focusColor'=>$fg,'paddingX'=>12,'paddingY'=>8,'radius'=>5,'borderWidth'=>0,'borderColor'=>$accent,'gapX'=>0,'gapY'=>0]),
            self::node('button-footer-contact-v0146','button','container-footer-reference-v0146',80,self::geometry([84,16,32,6],[80,16,38,6],[4,60,112,6]),['text'=>'Kontakt','linkType'=>'url','url'=>self::referenceLink($links,'contact','/kontakt/'),'targetBlank'=>false,'autoSize'=>false,'placementMode'=>'normal','zIndex'=>20,'background'=>$bg,'textColor'=>$fg,'hoverBackground'=>$bg,'hoverTextColor'=>$fg,'focusColor'=>$accent,'paddingX'=>12,'paddingY'=>8,'radius'=>5,'borderWidth'=>1,'borderColor'=>$accent,'gapX'=>0,'gapY'=>0]),
            self::node('container-footer-divider-v0146','container','container-footer-reference-v0146',90,self::geometry([2,31,116,1],[2,34,116,1],[4,70,112,1]),['background'=>'#596052','radius'=>0,'padding'=>0,'minHeightRows'=>1,'borderWidth'=>0,'borderColor'=>'#596052','gapX'=>0,'gapY'=>0]),
            self::node('text-footer-copyright-v0146','text','container-footer-reference-v0146',100,self::geometry([35,34,50,4],[30,37,60,4],[4,74,112,5]),['heading'=>'','headingLevel'=>'h2','text'=>'© 2026 Aalborg Kaserners Veteran Panser- og Køretøjsforening','align'=>'center','verticalAlign'=>'center','background'=>$bg,'backgroundTransparent'=>true,'textColor'=>$fg,'headingColor'=>$fg,'padding'=>0,'radius'=>0,'fontFamily'=>'system','fontSize'=>11,'fontWeight'=>400,'lineHeight'=>1.3,'letterSpacing'=>0,'borderWidth'=>0,'borderColor'=>'#000000','gapX'=>0,'gapY'=>0]),
        ];
        return LayoutModel::normalize(['schemaVersion'=>LayoutModel::SCHEMA,'units'=>LayoutModel::UNITS,'rowPx'=>LayoutModel::ROW_PX,'nodes'=>$nodes]);
    }

    /** @param array<string,mixed> $design */
    public static function buildReferenceFooterModel(array $design=[]): array {
        return self::buildDesktopReferenceFooterModel($design,[]);
    }

    /** @param array<string,string> $links */
    private static function referenceShortcutHtml(array $links): string {
        $items=[['home','Hjem','/'],['about','Om','/om-foreningen/'],['vehicles','Køretøjer','/koeretoejer-og-materiel/'],['events','Events','/events/'],['gallery','Billedgalleri','/billedgalleri/']];
        $rows=[];
        foreach ($items as $item) {
            [$key,$label,$fallback]=$item; $url=self::referenceLink($links,$key,$fallback);
            $rows[]='<a href="'.htmlspecialchars($url,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8').'">'.htmlspecialchars($label,ENT_QUOTES|ENT_SUBSTITUTE,'UTF-8').'</a>';
        }
        return implode("<br>\n",$rows);
    }

    /** @param array<string,string> $links */
    private static function referenceLink(array $links,string $key,string $fallback): string {
        $url=esc_url_raw((string)($links[$key]??'')); return $url!==''?$url:$fallback;
    }

    /** @return array<string,string> */
    private static function referenceFooterLinks(): array {
        return [
            'home'=>self::referencePageUrl([], '/'),
            'about'=>self::referencePageUrl(['om-foreningen','om'], '/om-foreningen/'),
            'vehicles'=>self::referencePageUrl(['koeretoejer-og-materiel','koretojer-og-materiel','koeretoejer'], '/koeretoejer-og-materiel/'),
            'events'=>self::referencePageUrl(['events'], '/events/'),
            'gallery'=>self::referencePageUrl(['billedgalleri'], '/billedgalleri/'),
            'join'=>self::referencePageUrl(['bliv-medlem'], '/bliv-medlem/'),
            'contact'=>self::referencePageUrl(['kontakt'], '/kontakt/'),
        ];
    }

    /** @param array<int,string> $slugs */
    private static function referencePageUrl(array $slugs,string $fallbackPath): string {
        if (function_exists('get_page_by_path') && function_exists('get_permalink')) {
            foreach ($slugs as $slug) {
                $page=get_page_by_path($slug,OBJECT,'page');
                if ($page instanceof \WP_Post) { $url=get_permalink($page); if (is_string($url) && $url!=='') return esc_url_raw($url); }
            }
        }
        if (function_exists('home_url')) return esc_url_raw((string)home_url($fallbackPath));
        return $fallbackPath;
    }
'''
s=replace_once(s,old,new,'reference Footer model')
write(path,s)

# Diagnostics -----------------------------------------------------------------
path='clean/hangar18-manager/src/Admin/GlobalDesignerController.php'
s=read(path)
s=replace_once(s,'Kildeprioritet: gammel Visual Header/Footer Builder → HANGAR18-FOOTER-blok → tydeligt mærket gammel Manager-standardfallback. En fallback betegnes aldrig som 1:1-konvertering. Hver kørsel gemmes som ny Footer-version.','Kildeprioritet: gammel Visual Header/Footer Builder → HANGAR18-FOOTER-blok → Desktop-reference fra 29-08-2026. Referencefallbacken er en visuel rekonstruktion og betegnes aldrig som 1:1-konvertering. Hver kørsel gemmes som ny Footer-version.','diagnostic text')
s=replace_once(s,"'Ikke fundet · gammel Manager-standardfallback er tilgængelig'","'Ikke fundet · Desktop-reference 29-08-2026 bruges som fallback'",'diagnostic fallback')
write(path,s)

# BUG-15: popup-free local preview -------------------------------------------
path='clean/hangar18-manager/assets/global-designer-v0123.js'
s=read(path)
start=s.index('    function previewLayout() {')
end=s.index('\n    function install() {',start)
new_preview=r'''    function ensurePreviewOverlay() {
        var overlay=document.getElementById('h18-global-preview-overlay');
        if (overlay) { return overlay; }
        overlay=document.createElement('div');
        overlay.id='h18-global-preview-overlay'; overlay.className='h18-global-preview-overlay'; overlay.hidden=true;
        overlay.innerHTML='<div class="h18-global-preview-dialog" role="dialog" aria-modal="true" aria-label="Header / Footer preview"><div class="h18-global-preview-bar"><strong>Visual Designer · Header / Footer preview</strong><button type="button" class="button" data-vd-preview-close>Luk</button></div><div class="h18-global-preview-scroll"><div class="h18-global-preview-host"></div></div></div>';
        document.body.appendChild(overlay);
        overlay.addEventListener('click',function(event){ if(event.target===overlay||(event.target&&event.target.closest&&event.target.closest('[data-vd-preview-close]'))){ closePreview(); } });
        document.addEventListener('keydown',function(event){ if(event.key==='Escape'&&!overlay.hidden){ closePreview(); } });
        return overlay;
    }
    function closePreview(){ var overlay=document.getElementById('h18-global-preview-overlay'); if(!overlay)return; overlay.hidden=true; document.body.classList.remove('h18-global-preview-open'); }
    function previewLayout() {
        syncModel();
        var canvas=document.getElementById('h18-clean-canvas'); if(!canvas)return;
        var copy=canvas.cloneNode(true); copy.removeAttribute('id'); copy.classList.add('vd-global-preview-canvas');
        copy.querySelectorAll('.h18-clean-node-header,.h18-clean-resize,.h18-clean-empty-drop,.h18-clean-v018-drop-overlay,.h18-clean-image-edit-frame').forEach(function(node){node.remove();});
        copy.querySelectorAll('.h18-clean-node').forEach(function(node){node.classList.remove('is-selected','is-resizing','is-dragging','has-layout-overlap','h18-clean-v018-drop-target','h18-clean-v018-drop-inside');node.style.outline='none';node.style.boxShadow='none';});
        var virtualWidth=parseInt(canvas.getAttribute('data-h18-viewport-width')||'0',10)||canvas.offsetWidth||1440;
        copy.removeAttribute('data-h18-viewport-scale'); copy.removeAttribute('data-h18-viewport-mode'); copy.style.transform='none'; copy.style.transformOrigin='0 0'; copy.style.width=virtualWidth+'px'; copy.style.maxWidth='none'; copy.style.margin='0';
        var overlay=ensurePreviewOverlay(); var host=overlay.querySelector('.h18-global-preview-host'); if(!host)return;
        host.innerHTML=''; host.style.width=virtualWidth+'px'; host.appendChild(copy); overlay.hidden=false; document.body.classList.add('h18-global-preview-open');
        var scroller=overlay.querySelector('.h18-global-preview-scroll'); if(scroller){scroller.scrollTop=0;scroller.scrollLeft=0;}
    }
'''
s=s[:start]+new_preview+s[end:]
write(path,s)

path='clean/hangar18-manager/assets/global-designer-v0123.css'
s=read(path)
if 'h18-global-preview-overlay' not in s:
    s += '''\n/* 0.1.46 popup-free Header/Footer preview */\nbody.h18-global-preview-open{overflow:hidden!important}\n.h18-global-preview-overlay[hidden]{display:none!important}\n.h18-global-preview-overlay{position:fixed;inset:0;z-index:1000000;background:rgba(0,0,0,.66);display:flex;padding:20px;box-sizing:border-box}\n.h18-global-preview-dialog{display:flex;flex-direction:column;width:100%;min-width:0;min-height:0;background:#f0f0f1;border-radius:8px;box-shadow:0 12px 48px rgba(0,0,0,.35);overflow:hidden}\n.h18-global-preview-bar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:10px 14px;background:#fff;border-bottom:1px solid #dcdcde;flex:0 0 auto}\n.h18-global-preview-scroll{flex:1 1 auto;min-width:0;min-height:0;overflow:auto;padding:24px;box-sizing:border-box}\n.h18-global-preview-host{min-height:120px;background:#fff;box-shadow:0 4px 24px rgba(0,0,0,.12)}\n.vd-global-preview-canvas .h18-clean-node{cursor:default!important}\n.vd-global-preview-canvas .h18-clean-inner-surface{min-height:100%}\n'''
write(path,s)

# Fit always starts Fit --------------------------------------------------------
path='clean/hangar18-manager/assets/editor-v0144-viewport.js'
s=read(path)
s=replace_once(s,"    function install() {\n        if (!ensureStage()) { return; }\n        setFit();\n","    function install() {\n        if (!ensureStage()) { return; }\n        mode = 'fit';\n        currentScale = 1;\n        setFit();\n",'fit install')
s=replace_once(s,"        window.addEventListener('resize', function () { if (mode === 'fit') { schedule(); } }, { passive: true });\n","        window.addEventListener('resize', function () { if (mode === 'fit') { schedule(); } }, { passive: true });\n        window.addEventListener('pageshow', function () { mode = 'fit'; window.requestAnimationFrame(setFit); }, { passive: true });\n",'fit pageshow')
write(path,s)

# Rich-text parity: theme CSS may not inject paragraph/list margins -----------
path='clean/hangar18-manager/src/Frontend/Renderer.php'
s=read(path)
s=replace_once(s,"        echo '.h18-clean-front-text{overflow-wrap:anywhere}';\n        echo '.h18-clean-front-text>p:first-of-type{margin-top:0}.h18-clean-front-text>p:last-child{margin-bottom:0}';\n","        echo '.h18-clean-front-text{overflow-wrap:anywhere}';\n        echo '.h18-clean-front-text p{margin:0!important;padding:0!important}.h18-clean-front-text ul,.h18-clean-front-text ol{margin:0!important;padding-top:0!important;padding-bottom:0!important}.h18-clean-front-text li{margin:0!important}.h18-clean-front-text a{display:inline!important;margin:0!important;padding:0!important;color:inherit;text-decoration:inherit}';\n",'frontend rich text reset')
write(path,s)

path='clean/hangar18-manager/assets/editor.css'
s=read(path)
if '.h18-clean-text-body p{' not in s:
    s += '\n/* 0.1.46 rich-text spacing parity with frontend */\n.h18-clean-text-body p{margin:0!important;padding:0!important}.h18-clean-text-body ul,.h18-clean-text-body ol{margin:0!important;padding-top:0!important;padding-bottom:0!important}.h18-clean-text-body li{margin:0!important}.h18-clean-text-body a{display:inline!important;margin:0!important;padding:0!important;color:inherit;text-decoration:inherit}\n'
write(path,s)

# Prevent editor rich links from navigating -----------------------------------
path='clean/hangar18-manager/assets/editor-v018-core.js'
s=read(path)
s=replace_once(s,"            body.innerHTML = richPreviewHtml(String(node.props.text || 'Ny tekst')) || 'Tekst';\n            wrap.appendChild(body);\n","            body.innerHTML = richPreviewHtml(String(node.props.text || 'Ny tekst')) || 'Tekst';\n            body.querySelectorAll('a').forEach(function (link) { link.addEventListener('click', function (event) { event.preventDefault(); }); });\n            wrap.appendChild(body);\n",'editor links')
write(path,s)

# QA --------------------------------------------------------------------------
path='.github/scripts/v0125_model_qa.php'
s=read(path)
old='''vdAssert(str_contains((string)$footerPhp,'legacy-manager-standard-fallback') && str_contains((string)$footerPhp,'ikke 1:1-kilde'),'Footer standard fallback is not explicitly labelled.');\n\necho "Visual Designer Manager 0.1.45 model QA PASS\\n";'''
new=r'''vdAssert(str_contains((string)$footerPhp,'hangar18_manager_site_templates_v1') && str_contains((string)$footerPhp,'hangar18_manager_site_template_assignments_v1'),'Footer legacy-source precedence regressed.');

/* 0.1.46 */
$footerDesktop=LegacyFooterConverter::buildDesktopReferenceFooterModel(['FooterWidthPercent'=>90,'PrimaryColor'=>'#30382a','LightTextColor'=>'#f2f0e8','AccentColor'=>'#c3ae83'],['home'=>'/','about'=>'/om-foreningen/','vehicles'=>'/koeretoejer-og-materiel/','events'=>'/events/','gallery'=>'/billedgalleri/','join'=>'/bliv-medlem/','contact'=>'/kontakt/']);
$fdBy=[]; foreach($footerDesktop['nodes'] as $n){$fdBy[$n['type']][]=$n;}
vdAssert(count($fdBy['section']??[])===1,'Footer reference must have one Section.');
vdAssert(count($fdBy['container']??[])>=2,'Footer reference must have main Kasse and divider Kasse.');
vdAssert(count($fdBy['text']??[])>=6,'Footer reference text structure is incomplete.');
vdAssert(count($fdBy['button']??[])===2,'Footer reference must have two CTA buttons.');
vdAssert((int)($fdBy['section'][0]['geometry']['desktop']['x']??-1)===6 && (int)($fdBy['section'][0]['geometry']['desktop']['w']??-1)===108,'Footer reference must be 90 percent centred.');
vdAssert((int)($fdBy['section'][0]['geometry']['desktop']['h']??-1)===40,'Footer reference Desktop height must be 40 rows.');
$fdText=implode("\n",array_map(static fn($n)=>(string)($n['props']['text']??''),$fdBy['text']??[]));
$fdButtons=implode("\n",array_map(static fn($n)=>(string)($n['props']['text']??''),$fdBy['button']??[]));
vdAssert(str_contains($fdText,'Genveje')&&str_contains($fdText,'Foreningen')&&str_contains($fdText,'Billedgalleri'),'Footer reference columns are incomplete.');
vdAssert(str_contains($fdButtons,'Bliv medlem')&&str_contains($fdButtons,'Kontakt'),'Footer reference CTA labels are incomplete.');
vdAssert(str_contains((string)$footerPhp,'desktop-reference-2026-08-29'),'Footer Desktop-reference fallback marker is missing.');
$globalPreviewJs=file_get_contents(__DIR__ . '/../../clean/hangar18-manager/assets/global-designer-v0123.js');
vdAssert(is_string($globalPreviewJs)&&str_contains($globalPreviewJs,'h18-global-preview-overlay')&&!str_contains($globalPreviewJs,'window.open('),'BUG-15 popup-free Header/Footer preview contract failed.');
vdAssert(str_contains((string)$viewportJs,"mode = 'fit';")&&str_contains((string)$viewportJs,"addEventListener('pageshow'"),'Designer must always enter in Fit mode.');
vdAssert(str_contains((string)$rendererPhp,'.h18-clean-front-text p{margin:0!important')&&str_contains((string)$rendererPhp,'.h18-clean-front-text li{margin:0!important'),'Frontend rich-text spacing is not isolated from theme CSS.');

echo "Visual Designer Manager 0.1.46 model QA PASS\n";'''
s=replace_once(s,old,new,'0.1.46 QA block')
write(path,s)

# Release history -------------------------------------------------------------
path='clean/hangar18-manager/release-history.json'
data=json.loads(read(path))
if not data or data[0].get('version')!='0.1.46':
    data.insert(0,{'version':'0.1.46','date':'2026-08-29','items':[
        'BUG-15: Header/Footer-forhåndsvisning åbner nu som intern Visual Designer-overlay og kræver ikke browser-popup-tilladelse.',
        'BUG-16: Manglende legacy Footer bruger Desktop-reference fra 29-08-2026 med tre indholdsområder, CTA-knapper, skillelinje og copyright i stedet for den simple standardfallback.',
        'Canvas starter altid i Fit ved editor-entry/pageshow og breakpointskift; 100% er fortsat kun manuel zoom.',
        'Rich-text spacing er isoleret fra temaets paragraph/list/link CSS, så Designer og frontend ikke får forskellige ekstra linje-/afsnitsafstande.',
        'Theme Shell forbliver OFF; Footer Desktop parity afventer bruger-QA før Menu bliver næste hovedopgave.'
    ]})
write(path,json.dumps(data,ensure_ascii=False,indent=2)+'\n')

write('clean-release-notes.html','''<h4>0.1.46</h4>\n<ul>\n<li>Popup-fri Header/Footer preview i intern overlay.</li>\n<li>Footer Desktop-reference fallback fra 29-08-2026 med tre områder, CTA-knapper, skillelinje og copyright.</li>\n<li>Designer starter altid i Fit; 100% er manuel zoom.</li>\n<li>Rich-text paragraph/list/link spacing isoleres fra tema-CSS for Designer/frontend parity.</li>\n<li>Theme Shell er fortsat deaktiveret.</li>\n</ul>\n''')
write('docs/v0146-status.md','''# Visual Designer Manager 0.1.46 – status\n\nDato: 2026-08-29\n\n## Implementeret\n\n- BUG-15: lokal Header/Footer preview er intern overlay og bruger ikke `window.open`.\n- BUG-16: manglende Footer-kilde bruger Desktop-reference fra 29-08-2026.\n- Canvas starter altid i Fit ved editor-entry/pageshow og breakpointskift.\n- Rich-text paragraph/list/link spacing nulstilles deterministisk i både Designer og frontend.\n- Theme Shell cutover er fortsat OFF.\n\n## QA-status\n\nKode-/modelkontrakter dækkes af release-gates. Bruger-QA af Footer Desktop parity afventer. Menu er næste hovedopgave efter Footer PASS.\n''')

path='CLEAN-TECHNICAL-MANUAL.md'
s=read(path)
append='''\n\n## 0.1.46 – Footer/preview/Fit/rich-text parity\n\n### VD-GLOBAL-PREVIEW-001\nHeader/Footer lokal preview må ikke kræve browser-popup-tilladelse. Preview vises i en intern overlay/modal og må ikke bruge popup som normalmekanisme.\n\n### VD-FOOTER-REFERENCE-001\nHvis hverken gammel Visual Header/Footer Builder-kilde eller HANGAR18-FOOTER-shell findes, bruges den godkendte Desktop-reference fra 29-08-2026 som eksplicit visuel fallback. Den må ikke beskrives som 1:1-kildekonvertering.\n\n### VD-CANVAS-START-FIT-001\nDesigner starter altid i Fit ved ny editor-entry, reload/pageshow og breakpointskift. 100% og anden manuel zoom er kun sessionens manuelle visningsvalg.\n\n### VD-RICHTEXT-SPACING-001\nTemaets globale CSS må ikke ændre Visual Designer Tekst-elementets paragraph-, liste- eller link-spacing. Designer og frontend ejer disse baselines deterministisk.\n'''
if 'VD-GLOBAL-PREVIEW-001' not in s:
    s += append
write(path,s)

print('Visual Designer Manager 0.1.46 patch prepared.')
