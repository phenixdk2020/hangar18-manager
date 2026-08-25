(function () {
    'use strict';

    const CFG = window.H18CleanEditor || {};
    const UNITS = Math.max(12, parseInt(CFG.units || 120, 10) || 120);
    const ROW_PX = Math.max(2, parseInt(CFG.rowPx || 8, 10) || 8);
    const POST_ID = parseInt(CFG.postId || 0, 10) || 0;
    const TYPES = ['section', 'container', 'text', 'image'];
    const PARENT_TYPES = ['section', 'container'];
    const undoStack = [];
    const redoStack = [];
    const HISTORY_LIMIT = 100;
    const MIN_SPLIT_H = 8;

    let state = normalizeModel(CFG.initialModel || {});
    let selectedId = '';
    let dragId = '';
    let dragPaletteType = '';
    let dragSource = null;
    let resize = null;
    let lastAction = '';

    function clone(value) { return JSON.parse(JSON.stringify(value)); }
    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
    function cleanId(value) { return String(value || '').toLowerCase().replace(/[^a-z0-9._-]/g, '').slice(0, 100); }
    function makeId(type) { return cleanId(type + '-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 8)); }
    function normalizeColor(value) { return /^#[0-9a-f]{6}$/i.test(String(value || '')) ? String(value).toLowerCase() : '#000000'; }

    function normalizeDevice(raw, responsive) {
        raw = raw && typeof raw === 'object' ? raw : {};
        const x = clamp(parseInt(raw.x || 0, 10) || 0, 0, UNITS - 1);
        let w = clamp(parseInt(raw.w || UNITS, 10) || UNITS, 1, UNITS);
        if (x + w > UNITS) { w = UNITS - x; }
        const out = {
            x: x,
            y: clamp(parseInt(raw.y || 0, 10) || 0, -4000, 10000),
            w: Math.max(1, w),
            h: clamp(parseInt(raw.h || 0, 10) || 0, 0, 4000)
        };
        if (responsive) { out.inheritDesktop = raw.inheritDesktop !== false; }
        return out;
    }

    function commonProps(raw) {
        return {
            borderWidth: clamp(parseInt(raw.borderWidth || 0, 10) || 0, 0, 20),
            borderColor: normalizeColor(raw.borderColor || '#000000'),
            gapX: clamp(parseInt(raw.gapX || 0, 10) || 0, 0, 200),
            gapY: clamp(parseInt(raw.gapY || 0, 10) || 0, 0, 200)
        };
    }

    function normalizeProps(type, raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        const common = commonProps(raw);
        if (type === 'text') {
            return Object.assign(common, {
                text: String(raw.text || 'Ny tekst'),
                align: ['left', 'center', 'right'].includes(raw.align) ? raw.align : 'left'
            });
        }
        if (type === 'image') {
            const fit = ['cover', 'contain', 'stretch'].includes(String(raw.fit || '').toLowerCase()) ? String(raw.fit).toLowerCase() : 'cover';
            return Object.assign(common, {
                mediaId: parseInt(raw.mediaId || 0, 10) || 0,
                url: String(raw.url || ''),
                alt: String(raw.alt || ''),
                fit: fit,
                focalX: clamp(parseInt(raw.focalX || 50, 10) || 50, 0, 100),
                focalY: clamp(parseInt(raw.focalY || 50, 10) || 50, 0, 100)
            });
        }
        if (PARENT_TYPES.includes(type)) {
            return Object.assign(common, {
                background: String(raw.background || ''),
                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),
                padding: clamp(parseInt(raw.padding || 0, 10) || 0, 0, 120),
                minHeightRows: clamp(parseInt(raw.minHeightRows || 0, 10) || 0, 0, 4000)
            });
        }
        return common;
    }

    function normalizeModel(raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        const used = {};
        const nodes = [];
        (Array.isArray(raw.nodes) ? raw.nodes : []).slice(0, 300).forEach(function (item, index) {
            if (!item || typeof item !== 'object') { return; }
            const id = cleanId(item.id);
            const type = String(item.type || 'text').toLowerCase();
            if (!id || used[id] || !TYPES.includes(type)) { return; }
            used[id] = true;
            nodes.push({
                id: id,
                type: type,
                parentId: cleanId(item.parentId || ''),
                order: Math.max(1, parseInt(item.order || ((index + 1) * 10), 10) || ((index + 1) * 10)),
                geometry: {
                    desktop: normalizeDevice(item.geometry && item.geometry.desktop, false),
                    tablet: normalizeDevice(item.geometry && item.geometry.tablet, true),
                    mobile: normalizeDevice(item.geometry && item.geometry.mobile, true)
                },
                props: normalizeProps(type, item.props)
            });
            const added = nodes[nodes.length - 1];
            if (PARENT_TYPES.includes(type) && (!item.props || !Object.prototype.hasOwnProperty.call(item.props, 'minHeightRows'))) {
                added.props.minHeightRows = added.geometry.desktop.h;
            }
        });
        const map = {};
        nodes.forEach(function (node) { map[node.id] = node; });
        nodes.forEach(function (node) {
            if (!node.parentId || node.parentId === node.id || !map[node.parentId] || !PARENT_TYPES.includes(map[node.parentId].type)) { node.parentId = ''; }
        });
        nodes.forEach(function (node) {
            const seen = {};
            let cursor = node;
            while (cursor && cursor.parentId) {
                if (seen[cursor.id]) { node.parentId = ''; break; }
                seen[cursor.id] = true;
                cursor = map[cursor.parentId];
            }
        });
        return { schemaVersion: 1, units: UNITS, rowPx: ROW_PX, nodes: nodes };
    }

    function mapById() {
        const map = {};
        state.nodes.forEach(function (node) { map[node.id] = node; });
        return map;
    }
    function nodeById(id) { return mapById()[cleanId(id)] || null; }
    function children(parentId) {
        return state.nodes.filter(function (node) { return node.parentId === parentId; }).sort(function (a, b) { return a.order - b.order; });
    }
    function descendants(id) {
        const result = [];
        const queue = [id];
        while (queue.length) {
            const parent = queue.shift();
            children(parent).forEach(function (child) { result.push(child.id); queue.push(child.id); });
        }
        return result;
    }

    function structuralSummary() {
        return {
            nodeCount: state.nodes.length,
            nodes: state.nodes.map(function (node) {
                const row = { id: node.id, type: node.type, parentId: node.parentId, order: node.order, geometry: clone(node.geometry) };
                if (node.type === 'image') {
                    row.image = { mediaId: node.props.mediaId, fit: node.props.fit, focalX: node.props.focalX, focalY: node.props.focalY };
                }
                return row;
            })
        };
    }

    function diag(type, detail) {
        if (!POST_ID || !CFG.ajaxUrl || !CFG.diagNonce) { return; }
        const body = new URLSearchParams();
        body.set('action', CFG.diagAction || 'h18_clean_diag_append');
        body.set('nonce', CFG.diagNonce);
        body.set('post_id', String(POST_ID));
        body.set('event_type', String(type || 'client'));
        body.set('detail_json', JSON.stringify(detail || {}));
        fetch(CFG.ajaxUrl, {
            method: 'POST', credentials: 'same-origin', keepalive: true,
            headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
            body: body.toString(), cache: 'no-store'
        }).catch(function () {});
    }

    function updateHidden() {
        const field = document.getElementById('h18-clean-model-json');
        if (field) { field.value = JSON.stringify(state); }
    }
    function updateHistoryUi() {
        const undo = document.getElementById('h18-clean-undo');
        const redo = document.getElementById('h18-clean-redo');
        if (undo) { undo.disabled = undoStack.length === 0; undo.title = undoStack.length ? undoStack[undoStack.length - 1].label : ''; }
        if (redo) { redo.disabled = redoStack.length === 0; redo.title = redoStack.length ? redoStack[redoStack.length - 1].label : ''; }
    }
    function commit(before, label) {
        const after = clone(state);
        if (JSON.stringify(before) === JSON.stringify(after)) { return; }
        undoStack.push({ before: before, after: after, label: label });
        if (undoStack.length > HISTORY_LIMIT) { undoStack.shift(); }
        redoStack.length = 0;
        lastAction = label;
        updateHistoryUi();
        updateHidden();
    }
    function undo() {
        if (!undoStack.length || resize) { return; }
        const entry = undoStack.pop();
        redoStack.push(entry);
        state = normalizeModel(clone(entry.before));
        if (selectedId && !nodeById(selectedId)) { selectedId = ''; }
        lastAction = 'Fortryd: ' + entry.label;
        render();
        diag('undo', { label: entry.label, state: structuralSummary() });
    }
    function redo() {
        if (!redoStack.length || resize) { return; }
        const entry = redoStack.pop();
        undoStack.push(entry);
        state = normalizeModel(clone(entry.after));
        if (selectedId && !nodeById(selectedId)) { selectedId = ''; }
        lastAction = 'Gentag: ' + entry.label;
        render();
        diag('redo', { label: entry.label, state: structuralSummary() });
    }

    function nextOrder(parentId) {
        const list = children(parentId);
        return list.length ? list[list.length - 1].order + 10 : 10;
    }
    function defaultWidth(type, parentId) {
        if (String(type || '').toLowerCase() === 'section') { return UNITS; }
        return parentId ? UNITS : Math.min(60, UNITS);
    }
    function nextFreeY(parentId) {
        let bottom = 0;
        children(parentId).forEach(function (node) {
            const g = node.geometry.desktop;
            bottom = Math.max(bottom, g.y + (g.h > 0 ? g.h : MIN_SPLIT_H));
        });
        return bottom;
    }

    function nodeDepth(node) {
        let depth = 0;
        let cursor = node;
        const seen = {};
        while (cursor && cursor.parentId && !seen[cursor.id]) {
            seen[cursor.id] = true;
            depth += 1;
            cursor = nodeById(cursor.parentId);
        }
        return depth;
    }

    function materializeNaturalLeafHeights() {
        const changed = new Set();
        document.querySelectorAll('.h18-clean-node[data-node-id]').forEach(function (card) {
            const node = nodeById(card.getAttribute('data-node-id') || '');
            if (!node || PARENT_TYPES.includes(node.type) || node.geometry.desktop.h > 0) { return; }
            const rect = card.getBoundingClientRect();
            const rows = Math.max(1, Math.ceil((Math.max(1, rect.height) + Math.max(0, parseInt(node.props.gapY || 0, 10) || 0)) / ROW_PX));
            node.geometry.desktop.h = rows;
            changed.add(node.id);
        });
        return changed;
    }

    function healMaterializationCollisions(materialized) {
        if (!materialized || !materialized.size) { return false; }
        let changed = false;
        const parents = Array.from(new Set(state.nodes.map(function (node) { return node.parentId; })));
        parents.forEach(function (parentId) {
            const list = children(parentId).slice().sort(function (a, b) {
                if (a.geometry.desktop.y !== b.geometry.desktop.y) { return a.geometry.desktop.y - b.geometry.desktop.y; }
                return a.order - b.order;
            });
            const placed = [];
            list.forEach(function (node) {
                const g = node.geometry.desktop;
                if (!materialized.has(node.id) && !placed.some(function (other) { return materialized.has(other.id); })) {
                    placed.push(node);
                    return;
                }
                let guard = 0;
                while (guard++ < 100) {
                    const current = { x: g.x, y: g.y, w: g.w, h: Math.max(1, g.h || MIN_SPLIT_H) };
                    let nextY = current.y;
                    placed.forEach(function (other) {
                        const og = other.geometry.desktop;
                        const otherRect = { x: og.x, y: og.y, w: og.w, h: Math.max(1, og.h || MIN_SPLIT_H) };
                        if (rectsOverlap(current, otherRect)) { nextY = Math.max(nextY, otherRect.y + otherRect.h); }
                    });
                    if (nextY === current.y) { break; }
                    g.y = nextY;
                    changed = true;
                }
                placed.push(node);
            });
        });
        return changed;
    }

    function syncContainerHeights() {
        let changed = false;
        const parents = state.nodes.filter(function (node) { return PARENT_TYPES.includes(node.type); });
        parents.sort(function (a, b) { return nodeDepth(b) - nodeDepth(a); });
        parents.forEach(function (parent) {
            const kids = children(parent.id);
            let required = kids.length ? 0 : MIN_SPLIT_H;
            kids.forEach(function (child) {
                const g = child.geometry.desktop;
                required = Math.max(required, Math.max(0, g.y) + Math.max(1, g.h || MIN_SPLIT_H));
            });
            const p = parent.props || {};
            const extraPx = (Math.max(0, parseInt(p.padding || 0, 10) || 0) * 2) + (Math.max(0, parseInt(p.borderWidth || 0, 10) || 0) * 2);
            required += Math.ceil(extraPx / ROW_PX);
            const manualMin = clamp(parseInt(p.minHeightRows || 0, 10) || 0, 0, 4000);
            const next = clamp(Math.max(manualMin, required), 1, 4000);
            if (parent.geometry.desktop.h !== next) {
                parent.geometry.desktop.h = next;
                changed = true;
            }
        });
        return changed;
    }

    function markOverlapWarnings() {
        document.querySelectorAll('.h18-clean-node.has-layout-overlap').forEach(function (card) { card.classList.remove('has-layout-overlap'); });
        const parents = Array.from(new Set(state.nodes.map(function (node) { return node.parentId; })));
        parents.forEach(function (parentId) {
            const list = children(parentId);
            for (let i = 0; i < list.length; i += 1) {
                for (let j = i + 1; j < list.length; j += 1) {
                    // Kasse/Sektion are layout wrappers and do not participate in leaf overlap warnings.
                    if (PARENT_TYPES.includes(list[i].type) || PARENT_TYPES.includes(list[j].type)) { continue; }
                    const a = list[i].geometry.desktop;
                    const b = list[j].geometry.desktop;
                    const ar = { x: a.x, y: a.y, w: a.w, h: Math.max(1, a.h || MIN_SPLIT_H) };
                    const br = { x: b.x, y: b.y, w: b.w, h: Math.max(1, b.h || MIN_SPLIT_H) };
                    if (!rectsOverlap(ar, br)) { continue; }
                    [list[i].id, list[j].id].forEach(function (id) {
                        document.querySelectorAll('.h18-clean-node[data-node-id="' + CSS.escape(id) + '"]').forEach(function (card) {
                            card.classList.add('has-layout-overlap');
                        });
                    });
                }
            }
        });
    }

    function reconcileLayoutAfterRender(canvas) {
        const materialized = materializeNaturalLeafHeights();
        const collisionHealed = healMaterializationCollisions(materialized);
        const containersChanged = syncContainerHeights();
        const changed = materialized.size > 0 || collisionHealed || containersChanged;
        if (changed && canvas) {
            renderSurface('', canvas);
            if (undoStack.length) { undoStack[undoStack.length - 1].after = clone(state); }
        }
        markOverlapWarnings();
        return changed;
    }

    function directDropTarget(event, parentId, movingId, surface) {
        const raw = event && event.target && event.target.closest ? event.target.closest('.h18-clean-node[data-node-id]') : null;
        if (!raw || !surface.contains(raw) || raw.parentElement !== surface) { return null; }
        const id = cleanId(raw.getAttribute('data-node-id') || '');
        const node = nodeById(id);
        if (!node || node.id === cleanId(movingId || '') || node.parentId !== parentId) { return null; }
        return { element: raw, node: node };
    }

    function effectiveRows(card, node) {
        if (node && node.geometry && node.geometry.desktop && node.geometry.desktop.h > 0) {
            return node.geometry.desktop.h;
        }
        if (!card) { return MIN_SPLIT_H; }
        return Math.max(MIN_SPLIT_H, Math.round(card.getBoundingClientRect().height / ROW_PX));
    }

    function visualBand(surface, targetElement, movingId) {
        if (!surface || !targetElement) { return { ids: [], h: MIN_SPLIT_H }; }
        const targetRect = targetElement.getBoundingClientRect();
        const rows = [];
        Array.from(surface.children).forEach(function (card) {
            if (!card.classList || !card.classList.contains('h18-clean-node')) { return; }
            const id = cleanId(card.getAttribute('data-node-id') || '');
            if (!id || id === cleanId(movingId || '')) { return; }
            const node = nodeById(id);
            if (!node) { return; }
            const rect = card.getBoundingClientRect();
            const overlap = Math.min(rect.bottom, targetRect.bottom) - Math.max(rect.top, targetRect.top);
            const sameTop = Math.abs(rect.top - targetRect.top) <= 6;
            if (sameTop || overlap >= Math.min(rect.height, targetRect.height) * 0.65) {
                rows.push({ id: id, left: rect.left, h: effectiveRows(card, node) });
            }
        });
        rows.sort(function (a, b) { return a.left - b.left; });
        let h = MIN_SPLIT_H;
        rows.forEach(function (item) { h = Math.max(h, item.h); });
        return { ids: rows.map(function (item) { return item.id; }), h: h };
    }

    function zoneForTarget(event, target) {
        const rect = target.element.getBoundingClientRect();
        const rx = clamp((event.clientX - rect.left) / Math.max(1, rect.width), 0, 1);
        const ry = clamp((event.clientY - rect.top) / Math.max(1, rect.height), 0, 1);
        if (PARENT_TYPES.includes(target.node.type)) {
            if (ry < 0.22) { return 'above'; }
            if (ry > 0.78) { return 'below'; }
            if (rx < 0.22) { return 'left'; }
            if (rx > 0.78) { return 'right'; }
            return 'inside';
        }
        if (ry < 0.28) { return 'above'; }
        if (ry > 0.72) { return 'below'; }
        return rx < 0.5 ? 'left' : 'right';
    }

    function dropPlacement(surface, event, parentId, width, movingId) {
        width = clamp(parseInt(width || 1, 10) || 1, 1, UNITS);
        const rect = surface.getBoundingClientRect();
        const unitPx = Math.max(1, rect.width / UNITS);
        const pointerUnit = clamp(Math.round((event.clientX - rect.left) / unitPx), 0, UNITS);
        const placement = {
            parentId: parentId,
            x: clamp(Math.round(pointerUnit - (width / 2)), 0, UNITS - width),
            y: nextFreeY(parentId),
            w: width,
            targetId: '',
            zone: parentId ? 'inside-empty' : 'free',
            bandIds: [],
            bandH: MIN_SPLIT_H,
            targetGeometry: null
        };
        const target = directDropTarget(event, parentId, movingId, surface);
        if (!target) {
            if (parentId) { placement.x = 0; placement.w = UNITS; }
            return placement;
        }

        const zone = zoneForTarget(event, target);
        const band = visualBand(surface, target.element, movingId);
        placement.targetId = target.node.id;
        placement.zone = zone;
        placement.bandIds = band.ids;
        placement.bandH = Math.max(MIN_SPLIT_H, band.h);
        placement.targetGeometry = clone(target.node.geometry.desktop);

        if (zone === 'inside' && PARENT_TYPES.includes(target.node.type)) {
            placement.parentId = target.node.id;
            placement.x = 0;
            placement.y = nextFreeY(target.node.id);
            placement.w = UNITS;
            placement.targetId = '';
            placement.bandIds = [];
            placement.targetGeometry = null;
            return placement;
        }
        return placement;
    }

    function reorderForPlacement(movingId, parentId, placement) {
        const moving = nodeById(movingId);
        if (!moving) { return; }
        const list = children(parentId).filter(function (node) { return node.id !== movingId; });
        let index = list.length;
        if (placement.targetId) {
            const targetIndex = list.findIndex(function (n) { return n.id === placement.targetId; });
            if (targetIndex >= 0) {
                index = targetIndex + ((placement.zone === 'right' || placement.zone === 'below') ? 1 : 0);
            }
        }
        list.splice(clamp(index, 0, list.length), 0, moving);
        list.forEach(function (node, i) { node.order = (i + 1) * 10; });
    }

    function materializeBand(placement, targetId) {
        const h = Math.max(MIN_SPLIT_H, parseInt(placement.bandH || MIN_SPLIT_H, 10) || MIN_SPLIT_H);
        const target = nodeById(targetId);
        const targetY = target ? target.geometry.desktop.y : 0;
        (placement.bandIds || []).forEach(function (id) {
            const node = nodeById(id);
            if (!node || node.parentId !== placement.parentId) { return; }
            if (Math.abs(node.geometry.desktop.y - targetY) > 1) { return; }
            if (node.geometry.desktop.h === 0 || node.geometry.desktop.h < h) {
                node.geometry.desktop.h = h;
            }
        });
        if (target && target.geometry.desktop.h === 0) { target.geometry.desktop.h = h; }
        return h;
    }

    function applyCellSplit(movingId, placement) {
        const moving = nodeById(movingId);
        const target = nodeById(placement.targetId);
        if (!moving || !target) { return false; }

        const zone = placement.zone;
        const tg = target.geometry.desktop;
        if (zone === 'left' || zone === 'right') {
            if (tg.w < 2) { return false; }
            const h = materializeBand(placement, target.id);
            const firstW = Math.max(1, Math.floor(tg.w / 2));
            const secondW = Math.max(1, tg.w - firstW);
            const baseX = tg.x;
            const y = tg.y;
            const cellH = Math.max(h, tg.h || h);
            if (zone === 'left') {
                moving.geometry.desktop = normalizeDevice({ x: baseX, y: y, w: firstW, h: cellH }, false);
                target.geometry.desktop.x = baseX + firstW;
                target.geometry.desktop.w = secondW;
                target.geometry.desktop.h = cellH;
            } else {
                target.geometry.desktop.x = baseX;
                target.geometry.desktop.w = firstW;
                target.geometry.desktop.h = cellH;
                moving.geometry.desktop = normalizeDevice({ x: baseX + firstW, y: y, w: secondW, h: cellH }, false);
            }
            return true;
        }

        if (zone === 'above' || zone === 'below') {
            const totalH = Math.max(2, materializeBand(placement, target.id));
            const topH = Math.max(1, Math.floor(totalH / 2));
            const bottomH = Math.max(1, totalH - topH);
            const baseY = tg.y;
            const x = tg.x;
            const w = tg.w;
            if (zone === 'above') {
                moving.geometry.desktop = normalizeDevice({ x: x, y: baseY, w: w, h: topH }, false);
                target.geometry.desktop.y = baseY + topH;
                target.geometry.desktop.h = bottomH;
            } else {
                target.geometry.desktop.y = baseY;
                target.geometry.desktop.h = topH;
                moving.geometry.desktop = normalizeDevice({ x: x, y: baseY + topH, w: w, h: bottomH }, false);
            }
            return true;
        }
        return false;
    }

    function applyDestinationGeometry(movingId, placement) {
        const moving = nodeById(movingId);
        if (!moving) { return; }
        if (placement.targetId && ['left', 'right', 'above', 'below'].includes(placement.zone)) {
            if (applyCellSplit(movingId, placement)) { return; }
        }
        moving.geometry.desktop.x = clamp(parseInt(placement.x || 0, 10) || 0, 0, UNITS - 1);
        moving.geometry.desktop.w = clamp(parseInt(placement.w || moving.geometry.desktop.w, 10) || moving.geometry.desktop.w, 1, UNITS - moving.geometry.desktop.x);
        moving.geometry.desktop.y = clamp(parseInt(placement.y || 0, 10) || 0, -4000, 10000);
        if (moving.geometry.desktop.h < 0) { moving.geometry.desktop.h = 0; }
    }

    function rectsOverlap(a, b) {
        return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
    }

    function healSourceCell(source, movingId) {
        if (!source || !source.geometry || !source.parentId) { return; }
        const g = clone(source.geometry);
        g.h = Math.max(1, g.h || source.effectiveH || MIN_SPLIT_H);
        const siblings = children(source.parentId).filter(function (n) { return n.id !== movingId; });
        const blockers = siblings.filter(function (n) {
            const ng = clone(n.geometry.desktop);
            ng.h = Math.max(1, ng.h || MIN_SPLIT_H);
            return rectsOverlap(ng, g);
        });
        if (blockers.length) { return; }

        const horizontal = siblings.filter(function (n) {
            const ng = n.geometry.desktop;
            const nh = Math.max(1, ng.h || source.effectiveH || MIN_SPLIT_H);
            return ng.y === g.y && nh === g.h && (ng.x + ng.w === g.x || g.x + g.w === ng.x);
        });
        if (horizontal.length === 1) {
            const n = horizontal[0];
            const left = Math.min(n.geometry.desktop.x, g.x);
            const right = Math.max(n.geometry.desktop.x + n.geometry.desktop.w, g.x + g.w);
            n.geometry.desktop.x = left;
            n.geometry.desktop.w = right - left;
            n.geometry.desktop.h = g.h;
            return;
        }

        const vertical = siblings.filter(function (n) {
            const ng = n.geometry.desktop;
            const nh = Math.max(1, ng.h || source.effectiveH || MIN_SPLIT_H);
            return ng.x === g.x && ng.w === g.w && (ng.y + nh === g.y || g.y + g.h === ng.y);
        });
        if (vertical.length === 1) {
            const n = vertical[0];
            const nh = Math.max(1, n.geometry.desktop.h || source.effectiveH || MIN_SPLIT_H);
            const top = Math.min(n.geometry.desktop.y, g.y);
            const bottom = Math.max(n.geometry.desktop.y + nh, g.y + g.h);
            n.geometry.desktop.y = top;
            n.geometry.desktop.h = bottom - top;
        }
    }

    function addNode(type, parentId, source, dropGeometry) {
        type = String(type || '').toLowerCase();
        if (!TYPES.includes(type)) { return; }
        const placement = dropGeometry && typeof dropGeometry === 'object' ? dropGeometry : null;
        parentId = cleanId(placement && placement.parentId != null ? placement.parentId : parentId || '');
        const parent = parentId ? nodeById(parentId) : null;
        if (parentId && (!parent || !PARENT_TYPES.includes(parent.type))) { return; }
        const before = clone(state);
        const id = makeId(type);
        const defaultW = defaultWidth(type, parentId);
        const p = placement || { parentId: parentId, x: 0, y: nextFreeY(parentId), w: defaultW, targetId: '', zone: 'free', bandIds: [], bandH: MIN_SPLIT_H };
        const desktop = normalizeDevice({ x: p.x, y: p.y, w: p.w || defaultW, h: 0 }, false);
        state.nodes.push({
            id: id,
            type: type,
            parentId: parentId,
            order: nextOrder(parentId),
            geometry: {
                desktop: desktop,
                tablet: Object.assign({}, desktop, { inheritDesktop: true }),
                mobile: { x: 0, y: 0, w: 120, h: 0, inheritDesktop: true }
            },
            props: normalizeProps(type, {})
        });
        reorderForPlacement(id, parentId, p);
        applyDestinationGeometry(id, p);
        selectedId = id;
        commit(before, 'Tilføj ' + type + ' · ' + p.zone);
        render();
        diag('cell_drop_commit', { id: id, type: type, operation: 'add', parentId: parentId, dropZone: p.zone, targetId: p.targetId || '', placement: clone(p), state: structuralSummary() });
    }

    function deleteSelected() {
        const node = nodeById(selectedId);
        if (!node) { return; }
        const before = clone(state);
        const remove = new Set([node.id].concat(descendants(node.id)));
        state.nodes = state.nodes.filter(function (candidate) { return !remove.has(candidate.id); });
        selectedId = '';
        commit(before, 'Slet ' + node.type);
        render();
        diag('delete_node', { id: node.id, type: node.type, removedCount: remove.size, state: structuralSummary() });
    }

    function reparent(id, parentId, placement) {
        const node = nodeById(id);
        if (!node) { return; }
        placement = placement && typeof placement === 'object' ? placement : { parentId: parentId, x: 0, y: 0, w: node.geometry.desktop.w, zone: 'free', bandIds: [], bandH: MIN_SPLIT_H };
        parentId = cleanId(placement.parentId != null ? placement.parentId : parentId);
        const parent = parentId ? nodeById(parentId) : null;
        if (parentId && (!parent || !PARENT_TYPES.includes(parent.type))) { return; }
        if (parentId === id || descendants(id).includes(parentId)) { return; }

        const before = clone(state);
        const from = node.parentId;
        const sourceSnapshot = dragSource ? clone(dragSource) : null;
        node.parentId = parentId;
        node.order = nextOrder(parentId);
        if (sourceSnapshot) { healSourceCell(sourceSnapshot, id); }
        reorderForPlacement(id, parentId, placement);
        applyDestinationGeometry(id, placement);
        node.geometry.desktop.w = Math.min(UNITS, Math.max(1, node.geometry.desktop.w));
        commit(before, 'Flyt ' + node.type + ' · ' + placement.zone);
        render();
        diag('cell_drop_commit', { id: id, type: node.type, operation: 'move', fromParentId: from, toParentId: parentId, dropZone: placement.zone, targetId: placement.targetId || '', placement: clone(placement), state: structuralSummary() });
    }

    function applyCardGeometry(card, node, geometry) {
        card.style.gridColumn = String(geometry.x + 1) + ' / span ' + String(geometry.w);
        card.style.marginTop = '0px';
        if (geometry.h > 0) {
            card.style.gridRow = String(Math.max(0, geometry.y) + 1) + ' / span ' + String(geometry.h);
            card.style.height = 'auto';
            card.style.minHeight = String(geometry.h * ROW_PX) + 'px';
            card.setAttribute('data-h18-explicit-grid', '1');
        } else {
            card.style.gridRow = '';
            card.style.height = '';
            card.style.minHeight = '';
            card.removeAttribute('data-h18-explicit-grid');
        }
        card.setAttribute('data-geometry', [geometry.x, geometry.y, geometry.w, geometry.h].join(','));
    }

    function applyVisualStyle(card, node) {
        const props = node && node.props ? node.props : {};
        const borderWidth = clamp(parseInt(props.borderWidth || 0, 10) || 0, 0, 20);
        const gapX = clamp(parseInt(props.gapX || 0, 10) || 0, 0, 200);
        const gapY = clamp(parseInt(props.gapY || 0, 10) || 0, 0, 200);
        card.style.boxSizing = 'border-box';
        card.style.borderStyle = borderWidth > 0 ? 'solid' : 'none';
        card.style.borderWidth = borderWidth + 'px';
        card.style.borderColor = normalizeColor(props.borderColor || '#000000');
        card.style.marginRight = gapX + 'px';
        card.style.marginBottom = gapY + 'px';
        card.setAttribute('data-gap-x', String(gapX));
        card.setAttribute('data-gap-y', String(gapY));
    }

    function makeHandle(direction) {
        const handle = document.createElement('span');
        handle.className = 'h18-clean-resize h18-clean-resize--' + direction;
        handle.setAttribute('data-resize', direction);
        handle.title = 'Resize ' + direction.toUpperCase();
        return handle;
    }

    function cardContent(node) {
        const wrap = document.createElement('div');
        wrap.className = 'h18-clean-node-preview';
        if (node.type === 'text') {
            wrap.classList.add('h18-clean-node-preview--text');
            wrap.style.textAlign = node.props.align || 'left';
            wrap.textContent = String(node.props.text || 'Ny tekst').replace(/<[^>]+>/g, '').slice(0, 220) || 'Tekst';
        } else if (node.type === 'image') {
            wrap.classList.add('h18-clean-node-preview--image');
            if (node.props.url) {
                const img = document.createElement('img');
                img.src = node.props.url;
                img.alt = node.props.alt || '';
                img.style.objectFit = node.props.fit === 'stretch' ? 'fill' : node.props.fit;
                img.style.objectPosition = node.props.focalX + '% ' + node.props.focalY + '%';
                wrap.appendChild(img);
            } else {
                wrap.textContent = 'Vælg billede i Inspector';
            }
        } else {
            wrap.textContent = node.type === 'section' ? 'Sektion' : 'Kasse';
        }
        return wrap;
    }

    function dataTransferValue(event, mime) {
        try { return String(event && event.dataTransfer ? event.dataTransfer.getData(mime) || '' : ''); } catch (ignore) { return ''; }
    }
    function dragPayload(event) {
        const paletteType = dragPaletteType || dataTransferValue(event, 'application/x-h18-clean-palette');
        if (paletteType && TYPES.includes(String(paletteType).toLowerCase())) {
            return { kind: 'palette', type: String(paletteType).toLowerCase() };
        }
        const nodeId = dragId || dataTransferValue(event, 'application/x-h18-clean-node');
        if (nodeId && nodeById(nodeId)) { return { kind: 'node', id: cleanId(nodeId) }; }
        const fallback = dataTransferValue(event, 'text/plain');
        if (fallback.indexOf('h18-palette:') === 0) {
            const type = String(fallback.slice(12)).toLowerCase();
            if (TYPES.includes(type)) { return { kind: 'palette', type: type }; }
        }
        if (fallback.indexOf('h18-node:') === 0) {
            const id = cleanId(fallback.slice(9));
            if (nodeById(id)) { return { kind: 'node', id: id }; }
        }
        return null;
    }

    function clearDropGuide() {
        document.querySelectorAll('.h18-clean-v018-drop-overlay').forEach(function (overlay) { overlay.remove(); });
        document.querySelectorAll('.h18-clean-v018-drop-target,.h18-clean-v018-drop-inside').forEach(function (card) {
            card.classList.remove('h18-clean-v018-drop-target', 'h18-clean-v018-drop-inside');
            card.removeAttribute('data-v018-zone');
        });
        const status = document.getElementById('h18-clean-v018-drop-status');
        if (status) { status.classList.remove('is-visible'); }
    }

    function zoneLabel(zone) {
        return ({ above: '↑ DEL CELLEN OVER', below: '↓ DEL CELLEN UNDER', left: '← DEL CELLEN VENSTRE', right: 'DEL CELLEN HØJRE →', inside: 'IND I KASSEN', 'inside-empty': 'IND I KASSEN', free: 'FRI PLACERING' })[zone] || zone;
    }

    function statusBubble(event, placement) {
        let status = document.getElementById('h18-clean-v018-drop-status');
        if (!status) {
            status = document.createElement('div');
            status.id = 'h18-clean-v018-drop-status';
            status.className = 'h18-clean-v018-drop-status';
            document.body.appendChild(status);
        }
        status.textContent = zoneLabel(placement.zone);
        status.style.left = Math.min(window.innerWidth - 230, event.clientX + 16) + 'px';
        status.style.top = Math.min(window.innerHeight - 48, event.clientY + 16) + 'px';
        status.classList.add('is-visible');
    }

    function showDropGuide(surface, event, placement) {
        clearDropGuide();
        statusBubble(event, placement);
        let card = placement.targetId ? surface.querySelector(':scope > .h18-clean-node[data-node-id="' + CSS.escape(placement.targetId) + '"]') : null;
        if (!card && placement.parentId && surface.classList.contains('h18-clean-inner-surface')) {
            card = surface.closest('.h18-clean-node[data-node-id]');
        }
        if (!card) { return; }
        card.classList.add('h18-clean-v018-drop-target');
        card.setAttribute('data-v018-zone', placement.zone);
        if (placement.zone === 'inside' || placement.zone === 'inside-empty') { card.classList.add('h18-clean-v018-drop-inside'); }

        const targetNode = nodeById(card.getAttribute('data-node-id'));
        const isParent = targetNode && PARENT_TYPES.includes(targetNode.type);
        const overlay = document.createElement('div');
        overlay.className = 'h18-clean-v018-drop-overlay ' + (isParent ? 'is-parent' : 'is-leaf');
        ['above', 'left'].forEach(function (zone) {
            const item = document.createElement('span');
            item.className = 'zone zone-' + zone + (placement.zone === zone ? ' is-active' : '');
            item.textContent = zone === 'above' ? '↑ OVER' : '← VENSTRE';
            overlay.appendChild(item);
        });
        if (isParent) {
            const inside = document.createElement('span');
            inside.className = 'zone zone-inside' + ((placement.zone === 'inside' || placement.zone === 'inside-empty') ? ' is-active' : '');
            inside.textContent = 'IND I';
            overlay.appendChild(inside);
        }
        ['right', 'below'].forEach(function (zone) {
            const item = document.createElement('span');
            item.className = 'zone zone-' + zone + (placement.zone === zone ? ' is-active' : '');
            item.textContent = zone === 'right' ? 'HØJRE →' : '↓ UNDER';
            overlay.appendChild(item);
        });
        card.appendChild(overlay);
    }

    function clearDragState() {
        dragId = '';
        dragPaletteType = '';
        dragSource = null;
        document.querySelectorAll('.is-drop-target,.is-palette-dragging').forEach(function (el) {
            el.classList.remove('is-drop-target', 'is-palette-dragging');
        });
        clearDropGuide();
    }

    function renderSurface(parentId, surface) {
        surface.innerHTML = '';
        surface.setAttribute('data-parent-id', parentId);
        surface.classList.add('h18-clean-surface');
        surface.style.gridAutoRows = ROW_PX + 'px';
        surface.ondragover = function (event) {
            const payload = dragPayload(event);
            if (!payload) { return; }
            event.preventDefault();
            event.stopPropagation();
            if (event.dataTransfer) { event.dataTransfer.dropEffect = payload.kind === 'node' ? 'move' : 'copy'; }
            surface.classList.add('is-drop-target');
            const width = payload.kind === 'node' && nodeById(payload.id) ? nodeById(payload.id).geometry.desktop.w : defaultWidth(payload.type, parentId);
            const placement = dropPlacement(surface, event, parentId, width, payload.kind === 'node' ? payload.id : '');
            showDropGuide(surface, event, placement);
        };
        surface.ondragleave = function (event) {
            const related = event.relatedTarget;
            if (!related || !surface.contains(related)) {
                surface.classList.remove('is-drop-target');
                clearDropGuide();
            }
        };
        surface.ondrop = function (event) {
            const payload = dragPayload(event);
            if (!payload) { return; }
            event.preventDefault();
            event.stopPropagation();
            surface.classList.remove('is-drop-target');
            if (payload.kind === 'palette') {
                const placement = dropPlacement(surface, event, parentId, defaultWidth(payload.type, parentId), '');
                clearDropGuide();
                addNode(payload.type, parentId, 'palette_drop', placement);
                dragPaletteType = '';
                return;
            }
            const movingNode = nodeById(payload.id);
            if (!movingNode) { clearDragState(); return; }
            const placement = dropPlacement(surface, event, parentId, movingNode.geometry.desktop.w, payload.id);
            clearDropGuide();
            reparent(payload.id, parentId, placement);
            dragId = '';
            dragSource = null;
        };

        const list = children(parentId);
        if (!list.length) {
            const empty = document.createElement('div');
            empty.className = 'h18-clean-empty-drop';
            empty.textContent = parentId ? 'Slip her for at lægge elementet ind i denne kasse' : 'Tilføj et element eller træk et element hertil';
            empty.style.gridColumn = '1 / span ' + UNITS;
            surface.appendChild(empty);
        }

        list.forEach(function (node) {
            const card = document.createElement('div');
            card.className = 'h18-clean-node h18-clean-node--' + node.type + (selectedId === node.id ? ' is-selected' : '');
            card.setAttribute('data-node-id', node.id);
            applyCardGeometry(card, node, node.geometry.desktop);
            applyVisualStyle(card, node);

            const header = document.createElement('div');
            header.className = 'h18-clean-node-header';
            const move = document.createElement('button');
            move.type = 'button';
            move.className = 'h18-clean-move';
            move.draggable = true;
            move.title = 'Træk: del celle Over / Under / Venstre / Højre eller læg Ind i Kasse';
            move.textContent = '✥';
            move.addEventListener('dragstart', function (event) {
                dragId = node.id;
                dragPaletteType = '';
                dragSource = {
                    parentId: node.parentId,
                    geometry: clone(node.geometry.desktop),
                    effectiveH: effectiveRows(card, node)
                };
                try {
                    event.dataTransfer.setData('application/x-h18-clean-node', node.id);
                    event.dataTransfer.setData('text/plain', 'h18-node:' + node.id);
                    event.dataTransfer.effectAllowed = 'move';
                } catch (ignore) {}
                card.classList.add('is-dragging');
                diag('reparent_begin', { id: node.id, parentId: node.parentId, sourceCell: clone(dragSource) });
            });
            move.addEventListener('dragend', function () { card.classList.remove('is-dragging'); clearDragState(); });
            const title = document.createElement('strong');
            title.textContent = ({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE'}[node.type] || node.type.toUpperCase()) + ' · ' + node.id.slice(-8);
            header.appendChild(move);
            header.appendChild(title);
            card.appendChild(header);
            card.appendChild(cardContent(node));

            if (PARENT_TYPES.includes(node.type)) {
                const inner = document.createElement('div');
                inner.className = 'h18-clean-surface h18-clean-inner-surface';
                const p = node.props || {};
                inner.style.background = p.background || 'transparent';
                inner.style.borderRadius = (p.radius || 0) + 'px';
                inner.style.padding = (p.padding || 0) + 'px';
                renderSurface(node.id, inner);
                card.appendChild(inner);
            }

            ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'].forEach(function (direction) { card.appendChild(makeHandle(direction)); });
            card.addEventListener('click', function (event) {
                if (event.target.closest('.h18-clean-resize,.h18-clean-move,.h18-clean-v018-drop-overlay')) { return; }
                event.stopPropagation();
                selectedId = node.id;
                render();
            });
            card.querySelectorAll('.h18-clean-resize').forEach(function (handle) {
                handle.addEventListener('pointerdown', function (event) {
                    beginResize(event, node.id, String(handle.getAttribute('data-resize') || ''), card, surface);
                });
            });
            surface.appendChild(card);
        });
    }

    function beginResize(event, id, direction, card, surface) {
        if (event.button !== 0 || resize) { return; }
        const node = nodeById(id);
        if (!node) { return; }
        const rect = card.getBoundingClientRect();
        const g = clone(node.geometry.desktop);
        const startH = g.h > 0 ? g.h : Math.max(1, Math.round(rect.height / ROW_PX));
        resize = {
            id: id, direction: direction, pointerId: event.pointerId, card: card, surface: surface,
            startX: event.clientX, startY: event.clientY, start: g, startH: startH, before: clone(state)
        };
        try { card.setPointerCapture(event.pointerId); } catch (ignore) {}
        card.classList.add('is-resizing');
        diag('resize_begin', { id: id, direction: direction, geometry: g });
        event.preventDefault();
        event.stopPropagation();
    }

    function moveResize(event) {
        if (!resize || event.pointerId !== resize.pointerId) { return; }
        const node = nodeById(resize.id);
        if (!node) { return; }
        const width = Math.max(1, resize.surface.getBoundingClientRect().width);
        const dx = Math.round((event.clientX - resize.startX) / (width / UNITS));
        const dy = Math.round((event.clientY - resize.startY) / ROW_PX);
        const next = clone(resize.start);
        const dir = resize.direction;
        if (dir.includes('e')) { next.w = clamp(resize.start.w + dx, 1, UNITS - resize.start.x); }
        if (dir.includes('w')) {
            const maxDelta = resize.start.w - 1;
            const applied = clamp(dx, -resize.start.x, maxDelta);
            next.x = resize.start.x + applied;
            next.w = resize.start.w - applied;
        }
        if (dir.includes('s')) { next.h = clamp(resize.startH + dy, 1, 4000); }
        if (dir.includes('n')) {
            const appliedY = clamp(dy, -4000 - resize.start.y, resize.startH - 1);
            next.y = resize.start.y + appliedY;
            next.h = resize.startH - appliedY;
        }
        node.geometry.desktop = next;
        applyCardGeometry(resize.card, node, next);
        event.preventDefault();
    }

    function endResize(event, commitChange) {
        if (!resize || (event && event.pointerId !== resize.pointerId)) { return; }
        const current = resize;
        resize = null;
        current.card.classList.remove('is-resizing');
        if (commitChange === false) {
            state = normalizeModel(current.before);
            render();
            return;
        }
        const resizedNode = nodeById(current.id);
        if (resizedNode && PARENT_TYPES.includes(resizedNode.type)) {
            resizedNode.props.minHeightRows = resizedNode.geometry.desktop.h;
        }
        commit(current.before, 'Resize ' + current.id);
        const node = nodeById(current.id);
        diag('resize_commit', { id: current.id, direction: current.direction, geometry: node ? clone(node.geometry.desktop) : null, state: structuralSummary() });
        render();
    }

    function renderInspector() {
        const host = document.getElementById('h18-clean-inspector');
        if (!host) { return; }
        const node = nodeById(selectedId);
        if (!node) { host.innerHTML = '<p class="description">Vælg et element på canvas.</p>'; return; }
        const g = node.geometry.desktop;
        let html = '<div class="h18-clean-inspector-head"><strong>' + escapeHtml(({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE'}[node.type] || node.type.toUpperCase())) + '</strong><code>' + escapeHtml(node.id) + '</code></div>';
        html += '<div class="h18-clean-field-grid"><label>X / 120<input data-field="gx" type="number" min="0" max="119" value="' + g.x + '"></label><label>Bredde / 120<input data-field="gw" type="number" min="1" max="120" value="' + g.w + '"></label><label>Y · 8px<input data-field="gy" type="number" value="' + g.y + '"></label><label>Højde · 8px<input data-field="gh" type="number" min="0" value="' + g.h + '"></label></div>';
        if (node.type === 'text') {
            html += '<label>Tekst<textarea data-field="text" rows="8">' + escapeHtml(node.props.text || '') + '</textarea></label>';
            html += '<label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label>';
        } else if (node.type === 'image') {
            html += '<button type="button" class="button" id="h18-clean-pick-image">Vælg / skift billede</button>';
            html += '<label>Tilpasning<select data-field="fit"><option value="cover"' + (node.props.fit === 'cover' ? ' selected' : '') + '>Fyld kassen · beskær automatisk</option><option value="contain"' + (node.props.fit === 'contain' ? ' selected' : '') + '>Vis hele billedet · behold proportioner</option><option value="stretch"' + (node.props.fit === 'stretch' ? ' selected' : '') + '>Fri bredde/højde · tillad deformation</option></select></label>';
            html += '<div class="h18-clean-field-grid"><label>Fokus X %<input data-field="focalX" type="number" min="0" max="100" value="' + node.props.focalX + '"></label><label>Fokus Y %<input data-field="focalY" type="number" min="0" max="100" value="' + node.props.focalY + '"></label></div>';
            html += '<label>Alt-tekst<input data-field="alt" type="text" value="' + escapeAttr(node.props.alt || '') + '"></label>';
        } else {
            html += '<label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#ffffff') + '"></label>';
            html += '<div class="h18-clean-field-grid"><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 0) + '"></label><label>Padding px<input data-field="padding" type="number" min="0" max="120" value="' + (node.props.padding || 0) + '"></label></div>';
        }
        html += '<div class="h18-clean-v0111-layout-style"><strong>Ramme og afstand</strong><div class="h18-clean-field-grid">';
        html += '<label>Ramme px<input data-field="borderWidth" type="number" min="0" max="20" value="' + (node.props.borderWidth || 0) + '"></label>';
        html += '<label>Rammefarve<input data-field="borderColor" type="color" value="' + escapeAttr(node.props.borderColor || '#000000') + '"></label>';
        html += '<label>Afstand X px<input data-field="gapX" type="number" min="0" max="200" value="' + (node.props.gapX || 0) + '"></label>';
        html += '<label>Afstand Y px<input data-field="gapY" type="number" min="0" max="200" value="' + (node.props.gapY || 0) + '"></label>';
        html += '</div><p class="description">0 = ingen ramme/afstand. X er luft mod næste element til højre; Y er luft mod næste element under.</p></div>';
        html += '<button type="button" class="button button-link-delete" id="h18-clean-delete">Slet element' + (PARENT_TYPES.includes(node.type) ? ' + indhold' : '') + '</button>';
        host.innerHTML = html;

        host.querySelectorAll('[data-field]').forEach(function (control) {
            control.addEventListener('change', function () {
                const current = nodeById(selectedId);
                if (!current) { return; }
                const before = clone(state);
                const field = control.getAttribute('data-field');
                if (field === 'gx') { current.geometry.desktop.x = clamp(parseInt(control.value || 0, 10) || 0, 0, UNITS - 1); current.geometry.desktop.w = Math.min(current.geometry.desktop.w, UNITS - current.geometry.desktop.x); }
                else if (field === 'gw') { current.geometry.desktop.w = clamp(parseInt(control.value || 1, 10) || 1, 1, UNITS - current.geometry.desktop.x); }
                else if (field === 'gy') { current.geometry.desktop.y = clamp(parseInt(control.value || 0, 10) || 0, -4000, 10000); }
                else if (field === 'gh') {
                    current.geometry.desktop.h = clamp(parseInt(control.value || 0, 10) || 0, 0, 4000);
                    if (PARENT_TYPES.includes(current.type)) { current.props.minHeightRows = current.geometry.desktop.h; }
                }
                else if (field === 'text') { current.props.text = String(control.value || ''); }
                else if (field === 'align') { current.props.align = ['left', 'center', 'right'].includes(control.value) ? control.value : 'left'; }
                else if (field === 'fit') { current.props.fit = ['cover', 'contain', 'stretch'].includes(control.value) ? control.value : 'cover'; }
                else if (field === 'focalX') { current.props.focalX = clamp(parseInt(control.value || 50, 10) || 50, 0, 100); }
                else if (field === 'focalY') { current.props.focalY = clamp(parseInt(control.value || 50, 10) || 50, 0, 100); }
                else if (field === 'alt') { current.props.alt = String(control.value || ''); }
                else if (field === 'background') { current.props.background = String(control.value || ''); }
                else if (field === 'radius') { current.props.radius = clamp(parseInt(control.value || 0, 10) || 0, 0, 100); }
                else if (field === 'padding') { current.props.padding = clamp(parseInt(control.value || 0, 10) || 0, 0, 120); }
                else if (field === 'borderWidth') { current.props.borderWidth = clamp(parseInt(control.value || 0, 10) || 0, 0, 20); }
                else if (field === 'borderColor') { current.props.borderColor = normalizeColor(control.value || '#000000'); }
                else if (field === 'gapX') { current.props.gapX = clamp(parseInt(control.value || 0, 10) || 0, 0, 200); }
                else if (field === 'gapY') {
                    const oldGap = clamp(parseInt(current.props.gapY || 0, 10) || 0, 0, 200);
                    const nextGap = clamp(parseInt(control.value || 0, 10) || 0, 0, 200);
                    const oldRows = Math.ceil(oldGap / ROW_PX);
                    const nextRows = Math.ceil(nextGap / ROW_PX);
                    current.props.gapY = nextGap;
                    if (current.geometry.desktop.h > 0) {
                        current.geometry.desktop.h = clamp(current.geometry.desktop.h + (nextRows - oldRows), 1, 4000);
                    }
                }
                commit(before, 'Ændr ' + field + ' på ' + current.type);
                diag('inspector_change', { id: current.id, type: current.type, field: field, state: structuralSummary() });
                render();
            });
        });
        const del = document.getElementById('h18-clean-delete');
        if (del) { del.addEventListener('click', function () { if (window.confirm('Slet det valgte element?')) { deleteSelected(); } }); }
        const pick = document.getElementById('h18-clean-pick-image');
        if (pick) { pick.addEventListener('click', pickImage); }
    }

    function pickImage() {
        const node = nodeById(selectedId);
        if (!node || node.type !== 'image' || !window.wp || !wp.media) { return; }
        const frame = wp.media({ title: 'Vælg billede', button: { text: 'Brug billede' }, multiple: false, library: { type: 'image' } });
        frame.on('select', function () {
            const attachment = frame.state().get('selection').first().toJSON();
            const current = nodeById(selectedId);
            if (!current) { return; }
            const before = clone(state);
            current.props.mediaId = parseInt(attachment.id || 0, 10) || 0;
            current.props.url = String(attachment.url || '');
            current.props.alt = String(attachment.alt || current.props.alt || '');
            commit(before, 'Vælg billede');
            diag('image_selected', { id: current.id, mediaId: current.props.mediaId, fit: current.props.fit, state: structuralSummary() });
            render();
        });
        frame.open();
    }

    function escapeHtml(value) {
        return String(value == null ? '' : value).replace(/[&<>"']/g, function (c) {
            return ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[c];
        });
    }
    function escapeAttr(value) { return escapeHtml(value); }

    function render() {
        state = normalizeModel(state);
        const canvas = document.getElementById('h18-clean-canvas');
        if (canvas) {
            renderSurface('', canvas);
            reconcileLayoutAfterRender(canvas);
        }
        renderInspector();
        updateHidden();
        updateHistoryUi();
    }

    function install() {
        document.querySelectorAll('.h18-clean-add').forEach(function (button) {
            const type = String(button.getAttribute('data-type') || 'text').toLowerCase();
            button.draggable = true;
            button.setAttribute('aria-grabbed', 'false');
            button.title = 'Klik: tilføj på root · Træk: del celle eller læg Ind i Kasse';
            button.addEventListener('click', function () { addNode(type, '', 'palette_click'); });
            button.addEventListener('dragstart', function (event) {
                dragPaletteType = type;
                dragId = '';
                dragSource = null;
                button.classList.add('is-palette-dragging');
                button.setAttribute('aria-grabbed', 'true');
                try {
                    event.dataTransfer.setData('application/x-h18-clean-palette', type);
                    event.dataTransfer.setData('text/plain', 'h18-palette:' + type);
                    event.dataTransfer.effectAllowed = 'copy';
                } catch (ignore) {}
                diag('palette_drag_begin', { type: type });
            });
            button.addEventListener('dragend', function () {
                button.setAttribute('aria-grabbed', 'false');
                clearDragState();
            });
        });

        const undoButton = document.getElementById('h18-clean-undo');
        const redoButton = document.getElementById('h18-clean-redo');
        if (undoButton) { undoButton.addEventListener('click', undo); }
        if (redoButton) { redoButton.addEventListener('click', redo); }
        document.addEventListener('keydown', function (event) {
            const key = String(event.key || '').toLowerCase();
            if (!(event.ctrlKey || event.metaKey)) { return; }
            if (key === 'z' && event.shiftKey) { event.preventDefault(); redo(); }
            else if (key === 'z') { event.preventDefault(); undo(); }
            else if (key === 'y') { event.preventDefault(); redo(); }
        });
        document.addEventListener('pointermove', moveResize, true);
        document.addEventListener('pointerup', function (event) { endResize(event, true); }, true);
        document.addEventListener('pointercancel', function (event) { endResize(event, false); }, true);
        document.addEventListener('keydown', function (event) { if (event.key === 'Escape' && resize) { endResize(null, false); } }, true);

        const form = document.getElementById('h18-clean-save-form');
        if (form) {
            form.addEventListener('submit', function () {
                updateHidden();
                const note = document.getElementById('h18-clean-change-note');
                if (note && !note.value) { note.value = lastAction || 'Gem clean layout'; }
                diag('save_client_intent', { state: structuralSummary(), lastAction: lastAction });
            }, true);
        }
        document.querySelectorAll('.h18-clean-restore-form').forEach(function (restoreForm) {
            restoreForm.addEventListener('submit', function () {
                const version = restoreForm.querySelector('[name="version"]');
                diag('restore_client_intent', { targetVersion: parseInt(version && version.value || 0, 10) || 0, state: structuralSummary() });
            }, true);
        });
        const copy = document.getElementById('h18-clean-copy-diag');
        if (copy) {
            copy.addEventListener('click', function () {
                const url = String(copy.getAttribute('data-url') || '');
                if (navigator.clipboard && url) {
                    navigator.clipboard.writeText(url).then(function () {
                        const old = copy.textContent;
                        copy.textContent = 'Link kopieret';
                        setTimeout(function () { copy.textContent = old; }, 1200);
                    });
                }
            });
        }
        render();
        diag('editor_boot', { version: CFG.version || '', layoutMode: 'cell-split-grid', state: structuralSummary() });
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());