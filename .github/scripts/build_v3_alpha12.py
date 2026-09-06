from pathlib import Path
import hashlib, json, subprocess

VERSION='3.0.0-alpha.12'
DEST=Path('build/visual-designer-manager')
def read(p): return (DEST/p).read_text(encoding='utf-8')
def write(p,s):
    q=DEST/p; q.parent.mkdir(parents=True,exist_ok=True); q.write_text(s,encoding='utf-8')
def repl(p,a,b,label):
    s=read(p); n=s.count(a)
    if n!=1: raise SystemExit(f'{label}: expected 1 anchor in {p}, found {n}')
    write(p,s.replace(a,b,1))
def sha(p): return hashlib.sha256((DEST/p).read_bytes()).hexdigest()

# V1 mobile parity reset: Alpha.12 intentionally rebuilds from Alpha.9.
subprocess.run(['python3','.github/scripts/build_v3_alpha9.py'],check=True)
rr='src/Frontend/ResponsiveRenderer.php'; rr_sha=sha(rr)

main=read('visual-designer-manager.php')
for a,b in [
 (' * Version: 3.0.0-alpha.9',f' * Version: {VERSION}'),
 ("define('VDM_VERSION', '3.0.0-alpha.9');",f"define('VDM_VERSION', '{VERSION}');"),
 ("define('H18_CLEAN_VERSION', '3.0.0-alpha.9');",f"define('H18_CLEAN_VERSION', '{VERSION}');")]:
    if main.count(a)!=1: raise SystemExit(f'version anchor {a!r}: {main.count(a)}')
    main=main.replace(a,b,1)
write('visual-designer-manager.php',main)

# Event image is a normal content image for every existing/new eventimage node.
model='src/Model/LayoutModel.php'
repl(model,
"            $fit = strtolower((string) ($raw['fit'] ?? 'cover'));\n            if (!in_array($fit, ['cover','contain'], true)) { $fit = 'cover'; }",
"            $fit = 'original';",
'eventimage PHP normal mode')
repl(model,
"                'imageHeight' => self::clamp($raw['imageHeight'] ?? 360, 80, 1000, 360),",
"                'imageHeight' => self::clamp($raw['imageHeight'] ?? 360, 80, 1000, 360),\n                'imageMaxWidth' => self::clamp($raw['imageMaxWidth'] ?? 900, 240, 1800, 900),",
'eventimage PHP max width')

renderer='src/Frontend/Renderer.php'
repl(renderer,
"    private static function eventDateLabel(string $start, string $end = ''): string\n    {",
"    private static function renderStoredRichText(string $raw): string\n    {\n        return strpos($raw, '<') === false ? nl2br(esc_html($raw), false) : wp_kses_post($raw);\n    }\n\n    private static function renderPlainMultiline(string $raw): string\n    {\n        return nl2br(esc_html($raw), false);\n    }\n\n    private static function eventDateLabel(string $start, string $end = ''): string\n    {",
'multiline helpers')
repl(renderer,
"            $bodyHtml = strpos($rawText, '<') === false ? nl2br(esc_html($rawText), false) : wp_kses_post($rawText);",
"            $bodyHtml = self::renderStoredRichText($rawText);",
'text multiline helper')
repl(renderer,
"            $content = $rich ? wp_kses_post((string) $value) : esc_html((string) $value);",
"            $content = $rich ? self::renderStoredRichText((string) $value) : self::renderPlainMultiline((string) $value);",
'eventvalue multiline')
repl(renderer,
"$content=$empty?'':($type==='richtext'?wp_kses_post((string)$value):($type==='boolean'?($value?'Ja':'Nej'):nl2br(esc_html((string)$value))));",
"$content=$empty?'':($type==='richtext'?self::renderStoredRichText((string)$value):($type==='boolean'?($value?'Ja':'Nej'):self::renderPlainMultiline((string)$value)));",
'eventfield multiline')
repl(renderer,
"$cards .= '<div class=\"h18-clean-front-event-fact\" style=\"' . esc_attr($cardStyle) . '\"><strong style=\"' . esc_attr($labelStyle) . '\">' . esc_html((string) $fact[0]) . '</strong><span style=\"' . esc_attr($valueStyle) . '\">' . esc_html((string) $fact[1]) . '</span></div>';",
"$cards .= '<div class=\"h18-clean-front-event-fact\" style=\"' . esc_attr($cardStyle) . '\"><strong style=\"' . esc_attr($labelStyle) . '\">' . esc_html((string) $fact[0]) . '</strong><span style=\"' . esc_attr($valueStyle) . '\">' . self::renderPlainMultiline((string) $fact[1]) . '</span></div>';",
'eventfacts multiline')
repl(renderer,
"$description=!empty($props['showDescription'])&&trim((string)($fields['description']??''))!==''?'<div class=\"h18-clean-front-event-description\">'.wp_kses_post((string)$fields['description']).'</div>':'';",
"$description=!empty($props['showDescription'])&&trim((string)($fields['description']??''))!==''?'<div class=\"h18-clean-front-event-description\">'.self::renderStoredRichText((string)$fields['description']).'</div>':'';",
'eventdetail description multiline')
repl(renderer,
"$rendered=$atype==='richtext'?wp_kses_post((string)$value):($atype==='boolean'?($value?'Ja':'Nej'):nl2br(esc_html((string)$value)));",
"$rendered=$atype==='richtext'?self::renderStoredRichText((string)$value):($atype==='boolean'?($value?'Ja':'Nej'):self::renderPlainMultiline((string)$value));",
'eventdetail custom multiline')
repl(renderer,"$meta.$summary.$description.'</article>';","$meta.$summary.$description.$custom.'</article>';",'classic custom fields')
repl(renderer,
"$featuredId=absint($record['featuredMediaId']??0);$hero='';if(!empty($props['showImage'])&&$featuredId>0){$url=wp_get_attachment_image_url($featuredId,'large');if(is_string($url)&&$url!==''){$hero='<img class=\"h18-clean-front-event-hero\" src=\"'.esc_url($url).'\" alt=\"'.esc_attr((string)($record['title']??'')).'\" style=\"height:'.esc_attr((string)$imageHeight).'px\">';}}",
"$featuredId=absint($record['featuredMediaId']??0);$hero='';if(!empty($props['showImage'])&&$featuredId>0){$url=wp_get_attachment_image_url($featuredId,'large');if(is_string($url)&&$url!==''){$hero='<img class=\"h18-clean-front-event-hero\" src=\"'.esc_url($url).'\" alt=\"'.esc_attr((string)($record['title']??'')).'\" style=\"display:block;width:100%;max-width:900px;height:auto;max-height:'.esc_attr((string)$imageHeight).'px;object-fit:contain;\">';}}",
'classic event normal image')
repl(renderer,
"            $height = max(80, min(1000, (int) ($props['imageHeight'] ?? 360)));\n            $fit = (string) ($props['fit'] ?? 'cover') === 'contain' ? 'contain' : 'cover';\n            $focalX = max(0, min(100, (int) ($props['focalX'] ?? 50))); $focalY = max(0, min(100, (int) ($props['focalY'] ?? 50)));\n            $background = sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff';\n            $imageStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';overflow:hidden;';\n            return '<figure id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-event-image\" style=\"' . esc_attr($imageStyle) . '\"><img src=\"' . esc_url($url) . '\" alt=\"' . esc_attr((string) ($record['title'] ?? '')) . '\" style=\"display:block;width:100%;height:' . esc_attr((string) $height) . 'px;object-fit:' . esc_attr($fit) . ';object-position:' . esc_attr((string) $focalX) . '% ' . esc_attr((string) $focalY) . '%\"></figure>';",
"            $height = max(80, min(1000, (int) ($props['imageHeight'] ?? 360)));\n            $maxWidth = max(240, min(1800, (int) ($props['imageMaxWidth'] ?? 900)));\n            $focalX = max(0, min(100, (int) ($props['focalX'] ?? 50))); $focalY = max(0, min(100, (int) ($props['focalY'] ?? 50)));\n            $background = sanitize_hex_color((string) ($props['background'] ?? '#ffffff')) ?: '#ffffff';\n            $imageStyle = $style . $borderStyle . $spacingStyle . $radiusStyle . 'background:' . $background . ';overflow:hidden;max-width:' . $maxWidth . 'px;justify-self:start;';\n            return '<figure id=\"h18-clean-' . $id . '\" class=\"h18-clean-front-node h18-clean-front-event-image\" style=\"' . esc_attr($imageStyle) . '\"><img src=\"' . esc_url($url) . '\" alt=\"' . esc_attr((string) ($record['title'] ?? '')) . '\" style=\"display:block;width:100%;height:auto;max-height:' . esc_attr((string) $height) . 'px;object-fit:contain;object-position:' . esc_attr((string) $focalX) . '% ' . esc_attr((string) $focalY) . '%\"></figure>';",
'eventimage normal renderer')

# Designer mirrors normal event-image rendering.
js='assets/editor-v018-core.js'
repl(js,
"            return Object.assign(common,{recordId:recordId,fit:String(raw.fit||'cover')==='contain'?'contain':'cover',imageHeight:clamp(parseInt(raw.imageHeight||360,10)||360,80,1000),focalX:clamp(parseInt(raw.focalX||50,10)||50,0,100),focalY:clamp(parseInt(raw.focalY||50,10)||50,0,100),background:normalizeColor(raw.background||'#ffffff'),radius:clamp(parseInt(raw.radius||4,10)||4,0,100)});",
"            return Object.assign(common,{recordId:recordId,fit:'original',imageHeight:clamp(parseInt(raw.imageHeight||360,10)||360,80,1000),imageMaxWidth:clamp(parseInt(raw.imageMaxWidth||900,10)||900,240,1800),focalX:clamp(parseInt(raw.focalX||50,10)||50,0,100),focalY:clamp(parseInt(raw.focalY||50,10)||50,0,100),background:normalizeColor(raw.background||'#ffffff'),radius:clamp(parseInt(raw.radius||4,10)||4,0,100)});",
'eventimage JS normalization')
repl(js,
"wrap.classList.add('h18-clean-node-preview--eventimage'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; if(!record||!record.featuredUrl){wrap.textContent='Eventbillede · eventet har intet billede';}else{const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt=String(record.title||'');img.style.display='block';img.style.width='100%';img.style.height=String(node.props.imageHeight||360)+'px';img.style.objectFit=node.props.fit==='contain'?'contain':'cover';img.style.objectPosition=String(node.props.focalX||50)+'% '+String(node.props.focalY||50)+'%';img.style.background=node.props.background||'#ffffff';img.style.borderRadius=String(node.props.radius||4)+'px';wrap.appendChild(img);}",
"wrap.classList.add('h18-clean-node-preview--eventimage'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; if(!record||!record.featuredUrl){wrap.textContent='Eventbillede · eventet har intet billede';}else{const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt=String(record.title||'');img.style.display='block';img.style.width='100%';img.style.maxWidth=String(node.props.imageMaxWidth||900)+'px';img.style.height='auto';img.style.maxHeight=String(node.props.imageHeight||360)+'px';img.style.objectFit='contain';img.style.objectPosition=String(node.props.focalX||50)+'% '+String(node.props.focalY||50)+'%';img.style.background=node.props.background||'#ffffff';img.style.borderRadius=String(node.props.radius||4)+'px';wrap.appendChild(img);}",
'eventimage JS preview')
repl(js,
"<label>Højde px<input data-field=\"eventDynamicImageHeight\" type=\"number\" min=\"80\" max=\"1000\" value=\"'+String(node.props.imageHeight||360)+'\"></label><label>Tilpasning<select data-field=\"eventDynamicImageFit\"><option value=\"cover\"'+(node.props.fit!=='contain'?' selected':'')+'>Fyld / beskær</option><option value=\"contain\"'+(node.props.fit==='contain'?' selected':'')+'>Vis hele billedet</option></select></label>",
"<label>Maks. højde px<input data-field=\"eventDynamicImageHeight\" type=\"number\" min=\"80\" max=\"1000\" value=\"'+String(node.props.imageHeight||360)+'\"></label><label>Maks. bredde px<input data-field=\"eventDynamicImageMaxWidth\" type=\"number\" min=\"240\" max=\"1800\" value=\"'+String(node.props.imageMaxWidth||900)+'\"></label><span>Visning: Normal størrelse</span>",
'eventimage JS inspector')
repl(js,
"                else if (field === 'eventDynamicImageFit') { current.props.fit=String(control.value||'cover')==='contain'?'contain':'cover'; }",
"                else if (field === 'eventDynamicImageFit') { current.props.fit='original'; }\n                else if (field === 'eventDynamicImageMaxWidth') { current.props.imageMaxWidth=clamp(parseInt(control.value||900,10)||900,240,1800); }",
'eventimage JS handlers')

# New generated event pages also declare normal image presentation.
hybrid='src/Migration/HybridModulePageMigration.php'
repl(hybrid,
"['id'=>'event-image','type'=>'eventimage','order'=>100,'geometry'=>self::geometry(3,102,114,36),'props'=>['recordId'=>'','fit'=>'cover','imageHeight'=>360,'focalX'=>50,'focalY'=>50,'background'=>'#ffffff','radius'=>4]],",
"['id'=>'event-image','type'=>'eventimage','order'=>100,'geometry'=>self::geometry(3,102,114,36),'props'=>['recordId'=>'','fit'=>'original','imageHeight'=>360,'imageMaxWidth'=>900,'focalX'=>50,'focalY'=>50,'background'=>'#ffffff','radius'=>4]],",
'event template normal image')

# Preserve historical releases in the package log while marking the workaround reset.
hp=DEST/'release-history.json'; hist=json.loads(hp.read_text(encoding='utf-8')); rows=hist['versions']
if not rows or rows[0].get('version')!='3.0.0-alpha.9': raise SystemExit('Alpha.9 history baseline missing')
a12={'version':VERSION,'date':'2026-09-06','items':['V1 Mobile Parity Reset: Alpha.10/11 grid→flex runtime-workarounds er fjernet.','Eventbillede vises som almindeligt billede med maks. bredde 900 px.','Linjeskift bevares i Program og øvrige event-/richtext-felter.']}
a11={'version':'3.0.0-alpha.11','date':'2026-09-06','items':['Historisk mobil order-workaround; tilbageført i Alpha.12.']}
a10={'version':'3.0.0-alpha.10','date':'2026-09-06','items':['Historisk mobil grid→flex-workaround; tilbageført i Alpha.12.']}
hp.write_text(json.dumps({'versions':[a12,a11,a10]+rows},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

# Hard gates: mobile renderer is Alpha.9 byte-for-byte and workaround assets are gone.
if sha(rr)!=rr_sha: raise SystemExit('ResponsiveRenderer changed relative to Alpha.9')
text=read(rr)
for token in ['h18-vdm-mobile-flow-repair','v3-alpha10-mobile-reflow.js','v3-alpha11-mobile-reflow.js','mobileOrder']:
    if token in text: raise SystemExit(f'stale mobile token: {token}')
for p in ['assets/v3-alpha10-mobile-reflow.js','assets/v3-alpha11-mobile-reflow.js']:
    if (DEST/p).exists(): raise SystemExit(f'stale mobile asset: {p}')
for token in ['renderStoredRichText','imageMaxWidth','max-width:900px','$meta.$summary.$description.$custom']:
    if token not in read(renderer): raise SystemExit(f'missing renderer token: {token}')
for token in ["'fit' => $fit","'imageMaxWidth' => self::clamp"]:
    if token not in read(model): raise SystemExit(f'missing model token: {token}')
for token in ['Visning: Normal størrelse','eventDynamicImageMaxWidth','imageMaxWidth:clamp']:
    if token not in read(js): raise SystemExit(f'missing editor token: {token}')
print('Alpha.12 V1 mobile parity reset: PASS')
print('Alpha.12 event image normal size: PASS')
print('Alpha.12 multiline event fields: PASS')
