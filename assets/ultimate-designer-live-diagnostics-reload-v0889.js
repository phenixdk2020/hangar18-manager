(function () {
    'use strict';

    if (window.__h18LiveDiagnosticsReloadV0889) { return; }

    const VERSION = '0.8.89';
    const config = window.H18LiveDiagnosticsV0888 || {};
    const ajaxUrl = String(config.ajaxUrl || '');
    const action = String(config.action || 'h18_diag_append');
    const nonce = String(config.nonce || '');
    const pageSlug = String(config.pageSlug || '');
    let lastReloadSignature = '';

    function session() {
        const field = document.querySelector('#h18-page-editor-form input[name="h18_diag_session"]');
        return String(field && field.value || '').trim().toLowerCase().replace(/[^a-z0-9._-]/g, '').slice(0, 100);
    }
    function api() { return window.__h18LiveDiagnosticsV0888 || null; }
    function snapshot(reason) {
        const runtime = api();
        if (!runtime || typeof runtime.snapshot !== 'function') { return null; }
        try {
            const data = runtime.snapshot(reason);
            if (data && typeof data === 'object') { data.diagVersion = VERSION; }
            return data;
        } catch (ignore) { return null; }
    }
    function entry(type, detail) {
        return { seq: 0, time: new Date().toISOString(), local: new Date().toLocaleTimeString('da-DK', { hour12: false }), session: session(), type: type, detail: detail || {} };
    }
    function body(entries) {
        const data = new URLSearchParams();
        data.set('action', action);
        data.set('nonce', nonce);
        data.set('session', session());
        data.set('page_slug', pageSlug);
        data.set('entries_json', JSON.stringify(entries));
        return data;
    }
    function send(entries, beacon) {
        if (!ajaxUrl || !nonce || !session() || !entries || !entries.length) { return false; }
        const payload = body(entries);
        if (beacon && navigator.sendBeacon) {
            try {
                return navigator.sendBeacon(ajaxUrl, new Blob([payload.toString()], { type: 'application/x-www-form-urlencoded;charset=UTF-8' }));
            } catch (ignore) {}
        }
        fetch(ajaxUrl, {
            method: 'POST', credentials: 'same-origin', cache: 'no-store', keepalive: true,
            headers: { 'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8' },
            body: payload.toString()
        }).catch(function () {});
        return true;
    }
    function signature(data) {
        if (!data || !Array.isArray(data.sections)) { return ''; }
        return JSON.stringify(data.sections.map(function (section) {
            return [
                section.key || '', section.type || '', section.parentKey || '',
                section.span || {}, section.stack || {}, section.element || {}, section.image || null
            ];
        }));
    }
    function sendReload(reason) {
        const data = snapshot(reason || 'reload-direct');
        if (!data || !Array.isArray(data.sections) || !data.sections.length) { return false; }
        const sig = signature(data);
        if (!sig || sig === lastReloadSignature) { return false; }
        lastReloadSignature = sig;
        return send([entry('DIAG_CLIENT_RELOAD_DIRECT_V0889', data)], false);
    }
    function parseGenerated(form, prefix) {
        const result = {};
        const selector = 'input[name^="' + prefix + '["]';
        Array.from(form.querySelectorAll(selector)).forEach(function (node) {
            const match = String(node.name || '').match(new RegExp('^' + prefix.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\[(\\d+)\\]\\[(SectionKey|StateJson)\\]$'));
            if (!match) { return; }
            const index = match[1];
            if (!result[index]) { result[index] = { sectionKey: '', state: {} }; }
            if (match[2] === 'SectionKey') {
                result[index].sectionKey = String(node.value || '').trim().toLowerCase().replace(/[^a-z0-9._-]/g, '').slice(0, 100);
            } else {
                try {
                    const parsed = JSON.parse(String(node.value || '{}'));
                    result[index].state = parsed && typeof parsed === 'object' ? parsed : {};
                } catch (ignore) { result[index].state = { parseError: true }; }
            }
        });
        return Object.keys(result).sort(function (a, b) { return Number(a) - Number(b); }).map(function (index) { return result[index]; });
    }
    function savePayloadSnapshot(form) {
        return {
            pageSlug: pageSlug,
            sectionCount: form.querySelectorAll('#h18-page-sections-sortable > .h18-page-section-row:not(.h18-page-section-removed)').length,
            spanPayload: parseGenerated(form, 'h18_lego_layout_span'),
            stackPayload: parseGenerated(form, 'h18_lego_stack_v0851'),
            canonical: snapshot('submit-after-generated-payload')
        };
    }
    function installSaveAudit() {
        const form = document.getElementById('h18-page-editor-form');
        if (!form || form.getAttribute('data-h18-v0889-save-audit') === '1') { return; }
        form.setAttribute('data-h18-v0889-save-audit', '1');
        /* Bubble/target listener is intentionally registered late. The v0.8.41
         * jQuery submit handler has already generated span hidden inputs by the
         * time this listener runs. No submit is prevented or modified here. */
        form.addEventListener('submit', function () {
            try { send([entry('DIAG_CLIENT_GENERATED_SAVE_PAYLOAD_V0889', savePayloadSnapshot(form))], true); }
            catch (ignore) {}
        }, false);
    }
    function install() {
        if (!api() || !session()) { window.setTimeout(install, 100); return; }
        installSaveAudit();
        [350, 800, 1500, 2600].forEach(function (delay) {
            window.setTimeout(function () { sendReload('page-load-stable-' + delay); }, delay);
        });
        document.documentElement.setAttribute('data-h18-live-diagnostics-reload', VERSION);
    }

    window.__h18LiveDiagnosticsReloadV0889 = { version: VERSION, snapshot: snapshot, sendReload: sendReload };
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
