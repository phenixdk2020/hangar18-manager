(function () {
    'use strict';

    const CFG = window.H18CleanEditor || {};
    const RECENT_KEY = 'vdm-recent-colors-v1';
    const LEGACY_RECENT_KEY = 'h18-vd-recent-colors-v1';
    const MAX_RECENT = 8;
    const COLOR_SELECTOR = 'input[type="color"]';
    const STANDARD_COLORS = [
        '#ffffff','#000000','#808080','#c3ae83','#30382a','#d63638','#ff6900','#fcb900',
        '#00a32a','#00a0d2','#2271b1','#3858e9','#8b5cf6','#d946ef','#e11d74'
    ];
    let openPicker = null;

    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
    function normalize(value) {
        value = String(value || '').trim().toLowerCase();
        if (/^#[0-9a-f]{3}$/.test(value)) {
            return '#' + value[1] + value[1] + value[2] + value[2] + value[3] + value[3];
        }
        return /^#[0-9a-f]{6}$/.test(value) ? value : '';
    }
    function rgbFromHex(value) {
        const hex = (normalize(value) || '#000000').slice(1);
        return {r:parseInt(hex.slice(0,2),16), g:parseInt(hex.slice(2,4),16), b:parseInt(hex.slice(4,6),16)};
    }
    function byteHex(value) { return clamp(Math.round(value),0,255).toString(16).padStart(2,'0'); }
    function hexFromRgb(rgb) { return '#' + byteHex(rgb.r) + byteHex(rgb.g) + byteHex(rgb.b); }
    function rgbToHsv(rgb) {
        const r=rgb.r/255, g=rgb.g/255, b=rgb.b/255;
        const max=Math.max(r,g,b), min=Math.min(r,g,b), delta=max-min;
        let h=0;
        if (delta) {
            if (max===r) { h=60*(((g-b)/delta)%6); }
            else if (max===g) { h=60*(((b-r)/delta)+2); }
            else { h=60*(((r-g)/delta)+4); }
        }
        if (h<0) { h+=360; }
        return {h:h, s:max ? delta/max : 0, v:max};
    }
    function hsvToRgb(hsv) {
        const h=((hsv.h%360)+360)%360, s=clamp(hsv.s,0,1), v=clamp(hsv.v,0,1);
        const c=v*s, x=c*(1-Math.abs(((h/60)%2)-1)), m=v-c;
        let r=0,g=0,b=0;
        if (h<60) { r=c;g=x; }
        else if (h<120) { r=x;g=c; }
        else if (h<180) { g=c;b=x; }
        else if (h<240) { g=x;b=c; }
        else if (h<300) { r=x;b=c; }
        else { r=c;b=x; }
        return {r:(r+m)*255,g:(g+m)*255,b:(b+m)*255};
    }
    function stateHex(picker) { return hexFromRgb(hsvToRgb(picker.state)); }

    function themePalette() {
        const list = Array.isArray(CFG.themePalette) ? CFG.themePalette : [];
        return list.map(normalize).filter(Boolean).filter(function (value,index,source) {
            return source.indexOf(value) === index;
        }).slice(0,24);
    }
    function storedRecent() {
        try {
            let raw=window.localStorage.getItem(RECENT_KEY);
            if (!raw) {
                raw=window.localStorage.getItem(LEGACY_RECENT_KEY);
                if (raw) { window.localStorage.setItem(RECENT_KEY,raw); }
            }
            const list=JSON.parse(raw || '[]');
            return Array.isArray(list) ? list.map(normalize).filter(Boolean).slice(0,MAX_RECENT) : [];
        } catch (error) { return []; }
    }
    function recentColors() { return storedRecent(); }
    function remember(value) {
        value=normalize(value); if (!value) { return; }
        const next=[value].concat(recentColors().filter(function (item) { return item!==value; })).slice(0,MAX_RECENT);
        try { window.localStorage.setItem(RECENT_KEY,JSON.stringify(next)); } catch (error) {}
    }

    function commit(input,value) {
        value=normalize(value); if (!value) { return; }
        input.value=value;
        input.setAttribute('data-h18-vd-color-commit','1');
        input.dispatchEvent(new Event('change',{bubbles:true}));
    }

    function chip(color,title,onClick) {
        const button=document.createElement('button');
        button.type='button';
        button.className='vdm-color-chip';
        button.style.backgroundColor=color;
        button.title=(title ? title + ': ' : '') + color.toUpperCase();
        button.setAttribute('aria-label',button.title);
        button.addEventListener('click',function (event) {
            event.preventDefault(); event.stopPropagation(); onClick(color);
        });
        return button;
    }

    function fillThemeView(picker) {
        picker.themeList.innerHTML='';
        themePalette().forEach(function (color) {
            picker.themeList.appendChild(chip(color,'Temafarve',function (value) { setHex(picker,value); }));
        });
        picker.recentBlock.hidden = recentColors().length === 0;
        picker.recentList.innerHTML='';
        recentColors().forEach(function (color) {
            picker.recentList.appendChild(chip(color,'Senest brugt',function (value) { setHex(picker,value); }));
        });
        picker.noTheme.hidden = themePalette().length > 0;
    }

    function render(picker) {
        const value=stateHex(picker);
        picker.sv.style.backgroundColor='hsl(' + Math.round(picker.state.h) + ' 100% 50%)';
        picker.marker.style.left=(picker.state.s*100) + '%';
        picker.marker.style.top=((1-picker.state.v)*100) + '%';
        picker.hue.value=String(Math.round(picker.state.h));
        picker.hex.value=value.toUpperCase();
        picker.preview.style.backgroundColor=value;
        picker.themePreview.style.backgroundColor=value;
        picker.themeValue.textContent=value.toUpperCase();
        picker.swatch.style.backgroundColor=value;
        picker.value.textContent=value.toUpperCase();
        picker.colorView.hidden = picker.mode !== 'color';
        picker.themeView.hidden = picker.mode !== 'theme';
        picker.themeToggle.textContent = picker.mode === 'theme' ? 'Farvevælger' : 'Tema';
        picker.themeToggle.setAttribute('aria-pressed',picker.mode === 'theme' ? 'true' : 'false');
    }
    function setHex(picker,value) {
        value=normalize(value); if (!value) { return false; }
        const hsv=rgbToHsv(rgbFromHex(value));
        picker.state={h:hsv.h,s:hsv.s,v:hsv.v};
        render(picker); return true;
    }
    function updateCompact(picker,value) {
        value=normalize(value) || '#000000';
        picker.swatch.style.backgroundColor=value;
        picker.value.textContent=value.toUpperCase();
    }
    function positionPanel(picker) {
        if (!picker || picker.panel.hidden || !picker.button.isConnected) { return; }
        const margin=8,gap=6;
        const vw=Math.max(document.documentElement.clientWidth || 0,window.innerWidth || 0);
        const vh=Math.max(document.documentElement.clientHeight || 0,window.innerHeight || 0);
        const buttonRect=picker.button.getBoundingClientRect();
        picker.panel.style.left='0px'; picker.panel.style.top='0px';
        const rect=picker.panel.getBoundingClientRect();
        const width=Math.min(rect.width,Math.max(1,vw-margin*2));
        const height=Math.min(rect.height,Math.max(1,vh-margin*2));
        let x=clamp(buttonRect.left,margin,Math.max(margin,vw-margin-width));
        if (buttonRect.left + width > vw-margin && buttonRect.right-width >= margin) { x=buttonRect.right-width; }
        let y=buttonRect.bottom+gap;
        if (y+height>vh-margin && buttonRect.top-gap-height>=margin) { y=buttonRect.top-gap-height; }
        else { y=clamp(y,margin,Math.max(margin,vh-margin-height)); }
        picker.panel.style.left=Math.round(x)+'px';
        picker.panel.style.top=Math.round(y)+'px';
    }
    function cancelPicker(picker) {
        if (!picker) { return; }
        const original=normalize(picker.original) || '#000000';
        picker.input.value=original;
        setHex(picker,original);
        updateCompact(picker,original);
        closePicker(picker);
    }
    function closePicker(picker) {
        if (!picker) { return; }
        picker.panel.hidden=true;
        picker.button.setAttribute('aria-expanded','false');
        if (picker.panel.parentNode===document.body) { document.body.removeChild(picker.panel); }
        if (openPicker===picker) { openPicker=null; }
    }
    function open(picker) {
        if (openPicker && openPicker!==picker) { cancelPicker(openPicker); }
        picker.original=normalize(picker.input.value) || '#000000';
        picker.mode='color';
        setHex(picker,picker.original);
        fillThemeView(picker);
        document.body.appendChild(picker.panel);
        picker.panel.hidden=false;
        picker.button.setAttribute('aria-expanded','true');
        openPicker=picker;
        render(picker);
        positionPanel(picker);
    }
    function svPointer(picker,event) {
        const rect=picker.sv.getBoundingClientRect(); if (!rect.width || !rect.height) { return; }
        picker.state.s=clamp((event.clientX-rect.left)/rect.width,0,1);
        picker.state.v=1-clamp((event.clientY-rect.top)/rect.height,0,1);
        render(picker);
    }

    function enhance(input) {
        if (!(input instanceof HTMLInputElement) || input.getAttribute('data-h18-vd-color-managed')==='1') { return; }
        const initial=normalize(input.value) || '#000000';
        input.setAttribute('data-h18-vd-color-managed','1');
        input.setAttribute('data-h18-vd-color-original',initial);
        input.type='hidden';
        input.value=initial;

        const control=document.createElement('div'); control.className='vdm-color-control';
        const button=document.createElement('button'); button.type='button'; button.className='vdm-color-button'; button.setAttribute('aria-expanded','false');
        const swatch=document.createElement('span'); swatch.className='vdm-color-swatch';
        const value=document.createElement('span'); value.className='vdm-color-value';
        button.appendChild(swatch); button.appendChild(value); control.appendChild(button);
        input.parentNode.insertBefore(control,input.nextSibling);

        const panel=document.createElement('div'); panel.className='vdm-color-panel'; panel.hidden=true;
        const colorView=document.createElement('div'); colorView.className='vdm-color-view is-picker';
        const sv=document.createElement('div'); sv.className='vdm-color-sv';
        const marker=document.createElement('span'); marker.className='vdm-color-marker'; sv.appendChild(marker);
        const hue=document.createElement('input'); hue.type='range'; hue.min='0'; hue.max='359'; hue.className='vdm-color-hue';
        const values=document.createElement('div'); values.className='vdm-color-values';
        const preview=document.createElement('span'); preview.className='vdm-color-preview';
        const hexInput=document.createElement('input'); hexInput.type='text'; hexInput.maxLength=7; hexInput.className='vdm-color-hex';
        values.appendChild(preview); values.appendChild(hexInput);
        const standard=document.createElement('div'); standard.className='vdm-color-chip-grid is-standard';
        colorView.appendChild(sv); colorView.appendChild(hue); colorView.appendChild(values); colorView.appendChild(standard);

        const themeView=document.createElement('div'); themeView.className='vdm-color-view is-theme'; themeView.hidden=true;
        const themeCurrent=document.createElement('div'); themeCurrent.className='vdm-color-theme-current';
        const themePreview=document.createElement('span'); themePreview.className='vdm-color-preview';
        const themeValue=document.createElement('code'); themeValue.className='vdm-color-theme-value';
        themeCurrent.appendChild(themePreview); themeCurrent.appendChild(themeValue);
        const themeTitle=document.createElement('strong'); themeTitle.textContent='Temafarver';
        const themeList=document.createElement('div'); themeList.className='vdm-color-chip-grid is-theme';
        const noTheme=document.createElement('p'); noTheme.className='description vdm-color-note'; noTheme.textContent='Temaet har ingen registrerede farver.';
        const recentBlock=document.createElement('div'); recentBlock.className='vdm-color-recent-block';
        const recentTitle=document.createElement('strong'); recentTitle.textContent='Senest brugt';
        const recentList=document.createElement('div'); recentList.className='vdm-color-chip-grid is-recent';
        recentBlock.appendChild(recentTitle); recentBlock.appendChild(recentList);
        themeView.appendChild(themeCurrent); themeView.appendChild(themeTitle); themeView.appendChild(themeList); themeView.appendChild(noTheme); themeView.appendChild(recentBlock);

        const actions=document.createElement('div'); actions.className='vdm-color-actions';
        const cancel=document.createElement('button'); cancel.type='button'; cancel.className='button'; cancel.textContent='Annuller';
        const themeToggle=document.createElement('button'); themeToggle.type='button'; themeToggle.className='button vdm-color-theme-toggle'; themeToggle.textContent='Tema'; themeToggle.setAttribute('aria-pressed','false');
        const apply=document.createElement('button'); apply.type='button'; apply.className='button button-primary'; apply.textContent='Anvend';
        actions.appendChild(cancel); actions.appendChild(themeToggle); actions.appendChild(apply);
        panel.appendChild(colorView); panel.appendChild(themeView); panel.appendChild(actions);

        const start=rgbToHsv(rgbFromHex(initial));
        const picker={input:input,control:control,button:button,swatch:swatch,value:value,panel:panel,colorView:colorView,themeView:themeView,sv:sv,marker:marker,hue:hue,hex:hexInput,preview:preview,themePreview:themePreview,themeValue:themeValue,themeList:themeList,noTheme:noTheme,recentBlock:recentBlock,recentList:recentList,themeToggle:themeToggle,state:start,mode:'color',original:initial,dragging:false};

        STANDARD_COLORS.forEach(function (color) { standard.appendChild(chip(color,'Standard',function (selected) { setHex(picker,selected); })); });
        updateCompact(picker,initial); render(picker);

        button.addEventListener('click',function (event) { event.preventDefault(); event.stopPropagation(); if (openPicker===picker) { cancelPicker(picker); } else { open(picker); } });
        sv.addEventListener('pointerdown',function (event) { event.preventDefault(); picker.dragging=true; try { sv.setPointerCapture(event.pointerId); } catch (ignore) {} svPointer(picker,event); });
        sv.addEventListener('pointermove',function (event) { if (picker.dragging) { event.preventDefault(); svPointer(picker,event); } });
        ['pointerup','pointercancel'].forEach(function (name) { sv.addEventListener(name,function () { picker.dragging=false; }); });
        hue.addEventListener('input',function () { picker.state.h=clamp(parseInt(hue.value || '0',10) || 0,0,359); render(picker); });
        hexInput.addEventListener('input',function () { const candidate=normalize(hexInput.value); if (candidate) { setHex(picker,candidate); } });
        cancel.addEventListener('click',function (event) { event.preventDefault(); event.stopPropagation(); cancelPicker(picker); });
        themeToggle.addEventListener('click',function (event) { event.preventDefault(); event.stopPropagation(); picker.mode=picker.mode==='theme'?'color':'theme'; if (picker.mode==='theme') { fillThemeView(picker); } render(picker); positionPanel(picker); });
        apply.addEventListener('click',function (event) {
            event.preventDefault(); event.stopPropagation();
            const selected=stateHex(picker); remember(selected); commit(input,selected); updateCompact(picker,selected); closePicker(picker);
        });
    }

    function scan(root) {
        const scope=root && (root.querySelectorAll || root.matches) ? root : document;
        if (scope.matches && scope.matches(COLOR_SELECTOR)) { enhance(scope); }
        if (scope.querySelectorAll) { scope.querySelectorAll(COLOR_SELECTOR).forEach(enhance); }
    }
    function init() {
        scan(document);
        const observer=new MutationObserver(function (mutations) {
            mutations.forEach(function (mutation) {
                mutation.addedNodes.forEach(function (node) { if (node instanceof Element) { scan(node); } });
            });
        });
        observer.observe(document.body,{childList:true,subtree:true});
        document.addEventListener('pointerdown',function (event) {
            if (!openPicker) { return; }
            if (openPicker.panel.contains(event.target) || openPicker.control.contains(event.target)) { return; }
            cancelPicker(openPicker);
        });
        document.addEventListener('keydown',function (event) { if (event.key==='Escape' && openPicker) { cancelPicker(openPicker); } });
        window.addEventListener('resize',function () { if (openPicker) { positionPanel(openPicker); } });
        window.addEventListener('scroll',function () { if (openPicker) { positionPanel(openPicker); } },true);
    }

    const api={refresh:scan,normalize:normalize,themePalette:themePalette,recentColors:recentColors,positionOpenPicker:function () { if (openPicker) { positionPanel(openPicker); } }};
    window.VDMColorPicker=api;
    window.H18VDColorPicker=api; // temporary compatibility alias until v0.2 migration

    if (document.readyState==='loading') { document.addEventListener('DOMContentLoaded',init,{once:true}); }
    else { init(); }
}());
