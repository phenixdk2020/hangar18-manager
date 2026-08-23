(function () {
    'use strict';

    if (window.__h18UltimateDesignerTraceV0876) { return; }

    const VERSION = '0.8.76';
    const STORAGE_KEY = 'h18.ultimate-designer.trace.v0876';
    const MAX_EVENTS = 2200;
    const MAX_PERSISTED = 1400;
    const HIGH_FREQ_MS = 90;
    const MUTATION_MS = 140;

    let events = [];
    let seq = 0;
    let sessionId = '';
    let startedAt = '';
    let logging = false;
    let panel = null;
    let pre = null;
    let statusNode = null;
    let countNode = null;
    let toggleButton = null;
    let persistTimer = 0;
    let highFreqTimer = 0;
    let mutationTimer = 0;
    let mutationBucket = null;
    const wrapped = [];

    function iso() { return new Date().toISOString(); }
    function clock() {
        const d = new Date();
        return d.toLocaleTimeString('da-DK', { hour12: false }) + '.' + String(d.getMilliseconds()).padStart(3, '0');
    }
    function text(value, max) {
        let result = '';
        try { result = value == null ? '' : String(value); } catch (ignore) { result = '[unprintable]'; }
        result = result.replace(/\s+/g, ' ').trim();
        const limit = max || 140;
        return result.length > limit ? result.slice(0, limit) + '…' : result;
    }
    function id() { return Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 9); }
    function sensitive(value) { return /pass(word)?|secret|token|nonce|authorization|api[-_ ]?key|cookie|bearer|credential/i.test(text(value, 120)); }
    function keyOfRow(row) {
        if (!row) { return ''; }
        const field = row.querySelector && row.querySelector('.h18-page-section-key');
        if (field && field.value) { return text(field.value, 100); }
        return text(row.getAttribute && row.getAttribute('data-key'), 100);
    }
    function valueOf(node) {
        if (!node) { return ''; }
        const identity = [node.id, node.name, node.type, node.getAttribute && node.getAttribute('data-h18-lego-path'), node.getAttribute && node.getAttribute('data-h18-lego-design-path')].join(' ');
        if (String(node.type || '').toLowerCase() === 'password' || sensitive(identity)) { return '[REDACTED]'; }
        if (node.type === 'checkbox' || node.type === 'radio') { return node.checked ? 'checked' : 'unchecked'; }
        if (node.type === 'file') { return node.files && node.files.length ? '[file:' + node.files.length + ']' : '[no-file]'; }
        if (node.tagName === 'SELECT') {
            const option = node.options && node.selectedIndex >= 0 ? node.options[node.selectedIndex] : null;
            return text((option ? option.text : '') + ' [' + String(node.value || '') + ']', 180);
        }
        if ('value' in node) { return text(node.value, 180); }
        if (node.isContentEditable) { return text(node.textContent, 180); }
        return '';
    }
    function nodeName(node) {
        if (!node || node.nodeType !== 1) { return '-'; }
        let result = node.tagName.toLowerCase();
        if (node.id) { result += '#' + node.id; }
        const classes = Array.from(node.classList || []).slice(0, 5);
        if (classes.length) { result += '.' + classes.join('.'); }
        return text(result, 190);
    }
    function pathOf(node) {
        if (!node || !node.closest) { return '-'; }
        const parts = [];
        let cursor = node;
        for (let i = 0; cursor && cursor.nodeType === 1 && i < 6; i += 1) {
            parts.unshift(nodeName(cursor));
            if (cursor.id === 'h18-page-sections-sortable' || cursor.id === 'h18-page-inspector-target') { break; }
            cursor = cursor.parentElement;
        }
        return parts.join(' > ');
    }
    function rowInfo(node) {
        const row = node && node.closest ? node.closest('.h18-page-section-row') : null;
        if (!row) { return null; }
        let parent = row.querySelector('.h18-layout-parent-key');
        if ((!parent || !parent.value) && row.classList.contains('is-selected')) {
            parent = document.querySelector('#h18-page-inspector-target .h18-layout-parent-key') || parent;
        }
        return {
            key: keyOfRow(row),
            type: text(row.getAttribute('data-section-type') || (row.querySelector('.h18-page-section-type') || {}).value, 70),
            parentKey: text(parent && parent.value, 100),
            selected: row.classList.contains('is-selected')
        };
    }
    function nestedInfo(node) {
        const nested = node && node.closest ? node.closest('.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child],.h18-v0851-stack-segment[data-h18-v0851-stack-key]') : null;
        if (!nested) { return null; }
        return {
            key: text(nested.getAttribute('data-h18-v0851-stack-key') || nested.getAttribute('data-h18-v0811-row') || nested.getAttribute('data-h18-v0811-child'), 100),
            selected: nested.classList.contains('is-h18-v0848-selected-element')
        };
    }
    function targetInfo(node) {
        if (!node || node.nodeType !== 1) { return { node: '-', path: '-', value: '', row: null, nested: null }; }
        return {
            node: nodeName(node),
            path: pathOf(node),
            value: valueOf(node),
            text: text(node.textContent, 100),
            row: rowInfo(node),
            nested: nestedInfo(node),
            data: {
                key: text(node.getAttribute('data-key'), 100),
                sectionType: text(node.getAttribute('data-section-type'), 60),
                position: text(node.getAttribute('data-h18-v0838-position'), 40),
                target: text(node.getAttribute('data-h18-v0838-target'), 100),
                inside: text(node.getAttribute('data-h18-v0871-inside-kasse'), 100),
                legoPath: text(node.getAttribute('data-h18-lego-path') || node.getAttribute('data-h18-lego-design-path'), 120)
            }
        };
    }
    function selectionState() {
        const api = window.__h18LegoInspectorOnlyV0847;
        let active = {};
        try { active = api && typeof api.activeSelection === 'function' ? api.activeSelection() : {}; } catch (ignore) { active = {}; }
        const row = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
        const red = Array.from(document.querySelectorAll('.is-h18-v0848-selected-element')).map(function (node) {
            return text(node.getAttribute('data-h18-v0851-stack-key') || node.getAttribute('data-h18-v0811-row') || node.getAttribute('data-h18-v0811-child') || keyOfRow(node.closest('.h18-page-section-row')), 100);
        }).filter(Boolean);
        return {
            runtime: text(document.documentElement.getAttribute('data-h18-lego-selection-marker'), 30),
            api: api ? text(api.version, 30) : '',
            key: text(active.key, 100), mode: text(active.mode, 20), nativeRow: keyOfRow(row), red: red
        };
    }
    function dropState() {
        const api = window.__h18LegoDropZonesV0838;
        let source = {};
        try { source = api && typeof api.activeSource === 'function' ? api.activeSource() : {}; } catch (ignore) { source = {}; }
        const active = document.querySelector('.h18-v0838-drop-zone.is-active');
        return {
            runtime: text(document.documentElement.getAttribute('data-h18-lego-inside-kasse-zone'), 30),
            api: api ? text(api.capabilityVersion || api.version, 30) : '',
            sourceKey: text(source.Key || source.key, 100), sourceType: text(source.Type || source.type, 50), sourceMode: text(source.Mode || source.mode, 30),
            overlays: document.querySelectorAll('.h18-v0838-drop-overlay').length,
            boxOverlays: document.querySelectorAll('.h18-v0838-drop-overlay[data-h18-v0871-target-box="1"]').length,
            insideZones: document.querySelectorAll('.h18-v0838-drop-zone.is-inside').length,
            active: active ? text(active.getAttribute('data-h18-v0838-position'), 30) + ':' + text(active.getAttribute('data-h18-v0838-target'), 100) : '',
            result: text(document.documentElement.getAttribute('data-h18-v0871-last-inside-result') || document.documentElement.getAttribute('data-h18-v0872-last-inside-result') || document.documentElement.getAttribute('data-h18-v0875-last-inside-result'), 80)
        };
    }
    function state() {
        const focus = document.activeElement;
        return {
            selection: selectionState(), drop: dropState(),
            focus: { node: nodeName(focus), path: pathOf(focus), value: valueOf(focus) },
            inspectorKey: text((document.querySelector('#h18-page-inspector-target .h18-page-section-key') || {}).value, 100)
        };
    }
    function simple(value, depth) {
        const d = depth || 0;
        if (d > 2) { return '[depth]'; }
        if (value == null || typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') { return value; }
        if (value instanceof Element) { return targetInfo(value); }
        if (window.jQuery && value && value.jquery) { return value.length ? targetInfo(value.get(0)) : '[empty-jquery]'; }
        if (Array.isArray(value)) { return value.slice(0, 8).map(function (item) { return simple(item, d + 1); }); }
        if (typeof value === 'object') {
            const result = {};
            Object.keys(value).slice(0, 18).forEach(function (key) {
                if (sensitive(key)) { result[key] = '[REDACTED]'; }
                else { try { result[key] = simple(value[key], d + 1); } catch (ignore) { result[key] = '[error]'; } }
            });
            return result;
        }
        return text(value, 120);
    }
    function schedulePersist() {
        clearTimeout(persistTimer);
        persistTimer = setTimeout(persist, 220);
    }
    function persist() {
        persistTimer = 0;
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: VERSION, sessionId: sessionId, startedAt: startedAt, logging: logging, events: events.slice(-MAX_PERSISTED) }));
        } catch (ignore) { /* local storage unavailable/full */ }
    }
    function restore() {
        try {
            const parsed = JSON.parse(localStorage.getItem(STORAGE_KEY) || 'null');
            if (parsed && Array.isArray(parsed.events)) {
                events = parsed.events.slice(-MAX_PERSISTED);
                seq = events.reduce(function (max, entry) { return Math.max(max, Number(entry.seq) || 0); }, 0);
                sessionId = text(parsed.sessionId, 100) || id();
                startedAt = text(parsed.startedAt, 80) || iso();
                logging = parsed.logging === true;
            }
        } catch (ignore) { /* ignore */ }
        if (!sessionId) { sessionId = id(); }
        if (!startedAt) { startedAt = iso(); }
    }
    function record(type, target, detail, options) {
        const force = options && options.force;
        if (!logging && !force) { return null; }
        const entry = { seq: ++seq, time: iso(), local: clock(), session: sessionId, type: type, target: targetInfo(target && target.nodeType === 1 ? target : null), detail: simple(detail || {}, 0), state: state() };
        events.push(entry);
        if (events.length > MAX_EVENTS) { events.splice(0, events.length - MAX_EVENTS); }
        updatePanel(); schedulePersist();
        return entry;
    }
    function line(entry) {
        const target = entry.target || {}; const row = target.row || {}; const nested = target.nested || {}; const s = entry.state || {}; const sel = s.selection || {}; const drop = s.drop || {};
        return String(entry.seq).padStart(5, '0') + ' ' + entry.local + ' [' + entry.type + '] target=' + (target.node || '-') + ' row=' + (row.key || '-') + '/' + (row.type || '-') + '/parent:' + (row.parentKey || '-') + ' nested=' + (nested.key || '-') + ' SEL=' + (sel.key || '-') + '/' + (sel.mode || '-') + '/native:' + (sel.nativeRow || '-') + '/red:' + (sel.red || []).join(',') + ' DROP=' + (drop.sourceKey || '-') + '/' + (drop.sourceType || '-') + '/' + (drop.active || '-') + '/inside:' + (drop.insideZones || 0) + '/result:' + (drop.result || '-') + ' focus=' + ((s.focus || {}).node || '-') + (Object.keys(entry.detail || {}).length ? ' detail=' + JSON.stringify(entry.detail) : '');
    }
    function exportText() {
        return ['Hangar18 Ultimate Designer Trace ' + VERSION, 'session=' + sessionId, 'started=' + startedAt, 'logging=' + (logging ? 'ON' : 'OFF'), 'exported=' + iso(), 'url=' + location.href, 'events=' + events.length, ''].join('\n') + events.map(line).join('\n');
    }
    function exportJson() { return JSON.stringify({ product: 'Hangar18 Ultimate Designer', traceVersion: VERSION, sessionId: sessionId, startedAt: startedAt, logging: logging, exportedAt: iso(), url: location.href, runtime: state(), events: events }, null, 2); }
    function download(name, content, mime) {
        const blob = new Blob([content], { type: mime }); const url = URL.createObjectURL(blob); const a = document.createElement('a');
        a.href = url; a.download = name; a.style.display = 'none'; document.body.appendChild(a); a.click(); a.remove(); setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    }
    function setLogging(value, reason) {
        logging = value === true;
        record(logging ? 'TRACE_ON' : 'TRACE_OFF', document.activeElement, { reason: reason || '' }, { force: true });
        persist(); updatePanel();
    }
    function startTest() {
        events = []; seq = 0; sessionId = id(); startedAt = iso(); logging = true;
        record('TEST_START', document.activeElement, { version: VERSION }, { force: true }); persist(); updatePanel();
    }
    function reset() {
        events = []; seq = 0; sessionId = id(); startedAt = iso(); logging = false;
        try { localStorage.removeItem(STORAGE_KEY); } catch (ignore) { /* ignore */ }
        updatePanel();
    }
    function button(label, fn) {
        const b = document.createElement('button'); b.type = 'button'; b.className = 'button button-small'; b.textContent = label;
        b.addEventListener('click', function (event) { event.preventDefault(); event.stopPropagation(); fn(b); }); return b;
    }
    function updatePanel() {
        if (!panel) { return; }
        statusNode.textContent = logging ? 'LOG TIL' : 'LOG FRA';
        statusNode.style.fontWeight = '700';
        countNode.textContent = events.length + ' events';
        toggleButton.textContent = logging ? 'Stop log' : 'Fortsæt log';
        if (panel.getAttribute('data-expanded') === '1') { pre.textContent = events.slice(-45).map(line).join('\n') || 'Ingen events endnu.'; pre.scrollTop = pre.scrollHeight; }
    }
    function installPanel() {
        if (panel || !document.body) { return; }
        panel = document.createElement('aside'); panel.id = 'h18-ultimate-designer-trace-v0876'; panel.setAttribute('data-expanded', '0');
        panel.style.cssText = 'position:fixed;left:16px;bottom:16px;z-index:2147483100;width:min(800px,calc(100vw - 32px));background:#fff;border:2px solid #1d2327;border-radius:8px;box-shadow:0 8px 28px rgba(0,0,0,.24);font:12px/1.35 Consolas,Monaco,monospace;color:#1d2327;';
        const head = document.createElement('div'); head.style.cssText = 'display:flex;align-items:center;gap:6px;padding:8px;flex-wrap:wrap;';
        statusNode = document.createElement('strong'); countNode = document.createElement('span'); countNode.style.marginRight = 'auto';
        const show = button('Vis log', function (b) { const on = panel.getAttribute('data-expanded') === '1'; panel.setAttribute('data-expanded', on ? '0' : '1'); pre.style.display = on ? 'none' : 'block'; b.textContent = on ? 'Vis log' : 'Skjul log'; updatePanel(); });
        const start = button('Start test', function () { startTest(); });
        toggleButton = button('Fortsæt log', function () { setLogging(!logging, 'manual-toggle'); });
        const mark = button('Markér', function () { const label = window.prompt('Beskriv hvad du tester/ser:', ''); if (label != null) { record('TEST_MARKER', document.activeElement, { label: text(label, 240) }, { force: true }); } });
        const copy = button('Kopiér', function (b) { const payload = exportText(); if (navigator.clipboard && navigator.clipboard.writeText) { navigator.clipboard.writeText(payload).then(function () { const old = b.textContent; b.textContent = 'Kopieret'; setTimeout(function () { b.textContent = old; }, 1000); }); } else { window.prompt('Kopiér trace:', payload); } });
        const txt = button('TXT', function () { download('hangar18-trace-' + sessionId + '.txt', exportText(), 'text/plain;charset=utf-8'); });
        const json = button('JSON', function () { download('hangar18-trace-' + sessionId + '.json', exportJson(), 'application/json;charset=utf-8'); });
        const clear = button('Nulstil', function () { if (window.confirm('Nulstil trace og slå log fra?')) { reset(); } });
        head.append(statusNode, countNode, show, start, toggleButton, mark, copy, txt, json, clear);
        pre = document.createElement('pre'); pre.style.cssText = 'display:none;margin:0;border-top:1px solid #c3c4c7;padding:8px;max-height:43vh;overflow:auto;white-space:pre-wrap;user-select:text;background:#f6f7f7;';
        panel.append(head, pre); document.body.appendChild(panel); updatePanel();
    }
    function eventDetail(event) { return { event: event.type, key: event.key, code: event.code, button: event.button, buttons: event.buttons, ctrl: !!event.ctrlKey, shift: !!event.shiftKey, alt: !!event.altKey, meta: !!event.metaKey, x: Number.isFinite(event.clientX) ? event.clientX : undefined, y: Number.isFinite(event.clientY) ? event.clientY : undefined, prevented: !!event.defaultPrevented }; }
    function installEvents() {
        ['pointerdown', 'pointerup', 'pointercancel', 'click', 'dblclick', 'focusin', 'focusout', 'input', 'change', 'keydown', 'dragstart', 'drop', 'dragend'].forEach(function (name) { document.addEventListener(name, function (event) { record(name, event.target, eventDetail(event)); }, true); });
        document.addEventListener('dragover', function (event) { if (!logging || highFreqTimer) { return; } highFreqTimer = setTimeout(function () { highFreqTimer = 0; record('dragover', event.target, eventDetail(event)); }, HIGH_FREQ_MS); }, true);
        window.addEventListener('resize', function () { record('window.resize', document.activeElement, { width: innerWidth, height: innerHeight }); });
        window.addEventListener('beforeunload', function () { if (logging) { record('PAGE_UNLOAD', document.activeElement, {}, { force: true }); } persist(); });
        window.addEventListener('error', function (event) { record('JS_ERROR', event.target, { message: event.message, file: event.filename, line: event.lineno, col: event.colno, stack: event.error && event.error.stack }, { force: true }); }, true);
        window.addEventListener('unhandledrejection', function (event) { const reason = event.reason; record('UNHANDLED_REJECTION', null, { reason: reason && (reason.stack || reason.message || reason) }, { force: true }); });
    }
    function installSortable() {
        if (!window.jQuery) { return; } const $ = window.jQuery; const selector = '#h18-page-sections-sortable';
        ['sortstart', 'sortchange', 'sortupdate', 'sortstop', 'sortcancel', 'sortreceive', 'sortremove'].forEach(function (name) { $(document).on(name + '.h18Trace0876', selector, function (event, ui) { const item = ui && ui.item && ui.item.length ? ui.item.get(0) : event.target; record(name, item, {}); }); });
        $(document).on('sort.h18Trace0876', selector, function (event, ui) { if (!logging || highFreqTimer) { return; } highFreqTimer = setTimeout(function () { highFreqTimer = 0; const item = ui && ui.item && ui.item.length ? ui.item.get(0) : event.target; record('sort', item, {}); }, HIGH_FREQ_MS); });
    }
    function installMutations() {
        if (!window.MutationObserver || !document.body) { return; }
        new MutationObserver(function (list) {
            if (!logging) { return; }
            if (!mutationBucket) { mutationBucket = { childList: 0, attributes: 0, added: 0, removed: 0, samples: [] }; }
            list.forEach(function (m) { if (m.type === 'childList') { mutationBucket.childList += 1; mutationBucket.added += m.addedNodes.length; mutationBucket.removed += m.removedNodes.length; } else { mutationBucket.attributes += 1; } if (mutationBucket.samples.length < 8 && m.target && m.target.nodeType === 1) { mutationBucket.samples.push({ type: m.type, attr: m.attributeName || '', target: nodeName(m.target) }); } });
            clearTimeout(mutationTimer); mutationTimer = setTimeout(function () { const bucket = mutationBucket; mutationBucket = null; record('DOM_MUTATIONS', document.activeElement, bucket); }, MUTATION_MS);
        }).observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'style', 'data-key', 'data-h18-v0838-position', 'data-h18-v0838-target', 'data-h18-v0871-inside-kasse', 'data-h18-nested-in-box', 'data-h18-v0811-child-source'] });
    }
    function wrapConsole() {
        ['warn', 'error'].forEach(function (name) { const native = console[name]; if (!native || native.__h18TraceWrapped) { return; } const fn = function () { record('console.' + name, null, { args: Array.from(arguments).map(function (arg) { return simple(arg, 0); }) }, { force: true }); return native.apply(console, arguments); }; fn.__h18TraceWrapped = true; console[name] = fn; });
    }
    function wrap(ownerName, object, methodName) {
        if (!object || typeof object[methodName] !== 'function' || object[methodName].__h18TraceWrapped) { return; }
        const native = object[methodName]; const fn = function () { record('CALL ' + ownerName + '.' + methodName, null, { args: Array.from(arguments).map(function (arg) { return simple(arg, 0); }) }); try { const result = native.apply(this, arguments); record('RETURN ' + ownerName + '.' + methodName, null, { result: simple(result, 0) }); return result; } catch (error) { record('THROW ' + ownerName + '.' + methodName, null, { message: error.message, stack: error.stack }, { force: true }); throw error; } }; fn.__h18TraceWrapped = true; object[methodName] = fn; wrapped.push(ownerName + '.' + methodName);
    }
    function instrument() {
        [['nesting', window.__h18NestingToolsV0840, ['refresh']], ['selection', window.__h18LegoInspectorOnlyV0847, ['selectInspectorForNode', 'refreshSelectedCanvasMarker', 'rememberSelectedCanvasKey']], ['parentGuard', window.__h18LegoParentKeyGuardV0845, ['reconcileNow', 'ensureParentOption', 'armVisualReconcile']], ['stack', window.__h18LegoFixesV0851, ['adoptUnder', 'clearStackForKey']], ['placement', window.__h18LegoPlacementStabilityV0862, ['moveElementIntoBox']], ['dropZones', window.__h18LegoDropZonesV0838, ['refresh', 'clear']]].forEach(function (group) { group[2].forEach(function (method) { wrap(group[0], group[1], method); }); });
        record('TRACE_INSTRUMENTATION', null, { wrapped: wrapped.slice() }, { force: true });
    }
    function install() {
        installPanel(); wrapConsole(); installEvents(); installSortable(); installMutations(); instrument();
        record('PAGE_LOAD', document.activeElement, { version: VERSION, loggingRestored: logging, viewport: { width: innerWidth, height: innerHeight }, userAgent: navigator.userAgent }, { force: true }); persist();
    }

    restore();
    document.documentElement.setAttribute('data-h18-ultimate-designer-trace', VERSION);
    window.__h18UltimateDesignerTraceV0876 = { version: VERSION, record: record, events: function () { return events.slice(); }, exportText: exportText, exportJson: exportJson, startTest: startTest, setLogging: setLogging, reset: reset, state: state, isLogging: function () { return logging; } };
    if (document.body) { setTimeout(install, 0); } else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); } else { setTimeout(install, 0); }
}());
