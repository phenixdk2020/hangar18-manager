(function(){
    'use strict';
    const cfg=window.Hangar18Portability||{};
    const maxJson=Number(cfg.maxJson||1048576);
    function request(action,payload){
        const body=new URLSearchParams(Object.assign({action:action,nonce:String(cfg.nonce||'')},payload||{}));
        return fetch(String(cfg.ajaxUrl||''),{method:'POST',credentials:'same-origin',headers:{'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'},body:body.toString()}).then(function(r){return r.json();});
    }
    function escapeHtml(value){const d=document.createElement('div');d.textContent=String(value==null?'':value);return d.innerHTML;}
    function jsonOk(value){return value.trim()!==''&&new Blob([value]).size<=maxJson;}

    const pageJson=document.getElementById('h18-ud-page-package-json');
    const pageButton=document.getElementById('h18-ud-preview-page-package');
    const pageResult=document.getElementById('h18-ud-page-package-result');
    if(pageJson&&pageButton&&pageResult){
        pageButton.addEventListener('click',function(){
            const value=pageJson.value||'';pageResult.className='h18-ud-port-result';
            if(!jsonOk(value)){pageResult.textContent='JSON mangler eller er større end 1 MB.';pageResult.classList.add('is-error');return;}
            pageButton.disabled=true;pageResult.textContent='Validerer…';
            request('h18_ud_preview_page_import',{package_json:value}).then(function(res){
                if(!res||!res.success){throw new Error(res&&res.data&&res.data.message?res.data.message:'Validering fejlede.');}
                const d=res.data||{};pageResult.classList.add('is-success');pageResult.innerHTML='<strong>Gyldig sidepakke</strong><dl><dt>Side</dt><dd>'+escapeHtml(d.PageTitle)+' <code>'+escapeHtml(d.PageSlug)+'</code></dd><dt>Elementer</dt><dd>'+escapeHtml(d.Sections)+'</dd><dt>Checksum</dt><dd><code>'+escapeHtml(String(d.PageChecksum||'').slice(0,20))+'…</code></dd><dt>Write</dt><dd>Låst til I10</dd></dl>';
            }).catch(function(err){pageResult.classList.add('is-error');pageResult.textContent=err.message||String(err);}).finally(function(){pageButton.disabled=false;});
        });
    }

    const form=document.getElementById('h18-ud-artifact-import-form');
    const packageJson=document.getElementById('h18-ud-artifact-package-json');
    const strategy=document.getElementById('h18-ud-import-strategy');
    const dryButton=document.getElementById('h18-ud-run-import-dry-run');
    const planResult=document.getElementById('h18-ud-import-plan-result');
    const token=document.getElementById('h18-ud-import-plan-token');
    const confirm=document.getElementById('h18-ud-confirm-import');
    const submit=document.getElementById('h18-ud-confirm-import-button');
    function invalidate(){if(token){token.value='';}if(confirm){confirm.checked=false;confirm.disabled=true;}if(submit){submit.disabled=true;}if(planResult){planResult.innerHTML='';planResult.className='h18-ud-port-result';}}
    if(packageJson){packageJson.addEventListener('input',invalidate);}if(strategy){strategy.addEventListener('change',invalidate);}
    if(confirm&&submit){confirm.addEventListener('change',function(){submit.disabled=!confirm.checked||!token.value;});}
    if(dryButton&&packageJson&&strategy&&planResult&&token&&confirm&&submit){
        dryButton.addEventListener('click',function(){
            const value=packageJson.value||'';invalidate();if(!jsonOk(value)){planResult.textContent='Artifact JSON mangler eller er større end 1 MB.';planResult.classList.add('is-error');return;}
            dryButton.disabled=true;planResult.textContent='Kører dry-run…';
            request('h18_ud_plan_artifact_import',{package_json:value,strategy:strategy.value}).then(function(res){
                if(!res||!res.success){throw new Error(res&&res.data&&res.data.message?res.data.message:'Dry-run fejlede.');}
                const d=res.data||{},p=d.plan||{},conflicts=Array.isArray(p.Conflicts)?p.Conflicts:[],actions=Array.isArray(p.Actions)?p.Actions:[],assets=Array.isArray(d.UnresolvedAssetRefs)?d.UnresolvedAssetRefs:[],broken=Array.isArray(d.BrokenArtifactRefs)?d.BrokenArtifactRefs:[];
                const rows=actions.map(function(a){return '<tr><td><code>'+escapeHtml(a.ExportId)+'</code></td><td>'+escapeHtml(a.Action)+'</td><td><code>'+escapeHtml(a.TargetId||'—')+'</code></td></tr>';}).join('');
                planResult.innerHTML='<strong>Dry-run '+(d.ReadyForImport?'klar':'blokeret')+'</strong><div class="h18-ud-plan-summary"><span>'+actions.length+' actions</span><span>'+conflicts.length+' conflicts</span><span>'+assets.length+' asset refs</span><span>'+broken.length+' broken refs</span></div><table><thead><tr><th>Artifact</th><th>Handling</th><th>Target</th></tr></thead><tbody>'+rows+'</tbody></table>'+(conflicts.length?'<details><summary>Conflicts</summary><pre>'+escapeHtml(JSON.stringify(conflicts,null,2))+'</pre></details>':'')+(assets.length?'<p class="h18-ud-blocker"><strong>Uløste asset refs:</strong> '+assets.map(escapeHtml).join(', ')+'</p>':'')+(broken.length?'<p class="h18-ud-blocker"><strong>Broken artifact refs:</strong> '+broken.map(escapeHtml).join(', ')+'</p>':'')+'<p>'+escapeHtml(d.message||'')+'</p>';
                planResult.classList.add(d.ReadyForImport?'is-success':'is-warning');
                if(d.ReadyForImport&&d.planToken){token.value=d.planToken;confirm.disabled=false;}
            }).catch(function(err){planResult.classList.add('is-error');planResult.textContent=err.message||String(err);}).finally(function(){dryButton.disabled=false;});
        });
    }
    if(form){form.addEventListener('submit',function(event){if(!token.value||!confirm.checked){event.preventDefault();window.alert('Kør og gennemgå en gyldig dry-run før import.');}});}
})();
