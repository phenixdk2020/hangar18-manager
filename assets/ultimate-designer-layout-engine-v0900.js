(function () {
    'use strict';

    if (window.__h18LayoutEngineV0900) { return; }

    const VERSION = '0.9.0';
    const SCHEMA_VERSION = 1;
    const config = window.H18LayoutEngineV0900 || {};
    const HOST_ID = 'h18-page-sections-sortable';
    const FORM_ID = 'h18-page-editor-form';
    const MODEL_FIELD = 'h18_layout_model_v0900';
    const READY_ATTR = 'data-h18-v0900-layout-ready';
    const CHILD_ATTR = 'data-h18-v0900-canonical-child';
    const AUTO_LABEL = 'Auto-kasser';
    const COLUMNS = 12;
    const SNAPSHOT_AGE_MS = 15000;

    let currentModel = null;
    let saveSnapshot = null;
    let scheduledFrame = 0;
    let rendering = false;
    let resizeDrag = null;
    let lastTraceSignature = '';

    function host() { return document.getElementById(HOST_ID); }
    function form() { return document.getElementById(FORM_ID); }
    function inspector() { return document.getElementById('h18-page-inspector-target'); }

    // Canonical editor rows are direct children. Never derive state from visual proxies.
    function sourceRows() {
        const root = host();
        if (!root) { return []; }
        return Array.from(root.children).filter(function (node) {
            return Boolean(node && node.classList && node.classList.contains('h18-page-section-row'));
        });
    }

    function controls(row, selector) {
        const result = row ? Array.from(row.querySelectorAll(selector)) : [];
        if (row && row.classList.contains('is-selected')) {
            const target = inspector();
            if (target) {
                Array.from(target.querySelectorAll(selector)).forEach(function (node) {
                    if (result.indexOf(node) === -1) { result.push(node); }
                });
            }
        }
        return result;
    }

    function value(row, selector, fallback) {
        const nodes = controls(row, selector);
        if (!nodes.length) { return fallback; }
        const node = nodes[0];
        if (node.type === 'checkbox') { return Boolean(node.checked); }
        const result = node.value;
        return result === undefined || result === null || String(result) === '' ? fallback : result;
    }

    function setValue(row, selector, next) {
        controls(row, selector).forEach(function (node) {
            if ('value' in node) { node.value = String(next); }
        });
    }

    function cleanKey(raw) {
        return String(raw == null ? '' : raw).trim().toLowerCase().replace(/[^a-z0-9._-]/g, '');
    }
    function rowKey(row) { return cleanKey(value(row, '.h18-page-section-key,[name$="[Key]"]', row && row.getAttribute('data-key') || '')); }
    function rowType(row) { return String(row && row.getAttribute('data-section-type') || value(row, '[name$="[Type]"]', 'text')).trim().toLowerCase(); }
    function parentKey(row) { return cleanKey(value(row, '.h18-layout-parent-key,[name$="[LayoutParentKey]"]', '')); }
    function rowLabel(row) { return String(value(row, '.h18-section-navigator-label,[name$="[NavigatorLabel]"]', '')).trim(); }
    function rowOrder(row, fallback) {
        const parsed = parseInt(value(row, '.h18-page-section-order,[name$="[Order]"]', fallback), 10);
        return Number.isFinite(parsed) ? Math.max(1, Math.min(10000, parsed)) : fallback;
    }
    function rowRemoved(row) {
        const raw = String(value(row, '.h18-page-section-remove,[name$="[Remove]"]', '0'));
        return Boolean(row && row.classList.contains('h18-page-section-removed')) || raw === '1';
    }
    function pageSlug() {
        const editorForm = form();
        const field = editorForm && editorForm.querySelector('[name="page_slug"]');
        return String(field && field.value || '').trim();
    }
    function canvasDevice() {
        const canvas = document.querySelector('.h18-builder-canvas');
        return String(canvas && canvas.getAttribute('data-canvas-device') || 'desktop').toLowerCase();
    }
    function clone(valueToClone) { return JSON.parse(JSON.stringify(valueToClone)); }
    function intValue(raw, fallback) { const parsed = parseInt(raw, 10); return Number.isFinite(parsed) ? parsed : fallback; }
    function clampSpan(raw) { return Math.max(0, Math.min(COLUMNS, intValue(raw, 0))); }
    function boolValue(raw, fallback) {
        if (typeof raw === 'boolean') { return raw; }
        if (raw === null || raw === undefined || raw === '') { return fallback; }
        if (typeof raw === 'number') { return raw !== 0; }
        return ['1', 'true', 'yes', 'on'].indexOf(String(raw).toLowerCase().trim()) !== -1;
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
    function percent(raw) {
        const parsed = intValue(raw, 0);
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
            DesktopPercent: percent(raw.DesktopPercent),
            TabletPercent: percent(raw.TabletPercent),
            MobilePercent: percent(raw.MobilePercent)
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
            try { const state = api.stateForKey(key); if (state) { return normalizeSpan(state); } } catch (ignore) {}
        }
        return normalizeSpan(storedSection(key).Span || {});
    }
    function stackForKey(key) {
        const api = window.__h18LegoFixesV0851;
        if (api && typeof api.stackStateForKey === 'function') {
            try { const state = api.stackStateForKey(key); if (state) { return normalizeStack(state, key); } } catch (ignore) {}
        }
        return normalizeStack(storedSection(key).Stack || {}, key);
    }

    function validate(candidate) {
        const sections = candidate && Array.isArray(candidate.sections) ? candidate.sections : [];
        const byKey = {};
        sections.forEach(function (section) { if (section && section.key) { byKey[section.key] = section; } });
        const parentTypes = ['container', 'flex', 'grid'];

        sections.forEach(function (section) {
            const parent = cleanKey(section.parentKey || '');
            if (!parent || parent === section.key || !byKey[parent] || byKey[parent].removed || parentTypes.indexOf(byKey[parent].type) === -1) { section.parentKey = ''; }
            else { section.parentKey = parent; }
            section.span = normalizeSpan(section.span);
            section.stack = normalizeStack(section.stack, section.key);
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
            const root = section.stack.StackRootKey;
            const parent = byKey[section.parentKey];
            if (!root || !byKey[root] || byKey[root].removed || byKey[root].parentKey !== section.parentKey || !parent || parent.type !== 'grid') {
                section.stack.StackRootKey = '';
                section.stack.StackOrder = 0;
            }
        });
        return candidate;
    }

    function diagnostics(candidate, reason) {
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
    function trace(type, candidate, reason, force) {
        if (!candidate) { return; }
        const detail = diagnostics(candidate, reason);
        const signature = type + '|' + JSON.stringify(detail);
        if (!force && signature === lastTraceSignature) { return; }
        lastTraceSignature = signature;
        const api = window.__h18UltimateDesignerTraceV0876;
        if (api && typeof api.record === 'function') {
            try { api.record(type, document.body, detail, { force: true }); } catch (ignore) {}
        }
        const live = window.__h18LiveDiagnosticsV0888;
        if (live && typeof live.flush === 'function') { window.setTimeout(function () { try { live.flush(); } catch (ignore) {} }, 20); }
    }

    function reconcile(reason) {
        const sections = sourceRows().map(function (row, index) {
            const key = rowKey(row);
            return {
                key: key,
                type: rowType(row),
                parentKey: parentKey(row),
                order: rowOrder(row, (index + 1) * 10),
                removed: rowRemoved(row),
                span: spanForKey(key),
                stack: stackForKey(key)
            };
        }).filter(function (section) { return Boolean(section.key); });

        currentModel = validate({
            schemaVersion: SCHEMA_VERSION,
            engineVersion: VERSION,
            pageSlug: pageSlug(),
            capturedAt: new Date().toISOString(),
            reason: String(reason || 'reconcile'),
            sections: sections
        });
        trace('DIAG_LAYOUT_MODEL_RECONCILE_V0900', currentModel, reason, false);
        render();
        return currentModel;
    }

    function rowMap() {
        const map = {};
        sourceRows().forEach(function (row) { const key = rowKey(row); if (key) { map[key] = row; } });
        return map;
    }
    function directPreview(row) {
        return row ? Array.from(row.children).find(function (node) { return node.classList && node.classList.contains('h18-canvas-preview'); }) || null : null;
    }
    function genericParent(section, row) {
        if (!section || section.removed) { return false; }
        if (section.type === 'flex') { return true; }
        return section.type === 'grid' && rowLabel(row) !== AUTO_LABEL;
    }
    function effectiveSpan(section) {
        const desktop = clampSpan(section && section.span && section.span.Desktop && section.span.Desktop.Span);
        const device = canvasDevice();
        if (device === 'desktop') { return desktop; }
        const branch = section && section.span && section.span[device === 'mobile' ? 'Mobile' : 'Tablet'] || {};
        return boolValue(branch.InheritDesktop, true) ? desktop : clampSpan(branch.Span);
    }
    function equalSpans(count) {
        if (!count) { return []; }
        const base = Math.floor(COLUMNS / count);
        let remainder = COLUMNS - (base * count);
        return new Array(count).fill(0).map(function () {
            const span = Math.max(1, base + (remainder > 0 ? 1 : 0));
            if (remainder > 0) { remainder--; }
            return span;
        });
    }
    function resolvedSpans(groups) {
        const result = groups.map(function (group) { return effectiveSpan(group.root); });
        if (result.every(function (span) { return span <= 0; })) { return equalSpans(groups.length); }
        const auto = [];
        let used = 0;
        result.forEach(function (span, index) { if (span > 0) { used += span; } else { auto.push(index); } });
        while (used + auto.length > COLUMNS) {
            let best = -1;
            result.forEach(function (span, index) { if (span > 1 && (best < 0 || span > result[best])) { best = index; } });
            if (best < 0) { break; }
            result[best]--; used--;
        }
        if (auto.length) {
            let remaining = Math.max(auto.length, COLUMNS - used);
            auto.forEach(function (index, offset) {
                const slots = auto.length - offset;
                result[index] = Math.max(1, Math.floor(remaining / slots));
                remaining -= result[index];
            });
        }
        return result.map(function (span) { return Math.max(1, Math.min(COLUMNS, span || 1)); });
    }
    function stackGroups(children) {
        const childKeys = {};
        children.forEach(function (section) { childKeys[section.key] = true; });
        return children.filter(function (section) {
            const root = section.stack.StackRootKey;
            return !root || !childKeys[root];
        }).map(function (root) {
            const members = children.filter(function (section) { return section.stack.StackRootKey === root.key; });
            members.sort(function (a, b) { return intValue(a.stack.StackOrder, 0) - intValue(b.stack.StackOrder, 0); });
            return { root: root, members: members };
        });
    }
    function cleanPreviewClone(row) {
        const preview = directPreview(row);
        if (!preview) { return null; }
        const copy = preview.cloneNode(true);
        copy.removeAttribute('id');
        copy.querySelectorAll('[id]').forEach(function (node) { node.removeAttribute('id'); });
        copy.querySelectorAll('[name]').forEach(function (node) { node.removeAttribute('name'); });
        copy.querySelectorAll('.h18-v0900-layout,.h18-v0890-saved-layout,.h18-v0889-saved-layout,.h18-ud-box-contents-preview,.h18-ud-auto-box-grid,.h18-v0838-drop-overlay,.h18-v0838-drop-zone,.h18-v0841-resize-handle,.h18-v0841-resize-rail').forEach(function (node) { node.remove(); });
        copy.querySelectorAll('input,select,textarea,button').forEach(function (node) { node.disabled = true; node.setAttribute('tabindex', '-1'); });
        copy.querySelectorAll('a').forEach(function (node) { node.setAttribute('tabindex', '-1'); });
        return copy;
    }
    function displayName(section, row) {
        const label = rowLabel(row);
        if (label && label !== AUTO_LABEL) { return label; }
        const summary = row && row.querySelector('.h18-page-section-title-summary');
        const title = String(summary && summary.textContent || '').trim();
        if (title) { return title; }
        const names = { grid: 'Række- og kolonne-kasse', flex: 'Flex', text: 'Tekst', image: 'Billede', text_image: 'Tekst + billede', container: 'Kasse', buttons: 'Knapper' };
        return names[section.type] || section.type || 'Element';
    }
    function layoutBar(section, row, span) {
        const bar = document.createElement('div');
        bar.className = 'h18-v0900-layout-bar';
        const title = document.createElement('strong');
        title.textContent = displayName(section, row);
        bar.appendChild(title);
        const actions = document.createElement('span');
        actions.className = 'h18-v0900-layout-actions';
        if (span > 0) {
            const badge = document.createElement('em');
            badge.className = 'h18-v0900-span-badge';
            badge.textContent = span + '/' + COLUMNS;
            actions.appendChild(badge);
        }
        const edit = document.createElement('button');
        edit.type = 'button';
        edit.className = 'button button-small h18-v0811-edit-child';
        edit.setAttribute('data-h18-v0811-edit-child', section.key);
        edit.textContent = 'Rediger';
        actions.appendChild(edit);
        bar.appendChild(actions);
        return bar;
    }
    function resizeHandle(leftKey, rightKey) {
        const handle = document.createElement('button');
        handle.type = 'button';
        handle.className = 'h18-v0900-resize-handle';
        handle.setAttribute('data-h18-v0900-left', leftKey);
        handle.setAttribute('data-h18-v0900-right', rightKey);
        handle.setAttribute('aria-label', 'Juster kolonnebredde');
        handle.title = 'Træk for at justere kolonnebredde';
        handle.textContent = '↔';
        return handle;
    }

    function render() {
        if (rendering || !currentModel) { return; }
        const root = host();
        if (!root) { return; }
        rendering = true;
        try {
            const rows = rowMap();
            sourceRows().forEach(function (row) { row.removeAttribute(CHILD_ATTR); });
            root.removeAttribute(READY_ATTR);
            root.querySelectorAll('.h18-v0900-layout').forEach(function (node) { node.remove(); });
            let proxyCount = 0;

            currentModel.sections.forEach(function (parent) {
                const parentRow = rows[parent.key];
                if (!genericParent(parent, parentRow)) { return; }
                const preview = directPreview(parentRow);
                if (!preview) { return; }
                const children = currentModel.sections.filter(function (section) { return !section.removed && section.parentKey === parent.key; });
                if (!children.length) { return; }
                const groups = stackGroups(children);
                const spans = resolvedSpans(groups);
                const wrapper = document.createElement('div');
                const direction = String(value(parentRow, '[name$="[LayoutDirection]"]', 'Row')).toLowerCase();
                wrapper.className = 'h18-v0900-layout ' + (parent.type === 'grid' ? 'h18-v0900-layout--grid' : (direction === 'column' ? 'h18-v0900-layout--flex-column' : 'h18-v0900-layout--flex-row'));
                wrapper.setAttribute('data-h18-v0900-parent', parent.key);
                wrapper.style.setProperty('--h18-v0900-gap', Math.max(0, intValue(value(parentRow, '[name$="[LayoutGapPx]"]', 16), 16)) + 'px');

                groups.forEach(function (group, index) {
                    const section = group.root;
                    const row = rows[section.key];
                    if (!row) { return; }
                    const span = spans[index] || COLUMNS;
                    const tile = document.createElement('section');
                    tile.className = 'h18-v0811-auto-box h18-v0900-layout-column';
                    tile.setAttribute('data-h18-v0811-row', section.key);
                    tile.setAttribute('data-h18-v0840-auto-child', section.key);
                    tile.setAttribute('data-h18-v0900-span', String(span));
                    tile.style.setProperty('--h18-v0900-span', String(span));
                    tile.appendChild(layoutBar(section, row, span));

                    const body = document.createElement('div');
                    body.className = 'h18-v0811-auto-box-preview h18-v0900-layout-body';
                    const rootCopy = cleanPreviewClone(row);
                    if (rootCopy) { body.appendChild(rootCopy); }
                    if (group.members.length) {
                        const stack = document.createElement('div');
                        stack.className = 'h18-v0900-stack';
                        group.members.forEach(function (member) {
                            const memberRow = rows[member.key];
                            if (!memberRow) { return; }
                            const card = document.createElement('section');
                            card.className = 'h18-v0811-child-card h18-v0900-stack-member';
                            card.setAttribute('data-h18-v0811-child', member.key);
                            card.appendChild(layoutBar(member, memberRow, 0));
                            const memberPreview = document.createElement('div');
                            memberPreview.className = 'h18-v0811-child-preview h18-v0900-stack-member-preview';
                            const memberCopy = cleanPreviewClone(memberRow);
                            if (memberCopy) { memberPreview.appendChild(memberCopy); }
                            card.appendChild(memberPreview);
                            stack.appendChild(card);
                        });
                        body.appendChild(stack);
                    }
                    tile.appendChild(body);
                    if (canvasDevice() === 'desktop' && index < groups.length - 1) { tile.appendChild(resizeHandle(section.key, groups[index + 1].root.key)); }
                    wrapper.appendChild(tile);
                });

                preview.appendChild(wrapper);
                if (wrapper.isConnected) {
                    proxyCount++;
                    children.forEach(function (section) { if (rows[section.key]) { rows[section.key].setAttribute(CHILD_ATTR, parent.key); } });
                }
            });
            if (proxyCount > 0) { root.setAttribute(READY_ATTR, '1'); }
            document.documentElement.setAttribute('data-h18-layout-engine', VERSION);
        } finally {
            rendering = false;
        }
    }

    function schedule(reason) {
        if (scheduledFrame || resizeDrag) { return; }
        scheduledFrame = window.requestAnimationFrame(function () {
            scheduledFrame = 0;
            reconcile(reason || 'scheduled');
        });
    }
    function sameKeys(candidate) {
        if (!candidate) { return false; }
        const modelKeys = candidate.sections.map(function (section) { return section.key; }).sort();
        const rowKeys = sourceRows().map(rowKey).filter(Boolean).sort();
        return JSON.stringify(modelKeys) === JSON.stringify(rowKeys);
    }
    function captureSave(reason) {
        saveSnapshot = { time: Date.now(), model: clone(reconcile(reason || 'save-intent')) };
        trace('DIAG_LAYOUT_MODEL_SAVE_INTENT_V0900', saveSnapshot.model, reason, true);
    }
    function projectToRows(candidate) {
        const rows = rowMap();
        candidate.sections.forEach(function (section) {
            const row = rows[section.key];
            if (!row) { return; }
            row.classList.toggle('h18-page-section-removed', Boolean(section.removed));
            setValue(row, '.h18-page-section-remove,[name$="[Remove]"]', section.removed ? '1' : '0');
            setValue(row, '.h18-layout-parent-key,[name$="[LayoutParentKey]"]', section.parentKey || '');
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
        let candidate;
        if (saveSnapshot && Date.now() - saveSnapshot.time <= SNAPSHOT_AGE_MS && sameKeys(saveSnapshot.model)) { candidate = clone(saveSnapshot.model); }
        else if (currentModel && sameKeys(currentModel)) { candidate = clone(currentModel); }
        else { candidate = clone(reconcile('submit-fallback')); }
        candidate.reason = 'submit-canonical';
        candidate.capturedAt = new Date().toISOString();
        validate(candidate);
        projectToRows(candidate);
        writeModelField(candidate);
        currentModel = clone(candidate);
        trace('DIAG_LAYOUT_MODEL_SAVE_V0900', candidate, 'submit', true);
    }
    function submitControl(node) {
        const editorForm = form();
        if (!editorForm || !node || !node.closest) { return null; }
        const button = node.closest('button[type="submit"],input[type="submit"],button:not([type])');
        return button && editorForm.contains(button) ? button : null;
    }

    function modelSection(key) {
        key = cleanKey(key);
        return currentModel && currentModel.sections.find(function (section) { return section.key === key; }) || null;
    }
    function findTile(key) {
        return Array.from(document.querySelectorAll('.h18-v0900-layout-column')).find(function (node) {
            return node.getAttribute('data-h18-v0840-auto-child') === key;
        }) || null;
    }
    function startResize(event) {
        if (canvasDevice() !== 'desktop' || event.button !== 0 || !event.target || !event.target.closest) { return; }
        const handle = event.target.closest('.h18-v0900-resize-handle');
        if (!handle) { return; }
        const leftKey = cleanKey(handle.getAttribute('data-h18-v0900-left'));
        const rightKey = cleanKey(handle.getAttribute('data-h18-v0900-right'));
        const left = modelSection(leftKey);
        const right = modelSection(rightKey);
        const wrapper = handle.closest('.h18-v0900-layout');
        const leftTile = findTile(leftKey);
        const rightTile = findTile(rightKey);
        if (!left || !right || !wrapper || !leftTile || !rightTile) { return; }
        event.preventDefault(); event.stopPropagation();
        const leftSpan = Math.max(1, intValue(leftTile.getAttribute('data-h18-v0900-span'), effectiveSpan(left) || 1));
        const rightSpan = Math.max(1, intValue(rightTile.getAttribute('data-h18-v0900-span'), effectiveSpan(right) || 1));
        const styles = window.getComputedStyle(wrapper);
        const gap = parseFloat(styles.columnGap || styles.gap || '0') || 0;
        resizeDrag = {
            pointerId: event.pointerId,
            startX: event.clientX,
            step: Math.max(1, (wrapper.getBoundingClientRect().width + gap) / COLUMNS),
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
        const leftTile = findTile(resizeDrag.leftKey);
        const rightTile = findTile(resizeDrag.rightKey);
        if (leftTile) { leftTile.style.setProperty('--h18-v0900-span', String(resizeDrag.currentLeft)); leftTile.setAttribute('data-h18-v0900-span', String(resizeDrag.currentLeft)); }
        if (rightTile) { rightTile.style.setProperty('--h18-v0900-span', String(resizeDrag.currentRight)); rightTile.setAttribute('data-h18-v0900-span', String(resizeDrag.currentRight)); }
    }
    function finishResize(event, commit) {
        if (!resizeDrag || (event && event.pointerId !== resizeDrag.pointerId)) { return; }
        const drag = resizeDrag;
        resizeDrag = null;
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
            if (submitControl(event.target) && (event.key === 'Enter' || event.key === ' ')) { captureSave('submit-keydown'); }
        }, true);
        window.addEventListener('submit', function (event) { if (event.target === editorForm) { prepareSubmit(); } }, true);

        document.addEventListener('input', function () { schedule('input'); }, false);
        document.addEventListener('change', function () { schedule('change'); }, false);
        document.addEventListener('drop', function () { window.setTimeout(function () { schedule('drop'); }, 0); }, false);
        document.addEventListener('dragend', function () { window.setTimeout(function () { schedule('dragend'); }, 0); }, false);
        document.addEventListener('click', function () { window.setTimeout(function () { schedule('click'); }, 0); }, false);

        if (window.MutationObserver) {
            new MutationObserver(function (mutations) {
                if (rendering) { return; }
                const relevant = mutations.some(function (mutation) {
                    if (mutation.type === 'attributes') { return mutation.target.classList && mutation.target.classList.contains('h18-page-section-row'); }
                    if (mutation.target === root) { return true; }
                    return Array.from(mutation.addedNodes || []).concat(Array.from(mutation.removedNodes || [])).some(function (node) {
                        return node && node.classList && node.classList.contains('h18-page-section-row');
                    });
                });
                if (relevant) { schedule('source-mutation'); }
            }).observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['class'] });
            const canvas = document.querySelector('.h18-builder-canvas');
            if (canvas) { new MutationObserver(function () { schedule('device'); }).observe(canvas, { attributes: true, attributeFilter: ['data-canvas-device'] }); }
        }

        reconcile('boot');
        trace('DIAG_LAYOUT_ENGINE_BOOT_V0900', currentModel, 'boot', true);
        [100, 350, 900].forEach(function (delay) { window.setTimeout(function () { schedule('hydrate-' + delay); }, delay); });
    }

    window.__h18LayoutEngineV0900 = {
        version: VERSION,
        schemaVersion: SCHEMA_VERSION,
        snapshot: function () { return currentModel ? clone(currentModel) : null; },
        reconcile: reconcile,
        render: render,
        validate: function () { return currentModel ? validate(clone(currentModel)) : null; },
        prepareSubmit: prepareSubmit,
        stateForKey: function (key) { const section = modelSection(key); return section ? clone(section) : null; }
    };

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
