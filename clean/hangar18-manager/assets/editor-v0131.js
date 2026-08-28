(function () {
    'use strict';

    const CFG = window.H18CleanEditor || {};
    const UNITS = Math.max(12, parseInt(CFG.units || 120, 10) || 120);
    const ROW_PX = Math.max(2, parseInt(CFG.rowPx || 8, 10) || 8);

    let richSelection = null;
    let floatingDrag = null;

    function clamp(value, min, max) {
        return Math.max(min, Math.min(max, value));
    }

    function cleanId(value) {
        return String(value || '').toLowerCase().replace(/[^a-z0-9._-]/g, '').slice(0, 100);
    }

    /*
     * 0.1.31 rich-text selection preservation.
     *
     * execCommand can replace text nodes when Bold/Italic are toggled. A cloned
     * DOM Range can therefore collapse even though the command itself succeeds.
     * Store logical character offsets before the toolbar command and rebuild a
     * fresh Range after the command has mutated the DOM.
     */
    function captureTextOffsets(editor) {
        if (!editor || !window.getSelection) { return null; }
        const selection = window.getSelection();
        if (!selection || !selection.rangeCount) { return null; }
        const range = selection.getRangeAt(0);
        const common = range.commonAncestorContainer.nodeType === 1
            ? range.commonAncestorContainer
            : range.commonAncestorContainer.parentNode;
        if (!common || !editor.contains(common)) { return null; }

        try {
            const startProbe = range.cloneRange();
            startProbe.selectNodeContents(editor);
            startProbe.setEnd(range.startContainer, range.startOffset);
            const endProbe = range.cloneRange();
            endProbe.selectNodeContents(editor);
            endProbe.setEnd(range.endContainer, range.endOffset);
            return {
                editor: editor,
                start: startProbe.toString().length,
                end: endProbe.toString().length
            };
        } catch (ignore) {
            return null;
        }
    }

    function textPointAtOffset(editor, requestedOffset) {
        let remaining = Math.max(0, parseInt(requestedOffset || 0, 10) || 0);
        const walker = document.createTreeWalker(editor, NodeFilter.SHOW_TEXT);
        let node = walker.nextNode();
        let last = null;
        while (node) {
            last = node;
            const length = String(node.nodeValue || '').length;
            if (remaining <= length) {
                return { node: node, offset: remaining };
            }
            remaining -= length;
            node = walker.nextNode();
        }
        if (last) {
            return { node: last, offset: String(last.nodeValue || '').length };
        }
        return { node: editor, offset: 0 };
    }

    function restoreTextOffsets(snapshot) {
        if (!snapshot || !snapshot.editor || !snapshot.editor.isConnected || !window.getSelection) { return; }
        const editor = snapshot.editor;
        const start = textPointAtOffset(editor, snapshot.start);
        const end = textPointAtOffset(editor, Math.max(snapshot.start, snapshot.end));
        try {
            const range = document.createRange();
            range.setStart(start.node, start.offset);
            range.setEnd(end.node, end.offset);
            editor.focus({ preventScroll: true });
            const selection = window.getSelection();
            selection.removeAllRanges();
            selection.addRange(range);
        } catch (ignore) {}
    }

    document.addEventListener('mousedown', function (event) {
        if (window.H18RichTextV0125 && window.H18RichTextV0125.selectionOwner === 'v0134') { return; }
        const button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;
        if (!button) { return; }
        const shell = button.closest('.h18-vd-rich-shell');
        const editor = shell ? shell.querySelector('.h18-vd-rich-editor') : null;
        richSelection = captureTextOffsets(editor);
    }, true);

    document.addEventListener('click', function (event) {
        if (window.H18RichTextV0125 && window.H18RichTextV0125.selectionOwner === 'v0134') { return; }
        const button = event.target && event.target.closest ? event.target.closest('.h18-vd-rich-button') : null;
        if (!button || !richSelection) { return; }
        const snapshot = richSelection;
        window.setTimeout(function () {
            restoreTextOffsets(snapshot);
            richSelection = captureTextOffsets(snapshot.editor) || snapshot;
        }, 0);
    }, false);

    /*
     * 0.1.31 true floating Button interaction.
     *
     * A floating Button is still a canonical Button node, but its move handle
     * must not enter the normal HTML5 cell-split/re-parent drag flow. It is
     * dragged directly inside its current parent surface and the resulting X/Y
     * is committed back through the existing Inspector, keeping the canonical
     * Save/Undo/Redo model as the only source of truth.
     */
    function floatingCardFromTarget(target) {
        if (!target || !target.closest) { return null; }
        const handle = target.closest('.h18-clean-move');
        if (!handle) { return null; }
        const card = handle.closest('.h18-clean-node--button.is-floating[data-h18-floating="1"]');
        return card || null;
    }

    function floatingHandle(card) {
        if (!card) { return null; }
        return card.querySelector(':scope > .h18-clean-node-header .h18-clean-move');
    }

    function refreshFloatingHandles(root) {
        const scope = root && root.querySelectorAll ? root : document;
        scope.querySelectorAll('.h18-clean-node--button.is-floating[data-h18-floating="1"]').forEach(function (card) {
            const canonicalLayer = clamp(parseInt(card.style.zIndex || '20', 10) || 20, 1, 200);
            card.style.setProperty('--h18-vd-floating-layer', String(canonicalLayer));
            const handle = floatingHandle(card);
            if (!handle) { return; }
            handle.draggable = false;
            handle.setAttribute('draggable', 'false');
            handle.setAttribute('aria-label', 'Flyt flydende knap frit i aktuelt område');
            handle.title = 'Træk frit i aktuelt område · ingen celle-split';
        });
    }

    function selectFloatingCard(card) {
        if (!card || card.classList.contains('is-selected')) { return card; }
        const id = cleanId(card.getAttribute('data-node-id') || '');
        if (!id) { return card; }
        card.dispatchEvent(new MouseEvent('click', { bubbles: true, cancelable: true, view: window }));
        return document.querySelector('.h18-clean-node[data-node-id="' + CSS.escape(id) + '"]') || card;
    }

    function inspectorNumber(field, fallback) {
        const input = document.querySelector('#h18-clean-inspector [data-field="' + field + '"]');
        if (!input) { return fallback; }
        const value = parseInt(input.value || '', 10);
        return Number.isFinite(value) ? value : fallback;
    }

    function beginFloatingDrag(event, initialCard) {
        let card = selectFloatingCard(initialCard);
        if (!card || !card.isConnected) { return; }
        refreshFloatingHandles(card.parentElement || document);

        const id = cleanId(card.getAttribute('data-node-id') || '');
        const surface = card.parentElement;
        if (!id || !surface || !surface.classList.contains('h18-clean-surface')) { return; }

        const surfaceRect = surface.getBoundingClientRect();
        const cardRect = card.getBoundingClientRect();
        const startX = clamp(inspectorNumber('gx', 0), 0, UNITS - 1);
        const widthUnits = clamp(inspectorNumber('gw', Math.max(1, Math.round((cardRect.width / Math.max(1, surfaceRect.width)) * UNITS))), 1, UNITS - startX);
        const startY = Math.max(0, inspectorNumber('gy', 0));
        const unitPx = Math.max(0.1, surfaceRect.width / UNITS);

        floatingDrag = {
            pointerId: event.pointerId,
            id: id,
            card: card,
            surface: surface,
            startClientX: event.clientX,
            startClientY: event.clientY,
            startLeftPx: startX * unitPx,
            startTopPx: startY * ROW_PX,
            unitPx: unitPx,
            widthUnits: widthUnits,
            maxLeftPx: Math.max(0, (UNITS - widthUnits) * unitPx),
            x: startX,
            y: startY
        };
        card.classList.add('h18-v0131-floating-drag');
    }

    function moveFloatingDrag(event) {
        if (!floatingDrag || event.pointerId !== floatingDrag.pointerId) { return; }
        const drag = floatingDrag;
        if (!drag.card || !drag.card.isConnected) { floatingDrag = null; return; }
        const dx = event.clientX - drag.startClientX;
        const dy = event.clientY - drag.startClientY;
        const leftPx = clamp(drag.startLeftPx + dx, 0, drag.maxLeftPx);
        const topPx = Math.max(0, drag.startTopPx + dy);
        drag.x = clamp(Math.round(leftPx / drag.unitPx), 0, UNITS - drag.widthUnits);
        drag.y = clamp(Math.round(topPx / ROW_PX), 0, 10000);
        drag.card.style.left = leftPx + 'px';
        drag.card.style.top = topPx + 'px';
        event.preventDefault();
    }

    function commitInspectorField(field, value, done) {
        const control = document.querySelector('#h18-clean-inspector [data-field="' + field + '"]');
        if (!control) {
            if (done) { done(); }
            return;
        }
        control.value = String(value);
        control.dispatchEvent(new Event('change', { bubbles: true }));
        if (done) { window.requestAnimationFrame(done); }
    }

    function endFloatingDrag(event) {
        if (!floatingDrag || (event && event.pointerId !== floatingDrag.pointerId)) { return; }
        const drag = floatingDrag;
        floatingDrag = null;
        if (drag.card && drag.card.isConnected) { drag.card.classList.remove('h18-v0131-floating-drag'); }

        commitInspectorField('gx', drag.x, function () {
            commitInspectorField('gy', drag.y, function () {
                refreshFloatingHandles(document);
            });
        });
    }

    document.addEventListener('dragstart', function (event) {
        const card = floatingCardFromTarget(event.target);
        if (!card) { return; }
        event.preventDefault();
        event.stopPropagation();
    }, true);

    document.addEventListener('pointerdown', function (event) {
        if (event.button !== 0 || floatingDrag) { return; }
        const card = floatingCardFromTarget(event.target);
        if (!card) { return; }
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
        beginFloatingDrag(event, card);
    }, true);

    document.addEventListener('pointermove', moveFloatingDrag, true);
    document.addEventListener('pointerup', endFloatingDrag, true);
    document.addEventListener('pointercancel', function (event) {
        if (!floatingDrag || event.pointerId !== floatingDrag.pointerId) { return; }
        const drag = floatingDrag;
        floatingDrag = null;
        if (drag.card && drag.card.isConnected) {
            drag.card.classList.remove('h18-v0131-floating-drag');
            drag.card.style.left = '';
            drag.card.style.top = '';
        }
    }, true);

    function install() {
        refreshFloatingHandles(document);
        const canvas = document.getElementById('h18-clean-canvas');
        const inspector = document.getElementById('h18-clean-inspector');
        const target = canvas && canvas.parentElement ? canvas.parentElement : (inspector || document.body);
        if (target && window.MutationObserver) {
            new MutationObserver(function () { refreshFloatingHandles(document); }).observe(target, { childList: true, subtree: true });
        }
    }

    window.H18VisualDesignerV0131 = {
        refreshFloatingHandles: function () { refreshFloatingHandles(document); },
        restoreRichSelection: function () { if (richSelection) { restoreTextOffsets(richSelection); } }
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
