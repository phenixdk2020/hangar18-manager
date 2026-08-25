(function () {
    'use strict';

    if (window.__h18PhysicalCanvasV0901) { return; }

    const VERSION = '0.9.1';
    const SCHEMA = 1;
    const CFG = window.H18PhysicalCanvasV0901 || {};
    const UNITS = Math.max(12, parseInt(CFG.horizontalUnits || 120, 10) || 120);
    const ROW_PX = Math.max(2, parseInt(CFG.rowPx || 8, 10) || 8);
    const HOST_ID = 'h18-page-sections-sortable';
    const FORM_ID = 'h18-page-editor-form';
    const FIELD = 'h18_layout_geometry_v0901';
    const CELL_CLASS = 'h18-v0901-physical-cell';
    const HANDLE_CLASS = 'h18-v0901-cell-handle';
    const MOVE_CLASS = 'h18-v0901-move-handle';
    const PARENT_TYPES = ['container', 'grid', 'flex'];

    let geometry = {};
    let installed = false;
    let decorateTimer = 0;
    let observer = null;
    let activeResize = null;
    let activeMove = null;
    let transactionBefore = null;
    let transactionLabel = '';
    let restoring = false;
    let formEditBefore = null;
    let formEditTimer = 0;
    const undoStack = [];
    const redoStack = [];
    const HISTORY_LIMIT = 80;

    function host() { return document.getElementById(HOST_ID); }
    function form() { return document.getElementById(FORM_ID); }
    function engine() { return window.__h18LayoutEngineV0900 || null; }
    function clone(value) { return value == null ? value : JSON.parse(JSON.stringify(value)); }
    function cleanKey(raw) { return String(raw == null ? '' : raw).trim().toLowerCase().replace(/[^a-z0-9._-]/g, ''); }
    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
    function pageSlug() {
        const f = form();
        const field = f && f.querySelector('[name="page_slug"]');
        return String(field && field.value || '').trim();
    }
    function canvasDevice() {
        const canvas = document.querySelector('.h18-builder-canvas');
        return String(canvas && canvas.getAttribute('data-canvas-device') || 'desktop').toLowerCase();
    }
    function sourceRows() {
        const root = host();
        if (!root) { return []; }
        return Array.from(root.children).filter(function (node) {
            return node && node.classList && node.classList.contains('h18-page-section-row');
        });
    }
    function rowKey(row) {
        const field = row && row.querySelector('.h18-page-section-key,[name$="[Key]"]');
        return cleanKey(field && field.value || row && row.getAttribute('data-key') || '');
    }
    function rowType(row) {
        const field = row && row.querySelector('[name$="[Type]"]');
        return String(row && row.getAttribute('data-section-type') || field && field.value || 'text').trim().toLowerCase();
    }
    function rowMap() {
        const map = {};
        sourceRows().forEach(function (row) { const key = rowKey(row); if (key) { map[key] = row; } });
        return map;
    }
    function baseSnapshot() {
        const api = engine();
        return api && typeof api.snapshot === 'function' ? api.snapshot() : null;
    }
    function baseSection(key) {
        const api = engine();
        if (api && typeof api.stateForKey === 'function') {
            try { return api.stateForKey(key); } catch (ignore) {}
        }
        const snapshot = baseSnapshot();
        return snapshot && Array.isArray(snapshot.sections)
            ? snapshot.sections.find(function (section) { return section.key === key; }) || null
            : null;
    }
    function currentParent(key) {
        const state = baseSection(key);
        return cleanKey(state && state.parentKey || '');
    }
    function setRowField(key, selector, value) {
        const row = rowMap()[key];
        if (!row) { return false; }
        const fields = Array.from(row.querySelectorAll(selector));
        const inspector = row.classList.contains('is-selected') ? document.getElementById('h18-page-inspector-target') : null;
        if (inspector) {
            Array.from(inspector.querySelectorAll(selector)).forEach(function (field) {
                if (fields.indexOf(field) === -1) { fields.push(field); }
            });
        }
        fields.forEach(function (field) {
            if ('value' in field) { field.value = String(value); }
        });
        return fields.length > 0;
    }
    function setParent(key, parentKey) {
        return setRowField(key, '.h18-layout-parent-key,[name$="[LayoutParentKey]"]', cleanKey(parentKey));
    }
    function setOrder(key, order) {
        return setRowField(key, '.h18-page-section-order,[name$="[Order]"]', Math.max(1, parseInt(order, 10) || 10));
    }

    function defaultDevice(responsive) {
        const result = { Explicit: false, X: 0, Y: 0, W: UNITS, H: 0 };
        if (responsive) { result.InheritDesktop = true; result.HasOverride = false; }
        return result;
    }
    function normalizeDevice(raw, responsive) {
        raw = raw && typeof raw === 'object' ? raw : {};
        let x = clamp(parseInt(raw.X || 0, 10) || 0, 0, UNITS - 1);
        let w = clamp(parseInt(raw.W || UNITS, 10) || UNITS, 1, UNITS);
        if (x + w > UNITS) { w = UNITS - x; }
        const result = {
            Explicit: Boolean(raw.Explicit),
            X: x,
            Y: clamp(parseInt(raw.Y || 0, 10) || 0, -4000, 10000),
            W: Math.max(1, w),
            H: clamp(parseInt(raw.H || 0, 10) || 0, 0, 4000)
        };
        if (responsive) {
            result.InheritDesktop = raw.InheritDesktop !== false;
            result.HasOverride = Boolean(raw.HasOverride);
        }
        return result;
    }
    function normalizeGeometry(raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        return {
            SchemaVersion: SCHEMA,
            Desktop: normalizeDevice(raw.Desktop || {}, false),
            Tablet: normalizeDevice(raw.Tablet || {}, true),
            Mobile: normalizeDevice(raw.Mobile || {}, true)
        };
    }
    function geometryFor(key, create) {
        key = cleanKey(key);
        if (!key) { return null; }
        if (!geometry[key] && create) { geometry[key] = normalizeGeometry({}); }
        return geometry[key] || null;
    }
    function effectiveDeviceGeometry(key) {
        const state = geometryFor(key, false);
        if (!state) { return null; }
        const device = canvasDevice();
        if (device === 'desktop') { return state.Desktop; }
        const branch = device === 'mobile' ? state.Mobile : state.Tablet;
        return branch && branch.InheritDesktop !== false ? state.Desktop : branch;
    }
    function loadGeometry() {
        const pages = CFG.pages && typeof CFG.pages === 'object' ? CFG.pages : {};
        const stored = pages[pageSlug()] && typeof pages[pageSlug()] === 'object' ? pages[pageSlug()] : {};
        geometry = {};
        Object.keys(stored).forEach(function (key) {
            const clean = cleanKey(key);
            if (clean) { geometry[clean] = normalizeGeometry(stored[key]); }
        });
    }
    function writeGeometryField() {
        const f = form();
        if (!f) { return; }
        let field = f.querySelector('input[name="' + FIELD + '"]');
        if (!field) {
            field = document.createElement('input');
            field.type = 'hidden';
            field.name = FIELD;
            f.appendChild(field);
        }
        field.value = JSON.stringify({
            schemaVersion: SCHEMA,
            engineVersion: VERSION,
            pageSlug: pageSlug(),
            horizontalUnits: UNITS,
            rowPx: ROW_PX,
            sections: geometry
        });
    }

    function visualKey(node) {
        if (!node) { return ''; }
        let key = cleanKey(node.getAttribute && (
            node.getAttribute('data-h18-v0840-auto-child') ||
            node.getAttribute('data-h18-v0811-row') ||
            node.getAttribute('data-h18-v0901-key') || ''
        ));
        if (key) { return key; }
        if (node.classList && node.classList.contains('h18-page-section-row')) { return rowKey(node); }
        const proxy = node.closest && node.closest('[data-h18-v0840-auto-child],[data-h18-v0811-row],.h18-page-section-row');
        return proxy && proxy !== node ? visualKey(proxy) : '';
    }
    function isRemoved(section) { return Boolean(section && section.removed); }
    function activeTopLevelRows() {
        const snapshot = baseSnapshot();
        if (!snapshot || !Array.isArray(snapshot.sections)) { return []; }
        const rows = rowMap();
        return snapshot.sections.filter(function (section) {
            return section && !isRemoved(section) && !section.parentKey && rows[section.key];
        }).map(function (section) { return rows[section.key]; });
    }
    function visualNodes() {
        const result = [];
        document.querySelectorAll('.h18-v0900-layout-column[data-h18-v0840-auto-child]').forEach(function (node) {
            const key = visualKey(node);
            if (key && result.indexOf(node) === -1) { result.push(node); }
        });
        activeTopLevelRows().forEach(function (node) {
            if (result.indexOf(node) === -1) { result.push(node); }
        });
        return result;
    }
    function surfaceFor(node) {
        if (!node) { return null; }
        if (node.classList.contains('h18-v0900-layout-column')) {
            return node.parentElement && node.parentElement.classList.contains('h18-v0900-layout') ? node.parentElement : null;
        }
        if (node.classList.contains('h18-page-section-row')) { return host(); }
        return node.parentElement;
    }
    function directSurfaceChildren(surface) {
        if (!surface) { return []; }
        if (surface === host()) { return activeTopLevelRows(); }
        return Array.from(surface.children).filter(function (node) {
            return node.classList && node.classList.contains('h18-v0900-layout-column');
        });
    }

    function ensureGeometryFromRect(node, forceExplicit) {
        const key = visualKey(node);
        const surface = surfaceFor(node);
        if (!key || !surface) { return null; }
        const state = geometryFor(key, true);
        const branch = state.Desktop;
        if (branch.Explicit && !forceExplicit) { return branch; }
        const rect = node.getBoundingClientRect();
        const surfaceRect = surface.getBoundingClientRect();
        const width = Math.max(1, surfaceRect.width || rect.width || 1);
        branch.X = clamp(Math.round(((rect.left - surfaceRect.left) / width) * UNITS), 0, UNITS - 1);
        branch.W = clamp(Math.round((rect.width / width) * UNITS), 1, UNITS);
        if (branch.X + branch.W > UNITS) { branch.W = Math.max(1, UNITS - branch.X); }
        branch.Y = 0;
        branch.H = Math.max(1, Math.round(rect.height / ROW_PX));
        branch.Explicit = Boolean(forceExplicit);
        return branch;
    }
    function captureSurfaceGeometry(surface) {
        const children = directSurfaceChildren(surface);
        if (!children.length) { return; }
        // Read every rectangle before adding 120-unit styles so the conversion
        // preserves the current visual proportions as closely as possible.
        const surfaceRect = surface.getBoundingClientRect();
        const width = Math.max(1, surfaceRect.width || 1);
        const captured = children.map(function (node) {
            const rect = node.getBoundingClientRect();
            return { node: node, key: visualKey(node), rect: rect };
        });
        captured.forEach(function (item) {
            if (!item.key) { return; }
            const state = geometryFor(item.key, true).Desktop;
            if (state.Explicit) { return; }
            state.X = clamp(Math.round(((item.rect.left - surfaceRect.left) / width) * UNITS), 0, UNITS - 1);
            state.W = clamp(Math.round((item.rect.width / width) * UNITS), 1, UNITS);
            if (state.X + state.W > UNITS) { state.W = Math.max(1, UNITS - state.X); }
            state.Y = 0;
            state.H = 0;
            state.Explicit = true;
        });
    }

    function applyGeometry(node) {
        const key = visualKey(node);
        const state = effectiveDeviceGeometry(key);
        if (!key || !state || !state.Explicit) {
            node.style.removeProperty('--h18-v0901-x');
            node.style.removeProperty('--h18-v0901-w');
            node.style.removeProperty('--h18-v0901-y-px');
            node.style.removeProperty('--h18-v0901-h-px');
            node.classList.remove('h18-v0901-geometry-explicit');
            return;
        }
        node.classList.add('h18-v0901-geometry-explicit');
        node.style.setProperty('--h18-v0901-x', String(state.X));
        node.style.setProperty('--h18-v0901-w', String(state.W));
        node.style.setProperty('--h18-v0901-y-px', String(state.Y * ROW_PX) + 'px');
        node.style.setProperty('--h18-v0901-h-px', state.H > 0 ? String(state.H * ROW_PX) + 'px' : 'auto');

        const surface = surfaceFor(node);
        if (surface && surface.classList.contains('h18-v0900-layout--grid')) {
            surface.classList.add('h18-v0901-unit-surface');
            node.style.gridColumn = String(state.X + 1) + ' / span ' + String(state.W);
            node.style.width = '';
            node.style.marginLeft = '';
        } else {
            node.style.gridColumn = '';
            node.style.width = 'calc((' + String(state.W) + ' / ' + String(UNITS) + ') * 100%)';
            node.style.marginLeft = 'calc((' + String(state.X) + ' / ' + String(UNITS) + ') * 100%)';
        }
        node.style.marginTop = String(state.Y * ROW_PX) + 'px';
        if (state.H > 0) {
            node.style.height = String(state.H * ROW_PX) + 'px';
            node.style.minHeight = String(state.H * ROW_PX) + 'px';
        } else {
            node.style.height = '';
            node.style.minHeight = '';
        }
        node.setAttribute('data-h18-v0901-geometry', state.X + ',' + state.Y + ',' + state.W + ',' + state.H);
    }

    function makeHandle(direction) {
        const handle = document.createElement('button');
        handle.type = 'button';
        handle.className = HANDLE_CLASS + ' ' + HANDLE_CLASS + '--' + direction;
        handle.setAttribute('data-h18-v0901-resize', direction);
        handle.setAttribute('aria-label', 'Ændr størrelse ' + direction.toUpperCase());
        handle.title = 'Træk for at ændre størrelse (' + direction.toUpperCase() + ')';
        return handle;
    }
    function decorateNode(node) {
        const key = visualKey(node);
        if (!key) { return; }
        node.classList.add(CELL_CLASS);
        node.setAttribute('data-h18-v0901-key', key);
        if (!node.querySelector(':scope > .' + MOVE_CLASS)) {
            const move = document.createElement('button');
            move.type = 'button';
            move.className = MOVE_CLASS;
            move.setAttribute('data-h18-v0901-move', key);
            move.title = 'Træk elementet ind i/ud af en kasse';
            move.setAttribute('aria-label', 'Flyt element');
            move.textContent = '✥';
            node.appendChild(move);
        }
        ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'].forEach(function (direction) {
            if (!node.querySelector(':scope > .' + HANDLE_CLASS + '--' + direction)) {
                node.appendChild(makeHandle(direction));
            }
        });
        applyGeometry(node);
    }
    function decorate() {
        if (restoring || activeResize || activeMove) { return; }
        visualNodes().forEach(decorateNode);
        writeGeometryField();
        updateHistoryUi();
    }
    function scheduleDecorate(delay) {
        window.clearTimeout(decorateTimer);
        decorateTimer = window.setTimeout(decorate, typeof delay === 'number' ? delay : 30);
    }

    function trace(type, detail) {
        const safe = detail && typeof detail === 'object' ? detail : {};
        const api = window.__h18UltimateDesignerTraceV0876;
        if (api && typeof api.record === 'function') {
            try { api.record(type, document.body, Object.assign({ version: VERSION }, safe), { force: true }); } catch (ignore) {}
        }
        const live = window.__h18LiveDiagnosticsV0888;
        if (live && typeof live.flush === 'function') {
            window.setTimeout(function () { try { live.flush(); } catch (ignore) {} }, 20);
        }
    }

    function collectEditableFields() {
        const f = form();
        const values = {};
        if (!f) { return values; }
        Array.from(f.querySelectorAll('input[name],select[name],textarea[name]')).forEach(function (field) {
            const name = String(field.name || '');
            if (!name || name === FIELD || name === 'h18_layout_model_v0900' || name === '_wpnonce' || name === 'action' || name === 'page_slug') { return; }
            if (name.indexOf('h18_lego_layout_span') === 0 || name.indexOf('h18_lego_stack_v0851') === 0) { return; }
            if (field.type === 'file' || field.type === 'submit' || field.type === 'button') { return; }
            if (field.type === 'checkbox' || field.type === 'radio') {
                values[name] = { kind: field.type, value: String(field.value || ''), checked: Boolean(field.checked) };
            } else {
                values[name] = { kind: 'value', value: String(field.value == null ? '' : field.value) };
            }
        });
        return values;
    }
    function snapshotState() {
        return {
            layout: clone(baseSnapshot()),
            geometry: clone(geometry),
            fields: collectEditableFields()
        };
    }
    function snapshotSignature(snapshot) {
        return JSON.stringify(snapshot || null);
    }
    function beginTransaction(label) {
        if (restoring || transactionBefore) { return; }
        transactionBefore = snapshotState();
        transactionLabel = String(label || 'Ændring');
    }
    function commitTransaction(label) {
        if (restoring) { return; }
        const before = transactionBefore;
        const finalLabel = String(label || transactionLabel || 'Ændring');
        transactionBefore = null;
        transactionLabel = '';
        if (!before) { return; }
        const after = snapshotState();
        if (snapshotSignature(before) === snapshotSignature(after)) { return; }
        undoStack.push({ label: finalLabel, before: before, after: after });
        if (undoStack.length > HISTORY_LIMIT) { undoStack.shift(); }
        redoStack.length = 0;
        updateHistoryUi();
    }
    function cancelTransaction() {
        transactionBefore = null;
        transactionLabel = '';
    }
    function restoreFields(values) {
        const f = form();
        if (!f || !values) { return; }
        const fields = Array.from(f.querySelectorAll('input[name],select[name],textarea[name]'));
        fields.forEach(function (field) {
            const state = values[field.name];
            if (!state) { return; }
            if (state.kind === 'checkbox' || state.kind === 'radio') { field.checked = Boolean(state.checked); }
            else if ('value' in field) { field.value = state.value; }
        });
    }
    function restoreLayout(layout) {
        if (!layout || !Array.isArray(layout.sections)) { return; }
        layout.sections.forEach(function (section) {
            if (!section || !section.key) { return; }
            setParent(section.key, section.parentKey || '');
            setOrder(section.key, section.order || 10);
            const row = rowMap()[section.key];
            if (row) {
                const remove = row.querySelector('.h18-page-section-remove,[name$="[Remove]"]');
                if (remove && section.removed !== undefined) { remove.value = section.removed ? '1' : '0'; }
            }
        });
    }
    function restoreSnapshot(snapshot, reason) {
        if (!snapshot) { return; }
        restoring = true;
        try {
            restoreFields(snapshot.fields || {});
            restoreLayout(snapshot.layout);
            geometry = clone(snapshot.geometry || {});
            writeGeometryField();
            const api = engine();
            if (api && typeof api.reconcile === 'function') { api.reconcile('v0901-' + String(reason || 'restore')); }
        } finally {
            restoring = false;
        }
        scheduleDecorate(0);
        scheduleDecorate(80);
    }
    function undo() {
        if (activeResize || activeMove || !undoStack.length) { return; }
        const entry = undoStack.pop();
        restoreSnapshot(entry.before, 'undo');
        redoStack.push(entry);
        trace('DIAG_CANVAS_UNDO_V0901', { label: entry.label, undoDepth: undoStack.length, redoDepth: redoStack.length });
        updateHistoryUi();
    }
    function redo() {
        if (activeResize || activeMove || !redoStack.length) { return; }
        const entry = redoStack.pop();
        restoreSnapshot(entry.after, 'redo');
        undoStack.push(entry);
        trace('DIAG_CANVAS_REDO_V0901', { label: entry.label, undoDepth: undoStack.length, redoDepth: redoStack.length });
        updateHistoryUi();
    }

    function installToolbar() {
        const heading = document.querySelector('.h18-builder-canvas-heading');
        if (!heading || heading.querySelector('.h18-v0901-history-toolbar')) { return; }
        const toolbar = document.createElement('div');
        toolbar.className = 'h18-v0901-history-toolbar';
        toolbar.innerHTML = '<button type="button" class="button h18-v0901-undo" disabled>↶ Fortryd</button>' +
            '<button type="button" class="button h18-v0901-redo" disabled>↷ Gentag</button>' +
            '<span class="h18-v0901-grid-badge">120 units · 8 px lodret snap</span>';
        heading.appendChild(toolbar);
        toolbar.querySelector('.h18-v0901-undo').addEventListener('click', undo);
        toolbar.querySelector('.h18-v0901-redo').addEventListener('click', redo);
    }
    function updateHistoryUi() {
        const undoButton = document.querySelector('.h18-v0901-undo');
        const redoButton = document.querySelector('.h18-v0901-redo');
        if (undoButton) {
            undoButton.disabled = !undoStack.length;
            undoButton.title = undoStack.length ? 'Fortryd: ' + undoStack[undoStack.length - 1].label : 'Intet at fortryde';
        }
        if (redoButton) {
            redoButton.disabled = !redoStack.length;
            redoButton.title = redoStack.length ? 'Gentag: ' + redoStack[redoStack.length - 1].label : 'Intet at gentage';
        }
    }

    function startResize(event, handle) {
        if (canvasDevice() !== 'desktop' || event.button !== 0 || activeMove || activeResize) { return; }
        const node = handle.closest('.' + CELL_CLASS);
        const key = visualKey(node);
        const surface = surfaceFor(node);
        if (!node || !key || !surface) { return; }

        captureSurfaceGeometry(surface);
        const state = geometryFor(key, true).Desktop;
        if (!state.H) {
            const rect = node.getBoundingClientRect();
            state.H = Math.max(1, Math.round(rect.height / ROW_PX));
        }
        state.Explicit = true;
        beginTransaction('Resize ' + key);

        activeResize = {
            pointerId: event.pointerId,
            direction: String(handle.getAttribute('data-h18-v0901-resize') || 'se'),
            node: node,
            key: key,
            surface: surface,
            surfaceWidth: Math.max(1, surface.getBoundingClientRect().width || 1),
            startX: event.clientX,
            startY: event.clientY,
            start: clone(state)
        };
        document.documentElement.classList.add('h18-v0901-is-resizing');
        node.classList.add('is-v0901-resizing');
        try { handle.setPointerCapture(event.pointerId); } catch (ignore) {}
        trace('DIAG_CANVAS_RESIZE_BEGIN_V0901', { key: key, direction: activeResize.direction, geometry: clone(state) });
        event.preventDefault();
        event.stopPropagation();
    }
    function moveResize(event) {
        if (!activeResize || event.pointerId !== activeResize.pointerId) { return; }
        const drag = activeResize;
        const dxUnits = Math.round(((event.clientX - drag.startX) / drag.surfaceWidth) * UNITS);
        const dyUnits = Math.round((event.clientY - drag.startY) / ROW_PX);
        const next = clone(drag.start);
        const dir = drag.direction;

        if (dir.indexOf('e') !== -1) { next.W = drag.start.W + dxUnits; }
        if (dir.indexOf('w') !== -1) { next.X = drag.start.X + dxUnits; next.W = drag.start.W - dxUnits; }
        if (dir.indexOf('s') !== -1) { next.H = drag.start.H + dyUnits; }
        if (dir.indexOf('n') !== -1) { next.Y = drag.start.Y + dyUnits; next.H = drag.start.H - dyUnits; }

        if (next.W < 1) {
            if (dir.indexOf('w') !== -1) { next.X -= (1 - next.W); }
            next.W = 1;
        }
        if (next.X < 0) {
            if (dir.indexOf('w') !== -1) { next.W += next.X; }
            next.X = 0;
        }
        if (next.X + next.W > UNITS) {
            if (dir.indexOf('e') !== -1) { next.W = UNITS - next.X; }
            else { next.X = UNITS - next.W; }
        }
        next.W = clamp(next.W, 1, UNITS);
        next.X = clamp(next.X, 0, UNITS - next.W);
        next.H = clamp(next.H, 1, 4000);
        next.Y = clamp(next.Y, -4000, 10000);
        next.Explicit = true;

        geometryFor(drag.key, true).Desktop = next;
        applyGeometry(drag.node);
        writeGeometryField();
        event.preventDefault();
    }
    function finishResize(event, commit) {
        if (!activeResize || event.pointerId !== activeResize.pointerId) { return; }
        const drag = activeResize;
        activeResize = null;
        document.documentElement.classList.remove('h18-v0901-is-resizing');
        drag.node.classList.remove('is-v0901-resizing');
        if (commit) {
            writeGeometryField();
            commitTransaction('Resize ' + drag.key);
            const state = geometryFor(drag.key, true).Desktop;
            trace('DIAG_CANVAS_RESIZE_COMMIT_V0901', { key: drag.key, direction: drag.direction, geometry: clone(state) });
        } else {
            restoreSnapshot(transactionBefore, 'resize-cancel');
            cancelTransaction();
        }
        scheduleDecorate(20);
    }

    function isDescendant(candidateKey, ancestorKey) {
        const snapshot = baseSnapshot();
        if (!snapshot || !Array.isArray(snapshot.sections)) { return false; }
        const byKey = {};
        snapshot.sections.forEach(function (section) { if (section && section.key) { byKey[section.key] = section; } });
        let cursor = cleanKey(candidateKey);
        const seen = {};
        while (cursor && byKey[cursor] && !seen[cursor]) {
            if (cursor === ancestorKey) { return true; }
            seen[cursor] = true;
            cursor = cleanKey(byKey[cursor].parentKey || '');
        }
        return false;
    }
    function validContainerKey(key, draggedKey) {
        key = cleanKey(key);
        if (!key || key === draggedKey) { return false; }
        const state = baseSection(key);
        if (!state || state.removed || PARENT_TYPES.indexOf(String(state.type || '').toLowerCase()) === -1) { return false; }
        if (isDescendant(key, draggedKey)) { return false; }
        return true;
    }
    function candidateFromPoint(x, y, draggedKey) {
        const elements = document.elementsFromPoint ? document.elementsFromPoint(x, y) : [document.elementFromPoint(x, y)];
        for (let i = 0; i < elements.length; i++) {
            const node = elements[i];
            if (!node) { continue; }
            if (node.classList && node.classList.contains('h18-v0901-root-drop-zone')) { return { kind: 'root', key: '' }; }
            const key = visualKey(node);
            if (validContainerKey(key, draggedKey)) { return { kind: 'container', key: key }; }
        }
        const root = host();
        const canvas = document.querySelector('.h18-builder-canvas');
        const target = document.elementFromPoint(x, y);
        if (target && ((root && root.contains(target)) || (canvas && canvas.contains(target)))) { return { kind: 'root', key: '' }; }
        return null;
    }
    function clearDropHighlight() {
        document.querySelectorAll('.h18-v0901-drop-target').forEach(function (node) { node.classList.remove('h18-v0901-drop-target'); });
        const root = host();
        if (root) { root.classList.remove('h18-v0901-root-target'); }
    }
    function highlightCandidate(candidate) {
        clearDropHighlight();
        if (!candidate) { return; }
        if (candidate.kind === 'root') {
            const root = host();
            if (root) { root.classList.add('h18-v0901-root-target'); }
            return;
        }
        visualNodes().forEach(function (node) {
            if (visualKey(node) === candidate.key) { node.classList.add('h18-v0901-drop-target'); }
        });
    }
    function installRootDropZone() {
        const canvas = document.querySelector('.h18-builder-canvas');
        if (!canvas) { return null; }
        let zone = canvas.querySelector('.h18-v0901-root-drop-zone');
        if (!zone) {
            zone = document.createElement('div');
            zone.className = 'h18-v0901-root-drop-zone';
            zone.textContent = 'Slip her for at flytte elementet ud på siden (root)';
            canvas.appendChild(zone);
        }
        return zone;
    }
    function startMove(event, handle) {
        if (canvasDevice() !== 'desktop' || event.button !== 0 || activeResize || activeMove) { return; }
        const node = handle.closest('.' + CELL_CLASS);
        const key = cleanKey(handle.getAttribute('data-h18-v0901-move') || visualKey(node));
        if (!node || !key) { return; }
        beginTransaction('Flyt ' + key);
        const zone = installRootDropZone();
        if (zone) { zone.classList.add('is-active'); }
        const ghost = document.createElement('div');
        ghost.className = 'h18-v0901-drag-ghost';
        ghost.textContent = 'Flytter: ' + key;
        document.body.appendChild(ghost);
        activeMove = {
            pointerId: event.pointerId,
            key: key,
            node: node,
            startParent: currentParent(key),
            candidate: null,
            ghost: ghost
        };
        document.documentElement.classList.add('h18-v0901-is-moving');
        node.classList.add('is-v0901-moving');
        try { handle.setPointerCapture(event.pointerId); } catch (ignore) {}
        trace('DIAG_CANVAS_REPARENT_BEGIN_V0901', { key: key, parentKey: activeMove.startParent });
        moveExisting(event);
        event.preventDefault();
        event.stopPropagation();
    }
    function moveExisting(event) {
        if (!activeMove || event.pointerId !== activeMove.pointerId) { return; }
        activeMove.ghost.style.left = String(event.clientX + 14) + 'px';
        activeMove.ghost.style.top = String(event.clientY + 14) + 'px';
        activeMove.candidate = candidateFromPoint(event.clientX, event.clientY, activeMove.key);
        highlightCandidate(activeMove.candidate);
        event.preventDefault();
    }
    function nextOrder(parentKey, movingKey) {
        const snapshot = baseSnapshot();
        if (!snapshot || !Array.isArray(snapshot.sections)) { return 10; }
        let max = 0;
        snapshot.sections.forEach(function (section) {
            if (!section || section.key === movingKey || section.removed) { return; }
            if (cleanKey(section.parentKey || '') === cleanKey(parentKey || '')) {
                max = Math.max(max, parseInt(section.order || 0, 10) || 0);
            }
        });
        return Math.min(10000, Math.max(10, max + 10));
    }
    function finishMove(event, commit) {
        if (!activeMove || event.pointerId !== activeMove.pointerId) { return; }
        const drag = activeMove;
        activeMove = null;
        clearDropHighlight();
        document.documentElement.classList.remove('h18-v0901-is-moving');
        drag.node.classList.remove('is-v0901-moving');
        if (drag.ghost && drag.ghost.parentNode) { drag.ghost.parentNode.removeChild(drag.ghost); }
        const zone = document.querySelector('.h18-v0901-root-drop-zone');
        if (zone) { zone.classList.remove('is-active'); }

        if (!commit || !drag.candidate) {
            restoreSnapshot(transactionBefore, 'move-cancel');
            cancelTransaction();
            return;
        }

        const parentKey = drag.candidate.kind === 'container' ? drag.candidate.key : '';
        if (parentKey === drag.startParent) {
            cancelTransaction();
            scheduleDecorate(20);
            return;
        }

        setParent(drag.key, parentKey);
        setOrder(drag.key, nextOrder(parentKey, drag.key));
        const state = geometryFor(drag.key, true);
        state.Desktop = defaultDevice(false);
        state.Tablet = defaultDevice(true);
        state.Mobile = defaultDevice(true);
        writeGeometryField();

        const api = engine();
        if (api && typeof api.reconcile === 'function') { api.reconcile('v0901-reparent'); }
        scheduleDecorate(0);
        scheduleDecorate(100);
        commitTransaction('Flyt ' + drag.key + (parentKey ? ' ind i ' + parentKey : ' ud på siden'));
        trace('DIAG_CANVAS_REPARENT_COMMIT_V0901', {
            key: drag.key,
            fromParentKey: drag.startParent,
            toParentKey: parentKey,
            order: nextOrder(parentKey, drag.key)
        });
    }

    function fieldEligible(target) {
        if (!target || !target.matches || !target.closest('#' + FORM_ID)) { return false; }
        if (!target.matches('input,select,textarea')) { return false; }
        const name = String(target.name || '');
        if (!name || name === FIELD || name === 'h18_layout_model_v0900' || name === '_wpnonce' || name === 'action' || name === 'page_slug') { return false; }
        if (name.indexOf('h18_lego_layout_span') === 0 || name.indexOf('h18_lego_stack_v0851') === 0) { return false; }
        if (name.match(/\[(LayoutParentKey|Order|Remove|Key)\]$/)) { return false; }
        return target.type !== 'file' && target.type !== 'hidden';
    }
    function beginFieldEdit(event) {
        if (restoring || activeResize || activeMove || !fieldEligible(event.target)) { return; }
        if (!formEditBefore) { formEditBefore = snapshotState(); }
    }
    function commitFieldEdit() {
        window.clearTimeout(formEditTimer);
        if (!formEditBefore || restoring || activeResize || activeMove) { formEditBefore = null; return; }
        const before = formEditBefore;
        formEditBefore = null;
        const after = snapshotState();
        if (snapshotSignature(before) === snapshotSignature(after)) { return; }
        undoStack.push({ label: 'Redigér element', before: before, after: after });
        if (undoStack.length > HISTORY_LIMIT) { undoStack.shift(); }
        redoStack.length = 0;
        updateHistoryUi();
    }
    function scheduleFieldCommit() {
        window.clearTimeout(formEditTimer);
        formEditTimer = window.setTimeout(commitFieldEdit, 350);
    }

    function handlePointerDown(event) {
        const target = event.target;
        if (!target || !target.closest) { return; }
        const resize = target.closest('.' + HANDLE_CLASS);
        if (resize) { startResize(event, resize); return; }
        const move = target.closest('.' + MOVE_CLASS);
        if (move) { startMove(event, move); }
    }
    function handlePointerMove(event) {
        if (activeResize) { moveResize(event); }
        else if (activeMove) { moveExisting(event); }
    }
    function handlePointerUp(event) {
        if (activeResize) { finishResize(event, true); }
        else if (activeMove) { finishMove(event, true); }
    }
    function handlePointerCancel(event) {
        if (activeResize) { finishResize(event, false); }
        else if (activeMove) { finishMove(event, false); }
    }
    function handleKeydown(event) {
        const modifier = event.ctrlKey || event.metaKey;
        if (!modifier) { return; }
        const key = String(event.key || '').toLowerCase();
        if (key === 'z' && event.shiftKey) { event.preventDefault(); redo(); return; }
        if (key === 'z') { event.preventDefault(); undo(); return; }
        if (key === 'y') { event.preventDefault(); redo(); }
    }
    function beforeSave(event) {
        const target = event.target;
        if (!target || !target.closest) { return; }
        const submit = target.closest('button[type="submit"],input[type="submit"],.button-primary');
        if (submit && submit.closest('#' + FORM_ID)) { writeGeometryField(); }
    }

    function install() {
        if (installed) { return; }
        if (!host() || !form() || !engine()) { window.setTimeout(install, 80); return; }
        installed = true;
        loadGeometry();
        installToolbar();
        writeGeometryField();

        window.addEventListener('pointerdown', handlePointerDown, true);
        window.addEventListener('pointermove', handlePointerMove, true);
        window.addEventListener('pointerup', handlePointerUp, true);
        window.addEventListener('pointercancel', handlePointerCancel, true);
        document.addEventListener('keydown', handleKeydown, true);
        document.addEventListener('focusin', beginFieldEdit, true);
        document.addEventListener('input', function (event) { if (fieldEligible(event.target)) { beginFieldEdit(event); scheduleFieldCommit(); } }, true);
        document.addEventListener('change', function (event) { if (fieldEligible(event.target)) { beginFieldEdit(event); commitFieldEdit(); } }, true);
        document.addEventListener('focusout', function (event) { if (fieldEligible(event.target)) { scheduleFieldCommit(); } }, true);
        window.addEventListener('pointerdown', beforeSave, true);
        form().addEventListener('submit', writeGeometryField, true);

        observer = new MutationObserver(function () { if (!activeResize && !activeMove && !restoring) { scheduleDecorate(40); } });
        observer.observe(host(), { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'data-canvas-device'] });

        document.documentElement.setAttribute('data-h18-physical-canvas', VERSION);
        decorate();
        [120, 400, 900].forEach(function (delay) { window.setTimeout(function () { scheduleDecorate(0); }, delay); });
        trace('DIAG_CANVAS_PHYSICAL_BOOT_V0901', {
            units: UNITS,
            rowPx: ROW_PX,
            persistedGeometryCount: Object.keys(geometry).length
        });
    }

    window.__h18PhysicalCanvasV0901 = {
        version: VERSION,
        horizontalUnits: UNITS,
        rowPx: ROW_PX,
        geometryForKey: function (key) { return clone(geometryFor(key, false)); },
        snapshot: snapshotState,
        undo: undo,
        redo: redo,
        canUndo: function () { return undoStack.length > 0; },
        canRedo: function () { return redoStack.length > 0; },
        refresh: function () { scheduleDecorate(0); },
        writeSavePayload: writeGeometryField
    };

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
