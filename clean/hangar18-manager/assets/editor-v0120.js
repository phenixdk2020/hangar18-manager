(function () {
    'use strict';

    var CFG = window.H18CleanEditor || {};
    var extras = Object.create(null);
    var initialNodes = Object.create(null);
    var transform = null;
    var scheduled = false;

    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
    function num(value, fallback) {
        var n = parseFloat(value);
        return Number.isFinite(n) ? n : fallback;
    }
    function color(value, fallback) {
        return /^#[0-9a-f]{6}$/i.test(String(value || '')) ? String(value).toLowerCase() : fallback;
    }
    function clone(value) { return JSON.parse(JSON.stringify(value)); }
    function editorScale() {
        if (window.H18VDViewport && typeof window.H18VDViewport.scale === 'function') {
            var value = parseFloat(window.H18VDViewport.scale());
            if (Number.isFinite(value) && value > 0) { return value; }
        }
        return 1;
    }

    (Array.isArray(CFG.initialModel && CFG.initialModel.nodes) ? CFG.initialModel.nodes : []).forEach(function (node) {
        if (node && node.id) { initialNodes[String(node.id)] = clone(node); }
    });

    function readModel() {
        var field = document.getElementById('h18-clean-model-json');
        if (!field) { return { nodes: [] }; }
        try {
            var model = JSON.parse(field.value || '{}');
            return model && typeof model === 'object' ? model : { nodes: [] };
        } catch (ignore) {
            return { nodes: [] };
        }
    }

    function nodeMap(model) {
        var map = Object.create(null);
        (Array.isArray(model && model.nodes) ? model.nodes : []).forEach(function (node) {
            if (node && node.id) { map[String(node.id)] = node; }
        });
        return map;
    }

    function currentNode(id) {
        var map = nodeMap(readModel());
        return map[String(id || '')] || initialNodes[String(id || '')] || null;
    }

    function ensureExtra(id, type, liveProps) {
        id = String(id || '');
        if (extras[id]) { return extras[id]; }
        var original = initialNodes[id] && initialNodes[id].props ? initialNodes[id].props : {};
        var props = Object.assign({}, original, liveProps || {});
        if (type === 'text') {
            extras[id] = {
                type: 'text',
                background: color(props.background, '#ffffff'),
                backgroundTransparent: Object.prototype.hasOwnProperty.call(props, 'backgroundTransparent') ? !!props.backgroundTransparent : true,
                textColor: color(props.textColor, '#000000'),
                headingColor: color(props.headingColor, '#000000'),
                padding: clamp(Math.round(num(props.padding, 0)), 0, 120),
                radius: clamp(Math.round(num(props.radius, 0)), 0, 100)
            };
        } else if (type === 'image') {
            extras[id] = {
                type: 'image',
                radius: clamp(Math.round(num(props.radius, 0)), 0, 100),
                manual: String(props.fit || '').toLowerCase() === 'manual',
                fitOverride: '',
                manualX: clamp(Math.round(num(props.manualX, 0)), -4000, 4000),
                manualY: clamp(Math.round(num(props.manualY, 0)), -4000, 4000),
                manualW: clamp(Math.round(num(props.manualW, 320)), 1, 4000),
                manualH: clamp(Math.round(num(props.manualH, 240)), 1, 4000),
                lockAspect: Object.prototype.hasOwnProperty.call(props, 'lockAspect') ? !!props.lockAspect : true
            };
        } else {
            extras[id] = { type: type || '' };
        }
        return extras[id];
    }

    function mergeModel() {
        var model = readModel();
        (Array.isArray(model.nodes) ? model.nodes : []).forEach(function (node) {
            if (!node || !node.id || !node.props) { return; }
            var e = extras[String(node.id)];
            if (!e) { return; }
            if (e.type === 'text') {
                node.props.background = e.background;
                node.props.backgroundTransparent = !!e.backgroundTransparent;
                node.props.textColor = e.textColor;
                node.props.headingColor = e.headingColor;
                node.props.padding = e.padding;
                node.props.radius = e.radius;
            } else if (e.type === 'image') {
                node.props.radius = e.radius;
                node.props.lockAspect = !!e.lockAspect;
                if (e.manual) {
                    node.props.fit = 'manual';
                    node.props.manualX = e.manualX;
                    node.props.manualY = e.manualY;
                    node.props.manualW = e.manualW;
                    node.props.manualH = e.manualH;
                } else if (e.fitOverride) {
                    node.props.fit = e.fitOverride;
                }
            }
        });
        return model;
    }

    function syncHidden() {
        var field = document.getElementById('h18-clean-model-json');
        if (!field) { return null; }
        var model = mergeModel();
        field.value = JSON.stringify(model);
        return model;
    }

    window.H18CleanV0120 = { sync: syncHidden };

    function selectedCard() {
        return document.querySelector('.h18-clean-node.is-selected[data-node-id]');
    }

    function setCardRadius(card, radius) {
        card.style.borderRadius = clamp(Math.round(num(radius, 0)), 0, 100) + 'px';
    }

    function applyText(card, node, e) {
        var preview = card.querySelector(':scope > .h18-clean-node-preview--text');
        if (!preview) { return; }
        setCardRadius(card, e.radius);
        preview.style.boxSizing = 'border-box';
        preview.style.height = '100%';
        preview.style.borderRadius = e.radius + 'px';
        preview.style.background = e.backgroundTransparent ? 'transparent' : e.background;
        preview.style.color = e.textColor;
        preview.style.padding = e.padding + 'px';
        var heading = preview.querySelector('.h18-clean-text-heading');
        if (heading) { heading.style.color = e.headingColor; }
        var body = preview.querySelector('.h18-clean-text-body');
        if (body) { body.style.color = e.textColor; }
    }

    function setManualGeometry(preview, img, frame, e) {
        var left = e.manualX + 'px';
        var top = e.manualY + 'px';
        var width = e.manualW + 'px';
        var height = e.manualH + 'px';
        preview.style.position = 'relative';
        if (img) {
            img.style.position = 'absolute';
            img.style.left = left;
            img.style.top = top;
            img.style.width = width;
            img.style.height = height;
            img.style.maxWidth = 'none';
            img.style.maxHeight = 'none';
            img.style.objectFit = 'fill';
            img.style.objectPosition = '50% 50%';
            img.style.margin = '0';
            img.style.userSelect = 'none';
            img.style.pointerEvents = 'none';
        }
        if (frame) {
            frame.style.left = left;
            frame.style.top = top;
            frame.style.width = width;
            frame.style.height = height;
        }
    }

    function initializeManualGeometry(preview, img, e) {
        var box = preview.getBoundingClientRect();
        var scale = editorScale();
        var boxWidth = box.width / scale;
        var boxHeight = box.height / scale;
        if (boxWidth <= 0 || boxHeight <= 0) { return; }
        var naturalW = Math.max(1, Number(img.naturalWidth || img.width || 1));
        var naturalH = Math.max(1, Number(img.naturalHeight || img.height || 1));
        var ratio = naturalW / naturalH;
        var width;
        var height;
        if ((boxWidth / boxHeight) >= ratio) {
            height = boxHeight;
            width = height * ratio;
        } else {
            width = boxWidth;
            height = width / ratio;
        }
        e.manualW = clamp(Math.round(width), 1, 4000);
        e.manualH = clamp(Math.round(height), 1, 4000);
        e.manualX = Math.round((boxWidth - width) / 2);
        e.manualY = Math.round((boxHeight - height) / 2);
    }

    function enterManual(id, card) {
        var node = currentNode(id);
        if (!node || node.type !== 'image') { return; }
        var e = ensureExtra(id, 'image', node.props || {});
        var preview = card.querySelector(':scope > .h18-clean-node-preview--image');
        var img = preview && preview.querySelector('img');
        if (!preview || !img) { return; }
        if (!e.manual) { initializeManualGeometry(preview, img, e); }
        e.manual = true;
        e.fitOverride = '';
        syncHidden();
        applyAll();
    }

    function makeImageFrame(card, preview, img, node, e) {
        var existing = preview.querySelector(':scope > .h18-clean-image-edit-frame');
        if (existing) {
            setManualGeometry(preview, img, existing, e);
            return;
        }
        var frame = document.createElement('div');
        frame.className = 'h18-clean-image-edit-frame';
        frame.setAttribute('data-image-node-id', String(node.id));
        frame.title = 'Træk for at flytte billedet inde i boksen';
        var label = document.createElement('span');
        label.className = 'h18-clean-image-edit-label';
        label.textContent = 'BILLEDINDHOLD';
        frame.appendChild(label);
        ['nw', 'ne', 'se', 'sw'].forEach(function (direction) {
            var handle = document.createElement('span');
            handle.className = 'h18-clean-image-inner-resize h18-clean-image-inner-resize--' + direction;
            handle.setAttribute('data-image-resize', direction);
            handle.title = 'Skalér selve billedet';
            handle.addEventListener('pointerdown', function (event) {
                beginTransform(event, node.id, 'resize', direction, preview, img, frame);
            });
            frame.appendChild(handle);
        });
        frame.addEventListener('pointerdown', function (event) {
            if (event.target.closest('[data-image-resize]')) { return; }
            beginTransform(event, node.id, 'move', '', preview, img, frame);
        });
        frame.addEventListener('click', function (event) { event.stopPropagation(); });
        preview.appendChild(frame);
        setManualGeometry(preview, img, frame, e);
    }

    function applyImage(card, node, e) {
        var preview = card.querySelector(':scope > .h18-clean-node-preview--image');
        if (!preview) { return; }
        var img = preview.querySelector('img');
        setCardRadius(card, e.radius);
        preview.style.borderRadius = e.radius + 'px';
        preview.style.overflow = 'hidden';
        if (!img) { return; }

        if (!e.manual) {
            if (e.fitOverride === 'contain') {
                preview.style.display = 'flex';
                preview.style.justifyContent = 'center';
                preview.style.alignItems = 'center';
                img.style.position = '';
                img.style.left = '';
                img.style.top = '';
                img.style.width = '100%';
                img.style.height = '100%';
                img.style.maxWidth = 'none';
                img.style.maxHeight = 'none';
                img.style.objectFit = 'contain';
                img.style.objectPosition = '50% 50%';
                img.style.pointerEvents = '';
            }
            if (card.classList.contains('is-selected') && !img.dataset.h18ManualDblClick) {
                img.dataset.h18ManualDblClick = '1';
                img.title = 'Dobbeltklik for at flytte og skalere selve billedet';
                img.addEventListener('dblclick', function (event) {
                    event.preventDefault();
                    event.stopPropagation();
                    enterManual(node.id, card);
                });
            }
            return;
        }

        preview.style.display = 'block';
        preview.style.justifyContent = '';
        preview.style.alignItems = '';
        setManualGeometry(preview, img, null, e);
        if (card.classList.contains('is-selected')) {
            makeImageFrame(card, preview, img, node, e);
        }
    }

    function applyAll() {
        var model = readModel();
        var map = nodeMap(model);
        document.querySelectorAll('.h18-clean-node[data-node-id]').forEach(function (card) {
            var id = String(card.getAttribute('data-node-id') || '');
            var node = map[id] || initialNodes[id];
            if (!node) { return; }
            if (node.type === 'text') {
                applyText(card, node, ensureExtra(id, 'text', node.props || {}));
            } else if (node.type === 'image') {
                applyImage(card, node, ensureExtra(id, 'image', node.props || {}));
            } else {
                setCardRadius(card, node.props && node.props.radius || 0);
            }
        });
        injectInspector();
    }

    function beginTransform(event, id, kind, direction, preview, img, frame) {
        if (event.button !== 0 || transform) { return; }
        var node = currentNode(id);
        if (!node) { return; }
        var e = ensureExtra(id, 'image', node.props || {});
        transform = {
            id: String(id), kind: kind, direction: direction,
            pointerId: event.pointerId, preview: preview, img: img, frame: frame,
            startX: event.clientX, startY: event.clientY,
            start: clone(e)
        };
        try { frame.setPointerCapture(event.pointerId); } catch (ignore) {}
        frame.classList.add('is-transforming');
        event.preventDefault();
        event.stopPropagation();
    }

    function moveTransform(event) {
        if (!transform || event.pointerId !== transform.pointerId) { return; }
        var e = extras[transform.id];
        if (!e) { return; }
        var scale = editorScale();
        var dx = (event.clientX - transform.startX) / scale;
        var dy = (event.clientY - transform.startY) / scale;
        var start = transform.start;
        if (transform.kind === 'move') {
            e.manualX = clamp(Math.round(start.manualX + dx), -4000, 4000);
            e.manualY = clamp(Math.round(start.manualY + dy), -4000, 4000);
        } else {
            var dir = transform.direction;
            var nextX = start.manualX;
            var nextY = start.manualY;
            var nextW = start.manualW;
            var nextH = start.manualH;
            if (dir.indexOf('e') !== -1) { nextW = start.manualW + dx; }
            if (dir.indexOf('w') !== -1) { nextW = start.manualW - dx; }
            if (dir.indexOf('s') !== -1) { nextH = start.manualH + dy; }
            if (dir.indexOf('n') !== -1) { nextH = start.manualH - dy; }
            nextW = clamp(Math.round(nextW), 16, 4000);
            nextH = clamp(Math.round(nextH), 16, 4000);

            if (e.lockAspect) {
                var ratio = Math.max(0.01, start.manualW / Math.max(1, start.manualH));
                var changeW = Math.abs(nextW - start.manualW) / Math.max(1, start.manualW);
                var changeH = Math.abs(nextH - start.manualH) / Math.max(1, start.manualH);
                if (changeW >= changeH) { nextH = Math.max(16, Math.round(nextW / ratio)); }
                else { nextW = Math.max(16, Math.round(nextH * ratio)); }
            }
            if (dir.indexOf('w') !== -1) { nextX = start.manualX + start.manualW - nextW; }
            if (dir.indexOf('n') !== -1) { nextY = start.manualY + start.manualH - nextH; }

            e.manualX = clamp(Math.round(nextX), -4000, 4000);
            e.manualY = clamp(Math.round(nextY), -4000, 4000);
            e.manualW = clamp(Math.round(nextW), 1, 4000);
            e.manualH = clamp(Math.round(nextH), 1, 4000);
        }
        setManualGeometry(transform.preview, transform.img, transform.frame, e);
        event.preventDefault();
    }

    function endTransform(event, cancel) {
        if (!transform || (event && event.pointerId !== transform.pointerId)) { return; }
        var current = transform;
        transform = null;
        current.frame.classList.remove('is-transforming');
        if (cancel) { extras[current.id] = current.start; }
        syncHidden();
        applyAll();
    }

    function makeField(label, name, type, value, min, max) {
        var wrap = document.createElement('label');
        wrap.textContent = label;
        var input = document.createElement('input');
        input.type = type;
        input.setAttribute('data-v0120-field', name);
        if (type === 'checkbox') { input.checked = !!value; }
        else { input.value = String(value); }
        if (min != null) { input.min = String(min); }
        if (max != null) { input.max = String(max); }
        wrap.appendChild(input);
        return wrap;
    }

    function injectInspector() {
        var card = selectedCard();
        var host = document.getElementById('h18-clean-inspector');
        if (!card || !host || host.querySelector('.h18-clean-v0120-style')) { return; }
        var id = String(card.getAttribute('data-node-id') || '');
        var node = currentNode(id);
        if (!node || (node.type !== 'text' && node.type !== 'image')) { return; }
        var e = ensureExtra(id, node.type, node.props || {});
        var panel = document.createElement('div');
        panel.className = 'h18-clean-v0120-style';
        var title = document.createElement('strong');
        title.textContent = node.type === 'text' ? 'Baggrund, tekst og hjørner' : 'Billedboks og billedindhold';
        panel.appendChild(title);
        var grid = document.createElement('div');
        grid.className = 'h18-clean-field-grid h18-clean-v0120-grid';

        if (node.type === 'text') {
            grid.appendChild(makeField('Gennemsigtig baggrund', 'backgroundTransparent', 'checkbox', e.backgroundTransparent));
            grid.appendChild(makeField('Baggrund', 'background', 'color', e.background));
            grid.appendChild(makeField('Tekstfarve', 'textColor', 'color', e.textColor));
            grid.appendChild(makeField('Overskriftsfarve', 'headingColor', 'color', e.headingColor));
            grid.appendChild(makeField('Padding px', 'padding', 'number', e.padding, 0, 120));
            grid.appendChild(makeField('Hjørner px', 'radius', 'number', e.radius, 0, 100));
            panel.appendChild(grid);
        } else {
            grid.appendChild(makeField('Hjørner px', 'radius', 'number', e.radius, 0, 100));
            panel.appendChild(grid);
            var edit = document.createElement('button');
            edit.type = 'button';
            edit.className = 'button h18-clean-v0120-manual-button';
            edit.textContent = e.manual ? 'Billedindhold er i manuel tilstand' : 'Redigér selve billedet manuelt';
            edit.disabled = !!e.manual;
            edit.addEventListener('click', function () { enterManual(id, card); });
            panel.appendChild(edit);
            if (e.manual) {
                var manualGrid = document.createElement('div');
                manualGrid.className = 'h18-clean-field-grid h18-clean-v0120-grid';
                manualGrid.appendChild(makeField('Billede X px', 'manualX', 'number', e.manualX, -4000, 4000));
                manualGrid.appendChild(makeField('Billede Y px', 'manualY', 'number', e.manualY, -4000, 4000));
                manualGrid.appendChild(makeField('Billede bredde px', 'manualW', 'number', e.manualW, 1, 4000));
                manualGrid.appendChild(makeField('Billede højde px', 'manualH', 'number', e.manualH, 1, 4000));
                manualGrid.appendChild(makeField('Lås proportioner', 'lockAspect', 'checkbox', e.lockAspect));
                panel.appendChild(manualGrid);
                var help = document.createElement('p');
                help.className = 'description';
                help.textContent = 'Grøn ramme = billedboks. Sand ramme = selve billedindholdet.';
                panel.appendChild(help);
                var reset = document.createElement('button');
                reset.type = 'button';
                reset.className = 'button';
                reset.textContent = 'Tilbage til Vis hele billedet';
                reset.addEventListener('click', function () {
                    e.manual = false;
                    e.fitOverride = 'contain';
                    var staleFrame = card.querySelector('.h18-clean-image-edit-frame');
                    if (staleFrame) { staleFrame.remove(); }
                    var fitSelect = host.querySelector('[data-field="fit"]');
                    if (fitSelect) {
                        fitSelect.value = 'contain';
                        fitSelect.dispatchEvent(new Event('change', { bubbles: true }));
                    } else {
                        syncHidden();
                        applyAll();
                    }
                    if (panel.isConnected) { panel.remove(); }
                    injectInspector();
                });
                panel.appendChild(reset);
            } else {
                var hint = document.createElement('p');
                hint.className = 'description';
                hint.textContent = 'Brug knappen for at flytte eller skalere billedet inde i billedboksen.';
                panel.appendChild(hint);
            }
        }

        panel.addEventListener('change', function (event) {
            var input = event.target.closest('[data-v0120-field]');
            if (!input) { return; }
            var field = String(input.getAttribute('data-v0120-field') || '');
            if (field === 'backgroundTransparent') { e.backgroundTransparent = !!input.checked; }
            else if (field === 'background') { e.background = color(input.value, '#ffffff'); }
            else if (field === 'textColor') { e.textColor = color(input.value, '#000000'); }
            else if (field === 'headingColor') { e.headingColor = color(input.value, '#000000'); }
            else if (field === 'padding') { e.padding = clamp(Math.round(num(input.value, 0)), 0, 120); }
            else if (field === 'radius') { e.radius = clamp(Math.round(num(input.value, 0)), 0, 100); }
            else if (field === 'manualX') { e.manualX = clamp(Math.round(num(input.value, 0)), -4000, 4000); }
            else if (field === 'manualY') { e.manualY = clamp(Math.round(num(input.value, 0)), -4000, 4000); }
            else if (field === 'manualW') { e.manualW = clamp(Math.round(num(input.value, 320)), 1, 4000); }
            else if (field === 'manualH') { e.manualH = clamp(Math.round(num(input.value, 240)), 1, 4000); }
            else if (field === 'lockAspect') { e.lockAspect = !!input.checked; }
            syncHidden();
            applyAll();
        });

        var del = host.querySelector('#h18-clean-delete');
        host.insertBefore(panel, del || null);
    }

    function scheduleApply() {
        if (scheduled) { return; }
        scheduled = true;
        window.requestAnimationFrame(function () {
            scheduled = false;
            applyAll();
        });
    }

    function install() {
        var canvas = document.getElementById('h18-clean-canvas');
        var inspector = document.getElementById('h18-clean-inspector');
        if (canvas) { new MutationObserver(scheduleApply).observe(canvas, { childList: true, subtree: true }); }
        if (inspector) { new MutationObserver(scheduleApply).observe(inspector, { childList: true, subtree: true }); }
        var form = document.getElementById('h18-clean-save-form');
        if (form) { form.addEventListener('submit', function () { syncHidden(); }, false); }
        document.addEventListener('change', function (event) {
            var target = event.target;
            if (!target || target.getAttribute('data-field') !== 'fit') { return; }
            var card = selectedCard();
            if (!card) { return; }
            var id = String(card.getAttribute('data-node-id') || '');
            var node = currentNode(id);
            if (!node || node.type !== 'image') { return; }
            var e = ensureExtra(id, 'image', node.props || {});
            e.manual = false;
            e.fitOverride = '';
            window.setTimeout(scheduleApply, 0);
        }, false);
        document.addEventListener('pointermove', moveTransform, true);
        document.addEventListener('pointerup', function (event) { endTransform(event, false); }, true);
        document.addEventListener('pointercancel', function (event) { endTransform(event, true); }, true);
        document.addEventListener('keydown', function (event) {
            if (event.key === 'Escape' && transform) { endTransform(null, true); }
        }, true);
        scheduleApply();
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
