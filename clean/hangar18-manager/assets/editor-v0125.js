(function () {
    'use strict';

    var CFG = window.H18CleanEditor || {};
    var active = null;
    var initialShellChoices = null;

    function cleanHtml(html) {
        var tpl = document.createElement('template');
        tpl.innerHTML = String(html || '');
        var allowed = ['P', 'BR', 'STRONG', 'B', 'EM', 'I', 'U', 'S', 'UL', 'OL', 'LI', 'A'];
        Array.prototype.slice.call(tpl.content.querySelectorAll('*')).forEach(function (el) {
            if (allowed.indexOf(el.tagName) === -1) {
                el.replaceWith.apply(el, Array.prototype.slice.call(el.childNodes));
                return;
            }
            Array.prototype.slice.call(el.attributes).forEach(function (attr) {
                var ok = el.tagName === 'A' && ['href', 'target', 'rel'].indexOf(attr.name.toLowerCase()) !== -1;
                if (!ok) { el.removeAttribute(attr.name); }
            });
            if (el.tagName === 'A') {
                var href = String(el.getAttribute('href') || '').trim();
                if (/^javascript:/i.test(href)) { el.removeAttribute('href'); }
                if (el.getAttribute('target') === '_blank') { el.setAttribute('rel', 'noopener'); }
            }
        });
        return tpl.innerHTML;
    }

    function plainToHtml(value) {
        var text = String(value || '');
        if (text.indexOf('<') !== -1) { return cleanHtml(text); }
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML.replace(/\r?\n/g, '<br>');
    }

    function command(name, value) {
        if (!active || !active.editor) { return; }
        active.editor.focus();
        try { document.execCommand(name, false, value || null); } catch (ignore) {}
        active.dirty = true;
        active.textarea.value = cleanHtml(active.editor.innerHTML);
        updateCanvasPreview(active.textarea.value);
    }

    function updateCanvasPreview(html) {
        var selected = document.querySelector('.h18-clean-node.is-selected[data-node-id]');
        var body = selected && selected.querySelector(':scope > .h18-clean-node-preview--text .h18-clean-text-body');
        if (body) { body.innerHTML = cleanHtml(html); }
    }

    function sync() {
        if (!active || !active.textarea || !active.editor) { return; }
        var html = cleanHtml(active.editor.innerHTML);
        active.textarea.value = html;
        if (active.dirty) {
            active.dirty = false;
            active.textarea.dispatchEvent(new Event('change', { bubbles: true }));
        }
    }

    function toolbarButton(label, title, handler) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'button h18-vd-rich-button';
        button.innerHTML = label;
        button.title = title;
        button.addEventListener('mousedown', function (event) { event.preventDefault(); });
        button.addEventListener('click', handler);
        return button;
    }

    function enhance() {
        var textarea = document.querySelector('#h18-clean-inspector textarea[data-field="text"]');
        if (!textarea || textarea.dataset.vdRich === '1') { return; }
        if (active) { sync(); active = null; }
        textarea.dataset.vdRich = '1';

        var shell = document.createElement('div');
        shell.className = 'h18-vd-rich-shell';
        var toolbar = document.createElement('div');
        toolbar.className = 'h18-vd-rich-toolbar';
        var editor = document.createElement('div');
        editor.className = 'h18-vd-rich-editor';
        editor.contentEditable = 'true';
        editor.setAttribute('role', 'textbox');
        editor.setAttribute('aria-multiline', 'true');
        editor.innerHTML = plainToHtml(textarea.value || '');

        active = { textarea: textarea, editor: editor, dirty: false };

        toolbar.appendChild(toolbarButton('<strong>B</strong>', 'Fed', function () { command('bold'); }));
        toolbar.appendChild(toolbarButton('<em>I</em>', 'Kursiv', function () { command('italic'); }));
        toolbar.appendChild(toolbarButton('<u>U</u>', 'Understregning', function () { command('underline'); }));
        toolbar.appendChild(toolbarButton('• Liste', 'Punktopstilling', function () { command('insertUnorderedList'); }));
        toolbar.appendChild(toolbarButton('1. Liste', 'Nummereret liste', function () { command('insertOrderedList'); }));
        toolbar.appendChild(toolbarButton('Link', 'Indsæt/redigér link', function () {
            var url = window.prompt('Linkdestination (URL, #anker, mailto: eller tel:):', 'https://');
            if (url) { command('createLink', url.trim()); }
        }));
        toolbar.appendChild(toolbarButton('× format', 'Fjern formatering', function () { command('removeFormat'); }));

        editor.addEventListener('input', function () {
            if (!active || active.editor !== editor) { return; }
            active.dirty = true;
            textarea.value = cleanHtml(editor.innerHTML);
            updateCanvasPreview(textarea.value);
        });
        editor.addEventListener('blur', function () { sync(); });

        textarea.style.display = 'none';
        textarea.parentNode.insertBefore(shell, textarea);
        shell.appendChild(toolbar);
        shell.appendChild(editor);
        shell.appendChild(textarea);
    }

    function readModel() {
        var field = document.getElementById('h18-clean-model-json');
        if (!field) { return { nodes: [] }; }
        try {
            var model = JSON.parse(field.value || '{}');
            return model && typeof model === 'object' ? model : { nodes: [] };
        } catch (ignore) { return { nodes: [] }; }
    }

    function mapNodes(model) {
        var map = Object.create(null);
        (Array.isArray(model && model.nodes) ? model.nodes : []).forEach(function (node) {
            if (node && node.id) { map[String(node.id)] = node; }
        });
        return map;
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

    function responsiveChangedCount() {
        var before = mapNodes(CFG.initialModel || { nodes: [] });
        var after = mapNodes(readModel());
        var count = 0;
        Object.keys(after).forEach(function (id) {
            if (!before[id]) { return; }
            var bg = before[id].geometry || {};
            var ag = after[id].geometry || {};
            if (!same(bg.laptop || {}, ag.laptop || {}) || !same(bg.mobile || {}, ag.mobile || {})) { count += 1; }
        });
        return count;
    }

    function currentShellChoices() {
        var header = document.querySelector('select[name="header_template_choice"]');
        var footer = document.querySelector('select[name="footer_template_choice"]');
        return {
            header: header ? String(header.value || 'auto') : null,
            footer: footer ? String(footer.value || 'auto') : null
        };
    }

    function appendNote(input, part) {
        if (!input || !part) { return; }
        var current = String(input.value || '').trim();
        if (current.indexOf(part) !== -1) { return; }
        input.value = (current ? current + ' · ' : '') + part;
        if (input.value.length > 240) { input.value = input.value.slice(0, 240); }
    }

    function augmentAutomaticNote() {
        var input = document.getElementById('h18-clean-change-note');
        if (!input) { return; }

        var coreLabels = window.H18CleanHistory && typeof window.H18CleanHistory.labels === 'function'
            ? window.H18CleanHistory.labels()
            : [];
        if (Array.isArray(coreLabels) && coreLabels.length) {
            var responsiveCount = responsiveChangedCount();
            if (responsiveCount > 0) {
                appendNote(input, responsiveCount === 1 ? 'Ændret responsivt layout' : 'Ændret responsivt layout for ' + responsiveCount + ' elementer');
            }
        }

        if (initialShellChoices) {
            var now = currentShellChoices();
            if (now.header !== null && now.header !== initialShellChoices.header) { appendNote(input, 'Ændret Header-valg'); }
            if (now.footer !== null && now.footer !== initialShellChoices.footer) { appendNote(input, 'Ændret Footer-valg'); }
        }
    }

    function install() {
        var inspector = document.getElementById('h18-clean-inspector');
        if (!inspector) { return; }
        initialShellChoices = currentShellChoices();
        enhance();
        new MutationObserver(function () { enhance(); }).observe(inspector, { childList: true, subtree: true });
        var form = document.getElementById('h18-clean-save-form');
        if (form) {
            form.addEventListener('submit', function () {
                sync();
                window.setTimeout(augmentAutomaticNote, 0);
            }, true);
        }
    }

    window.H18RichTextV0125 = { sync: sync };
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
