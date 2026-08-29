(function () {
    'use strict';

    const CFG = window.H18CleanEditor || {};
    const UNITS = Math.max(12, parseInt(CFG.units || 120, 10) || 120);
    const ROW_PX = Math.max(2, parseInt(CFG.rowPx || 8, 10) || 8);
    const POST_ID = parseInt(CFG.postId || 0, 10) || 0;
    const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu'];
    const PARENT_TYPES = ['section', 'container'];
    const undoStack = [];
    const redoStack = [];
    const HISTORY_LIMIT = 100;
    const MIN_SPLIT_H = 8;
    const FONT_TOKENS = ['system','arial','verdana','tahoma','trebuchet','georgia','times','courier'];

    function editorScale() {
        if (window.H18VDViewport && typeof window.H18VDViewport.scale === 'function') {
            const value = parseFloat(window.H18VDViewport.scale());
            if (Number.isFinite(value) && value > 0) { return value; }
        }
        const canvas = document.getElementById('h18-clean-canvas');
        const value = canvas ? parseFloat(canvas.getAttribute('data-h18-viewport-scale') || '1') : 1;
        return Number.isFinite(value) && value > 0 ? value : 1;
    }
    function editorRowPx() { return ROW_PX * editorScale(); }

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
    function normalizeFontToken(value, heading) {
        const token = String(value || '').toLowerCase();
        if (heading && token === 'body') { return 'body'; }
        return FONT_TOKENS.includes(token) ? token : 'system';
    }
    function fontCss(token, bodyToken) {
        token = normalizeFontToken(token, true);
        if (token === 'body') { token = normalizeFontToken(bodyToken, false); }
        return ({system:'system-ui,-apple-system,\"Segoe UI\",sans-serif',arial:'Arial,sans-serif',verdana:'Verdana,sans-serif',tahoma:'Tahoma,sans-serif',trebuchet:'\"Trebuchet MS\",sans-serif',georgia:'Georgia,serif',times:'\"Times New Roman\",serif',courier:'\"Courier New\",monospace'})[token] || 'system-ui,-apple-system,\"Segoe UI\",sans-serif';
    }
    function fontOptions(selected, allowBody) {
        const options = [];
        if (allowBody) { options.push(['body','Samme som brødtekst']); }
        options.push(['system','System / Segoe UI'],['arial','Arial'],['verdana','Verdana'],['tahoma','Tahoma'],['trebuchet','Trebuchet MS'],['georgia','Georgia'],['times','Times New Roman'],['courier','Courier New']);
        return options.map(function (item) { return '<option value=\"' + item[0] + '\"' + (selected === item[0] ? ' selected' : '') + '>' + item[1] + '</option>'; }).join('');
    }
    function headingPx(props) {
        const explicit = clamp(parseInt(props.headingFontSize || 0, 10) || 0, 0, 160);
        if (explicit > 0) { return explicit; }
        return ({h2:32,h3:28,h4:24,h5:20,h6:18})[String(props.headingLevel || 'h2')] || 32;
    }
    function typeLabel(type) { return ({section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap',menu:'Menu'})[String(type || '')] || String(type || 'Element'); }
    function isFloatingButton(node) { return !!(node && node.type === 'button' && node.props && node.props.placementMode === 'overlay'); }
    function fieldLabel(field) { return ({gx:'X-position',gw:'bredde',gy:'Y-position',gh:'højde',heading:'overskrift',headingLevel:'overskrifttype',text:'tekstindhold',align:'tekstjustering',verticalAlign:'lodret justering',fontFamily:'skrifttype',fontSize:'skriftstørrelse',fontWeight:'skrifttykkelse',lineHeight:'linjeafstand',letterSpacing:'bogstavafstand',headingFontFamily:'overskriftsskrifttype',headingFontSize:'overskriftsstørrelse',headingFontWeight:'overskriftstykkelse',headingLineHeight:'overskriftens linjeafstand',headingLetterSpacing:'overskriftens bogstavafstand',fit:'billedtilpasning',imageAlignX:'vandret billedplacering',imageAlignY:'lodret billedplacering',boxTransparent:'boksbaggrund',boxBackground:'boksbaggrundsfarve',focalX:'billedfokus X',focalY:'billedfokus Y',alt:'alt-tekst',background:'baggrund',radius:'hjørner',padding:'padding',borderWidth:'ramme',borderColor:'rammefarve',gapX:'Afstand X',gapY:'Afstand Y',buttonText:'knaptekst',linkType:'linktype',pageId:'intern side',url:'linkdestination',targetBlank:'ny fane',textColor:'tekstfarve',hoverBackground:'hover-baggrund',hoverTextColor:'hover-tekstfarve',focusColor:'focus-farve',paddingX:'vandret padding',paddingY:'lodret padding',autoSize:'automatisk størrelse',placementMode:'placering',zIndex:'lag',menuId:'WordPress-menu',orientation:'menuretning',mobileMode:'mobilmenu',mobilePresentation:'mobilmenu-visning',mobileCloseOnSelect:'luk efter valg',mobileCloseOutside:'luk ved klik udenfor',activeTextColor:'aktiv menufarve',backgroundTransparent:'gennemsigtig baggrund',menuGap:'menuafstand'})[String(field || '')] || String(field || 'felt'); }
    function richPreviewHtml(value) {
        const raw = String(value || '');
        const tpl = document.createElement('template');
        tpl.innerHTML = raw.indexOf('<') === -1 ? raw.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\r?\n/g, '<br>') : raw;
        const allowed = new Set(['P','BR','STRONG','B','EM','I','U','S','UL','OL','LI','A']);
        Array.from(tpl.content.querySelectorAll('*')).forEach(function (el) {
            if (!allowed.has(el.tagName)) {
                const parent = el.parentNode;
                if (parent) { while (el.firstChild) { parent.insertBefore(el.firstChild, el); } parent.removeChild(el); }
                return;
            }
            Array.from(el.attributes).forEach(function (attr) {
                const ok = el.tagName === 'A' && ['href','target','rel'].includes(attr.name.toLowerCase());
                if (!ok) { el.removeAttribute(attr.name); }
            });
            if (el.tagName === 'A') {
                const href = String(el.getAttribute('href') || '');
                if (/^javascript:/i.test(href)) { el.removeAttribute('href'); }
            }
        });
        return tpl.innerHTML;
    }

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
                heading: String(raw.heading || ''),
                headingLevel: ['h2', 'h3', 'h4', 'h5', 'h6'].includes(String(raw.headingLevel || '').toLowerCase()) ? String(raw.headingLevel).toLowerCase() : 'h2',
                text: String(raw.text || 'Ny tekst'),
                align: ['left', 'center', 'right'].includes(raw.align) ? raw.align : 'left',
                verticalAlign: ['top', 'center', 'bottom'].includes(String(raw.verticalAlign || '').toLowerCase()) ? String(raw.verticalAlign).toLowerCase() : 'top',
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#ffffff',
                backgroundTransparent: raw.backgroundTransparent !== false,
                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#000000',
                headingColor: /^#[0-9a-f]{6}$/i.test(String(raw.headingColor || '')) ? String(raw.headingColor).toLowerCase() : '#000000',
                padding: clamp(parseInt(raw.padding || 0, 10) || 0, 0, 120),
                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 16, 10) || 16, 8, 120),
                fontWeight: clamp(parseInt(raw.fontWeight || 400, 10) || 400, 100, 900),
                lineHeight: Math.max(0.8, Math.min(3, parseFloat(raw.lineHeight || 1.5) || 1.5)),
                letterSpacing: Math.max(-10, Math.min(30, parseFloat(raw.letterSpacing || 0) || 0)),
                headingFontFamily: normalizeFontToken(raw.headingFontFamily || 'body', true),
                headingFontSize: clamp(parseInt(raw.headingFontSize || 0, 10) || 0, 0, 160),
                headingFontWeight: clamp(parseInt(raw.headingFontWeight || 700, 10) || 700, 100, 900),
                headingLineHeight: Math.max(0.8, Math.min(3, parseFloat(raw.headingLineHeight || 1.2) || 1.2)),
                headingLetterSpacing: Math.max(-10, Math.min(30, parseFloat(raw.headingLetterSpacing || 0) || 0))
            });
        }
        if (type === 'button') {
            const linkType = ['page', 'url', 'anchor', 'email', 'phone'].includes(String(raw.linkType || '').toLowerCase()) ? String(raw.linkType).toLowerCase() : 'url';
            return Object.assign(common, {
                text: String(raw.text || 'Knap'),
                linkType: linkType,
                pageId: parseInt(raw.pageId || 0, 10) || 0,
                url: String(raw.url || ''),
                targetBlank: !!raw.targetBlank,
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#30382a',
                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#ffffff',
                hoverBackground: /^#[0-9a-f]{6}$/i.test(String(raw.hoverBackground || '')) ? String(raw.hoverBackground).toLowerCase() : '#525a5f',
                hoverTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.hoverTextColor || '')) ? String(raw.hoverTextColor).toLowerCase() : '#ffffff',
                focusColor: /^#[0-9a-f]{6}$/i.test(String(raw.focusColor || '')) ? String(raw.focusColor).toLowerCase() : '#c3ae83',
                paddingX: clamp(parseInt(raw.paddingX || 20, 10) || 20, 0, 120),
                paddingY: clamp(parseInt(raw.paddingY || 10, 10) || 10, 0, 120),
                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),
                autoSize: raw.autoSize !== false,
                placementMode: String(raw.placementMode || 'normal').toLowerCase() === 'overlay' ? 'overlay' : 'normal',
                zIndex: clamp(parseInt(raw.zIndex || 20, 10) || 20, 1, 200)
            });
        }
        if (type === 'menu') {
            return Object.assign(common, {
                menuId: parseInt(raw.menuId || 0, 10) || 0,
                orientation: ['horizontal', 'vertical'].includes(String(raw.orientation || '').toLowerCase()) ? String(raw.orientation).toLowerCase() : 'horizontal',
                align: ['left', 'center', 'right'].includes(String(raw.align || '').toLowerCase()) ? String(raw.align).toLowerCase() : 'right',
                mobileMode: ['hamburger', 'vertical', 'wrap'].includes(String(raw.mobileMode || '').toLowerCase()) ? String(raw.mobileMode).toLowerCase() : 'hamburger',
                mobilePresentation: ['dropdown', 'panel-right', 'panel-left'].includes(String(raw.mobilePresentation || '').toLowerCase()) ? String(raw.mobilePresentation).toLowerCase() : 'dropdown',
                mobileCloseOnSelect: raw.mobileCloseOnSelect !== false,
                mobileCloseOutside: raw.mobileCloseOutside !== false,
                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#ffffff',
                hoverTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.hoverTextColor || '')) ? String(raw.hoverTextColor).toLowerCase() : '#c3ae83',
                activeTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.activeTextColor || '')) ? String(raw.activeTextColor).toLowerCase() : '#c3ae83',
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#30382a',
                backgroundTransparent: raw.backgroundTransparent !== false,
                fontSize: clamp(parseInt(raw.fontSize || 16, 10) || 16, 8, 64),
                fontWeight: clamp(parseInt(raw.fontWeight || 600, 10) || 600, 100, 900),
                menuGap: clamp(parseInt(raw.menuGap || 24, 10) || 24, 0, 120),
                paddingX: clamp(parseInt(raw.paddingX || 8, 10) || 8, 0, 120),
                paddingY: clamp(parseInt(raw.paddingY || 8, 10) || 8, 0, 120),
                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100)
            });
        }
        if (type === 'image') {
            const fit = ['cover', 'contain', 'original', 'stretch', 'manual'].includes(String(raw.fit || '').toLowerCase()) ? String(raw.fit).toLowerCase() : 'contain';
            return Object.assign(common, {
                mediaId: parseInt(raw.mediaId || 0, 10) || 0,
                url: String(raw.url || ''),
                alt: String(raw.alt || ''),
                fit: fit,
                imageAlignX: ['left', 'center', 'right'].includes(String(raw.imageAlignX || '').toLowerCase()) ? String(raw.imageAlignX).toLowerCase() : 'center',
                imageAlignY: ['top', 'center', 'bottom'].includes(String(raw.imageAlignY || '').toLowerCase()) ? String(raw.imageAlignY).toLowerCase() : 'center',
                boxBackground: /^#[0-9a-f]{6}$/i.test(String(raw.boxBackground || '')) ? String(raw.boxBackground).toLowerCase() : '#ffffff',
                boxTransparent: raw.boxTransparent !== false,
                focalX: clamp(parseInt(raw.focalX || 50, 10) || 50, 0, 100),
                focalY: clamp(parseInt(raw.focalY || 50, 10) || 50, 0, 100),
                manualX: clamp(parseInt(raw.manualX || 0, 10) || 0, -4000, 4000),
                manualY: clamp(parseInt(raw.manualY || 0, 10) || 0, -4000, 4000),
                manualW: clamp(parseInt(raw.manualW || 320, 10) || 320, 1, 4000),
                manualH: clamp(parseInt(raw.manualH || 240, 10) || 240, 1, 4000),
                lockAspect: raw.lockAspect !== false
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
    window.H18CleanHistory = { labels: function () { return undoStack.map(function (entry) { return entry.label; }); } };
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
            if (isFloatingButton(node)) { return; }
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
            const rows = Math.max(1, Math.ceil((Math.max(1, rect.height / editorScale()) + Math.max(0, parseInt(node.props.gapY || 0, 10) || 0)) / ROW_PX));
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
            const list = children(parentId).filter(function (node) { return !isFloatingButton(node); }).slice().sort(function (a, b) {
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
            const kids = children(parent.id).filter(function (child) { return !isFloatingButton(child); });
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
                    if (isFloatingButton(list[i]) || isFloatingButton(list[j])) { continue; }
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

    function autoFitButtons() {
        const changed = new Set();
        document.querySelectorAll('.h18-clean-node--button[data-node-id]').forEach(function (card) {
            const node = nodeById(card.getAttribute('data-node-id') || '');
            if (!node || node.type !== 'button' || node.props.autoSize === false) { return; }
            const button = card.querySelector(':scope > .h18-clean-node-preview--button .h18-clean-button-preview');
            const surface = card.parentElement;
            if (!button || !surface) { return; }
            const surfaceWidth = Math.max(1, surface.getBoundingClientRect().width);
            const unitPx = Math.max(0.1, surfaceWidth / UNITS);
            const rect = button.getBoundingClientRect();
            const nextW = clamp(Math.ceil(Math.max(1, rect.width) / unitPx), 1, UNITS - node.geometry.desktop.x);
            const nextH = clamp(Math.ceil(Math.max(1, rect.height) / editorRowPx()), 1, 4000);
            if (node.geometry.desktop.w !== nextW || node.geometry.desktop.h !== nextH) {
                node.geometry.desktop.w = nextW;
                node.geometry.desktop.h = nextH;
                changed.add(node.id);
            }
        });
        return changed;
    }

    function reconcileLayoutAfterRender(canvas) {
        const autoButtons = autoFitButtons();
        const materialized = materializeNaturalLeafHeights();
        autoButtons.forEach(function (id) { const node = nodeById(id); if (!isFloatingButton(node)) { materialized.add(id); } });
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
        return Math.max(MIN_SPLIT_H, Math.round(card.getBoundingClientRect().height / editorRowPx()));
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

    function dropPlacement(surface, event, parentId, width, movingId, paletteType) {
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
        const movingNode = movingId ? nodeById(movingId) : null;
        const paletteFloatingButton = String(paletteType || '').toLowerCase() === 'button';
        if (isFloatingButton(movingNode) || paletteFloatingButton) {
            const overlayWidth = paletteFloatingButton ? Math.min(30, UNITS) : width;
            const pointerRow = clamp(Math.round((event.clientY - rect.top) / editorRowPx()), 0, 10000);
            const movingH = movingNode ? Math.max(1, movingNode.geometry.desktop.h || MIN_SPLIT_H) : MIN_SPLIT_H;
            placement.w = clamp(overlayWidth, 1, UNITS);
            placement.x = clamp(Math.round(pointerUnit - (placement.w / 2)), 0, UNITS - placement.w);
            placement.y = Math.max(0, pointerRow - Math.floor(movingH / 2));
            placement.targetId = '';
            placement.zone = 'overlay';
            placement.bandIds = [];
            placement.targetGeometry = null;
            return placement;
        }
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
        const defaultRows = { section: 20, container: 16, text: 14, image: 20, button: 8, menu: 10 };
        const defaultH = Math.max(MIN_SPLIT_H, parseInt(defaultRows[type] || MIN_SPLIT_H, 10) || MIN_SPLIT_H);
        const newProps = normalizeProps(type, {});
        if (type === 'button' && p.zone === 'overlay') { newProps.placementMode = 'overlay'; }
        if (PARENT_TYPES.includes(type)) { newProps.minHeightRows = defaultH; }
        if (type === 'text') { newProps.padding = 12; }
        const desktop = normalizeDevice({ x: p.x, y: p.y, w: p.w || defaultW, h: defaultH }, false);
        state.nodes.push({
            id: id,
            type: type,
            parentId: parentId,
            order: nextOrder(parentId),
            geometry: {
                desktop: desktop,
                tablet: Object.assign({}, desktop, { inheritDesktop: true }),
                mobile: { x: 0, y: 0, w: 120, h: defaultH, inheritDesktop: true }
            },
            props: newProps
        });
        reorderForPlacement(id, parentId, p);
        applyDestinationGeometry(id, p);
        selectedId = id;
        commit(before, 'Tilføj ' + typeLabel(type) + ' · ' + p.zone);
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
        commit(before, 'Slet ' + typeLabel(node.type));
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
        if (sourceSnapshot && !isFloatingButton(node)) { healSourceCell(sourceSnapshot, id); }
        reorderForPlacement(id, parentId, placement);
        applyDestinationGeometry(id, placement);
        node.geometry.desktop.w = Math.min(UNITS, Math.max(1, node.geometry.desktop.w));
        commit(before, 'Flyt ' + typeLabel(node.type) + ' · ' + placement.zone);
        render();
        diag('cell_drop_commit', { id: id, type: node.type, operation: 'move', fromParentId: from, toParentId: parentId, dropZone: placement.zone, targetId: placement.targetId || '', placement: clone(placement), state: structuralSummary() });
    }

    function applyCardGeometry(card, node, geometry) {
        if (isFloatingButton(node)) {
            card.style.position = 'absolute';
            card.style.gridColumn = 'auto';
            card.style.gridRow = 'auto';
            card.style.left = ((geometry.x / UNITS) * 100) + '%';
            card.style.top = String(Math.max(0, geometry.y) * ROW_PX) + 'px';
            card.style.width = ((geometry.w / UNITS) * 100) + '%';
            card.style.height = geometry.h > 0 ? String(geometry.h * ROW_PX) + 'px' : 'auto';
            card.style.minHeight = geometry.h > 0 ? String(geometry.h * ROW_PX) + 'px' : '';
            card.style.zIndex = String(clamp(parseInt(node.props.zIndex || 20, 10) || 20, 1, 200));
            card.style.marginTop = '0px';
            card.setAttribute('data-h18-floating', '1');
            card.setAttribute('data-h18-explicit-grid', '1');
            card.setAttribute('data-geometry', [geometry.x, geometry.y, geometry.w, geometry.h].join(','));
            return;
        }
        card.style.position = 'relative';
        card.style.left = '';
        card.style.top = '';
        card.style.width = '';
        card.style.zIndex = '';
        card.removeAttribute('data-h18-floating');
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
        if (PARENT_TYPES.includes(node.type)) {
            const background = /^#[0-9a-f]{6}$/i.test(String(props.background || '')) ? String(props.background).toLowerCase() : 'transparent';
            card.style.background = background;
            card.style.borderRadius = clamp(parseInt(props.radius || 0, 10) || 0, 0, 100) + 'px';
            card.setAttribute('data-h18-parent-painted-box', '1');
            card.removeAttribute('data-h18-leaf-transparent');
        } else if (node.type === 'text' || node.type === 'menu' || node.type === 'image') {
            const transparent = node.type === 'image' ? props.boxTransparent !== false : props.backgroundTransparent !== false;
            const fallback = node.type === 'image' ? '#ffffff' : (node.type === 'menu' ? '#30382a' : '#ffffff');
            const requested = node.type === 'image' ? props.boxBackground : props.background;
            const background = transparent ? 'transparent' : (/^#[0-9a-f]{6}$/i.test(String(requested || '')) ? String(requested).toLowerCase() : fallback);
            card.style.background = background;
            card.style.borderRadius = clamp(parseInt(props.radius || 0, 10) || 0, 0, 100) + 'px';
            card.setAttribute('data-h18-leaf-transparent', transparent ? '1' : '0');
        } else {
            card.removeAttribute('data-h18-leaf-transparent');
        }
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
            wrap.style.display = 'flex';
            wrap.style.flexDirection = 'column';
            wrap.style.justifyContent = ({ top: 'flex-start', center: 'center', bottom: 'flex-end' })[node.props.verticalAlign || 'top'] || 'flex-start';
            wrap.style.height = '100%';
            wrap.style.boxSizing = 'border-box';
            wrap.style.fontFamily = fontCss(node.props.fontFamily || 'system');
            wrap.style.fontSize = String(node.props.fontSize || 16) + 'px';
            wrap.style.fontWeight = String(node.props.fontWeight || 400);
            wrap.style.lineHeight = String(node.props.lineHeight || 1.5);
            wrap.style.letterSpacing = String(node.props.letterSpacing || 0) + 'px';
            const heading = String(node.props.heading || '').trim();
            if (heading) {
                const headingLevel = ['h2', 'h3', 'h4', 'h5', 'h6'].includes(node.props.headingLevel) ? node.props.headingLevel : 'h2';
                const title = document.createElement(headingLevel);
                title.className = 'h18-clean-text-heading';
                title.textContent = heading;
                title.style.fontFamily = fontCss(node.props.headingFontFamily || 'body', node.props.fontFamily || 'system');
                title.style.fontSize = headingPx(node.props) + 'px';
                title.style.fontWeight = String(node.props.headingFontWeight || 700);
                title.style.lineHeight = String(node.props.headingLineHeight || 1.2);
                title.style.letterSpacing = String(node.props.headingLetterSpacing || 0) + 'px';
                wrap.appendChild(title);
            }
            const body = document.createElement('div');
            body.className = 'h18-clean-text-body';
            body.innerHTML = richPreviewHtml(String(node.props.text || 'Ny tekst')) || 'Tekst';
            body.querySelectorAll('a').forEach(function (link) { link.addEventListener('click', function (event) { event.preventDefault(); }); });
            wrap.appendChild(body);
        } else if (node.type === 'button') {
            wrap.classList.add('h18-clean-node-preview--button');
            const button = document.createElement('span');
            button.className = 'h18-clean-button-preview';
            button.textContent = String(node.props.text || 'Knap');
            button.style.display = 'flex';
            button.style.alignItems = 'center';
            button.style.justifyContent = 'center';
            button.style.width = node.props.autoSize === false ? '100%' : 'max-content';
            button.style.height = node.props.autoSize === false ? '100%' : 'auto';
            button.style.boxSizing = 'border-box';
            button.style.background = node.props.background || '#30382a';
            button.style.color = node.props.textColor || '#ffffff';
            button.style.borderRadius = String(node.props.radius || 0) + 'px';
            button.style.padding = String(node.props.paddingY || 10) + 'px ' + String(node.props.paddingX || 20) + 'px';
            wrap.appendChild(button);
        } else if (node.type === 'menu') {
            wrap.classList.add('h18-clean-node-preview--menu');
            const menus = Array.isArray(CFG.menus) ? CFG.menus : [];
            const menuDef = menus.find(function (entry) { return parseInt(entry.id || 0, 10) === parseInt(node.props.menuId || 0, 10); }) || null;
            wrap.style.display = 'flex';
            wrap.style.alignItems = 'center';
            wrap.style.boxSizing = 'border-box';
            wrap.style.padding = String(node.props.paddingY || 8) + 'px ' + String(node.props.paddingX || 8) + 'px';
            wrap.style.borderRadius = String(node.props.radius || 0) + 'px';
            wrap.style.background = node.props.backgroundTransparent === false ? (node.props.background || '#30382a') : 'transparent';
            if (!menuDef) {
                wrap.textContent = 'Vælg WordPress-menu i Inspector';
            } else {
                const nav = document.createElement('div');
                nav.className = 'h18-clean-menu-preview';
                nav.style.display = 'flex';
                nav.style.width = '100%';
                nav.style.flexDirection = node.props.orientation === 'vertical' ? 'column' : 'row';
                nav.style.flexWrap = node.props.mobileMode === 'wrap' ? 'wrap' : 'nowrap';
                nav.style.justifyContent = ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-end';
                nav.style.alignItems = node.props.orientation === 'vertical' ? ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-start' : 'center';
                nav.style.gap = String(node.props.menuGap || 24) + 'px';
                nav.style.fontSize = String(node.props.fontSize || 16) + 'px';
                nav.style.fontWeight = String(node.props.fontWeight || 600);
                const items = Array.isArray(menuDef.items) ? menuDef.items.filter(function (item) { return parseInt(item.parent || 0, 10) === 0; }) : [];
                const previewDevice = document.body ? String(document.body.getAttribute('data-h18-clean-device') || 'desktop') : 'desktop';
                if (previewDevice === 'mobile' && node.props.mobileMode === 'hamburger') {
                    nav.classList.add('is-mobile-hamburger-preview');
                    nav.style.justifyContent = node.props.align === 'left' ? 'flex-start' : 'flex-end';
                    const toggle = document.createElement('button');
                    toggle.type = 'button';
                    toggle.className = 'h18-vd-menu-preview-toggle';
                    toggle.textContent = '☰ Menu';
                    toggle.style.color = node.props.textColor || '#ffffff';
                    toggle.addEventListener('click', function (event) {
                        event.preventDefault(); event.stopPropagation();
                        nav.classList.toggle('is-open');
                        toggle.textContent = nav.classList.contains('is-open') ? '✕ Luk' : '☰ Menu';
                    });
                    nav.appendChild(toggle);
                    const previewList = document.createElement('div');
                    previewList.className = 'h18-vd-menu-preview-mobile-list is-' + (node.props.mobilePresentation || 'dropdown');
                    items.forEach(function (item) { const label = document.createElement('span'); label.textContent = String(item.title || 'Menupunkt'); label.style.color = node.props.textColor || '#ffffff'; previewList.appendChild(label); });
                    nav.appendChild(previewList);
                } else if (!items.length) {
                    nav.textContent = menuDef.name || 'Tom menu';
                } else {
                    items.forEach(function (item) {
                        const label = document.createElement('span');
                        label.textContent = String(item.title || 'Menupunkt');
                        label.style.color = node.props.textColor || '#ffffff';
                        label.style.whiteSpace = 'nowrap';
                        nav.appendChild(label);
                    });
                }
                wrap.appendChild(nav);
            }
        } else if (node.type === 'image') {
            wrap.classList.add('h18-clean-node-preview--image');
            const alignX = ['left', 'center', 'right'].includes(node.props.imageAlignX) ? node.props.imageAlignX : 'center';
            const alignY = ['top', 'center', 'bottom'].includes(node.props.imageAlignY) ? node.props.imageAlignY : 'center';
            wrap.style.justifyContent = ({ left: 'flex-start', center: 'center', right: 'flex-end' })[alignX];
            wrap.style.alignItems = ({ top: 'flex-start', center: 'center', bottom: 'flex-end' })[alignY];
            wrap.style.backgroundColor = node.props.boxTransparent === false ? normalizeColor(node.props.boxBackground || '#ffffff') : 'transparent';
            if (node.props.url) {
                const img = document.createElement('img');
                img.src = node.props.url;
                img.alt = node.props.alt || '';
                const fit = ['cover', 'contain', 'original', 'stretch'].includes(node.props.fit) ? node.props.fit : 'contain';
                const posX = ({ left: '0%', center: '50%', right: '100%' })[alignX];
                const posY = ({ top: '0%', center: '50%', bottom: '100%' })[alignY];
                if (fit === 'original') {
                    img.style.width = 'auto';
                    img.style.height = 'auto';
                    img.style.maxWidth = '100%';
                    img.style.maxHeight = '100%';
                    img.style.objectFit = 'contain';
                } else {
                    img.style.width = '100%';
                    img.style.height = '100%';
                    img.style.maxWidth = 'none';
                    img.style.maxHeight = 'none';
                    img.style.objectFit = fit === 'stretch' ? 'fill' : fit;
                }
                img.style.objectPosition = fit === 'cover' ? (node.props.focalX + '% ' + node.props.focalY + '%') : (posX + ' ' + posY);
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
        return ({ above: '↑ DEL CELLEN OVER', below: '↓ DEL CELLEN UNDER', left: '← DEL CELLEN VENSTRE', right: 'DEL CELLEN HØJRE →', inside: 'IND I KASSEN', 'inside-empty': 'IND I KASSEN', free: 'FRI PLACERING', overlay: 'FLYDENDE · FRI PLACERING' })[zone] || zone;
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
            const placement = dropPlacement(surface, event, parentId, width, payload.kind === 'node' ? payload.id : '', payload.kind === 'palette' ? payload.type : '');
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
                const placement = dropPlacement(surface, event, parentId, defaultWidth(payload.type, parentId), '', payload.type);
                clearDropGuide();
                addNode(payload.type, parentId, 'palette_drop', placement);
                dragPaletteType = '';
                return;
            }
            const movingNode = nodeById(payload.id);
            if (!movingNode) { clearDragState(); return; }
            const placement = dropPlacement(surface, event, parentId, movingNode.geometry.desktop.w, payload.id, '');
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
            card.className = 'h18-clean-node h18-clean-node--' + node.type + (isFloatingButton(node) ? ' is-floating' : '') + (selectedId === node.id ? ' is-selected' : '');
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
            title.textContent = ({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP',menu:'MENU'}[node.type] || node.type.toUpperCase()) + ' · ' + node.id.slice(-8);
            header.appendChild(move);
            header.appendChild(title);
            card.appendChild(header);
            if (!PARENT_TYPES.includes(node.type)) {
                try {
                    card.appendChild(cardContent(node));
                } catch (error) {
                    const failed = document.createElement('div');
                    failed.className = 'h18-clean-render-error';
                    failed.textContent = 'Elementet kunne ikke vises: ' + (error && error.message ? error.message : 'ukendt render-fejl');
                    card.appendChild(failed);
                    diag('node_render_error', { id: node.id, type: node.type, message: String(error && error.message || error || 'unknown') });
                }
            }

            if (PARENT_TYPES.includes(node.type)) {
                const inner = document.createElement('div');
                inner.className = 'h18-clean-surface h18-clean-inner-surface';
                const p = node.props || {};
                inner.style.background = 'transparent';
                inner.style.borderRadius = 'inherit';
                inner.style.padding = (p.padding || 0) + 'px';
                try {
                    renderSurface(node.id, inner);
                } catch (error) {
                    const failed = document.createElement('div');
                    failed.className = 'h18-clean-render-error';
                    failed.textContent = 'Indholdet i denne ' + typeLabel(node.type) + ' kunne ikke vises fuldt: ' + (error && error.message ? error.message : 'ukendt render-fejl');
                    inner.appendChild(failed);
                    diag('surface_render_error', { id: node.id, type: node.type, message: String(error && error.message || error || 'unknown') });
                }
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
        const startH = g.h > 0 ? g.h : Math.max(1, Math.round(rect.height / editorRowPx()));
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
        const dy = Math.round((event.clientY - resize.startY) / editorRowPx());
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
        if (resizedNode && resizedNode.type === 'button') { resizedNode.props.autoSize = false; }
        commit(current.before, 'Ændr størrelse på ' + typeLabel((nodeById(current.id) || {}).type));
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
        let html = '<div class="h18-clean-inspector-head"><strong>' + escapeHtml(({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP',menu:'MENU'}[node.type] || node.type.toUpperCase())) + '</strong><code>' + escapeHtml(node.id) + '</code></div>';
        html += '<div class="h18-clean-field-grid"><label>X / 120<input data-field="gx" type="number" min="0" max="119" value="' + g.x + '"></label><label>Bredde / 120<input data-field="gw" type="number" min="1" max="120" value="' + g.w + '"></label><label>Y · 8px<input data-field="gy" type="number" value="' + g.y + '"></label><label>Højde · 8px<input data-field="gh" type="number" min="0" value="' + g.h + '"></label></div>';
        if (node.type === 'text') {
            html += '<label>Overskrift <span class="description">(valgfri)</span><input data-field="heading" type="text" value="' + escapeAttr(node.props.heading || '') + '"></label>';
            html += '<label>Overskrifttype<select data-field="headingLevel"><option value="h2"' + (node.props.headingLevel === 'h2' ? ' selected' : '') + '>H2</option><option value="h3"' + (node.props.headingLevel === 'h3' ? ' selected' : '') + '>H3</option><option value="h4"' + (node.props.headingLevel === 'h4' ? ' selected' : '') + '>H4</option><option value="h5"' + (node.props.headingLevel === 'h5' ? ' selected' : '') + '>H5</option><option value="h6"' + (node.props.headingLevel === 'h6' ? ' selected' : '') + '>H6</option></select></label>';
            html += '<label>Tekst<textarea data-field="text" rows="8">' + escapeHtml(node.props.text || '') + '</textarea></label>';
            html += '<label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label>';
            html += '<label>Lodret justering<select data-field="verticalAlign"><option value="top"' + (node.props.verticalAlign === 'top' ? ' selected' : '') + '>Top</option><option value="center"' + (node.props.verticalAlign === 'center' ? ' selected' : '') + '>Midt</option><option value="bottom"' + (node.props.verticalAlign === 'bottom' ? ' selected' : '') + '>Bund</option></select></label>';
            html += '<div class="h18-vd-typography"><strong>Typografi · brødtekst</strong><div class="h18-clean-field-grid"><label>Skrifttype<select data-field="fontFamily">' + fontOptions(node.props.fontFamily || 'system', false) + '</select></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="120" value="' + (node.props.fontSize || 16) + '"></label><label>Tykkelse<select data-field="fontWeight">' + [300,400,500,600,700,800,900].map(function (v) { return '<option value="' + v + '"' + (parseInt(node.props.fontWeight || 400, 10) === v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label><label>Linjeafstand<input data-field="lineHeight" type="number" step="0.1" min="0.8" max="3" value="' + (node.props.lineHeight || 1.5) + '"></label><label>Bogstavafstand px<input data-field="letterSpacing" type="number" step="0.1" min="-10" max="30" value="' + (node.props.letterSpacing || 0) + '"></label></div><strong>Typografi · overskrift</strong><div class="h18-clean-field-grid"><label>Skrifttype<select data-field="headingFontFamily">' + fontOptions(node.props.headingFontFamily || 'body', true) + '</select></label><label>Størrelse px <span class="description">(0 = automatisk)</span><input data-field="headingFontSize" type="number" min="0" max="160" value="' + (node.props.headingFontSize || 0) + '"></label><label>Tykkelse<select data-field="headingFontWeight">' + [300,400,500,600,700,800,900].map(function (v) { return '<option value="' + v + '"' + (parseInt(node.props.headingFontWeight || 700, 10) === v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label><label>Linjeafstand<input data-field="headingLineHeight" type="number" step="0.1" min="0.8" max="3" value="' + (node.props.headingLineHeight || 1.2) + '"></label><label>Bogstavafstand px<input data-field="headingLetterSpacing" type="number" step="0.1" min="-10" max="30" value="' + (node.props.headingLetterSpacing || 0) + '"></label></div></div>';
        } else if (node.type === 'button') {
            html += '<label>Knaptekst<input data-field="buttonText" type="text" value="' + escapeAttr(node.props.text || 'Knap') + '"></label>';
            html += '<label>Linktype<select data-field="linkType"><option value="page"' + (node.props.linkType === 'page' ? ' selected' : '') + '>Intern side</option><option value="url"' + (node.props.linkType === 'url' ? ' selected' : '') + '>Ekstern URL</option><option value="anchor"' + (node.props.linkType === 'anchor' ? ' selected' : '') + '>Anker</option><option value="email"' + (node.props.linkType === 'email' ? ' selected' : '') + '>E-mail</option><option value="phone"' + (node.props.linkType === 'phone' ? ' selected' : '') + '>Telefon</option></select></label>';
            if (node.props.linkType === 'page') {
                html += '<label>Intern side<select data-field="pageId"><option value="0">Vælg side…</option>' + (Array.isArray(CFG.pages) ? CFG.pages.map(function (page) { const id = parseInt(page.id || 0, 10) || 0; return '<option value="' + id + '"' + (parseInt(node.props.pageId || 0, 10) === id ? ' selected' : '') + '>' + escapeHtml(String(page.title || ('Side ' + id))) + '</option>'; }).join('') : '') + '</select></label>';
            } else {
                const linkLabel = ({url:'URL',anchor:'Anker, fx #kontakt',email:'E-mailadresse',phone:'Telefonnummer'})[node.props.linkType] || 'Destination';
                html += '<label>' + linkLabel + '<input data-field="url" type="text" value="' + escapeAttr(node.props.url || '') + '"></label>';
            }
            html += '<label class="h18-clean-checkbox"><input data-field="targetBlank" type="checkbox"' + (node.props.targetBlank ? ' checked' : '') + '> Åbn i ny fane</label>';
            html += '<label>Placering<select data-field="placementMode"><option value="normal"' + (node.props.placementMode !== 'overlay' ? ' selected' : '') + '>Normal i layout</option><option value="overlay"' + (node.props.placementMode === 'overlay' ? ' selected' : '') + '>Flydende i område</option></select></label>';
            if (node.props.placementMode === 'overlay') { html += '<label>Lag<input data-field="zIndex" type="number" min="1" max="200" value="' + (node.props.zIndex || 20) + '"><span class="description">Højere lag ligger foran andre elementer. Knappen flyder frit i sin aktuelle Side/Sektion/Kasse og flyttes med ✥ eller X/Y.</span></label>'; }
            html += '<label class="h18-clean-checkbox"><input data-field="autoSize" type="checkbox"' + (node.props.autoSize !== false ? ' checked' : '') + '> Automatisk størrelse efter tekst og padding</label>';
            html += '<div class="h18-clean-field-grid"><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#30382a') + '"></label><label>Tekstfarve<input data-field="textColor" type="color" value="' + escapeAttr(node.props.textColor || '#ffffff') + '"></label><label>Hover baggrund<input data-field="hoverBackground" type="color" value="' + escapeAttr(node.props.hoverBackground || '#525a5f') + '"></label><label>Hover tekst<input data-field="hoverTextColor" type="color" value="' + escapeAttr(node.props.hoverTextColor || '#ffffff') + '"></label><label>Focus-farve<input data-field="focusColor" type="color" value="' + escapeAttr(node.props.focusColor || '#c3ae83') + '"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 0) + '"></label><label>Padding X<input data-field="paddingX" type="number" min="0" max="120" value="' + (node.props.paddingX || 20) + '"></label><label>Padding Y<input data-field="paddingY" type="number" min="0" max="120" value="' + (node.props.paddingY || 10) + '"></label></div>';
        } else if (node.type === 'menu') {
            html += '<div class="h18-vd-menu-group"><h3>Indhold</h3><label>Menu<select data-field="menuId"><option value="0">Vælg menu…</option>' + (Array.isArray(CFG.menus) ? CFG.menus.map(function (menu) { const id = parseInt(menu.id || 0, 10) || 0; return '<option value="' + id + '"' + (parseInt(node.props.menuId || 0, 10) === id ? ' selected' : '') + '>' + escapeHtml(String(menu.name || ('Menu ' + id))) + '</option>'; }).join('') : '') + '</select></label>';
            if (CFG.menuAdminUrl) { html += '<p><a class="button" href="' + escapeAttr(String(CFG.menuAdminUrl)) + '">Redigér menupunkter</a></p>'; }
            html += '<p class="description">Menupunkterne ligger ét sted i WordPress/Manager. Visual Designer gemmer kun valg og udseende.</p></div>';
            html += '<div class="h18-vd-menu-group"><h3>Layout</h3><div class="h18-clean-field-grid"><label>Retning<select data-field="orientation"><option value="horizontal"' + (node.props.orientation !== 'vertical' ? ' selected' : '') + '>Vandret</option><option value="vertical"' + (node.props.orientation === 'vertical' ? ' selected' : '') + '>Lodret</option></select></label><label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Center</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label><label>Afstand px<input data-field="menuGap" type="number" min="0" max="120" value="' + (node.props.menuGap || 24) + '"></label><label>Padding X<input data-field="paddingX" type="number" min="0" max="120" value="' + (node.props.paddingX || 8) + '"></label><label>Padding Y<input data-field="paddingY" type="number" min="0" max="120" value="' + (node.props.paddingY || 8) + '"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 0) + '"></label></div></div>';
            html += '<div class="h18-vd-menu-group"><h3>Tekst</h3><div class="h18-clean-field-grid"><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="64" value="' + (node.props.fontSize || 16) + '"></label><label>Tykkelse<select data-field="fontWeight">' + [300,400,500,600,700,800,900].map(function (v) { return '<option value="' + v + '"' + (parseInt(node.props.fontWeight || 600, 10) === v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label></div></div>';
            html += '<div class="h18-vd-menu-group"><h3>Farver</h3><label class="h18-clean-checkbox"><input data-field="backgroundTransparent" type="checkbox"' + (node.props.backgroundTransparent !== false ? ' checked' : '') + '> Gennemsigtig baggrund</label><div class="h18-clean-field-grid"><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#30382a') + '"></label><label>Normal<input data-field="textColor" type="color" value="' + escapeAttr(node.props.textColor || '#ffffff') + '"></label><label>Hover<input data-field="hoverTextColor" type="color" value="' + escapeAttr(node.props.hoverTextColor || '#c3ae83') + '"></label><label>Aktiv side<input data-field="activeTextColor" type="color" value="' + escapeAttr(node.props.activeTextColor || '#c3ae83') + '"></label></div></div>';
            html += '<div class="h18-vd-menu-group"><h3>Mobil</h3><label>Mobilvisning<select data-field="mobileMode"><option value="hamburger"' + (node.props.mobileMode === 'hamburger' ? ' selected' : '') + '>Hamburger</option><option value="vertical"' + (node.props.mobileMode === 'vertical' ? ' selected' : '') + '>Lodret menu</option><option value="wrap"' + (node.props.mobileMode === 'wrap' ? ' selected' : '') + '>Ombryd menupunkter</option></select></label>';
            if (node.props.mobileMode === 'hamburger') { html += '<label>Åbn som<select data-field="mobilePresentation"><option value="dropdown"' + (node.props.mobilePresentation === 'dropdown' ? ' selected' : '') + '>Dropdown</option><option value="panel-right"' + (node.props.mobilePresentation === 'panel-right' ? ' selected' : '') + '>Panel fra højre</option><option value="panel-left"' + (node.props.mobilePresentation === 'panel-left' ? ' selected' : '') + '>Panel fra venstre</option></select></label><label class="h18-clean-checkbox"><input data-field="mobileCloseOnSelect" type="checkbox"' + (node.props.mobileCloseOnSelect !== false ? ' checked' : '') + '> Luk efter valg</label><label class="h18-clean-checkbox"><input data-field="mobileCloseOutside" type="checkbox"' + (node.props.mobileCloseOutside !== false ? ' checked' : '') + '> Luk ved klik udenfor</label>'; }
            html += '<p class="description">Mobil bruger de samme menupunkter som Desktop; kun præsentationen ændres.</p></div>';
        } else if (node.type === 'image') {
            html += '<button type="button" class="button" id="h18-clean-pick-image">Vælg / skift billede</button><p class="description">PNG, JPG/JPEG, WebP, GIF og andre image/*-formater som WordPress tillader. PNG-transparens bevares.</p>';
            html += '<label>Billede i boksen<select data-field="fit"><option value="contain"' + (node.props.fit === 'contain' ? ' selected' : '') + '>Vis hele billedet</option><option value="cover"' + (node.props.fit === 'cover' ? ' selected' : '') + '>Fyld boksen · beskær</option><option value="original"' + (node.props.fit === 'original' ? ' selected' : '') + '>Original størrelse</option><option value="stretch"' + (node.props.fit === 'stretch' ? ' selected' : '') + '>Stræk til boks</option></select></label>';
            html += '<div class="h18-clean-field-grid"><label>Vandret placering<select data-field="imageAlignX"><option value="left"' + (node.props.imageAlignX === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.imageAlignX === 'center' ? ' selected' : '') + '>Center</option><option value="right"' + (node.props.imageAlignX === 'right' ? ' selected' : '') + '>Højre</option></select></label><label>Lodret placering<select data-field="imageAlignY"><option value="top"' + (node.props.imageAlignY === 'top' ? ' selected' : '') + '>Top</option><option value="center"' + (node.props.imageAlignY === 'center' ? ' selected' : '') + '>Center</option><option value="bottom"' + (node.props.imageAlignY === 'bottom' ? ' selected' : '') + '>Bund</option></select></label></div>';
            html += '<label class="h18-clean-checkbox"><input data-field="boxTransparent" type="checkbox"' + (node.props.boxTransparent !== false ? ' checked' : '') + '> Gennemsigtig boksbaggrund</label>';
            html += '<label>Boksbaggrund<input data-field="boxBackground" type="color" value="' + escapeAttr(node.props.boxBackground || '#ffffff') + '"></label>';
            html += '<div class="h18-clean-field-grid"><label>Fokus X % <span class="description">(beskæring)</span><input data-field="focalX" type="number" min="0" max="100" value="' + node.props.focalX + '"></label><label>Fokus Y % <span class="description">(beskæring)</span><input data-field="focalY" type="number" min="0" max="100" value="' + node.props.focalY + '"></label></div>';
            html += '<p class="description">De grønne resize-punkter ændrer kun billedboksen. Billedet følger indstillingen ovenfor.</p>';
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
                else if (field === 'heading') { current.props.heading = String(control.value || ''); }
                else if (field === 'headingLevel') { current.props.headingLevel = ['h2', 'h3', 'h4', 'h5', 'h6'].includes(control.value) ? control.value : 'h2'; }
                else if (field === 'text') { current.props.text = String(control.value || ''); }
                else if (field === 'align') { current.props.align = ['left', 'center', 'right'].includes(control.value) ? control.value : 'left'; }
                else if (field === 'verticalAlign') { current.props.verticalAlign = ['top', 'center', 'bottom'].includes(control.value) ? control.value : 'top'; }
                else if (field === 'fontFamily') { current.props.fontFamily = normalizeFontToken(control.value, false); }
                else if (field === 'fontSize') { current.props.fontSize = clamp(parseInt(control.value || 16, 10) || 16, 8, 120); }
                else if (field === 'fontWeight') { current.props.fontWeight = clamp(parseInt(control.value || 400, 10) || 400, 100, 900); }
                else if (field === 'lineHeight') { current.props.lineHeight = Math.max(0.8, Math.min(3, parseFloat(control.value || 1.5) || 1.5)); }
                else if (field === 'letterSpacing') { current.props.letterSpacing = Math.max(-10, Math.min(30, parseFloat(control.value || 0) || 0)); }
                else if (field === 'headingFontFamily') { current.props.headingFontFamily = normalizeFontToken(control.value, true); }
                else if (field === 'headingFontSize') { current.props.headingFontSize = clamp(parseInt(control.value || 0, 10) || 0, 0, 160); }
                else if (field === 'headingFontWeight') { current.props.headingFontWeight = clamp(parseInt(control.value || 700, 10) || 700, 100, 900); }
                else if (field === 'headingLineHeight') { current.props.headingLineHeight = Math.max(0.8, Math.min(3, parseFloat(control.value || 1.2) || 1.2)); }
                else if (field === 'headingLetterSpacing') { current.props.headingLetterSpacing = Math.max(-10, Math.min(30, parseFloat(control.value || 0) || 0)); }
                else if (field === 'buttonText') { current.props.text = String(control.value || 'Knap'); }
                else if (field === 'linkType') { current.props.linkType = ['page', 'url', 'anchor', 'email', 'phone'].includes(control.value) ? control.value : 'url'; }
                else if (field === 'pageId') { current.props.pageId = parseInt(control.value || 0, 10) || 0; }
                else if (field === 'url') { current.props.url = String(control.value || ''); }
                else if (field === 'targetBlank') { current.props.targetBlank = !!control.checked; }
                else if (field === 'autoSize') { current.props.autoSize = !!control.checked; }
                else if (field === 'placementMode') { current.props.placementMode = control.value === 'overlay' ? 'overlay' : 'normal'; }
                else if (field === 'zIndex') { current.props.zIndex = clamp(parseInt(control.value || 20, 10) || 20, 1, 200); }
                else if (field === 'textColor') { current.props.textColor = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'hoverBackground') { current.props.hoverBackground = normalizeColor(control.value || '#525a5f'); }
                else if (field === 'hoverTextColor') { current.props.hoverTextColor = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'focusColor') { current.props.focusColor = normalizeColor(control.value || '#c3ae83'); }
                else if (field === 'paddingX') { current.props.paddingX = clamp(parseInt(control.value || 20, 10) || 20, 0, 120); }
                else if (field === 'paddingY') { current.props.paddingY = clamp(parseInt(control.value || 10, 10) || 10, 0, 120); }
                else if (field === 'menuId') { current.props.menuId = parseInt(control.value || 0, 10) || 0; }
                else if (field === 'orientation') { current.props.orientation = control.value === 'vertical' ? 'vertical' : 'horizontal'; }
                else if (field === 'mobileMode') { current.props.mobileMode = ['hamburger', 'vertical', 'wrap'].includes(control.value) ? control.value : 'hamburger'; }
                else if (field === 'mobilePresentation') { current.props.mobilePresentation = ['dropdown', 'panel-right', 'panel-left'].includes(control.value) ? control.value : 'dropdown'; }
                else if (field === 'mobileCloseOnSelect') { current.props.mobileCloseOnSelect = !!control.checked; }
                else if (field === 'mobileCloseOutside') { current.props.mobileCloseOutside = !!control.checked; }
                else if (field === 'activeTextColor') { current.props.activeTextColor = normalizeColor(control.value || '#c3ae83'); }
                else if (field === 'backgroundTransparent') { current.props.backgroundTransparent = !!control.checked; }
                else if (field === 'menuGap') { current.props.menuGap = clamp(parseInt(control.value || 24, 10) || 24, 0, 120); }
                else if (field === 'fit') { current.props.fit = ['cover', 'contain', 'original', 'stretch'].includes(control.value) ? control.value : 'contain'; }
                else if (field === 'imageAlignX') { current.props.imageAlignX = ['left', 'center', 'right'].includes(control.value) ? control.value : 'center'; }
                else if (field === 'imageAlignY') { current.props.imageAlignY = ['top', 'center', 'bottom'].includes(control.value) ? control.value : 'center'; }
                else if (field === 'boxTransparent') { current.props.boxTransparent = !!control.checked; }
                else if (field === 'boxBackground') { current.props.boxBackground = normalizeColor(control.value || '#ffffff'); }
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
                commit(before, 'Ændr ' + fieldLabel(field) + ' på ' + typeLabel(current.type));
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
            try {
                renderSurface('', canvas);
                reconcileLayoutAfterRender(canvas);
                canvas.removeAttribute('data-render-failed');
            } catch (error) {
                canvas.setAttribute('data-render-failed', '1');
                if (!canvas.querySelector('.h18-clean-root-render-error')) {
                    const failed = document.createElement('div');
                    failed.className = 'h18-clean-root-render-error';
                    failed.textContent = 'Designer-rendering fejlede, men layoutdata er bevaret: ' + (error && error.message ? error.message : 'ukendt fejl');
                    canvas.appendChild(failed);
                }
                diag('root_render_error', { message: String(error && error.message || error || 'unknown'), state: structuralSummary() });
            }
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
                if (note && !note.value) {
                    const labels = window.H18CleanHistory && typeof window.H18CleanHistory.labels === 'function' ? window.H18CleanHistory.labels() : [];
                    const compact = Array.isArray(labels) ? labels.filter(function (value, index, all) { return value && all.indexOf(value) === index; }).slice(-6) : [];
                    note.value = compact.length ? compact.join(' · ') : (lastAction || 'Gemt Visual Designer-layout');
                }
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