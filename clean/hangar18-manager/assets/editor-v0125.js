(function () {
    'use strict';

    var CFG = window.H18CleanEditor || {};
    var active = null;
    var initialShellChoices = null;
    var selectionGeneration = 0;

    function cleanHtml(html) {
        var tpl = document.createElement('template');
        tpl.innerHTML = String(html || '');
        var allowed = ['P', 'BR', 'STRONG', 'B', 'EM', 'I', 'U', 'S', 'UL', 'OL', 'LI', 'A'];
        Array.prototype.slice.call(tpl.content.querySelectorAll('div')).forEach(function (el) {
            var p = document.createElement('p');
            while (el.firstChild) { p.appendChild(el.firstChild); }
            el.replaceWith(p);
        });
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

    function rememberSelection() {
        if (!active || !active.editor) { return; }
        var selection = window.getSelection && window.getSelection();
        if (!selection || !selection.rangeCount) { return; }
        var range = selection.getRangeAt(0);
        var container = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentNode;
        if (container && active.editor.contains(container)) {
            try { active.savedRange = range.cloneRange(); } catch (ignoreRange) {}
            if (!active.formatting) {
                var logical = captureLogicalSelection(active.editor);
                if (logical) { active.savedLogical = logical; }
            }
        }
    }

    function restoreSelection() {
        if (!active || !active.editor) { return false; }
        try { active.editor.focus({ preventScroll: true }); } catch (ignoreFocus) { active.editor.focus(); }
        if (!active.savedRange || !window.getSelection) { return false; }
        try {
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(active.savedRange);
            return true;
        } catch (ignoreRange) {
            return false;
        }
    }

    function captureLogicalSelection(editor) {
        if (!editor || !window.getSelection) { return null; }
        var selection = window.getSelection();
        if (!selection || !selection.rangeCount) { return null; }
        var range = selection.getRangeAt(0);
        var common = range.commonAncestorContainer.nodeType === 1 ? range.commonAncestorContainer : range.commonAncestorContainer.parentNode;
        if (!common || !editor.contains(common) || range.collapsed) { return null; }
        try {
            var startProbe = document.createRange();
            startProbe.selectNodeContents(editor);
            startProbe.setEnd(range.startContainer, range.startOffset);
            var endProbe = document.createRange();
            endProbe.selectNodeContents(editor);
            endProbe.setEnd(range.endContainer, range.endOffset);
            var start = startProbe.toString().length;
            var end = endProbe.toString().length;
            return end > start ? { editor: editor, start: start, end: end } : null;
        } catch (ignore) {
            return null;
        }
    }

    function logicalPoint(editor, requestedOffset) {
        var remaining = Math.max(0, parseInt(requestedOffset || 0, 10) || 0);
        var walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT);
        var node = walker.nextNode();
        var last = null;
        while (node) {
            last = node;
            var length = String(node.nodeValue || '').length;
            if (remaining <= length) { return { node: node, offset: remaining }; }
            remaining -= length;
            node = walker.nextNode();
        }
        if (last) { return { node: last, offset: String(last.nodeValue || '').length }; }
        return { node: editor, offset: 0 };
    }

    function restoreLogicalSelection(snapshot) {
        if (!snapshot || !snapshot.editor || !snapshot.editor.isConnected || !window.getSelection) { return false; }
        var start = logicalPoint(snapshot.editor, snapshot.start);
        var end = logicalPoint(snapshot.editor, snapshot.end);
        try {
            var range = document.createRange();
            range.setStart(start.node, start.offset);
            range.setEnd(end.node, end.offset);
            if (range.collapsed && snapshot.end > snapshot.start) { return false; }
            try { snapshot.editor.focus({ preventScroll: true }); } catch (ignoreFocus) { snapshot.editor.focus(); }
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            if (active && active.editor === snapshot.editor) { active.savedRange = range.cloneRange(); }
            return true;
        } catch (ignore) {
            return false;
        }
    }

    function reinforceLogicalSelection(snapshot) {
        if (!snapshot) { return; }
        var generation = ++selectionGeneration;
        var restore = function () {
            if (generation !== selectionGeneration) { return; }
            if (!active || active.editor !== snapshot.editor || !snapshot.editor.isConnected) { return; }
            restoreLogicalSelection(snapshot);
        };
        restore();
        if (window.queueMicrotask) { window.queueMicrotask(restore); }
        else if (window.Promise) { Promise.resolve().then(restore); }
        window.setTimeout(restore, 0);
        if (window.requestAnimationFrame) { window.requestAnimationFrame(restore); }
    }

    /*
     * VD-TEXT-SEL-001 / 0.1.36
     *
     * Firefox may replace or split text nodes differently for STRONG and EM.
     * Logical offsets remain useful as a fallback, but toolbar chaining now
     * owns two persistent empty boundary elements around the selected content.
     * Formatting happens between those boundaries and the native Range is
     * rebuilt from the same DOM anchors after every command.
     */
    function markerSelectionValid() {
        return !!(active && active.editor && active.markerStart && active.markerEnd &&
            active.markerStart.isConnected && active.markerEnd.isConnected &&
            active.editor.contains(active.markerStart) && active.editor.contains(active.markerEnd));
    }

    function clearSelectionMarkers() {
        if (!active) { return; }
        [active.markerStart, active.markerEnd].forEach(function (marker) {
            if (marker && marker.parentNode) { marker.parentNode.removeChild(marker); }
        });
        active.markerStart = null;
        active.markerEnd = null;
    }

    function boundaryMarker(kind) {
        var marker = document.createElement('span');
        marker.setAttribute('data-vd-selection-boundary', kind);
        marker.setAttribute('aria-hidden', 'true');
        marker.contentEditable = 'false';
        marker.style.fontSize = '0';
        marker.style.lineHeight = '0';
        marker.style.pointerEvents = 'none';
        return marker;
    }

    function restoreMarkerSelection() {
        if (!markerSelectionValid() || !window.getSelection) { return false; }
        try {
            var range = document.createRange();
            range.setStartAfter(active.markerStart);
            range.setEndBefore(active.markerEnd);
            if (range.collapsed) { return false; }
            try { active.editor.focus({ preventScroll: true }); } catch (ignoreFocus) { active.editor.focus(); }
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            active.savedRange = range.cloneRange();
            return true;
        } catch (ignore) { return false; }
    }

    function installSelectionMarkers() {
        if (!active || !active.editor || !window.getSelection) { return false; }
        var logical = captureLogicalSelection(active.editor) || active.savedLogical;
        if (!logical) { return false; }
        clearSelectionMarkers();
        if (!restoreLogicalSelection(logical)) { return false; }
        var selection = window.getSelection();
        if (!selection || !selection.rangeCount || selection.getRangeAt(0).collapsed) { return false; }
        var range = selection.getRangeAt(0);
        try {
            var end = boundaryMarker('end');
            var endRange = range.cloneRange();
            endRange.collapse(false);
            endRange.insertNode(end);
            var start = boundaryMarker('start');
            var startRange = range.cloneRange();
            startRange.collapse(true);
            startRange.insertNode(start);
            active.markerStart = start;
            active.markerEnd = end;
            active.savedLogical = logical;
            return restoreMarkerSelection();
        } catch (ignore) {
            clearSelectionMarkers();
            return false;
        }
    }

    function reinforceMarkerSelection() {
        if (!markerSelectionValid()) { return; }
        var generation = ++selectionGeneration;
        var restore = function () {
            if (generation !== selectionGeneration || !markerSelectionValid()) { return; }
            restoreMarkerSelection();
        };
        restore();
        if (window.queueMicrotask) { window.queueMicrotask(restore); }
        else if (window.Promise) { Promise.resolve().then(restore); }
        window.setTimeout(restore, 0);
        window.setTimeout(restore, 24);
        if (window.requestAnimationFrame) { window.requestAnimationFrame(restore); }
    }

    var INLINE_FORMAT_TAGS = { bold: 'STRONG', italic: 'EM', underline: 'U' };

    function formatAncestor(node, tagName, editor) {
        var current = node && node.nodeType === 1 ? node : (node ? node.parentElement : null);
        while (current && current !== editor) {
            if (current.tagName === tagName) { return current; }
            current = current.parentElement;
        }
        return null;
    }

    function textNodesIn(root) {
        var out = [];
        var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
        var node = walker.nextNode();
        while (node) {
            if (String(node.nodeValue || '').length) { out.push(node); }
            node = walker.nextNode();
        }
        return out;
    }

    function unwrap(element) {
        if (!element || !element.parentNode) { return; }
        var parent = element.parentNode;
        while (element.firstChild) { parent.insertBefore(element.firstChild, element); }
        parent.removeChild(element);
    }

    function removeMarker(marker) {
        var fragment = document.createDocumentFragment();
        while (marker.firstChild) { fragment.appendChild(marker.firstChild); }
        marker.parentNode.replaceChild(fragment, marker);
    }

    function splitTargetAroundMarker(marker, ancestor) {
        try {
            var beforeRange = document.createRange();
            beforeRange.selectNodeContents(ancestor);
            beforeRange.setEndBefore(marker);
            var before = beforeRange.cloneContents();
            var afterRange = document.createRange();
            afterRange.selectNodeContents(ancestor);
            afterRange.setStartAfter(marker);
            var after = afterRange.cloneContents();

            var chain = [];
            var current = marker.parentElement;
            while (current && current !== ancestor) { chain.push(current); current = current.parentElement; }
            if (current !== ancestor) { return false; }
            var selected = marker;
            chain.forEach(function (element) {
                var clone = element.cloneNode(false);
                clone.appendChild(selected);
                selected = clone;
            });

            var replacement = document.createDocumentFragment();
            if (before.childNodes.length) {
                var left = ancestor.cloneNode(false);
                left.appendChild(before);
                replacement.appendChild(left);
            }
            replacement.appendChild(selected);
            if (after.childNodes.length) {
                var right = ancestor.cloneNode(false);
                right.appendChild(after);
                replacement.appendChild(right);
            }
            ancestor.parentNode.replaceChild(replacement, ancestor);
            return true;
        } catch (ignore) { return false; }
    }

    function applyInlineFormat(name, snapshot) {
        var tagName = INLINE_FORMAT_TAGS[String(name || '').toLowerCase()] || '';
        if (!tagName || !snapshot || !window.getSelection) { return false; }
        if (markerSelectionValid()) { restoreMarkerSelection(); }
        else if (!restoreLogicalSelection(snapshot)) { return false; }
        var selection = window.getSelection();
        if (!selection || !selection.rangeCount) { return false; }
        var range = selection.getRangeAt(0);
        if (range.collapsed) { return false; }

        var marker = document.createElement('span');
        marker.setAttribute('data-vd-selection-marker', '1');
        marker.style.display = 'contents';
        try {
            marker.appendChild(range.extractContents());
            range.insertNode(marker);
        } catch (ignoreExtract) { return false; }

        var nodes = textNodesIn(marker);
        if (!nodes.length) { removeMarker(marker); restoreLogicalSelection(snapshot); return false; }
        var allFormatted = nodes.every(function (node) { return !!formatAncestor(node, tagName, snapshot.editor); });

        if (allFormatted) {
            Array.prototype.slice.call(marker.querySelectorAll(tagName.toLowerCase())).reverse().forEach(unwrap);
            var guard = 0;
            var outer = formatAncestor(marker, tagName, snapshot.editor);
            while (outer && guard++ < 12) {
                if (!splitTargetAroundMarker(marker, outer)) { break; }
                outer = formatAncestor(marker, tagName, snapshot.editor);
            }
        } else {
            textNodesIn(marker).forEach(function (node) {
                if (formatAncestor(node, tagName, snapshot.editor)) { return; }
                var wrapper = document.createElement(tagName.toLowerCase());
                node.parentNode.insertBefore(wrapper, node);
                wrapper.appendChild(node);
            });
        }

        removeMarker(marker);
        try { snapshot.editor.normalize(); } catch (ignoreNormalize) {}
        if (markerSelectionValid()) { restoreMarkerSelection(); }
        else { restoreLogicalSelection(snapshot); }
        return true;
    }

    function command(name, value) {
        if (!active || !active.editor) { return; }
        var logicalSelection = active.savedLogical || captureLogicalSelection(active.editor);
        if (markerSelectionValid()) { restoreMarkerSelection(); }
        else if (logicalSelection) { restoreLogicalSelection(logicalSelection); }
        else { restoreSelection(); }

        active.formatting = true;
        try {
            if (INLINE_FORMAT_TAGS[String(name || '').toLowerCase()] && logicalSelection) {
                applyInlineFormat(name, logicalSelection);
            } else {
                try { document.execCommand('styleWithCSS', false, 'false'); } catch (ignoreStyleMode) {}
                try { document.execCommand(name, false, value || null); } catch (ignoreCommand) {}
                try { active.editor.normalize(); } catch (ignoreNormalize) {}
                if (markerSelectionValid()) { restoreMarkerSelection(); }
                else if (logicalSelection) { restoreLogicalSelection(logicalSelection); }
                else { rememberSelection(); }
            }
        } finally { active.formatting = false; }

        if (logicalSelection) { active.savedLogical = captureLogicalSelection(active.editor) || logicalSelection; }
        active.dirty = true;
        active.textarea.value = cleanHtml(active.editor.innerHTML);
        updateCanvasPreview(active.textarea.value);
        if (markerSelectionValid()) { reinforceMarkerSelection(); }
        else { reinforceLogicalSelection(logicalSelection); }
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

    function captureToolbarSelection() {
        if (!active || !active.editor) { return; }
        if (markerSelectionValid()) {
            restoreMarkerSelection();
            return;
        }
        var logical = captureLogicalSelection(active.editor);
        if (logical) { active.savedLogical = logical; }
        rememberSelection();
        installSelectionMarkers();
    }

    function toolbarButton(label, title, handler) {
        var button = document.createElement('button');
        button.type = 'button';
        button.className = 'button h18-vd-rich-button';
        button.innerHTML = label;
        button.title = title;
        button.addEventListener('pointerdown', function (event) {
            captureToolbarSelection();
            event.preventDefault();
        });
        button.addEventListener('mousedown', function (event) { event.preventDefault(); });
        button.addEventListener('click', function (event) {
            event.preventDefault();
            handler(event);
        });
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

        active = { textarea: textarea, editor: editor, dirty: false, savedRange: null, savedLogical: null, formatting: false, markerStart: null, markerEnd: null };

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

        ['mouseup','keyup'].forEach(function (eventName) {
            editor.addEventListener(eventName, function () {
                if (!active || active.editor !== editor || active.formatting) { return; }
                clearSelectionMarkers();
                selectionGeneration += 1;
                rememberSelection();
            });
        });
        editor.addEventListener('focus', function () {
            if (!active || active.editor !== editor || active.formatting || markerSelectionValid()) { return; }
            rememberSelection();
        });
        editor.addEventListener('input', function () {
            if (!active || active.editor !== editor) { return; }
            active.dirty = true;
            textarea.value = cleanHtml(editor.innerHTML);
            updateCanvasPreview(textarea.value);
            if (!active.formatting) {
                clearSelectionMarkers();
                selectionGeneration += 1;
                rememberSelection();
            }
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
        var userEntered = document.querySelector('[name="change_note_user_entered"]');
        if (userEntered && String(userEntered.value || '') === '1') { return; }

        var coreLabels = window.H18CleanHistory && typeof window.H18CleanHistory.labels === 'function'
            ? window.H18CleanHistory.labels()
            : [];
        if (Array.isArray(coreLabels) && coreLabels.length) {
            var seen = Object.create(null);
            var compactLabels = coreLabels.filter(function (label) { label = String(label || '').trim(); if (!label || seen[label]) { return false; } seen[label] = true; return true; }).slice(-6);
            if (!String(input.value || '').trim() && compactLabels.length) { input.value = compactLabels.join(' · '); }
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
            document.addEventListener('submit', function (event) {
                if (event.target !== form) { return; }
                sync();
                augmentAutomaticNote();
            }, true);
        }
    }

    window.H18RichTextV0125 = {
        sync: sync,
        selectionOwner: 'v0135',
        selectionMode: 'boundary-markers-v0136',
        restoreSelection: function () {
            if (!active) { return false; }
            if (markerSelectionValid()) { return restoreMarkerSelection(); }
            return active.savedLogical ? restoreLogicalSelection(active.savedLogical) : restoreSelection();
        }
    };
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
