(function () {
    'use strict';

    const config = window.H18UltimateDesignerTraceSettingsV0876 || {};
    const storageKey = String(config.storageKey || 'h18.ultimate-designer.trace.v0876');
    const summary = document.getElementById('h18-trace-browser-summary');
    const exportButton = document.getElementById('h18-trace-export-json');
    const clearButton = document.getElementById('h18-trace-clear-browser');

    function read() {
        try {
            const raw = localStorage.getItem(storageKey);
            if (!raw) { return null; }
            const parsed = JSON.parse(raw);
            return parsed && typeof parsed === 'object' ? parsed : null;
        } catch (ignore) {
            return null;
        }
    }

    function update() {
        if (!summary) { return; }
        const data = read();
        if (!data) {
            summary.innerHTML = '<strong>Browser-log:</strong> ingen gemt trace.';
            if (exportButton) { exportButton.disabled = true; }
            return;
        }

        const count = Array.isArray(data.events) ? data.events.length : 0;
        const logging = data.logging === true ? 'TIL' : 'FRA';
        const session = String(data.sessionId || '-');
        summary.innerHTML = '<strong>Browser-log:</strong> ' + count + ' events · optagelse ' + logging + ' · session <code>' + session.replace(/[&<>"']/g, '') + '</code>';
        if (exportButton) { exportButton.disabled = false; }
    }

    function downloadJson() {
        const data = read();
        if (!data) { return; }
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'hangar18-trace-' + String(data.sessionId || 'browser') + '.json';
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
    }

    if (exportButton) {
        exportButton.addEventListener('click', function () { downloadJson(); });
    }

    if (clearButton) {
        clearButton.addEventListener('click', function () {
            if (!window.confirm('Nulstil den gemte browser-trace?')) { return; }
            try { localStorage.removeItem(storageKey); } catch (ignore) { /* ignore */ }
            update();
        });
    }

    update();
}());
