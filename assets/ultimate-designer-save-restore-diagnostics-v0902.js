(function () {
    'use strict';

    if (window.__h18SaveRestoreDiagnosticsV0902) { return; }

    const VERSION = '0.9.2';
    const CFG = window.H18SaveRestoreDiagnosticsV0902 || {};
    const PAGE_SLUG = String(CFG.pageSlug || '').trim();
    const RETURN_KEY = 'h18-v0902-restore-return';

    function cleanKey(value) {
        return String(value == null ? '' : value).trim().toLowerCase().replace(/[^a-z0-9._-]/g, '').slice(0, 100);
    }

    function traceApi() {
        return window.__h18UltimateDesignerTraceV0876 || null;
    }

    function liveApi() {
        return window.__h18LiveDiagnosticsV0888 || null;
    }

    function layoutApi() {
        return window.__h18LayoutEngineV0900 || null;
    }

    function physicalApi() {
        return window.__h18PhysicalCanvasV0901 || null;
    }

    function activeSession() {
        const api = traceApi();
        let events = [];
        try { events = api && typeof api.events === 'function' ? api.events() : []; } catch (ignore) {}
        for (let i = events.length - 1; i >= 0; i -= 1) {
            const session = cleanKey(events[i] && events[i].session || '');
            if (session) { return session; }
        }
        return '';
    }

    function structuralState() {
        const layout = layoutApi();
        const physical = physicalApi();
        let snapshot = null;
        try { snapshot = layout && typeof layout.snapshot === 'function' ? layout.snapshot() : null; } catch (ignore) {}
        const sections = snapshot && Array.isArray(snapshot.sections) ? snapshot.sections : [];
        return {
            pageSlug: PAGE_SLUG,
            sectionCount: sections.length,
            sections: sections.slice(0, 150).map(function (section) {
                const key = cleanKey(section && section.key || '');
                let geometry = null;
                try {
                    geometry = physical && typeof physical.geometryForKey === 'function'
                        ? physical.geometryForKey(key)
                        : null;
                } catch (ignore) {}
                return {
                    key: key,
                    type: cleanKey(section && section.type || ''),
                    parentKey: cleanKey(section && section.parentKey || ''),
                    order: Number(section && section.order || 0),
                    removed: Boolean(section && section.removed),
                    span: section && section.span ? section.span : {},
                    stack: section && section.stack ? section.stack : {},
                    geometry: geometry || {}
                };
            })
        };
    }

    function record(type, detail) {
        const api = traceApi();
        if (!api || typeof api.record !== 'function') { return false; }
        try {
            api.record(type, document.activeElement, detail || {}, { force: true });
            return true;
        } catch (ignore) {
            return false;
        }
    }

    function flushSoon() {
        const live = liveApi();
        if (!live || typeof live.flush !== 'function') { return; }
        window.setTimeout(function () {
            try { live.flush(); } catch (ignore) {}
        }, 10);
    }

    function ensureSessionField(form) {
        const session = activeSession();
        if (!form || !session) { return; }
        let field = form.querySelector('input[name="h18_diag_session"]');
        if (!field) {
            field = document.createElement('input');
            field.type = 'hidden';
            field.name = 'h18_diag_session';
            form.appendChild(field);
        }
        field.value = session;
    }

    function restoreMode(form) {
        const action = form && form.querySelector('input[name="action"]');
        const value = String(action && action.value || '');
        if (value === 'h18_ud_restore_page_version_original') { return 'original'; }
        if (value === 'h18_ud_restore_page_version_copy') { return 'copy'; }
        return '';
    }

    function installSaveTrace() {
        const form = document.getElementById('h18-page-editor-form');
        if (!form) { return; }
        form.addEventListener('submit', function () {
            ensureSessionField(form);
            record('DIAG_CLIENT_SAVE_INTENT_V0902', {
                version: VERSION,
                state: structuralState()
            });
            flushSoon();
        }, true);
    }

    function installRestoreTrace() {
        document.addEventListener('submit', function (event) {
            const form = event.target;
            if (!(form instanceof HTMLFormElement)) { return; }
            const mode = restoreMode(form);
            if (!mode) { return; }

            ensureSessionField(form);
            const versionField = form.querySelector('input[name="version"]');
            const slugField = form.querySelector('input[name="page_slug"]');
            const marker = {
                mode: mode,
                version: Math.max(0, parseInt(versionField && versionField.value || '0', 10) || 0),
                pageSlug: String(slugField && slugField.value || PAGE_SLUG).trim(),
                startedAt: Date.now()
            };

            record('DIAG_CLIENT_RESTORE_INTENT_V0902', {
                version: VERSION,
                mode: marker.mode,
                targetVersion: marker.version,
                pageSlug: marker.pageSlug,
                state: structuralState()
            });
            try { window.sessionStorage.setItem(RETURN_KEY, JSON.stringify(marker)); } catch (ignore) {}
            flushSoon();
        }, true);
    }

    function restoreReturnMarker() {
        let marker = null;
        try {
            const raw = window.sessionStorage.getItem(RETURN_KEY);
            marker = raw ? JSON.parse(raw) : null;
        } catch (ignore) {}
        if (!marker || typeof marker !== 'object') { return; }

        const age = Date.now() - Number(marker.startedAt || 0);
        if (age < 0 || age > 10 * 60 * 1000) {
            try { window.sessionStorage.removeItem(RETURN_KEY); } catch (ignore) {}
            return;
        }
        if (marker.pageSlug && PAGE_SLUG && String(marker.pageSlug) !== PAGE_SLUG) { return; }

        const params = new URLSearchParams(window.location.search || '');
        record('DIAG_CLIENT_RESTORE_RETURN_V0902', {
            version: VERSION,
            mode: String(marker.mode || ''),
            targetVersion: Number(marker.version || 0),
            pageSlug: PAGE_SLUG,
            restoreStatus: cleanKey(params.get('h18_version_restore_status') || ''),
            elapsedMs: age,
            state: structuralState()
        });
        try { window.sessionStorage.removeItem(RETURN_KEY); } catch (ignore) {}
        flushSoon();
    }

    function install() {
        if (!traceApi()) {
            window.setTimeout(install, 80);
            return;
        }
        installSaveTrace();
        installRestoreTrace();
        window.setTimeout(restoreReturnMarker, 150);
        record('DIAG_SAVE_RESTORE_BOOT_V0902', {
            version: VERSION,
            pageSlug: PAGE_SLUG,
            privacy: 'structural-only'
        });
        flushSoon();
    }

    window.__h18SaveRestoreDiagnosticsV0902 = {
        version: VERSION,
        snapshot: structuralState,
        session: activeSession
    };

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', install, { once: true });
    } else {
        install();
    }
}());
