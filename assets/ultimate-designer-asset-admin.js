(function () {
    'use strict';
    const config = window.Hangar18AssetManager || {};
    const form = document.querySelector('.h18-ud-asset-metadata-form');
    const preview = document.querySelector('.h18-ud-focal-preview');
    const image = document.getElementById('h18-ud-focal-image');
    const marker = document.querySelector('.h18-ud-focal-marker');
    let activeDevice = 'desktop';

    function focalControl(device, axis) {
        return form && form.querySelector('[name="asset[Focal' + device.charAt(0).toUpperCase() + device.slice(1) + axis + ']"]');
    }
    function value(device, axis) {
        const control = focalControl(device, axis);
        const n = control ? parseFloat(control.value) : 50;
        return Number.isFinite(n) ? Math.max(0, Math.min(100, n)) : 50;
    }
    function updateFocal() {
        if (!image || !marker) { return; }
        const x = value(activeDevice, 'X');
        const y = value(activeDevice, 'Y');
        image.style.objectPosition = x + '% ' + y + '%';
        marker.style.left = x + '%';
        marker.style.top = y + '%';
        if (preview) { preview.dataset.device = activeDevice; }
        if (form) {
            form.querySelectorAll('[data-focal-device]').forEach(function (group) {
                group.classList.toggle('is-active', group.dataset.focalDevice === activeDevice);
                group.querySelectorAll('input[type="range"]').forEach(function (input) {
                    const output = input.parentElement && input.parentElement.querySelector('output');
                    if (output) { output.value = input.value; output.textContent = input.value; }
                });
            });
        }
    }
    if (form) {
        form.querySelectorAll('[data-focal-device]').forEach(function (group) {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'button button-small h18-ud-focal-device-button';
            button.textContent = group.querySelector('strong') ? group.querySelector('strong').textContent : group.dataset.focalDevice;
            button.addEventListener('click', function () { activeDevice = group.dataset.focalDevice || 'desktop'; updateFocal(); });
            group.insertBefore(button, group.firstChild);
            const strong = group.querySelector('strong'); if (strong) { strong.hidden = true; }
        });
        form.addEventListener('input', function (event) {
            if (event.target.matches('input[type="range"]')) {
                const group = event.target.closest('[data-focal-device]');
                if (group) { activeDevice = group.dataset.focalDevice || activeDevice; }
                updateFocal();
            }
        });
        updateFocal();
    }

    const scanButton = document.getElementById('h18-ud-scan-duplicates');
    const results = document.getElementById('h18-ud-duplicate-results');
    function esc(value) { const d=document.createElement('div'); d.textContent=String(value==null?'':value); return d.innerHTML; }
    if (scanButton && results && config.ajaxUrl && config.duplicateNonce) {
        scanButton.addEventListener('click', function () {
            scanButton.disabled = true;
            results.innerHTML = '<p class="description">Scanner SHA-256… ingen filer ændres.</p>';
            const body = new URLSearchParams({ action:'h18_ud_asset_duplicates', nonce:String(config.duplicateNonce) });
            fetch(config.ajaxUrl, { method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'}, body:body.toString() })
                .then(function (response) { return response.json(); })
                .then(function (payload) {
                    if (!payload || !payload.success) { throw new Error(payload && payload.data && payload.data.message ? payload.data.message : 'Dubletscan fejlede'); }
                    const groups = payload.data && Array.isArray(payload.data.groups) ? payload.data.groups : [];
                    const scanned = payload.data ? parseInt(payload.data.scanned,10)||0 : 0;
                    if (!groups.length) { results.innerHTML='<div class="notice notice-success inline"><p>Ingen SHA-256 dubletter fundet blandt '+scanned+' filer.</p></div>'; return; }
                    results.innerHTML='<p><strong>'+groups.length+' dubletgruppe(r)</strong> blandt '+scanned+' filer. Read-only resultat:</p><div class="h18-ud-duplicate-groups">'+groups.map(function(group){return '<article><code>'+esc(String(group.Hash||'').slice(0,18))+'…</code><strong>Media IDs: '+esc((group.MediaIds||[]).join(', '))+'</strong><small>'+esc(group.Count)+' identiske filer</small></article>';}).join('')+'</div>';
                })
                .catch(function (error) { results.innerHTML='<div class="notice notice-error inline"><p>'+esc(error.message||'Dubletscan fejlede')+'</p></div>'; })
                .finally(function () { scanButton.disabled=false; });
        });
    }
})();
