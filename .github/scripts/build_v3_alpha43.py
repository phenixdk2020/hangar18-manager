from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.43'
DEST = Path('build/visual-designer-manager')

subprocess.run(['python3', '.github/scripts/build_v3_alpha42.py'], check=True)


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


# Version cutover.
main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.42', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.42');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.42');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.43 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

# ---------------------------------------------------------------------------
# Designer+ hardening 1: safe-area overlay must live and style inside iframe.
# Parent document CSS cannot style nodes inserted into an iframe document.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0200-designer-suite.js',
    """    function applySafeArea() {
        var frame=document.getElementById('h18-vd-canonical-responsive-frame');if(!frame)return;
        try{var doc=frame.contentDocument;if(!doc||!doc.body)return;qa('.h18-suite-safe-top,.h18-suite-safe-bottom',doc).forEach(function(el){el.remove();});if(!safeArea)return;var top=doc.createElement('div');top.className='h18-suite-safe-top';var bottom=doc.createElement('div');bottom.className='h18-suite-safe-bottom';doc.body.appendChild(top);doc.body.appendChild(bottom);}catch(ignore){}
    }
""",
    """    function applySafeArea() {
        var frame=document.getElementById('h18-vd-canonical-responsive-frame');if(!frame)return;
        try{
            var doc=frame.contentDocument;if(!doc||!doc.body)return;
            qa('.h18-suite-safe-top,.h18-suite-safe-bottom',doc).forEach(function(el){el.remove();});
            if(!safeArea)return;
            var top=doc.createElement('div');top.className='h18-suite-safe-top';
            top.style.cssText='position:fixed;left:0;right:0;top:0;height:47px;z-index:2147483000;pointer-events:none;background:rgba(34,113,177,.12);border-bottom:1px dashed #2271b1;box-sizing:border-box';
            var bottom=doc.createElement('div');bottom.className='h18-suite-safe-bottom';
            bottom.style.cssText='position:fixed;left:0;right:0;bottom:0;height:34px;z-index:2147483000;pointer-events:none;background:rgba(34,113,177,.12);border-top:1px dashed #2271b1;box-sizing:border-box';
            doc.body.appendChild(top);doc.body.appendChild(bottom);
        }catch(ignore){}
    }
""",
    'Alpha.43 iframe safe-area overlay'
)

# ---------------------------------------------------------------------------
# Designer+ hardening 2: image tools gain alt, replace, zoom and manual X/Y.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0200-designer-suite.js',
    """        host.innerHTML = '<h4>Billedeværktøjer</h4><div class="h18-suite-image-tools"><button class="button" data-fit="cover">Cover</button><button class="button" data-fit="contain">Contain</button><button class="button" data-fit="original">Original</button><button class="button" data-focus>Vælg fokuspunkt</button><button class="button" data-focus-center>Centrér fokus</button></div>';
        qa('[data-fit]',host).forEach(function (button) { button.addEventListener('click', function () {
            mutate('Billede · ' + button.getAttribute('data-fit'), function (state) { var node=nodeById(n.id,state); if(node){node.props.fit=button.getAttribute('data-fit');} });
        }); });
        q('[data-focus]',host).addEventListener('click', function () { enableFocusPoint(n.id); });
        q('[data-focus-center]',host).addEventListener('click', function () { mutate('Centrér billedfokus', function (state) { var node=nodeById(n.id,state); if(node){node.props.focalX=50;node.props.focalY=50;} }); });
""",
    """        var p=n.props||{};
        host.innerHTML = '<h4>Billedeværktøjer</h4><div class="h18-suite-image-tools"><button class="button" data-fit="cover">Cover</button><button class="button" data-fit="contain">Contain</button><button class="button" data-fit="original">Original</button><button class="button" data-image-zoom="-1">Zoom −</button><button class="button" data-image-zoom="1">Zoom +</button><button class="button" data-focus>Vælg fokuspunkt</button><button class="button" data-focus-center>Centrér fokus</button><button class="button" data-pick-image>Udskift billede</button></div><div class="h18-suite-row"><label>Alt-tekst <input type="text" data-image-alt value="'+esc(p.alt||'')+'"></label><label>X <input type="number" data-image-x min="-4000" max="4000" value="'+(parseInt(p.manualX||0,10)||0)+'"></label><label>Y <input type="number" data-image-y min="-4000" max="4000" value="'+(parseInt(p.manualY||0,10)||0)+'"></label></div>';
        qa('[data-fit]',host).forEach(function (button) { button.addEventListener('click', function () {
            mutate('Billede · ' + button.getAttribute('data-fit'), function (state) { var node=nodeById(n.id,state); if(node){node.props.fit=button.getAttribute('data-fit');} });
        }); });
        qa('[data-image-zoom]',host).forEach(function(button){button.addEventListener('click',function(){var dir=parseInt(button.getAttribute('data-image-zoom')||0,10)||0;mutate('Billede · zoom',function(state){var node=nodeById(n.id,state);if(!node)return;var factor=dir>0?1.12:.89;node.props.fit='manual';node.props.manualW=Math.max(20,Math.min(4000,Math.round((parseInt(node.props.manualW||320,10)||320)*factor)));node.props.manualH=Math.max(20,Math.min(4000,Math.round((parseInt(node.props.manualH||240,10)||240)*factor)));});});});
        q('[data-focus]',host).addEventListener('click', function () { enableFocusPoint(n.id); });
        q('[data-focus-center]',host).addEventListener('click', function () { mutate('Centrér billedfokus', function (state) { var node=nodeById(n.id,state); if(node){node.props.focalX=50;node.props.focalY=50;} }); });
        q('[data-pick-image]',host).addEventListener('click',function(){var pick=document.getElementById('h18-clean-pick-image');if(pick)pick.click();});
        q('[data-image-alt]',host).addEventListener('change',function(event){mutate('Billede · alt-tekst',function(state){var node=nodeById(n.id,state);if(node)node.props.alt=String(event.target.value||'');});});
        [['[data-image-x]','manualX'],['[data-image-y]','manualY']].forEach(function(pair){var input=q(pair[0],host);input.addEventListener('change',function(){mutate('Billede · position',function(state){var node=nodeById(n.id,state);if(node){node.props.fit='manual';node.props[pair[1]]=Math.max(-4000,Math.min(4000,parseInt(input.value||0,10)||0));}});});});
""",
    'Alpha.43 complete image quick tools'
)

# ---------------------------------------------------------------------------
# Designer+ hardening 3: Layer rows always have a type icon, even without a
# custom label, while still preserving the user-defined label.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0200-designer-suite.js',
    """            var layerPick=q('.h18-vd-layer-pick',item);if(layerPick&&p.suiteLabel){layerPick.textContent=String(p.suiteLabel)+' · '+String(n.type||'element');layerPick.title='Vælg '+String(p.suiteLabel);}
""",
    """            var layerPick=q('.h18-vd-layer-pick',item);
            if(layerPick){
                var typeIcons={section:'▤',container:'□',text:'T',image:'▧',button:'▰',link:'↗',menu:'☰',spacer:'↕',divider:'—',icon:'★',badge:'●',datalist:'☷',table:'▦',contactform:'✉',membershipform:'✓',vehiclelist:'▦',eventlist:'▦',gallerylist:'▦'};
                var typeNames={section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap',link:'Link',menu:'Menu',spacer:'Mellemrum',divider:'Skillelinje',icon:'Ikon',badge:'Badge',datalist:'Data List',table:'Tabel',contactform:'Kontaktformular',membershipform:'Indmeldelsesformular'};
                var display=String(p.suiteLabel||typeNames[n.type]||n.type||'Element');
                layerPick.textContent=String(typeIcons[n.type]||'◇')+' '+display+' · '+String(id).slice(-6);
                layerPick.title='Vælg '+display;
            }
""",
    'Alpha.43 Layer type icons'
)

# ---------------------------------------------------------------------------
# Designer+ hardening 4: live compare removes logged-in admin bar inside the
# same-origin live iframe. Version compare also shows semantic diff counts.
# ---------------------------------------------------------------------------
replace_once(
    'assets/editor-v0200-designer-suite.js',
    """    function fitCompareFrame(stage,frame,width){var available=Math.max(280,stage.clientWidth-8),scale=Math.min(1,available/width);frame.style.width=width+'px';frame.style.height=Math.max(700,Math.round((stage.clientHeight||750)/Math.max(.2,scale)))+'px';frame.style.transform='scale('+scale+')';frame.style.transformOrigin='0 0';}
    function openLiveCompare(){var modal=modalShell('Designer vs. live · '+activeDevice()),compare=q('.h18-suite-compare',modal),left=document.createElement('div'),right=document.createElement('div');left.className=right.className='h18-suite-compare-stage';left.innerHTML='<iframe title="Designer-preview"></iframe>';right.innerHTML='<iframe title="Live side"></iframe>';compare.appendChild(left);compare.appendChild(right);var w=previewWidth(),lf=q('iframe',left),rf=q('iframe',right);rf.src=String(CFG.pageUrl||'about:blank');submitModelToFrame(lf,model(),activeDevice());function fit(){fitCompareFrame(left,lf,w);fitCompareFrame(right,rf,w);}lf.onload=fit;rf.onload=fit;window.setTimeout(fit,100);}
    function openModelCompare(a,b){if(!a||!b||!a.model||!b.model){notice('Vælg to versioner.','warn');return;}var modal=modalShell('Versionssammenligning · v'+a.version+' vs v'+b.version),compare=q('.h18-suite-compare',modal),left=document.createElement('div'),right=document.createElement('div');left.className=right.className='h18-suite-compare-stage';left.innerHTML='<iframe title="Version A"></iframe>';right.innerHTML='<iframe title="Version B"></iframe>';compare.appendChild(left);compare.appendChild(right);var w=previewWidth(),lf=q('iframe',left),rf=q('iframe',right);submitModelToFrame(lf,a.model,activeDevice());submitModelToFrame(rf,b.model,activeDevice());function fit(){fitCompareFrame(left,lf,w);fitCompareFrame(right,rf,w);}lf.onload=fit;rf.onload=fit;setTimeout(fit,100);}
""",
    """    function fitCompareFrame(stage,frame,width){var available=Math.max(280,stage.clientWidth-8),scale=Math.min(1,available/width);frame.style.width=width+'px';frame.style.height=Math.max(700,Math.round((stage.clientHeight||750)/Math.max(.2,scale)))+'px';frame.style.transform='scale('+scale+')';frame.style.transformOrigin='0 0';}
    function cleanCompareFrame(frame){try{var doc=frame.contentDocument;if(!doc||!doc.head)return;var style=doc.createElement('style');style.textContent='#wpadminbar{display:none!important}html{margin-top:0!important}';doc.head.appendChild(style);}catch(ignore){}}
    function modelDiff(a,b){
        var am={},bm={},added=0,removed=0,moved=0,textChanged=0,designChanged=0;
        (a&&a.nodes||[]).forEach(function(n){if(n&&n.id)am[n.id]=n;});(b&&b.nodes||[]).forEach(function(n){if(n&&n.id)bm[n.id]=n;});
        Object.keys(bm).forEach(function(id){if(!am[id]){added++;return;}var an=am[id],bn=bm[id];if(JSON.stringify(an.geometry||{})!==JSON.stringify(bn.geometry||{}))moved++;var at={heading:(an.props||{}).heading,text:(an.props||{}).text,button:(an.props||{}).text};var bt={heading:(bn.props||{}).heading,text:(bn.props||{}).text,button:(bn.props||{}).text};if(JSON.stringify(at)!==JSON.stringify(bt))textChanged++;var ap=clone(an.props||{}),bp=clone(bn.props||{});['heading','text'].forEach(function(k){delete ap[k];delete bp[k];});if(JSON.stringify(ap)!==JSON.stringify(bp))designChanged++;});
        Object.keys(am).forEach(function(id){if(!bm[id])removed++;});
        return {added:added,removed:removed,moved:moved,textChanged:textChanged,designChanged:designChanged};
    }
    function openLiveCompare(){var modal=modalShell('Designer vs. live · '+activeDevice()),compare=q('.h18-suite-compare',modal),left=document.createElement('div'),right=document.createElement('div');left.className=right.className='h18-suite-compare-stage';left.innerHTML='<iframe title="Designer-preview"></iframe>';right.innerHTML='<iframe title="Live side"></iframe>';compare.appendChild(left);compare.appendChild(right);var w=previewWidth(),lf=q('iframe',left),rf=q('iframe',right);rf.src=String(CFG.pageUrl||'about:blank');submitModelToFrame(lf,model(),activeDevice());function fit(){cleanCompareFrame(lf);cleanCompareFrame(rf);fitCompareFrame(left,lf,w);fitCompareFrame(right,rf,w);}lf.onload=fit;rf.onload=fit;window.setTimeout(fit,100);}
    function openModelCompare(a,b){if(!a||!b||!a.model||!b.model){notice('Vælg to versioner.','warn');return;}var modal=modalShell('Versionssammenligning · v'+a.version+' vs v'+b.version),compare=q('.h18-suite-compare',modal),left=document.createElement('div'),right=document.createElement('div'),diff=modelDiff(a.model,b.model),status=q('[data-modal-status]',modal);if(status)status.textContent='+'+diff.added+' / −'+diff.removed+' · '+diff.moved+' flyttet/størrelse · '+diff.textChanged+' tekst · '+diff.designChanged+' design';left.className=right.className='h18-suite-compare-stage';left.innerHTML='<iframe title="Version A"></iframe>';right.innerHTML='<iframe title="Version B"></iframe>';compare.appendChild(left);compare.appendChild(right);var w=previewWidth(),lf=q('iframe',left),rf=q('iframe',right);submitModelToFrame(lf,a.model,activeDevice());submitModelToFrame(rf,b.model,activeDevice());function fit(){cleanCompareFrame(lf);cleanCompareFrame(rf);fitCompareFrame(left,lf,w);fitCompareFrame(right,rf,w);}lf.onload=fit;rf.onload=fit;setTimeout(fit,100);}
""",
    'Alpha.43 compare parity and semantic diff'
)

# Release history.
history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if isinstance(rows, list):
    rows.insert(0, {
        'version': VERSION,
        'date': '2026-10-24',
        'items': [
            'Designer+ safe-area-overlay styles nu inde i det responsive frontend-iframe og er derfor synligt på Mobil/Tablet presets.',
            'Billedeværktøjer udvides med alt-tekst, Udskift billede, Zoom +/- samt manuel X/Y-position oven på Cover/Contain/Original og fokuspunkt.',
            'Lag+ viser altid et typeikon og et kort stabilt ID; brugerdefinerede lagnavne bevares.',
            'Live-sammenligning fjerner WordPress admin-bar i same-origin iframe, så geometrien kan sammenlignes fair.',
            'Versionssammenligning viser nu antal tilføjede/slettede elementer, geometriændringer, tekstændringer og designændringer ud over side-by-side render.',
            'Hele Alpha.42 Designer Productivity Suite og Alpha.41 panel-recovery bevares.'
        ],
    })
    history_path.write_text(json.dumps({'versions': rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

suite = read('assets/editor-v0200-designer-suite.js')
main = read('visual-designer-manager.php')
for token in ['Version: 3.0.0-alpha.43', "define('VDM_VERSION', '3.0.0-alpha.43');"]:
    if token not in main:
        raise SystemExit(f'Alpha.43 version token missing: {token}')
for token in [
    "top.style.cssText='position:fixed",
    "data-image-zoom",
    "data-image-alt",
    "typeIcons={section:'▤'",
    "function modelDiff(a,b)",
    "cleanCompareFrame(frame)",
    "diff.textChanged",
]:
    if token not in suite:
        raise SystemExit(f'Alpha.43 Suite hardening token missing: {token}')

print('Visual Designer Manager V3 3.0.0-alpha.43 Designer Suite hardening: PASS')
