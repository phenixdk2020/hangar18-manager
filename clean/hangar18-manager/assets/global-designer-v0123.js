(function () {
    'use strict';

    function syncModel() {
        if (window.H18CleanV0120 && typeof window.H18CleanV0120.sync === 'function') {
            window.H18CleanV0120.sync();
        }
    }

    function previewLayout() {
        syncModel();
        var canvas = document.getElementById('h18-clean-canvas');
        if (!canvas) { return; }
        var copy = canvas.cloneNode(true);
        copy.removeAttribute('id');
        copy.classList.add('vd-global-preview-canvas');
        copy.querySelectorAll('.h18-clean-node-header,.h18-clean-resize,.h18-clean-empty-drop,.h18-clean-v018-drop-overlay,.h18-clean-image-edit-frame').forEach(function (node) { node.remove(); });
        copy.querySelectorAll('.h18-clean-node').forEach(function (node) {
            node.classList.remove('is-selected', 'is-resizing', 'is-dragging', 'has-layout-overlap', 'h18-clean-v018-drop-target', 'h18-clean-v018-drop-inside');
            node.style.outline = 'none';
            node.style.boxShadow = 'none';
        });

        var win = window.open('', '_blank', 'noopener');
        if (!win) {
            window.alert('Browseren blokerede forhåndsvisningsvinduet. Tillad popups for WordPress-admin og prøv igen.');
            return;
        }
        var links = Array.prototype.slice.call(document.querySelectorAll('link[rel="stylesheet"]')).map(function (link) {
            return '<link rel="stylesheet" href="' + String(link.href).replace(/&/g, '&amp;').replace(/"/g, '&quot;') + '">';
        }).join('');
        win.document.open();
        win.document.write('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Header / Footer preview</title>' + links + '<style>body{margin:0;padding:24px;background:#f0f0f1;font-family:system-ui,sans-serif}.vd-preview-shell{max-width:1440px;margin:0 auto;background:#fff;box-shadow:0 4px 24px rgba(0,0,0,.12)}.vd-global-preview-canvas{width:100%;min-height:120px}.vd-global-preview-canvas .h18-clean-node{cursor:default!important}.vd-global-preview-canvas .h18-clean-inner-surface{min-height:100%}.vd-preview-note{max-width:1440px;margin:0 auto 10px;color:#50575e;font-size:13px}</style></head><body><div class="vd-preview-note">Visual Designer · lokal Header/Footer-forhåndsvisning. Temaets shell overtages ikke endnu i 0.1.23.</div><div class="vd-preview-shell"></div></body></html>');
        win.document.close();
        var shell = win.document.querySelector('.vd-preview-shell');
        if (shell) { shell.appendChild(win.document.importNode(copy, true)); }
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
