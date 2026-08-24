(function () {
    'use strict';

    if (window.__h18LayoutEngineV0900) { return; }

    const VERSION = '0.9.0';
    const SCHEMA_VERSION = 1;
    const config = window.H18LayoutEngineV0900 || {};
    const HOST_ID = 'h18-page-sections-sortable';
    const FORM_ID = 'h18-page-editor-form';
    const READY_ATTR = 'data-h18-v0900-layout-ready';
    const CHILD_ATTR = 'data-h18-v0900-canonical-child';
    const MODEL_FIELD = 'h18_layout_model_v0900';
    const AUTO_LABEL = 'Auto-kasser';
    const COLUMN_COUNT = 12;
    const SAVE_SNAPSHOT_MAX_AGE = 15000;

    let model = null;
    let saveSnapshot = null;
    let frame = 0;
    let rendering = false;
    let resizeDrag = null;
    let lastTraceSignature = '';

    function host() { return document.getElementById(HOST_ID); }
    function form() { return document.getElementById(FORM_ID); }
    function sourceRows() {
        const root = host();
        if (!root) { return []; }
        return Array.from(root.children).filter(function (node) {
            return node && node.classList && node.classList.contains('h18-page-section-row') && node.hasAttribute('data-index');
        });
    }
    function inspector() { return document.getElementById('h18-page-inspector-target'); }
    function controls(row, selector) {
        const result = row ? Array.from(row.querySelectorAll(selector)) : [];
        if (row && row.classList.contains('is-selected')) {
            const panel = inspector();
            if (panel) {
                Array.from(panel.querySelectorAll(selector)).forEach(function (node) {
                    if (result.indexOf(node) === -1) { result.push(node); }
                });
            }
        }
        return result;
    }
    function firstValue(row, selector, fallback) {
        const nodes = controls(row, selector);
        if (!nodes.length) { return fallback; }
        const node = nodes[0];
        if (node.type === 'checkbox') { return Boolean(node.checked); }
        return node.value === undefined || node.value === null || String(node.value) === '' ? fallback : node.value;
    }
    function setValue(row, selector, value) {
        controls(row, selector).forEach(function (node) {
            if ('value' in node) { node.value = String(value); }
        });
    }
    function cleanKey(value) { return String(value == null ? '' : value).trim().toLowerCase().replace(/[^a-z0-9._-]/g, ''); }
    function rowKey(row) { return cleanKey(firstValue(row, '.h18-page-section-key,[name$="[Key]"]', row && row.getAttribute('data-key') || '')); }
    function rowType(row) { return String(row && row.getAttribute('data-section-type') || firstValue(row, '[name$="[Type]"]', 'text')).trim().toLowerCase(); }
    function parentKey(row) { return cleanKey(firstValue(row, '.h18-layout-parent-key,.h18-page-section-layout-parent,[name$="[LayoutParentKey]"]', '')); }
    function order(row, fallback) {
        const value = parseInt(firstValue(row, '.h18-page-section-order,[name$="[Order]"]', fallback), 10);
        return Number.isFinite(value) ? Math.max(1, Math.min(10000, value)) : fallback;
    }
    function removed(row) {
        const value = String(firstValue(row, '.h18-page-section-remove,[name$="[Remove]"]', '0'));
        return Boolean(row && row.classList.contains('h18-page-section-removed')) || value === '1';
    }
    function rowLabel(row) { return String(firstValue(row, '.h18-section-navigator-label,[name$="[NavigatorLabel]"]', '')).trim(); }
    function pageSlug() {
        const editorForm = form();
        const field = editorForm && editorForm.querySelector('[name="page_slug"]');
        return String(field && field.value || '').trim();
    }
    function canvasDevice() {
        const canvas = document.querySelector('.h18-builder-canvas');
        return String(canvas && canvas.getAttribute('data-canvas-device') || 'desktop').toLowerCase();
    }
    function deepClone(value) { return JSON.parse(JSON.stringify(value)); }
    function intValue(value, fallback) { const parsed = parseInt(value, 10); return Number.isFinite(parsed) ? parsed : fallback; }
    function clampSpan(value) { return Math.max(0, Math.min(COLUMN_COUNT, intValue(value, 0))); }
    function boolValue(value, fallback) {
        if (typeof value === 'boolean') { return value; }
        if (value === null || value === undefined || value === '') { return fallback; }
        if (typeof value === 'number') { return value !== 0; }
        return ['1', 'true', 'yes', 'on'].indexOf(String(value).toLowerCase().trim()) !== -1;
    }
    function responsiveSpan(raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        const inherit = Object.prototype.hasOwnProperty.call(raw, 'InheritDesktop') ? boolValue(raw.InheritDesktop, true) : true;
        const span = clampSpan(raw.Span);
        return {
            InheritDesktop: inherit,
            HasOverride: Object.prototype.hasOwnProperty.call(raw, 'HasOverride') ? boolValue(raw.HasOverride, !inherit) : (!inherit || span > 0),
            Span: span
        };
    }
    function normalizeSpan(raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        return {
            SchemaVersion: 2,
            Desktop: { Span: clampSpan(raw.Desktop && raw.Desktop.Span) },
            Tablet: responsiveSpan(raw.Tablet),
            Mobile: responsiveSpan(raw.Mobile)
        };
    }
    function clampPercent(value) {
        const parsed = intValue(value, 0);
        return parsed <= 0 ? 0 : Math.max(10, Math.min(90, parsed));
    }
    function normalizeStack(raw, key) {
        raw = raw && typeof raw === 'object' ? raw : {};
        let root = cleanKey(raw.StackRootKey || '');
        if (root === key) { root = ''; }
        return {
            SchemaVersion: 1,
            StackRootKey: root,
            StackOrder: Math.max(0, intValue(raw.StackOrder, 0)),
            DesktopPercent: clampPercent(raw.DesktopPercent),
            TabletPercent: clampPercent(raw.TabletPercent),
            MobilePercent: clampPercent(raw.MobilePercent)
        };
    }
    function storedSection(key) {
        const pages = config.pages && typeof config.pages === 'object' ? config.pages : {};
        const page = pages[pageSlug()] && typeof pages[pageSlug()] === 'object' ? pages[pageSlug()] : {};
        const sections = page.Sections && typeof page.Sections === 'object' ? page.Sections : {};
        return key && sections[key] && typeof sections[key] === 'object' ? sections[key] : {};
    }
    function spanForKey(key) {
        const api = window.__h18LegoResizeV0841;
        if (api && typeof api.stateForKey === 'function') {
            try {
                const state = api.stateForKey(key);
                if (state) { return normalizeSpan(state); }
            } catch (ignore) {}
        }
        return normalizeSpan(storedSection(key).Span || {});
    }
    function stackForKey(key) {
        const api = window.__h18LegoFixesV0851;
        if (api && typeof api.stackStateForKey === 'function') {
            try {
                const state = api.stackStateForKey(key);
                if (state) { return normalizeStack(state, key); }
            } catch (ignore) {}
        }
        return normalizeStack(storedSection(key).Stack || {}, key);
    }

    function validate(candidate) {
        candidate = candidate && typeof candidate === 'object' ? candidate : { sections: [] };
        const sections = Array.isArray(candidate.sections) ? candidate.sections : [];
        const byKey = {};
        sections.forEach(function (section) { if (section && section.key) { byKey[section.key] = section; } });
        const validParents = ['container', 'flex', 'grid'];

        sections.forEach(function (section) {
            const parent = cleanKey(section.parentKey || '');
            if (!parent || parent === section.key || !byKey[parent] || byKey[parent].removed || validParents.indexOf(byKey[parent].type) === -1) {
                section.parentKey = '';
            } else {
                section.parentKey = parent;
            }
        });
        sections.forEach(function (section) {
            const seen = {};
            let cursor = section.key;
            while (cursor && byKey[cursor]) {
                if (seen[cursor]) { byKey[cursor].parentKey = ''; break; }
                seen[cursor] = true;
                cursor = cleanKey(byKey[cursor].parentKey || '');
            }
        });
        sections.forEach(function (section) {
            section.span = normalizeSpan(section.span);
            section.stack = normalizeStack(section.stack, section.key);
            const root = section.stack.StackRootKey;
            if (!root || !byKey[root] || byKey[root].removed || byKey[root].parentKey !== section.parentKey) {
                section.stack.StackRootKey = '';
                section.stack.StackOrder = 0;
            }
        });
        return candidate;
    }

    function diagnosticShape(candidate, reason) {
        return {
            version: VERSION,
            schemaVersion: SCHEMA_VERSION,
            reason: String(reason || ''),
            pageSlug: candidate.pageSlug,
            sectionCount: candidate.sections.length,
            activeCount: candidate.sections.filter(function (section) { return !section.removed; }).length,
            sections: candidate.sections.map(function (section) {
                return {
                    key: section.key,
                    type: section.type,
                    parentKey: section.parentKey,
                    order: section.order,
                    removed: section.removed,
                    desktopSpan: section.span.Desktop.Span,
                    stackRootKey: section.stack.StackRootKey,
                    stackOrder: section.stack.StackOrder
                };
            })
        };
    }
    function trace(type, detail) {
        const api = window.__h18UltimateDesignerTraceV0876;
        if (api && typeof api.record === 'function') {
            try { api.record(type, document.body, detail || {}, { force: true }); } catch (ignore) {}
        }
    }
    function traceModel(type, candidate, reason, force) {
        const detail = diagnosticShape(candidate, reason);
        const signature = type + '|' + JSON.stringify(detail);
        if (!force && signature === lastTraceSignature) { return; }
        lastTraceSignature = signature;
        trace(type, detail);
        const live = window.__h18LiveDiagnosticsV0888;
        if (live && typeof live.flush === 'function') {
            window.setTimeout(function () { try { live.flush(); } catch (ignore) {} }, 20);
        }
    }

    function reconcile(reason) {
        const rows = sourceRows();
        const sections = rows.map(function (row, index) {
            const key = rowKey(row);
            return {
                key: key,
                type: rowType(row),
                parentKey: parentKey(row),
                order: order(row, (index + 1) * 10),
                removed: removed(row),
                span: spanForKey(key),
                stack: stackForKey(key)
            };
        }).filter(function (section) { return Boolean(section.key); });

        model = validate({
            schemaVersion: SCHEMA_VERSION,
            engineVersion: VERSION,
            pageSlug: pageSlug(),
            capturedAt: new Date().toISOString(),
            reason: String(reason || 'reconcile'),
            sections: sections
        });
        traceModel('DIAG_LAYOUT_MODEL_RECONCILE_V0900', model, reason, false);
        render();
        return model;
    }

    function rowMap() {
        const map = {};
        sourceRows().forEach(function (row) { const key = rowKey(row); if (key) { map[key] = row; } });
        return map;
    }
    function directPreview(row) {
        if (!row) { return null; }
        return Array.from(row.children).find(function (node) { return node.classList && node.classList.contains('h18-canvas-preview'); }) || null;
    }
    function isGenericParent(section, row) {
        if (!section || section.removed) { return false; }
        if (section.type === 'flex') { return true; }
        return section.type === 'grid' && rowLabel(row) !== AUTO_LABEL;
    }
    function effectiveSpan(section) {
        if (!section) { return 0; }
        const desktop = clampSpan(section.span && section.span.Desktop && section.span.Desktop.Span);
        const device = canvasDevice();
        if (device === 'desktop') { return desktop; }
        const branch = section.span && section.span[device === 'mobile' ? 'Mobile' : 'Tablet'] || {};
        return boolValue(branch.InheritDesktop, true) ? desktop : clampSpan(branch.Span);
    }
    function equalSpans(count) {
        if (count <= 0) { return []; }
        const base = Math.floor(COLUMN_COUNT / count);
        let remainder = COLUMN_COUNT - (base * count);
        return new Array(count).fill(0).map(function () {
            const value = Math.max(1, base + (remainder > 0 ? 1 : 0));
            if (remainder > 0) { remainder -= 1; }
            return value;
        });
    }
    function resolvedSpans(groups) {
        const spans = groups.map(function (group) { return effectiveSpan(group.root); });
        if (spans.every(function (span) { return span <= 0; })) { return equalSpans(groups.length); }
        const result = spans.slice();
        const auto = [];
        let used = 0;
        result.forEach(function (span, index) { if (span > 0) { used += span; } else { auto.push(index); } });
        while (used + auto.length > COLUMN_COUNT) {
            let best = -1;
            result.forEach(function (span, index) { if (span > 1 && (best < 0 || span > result[best])) { best = index; } });
            if (best < 0) { break; }
            result[best] -= 1; used -= 1;
        }
        if (auto.length) {
            let remaining = Math.max(auto.length, COLUMN_COUNT - used);
            auto.forEach(function (index, offset) {
                const slots = auto.length - offset;
                result[index] = Math.max(1, Math.floor(remaining / slots));
                remaining -= result[index];
            });
        }
        return result.map(function (span) { return Math.max(1, Math.min(COLUMN_COUNT, span || 1)); });
    }
    function groupsFor(children, byKey) {
        const childKeys = {};
        children.forEach(function (section) { childKeys[section.key] = true; });
        const roots = children.filter(function (section) {
            const root = section.stack && section.stack.StackRootKey || '';
            return !root || !childKeys[root];
        });
        return roots.map(function (root) {
            const members = children.filter(function (section) { return section.stack && section.stack.StackRootKey === root.key; });
            members.sort(function (a, b) { return intValue(a.stack.StackOrder, 0) - intValue(b.stack.StackOrder, 0); });
            return { root: root, members: members, byKey: byKey };
        });
    }
    function cleanClone(row) {
        const preview = directPreview(row);
        if (!preview) { return null; }
        const clone = preview.cloneNode(true);
        clone.removeAttribute('id');
        clone.querySelectorAll('[id]').forEach(function (node) { node.removeAttribute('id'); });
        clone.querySelectorAll('[name]').forEach(function (node) { node.removeAttribute('name'); });
        clone.querySelectorAll('.h18-v0900-layout,.h18-v0890-saved-layout,.h18-v0889-saved-layout,.h18-ud-box-contents-preview,.h18-ud-auto-box-grid,.h18-v0838-drop-overlay,.h18-v0838-drop-zone,.h18-v0841-resize-handle,.h18-v0841-resize-rail').forEach(function (node) { node.remove(); });
        clone.querySelectorAll('input,select,textarea,button').forEach(function (node) { node.disabled = true; node.setAttribute('tabindex', '-1'); });
        clone.querySelectorAll('a').forEach(function (node) { node.setAttribute('tabindex', '-1'); });
        return clone;
    }
    function displayName(section, row) {
        const label = rowLabel(row);
        if (label && label !== AUTO_LABEL) { return label; }
        const summary = row && row.querySelector('.h18-page-section-title-summary');
        const text = String(summary && summary.textContent || '').trim();
        if (text) { return text; }
        const names = { grid: 'Række- og kolonne-kasse', flex: 'Flex', text: 'Tekst', image: 'Billede', text_image: 'Tekst + billede', container: 'Kasse', buttons: 'Knapper' };
        return names[section.type] || section.type || 'Element';
    }
    function bar(section, row, span) {
        const node = document.createElement('div');
        node.className = 'h18-v0900-layout-bar';
        const title = document.createElement('strong');
        title.textContent = displayName(section, row);
        node.appendChild(title);
        const actions = document.createElement('span');
        actions.className = 'h18-v0900-layout-actions';
        if (span > 0) {
            const badge = document.createElement('em');
            badge.className = 'h18-v0900-span-badge';
            badge.textContent = span + '/' + COLUMN_COUNT;
            actions.appendChild(badge);
        }
        const edit = document.createElement('button');
        edit.type = 'button';
        edit.className = 'button button-small h18-v0811-edit-child';
        edit.setAttribute('data-h18-v0811-edit-child', section.key);
        edit.textContent = 'Rediger';
        actions.appendChild(edit);
        node.appendChild(actions);
        return node;
    }
    function resizeHandle(leftKey, rightKey) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'h18-v0900-resize-handle';
        button.setAttribute('data-h18-v0900-left', leftKey);
        button.setAttribute('data-h18-v0900-right', rightKey);
        button.setAttribute('aria-label', 'Juster kolonnebredde');
        button.title = 'Træk for at justere kolonnebredde';
        button.textContent = '↔';
        return button;
    }

    function render() {
        if (rendering || !model) { return; }
        const root = host();
        if (!root) { return; }
        rendering = true;
        try {
            const rows = rowMap();
            const byKey = {};
            model.sections.forEach(function (section) { byKey[section.key] = section; });
            sourceRows().forEach(function (row) { row.removeAttribute(CHILD_ATTR); });
            root.removeAttribute(READY_ATTR);
            root.querySelectorAll('.h18-v0900-layout').forEach(function (node) { node.remove(); });
            let proxies = 0;

            model.sections.forEach(function (parent) {
                const parentRow = rows[parent.key];
                if (!isGenericParent(parent, parentRow)) { return; }
                const preview = directPreview(parentRow);
                if (!preview) { return; }
                const children = model.sections.filter(function (section) { return !section.removed && section.parentKey === parent.key; });
                if (!children.length) { return; }
                const groups = groupsFor(children, byKey);
                const spans = resolvedSpans(groups);
                const wrapper = document.createElement('div');
                const direction = String(firstValue(parentRow, '[name$="[LayoutDirection]"]', 'Row')).toLowerCase();
                wrapper.className = 'h18-v0900-layout ' + (parent.type === 'grid' ? 'h18-v0900-layout--grid' : (direction === 'column' ? 'h18-v0900-layout--flex-column' : 'h18-v0900-layout--flex-row'));
                wrapper.setAttribute('data-h18-v0900-parent', parent.key);
                wrapper.style.setProperty('--h18-v0900-gap', Math.max(0, intValue(firstValue(parentRow, '[name$="[LayoutGapPx]"]', 16), 16)) + 'px');

                groups.forEach(function (group, index) {
                    const section = group.root;
                    const row = rows[section.key];
                    if (!row) { return; }
                    const span = spans[index] || COLUMN_COUNT;
                    const tile = document.createElement('section');
                    tile.className = 'h18-v0811-auto-box h18-v0900-layout-column';
                    tile.setAttribute('data-h18-v0811-row', section.key);
                    tile.setAttribute('data-h18-v0840-auto-child', section.key);
                    tile.setAttribute('data-h18-v0900-span', String(span));
                    tile.style.setProperty('--h18-v0900-span', String(span));
                    tile.appendChild(bar(section, row, span));

                    const body = document.createElement('div');
                    body.className = 'h18-v0811-auto-box-preview h18-v0900-layout-body';
                    const clone = cleanClone(row);
                    if (clone) { body.appendChild(clone); }

                    if (group.members.length) {
                        const stack = document.createElement('div');
                        stack.className = 'h18-v0900-stack';
                        group.members.forEach(function (member) {
                            const memberRow = rows[member.key];
                            if (!memberRow) { return; }
                            const card = document.createElement('section');
                            card.className = 'h18-v0811-child-card h18-v0900-stack-member';
                            card.setAttribute('data-h18-v0811-child', member.key);
                            card.appendChild(bar(member, memberRow, 0));
                            const memberPreview = document.createElement('div');
                            memberPreview.className = 'h18-v0811-child-preview h18-v0900-stack-member-preview';
                            const memberClone = cleanClone(memberRow);
                            if (memberClone) { memberPreview.appendChild(memberClone); }
                            card.appendChild(memberPreview);
                            stack.appendChild(card);
                        });
                        body.appendChild(stack);
                    }
                    tile.appendChild(body);
                    if (canvasDevice() === 'desktop' && index < groups.length - 1) {
                        tile.appendChild(resizeHandle(section.key, groups[index + 1].root.key));
                    }
                    wrapper.appendChild(tile);
                });

                preview.appendChild(wrapper);
                if (wrapper.isConnected) {
                    proxies += 1;
                    children.forEach(function (section) { if (rows[section.key]) { rows[section.key].setAttribute(CHILD_ATTR, parent.key); } });
                }
            });
            if (proxies > 0) { root.setAttribute(READY_ATTR, '1'); }
            document.documentElement.setAttribute('data-h18-layout-engine', VERSION);
        } finally {
            rendering = false;
        }
    }

    function schedule(reason) {
        if (frame || resizeDrag) { return; }
        frame = window.requestAnimationFrame(function () {
            frame = 0;
            reconcile(reason || 'scheduled');
        });
    }

    function captureSave(reason) {
        const current = reconcile(reason || 'save-intent');
        saveSnapshot = { time: Date.now(), model: deepClone(current) };
        traceModel('DIAG_LAYOUT_MODEL_SAVE_INTENT_V0900', saveSnapshot.model, reason, true);
    }
    function sameKeys(candidate) {
        const left = candidate.sections.map(function (section) { return section.key; }).sort();
        const right = sourceRows().map(rowKey).filter(Boolean).sort();
        return JSON.stringify(left) === JSON.stringify(right);
    }
    function projectToRows(candidate) {
        const rows = rowMap();
        candidate.sections.forEach(function (section) {
            const row = rows[section.key];
            if (!row) { return; }
            row.classList.toggle('h18-page-section-removed', Boolean(section.removed));
            setValue(row, '.h18-page-section-remove,[name$="[Remove]"]', section.removed ? '1' : '0');
            setValue(row, '.h18-layout-parent-key,.h18-page-section-layout-parent,[name$="[LayoutParentKey]"]', section.parentKey || '');
            setValue(row, '.h18-page-section-order,[name$="[Order]"]', section.order);
        });
    }
    function writeModelField(candidate) {
        const editorForm = form();
        if (!editorForm) { return; }
        let field = editorForm.querySelector('input[name="' + MODEL_FIELD + '"]');
        if (!field) {
            field = document.createElement('input');
            field.type = 'hidden';
            field.name = MODEL_FIELD;
            editorForm.appendChild(field);
        }
        field.value = JSON.stringify(candidate);
    }
    function prepareSubmit() {
        let candidate = null;
        if (saveSnapshot && Date.now() - saveSnapshot.time <= SAVE_SNAPSHOT_MAX_AGE && sameKeys(saveSnapshot.model)) {
            candidate = deepClone(saveSnapshot.model);
        } else if (model && sameKeys(model)) {
            candidate = deepClone(model);
        } else {
            candidate = deepClone(reconcile('submit-fallback'));
        }
        candidate.reason = 'submit-canonical';
        candidate.capturedAt = new Date().toISOString();
        validate(candidate);
        projectToRows(candidate);
        writeModelField(candidate);
        model = deepClone(candidate);
        traceModel('DIAG_LAYOUT_MODEL_SAVE_V0900', candidate, 'submit', true);
    }

    function submitControl(node) {
        const editorForm = form();
        if (!editorForm || !node || !node.closest) { return null; }
        const button = node.closest('button[type="submit"],input[type="submit"],button:not([type])');
        return button && editorForm.contains(button) ? button : null;
    }

    function startResize(event) {
        if (canvasDevice() !== 'desktop' || event.button !== 0) { return; }
        const handle = event.target && event.target.closest ? event.target.closest('.h18-v0900-resize-handle') : null;
        if (!handle) { return; }
        const leftKey = cleanKey(handle.getAttribute('data-h18-v0900-left'));
        const rightKey = cleanKey(handle.getAttribute('data-h18-v0900-right'));
        const left = model && model.sections.find(function (section) { return section.key === leftKey; });
        const right = model && model.sections.find(function (section) { return section.key === rightKey; });
        const wrapper = handle.closest('.h18-v0900-layout');
        const tile = handle.closest('.h18-v0900-layout-column');
        if (!left || !right || !wrapper || !tile) { return; }
        event.preventDefault(); event.stopPropagation();
        const leftSpan = Math.max(1, intValue(tile.getAttribute('data-h18-v0900-span'), effectiveSpan(left) || 1));
        const rightTile = Array.from(wrapper.children).find(function (node) { return node.getAttribute && node.getAttribute('data-h18-v0840-auto-child') === rightKey; });
        const rightSpan = Math.max(1, intValue(rightTile && rightTile.getAttribute('data-h18-v0900-span'), effectiveSpan(right) || 1));
        const rect = wrapper.getBoundingClientRect();
        const gap = parseFloat(window.getComputedStyle(wrapper).columnGap || window.getComputedStyle(wrapper).gap || '0') || 0;
        resizeDrag = {
            pointerId: event.pointerId,
            startX: event.clientX,
            step: Math.max(1, (rect.width + gap) / COLUMN_COUNT),
            leftKey: leftKey,
            rightKey: rightKey,
            leftSpan: leftSpan,
            rightSpan: rightSpan,
            currentLeft: leftSpan,
            currentRight: rightSpan,
            total: leftSpan + rightSpan
        };
        handle.classList.add('is-active');
        if (handle.setPointerCapture) { try { handle.setPointerCapture(event.pointerId); } catch (ignore) {} }
    }
    function moveResize(event) {
        if (!resizeDrag || event.pointerId !== resizeDrag.pointerId) { return; }
        event.preventDefault();
        const delta = Math.round((event.clientX - resizeDrag.startX) / resizeDrag.step);
        resizeDrag.currentLeft = Math.max(1, Math.min(resizeDrag.total - 1, resizeDrag.leftSpan + delta));
        resizeDrag.currentRight = resizeDrag.total - resizeDrag.currentLeft;
        const leftTile = document.querySelector('.h18-v0900-layout-column[data-h18-v0840-auto-child="' + CSS.escape(resizeDrag.leftKey) + '"]');
        const rightTile = document.querySelector('.h18-v0900-layout-column[data-h18-v0840-auto-child="' + CSS.escape(resizeDrag.rightKey) + '"]');
        if (leftTile) { leftTile.style.setProperty('--h18-v0900-span', String(resizeDrag.currentLeft)); leftTile.setAttribute('data-h18-v0900-span', String(resizeDrag.currentLeft)); }
        if (rightTile) { rightTile.style.setProperty('--h18-v0900-span', String(resizeDrag.currentRight)); rightTile.setAttribute('data-h18-v0900-span', String(resizeDrag.currentRight)); }
    }
    function finishResize(event, commit) {
        if (!resizeDrag || (event && event.pointerId !== resizeDrag.pointerId)) { return; }
        const drag = resizeDrag; resizeDrag = null;
        document.querySelectorAll('.h18-v0900-resize-handle.is-active').forEach(function (node) { node.classList.remove('is-active'); });
        if (commit !== false && (drag.currentLeft !== drag.leftSpan || drag.currentRight !== drag.rightSpan)) {
            const api = window.__h18LegoResizeV0841;
            if (api && typeof api.stateForKey === 'function' && typeof api.writeStateForKey === 'function') {
                [drag.leftKey, drag.rightKey].forEach(function (key, index) {
                    try {
                        const state = normalizeSpan(api.stateForKey(key) || {});
                        state.Desktop.Span = index === 0 ? drag.currentLeft : drag.currentRight;
                        api.writeStateForKey(key, state, true);
                    } catch (ignore) {}
                });
            }
        }
        schedule('resize-finish');
    }

    function install() {
        const root = host();
        const editorForm = form();
        if (!root || !editorForm) { window.setTimeout(install, 80); return; }

        window.addEventListener('pointerdown', function (event) {
            if (submitControl(event.target)) { captureSave('submit-pointerdown'); return; }
            startResize(event);
        }, true);
        window.addEventListener('pointermove', moveResize, true);
        window.addEventListener('pointerup', function (event) { finishResize(event, true); }, true);
        window.addEventListener('pointercancel', function (event) { finishResize(event, false); }, true);
        window.addEventListener('keydown', function (event) {
            if (!submitControl(event.target)) { return; }
            if (event.key === 'Enter' || event.key === ' ') { captureSave('submit-keydown'); }
        }, true);
        window.addEventListener('submit', function (event) {
            if (event.target === editorForm) { prepareSubmit(); }
        }, true);

        document.addEventListener('input', function () { schedule('input'); }, false);
        document.addEventListener('change', function () { schedule('change'); }, false);
        document.addEventListener('drop', function () { window.setTimeout(function () { schedule('drop'); }, 0); }, false);
        document.addEventListener('dragend', function () { window.setTimeout(function () { schedule('dragend'); }, 0); }, false);
        document.addEventListener('click', function () { window.setTimeout(function () { schedule('click'); }, 0); }, false);

        if (window.MutationObserver) {
            const observer = new MutationObserver(function (mutations) {
                const relevant = mutations.some(function (mutation) {
                    if (mutation.type === 'attributes') { return mutation.target.classList && mutation.target.classList.contains('h18-page-section-row'); }
                    if (mutation.target === root) { return true; }
                    return Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || [])).some(function (node) {
                        return node && node.classList && node.classList.contains('h18-page-section-row');
                    });
                });
                if (relevant) { schedule('source-mutation'); }
            });
            observer.observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
            const canvas = document.querySelector('.h18-builder-canvas');
            if (canvas) { new MutationObserver(function () { schedule('device'); }).observe(canvas, { attributes: true, attributeFilter: ['data-canvas-device'] }); }
        }

        reconcile('boot');
        traceModel('DIAG_LAYOUT_ENGINE_BOOT_V0900', model, 'boot', true);
        [100, 350, 900].forEach(function (delay) { window.setTimeout(function () { schedule('hydrate-' + delay); }, delay); });
    }

    window.__h18LayoutEngineV0900 = {
        version: VERSION,
        schemaVersion: SCHEMA_VERSION,
        snapshot: function () { return model ? deepClone(model) : null; },
        reconcile: reconcile,
        render: render,
        validate: function () { return model ? validate(deepClone(model)) : null; },
        prepareSubmit: prepareSubmit,
        stateForKey: function (key) {
            key = cleanKey(key);
            const section = model && model.sections.find(function (item) { return item.key === key; });
            return section ? deepClone(section) : null;
        }
    };

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
