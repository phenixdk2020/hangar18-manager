(function () {
    'use strict';

    if (window.__h18LiveDiagnosticsV0888) { return; }

    const VERSION = '0.8.88';
    const config = window.H18LiveDiagnosticsV0888 || {};
    const ajaxUrl = String(config.ajaxUrl || '').trim();
    const ajaxAction = String(config.action || 'h18_diag_append').trim();
    const nonce = String(config.nonce || '').trim();
    const shareUrl = String(config.shareUrl || '').trim();
    const pageSlug = String(config.pageSlug || '').trim();
    const maxBatch = Math.max(10, Math.min(120, parseInt(config.maxBatch, 10) || 80));

    let api = null;
    let lastSeq = 0;
    let activeSession = '';
    let timer = 0;
    let inFlight = false;
    let pendingFlush = false;
    let installedUi = false;

    function traceApi() {
        return window.__h18UltimateDesignerTraceV0876 || null;
    }

    function text(value, max) {
        let result = '';
        try { result = value == null ? '' : String(value); } catch (ignore) { result = ''; }
        result = result.replace(/\s+/g, ' ').trim();
        const limit = max || 300;
        return result.length > limit ? result.slice(0, limit) + '…' : result;
    }

    function sensitiveKey(key) {
        return /pass(word)?|secret|token|nonce|authorization|api[-_ ]?key|cookie|bearer|credential|csrf|sessionid/i.test(String(key || ''));
    }

    function privateUiKey(key) {
        return /^(value|text|content|html|markup|body)$/i.test(String(key || ''));
    }

    function sanitize(value, key, depth) {
        const level = depth || 0;
        if (level > 6) { return '[depth]'; }
        if (sensitiveKey(key)) { return '[REDACTED]'; }
        if (privateUiKey(key)) {
            if (typeof value === 'string') { return '[REDACTED_UI length=' + value.length + ']'; }
            return '[REDACTED_UI]';
        }
        if (Array.isArray(value)) {
            return value.slice(0, 250).map(function (item) { return sanitize(item, '', level + 1); });
        }
        if (value && typeof value === 'object') {
            const out = {};
            Object.keys(value).slice(0, 250).forEach(function (name) {
                out[name] = sanitize(value[name], name, level + 1);
            });
            return out;
        }
        if (typeof value === 'string') {
            let result = value
                .replace(/(Bearer\s+)[A-Za-z0-9._~+\/-]+/gi, '$1[REDACTED]')
                .replace(/((?:token|nonce|password|secret|cookie|authorization)\s*[=:]\s*)[^\s,;]+/gi, '$1[REDACTED]');
            if (/^https?:\/\//i.test(result)) {
                try {
                    const url = new URL(result);
                    const safe = new URL(url.origin + url.pathname);
                    ['page', 'page_slug', 'post', 'action'].forEach(function (name) {
                        if (url.searchParams.has(name)) { safe.searchParams.set(name, text(url.searchParams.get(name), 100)); }
                    });
                    result = safe.toString();
                } catch (ignore) {}
            }
            return text(result, 4000);
        }
        return value;
    }

    function sessionFromEvents(events) {
        for (let i = events.length - 1; i >= 0; i -= 1) {
            const session = text(events[i] && events[i].session, 100).toLowerCase().replace(/[^a-z0-9._-]/g, '');
            if (session) { return session; }
        }
        return '';
    }

    function fallbackSession() {
        return 'diag-' + Date.now().toString(36) + '-' + Math.random().toString(36).slice(2, 10);
    }

    function ensureSession(events) {
        const next = sessionFromEvents(events || []) || activeSession || fallbackSession();
        if (next !== activeSession) {
            activeSession = next;
            lastSeq = 0;
        }
        ensureHiddenSession();
        return activeSession;
    }

    function ensureHiddenSession() {
        const form = document.getElementById('h18-page-editor-form');
        if (!form || !activeSession) { return; }
        let hidden = form.querySelector('input[name="h18_diag_session"]');
        if (!hidden) {
            hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = 'h18_diag_session';
            form.appendChild(hidden);
        }
        hidden.value = activeSession;
    }

    function controlValue(row, fieldName, fallback) {
        if (!row) { return fallback; }
        const selector = '[name$="[' + fieldName + ']"]';
        let node = row.querySelector(selector);
        if (!node && row.classList.contains('is-selected')) {
            const inspector = document.getElementById('h18-page-inspector-target');
            node = inspector ? inspector.querySelector(selector) : null;
        }
        if (!node) { return fallback; }
        if (node.type === 'checkbox') { return Boolean(node.checked); }
        return node.value === '' ? fallback : node.value;
    }

    function numberValue(row, fieldName, fallback) {
        const parsed = parseInt(controlValue(row, fieldName, fallback), 10);
        return Number.isFinite(parsed) ? parsed : fallback;
    }

    function rowKey(row) {
        const node = row && row.querySelector('.h18-page-section-key');
        return text(node && node.value, 100).toLowerCase().replace(/[^a-z0-9._-]/g, '');
    }

    function spanState(key) {
        const resize = window.__h18LegoResizeV0841;
        if (!resize || typeof resize.stateForKey !== 'function' || !key) { return {}; }
        try { return sanitize(resize.stateForKey(key) || {}, '', 0); } catch (ignore) { return {}; }
    }

    function stackState(key) {
        const stack = window.__h18LegoFixesV0851;
        if (!stack || typeof stack.stackStateForKey !== 'function' || !key) { return {}; }
        try { return sanitize(stack.stackStateForKey(key) || {}, '', 0); } catch (ignore) { return {}; }
    }

    function snapshotSections(reason) {
        const host = document.getElementById('h18-page-sections-sortable');
        const rows = host ? Array.from(host.querySelectorAll(':scope > .h18-page-section-row')) : [];
        return {
            reason: text(reason, 80),
            pageSlug: pageSlug,
            canvasDevice: text((document.querySelector('.h18-builder-canvas') || {}).getAttribute && document.querySelector('.h18-builder-canvas').getAttribute('data-canvas-device'), 20),
            sectionCount: rows.length,
            sections: rows.slice(0, 200).map(function (row, index) {
                const key = rowKey(row);
                const parent = text(controlValue(row, 'LayoutParentKey', ''), 100).toLowerCase().replace(/[^a-z0-9._-]/g, '');
                const type = text(row.getAttribute('data-section-type') || controlValue(row, 'Type', ''), 50).toLowerCase();
                const preview = row.querySelector(':scope > .h18-canvas-preview');
                const rect = preview ? preview.getBoundingClientRect() : null;
                return {
                    index: index,
                    key: key,
                    type: type,
                    parentKey: parent,
                    selected: row.classList.contains('is-selected'),
                    span: spanState(key),
                    stack: stackState(key),
                    element: {
                        width: numberValue(row, 'ElementWidthPercent', 100),
                        tabletWidth: numberValue(row, 'TabletWidthPercent', -1),
                        mobileWidth: numberValue(row, 'MobileWidthPercent', -1),
                        minHeight: numberValue(row, 'ElementMinHeightPx', 0),
                        tabletMinHeight: numberValue(row, 'TabletMinHeightPx', 0),
                        mobileMinHeight: numberValue(row, 'MobileMinHeightPx', 0)
                    },
                    image: type === 'image' || type === 'text_image' ? {
                        mediaId: numberValue(row, 'MediaId', 0),
                        aspect: text(controlValue(row, 'ImageAspectRatio', 'Auto'), 30),
                        fit: text(controlValue(row, 'ImageFit', 'Cover'), 30),
                        height: numberValue(row, 'ImageHeightPx', 0),
                        mobileHeight: numberValue(row, 'MobileImageHeightPx', 0),
                        width: numberValue(row, 'ImageWidthPercent', 100),
                        mobileWidth: numberValue(row, 'MobileImageWidthPercent', 100),
                        maxWidth: numberValue(row, 'ImageMaxWidthPx', 0),
                        aspectLocked: Boolean(controlValue(row, 'ImageAspectLocked', false))
                    } : null,
                    canvasRect: rect ? {
                        width: Math.round(rect.width),
                        height: Math.round(rect.height),
                        left: Math.round(rect.left),
                        top: Math.round(rect.top)
                    } : null
                };
            })
        };
    }

    function customEntry(type, detail) {
        return {
            seq: 0,
            time: new Date().toISOString(),
            local: new Date().toLocaleTimeString('da-DK', { hour12: false }),
            session: activeSession,
            type: type,
            detail: sanitize(detail || {}, '', 0)
        };
    }

    function formPayload(entries) {
        const data = new URLSearchParams();
        data.set('action', ajaxAction);
        data.set('nonce', nonce);
        data.set('session', activeSession);
        data.set('page_slug', pageSlug);
        data.set('entries_json', JSON.stringify(entries));
        return data;
    }

    function send(entries, useBeacon) {
        if (!ajaxUrl || !nonce || !activeSession || !entries.length) { return Promise.resolve(false); }
        const safeEntries = entries.slice(0, maxBatch).map(function (entry) { return sanitize(entry, '', 0); });
        const body = formPayload(safeEntries);

        if (useBeacon && navigator.sendBeacon) {
            try {
                const blob = new Blob([body.toString()], { type: 'application/x-www-form-urlencoded;charset=UTF-8' });
                return Promise.resolve(navigator.sendBeacon(ajaxUrl, blob));
            } catch (ignore) {}
        }

        return fetch(ajaxUrl, {
            method: 'POST',
            credentials: 'same-origin',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
            body: body.toString(),
            cache: 'no-store',
            keepalive: true
        }).then(function (response) { return response.ok; }).catch(function () { return false; });
    }

    function eventList() {
        try { return api && typeof api.events === 'function' ? api.events() : []; } catch (ignore) { return []; }
    }

    function isLogging() {
        try { return Boolean(api && typeof api.isLogging === 'function' && api.isLogging()); } catch (ignore) { return false; }
    }

    function newTraceEvents(events) {
        return events.filter(function (entry) {
            const seq = Number(entry && entry.seq) || 0;
            return seq > lastSeq;
        }).slice(0, maxBatch);
    }

    function flush(force, useBeacon) {
        if (!api || inFlight) {
            pendingFlush = Boolean(force || pendingFlush);
            return;
        }
        const events = eventList();
        ensureSession(events);
        const fresh = newTraceEvents(events);
        if (!fresh.length || (!force && !isLogging())) { return; }

        const maxSeq = fresh.reduce(function (max, entry) { return Math.max(max, Number(entry.seq) || 0); }, lastSeq);
        inFlight = true;
        send(fresh, Boolean(useBeacon)).then(function (ok) {
            if (ok) { lastSeq = maxSeq; }
        }).finally(function () {
            inFlight = false;
            if (pendingFlush) {
                pendingFlush = false;
                window.setTimeout(function () { flush(true, false); }, 20);
            }
        });
    }

    function record(type, detail, force) {
        if (!api || typeof api.record !== 'function') { return; }
        try { api.record(type, document.activeElement, sanitize(detail || {}, '', 0), force ? { force: true } : undefined); } catch (ignore) {}
    }

    function installSupportUi() {
        if (installedUi || !shareUrl) { return; }
        const dock = document.getElementById('h18-trace-tools-v0879');
        const top = dock ? dock.firstElementChild : null;
        if (!top) { return; }
        installedUi = true;

        const status = document.createElement('span');
        status.id = 'h18-live-diagnostics-status-v0888';
        status.textContent = 'Site-log klar';
        status.style.cssText = 'font-size:12px;font-weight:700;color:#008a20;';
        top.appendChild(status);

        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'button button-small';
        button.textContent = 'Kopiér diagnose-link';
        button.addEventListener('click', function (event) {
            event.preventDefault();
            event.stopPropagation();
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(shareUrl).then(function () {
                    const old = button.textContent;
                    button.textContent = 'Link kopieret';
                    window.setTimeout(function () { button.textContent = old; }, 1400);
                    record('DIAG_SUPPORT_LINK_COPIED', { ready: true }, true);
                    flush(true, false);
                });
            }
        });
        top.appendChild(button);
    }

    function installSaveCapture() {
        const form = document.getElementById('h18-page-editor-form');
        if (!form) { return; }
        form.addEventListener('submit', function () {
            const events = eventList();
            ensureSession(events);
            const entry = customEntry('DIAG_CLIENT_BEFORE_SAVE', snapshotSections('before-save'));
            send([entry], true);
            flush(true, true);
        }, true);
    }

    function installPreviewCapture() {
        document.addEventListener('click', function (event) {
            const target = event.target && event.target.closest ? event.target.closest('#h18-unsaved-preview-open,[data-h18-preview-device]') : null;
            if (!target) { return; }
            record('DIAG_PREVIEW_SNAPSHOT', snapshotSections('preview-click'), true);
            window.setTimeout(function () { flush(true, false); }, 20);
        }, true);
    }

    function install() {
        api = traceApi();
        if (!api) {
            window.setTimeout(install, 80);
            return;
        }
        ensureSession(eventList());
        installSaveCapture();
        installPreviewCapture();
        record('DIAG_SITE_STORE_READY', {
            version: VERSION,
            pageSlug: pageSlug,
            supportEndpoint: 'configured',
            privacy: 'ui-values-and-sensitive-fields-redacted'
        }, true);
        record('DIAG_CLIENT_RELOAD_SNAPSHOT', snapshotSections('page-load'), true);
        flush(true, false);

        timer = window.setInterval(function () {
            installSupportUi();
            flush(false, false);
        }, 1200);
        [100, 400, 900].forEach(function (delay) { window.setTimeout(installSupportUi, delay); });
    }

    window.addEventListener('pagehide', function () {
        if (timer) { clearInterval(timer); }
        flush(true, true);
    });
    document.addEventListener('visibilitychange', function () {
        if (document.visibilityState === 'hidden') { flush(true, true); }
    });

    window.__h18LiveDiagnosticsV0888 = {
        version: VERSION,
        snapshot: snapshotSections,
        flush: function () { flush(true, false); },
        supportUrl: function () { return shareUrl; }
    };

    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
