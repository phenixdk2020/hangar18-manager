from pathlib import Path

p = Path('clean/hangar18-manager/assets/editor-v0125.js')
s = p.read_text(encoding='utf-8')
start = s.index('    function command(name, value) {')
end = s.index('    function updateCanvasPreview(html) {', start)
new = r'''    var INLINE_FORMAT_TAGS = { bold: 'STRONG', italic: 'EM', underline: 'U' };

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
        if (!tagName || !snapshot || !restoreLogicalSelection(snapshot) || !window.getSelection) { return false; }
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
        restoreLogicalSelection(snapshot);
        return true;
    }

    function command(name, value) {
        if (!active || !active.editor) { return; }
        var logicalSelection = active.savedLogical || captureLogicalSelection(active.editor);
        if (logicalSelection) { restoreLogicalSelection(logicalSelection); }
        else { restoreSelection(); }

        active.formatting = true;
        try {
            if (INLINE_FORMAT_TAGS[String(name || '').toLowerCase()] && logicalSelection) {
                applyInlineFormat(name, logicalSelection);
            } else {
                try { document.execCommand('styleWithCSS', false, 'false'); } catch (ignoreStyleMode) {}
                try { document.execCommand(name, false, value || null); } catch (ignoreCommand) {}
                try { active.editor.normalize(); } catch (ignoreNormalize) {}
                if (logicalSelection) { restoreLogicalSelection(logicalSelection); }
                else { rememberSelection(); }
            }
        } finally { active.formatting = false; }

        if (logicalSelection) { active.savedLogical = logicalSelection; }
        active.dirty = true;
        active.textarea.value = cleanHtml(active.editor.innerHTML);
        updateCanvasPreview(active.textarea.value);
        reinforceLogicalSelection(logicalSelection);
    }

'''
s = s[:start] + new + s[end:]
s = s.replace("button.addEventListener('pointerdown', function () { captureToolbarSelection(); });", "button.addEventListener('pointerdown', function (event) { captureToolbarSelection(); event.preventDefault(); });", 1)
s = s.replace("selectionOwner: 'v0134'", "selectionOwner: 'v0135'", 1)
p.write_text(s, encoding='utf-8')
print('rich-text patch applied')
