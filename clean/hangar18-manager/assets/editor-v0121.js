(function () {
    'use strict';

    var CFG = window.H18CleanEditor || {};
    var UNITS = Math.max(12, parseInt(CFG.units || 120, 10) || 120);
    var ROW_PX = Math.max(2, parseInt(CFG.rowPx || 8, 10) || 8);
    var DEVICES = ['desktop', 'laptop', 'mobile'];
    var activeDevice = 'desktop';
    var responsive = Object.create(null);
    var undo = [];
    var redo = [];
    var transform = null;
    var scheduled = false;
    var initial = Object.create(null);

    (Array.isArray(CFG.initialModel && CFG.initialModel.nodes) ? CFG.initialModel.nodes : []).forEach(function (node) {
        if (node && node.id) { initial[String(node.id)] = JSON.parse(JSON.stringify(node)); }
    });

    function clone(value) { return JSON.parse(JSON.stringify(value)); }
    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
    function n(value, fallback) {
        var parsed = parseInt(value, 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }
    function readModel() {
        var field = document.getElementById('h18-clean-model-json');
        if (!field) { return { nodes: [] }; }
        try {
            var model = JSON.parse(field.value || '{}');
            return model && typeof model === 'object' ? model : { nodes: [] };
        } catch (ignore) { return { nodes: [] }; }
    }
    function nodeMap(model) {
        var map = Object.create(null);
        (Array.isArray(model && model.nodes) ? model.nodes : []).forEach(function (node) {
            if (node && node.id) { map[String(node.id)] = node; }
        });
        return map;
    }
    function normalizeGeometry(raw, fallback, responsiveFlag) {
        fallback = fallback || { x: 0, y: 0, w: UNITS, h: 0 };
        raw = raw && typeof raw === 'object' ? raw : {};
        var x = clamp(n(raw.x, fallback.x), 0, UNITS - 1);
        var w = clamp(n(raw.w, fallback.w), 1, UNITS - x);
        var result = {
            x: x,
            y: clamp(n(raw.y, fallback.y), -4000, 10000),
            w: w,
            h: clamp(n(raw.h, fallback.h), 0, 4000)
        };
        if (responsiveFlag) { result.inheritDesktop = raw.inheritDesktop !== false; }
        return result;
    }
    function ensureResponsive(model) {
        var map = nodeMap(model);
        Object.keys(responsive).forEach(function (id) {
            if (!map[id]) { delete responsive[id]; }
        });
        Object.keys(map).forEach(function (id) {
            var node = map[id];
            var source = initial[id] || node;
            var desktop = normalizeGeometry(node.geometry && node.geometry.desktop, null, false);
            if (!responsive[id]) {
                var laptopRaw = source.geometry && source.geometry.laptop;
                var mobileRaw = source.geometry && source.geometry.mobile;
                responsive[id] = {
                    laptop: normalizeGeometry(laptopRaw, desktop, true),
                    mobile: normalizeGeometry(mobileRaw, desktop, true)
                };
                if (!laptopRaw) { responsive[id].laptop.inheritDesktop = true; }
                if (!mobileRaw) { responsive[id].mobile.inheritDesktop = true; }
            }
        });
        return map;
    }
    function effective(node, device) {
        var desktop = normalizeGeometry(node && node.geometry && node.geometry.desktop, null, false);
        if (device === 'desktop') { return desktop; }
        var state = responsive[String(node.id)] || {};
        var laptop = state.laptop || normalizeGeometry(null, desktop, true);
        var effectiveLaptop = laptop.inheritDesktop !== false ? desktop : normalizeGeometry(laptop, desktop, false);
        if (device === 'laptop') { return effectiveLaptop; }
        var mobile = state.mobile || normalizeGeometry(null, effectiveLaptop, true);
        return mobile.inheritDesktop !== false ? effectiveLaptop : normalizeGeometry(mobile, effectiveLaptop, false);
    }
    function ownGeometry(node, device) {
        if (device === 'desktop') { return node.geometry.desktop; }
        ensureResponsive(readModel());
        return responsive[String(node.id)][device];
    }
    function ensureOverride(node, device) {
        if (device === 'desktop') { return node.geometry.desktop; }
        var id = String(node.id);
        if (!responsive[id]) { ensureResponsive(readModel()); }
        var current = responsive[id][device];
        if (current.inheritDesktop !== false) {
            var resolved = effective(node, device);
            responsive[id][device] = Object.assign({}, resolved, { inheritDesktop: false });
        }
        return responsive[id][device];
    }
    function mergeResponsive() {
        if (window.H18CleanV0120 && typeof window.H18CleanV0120.sync === 'function') {
            window.H18CleanV0120.sync();
        }
        var field = document.getElementById('h18-clean-model-json');
        if (!field) { return null; }
        var model = readModel();
        var map = ensureResponsive(model);
        Object.keys(map).forEach(function (id) {
            var node = map[id];
            node.geometry = node.geometry || {};
            node.geometry.laptop = clone(responsive[id].laptop);
            node.geometry.mobile = clone(responsive[id].mobile);
        });
        field.value = JSON.stringify(model);
        return model;
    }
    window.H18CleanResponsive = { sync: mergeResponsive, device: function () { return activeDevice; } };

    function isFloatingButton(node) { return !!(node && node.type === 'button' && node.props && node.props.placementMode === 'overlay'); }
    function children(parentId, map) {
        return Object.keys(map).map(function (id) { return map[id]; }).filter(function (node) {
            return String(node.parentId || '') === String(parentId || '');
        });
    }
    function rowsFor(id, device, map, seen) {
        var node = map[id];
        if (!node || seen[id]) { return 1; }
        seen = Object.assign({}, seen); seen[id] = true;
        var g = effective(node, device);
        var type = String(node.type || '');
        var base = g.h > 0 ? g.h : ((type === 'text' || type === 'image') ? 10 : 8);
        if (type !== 'section' && type !== 'container') { return Math.max(1, base); }
        var required = 0;
        children(id, map).forEach(function (child) {
            if (isFloatingButton(child)) { return; }
            var cg = effective(child, device);
            required = Math.max(required, Math.max(0, cg.y) + rowsFor(String(child.id), device, map, seen));
        });
        var props = node.props || {};
        required += Math.ceil(((Math.max(0, n(props.padding, 0)) * 2) + (Math.max(0, n(props.borderWidth, 0)) * 2)) / ROW_PX);
        return Math.max(1, base, required);
    }
    function applyGeometry(card, g, rows, node) {
        if (isFloatingButton(node)) {
            card.style.position = 'absolute';
            card.style.gridColumn = 'auto';
            card.style.gridRow = 'auto';
            card.style.left = ((g.x / UNITS) * 100) + '%';
            card.style.top = String(Math.max(0, g.y) * ROW_PX) + 'px';
            card.style.width = ((g.w / UNITS) * 100) + '%';
            card.style.height = String(Math.max(1, rows) * ROW_PX) + 'px';
            card.style.minHeight = String(Math.max(1, rows) * ROW_PX) + 'px';
            card.style.zIndex = String(clamp(n(node.props && node.props.zIndex, 20), 1, 200));
        } else {
            card.style.position = 'relative';
            card.style.left = '';
            card.style.top = '';
            card.style.width = '';
            card.style.height = '';
            card.style.zIndex = '';
            card.style.gridColumn = String(g.x + 1) + ' / span ' + String(g.w);
            card.style.gridRow = String(Math.max(0, g.y) + 1) + ' / span ' + String(Math.max(1, rows));
            card.style.minHeight = String(Math.max(1, rows) * ROW_PX) + 'px';
        }
        card.style.marginTop = '0px';
        card.setAttribute('data-h18-active-geometry', [g.x, g.y, g.w, g.h].join(','));
    }
    function applyCanvas() {
        var model = readModel();
        var map = ensureResponsive(model);
        var root = document.getElementById('h18-clean-canvas');
        if (!root) { return; }
        root.setAttribute('data-h18-device', activeDevice);
        document.body.setAttribute('data-h18-clean-device', activeDevice);
        root.querySelectorAll('.h18-clean-node[data-node-id]').forEach(function (card) {
            var id = String(card.getAttribute('data-node-id') || '');
            var node = map[id];
            if (!node) { return; }
            applyGeometry(card, effective(node, activeDevice), rowsFor(id, activeDevice, map, {}), node);
            var move = card.querySelector(':scope > .h18-clean-node-header .h18-clean-move');
            if (move) {
                move.draggable = activeDevice === 'desktop';
                move.title = activeDevice === 'desktop'
                    ? 'Træk: flyt/del layout'
                    : 'Træk: flyt elementet i ' + labelDevice(activeDevice) + '-layoutet';
            }
        });
        injectInspector(map);
        updateButtons();
    }
    function labelDevice(device) {
        return ({ desktop: 'Desktop', laptop: 'Laptop', mobile: 'Mobil' })[device] || device;
    }

    function installToolbar() {
        var toolbar = document.querySelector('.h18-clean-toolbar');
        if (!toolbar || document.getElementById('h18-clean-device-switcher')) { return; }
        var switcher = document.createElement('div');
        switcher.id = 'h18-clean-device-switcher';
        switcher.className = 'h18-clean-device-switcher';
        DEVICES.forEach(function (device) {
            var button = document.createElement('button');
            button.type = 'button';
            button.className = 'button h18-clean-device-button';
            button.setAttribute('data-device', device);
            button.textContent = labelDevice(device);
            button.addEventListener('click', function () {
                mergeResponsive();
                activeDevice = device;
                transform = null;
                scheduleApply();
            });
            switcher.appendChild(button);
        });
        var gridLabel = toolbar.querySelector('.h18-clean-grid-label');
        toolbar.insertBefore(switcher, gridLabel || toolbar.firstChild);
    }

    function injectInspector(map) {
        var host = document.getElementById('h18-clean-inspector');
        if (!host) { return; }
        var coreGrid = host.querySelector('.h18-clean-inspector-head + .h18-clean-field-grid');
        if (coreGrid) { coreGrid.classList.toggle('h18-clean-core-geometry-hidden', activeDevice !== 'desktop'); }
        var old = host.querySelector('.h18-clean-responsive-panel');
        if (activeDevice === 'desktop') { if (old) { old.remove(); } return; }

        var card = document.querySelector('.h18-clean-node.is-selected[data-node-id]');
        if (!card) { if (old) { old.remove(); } return; }
        var id = String(card.getAttribute('data-node-id') || '');
        var node = map[id];
        if (!node) { return; }
        if (old) { old.remove(); }

        var own = ownGeometry(node, activeDevice);
        var resolved = effective(node, activeDevice);
        var inherited = own.inheritDesktop !== false;
        var panel = document.createElement('div');
        panel.className = 'h18-clean-responsive-panel';
        panel.innerHTML = '<div class="h18-clean-responsive-panel-head"><strong>' + labelDevice(activeDevice) + ' layout</strong><span class="h18-clean-responsive-state">' + (inherited ? 'Arver' : 'Egen layout') + '</span></div>'
            + '<label class="h18-clean-checkbox"><input type="checkbox" data-responsive-field="inherit"' + (inherited ? ' checked' : '') + '> Arv fra ' + (activeDevice === 'mobile' ? 'Laptop/Desktop' : 'Desktop') + '</label>'
            + '<div class="h18-clean-field-grid">'
            + '<label>X / 120<input type="number" data-responsive-field="x" min="0" max="119" value="' + resolved.x + '"' + (inherited ? ' disabled' : '') + '></label>'
            + '<label>Bredde / 120<input type="number" data-responsive-field="w" min="1" max="120" value="' + resolved.w + '"' + (inherited ? ' disabled' : '') + '></label>'
            + '<label>Y · 8px<input type="number" data-responsive-field="y" value="' + resolved.y + '"' + (inherited ? ' disabled' : '') + '></label>'
            + '<label>Højde · 8px<input type="number" data-responsive-field="h" min="0" value="' + resolved.h + '"' + (inherited ? ' disabled' : '') + '></label>'
            + '</div>'
            + '<p class="description">Når arv er slået til, følger elementet automatisk det større breakpoint. Flyt eller resize elementet for automatisk at oprette et lokalt override.</p>';
        var head = host.querySelector('.h18-clean-inspector-head');
        if (head) { head.insertAdjacentElement('afterend', panel); } else { host.prepend(panel); }

        panel.querySelectorAll('[data-responsive-field]').forEach(function (control) {
            control.addEventListener('change', function () {
                var before = clone(responsive);
                var field = String(control.getAttribute('data-responsive-field') || '');
                if (field === 'inherit') {
                    responsive[id][activeDevice].inheritDesktop = !!control.checked;
                } else {
                    var g = ensureOverride(node, activeDevice);
                    if (field === 'x') { g.x = clamp(n(control.value, g.x), 0, UNITS - 1); g.w = Math.min(g.w, UNITS - g.x); }
                    if (field === 'w') { g.w = clamp(n(control.value, g.w), 1, UNITS - g.x); }
                    if (field === 'y') { g.y = clamp(n(control.value, g.y), -4000, 10000); }
                    if (field === 'h') { g.h = clamp(n(control.value, g.h), 0, 4000); }
                }
                commitResponsive(before, 'Ændr ' + labelDevice(activeDevice) + ' layout');
                mergeResponsive();
                scheduleApply();
            });
        });
    }

    function commitResponsive(before, label) {
        var after = clone(responsive);
        if (JSON.stringify(before) === JSON.stringify(after)) { return; }
        undo.push({ before: before, after: after, label: label });
        if (undo.length > 100) { undo.shift(); }
        redo.length = 0;
        updateButtons();
    }
    function undoResponsive() {
        if (!undo.length) { return; }
        var entry = undo.pop(); redo.push(entry); responsive = clone(entry.before); mergeResponsive(); scheduleApply();
    }
    function redoResponsive() {
        if (!redo.length) { return; }
        var entry = redo.pop(); undo.push(entry); responsive = clone(entry.after); mergeResponsive(); scheduleApply();
    }
    function updateButtons() {
        document.querySelectorAll('.h18-clean-device-button').forEach(function (button) {
            button.classList.toggle('button-primary', button.getAttribute('data-device') === activeDevice);
        });
        if (activeDevice === 'desktop') { return; }
        var undoButton = document.getElementById('h18-clean-undo');
        var redoButton = document.getElementById('h18-clean-redo');
        if (undoButton) { undoButton.disabled = undo.length === 0; undoButton.title = undo.length ? undo[undo.length - 1].label : ''; }
        if (redoButton) { redoButton.disabled = redo.length === 0; redoButton.title = redo.length ? redo[redo.length - 1].label : ''; }
    }

    function beginTransform(event, kind, direction) {
        if (activeDevice === 'desktop' || transform || event.button !== 0) { return false; }
        var card = event.target.closest('.h18-clean-node[data-node-id]');
        if (!card) { return false; }
        var id = String(card.getAttribute('data-node-id') || '');
        var model = readModel();
        var map = ensureResponsive(model);
        var node = map[id];
        if (!node) { return false; }
        var surface = card.parentElement;
        if (!surface) { return false; }
        var g = ensureOverride(node, activeDevice);
        transform = {
            id: id, kind: kind, direction: direction || '', pointerId: event.pointerId,
            card: card, surface: surface, startX: event.clientX, startY: event.clientY,
            start: clone(g), before: clone(responsive)
        };
        event.preventDefault(); event.stopPropagation(); event.stopImmediatePropagation();
        return true;
    }
    function moveTransform(event) {
        if (!transform || event.pointerId !== transform.pointerId) { return; }
        var model = readModel();
        var map = ensureResponsive(model);
        var node = map[transform.id];
        if (!node) { return; }
        var g = responsive[transform.id][activeDevice];
        var surfaceRect = transform.surface.getBoundingClientRect();
        var unit = Math.max(1, surfaceRect.width / UNITS);
        var dx = Math.round((event.clientX - transform.startX) / unit);
        var dy = Math.round((event.clientY - transform.startY) / ROW_PX);
        var start = transform.start;
        if (transform.kind === 'move') {
            g.x = clamp(start.x + dx, 0, UNITS - start.w);
            g.y = clamp(start.y + dy, -4000, 10000);
        } else {
            var dir = transform.direction;
            g.x = start.x; g.y = start.y; g.w = start.w; g.h = Math.max(1, start.h || 1);
            if (dir.indexOf('e') !== -1) { g.w = clamp(start.w + dx, 1, UNITS - start.x); }
            if (dir.indexOf('w') !== -1) {
                var appliedX = clamp(dx, -start.x, start.w - 1);
                g.x = start.x + appliedX; g.w = start.w - appliedX;
            }
            if (dir.indexOf('s') !== -1) { g.h = clamp(Math.max(1, start.h || 1) + dy, 1, 4000); }
            if (dir.indexOf('n') !== -1) {
                var startH = Math.max(1, start.h || 1);
                var appliedY = clamp(dy, -4000 - start.y, startH - 1);
                g.y = start.y + appliedY; g.h = startH - appliedY;
            }
        }
        applyCanvas();
        event.preventDefault();
    }
    function endTransform(event) {
        if (!transform || (event && event.pointerId !== transform.pointerId)) { return; }
        var current = transform; transform = null;
        commitResponsive(current.before, (current.kind === 'move' ? 'Flyt ' : 'Resize ') + labelDevice(activeDevice) + ' · ' + current.id);
        mergeResponsive(); scheduleApply();
    }

    function scheduleApply() {
        if (scheduled) { return; }
        scheduled = true;
        window.requestAnimationFrame(function () { scheduled = false; applyCanvas(); });
    }
    function installObservers() {
        var canvas = document.getElementById('h18-clean-canvas');
        var inspector = document.getElementById('h18-clean-inspector');
        var observer = new MutationObserver(scheduleApply);
        if (canvas) { observer.observe(canvas, { childList: true, subtree: true }); }
        if (inspector) { observer.observe(inspector, { childList: true, subtree: true }); }
    }

    function install() {
        installToolbar();
        ensureResponsive(readModel());

        document.addEventListener('pointerdown', function (event) {
            if (activeDevice === 'desktop') { return; }
            var handle = event.target.closest('.h18-clean-resize[data-resize]');
            if (handle) { beginTransform(event, 'resize', String(handle.getAttribute('data-resize') || '')); return; }
            var move = event.target.closest('.h18-clean-move');
            if (move) { beginTransform(event, 'move', ''); }
        }, true);
        document.addEventListener('pointermove', moveTransform, true);
        document.addEventListener('pointerup', endTransform, true);
        document.addEventListener('pointercancel', endTransform, true);

        document.addEventListener('click', function (event) {
            if (activeDevice === 'desktop') { return; }
            if (event.target.closest('#h18-clean-undo')) {
                event.preventDefault(); event.stopPropagation(); event.stopImmediatePropagation(); undoResponsive();
            } else if (event.target.closest('#h18-clean-redo')) {
                event.preventDefault(); event.stopPropagation(); event.stopImmediatePropagation(); redoResponsive();
            }
        }, true);
        document.addEventListener('keydown', function (event) {
            if (activeDevice === 'desktop' || !(event.ctrlKey || event.metaKey)) { return; }
            var key = String(event.key || '').toLowerCase();
            if (key === 'z' && event.shiftKey) { event.preventDefault(); event.stopImmediatePropagation(); redoResponsive(); }
            else if (key === 'z') { event.preventDefault(); event.stopImmediatePropagation(); undoResponsive(); }
            else if (key === 'y') { event.preventDefault(); event.stopImmediatePropagation(); redoResponsive(); }
        }, true);

        var form = document.getElementById('h18-clean-save-form');
        if (form) { form.addEventListener('submit', mergeResponsive, true); }
        var preview = document.getElementById('h18-clean-preview');
        if (preview) { preview.addEventListener('click', mergeResponsive, true); }

        installObservers();
        scheduleApply();
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
