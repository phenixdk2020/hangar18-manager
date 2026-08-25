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
                manualX: clamp(Math.round(num(props.manualX, 0)), -300, 300),
                manualY: clamp(Math.round(num(props.manualY, 0)), -300, 300),
                manualW: clamp(Math.round(num(props.manualW, 100)), 1, 600),
                manualH: clamp(Math.round(num(props.manualH, 100)), 1, 600),
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

    function currentNode(id) {
        var map = nodeMap(readModel());
        return map[String(id || '')] || initialNodes[String(id || '')] || null;
    }

    function selectedCard() {
        return document.querySelector('.h18-clean-node.is-selected[data-node-id]');
    }

    function applyText(card, node, e) {
        var preview = card.querySelector(':scope > .h18-clean-node-preview--text');
        if (!preview) { return; }
        card.style.borderRadius = e.radius + 'px';
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
        var left = e.manualX + '%';
        var top = e.manualY + '%';
        var width = e.manualW + '%';
        var height = e.manualH + '%';
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
        if (box.width <= 0 || box.height <= 0) { return; }
        var naturalW = Math.max(1, Number(img.naturalWidth || 1));
        var naturalH = Math.max(1, Number(img.naturalHeight || 1));
        var imageRatio = naturalW / naturalH;
        var boxRatio = box.width / box.height;
        if (imageRatio >= boxRatio) {
            e.manualW = 100;
            e.manualH = clamp(Math.round(((box.width / imageRatio) / box.height) * 100), 1, 600);
            e.manualX = 0;
            e.manualY = Math.round((100 - e.manualH) / 2);
        } else {
            e.manualH = 100;
            e.manualW = clamp(Math.round(((box.height * imageRatio) / box.width) * 100), 1, 600);
            e.manualY = 0;
            e.manualX = Math.round((100 - e.manualW) / 2);
        }
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
        e.lockAspect = true;
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
        card.style.borderRadius = e.radius + 'px';
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

        preview.style.position = 'relative';
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
            if (node.type !== 'text' && node.type !== 'image') { return; }
            var e = ensureExtra(id, node.type, node.props || {});
            if (node.type === 'text') { applyText(card, node, e); }
            else { applyImage(card, node, e); }
        });
        injectInspector();
    }

    function beginTransform(event, id, kind, direction, preview, img, frame) {
        if (event.button !== 0 || transform) { return; }
        var node = currentNode(id);
        if (!node) { return; }
        var e = ensureExtra(id, 'image', node.props || {});
        var box = preview.getBoundingClientRect();
        if (box.width <= 0 || box.height <= 0) { return; }
        transform = {
            id: String(id), kind: kind, direction: direction,
            pointerId: event.pointerId, preview: preview, img: img, frame: frame,
            startX: event.clientX, startY: event.clientY,
            boxW: box.width, boxH: box.height,
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
        var dx = event.clientX - transform.startX;
        var dy = event.clientY - transform.startY;
        var start = transform.start;
        if (transform.kind === 'move') {
            e.manualX = clamp(Math.round(start.manualX + (dx / transform.boxW) * 100), -300, 300);
            e.manualY = clamp(Math.round(start.manualY + (dy / transform.boxH) * 100), -300, 300);
        } else {
            var startLeft = (start.manualX / 100) * transform.boxW;
            var startTop = (start.manualY / 100) * transform.boxH;
            var startW = Math.max(1, (start.manualW / 100) * transform.boxW);
            var startH = Math.max(1, (start.manualH / 100) * transform.boxH);
            var rawW = startW;
            var rawH = startH;
            var dir = transform.direction;
            if (dir.indexOf('e') !== -1) { rawW = startW + dx; }
            if (dir.indexOf('w') !== -1) { rawW = startW - dx; }
            if (dir.indexOf('s') !== -1) { rawH = startH + dy; }
            if (dir.indexOf('n') !== -1) { rawH = startH - dy; }
            rawW = clamp(rawW, 16, transform.boxW * 6);
            rawH = clamp(rawH, 16, transform.boxH * 6);

            var nextW = rawW;
            var nextH = rawH;
            if (e.lockAspect) {
                var scaleW = rawW / startW;
                var scaleH = rawH / startH;
                var scale = Math.abs(scaleW - 1) >= Math.abs(scaleH - 1) ? scaleW : scaleH;
                scale = clamp(scale, 0.05, 6);
                nextW = startW * scale;
                nextH = startH * scale;
            }

            var nextLeft = startLeft;
            var nextTop = startTop;
            if (dir.indexOf('w') !== -1) { nextLeft = startLeft + startW - nextW; }
            if (dir.indexOf('n') !== -1) { nextTop = startTop + startH - nextH; }
            e.manualX = clamp(Math.round((nextLeft / transform.boxW) * 100), -300, 300);
            e.manualY = clamp(Math.round((nextTop / transform.boxH) * 100), -300, 300);
            e.manualW = clamp(Math.round((nextW / transform.boxW) * 100), 1, 600);
            e.manualH = clamp(Math.round((nextH / transform.boxH) * 100), 1, 600);
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
                manualGrid.appendChild(makeField('Billede X %', 'manualX', 'number', e.manualX, -300, 300));
                manualGrid.appendChild(makeField('Billede Y %', 'manualY', 'number', e.manualY, -300, 300));
                manualGrid.appendChild(makeField('Billede bredde %', 'manualW', 'number', e.manualW, 1, 600));
                manualGrid.appendChild(makeField('Billede højde %', 'manualH', 'number', e.manualH, 1, 600));
                manualGrid.appendChild(makeField('Lås proportioner', 'lockAspect', 'checkbox', e.lockAspect));
                panel.appendChild(manualGrid);
                var help = document.createElement('p');
                help.className = 'description';
                help.textContent = 'Den grønne ramme styrer billedboksen. Den sandfarvede ramme styrer selve billedet. Træk i billedet for at flytte det, eller brug hjørnepunkterne for at skalere.';
                panel.appendChild(help);
                var reset = document.createElement('button');
                reset.type = 'button';
                reset.className = 'button';
                reset.textContent = 'Tilbage til Vis hele billedet';
                reset.addEventListener('click', function () {
                    e.manual = false;
                    e.fitOverride = 'contain';
                    syncHidden();
                    applyAll();
                    panel.remove();
                    injectInspector();
                });
                panel.appendChild(reset);
            } else {
                var hint = document.createElement('p');
                hint.className = 'description';
                hint.textContent = 'Du kan også dobbeltklikke på billedet på canvas for at gå i manuel billedtilstand.';
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
            else if (field === 'manualX') { e.manualX = clamp(Math.round(num(input.value, 0)), -300, 300); }
            else if (field === 'manualY') { e.manualY = clamp(Math.round(num(input.value, 0)), -300, 300); }
            else if (field === 'manualW') { e.manualW = clamp(Math.round(num(input.value, 100)), 1, 600); }
            else if (field === 'manualH') { e.manualH = clamp(Math.round(num(input.value, 100)), 1, 600); }
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
        if (canvas) {
            new MutationObserver(scheduleApply).observe(canvas, { childList: true, subtree: true });
        }
        if (inspector) {
            new MutationObserver(scheduleApply).observe(inspector, { childList: true, subtree: true });
        }
        var form = document.getElementById('h18-clean-save-form');
        if (form) {
            form.addEventListener('submit', function () { syncHidden(); }, false);
        }
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
