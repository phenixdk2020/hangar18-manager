(function () {
    'use strict';

    const list = document.getElementById('h18-ud-menu-item-list');
    const preview = document.getElementById('h18-ud-menu-preview');
    const addButton = document.getElementById('h18-ud-add-menu-item');
    const editor = list && list.closest('.h18-ud-menu-editor');
    if (!list || !preview || !editor) { return; }

    let nextIndex = parseInt(list.dataset.nextIndex || '0', 10);
    if (!Number.isFinite(nextIndex)) { nextIndex = list.children.length; }
    let dragged = null;
    let previewDevice = 'desktop';
    let mobileOpen = false;

    const presetMeta = {
        'classic': { label: 'Klassisk menu', description: 'Horisontal/dropdown på desktop og normal navigation.' },
        'floating-pill': { label: 'Floating pill', description: 'Flydende afrundet navigation med kompakt maksimal bredde.' },
        'mega-menu': { label: 'Mega menu', description: 'Bredt panel med 3–5 kolonner og mulighed for ComponentId-paneler.' },
        'side-rail': { label: 'Side rail', description: 'Lodret navigation langs siden.' },
        'off-canvas-mobile': { label: 'Off-canvas mobile', description: 'Mobilpanel fra højre med overlay, focus trap og Escape-close ved frontend-cutover.' },
        'fullscreen-overlay': { label: 'Fullscreen overlay', description: 'Fuldskærmsnavigation med focus trap og scroll-lock ved frontend-cutover.' },
        'bottom-mobile': { label: 'Bottom mobile navigation', description: 'Fast mobilnavigation i bunden med safe-area hensyn.' },
        'none': { label: 'Ingen animation', description: 'Ingen hover/active motion.' },
        'motion-underline': { label: 'Underline', description: 'Animeret understregning uden layout shift.' },
        'motion-pill': { label: 'Pill', description: 'Aktivt/hover menupunkt vises som pill.' },
        'motion-slide': { label: 'Slide', description: 'Kort slide-bevægelse med reduced-motion fallback.' },
        'motion-icon': { label: 'Icon', description: 'Ikonmarkering på hover/aktivt punkt.' }
    };

    function esc(value) {
        const d = document.createElement('div');
        d.textContent = String(value == null ? '' : value);
        return d.innerHTML;
    }
    function activeRows() { return Array.from(list.querySelectorAll('.h18-ud-menu-item-card')).filter(r => !r.classList.contains('is-removed')); }
    function field(row, suffix) { return row.querySelector('[name$="[' + suffix + ']"]'); }
    function value(row, suffix, fallback) { const el = field(row, suffix); return el && el.value != null ? el.value : (fallback || ''); }
    function checked(row, suffix) { const controls = row.querySelectorAll('[name$="[' + suffix + ']"]'); let out=false; controls.forEach(el=>{if(el.type==='checkbox'&&el.checked){out=true;}}); return out; }
    function presentation(name, fallback) { const el=editor.querySelector('[name="presentation['+name+']"]'); if(!el){return fallback;} if(el.type==='checkbox'){return el.checked;} return el.value; }

    function rowHtml(index) {
        const id='item-'+(index+1);
        return [
            '<article class="h18-ud-menu-item-card" data-index="'+index+'" draggable="true">',
            '<div class="h18-ud-template-element-head"><span class="dashicons dashicons-move h18-ud-menu-drag" aria-hidden="true"></span>',
            '<strong class="h18-ud-menu-summary">Nyt menupunkt</strong>',
            '<span class="h18-ud-move-controls"><button type="button" class="button-link h18-ud-menu-up" aria-label="Flyt op">↑</button><button type="button" class="button-link h18-ud-menu-down" aria-label="Flyt ned">↓</button><button type="button" class="button-link h18-ud-menu-outdent" aria-label="Flyt et niveau ud">←</button><button type="button" class="button-link h18-ud-menu-indent" aria-label="Gør til underpunkt">→</button></span>',
            '<button type="button" class="button-link-delete h18-ud-remove-menu-item">Fjern</button></div>',
            '<div class="h18-ud-menu-item-grid">',
            '<label>Id<input type="text" name="items['+index+'][Id]" value="'+id+'"></label>',
            '<label>Parent Id<input type="text" name="items['+index+'][ParentId]" class="h18-ud-menu-parent"></label>',
            '<label>Type<select name="items['+index+'][Type]" class="h18-ud-menu-type"><option>page</option><option selected>url</option><option>taxonomy</option><option>dynamic</option><option>anchor</option><option>action</option></select></label>',
            '<label>Tekst/label<input type="text" name="items['+index+'][Label]" class="h18-ud-menu-label" value="Nyt punkt"></label>',
            '<label>URL<input type="text" name="items['+index+'][Url]"></label>',
            '<label>Target/anchor<input type="text" name="items['+index+'][Target]"></label>',
            '<label>Ikon<input type="text" name="items['+index+'][Icon]"></label>',
            '<label>Badge<input type="text" name="items['+index+'][Badge]"></label>',
            '<label class="is-wide">Beskrivelse<input type="text" name="items['+index+'][Description]"></label>',
            '<label class="is-wide">Mega-panel ComponentId<input type="text" name="items['+index+'][ComponentId]" class="h18-ud-component-id"></label>',
            '<label class="h18-ud-check"><input type="hidden" name="items['+index+'][OpenNew]" value="0"><input type="checkbox" name="items['+index+'][OpenNew]" value="1"> Åbn i nyt vindue</label>',
            '<input type="hidden" name="items['+index+'][Remove]" value="0" class="h18-ud-menu-remove">',
            '</div></article>'
        ].join('');
    }

    function renumber() {
        Array.from(list.querySelectorAll('.h18-ud-menu-item-card')).forEach((row,index)=>{
            row.dataset.index=String(index);
            row.querySelectorAll('[name]').forEach(control=>{control.name=control.name.replace(/items\[\d+\]/,'items['+index+']');});
        });
    }

    function rowId(row) { return String(value(row,'Id','')).trim(); }
    function parentId(row) { return String(value(row,'ParentId','')).trim(); }
    function depthFor(row, byId) {
        let depth=0,cursor=parentId(row),seen=new Set([rowId(row)]);
        while(cursor && byId.has(cursor) && !seen.has(cursor) && depth<6){seen.add(cursor);depth++;cursor=parentId(byId.get(cursor));}
        return depth;
    }
    function refreshIndentation() {
        const rows=activeRows(),byId=new Map();rows.forEach(row=>byId.set(rowId(row),row));
        rows.forEach(row=>{row.style.setProperty('--h18-menu-depth',String(depthFor(row,byId)));const summary=row.querySelector('.h18-ud-menu-summary');if(summary){summary.textContent=(value(row,'Label','')||rowId(row)||'Menupunkt')+' · '+value(row,'Type','url');}});
    }

    function move(row,delta){const rows=activeRows(),i=rows.indexOf(row),target=rows[i+delta];if(!target)return;if(delta<0)list.insertBefore(row,target);else list.insertBefore(target,row);renumber();refresh();row.scrollIntoView({block:'nearest'});}
    function indent(row){const rows=activeRows(),i=rows.indexOf(row);if(i<=0)return;const previous=rows[i-1],parentField=field(row,'ParentId');const previousId=rowId(previous);if(parentField&&previousId&&previousId!==rowId(row)){parentField.value=previousId;refresh();}}
    function outdent(row){const byId=new Map();activeRows().forEach(r=>byId.set(rowId(r),r));const parent=byId.get(parentId(row));const parentField=field(row,'ParentId');if(parentField){parentField.value=parent?parentId(parent):'';refresh();}}

    function previewItem(row,children,byId,depth){
        const id=rowId(row),label=String(value(row,'Label',id||'Punkt')),icon=String(value(row,'Icon','')),badge=String(value(row,'Badge','')),component=String(value(row,'ComponentId','')),description=String(value(row,'Description',''));
        const li=document.createElement('li');li.className='h18-ud-preview-menu-item';li.dataset.itemId=id;li.dataset.depth=String(depth);
        const link=document.createElement('button');link.type='button';link.className='h18-ud-preview-menu-link';link.dataset.itemId=id;
        if(presentation('ShowIcons',true) && icon){const span=document.createElement('span');span.className='h18-ud-preview-menu-icon';span.textContent=icon;span.setAttribute('aria-hidden','true');link.appendChild(span);}
        const text=document.createElement('span');text.textContent=label;link.appendChild(text);
        if(presentation('ShowBadges',true) && badge){const b=document.createElement('small');b.className='h18-ud-preview-menu-badge';b.textContent=badge;link.appendChild(b);}
        li.appendChild(link);
        const childRows=children.get(id)||[];
        if(childRows.length){link.setAttribute('aria-expanded','false');link.classList.add('has-children');const ul=document.createElement('ul');ul.className='h18-ud-preview-submenu';ul.hidden=true;childRows.forEach(child=>ul.appendChild(previewItem(child,children,byId,depth+1)));if(component&&presentation('DesktopPreset','classic')==='mega-menu'){const panel=document.createElement('li');panel.className='h18-ud-preview-component-panel';panel.textContent='Component panel: '+component;ul.appendChild(panel);}li.appendChild(ul);}
        if(description){li.title=description;}
        return li;
    }

    function renderPreview() {
        preview.innerHTML='';
        const rows=activeRows(),byId=new Map(),children=new Map();rows.forEach(r=>byId.set(rowId(r),r));
        rows.forEach(row=>{let p=parentId(row);if(!p||!byId.has(p)){p='';}if(!children.has(p))children.set(p,[]);children.get(p).push(row);});
        const desktop=String(presentation('DesktopPreset','classic')),mobile=String(presentation('MobilePreset','off-canvas-mobile')),motion=String(presentation('MotionPreset','motion-underline'));
        preview.className='h18-ud-menu-preview-canvas device-'+previewDevice+' desktop-'+desktop+' mobile-'+mobile+' motion-'+motion+(mobileOpen?' is-mobile-open':'');
        const control=document.createElement('div');control.className='h18-ud-preview-device-bar';control.innerHTML='<button type="button" data-preview-device="desktop" class="button '+(previewDevice==='desktop'?'button-primary':'')+'">Desktop</button><button type="button" data-preview-device="mobile" class="button '+(previewDevice==='mobile'?'button-primary':'')+'">Mobil</button>'+(previewDevice==='mobile'?'<button type="button" data-mobile-toggle class="button">'+esc(String(presentation('MobileToggleLabel','Menu')))+'</button>':'');preview.appendChild(control);
        const shell=document.createElement('nav');shell.className='h18-ud-preview-menu-shell';shell.setAttribute('aria-label',String(presentation('AriaLabel','Hovedmenu')));const ul=document.createElement('ul');ul.className='h18-ud-preview-menu-root';(children.get('')||[]).forEach(row=>ul.appendChild(previewItem(row,children,byId,0)));shell.appendChild(ul);preview.appendChild(shell);
        if(rows.length===0){shell.innerHTML='<p class="description">Ingen aktive menupunkter.</p>';}
        updatePresetInfo();
    }

    function closeSubmenus(focusParent){preview.querySelectorAll('.h18-ud-preview-menu-link[aria-expanded="true"]').forEach(link=>{link.setAttribute('aria-expanded','false');const sub=link.parentElement&&link.parentElement.querySelector(':scope > .h18-ud-preview-submenu');if(sub)sub.hidden=true;if(focusParent)link.focus();});}
    function topLinks(){return Array.from(preview.querySelectorAll('.h18-ud-preview-menu-root > .h18-ud-preview-menu-item > .h18-ud-preview-menu-link'));}
    function keyboard(event){const link=event.target.closest('.h18-ud-preview-menu-link');if(!link)return;const top=topLinks(),isTop=top.includes(link),li=link.parentElement,submenu=li&&li.querySelector(':scope > .h18-ud-preview-submenu');if(event.key==='Escape'){event.preventDefault();closeSubmenus(true);mobileOpen=false;renderPreview();return;}if(isTop&&(event.key==='ArrowRight'||event.key==='ArrowLeft')){event.preventDefault();const i=top.indexOf(link),delta=event.key==='ArrowRight'?1:-1;top[(i+delta+top.length)%top.length].focus();return;}if(event.key==='ArrowDown'&&submenu){event.preventDefault();submenu.hidden=false;link.setAttribute('aria-expanded','true');const first=submenu.querySelector('.h18-ud-preview-menu-link');if(first)first.focus();return;}if(event.key==='ArrowUp'&&!isTop){event.preventDefault();const siblings=Array.from(li.parentElement.querySelectorAll(':scope > .h18-ud-preview-menu-item > .h18-ud-preview-menu-link')),i=siblings.indexOf(link);if(i>0)siblings[i-1].focus();else{const parentLi=li.parentElement.closest('.h18-ud-preview-menu-item');const parentLink=parentLi&&parentLi.querySelector(':scope > .h18-ud-preview-menu-link');if(parentLink)parentLink.focus();}}
    }

    function updatePresetInfo(){const target=document.getElementById('h18-ud-menu-preset-info');if(!target)return;const keys=[presentation('DesktopPreset','classic'),presentation('MobilePreset','off-canvas-mobile'),presentation('MotionPreset','motion-underline')];target.innerHTML=keys.map(key=>{const meta=presetMeta[key]||{label:key,description:''};return '<div><strong>'+esc(meta.label)+'</strong><span>'+esc(meta.description)+'</span></div>';}).join('');const mega=editor.querySelectorAll('.h18-ud-component-id');mega.forEach(el=>{const label=el.closest('label');if(label)label.classList.toggle('is-preset-relevant',presentation('DesktopPreset','classic')==='mega-menu');});}
    function refresh(){renumber();refreshIndentation();renderPreview();}

    if(addButton){addButton.addEventListener('click',()=>{list.insertAdjacentHTML('beforeend',rowHtml(nextIndex++));refresh();const rows=activeRows();const last=rows[rows.length-1];if(last)last.scrollIntoView({block:'nearest'});});}
    list.addEventListener('click',event=>{const row=event.target.closest('.h18-ud-menu-item-card');if(!row)return;if(event.target.closest('.h18-ud-remove-menu-item')){event.preventDefault();const remove=field(row,'Remove');if(remove){remove.value='1';row.classList.add('is-removed');refresh();}return;}if(event.target.closest('.h18-ud-menu-up')){event.preventDefault();move(row,-1);}else if(event.target.closest('.h18-ud-menu-down')){event.preventDefault();move(row,1);}else if(event.target.closest('.h18-ud-menu-indent')){event.preventDefault();indent(row);}else if(event.target.closest('.h18-ud-menu-outdent')){event.preventDefault();outdent(row);}});
    list.addEventListener('dragstart',event=>{const row=event.target.closest('.h18-ud-menu-item-card');if(!row||!event.target.closest('.h18-ud-menu-drag')){event.preventDefault();return;}dragged=row;row.classList.add('is-dragging');if(event.dataTransfer){event.dataTransfer.effectAllowed='move';event.dataTransfer.setData('text/plain',row.dataset.index||'');}});
    list.addEventListener('dragover',event=>{if(!dragged)return;event.preventDefault();const target=event.target.closest('.h18-ud-menu-item-card');if(!target||target===dragged||target.classList.contains('is-removed'))return;const rect=target.getBoundingClientRect(),after=event.clientY>rect.top+rect.height/2;list.insertBefore(dragged,after?target.nextSibling:target);});
    list.addEventListener('drop',event=>{if(!dragged)return;event.preventDefault();dragged.classList.remove('is-dragging');dragged=null;refresh();});
    list.addEventListener('dragend',()=>{if(dragged)dragged.classList.remove('is-dragging');dragged=null;refresh();});
    list.addEventListener('input',refresh);list.addEventListener('change',refresh);
    editor.addEventListener('input',event=>{if(event.target.closest('.h18-ud-menu-presentation'))renderPreview();});editor.addEventListener('change',event=>{if(event.target.closest('.h18-ud-menu-presentation'))renderPreview();});editor.addEventListener('submit',renumber);
    preview.addEventListener('click',event=>{const device=event.target.closest('[data-preview-device]');if(device){previewDevice=device.dataset.previewDevice;mobileOpen=false;renderPreview();return;}if(event.target.closest('[data-mobile-toggle]')){mobileOpen=!mobileOpen;renderPreview();return;}const link=event.target.closest('.h18-ud-preview-menu-link.has-children');if(link){const sub=link.parentElement.querySelector(':scope > .h18-ud-preview-submenu'),open=link.getAttribute('aria-expanded')==='true';link.setAttribute('aria-expanded',open?'false':'true');if(sub)sub.hidden=open;}});
    preview.addEventListener('keydown',keyboard);

    activeRows().forEach(row=>{row.draggable=true;});
    new MutationObserver(mutations=>mutations.forEach(m=>m.addedNodes.forEach(node=>{if(node.nodeType===1&&node.classList.contains('h18-ud-menu-item-card'))node.draggable=true;}))).observe(list,{childList:true});
    refresh();
})();
