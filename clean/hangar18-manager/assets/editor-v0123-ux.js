(function () {
    'use strict';

    var CFG = window.H18CleanEditor || {};

    function clone(value) {
        try { return JSON.parse(JSON.stringify(value)); } catch (ignore) { return value; }
    }

    function readCurrentModel() {
        var field = document.getElementById('h18-clean-model-json');
        if (!field) { return { nodes: [] }; }
        try {
            var model = JSON.parse(field.value || '{}');
            return model && typeof model === 'object' ? model : { nodes: [] };
        } catch (ignore) {
            return { nodes: [] };
        }
    }

    function mapNodes(model) {
        var map = Object.create(null);
        (Array.isArray(model && model.nodes) ? model.nodes : []).forEach(function (node) {
            if (node && node.id) { map[String(node.id)] = node; }
        });
        return map;
    }

    function typeLabel(type) {
        return ({ section: 'Sektion', container: 'Kasse', text: 'Tekst', image: 'Billede' })[String(type || '')] || 'element';
    }

    function stable(value) {
        if (Array.isArray(value)) { return value.map(stable); }
        if (!value || typeof value !== 'object') { return value; }
        var result = {};
        Object.keys(value).sort().forEach(function (key) { result[key] = stable(value[key]); });
        return result;
    }

    function same(a, b) {
        return JSON.stringify(stable(a)) === JSON.stringify(stable(b));
    }

    function automaticChangeNote() {
        var labels = window.H18CleanHistory && typeof window.H18CleanHistory.labels === 'function' ? window.H18CleanHistory.labels() : [];
        labels = Array.isArray(labels) ? labels.filter(Boolean) : [];
        if (labels.length) { return labels.slice(-12).join(' · ').slice(0, 240); }
        var before = mapNodes(clone(CFG.initialModel || { nodes: [] }));
        var afterModel = readCurrentModel();
        var after = mapNodes(afterModel);
        var added = [];
        var removed = [];
        var moved = 0;
        var content = 0;
        var styling = 0;

        Object.keys(after).forEach(function (id) {
            if (!before[id]) {
                added.push(typeLabel(after[id].type));
                return;
            }
            var a = before[id];
            var b = after[id];
            if (String(a.parentId || '') !== String(b.parentId || '') || !same(a.geometry || {}, b.geometry || {})) {
                moved += 1;
            }
            if (b.type === 'text' && (!same(a.props && a.props.text, b.props && b.props.text) || !same(a.props && a.props.heading, b.props && b.props.heading))) {
                content += 1;
            } else if (b.type === 'image' && (!same(a.props && a.props.mediaId, b.props && b.props.mediaId) || !same(a.props && a.props.url, b.props && b.props.url))) {
                content += 1;
            }
            var ap = Object.assign({}, a.props || {});
            var bp = Object.assign({}, b.props || {});
            ['text', 'heading', 'mediaId', 'url'].forEach(function (key) { delete ap[key]; delete bp[key]; });
            if (!same(ap, bp)) { styling += 1; }
        });
        Object.keys(before).forEach(function (id) {
            if (!after[id]) { removed.push(typeLabel(before[id].type)); }
        });

        var parts = [];
        if (added.length) {
            parts.push(added.length === 1 ? 'Tilføjet ' + added[0] : 'Tilføjet ' + added.length + ' elementer');
        }
        if (removed.length) {
            parts.push(removed.length === 1 ? 'Slettet ' + removed[0] : 'Slettet ' + removed.length + ' elementer');
        }
        if (content) { parts.push(content === 1 ? 'Opdateret indhold' : 'Opdateret indhold i ' + content + ' elementer'); }
        if (moved) { parts.push(moved === 1 ? 'Ændret placering/størrelse' : 'Ændret layout for ' + moved + ' elementer'); }
        if (styling) { parts.push(styling === 1 ? 'Ændret design' : 'Ændret design på ' + styling + ' elementer'); }
        return parts.length ? parts.join(' · ').slice(0, 180) : 'Gemt Visual Designer-layout';
    }

    function makeChangeNoteOptional() {
        var form = document.getElementById('h18-clean-save-form');
        var input = document.getElementById('h18-clean-change-note');
        if (!form || !input) { return; }

        input.required = false;
        input.removeAttribute('required');
        input.placeholder = 'Valgfri – ellers beskriver systemet automatisk ændringen';
        var label = document.querySelector('.h18-clean-change-note-label');
        if (label) { label.textContent = 'Ændringer (valgfri):'; }

        form.addEventListener('submit', function () {
            if (window.H18RichTextV0125 && typeof window.H18RichTextV0125.sync === 'function') { window.H18RichTextV0125.sync(); }
            if (window.H18CleanV0120 && typeof window.H18CleanV0120.sync === 'function') {
                window.H18CleanV0120.sync();
            }
            if ((input.value || '').trim() === '') {
                input.value = automaticChangeNote();
                var userEntered = form.querySelector('[name="change_note_user_entered"]');
                if (userEntered) { userEntered.value = '0'; }
            }
        }, true);
    }

    function cleanupImageReset(button) {
        var card = button && button.closest ? button.closest('.h18-clean-inspector') : null;
        var selected = document.querySelector('.h18-clean-node.is-selected[data-node-id]');
        if (!selected) { return; }
        var preview = selected.querySelector(':scope > .h18-clean-node-preview--image');
        var img = preview && preview.querySelector('img');
        if (!preview) { return; }
        preview.querySelectorAll(':scope > .h18-clean-image-edit-frame').forEach(function (frame) { frame.remove(); });
        preview.style.position = '';
        preview.style.display = 'flex';
        preview.style.justifyContent = 'center';
        preview.style.alignItems = 'center';
        if (img) {
            img.style.position = '';
            img.style.left = '';
            img.style.top = '';
            img.style.width = '100%';
            img.style.height = '100%';
            img.style.maxWidth = 'none';
            img.style.maxHeight = 'none';
            img.style.objectFit = 'contain';
            img.style.objectPosition = '50% 50%';
            img.style.margin = '0';
            img.style.userSelect = '';
            img.style.pointerEvents = '';
        }
        if (card) { card.classList.remove('h18-vd-image-manual-active'); }
    }

    function makeImageControlsVisible() {
        var host = document.getElementById('h18-clean-inspector');
        if (!host) { return; }
        var panel = host.querySelector('.h18-clean-v0120-style');
        var selected = document.querySelector('.h18-clean-node.is-selected.h18-clean-node--image');
        if (!panel || !selected || panel.dataset.v0123Enhanced === '1') { return; }
        panel.dataset.v0123Enhanced = '1';
        panel.classList.add('h18-vd-image-controls');
        var button = panel.querySelector('.h18-clean-v0120-manual-button');
        if (!button) { return; }
        var heading = document.createElement('strong');
        heading.className = 'h18-vd-image-content-heading';
        heading.textContent = 'Billedindhold';
        button.parentNode.insertBefore(heading, button);
        if (!button.disabled) {
            button.textContent = 'Redigér billedets størrelse og placering';
        } else {
            button.textContent = 'Billedindhold redigeres separat';
            panel.classList.add('is-manual');
        }
    }

    function installImageResetGuard() {
        document.addEventListener('click', function (event) {
            var button = event.target && event.target.closest ? event.target.closest('button') : null;
            if (!button || (button.textContent || '').trim() !== 'Tilbage til Vis hele billedet') { return; }
            window.setTimeout(function () { cleanupImageReset(button); }, 0);
        }, true);

        var inspector = document.getElementById('h18-clean-inspector');
        if (inspector) {
            new MutationObserver(function () { makeImageControlsVisible(); }).observe(inspector, { childList: true, subtree: true });
        }
        makeImageControlsVisible();
    }

    function install() {
        makeChangeNoteOptional();
        installImageResetGuard();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
