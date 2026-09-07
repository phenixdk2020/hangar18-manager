from pathlib import Path
import json
import subprocess

VERSION = '3.0.0-alpha.17'
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


def replace_between(rel: str, start: str, end: str, replacement: str, label: str) -> None:
    value = read(rel)
    if value.count(start) != 1:
        raise SystemExit(f'{label}: start anchor count={value.count(start)} in {rel}')
    pos = value.find(start)
    end_pos = value.find(end, pos + len(start))
    if end_pos < 0:
        raise SystemExit(f'{label}: end anchor missing in {rel}')
    write(rel, value[:pos] + replacement + value[end_pos:])


subprocess.run(['python3', '.github/scripts/build_v3_alpha16.py'], check=True)

main = read('visual-designer-manager.php')
for old, new in [
    (' * Version: 3.0.0-alpha.16', f' * Version: {VERSION}'),
    ("define('VDM_VERSION', '3.0.0-alpha.16');", f"define('VDM_VERSION', '{VERSION}');"),
    ("define('H18_CLEAN_VERSION', '3.0.0-alpha.16');", f"define('H18_CLEAN_VERSION', '{VERSION}');"),
]:
    if main.count(old) != 1:
        raise SystemExit(f'Alpha.17 version anchor mismatch: {old!r} count={main.count(old)}')
    main = main.replace(old, new, 1)
write('visual-designer-manager.php', main)

model_rel = 'src/Model/LayoutModel.php'
model_eventlist = r'''        if ($type === 'eventlist') {
            $orderBy = in_array((string) ($raw['orderBy'] ?? 'start'), ['start', 'title', 'updatedAt'], true) ? (string) ($raw['orderBy'] ?? 'start') : 'start';
            $order = strtoupper((string) ($raw['order'] ?? 'ASC')) === 'DESC' ? 'DESC' : 'ASC';
            $limit = self::clamp($raw['limit'] ?? 50, 1, 100, 50);
            $dateFilter = in_array((string) ($raw['dateFilter'] ?? 'upcoming'), ['all', 'upcoming', 'past'], true) ? (string) ($raw['dateFilter'] ?? 'upcoming') : 'upcoming';
            $minCardWidth = self::clamp($raw['minCardWidth'] ?? 280, 160, 600, 280);
            $maxCardWidth = max($minCardWidth, self::clamp($raw['maxCardWidth'] ?? 360, 160, 720, 360));
            $cardAlign = in_array((string) ($raw['cardAlign'] ?? 'left'), ['left', 'center', 'right'], true) ? (string) ($raw['cardAlign'] ?? 'left') : 'left';
            $imageRatio = in_array((string) ($raw['imageRatio'] ?? '16:10'), ['16:10', '16:9', '4:3', 'custom'], true) ? (string) ($raw['imageRatio'] ?? '16:10') : '16:10';
            $binding = ModuleBinding::normalize(['mode' => 'module', 'module' => 'events', 'view' => 'list', 'query' => ['status' => 'publish', 'orderBy' => $orderBy, 'order' => $order, 'limit' => $limit]]);
            return array_merge([
                'binding' => $binding,
                'limit' => $limit,
                'orderBy' => $orderBy,
                'order' => $order,
                'dateFilter' => $dateFilter,
                'detailPageId' => absint($raw['detailPageId'] ?? 0),
                'columns' => self::clamp($raw['columns'] ?? 3, 1, 4, 3),
                'minCardWidth' => $minCardWidth,
                'maxCardWidth' => $maxCardWidth,
                'cardAlign' => $cardAlign,
                'cardGap' => self::clamp($raw['cardGap'] ?? 18, 0, 80, 18),
                'cardPadding' => self::clamp($raw['cardPadding'] ?? 20, 0, 60, 20),
                'imageRatio' => $imageRatio,
                'imageHeight' => self::clamp($raw['imageHeight'] ?? 180, 60, 600, 180),
                'showImage' => array_key_exists('showImage', $raw) ? (bool) $raw['showImage'] : true,
                'showDate' => array_key_exists('showDate', $raw) ? (bool) $raw['showDate'] : true,
                'showLocation' => array_key_exists('showLocation', $raw) ? (bool) $raw['showLocation'] : true,
                'showSummary' => array_key_exists('showSummary', $raw) ? (bool) $raw['showSummary'] : true,
                'linkCards' => array_key_exists('linkCards', $raw) ? (bool) $raw['linkCards'] : true,
                'cardBackground' => sanitize_hex_color((string) ($raw['cardBackground'] ?? '#f2f0e8')) ?: '#f2f0e8',
                'textColor' => sanitize_hex_color((string) ($raw['textColor'] ?? '#30382a')) ?: '#30382a',
                'accentColor' => sanitize_hex_color((string) ($raw['accentColor'] ?? '#c3ae83')) ?: '#c3ae83',
                'cardRadius' => self::clamp($raw['cardRadius'] ?? 8, 0, 60, 8),
            ], $border);
        }
'''
replace_between(model_rel, "        if ($type === 'eventlist') {\n", "        if ($type === 'eventdetail') {\n", model_eventlist, 'Alpha.17 eventlist model')

renderer_rel = 'src/Frontend/Renderer.php'
renderer_eventlist = r'''        if ($type === 'eventlist') {
            $binding = isset($props['binding']) && is_array($props['binding']) ? $props['binding'] : [];
            $query = isset($binding['query']) && is_array($binding['query']) ? $binding['query'] : [];
            $query['status'] = 'publish';
            $query['limit'] = max(1, min(100, (int) ($props['limit'] ?? ($query['limit'] ?? 50))));
            $query['orderBy'] = in_array((string) ($props['orderBy'] ?? ($query['orderBy'] ?? 'start')), ['start', 'title', 'updatedAt'], true) ? (string) ($props['orderBy'] ?? ($query['orderBy'] ?? 'start')) : 'start';
            $query['order'] = strtoupper((string) ($props['order'] ?? ($query['order'] ?? 'ASC'))) === 'DESC' ? 'DESC' : 'ASC';
            $records = ModuleStore::listRecords('events', $query);
            $dateFilter = in_array((string) ($props['dateFilter'] ?? 'upcoming'), ['all', 'upcoming', 'past'], true) ? (string) ($props['dateFilter'] ?? 'upcoming') : 'upcoming';
            $now = current_time('Y-m-d\\TH:i');
            $columns = max(1, min(4, (int) ($props['columns'] ?? 3)));
            $minCardWidth = max(160, min(600, (int) ($props['minCardWidth'] ?? 280)));
            $maxCardWidth = max($minCardWidth, min(720, (int) ($props['maxCardWidth'] ?? 360)));
            $cardAlign = in_array((string) ($props['cardAlign'] ?? 'left'), ['left', 'center', 'right'], true) ? (string) ($props['cardAlign'] ?? 'left') : 'left';
            $gap = max(0, min(80, (int) ($props['cardGap'] ?? 18)));
            $padding = max(0, min(60, (int) ($props['cardPadding'] ?? 20)));
            $imageRatio = in_array((string) ($props['imageRatio'] ?? '16:10'), ['16:10', '16:9', '4:3', 'custom'], true) ? (string) ($props['imageRatio'] ?? '16:10') : '16:10';
            $imageHeight = max(60, min(600, (int) ($props['imageHeight'] ?? 180)));
            $cardBg = sanitize_hex_color((string) ($props['cardBackground'] ?? '#f2f0e8')) ?: '#f2f0e8';
            $textColor = sanitize_hex_color((string) ($props['textColor'] ?? '#30382a')) ?: '#30382a';
            $accent = sanitize_hex_color((string) ($props['accentColor'] ?? '#c3ae83')) ?: '#c3ae83';
            $cardRadius = max(0, min(60, (int) ($props['cardRadius'] ?? 8)));
            $detailPageId = absint($props['detailPageId'] ?? 0);
            $detailBase = $detailPageId > 0 ? get_permalink($detailPageId) : false;
            $cards = '';
            $ratioCss = ['16:10' => '16 / 10', '16:9' => '16 / 9', '4:3' => '4 / 3'][$imageRatio] ?? '';
            foreach ($records as $item) {
                $record = isset($item['record']) && is_array($item['record']) ? $item['record'] : [];
                if ((string) ($record['status'] ?? '') !== 'publish') { continue; }
                $fields = isset($record['fields']) && is_array($record['fields']) ? $record['fields'] : [];
                $start = (string) ($fields['start'] ?? '');
                $end = (string) ($fields['end'] ?? '');
                $edge = $end !== '' ? $end : $start;
                $past = $edge !== '' && strcmp(substr($edge, 0, 16), $now) < 0;
                if ($dateFilter === 'upcoming' && $past) { continue; }
                if ($dateFilter === 'past' && !$past) { continue; }
                $recordId = (string) ($record['id'] ?? '');
                $href = is_string($detailBase) && $detailBase !== '' && !empty($props['linkCards']) ? add_query_arg('h18_event', rawurlencode($recordId), $detailBase) : '';
                $tag = $href !== '' ? 'a' : 'article';
                $hrefAttr = $href !== '' ? ' href="' . esc_url($href) . '"' : '';
                $image = '';
                $featuredId = absint($record['featuredMediaId'] ?? 0);
                if (!empty($props['showImage']) && $featuredId > 0) {
                    $url = wp_get_attachment_image_url($featuredId, 'large');
                    if (is_string($url) && $url !== '') {
                        $imageStyle = $imageRatio === 'custom'
                            ? 'width:100%;height:' . esc_attr((string) $imageHeight) . 'px;object-fit:cover;'
                            : 'width:100%;height:auto;aspect-ratio:' . esc_attr($ratioCss) . ';object-fit:cover;';
                        $image = '<img src="' . esc_url($url) . '" alt="' . esc_attr((string) ($record['title'] ?? '')) . '" style="' . $imageStyle . '">';
                    }
                }
                $meta = '';
                if (!empty($props['showDate'])) {
                    $dateLabel = self::eventDateLabel($start, $end);
                    if ($dateLabel !== '') { $meta .= '<span style="color:' . esc_attr($accent) . '">' . esc_html($dateLabel) . '</span>'; }
                }
                if (!empty($props['showLocation']) && trim((string) ($fields['location'] ?? '')) !== '') { $meta .= '<span>' . esc_html((string) $fields['location']) . '</span>'; }
                $meta = $meta !== '' ? '<div class="h18-clean-front-event-meta">' . $meta . '</div>' : '';
                $summary = !empty($props['showSummary']) && trim((string) ($record['summary'] ?? '')) !== '' ? '<p>' . esc_html((string) $record['summary']) . '</p>' : '';
                $cardStyle = 'background:' . $cardBg . ';color:' . $textColor . ';padding:' . $padding . 'px;border-radius:' . $cardRadius . 'px;';
                $cards .= '<' . $tag . ' class="h18-clean-front-event-card"' . $hrefAttr . ' style="' . esc_attr($cardStyle) . '">' . $image . '<h3>' . esc_html((string) ($record['title'] ?? 'Event')) . '</h3>' . $meta . $summary . '</' . $tag . '>';
            }
            if ($cards === '' && self::$forceStandaloneCss) { $cards = '<p>Ingen publicerede events matcher visningen.</p>'; }
            $maxListWidth = ($columns * $maxCardWidth) + (max(0, $columns - 1) * $gap);
            $marginStyle = $cardAlign === 'center' ? 'margin-left:auto;margin-right:auto;' : ($cardAlign === 'right' ? 'margin-left:auto;margin-right:0;' : 'margin-left:0;margin-right:auto;');
            $listStyle = $style . $borderStyle . $spacingStyle
                . 'grid-template-columns:repeat(auto-fit,minmax(min(100%,' . $minCardWidth . 'px),' . $maxCardWidth . 'px));'
                . 'gap:' . $gap . 'px;max-width:' . $maxListWidth . 'px;justify-content:' . ($cardAlign === 'center' ? 'center' : ($cardAlign === 'right' ? 'end' : 'start')) . ';'
                . $marginStyle;
            return '<div id="h18-clean-' . $id . '" class="h18-clean-front-node h18-clean-front-event-list" style="' . esc_attr($listStyle) . '">' . $cards . '</div>';
        }
'''
replace_between(renderer_rel, "        if ($type === 'eventlist') {\n", "        if ($type === 'eventdetail') {\n", renderer_eventlist, 'Alpha.17 eventlist frontend')

js_rel = 'assets/editor-v018-core.js'
js_norm = r'''        if (type === 'eventlist') {
            const orderBy=['start','title','updatedAt'].includes(String(raw.orderBy||'start'))?String(raw.orderBy||'start'):'start';
            const order=String(raw.order||'ASC').toUpperCase()==='DESC'?'DESC':'ASC';
            const limit=clamp(parseInt(raw.limit||50,10)||50,1,100);
            const dateFilter=['all','upcoming','past'].includes(String(raw.dateFilter||'upcoming'))?String(raw.dateFilter||'upcoming'):'upcoming';
            const minCardWidth=clamp(parseInt(raw.minCardWidth||280,10)||280,160,600);
            const maxCardWidth=Math.max(minCardWidth,clamp(parseInt(raw.maxCardWidth||360,10)||360,160,720));
            const cardAlign=['left','center','right'].includes(String(raw.cardAlign||'left'))?String(raw.cardAlign||'left'):'left';
            const imageRatio=['16:10','16:9','4:3','custom'].includes(String(raw.imageRatio||'16:10'))?String(raw.imageRatio||'16:10'):'16:10';
            return Object.assign(common,{binding:{schema:1,mode:'module',module:'events',view:'list',recordId:'',query:{status:'publish',orderBy:orderBy,order:order,limit:limit},fieldMap:{}},limit:limit,orderBy:orderBy,order:order,dateFilter:dateFilter,detailPageId:parseInt(raw.detailPageId||0,10)||0,columns:clamp(parseInt(raw.columns||3,10)||3,1,4),minCardWidth:minCardWidth,maxCardWidth:maxCardWidth,cardAlign:cardAlign,cardGap:clamp(parseInt(raw.cardGap||18,10)||18,0,80),cardPadding:clamp(parseInt(raw.cardPadding||20,10)||20,0,60),imageRatio:imageRatio,imageHeight:clamp(parseInt(raw.imageHeight||180,10)||180,60,600),showImage:raw.showImage!==false,showDate:raw.showDate!==false,showLocation:raw.showLocation!==false,showSummary:raw.showSummary!==false,linkCards:raw.linkCards!==false,cardBackground:normalizeColor(raw.cardBackground||'#f2f0e8'),textColor:normalizeColor(raw.textColor||'#30382a'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),cardRadius:clamp(parseInt(raw.cardRadius||8,10)||8,0,60)});
        }
'''
replace_between(js_rel, "        if (type === 'eventlist') {\n", "        if (type === 'eventdetail') {\n", js_norm, 'Alpha.17 designer eventlist normalization')

preview_old = """        } else if (node.type === 'eventlist') {\n            wrap.classList.add('h18-clean-node-preview--eventlist'); let records=eventRecords().filter(function(record){return String(record.status||'')==='publish';}); if(node.props.dateFilter==='upcoming'){records=records.filter(function(record){return !eventIsPast(record);});}else if(node.props.dateFilter==='past'){records=records.filter(eventIsPast);} records=records.slice(0,node.props.limit||50);\n            const grid=document.createElement('div'); grid.className='h18-vd-event-list-preview'; grid.style.gridTemplateColumns='repeat('+String(node.props.columns||3)+',minmax(0,1fr))'; grid.style.gap=String(node.props.cardGap||18)+'px'; if(!records.length){grid.textContent='Ingen publicerede events matcher filteret · opret dem under Manager → Events';}\n            records.forEach(function(record){const card=document.createElement('article'); card.className='h18-vd-event-card-preview'; card.style.padding=String(node.props.cardPadding||12)+'px'; card.style.borderRadius=String(node.props.cardRadius||4)+'px'; card.style.background=node.props.cardBackground||'#ffffff'; card.style.color=node.props.textColor||'#30382a'; if(node.props.showImage!==false&&record.featuredUrl){const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt='';img.style.height=String(node.props.imageHeight||180)+'px';card.appendChild(img);} const title=document.createElement('strong');title.textContent=String(record.title||'Event');card.appendChild(title);const fields=record.fields&&typeof record.fields==='object'?record.fields:{};if(node.props.showDate!==false&&eventDateLabel(record)){const meta=document.createElement('small');meta.textContent=eventDateLabel(record);meta.style.color=node.props.accentColor||'#c3ae83';card.appendChild(meta);}if(node.props.showLocation!==false&&fields.location){const loc=document.createElement('small');loc.textContent=String(fields.location);card.appendChild(loc);}if(node.props.showSummary!==false&&record.summary){const p=document.createElement('p');p.textContent=String(record.summary);card.appendChild(p);}grid.appendChild(card);}); wrap.appendChild(grid);\n"""
preview_new = """        } else if (node.type === 'eventlist') {\n            wrap.classList.add('h18-clean-node-preview--eventlist'); let records=eventRecords().filter(function(record){return String(record.status||'')==='publish';}); if(node.props.dateFilter==='upcoming'){records=records.filter(function(record){return !eventIsPast(record);});}else if(node.props.dateFilter==='past'){records=records.filter(eventIsPast);} records=records.slice(0,node.props.limit||50);\n            const grid=document.createElement('div'); grid.className='h18-vd-event-list-preview'; const minCardWidth=parseInt(node.props.minCardWidth||280,10)||280; const maxCardWidth=Math.max(minCardWidth,parseInt(node.props.maxCardWidth||360,10)||360); const columns=parseInt(node.props.columns||3,10)||3; const cardGap=parseInt(node.props.cardGap||18,10)||18; grid.style.gridTemplateColumns='repeat(auto-fit,minmax(min(100%,'+String(minCardWidth)+'px),'+String(maxCardWidth)+'px))'; grid.style.gap=String(cardGap)+'px'; grid.style.maxWidth=String((columns*maxCardWidth)+(Math.max(0,columns-1)*cardGap))+'px'; grid.style.justifyContent=node.props.cardAlign==='center'?'center':(node.props.cardAlign==='right'?'end':'start'); grid.style.marginLeft=node.props.cardAlign==='center'||node.props.cardAlign==='right'?'auto':'0'; grid.style.marginRight=node.props.cardAlign==='center'||node.props.cardAlign==='left'?'auto':'0'; if(!records.length){grid.textContent='Ingen publicerede events matcher filteret · opret dem under Manager → Events';}\n            records.forEach(function(record){const card=document.createElement('article'); card.className='h18-vd-event-card-preview'; card.style.padding=String(node.props.cardPadding||20)+'px'; card.style.borderRadius=String(node.props.cardRadius||8)+'px'; card.style.background=node.props.cardBackground||'#f2f0e8'; card.style.color=node.props.textColor||'#30382a'; if(node.props.showImage!==false&&record.featuredUrl){const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt='';const ratio=String(node.props.imageRatio||'16:10');if(ratio==='custom'){img.style.height=String(node.props.imageHeight||180)+'px';}else{img.style.height='auto';img.style.aspectRatio=ratio.replace(':',' / ');}img.style.objectFit='cover';card.appendChild(img);} const title=document.createElement('strong');title.textContent=String(record.title||'Event');card.appendChild(title);const fields=record.fields&&typeof record.fields==='object'?record.fields:{};if(node.props.showDate!==false&&eventDateLabel(record)){const meta=document.createElement('small');meta.textContent=eventDateLabel(record);meta.style.color=node.props.accentColor||'#c3ae83';card.appendChild(meta);}if(node.props.showLocation!==false&&fields.location){const loc=document.createElement('small');loc.textContent=String(fields.location);card.appendChild(loc);}if(node.props.showSummary!==false&&record.summary){const p=document.createElement('p');p.textContent=String(record.summary);card.appendChild(p);}grid.appendChild(card);}); wrap.appendChild(grid);\n"""
replace_once(js_rel, preview_old, preview_new, 'Alpha.17 eventlist preview')

inspector_old = """        } else if (node.type === 'eventlist') {\n            html += '<div class=\"h18-vd-menu-group\"><h3>Eventliste</h3><p class=\"description\">Data kommer fra Manager → Events. Frontend viser kun publicerede records.</p><label>Detaljeside<select data-field=\"eventDetailPageId\"><option value=\"0\">Ingen link / vælg senere</option>'+(Array.isArray(CFG.pages)?CFG.pages.map(function(page){const id=parseInt(page.id||0,10)||0;return '<option value=\"'+id+'\"'+(parseInt(node.props.detailPageId||0,10)===id?' selected':'')+'>'+escapeHtml(String(page.title||('Side '+id)))+'</option>';}).join(''):'')+'</select></label>';\n            html += '<div class=\"h18-clean-field-grid\"><label>Visning<select data-field=\"eventDateFilter\"><option value=\"upcoming\"'+(node.props.dateFilter==='upcoming'?' selected':'')+'>Kommende</option><option value=\"past\"'+(node.props.dateFilter==='past'?' selected':'')+'>Afholdte</option><option value=\"all\"'+(node.props.dateFilter==='all'?' selected':'')+'>Alle publicerede</option></select></label><label>Kolonner<input data-field=\"eventColumns\" type=\"number\" min=\"1\" max=\"4\" value=\"'+(node.props.columns||3)+'\"></label><label>Max. records<input data-field=\"eventLimit\" type=\"number\" min=\"1\" max=\"100\" value=\"'+(node.props.limit||50)+'\"></label><label>Sortér efter<select data-field=\"eventOrderBy\"><option value=\"start\"'+(node.props.orderBy==='start'?' selected':'')+'>Startdato</option><option value=\"title\"'+(node.props.orderBy==='title'?' selected':'')+'>Titel</option><option value=\"updatedAt\"'+(node.props.orderBy==='updatedAt'?' selected':'')+'>Senest ændret</option></select></label><label>Retning<select data-field=\"eventOrder\"><option value=\"ASC\"'+(node.props.order!=='DESC'?' selected':'')+'>Stigende</option><option value=\"DESC\"'+(node.props.order==='DESC'?' selected':'')+'>Faldende</option></select></label><label>Kortafstand px<input data-field=\"eventCardGap\" type=\"number\" min=\"0\" max=\"80\" value=\"'+(node.props.cardGap||18)+'\"></label><label>Kortpadding px<input data-field=\"eventCardPadding\" type=\"number\" min=\"0\" max=\"60\" value=\"'+(node.props.cardPadding||12)+'\"></label><label>Billedhøjde px<input data-field=\"eventImageHeight\" type=\"number\" min=\"60\" max=\"600\" value=\"'+(node.props.imageHeight||180)+'\"></label><label>Hjørner px<input data-field=\"eventCardRadius\" type=\"number\" min=\"0\" max=\"60\" value=\"'+(node.props.cardRadius||4)+'\"></label></div><label class=\"h18-clean-checkbox\"><input data-field=\"eventShowImage\" type=\"checkbox\"'+(node.props.showImage!==false?' checked':'')+'> Vis billede</label><label class=\"h18-clean-checkbox\"><input data-field=\"eventShowDate\" type=\"checkbox\"'+(node.props.showDate!==false?' checked':'')+'> Vis dato/tid</label><label class=\"h18-clean-checkbox\"><input data-field=\"eventShowLocation\" type=\"checkbox\"'+(node.props.showLocation!==false?' checked':'')+'> Vis sted</label><label class=\"h18-clean-checkbox\"><input data-field=\"eventShowSummary\" type=\"checkbox\"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class=\"h18-clean-checkbox\"><input data-field=\"eventLinkCards\" type=\"checkbox\"'+(node.props.linkCards!==false?' checked':'')+'> Link kort til detaljeside med ?h18_event=record-id</label><div class=\"h18-clean-field-grid\"><label>Kortbaggrund<input data-field=\"eventCardBackground\" type=\"color\" value=\"'+escapeAttr(node.props.cardBackground||'#ffffff')+'\"></label><label>Tekst<input data-field=\"textColor\" type=\"color\" value=\"'+escapeAttr(node.props.textColor||'#30382a')+'\"></label><label>Accent<input data-field=\"eventAccentColor\" type=\"color\" value=\"'+escapeAttr(node.props.accentColor||'#c3ae83')+'\"></label></div></div>'; if(CFG.eventAdminUrl){html+='<p><a class=\"button\" href=\"'+escapeAttr(String(CFG.eventAdminUrl))+'\">Administrér events</a></p>';}\n"""
inspector_new = """        } else if (node.type === 'eventlist') {\n            html += '<div class=\"h18-vd-menu-group\"><h3>Eventliste</h3><p class=\"description\">Data kommer fra Manager → Events. Frontend viser kun publicerede records. V1-standard for kort er 280–360 px.</p><label>Detaljeside<select data-field=\"eventDetailPageId\"><option value=\"0\">Ingen link / vælg senere</option>'+(Array.isArray(CFG.pages)?CFG.pages.map(function(page){const id=parseInt(page.id||0,10)||0;return '<option value=\"'+id+'\"'+(parseInt(node.props.detailPageId||0,10)===id?' selected':'')+'>'+escapeHtml(String(page.title||('Side '+id)))+'</option>';}).join(''):'')+'</select></label>';\n            html += '<div class=\"h18-clean-field-grid\"><label>Visning<select data-field=\"eventDateFilter\"><option value=\"upcoming\"'+(node.props.dateFilter==='upcoming'?' selected':'')+'>Kommende</option><option value=\"past\"'+(node.props.dateFilter==='past'?' selected':'')+'>Afholdte</option><option value=\"all\"'+(node.props.dateFilter==='all'?' selected':'')+'>Alle publicerede</option></select></label><label>Maks. kolonner<input data-field=\"eventColumns\" type=\"number\" min=\"1\" max=\"4\" value=\"'+(node.props.columns||3)+'\"></label><label>Min. kortbredde px<input data-field=\"eventMinCardWidth\" type=\"number\" min=\"160\" max=\"600\" value=\"'+(node.props.minCardWidth||280)+'\"></label><label>Maks. kortbredde px<input data-field=\"eventMaxCardWidth\" type=\"number\" min=\"160\" max=\"720\" value=\"'+(node.props.maxCardWidth||360)+'\"></label><label>Kortjustering<select data-field=\"eventCardAlign\"><option value=\"left\"'+(node.props.cardAlign!=='center'&&node.props.cardAlign!=='right'?' selected':'')+'>Venstre</option><option value=\"center\"'+(node.props.cardAlign==='center'?' selected':'')+'>Centreret</option><option value=\"right\"'+(node.props.cardAlign==='right'?' selected':'')+'>Højre</option></select></label><label>Max. records<input data-field=\"eventLimit\" type=\"number\" min=\"1\" max=\"100\" value=\"'+(node.props.limit||50)+'\"></label><label>Sortér efter<select data-field=\"eventOrderBy\"><option value=\"start\"'+(node.props.orderBy==='start'?' selected':'')+'>Startdato</option><option value=\"title\"'+(node.props.orderBy==='title'?' selected':'')+'>Titel</option><option value=\"updatedAt\"'+(node.props.orderBy==='updatedAt'?' selected':'')+'>Senest ændret</option></select></label><label>Retning<select data-field=\"eventOrder\"><option value=\"ASC\"'+(node.props.order!=='DESC'?' selected':'')+'>Stigende</option><option value=\"DESC\"'+(node.props.order==='DESC'?' selected':'')+'>Faldende</option></select></label><label>Kortafstand px<input data-field=\"eventCardGap\" type=\"number\" min=\"0\" max=\"80\" value=\"'+(node.props.cardGap||18)+'\"></label><label>Kortpadding px<input data-field=\"eventCardPadding\" type=\"number\" min=\"0\" max=\"60\" value=\"'+(node.props.cardPadding||20)+'\"></label><label>Billedformat<select data-field=\"eventImageRatio\"><option value=\"16:10\"'+((node.props.imageRatio||'16:10')==='16:10'?' selected':'')+'>16:10 · V1</option><option value=\"16:9\"'+(node.props.imageRatio==='16:9'?' selected':'')+'>16:9</option><option value=\"4:3\"'+(node.props.imageRatio==='4:3'?' selected':'')+'>4:3</option><option value=\"custom\"'+(node.props.imageRatio==='custom'?' selected':'')+'>Fast højde</option></select></label><label>Billedhøjde px · kun Fast højde<input data-field=\"eventImageHeight\" type=\"number\" min=\"60\" max=\"600\" value=\"'+(node.props.imageHeight||180)+'\"></label><label>Hjørner px<input data-field=\"eventCardRadius\" type=\"number\" min=\"0\" max=\"60\" value=\"'+(node.props.cardRadius||8)+'\"></label></div><label class=\"h18-clean-checkbox\"><input data-field=\"eventShowImage\" type=\"checkbox\"'+(node.props.showImage!==false?' checked':'')+'> Vis billede</label><label class=\"h18-clean-checkbox\"><input data-field=\"eventShowDate\" type=\"checkbox\"'+(node.props.showDate!==false?' checked':'')+'> Vis dato/tid</label><label class=\"h18-clean-checkbox\"><input data-field=\"eventShowLocation\" type=\"checkbox\"'+(node.props.showLocation!==false?' checked':'')+'> Vis sted</label><label class=\"h18-clean-checkbox\"><input data-field=\"eventShowSummary\" type=\"checkbox\"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class=\"h18-clean-checkbox\"><input data-field=\"eventLinkCards\" type=\"checkbox\"'+(node.props.linkCards!==false?' checked':'')+'> Link kort til detaljeside med ?h18_event=record-id</label><div class=\"h18-clean-field-grid\"><label>Kortbaggrund<input data-field=\"eventCardBackground\" type=\"color\" value=\"'+escapeAttr(node.props.cardBackground||'#f2f0e8')+'\"></label><label>Tekst<input data-field=\"textColor\" type=\"color\" value=\"'+escapeAttr(node.props.textColor||'#30382a')+'\"></label><label>Accent<input data-field=\"eventAccentColor\" type=\"color\" value=\"'+escapeAttr(node.props.accentColor||'#c3ae83')+'\"></label></div></div>'; if(CFG.eventAdminUrl){html+='<p><a class=\"button\" href=\"'+escapeAttr(String(CFG.eventAdminUrl))+'\">Administrér events</a></p>';}\n"""
replace_once(js_rel, inspector_old, inspector_new, 'Alpha.17 eventlist inspector')

replace_once(js_rel, "                else if (field === 'eventColumns') { current.props.columns=clamp(parseInt(control.value||3,10)||3,1,4); }", "                else if (field === 'eventColumns') { current.props.columns=clamp(parseInt(control.value||3,10)||3,1,4); }\n                else if (field === 'eventMinCardWidth') { current.props.minCardWidth=clamp(parseInt(control.value||280,10)||280,160,600); if((current.props.maxCardWidth||360)<current.props.minCardWidth){current.props.maxCardWidth=current.props.minCardWidth;} }\n                else if (field === 'eventMaxCardWidth') { current.props.maxCardWidth=Math.max(current.props.minCardWidth||280,clamp(parseInt(control.value||360,10)||360,160,720)); }\n                else if (field === 'eventCardAlign') { current.props.cardAlign=['left','center','right'].includes(control.value)?control.value:'left'; }", 'Alpha.17 eventlist width handlers')
replace_once(js_rel, "                else if (field === 'eventCardPadding') { current.props.cardPadding=clamp(parseInt(control.value||12,10)||12,0,60); }", "                else if (field === 'eventCardPadding') { current.props.cardPadding=clamp(parseInt(control.value||20,10)||20,0,60); }\n                else if (field === 'eventImageRatio') { current.props.imageRatio=['16:10','16:9','4:3','custom'].includes(control.value)?control.value:'16:10'; }", 'Alpha.17 eventlist image ratio handler')
replace_once(js_rel, "                else if (field === 'eventCardRadius') { current.props.cardRadius=clamp(parseInt(control.value||4,10)||4,0,60); }", "                else if (field === 'eventCardRadius') { current.props.cardRadius=clamp(parseInt(control.value||8,10)||8,0,60); }", 'Alpha.17 eventlist radius default handler')

history_path = DEST / 'release-history.json'
history = json.loads(history_path.read_text(encoding='utf-8'))
rows = history.get('versions', []) if isinstance(history, dict) else []
if not isinstance(rows, list) or not rows or rows[0].get('version') != '3.0.0-alpha.16':
    raise SystemExit('Expected Alpha.16 release-history baseline missing')
alpha17 = {
    'version': VERSION,
    'date': '2026-09-07',
    'items': [
        'Eventliste bruger nu V1-lignende kompakte kort med standardbredde 280–360 px i stedet for at strække kort over hele sidens kolonner.',
        'Designer → Eventliste har nye indstillinger for minimum/maksimum kortbredde og venstre/centreret/højre kortjustering.',
        'Kolonner betyder nu maksimalt antal kort pr. række; Eventlistens maksimale bredde beregnes af kortbredde, antal kolonner og gap.',
        'Eventbilleder bruger 16:10 som V1-standard; 16:9, 4:3 og Fast højde kan vælges i Designer.',
        'Nye Eventlister bruger V1-standarderne 18 px gap, 20 px kortpadding, 8 px hjørner og lys kortbaggrund; eksisterende eksplicitte valg bevares.'
    ]
}
history_path.write_text(json.dumps({'versions': [alpha17] + rows}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

model = read(model_rel)
renderer = read(renderer_rel)
js = read(js_rel)
main = read('visual-designer-manager.php')
for token in ['Version: 3.0.0-alpha.17', "define('VDM_VERSION', '3.0.0-alpha.17');"]:
    if token not in main:
        raise SystemExit(f'Alpha.17 version token missing: {token}')
for token in ["'minCardWidth' => $minCardWidth", "'maxCardWidth' => $maxCardWidth", "'cardAlign' => $cardAlign", "'imageRatio' => $imageRatio", "cardPadding'] ?? 20", "cardRadius'] ?? 8"]:
    if token not in model:
        raise SystemExit(f'Alpha.17 model token missing: {token}')
for token in ['repeat(auto-fit,minmax(min(100%,', '$maxListWidth', "['16:10' => '16 / 10'", "max-width:' . $maxListWidth . 'px", "cardAlign === 'right'"]:
    if token not in renderer:
        raise SystemExit(f'Alpha.17 renderer token missing: {token}')
for token in ['eventMinCardWidth', 'eventMaxCardWidth', 'eventCardAlign', 'eventImageRatio', 'V1-standard for kort er 280–360 px', "imageRatio||'16:10'", 'Maks. kolonner']:
    if token not in js:
        raise SystemExit(f'Alpha.17 Designer token missing: {token}')

print('V3 Alpha.17 event-card sizing controls: PASS')
print('V1 280-360px compact card default: PASS')
print('Max columns + alignment + 16:10 image ratio: PASS')
