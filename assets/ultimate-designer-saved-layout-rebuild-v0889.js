(function () {
    'use strict';

    if (window.__h18SavedLayoutRebuildV0889) { return; }

    const VERSION = '0.8.89';
    const HOST_ID = 'h18-page-sections-sortable';
    const ROW_SELECTOR = ':scope > .h18-page-section-row:not(.h18-page-section-removed)';
    const PROXY_CLASS = 'h18-v0889-saved-layout';
    const CHILD_ATTR = 'data-h18-v0889-generic-child-source';
    const AUTO_LABEL = 'Auto-kasser';
    let scheduled = 0;
    let rendering = false;

    function host() { return document.getElementById(HOST_ID); }
    function rows() {
        const node = host();
        return node ? Array.from(node.querySelectorAll(ROW_SELECTOR)) : [];
    }
    function control(row, fieldName) {
        if (!row) { return null; }
        const selector = '[name$="[' + fieldName + ']"]';
        let node = row.querySelector(selector);
        if (!node && row.classList.contains('is-selected')) {
            const inspector = document.getElementById('h18-page-inspector-target');
            node = inspector ? inspector.querySelector(selector) : null;
        }
        return node || null;
    }
    function value(row, fieldName, fallback) {
        const node = control(row, fieldName);
        if (!node) { return fallback; }
        if (node.type === 'checkbox') { return Boolean(node.checked); }
        return node.value === undefined || node.value === null || node.value === '' ? fallback : node.value;
    }
    function key(row) {
        const node = row && row.querySelector('.h18-page-section-key');
        return String(node && node.value || '').trim();
    }
    function type(row) { return String(row && row.getAttribute('data-section-type') || value(row, 'Type', '')).trim().toLowerCase(); }
    function parentKey(row) { return String(value(row, 'LayoutParentKey', '') || '').trim(); }
    function label(row) { return String(value(row, 'NavigatorLabel', '') || value(row, 'SectionNavigatorLabel', '') || '').trim(); }
    function rowByKey(allRows, wanted) {
        const target = String(wanted || '');
        return allRows.find(function (row) { return key(row) === target; }) || null;
    }
    function isGenericParent(row) {
        const rowType = type(row);
        if (rowType === 'flex') { return true; }
        if (rowType !== 'grid') { return false; }
        return label(row) !== AUTO_LABEL;
    }
    function childRows(allRows, parent) {
        const parentId = key(parent);
        return allRows.filter(function (row) { return parentKey(row) === parentId; });
    }
    function resizeState(sectionKey) {
        const api = window.__h18LegoResizeV0841;
        try { return api && typeof api.stateForKey === 'function' ? api.stateForKey(sectionKey) || {} : {}; }
        catch (ignore) { return {}; }
    }
    function stackState(sectionKey) {
        const api = window.__h18LegoFixesV0851;
        try { return api && typeof api.stackStateForKey === 'function' ? api.stackStateForKey(sectionKey) || {} : {}; }
        catch (ignore) { return {}; }
    }
    function canvasDevice() {
        const canvas = document.querySelector('.h18-builder-canvas');
        return String(canvas && canvas.getAttribute('data-canvas-device') || 'desktop').toLowerCase();
    }
    function int(value, fallback) {
        const parsed = parseInt(value, 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }
    function effectiveSpan(sectionKey) {
        const state = resizeState(sectionKey);
        const desktop = Math.max(0, Math.min(12, int(state && state.Desktop && state.Desktop.Span, 0)));
        const device = canvasDevice();
        if (device === 'desktop') { return desktop; }
        const branchName = device === 'mobile' ? 'Mobile' : 'Tablet';
        const branch = state && state[branchName] || {};
        const inherit = branch.InheritDesktop === undefined ? true : Boolean(branch.InheritDesktop);
        return inherit ? desktop : Math.max(0, Math.min(12, int(branch.Span, 0)));
    }
    function resolvedSpans(rootKeys) {
        const raw = rootKeys.map(effectiveSpan);
        if (!raw.length) { return []; }
        if (raw.every(function (span) { return span <= 0; })) {
            const base = Math.floor(12 / raw.length);
            let remainder = 12 - (base * raw.length);
            return raw.map(function () {
                const value = Math.max(1, base + (remainder > 0 ? 1 : 0));
                if (remainder > 0) { remainder -= 1; }
                return value;
            });
        }

        const result = raw.map(function (span) { return span > 0 ? span : 0; });
        const auto = [];
        result.forEach(function (span, index) { if (span <= 0) { auto.push(index); } });
        let explicitTotal = result.reduce(function (sum, span) { return sum + span; }, 0);

        while (explicitTotal + auto.length > 12) {
            let changed = false;
            for (let index = result.length - 1; index >= 0 && explicitTotal + auto.length > 12; index -= 1) {
                if (result[index] > 1) {
                    result[index] -= 1;
                    explicitTotal -= 1;
                    changed = true;
                }
            }
            if (!changed) { break; }
        }

        if (auto.length) {
            let remaining = Math.max(auto.length, 12 - explicitTotal);
            auto.forEach(function (index, offset) {
                const slotsLeft = auto.length - offset;
                const span = Math.max(1, Math.floor(remaining / slotsLeft));
                result[index] = span;
                remaining -= span;
            });
        }

        let total = result.reduce(function (sum, span) { return sum + span; }, 0);
        let cursor = 0;
        while (total < 12 && result.length) {
            result[cursor % result.length] += 1;
            total += 1;
            cursor += 1;
        }
        return result.map(function (span) { return Math.max(1, Math.min(12, span)); });
    }
    function displayName(row) {
        const nav = label(row);
        if (nav && nav !== AUTO_LABEL) { return nav; }
        const title = row && row.querySelector('.h18-page-section-title-summary');
        const text = String(title && title.textContent || '').trim();
        if (text) { return text; }
        const names = { grid: 'Række- og kolonne-kasse', flex: 'Flex', text: 'Tekst', image: 'Billede', text_image: 'Tekst + billede', container: 'Kasse' };
        return names[type(row)] || type(row) || 'Element';
    }
    function cleanClone(row) {
        const preview = row && row.querySelector(':scope > .h18-canvas-preview');
        if (!preview) { return null; }
        const clone = preview.cloneNode(true);
        clone.removeAttribute('id');
        clone.querySelectorAll('[id]').forEach(function (node) { node.removeAttribute('id'); });
        clone.querySelectorAll('[name]').forEach(function (node) { node.removeAttribute('name'); });
        clone.querySelectorAll('.' + PROXY_CLASS + ',.h18-ud-box-contents-preview,.h18-ud-auto-box-grid,.h18-v0810-side-zones,.h18-v0811-side-zones,.h18-v0814-auto-drop-zone,.h18-v0814-auto-kasse-drop,.h18-v0838-drop-overlay,.h18-v0838-drop-zone,.h18-v0841-resize-handle,.h18-v0841-resize-rail').forEach(function (node) { node.remove(); });
        clone.querySelectorAll('input,select,textarea,button').forEach(function (node) {
            node.disabled = true;
            node.setAttribute('tabindex', '-1');
        });
        clone.querySelectorAll('a').forEach(function (node) { node.setAttribute('tabindex', '-1'); });
        return clone;
    }
    function editButton(sectionKey, labelText) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'button button-small h18-v0811-edit-child';
        button.setAttribute('data-h18-v0811-edit-child', sectionKey);
        button.textContent = labelText || 'Rediger';
        return button;
    }
    function bar(row, runtimeBadge) {
        const node = document.createElement('div');
        node.className = 'h18-v0889-layout-bar';
        const strong = document.createElement('strong');
        strong.textContent = displayName(row);
        node.appendChild(strong);
        if (runtimeBadge) {
            const wrap = document.createElement('span');
            wrap.style.display = 'inline-flex';
            wrap.style.gap = '6px';
            wrap.style.alignItems = 'center';
            const badge = document.createElement('em');
            badge.className = 'h18-v0889-runtime-badge';
            badge.textContent = 'v0.8.89';
            wrap.appendChild(badge);
            wrap.appendChild(editButton(key(row), 'Rediger'));
            node.appendChild(wrap);
        } else {
            node.appendChild(editButton(key(row), 'Rediger'));
        }
        return node;
    }
    function stackGroups(children) {
        const keys = new Set(children.map(key));
        const rootFor = {};
        children.forEach(function (row) {
            const state = stackState(key(row));
            const root = String(state && state.StackRootKey || '').trim();
            rootFor[key(row)] = root && root !== key(row) && keys.has(root) ? root : '';
        });
        const roots = children.filter(function (row) { return !rootFor[key(row)]; });
        return roots.map(function (root) {
            const rootKey = key(root);
            const members = children.filter(function (candidate) { return rootFor[key(candidate)] === rootKey; });
            members.sort(function (a, b) {
                const sa = stackState(key(a));
                const sb = stackState(key(b));
                return int(sa.StackOrder, 0) - int(sb.StackOrder, 0);
            });
            return { root: root, members: members };
        });
    }
    function proxySignature(parent, children, groups) {
        const parts = [key(parent), type(parent), canvasDevice(), String(value(parent, 'LayoutDirection', 'Row')), String(value(parent, 'LayoutGapPx', 16))];
        groups.forEach(function (group) {
            const rootKey = key(group.root);
            parts.push(rootKey + ':' + effectiveSpan(rootKey));
            group.members.forEach(function (member) {
                const state = stackState(key(member));
                parts.push(key(member) + '>' + rootKey + ':' + int(state.StackOrder, 0));
            });
        });
        parts.push('children=' + children.map(key).join(','));
        return parts.join('|');
    }
    function renderParent(parent, allRows) {
        const parentKeyValue = key(parent);
        const preview = parent.querySelector(':scope > .h18-canvas-preview');
        if (!parentKeyValue || !preview) { return; }
        const children = childRows(allRows, parent);
        const previousChildren = allRows.filter(function (row) { return row.getAttribute(CHILD_ATTR) === parentKeyValue; });
        previousChildren.forEach(function (row) { if (children.indexOf(row) === -1) { row.removeAttribute(CHILD_ATTR); } });
        children.forEach(function (row) { row.setAttribute(CHILD_ATTR, parentKeyValue); });

        const groups = stackGroups(children);
        const signature = proxySignature(parent, children, groups);
        let wrapper = preview.querySelector(':scope > .' + PROXY_CLASS);
        if (wrapper && wrapper.getAttribute('data-h18-v0889-signature') === signature) { return; }
        if (wrapper) { wrapper.remove(); }

        wrapper = document.createElement('div');
        const direction = String(value(parent, 'LayoutDirection', 'Row') || 'Row').toLowerCase();
        const parentType = type(parent);
        wrapper.className = PROXY_CLASS + (parentType === 'grid' ? ' h18-v0889-saved-layout--grid' : (direction === 'column' ? ' h18-v0889-saved-layout--flex-column' : ' h18-v0889-saved-layout--flex-row'));
        wrapper.setAttribute('data-h18-v0889-parent', parentKeyValue);
        wrapper.setAttribute('data-h18-v0889-signature', signature);
        wrapper.style.setProperty('--h18-v0889-gap', Math.max(0, int(value(parent, canvasDevice() === 'mobile' ? 'MobileLayoutGapPx' : 'LayoutGapPx', 16), 16)) + 'px');

        if (!groups.length) {
            const empty = document.createElement('div');
            empty.className = 'h18-ud-box-empty-drop';
            empty.textContent = 'Kassen er tom.';
            empty.style.gridColumn = '1 / -1';
            wrapper.appendChild(empty);
            preview.appendChild(wrapper);
            return;
        }

        const spans = resolvedSpans(groups.map(function (group) { return key(group.root); }));
        groups.forEach(function (group, index) {
            const root = group.root;
            const rootKey = key(root);
            const tile = document.createElement('section');
            tile.className = 'h18-v0811-auto-box h18-v0889-layout-column';
            tile.setAttribute('data-h18-v0811-row', rootKey);
            tile.setAttribute('data-h18-v0840-auto-child', rootKey);
            tile.style.setProperty('--h18-v0889-span', String(spans[index] || 12));
            tile.appendChild(bar(root, index === 0));

            const body = document.createElement('div');
            body.className = 'h18-v0811-auto-box-preview h18-v0889-layout-body';
            const rootClone = cleanClone(root);
            if (rootClone) { body.appendChild(rootClone); }

            if (group.members.length) {
                const stack = document.createElement('div');
                stack.className = 'h18-v0889-stack';
                group.members.forEach(function (member) {
                    const memberKey = key(member);
                    const memberCard = document.createElement('section');
                    memberCard.className = 'h18-v0811-child-card h18-v0889-stack-member';
                    memberCard.setAttribute('data-h18-v0811-child', memberKey);
                    memberCard.appendChild(bar(member, false));
                    const memberPreview = document.createElement('div');
                    memberPreview.className = 'h18-v0811-child-preview h18-v0889-stack-member-preview';
                    const clone = cleanClone(member);
                    if (clone) { memberPreview.appendChild(clone); }
                    memberCard.appendChild(memberPreview);
                    stack.appendChild(memberCard);
                });
                body.appendChild(stack);
            }
            tile.appendChild(body);
            wrapper.appendChild(tile);
        });
        preview.appendChild(wrapper);
    }
    function render() {
        scheduled = 0;
        if (rendering) { return; }
        const root = host();
        if (!root) { return; }
        rendering = true;
        try {
            const allRows = rows();
            const genericKeys = new Set(allRows.filter(isGenericParent).map(key));
            allRows.forEach(function (row) {
                const parent = parentKey(row);
                if (!parent || !genericKeys.has(parent)) { row.removeAttribute(CHILD_ATTR); }
            });
            allRows.forEach(function (row) { if (isGenericParent(row)) { renderParent(row, allRows); } });
            document.documentElement.setAttribute('data-h18-saved-layout-rebuild', VERSION);
        } finally {
            rendering = false;
        }
    }
    function schedule() {
        if (scheduled) { return; }
        scheduled = window.requestAnimationFrame(render);
    }
    function install() {
        const root = host();
        if (!root) { window.setTimeout(install, 80); return; }
        if (window.MutationObserver) {
            const observer = new MutationObserver(function (mutations) {
                if (rendering) { return; }
                if (mutations.some(function (mutation) { return mutation.type === 'childList'; })) { schedule(); }
            });
            observer.observe(root, { childList: true, subtree: true });
            const canvas = document.querySelector('.h18-builder-canvas');
            if (canvas) {
                new MutationObserver(schedule).observe(canvas, { attributes: true, attributeFilter: ['data-canvas-device'] });
            }
        }
        document.addEventListener('change', schedule, false);
        document.addEventListener('input', schedule, false);
        document.addEventListener('click', function () { window.setTimeout(schedule, 0); }, false);
        [0, 60, 180, 500, 1200].forEach(function (delay) { window.setTimeout(schedule, delay); });
    }

    window.__h18SavedLayoutRebuildV0889 = { version: VERSION, refresh: render };
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
