(function () {
    'use strict';

    if (window.__h18UltimateDesignerTraceV0876) { return; }

    const VERSION = '0.8.76';
    const STORAGE_KEY = 'h18.ultimate-designer.trace.v0876';
    const MAX_MEMORY_EVENTS = 3000;
    const MAX_PERSISTED_EVENTS = 1400;
    const VALUE_LIMIT = 180;
    const TEXT_LIMIT = 120;
    const MUTATION_FLUSH_MS = 120;
    const MOVE_SAMPLE_MS = 90;

    let events = [];
    let seq = 0;
    let paused = false;
    let panel = null;
    let bodyPre = null;
    let countNode = null;
    let statusNode = null;
    let persistTimer = 0;
    let mutationTimer = 0;
    let moveTimer = 0;
    let mutationBucket = null;
    let sessionId = '';
    let traceStartedAt = '';
    const wrappedFunctions = [];

    function nowIso() { return new Date().toISOString(); }
    function localTime() {
        const d = new Date();
        return d.toLocaleTimeString('da-DK', { hour12: false }) + '.' + String(d.getMilliseconds()).padStart(3, '0');
    }
    function safeString(value) {
        if (value == null) { return ''; }
        try { return String(value); } catch (ignore) { return '[unprintable]'; }
    }
    function truncate(value, max) {
        const text = safeString(value).replace(/\s+/g, ' ').trim();
        const limit = typeof max === 'number' ? max : TEXT_LIMIT;
        return text.length > limit ? text.slice(0, limit) + '…' : text;
    }
    function randomId() {
        return Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 9);
    }
    function isSensitiveName(value) {
        return /pass(word)?|secret|token|nonce|authorization|api[-_ ]?key|cookie|bearer|credential/i.test(safeString(value));
    }
    function safeValue(node) {
        if (!node) { return ''; }
        const type = safeString(node.type).toLowerCase();
        const identity = [node.id, node.name, node.getAttribute && node.getAttribute('data-h18-lego-path'), node.getAttribute && node.getAttribute('data-h18-lego-design-path')].join(' ');
        if (type === 'password' || isSensitiveName(identity)) { return '[REDACTED]'; }
        if (type === 'checkbox' || type === 'radio') { return node.checked ? 'checked' : 'unchecked'; }
        if (type === 'file') { return node.files && node.files.length ? '[file:' + node.files.length + ']' : '[no-file]'; }
        if (node.tagName === 'SELECT') {
            const option = node.options && node.selectedIndex >= 0 ? node.options[node.selectedIndex] : null;
            return truncate((option ? option.text : '') + ' [' + safeString(node.value) + ']', VALUE_LIMIT);
        }
        if ('value' in node) { return truncate(node.value, VALUE_LIMIT); }
        if (node.isContentEditable) { return truncate(node.textContent, VALUE_LIMIT); }
        return '';
    }
    function importantData(node) {
        if (!node || !node.getAttribute) { return {}; }
        const names = [
            'data-key', 'data-section-type', 'data-h18-v0811-row', 'data-h18-v0811-child',
            'data-h18-v0851-stack-key', 'data-h18-v0838-position', 'data-h18-v0838-target',
            'data-h18-v0871-inside-kasse', 'data-h18-layout-tool', 'data-section-type',
            'data-h18-lego-path', 'data-h18-lego-design-path'
        ];
        const result = {};
        names.forEach(function (name) {
            const value = node.getAttribute(name);
            if (value != null && value !== '') { result[name] = truncate(value, 100); }
        });
        return result;
    }
    function nodeLabel(node) {
        if (!node || node.nodeType !== 1) { return node && node.nodeName ? node.nodeName : '-'; }
        let label = node.tagName.toLowerCase();
        if (node.id) { label += '#' + node.id; }
        const classes = Array.from(node.classList || []).slice(0, 5);
        if (classes.length) { label += '.' + classes.join('.'); }
        return truncate(label, 180);
    }
    function domPath(node) {
        if (!node || !node.closest) { return '-'; }
        const parts = [];
        let cursor = node;
        let depth = 0;
        while (cursor && cursor.nodeType === 1 && depth < 6) {
            parts.unshift(nodeLabel(cursor));
            if (cursor.id === 'h18-page-sections-sortable' || cursor.id === 'h18-page-inspector-target') { break; }
            cursor = cursor.parentElement;
            depth += 1;
        }
        return parts.join(' > ');
    }
    function rowKey(row) {
        if (!row) { return ''; }
        const direct = row.querySelector && row.querySelector('.h18-page-section-key');
        if (direct && direct.value) { return safeString(direct.value).trim(); }
        return safeString(row.getAttribute && row.getAttribute('data-key')).trim();
    }
    function rowContext(node) {
        const row = node && node.closest ? node.closest('.h18-page-section-row') : null;
        if (!row) { return null; }
        let parent = row.querySelector('.h18-layout-parent-key');
        if ((!parent || !parent.value) && row.classList.contains('is-selected')) {
            parent = document.querySelector('#h18-page-inspector-target .h18-layout-parent-key') || parent;
        }
        return {
            key: rowKey(row),
            type: safeString(row.getAttribute('data-section-type') || (row.querySelector('.h18-page-section-type') || {}).value).trim(),
            parentKey: safeString(parent && parent.value).trim(),
            selected: row.classList.contains('is-selected'),
            removed: row.classList.contains('h18-page-section-removed')
        };
    }
    function nestedContext(node) {
        const nested = node && node.closest ? node.closest('.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child],.h18-v0851-stack-segment[data-h18-v0851-stack-key]') : null;
        if (!nested) { return null; }
        return {
            key: safeString(nested.getAttribute('data-h18-v0851-stack-key') || nested.getAttribute('data-h18-v0811-row') || nested.getAttribute('data-h18-v0811-child')).trim(),
            selected: nested.classList.contains('is-h18-v0848-selected-element'),
            node: nodeLabel(nested)
        };
    }
    function focusContext() {
        const node = document.activeElement;
        return {
            node: nodeLabel(node),
            path: domPath(node),
            value: safeValue(node)
        };
    }
    function inspectorTab() {
        const selected = document.querySelector('#h18-page-inspector-target [aria-selected="true"],#h18-page-inspector-target .is-active,#h18-page-inspector-target .active');
        return selected ? truncate(selected.textContent || selected.getAttribute('aria-label') || nodeLabel(selected), 80) : '';
    }
    function selectionState() {
        const api = window.__h18LegoInspectorOnlyV0847;
        let active = {};
        try { active = api && typeof api.activeSelection === 'function' ? api.activeSelection() : {}; } catch (ignore) { active = {}; }
        const nativeRow = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
        const redNodes = Array.from(document.querySelectorAll('.is-h18-v0848-selected-element'));
        return {
            runtime: safeString(document.documentElement.getAttribute('data-h18-lego-selection-marker')),
            api: api ? safeString(api.version) : '',
            key: safeString(active && active.key),
            mode: safeString(active && active.mode),
            nativeRowKey: rowKey(nativeRow),
            redKeys: redNodes.map(function (node) {
                return safeString(node.getAttribute('data-h18-v0851-stack-key') || node.getAttribute('data-h18-v0811-row') || node.getAttribute('data-h18-v0811-child') || rowKey(node.closest('.h18-page-section-row'))).trim();
            }).filter(Boolean),
            redCount: redNodes.length
        };
    }
    function dropState() {
        const api = window.__h18LegoDropZonesV0838;
        let source = {};
        try { source = api && typeof api.activeSource === 'function' ? api.activeSource() : {}; } catch (ignore) { source = {}; }
        const overlays = document.querySelectorAll('.h18-v0838-drop-overlay');
        const boxOverlays = document.querySelectorAll('.h18-v0838-drop-overlay[data-h18-v0871-target-box="1"]');
        const inside = document.querySelectorAll('.h18-v0838-drop-zone.is-inside');
        const active = document.querySelector('.h18-v0838-drop-zone.is-active');
        return {
            runtime: safeString(document.documentElement.getAttribute('data-h18-lego-inside-kasse-zone')),
            api: api ? safeString(api.capabilityVersion || api.version) : '',
            sourceKey: safeString(source.Key || source.key),
            sourceType: safeString(source.Type || source.type),
            sourceMode: safeString(source.Mode || source.mode),
            overlays: overlays.length,
            boxOverlays: boxOverlays.length,
            insideZones: inside.length,
            active: active ? safeString(active.getAttribute('data-h18-v0838-position')) + ':' + safeString(active.getAttribute('data-h18-v0838-target')) : '',
            result: safeString(document.documentElement.getAttribute('data-h18-v0871-last-inside-result') || document.documentElement.getAttribute('data-h18-v0872-last-inside-result') || document.documentElement.getAttribute('data-h18-v0875-last-inside-result'))
        };
    }
    function runtimeState() {
        return {
            selection: selectionState(),
            drop: dropState(),
            focus: focusContext(),
            inspectorTab: inspectorTab(),
            pageMode: truncate((document.querySelector('.h18-builder-mode,.h18-preview-state.is-active,.h18-preview-device.is-active') || {}).textContent || '', 80)
        };
    }
    function eventTargetContext(target) {
        return {
            node: nodeLabel(target),
            path: domPath(target),
            text: truncate(target && target.textContent, TEXT_LIMIT),
            value: safeValue(target),
            data: importantData(target),
            row: rowContext(target),
            nested: nestedContext(target)
        };
    }
    function simplify(value, depth) {
        const level = depth || 0;
        if (level > 2) { return '[depth]'; }
        if (value == null || typeof value === 'string' || typeof value === 'number' || typeof value === 'boolean') { return value; }
        if (value instanceof Element) { return eventTargetContext(value); }
        if (window.jQuery && value && value.jquery) { return value.length ? eventTargetContext(value.get(0)) : '[empty-jquery]'; }
        if (Array.isArray(value)) { return value.slice(0, 8).map(function (item) { return simplify(item, level + 1); }); }
        if (typeof value === 'object') {
            const result = {};
            Object.keys(value).slice(0, 16).forEach(function (key) {
                if (isSensitiveName(key)) { result[key] = '[REDACTED]'; }
                else {
                    try { result[key] = simplify(value[key], level + 1); } catch (ignore) { result[key] = '[error]'; }
                }
            });
            return result;
        }
        return truncate(value, 120);
    }
    function shouldPersistEvent(type) {
        return type !== 'pointermove' && type !== 'dragover' && type !== 'sort';
    }
    function record(type, target, detail, options) {
        if (paused && !(options && options.force)) { return null; }
        const entry = {
            seq: ++seq,
            time: nowIso(),
            local: localTime(),
            perfMs: Math.round((window.performance && performance.now ? performance.now() : 0) * 1000) / 1000,
            session: sessionId,
            type: type,
            target: eventTargetContext(target && target.nodeType === 1 ? target : null),
            detail: simplify(detail || {}, 0),
            state: runtimeState()
        };
        events.push(entry);
        if (events.length > MAX_MEMORY_EVENTS) { events.splice(0, events.length - MAX_MEMORY_EVENTS); }
        updatePanel();
        if (shouldPersistEvent(type)) { schedulePersist(); }
        return entry;
    }
    function loadPersisted() {
        try {
            const raw = localStorage.getItem(STORAGE_KEY);
            if (!raw) { return; }
            const parsed = JSON.parse(raw);
            if (parsed && Array.isArray(parsed.events)) {
                events = parsed.events.slice(-MAX_PERSISTED_EVENTS);
                seq = events.reduce(function (max, item) { return Math.max(max, Number(item.seq) || 0); }, 0);
            }
            sessionId = safeString(parsed && parsed.sessionId) || randomId();
            traceStartedAt = safeString(parsed && parsed.traceStartedAt) || nowIso();
        } catch (ignore) { /* storage may be disabled */ }
    }
    function persist() {
        persistTimer = 0;
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify({
                version: VERSION,
                sessionId: sessionId,
                traceStartedAt: traceStartedAt,
                savedAt: nowIso(),
                events: events.slice(-MAX_PERSISTED_EVENTS)
            }));
        } catch (error) {
            if (events.length > 400) {
                events = events.slice(-400);
                try { localStorage.setItem(STORAGE_KEY, JSON.stringify({ version: VERSION, sessionId: sessionId, traceStartedAt: traceStartedAt, savedAt: nowIso(), events: events })); } catch (ignore) { /* ignore */ }
            }
        }
    }
    function schedulePersist() {
        window.clearTimeout(persistTimer);
        persistTimer = window.setTimeout(persist, 250);
    }
    function clearTrace(startNew) {
        events = [];
        seq = 0;
        sessionId = randomId();
        traceStartedAt = nowIso();
        try { localStorage.removeItem(STORAGE_KEY); } catch (ignore) { /* ignore */ }
        if (startNew !== false) { record('TEST_START', null, { label: 'Ny test startet', version: VERSION }, { force: true }); }
        updatePanel();
    }
    function textLine(entry) {
        const t = entry.target || {};
        const state = entry.state || {};
        const sel = state.selection || {};
        const drop = state.drop || {};
        const row = t.row || {};
        const nested = t.nested || {};
        const detail = entry.detail && Object.keys(entry.detail).length ? ' detail=' + JSON.stringify(entry.detail) : '';
        return [
            String(entry.seq).padStart(5, '0'), entry.local, '[' + entry.type + ']',
            'target=' + (t.node || '-'),
            'row=' + (row.key || '-') + '/' + (row.type || '-') + '/parent:' + (row.parentKey || '-'),
            'nested=' + (nested.key || '-'),
            'SEL=' + (sel.key || '-') + '/' + (sel.mode || '-') + '/native:' + (sel.nativeRowKey || '-') + '/red:' + (sel.redKeys || []).join(','),
            'DROP=' + (drop.sourceKey || '-') + '/' + (drop.sourceType || '-') + '/' + (drop.active || '-') + '/inside:' + (drop.insideZones || 0) + '/result:' + (drop.result || '-'),
            'focus=' + ((state.focus || {}).node || '-')
        ].join(' ') + detail;
    }
    function exportText() {
        const header = [
            'Hangar18 Ultimate Designer Trace ' + VERSION,
            'session=' + sessionId,
            'started=' + traceStartedAt,
            'exported=' + nowIso(),
            'url=' + location.href,
            'events=' + events.length,
            ''
        ].join('\n');
        return header + events.map(textLine).join('\n');
    }
    function exportJson() {
        return JSON.stringify({
            product: 'Hangar18 Ultimate Designer',
            traceVersion: VERSION,
            sessionId: sessionId,
            startedAt: traceStartedAt,
            exportedAt: nowIso(),
            url: location.href,
            runtime: runtimeState(),
            events: events
        }, null, 2);
    }
    function download(name, content, type) {
        const blob = new Blob([content], { type: type || 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = name; a.style.display = 'none';
        document.body.appendChild(a); a.click(); a.remove();
        window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    }
    function copyText() {
        const text = exportText();
        if (navigator.clipboard && navigator.clipboard.writeText) { return navigator.clipboard.writeText(text); }
        window.prompt('Kopiér trace:', text);
        return Promise.resolve();
    }
    function updatePanel() {
        if (!panel) { return; }
        if (countNode) { countNode.textContent = String(events.length) + ' events'; }
        if (statusNode) { statusNode.textContent = paused ? 'PAUSE' : 'LOGGER'; }
        if (bodyPre && panel.getAttribute('data-expanded') === '1') {
            bodyPre.textContent = events.slice(-40).map(textLine).join('\n') || 'Ingen events endnu.';
            bodyPre.scrollTop = bodyPre.scrollHeight;
        }
    }
    function button(text, fn) {
        const b = document.createElement('button');
        b.type = 'button'; b.className = 'button button-small'; b.textContent = text;
        b.addEventListener('click', function (event) { event.preventDefault(); event.stopPropagation(); fn(b); });
        return b;
    }
    function installPanel() {
        if (panel || !document.body) { return; }
        panel = document.createElement('aside');
        panel.id = 'h18-ultimate-designer-trace-v0876';
        panel.setAttribute('data-expanded', '0');
        panel.style.cssText = 'position:fixed;left:16px;bottom:16px;z-index:2147483100;width:min(760px,calc(100vw - 32px));background:#fff;border:2px solid #1d2327;border-radius:8px;box-shadow:0 8px 28px rgba(0,0,0,.24);font:12px/1.35 Consolas,Monaco,monospace;color:#1d2327;';
        const head = document.createElement('div');
        head.style.cssText = 'display:flex;align-items:center;gap:6px;padding:8px;flex-wrap:wrap;';
        statusNode = document.createElement('strong'); statusNode.textContent = 'LOGGER';
        countNode = document.createElement('span'); countNode.style.marginRight = 'auto';
        const toggle = button('Vis log', function (b) {
            const expanded = panel.getAttribute('data-expanded') === '1';
            panel.setAttribute('data-expanded', expanded ? '0' : '1');
            bodyPre.style.display = expanded ? 'none' : 'block';
            b.textContent = expanded ? 'Vis log' : 'Skjul log';
            updatePanel();
        });
        const start = button('Start test', function () { clearTrace(true); });
        const marker = button('Markér', function () {
            const label = window.prompt('Navn/beskrivelse til markeringen:', '');
            if (label != null) { record('TEST_MARKER', document.activeElement, { label: truncate(label, 200) }, { force: true }); }
        });
        const pause = button('Pause', function (b) {
            paused = !paused; b.textContent = paused ? 'Fortsæt' : 'Pause';
            record(paused ? 'TRACE_PAUSE' : 'TRACE_RESUME', null, {}, { force: true }); updatePanel();
        });
        const copy = button('Kopiér', function (b) {
            copyText().then(function () { const old = b.textContent; b.textContent = 'Kopieret'; window.setTimeout(function () { b.textContent = old; }, 1000); });
        });
        const txt = button('TXT', function () { download('hangar18-trace-' + sessionId + '.txt', exportText(), 'text/plain;charset=utf-8'); });
        const json = button('JSON', function () { download('hangar18-trace-' + sessionId + '.json', exportJson(), 'application/json;charset=utf-8'); });
        const clear = button('Nulstil', function () { if (window.confirm('Nulstil hele trace-loggen?')) { clearTrace(false); } });
        head.append(statusNode, countNode, toggle, start, marker, pause, copy, txt, json, clear);
        bodyPre = document.createElement('pre');
        bodyPre.style.cssText = 'display:none;margin:0;border-top:1px solid #c3c4c7;padding:8px;max-height:42vh;overflow:auto;white-space:pre-wrap;user-select:text;background:#f6f7f7;';
        panel.append(head, bodyPre);
        document.body.appendChild(panel);
        updatePanel();
    }
    function eventDetail(event) {
        return {
            eventType: event.type,
            button: event.button,
            buttons: event.buttons,
            key: event.key,
            code: event.code,
            ctrl: !!event.ctrlKey,
            shift: !!event.shiftKey,
            alt: !!event.altKey,
            meta: !!event.metaKey,
            clientX: Number.isFinite(event.clientX) ? event.clientX : undefined,
            clientY: Number.isFinite(event.clientY) ? event.clientY : undefined,
            defaultPrevented: !!event.defaultPrevented
        };
    }
    function installDomEvents() {
        ['pointerdown', 'pointerup', 'pointercancel', 'click', 'dblclick', 'focusin', 'focusout', 'change', 'input', 'keydown', 'dragstart', 'drop', 'dragend'].forEach(function (type) {
            document.addEventListener(type, function (event) {
                record(type, event.target, eventDetail(event));
            }, true);
        });
        document.addEventListener('dragover', function (event) {
            if (moveTimer) { return; }
            moveTimer = window.setTimeout(function () { moveTimer = 0; record('dragover', event.target, eventDetail(event)); }, MOVE_SAMPLE_MS);
        }, true);
        window.addEventListener('resize', function () { record('window.resize', document.activeElement, { width: innerWidth, height: innerHeight }); });
        window.addEventListener('beforeunload', function () { record('PAGE_UNLOAD', document.activeElement, {}, { force: true }); persist(); });
        window.addEventListener('error', function (event) {
            record('JS_ERROR', event.target, { message: event.message, file: event.filename, line: event.lineno, col: event.colno, error: event.error && (event.error.stack || event.error.message) }, { force: true });
        }, true);
        window.addEventListener('unhandledrejection', function (event) {
            const reason = event.reason;
            record('UNHANDLED_REJECTION', null, { reason: reason && (reason.stack || reason.message || reason) }, { force: true });
        });
    }
    function installSortableEvents() {
        if (!window.jQuery) { return; }
        const $ = window.jQuery;
        const selector = '#h18-page-sections-sortable';
        ['sortstart', 'sortchange', 'sortupdate', 'sortstop', 'sortcancel', 'sortreceive', 'sortremove'].forEach(function (name) {
            $(document).on(name + '.h18Trace0876', selector, function (event, ui) {
                const item = ui && ui.item && ui.item.length ? ui.item.get(0) : null;
                record(name, item || event.target, { item: item ? eventTargetContext(item) : null });
            });
        });
        $(document).on('sort.h18Trace0876', selector, function (event, ui) {
            if (moveTimer) { return; }
            moveTimer = window.setTimeout(function () {
                moveTimer = 0;
                const item = ui && ui.item && ui.item.length ? ui.item.get(0) : null;
                record('sort', item || event.target, { item: item ? eventTargetContext(item) : null });
            }, MOVE_SAMPLE_MS);
        });
    }
    function installMutationObserver() {
        if (!window.MutationObserver || !document.body) { return; }
        new MutationObserver(function (mutations) {
            if (!mutationBucket) { mutationBucket = { childList: 0, attributes: 0, added: 0, removed: 0, samples: [] }; }
            mutations.forEach(function (mutation) {
                if (mutation.type === 'childList') {
                    mutationBucket.childList += 1;
                    mutationBucket.added += mutation.addedNodes ? mutation.addedNodes.length : 0;
                    mutationBucket.removed += mutation.removedNodes ? mutation.removedNodes.length : 0;
                } else if (mutation.type === 'attributes') { mutationBucket.attributes += 1; }
                if (mutationBucket.samples.length < 8 && mutation.target && mutation.target.nodeType === 1) {
                    mutationBucket.samples.push({ type: mutation.type, attribute: mutation.attributeName || '', target: nodeLabel(mutation.target), data: importantData(mutation.target) });
                }
            });
            window.clearTimeout(mutationTimer);
            mutationTimer = window.setTimeout(function () {
                const bucket = mutationBucket; mutationBucket = null; mutationTimer = 0;
                record('DOM_MUTATIONS', document.activeElement, bucket);
            }, MUTATION_FLUSH_MS);
        }).observe(document.body, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'style', 'data-key', 'data-h18-v0838-position', 'data-h18-v0838-target', 'data-h18-v0871-inside-kasse', 'data-h18-nested-in-box', 'data-h18-v0811-child-source'] });
    }
    function wrapConsole() {
        ['warn', 'error'].forEach(function (level) {
            const native = console[level];
            if (!native || native.__h18TraceWrapped) { return; }
            const wrapped = function () {
                try { record('console.' + level, null, { args: Array.from(arguments).map(function (arg) { return simplify(arg, 0); }) }, { force: true }); } catch (ignore) { /* ignore */ }
                return native.apply(console, arguments);
            };
            wrapped.__h18TraceWrapped = true;
            wrapped.__h18TraceNative = native;
            console[level] = wrapped;
        });
    }
    function wrapMethod(ownerName, object, methodName, noisy) {
        if (!object || typeof object[methodName] !== 'function') { return; }
        const native = object[methodName];
        if (native.__h18TraceWrapped) { return; }
        let last = 0;
        const wrapped = function () {
            if (noisy) {
                const now = Date.now();
                if (now - last < MOVE_SAMPLE_MS) { return native.apply(this, arguments); }
                last = now;
            }
            const args = Array.from(arguments).map(function (arg) { return simplify(arg, 0); });
            record('CALL ' + ownerName + '.' + methodName, null, { args: args });
            try {
                const result = native.apply(this, arguments);
                record('RETURN ' + ownerName + '.' + methodName, null, { result: simplify(result, 0) });
                return result;
            } catch (error) {
                record('THROW ' + ownerName + '.' + methodName, null, { message: error.message, stack: error.stack }, { force: true });
                throw error;
            }
        };
        wrapped.__h18TraceWrapped = true;
        wrapped.__h18TraceNative = native;
        object[methodName] = wrapped;
        wrappedFunctions.push(ownerName + '.' + methodName);
    }
    function instrumentRuntimes() {
        const targets = [
            ['nesting', window.__h18NestingToolsV0840, ['refresh']],
            ['selection', window.__h18LegoInspectorOnlyV0847, ['selectInspectorForNode', 'refreshSelectedCanvasMarker', 'rememberSelectedCanvasKey']],
            ['parentGuard', window.__h18LegoParentKeyGuardV0845, ['reconcileNow', 'ensureParentOption', 'armVisualReconcile']],
            ['stack', window.__h18LegoFixesV0851, ['adoptUnder', 'clearStackForKey']],
            ['placement', window.__h18LegoPlacementStabilityV0862, ['moveElementIntoBox']],
            ['dropZones', window.__h18LegoDropZonesV0838, ['refresh', 'clear']]
        ];
        targets.forEach(function (item) {
            item[2].forEach(function (method) { wrapMethod(item[0], item[1], method, method === 'refresh'); });
        });
        record('TRACE_INSTRUMENTATION', null, { wrapped: wrappedFunctions.slice() }, { force: true });
    }
    function install() {
        if (!sessionId) { sessionId = randomId(); }
        if (!traceStartedAt) { traceStartedAt = nowIso(); }
        installPanel();
        wrapConsole();
        installDomEvents();
        installSortableEvents();
        installMutationObserver();
        instrumentRuntimes();
        record('PAGE_LOAD', document.activeElement, {
            version: VERSION,
            href: location.href,
            userAgent: navigator.userAgent,
            viewport: { width: innerWidth, height: innerHeight },
            restoredEvents: events.length
        }, { force: true });
        persist();
    }

    loadPersisted();
    document.documentElement.setAttribute('data-h18-ultimate-designer-trace', VERSION);
    window.__h18UltimateDesignerTraceV0876 = {
        version: VERSION,
        record: record,
        events: function () { return events.slice(); },
        exportText: exportText,
        exportJson: exportJson,
        clear: clearTrace,
        pause: function (value) { paused = value !== false; updatePanel(); },
        state: runtimeState
    };

    if (document.body) { window.setTimeout(install, 0); }
    else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { window.setTimeout(install, 0); }
}());
