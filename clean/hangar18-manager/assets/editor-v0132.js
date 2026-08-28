(function () {
    'use strict';

    /*
     * Visual Designer Manager 0.1.32 contract hardening.
     *
     * VD-TEXT-SEL-001:
     * A rich-text selection must survive Bold/Italic/Underline and chained
     * toolbar commands, even when the browser rewrites text nodes.
     *
     * VD-BUTTON-TYPE-001:
     * A palette Button is always canonical type=button. When hierarchy rules
     * reject a root-level Button drop, make the rejection explicit so the
     * previously selected Text node cannot be mistaken for a newly created Button.
     */

    var richSnapshot = null;
    var richRestoreUntil = 0;
    var richRestoreScheduled = false;
    var paletteDrag = null;
    var noticeTimer = 0;

    function richEditorForButton(button) {
        var shell = button && button.closest ? button.closest('.h18-vd-rich-shell') : null;
        return shell ? shell.querySelector('.h18-vd-rich-editor') : null;
    }

    function selectionBelongsToEditor(editor, range) {
        if (!editor || !range) { return false; }
        var common = range.commonAncestorContainer;
        if (common && common.nodeType !== 1) { common = common.parentNode; }
        return !!(common && (common === editor || editor.contains(common)));
    }

    function captureRichSelection(editor) {
        if (!editor || !editor.isConnected || !window.getSelection) { return null; }
        var selection = window.getSelection();
        if (!selection || !selection.rangeCount) { return null; }
        var range = selection.getRangeAt(0);
        if (!selectionBelongsToEditor(editor, range) || range.collapsed) { return null; }
        try {
            var startProbe = document.createRange();
            startProbe.selectNodeContents(editor);
            startProbe.setEnd(range.startContainer, range.startOffset);
            var endProbe = document.createRange();
            endProbe.selectNodeContents(editor);
            endProbe.setEnd(range.endContainer, range.endOffset);
            var start = startProbe.toString().length;
            var end = endProbe.toString().length;
            if (end <= start) { return null; }
            return { editor: editor, start: start, end: end };
        } catch (ignore) {
            return null;
        }
    }

    function pointAtOffset(editor, requestedOffset) {
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

    function restoreRichSelection(snapshot) {
        if (!snapshot || !snapshot.editor || !snapshot.editor.isConnected || !window.getSelection) { return false; }
        var editor = snapshot.editor;
        var start = pointAtOffset(editor, snapshot.start);
        var end = pointAtOffset(editor, Math.max(snapshot.start, snapshot.end));
        try {
            var range = document.createRange();
            range.setStart(start.node, start.offset);
            range.setEnd(end.node, end.offset);
            if (range.collapsed && snapshot.end > snapshot.start) { return false; }
            try { editor.focus({ preventScroll: true }); } catch (ignoreFocus) { editor.focus(); }
            var selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
            return true;
        } catch (ignore) {
            return false;
        }
    }

    function restoreBurst(snapshot) {
        if (!snapshot || !snapshot.editor) { return; }
        richRestoreUntil = Date.now() + 320;
        var restore = function () {
            if (!snapshot.editor.isConnected) { return; }
            if (restoreRichSelection(snapshot)) { richSnapshot = snapshot; }
        };

        if (window.queueMicrotask) { window.queueMicrotask(restore); }
        else if (window.Promise) { Promise.resolve().then(restore); }
        window.setTimeout(restore, 0);
        window.setTimeout(restore, 24);
        window.setTimeout(restore, 80);
        window.setTimeout(restore, 180);
        if (window.requestAnimationFrame) {
            window.requestAnimationFrame(function () {
                restore();
                window.requestAnimationFrame(restore);
            });
        }
    }

    function armRichSelection(button) {
        var editor = richEditorForButton(button);
        if (!editor) { return null; }
        var fresh = captureRichSelection(editor);
        if (fresh) { richSnapshot = fresh; }
        if (richSnapshot && richSnapshot.editor === editor) { return richSnapshot; }
        return null;
    }

    document.addEventListener('selectionchange', function () {
        var selection = window.getSelection && window.getSelection();
        if (selection && selection.rangeCount) {
            var range = selection.getRangeAt(0);
            var common = range.commonAncestorContainer;
            if (common && common.nodeType !== 1) { common = common.parentNode; }
            var editor = common && common.closest ? common.closest('.h18-vd-rich-editor') : null;
            if (editor && !range.collapsed) {
                var fresh = captureRichSelection(editor);
                if (fresh) { richSnapshot = fresh; }
                return;
            }
        }

        if (richSnapshot && Date.now() < richRestoreUntil && !richRestoreScheduled) {
            richRestoreScheduled = true;
            var run = function () {
                richRestoreScheduled = false;
                if (Date.now() < richRestoreUntil) { restoreRichSelection(richSnapshot); }
            };
            if (window.requestAnimationFrame) { window.requestAnimationFrame(run); }
            else { window.setTimeout(run, 0); }
        }
    });

    ['pointerdown', 'mousedown'].forEach(function (eventName) {
        document.addEventListener(eventName, function (event) {
            var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;
            if (!button) { return; }
            armRichSelection(button);
        }, true);
    });

    document.addEventListener('keydown', function (event) {
        var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;
        if (!button || (event.key !== 'Enter' && event.key !== ' ')) { return; }
        armRichSelection(button);
    }, true);

    document.addEventListener('click', function (event) {
        var button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;
        if (!button) { return; }
        var snapshot = armRichSelection(button);
        if (!snapshot) { return; }
        restoreBurst({ editor: snapshot.editor, start: snapshot.start, end: snapshot.end });
    }, false);

    function modelTypes() {
        var field = document.getElementById('h18-clean-model-json');
        var result = Object.create(null);
        if (!field) { return result; }
        try {
            var model = JSON.parse(field.value || '{}');
            (Array.isArray(model && model.nodes) ? model.nodes : []).forEach(function (node) {
                if (node && node.id) { result[String(node.id)] = String(node.type || '').toLowerCase(); }
            });
        } catch (ignore) {}
        return result;
    }

    function showNotice(message, error) {
        var el = document.getElementById('h18-v0132-contract-notice');
        if (!el) {
            el = document.createElement('div');
            el.id = 'h18-v0132-contract-notice';
            el.setAttribute('role', 'status');
            el.setAttribute('aria-live', 'polite');
            document.body.appendChild(el);
        }
        el.className = 'h18-v0132-contract-notice' + (error ? ' is-error' : '');
        el.textContent = String(message || '');
        el.classList.add('is-visible');
        window.clearTimeout(noticeTimer);
        noticeTimer = window.setTimeout(function () { el.classList.remove('is-visible'); }, 4200);
    }

    function dragBadge(show) {
        var el = document.getElementById('h18-v0132-button-drag-badge');
        if (!show) {
            if (el) { el.remove(); }
            document.body.removeAttribute('data-h18-v0132-palette-type');
            return;
        }
        if (!el) {
            el = document.createElement('div');
            el.id = 'h18-v0132-button-drag-badge';
            el.className = 'h18-v0132-button-drag-badge';
            el.textContent = 'TRÆKKER KNAP · slip på canvas, i Sektion eller Kasse';
            document.body.appendChild(el);
        }
        document.body.setAttribute('data-h18-v0132-palette-type', 'button');
    }

    function paletteType(target) {
        var button = target && target.closest ? target.closest('.h18-clean-add[data-type]') : null;
        return button ? String(button.getAttribute('data-type') || '').toLowerCase() : '';
    }

    window.addEventListener('dragstart', function (event) {
        var type = paletteType(event.target);
        if (!type) { return; }
        paletteDrag = { type: type, before: modelTypes() };
        if (type === 'button') { dragBadge(true); }
    }, true);

    window.addEventListener('drop', function () {
        if (!paletteDrag) { return; }
        var attempt = { type: paletteDrag.type, before: paletteDrag.before };
        window.setTimeout(function () {
            var after = modelTypes();
            var added = Object.keys(after).filter(function (id) { return !Object.prototype.hasOwnProperty.call(attempt.before, id); });
            if (attempt.type !== 'button') { return; }
            if (!added.length) {
                showNotice('Knap blev ikke oprettet. Slip Knap på canvas eller i en Sektion/Kasse – det valgte element er stadig det gamle element.', true);
                return;
            }
            var buttonIds = added.filter(function (id) { return after[id] === 'button'; });
            if (!buttonIds.length) {
                showNotice('Typekontrol fejlede: palette-elementet KNAP må kun oprettes som canonical type button.', true);
                return;
            }
            showNotice('Knap oprettet som KNAP.', false);
        }, 40);
    }, true);

    window.addEventListener('dragend', function () {
        paletteDrag = null;
        dragBadge(false);
    }, true);

    window.H18VisualDesignerV0132 = {
        captureRichSelection: captureRichSelection,
        restoreRichSelection: restoreRichSelection,
        verifyButtonType: function () {
            var types = modelTypes();
            return Object.keys(types).filter(function (id) { return types[id] === 'button'; });
        }
    };
}());
