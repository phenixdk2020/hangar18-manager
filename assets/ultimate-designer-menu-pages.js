(function(){
    'use strict';
    const config=window.Hangar18MenuPages||{};
    const pages=Array.isArray(config.pages)?config.pages:[];
    const editor=document.querySelector('.h18-ud-menu-editor');
    const list=document.getElementById('h18-ud-menu-item-list');
    const addButton=document.getElementById('h18-ud-add-menu-item');
    if(!editor||!list||!addButton||!pages.length){return;}

    function field(row,suffix){return row.querySelector('[name$="['+suffix+']"]');}
    function activeRows(){return Array.from(list.querySelectorAll('.h18-ud-menu-item-card')).filter(function(row){return !row.classList.contains('is-removed');});}
    function pageRow(pageId){
        const id=String(pageId);
        return activeRows().find(function(row){
            const type=field(row,'Type'),target=field(row,'Target');
            return type&&type.value==='page'&&target&&String(target.value)===id;
        })||null;
    }
    function setValue(row,suffix,value){const el=field(row,suffix);if(el){el.value=String(value==null?'':value);el.dispatchEvent(new Event('input',{bubbles:true}));}}
    function addPage(page){
        if(pageRow(page.Id)){return;}
        addButton.click();
        const rows=activeRows();const row=rows[rows.length-1];if(!row){return;}
        setValue(row,'Id','page-'+page.Id);
        setValue(row,'Type','page');
        setValue(row,'Label',page.Title);
        setValue(row,'Target',page.Id);
        setValue(row,'Url',page.Url||'');
        const summary=row.querySelector('.h18-ud-menu-summary');if(summary){summary.textContent=page.Title+' · page';}
    }
    function removePage(page){
        const row=pageRow(page.Id);if(!row){return;}
        const button=row.querySelector('.h18-ud-remove-menu-item');
        if(button){button.click();}
    }
    function esc(value){const d=document.createElement('div');d.textContent=String(value==null?'':value);return d.innerHTML;}

    const panel=document.createElement('section');
    panel.className='h18-ud-menu-page-chooser';
    panel.innerHTML='<div class="h18-ud-menu-page-head"><div><h3>Tilgængelige sider</h3><p class="description">En side behøver ikke være i menuen. Markér kun de sider, der skal være menupunkter.</p></div><input type="search" class="h18-ud-menu-page-search" placeholder="Søg sider" aria-label="Søg tilgængelige sider"></div><div class="h18-ud-menu-page-list"></div>';
    const workspace=editor.querySelector('.h18-ud-menu-workspace');
    editor.insertBefore(panel,workspace||null);
    const pageList=panel.querySelector('.h18-ud-menu-page-list');
    const search=panel.querySelector('.h18-ud-menu-page-search');

    function render(){
        const q=String(search.value||'').trim().toLowerCase();
        pageList.innerHTML=pages.filter(function(page){return !q||String(page.Title||'').toLowerCase().includes(q)||String(page.Id).includes(q);}).map(function(page){
            const checked=!!pageRow(page.Id);
            return '<label class="h18-ud-menu-page-option"><input type="checkbox" data-page-id="'+esc(page.Id)+'" '+(checked?'checked':'')+'><span><strong>'+esc(page.Title)+'</strong><small>'+esc(page.Status)+' · ID '+esc(page.Id)+'</small></span></label>';
        }).join('')||'<p class="description">Ingen sider matcher søgningen.</p>';
    }
    pageList.addEventListener('change',function(event){
        const input=event.target.closest('input[data-page-id]');if(!input){return;}
        const page=pages.find(function(item){return String(item.Id)===String(input.dataset.pageId);});if(!page){return;}
        if(input.checked){addPage(page);}else{removePage(page);}render();
    });
    search.addEventListener('input',render);
    list.addEventListener('change',function(){window.setTimeout(render,0);});
    list.addEventListener('click',function(){window.setTimeout(render,0);});
    render();
})();
