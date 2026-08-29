(function () {
    'use strict';

    function syncModel() {
        if (window.H18CleanV0120 && typeof window.H18CleanV0120.sync === 'function') {
            window.H18CleanV0120.sync();
        }
    }

    function ensurePreviewOverlay() {
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

    function install() {
        var preview = document.getElementById('h18-global-local-preview');
        if (preview) { preview.addEventListener('click', previewLayout); }
        var form = document.getElementById('h18-clean-save-form');
        if (form) { form.addEventListener('submit', syncModel, true); }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
