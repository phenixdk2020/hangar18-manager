(function () {
    'use strict';

    var CFG = window.H18CleanEditor || {};
    var POST_ID = parseInt(CFG.postId || 0, 10) || 0;
    var CONTEXT = String(CFG.contextLabel || 'Visual Designer');
    var AUTOSAVE_KEY = 'vdm_suite_autosave_v1_' + String(POST_ID || CONTEXT);
    var LOCAL_COMPONENTS_KEY = 'vdm_suite_local_components_v1';
    var FAV_KEY = 'vdm_suite_inspector_favorites_v1';
    var selected = new Set();
    var bootModel = null;
    var dirty = false;
    var suiteData = { components: [], tokens: {} };
    var safeArea = false;
    var currentPreset = '';
    var currentPresetWidth = 0;
    var focusPointMode = false;
    var layerDragId = '';
    var autosaveTimer = 0;
    var bootstrapReady = false;

    function api() { return window.H18VDDesigner || {}; }
    function clone(value) { return JSON.parse(JSON.stringify(value)); }
    function q(selector, root) { return (root || document).querySelector(selector); }
    function qa(selector, root) { return Array.prototype.slice.call((root || document).querySelectorAll(selector)); }
    function esc(value) { return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) { return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'})[c]; }); }
    function uid(prefix) { return String(prefix || 'node') + '-suite-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2,8); }

    function model() {
        var bridge = api();
        if (typeof bridge.getModel === 'function') { return bridge.getModel(); }
        var field = document.getElementById('h18-clean-model-json');
        try { return JSON.parse(field ? field.value || '{}' : '{}'); } catch (ignore) { return {schemaVersion:1,units:120,rowPx:8,nodes:[]}; }
    }
    function applyModel(next, label, selectId) {
        var bridge = api();
        if (typeof bridge.applyModel === 'function') { return bridge.applyModel(next, label || 'Designer+ ændring', selectId || ''); }
        return false;
    }
    function mutate(label, fn) {
        var bridge = api();
        if (typeof bridge.mutate === 'function') {
            return bridge.mutate(fn, label || 'Designer+ ændring');
        }
        var next = model();
        fn(next);
        return applyModel(next, label || 'Designer+ ændring');
    }
    function activeDevice() {
        return document.body ? String(document.body.getAttribute('data-h18-clean-device') || 'desktop') : 'desktop';
    }
    function nodeById(id, source) {
        source = source || model();
        return (Array.isArray(source.nodes) ? source.nodes : []).find(function (node) { return node && String(node.id || '') === String(id || ''); }) || null;
    }
    function childrenOf(id, source) {
        source = source || model();
        return (Array.isArray(source.nodes) ? source.nodes : []).filter(function (node) { return node && String(node.parentId || '') === String(id || ''); }).sort(function (a,b) { return (parseInt(a.order||0,10)||0)-(parseInt(b.order||0,10)||0); });
    }
    function descendantIds(id, source) {
        source = source || model();
        var out = [], queue = [String(id || '')];
        while (queue.length) {
            var parent = queue.shift();
            childrenOf(parent, source).forEach(function (node) { out.push(String(node.id)); queue.push(String(node.id)); });
        }
        return out;
    }
    function selectedId() {
        var bridge = api();
        if (typeof bridge.selectedId === 'function') { return String(bridge.selectedId() || ''); }
        return selected.size ? Array.from(selected)[selected.size - 1] : '';
    }
    function selectionIds() {
        var ids = Array.from(selected).filter(function (id) { return !!nodeById(id); });
        if (!ids.length) {
            var id = selectedId();
            if (id) { ids = [id]; }
        }
        return ids;
    }

    function suiteAjax(op, payload) {
        var body = new URLSearchParams();
        body.set('action', 'vdm_designer_suite');
        body.set('nonce', String(CFG.suiteNonce || ''));
        body.set('op', op);
        Object.keys(payload || {}).forEach(function (key) { body.set(key, String(payload[key] == null ? '' : payload[key])); });
        return fetch(String(CFG.ajaxUrl || ''), {
            method: 'POST',
            credentials: 'same-origin',
            headers: {'Content-Type':'application/x-www-form-urlencoded;charset=UTF-8'},
            body: body.toString(),
            cache: 'no-store'
        }).then(function (response) { return response.json(); }).then(function (json) {
            if (!json || !json.success) { throw new Error(json && json.data && json.data.message ? json.data.message : 'Designer Suite-handlingen fejlede.'); }
            return json.data || {};
        });
    }

    function notice(message, type) {
        var host = document.getElementById('h18-suite-notice');
        if (!host) { return; }
        host.className = 'h18-suite-card ' + (type === 'error' ? 'h18-suite-bad' : type === 'warn' ? 'h18-suite-warn' : 'h18-suite-good');
        host.textContent = String(message || '');
        host.hidden = !message;
        if (message) { window.setTimeout(function () { if (host.textContent === message) { host.hidden = true; } }, 4200); }
    }

    function installLaunch() {
        var toolbar = q('.h18-clean-toolbar');
        if (!toolbar || document.getElementById('h18-vd-suite-launch')) { return; }
        var button = document.createElement('button');
        button.type = 'button';
        button.id = 'h18-vd-suite-launch';
        button.className = 'button';
        button.textContent = 'Designer+';
        button.title = 'Produktivitet, responsive værktøjer, komponenter, tokens og QA · Ctrl+K';
        button.addEventListener('click', function () { toggleDrawer(true); });
        var wide = document.getElementById('h18-clean-wide-canvas');
        if (wide && wide.nextSibling) { toolbar.insertBefore(button, wide.nextSibling); } else { toolbar.appendChild(button); }

        var status = document.createElement('span');
        status.id = 'h18-suite-workflow-status';
        status.className = 'h18-suite-status';
        toolbar.appendChild(status);
        updateWorkflowStatus();
    }

    function drawerMarkup() {
        return '' +
        '<aside id="h18-suite-drawer" class="h18-suite-drawer" hidden>' +
          '<div class="h18-suite-head"><strong>Designer+</strong><span id="h18-suite-selection-summary" class="h18-suite-muted"></span><button type="button" class="button" data-suite-close>Luk</button></div>' +
          '<div class="h18-suite-tabs">' +
            '<button data-suite-tab="quick" class="is-active">Hurtig</button><button data-suite-tab="responsive">Responsive</button><button data-suite-tab="layers">Lag+</button><button data-suite-tab="components">Komponenter</button><button data-suite-tab="tokens">Tokens</button><button data-suite-tab="history">Historik</button><button data-suite-tab="qa">QA</button>' +
          '</div>' +
          '<div class="h18-suite-body">' +
            '<div id="h18-suite-notice" class="h18-suite-card" hidden></div>' +
            '<section class="h18-suite-panel" data-suite-panel="quick"></section>' +
            '<section class="h18-suite-panel" data-suite-panel="responsive" hidden></section>' +
            '<section class="h18-suite-panel" data-suite-panel="layers" hidden></section>' +
            '<section class="h18-suite-panel" data-suite-panel="components" hidden></section>' +
            '<section class="h18-suite-panel" data-suite-panel="tokens" hidden></section>' +
            '<section class="h18-suite-panel" data-suite-panel="history" hidden></section>' +
            '<section class="h18-suite-panel" data-suite-panel="qa" hidden></section>' +
          '</div>' +
        '</aside>';
    }

    function installDrawer() {
        if (document.getElementById('h18-suite-drawer')) { return; }
        document.body.insertAdjacentHTML('beforeend', drawerMarkup());
        var drawer = document.getElementById('h18-suite-drawer');
        q('[data-suite-close]', drawer).addEventListener('click', function () { toggleDrawer(false); });
        qa('[data-suite-tab]', drawer).forEach(function (button) {
            button.addEventListener('click', function () { activateTab(button.getAttribute('data-suite-tab') || 'quick'); });
        });
        renderAllPanels();
    }
    function toggleDrawer(open) {
        installDrawer();
        var drawer = document.getElementById('h18-suite-drawer');
        if (!drawer) { return; }
        drawer.hidden = open === false ? true : !drawer.hidden;
        if (!drawer.hidden) { renderAllPanels(); }
    }
    function activateTab(name) {
        var drawer = document.getElementById('h18-suite-drawer');
        if (!drawer) { return; }
        qa('[data-suite-tab]', drawer).forEach(function (b) { b.classList.toggle('is-active', b.getAttribute('data-suite-tab') === name); });
        qa('[data-suite-panel]', drawer).forEach(function (p) { p.hidden = p.getAttribute('data-suite-panel') !== name; });
        renderPanel(name);
    }

    function updateWorkflowStatus() {
        var status = document.getElementById('h18-suite-workflow-status');
        if (!status) { return; }
        var source = q('.h18-clean-toolbar');
        var text = source ? String(source.textContent || '') : '';
        var published = /Publiceret/i.test(text);
        status.className = 'h18-suite-status ' + (dirty ? 'is-dirty' : published ? 'is-published' : '');
        status.textContent = dirty ? '● Ikke gemt' : published ? '● Publiceret' : '● Kladde';
        status.title = dirty ? 'Der er ændringer siden siden blev åbnet/gemt.' : 'Designerens aktuelle workflow-status.';
    }

    function syncSelectedClasses() {
        var source = model();
        qa('#h18-clean-canvas .h18-clean-node[data-node-id]').forEach(function (card) {
            var id = String(card.getAttribute('data-node-id') || '');
            var node = nodeById(id, source);
            var props = node && node.props || {};
            card.classList.toggle('h18-suite-selected', selected.has(id));
            card.classList.toggle('h18-suite-hidden', !!props.suiteHidden);
            card.classList.toggle('h18-suite-locked', !!props.suiteLocked);
        });
        var summary = document.getElementById('h18-suite-selection-summary');
        if (summary) {
            var count = selectionIds().length;
            summary.textContent = count ? count + ' valgt' : 'Ingen valgt';
        }
        enhanceLayerTree();
        renderQuickContext();
    }

    function installMultiSelect() {
        document.addEventListener('click', function (event) {
            var card = event.target && event.target.closest ? event.target.closest('#h18-clean-canvas .h18-clean-node[data-node-id]') : null;
            if (!card) { return; }
            var id = String(card.getAttribute('data-node-id') || '');
            if (!id) { return; }
            if (event.ctrlKey || event.metaKey || event.shiftKey) {
                if (selected.has(id) && (event.ctrlKey || event.metaKey)) { selected.delete(id); } else { selected.add(id); }
            } else {
                selected.clear();
                selected.add(id);
            }
            window.setTimeout(syncSelectedClasses, 0);
        }, true);

        document.addEventListener('keydown', function (event) {
            if (!['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(String(event.key || ''))) { return; }
            var ids = selectionIds();
            if (ids.length !== 1) { return; }
            var node = nodeById(ids[0]);
            if (node && node.props && node.props.suiteLocked) {
                event.preventDefault();
                event.stopImmediatePropagation();
                notice('Elementet er låst i Lag+.', 'warn');
            }
        }, true);
    }

    function currentGeometry(node, device, create) {
        if (!node || !node.geometry) { return null; }
        device = device || activeDevice();
        if (device === 'desktop') { return node.geometry.desktop; }
        var g = node.geometry[device] || {};
        if (g.inheritDesktop !== false) {
            if (!create) { return node.geometry.desktop; }
            node.geometry[device] = Object.assign({}, clone(node.geometry.desktop), {inheritDesktop:false});
        }
        return node.geometry[device];
    }

    function align(action) {
        var ids = selectionIds();
        if (ids.length < 2) { notice('Vælg mindst to elementer med Ctrl/Shift+klik.', 'warn'); return; }
        var source = model();
        var nodes = ids.map(function (id) { return nodeById(id, source); }).filter(Boolean);
        var parent = nodes[0] ? String(nodes[0].parentId || '') : '';
        if (nodes.some(function (node) { return String(node.parentId || '') !== parent; })) {
            notice('Alignment kræver elementer med samme parent/Sektion.', 'warn'); return;
        }
        var device = activeDevice();
        mutate('Juster ' + action + ' · ' + device, function (state) {
            var list = ids.map(function (id) { return nodeById(id, state); }).filter(Boolean);
            var gs = list.map(function (node) { return currentGeometry(node, device, true); });
            var left = Math.min.apply(null, gs.map(function (g) { return g.x; }));
            var right = Math.max.apply(null, gs.map(function (g) { return g.x + g.w; }));
            var top = Math.min.apply(null, gs.map(function (g) { return g.y; }));
            var bottom = Math.max.apply(null, gs.map(function (g) { return g.y + Math.max(1,g.h||1); }));
            var ref = gs[0];
            gs.forEach(function (g) {
                if (action === 'left') { g.x = left; }
                else if (action === 'center') { g.x = Math.max(0, Math.round((left + right - g.w) / 2)); }
                else if (action === 'right') { g.x = Math.max(0, right - g.w); }
                else if (action === 'top') { g.y = top; }
                else if (action === 'middle') { g.y = Math.round((top + bottom - Math.max(1,g.h||1)) / 2); }
                else if (action === 'bottom') { g.y = bottom - Math.max(1,g.h||1); }
                else if (action === 'samew') { g.w = ref.w; }
                else if (action === 'sameh') { g.h = ref.h; }
            });
            if (action === 'disth') {
                var sortedH = list.slice().sort(function (a,b) { return currentGeometry(a,device,true).x-currentGeometry(b,device,true).x; });
                var totalW = sortedH.reduce(function (s,n) { return s+currentGeometry(n,device,true).w; },0);
                var gap = sortedH.length>1 ? Math.max(0,(right-left-totalW)/(sortedH.length-1)) : 0;
                var x = left;
                sortedH.forEach(function (n) { var g=currentGeometry(n,device,true); g.x=Math.round(x); x += g.w+gap; });
            }
            if (action === 'distv') {
                var sortedV = list.slice().sort(function (a,b) { return currentGeometry(a,device,true).y-currentGeometry(b,device,true).y; });
                var totalH = sortedV.reduce(function (s,n) { return s+Math.max(1,currentGeometry(n,device,true).h||1); },0);
                var vgap = sortedV.length>1 ? Math.max(0,(bottom-top-totalH)/(sortedV.length-1)) : 0;
                var y = top;
                sortedV.forEach(function (n) { var g=currentGeometry(n,device,true); g.y=Math.round(y); y += Math.max(1,g.h||1)+vgap; });
            }
        });
        window.setTimeout(syncSelectedClasses, 0);
    }

    function quickPanelHtml() {
        return '<h3>Produktivitet</h3>' +
          '<div id="h18-suite-quick-context" class="h18-suite-card"></div>' +
          '<h4>Alignment / multi-select</h4><div class="h18-suite-grid three">' +
            '<button class="button" data-align="left">← Venstre</button><button class="button" data-align="center">↔ Center</button><button class="button" data-align="right">Højre →</button>' +
            '<button class="button" data-align="top">↑ Top</button><button class="button" data-align="middle">↕ Midt</button><button class="button" data-align="bottom">Bund ↓</button>' +
            '<button class="button" data-align="samew">Samme bredde</button><button class="button" data-align="sameh">Samme højde</button><button class="button" data-align="disth">Fordel ↔</button><button class="button" data-align="distv">Fordel ↕</button>' +
          '</div>' +
          '<h4>Sideværktøjer</h4><div class="h18-suite-grid">' +
            '<button class="button" data-suite-live-compare>Sammenlign med live</button><button class="button" data-suite-run-qa>Test siden</button>' +
            '<button class="button" data-suite-command>Ctrl+K kommandoer</button><button class="button" data-suite-autosave-now>Gem lokal recovery</button>' +
          '</div>' +
          '<h4>Sektionspresets</h4><div class="h18-suite-row"><select id="h18-suite-preset"><option value="hero">Hero + CTA</option><option value="text-image">Tekst + billede</option><option value="two-col">2 kolonner</option><option value="cards">3 infokort</option><option value="cta">CTA-bånd</option><option value="faq">FAQ</option><option value="contact">Kontakt</option><option value="gallery">Galleri</option></select><button class="button button-primary" data-suite-add-preset>Indsæt sektion</button></div>' +
          '<div id="h18-suite-image-context"></div>';
    }

    function bindQuickPanel(panel) {
        qa('[data-align]', panel).forEach(function (button) { button.addEventListener('click', function () { align(button.getAttribute('data-align')); }); });
        q('[data-suite-live-compare]', panel).addEventListener('click', openLiveCompare);
        q('[data-suite-run-qa]', panel).addEventListener('click', function () { activateTab('qa'); runQa(); });
        q('[data-suite-command]', panel).addEventListener('click', openCommandPalette);
        q('[data-suite-autosave-now]', panel).addEventListener('click', function () { saveAutosave(true); });
        q('[data-suite-add-preset]', panel).addEventListener('click', function () { addSectionPreset(q('#h18-suite-preset',panel).value); });
    }

    function renderQuickContext() {
        var host = document.getElementById('h18-suite-quick-context');
        if (!host) { return; }
        var ids = selectionIds();
        var n = ids.length ? nodeById(ids[ids.length-1]) : null;
        host.innerHTML = ids.length
            ? '<strong>' + ids.length + ' valgt</strong><div class="h18-suite-muted">Aktiv: ' + esc(n ? ((n.props && n.props.suiteLabel) || n.type) : '') + ' · ' + esc(activeDevice()) + '</div>'
            : '<strong>Ingen elementer valgt</strong><div class="h18-suite-muted">Ctrl/Shift+klik vælger flere elementer.</div>';
        renderImageContext();
    }

    function renderImageContext() {
        var host = document.getElementById('h18-suite-image-context');
        if (!host) { return; }
        var ids = selectionIds();
        var n = ids.length === 1 ? nodeById(ids[0]) : null;
        if (!n || n.type !== 'image') { host.innerHTML = ''; return; }
        host.innerHTML = '<h4>Billedeværktøjer</h4><div class="h18-suite-image-tools"><button class="button" data-fit="cover">Cover</button><button class="button" data-fit="contain">Contain</button><button class="button" data-fit="original">Original</button><button class="button" data-focus>Vælg fokuspunkt</button><button class="button" data-focus-center>Centrér fokus</button></div>';
        qa('[data-fit]',host).forEach(function (button) { button.addEventListener('click', function () {
            mutate('Billede · ' + button.getAttribute('data-fit'), function (state) { var node=nodeById(n.id,state); if(node){node.props.fit=button.getAttribute('data-fit');} });
        }); });
        q('[data-focus]',host).addEventListener('click', function () { enableFocusPoint(n.id); });
        q('[data-focus-center]',host).addEventListener('click', function () { mutate('Centrér billedfokus', function (state) { var node=nodeById(n.id,state); if(node){node.props.focalX=50;node.props.focalY=50;} }); });
    }

    function enableFocusPoint(id) {
        focusPointMode = true;
        var card = q('#h18-clean-canvas .h18-clean-node[data-node-id="' + CSS.escape(id) + '"]');
        if (!card) { return; }
        card.classList.add('h18-suite-focus-mode');
        notice('Klik på billedet dér, hvor fokuspunktet skal ligge.', '');
        var once = function (event) {
            event.preventDefault(); event.stopPropagation();
            var rect = card.getBoundingClientRect();
            var x = Math.max(0,Math.min(100,Math.round((event.clientX-rect.left)/Math.max(1,rect.width)*100)));
            var y = Math.max(0,Math.min(100,Math.round((event.clientY-rect.top)/Math.max(1,rect.height)*100)));
            mutate('Sæt billedfokus', function (state) { var node=nodeById(id,state); if(node){node.props.focalX=x;node.props.focalY=y;} });
            card.classList.remove('h18-suite-focus-mode');
            card.removeEventListener('click', once, true);
            focusPointMode = false;
        };
        card.addEventListener('click', once, true);
    }

    function makeNode(type, parentId, order, x, y, w, h, props) {
        return {id:uid(type),type:type,parentId:parentId||'',order:order||10,geometry:{desktop:{x:x||0,y:y||0,w:w||120,h:h||0},laptop:{x:x||0,y:y||0,w:w||120,h:h||0,inheritDesktop:true},tablet:{x:x||0,y:y||0,w:w||120,h:h||0,inheritDesktop:true},mobile:{x:x||0,y:y||0,w:w||120,h:h||0,inheritDesktop:true}},props:Object.assign({borderWidth:0,borderColor:'#000000',gapX:0,gapY:0,offsetX:0,offsetY:0},props||{})};
    }
    function rootBottom(source) {
        return (source.nodes||[]).filter(function(n){return !n.parentId && n.type==='section';}).reduce(function(m,n){var g=n.geometry&&n.geometry.desktop||{};return Math.max(m,(parseInt(g.y||0,10)||0)+(parseInt(g.h||0,10)||20));},0);
    }
    function addSectionPreset(kind) {
        var next = model(), y = rootBottom(next) + 4, section = makeNode('section','',9999,0,y,120,26,{background:'#ffffff',padding:0,minHeightRows:26,suiteLabel:'Preset · '+kind});
        var nodes=[section], sid=section.id;
        if(kind==='hero'){
            nodes.push(makeNode('text',sid,10,6,3,108,8,{heading:'Ny hero-overskrift',headingLevel:'h1',text:'<p>Skriv en kort introduktion.</p>',align:'center',background:'#ffffff',backgroundTransparent:true,textColor:'#30382a',headingColor:'#30382a',padding:12,fontSize:18,fontWeight:400,lineHeight:1.5,headingFontSize:42,headingFontWeight:700}));
            nodes.push(makeNode('button',sid,20,45,13,30,6,{text:'Læs mere',linkType:'url',url:'#',background:'#30382a',textColor:'#ffffff',paddingX:20,paddingY:10,radius:24,autoSize:true}));
        } else if(kind==='text-image'){
            nodes.push(makeNode('text',sid,10,4,3,54,18,{heading:'Overskrift',text:'<p>Fortæl historien her.</p>',background:'#ffffff',backgroundTransparent:true,textColor:'#30382a',headingColor:'#30382a',padding:12,fontSize:16,fontWeight:400,lineHeight:1.5,headingFontWeight:700}));
            nodes.push(makeNode('image',sid,20,62,3,54,18,{mediaId:0,url:'',alt:'',fit:'cover',focalX:50,focalY:50,boxBackground:'#f4f1e8',boxTransparent:false}));
        } else if(kind==='two-col' || kind==='cards'){
            var count=kind==='cards'?3:2, width=kind==='cards'?34:52;
            for(var i=0;i<count;i++){var x=4+i*(width+5);var box=makeNode('container',sid,10+i*10,x,3,width,18,{background:i===1?'#c3ae83':'#f4f1e8',padding:14,radius:7,minHeightRows:18,suiteLabel:'Kort '+(i+1)});nodes.push(box);nodes.push(makeNode('text',box.id,10,0,0,120,0,{heading:'Punkt '+(i+1),text:'<p>Beskrivelse.</p>',background:'#ffffff',backgroundTransparent:true,textColor:'#30382a',headingColor:'#30382a',padding:0,fontSize:16,fontWeight:400,lineHeight:1.5,headingFontWeight:700}));}
        } else if(kind==='cta'){
            section.props.background='#c3ae83';
            nodes.push(makeNode('text',sid,10,8,3,104,8,{heading:'Klar til næste skridt?',text:'<p>Skriv en tydelig handling.</p>',align:'center',background:'#ffffff',backgroundTransparent:true,textColor:'#30382a',headingColor:'#30382a',padding:8,fontSize:16,fontWeight:400,lineHeight:1.5,headingFontWeight:700}));
            nodes.push(makeNode('button',sid,20,45,14,30,6,{text:'Bliv medlem',linkType:'page',pageId:0,background:'#30382a',textColor:'#ffffff',paddingX:20,paddingY:10,radius:24,autoSize:true}));
        } else if(kind==='faq'){
            nodes.push(makeNode('text',sid,10,5,2,110,6,{heading:'Ofte stillede spørgsmål',text:'',background:'#ffffff',backgroundTransparent:true,textColor:'#30382a',headingColor:'#30382a',padding:6,headingFontWeight:700}));
            for(var f=0;f<3;f++){nodes.push(makeNode('text',sid,20+f*10,8,9+f*5,104,4,{heading:'Spørgsmål '+(f+1),text:'<p>Svar på spørgsmålet.</p>',background:'#f4f1e8',backgroundTransparent:false,textColor:'#30382a',headingColor:'#30382a',padding:10,radius:5,fontSize:15,fontWeight:400,lineHeight:1.45,headingFontWeight:700}));}
        } else if(kind==='contact'){
            section.geometry.desktop.h=82;section.props.minHeightRows=82;
            nodes.push(makeNode('contactform',sid,10,5,3,110,76,{heading:'Kontakt os',intro:'Har du spørgsmål, er du velkommen til at kontakte os.',buttonText:'Send besked',recipient:'',background:'#f4f1e8',fieldBackground:'#ffffff',textColor:'#30382a',accentColor:'#30382a',padding:24,radius:6,fieldGap:16,textareaHeight:168,consentMargin:18,buttonPaddingX:20,buttonPaddingY:11,showPhone:true,requireConsent:true}));
        } else if(kind==='gallery'){
            section.geometry.desktop.h=52;section.props.minHeightRows=52;
            nodes.push(makeNode('gallerylist',sid,10,4,3,112,44,{heading:'Billedgalleri'}));
        }
        next.nodes=(next.nodes||[]).concat(nodes);
        applyModel(next,'Indsæt preset · '+kind,section.id);
        selected.clear();selected.add(section.id);window.setTimeout(syncSelectedClasses,0);
    }

    function responsivePanelHtml() {
        return '<h3>Responsive</h3><div id="h18-suite-responsive-state" class="h18-suite-card"></div>' +
          '<div class="h18-suite-row"><label>Device preset <select id="h18-suite-device-preset"><option value="">Standard</option><option value="iphone-se">iPhone SE · 375</option><option value="iphone-15">iPhone 15 · 393</option><option value="galaxy-s24">Galaxy S24 · 360</option><option value="ipad">iPad · 820</option><option value="ipad-landscape">iPad landscape · 980</option><option value="laptop">Laptop · 1100</option><option value="desktop">Desktop · 1920</option></select></label><button class="button" data-suite-rotate>⇄ Rotér</button></div>' +
          '<div class="h18-suite-row"><label><input type="checkbox" id="h18-suite-safe-area"> Vis safe-area</label><label><input type="checkbox" id="h18-suite-only-overrides"> Vis kun overrides</label></div>' +
          '<button class="button" data-suite-reset-device>Nulstil valgt element til Desktop</button>' +
          '<h4>Box model</h4><div id="h18-suite-spacing-editor"></div>';
    }
    function bindResponsivePanel(panel) {
        var preset=q('#h18-suite-device-preset',panel);preset.value=currentPreset;preset.addEventListener('change',function(){applyDevicePreset(preset.value,false);});
        q('[data-suite-rotate]',panel).addEventListener('click',function(){applyDevicePreset(currentPreset,true);});
        var safe=q('#h18-suite-safe-area',panel);safe.checked=safeArea;safe.addEventListener('change',function(){safeArea=safe.checked;applySafeArea();});
        var only=q('#h18-suite-only-overrides',panel);only.checked=document.body.classList.contains('h18-suite-only-overrides');only.addEventListener('change',function(){document.body.classList.toggle('h18-suite-only-overrides',only.checked);enhanceLayerTree();});
        q('[data-suite-reset-device]',panel).addEventListener('click',resetSelectedResponsive);
        renderResponsiveState();
        renderSpacingEditor();
    }

    var PRESETS={ 'iphone-se':{device:'mobile',w:375,h:667},'iphone-15':{device:'mobile',w:393,h:852},'galaxy-s24':{device:'mobile',w:360,h:780},'ipad':{device:'tablet',w:820,h:1180},'ipad-landscape':{device:'tablet',w:980,h:820},'laptop':{device:'laptop',w:1100,h:760},'desktop':{device:'desktop',w:1920,h:1080} };
    function clickDevice(device) {
        var button=q('.h18-clean-device-button[data-device="'+CSS.escape(device)+'"]');
        if(button){button.click();}
    }
    function applyDevicePreset(key, rotate) {
        if(!key||!PRESETS[key]){currentPreset='';currentPresetWidth=0;var rp=window.H18VDResponsivePreview;if(rp&&typeof rp.reset==='function'){rp.reset();}renderResponsiveState();return;}
        var p=PRESETS[key], width=rotate?p.h:p.w;
        currentPreset=key;currentPresetWidth=width;clickDevice(p.device);
        window.setTimeout(function(){var rp=window.H18VDResponsivePreview;if(rp&&typeof rp.setWidth==='function'){rp.setWidth(p.device,width);}applySafeArea();renderResponsiveState();},80);
    }
    function applySafeArea() {
        var frame=document.getElementById('h18-vd-canonical-responsive-frame');if(!frame)return;
        try{var doc=frame.contentDocument;if(!doc||!doc.body)return;qa('.h18-suite-safe-top,.h18-suite-safe-bottom',doc).forEach(function(el){el.remove();});if(!safeArea)return;var top=doc.createElement('div');top.className='h18-suite-safe-top';var bottom=doc.createElement('div');bottom.className='h18-suite-safe-bottom';doc.body.appendChild(top);doc.body.appendChild(bottom);}catch(ignore){}
    }
    function renderResponsiveState() {
        var host=document.getElementById('h18-suite-responsive-state');if(!host)return;
        var ids=selectionIds(),n=ids.length===1?nodeById(ids[0]):null,dev=activeDevice(),g=n&&n.geometry&&n.geometry[dev],inherit=dev!=='desktop'&&g&&g.inheritDesktop!==false;
        host.innerHTML='<strong>'+esc(dev.charAt(0).toUpperCase()+dev.slice(1))+'</strong>'+(currentPresetWidth?' · '+currentPresetWidth+' px':'')+'<div class="h18-suite-muted">'+(n?(inherit?'Valgt element arver Desktop':'Valgt element har eget '+esc(dev)+' override'):'Vælg ét element for override-status')+'</div>';
    }
    function resetSelectedResponsive() {
        var ids=selectionIds(),dev=activeDevice();if(dev==='desktop'||ids.length!==1){notice('Vælg ét element på Laptop/Tablet/Mobil.','warn');return;}
        mutate('Nulstil '+dev+' til Desktop',function(state){var n=nodeById(ids[0],state);if(!n)return;n.geometry[dev]=Object.assign({},clone(n.geometry.desktop),{inheritDesktop:true});});
        renderResponsiveState();
    }
    function renderSpacingEditor() {
        var host=document.getElementById('h18-suite-spacing-editor');if(!host)return;var ids=selectionIds(),n=ids.length===1?nodeById(ids[0]):null;if(!n){host.innerHTML='<p class="h18-suite-muted">Vælg ét element.</p>';return;}
        var p=n.props||{};host.innerHTML='<div class="h18-suite-spacing-box"><div class="h18-suite-spacing-inner">INDHOLD</div></div><div class="h18-suite-spacing-controls"><label>Padding<input type="number" data-space="padding" min="0" max="120" value="'+(parseInt(p.padding||0,10)||0)+'"></label><label>Gap X<input type="number" data-space="gapX" min="0" max="200" value="'+(parseInt(p.gapX||0,10)||0)+'"></label><label>Gap Y<input type="number" data-space="gapY" min="0" max="200" value="'+(parseInt(p.gapY||0,10)||0)+'"></label></div>';
        qa('[data-space]',host).forEach(function(input){input.addEventListener('change',function(){var key=input.getAttribute('data-space'),val=Math.max(0,parseInt(input.value||0,10)||0);mutate('Box model · '+key,function(state){var node=nodeById(n.id,state);if(node){node.props[key]=val;}});});});
    }

    function layersPanelHtml() {
        return '<h3>Lag+</h3><p class="h18-suite-muted">Brug også det eksisterende <strong>Lag</strong>-faneblad til venstre. Alpha.42 tilføjer navn, skjul, lås og drag-rækkefølge direkte dér.</p><div class="h18-suite-row"><button class="button" data-suite-rename>Omdøb valgt</button><button class="button" data-suite-hide>👁 Skjul/vis</button><button class="button" data-suite-lock>🔒 Lås/lås op</button></div><div class="h18-suite-breakpoint-note">Ctrl/Shift+klik på canvas giver multi-select. Lag kan trækkes op/ned blandt søskende.</div>';
    }
    function bindLayersPanel(panel) {
        q('[data-suite-rename]',panel).addEventListener('click',renameSelected);
        q('[data-suite-hide]',panel).addEventListener('click',function(){toggleMeta('suiteHidden','Skjul/vis element');});
        q('[data-suite-lock]',panel).addEventListener('click',function(){toggleMeta('suiteLocked','Lås/lås op element');});
    }
    function toggleMeta(key,label) {
        var ids=selectionIds();if(!ids.length)return;mutate(label,function(state){ids.forEach(function(id){var n=nodeById(id,state);if(n){n.props[key]=!n.props[key];}});});window.setTimeout(syncSelectedClasses,0);
    }
    function renameSelected() {
        var ids=selectionIds();if(ids.length!==1){notice('Vælg ét element.','warn');return;}var n=nodeById(ids[0]),name=window.prompt('Navn i Lag-panelet:',String(n&&n.props&&n.props.suiteLabel||''));if(name===null)return;mutate('Omdøb lag',function(state){var node=nodeById(ids[0],state);if(node){node.props.suiteLabel=String(name).trim();}});window.setTimeout(enhanceLayerTree,0);
    }

    function enhanceLayerTree() {
        var source=model(),dev=activeDevice();
        qa('.h18-vd-layer-item').forEach(function(item){
            var id=String(item.getAttribute('data-node-id')||'');if(!id)return;var n=nodeById(id,source);if(!n)return;var p=n.props||{},g=n.geometry&&n.geometry[dev]||{};
            item.setAttribute('data-suite-hidden',p.suiteHidden?'1':'0');item.setAttribute('data-suite-locked',p.suiteLocked?'1':'0');item.setAttribute('data-suite-override',dev==='desktop'||g.inheritDesktop===false?'1':'0');
            var layerPick=q('.h18-vd-layer-pick',item);if(layerPick&&p.suiteLabel){layerPick.textContent=String(p.suiteLabel)+' · '+String(n.type||'element');layerPick.title='Vælg '+String(p.suiteLabel);}
            item.draggable=!p.suiteLocked;
            var actions=q('.h18-suite-layer-actions',item);if(!actions){actions=document.createElement('span');actions.className='h18-suite-layer-actions';actions.innerHTML='<button type="button" data-la="eye" title="Skjul/vis">👁</button><button type="button" data-la="lock" title="Lås/lås op">🔒</button><button type="button" data-la="rename" title="Omdøb">✎</button>';item.appendChild(actions);
                actions.addEventListener('click',function(event){var b=event.target.closest('[data-la]');if(!b)return;event.stopPropagation();selected.clear();selected.add(id);if(b.dataset.la==='eye')toggleMeta('suiteHidden','Skjul/vis element');else if(b.dataset.la==='lock')toggleMeta('suiteLocked','Lås/lås op element');else renameSelected();});
            }
            item.ondragstart=function(event){layerDragId=id;try{event.dataTransfer.setData('text/x-vdm-layer',id);}catch(ignore){}};
            item.ondragover=function(event){if(layerDragId){event.preventDefault();}};
            item.ondrop=function(event){event.preventDefault();var targetId=id,dragId=layerDragId;layerDragId='';reorderLayer(dragId,targetId);};
        });
    }
    function reorderLayer(dragId,targetId) {
        if(!dragId||!targetId||dragId===targetId)return;var source=model(),a=nodeById(dragId,source),b=nodeById(targetId,source);if(!a||!b||String(a.parentId)!==String(b.parentId)){notice('Lag kan kun omarrangeres blandt samme parent.','warn');return;}
        mutate('Omarrangér lag',function(state){var siblings=childrenOf(a.parentId,state),ids=siblings.map(function(n){return n.id;}).filter(function(id){return id!==dragId;}),idx=ids.indexOf(targetId);ids.splice(Math.max(0,idx),0,dragId);ids.forEach(function(id,i){var n=nodeById(id,state);if(n)n.order=(i+1)*10;});});window.setTimeout(enhanceLayerTree,30);
    }

    function subtreeModel(rootId) {
        var source=model(),ids=new Set([rootId].concat(descendantIds(rootId,source))),nodes=(source.nodes||[]).filter(function(n){return ids.has(String(n.id));}).map(clone),root=nodes.find(function(n){return n.id===rootId;});if(root){root.parentId='';root.order=10;root.geometry.desktop.y=0;}return {schemaVersion:1,units:120,rowPx:8,nodes:nodes};
    }
    function localComponents() { try { var v=JSON.parse(localStorage.getItem(LOCAL_COMPONENTS_KEY)||'[]');return Array.isArray(v)?v:[];} catch(ignore){return[];} }
    function saveLocalComponents(rows){localStorage.setItem(LOCAL_COMPONENTS_KEY,JSON.stringify(rows.slice(0,50)));}
    function componentsPanelHtml() {
        return '<h3>Komponenter</h3><div class="h18-suite-row"><button class="button" data-suite-save-local>Gem som lokal kopi</button><button class="button button-primary" data-suite-save-global>Gem/opdatér global</button></div><p class="h18-suite-muted">Globale komponenter kræver en valgt Sektion. Når en global komponent opdateres, synkroniseres gemte instanser på andre sider og får en ny sideversion.</p><h4>Lokale komponenter</h4><div id="h18-suite-local-components" class="h18-suite-components-list"></div><h4>Globale komponenter</h4><div id="h18-suite-global-components" class="h18-suite-components-list"></div>';
    }
    function bindComponentsPanel(panel) {
        q('[data-suite-save-local]',panel).addEventListener('click',saveLocalComponent);
        q('[data-suite-save-global]',panel).addEventListener('click',saveGlobalComponent);
        renderComponentsLists();
    }
    function saveLocalComponent() {
        var ids=selectionIds();if(ids.length!==1){notice('Vælg én Sektion.','warn');return;}var n=nodeById(ids[0]);if(!n||n.type!=='section'){notice('Komponenter gemmes fra en Sektion.','warn');return;}var name=window.prompt('Navn på komponent:',String(n.props&&n.props.suiteLabel||'Ny komponent'));if(!name)return;var rows=localComponents();rows.unshift({id:uid('local'),name:name,updatedUtc:new Date().toISOString(),model:subtreeModel(n.id)});saveLocalComponents(rows);renderComponentsLists();notice('Lokal komponent gemt.','');
    }
    function saveGlobalComponent() {
        var ids=selectionIds();if(ids.length!==1){notice('Vælg én Sektion.','warn');return;}var n=nodeById(ids[0]);if(!n||n.type!=='section'){notice('Globale komponenter skal være en Sektion.','warn');return;}var existing=String(n.props&&n.props.suiteComponentId||''),name=window.prompt(existing?'Opdatér global komponent – navn:':'Navn på global komponent:',String(n.props&&n.props.suiteLabel||'Global komponent'));if(!name)return;
        suiteAjax('save_component',{name:name,component_id:existing,model_json:JSON.stringify(subtreeModel(n.id)),sync:'1'}).then(function(data){suiteData.components=data.components||[];var c=data.component||{};mutate('Link global komponent',function(state){var node=nodeById(n.id,state);if(node){node.props.suiteComponentId=String(c.id||'');node.props.suiteComponentVersion=parseInt(c.version||1,10)||1;node.props.suiteLabel=name;}});renderComponentsLists();notice('Global komponent gemt · '+String(data.syncedPages||0)+' gemte sider synkroniseret.','');}).catch(function(e){notice(e.message,'error');});
    }
    function renderComponentsLists() {
        var localHost=document.getElementById('h18-suite-local-components'),globalHost=document.getElementById('h18-suite-global-components');if(localHost){var locals=localComponents();localHost.innerHTML=locals.length?locals.map(function(c,i){return '<div class="h18-suite-component"><span><strong>'+esc(c.name)+'</strong><br><small>'+esc(c.updatedUtc||'')+'</small></span><span class="h18-suite-component-actions"><button class="button button-small" data-local-insert="'+i+'">Indsæt</button><button class="button button-small" data-local-delete="'+i+'">Slet</button></span></div>';}).join(''):'<p class="h18-suite-muted">Ingen lokale komponenter.</p>';qa('[data-local-insert]',localHost).forEach(function(b){b.onclick=function(){insertComponent(locals[parseInt(b.dataset.localInsert,10)],false);};});qa('[data-local-delete]',localHost).forEach(function(b){b.onclick=function(){var i=parseInt(b.dataset.localDelete,10);locals.splice(i,1);saveLocalComponents(locals);renderComponentsLists();};});}
        if(globalHost){var globals=Array.isArray(suiteData.components)?suiteData.components:[];globalHost.innerHTML=globals.length?globals.map(function(c,i){return '<div class="h18-suite-component"><span><strong>'+esc(c.name)+'</strong><br><small>v'+esc(c.version)+' · '+esc(c.updatedUtc||'')+'</small></span><span class="h18-suite-component-actions"><button class="button button-small" data-global-insert="'+i+'">Indsæt</button><button class="button button-small" data-global-delete="'+i+'">Slet</button></span></div>';}).join(''):'<p class="h18-suite-muted">Ingen globale komponenter.</p>';qa('[data-global-insert]',globalHost).forEach(function(b){b.onclick=function(){insertComponent(globals[parseInt(b.dataset.globalInsert,10)],true);};});qa('[data-global-delete]',globalHost).forEach(function(b){b.onclick=function(){var c=globals[parseInt(b.dataset.globalDelete,10)];if(!c||!confirm('Slet global komponent "'+c.name+'"?'))return;suiteAjax('delete_component',{component_id:c.id}).then(function(data){suiteData.components=data.components||[];renderComponentsLists();});};});}
    }
    function insertComponent(component,global) {
        if(!component||!component.model||!Array.isArray(component.model.nodes))return;var source=component.model,nodes=clone(source.nodes),root=nodes.find(function(n){return !n.parentId;});if(!root)return;var next=model(),map={},existing=new Set((next.nodes||[]).map(function(n){return n.id;}));nodes.forEach(function(n){var id=uid(n.type);while(existing.has(id)){id=uid(n.type);}map[n.id]=id;existing.add(id);});var y=rootBottom(next)+4;nodes.forEach(function(n){var old=n.id;n.id=map[old];n.parentId=n.parentId?(map[n.parentId]||''):'';if(old===root.id){n.geometry.desktop.y=y;n.order=9999;if(global){n.props=n.props||{};n.props.suiteComponentId=String(component.id||'');n.props.suiteComponentVersion=parseInt(component.version||1,10)||1;n.props.suiteLabel=String(component.name||'Global komponent');}}});next.nodes=(next.nodes||[]).concat(nodes);applyModel(next,'Indsæt '+(global?'global ':'')+'komponent · '+String(component.name||''),map[root.id]);selected.clear();selected.add(map[root.id]);window.setTimeout(syncSelectedClasses,0);
    }

    function tokensPanelHtml() {
        return '<h3>Design Tokens</h3><p class="h18-suite-muted">Tokens kan linkes til elementer. <strong>Gem + synkronisér</strong> opdaterer alle gemte sider, der bruger token-referencen.</p><div id="h18-suite-token-editor"></div><div class="h18-suite-row"><button class="button button-primary" data-suite-save-tokens>Gem + synkronisér</button></div><h4>Anvend på valgt element</h4><div id="h18-suite-token-apply"></div>';
    }
    function bindTokensPanel(panel) { renderTokenEditor();q('[data-suite-save-tokens]',panel).addEventListener('click',saveTokens);renderTokenApply(); }
    function tokenGroups(){return suiteData.tokens&&typeof suiteData.tokens==='object'?suiteData.tokens:{};}
    function renderTokenEditor() {
        var host=document.getElementById('h18-suite-token-editor');if(!host)return;var groups=tokenGroups(),html='';['colors','radius','spacing','fonts'].forEach(function(group){html+='<h4>'+esc(group)+'</h4>';var rows=groups[group]||{};Object.keys(rows).forEach(function(key){var row=rows[key]||{},type=group==='colors'?'color':group==='radius'||group==='spacing'?'number':'text';html+='<div class="h18-suite-token-row" data-token-group="'+group+'" data-token-key="'+esc(key)+'"><input type="text" data-token-label value="'+esc(row.label||key)+'"><input type="'+type+'" data-token-value value="'+esc(row.value)+'"><code>'+esc(key)+'</code></div>';});});host.innerHTML=html;
    }
    function saveTokens() {
        var next=clone(tokenGroups());qa('#h18-suite-token-editor [data-token-group]').forEach(function(row){var g=row.dataset.tokenGroup,k=row.dataset.tokenKey;next[g]=next[g]||{};next[g][k]={label:q('[data-token-label]',row).value,value:q('[data-token-value]',row).value};});suiteAjax('save_tokens',{tokens_json:JSON.stringify(next),sync:'1'}).then(function(data){suiteData.tokens=data.tokens||next;renderTokenEditor();renderTokenApply();notice('Tokens gemt · '+String(data.syncedPages||0)+' sider synkroniseret.','');}).catch(function(e){notice(e.message,'error');});
    }
    function optionsFor(group){var rows=tokenGroups()[group]||{};return '<option value="">— vælg —</option>'+Object.keys(rows).map(function(k){return '<option value="'+esc(k)+'">'+esc(rows[k].label||k)+'</option>';}).join('');}
    function renderTokenApply(){var host=document.getElementById('h18-suite-token-apply');if(!host)return;host.innerHTML='<div class="h18-suite-row"><label>Baggrund <select data-token-apply="background">'+optionsFor('colors')+'</select></label><label>Tekst <select data-token-apply="text">'+optionsFor('colors')+'</select></label></div><div class="h18-suite-row"><label>Radius <select data-token-apply="radius">'+optionsFor('radius')+'</select></label><label>Spacing <select data-token-apply="spacing">'+optionsFor('spacing')+'</select></label><label>Font <select data-token-apply="font">'+optionsFor('fonts')+'</select></label></div>';qa('[data-token-apply]',host).forEach(function(sel){sel.addEventListener('change',function(){if(sel.value)applyToken(sel.dataset.tokenApply,sel.value);});});}
    function tokenValue(group,key){var row=tokenGroups()[group]&&tokenGroups()[group][key];return row?row.value:null;}
    function applyToken(kind,key){var ids=selectionIds();if(!ids.length){notice('Vælg mindst ét element.','warn');return;}mutate('Anvend design token · '+kind,function(state){ids.forEach(function(id){var n=nodeById(id,state);if(!n)return;var p=n.props||{};if(kind==='background'){p.suiteTokenBackground=key;var v=tokenValue('colors',key);if('background'in p)p.background=v;else if('boxBackground'in p)p.boxBackground=v;}else if(kind==='text'){p.suiteTokenText=key;var t=tokenValue('colors',key);if('textColor'in p)p.textColor=t;if('headingColor'in p)p.headingColor=t;}else if(kind==='radius'){p.suiteTokenRadius=key;if('radius'in p)p.radius=parseInt(tokenValue('radius',key)||0,10)||0;}else if(kind==='spacing'){p.suiteTokenSpacing=key;var s=parseInt(tokenValue('spacing',key)||0,10)||0;if('padding'in p)p.padding=s;p.gapY=s;}else if(kind==='font'){p.suiteTokenFont=key;var f=String(tokenValue('fonts',key)||'system');if('fontFamily'in p)p.fontFamily=f;if('headingFontFamily'in p)p.headingFontFamily=f;}});});}
    
    function historyPanelHtml(){return '<h3>Historik</h3><p class="h18-suite-muted">Klik på et Undo-trin for at hoppe tilbage. Gemte versioner kan sammenlignes visuelt side-by-side.</p><div id="h18-suite-history-list" class="h18-suite-history"></div><h4>Gemte versioner</h4><button class="button" data-suite-load-versions>Hent versioner</button><div id="h18-suite-version-compare"></div>';}
    function bindHistoryPanel(panel){q('[data-suite-load-versions]',panel).addEventListener('click',loadVersions);renderHistory();}
    function renderHistory(){var host=document.getElementById('h18-suite-history-list');if(!host)return;var bridge=api(),rows=typeof bridge.history==='function'?bridge.history():[];host.innerHTML=rows.length?rows.slice().reverse().map(function(label,i){return '<button class="button" data-undo-steps="'+(i+1)+'">'+esc(label)+'</button>';}).join(''):'<span class="h18-suite-muted">Ingen lokale Undo-trin endnu.</span>';qa('[data-undo-steps]',host).forEach(function(b){b.onclick=function(){var n=parseInt(b.dataset.undoSteps,10)||1;var a=api();for(var i=0;i<n;i++){if(typeof a.undo==='function')a.undo();}renderHistory();};});}
    function loadVersions(){if(!POST_ID){notice('Versionssammenligning kræver en side.','warn');return;}suiteAjax('versions',{post_id:POST_ID}).then(function(data){var rows=data.versions||[],host=document.getElementById('h18-suite-version-compare');if(!host)return;var opts=rows.map(function(v,i){return '<option value="'+i+'">v'+esc(v.version)+' · '+esc(v.note||v.savedUtc)+'</option>';}).join('');host.innerHTML=rows.length?'<div class="h18-suite-row"><select id="h18-suite-version-a">'+opts+'</select><select id="h18-suite-version-b">'+opts+'</select><button class="button" id="h18-suite-compare-versions">Sammenlign</button></div>':'<p>Ingen versioner.</p>';if(rows.length>1){q('#h18-suite-version-b',host).selectedIndex=1;}var btn=q('#h18-suite-compare-versions',host);if(btn)btn.onclick=function(){openModelCompare(rows[parseInt(q('#h18-suite-version-a',host).value,10)],rows[parseInt(q('#h18-suite-version-b',host).value,10)]);};}).catch(function(e){notice(e.message,'error');});}

    function qaPanelHtml(){return '<h3>Responsive QA</h3><div class="h18-suite-row"><button class="button button-primary" data-suite-run-qa>Test siden</button></div><div id="h18-suite-qa-results"></div>';}
    function bindQaPanel(panel){q('[data-suite-run-qa]',panel).addEventListener('click',runQa);}
    function runQa(){var source=model(),issues=[],nodes=source.nodes||[],map={};nodes.forEach(function(n){map[n.id]=n;});nodes.forEach(function(n){var p=n.props||{};if(n.type==='image'&&!String(p.alt||'').trim())issues.push({s:'warn',m:'Billede '+n.id+' mangler alt-tekst.'});if(n.type==='image'&&!p.mediaId&&!p.url)issues.push({s:'error',m:'Billede '+n.id+' har ingen billedkilde.'});if((n.type==='button'||n.type==='link')&&((p.linkType==='url'&&!String(p.url||'').trim())||String(p.url||'')==='#'))issues.push({s:'warn',m:'Link/knap '+n.id+' har tom eller # destination.'});if(n.type==='text'&&!String(p.heading||p.text||'').replace(/<[^>]+>/g,'').trim())issues.push({s:'warn',m:'Tekstelement '+n.id+' er tomt.'});['desktop','laptop','tablet','mobile'].forEach(function(dev){var g=n.geometry&&n.geometry[dev];if(!g)return;var actual=dev!=='desktop'&&g.inheritDesktop!==false?n.geometry.desktop:g;if((actual.x||0)+(actual.w||0)>120)issues.push({s:'error',m:n.id+' går udenfor '+dev+'-bredden.'});if(n.type==='button'&&(actual.w||120)<10)issues.push({s:'warn',m:'Knappen '+n.id+' er meget smal på '+dev+'.'});});});
        var parents={};nodes.forEach(function(n){var p=n.parentId||'';parents[p]=parents[p]||[];parents[p].push(n);});Object.keys(parents).forEach(function(pid){var list=parents[pid];for(var i=0;i<list.length;i++)for(var j=i+1;j<list.length;j++){var a=list[i].geometry&&list[i].geometry.desktop,b=list[j].geometry&&list[j].geometry.desktop;if(!a||!b)continue;if(a.x<b.x+b.w&&a.x+a.w>b.x&&a.y<b.y+Math.max(1,b.h||1)&&a.y+Math.max(1,a.h||1)>b.y){issues.push({s:'warn',m:'Desktop-overlap: '+list[i].id+' ↔ '+list[j].id});}}});
        var frame=document.getElementById('h18-vd-canonical-responsive-frame');try{if(frame&&frame.contentDocument&&frame.contentDocument.documentElement.scrollWidth>frame.contentDocument.documentElement.clientWidth+2)issues.push({s:'error',m:'Frontend-preview har vandret overflow på '+activeDevice()+'.'});}catch(ignore){}
        var errors=issues.filter(function(x){return x.s==='error';}).length,warns=issues.filter(function(x){return x.s==='warn';}).length,host=document.getElementById('h18-suite-qa-results');if(host){host.innerHTML='<div class="h18-suite-qa-summary"><span class="h18-suite-qa-pill error">'+errors+' fejl</span><span class="h18-suite-qa-pill warn">'+warns+' advarsler</span><span class="h18-suite-qa-pill ok">'+(issues.length?'Kontrol gennemført':'Alt OK')+'</span></div>'+(issues.length?'<ul class="h18-suite-qa-list">'+issues.map(function(x){return '<li class="'+(x.s==='error'?'h18-suite-bad':'h18-suite-warn')+'">'+esc(x.m)+'</li>';}).join('')+'</ul>':'<p class="h18-suite-good">Ingen kendte layout-/indholdsproblemer fundet.</p>');}return issues;
    }

    function renderPanel(name){var panel=q('[data-suite-panel="'+name+'"]');if(!panel)return;if(name==='quick'){panel.innerHTML=quickPanelHtml();bindQuickPanel(panel);renderQuickContext();}else if(name==='responsive'){panel.innerHTML=responsivePanelHtml();bindResponsivePanel(panel);}else if(name==='layers'){panel.innerHTML=layersPanelHtml();bindLayersPanel(panel);}else if(name==='components'){panel.innerHTML=componentsPanelHtml();bindComponentsPanel(panel);}else if(name==='tokens'){panel.innerHTML=tokensPanelHtml();bindTokensPanel(panel);}else if(name==='history'){panel.innerHTML=historyPanelHtml();bindHistoryPanel(panel);}else if(name==='qa'){panel.innerHTML=qaPanelHtml();bindQaPanel(panel);}}
    function renderAllPanels(){var drawer=document.getElementById('h18-suite-drawer');if(!drawer)return;var active=q('[data-suite-tab].is-active',drawer);renderPanel(active?active.dataset.suiteTab:'quick');}

    function saveAutosave(manual){var current=model();try{localStorage.setItem(AUTOSAVE_KEY,JSON.stringify({savedUtc:new Date().toISOString(),model:current,context:CONTEXT,version:CFG.version||''}));if(manual)notice('Lokal recovery gemt.','');}catch(e){if(manual)notice('Kunne ikke gemme lokal recovery: '+e.message,'error');}}
    function installAutosave(){bootModel=model();try{var raw=JSON.parse(localStorage.getItem(AUTOSAVE_KEY)||'null');if(raw&&raw.model){if(JSON.stringify(raw.model)===JSON.stringify(bootModel)){localStorage.removeItem(AUTOSAVE_KEY);}else{showRecovery(raw);}}}catch(ignore){}autosaveTimer=window.setInterval(function(){if(dirty)saveAutosave(false);},20000);document.addEventListener('h18-clean-model-changed',function(){dirty=true;updateWorkflowStatus();window.clearTimeout(autosaveTimer);autosaveTimer=window.setTimeout(function(){saveAutosave(false);},3000);});}
    function showRecovery(raw){var toolbar=q('.h18-clean-toolbar');if(!toolbar||document.getElementById('h18-suite-recovery'))return;var box=document.createElement('div');box.id='h18-suite-recovery';box.className='h18-suite-autosave';box.innerHTML='<strong>Der findes en nyere lokal kladde.</strong> <span>'+esc(raw.savedUtc||'')+'</span> <button type="button" class="button button-primary" data-recover>Gendan</button> <button type="button" class="button" data-discard>Kassér</button>';toolbar.insertAdjacentElement('afterend',box);q('[data-recover]',box).onclick=function(){applyModel(raw.model,'Gendan lokal recovery');localStorage.removeItem(AUTOSAVE_KEY);box.remove();notice('Lokal recovery gendannet.','');};q('[data-discard]',box).onclick=function(){localStorage.removeItem(AUTOSAVE_KEY);box.remove();};}

    function installInspectorSearch(){var inspector=q('.h18-clean-inspector');if(!inspector||q('.h18-suite-inspector-search',inspector))return;var head=q(':scope > .h18-clean-panel-head, :scope > h2',inspector);var tools=document.createElement('div');tools.className='h18-suite-inspector-search';tools.innerHTML='<input type="search" placeholder="Søg i Inspector…" aria-label="Søg i Inspector"><button type="button" class="button" title="Gem aktuelt felt som favorit">☆</button>';if(head&&head.nextSibling)inspector.insertBefore(tools,head.nextSibling);else inspector.insertBefore(tools,inspector.firstChild);var input=q('input',tools);input.addEventListener('input',function(){filterInspector(input.value);});q('button',tools).onclick=function(){var active=document.activeElement,label=active&&active.closest?active.closest('label'):null;if(!label){notice('Klik først i et Inspector-felt, og tryk derefter ☆.','warn');return;}var text=String(label.textContent||'').replace(/\s+/g,' ').trim();if(!text)return;var favs=inspectorFavorites();if(favs.indexOf(text)<0)favs.push(text);localStorage.setItem(FAV_KEY,JSON.stringify(favs.slice(-12)));renderFavoriteChips();};renderFavoriteChips();}
    function inspectorFavorites(){try{var v=JSON.parse(localStorage.getItem(FAV_KEY)||'[]');return Array.isArray(v)?v:[];}catch(ignore){return[];}}
    function renderFavoriteChips(){var inspector=q('.h18-clean-inspector'),tools=inspector&&q('.h18-suite-inspector-search',inspector);if(!tools)return;var old=q('.h18-suite-favchips',inspector);if(old)old.remove();var favs=inspectorFavorites();if(!favs.length)return;var chips=document.createElement('div');chips.className='h18-suite-favchips';chips.innerHTML=favs.map(function(f){return '<button type="button" class="button button-small" data-fav="'+esc(f)+'">'+esc(f.slice(0,22))+'</button>';}).join('');tools.insertAdjacentElement('afterend',chips);qa('[data-fav]',chips).forEach(function(b){b.onclick=function(){filterInspector(b.dataset.fav||'');q('input',tools).value=b.dataset.fav||'';};});}
    function filterInspector(term){term=String(term||'').toLowerCase().trim();var host=document.getElementById('h18-clean-inspector');if(!host)return;qa(':scope > *',host).forEach(function(el){if(!term){el.style.removeProperty('display');return;}var text=String(el.textContent||'').toLowerCase();el.style.display=text.indexOf(term)>=0?'':'none';});}

    function installCommandPalette(){if(document.getElementById('h18-suite-command'))return;var host=document.createElement('div');host.id='h18-suite-command';host.className='h18-suite-command';host.hidden=true;host.innerHTML='<div class="h18-suite-command-card"><input type="search" placeholder="Skriv en kommando…"><div class="h18-suite-command-list"></div></div>';document.body.appendChild(host);host.addEventListener('click',function(e){if(e.target===host)closeCommandPalette();});q('input',host).addEventListener('input',renderCommands);q('input',host).addEventListener('keydown',function(e){if(e.key==='Escape')closeCommandPalette();if(e.key==='Enter'){var first=q('.h18-suite-command-list button',host);if(first){e.preventDefault();first.click();}}});document.addEventListener('keydown',function(e){if((e.ctrlKey||e.metaKey)&&String(e.key).toLowerCase()==='k'){e.preventDefault();openCommandPalette();}});}
    function commands(){return[
        ['Tilføj Sektion',function(){clickPalette('section');},'sektion add'],
        ['Tilføj Tekst',function(){clickPalette('text');},'tekst add'],
        ['Tilføj Billede',function(){clickPalette('image');},'billede add'],
        ['Tilføj Knap',function(){clickPalette('button');},'knap add'],
        ['Skift til Desktop',function(){clickDevice('desktop');},'responsive'],
        ['Skift til Laptop',function(){clickDevice('laptop');},'responsive'],
        ['Skift til Tablet',function(){clickDevice('tablet');},'responsive'],
        ['Skift til Mobil',function(){clickDevice('mobile');},'responsive'],
        ['Sammenlign med live',openLiveCompare,'preview live compare'],
        ['Test siden',function(){toggleDrawer(true);activateTab('qa');runQa();},'qa test'],
        ['Gem som ny version',function(){var b=q('.h18-clean-save');if(b)b.click();},'save version'],
        ['Åbn Komponenter',function(){toggleDrawer(true);activateTab('components');},'component'],
        ['Åbn Design Tokens',function(){toggleDrawer(true);activateTab('tokens');},'tokens']
    ];}
    function clickPalette(type){var b=q('.h18-clean-add[data-type="'+CSS.escape(type)+'"]');if(b)b.click();}
    function openCommandPalette(){installCommandPalette();var host=document.getElementById('h18-suite-command');host.hidden=false;q('input',host).value='';renderCommands();window.setTimeout(function(){q('input',host).focus();},0);}
    function closeCommandPalette(){var host=document.getElementById('h18-suite-command');if(host)host.hidden=true;}
    function renderCommands(){var host=document.getElementById('h18-suite-command');if(!host)return;var term=String(q('input',host).value||'').toLowerCase(),list=q('.h18-suite-command-list',host),rows=commands().filter(function(c){return(c[0]+' '+c[2]).toLowerCase().indexOf(term)>=0;});list.innerHTML=rows.map(function(c,i){return '<button type="button" data-cmd="'+i+'">'+esc(c[0])+'</button>';}).join('');qa('[data-cmd]',list).forEach(function(b){b.onclick=function(){var row=rows[parseInt(b.dataset.cmd,10)];closeCommandPalette();if(row)row[1]();};});}

    function modalShell(title){var old=document.getElementById('h18-suite-modal');if(old)old.remove();var modal=document.createElement('div');modal.id='h18-suite-modal';modal.className='h18-suite-modal';modal.innerHTML='<div class="h18-suite-modal-card"><div class="h18-suite-modal-head"><strong>'+esc(title)+'</strong><span class="h18-suite-muted" data-modal-status></span><button type="button" class="button" data-modal-close>Luk</button></div><div class="h18-suite-compare"></div></div>';document.body.appendChild(modal);q('[data-modal-close]',modal).onclick=function(){modal.remove();};modal.addEventListener('click',function(e){if(e.target===modal)modal.remove();});return modal;}
    function previewWidth(){var rp=window.H18VDResponsivePreview;if(rp&&typeof rp.width==='function'){var w=parseInt(rp.width()||0,10);if(w)return w;}return({desktop:1920,laptop:1100,tablet:850,mobile:390})[activeDevice()]||1920;}
    function submitModelToFrame(frame,mdl,device){var button=document.getElementById('h18-clean-preview');if(!button||!frame)return;var name='h18_suite_frame_'+Math.random().toString(36).slice(2);frame.name=name;var form=document.createElement('form');form.method='post';form.action=button.getAttribute('data-url')||'';form.target=name;form.style.display='none';[['action','h18_clean_preview'],['_wpnonce',button.getAttribute('data-nonce')||''],['post_id',button.getAttribute('data-post-id')||'0'],['model_json',JSON.stringify(mdl)],['preview_device',device||activeDevice()]].forEach(function(pair){var i=document.createElement('input');i.type='hidden';i.name=pair[0];i.value=pair[1];form.appendChild(i);});document.body.appendChild(form);form.submit();setTimeout(function(){form.remove();},1000);}
    function fitCompareFrame(stage,frame,width){var available=Math.max(280,stage.clientWidth-8),scale=Math.min(1,available/width);frame.style.width=width+'px';frame.style.height=Math.max(700,Math.round((stage.clientHeight||750)/Math.max(.2,scale)))+'px';frame.style.transform='scale('+scale+')';frame.style.transformOrigin='0 0';}
    function openLiveCompare(){var modal=modalShell('Designer vs. live · '+activeDevice()),compare=q('.h18-suite-compare',modal),left=document.createElement('div'),right=document.createElement('div');left.className=right.className='h18-suite-compare-stage';left.innerHTML='<iframe title="Designer-preview"></iframe>';right.innerHTML='<iframe title="Live side"></iframe>';compare.appendChild(left);compare.appendChild(right);var w=previewWidth(),lf=q('iframe',left),rf=q('iframe',right);rf.src=String(CFG.pageUrl||'about:blank');submitModelToFrame(lf,model(),activeDevice());function fit(){fitCompareFrame(left,lf,w);fitCompareFrame(right,rf,w);}lf.onload=fit;rf.onload=fit;window.setTimeout(fit,100);}
    function openModelCompare(a,b){if(!a||!b||!a.model||!b.model){notice('Vælg to versioner.','warn');return;}var modal=modalShell('Versionssammenligning · v'+a.version+' vs v'+b.version),compare=q('.h18-suite-compare',modal),left=document.createElement('div'),right=document.createElement('div');left.className=right.className='h18-suite-compare-stage';left.innerHTML='<iframe title="Version A"></iframe>';right.innerHTML='<iframe title="Version B"></iframe>';compare.appendChild(left);compare.appendChild(right);var w=previewWidth(),lf=q('iframe',left),rf=q('iframe',right);submitModelToFrame(lf,a.model,activeDevice());submitModelToFrame(rf,b.model,activeDevice());function fit(){fitCompareFrame(left,lf,w);fitCompareFrame(right,rf,w);}lf.onload=fit;rf.onload=fit;setTimeout(fit,100);}

    function installDeleteGuard(){var del=document.getElementById('h18-clean-delete');if(!del||del.dataset.suiteGuard==='1')return;del.dataset.suiteGuard='1';del.addEventListener('click',function(event){var id=selectedId(),count=id?descendantIds(id).length:0;if(count>0&&!window.confirm('Dette element indeholder '+count+' under-element'+(count===1?'':'er')+'.\n\nSlet element + alle under-elementer?')){event.preventDefault();event.stopImmediatePropagation();}},true);}

    function bootstrapSuite(){if(!CFG.suiteNonce){bootstrapReady=true;return;}suiteAjax('bootstrap',{}).then(function(data){suiteData.components=data.components||[];suiteData.tokens=data.tokens||{};bootstrapReady=true;renderAllPanels();}).catch(function(e){bootstrapReady=true;notice(e.message,'error');});}

    function renderNativeLayerLabelMetadata(){enhanceLayerTree();syncSelectedClasses();}
    function modelChanged(event){dirty=true;updateWorkflowStatus();var id=event&&event.detail&&event.detail.selectedId?String(event.detail.selectedId):selectedId();if(id&&selected.size<=1){selected.clear();selected.add(id);}window.setTimeout(function(){syncSelectedClasses();renderHistory();renderResponsiveState();renderSpacingEditor();},0);}

    function installObservers(){document.addEventListener('h18-clean-model-changed',modelChanged);var palette=q('.h18-clean-palette');if(window.MutationObserver&&palette){new MutationObserver(function(){window.setTimeout(enhanceLayerTree,0);}).observe(palette,{subtree:true,childList:true});}var inspector=q('.h18-clean-inspector');if(window.MutationObserver&&inspector){new MutationObserver(function(){installInspectorSearch();}).observe(inspector,{subtree:true,childList:true});}var frame=document.getElementById('h18-vd-canonical-responsive-frame');if(frame){frame.addEventListener('load',function(){window.setTimeout(applySafeArea,60);});}}

    function install() {
        installLaunch();
        installDrawer();
        installMultiSelect();
        installAutosave();
        installInspectorSearch();
        installCommandPalette();
        // Delete protection is owned by the canonical core in Alpha.42 to avoid double-confirm dialogs.
        installObservers();
        bootstrapSuite();
        bootModel=model();
        window.setTimeout(function(){syncSelectedClasses();enhanceLayerTree();},150);
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, {once:true}); } else { install(); }
}());
