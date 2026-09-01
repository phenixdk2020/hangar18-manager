from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

# EditorController: target only the render-time collection state and module-panel branch.
p=ROOT/'clean/hangar18-manager/src/Admin/EditorController.php'
s=p.read_text(encoding='utf-8')
old="        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $moduleDesign = $isCollectionPage ? ModuleDesignModel::get($postId) : [];"
new="        $isCollectionPage = CollectionPageRenderer::supports($postId);\n        $collectionMode = $isCollectionPage && sanitize_key((string) ($_GET['h18_collection_mode'] ?? 'content')) === 'module' ? 'module' : 'content';\n        $moduleDesign = $isCollectionPage ? ModuleDesignModel::get($postId) : [];"
if new not in s:
    if old not in s: raise SystemExit('EditorController render collection anchor missing')
    s=s.replace(old,new,1)
old_panel="        if ($isCollectionPage) {\n            $moduleSlug = sanitize_title((string) get_post_field('post_name', $postId));"
new_panel="        if ($isCollectionPage && $collectionMode === 'module') {\n            $moduleSlug = sanitize_title((string) get_post_field('post_name', $postId));"
if new_panel not in s:
    if old_panel not in s: raise SystemExit('EditorController module panel anchor missing')
    s=s.replace(old_panel,new_panel,1)
p.write_text(s,encoding='utf-8')

# editor-v018-core.js has two gallerylist branches: canvas preview and Inspector.
# Insert Eventfelt in each branch by classifying its surrounding code instead of
# relying on an ambiguous raw anchor.
js_path=ROOT/'clean/hangar18-manager/assets/editor-v018-core.js'
js=js_path.read_text(encoding='utf-8')
needle="        } else if (node.type === 'gallerylist') {"

preview_code="""        } else if (node.type === 'eventfield') {
            wrap.classList.add('h18-clean-node-preview--eventfield'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[]; const def=defs.find(function(row){return String(row.id||'')===String(node.props.fieldKey||'');})||null; const attr=record&&Array.isArray(record.attributes)?record.attributes.find(function(row){return row&&String(row.key||'')===String(node.props.fieldKey||'');}):null; const box=document.createElement('div');box.style.padding=String(node.props.padding||0)+'px';box.style.borderRadius=String(node.props.radius||0)+'px';box.style.color=node.props.textColor||'#30382a';if(node.props.background){box.style.background=node.props.background;} if(!record||!attr||String(attr.value==null?'':attr.value)===''){box.textContent='Eventfelt · '+String(def&&def.label||node.props.fieldKey||'vælg felt');}else{if(node.props.showHeading!==false){const h=document.createElement('h3');h.textContent=String(def&&def.label||attr.label||node.props.fieldKey);box.appendChild(h);}const value=document.createElement('div'); if(String(def&&def.type||attr.type)==='richtext'){value.innerHTML=richPreviewHtml(String(attr.value||''));}else{value.textContent=typeof attr.value==='boolean'?(attr.value?'Ja':'Nej'):String(attr.value);}box.appendChild(value);}wrap.appendChild(box);
"""
inspector_code="""        } else if (node.type === 'eventfield') {
            const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[]; html += '<div class=\"h18-vd-menu-group\"><h3>Eventfelt</h3><label>Felt<select data-field=\"eventFieldKey\">'+defs.map(function(row){return '<option value=\"'+escapeAttr(String(row.id||''))+'\"'+(String(node.props.fieldKey||'')===String(row.id||'')?' selected':'')+'>'+escapeHtml(String(row.label||row.id||'Felt'))+'</option>';}).join('')+'</select></label><label>Preview-event<select data-field=\"eventRecordId\"><option value=\"\">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value=\"'+escapeAttr(String(record.id||''))+'\"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><label class=\"h18-clean-checkbox\"><input data-field=\"eventFieldShowHeading\" type=\"checkbox\"'+(node.props.showHeading!==false?' checked':'')+'> Vis feltoverskrift</label><div class=\"h18-clean-field-grid\"><label>Padding<input data-field=\"padding\" type=\"number\" min=\"0\" max=\"80\" value=\"'+String(node.props.padding||0)+'\"></label><label>Hjørner<input data-field=\"radius\" type=\"number\" min=\"0\" max=\"60\" value=\"'+String(node.props.radius||0)+'\"></label><label>Baggrund<input data-field=\"background\" type=\"color\" value=\"'+escapeAttr(node.props.background||'#ffffff')+'\"></label><label>Tekst<input data-field=\"textColor\" type=\"color\" value=\"'+escapeAttr(node.props.textColor||'#30382a')+'\"></label></div></div>';
"""

if "node.type === 'eventfield'" not in js:
    positions=[]; start=0
    while True:
        idx=js.find(needle,start)
        if idx<0: break
        positions.append(idx); start=idx+len(needle)
    if len(positions)!=2:
        raise SystemExit(f'Expected exactly 2 gallerylist JS branches, found {len(positions)}')
    classified={}
    for idx in positions:
        before=js[max(0,idx-5000):idx]
        if 'wrap.appendChild(box)' in before and "node.type === 'eventdetail'" in before:
            classified['preview']=idx
        elif '<h3>Eventdetalje</h3>' in before and 'html +=' in before:
            classified['inspector']=idx
    if set(classified)!={'preview','inspector'}:
        raise SystemExit(f'Could not classify gallerylist JS branches: {sorted(classified)}')
    for kind,idx in sorted(classified.items(), key=lambda item:item[1], reverse=True):
        code=preview_code if kind=='preview' else inspector_code
        js=js[:idx]+code+js[idx:]

# Section uses the generic Inspector branch. Add a real slot selector there and
# expose the section's minimum height using the existing canonical gh handler.
slot_marker="<label>Placering på modulside<select data-field=\"moduleSlot\"><option value=\"before\"'+(node.props.moduleSlot==='before'?' selected':'')+'>Før modulindhold</option><option value=\"between\"'+(node.props.moduleSlot==='between'?' selected':'')+'>Mellem modulsektioner</option><option value=\"after\"'+(node.props.moduleSlot==='after'?' selected':'')+'>Efter modulindhold</option></select></label><label>Minimumshøjde"
if slot_marker not in js:
    anchor="        } else {\n            html += '<label>Baggrund<input data-field=\"background\" type=\"color\" value=\"' + escapeAttr(node.props.background || '#ffffff') + '\"></label>';"
    replacement="        } else {\n            if (node.type === 'section') { html += '<label>Placering på modulside<select data-field=\"moduleSlot\"><option value=\"before\"'+(node.props.moduleSlot==='before'?' selected':'')+'>Før modulindhold</option><option value=\"between\"'+(node.props.moduleSlot==='between'?' selected':'')+'>Mellem modulsektioner</option><option value=\"after\"'+(node.props.moduleSlot==='after'?' selected':'')+'>Efter modulindhold</option></select></label><label>Minimumshøjde · 8px<input data-field=\"gh\" type=\"number\" min=\"0\" value=\"'+String(node.props.minHeightRows||node.geometry.desktop.h||0)+'\"></label>'; }\n            html += '<label>Baggrund<input data-field=\"background\" type=\"color\" value=\"' + escapeAttr(node.props.background || '#ffffff') + '\"></label>';"
    if anchor not in js:
        raise SystemExit('Section generic Inspector anchor missing')
    js=js.replace(anchor,replacement,1)

js_path.write_text(js,encoding='utf-8')
print('v0.1.78 pre-apply anchors ready')
