(function () {
    'use strict';

    const CFG = window.H18CleanEditor || {};
    const UNITS = Math.max(12, parseInt(CFG.units || 120, 10) || 120);
    const ROW_PX = Math.max(2, parseInt(CFG.rowPx || 8, 10) || 8);
    const POST_ID = parseInt(CFG.postId || 0, 10) || 0;
    const USER_ID = Math.max(0, parseInt(CFG.userId || 0, 10) || 0);
    const CONTEXT_LABEL = String(CFG.contextLabel || (POST_ID ? ('Side ' + POST_ID) : 'Global Designer'));
    const CLIPBOARD_KEY = 'h18-vd-clipboard-v1-u' + String(USER_ID);
    const TYPES = ['section', 'container', 'text', 'image', 'button', 'menu', 'spacer', 'divider', 'icon', 'badge', 'link', 'datalist', 'table', 'vehiclelist', 'vehicledetail', 'eventlist', 'eventdetail', 'eventvalue', 'eventimage', 'eventfacts', 'gallerylist', 'gallerydetail', 'eventfield', 'contactform', 'membershipform'];
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
    let nudgeSession = null;
    let memoryClipboard = null;
    let productivityNoticeTimer = 0;
    let tableCellSelection = null;

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
        return ({h1:44,h2:32,h3:28,h4:24,h5:20,h6:18})[String(props.headingLevel || 'h2')] || 32;
    }
    function typeLabel(type) { return ({section:'Sektion',container:'Kasse',text:'Tekst',image:'Billede',button:'Knap',menu:'Menu',spacer:'Mellemrum',divider:'Skillelinje',icon:'Ikon',badge:'Badge',link:'Link',datalist:'Data List',table:'Tabel',vehiclelist:'Køretøjsliste',vehicledetail:'Køretøjsdetalje',eventlist:'Eventliste',eventdetail:'Eventdetalje',eventvalue:'Eventværdi',eventimage:'Eventbillede',eventfacts:'Eventfaktabånd',gallerylist:'Gallerioversigt',gallerydetail:'Albumvisning',eventfield:'Eventfelt',contactform:'Kontaktformular',membershipform:'Bliv medlem-formular'})[String(type || '')] || String(type || 'Element'); }
    function isFloatingButton(node) { return !!(node && node.type === 'button' && node.props && node.props.placementMode === 'overlay'); }
    function fieldLabel(field) { return ({gx:'X-position',gw:'bredde',gy:'Y-position',gh:'højde',heading:'overskrift',headingLevel:'overskrifttype',text:'tekstindhold',align:'tekstjustering',verticalAlign:'lodret justering',fontFamily:'skrifttype',fontSize:'skriftstørrelse',fontWeight:'skrifttykkelse',lineHeight:'linjeafstand',letterSpacing:'bogstavafstand',headingFontFamily:'overskriftsskrifttype',headingFontSize:'overskriftsstørrelse',headingFontWeight:'overskriftstykkelse',headingLineHeight:'overskriftens linjeafstand',headingLetterSpacing:'overskriftens bogstavafstand',fit:'billedtilpasning',imageAlignX:'vandret billedplacering',imageAlignY:'lodret billedplacering',boxTransparent:'boksbaggrund',boxBackground:'boksbaggrundsfarve',focalX:'billedfokus X',focalY:'billedfokus Y',alt:'alt-tekst',background:'baggrund',radius:'hjørner',padding:'padding',borderWidth:'ramme',borderColor:'rammefarve',gapX:'Afstand X',gapY:'Afstand Y',offsetX:'finjustering X',offsetY:'finjustering Y',buttonText:'knaptekst',linkType:'linktype',pageId:'intern side',url:'linkdestination',targetBlank:'ny fane',textColor:'tekstfarve',hoverBackground:'hover-baggrund',hoverTextColor:'hover-tekstfarve',focusColor:'focus-farve',paddingX:'vandret padding',paddingY:'lodret padding',autoSize:'automatisk størrelse',placementMode:'placering',zIndex:'lag',menuId:'WordPress-menu',orientation:'menuretning',mobileMode:'mobilmenu',mobilePresentation:'mobilmenu-visning',mobileCloseOnSelect:'luk efter valg',mobileCloseOutside:'luk ved klik udenfor',activeTextColor:'aktiv menufarve',backgroundTransparent:'gennemsigtig baggrund',menuGap:'menuafstand'})[String(field || '')] || String(field || 'felt'); }
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
            gapY: clamp(parseInt(raw.gapY || 0, 10) || 0, 0, 200),
            offsetX: clamp(parseInt(raw.offsetX || 0, 10) || 0, -2000, 2000),
            offsetY: clamp(parseInt(raw.offsetY || 0, 10) || 0, -2000, 2000)
        };
    }

    function normalizePairRows(raw) {
        const source = Array.isArray(raw) ? raw : [];
        const rows = source.slice(0, 50).map(function (row) {
            row = row && typeof row === 'object' ? row : {};
            return { label: String(row.label || '').trim(), value: String(row.value || '').trim() };
        }).filter(function (row) { return row.label || row.value; });
        return rows.length ? rows : [{label:'Felt',value:'Værdi'},{label:'Eksempel',value:'Indhold'}];
    }
    function normalizeHeaders(raw) {
        const headers = (Array.isArray(raw) ? raw : []).slice(0, 12).map(function (item) { return String(item || '').trim(); }).filter(Boolean);
        return headers.length ? headers : ['Kolonne 1','Kolonne 2','Kolonne 3'];
    }
    function normalizeMatrixRows(raw, columns) {
        columns = clamp(parseInt(columns || 1, 10) || 1, 1, 12);
        const rows = (Array.isArray(raw) ? raw : []).slice(0, 50).map(function (row) {
            const source = Array.isArray(row) ? row : [];
            const cells = [];
            for (let i = 0; i < columns; i += 1) { cells.push(String(source[i] || '').trim()); }
            return cells;
        }).filter(function (row) { return row.join('').length > 0; });
        if (rows.length) { return rows; }
        const a = Array(columns).fill(''); const b = Array(columns).fill('');
        a[0] = 'Række 1'; b[0] = 'Række 2'; if (columns > 1) { a[1] = 'Værdi'; b[1] = 'Værdi'; }
        return [a,b];
    }
    function pairRowsText(rows) { return normalizePairRows(rows).map(function (row) { return row.label + ' | ' + row.value; }).join('\n'); }
    function parsePairRowsText(value) {
        return String(value || '').split(/\r?\n/).slice(0,50).map(function (line) {
            const parts = line.split('|'); return {label:String(parts.shift() || '').trim(),value:String(parts.join('|') || '').trim()};
        }).filter(function (row) { return row.label || row.value; });
    }
    function headersText(headers) { return normalizeHeaders(headers).join(' | '); }
    function parseHeadersText(value) { return normalizeHeaders(String(value || '').split('|')); }
    function matrixRowsText(rows, columns) { return normalizeMatrixRows(rows, columns).map(function (row) { return row.join(' | '); }).join('\n'); }
    function parseMatrixRowsText(value, columns) {
        const rows = String(value || '').split(/\r?\n/).slice(0,50).map(function (line) { return line.split('|').map(function (cell) { return cell.trim(); }); });
        return normalizeMatrixRows(rows, columns);
    }
    function vehicleRecords() {
        return Array.isArray(CFG.vehicleRecords) ? CFG.vehicleRecords.filter(function (record) { return record && record.id; }) : [];
    }
    function vehicleRecordById(recordId) {
        recordId = String(recordId || '');
        return vehicleRecords().find(function (record) { return String(record.id || '') === recordId; }) || null;
    }
    function vehicleCategory(record) {
        return record && record.fields && typeof record.fields === 'object' ? String(record.fields.category || '') : '';
    }
    function eventRecords() { return Array.isArray(CFG.eventRecords) ? CFG.eventRecords.filter(function (record) { return record && record.id; }) : []; }
    function eventRecordById(recordId) { recordId = String(recordId || ''); return eventRecords().find(function (record) { return String(record.id || '') === recordId; }) || null; }
    function eventDateLabel(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const start=String(fields.start||'').replace('T',' '), end=String(fields.end||'').replace('T',' '); return start&&end?(start+' – '+end):start; }
    function eventIsPast(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; let edge=String(fields.end||''); if(!edge){const start=String(fields.start||''); if(!start){return false;} edge=start.slice(0,10)+'T23:59:59';} const timestamp=Date.parse(edge); return Number.isFinite(timestamp)&&timestamp<Date.now(); }
    function galleryRecords() { return Array.isArray(CFG.galleryRecords) ? CFG.galleryRecords.filter(function (record) { return record && record.id; }) : []; }
    function galleryRecordById(recordId) { recordId=String(recordId||''); return galleryRecords().find(function(record){return String(record.id||'')===recordId;})||null; }
    function galleryImageCount(record) { const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; return Array.isArray(fields.imageIds)?fields.imageIds.length:(Array.isArray(record&&record.imageUrls)?record.imageUrls.length:0); }

    function iconLibrarySets() {
        const library = CFG.iconLibrary && typeof CFG.iconLibrary === 'object' ? CFG.iconLibrary : {};
        return Array.isArray(library.sets) ? library.sets : [];
    }
    function iconEntry(setKey, iconKey) {
        setKey = String(setKey || 'core'); iconKey = String(iconKey || 'star');
        for (const set of iconLibrarySets()) {
            if (String(set.key || '') !== setKey) { continue; }
            for (const category of (Array.isArray(set.categories) ? set.categories : [])) {
                for (const icon of (Array.isArray(category.icons) ? category.icons : [])) {
                    if (String(icon.key || '') === iconKey) { return {set:set, category:category, icon:icon}; }
                }
            }
        }
        return null;
    }
    function normalizeIconSelection(setKey, iconKey) {
        const direct = iconEntry(setKey, iconKey);
        if (direct) { return {set:String(direct.set.key), icon:String(direct.icon.key)}; }
        const legacy = iconEntry('core', iconKey);
        if (legacy) { return {set:'core', icon:String(legacy.icon.key)}; }
        return {set:'core', icon:'star'};
    }
    function registryIconSvgMarkup(setKey, iconKey) {
        const entry = iconEntry(setKey, iconKey);
        return entry && entry.icon && entry.icon.svg ? String(entry.icon.svg) : iconSvgMarkup(iconKey);
    }
    function currentIconLabel(setKey, iconKey) {
        const entry = iconEntry(setKey, iconKey);
        return entry ? String(entry.icon.label || entry.icon.key || iconKey) : String(iconKey || 'star');
    }

    function normalizeTableCellBorders(raw) {
        raw = raw && typeof raw === 'object' && !Array.isArray(raw) ? raw : {};
        const out = {}; let count = 0;
        Object.keys(raw).forEach(function (key) {
            if (count >= 700 || !/^(?:h\d+|r\d+c\d+)$/.test(key)) { return; }
            const cell = raw[key] && typeof raw[key] === 'object' ? raw[key] : {};
            ['top','right','bottom','left'].forEach(function (side) {
                if (!cell[side] || typeof cell[side] !== 'object') { return; }
                const value = cell[side];
                if (!out[key]) { out[key] = {}; }
                out[key][side] = {
                    enabled: value.enabled !== false,
                    width: clamp(parseInt(value.width != null ? value.width : 1, 10) || 0, 0, 10),
                    color: /^#[0-9a-f]{6}$/i.test(String(value.color || '')) ? String(value.color).toLowerCase() : '#dcdcde',
                    style: ['solid','dashed','dotted'].includes(String(value.style || '').toLowerCase()) ? String(value.style).toLowerCase() : 'solid'
                };
            });
            if (out[key]) { count += 1; }
        });
        return out;
    }
    function tableGrid(node) {
        const headers = normalizeHeaders(node && node.props ? node.props.headers : []);
        const rows = normalizeMatrixRows(node && node.props ? node.props.rows : [], headers.length);
        const grid = [headers.map(function (_value, col) { return 'h' + col; })];
        rows.forEach(function (row, rowIndex) { grid.push(row.map(function (_value, col) { return 'r' + rowIndex + 'c' + col; })); });
        const pos = {};
        grid.forEach(function (row, r) { row.forEach(function (key, c) { pos[key] = {row:r,col:c}; }); });
        return {headers:headers, rows:rows, grid:grid, pos:pos, rowCount:grid.length, colCount:headers.length};
    }
    function tableSelectionKeys(node) {
        if (!tableCellSelection || !node || tableCellSelection.nodeId !== node.id) { return []; }
        const grid = tableGrid(node);
        return (Array.isArray(tableCellSelection.keys) ? tableCellSelection.keys : []).filter(function (key) { return !!grid.pos[key]; });
    }
    function tableRangeKeys(node, fromKey, toKey) {
        const grid = tableGrid(node), a = grid.pos[fromKey], b = grid.pos[toKey];
        if (!a || !b) { return [toKey]; }
        const out = [];
        const minR = Math.min(a.row,b.row), maxR = Math.max(a.row,b.row), minC = Math.min(a.col,b.col), maxC = Math.max(a.col,b.col);
        for (let r=minR; r<=maxR; r+=1) { for (let c=minC; c<=maxC; c+=1) { if (grid.grid[r] && grid.grid[r][c]) { out.push(grid.grid[r][c]); } } }
        return out;
    }
    function tableNeighborKey(node, key, side) {
        const grid = tableGrid(node), p = grid.pos[key]; if (!p) { return ''; }
        const delta = {top:[-1,0],right:[0,1],bottom:[1,0],left:[0,-1]}[side];
        const r = p.row + delta[0], c = p.col + delta[1];
        return grid.grid[r] && grid.grid[r][c] ? grid.grid[r][c] : '';
    }
    function tableBaseSideEnabled(node, key, side) {
        const grid = tableGrid(node), p = grid.pos[key]; if (!p) { return false; }
        const mode = ['all','outer','inner','none'].includes(String(node.props.borderMode || 'all')) ? String(node.props.borderMode || 'all') : 'all';
        if (mode === 'all') { return true; }
        if (mode === 'none') { return false; }
        const outer = side === 'top' ? p.row === 0 : side === 'bottom' ? p.row === grid.rowCount - 1 : side === 'left' ? p.col === 0 : p.col === grid.colCount - 1;
        return mode === 'outer' ? outer : !outer;
    }
    function tableEffectiveSide(node, key, side) {
        const custom = node.props.cellBorders && node.props.cellBorders[key] && node.props.cellBorders[key][side];
        if (custom) { return custom; }
        return {
            enabled: tableBaseSideEnabled(node,key,side),
            width: clamp(parseInt(node.props.cellBorderWidth != null ? node.props.cellBorderWidth : 1,10) || 0,0,10),
            color: /^#[0-9a-f]{6}$/i.test(String(node.props.cellBorderColor || '')) ? String(node.props.cellBorderColor).toLowerCase() : '#dcdcde',
            style: ['solid','dashed','dotted'].includes(String(node.props.cellBorderStyle || '').toLowerCase()) ? String(node.props.cellBorderStyle).toLowerCase() : 'solid'
        };
    }
    function tableBorderCssValue(value) { return value && value.enabled && value.width > 0 ? (String(value.width) + 'px ' + value.style + ' ' + value.color) : '0'; }
    function applyTableCellBorders(element, node, key) {
        element.style.borderTop = tableBorderCssValue(tableEffectiveSide(node,key,'top'));
        element.style.borderRight = tableBorderCssValue(tableEffectiveSide(node,key,'right'));
        element.style.borderBottom = tableBorderCssValue(tableEffectiveSide(node,key,'bottom'));
        element.style.borderLeft = tableBorderCssValue(tableEffectiveSide(node,key,'left'));
    }
    function setTableCellSide(node, key, side, enabled, pen) {
        if (!node.props.cellBorders || typeof node.props.cellBorders !== 'object') { node.props.cellBorders = {}; }
        if (!node.props.cellBorders[key]) { node.props.cellBorders[key] = {}; }
        const value = {enabled:!!enabled,width:pen.width,color:pen.color,style:pen.style};
        node.props.cellBorders[key][side] = value;
        const opposite = {top:'bottom',right:'left',bottom:'top',left:'right'}[side];
        const neighbor = tableNeighborKey(node,key,side);
        if (neighbor) {
            if (!node.props.cellBorders[neighbor]) { node.props.cellBorders[neighbor] = {}; }
            node.props.cellBorders[neighbor][opposite] = clone(value);
        }
    }
    function applyTableBorderAction(node, keys, action, pen) {
        const selected = new Set(keys);
        function neighborSelected(key, side) { const n = tableNeighborKey(node,key,side); return !!n && selected.has(n); }
        keys.forEach(function (key) {
            if (action === 'none') { ['top','right','bottom','left'].forEach(function (side) { setTableCellSide(node,key,side,false,pen); }); return; }
            if (action === 'all') { ['top','right','bottom','left'].forEach(function (side) { setTableCellSide(node,key,side,true,pen); }); return; }
            if (action === 'outer') { ['top','right','bottom','left'].forEach(function (side) { if (!neighborSelected(key,side)) { setTableCellSide(node,key,side,true,pen); } }); return; }
            if (action === 'inner') { ['right','bottom'].forEach(function (side) { if (neighborSelected(key,side)) { setTableCellSide(node,key,side,true,pen); } }); return; }
            if (action === 'horizontal') { if (neighborSelected(key,'bottom')) { setTableCellSide(node,key,'bottom',true,pen); } return; }
            if (action === 'vertical') { if (neighborSelected(key,'right')) { setTableCellSide(node,key,'right',true,pen); } return; }
            if (['top','right','bottom','left'].includes(action) && !neighborSelected(key,action)) { setTableCellSide(node,key,action,true,pen); }
        });
    }
    function selectTableCell(node, key, event) {
        const current = tableCellSelection && tableCellSelection.nodeId === node.id ? tableCellSelection : {nodeId:node.id,keys:[],anchorKey:key};
        let keys = [];
        if (event.shiftKey && current.anchorKey) {
            keys = tableRangeKeys(node,current.anchorKey,key);
        } else if (event.ctrlKey || event.metaKey) {
            keys = Array.isArray(current.keys) ? current.keys.slice() : [];
            const index = keys.indexOf(key); if (index >= 0) { keys.splice(index,1); } else { keys.push(key); }
            if (!keys.length) { keys = [key]; }
        } else { keys = [key]; current.anchorKey = key; }
        tableCellSelection = {nodeId:node.id,keys:keys,anchorKey:current.anchorKey || key};
        selectedId = node.id;
        render();
    }

    function openIconLibrary() {
        const node = nodeById(selectedId); if (!node || node.type !== 'icon') { return; }
        const old = document.getElementById('h18-vd-icon-library-dialog'); if (old) { old.remove(); }
        const dialog = document.createElement('div'); dialog.id = 'h18-vd-icon-library-dialog'; dialog.className = 'h18-vd-icon-library-dialog';
        const backdrop = document.createElement('div'); backdrop.className = 'h18-vd-icon-library-backdrop'; dialog.appendChild(backdrop);
        const card = document.createElement('div'); card.className = 'h18-vd-icon-library-card'; dialog.appendChild(card);
        const head = document.createElement('div'); head.className = 'h18-vd-icon-library-head'; head.innerHTML = '<div><h2>Ikonbibliotek</h2><p class="description">Core icons følger med Designer. Module icons registreres af moduler. Egne SVG-ikoner er reserveret til en senere Custom icons-funktion.</p></div><button type="button" class="button" data-icon-close>Luk</button>'; card.appendChild(head);
        const tools = document.createElement('div'); tools.className = 'h18-vd-icon-library-tools'; tools.innerHTML = '<input type="search" placeholder="Søg efter ikon…" aria-label="Søg efter ikon"><select aria-label="Ikonsæt"><option value="">Alle ikonsæt</option></select>'; card.appendChild(tools);
        const search = tools.querySelector('input'), setSelect = tools.querySelector('select');
        iconLibrarySets().forEach(function (set) { const option = document.createElement('option'); option.value = String(set.key || ''); option.textContent = String(set.label || set.key || 'Ikonsæt'); setSelect.appendChild(option); });
        const scroll = document.createElement('div'); scroll.className = 'h18-vd-icon-library-scroll'; card.appendChild(scroll);
        const footer = document.createElement('div'); footer.className = 'h18-vd-icon-library-footer'; footer.textContent = 'Custom icons: upload/indsæt af egne SVG-filer er planlagt som næste udvidelsesniveau og er ikke aktiveret endnu.'; card.appendChild(footer);
        function close() { dialog.remove(); }
        function rebuild() {
            const needle = String(search.value || '').toLowerCase().trim(), setFilter = String(setSelect.value || ''); scroll.replaceChildren();
            iconLibrarySets().forEach(function (set) {
                if (setFilter && String(set.key || '') !== setFilter) { return; }
                const setBox = document.createElement('section'); setBox.className = 'h18-vd-icon-library-set'; const h3 = document.createElement('h3'); h3.textContent = String(set.label || set.key || 'Ikonsæt'); setBox.appendChild(h3); let count = 0;
                (Array.isArray(set.categories) ? set.categories : []).forEach(function (category) {
                    const matches = (Array.isArray(category.icons) ? category.icons : []).filter(function (icon) { const hay = [set.label,category.label,icon.label,icon.key].join(' ').toLowerCase(); return !needle || hay.indexOf(needle) >= 0; });
                    if (!matches.length) { return; }
                    const cat = document.createElement('section'); cat.className = 'h18-vd-icon-library-category'; const h4 = document.createElement('h4'); h4.textContent = String(category.label || category.key || 'Kategori'); cat.appendChild(h4); const grid = document.createElement('div'); grid.className = 'h18-vd-icon-library-grid';
                    matches.forEach(function (icon) {
                        const button = document.createElement('button'); button.type = 'button'; button.className = 'h18-vd-icon-library-item'; const selection = normalizeIconSelection(node.props.iconSet || 'core', node.props.icon || 'star'); if (selection.set === String(set.key) && selection.icon === String(icon.key)) { button.classList.add('is-current'); }
                        const mark = document.createElement('span'); mark.innerHTML = String(icon.svg || ''); const label = document.createElement('small'); label.textContent = String(icon.label || icon.key || 'Ikon'); button.appendChild(mark); button.appendChild(label);
                        button.addEventListener('click', function () { const before = clone(state); node.props.iconSet = String(set.key || 'core'); node.props.icon = String(icon.key || 'star'); commit(before, 'Skift ikon'); close(); render(); }); grid.appendChild(button); count += 1;
                    }); cat.appendChild(grid); setBox.appendChild(cat);
                });
                if (count) { scroll.appendChild(setBox); }
            });
            if (!scroll.children.length) { const empty = document.createElement('p'); empty.textContent = 'Ingen ikoner matcher søgningen.'; scroll.appendChild(empty); }
        }
        backdrop.addEventListener('click', close); head.querySelector('[data-icon-close]').addEventListener('click', close); search.addEventListener('input', rebuild); setSelect.addEventListener('change', rebuild); dialog.addEventListener('keydown', function (event) { if (event.key === 'Escape') { event.preventDefault(); event.stopPropagation(); close(); } });
        document.body.appendChild(dialog); rebuild(); setTimeout(function () { search.focus(); },0);
    }

    function iconSvgMarkup(token) {
        const shapes = {
            star:'<polygon points="12 2.7 14.8 8.4 21 9.3 16.5 13.7 17.6 20 12 17 6.4 20 7.5 13.7 3 9.3 9.2 8.4 12 2.7"/>',
            check:'<polyline points="4 12.5 9.5 18 20 6"/>',
            info:'<circle cx="12" cy="12" r="9"/><line x1="12" y1="10.5" x2="12" y2="17"/><line x1="12" y1="7" x2="12.01" y2="7"/>',
            calendar:'<rect x="3" y="5" width="18" height="16" rx="2"/><line x1="7" y1="3" x2="7" y2="7"/><line x1="17" y1="3" x2="17" y2="7"/><line x1="3" y1="10" x2="21" y2="10"/>',
            camera:'<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7l1.5-3h5L16 7"/><circle cx="12" cy="13.5" r="3.5"/>',
            people:'<circle cx="9" cy="8" r="3"/><circle cx="17" cy="9" r="2.5"/><path d="M3 20c.8-4 3-6 6-6s5.2 2 6 6"/><path d="M14 15c3.5-.5 6 1.1 7 4"/>',
            ruler:'<path d="M4 17L17 4l3 3L7 20z"/><line x1="13" y1="8" x2="16" y2="11"/><line x1="10" y1="11" x2="12" y2="13"/><line x1="7" y1="14" x2="10" y2="17"/>',
            weight:'<path d="M6 8h12l2 12H4z"/><path d="M9 8a3 3 0 016 0"/><line x1="12" y1="11" x2="14" y2="14"/>',
            gear:'<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M5 5l2 2M17 17l2 2M19 5l-2 2M7 17l-2 2"/>',
            link:'<path d="M10 13a5 5 0 007 0l2-2a5 5 0 00-7-7l-1 1"/><path d="M14 11a5 5 0 00-7 0l-2 2a5 5 0 007 7l1-1"/>'
        };
        return '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false">' + (shapes[String(token || '')] || shapes.star) + '</svg>';
    }

    function normalizeProps(type, raw) {
        raw = raw && typeof raw === 'object' ? raw : {};
        const common = commonProps(raw);
        if (type === 'text') {
            return Object.assign(common, {
                heading: String(raw.heading || ''),
                headingLevel: ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(String(raw.headingLevel || '').toLowerCase()) ? String(raw.headingLevel).toLowerCase() : 'h2',
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
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 16, 10) || 16, 8, 120),
                fontWeight: clamp(parseInt(raw.fontWeight || 400, 10) || 400, 100, 900),
                lineHeight: Math.max(0.8, Math.min(3, parseFloat(raw.lineHeight || 1.2) || 1.2)),
                letterSpacing: Math.max(-10, Math.min(30, parseFloat(raw.letterSpacing || 0) || 0)),
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
        if (type === 'spacer') { return common; }
        if (type === 'divider') {
            return Object.assign(common, {
                orientation: ['horizontal','vertical'].includes(String(raw.orientation || '').toLowerCase()) ? String(raw.orientation).toLowerCase() : 'horizontal',
                lineColor: /^#[0-9a-f]{6}$/i.test(String(raw.lineColor || '')) ? String(raw.lineColor).toLowerCase() : '#c3c4c7',
                lineWidth: clamp(parseInt(raw.lineWidth || 1, 10) || 1, 1, 20),
                lineStyle: ['solid','dashed','dotted'].includes(String(raw.lineStyle || '').toLowerCase()) ? String(raw.lineStyle).toLowerCase() : 'solid'
            });
        }
        if (type === 'icon') {
            const iconSelection = normalizeIconSelection(raw.iconSet || 'core', raw.icon || 'star');
            return Object.assign(common, {
                iconSet: iconSelection.set,
                icon: iconSelection.icon,
                iconSize: clamp(parseInt(raw.iconSize || 32, 10) || 32, 8, 240),
                iconColor: /^#[0-9a-f]{6}$/i.test(String(raw.iconColor || '')) ? String(raw.iconColor).toLowerCase() : '#30382a',
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#ffffff',
                backgroundTransparent: raw.backgroundTransparent !== false,
                padding: clamp(parseInt(raw.padding || 0, 10) || 0, 0, 120),
                radius: clamp(parseInt(raw.radius || 0, 10) || 0, 0, 100),
                align: ['left','center','right'].includes(String(raw.align || '').toLowerCase()) ? String(raw.align).toLowerCase() : 'center'
            });
        }
        if (type === 'badge') {
            return Object.assign(common, {
                text: String(raw.text || 'Badge'),
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#c3ae83',
                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#30382a',
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 13, 10) || 13, 8, 80),
                fontWeight: clamp(parseInt(raw.fontWeight || 700, 10) || 700, 100, 900),
                paddingX: clamp(parseInt(raw.paddingX || 12, 10) || 12, 0, 120),
                paddingY: clamp(parseInt(raw.paddingY || 5, 10) || 5, 0, 120),
                radius: clamp(parseInt(raw.radius || 20, 10) || 20, 0, 100),
                align: ['left','center','right'].includes(String(raw.align || '').toLowerCase()) ? String(raw.align).toLowerCase() : 'left'
            });
        }
        if (type === 'link') {
            return Object.assign(common, {
                text: String(raw.text || 'Læs mere →'),
                linkType: ['page','url','anchor','email','phone'].includes(String(raw.linkType || '').toLowerCase()) ? String(raw.linkType).toLowerCase() : 'url',
                pageId: parseInt(raw.pageId || 0, 10) || 0,
                url: String(raw.url || ''),
                targetBlank: !!raw.targetBlank,
                textColor: /^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#2271b1',
                hoverTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.hoverTextColor || '')) ? String(raw.hoverTextColor).toLowerCase() : '#135e96',
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 16, 10) || 16, 8, 120),
                fontWeight: clamp(parseInt(raw.fontWeight || 600, 10) || 600, 100, 900),
                lineHeight: Math.max(0.8, Math.min(3, parseFloat(raw.lineHeight || 1.3) || 1.3)),
                letterSpacing: Math.max(-10, Math.min(30, parseFloat(raw.letterSpacing || 0) || 0)),
                underline: !!raw.underline,
                align: ['left','center','right'].includes(String(raw.align || '').toLowerCase()) ? String(raw.align).toLowerCase() : 'left'
            });
        }
        if (type === 'datalist') {
            return Object.assign(common, {
                rows: normalizePairRows(raw.rows),
                layout: ['rows','stacked'].includes(String(raw.layout || '').toLowerCase()) ? String(raw.layout).toLowerCase() : 'rows',
                labelWidth: clamp(parseInt(raw.labelWidth || 40, 10) || 40, 15, 80),
                cellPadding: clamp(parseInt(raw.cellPadding || 8, 10) || 8, 0, 60),
                showDividers: raw.showDividers !== false,
                zebra: !!raw.zebra,
                background: /^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#ffffff',
                zebraBackground: /^#[0-9a-f]{6}$/i.test(String(raw.zebraBackground || '')) ? String(raw.zebraBackground).toLowerCase() : '#f6f7f7',
                lineColor: /^#[0-9a-f]{6}$/i.test(String(raw.lineColor || '')) ? String(raw.lineColor).toLowerCase() : '#dcdcde',
                labelColor: /^#[0-9a-f]{6}$/i.test(String(raw.labelColor || '')) ? String(raw.labelColor).toLowerCase() : '#30382a',
                valueColor: /^#[0-9a-f]{6}$/i.test(String(raw.valueColor || '')) ? String(raw.valueColor).toLowerCase() : '#30382a',
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 15, 10) || 15, 8, 80),
                labelWeight: clamp(parseInt(raw.labelWeight || 600, 10) || 600, 100, 900),
                valueWeight: clamp(parseInt(raw.valueWeight || 400, 10) || 400, 100, 900)
            });
        }
        if (type === 'table') {
            const headers = normalizeHeaders(raw.headers);
            return Object.assign(common, {
                headers: headers,
                rows: normalizeMatrixRows(raw.rows, headers.length),
                headerBackground: /^#[0-9a-f]{6}$/i.test(String(raw.headerBackground || '')) ? String(raw.headerBackground).toLowerCase() : '#30382a',
                headerTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.headerTextColor || '')) ? String(raw.headerTextColor).toLowerCase() : '#ffffff',
                cellBackground: /^#[0-9a-f]{6}$/i.test(String(raw.cellBackground || '')) ? String(raw.cellBackground).toLowerCase() : '#ffffff',
                cellTextColor: /^#[0-9a-f]{6}$/i.test(String(raw.cellTextColor || '')) ? String(raw.cellTextColor).toLowerCase() : '#30382a',
                zebra: raw.zebra !== false,
                zebraBackground: /^#[0-9a-f]{6}$/i.test(String(raw.zebraBackground || '')) ? String(raw.zebraBackground).toLowerCase() : '#f6f7f7',
                cellBorderColor: /^#[0-9a-f]{6}$/i.test(String(raw.cellBorderColor || '')) ? String(raw.cellBorderColor).toLowerCase() : '#dcdcde',
                cellBorderWidth: clamp(parseInt(raw.cellBorderWidth != null ? raw.cellBorderWidth : 1, 10) || 0, 0, 10),
                cellBorderStyle: ['solid','dashed','dotted'].includes(String(raw.cellBorderStyle || '').toLowerCase()) ? String(raw.cellBorderStyle).toLowerCase() : 'solid',
                borderMode: ['all','outer','inner','none'].includes(String(raw.borderMode || '').toLowerCase()) ? String(raw.borderMode).toLowerCase() : 'all',
                cellBorders: normalizeTableCellBorders(raw.cellBorders),
                cellPadding: clamp(parseInt(raw.cellPadding || 8, 10) || 8, 0, 60),
                fontFamily: normalizeFontToken(raw.fontFamily || 'system', false),
                fontSize: clamp(parseInt(raw.fontSize || 14, 10) || 14, 8, 80),
                headerWeight: clamp(parseInt(raw.headerWeight || 700, 10) || 700, 100, 900),
                mobileMode: ['scroll','cards'].includes(String(raw.mobileMode || '').toLowerCase()) ? String(raw.mobileMode).toLowerCase() : 'scroll'
            });
        }
        if (type === 'vehiclelist') {
            const orderBy = ['sortOrder','title','updatedAt'].includes(String(raw.orderBy || 'sortOrder')) ? String(raw.orderBy || 'sortOrder') : 'sortOrder';
            const order = String(raw.order || 'ASC').toUpperCase() === 'DESC' ? 'DESC' : 'ASC';
            const limit = clamp(parseInt(raw.limit || 50,10) || 50,1,100);
            return Object.assign(common, {
                binding:{schema:1,mode:'module',module:'vehicles',view:'list',recordId:'',query:{status:'publish',orderBy:orderBy,order:order,limit:limit},fieldMap:{}},
                limit:limit, orderBy:orderBy, order:order,
                detailPageId:parseInt(raw.detailPageId || 0,10) || 0,
                columns:clamp(parseInt(raw.columns || 3,10) || 3,1,4),
                cardGap:clamp(parseInt(raw.cardGap || 18,10) || 18,0,80),
                cardPadding:clamp(parseInt(raw.cardPadding || 12,10) || 12,0,60),
                imageHeight:clamp(parseInt(raw.imageHeight || 180,10) || 180,60,600),
                showImage:raw.showImage !== false, showCategory:raw.showCategory !== false, showSummary:raw.showSummary !== false, linkCards:raw.linkCards !== false,
                cardBackground:/^#[0-9a-f]{6}$/i.test(String(raw.cardBackground || '')) ? String(raw.cardBackground).toLowerCase() : '#ffffff',
                textColor:/^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#30382a',
                accentColor:/^#[0-9a-f]{6}$/i.test(String(raw.accentColor || '')) ? String(raw.accentColor).toLowerCase() : '#c3ae83',
                cardRadius:clamp(parseInt(raw.cardRadius || 4,10) || 4,0,60)
            });
        }
        if (type === 'vehicledetail') {
            let recordId = String(raw.recordId || '').toLowerCase().trim();
            if (recordId && !/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(recordId)) { recordId = ''; }
            return Object.assign(common, {
                binding:{schema:1,mode:'module',module:'vehicles',view:'detail',recordId:recordId,query:{status:'publish',orderBy:'sortOrder',order:'ASC',limit:50},fieldMap:{}},
                recordId:recordId,
                showGallery:raw.showGallery !== false, showCategory:raw.showCategory !== false, showSummary:raw.showSummary !== false, showDescription:raw.showDescription !== false, showAttributes:raw.showAttributes !== false,
                imageHeight:clamp(parseInt(raw.imageHeight || 360,10) || 360,80,900), labelWidth:clamp(parseInt(raw.labelWidth || 34,10) || 34,20,60),
                background:/^#[0-9a-f]{6}$/i.test(String(raw.background || '')) ? String(raw.background).toLowerCase() : '#ffffff',
                textColor:/^#[0-9a-f]{6}$/i.test(String(raw.textColor || '')) ? String(raw.textColor).toLowerCase() : '#30382a',
                accentColor:/^#[0-9a-f]{6}$/i.test(String(raw.accentColor || '')) ? String(raw.accentColor).toLowerCase() : '#c3ae83',
                padding:clamp(parseInt(raw.padding || 16,10) || 16,0,80), radius:clamp(parseInt(raw.radius || 4,10) || 4,0,60)
            });
        }
        if (type === 'eventlist') {
            const orderBy=['start','title','updatedAt'].includes(String(raw.orderBy||'start'))?String(raw.orderBy||'start'):'start'; const order=String(raw.order||'ASC').toUpperCase()==='DESC'?'DESC':'ASC'; const limit=clamp(parseInt(raw.limit||50,10)||50,1,100); const dateFilter=['all','upcoming','past'].includes(String(raw.dateFilter||'upcoming'))?String(raw.dateFilter||'upcoming'):'upcoming';
            return Object.assign(common,{binding:{schema:1,mode:'module',module:'events',view:'list',recordId:'',query:{status:'publish',orderBy:orderBy,order:order,limit:limit},fieldMap:{}},limit:limit,orderBy:orderBy,order:order,dateFilter:dateFilter,detailPageId:parseInt(raw.detailPageId||0,10)||0,columns:clamp(parseInt(raw.columns||3,10)||3,1,4),cardGap:clamp(parseInt(raw.cardGap||18,10)||18,0,80),cardPadding:clamp(parseInt(raw.cardPadding||12,10)||12,0,60),imageHeight:clamp(parseInt(raw.imageHeight||180,10)||180,60,600),showImage:raw.showImage!==false,showDate:raw.showDate!==false,showLocation:raw.showLocation!==false,showSummary:raw.showSummary!==false,linkCards:raw.linkCards!==false,cardBackground:normalizeColor(raw.cardBackground||'#ffffff'),textColor:normalizeColor(raw.textColor||'#30382a'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),cardRadius:clamp(parseInt(raw.cardRadius||4,10)||4,0,60)});
        }
        if (type === 'eventdetail') {
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{binding:{schema:1,mode:'module',module:'events',view:'detail',recordId:recordId,query:{status:'publish',orderBy:'start',order:'ASC',limit:50},fieldMap:{}},recordId:recordId,showImage:raw.showImage!==false,showDate:raw.showDate!==false,showLocation:raw.showLocation!==false,showSummary:raw.showSummary!==false,showDescription:raw.showDescription!==false,imageHeight:clamp(parseInt(raw.imageHeight||360,10)||360,80,900),background:normalizeColor(raw.background||'#ffffff'),textColor:normalizeColor(raw.textColor||'#30382a'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),padding:clamp(parseInt(raw.padding||16,10)||16,0,80),radius:clamp(parseInt(raw.radius||4,10)||4,0,60)});
        }

        if (type === 'eventvalue') {
            const valueKey=['title','date','location','summary','description'].includes(String(raw.valueKey||''))?String(raw.valueKey):'title';
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            const defaultTag=valueKey==='title'?'h1':(valueKey==='description'?'div':'p'); const tag=['div','p','h1','h2','h3','h4','h5','h6'].includes(String(raw.tag||''))?String(raw.tag):defaultTag;
            return Object.assign(common,{valueKey:valueKey,recordId:recordId,tag:tag,align:['left','center','right'].includes(String(raw.align||''))?String(raw.align):'left',fontFamily:normalizeFontToken(raw.fontFamily||'system',false),fontSize:clamp(parseInt(raw.fontSize||(valueKey==='title'?44:16),10)||(valueKey==='title'?44:16),8,160),fontWeight:clamp(parseInt(raw.fontWeight||(valueKey==='title'||valueKey==='summary'?700:400),10)||(valueKey==='title'||valueKey==='summary'?700:400),100,900),lineHeight:Math.max(.8,Math.min(3,parseFloat(raw.lineHeight||(valueKey==='title'?1.1:1.5))||(valueKey==='title'?1.1:1.5))),letterSpacing:Math.max(-10,Math.min(30,parseFloat(raw.letterSpacing||0)||0)),textColor:normalizeColor(raw.textColor||'#30382a'),background:normalizeColor(raw.background||'#ffffff'),backgroundTransparent:raw.backgroundTransparent!==false,padding:clamp(parseInt(raw.padding||0,10)||0,0,120),radius:clamp(parseInt(raw.radius||0,10)||0,0,100)});
        }
        if (type === 'eventimage') {
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{recordId:recordId,fit:String(raw.fit||'cover')==='contain'?'contain':'cover',imageHeight:clamp(parseInt(raw.imageHeight||360,10)||360,80,1000),focalX:clamp(parseInt(raw.focalX||50,10)||50,0,100),focalY:clamp(parseInt(raw.focalY||50,10)||50,0,100),background:normalizeColor(raw.background||'#ffffff'),radius:clamp(parseInt(raw.radius||4,10)||4,0,100)});
        }

        if (type === 'eventfacts') {
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{recordId:recordId,showDate:raw.showDate!==false,showTime:raw.showTime!==false,showLocation:raw.showLocation!==false,showAddress:raw.showAddress!==false,showContact:raw.showContact!==false,gap:clamp(parseInt(raw.gap||12,10)||12,0,80),minCardWidth:clamp(parseInt(raw.minCardWidth||150,10)||150,100,360),cardBackground:normalizeColor(raw.cardBackground||'#f4f1e8'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),labelColor:normalizeColor(raw.labelColor||'#30382a'),valueColor:normalizeColor(raw.valueColor||'#30382a'),paddingX:clamp(parseInt(raw.paddingX||16,10)||16,0,80),paddingY:clamp(parseInt(raw.paddingY||16,10)||16,0,80),radius:clamp(parseInt(raw.radius||0,10)||0,0,60),labelFontFamily:normalizeFontToken(raw.labelFontFamily||'system',false),labelFontSize:clamp(parseInt(raw.labelFontSize||16,10)||16,8,80),labelFontWeight:clamp(parseInt(raw.labelFontWeight||700,10)||700,100,900),valueFontFamily:normalizeFontToken(raw.valueFontFamily||'system',false),valueFontSize:clamp(parseInt(raw.valueFontSize||16,10)||16,8,80),valueFontWeight:clamp(parseInt(raw.valueFontWeight||400,10)||400,100,900),lineHeight:Math.max(0.8,Math.min(3,parseFloat(raw.lineHeight||1.35)||1.35))});
        }

        if (type === 'eventfield') {
            const key=String(raw.fieldKey||'about').toLowerCase().replace(/[^a-z0-9_-]/g,''); const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{fieldKey:key||'about',recordId:recordId,showHeading:raw.showHeading!==false,showWhenEmpty:raw.showWhenEmpty===true,background:/^#[0-9a-f]{6}$/i.test(String(raw.background||''))?String(raw.background).toLowerCase():'',textColor:normalizeColor(raw.textColor||'#30382a'),fontFamily:normalizeFontToken(raw.fontFamily||'system',false),fontSize:clamp(parseInt(raw.fontSize||16,10)||16,8,120),fontWeight:clamp(parseInt(raw.fontWeight||400,10)||400,100,900),lineHeight:Math.max(0.8,Math.min(3,parseFloat(raw.lineHeight||1.5)||1.5)),headingColor:normalizeColor(raw.headingColor||'#30382a'),headingFontFamily:normalizeFontToken(raw.headingFontFamily||'body',true),headingFontSize:clamp(parseInt(raw.headingFontSize||40,10)||40,8,160),headingFontWeight:clamp(parseInt(raw.headingFontWeight||400,10)||400,100,900),headingLineHeight:Math.max(0.8,Math.min(3,parseFloat(raw.headingLineHeight||1.15)||1.15)),headingGap:clamp(parseInt(raw.headingGap||12,10)||12,0,80),padding:clamp(parseInt(raw.padding||0,10)||0,0,80),radius:clamp(parseInt(raw.radius||0,10)||0,0,60)});
        }
        if (type === 'gallerylist') {
            const orderBy=['sortOrder','title','updatedAt'].includes(String(raw.orderBy||'sortOrder'))?String(raw.orderBy||'sortOrder'):'sortOrder'; const order=String(raw.order||'ASC').toUpperCase()==='DESC'?'DESC':'ASC'; const limit=clamp(parseInt(raw.limit||50,10)||50,1,100);
            return Object.assign(common,{binding:{schema:1,mode:'module',module:'galleries',view:'list',recordId:'',query:{status:'publish',orderBy:orderBy,order:order,limit:limit},fieldMap:{}},limit:limit,orderBy:orderBy,order:order,detailPageId:parseInt(raw.detailPageId||0,10)||0,columns:clamp(parseInt(raw.columns||3,10)||3,1,4),cardGap:clamp(parseInt(raw.cardGap||18,10)||18,0,80),cardPadding:clamp(parseInt(raw.cardPadding||12,10)||12,0,60),imageHeight:clamp(parseInt(raw.imageHeight||220,10)||220,80,600),showImage:raw.showImage!==false,showSummary:raw.showSummary!==false,showCount:raw.showCount!==false,linkCards:raw.linkCards!==false,cardBackground:normalizeColor(raw.cardBackground||'#ffffff'),textColor:normalizeColor(raw.textColor||'#30382a'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),cardRadius:clamp(parseInt(raw.cardRadius||4,10)||4,0,60)});
        }
        if (type === 'gallerydetail') {
            const recordId=/^[a-z0-9][a-z0-9._:-]{0,127}$/.test(String(raw.recordId||'').toLowerCase())?String(raw.recordId||'').toLowerCase():'';
            return Object.assign(common,{binding:{schema:1,mode:'module',module:'galleries',view:'detail',recordId:recordId,query:{status:'publish',orderBy:'sortOrder',order:'ASC',limit:50},fieldMap:{}},recordId:recordId,showDescription:raw.showDescription!==false,columns:clamp(parseInt(raw.columns||4,10)||4,1,6),gap:clamp(parseInt(raw.gap||12,10)||12,0,80),imageHeight:clamp(parseInt(raw.imageHeight||220,10)||220,80,700),background:normalizeColor(raw.background||'#ffffff'),textColor:normalizeColor(raw.textColor||'#30382a'),accentColor:normalizeColor(raw.accentColor||'#c3ae83'),padding:clamp(parseInt(raw.padding||16,10)||16,0,80),radius:clamp(parseInt(raw.radius||4,10)||4,0,60)});
        }

        if (type === 'contactform' || type === 'membershipform') {
            const membership = type === 'membershipform';
            return Object.assign(common, {
                heading:String(raw.heading || (membership ? 'Bliv medlem' : 'Kontakt os')),
                intro:String(raw.intro || (membership ? 'Udfyld formularen, så kontakter vi dig om medlemskab.' : 'Har du spørgsmål, er du velkommen til at kontakte os.')),
                buttonText:String(raw.buttonText || (membership ? 'Send indmeldelse' : 'Send besked')),
                recipient:String(raw.recipient || ''),
                background:normalizeColor(raw.background || '#f4f1e8'), fieldBackground:normalizeColor(raw.fieldBackground || '#ffffff'),
                textColor:normalizeColor(raw.textColor || '#30382a'), accentColor:normalizeColor(raw.accentColor || '#30382a'),
                padding:clamp(parseInt(raw.padding || 24,10)||24,0,80), radius:clamp(parseInt(raw.radius || 6,10)||6,0,60),
                showPhone:raw.showPhone !== false, requireConsent:raw.requireConsent !== false
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
                minHeightRows: clamp(parseInt(raw.minHeightRows || 0, 10) || 0, 0, 4000), moduleSlot: type === 'section' && ['before','between','after'].includes(String(raw.moduleSlot||'before')) ? String(raw.moduleSlot||'before') : 'before'
            });
        }
        return common;
    }


    function hierarchyLocalGeometry(geometry) {
        geometry = geometry && typeof geometry === 'object' ? geometry : {};
        const desktopSource = normalizeDevice(geometry.desktop, false);
        const result = {
            desktop: { x: 0, y: 0, w: UNITS, h: desktopSource.h }
        };
        ['laptop', 'tablet', 'mobile'].forEach(function (key) {
            const source = normalizeDevice(geometry[key], true);
            const inherit = source.inheritDesktop !== false;
            result[key] = { x: 0, y: 0, w: UNITS, h: inherit ? desktopSource.h : source.h, inheritDesktop: inherit };
        });
        return result;
    }

    function hierarchyWrapperId(sourceId, map) {
        const tail = cleanId(sourceId).slice(-70) || 'element';
        const base = cleanId('section-migrated-' + tail) || 'section-migrated';
        let candidate = base;
        let suffix = 2;
        while (map[candidate]) {
            candidate = cleanId(base.slice(0, 92) + '-' + String(suffix));
            suffix += 1;
        }
        return candidate;
    }

    function normalizeCanvasHierarchy(nodes) {
        const map = {};
        nodes.forEach(function (node) { map[node.id] = node; });

        // Sektion is page-level only. Historical nested sections are losslessly
        // treated as Kasser, matching the server HierarchyNormalizer contract.
        nodes.forEach(function (node) {
            if (node.type === 'section' && node.parentId) {
                node.type = 'container';
                node.props = normalizeProps('container', node.props || {});
            }
        });

        const roots = nodes.filter(function (node) { return !node.parentId && node.type !== 'section'; });
        roots.forEach(function (node) {
            const oldGeometry = clone(node.geometry || {});
            const wrapperId = hierarchyWrapperId(node.id, map);
            const gapX = clamp(parseInt(node.props && node.props.gapX || 0, 10) || 0, 0, 200);
            const gapY = clamp(parseInt(node.props && node.props.gapY || 0, 10) || 0, 0, 200);
            const wrapper = {
                id: wrapperId,
                type: 'section',
                parentId: '',
                order: Math.max(1, parseInt(node.order || 10, 10) || 10),
                geometry: clone(oldGeometry),
                props: normalizeProps('section', { gapX: gapX, gapY: gapY, minHeightRows: 0 })
            };
            map[wrapperId] = wrapper;
            nodes.push(wrapper);
            if (node.props) { node.props.gapX = 0; node.props.gapY = 0; }
            node.parentId = wrapperId;
            node.order = 10;
            node.geometry = hierarchyLocalGeometry(oldGeometry);
        });

        return nodes;
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
                    laptop: normalizeDevice(item.geometry && item.geometry.laptop, true),
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
        normalizeCanvasHierarchy(nodes);
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

    function isEditableTarget(target) {
        if (!target || typeof target.closest !== 'function') { return false; }
        return !!target.closest('input,textarea,select,[contenteditable="true"],.wp-editor-area,.mce-content-body');
    }

    function selectedNodeForProductivity() {
        const direct = nodeById(selectedId);
        if (direct) { return direct; }
        const card = document.querySelector('#h18-clean-canvas .h18-clean-node.is-selected[data-node-id]');
        if (!card) { return null; }
        const recovered = nodeById(card.getAttribute('data-node-id') || '');
        if (recovered) { selectedId = recovered.id; }
        return recovered;
    }

    function productivityNotice(message) {
        const status = document.getElementById('h18-vd-clipboard-status');
        if (!status) { return; }
        if (productivityNoticeTimer) { window.clearTimeout(productivityNoticeTimer); }
        status.textContent = String(message || '');
        productivityNoticeTimer = window.setTimeout(function () {
            productivityNoticeTimer = 0;
            updateProductivityToolbar();
        }, 2200);
    }

    function revealSelected(message) {
        const id = cleanId(selectedId);
        const reveal = function () {
            const card = id ? document.querySelector('#h18-clean-canvas .h18-clean-node[data-node-id="' + CSS.escape(id) + '"]') : null;
            if (card) {
                try { card.scrollIntoView({ block: 'center', inline: 'nearest', behavior: 'smooth' }); }
                catch (ignore) { try { card.scrollIntoView(); } catch (ignoreFallback) {} }
            }
            productivityNotice(message);
        };
        if (window.requestAnimationFrame) { window.requestAnimationFrame(reveal); }
        else { window.setTimeout(reveal, 0); }
    }

    function clipboardPayloadFor(id) {
        const root = nodeById(id);
        if (!root) { return null; }
        const ids = new Set([root.id].concat(descendants(root.id)));
        return {
            schemaVersion: 1,
            sourcePostId: POST_ID,
            sourceContext: CONTEXT_LABEL,
            copiedUtc: new Date().toISOString(),
            rootId: root.id,
            rootType: root.type,
            nodes: clone(state.nodes.filter(function (node) { return ids.has(node.id); }))
        };
    }

    function readClipboard() {
        let value = memoryClipboard;
        try {
            const raw = window.localStorage ? window.localStorage.getItem(CLIPBOARD_KEY) : '';
            if (raw) { value = JSON.parse(raw); memoryClipboard = value; }
        } catch (ignore) {}
        if (!value || !Array.isArray(value.nodes) || !value.nodes.length || !value.rootId) { return null; }
        return value;
    }

    function writeClipboard(value) {
        memoryClipboard = value;
        try { if (window.localStorage) { window.localStorage.setItem(CLIPBOARD_KEY, JSON.stringify(value)); } } catch (ignore) {}
        updateProductivityToolbar();
    }

    function clearClipboard() {
        memoryClipboard = null;
        try { if (window.localStorage) { window.localStorage.removeItem(CLIPBOARD_KEY); } } catch (ignore) {}
        updateProductivityToolbar();
    }

    function copySelected() {
        const selected = selectedNodeForProductivity();
        const payload = selected ? clipboardPayloadFor(selected.id) : null;
        if (!payload) { productivityNotice('Vælg først et element'); return false; }
        writeClipboard(payload);
        lastAction = 'Kopiér ' + typeLabel(payload.rootType);
        productivityNotice('Kopieret: ' + typeLabel(payload.rootType) + (payload.nodes.length > 1 ? ' + indhold' : '') + ' · brug Indsæt eller Ctrl+V');
        diag('clipboard_copy', { rootId: payload.rootId, rootType: payload.rootType, nodeCount: payload.nodes.length, sourcePostId: POST_ID });
        return true;
    }

    function resolvePasteParent(payload) {
        const selected = selectedNodeForProductivity();
        if (selected && PARENT_TYPES.includes(selected.type) && selected.id !== payload.rootId) { return selected.id; }
        if (selected && !PARENT_TYPES.includes(selected.type)) { return selected.parentId; }
        if (parseInt(payload.sourcePostId || 0, 10) === POST_ID) {
            const source = nodeById(payload.rootId);
            if (source) { return source.parentId; }
        }
        return '';
    }

    function pastePayload(payload, duplicateMode) {
        if (!payload || !Array.isArray(payload.nodes) || !payload.nodes.length) { return false; }
        if (state.nodes.length + payload.nodes.length > 300) {
            window.alert('Indsætning ville overskride Designerens maksimum på 300 elementer.');
            return false;
        }
        const sourceRoot = payload.nodes.find(function (node) { return node && node.id === payload.rootId; });
        if (!sourceRoot || !TYPES.includes(String(sourceRoot.type || '').toLowerCase())) { return false; }
        let parentId = resolvePasteParent(payload);
        const parent = parentId ? nodeById(parentId) : null;
        if (parentId && (!parent || !PARENT_TYPES.includes(parent.type))) { parentId = ''; }

        const before = clone(state);
        const idMap = {};
        payload.nodes.forEach(function (source) {
            if (!source || !TYPES.includes(String(source.type || '').toLowerCase())) { return; }
            let next = makeId(String(source.type));
            while (nodeById(next) || Object.values(idMap).includes(next)) { next = makeId(String(source.type)); }
            idMap[String(source.id)] = next;
        });
        if (!idMap[payload.rootId]) { return false; }

        const newNodes = [];
        payload.nodes.forEach(function (source) {
            if (!source || !idMap[source.id]) { return; }
            const next = clone(source);
            next.id = idMap[source.id];
            if (source.id === payload.rootId) {
                next.parentId = parentId;
                next.order = nextOrder(parentId);
                if (!next.geometry || !next.geometry.desktop) { next.geometry = { desktop: normalizeDevice({}, false) }; }
                next.geometry.desktop.y = nextFreeY(parentId);
                next.geometry.desktop.x = clamp(parseInt(next.geometry.desktop.x || 0, 10) || 0, 0, UNITS - 1);
                next.geometry.desktop.w = clamp(parseInt(next.geometry.desktop.w || UNITS, 10) || UNITS, 1, UNITS - next.geometry.desktop.x);
            } else {
                next.parentId = idMap[source.parentId] || '';
            }
            newNodes.push(next);
        });
        state.nodes = state.nodes.concat(newNodes);
        state = normalizeModel(state);
        selectedId = idMap[payload.rootId];
        const label = (duplicateMode ? 'Duplikér ' : 'Indsæt ') + typeLabel(sourceRoot.type) + (payload.nodes.length > 1 ? ' + indhold' : '');
        commit(before, label);
        render();
        revealSelected((duplicateMode ? 'Duplikeret: ' : 'Indsat: ') + typeLabel(sourceRoot.type) + (payload.nodes.length > 1 ? ' + indhold' : ''));
        diag(duplicateMode ? 'clipboard_duplicate' : 'clipboard_paste', { sourceRootId: payload.rootId, newRootId: selectedId, nodeCount: payload.nodes.length, targetParentId: parentId, sourcePostId: parseInt(payload.sourcePostId || 0, 10) || 0, targetPostId: POST_ID });
        return true;
    }

    function pasteClipboard() {
        const payload = readClipboard();
        if (!payload) { productivityNotice('Clipboard er tomt'); return false; }
        return pastePayload(payload, false);
    }
    function duplicateSelected() {
        const selected = selectedNodeForProductivity();
        const payload = selected ? clipboardPayloadFor(selected.id) : null;
        if (!payload) { productivityNotice('Vælg først et element'); return false; }
        return pastePayload(payload, true);
    }

    function finalizeNudge() {
        if (!nudgeSession) { return; }
        const session = nudgeSession;
        nudgeSession = null;
        const node = nodeById(session.id);
        commit(session.before, 'Finjuster ' + typeLabel(node ? node.type : session.type) + ' med piletaster');
        diag('keyboard_nudge_commit', { id: session.id, offsetX: node ? node.props.offsetX : 0, offsetY: node ? node.props.offsetY : 0, state: structuralSummary() });
    }

    function nudgeSelected(dx, dy) {
        const node = nodeById(selectedId);
        if (!node || resize) { return false; }
        if (!nudgeSession || nudgeSession.id !== node.id) {
            finalizeNudge();
            nudgeSession = { id: node.id, type: node.type, before: clone(state) };
        }
        node.props.offsetX = clamp((parseInt(node.props.offsetX || 0, 10) || 0) + dx, -2000, 2000);
        node.props.offsetY = clamp((parseInt(node.props.offsetY || 0, 10) || 0) + dy, -2000, 2000);
        lastAction = 'Finjuster ' + typeLabel(node.type);
        render();
        return true;
    }

    function ensureProductivityToolbar() {
        if (document.getElementById('h18-vd-productivity')) { return; }
        const toolbar = document.querySelector('.h18-clean-toolbar');
        if (!toolbar) { return; }
        const host = document.createElement('span');
        host.id = 'h18-vd-productivity';
        host.className = 'h18-vd-productivity';
        host.innerHTML = '<button type="button" class="button" id="h18-vd-copy">Kopiér</button><button type="button" class="button" id="h18-vd-paste">Indsæt</button><button type="button" class="button" id="h18-vd-duplicate">Duplikér</button><span id="h18-vd-clipboard-status" class="h18-vd-clipboard-status" aria-live="polite"></span><button type="button" class="button-link" id="h18-vd-clear-clipboard">Ryd clipboard</button>';
        toolbar.appendChild(host);
        host.querySelector('#h18-vd-copy').addEventListener('click', copySelected);
        host.querySelector('#h18-vd-paste').addEventListener('click', pasteClipboard);
        host.querySelector('#h18-vd-duplicate').addEventListener('click', duplicateSelected);
        host.querySelector('#h18-vd-clear-clipboard').addEventListener('click', clearClipboard);
        updateProductivityToolbar();
    }

    function updateProductivityToolbar() {
        const host = document.getElementById('h18-vd-productivity');
        if (!host) { return; }
        const payload = readClipboard();
        const copyButton = host.querySelector('#h18-vd-copy');
        const pasteButton = host.querySelector('#h18-vd-paste');
        const duplicateButton = host.querySelector('#h18-vd-duplicate');
        const clearButton = host.querySelector('#h18-vd-clear-clipboard');
        const status = host.querySelector('#h18-vd-clipboard-status');
        const selected = selectedNodeForProductivity();
        if (copyButton) { copyButton.disabled = !selected; }
        if (duplicateButton) { duplicateButton.disabled = !selected; }
        if (pasteButton) { pasteButton.disabled = !payload; }
        if (clearButton) { clearButton.disabled = !payload; }
        if (status) {
            status.textContent = payload ? ('Clipboard: ' + typeLabel(payload.rootType || '') + ' · ' + payload.nodes.length + ' element' + (payload.nodes.length === 1 ? '' : 'er') + (payload.sourceContext ? ' · ' + payload.sourceContext : '')) : 'Clipboard: tom';
        }
    }

    window.H18VDProductivity = {
        copySelected: copySelected,
        pasteClipboard: pasteClipboard,
        duplicateSelected: duplicateSelected,
        selectedId: function () { const node = selectedNodeForProductivity(); return node ? node.id : ''; },
        clipboard: function () { return clone(readClipboard()); }
    };

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
        let placement = dropGeometry && typeof dropGeometry === 'object' ? dropGeometry : null;
        parentId = cleanId(placement && placement.parentId != null ? placement.parentId : parentId || '');
        if (type === 'section' && parentId) { parentId = ''; placement = null; }
        const parent = parentId ? nodeById(parentId) : null;
        if (parentId && (!parent || !PARENT_TYPES.includes(parent.type))) { return; }
        const before = clone(state);
        const id = makeId(type);
        const defaultW = defaultWidth(type, parentId);
        const p = placement || { parentId: parentId, x: 0, y: nextFreeY(parentId), w: defaultW, targetId: '', zone: 'free', bandIds: [], bandH: MIN_SPLIT_H };
        const defaultRows = { section: 20, container: 16, text: 14, image: 20, button: 8, menu: 10, spacer: 4, divider: 6, icon: 10, badge: 8, link: 8, datalist: 18, table: 22, vehiclelist: 42, vehicledetail: 54, eventlist: 38, eventdetail: 46, gallerylist: 40, gallerydetail: 52, eventvalue: 10, eventimage: 40, eventfacts: 12, eventfield: 18, contactform: 76, membershipform: 87 };
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
                laptop: Object.assign({}, desktop, { inheritDesktop: true }),
                tablet: Object.assign({}, desktop, { inheritDesktop: true }),
                mobile: { x: 0, y: 0, w: 120, h: defaultH, inheritDesktop: true }
            },
            props: newProps
        });
        reorderForPlacement(id, parentId, p);
        applyDestinationGeometry(id, p);
        state = normalizeModel(state);
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
        if (node.type === 'section' && parentId) { productivityNotice('Sektioner kan kun ligge direkte på websiden'); return; }

        const before = clone(state);
        const from = node.parentId;
        const sourceSnapshot = dragSource ? clone(dragSource) : null;
        node.parentId = parentId;
        node.order = nextOrder(parentId);
        if (sourceSnapshot && !isFloatingButton(node)) { healSourceCell(sourceSnapshot, id); }
        reorderForPlacement(id, parentId, placement);
        applyDestinationGeometry(id, placement);
        node.geometry.desktop.w = Math.min(UNITS, Math.max(1, node.geometry.desktop.w));
        state = normalizeModel(state);
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
        const offsetX = clamp(parseInt(props.offsetX || 0, 10) || 0, -2000, 2000);
        const offsetY = clamp(parseInt(props.offsetY || 0, 10) || 0, -2000, 2000);
        card.style.transform = (offsetX || offsetY) ? ('translate(' + offsetX + 'px,' + offsetY + 'px)') : '';
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
                const headingLevel = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(node.props.headingLevel) ? node.props.headingLevel : 'h2';
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
            button.style.fontFamily = fontCss(node.props.fontFamily || 'system', 'system');
            button.style.fontSize = String(node.props.fontSize || 16) + 'px';
            button.style.fontWeight = String(node.props.fontWeight || 400);
            button.style.lineHeight = String(node.props.lineHeight || 1.2);
            button.style.letterSpacing = String(node.props.letterSpacing || 0) + 'px';
            button.style.whiteSpace = node.props.autoSize === false ? 'normal' : 'nowrap';
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
        } else if (node.type === 'spacer') {
            wrap.classList.add('h18-clean-node-preview--spacer');
            wrap.textContent = 'Mellemrum · ' + Math.max(0, node.geometry.desktop.h * ROW_PX) + ' px';
        } else if (node.type === 'divider') {
            wrap.classList.add('h18-clean-node-preview--divider');
            const line = document.createElement('span');
            line.className = 'h18-vd-divider-line';
            const vertical = node.props.orientation === 'vertical';
            line.style.width = vertical ? String(node.props.lineWidth || 1) + 'px' : '100%';
            line.style.height = vertical ? '100%' : String(node.props.lineWidth || 1) + 'px';
            line.style.borderStyle = node.props.lineStyle || 'solid';
            line.style.borderColor = node.props.lineColor || '#c3c4c7';
            line.style.borderWidth = vertical ? '0 0 0 ' + String(node.props.lineWidth || 1) + 'px' : String(node.props.lineWidth || 1) + 'px 0 0 0';
            wrap.appendChild(line);
        } else if (node.type === 'icon') {
            wrap.classList.add('h18-clean-node-preview--icon');
            wrap.style.justifyContent = ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'center';
            const icon = document.createElement('span');
            icon.className = 'h18-vd-icon-preview';
            icon.style.width = String(node.props.iconSize || 32) + 'px'; icon.style.height = String(node.props.iconSize || 32) + 'px';
            icon.style.color = node.props.iconColor || '#30382a';
            icon.style.background = node.props.backgroundTransparent === false ? (node.props.background || '#ffffff') : 'transparent';
            icon.style.padding = String(node.props.padding || 0) + 'px'; icon.style.borderRadius = String(node.props.radius || 0) + 'px';
            icon.innerHTML = registryIconSvgMarkup(node.props.iconSet || 'core', node.props.icon || 'star'); wrap.appendChild(icon);
        } else if (node.type === 'badge') {
            wrap.classList.add('h18-clean-node-preview--badge');
            wrap.style.justifyContent = ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-start';
            const badge = document.createElement('span'); badge.className = 'h18-vd-badge-preview'; badge.textContent = String(node.props.text || 'Badge');
            badge.style.background = node.props.background || '#c3ae83'; badge.style.color = node.props.textColor || '#30382a'; badge.style.fontFamily = fontCss(node.props.fontFamily || 'system');
            badge.style.fontSize = String(node.props.fontSize || 13) + 'px'; badge.style.fontWeight = String(node.props.fontWeight || 700); badge.style.padding = String(node.props.paddingY || 5) + 'px ' + String(node.props.paddingX || 12) + 'px'; badge.style.borderRadius = String(node.props.radius || 20) + 'px'; wrap.appendChild(badge);
        } else if (node.type === 'link') {
            wrap.classList.add('h18-clean-node-preview--link'); wrap.style.justifyContent = ({left:'flex-start',center:'center',right:'flex-end'})[node.props.align] || 'flex-start';
            const link = document.createElement('span'); link.className = 'h18-vd-link-preview'; link.textContent = String(node.props.text || 'Læs mere →'); link.style.color = node.props.textColor || '#2271b1'; link.style.fontFamily = fontCss(node.props.fontFamily || 'system'); link.style.fontSize = String(node.props.fontSize || 16) + 'px'; link.style.fontWeight = String(node.props.fontWeight || 600); link.style.lineHeight = String(node.props.lineHeight || 1.3); link.style.letterSpacing = String(node.props.letterSpacing || 0) + 'px'; link.style.textDecoration = node.props.underline ? 'underline' : 'none'; wrap.appendChild(link);
        } else if (node.type === 'datalist') {
            wrap.classList.add('h18-clean-node-preview--datalist'); const list = document.createElement('div'); list.className = 'h18-vd-datalist-preview' + (node.props.layout === 'stacked' ? ' is-stacked' : ''); list.style.setProperty('--h18-vd-label-width', String(node.props.labelWidth || 40) + '%'); list.style.fontFamily = fontCss(node.props.fontFamily || 'system'); list.style.fontSize = String(node.props.fontSize || 15) + 'px';
            normalizePairRows(node.props.rows).forEach(function (row, index) { const item = document.createElement('div'); item.className = 'h18-vd-datalist-row'; item.style.background = node.props.zebra && index % 2 ? (node.props.zebraBackground || '#f6f7f7') : (node.props.background || '#ffffff'); if (node.props.showDividers && index) { item.style.borderTop = '1px solid ' + (node.props.lineColor || '#dcdcde'); } const label = document.createElement('span'); label.className = 'h18-vd-datalist-label'; label.textContent = row.label; label.style.padding = String(node.props.cellPadding || 8) + 'px'; label.style.color = node.props.labelColor || '#30382a'; label.style.fontWeight = String(node.props.labelWeight || 600); const value = document.createElement('span'); value.textContent = row.value; value.style.padding = String(node.props.cellPadding || 8) + 'px'; value.style.color = node.props.valueColor || '#30382a'; value.style.fontWeight = String(node.props.valueWeight || 400); item.appendChild(label); item.appendChild(value); list.appendChild(item); }); wrap.appendChild(list);
        } else if (node.type === 'table') {
            wrap.classList.add('h18-clean-node-preview--table');
            const table = document.createElement('table'); table.className = 'h18-vd-table-preview'; table.style.fontFamily = fontCss(node.props.fontFamily || 'system'); table.style.fontSize = String(node.props.fontSize || 14) + 'px';
            const grid = tableGrid(node), selectedCells = new Set(tableSelectionKeys(node));
            function configureCell(cell, key) {
                cell.dataset.vdTableCell = key; applyTableCellBorders(cell,node,key); if (selectedCells.has(key)) { cell.classList.add('is-vd-table-cell-selected'); }
                cell.addEventListener('click', function (event) { event.preventDefault(); event.stopPropagation(); selectTableCell(node,key,event); });
            }
            const head = document.createElement('thead'), hr = document.createElement('tr');
            grid.headers.forEach(function (value,col) { const th = document.createElement('th'); th.textContent = value; th.style.background = node.props.headerBackground || '#30382a'; th.style.color = node.props.headerTextColor || '#ffffff'; th.style.fontWeight = String(node.props.headerWeight || 700); th.style.padding = String(node.props.cellPadding || 8) + 'px'; configureCell(th,'h'+col); hr.appendChild(th); }); head.appendChild(hr); table.appendChild(head);
            const body = document.createElement('tbody');
            grid.rows.forEach(function (row,rowIndex) { const tr = document.createElement('tr'); row.forEach(function (value,col) { const td = document.createElement('td'); td.textContent = value; td.style.background = node.props.zebra && rowIndex % 2 ? (node.props.zebraBackground || '#f6f7f7') : (node.props.cellBackground || '#ffffff'); td.style.color = node.props.cellTextColor || '#30382a'; td.style.padding = String(node.props.cellPadding || 8) + 'px'; configureCell(td,'r'+rowIndex+'c'+col); tr.appendChild(td); }); body.appendChild(tr); }); table.appendChild(body); wrap.appendChild(table);
        } else if (node.type === 'vehiclelist') {
            wrap.classList.add('h18-clean-node-preview--vehiclelist');
            const records = vehicleRecords().filter(function (record) { return String(record.status || '') === 'publish'; }).slice(0, node.props.limit || 50);
            const grid = document.createElement('div'); grid.className = 'h18-vd-vehicle-list-preview'; grid.style.gridTemplateColumns = 'repeat(' + String(node.props.columns || 3) + ',minmax(0,1fr))'; grid.style.gap = String(node.props.cardGap || 18) + 'px';
            if (!records.length) { grid.textContent = 'Ingen publicerede køretøjer endnu · opret dem under Manager → Køretøjer'; }
            records.forEach(function (record) {
                const card = document.createElement('article'); card.className = 'h18-vd-vehicle-card-preview'; card.style.background = node.props.cardBackground || '#ffffff'; card.style.color = node.props.textColor || '#30382a'; card.style.padding = String(node.props.cardPadding || 12) + 'px'; card.style.borderRadius = String(node.props.cardRadius || 4) + 'px';
                if (node.props.showImage && record.featuredUrl) { const img = document.createElement('img'); img.src = String(record.featuredUrl); img.alt = ''; img.style.height = String(node.props.imageHeight || 180) + 'px'; card.appendChild(img); }
                const title = document.createElement('strong'); title.textContent = String(record.title || 'Køretøj'); card.appendChild(title);
                const category = vehicleCategory(record); if (node.props.showCategory && category) { const meta = document.createElement('small'); meta.textContent = category; meta.style.color = node.props.accentColor || '#c3ae83'; card.appendChild(meta); }
                if (node.props.showSummary && record.summary) { const summary = document.createElement('p'); summary.textContent = String(record.summary); card.appendChild(summary); }
                grid.appendChild(card);
            }); wrap.appendChild(grid);
        } else if (node.type === 'vehicledetail') {
            wrap.classList.add('h18-clean-node-preview--vehicledetail');
            const record = vehicleRecordById(node.props.recordId) || vehicleRecords().find(function (item) { return String(item.status || '') === 'publish'; }) || null;
            if (!record) { wrap.textContent = 'Ingen køretøjer at vise · opret data under Manager → Køretøjer'; }
            else {
                const detail = document.createElement('div'); detail.className = 'h18-vd-vehicle-detail-preview'; detail.style.background = node.props.background || '#ffffff'; detail.style.color = node.props.textColor || '#30382a'; detail.style.padding = String(node.props.padding || 16) + 'px'; detail.style.borderRadius = String(node.props.radius || 4) + 'px';
                if (record.featuredUrl) { const img = document.createElement('img'); img.src = String(record.featuredUrl); img.alt = ''; img.style.height = String(node.props.imageHeight || 360) + 'px'; detail.appendChild(img); }
                const title = document.createElement('h3'); title.textContent = String(record.title || 'Køretøj'); detail.appendChild(title);
                const category = vehicleCategory(record); if (node.props.showCategory && category) { const meta = document.createElement('strong'); meta.textContent = category; meta.style.color = node.props.accentColor || '#c3ae83'; detail.appendChild(meta); }
                if (node.props.showSummary && record.summary) { const summary = document.createElement('p'); summary.textContent = String(record.summary); detail.appendChild(summary); }
                if (node.props.showAttributes && Array.isArray(record.attributes)) { const dl = document.createElement('dl'); record.attributes.filter(function (a) { return a && a.enabled !== false && String(a.value == null ? '' : a.value) !== ''; }).slice(0,12).forEach(function (a) { const dt=document.createElement('dt');dt.textContent=String(a.label||a.key||'Felt');const dd=document.createElement('dd');dd.textContent=String(a.value);dl.appendChild(dt);dl.appendChild(dd); }); detail.appendChild(dl); }
                wrap.appendChild(detail);
            }
        } else if (node.type === 'eventlist') {
            wrap.classList.add('h18-clean-node-preview--eventlist'); let records=eventRecords().filter(function(record){return String(record.status||'')==='publish';}); if(node.props.dateFilter==='upcoming'){records=records.filter(function(record){return !eventIsPast(record);});}else if(node.props.dateFilter==='past'){records=records.filter(eventIsPast);} records=records.slice(0,node.props.limit||50);
            const grid=document.createElement('div'); grid.className='h18-vd-event-list-preview'; grid.style.gridTemplateColumns='repeat('+String(node.props.columns||3)+',minmax(0,1fr))'; grid.style.gap=String(node.props.cardGap||18)+'px'; if(!records.length){grid.textContent='Ingen publicerede events matcher filteret · opret dem under Manager → Events';}
            records.forEach(function(record){const card=document.createElement('article'); card.className='h18-vd-event-card-preview'; card.style.padding=String(node.props.cardPadding||12)+'px'; card.style.borderRadius=String(node.props.cardRadius||4)+'px'; card.style.background=node.props.cardBackground||'#ffffff'; card.style.color=node.props.textColor||'#30382a'; if(node.props.showImage!==false&&record.featuredUrl){const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt='';img.style.height=String(node.props.imageHeight||180)+'px';card.appendChild(img);} const title=document.createElement('strong');title.textContent=String(record.title||'Event');card.appendChild(title);const fields=record.fields&&typeof record.fields==='object'?record.fields:{};if(node.props.showDate!==false&&eventDateLabel(record)){const meta=document.createElement('small');meta.textContent=eventDateLabel(record);meta.style.color=node.props.accentColor||'#c3ae83';card.appendChild(meta);}if(node.props.showLocation!==false&&fields.location){const loc=document.createElement('small');loc.textContent=String(fields.location);card.appendChild(loc);}if(node.props.showSummary!==false&&record.summary){const p=document.createElement('p');p.textContent=String(record.summary);card.appendChild(p);}grid.appendChild(card);}); wrap.appendChild(grid);
        } else if (node.type === 'eventdetail') {
            wrap.classList.add('h18-clean-node-preview--eventdetail'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; const box=document.createElement('article');box.className='h18-vd-event-detail-preview';box.style.background=node.props.background||'#ffffff';box.style.color=node.props.textColor||'#30382a';box.style.padding=String(node.props.padding||16)+'px';box.style.borderRadius=String(node.props.radius||4)+'px'; if(!record){box.textContent='Vælg et event i Inspector eller opret et under Manager → Events';wrap.appendChild(box);}else{if(node.props.showImage!==false&&record.featuredUrl){const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt='';img.style.height=String(node.props.imageHeight||360)+'px';box.appendChild(img);}const h=document.createElement('h3');h.textContent=String(record.title||'Event');box.appendChild(h);const fields=record.fields&&typeof record.fields==='object'?record.fields:{};if(node.props.showDate!==false&&eventDateLabel(record)){const meta=document.createElement('p');meta.textContent=eventDateLabel(record);meta.style.color=node.props.accentColor||'#c3ae83';box.appendChild(meta);}if(node.props.showLocation!==false&&fields.location){const loc=document.createElement('p');loc.textContent=String(fields.location);box.appendChild(loc);}if(node.props.showSummary!==false&&record.summary){const p=document.createElement('p');p.textContent=String(record.summary);box.appendChild(p);}if(node.props.showDescription!==false&&fields.description){const desc=document.createElement('div');desc.innerHTML=richPreviewHtml(String(fields.description));box.appendChild(desc);}wrap.appendChild(box);}

        } else if (node.type === 'eventvalue') {
            wrap.classList.add('h18-clean-node-preview--eventvalue'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const key=String(node.props.valueKey||'title'); let value=''; if(record){if(key==='date'){value=eventDateLabel(record);}else if(key==='location'){value=String(fields.location||'');}else if(key==='summary'){value=String(record.summary||'');}else if(key==='description'){value=String(fields.description||'');}else{value=String(record.title||'');}} const labels={title:'Eventtitel',date:'Dato / tid',location:'Sted',summary:'Kort beskrivelse',description:'Beskrivelse'}; const tag=document.createElement(['DIV','P','H1','H2','H3','H4','H5','H6'].includes(String(node.props.tag||'').toUpperCase())?String(node.props.tag):'div'); tag.style.fontFamily=fontCss(node.props.fontFamily||'system');tag.style.fontSize=String(node.props.fontSize||16)+'px';tag.style.fontWeight=String(node.props.fontWeight||400);tag.style.lineHeight=String(node.props.lineHeight||1.5);tag.style.letterSpacing=String(node.props.letterSpacing||0)+'px';tag.style.color=node.props.textColor||'#30382a';tag.style.textAlign=node.props.align||'left';tag.style.padding=String(node.props.padding||0)+'px';tag.style.borderRadius=String(node.props.radius||0)+'px';tag.style.background=node.props.backgroundTransparent===false?(node.props.background||'#ffffff'):'transparent';if(key==='description'&&value){tag.innerHTML=richPreviewHtml(value);}else{tag.textContent=value||labels[key]||'Eventværdi';}wrap.appendChild(tag);
        } else if (node.type === 'eventimage') {
            wrap.classList.add('h18-clean-node-preview--eventimage'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; if(!record||!record.featuredUrl){wrap.textContent='Eventbillede · eventet har intet billede';}else{const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt=String(record.title||'');img.style.display='block';img.style.width='100%';img.style.height=String(node.props.imageHeight||360)+'px';img.style.objectFit=node.props.fit==='contain'?'contain':'cover';img.style.objectPosition=String(node.props.focalX||50)+'% '+String(node.props.focalY||50)+'%';img.style.background=node.props.background||'#ffffff';img.style.borderRadius=String(node.props.radius||4)+'px';wrap.appendChild(img);}

        } else if (node.type === 'eventfacts') {
            wrap.classList.add('h18-clean-node-preview--eventfacts'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; const fields=record&&record.fields&&typeof record.fields==='object'?record.fields:{}; const start=String(fields.start||''); const end=String(fields.end||''); const dateOnly=function(value){const m=String(value||'').match(/^(\d{4})-(\d{2})-(\d{2})T/);return m?m[3]+'-'+m[2]+'-'+m[1]:'';}; const timeOnly=function(value){const m=String(value||'').match(/^\d{4}-\d{2}-\d{2}T(\d{2}:\d{2})/);return m?m[1]:'';}; const sd=dateOnly(start),ed=dateOnly(end),st=timeOnly(start),et=timeOnly(end); const facts=[]; if(node.props.showDate!==false)facts.push(['Dato',sd&&ed&&ed!==sd?sd+' – '+ed:(sd||ed)]);if(node.props.showTime!==false)facts.push(['Tid',st?(et?st+' – '+et:st):et]);if(node.props.showLocation!==false)facts.push(['Sted',String(fields.location||'')]);if(node.props.showAddress!==false)facts.push(['Adresse',String(fields.address||'')]);if(node.props.showContact!==false)facts.push(['Kontakt',String(fields.contact||'')]); const grid=document.createElement('div');grid.style.display='grid';grid.style.gridTemplateColumns='repeat(auto-fit,minmax('+String(node.props.minCardWidth||150)+'px,1fr))';grid.style.gap=String(node.props.gap||12)+'px';facts.forEach(function(fact){const card=document.createElement('div');card.style.minWidth='0';card.style.background=node.props.cardBackground||'#f4f1e8';card.style.borderLeft='4px solid '+String(node.props.accentColor||'#c3ae83');card.style.padding=String(node.props.paddingY||16)+'px '+String(node.props.paddingX||16)+'px';card.style.borderRadius=String(node.props.radius||0)+'px';const label=document.createElement('strong');label.textContent=fact[0];label.style.display='block';label.style.marginBottom='4px';label.style.color=node.props.labelColor||'#30382a';label.style.fontFamily=fontCss(node.props.labelFontFamily||'system');label.style.fontSize=String(node.props.labelFontSize||16)+'px';label.style.fontWeight=String(node.props.labelFontWeight||700);label.style.lineHeight=String(node.props.lineHeight||1.35);const value=document.createElement('span');value.textContent=fact[1]||'';value.style.display='block';value.style.color=node.props.valueColor||'#30382a';value.style.fontFamily=fontCss(node.props.valueFontFamily||'system');value.style.fontSize=String(node.props.valueFontSize||16)+'px';value.style.fontWeight=String(node.props.valueFontWeight||400);value.style.lineHeight=String(node.props.lineHeight||1.35);card.appendChild(label);card.appendChild(value);grid.appendChild(card);});if(!record){const hint=document.createElement('div');hint.textContent='Eventfaktabånd · vælg preview-event';grid.appendChild(hint);}wrap.appendChild(grid);

        } else if (node.type === 'eventfield') {
            wrap.classList.add('h18-clean-node-preview--eventfield'); const record=eventRecordById(node.props.recordId)||eventRecords().find(function(item){return String(item.status||'')==='publish';})||null; const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[]; const def=defs.find(function(row){return String(row.id||'')===String(node.props.fieldKey||'');})||null; const attr=record&&Array.isArray(record.attributes)?record.attributes.find(function(row){return row&&String(row.key||'')===String(node.props.fieldKey||'');}):null; const box=document.createElement('div');box.style.padding=String(node.props.padding||0)+'px';box.style.borderRadius=String(node.props.radius||0)+'px';box.style.color=node.props.textColor||'#30382a';box.style.fontFamily=fontCss(node.props.fontFamily||'system');box.style.fontSize=String(node.props.fontSize||16)+'px';box.style.fontWeight=String(node.props.fontWeight||400);box.style.lineHeight=String(node.props.lineHeight||1.5);if(node.props.background){box.style.background=node.props.background;} if(!record){box.textContent='Eventfelt · '+String(def&&def.label||node.props.fieldKey||'vælg felt');}else{const empty=!attr||String(attr.value==null?'':attr.value)==='';if(empty&&node.props.showWhenEmpty!==true){box.textContent='Eventfelt · '+String(def&&def.label||node.props.fieldKey||'vælg felt');}else{if(node.props.showHeading!==false){const h=document.createElement('h3');h.textContent=String(def&&def.label||attr.label||node.props.fieldKey);h.style.margin='0 0 '+String(node.props.headingGap||12)+'px';h.style.color=node.props.headingColor||'#30382a';h.style.fontFamily=fontCss(node.props.headingFontFamily||'body');h.style.fontSize=String(node.props.headingFontSize||40)+'px';h.style.fontWeight=String(node.props.headingFontWeight||400);h.style.lineHeight=String(node.props.headingLineHeight||1.15);box.appendChild(h);}const value=document.createElement('div'); if(!empty){if(String(def&&def.type||(attr&&attr.type)||'text')==='richtext'){value.innerHTML=richPreviewHtml(String(attr&&attr.value||''));}else{value.textContent=typeof (attr&&attr.value)==='boolean'?(attr.value?'Ja':'Nej'):String(attr&&attr.value||'');}box.appendChild(value);}}}wrap.appendChild(box);
        } else if (node.type === 'gallerylist') {
            wrap.classList.add('h18-clean-node-preview--gallerylist'); const records=galleryRecords().filter(function(record){return String(record.status||'')==='publish';}).slice(0,node.props.limit||50); const grid=document.createElement('div'); grid.className='h18-vd-gallery-list-preview'; grid.style.gridTemplateColumns='repeat('+String(node.props.columns||3)+',minmax(0,1fr))'; grid.style.gap=String(node.props.cardGap||18)+'px'; if(!records.length){grid.textContent='Ingen publicerede album · opret dem under Manager → Billedgalleri';} records.forEach(function(record){const card=document.createElement('article');card.className='h18-vd-gallery-card-preview';card.style.padding=String(node.props.cardPadding||12)+'px';card.style.borderRadius=String(node.props.cardRadius||4)+'px';card.style.background=node.props.cardBackground||'#ffffff';card.style.color=node.props.textColor||'#30382a';if(node.props.showImage!==false&&record.featuredUrl){const img=document.createElement('img');img.src=String(record.featuredUrl);img.alt='';img.style.height=String(node.props.imageHeight||220)+'px';card.appendChild(img);}const title=document.createElement('strong');title.textContent=String(record.title||'Album');card.appendChild(title);if(node.props.showCount!==false){const count=document.createElement('small');count.textContent=String(galleryImageCount(record))+' billeder';count.style.color=node.props.accentColor||'#c3ae83';card.appendChild(count);}if(node.props.showSummary!==false&&record.summary){const p=document.createElement('p');p.textContent=String(record.summary);card.appendChild(p);}grid.appendChild(card);});wrap.appendChild(grid);
        } else if (node.type === 'gallerydetail') {
            wrap.classList.add('h18-clean-node-preview--gallerydetail'); const record=galleryRecordById(node.props.recordId)||galleryRecords().find(function(item){return String(item.status||'')==='publish';})||null; const box=document.createElement('article');box.className='h18-vd-gallery-detail-preview';box.style.background=node.props.background||'#ffffff';box.style.color=node.props.textColor||'#30382a';box.style.padding=String(node.props.padding||16)+'px';box.style.borderRadius=String(node.props.radius||4)+'px';if(!record){box.textContent='Vælg et album i Inspector eller opret et under Manager → Billedgalleri';wrap.appendChild(box);}else{const h=document.createElement('h3');h.textContent=String(record.title||'Album');box.appendChild(h);const images=document.createElement('div');images.className='h18-vd-gallery-images-preview';images.style.gridTemplateColumns='repeat('+String(node.props.columns||4)+',minmax(0,1fr))';images.style.gap=String(node.props.gap||12)+'px';(Array.isArray(record.imageUrls)?record.imageUrls:[]).forEach(function(item){const img=document.createElement('img');img.src=String(item&&item.url||'');img.alt='';img.style.height=String(node.props.imageHeight||220)+'px';if(img.src){images.appendChild(img);}});box.appendChild(images);const fields=record.fields&&typeof record.fields==='object'?record.fields:{};if(node.props.showDescription!==false&&fields.description){const desc=document.createElement('div');desc.innerHTML=richPreviewHtml(String(fields.description));box.appendChild(desc);}wrap.appendChild(box);}

        } else if (node.type === 'contactform' || node.type === 'membershipform') {
            wrap.classList.add('h18-clean-node-preview--form');
            const membership = node.type === 'membershipform';
            const box = document.createElement('div'); box.className = 'h18-vd-form-preview h18-vd-form-preview--' + node.type;
            box.style.background = node.props.background || '#f4f1e8';
            box.style.color = node.props.textColor || '#30382a';
            box.style.padding = String(node.props.padding || 24) + 'px';
            box.style.borderRadius = String(node.props.radius || 6) + 'px';
            box.style.setProperty('--h18-form-preview-field-bg', node.props.fieldBackground || '#ffffff');
            box.style.setProperty('--h18-form-preview-accent', node.props.accentColor || '#30382a');

            const heading = document.createElement('h2');
            heading.textContent = String(node.props.heading || (membership ? 'Bliv medlem' : 'Kontakt os'));
            if (heading.textContent) { box.appendChild(heading); }
            const intro = document.createElement('p'); intro.className = 'h18-vd-form-preview-intro';
            intro.textContent = String(node.props.intro || ''); if (intro.textContent) { box.appendChild(intro); }

            const form = document.createElement('div'); form.className = 'h18-vd-form-preview-body';
            const grid = document.createElement('div'); grid.className = 'h18-vd-form-preview-grid';
            const addField = function (labelText, kind, wide) {
                const field = document.createElement('label'); field.className = 'h18-vd-form-preview-field' + (wide ? ' is-wide' : '');
                const label = document.createElement('span'); label.textContent = labelText; field.appendChild(label);
                const control = kind === 'textarea' ? document.createElement('textarea') : document.createElement('input');
                if (kind !== 'textarea') { control.type = kind || 'text'; }
                else { control.rows = 5; }
                control.disabled = true; control.tabIndex = -1; control.setAttribute('aria-hidden', 'true');
                field.appendChild(control); grid.appendChild(field);
            };
            addField('Navn *', 'text', false);
            addField('E-mail *', 'email', false);
            if (membership || node.props.showPhone !== false) { addField('Telefon' + (membership ? ' *' : ''), 'tel', false); }
            if (membership) {
                addField('Adresse *', 'text', false);
                addField('Postnr. *', 'text', false);
                addField('By *', 'text', false);
                addField('Kommentar', 'textarea', true);
            } else {
                addField('Emne *', 'text', false);
                addField('Besked *', 'textarea', true);
            }
            form.appendChild(grid);
            if (node.props.requireConsent !== false) {
                const consent = document.createElement('label'); consent.className = 'h18-vd-form-preview-consent';
                const checkbox = document.createElement('input'); checkbox.type = 'checkbox'; checkbox.disabled = true; checkbox.tabIndex = -1;
                const consentText = document.createElement('span'); consentText.textContent = 'Jeg accepterer, at oplysningerne bruges til at besvare min henvendelse.';
                consent.appendChild(checkbox); consent.appendChild(consentText); form.appendChild(consent);
            }
            const submit = document.createElement('button'); submit.type = 'button'; submit.disabled = true; submit.className = 'h18-vd-form-preview-submit';
            submit.textContent = String(node.props.buttonText || (membership ? 'Send indmeldelse' : 'Send besked'));
            form.appendChild(submit); box.appendChild(form); wrap.appendChild(box);
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
            title.textContent = ({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP',menu:'MENU',spacer:'MELLEMRUM',divider:'SKILLELINJE',icon:'IKON',badge:'BADGE',link:'LINK',datalist:'DATA LIST',table:'TABEL',vehiclelist:'KØRETØJSLISTE',vehicledetail:'KØRETØJSDETALJE',eventlist:'EVENTLISTE',eventdetail:'EVENTDETALJE',eventvalue:'EVENTVÆRDI',eventimage:'EVENTBILLEDE',eventfacts:'EVENTFAKTABÅND',eventfield:'EVENTFELT',gallerylist:'GALLERIOVERSIGT',gallerydetail:'ALBUMVISNING',contactform:'KONTAKTFORMULAR',membershipform:'BLIV MEDLEM-FORMULAR'}[node.type] || node.type.toUpperCase()) + ' · ' + node.id.slice(-8);
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
        let html = '<div class="h18-clean-inspector-head"><strong>' + escapeHtml(({section:'SEKTION',container:'KASSE',text:'TEKST',image:'BILLEDE',button:'KNAP',menu:'MENU',spacer:'MELLEMRUM',divider:'SKILLELINJE',icon:'IKON',badge:'BADGE',link:'LINK',datalist:'DATA LIST',table:'TABEL',vehiclelist:'KØRETØJSLISTE',vehicledetail:'KØRETØJSDETALJE',eventlist:'EVENTLISTE',eventdetail:'EVENTDETALJE',eventvalue:'EVENTVÆRDI',eventimage:'EVENTBILLEDE',eventfacts:'EVENTFAKTABÅND',eventfield:'EVENTFELT',gallerylist:'GALLERIOVERSIGT',gallerydetail:'ALBUMVISNING',contactform:'KONTAKTFORMULAR',membershipform:'BLIV MEDLEM-FORMULAR'}[node.type] || node.type.toUpperCase())) + '</strong><code>' + escapeHtml(node.id) + '</code></div>';
        html += '<div class="h18-clean-field-grid"><label>X / 120<input data-field="gx" type="number" min="0" max="119" value="' + g.x + '"></label><label>Bredde / 120<input data-field="gw" type="number" min="1" max="120" value="' + g.w + '"></label><label>Y · 8px<input data-field="gy" type="number" value="' + g.y + '"></label><label>Højde · 8px<input data-field="gh" type="number" min="0" value="' + g.h + '"></label></div>';
        html += '<div class="h18-vd-nudge-inspector"><strong>Finjustering · pixels</strong><div class="h18-clean-field-grid"><label>Offset X px<input data-field="offsetX" type="number" min="-2000" max="2000" value="' + (node.props.offsetX || 0) + '"></label><label>Offset Y px<input data-field="offsetY" type="number" min="-2000" max="2000" value="' + (node.props.offsetY || 0) + '"></label></div><button type="button" class="button" id="h18-clean-reset-offset">Nulstil finjustering</button><p class="description">Piletaster flytter 1 px. Shift + piletast flytter 10 px. Grid-positionen ændres ikke.</p></div>';
        if (node.type === 'text') {
            html += '<label>Overskrift <span class="description">(valgfri)</span><input data-field="heading" type="text" value="' + escapeAttr(node.props.heading || '') + '"></label>';
            html += '<label>Overskrifttype<select data-field="headingLevel"><option value="h1"' + (node.props.headingLevel === 'h1' ? ' selected' : '') + '>H1</option><option value="h2"' + (node.props.headingLevel === 'h2' ? ' selected' : '') + '>H2</option><option value="h3"' + (node.props.headingLevel === 'h3' ? ' selected' : '') + '>H3</option><option value="h4"' + (node.props.headingLevel === 'h4' ? ' selected' : '') + '>H4</option><option value="h5"' + (node.props.headingLevel === 'h5' ? ' selected' : '') + '>H5</option><option value="h6"' + (node.props.headingLevel === 'h6' ? ' selected' : '') + '>H6</option></select></label>';
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
            html += '<div class="h18-vd-typography"><strong>Typografi · knap</strong><div class="h18-clean-field-grid"><label>Skrifttype<select data-field="fontFamily">' + fontOptions(node.props.fontFamily || 'system', false) + '</select></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="120" value="' + (node.props.fontSize || 16) + '"></label><label>Tykkelse<select data-field="fontWeight">' + [300,400,500,600,700,800,900].map(function (v) { return '<option value="' + v + '"' + (parseInt(node.props.fontWeight || 400, 10) === v ? ' selected' : '') + '>' + v + '</option>'; }).join('') + '</select></label><label>Linjeafstand<input data-field="lineHeight" type="number" step="0.1" min="0.8" max="3" value="' + (node.props.lineHeight || 1.2) + '"></label><label>Bogstavafstand px<input data-field="letterSpacing" type="number" step="0.1" min="-10" max="30" value="' + (node.props.letterSpacing || 0) + '"></label></div></div>';
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
        } else if (node.type === 'spacer') {
            html += '<div class="h18-vd-element-note"><strong>Mellemrum</strong><br>Elementet er usynligt på frontend. Brug Højde ovenfor og responsive Desktop/Laptop/Tablet/Mobil-indstillinger til at styre luften.</div>';
        } else if (node.type === 'divider') {
            html += '<label>Retning<select data-field="orientation"><option value="horizontal"' + (node.props.orientation === 'horizontal' ? ' selected' : '') + '>Vandret</option><option value="vertical"' + (node.props.orientation === 'vertical' ? ' selected' : '') + '>Lodret</option></select></label><div class="h18-clean-field-grid"><label>Tykkelse px<input data-field="lineWidth" type="number" min="1" max="20" value="' + (node.props.lineWidth || 1) + '"></label><label>Farve<input data-field="lineColor" type="color" value="' + escapeAttr(node.props.lineColor || '#c3c4c7') + '"></label></div><label>Stil<select data-field="lineStyle"><option value="solid"' + (node.props.lineStyle === 'solid' ? ' selected' : '') + '>Solid</option><option value="dashed"' + (node.props.lineStyle === 'dashed' ? ' selected' : '') + '>Stiplet</option><option value="dotted"' + (node.props.lineStyle === 'dotted' ? ' selected' : '') + '>Prikket</option></select></label>';
        } else if (node.type === 'icon') {
            const selection = normalizeIconSelection(node.props.iconSet || 'core', node.props.icon || 'star');
            html += '<button type="button" class="button" id="h18-vd-icon-library-open">Vælg ikon fra bibliotek</button><div class="h18-vd-icon-current"><span class="h18-vd-icon-current-mark">' + registryIconSvgMarkup(selection.set,selection.icon) + '</span><span><strong>' + escapeHtml(currentIconLabel(selection.set,selection.icon)) + '</strong><br><small>' + escapeHtml(selection.set) + '</small></span></div><div class="h18-clean-field-grid"><label>Størrelse px<input data-field="iconSize" type="number" min="8" max="240" value="' + (node.props.iconSize || 32) + '"></label><label>Farve<input data-field="iconColor" type="color" value="' + escapeAttr(node.props.iconColor || '#30382a') + '"></label></div><label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label><label class="h18-clean-checkbox"><input data-field="backgroundTransparent" type="checkbox"' + (node.props.backgroundTransparent !== false ? ' checked' : '') + '> Gennemsigtig baggrund</label><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#ffffff') + '"></label><div class="h18-clean-field-grid"><label>Padding px<input data-field="padding" type="number" min="0" max="120" value="' + (node.props.padding || 0) + '"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 0) + '"></label></div>';
        } else if (node.type === 'badge') {
            html += '<label>Tekst<input data-field="badgeText" type="text" value="' + escapeAttr(node.props.text || 'Badge') + '"></label><label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label><div class="h18-clean-field-grid"><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#c3ae83') + '"></label><label>Tekst<input data-field="textColor" type="color" value="' + escapeAttr(node.props.textColor || '#30382a') + '"></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="80" value="' + (node.props.fontSize || 13) + '"></label><label>Tykkelse<input data-field="fontWeight" type="number" min="100" max="900" step="100" value="' + (node.props.fontWeight || 700) + '"></label><label>Padding X<input data-field="paddingX" type="number" min="0" max="120" value="' + (node.props.paddingX || 12) + '"></label><label>Padding Y<input data-field="paddingY" type="number" min="0" max="120" value="' + (node.props.paddingY || 5) + '"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 20) + '"></label></div>';
        } else if (node.type === 'link') {
            html += '<label>Linktekst<input data-field="linkText" type="text" value="' + escapeAttr(node.props.text || 'Læs mere →') + '"></label><label>Linktype<select data-field="linkType"><option value="page"' + (node.props.linkType === 'page' ? ' selected' : '') + '>Intern side</option><option value="url"' + (node.props.linkType === 'url' ? ' selected' : '') + '>Ekstern URL</option><option value="anchor"' + (node.props.linkType === 'anchor' ? ' selected' : '') + '>Anker</option><option value="email"' + (node.props.linkType === 'email' ? ' selected' : '') + '>E-mail</option><option value="phone"' + (node.props.linkType === 'phone' ? ' selected' : '') + '>Telefon</option></select></label>';
            if (node.props.linkType === 'page') { html += '<label>Intern side<select data-field="pageId"><option value="0">Vælg side…</option>' + (Array.isArray(CFG.pages) ? CFG.pages.map(function (page) { const id = parseInt(page.id || 0, 10) || 0; return '<option value="' + id + '"' + (parseInt(node.props.pageId || 0, 10) === id ? ' selected' : '') + '>' + escapeHtml(String(page.title || ('Side ' + id))) + '</option>'; }).join('') : '') + '</select></label>'; } else { html += '<label>Destination<input data-field="url" type="text" value="' + escapeAttr(node.props.url || '') + '"></label>'; }
            html += '<label class="h18-clean-checkbox"><input data-field="targetBlank" type="checkbox"' + (node.props.targetBlank ? ' checked' : '') + '> Åbn i ny fane</label><label class="h18-clean-checkbox"><input data-field="underline" type="checkbox"' + (node.props.underline ? ' checked' : '') + '> Understreg link</label><label>Justering<select data-field="align"><option value="left"' + (node.props.align === 'left' ? ' selected' : '') + '>Venstre</option><option value="center"' + (node.props.align === 'center' ? ' selected' : '') + '>Midt</option><option value="right"' + (node.props.align === 'right' ? ' selected' : '') + '>Højre</option></select></label><div class="h18-clean-field-grid"><label>Tekstfarve<input data-field="textColor" type="color" value="' + escapeAttr(node.props.textColor || '#2271b1') + '"></label><label>Hoverfarve<input data-field="hoverTextColor" type="color" value="' + escapeAttr(node.props.hoverTextColor || '#135e96') + '"></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="120" value="' + (node.props.fontSize || 16) + '"></label><label>Tykkelse<input data-field="fontWeight" type="number" min="100" max="900" step="100" value="' + (node.props.fontWeight || 600) + '"></label></div>';
        } else if (node.type === 'datalist') {
            html += '<div class="h18-vd-structured-editor"><div class="h18-vd-element-note"><strong>Statisk Data List · test</strong><br>Én linje pr. felt: <code>Felt | Værdi</code>. Dynamisk datakilde kobles på i næste fundament-version.</div><label>Rækker<textarea data-field="dataRows" rows="7">' + escapeHtml(pairRowsText(node.props.rows)) + '</textarea></label><label>Layout<select data-field="dataLayout"><option value="rows"' + (node.props.layout === 'rows' ? ' selected' : '') + '>Felt + værdi i samme række</option><option value="stacked"' + (node.props.layout === 'stacked' ? ' selected' : '') + '>Felt over værdi</option></select></label><div class="h18-clean-field-grid"><label>Labelbredde %<input data-field="labelWidth" type="number" min="15" max="80" value="' + (node.props.labelWidth || 40) + '"></label><label>Cell padding px<input data-field="cellPadding" type="number" min="0" max="60" value="' + (node.props.cellPadding || 8) + '"></label><label>Skrift px<input data-field="fontSize" type="number" min="8" max="80" value="' + (node.props.fontSize || 15) + '"></label><label>Label tykkelse<input data-field="labelWeight" type="number" min="100" max="900" step="100" value="' + (node.props.labelWeight || 600) + '"></label><label>Værdi tykkelse<input data-field="valueWeight" type="number" min="100" max="900" step="100" value="' + (node.props.valueWeight || 400) + '"></label></div><label class="h18-clean-checkbox"><input data-field="showDividers" type="checkbox"' + (node.props.showDividers !== false ? ' checked' : '') + '> Skillelinjer mellem rækker</label><label class="h18-clean-checkbox"><input data-field="zebra" type="checkbox"' + (node.props.zebra ? ' checked' : '') + '> Zebra-baggrund</label><div class="h18-clean-field-grid"><label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#ffffff') + '"></label><label>Zebra<input data-field="zebraBackground" type="color" value="' + escapeAttr(node.props.zebraBackground || '#f6f7f7') + '"></label><label>Linje<input data-field="lineColor" type="color" value="' + escapeAttr(node.props.lineColor || '#dcdcde') + '"></label><label>Label<input data-field="labelColor" type="color" value="' + escapeAttr(node.props.labelColor || '#30382a') + '"></label><label>Værdi<input data-field="valueColor" type="color" value="' + escapeAttr(node.props.valueColor || '#30382a') + '"></label></div></div>';
        } else if (node.type === 'table') {
            const tableHeaders = normalizeHeaders(node.props.headers), selectedCells = tableSelectionKeys(node);
            html += '<div class="h18-vd-structured-editor"><div class="h18-vd-element-note"><strong>Statisk Tabel · test</strong><br>Kolonner og rækker redigeres med <code>|</code> som separator. Klik celler i preview for Excel-lignende kantstyring; Ctrl/Cmd vælger flere og Shift vælger et område.</div><label>Kolonner<input data-field="tableHeaders" type="text" value="' + escapeAttr(headersText(tableHeaders)) + '"></label><label>Rækker<textarea data-field="tableRows" rows="8">' + escapeHtml(matrixRowsText(node.props.rows, tableHeaders.length)) + '</textarea></label><label>Mobilvisning<select data-field="mobileTableMode"><option value="scroll"' + (node.props.mobileMode === 'scroll' ? ' selected' : '') + '>Horisontal scroll</option><option value="cards"' + (node.props.mobileMode === 'cards' ? ' selected' : '') + '>Kort · kolonnenavn + værdi</option></select></label><label>Tabelstandard for kanter<select data-field="tableBorderMode"><option value="all"' + (node.props.borderMode === 'all' ? ' selected' : '') + '>Alle kanter</option><option value="outer"' + (node.props.borderMode === 'outer' ? ' selected' : '') + '>Kun yderramme</option><option value="inner"' + (node.props.borderMode === 'inner' ? ' selected' : '') + '>Kun indvendige linjer</option><option value="none"' + (node.props.borderMode === 'none' ? ' selected' : '') + '>Ingen kanter</option></select></label><div class="h18-clean-field-grid"><label>Standard ramme px<input data-field="cellBorderWidth" type="number" min="0" max="10" value="' + (node.props.cellBorderWidth || 0) + '"></label><label>Standard streg<select data-field="cellBorderStyle"><option value="solid"' + (node.props.cellBorderStyle === 'solid' ? ' selected' : '') + '>Solid</option><option value="dashed"' + (node.props.cellBorderStyle === 'dashed' ? ' selected' : '') + '>Stiplet</option><option value="dotted"' + (node.props.cellBorderStyle === 'dotted' ? ' selected' : '') + '>Prikket</option></select></label><label>Standard farve<input data-field="cellBorderColor" type="color" value="' + escapeAttr(node.props.cellBorderColor || '#dcdcde') + '"></label><label>Cell padding px<input data-field="cellPadding" type="number" min="0" max="60" value="' + (node.props.cellPadding || 8) + '"></label><label>Skrift px<input data-field="fontSize" type="number" min="8" max="80" value="' + (node.props.fontSize || 14) + '"></label><label>Header tykkelse<input data-field="headerWeight" type="number" min="100" max="900" step="100" value="' + (node.props.headerWeight || 700) + '"></label></div><label class="h18-clean-checkbox"><input data-field="zebra" type="checkbox"' + (node.props.zebra !== false ? ' checked' : '') + '> Zebra-rækker</label><div class="h18-clean-field-grid"><label>Header baggrund<input data-field="headerBackground" type="color" value="' + escapeAttr(node.props.headerBackground || '#30382a') + '"></label><label>Header tekst<input data-field="headerTextColor" type="color" value="' + escapeAttr(node.props.headerTextColor || '#ffffff') + '"></label><label>Cell baggrund<input data-field="cellBackground" type="color" value="' + escapeAttr(node.props.cellBackground || '#ffffff') + '"></label><label>Cell tekst<input data-field="cellTextColor" type="color" value="' + escapeAttr(node.props.cellTextColor || '#30382a') + '"></label><label>Zebra<input data-field="zebraBackground" type="color" value="' + escapeAttr(node.props.zebraBackground || '#f6f7f7') + '"></label></div>';
            if (selectedCells.length) {
                html += '<div class="h18-vd-table-selection-note"><strong>' + selectedCells.length + ' celle' + (selectedCells.length === 1 ? '' : 'r') + ' markeret.</strong><div class="h18-vd-table-selection-help">Klik = ny markering · Ctrl/Cmd+klik = til/fra · Shift+klik = rektangulært område.</div></div><div class="h18-vd-table-border-designer"><h4>Kantværktøj</h4><div class="h18-vd-table-pen"><label>Tykkelse px<input id="h18-vd-table-pen-width" type="number" min="0" max="10" value="' + (node.props.cellBorderWidth || 1) + '"></label><label>Farve<input id="h18-vd-table-pen-color" type="color" value="' + escapeAttr(node.props.cellBorderColor || '#dcdcde') + '"></label><label>Stil<select id="h18-vd-table-pen-style"><option value="solid">Solid</option><option value="dashed">Stiplet</option><option value="dotted">Prikket</option></select></label></div><div class="h18-vd-table-border-actions"><button type="button" class="button" data-table-border-action="outer">Yderramme</button><button type="button" class="button" data-table-border-action="inner">Indvendige</button><button type="button" class="button" data-table-border-action="all">Alle</button><button type="button" class="button" data-table-border-action="horizontal">Vandret</button><button type="button" class="button" data-table-border-action="vertical">Lodret</button><button type="button" class="button" data-table-border-action="top">Top</button><button type="button" class="button" data-table-border-action="right">Højre</button><button type="button" class="button" data-table-border-action="bottom">Bund</button><button type="button" class="button" data-table-border-action="left">Venstre</button><button type="button" class="button" data-table-border-action="none">Ingen</button></div></div>';
            } else { html += '<div class="h18-vd-table-selection-note">Klik en eller flere celler i tabel-previewet for at tegne kanter på det valgte område.</div>'; }
            html += '</div>';
        } else if (node.type === 'vehiclelist') {
            html += '<div class="h18-vd-menu-group"><h3>Køretøjsliste</h3><p class="description">Data kommer fra Manager → Køretøjer. Listen viser kun publicerede records.</p>';
            html += '<label>Detaljeside<select data-field="vehicleDetailPageId"><option value="0">Ingen link / vælg senere</option>' + (Array.isArray(CFG.pages) ? CFG.pages.map(function (page) { const id=parseInt(page.id||0,10)||0; return '<option value="'+id+'"'+(parseInt(node.props.detailPageId||0,10)===id?' selected':'')+'>'+escapeHtml(String(page.title||('Side '+id)))+'</option>'; }).join('') : '') + '</select></label>';
            html += '<div class="h18-clean-field-grid"><label>Kolonner<input data-field="vehicleColumns" type="number" min="1" max="4" value="'+(node.props.columns||3)+'"></label><label>Max. records<input data-field="vehicleLimit" type="number" min="1" max="100" value="'+(node.props.limit||50)+'"></label><label>Sortér efter<select data-field="vehicleOrderBy"><option value="sortOrder"'+(node.props.orderBy==='sortOrder'?' selected':'')+'>Sortering</option><option value="title"'+(node.props.orderBy==='title'?' selected':'')+'>Titel</option><option value="updatedAt"'+(node.props.orderBy==='updatedAt'?' selected':'')+'>Senest ændret</option></select></label><label>Retning<select data-field="vehicleOrder"><option value="ASC"'+(node.props.order!=='DESC'?' selected':'')+'>Stigende</option><option value="DESC"'+(node.props.order==='DESC'?' selected':'')+'>Faldende</option></select></label><label>Kortafstand px<input data-field="vehicleCardGap" type="number" min="0" max="80" value="'+(node.props.cardGap||18)+'"></label><label>Kortpadding px<input data-field="vehicleCardPadding" type="number" min="0" max="60" value="'+(node.props.cardPadding||12)+'"></label><label>Billedhøjde px<input data-field="vehicleImageHeight" type="number" min="60" max="600" value="'+(node.props.imageHeight||180)+'"></label><label>Hjørner px<input data-field="vehicleCardRadius" type="number" min="0" max="60" value="'+(node.props.cardRadius||4)+'"></label></div>';
            html += '<label class="h18-clean-checkbox"><input data-field="vehicleShowImage" type="checkbox"'+(node.props.showImage!==false?' checked':'')+'> Vis billede</label><label class="h18-clean-checkbox"><input data-field="vehicleShowCategory" type="checkbox"'+(node.props.showCategory!==false?' checked':'')+'> Vis kategori</label><label class="h18-clean-checkbox"><input data-field="vehicleShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="vehicleLinkCards" type="checkbox"'+(node.props.linkCards!==false?' checked':'')+'> Link kort til detaljeside med ?h18_vehicle=record-id</label>';
            html += '<div class="h18-clean-field-grid"><label>Kortbaggrund<input data-field="vehicleCardBackground" type="color" value="'+escapeAttr(node.props.cardBackground||'#ffffff')+'"></label><label>Tekst<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="vehicleAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label></div></div>';
            if (CFG.vehicleAdminUrl) { html += '<p><a class="button" href="'+escapeAttr(String(CFG.vehicleAdminUrl))+'">Administrér køretøjer</a></p>'; }
        } else if (node.type === 'vehicledetail') {
            html += '<div class="h18-vd-menu-group"><h3>Køretøjsdetalje</h3><label>Køretøj<select data-field="vehicleRecordId"><option value="">Fra URL · ?h18_vehicle=record-id</option>'+vehicleRecords().map(function (record) { return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Køretøj'))+' · '+escapeHtml(String(record.status||''))+'</option>'; }).join('')+'</select></label><p class="description">Lad feltet stå på “Fra URL”, når samme detaljeside skal bruges af alle kort i en Køretøjsliste.</p>';
            html += '<label class="h18-clean-checkbox"><input data-field="vehicleShowGallery" type="checkbox"'+(node.props.showGallery!==false?' checked':'')+'> Vis galleri</label><label class="h18-clean-checkbox"><input data-field="vehicleShowCategory" type="checkbox"'+(node.props.showCategory!==false?' checked':'')+'> Vis kategori</label><label class="h18-clean-checkbox"><input data-field="vehicleShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="vehicleShowDescription" type="checkbox"'+(node.props.showDescription!==false?' checked':'')+'> Vis beskrivelse</label><label class="h18-clean-checkbox"><input data-field="vehicleShowAttributes" type="checkbox"'+(node.props.showAttributes!==false?' checked':'')+'> Vis tekniske data</label>';
            html += '<div class="h18-clean-field-grid"><label>Billedhøjde px<input data-field="vehicleImageHeight" type="number" min="80" max="900" value="'+(node.props.imageHeight||360)+'"></label><label>Labelbredde %<input data-field="vehicleLabelWidth" type="number" min="20" max="60" value="'+(node.props.labelWidth||34)+'"></label><label>Padding px<input data-field="padding" type="number" min="0" max="80" value="'+(node.props.padding||16)+'"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="60" value="'+(node.props.radius||4)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label><label>Tekst<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="vehicleAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label></div></div>';
            if (CFG.vehicleAdminUrl) { html += '<p><a class="button" href="'+escapeAttr(String(CFG.vehicleAdminUrl))+'">Administrér køretøjer</a></p>'; }
        } else if (node.type === 'eventlist') {
            html += '<div class="h18-vd-menu-group"><h3>Eventliste</h3><p class="description">Data kommer fra Manager → Events. Frontend viser kun publicerede records.</p><label>Detaljeside<select data-field="eventDetailPageId"><option value="0">Ingen link / vælg senere</option>'+(Array.isArray(CFG.pages)?CFG.pages.map(function(page){const id=parseInt(page.id||0,10)||0;return '<option value="'+id+'"'+(parseInt(node.props.detailPageId||0,10)===id?' selected':'')+'>'+escapeHtml(String(page.title||('Side '+id)))+'</option>';}).join(''):'')+'</select></label>';
            html += '<div class="h18-clean-field-grid"><label>Visning<select data-field="eventDateFilter"><option value="upcoming"'+(node.props.dateFilter==='upcoming'?' selected':'')+'>Kommende</option><option value="past"'+(node.props.dateFilter==='past'?' selected':'')+'>Afholdte</option><option value="all"'+(node.props.dateFilter==='all'?' selected':'')+'>Alle publicerede</option></select></label><label>Kolonner<input data-field="eventColumns" type="number" min="1" max="4" value="'+(node.props.columns||3)+'"></label><label>Max. records<input data-field="eventLimit" type="number" min="1" max="100" value="'+(node.props.limit||50)+'"></label><label>Sortér efter<select data-field="eventOrderBy"><option value="start"'+(node.props.orderBy==='start'?' selected':'')+'>Startdato</option><option value="title"'+(node.props.orderBy==='title'?' selected':'')+'>Titel</option><option value="updatedAt"'+(node.props.orderBy==='updatedAt'?' selected':'')+'>Senest ændret</option></select></label><label>Retning<select data-field="eventOrder"><option value="ASC"'+(node.props.order!=='DESC'?' selected':'')+'>Stigende</option><option value="DESC"'+(node.props.order==='DESC'?' selected':'')+'>Faldende</option></select></label><label>Kortafstand px<input data-field="eventCardGap" type="number" min="0" max="80" value="'+(node.props.cardGap||18)+'"></label><label>Kortpadding px<input data-field="eventCardPadding" type="number" min="0" max="60" value="'+(node.props.cardPadding||12)+'"></label><label>Billedhøjde px<input data-field="eventImageHeight" type="number" min="60" max="600" value="'+(node.props.imageHeight||180)+'"></label><label>Hjørner px<input data-field="eventCardRadius" type="number" min="0" max="60" value="'+(node.props.cardRadius||4)+'"></label></div><label class="h18-clean-checkbox"><input data-field="eventShowImage" type="checkbox"'+(node.props.showImage!==false?' checked':'')+'> Vis billede</label><label class="h18-clean-checkbox"><input data-field="eventShowDate" type="checkbox"'+(node.props.showDate!==false?' checked':'')+'> Vis dato/tid</label><label class="h18-clean-checkbox"><input data-field="eventShowLocation" type="checkbox"'+(node.props.showLocation!==false?' checked':'')+'> Vis sted</label><label class="h18-clean-checkbox"><input data-field="eventShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="eventLinkCards" type="checkbox"'+(node.props.linkCards!==false?' checked':'')+'> Link kort til detaljeside med ?h18_event=record-id</label><div class="h18-clean-field-grid"><label>Kortbaggrund<input data-field="eventCardBackground" type="color" value="'+escapeAttr(node.props.cardBackground||'#ffffff')+'"></label><label>Tekst<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="eventAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label></div></div>'; if(CFG.eventAdminUrl){html+='<p><a class="button" href="'+escapeAttr(String(CFG.eventAdminUrl))+'">Administrér events</a></p>';}
        } else if (node.type === 'eventdetail') {
            html += '<div class="h18-vd-menu-group"><h3>Eventdetalje</h3><label>Event<select data-field="eventRecordId"><option value="">Fra URL · ?h18_event=record-id</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+' · '+escapeHtml(String(record.status||''))+'</option>';}).join('')+'</select></label><p class="description">Lad feltet stå på “Fra URL”, når samme detaljeside bruges af alle kort.</p><label class="h18-clean-checkbox"><input data-field="eventShowImage" type="checkbox"'+(node.props.showImage!==false?' checked':'')+'> Vis billede</label><label class="h18-clean-checkbox"><input data-field="eventShowDate" type="checkbox"'+(node.props.showDate!==false?' checked':'')+'> Vis dato/tid</label><label class="h18-clean-checkbox"><input data-field="eventShowLocation" type="checkbox"'+(node.props.showLocation!==false?' checked':'')+'> Vis sted</label><label class="h18-clean-checkbox"><input data-field="eventShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="eventShowDescription" type="checkbox"'+(node.props.showDescription!==false?' checked':'')+'> Vis beskrivelse</label><div class="h18-clean-field-grid"><label>Billedhøjde px<input data-field="eventImageHeight" type="number" min="80" max="900" value="'+(node.props.imageHeight||360)+'"></label><label>Padding px<input data-field="padding" type="number" min="0" max="80" value="'+(node.props.padding||16)+'"></label><label>Hjørner px<input data-field="radius" type="number" min="0" max="60" value="'+(node.props.radius||4)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label><label>Tekst<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="eventAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label></div></div>'; if(CFG.eventAdminUrl){html+='<p><a class="button" href="'+escapeAttr(String(CFG.eventAdminUrl))+'">Administrér events</a></p>';}

        } else if (node.type === 'eventvalue') {
            html += '<div class="h18-vd-menu-group"><h3>Eventværdi</h3><label>Værdi<select data-field="eventValueKey"><option value="title"'+(node.props.valueKey==='title'?' selected':'')+'>Titel</option><option value="date"'+(node.props.valueKey==='date'?' selected':'')+'>Dato / tid</option><option value="location"'+(node.props.valueKey==='location'?' selected':'')+'>Sted</option><option value="summary"'+(node.props.valueKey==='summary'?' selected':'')+'>Kort beskrivelse</option><option value="description"'+(node.props.valueKey==='description'?' selected':'')+'>Beskrivelse</option></select></label><label>Preview-event<select data-field="eventRecordId"><option value="">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><label>HTML-element<select data-field="eventValueTag">'+['h1','h2','h3','h4','h5','h6','p','div'].map(function(tag){return '<option value="'+tag+'"'+(String(node.props.tag||'')===tag?' selected':'')+'>'+tag.toUpperCase()+'</option>';}).join('')+'</select></label><label>Justering<select data-field="align"><option value="left"'+(node.props.align==='left'?' selected':'')+'>Venstre</option><option value="center"'+(node.props.align==='center'?' selected':'')+'>Midt</option><option value="right"'+(node.props.align==='right'?' selected':'')+'>Højre</option></select></label><div class="h18-clean-field-grid"><label>Skrifttype<select data-field="fontFamily">'+fontOptions(node.props.fontFamily||'system',false)+'</select></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="160" value="'+String(node.props.fontSize||16)+'"></label><label>Tykkelse<input data-field="fontWeight" type="number" min="100" max="900" step="100" value="'+String(node.props.fontWeight||400)+'"></label><label>Linjeafstand<input data-field="lineHeight" type="number" min="0.8" max="3" step="0.1" value="'+String(node.props.lineHeight||1.5)+'"></label><label>Tekstfarve<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Padding<input data-field="padding" type="number" min="0" max="120" value="'+String(node.props.padding||0)+'"></label><label>Hjørner<input data-field="radius" type="number" min="0" max="100" value="'+String(node.props.radius||0)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label></div><label class="h18-clean-checkbox"><input data-field="backgroundTransparent" type="checkbox"'+(node.props.backgroundTransparent!==false?' checked':'')+'> Gennemsigtig baggrund</label><p class="description">Værdien kommer automatisk fra eventet. Flyt og style elementet som alle andre Designer-elementer.</p></div>';
        } else if (node.type === 'eventimage') {
            html += '<div class="h18-vd-menu-group"><h3>Eventbillede</h3><label>Preview-event<select data-field="eventRecordId"><option value="">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><div class="h18-clean-field-grid"><label>Højde px<input data-field="eventDynamicImageHeight" type="number" min="80" max="1000" value="'+String(node.props.imageHeight||360)+'"></label><label>Tilpasning<select data-field="eventDynamicImageFit"><option value="cover"'+(node.props.fit!=='contain'?' selected':'')+'>Fyld / beskær</option><option value="contain"'+(node.props.fit==='contain'?' selected':'')+'>Vis hele billedet</option></select></label><label>Fokus X %<input data-field="eventDynamicImageFocalX" type="number" min="0" max="100" value="'+String(node.props.focalX||50)+'"></label><label>Fokus Y %<input data-field="eventDynamicImageFocalY" type="number" min="0" max="100" value="'+String(node.props.focalY||50)+'"></label><label>Hjørner<input data-field="radius" type="number" min="0" max="100" value="'+String(node.props.radius||4)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label></div><p class="description">Viser eventets primære billede. Elementet kan flyttes eller slettes frit.</p></div>';

        } else if (node.type === 'eventfacts') {
            html += '<div class="h18-vd-menu-group"><h3>Eventfaktabånd</h3><label>Preview-event<select data-field="eventRecordId"><option value="">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><div class="h18-clean-field-grid"><label class="h18-clean-checkbox"><input data-field="eventFactsShowDate" type="checkbox"'+(node.props.showDate!==false?' checked':'')+'> Dato</label><label class="h18-clean-checkbox"><input data-field="eventFactsShowTime" type="checkbox"'+(node.props.showTime!==false?' checked':'')+'> Tid</label><label class="h18-clean-checkbox"><input data-field="eventFactsShowLocation" type="checkbox"'+(node.props.showLocation!==false?' checked':'')+'> Sted</label><label class="h18-clean-checkbox"><input data-field="eventFactsShowAddress" type="checkbox"'+(node.props.showAddress!==false?' checked':'')+'> Adresse</label><label class="h18-clean-checkbox"><input data-field="eventFactsShowContact" type="checkbox"'+(node.props.showContact!==false?' checked':'')+'> Kontakt</label></div><h4>Layout</h4><div class="h18-clean-field-grid"><label>Afstand<input data-field="eventFactsGap" type="number" min="0" max="80" value="'+String(node.props.gap||12)+'"></label><label>Min. kortbredde<input data-field="eventFactsMinCardWidth" type="number" min="100" max="360" value="'+String(node.props.minCardWidth||150)+'"></label><label>Padding X<input data-field="eventFactsPaddingX" type="number" min="0" max="80" value="'+String(node.props.paddingX||16)+'"></label><label>Padding Y<input data-field="eventFactsPaddingY" type="number" min="0" max="80" value="'+String(node.props.paddingY||16)+'"></label><label>Hjørner<input data-field="eventFactsRadius" type="number" min="0" max="60" value="'+String(node.props.radius||0)+'"></label></div><h4>Farver</h4><div class="h18-clean-field-grid"><label>Kortbaggrund<input data-field="eventFactsCardBackground" type="color" value="'+escapeAttr(node.props.cardBackground||'#f4f1e8')+'"></label><label>Accent<input data-field="eventFactsAccentColor" type="color" value="'+escapeAttr(node.props.accentColor||'#c3ae83')+'"></label><label>Label<input data-field="eventFactsLabelColor" type="color" value="'+escapeAttr(node.props.labelColor||'#30382a')+'"></label><label>Værdi<input data-field="eventFactsValueColor" type="color" value="'+escapeAttr(node.props.valueColor||'#30382a')+'"></label></div><h4>Typografi</h4><div class="h18-clean-field-grid"><label>Label skrifttype<select data-field="eventFactsLabelFontFamily">'+fontOptions(node.props.labelFontFamily||'system',false)+'</select></label><label>Label størrelse<input data-field="eventFactsLabelFontSize" type="number" min="8" max="80" value="'+String(node.props.labelFontSize||16)+'"></label><label>Label tykkelse<input data-field="eventFactsLabelFontWeight" type="number" min="100" max="900" step="100" value="'+String(node.props.labelFontWeight||700)+'"></label><label>Værdi skrifttype<select data-field="eventFactsValueFontFamily">'+fontOptions(node.props.valueFontFamily||'system',false)+'</select></label><label>Værdi størrelse<input data-field="eventFactsValueFontSize" type="number" min="8" max="80" value="'+String(node.props.valueFontSize||16)+'"></label><label>Værdi tykkelse<input data-field="eventFactsValueFontWeight" type="number" min="100" max="900" step="100" value="'+String(node.props.valueFontWeight||400)+'"></label><label>Linjeafstand<input data-field="eventFactsLineHeight" type="number" min="0.8" max="3" step="0.05" value="'+String(node.props.lineHeight||1.35)+'"></label></div><p class="description">Dato og tid kommer fra Start/Slut. Sted, Adresse og Kontakt redigeres på eventet.</p></div>';

        } else if (node.type === 'eventfield') {
            const defs=Array.isArray(CFG.eventFieldDefinitions)?CFG.eventFieldDefinitions:[]; html += '<div class="h18-vd-menu-group"><h3>Eventfelt</h3><label>Felt<select data-field="eventFieldKey">'+defs.map(function(row){return '<option value="'+escapeAttr(String(row.id||''))+'"'+(String(node.props.fieldKey||'')===String(row.id||'')?' selected':'')+'>'+escapeHtml(String(row.label||row.id||'Felt'))+'</option>';}).join('')+'</select></label><label>Preview-event<select data-field="eventRecordId"><option value="">Fra URL / første publicerede</option>'+eventRecords().map(function(record){return '<option value="'+escapeAttr(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Event'))+'</option>';}).join('')+'</select></label><label class="h18-clean-checkbox"><input data-field="eventFieldShowHeading" type="checkbox"'+(node.props.showHeading!==false?' checked':'')+'> Vis feltoverskrift</label><label class="h18-clean-checkbox"><input data-field="eventFieldShowWhenEmpty" type="checkbox"'+(node.props.showWhenEmpty===true?' checked':'')+'> Vis overskrift selv når feltet er tomt</label><h4>Overskrift</h4><div class="h18-clean-field-grid"><label>Skrifttype<select data-field="headingFontFamily">'+fontOptions(node.props.headingFontFamily||'body',true)+'</select></label><label>Størrelse px<input data-field="headingFontSize" type="number" min="8" max="160" value="'+String(node.props.headingFontSize||40)+'"></label><label>Tykkelse<input data-field="headingFontWeight" type="number" min="100" max="900" step="100" value="'+String(node.props.headingFontWeight||400)+'"></label><label>Linjeafstand<input data-field="headingLineHeight" type="number" min="0.8" max="3" step="0.05" value="'+String(node.props.headingLineHeight||1.15)+'"></label><label>Afstand efter<input data-field="eventFieldHeadingGap" type="number" min="0" max="80" value="'+String(node.props.headingGap||12)+'"></label><label>Farve<input data-field="headingColor" type="color" value="'+escapeAttr(node.props.headingColor||'#30382a')+'"></label></div><h4>Indhold</h4><div class="h18-clean-field-grid"><label>Skrifttype<select data-field="fontFamily">'+fontOptions(node.props.fontFamily||'system',false)+'</select></label><label>Størrelse px<input data-field="fontSize" type="number" min="8" max="120" value="'+String(node.props.fontSize||16)+'"></label><label>Tykkelse<input data-field="fontWeight" type="number" min="100" max="900" step="100" value="'+String(node.props.fontWeight||400)+'"></label><label>Linjeafstand<input data-field="lineHeight" type="number" min="0.8" max="3" step="0.05" value="'+String(node.props.lineHeight||1.5)+'"></label><label>Tekstfarve<input data-field="textColor" type="color" value="'+escapeAttr(node.props.textColor||'#30382a')+'"></label><label>Padding<input data-field="padding" type="number" min="0" max="80" value="'+String(node.props.padding||0)+'"></label><label>Hjørner<input data-field="radius" type="number" min="0" max="60" value="'+String(node.props.radius||0)+'"></label><label>Baggrund<input data-field="background" type="color" value="'+escapeAttr(node.props.background||'#ffffff')+'"></label></div></div>';
        } else if (node.type === 'gallerylist') {
            html += '<div class="h18-vd-menu-group"><h3>Gallerioversigt</h3><p class="description">Data kommer fra Manager → Billedgalleri. Kun publicerede album vises på frontend.</p><label>Album-detaljeside<select data-field="galleryDetailPageId"><option value="0">Ingen link / vælg senere</option>'+(Array.isArray(CFG.pages)?CFG.pages.map(function(page){const id=parseInt(page.id||0,10)||0;return '<option value="'+id+'"'+(parseInt(node.props.detailPageId||0,10)===id?' selected':'')+'>'+escapeHtml(String(page.title||('Side '+id)))+'</option>';}).join(''):'')+'</select></label><div class="h18-clean-field-grid"><label>Kolonner<input data-field="galleryColumns" type="number" min="1" max="4" value="'+String(node.props.columns||3)+'"></label><label>Maks. album<input data-field="galleryLimit" type="number" min="1" max="100" value="'+String(node.props.limit||50)+'"></label><label>Sortér<select data-field="galleryOrderBy"><option value="sortOrder"'+(node.props.orderBy==='sortOrder'?' selected':'')+'>Sortering</option><option value="title"'+(node.props.orderBy==='title'?' selected':'')+'>Titel</option><option value="updatedAt"'+(node.props.orderBy==='updatedAt'?' selected':'')+'>Senest ændret</option></select></label><label>Retning<select data-field="galleryOrder"><option value="ASC"'+(node.props.order==='ASC'?' selected':'')+'>Stigende</option><option value="DESC"'+(node.props.order==='DESC'?' selected':'')+'>Faldende</option></select></label><label>Afstand<input data-field="galleryCardGap" type="number" min="0" max="80" value="'+String(node.props.cardGap||18)+'"></label><label>Padding<input data-field="galleryCardPadding" type="number" min="0" max="60" value="'+String(node.props.cardPadding||12)+'"></label><label>Billedhøjde<input data-field="galleryImageHeight" type="number" min="80" max="600" value="'+String(node.props.imageHeight||220)+'"></label><label>Hjørner<input data-field="galleryCardRadius" type="number" min="0" max="60" value="'+String(node.props.cardRadius||4)+'"></label></div><div class="h18-clean-field-grid"><label>Kortbaggrund<input data-field="galleryCardBackground" type="color" value="'+escapeHtml(node.props.cardBackground||'#ffffff')+'"></label><label>Tekst<input data-field="galleryTextColor" type="color" value="'+escapeHtml(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="galleryAccentColor" type="color" value="'+escapeHtml(node.props.accentColor||'#c3ae83')+'"></label></div><label class="h18-clean-checkbox"><input data-field="galleryShowImage" type="checkbox"'+(node.props.showImage!==false?' checked':'')+'> Vis cover</label><label class="h18-clean-checkbox"><input data-field="galleryShowCount" type="checkbox"'+(node.props.showCount!==false?' checked':'')+'> Vis antal billeder</label><label class="h18-clean-checkbox"><input data-field="galleryShowSummary" type="checkbox"'+(node.props.showSummary!==false?' checked':'')+'> Vis kort beskrivelse</label><label class="h18-clean-checkbox"><input data-field="galleryLinkCards" type="checkbox"'+(node.props.linkCards!==false?' checked':'')+'> Link kort til detaljeside</label><p><a class="button" href="'+escapeHtml(String(CFG.galleryAdminUrl||'#'))+'">Åbn Billedgalleri</a></p></div>';
        } else if (node.type === 'gallerydetail') {
            const records=galleryRecords(); html += '<div class="h18-vd-menu-group"><h3>Albumvisning</h3><label>Preview-album<select data-field="galleryRecordId"><option value="">Fra URL / første publicerede</option>'+records.map(function(record){return '<option value="'+escapeHtml(String(record.id||''))+'"'+(String(node.props.recordId||'')===String(record.id||'')?' selected':'')+'>'+escapeHtml(String(record.title||record.id||'Album'))+'</option>';}).join('')+'</select></label><p class="description">Frontend kan vælge album via <code>?h18_gallery=record-id</code>.</p><div class="h18-clean-field-grid"><label>Kolonner<input data-field="galleryColumns" type="number" min="1" max="6" value="'+String(node.props.columns||4)+'"></label><label>Afstand<input data-field="galleryGap" type="number" min="0" max="80" value="'+String(node.props.gap||12)+'"></label><label>Billedhøjde<input data-field="galleryImageHeight" type="number" min="80" max="700" value="'+String(node.props.imageHeight||220)+'"></label><label>Padding<input data-field="galleryPadding" type="number" min="0" max="80" value="'+String(node.props.padding||16)+'"></label></div><div class="h18-clean-field-grid"><label>Baggrund<input data-field="galleryBackground" type="color" value="'+escapeHtml(node.props.background||'#ffffff')+'"></label><label>Tekst<input data-field="galleryTextColor" type="color" value="'+escapeHtml(node.props.textColor||'#30382a')+'"></label><label>Accent<input data-field="galleryAccentColor" type="color" value="'+escapeHtml(node.props.accentColor||'#c3ae83')+'"></label></div><label class="h18-clean-checkbox"><input data-field="galleryShowDescription" type="checkbox"'+(node.props.showDescription!==false?' checked':'')+'> Vis albumbeskrivelse</label><p><a class="button" href="'+escapeHtml(String(CFG.galleryAdminUrl||'#'))+'">Åbn Billedgalleri</a></p></div>';

        } else if (node.type === 'contactform' || node.type === 'membershipform') {
            const membership = node.type === 'membershipform';
            html += '<div class="h18-vd-menu-group"><h3>Formular</h3><label>Overskrift<input data-field="formHeading" type="text" value="' + escapeAttr(node.props.heading || (membership ? 'Bliv medlem' : 'Kontakt os')) + '"></label><label>Intro<textarea data-field="formIntro" rows="4">' + escapeHtml(node.props.intro || '') + '</textarea></label><label>Knaptekst<input data-field="formButtonText" type="text" value="' + escapeAttr(node.props.buttonText || (membership ? 'Send indmeldelse' : 'Send besked')) + '"></label><label>Modtager-e-mail <span class="description">(tom = WordPress admin-e-mail)</span><input data-field="formRecipient" type="email" value="' + escapeAttr(node.props.recipient || '') + '"></label><label class="h18-clean-checkbox"><input data-field="formShowPhone" type="checkbox"' + (node.props.showPhone !== false ? ' checked' : '') + '> Vis telefonfelt</label><label class="h18-clean-checkbox"><input data-field="formRequireConsent" type="checkbox"' + (node.props.requireConsent !== false ? ' checked' : '') + '> Kræv samtykke</label></div>';
            html += '<div class="h18-vd-menu-group"><h3>Design</h3><div class="h18-clean-field-grid"><label>Baggrund<input data-field="formBackground" type="color" value="' + escapeAttr(node.props.background || '#f4f1e8') + '"></label><label>Feltbaggrund<input data-field="formFieldBackground" type="color" value="' + escapeAttr(node.props.fieldBackground || '#ffffff') + '"></label><label>Tekst<input data-field="formTextColor" type="color" value="' + escapeAttr(node.props.textColor || '#30382a') + '"></label><label>Knap/accent<input data-field="formAccentColor" type="color" value="' + escapeAttr(node.props.accentColor || '#30382a') + '"></label><label>Padding<input data-field="formPadding" type="number" min="0" max="80" value="' + (node.props.padding || 24) + '"></label><label>Hjørner<input data-field="formRadius" type="number" min="0" max="60" value="' + (node.props.radius || 6) + '"></label></div></div>';
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
            if (node.type === 'section') { html += '<label>Placering på modulside<select data-field="moduleSlot"><option value="before"'+(node.props.moduleSlot==='before'?' selected':'')+'>Før modulindhold</option><option value="between"'+(node.props.moduleSlot==='between'?' selected':'')+'>Mellem modulsektioner</option><option value="after"'+(node.props.moduleSlot==='after'?' selected':'')+'>Efter modulindhold</option></select></label><label>Minimumshøjde · 8px<input data-field="gh" type="number" min="0" value="'+String(node.props.minHeightRows||node.geometry.desktop.h||0)+'"></label>'; }
            html += '<label>Baggrund<input data-field="background" type="color" value="' + escapeAttr(node.props.background || '#ffffff') + '"></label>';
            html += '<div class="h18-clean-field-grid"><label>Hjørner px<input data-field="radius" type="number" min="0" max="100" value="' + (node.props.radius || 0) + '"></label><label>Padding px<input data-field="padding" type="number" min="0" max="120" value="' + (node.props.padding || 0) + '"></label></div>';
        }
        if (node.type !== 'spacer') { html += '<div class="h18-clean-v0111-layout-style"><strong>Ramme og afstand</strong><div class="h18-clean-field-grid">';
        html += '<label>Ramme px<input data-field="borderWidth" type="number" min="0" max="20" value="' + (node.props.borderWidth || 0) + '"></label>';
        html += '<label>Rammefarve<input data-field="borderColor" type="color" value="' + escapeAttr(node.props.borderColor || '#000000') + '"></label>';
        html += '<label>Afstand X px<input data-field="gapX" type="number" min="0" max="200" value="' + (node.props.gapX || 0) + '"></label>';
        html += '<label>Afstand Y px<input data-field="gapY" type="number" min="0" max="200" value="' + (node.props.gapY || 0) + '"></label>';
        html += '</div><p class="description">0 = ingen ramme/afstand. X er luft mod næste element til højre; Y er luft mod næste element under.</p></div>'; }
        html += '<button type="button" class="button button-link-delete" id="h18-clean-delete">Slet element' + (PARENT_TYPES.includes(node.type) ? ' + indhold' : '') + '</button>';
        host.innerHTML = html;
        // v0.1.87: Inspector is rebuilt on every render. Refresh the one canonical
        // VDM color picker synchronously when available instead of relying only on
        // MutationObserver ordering. Initial render is still covered by picker init.
        if (window.VDMColorPicker && typeof window.VDMColorPicker.refresh === 'function') {
            window.VDMColorPicker.refresh(host);
        }

        host.querySelectorAll('[data-field]').forEach(function (control) {
            control.addEventListener('change', function () {
                if (control.getAttribute('data-h18-vd-color-managed') === '1' && control.getAttribute('data-h18-vd-color-commit') !== '1') { return; }
                if (control.getAttribute('data-h18-vd-color-commit') === '1') { control.removeAttribute('data-h18-vd-color-commit'); }
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
                else if (field === 'headingLevel') { current.props.headingLevel = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'].includes(control.value) ? control.value : 'h2'; }
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
                else if (field === 'badgeText') { current.props.text = String(control.value || 'Badge'); }
                else if (field === 'linkText') { current.props.text = String(control.value || 'Læs mere →'); }
                else if (field === 'underline') { current.props.underline = !!control.checked; }
                else if (field === 'lineWidth') { current.props.lineWidth = clamp(parseInt(control.value || 1, 10) || 1, 1, 20); }
                else if (field === 'lineColor') { current.props.lineColor = normalizeColor(control.value || '#dcdcde'); }
                else if (field === 'lineStyle') { current.props.lineStyle = ['solid','dashed','dotted'].includes(control.value) ? control.value : 'solid'; }
                else if (field === 'icon') { current.props.icon = ['star','check','info','calendar','camera','people','ruler','weight','gear','link'].includes(control.value) ? control.value : 'star'; }
                else if (field === 'iconSize') { current.props.iconSize = clamp(parseInt(control.value || 32, 10) || 32, 8, 240); }
                else if (field === 'iconColor') { current.props.iconColor = normalizeColor(control.value || '#30382a'); }
                else if (field === 'dataRows') { current.props.rows = normalizePairRows(parsePairRowsText(control.value)); }
                else if (field === 'dataLayout') { current.props.layout = ['rows','stacked'].includes(control.value) ? control.value : 'rows'; }
                else if (field === 'labelWidth') { current.props.labelWidth = clamp(parseInt(control.value || 40, 10) || 40, 15, 80); }
                else if (field === 'cellPadding') { current.props.cellPadding = clamp(parseInt(control.value || 8, 10) || 8, 0, 60); }
                else if (field === 'showDividers') { current.props.showDividers = !!control.checked; }
                else if (field === 'zebra') { current.props.zebra = !!control.checked; }
                else if (field === 'zebraBackground') { current.props.zebraBackground = normalizeColor(control.value || '#f6f7f7'); }
                else if (field === 'labelColor') { current.props.labelColor = normalizeColor(control.value || '#30382a'); }
                else if (field === 'valueColor') { current.props.valueColor = normalizeColor(control.value || '#30382a'); }
                else if (field === 'labelWeight') { current.props.labelWeight = clamp(parseInt(control.value || 600, 10) || 600, 100, 900); }
                else if (field === 'valueWeight') { current.props.valueWeight = clamp(parseInt(control.value || 400, 10) || 400, 100, 900); }
                else if (field === 'tableHeaders') { current.props.headers = parseHeadersText(control.value); current.props.rows = normalizeMatrixRows(current.props.rows, current.props.headers.length); }
                else if (field === 'tableRows') { current.props.rows = parseMatrixRowsText(control.value, normalizeHeaders(current.props.headers).length); }
                else if (field === 'headerBackground') { current.props.headerBackground = normalizeColor(control.value || '#30382a'); }
                else if (field === 'headerTextColor') { current.props.headerTextColor = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'cellBackground') { current.props.cellBackground = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'cellTextColor') { current.props.cellTextColor = normalizeColor(control.value || '#30382a'); }
                else if (field === 'cellBorderColor') { current.props.cellBorderColor = normalizeColor(control.value || '#dcdcde'); }
                else if (field === 'cellBorderWidth') { current.props.cellBorderWidth = clamp(parseInt(control.value || 0, 10) || 0, 0, 10); }
                else if (field === 'cellBorderStyle') { current.props.cellBorderStyle = ['solid','dashed','dotted'].includes(control.value) ? control.value : 'solid'; }
                else if (field === 'tableBorderMode') { current.props.borderMode = ['all','outer','inner','none'].includes(control.value) ? control.value : 'all'; }
                else if (field === 'headerWeight') { current.props.headerWeight = clamp(parseInt(control.value || 700, 10) || 700, 100, 900); }
                else if (field === 'mobileTableMode') { current.props.mobileMode = ['scroll','cards'].includes(control.value) ? control.value : 'scroll'; }
                else if (field === 'vehicleDetailPageId') { current.props.detailPageId = parseInt(control.value || 0,10) || 0; }
                else if (field === 'vehicleColumns') { current.props.columns = clamp(parseInt(control.value || 3,10) || 3,1,4); }
                else if (field === 'vehicleLimit') { current.props.limit = clamp(parseInt(control.value || 50,10) || 50,1,100); if (current.props.binding && current.props.binding.query) { current.props.binding.query.limit = current.props.limit; } }
                else if (field === 'vehicleOrderBy') { current.props.orderBy = ['sortOrder','title','updatedAt'].includes(control.value) ? control.value : 'sortOrder'; if (current.props.binding && current.props.binding.query) { current.props.binding.query.orderBy = current.props.orderBy; } }
                else if (field === 'vehicleOrder') { current.props.order = control.value === 'DESC' ? 'DESC' : 'ASC'; if (current.props.binding && current.props.binding.query) { current.props.binding.query.order = current.props.order; } }
                else if (field === 'vehicleCardGap') { current.props.cardGap = clamp(parseInt(control.value || 18,10) || 18,0,80); }
                else if (field === 'vehicleCardPadding') { current.props.cardPadding = clamp(parseInt(control.value || 12,10) || 12,0,60); }
                else if (field === 'vehicleImageHeight') { current.props.imageHeight = clamp(parseInt(control.value || 180,10) || 180,current.type === 'vehicledetail' ? 80 : 60,current.type === 'vehicledetail' ? 900 : 600); }
                else if (field === 'vehicleCardRadius') { current.props.cardRadius = clamp(parseInt(control.value || 4,10) || 4,0,60); }
                else if (field === 'vehicleShowImage') { current.props.showImage = !!control.checked; }
                else if (field === 'vehicleShowCategory') { current.props.showCategory = !!control.checked; }
                else if (field === 'vehicleShowSummary') { current.props.showSummary = !!control.checked; }
                else if (field === 'vehicleLinkCards') { current.props.linkCards = !!control.checked; }
                else if (field === 'vehicleCardBackground') { current.props.cardBackground = normalizeColor(control.value || '#ffffff'); }
                else if (field === 'vehicleAccentColor') { current.props.accentColor = normalizeColor(control.value || '#c3ae83'); }
                else if (field === 'vehicleRecordId') { current.props.recordId = String(control.value || ''); if (current.props.binding) { current.props.binding.recordId = current.props.recordId; } }
                else if (field === 'vehicleShowGallery') { current.props.showGallery = !!control.checked; }
                else if (field === 'vehicleShowDescription') { current.props.showDescription = !!control.checked; }
                else if (field === 'vehicleShowAttributes') { current.props.showAttributes = !!control.checked; }
                else if (field === 'vehicleLabelWidth') { current.props.labelWidth = clamp(parseInt(control.value || 34,10) || 34,20,60); }
                else if (field === 'eventDetailPageId') { current.props.detailPageId=parseInt(control.value||0,10)||0; }
                else if (field === 'eventDateFilter') { current.props.dateFilter=['all','upcoming','past'].includes(control.value)?control.value:'upcoming'; }
                else if (field === 'eventColumns') { current.props.columns=clamp(parseInt(control.value||3,10)||3,1,4); }
                else if (field === 'eventLimit') { current.props.limit=clamp(parseInt(control.value||50,10)||50,1,100); if(current.props.binding&&current.props.binding.query){current.props.binding.query.limit=current.props.limit;} }
                else if (field === 'eventOrderBy') { current.props.orderBy=['start','title','updatedAt'].includes(control.value)?control.value:'start'; if(current.props.binding&&current.props.binding.query){current.props.binding.query.orderBy=current.props.orderBy;} }
                else if (field === 'eventOrder') { current.props.order=control.value==='DESC'?'DESC':'ASC'; if(current.props.binding&&current.props.binding.query){current.props.binding.query.order=current.props.order;} }
                else if (field === 'eventCardGap') { current.props.cardGap=clamp(parseInt(control.value||18,10)||18,0,80); }
                else if (field === 'eventCardPadding') { current.props.cardPadding=clamp(parseInt(control.value||12,10)||12,0,60); }
                else if (field === 'eventImageHeight') { current.props.imageHeight=current.type==='eventdetail'?clamp(parseInt(control.value||360,10)||360,80,900):clamp(parseInt(control.value||180,10)||180,60,600); }
                else if (field === 'eventCardRadius') { current.props.cardRadius=clamp(parseInt(control.value||4,10)||4,0,60); }
                else if (field === 'eventShowImage') { current.props.showImage=!!control.checked; }
                else if (field === 'eventShowDate') { current.props.showDate=!!control.checked; }
                else if (field === 'eventShowLocation') { current.props.showLocation=!!control.checked; }
                else if (field === 'eventShowSummary') { current.props.showSummary=!!control.checked; }
                else if (field === 'eventLinkCards') { current.props.linkCards=!!control.checked; }
                else if (field === 'eventCardBackground') { current.props.cardBackground=normalizeColor(control.value||'#ffffff'); }
                else if (field === 'eventAccentColor') { current.props.accentColor=normalizeColor(control.value||'#c3ae83'); }
                else if (field === 'eventRecordId') { current.props.recordId=String(control.value||''); if(current.props.binding){current.props.binding.recordId=current.props.recordId;} }
                else if (field === 'eventShowDescription') { current.props.showDescription=!!control.checked; }
                else if (field === 'eventValueKey') { current.props.valueKey=['title','date','location','summary','description'].includes(String(control.value||''))?String(control.value):'title'; }
                else if (field === 'eventValueTag') { current.props.tag=['div','p','h1','h2','h3','h4','h5','h6'].includes(String(control.value||''))?String(control.value):'div'; }
                else if (field === 'eventDynamicImageHeight') { current.props.imageHeight=clamp(parseInt(control.value||360,10)||360,80,1000); }
                else if (field === 'eventDynamicImageFit') { current.props.fit=String(control.value||'cover')==='contain'?'contain':'cover'; }
                else if (field === 'eventDynamicImageFocalX') { current.props.focalX=clamp(parseInt(control.value||50,10)||50,0,100); }
                else if (field === 'eventDynamicImageFocalY') { current.props.focalY=clamp(parseInt(control.value||50,10)||50,0,100); }
                else if (field === 'eventFactsShowDate') { current.props.showDate=!!control.checked; }
                else if (field === 'eventFactsShowTime') { current.props.showTime=!!control.checked; }
                else if (field === 'eventFactsShowLocation') { current.props.showLocation=!!control.checked; }
                else if (field === 'eventFactsShowAddress') { current.props.showAddress=!!control.checked; }
                else if (field === 'eventFactsShowContact') { current.props.showContact=!!control.checked; }
                else if (field === 'eventFactsGap') { current.props.gap=clamp(parseInt(control.value||12,10)||12,0,80); }
                else if (field === 'eventFactsMinCardWidth') { current.props.minCardWidth=clamp(parseInt(control.value||150,10)||150,100,360); }
                else if (field === 'eventFactsPaddingX') { current.props.paddingX=clamp(parseInt(control.value||16,10)||16,0,80); }
                else if (field === 'eventFactsPaddingY') { current.props.paddingY=clamp(parseInt(control.value||16,10)||16,0,80); }
                else if (field === 'eventFactsRadius') { current.props.radius=clamp(parseInt(control.value||0,10)||0,0,60); }
                else if (field === 'eventFactsCardBackground') { current.props.cardBackground=normalizeColor(control.value||'#f4f1e8'); }
                else if (field === 'eventFactsAccentColor') { current.props.accentColor=normalizeColor(control.value||'#c3ae83'); }
                else if (field === 'eventFactsLabelColor') { current.props.labelColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'eventFactsValueColor') { current.props.valueColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'eventFactsLabelFontFamily') { current.props.labelFontFamily=normalizeFontToken(control.value,false); }
                else if (field === 'eventFactsLabelFontSize') { current.props.labelFontSize=clamp(parseInt(control.value||16,10)||16,8,80); }
                else if (field === 'eventFactsLabelFontWeight') { current.props.labelFontWeight=clamp(parseInt(control.value||700,10)||700,100,900); }
                else if (field === 'eventFactsValueFontFamily') { current.props.valueFontFamily=normalizeFontToken(control.value,false); }
                else if (field === 'eventFactsValueFontSize') { current.props.valueFontSize=clamp(parseInt(control.value||16,10)||16,8,80); }
                else if (field === 'eventFactsValueFontWeight') { current.props.valueFontWeight=clamp(parseInt(control.value||400,10)||400,100,900); }
                else if (field === 'eventFactsLineHeight') { current.props.lineHeight=Math.max(0.8,Math.min(3,parseFloat(control.value||1.35)||1.35)); }
                else if (field === 'eventFieldKey') { current.props.fieldKey=String(control.value||'about'); }
                else if (field === 'eventFieldShowHeading') { current.props.showHeading=!!control.checked; }
                else if (field === 'eventFieldShowWhenEmpty') { current.props.showWhenEmpty=!!control.checked; }
                else if (field === 'eventFieldHeadingGap') { current.props.headingGap=clamp(parseInt(control.value||12,10)||12,0,80); }
                else if (field === 'moduleSlot') { current.props.moduleSlot=['before','between','after'].includes(String(control.value||''))?String(control.value):'before'; }
                else if (field === 'galleryDetailPageId') { current.props.detailPageId=parseInt(control.value||0,10)||0; }
                else if (field === 'galleryColumns') { current.props.columns=clamp(parseInt(control.value||(current.type==='gallerydetail'?4:3),10)||(current.type==='gallerydetail'?4:3),1,current.type==='gallerydetail'?6:4); }
                else if (field === 'galleryLimit') { current.props.limit=clamp(parseInt(control.value||50,10)||50,1,100); if(current.props.binding&&current.props.binding.query){current.props.binding.query.limit=current.props.limit;} }
                else if (field === 'galleryOrderBy') { current.props.orderBy=['sortOrder','title','updatedAt'].includes(control.value)?control.value:'sortOrder'; if(current.props.binding&&current.props.binding.query){current.props.binding.query.orderBy=current.props.orderBy;} }
                else if (field === 'galleryOrder') { current.props.order=control.value==='DESC'?'DESC':'ASC'; if(current.props.binding&&current.props.binding.query){current.props.binding.query.order=current.props.order;} }
                else if (field === 'galleryCardGap') { current.props.cardGap=clamp(parseInt(control.value||18,10)||18,0,80); }
                else if (field === 'galleryCardPadding') { current.props.cardPadding=clamp(parseInt(control.value||12,10)||12,0,60); }
                else if (field === 'galleryGap') { current.props.gap=clamp(parseInt(control.value||12,10)||12,0,80); }
                else if (field === 'galleryImageHeight') { current.props.imageHeight=clamp(parseInt(control.value||(current.type==='gallerydetail'?220:220),10)||220,80,current.type==='gallerydetail'?700:600); }
                else if (field === 'galleryCardRadius') { current.props.cardRadius=clamp(parseInt(control.value||4,10)||4,0,60); }
                else if (field === 'galleryPadding') { current.props.padding=clamp(parseInt(control.value||16,10)||16,0,80); }
                else if (field === 'galleryShowImage') { current.props.showImage=!!control.checked; }
                else if (field === 'galleryShowSummary') { current.props.showSummary=!!control.checked; }
                else if (field === 'galleryShowCount') { current.props.showCount=!!control.checked; }
                else if (field === 'galleryLinkCards') { current.props.linkCards=!!control.checked; }
                else if (field === 'galleryCardBackground') { current.props.cardBackground=normalizeColor(control.value||'#ffffff'); }
                else if (field === 'galleryBackground') { current.props.background=normalizeColor(control.value||'#ffffff'); }
                else if (field === 'galleryTextColor') { current.props.textColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'galleryAccentColor') { current.props.accentColor=normalizeColor(control.value||'#c3ae83'); }
                else if (field === 'galleryRecordId') { current.props.recordId=String(control.value||''); if(current.props.binding){current.props.binding.recordId=current.props.recordId;} }
                else if (field === 'galleryShowDescription') { current.props.showDescription=!!control.checked; }
                else if (field === 'formHeading') { current.props.heading=String(control.value||''); }
                else if (field === 'formIntro') { current.props.intro=String(control.value||''); }
                else if (field === 'formButtonText') { current.props.buttonText=String(control.value||'Send'); }
                else if (field === 'formRecipient') { current.props.recipient=String(control.value||'').trim(); }
                else if (field === 'formShowPhone') { current.props.showPhone=!!control.checked; }
                else if (field === 'formRequireConsent') { current.props.requireConsent=!!control.checked; }
                else if (field === 'formBackground') { current.props.background=normalizeColor(control.value||'#f4f1e8'); }
                else if (field === 'formFieldBackground') { current.props.fieldBackground=normalizeColor(control.value||'#ffffff'); }
                else if (field === 'formTextColor') { current.props.textColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'formAccentColor') { current.props.accentColor=normalizeColor(control.value||'#30382a'); }
                else if (field === 'formPadding') { current.props.padding=clamp(parseInt(control.value||24,10)||24,0,80); }
                else if (field === 'formRadius') { current.props.radius=clamp(parseInt(control.value||6,10)||6,0,60); }
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
                else if (field === 'offsetX') { current.props.offsetX = clamp(parseInt(control.value || 0, 10) || 0, -2000, 2000); }
                else if (field === 'offsetY') { current.props.offsetY = clamp(parseInt(control.value || 0, 10) || 0, -2000, 2000); }
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
        const iconLibraryOpen = document.getElementById('h18-vd-icon-library-open');
        if (iconLibraryOpen) { iconLibraryOpen.addEventListener('click', openIconLibrary); }
        document.querySelectorAll('[data-table-border-action]').forEach(function (button) {
            button.addEventListener('click', function () {
                const current = nodeById(selectedId); if (!current || current.type !== 'table') { return; }
                const keys = tableSelectionKeys(current); if (!keys.length) { return; }
                const widthInput = document.getElementById('h18-vd-table-pen-width'), colorInput = document.getElementById('h18-vd-table-pen-color'), styleInput = document.getElementById('h18-vd-table-pen-style');
                const pen = {width:clamp(parseInt(widthInput && widthInput.value || current.props.cellBorderWidth || 1,10) || 0,0,10),color:normalizeColor(colorInput && colorInput.value || current.props.cellBorderColor || '#dcdcde'),style:['solid','dashed','dotted'].includes(String(styleInput && styleInput.value || 'solid')) ? String(styleInput && styleInput.value || 'solid') : 'solid'};
                const before = clone(state), action = String(button.getAttribute('data-table-border-action') || 'all');
                applyTableBorderAction(current,keys,action,pen); commit(before,'Tabelkanter · ' + action); render();
            });
        });
        const resetOffset = document.getElementById('h18-clean-reset-offset');
        if (resetOffset) {
            resetOffset.addEventListener('click', function () {
                const current = nodeById(selectedId);
                if (!current) { return; }
                const before = clone(state);
                current.props.offsetX = 0;
                current.props.offsetY = 0;
                commit(before, 'Nulstil finjustering på ' + typeLabel(current.type));
                render();
            });
        }
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
        updateProductivityToolbar();
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
            if (isEditableTarget(event.target)) { return; }
            const key = String(event.key || '').toLowerCase();
            if (event.ctrlKey || event.metaKey) {
                if (key === 'z' && event.shiftKey) { event.preventDefault(); finalizeNudge(); redo(); }
                else if (key === 'z') { event.preventDefault(); finalizeNudge(); undo(); }
                else if (key === 'y') { event.preventDefault(); finalizeNudge(); redo(); }
                else if (key === 'c' && selectedNodeForProductivity()) { event.preventDefault(); finalizeNudge(); copySelected(); }
                else if (key === 'v') { event.preventDefault(); finalizeNudge(); pasteClipboard(); }
                else if (key === 'd' && selectedNodeForProductivity()) { event.preventDefault(); finalizeNudge(); duplicateSelected(); }
                return;
            }
            const step = event.shiftKey ? 10 : 1;
            if (key === 'arrowleft' && nudgeSelected(-step, 0)) { event.preventDefault(); }
            else if (key === 'arrowright' && nudgeSelected(step, 0)) { event.preventDefault(); }
            else if (key === 'arrowup' && nudgeSelected(0, -step)) { event.preventDefault(); }
            else if (key === 'arrowdown' && nudgeSelected(0, step)) { event.preventDefault(); }
        });
        document.addEventListener('keyup', function (event) {
            if (['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'].includes(String(event.key || ''))) { finalizeNudge(); }
        });
        window.addEventListener('blur', finalizeNudge);
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
        ensureProductivityToolbar();
        render();
        diag('editor_boot', { version: CFG.version || '', layoutMode: 'cell-split-grid', state: structuralSummary() });
    }

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());