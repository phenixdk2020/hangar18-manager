(function () {
    'use strict';

    if (window.__h18SavedLayoutRebuildV0890) { return; }

    const VERSION = '0.8.90';
    const HOST_ID = 'h18-page-sections-sortable';
    const PROXY_CLASS = 'h18-v0890-saved-layout';
    const CHILD_ATTR = 'data-h18-v0890-generic-child-source';
    const READY_ATTR = 'data-h18-v0890-layout-ready';
    const AUTO_LABEL = 'Auto-kasser';
    const COLUMN_COUNT = 12;

    let frame = 0;
    let rendering = false;
    let lastDiagnosticSignature = '';

    function host() {
        return document.getElementById(HOST_ID);
    }

    function activeRows() {
        const root = host();
        if (!root) { return []; }
        return Array.from(root.children).filter(function (node) {
            return node && node.classList &&
                node.classList.contains('h18-page-section-row') &&
                !node.classList.contains('h18-page-section-removed');
        });
    }

    function directPreview(row) {
        if (!row) { return null; }
        return Array.from(row.children).find(function (node) {
            return node && node.classList && node.classList.contains('h18-canvas-preview');
        }) || null;
    }

    function field(row, name, className) {
        if (!row) { return null; }
        let node = className ? row.querySelector('.' + className) : null;
        if (!node) { node = row.querySelector('[name$="[' + name + ']"]'); }
        if (!node && row.classList.contains('is-selected')) {
            const inspector = document.getElementById('h18-page-inspector-target');
            if (inspector) {
                node = className ? inspector.querySelector('.' + className) : null;
                if (!node) { node = inspector.querySelector('[name$="[' + name + ']"]'); }
            }
        }
        return node || null;
    }

    function value(row, name, fallback, className) {
        const node = field(row, name, className);
        if (!node) { return fallback; }
        if (node.type === 'checkbox') { return Boolean(node.checked); }
        const result = node.value;
        return result === undefined || result === null || String(result) === '' ? fallback : result;
    }

    function rowKey(row) {
        return String(value(row, 'Key', '', 'h18-page-section-key') || row && row.getAttribute('data-key') || '').trim();
    }

    function rowType(row) {
        return String(row && row.getAttribute('data-section-type') || value(row, 'Type', '') || '').trim().toLowerCase();
    }

    function parentKey(row) {
        return String(value(row, 'LayoutParentKey', '', 'h18-layout-parent-key') || '').trim();
    }

    function rowLabel(row) {
        return String(value(row, 'NavigatorLabel', '', 'h18-section-navigator-label') || '').trim();
    }

    function rowByKey(rows, wanted) {
        wanted = String(wanted || '').trim();
        if (!wanted) { return null; }
        return rows.find(function (row) { return rowKey(row) === wanted; }) || null;
    }

    function isGenericParent(row) {
        const type = rowType(row);
        if (type === 'flex') { return true; }
        if (type !== 'grid') { return false; }
        return rowLabel(row) !== AUTO_LABEL;
    }

    function childRows(rows, parent) {
        const key = rowKey(parent);
        if (!key) { return []; }
        return rows.filter(function (row) { return parentKey(row) === key; });
    }

    function resizeApi() {
        return window.__h18LegoResizeV0841 || null;
    }

    function stackApi() {
        return window.__h18LegoFixesV0851 || null;
    }

    function spanState(key) {
        const api = resizeApi();
        if (!api || typeof api.stateForKey !== 'function' || !key) { return {}; }
        try { return api.stateForKey(key) || {}; } catch (ignore) { return {}; }
    }

    function stackState(key) {
        const api = stackApi();
        if (!api || typeof api.stackStateForKey !== 'function' || !key) { return {}; }
        try { return api.stackStateForKey(key) || {}; } catch (ignore) { return {}; }
    }

    function intValue(raw, fallback) {
        const parsed = parseInt(raw, 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function desktopSpan(key) {
        const state = spanState(key);
        return Math.max(0, Math.min(COLUMN_COUNT, intValue(state && state.Desktop && state.Desktop.Span, 0)));
    }

    function equalSpans(count) {
        count = Math.max(1, Math.min(COLUMN_COUNT, intValue(count, 1)));
        const base = Math.floor(COLUMN_COUNT / count);
        let remainder = COLUMN_COUNT - (base * count);
        const result = [];
        for (let index = 0; index < count; index += 1) {
            result.push(base + (remainder > 0 ? 1 : 0));
            if (remainder > 0) { remainder -= 1; }
        }
        return result;
    }

    function stackGroups(children) {
        const childKeys = new Set(children.map(rowKey));
        const rootFor = {};

        children.forEach(function (row) {
            const key = rowKey(row);
            const state = stackState(key);
            const root = String(state && state.StackRootKey || '').trim();
            rootFor[key] = root && root !== key && childKeys.has(root) ? root : '';
        });

        const roots = children.filter(function (row) { return !rootFor[rowKey(row)]; });
        return roots.map(function (root) {
            const key = rowKey(root);
            const members = children.filter(function (candidate) { return rootFor[rowKey(candidate)] === key; });
            members.sort(function (a, b) {
                return intValue(stackState(rowKey(a)).StackOrder, 0) - intValue(stackState(rowKey(b)).StackOrder, 0);
            });
            return { root: root, members: members };
        });
    }

    function ensureImplicitSpans(groups) {
        if (!groups || groups.length < 2) { return false; }
        const api = resizeApi();
        if (!api || typeof api.writeStateForKey !== 'function') { return false; }

        const roots = groups.map(function (group) { return rowKey(group.root); });
        const current = roots.map(desktopSpan);
        if (!current.every(function (span) { return span === 0; })) { return false; }

        const spans = equalSpans(roots.length);
        let changed = false;
        roots.forEach(function (key, index) {
            const state = spanState(key);
            if (!state || typeof state !== 'object') { return; }
            if (!state.Desktop || typeof state.Desktop !== 'object') { state.Desktop = {}; }
            state.Desktop.Span = spans[index];
            try {
                if (api.writeStateForKey(key, state, false)) { changed = true; }
            } catch (ignore) {}
        });
        return changed;
    }

    function effectiveSpans(groups) {
        if (!groups.length) { return []; }
        const explicit = groups.map(function (group) { return desktopSpan(rowKey(group.root)); });
        if (explicit.every(function (span) { return span === 0; })) { return equalSpans(groups.length); }

        const result = explicit.slice();
        const auto = [];
        let used = 0;
        result.forEach(function (span, index) {
            if (span > 0) { used += span; } else { auto.push(index); }
        });

        if (used > COLUMN_COUNT) {
            while (used > COLUMN_COUNT) {
                let best = -1;
                result.forEach(function (span, index) {
                    if (span > 1 && (best < 0 || span > result[best])) { best = index; }
                });
                if (best < 0) { break; }
                result[best] -= 1;
                used -= 1;
            }
        }

        if (auto.length) {
            let remaining = Math.max(auto.length, COLUMN_COUNT - used);
            auto.forEach(function (index, offset) {
                const slots = auto.length - offset;
                const span = Math.max(1, Math.floor(remaining / slots));
                result[index] = span;
                remaining -= span;
            });
        }

        return result.map(function (span) { return Math.max(1, Math.min(COLUMN_COUNT, span || 1)); });
    }

    function displayName(row) {
        const label = rowLabel(row);
        if (label && label !== AUTO_LABEL) { return label; }
        const summary = row && row.querySelector('.h18-page-section-title-summary');
        const text = String(summary && summary.textContent || '').trim();
        if (text) { return text; }
        const names = {
            grid: 'Række- og kolonne-kasse', flex: 'Flex', text: 'Tekst', image: 'Billede',
            text_image: 'Tekst + billede', container: 'Kasse', buttons: 'Knapper'
        };
        return names[rowType(row)] || rowType(row) || 'Element';
    }

    function cleanClone(row) {
        const preview = directPreview(row);
        if (!preview) { return null; }
        const clone = preview.cloneNode(true);
        clone.removeAttribute('id');
        clone.querySelectorAll('[id]').forEach(function (node) { node.removeAttribute('id'); });
        clone.querySelectorAll('[name]').forEach(function (node) { node.removeAttribute('name'); });
        clone.querySelectorAll(
            '.h18-v0890-saved-layout,.h18-v0889-saved-layout,' +
            '.h18-ud-box-contents-preview,.h18-ud-auto-box-grid,' +
            '.h18-v0810-side-zones,.h18-v0811-side-zones,.h18-v0814-auto-drop-zone,.h18-v0814-auto-kasse-drop,' +
            '.h18-v0838-drop-overlay,.h18-v0838-drop-zone,.h18-v0841-resize-handle,.h18-v0841-resize-rail'
        ).forEach(function (node) { node.remove(); });
        clone.querySelectorAll('input,select,textarea,button').forEach(function (node) {
            node.disabled = true;
            node.setAttribute('tabindex', '-1');
        });
        clone.querySelectorAll('a').forEach(function (node) { node.setAttribute('tabindex', '-1'); });
        return clone;
    }

    function editButton(key, label) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'button button-small h18-v0811-edit-child';
        button.setAttribute('data-h18-v0811-edit-child', key);
        button.textContent = label || 'Rediger';
        return button;
    }

    function bar(row, span) {
        const node = document.createElement('div');
        node.className = 'h18-v0890-layout-bar';

        const title = document.createElement('strong');
        title.textContent = displayName(row);
        node.appendChild(title);

        const actions = document.createElement('span');
        actions.className = 'h18-v0890-layout-actions';
        if (span > 0) {
            const badge = document.createElement('em');
            badge.className = 'h18-v0890-span-badge';
            badge.textContent = span + '/' + COLUMN_COUNT;
            actions.appendChild(badge);
        }
        actions.appendChild(editButton(rowKey(row), 'Rediger'));
        node.appendChild(actions);
        return node;
    }

    function renderParent(parent, rows) {
        const key = rowKey(parent);
        const preview = directPreview(parent);
        if (!key || !preview) { return null; }

        const children = childRows(rows, parent);
        preview.querySelectorAll(':scope > .h18-v0890-saved-layout,:scope > .h18-v0889-saved-layout').forEach(function (node) { node.remove(); });
        if (!children.length) { return { parentKey: key, childKeys: [], proxy: false, spans: [] }; }

        const groups = stackGroups(children);
        ensureImplicitSpans(groups);
        const spans = effectiveSpans(groups);

        const wrapper = document.createElement('div');
        const direction = String(value(parent, 'LayoutDirection', 'Row') || 'Row').toLowerCase();
        const type = rowType(parent);
        wrapper.className = PROXY_CLASS + (
            type === 'grid'
                ? ' h18-v0890-saved-layout--grid'
                : (direction === 'column' ? ' h18-v0890-saved-layout--flex-column' : ' h18-v0890-saved-layout--flex-row')
        );
        wrapper.setAttribute('data-h18-v0890-parent', key);
        wrapper.style.setProperty('--h18-v0890-gap', Math.max(0, intValue(value(parent, 'LayoutGapPx', 16), 16)) + 'px');

        groups.forEach(function (group, index) {
            const root = group.root;
            const rootKey = rowKey(root);
            const span = spans[index] || COLUMN_COUNT;

            const tile = document.createElement('section');
            tile.className = 'h18-v0811-auto-box h18-v0890-layout-column';
            tile.setAttribute('data-h18-v0811-row', rootKey);
            tile.setAttribute('data-h18-v0840-auto-child', rootKey);
            tile.setAttribute('data-h18-v0890-span', String(span));
            tile.style.setProperty('--h18-v0890-span', String(span));
            tile.appendChild(bar(root, span));

            const body = document.createElement('div');
            body.className = 'h18-v0811-auto-box-preview h18-v0890-layout-body';
            const rootClone = cleanClone(root);
            if (rootClone) { body.appendChild(rootClone); }

            if (group.members.length) {
                const stack = document.createElement('div');
                stack.className = 'h18-v0890-stack';
                group.members.forEach(function (member) {
                    const memberKey = rowKey(member);
                    const card = document.createElement('section');
                    card.className = 'h18-v0811-child-card h18-v0890-stack-member';
                    card.setAttribute('data-h18-v0811-child', memberKey);
                    card.appendChild(bar(member, 0));

                    const memberPreview = document.createElement('div');
                    memberPreview.className = 'h18-v0811-child-preview h18-v0890-stack-member-preview';
                    const memberClone = cleanClone(member);
                    if (memberClone) { memberPreview.appendChild(memberClone); }
                    card.appendChild(memberPreview);
                    stack.appendChild(card);
                });
                body.appendChild(stack);
            }

            tile.appendChild(body);
            wrapper.appendChild(tile);
        });

        preview.appendChild(wrapper);
        const ready = wrapper.isConnected && wrapper.parentNode === preview;
        if (ready) {
            children.forEach(function (row) { row.setAttribute(CHILD_ATTR, key); });
        }

        return {
            parentKey: key,
            childKeys: children.map(rowKey),
            rootKeys: groups.map(function (group) { return rowKey(group.root); }),
            proxy: ready,
            spans: spans
        };
    }

    function diagnostics(results) {
        const root = host();
        const rows = activeRows();
        const hiddenSources = rows.filter(function (row) { return row.hasAttribute(CHILD_ATTR); });
        const proxies = root ? root.querySelectorAll('.' + PROXY_CLASS) : [];
        return {
            version: VERSION,
            rendererMarker: document.documentElement.getAttribute('data-h18-saved-layout-rebuild') || '',
            ready: Boolean(root && root.getAttribute(READY_ATTR) === '1'),
            proxyCount: proxies.length,
            hiddenSourceCount: hiddenSources.length,
            hiddenSourceKeys: hiddenSources.map(rowKey),
            parents: Array.isArray(results) ? results : []
        };
    }

    function recordDiagnostics(results) {
        const detail = diagnostics(results);
        const signature = JSON.stringify(detail);
        if (signature === lastDiagnosticSignature) { return; }
        lastDiagnosticSignature = signature;

        const trace = window.__h18UltimateDesignerTraceV0876;
        if (trace && typeof trace.record === 'function') {
            try { trace.record('DIAG_LAYOUT_REBUILD_V0890', document.body, detail, { force: true }); } catch (ignore) {}
        }
        const live = window.__h18LiveDiagnosticsV0888;
        if (live && typeof live.flush === 'function') {
            window.setTimeout(function () { try { live.flush(); } catch (ignore) {} }, 20);
        }
    }

    function render() {
        frame = 0;
        if (rendering) { return; }
        const root = host();
        if (!root) { return; }

        rendering = true;
        const results = [];
        try {
            const rows = activeRows();
            rows.forEach(function (row) { row.removeAttribute(CHILD_ATTR); });
            root.removeAttribute(READY_ATTR);

            rows.forEach(function (row) {
                if (!isGenericParent(row)) { return; }
                const result = renderParent(row, rows);
                if (result && result.proxy) { results.push(result); }
            });

            if (results.length) { root.setAttribute(READY_ATTR, '1'); }
            document.documentElement.setAttribute('data-h18-saved-layout-rebuild', VERSION);
        } finally {
            rendering = false;
        }
        recordDiagnostics(results);
    }

    function schedule() {
        if (frame) { return; }
        frame = window.requestAnimationFrame(render);
    }

    function canonicalizeBeforeSubmit() {
        const rows = activeRows();
        rows.filter(isGenericParent).forEach(function (parent) {
            ensureImplicitSpans(stackGroups(childRows(rows, parent)));
        });
        render();
    }

    function install() {
        const root = host();
        if (!root) {
            window.setTimeout(install, 80);
            return;
        }

        const form = document.getElementById('h18-page-editor-form');
        if (form && form.getAttribute('data-h18-v0890-span-submit') !== '1') {
            form.setAttribute('data-h18-v0890-span-submit', '1');
            form.addEventListener('submit', canonicalizeBeforeSubmit, true);
        }

        if (window.MutationObserver) {
            const observer = new MutationObserver(function (mutations) {
                if (rendering) { return; }
                if (mutations.some(function (mutation) { return mutation.type === 'childList'; })) { schedule(); }
            });
            observer.observe(root, { childList: true, subtree: true });

            const canvas = document.querySelector('.h18-builder-canvas');
            if (canvas) {
                new MutationObserver(schedule).observe(canvas, {
                    attributes: true,
                    attributeFilter: ['data-canvas-device']
                });
            }
        }

        document.addEventListener('change', schedule, false);
        document.addEventListener('input', schedule, false);
        document.addEventListener('click', function () { window.setTimeout(schedule, 0); }, false);

        [0, 60, 180, 500, 1200, 2500].forEach(function (delay) {
            window.setTimeout(schedule, delay);
        });
    }

    window.__h18SavedLayoutRebuildV0890 = {
        version: VERSION,
        refresh: render,
        diagnostics: function () { return diagnostics(); },
        canonicalizeSpans: canonicalizeBeforeSubmit
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
