(function () {
    'use strict';

    if (window.__h18UltimateDesignerTraceToolsV0879) { return; }

    const VERSION = '0.8.79';
    const MAX_BASE_EVENTS = 2200;
    const config = window.H18UltimateDesignerTraceToolsV0879 || {};
    let api = null;
    let lastStartSeq = 0;
    let dock = null;
    let indicator = null;
    let filterSelect = null;
    let searchInput = null;
    let preview = null;
    let warning = null;
    let refreshTimer = 0;

    const GROUPS = {
        all: [],
        selection: ['SELECT', 'CLICK', 'FOCUS', 'INSPECTOR'],
        drag: ['DRAG', 'DROP', 'SORT', 'POINTER'],
        layout: ['LAYOUT', 'STACK', 'PARENT', 'RESIZE', 'RENDER', 'REFRESH'],
        inspector: ['INSPECTOR', 'INPUT', 'CHANGE', 'FOCUS'],
        save: ['SAVE', 'SUBMIT', 'VERSION', 'BACKUP'],
        error: ['ERROR', 'CRITICAL', 'REJECTION', 'WARN'],
        network: ['NETWORK', 'FETCH', 'AJAX', 'HTTP']
    };

    function text(value, max) {
        let out = '';
        try { out = value == null ? '' : String(value); } catch (ignore) { out = '[unprintable]'; }
        out = out.replace(/\s+/g, ' ').trim();
        return out.length > (max || 300) ? out.slice(0, max || 300) + '…' : out;
    }

    function redact(value, key) {
        const keyText = String(key || '');
        if (/pass(word)?|secret|token|nonce|authorization|api[-_ ]?key|cookie|bearer|credential|session|csrf/i.test(keyText)) {
            return '[REDACTED]';
        }
        if (Array.isArray(value)) { return value.slice(0, 5000).map(function (item) { return redact(item, ''); }); }
        if (value && typeof value === 'object') {
            const out = {};
            Object.keys(value).forEach(function (name) { out[name] = redact(value[name], name); });
            return out;
        }
        if (typeof value === 'string') {
            return value
                .replace(/(Bearer\s+)[A-Za-z0-9._~+\/-]+/gi, '$1[REDACTED]')
                .replace(/((?:token|nonce|password|secret|cookie|authorization)\s*[=:]\s*)[^\s,;]+/gi, '$1[REDACTED]');
        }
        return value;
    }

    function redactionSelfTest() {
        const sample = redact({ password: 'p', token: 't', nonce: 'n', cookie: 'c', nested: { authorization: 'Bearer abc' }, ok: 'value' }, '');
        return sample.password === '[REDACTED]' && sample.token === '[REDACTED]' && sample.nonce === '[REDACTED]' && sample.cookie === '[REDACTED]' && sample.nested.authorization === '[REDACTED]' && sample.ok === 'value';
    }

    function baseApi() {
        return window.__h18UltimateDesignerTraceV0876 || null;
    }

    function eventList() {
        try { return api && typeof api.events === 'function' ? api.events() : []; } catch (ignore) { return []; }
    }

    function pluginVersion() {
        return text(config.pluginVersion || document.querySelector('.h18-editor-version')?.textContent || '', 40).replace(/^Editor\s*v/i, '');
    }

    function pageSlug() {
        const params = new URLSearchParams(location.search);
        const hidden = document.querySelector('input[name="page_slug"]');
        return text((hidden && hidden.value) || params.get('page_slug') || '', 120);
    }

    function metadata() {
        return {
            traceToolsVersion: VERSION,
            pluginVersion: pluginVersion(),
            browser: navigator.userAgent,
            viewport: { width: window.innerWidth, height: window.innerHeight, dpr: window.devicePixelRatio || 1 },
            adminPage: new URLSearchParams(location.search).get('page') || '',
            pageSlug: pageSlug(),
            url: location.href,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || '',
            redactionSelfTest: redactionSelfTest()
        };
    }

    function record(type, detail, force) {
        if (!api || typeof api.record !== 'function') { return; }
        try { api.record(type, document.activeElement, redact(detail || {}, ''), force ? { force: true } : undefined); } catch (ignore) { /* diagnostics must not break editor */ }
    }

    function detectStart() {
        const events = eventList();
        for (let i = events.length - 1; i >= 0; i -= 1) {
            const entry = events[i] || {};
            if (entry.type === 'TEST_START') {
                const seq = Number(entry.seq) || 0;
                if (seq > lastStartSeq) {
                    lastStartSeq = seq;
                    record('SESSION_METADATA', metadata(), true);
                }
                return;
            }
        }
    }

    function isLogging() {
        try { return !!(api && typeof api.isLogging === 'function' && api.isLogging()); } catch (ignore) { return false; }
    }

    function typeMatches(type, group) {
        if (group === 'all') { return true; }
        const upper = String(type || '').toUpperCase();
        return (GROUPS[group] || []).some(function (needle) { return upper.indexOf(needle) !== -1; });
    }

    function eventHaystack(entry) {
        try { return JSON.stringify(redact(entry, '')).toLowerCase(); } catch (ignore) { return ''; }
    }

    function filteredEvents() {
        const group = filterSelect ? filterSelect.value : 'all';
        const query = searchInput ? searchInput.value.trim().toLowerCase() : '';
        return eventList().filter(function (entry) {
            if (!typeMatches(entry.type, group)) { return false; }
            return !query || eventHaystack(entry).indexOf(query) !== -1;
        });
    }

    function shortLine(entry) {
        const s = entry.state || {};
        const sel = s.selection || {};
        const drop = s.drop || {};
        return [
            String(entry.seq || '').padStart(5, '0'),
            entry.local || '',
            '[' + (entry.type || '-') + ']',
            'SEL=' + (sel.key || '-') + '/' + (sel.mode || '-'),
            'DROP=' + (drop.sourceKey || '-') + '/' + (drop.active || '-'),
            text(JSON.stringify(redact(entry.detail || {}, '')), 260)
        ].join(' ');
    }

    function runtimeSummary() {
        const root = document.documentElement;
        const globals = {
            trace: api ? api.version : '',
            traceTools: VERSION,
            selection: window.__h18LegoInspectorOnlyV0847?.version || '',
            nesting: window.__h18NestingToolsV0840?.version || '',
            dropZones: window.__h18LegoDropZonesV0838?.capabilityVersion || window.__h18LegoDropZonesV0838?.version || '',
            placement: window.__h18LegoPlacementStabilityV0862?.version || '',
            stack: window.__h18LegoFixesV0851?.version || ''
        };
        return {
            metadata: metadata(),
            globals: globals,
            rootAttributes: {
                selection: root.getAttribute('data-h18-lego-selection-marker') || '',
                inside: root.getAttribute('data-h18-lego-inside-kasse-zone') || '',
                placement: root.getAttribute('data-h18-lego-placement-stability') || '',
                trace: root.getAttribute('data-h18-ultimate-designer-trace') || ''
            },
            traceState: api && typeof api.state === 'function' ? redact(api.state(), '') : {}
        };
    }

    function supportBundle() {
        return redact({
            product: 'Hangar18 Ultimate Designer',
            bundleVersion: VERSION,
            exportedUtc: new Date().toISOString(),
            runtime: runtimeSummary(),
            events: eventList()
        }, '');
    }

    function downloadBundle() {
        const content = JSON.stringify(supportBundle(), null, 2);
        const blob = new Blob([content], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'hangar18-support-' + new Date().toISOString().replace(/[:.]/g, '-') + '.json';
        document.body.appendChild(a);
        a.click();
        a.remove();
        setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
        record('SUPPORT_BUNDLE_EXPORTED', { events: eventList().length, redactionSelfTest: redactionSelfTest() }, true);
    }

    function copyBundle() {
        const content = JSON.stringify(supportBundle(), null, 2);
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(content).then(function () { record('SUPPORT_BUNDLE_COPIED', { events: eventList().length }, true); });
        }
    }

    function makeButton(label, handler) {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'button button-small';
        button.textContent = label;
        button.addEventListener('click', handler);
        return button;
    }

    function installIndicator() {
        if (indicator) { return; }
        const host = document.querySelector('.h18-form-header') || document.querySelector('.wrap h1') || document.body;
        indicator = document.createElement('span');
        indicator.id = 'h18-trace-recording-indicator-v0879';
        indicator.setAttribute('role', 'status');
        indicator.style.cssText = 'display:inline-flex;align-items:center;gap:6px;margin-left:10px;padding:4px 8px;border-radius:999px;font-size:12px;font-weight:700;border:1px solid #8c8f94;background:#f6f7f7;color:#50575e;vertical-align:middle;';
        if (host.tagName === 'H1') { host.appendChild(indicator); } else { host.insertBefore(indicator, host.firstChild); }
    }

    function installDock() {
        if (dock) { return; }
        dock = document.createElement('section');
        dock.id = 'h18-trace-tools-v0879';
        dock.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:2147483099;width:min(660px,calc(100vw - 32px));background:#fff;border:1px solid #8c8f94;border-radius:6px;box-shadow:0 4px 18px rgba(0,0,0,.16);padding:10px;';

        const top = document.createElement('div');
        top.style.cssText = 'display:flex;gap:7px;align-items:center;flex-wrap:wrap;margin-bottom:8px;';
        const title = document.createElement('strong'); title.textContent = 'Trace support'; top.appendChild(title);

        filterSelect = document.createElement('select');
        Object.keys(GROUPS).forEach(function (name) { const option = document.createElement('option'); option.value = name; option.textContent = name === 'all' ? 'Alle events' : name.charAt(0).toUpperCase() + name.slice(1); filterSelect.appendChild(option); });
        top.appendChild(filterSelect);

        searchInput = document.createElement('input'); searchInput.type = 'search'; searchInput.placeholder = 'Søg key / event / tekst'; searchInput.style.minWidth = '190px'; top.appendChild(searchInput);
        top.appendChild(makeButton('Kopiér bundle', copyBundle));
        top.appendChild(makeButton('Download bundle', downloadBundle));

        warning = document.createElement('div'); warning.style.cssText = 'font-size:12px;margin:4px 0;';
        preview = document.createElement('pre'); preview.style.cssText = 'margin:6px 0 0;max-height:180px;overflow:auto;white-space:pre-wrap;font:11px/1.35 monospace;background:#f6f7f7;padding:7px;';
        dock.appendChild(top); dock.appendChild(warning); dock.appendChild(preview); document.body.appendChild(dock);
        filterSelect.addEventListener('change', refresh);
        searchInput.addEventListener('input', refresh);
    }

    function refresh() {
        if (!api) { return; }
        detectStart();
        installIndicator();
        installDock();
        const logging = isLogging();
        indicator.textContent = logging ? '● TRACE OPTAGER' : '○ TRACE STOPPET';
        indicator.style.background = logging ? '#fcf0f1' : '#f6f7f7';
        indicator.style.borderColor = logging ? '#d63638' : '#8c8f94';
        indicator.style.color = logging ? '#b32d2e' : '#50575e';

        const all = eventList();
        const filtered = filteredEvents();
        const remaining = Math.max(0, MAX_BASE_EVENTS - all.length);
        warning.textContent = all.length >= 2000
            ? 'Ringbuffer nær grænsen: ' + all.length + '/' + MAX_BASE_EVENTS + '. Ældre events roteres snart ud.'
            : all.length + ' events · ' + remaining + ' pladser før rotation · redaction QA ' + (redactionSelfTest() ? 'PASS' : 'FAIL');
        warning.style.color = all.length >= 2000 ? '#b32d2e' : '#50575e';
        preview.textContent = filtered.slice(-35).map(shortLine).join('\n') || 'Ingen events matcher filteret.';
    }

    function installCriticalErrors() {
        window.addEventListener('error', function (event) {
            record('CRITICAL_JS_ERROR', {
                message: text(event.message, 500),
                file: text(event.filename, 300),
                line: event.lineno || 0,
                column: event.colno || 0,
                stack: text(event.error && event.error.stack, 1200)
            }, true);
        }, true);
        window.addEventListener('unhandledrejection', function (event) {
            const reason = event.reason || '';
            record('CRITICAL_PROMISE_REJECTION', {
                reason: text(reason && reason.message ? reason.message : reason, 600),
                stack: text(reason && reason.stack, 1200)
            }, true);
        });
    }

    function install() {
        api = baseApi();
        if (!api) { setTimeout(install, 80); return; }
        installCriticalErrors();
        installIndicator();
        installDock();
        record('TRACE_TOOLS_READY', { version: VERSION, redactionSelfTest: redactionSelfTest() }, true);
        refresh();
        refreshTimer = window.setInterval(refresh, 350);
    }

    window.__h18UltimateDesignerTraceToolsV0879 = {
        version: VERSION,
        supportBundle: supportBundle,
        redactionSelfTest: redactionSelfTest,
        refresh: refresh
    };

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); } else { install(); }
    window.addEventListener('beforeunload', function () { if (refreshTimer) { clearInterval(refreshTimer); } });
}());
