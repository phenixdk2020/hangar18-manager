from pathlib import Path

path = Path('clean/hangar18-manager/assets/editor.js')
text = path.read_text(encoding='utf-8')

old = """    function nextOrder(parentId) {
        const list = children(parentId);
        return list.length ? list[list.length - 1].order + 10 : 10;
    }
    function addNode(type, parentId, source) {
        type = String(type || '').toLowerCase();
        if (!TYPES.includes(type)) { return; }
        parentId = cleanId(parentId || '');
        const parent = parentId ? nodeById(parentId) : null;
        if (parentId && (!parent || !PARENT_TYPES.includes(parent.type))) { return; }
        const before = clone(state);
        const id = makeId(type);
        const defaultW = type === 'section' ? 120 : 60;
        state.nodes.push({
            id: id, type: type, parentId: parentId, order: nextOrder(parentId),
            geometry: { desktop: { x: 0, y: 0, w: defaultW, h: 0 }, tablet: { x: 0, y: 0, w: defaultW, h: 0, inheritDesktop: true }, mobile: { x: 0, y: 0, w: 120, h: 0, inheritDesktop: true } },
            props: normalizeProps(type, {})
        });
        selectedId = id;
        commit(before, 'Tilføj ' + type + (parentId ? ' i ' + parent.type : ' på root'));
        render();
        diag('add_node', { id: id, type: type, parentId: parentId, source: String(source || 'click'), state: structuralSummary() });
    }
"""
new = """    function nextOrder(parentId) {
        const list = children(parentId);
        return list.length ? list[list.length - 1].order + 10 : 10;
    }
    function defaultWidth(type) {
        return String(type || '').toLowerCase() === 'section' ? UNITS : Math.min(60, UNITS);
    }
    function directDropTarget(event, parentId, movingId, surface) {
        const raw = event && event.target && event.target.closest ? event.target.closest('.h18-clean-node[data-node-id]') : null;
        if (!raw || !surface.contains(raw)) { return null; }
        const id = cleanId(raw.getAttribute('data-node-id') || '');
        const node = nodeById(id);
        if (!node || node.id === cleanId(movingId || '') || node.parentId !== parentId) { return null; }
        return { element: raw, node: node };
    }
    function dropPlacement(surface, event, parentId, width, movingId) {
        width = clamp(parseInt(width || 1, 10) || 1, 1, UNITS);
        const rect = surface.getBoundingClientRect();
        const unitPx = Math.max(1, rect.width / UNITS);
        const pointerUnit = clamp(Math.round((event.clientX - rect.left) / unitPx), 0, UNITS);
        const placement = {
            x: clamp(Math.round(pointerUnit - (width / 2)), 0, UNITS - width),
            y: 0,
            w: width,
            targetId: '',
            targetX: null,
            side: 'free'
        };
        const target = directDropTarget(event, parentId, movingId, surface);
        if (!target) { return placement; }

        const targetRect = target.element.getBoundingClientRect();
        const targetGeometry = target.node.geometry.desktop;
        const side = event.clientX < (targetRect.left + targetRect.width / 2) ? 'left' : 'right';
        placement.targetId = target.node.id;
        placement.side = side;
        placement.y = targetGeometry.y;

        const pairWidth = width + targetGeometry.w;
        if (pairWidth <= UNITS) {
            if (side === 'left') {
                const pairStart = clamp(targetGeometry.x - width, 0, UNITS - pairWidth);
                placement.x = pairStart;
                placement.targetX = pairStart + width;
            } else {
                const pairStart = clamp(targetGeometry.x, 0, UNITS - pairWidth);
                placement.targetX = pairStart;
                placement.x = pairStart + targetGeometry.w;
            }
        }
        return placement;
    }
    function applyPlacementTargetShift(placement, movingId) {
        if (!placement || !placement.targetId || placement.targetX === null) { return; }
        const target = nodeById(placement.targetId);
        if (!target || target.id === cleanId(movingId || '')) { return; }
        target.geometry.desktop.x = clamp(parseInt(placement.targetX || 0, 10) || 0, 0, UNITS - target.geometry.desktop.w);
        target.geometry.desktop.y = clamp(parseInt(placement.y || 0, 10) || 0, -4000, 10000);
    }
    function reorderAroundTarget(movingId, parentId, targetId, side) {
        movingId = cleanId(movingId);
        targetId = cleanId(targetId);
        if (!movingId || !targetId || !['left', 'right'].includes(side)) { return; }
        const moving = nodeById(movingId);
        if (!moving) { return; }
        const list = children(parentId).filter(function (node) { return node.id !== movingId; });
        const targetIndex = list.findIndex(function (node) { return node.id === targetId; });
        if (targetIndex < 0) { return; }
        list.splice(side === 'left' ? targetIndex : targetIndex + 1, 0, moving);
        list.forEach(function (node, index) { node.order = (index + 1) * 10; });
    }
    function addNode(type, parentId, source, dropGeometry) {
        type = String(type || '').toLowerCase();
        if (!TYPES.includes(type)) { return; }
        parentId = cleanId(parentId || '');
        const parent = parentId ? nodeById(parentId) : null;
        if (parentId && (!parent || !PARENT_TYPES.includes(parent.type))) { return; }
        const before = clone(state);
        const id = makeId(type);
        const defaultW = defaultWidth(type);
        const placement = dropGeometry && typeof dropGeometry === 'object' ? dropGeometry : { x: 0, y: 0, w: defaultW, targetId: '', targetX: null, side: 'free' };
        const desktop = normalizeDevice({ x: placement.x, y: placement.y, w: placement.w || defaultW, h: 0 }, false);
        state.nodes.push({
            id: id, type: type, parentId: parentId, order: nextOrder(parentId),
            geometry: { desktop: desktop, tablet: Object.assign({}, desktop, { inheritDesktop: true }), mobile: { x: 0, y: 0, w: 120, h: 0, inheritDesktop: true } },
            props: normalizeProps(type, {})
        });
        applyPlacementTargetShift(placement, id);
        reorderAroundTarget(id, parentId, placement.targetId || '', placement.side || 'free');
        selectedId = id;
        commit(before, 'Tilføj ' + type + (parentId ? ' i ' + parent.type : ' på root'));
        render();
        diag('add_node', { id: id, type: type, parentId: parentId, source: String(source || 'click'), placement: clone(placement), state: structuralSummary() });
    }
"""
if old not in text:
    raise SystemExit('addNode anchor not found')
text = text.replace(old, new, 1)

old = """    function reparent(id, parentId) {
        const node = nodeById(id);
        if (!node) { return; }
        parentId = cleanId(parentId);
        const parent = parentId ? nodeById(parentId) : null;
        if (parentId && (!parent || !PARENT_TYPES.includes(parent.type))) { return; }
        if (parentId === id || descendants(id).includes(parentId)) { return; }
        if (node.parentId === parentId) { return; }
        const before = clone(state);
        const from = node.parentId;
        node.parentId = parentId;
        node.order = nextOrder(parentId);
        node.geometry.desktop.x = 0;
        node.geometry.desktop.w = Math.min(UNITS, Math.max(1, node.geometry.desktop.w));
        commit(before, 'Flyt ' + node.type + (parentId ? ' ind i kasse' : ' ud til root'));
        render();
        diag('reparent_commit', { id: id, fromParentId: from, toParentId: parentId, state: structuralSummary() });
    }
"""
new = """    function reparent(id, parentId, dropGeometry) {
        const node = nodeById(id);
        if (!node) { return; }
        parentId = cleanId(parentId);
        const parent = parentId ? nodeById(parentId) : null;
        if (parentId && (!parent || !PARENT_TYPES.includes(parent.type))) { return; }
        if (parentId === id || descendants(id).includes(parentId)) { return; }
        const placement = dropGeometry && typeof dropGeometry === 'object' ? dropGeometry : null;
        if (node.parentId === parentId && !placement) { return; }
        const before = clone(state);
        const from = node.parentId;
        if (node.parentId !== parentId) {
            node.parentId = parentId;
            node.order = nextOrder(parentId);
        }
        if (placement) {
            applyPlacementTargetShift(placement, id);
            node.geometry.desktop.x = clamp(parseInt(placement.x || 0, 10) || 0, 0, UNITS - node.geometry.desktop.w);
            node.geometry.desktop.y = clamp(parseInt(placement.y || 0, 10) || 0, -4000, 10000);
            reorderAroundTarget(id, parentId, placement.targetId || '', placement.side || 'free');
        } else {
            node.geometry.desktop.x = 0;
        }
        node.geometry.desktop.w = Math.min(UNITS, Math.max(1, node.geometry.desktop.w));
        commit(before, 'Flyt ' + node.type + (parentId ? ' ind/omplacer i kasse' : ' ud/omplacer på root'));
        render();
        diag('reparent_commit', { id: id, fromParentId: from, toParentId: parentId, placement: placement ? clone(placement) : null, state: structuralSummary() });
    }
"""
if old not in text:
    raise SystemExit('reparent anchor not found')
text = text.replace(old, new, 1)

old = """        surface.addEventListener('dragover', function (event) {
            const payload = dragPayload(event);
            if (!payload) { return; }
            event.preventDefault();
            event.stopPropagation();
            if (event.dataTransfer) { event.dataTransfer.dropEffect = payload.kind === 'node' ? 'move' : 'copy'; }
            surface.classList.add('is-drop-target');
        });
        surface.addEventListener('dragleave', function (event) {
            const related = event.relatedTarget;
            if (!related || !surface.contains(related)) { surface.classList.remove('is-drop-target'); }
        });
        surface.addEventListener('drop', function (event) {
            const payload = dragPayload(event);
            if (!payload) { return; }
            event.preventDefault();
            event.stopPropagation();
            surface.classList.remove('is-drop-target');
            if (payload.kind === 'palette') {
                const type = payload.type;
                clearDragState();
                addNode(type, parentId, 'palette_drop');
                diag('palette_drop_commit', { type: type, parentId: parentId, state: structuralSummary() });
                return;
            }
            const moving = payload.id;
            clearDragState();
            reparent(moving, parentId);
        });
"""
new = """        surface.ondragover = function (event) {
            const payload = dragPayload(event);
            if (!payload) { return; }
            event.preventDefault();
            event.stopPropagation();
            if (event.dataTransfer) { event.dataTransfer.dropEffect = payload.kind === 'node' ? 'move' : 'copy'; }
            surface.classList.add('is-drop-target');
        };
        surface.ondragleave = function (event) {
            const related = event.relatedTarget;
            if (!related || !surface.contains(related)) { surface.classList.remove('is-drop-target'); }
        };
        surface.ondrop = function (event) {
            const payload = dragPayload(event);
            if (!payload) { return; }
            event.preventDefault();
            event.stopPropagation();
            surface.classList.remove('is-drop-target');
            if (payload.kind === 'palette') {
                const type = payload.type;
                const placement = dropPlacement(surface, event, parentId, defaultWidth(type), '');
                clearDragState();
                addNode(type, parentId, 'palette_drop', placement);
                diag('palette_drop_commit', { type: type, parentId: parentId, placement: clone(placement), state: structuralSummary() });
                return;
            }
            const moving = payload.id;
            const movingNode = nodeById(moving);
            if (!movingNode) { clearDragState(); return; }
            const placement = dropPlacement(surface, event, parentId, movingNode.geometry.desktop.w, moving);
            clearDragState();
            reparent(moving, parentId, placement);
        };
"""
if old not in text:
    raise SystemExit('surface listener anchor not found')
text = text.replace(old, new, 1)

path.write_text(text, encoding='utf-8')

main = Path('clean/hangar18-manager/hangar18-manager.php')
data = main.read_text(encoding='utf-8')
data = data.replace('Version: 0.1.2', 'Version: 0.1.3').replace("H18_CLEAN_VERSION', '0.1.2'", "H18_CLEAN_VERSION', '0.1.3'")
main.write_text(data, encoding='utf-8')

readme = Path('clean/hangar18-manager/readme.txt')
if readme.exists():
    data = readme.read_text(encoding='utf-8').replace('Version: 0.1.0', 'Version: 0.1.3')
    if '== 0.1.3 ==' not in data:
        data += '\n== 0.1.3 ==\n* Drop placeres fysisk venstre/højre efter pointer og nabo.\n* Eksisterende element kan omplaceres inden for samme Kasse.\n* Root/surface drop-handlers bindes kun én gang og duplikerer ikke elementer efter Undo/Redo.\n'
    readme.write_text(data, encoding='utf-8')
