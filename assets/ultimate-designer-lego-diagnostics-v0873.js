(function () {
    'use strict';

    if (window.__h18LegoDiagnosticsV0873) { return; }

    const VERSION = '0.8.73';
    const LOG_LIMIT = 28;
    const log = [];
    let lastSignature = '';
    let panel = null;
    let pre = null;

    function now() {
        const d = new Date();
        return d.toLocaleTimeString('da-DK', { hour12: false }) + '.' + String(d.getMilliseconds()).padStart(3, '0');
    }

    function esc(value) {
        return String(value == null ? '' : value);
    }

    function keyOfRow(row) {
        if (!row) { return ''; }
        const direct = row.querySelector('.h18-page-section-key');
        if (direct && direct.value) { return String(direct.value); }
        return String(row.getAttribute('data-key') || '');
    }

    function selectionState() {
        const api = window.__h18LegoInspectorOnlyV0847;
        const active = api && typeof api.activeSelection === 'function' ? api.activeSelection() : { key: '', mode: '' };
        const key = esc(active && active.key).trim();
        const mode = esc(active && active.mode).trim();
        const nested = Array.from(document.querySelectorAll('.h18-v0811-auto-box[data-h18-v0811-row],.h18-v0811-child-card[data-h18-v0811-child]'));
        const matching = key ? nested.filter(function (node) {
            return esc(node.getAttribute('data-h18-v0811-row') || node.getAttribute('data-h18-v0811-child')).trim() === key;
        }) : [];
        const selected = nested.filter(function (node) { return node.classList.contains('is-h18-v0848-selected-element'); });
        const selectedMatching = matching.filter(function (node) { return node.classList.contains('is-h18-v0848-selected-element'); });
        const selectedRow = document.querySelector('#h18-page-sections-sortable > .h18-page-section-row.is-selected');
        let outline = '';
        let visible = 0;
        if (matching[0] && window.getComputedStyle) {
            const style = window.getComputedStyle(matching[0]);
            outline = [style.outlineStyle, style.outlineWidth, style.outlineColor].join(' ');
            visible = matching.filter(function (node) {
                const r = node.getBoundingClientRect();
                const s = window.getComputedStyle(node);
                return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden';
            }).length;
        }
        return {
            key: key,
            mode: mode,
            matching: matching.length,
            visibleMatching: visible,
            selectedTotal: selected.length,
            selectedMatching: selectedMatching.length,
            nativeRowKey: keyOfRow(selectedRow),
            outline: outline,
            runtime: esc(document.documentElement.getAttribute('data-h18-lego-selection-marker'))
        };
    }

    function dropState() {
        const api = window.__h18LegoDropZonesV0838;
        const source = api && typeof api.activeSource === 'function' ? api.activeSource() : {};
        const overlays = document.querySelectorAll('.h18-v0838-drop-overlay');
        const boxOverlays = document.querySelectorAll('.h18-v0838-drop-overlay[data-h18-v0871-target-box="1"]');
        const inside = document.querySelectorAll('.h18-v0838-drop-zone.is-inside');
        const insideVisible = Array.from(inside).filter(function (node) {
            const r = node.getBoundingClientRect();
            const s = window.getComputedStyle(node);
            return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0;
        });
        const active = document.querySelector('.h18-v0838-drop-zone.is-active');
        return {
            sourceKey: esc(source && (source.Key || source.key)),
            sourceType: esc(source && (source.Type || source.type)),
            sourceMode: esc(source && (source.Mode || source.mode)),
            overlays: overlays.length,
            boxOverlays: boxOverlays.length,
            inside: inside.length,
            insideVisible: insideVisible.length,
            active: active ? esc(active.getAttribute('data-h18-v0838-position')) + ':' + esc(active.getAttribute('data-h18-v0838-target')) : '',
            runtime: esc(document.documentElement.getAttribute('data-h18-lego-inside-kasse-zone')),
            lastResult: esc(document.documentElement.getAttribute('data-h18-v0870-last-inside-result') || document.documentElement.getAttribute('data-h18-v0871-last-inside-result') || document.documentElement.getAttribute('data-h18-v0872-last-inside-result'))
        };
    }

    function snapshot(reason) {
        const s = selectionState();
        const d = dropState();
        const signature = JSON.stringify([s.key, s.mode, s.matching, s.selectedMatching, s.selectedTotal, s.nativeRowKey, s.outline, d.sourceKey, d.sourceType, d.overlays, d.boxOverlays, d.inside, d.insideVisible, d.active, d.lastResult]);
        if (reason === 'tick' && signature === lastSignature) { return; }
        lastSignature = signature;
        log.push(now() + ' [' + reason + '] SEL key=' + (s.key || '-') + ' mode=' + (s.mode || '-') + ' match=' + s.matching + '/' + s.visibleMatching + ' red=' + s.selectedMatching + ' allRed=' + s.selectedTotal + ' row=' + (s.nativeRowKey || '-') + ' outline=' + (s.outline || '-') + ' | DROP src=' + (d.sourceKey || '-') + '/' + (d.sourceType || '-') + ' overlays=' + d.overlays + ' box=' + d.boxOverlays + ' inside=' + d.inside + '/' + d.insideVisible + ' active=' + (d.active || '-') + ' result=' + (d.lastResult || '-'));
        while (log.length > LOG_LIMIT) { log.shift(); }
        render();
    }

    function report() {
        const s = selectionState();
        const d = dropState();
        return [
            'Hangar18 LEGO diagnose ' + VERSION,
            'selection-runtime=' + s.runtime,
            'inside-runtime=' + d.runtime,
            'selection: key=' + (s.key || '-') + ' mode=' + (s.mode || '-') + ' matching=' + s.matching + ' visible=' + s.visibleMatching + ' selectedMatching=' + s.selectedMatching + ' selectedTotal=' + s.selectedTotal + ' nativeRow=' + (s.nativeRowKey || '-') + ' outline=' + (s.outline || '-'),
            'drop: source=' + (d.sourceKey || '-') + ' type=' + (d.sourceType || '-') + ' mode=' + (d.sourceMode || '-') + ' overlays=' + d.overlays + ' boxOverlays=' + d.boxOverlays + ' inside=' + d.inside + ' visibleInside=' + d.insideVisible + ' active=' + (d.active || '-') + ' lastResult=' + (d.lastResult || '-'),
            '',
            'Seneste hændelser:',
            log.join('\n')
        ].join('\n');
    }

    function render() {
        if (!pre) { return; }
        pre.textContent = report();
    }

    function installPanel() {
        if (panel || !document.body) { return; }
        panel = document.createElement('aside');
        panel.id = 'h18-lego-diagnostics-v0873';
        panel.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:2147483000;width:min(620px,calc(100vw - 32px));max-height:44vh;overflow:auto;background:#fff;border:2px solid #1d2327;border-radius:8px;box-shadow:0 8px 28px rgba(0,0,0,.28);padding:10px;font:12px/1.35 Consolas,Monaco,monospace;color:#1d2327;';
        const head = document.createElement('div');
        head.style.cssText = 'display:flex;align-items:center;gap:8px;margin-bottom:8px;position:sticky;top:0;background:#fff;padding-bottom:6px;';
        const title = document.createElement('strong');
        title.textContent = 'LEGO diagnose v0.8.73';
        title.style.marginRight = 'auto';
        const copy = document.createElement('button');
        copy.type = 'button';
        copy.className = 'button button-small';
        copy.textContent = 'Kopiér diagnose';
        copy.addEventListener('click', function () {
            const text = report();
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function () { copy.textContent = 'Kopieret'; window.setTimeout(function () { copy.textContent = 'Kopiér diagnose'; }, 1200); });
            } else {
                window.prompt('Kopiér diagnosen:', text);
            }
        });
        const close = document.createElement('button');
        close.type = 'button';
        close.className = 'button button-small';
        close.textContent = 'Skjul';
        close.addEventListener('click', function () { panel.style.display = 'none'; });
        pre = document.createElement('pre');
        pre.style.cssText = 'white-space:pre-wrap;margin:0;user-select:text;';
        head.append(title, copy, close);
        panel.append(head, pre);
        document.body.appendChild(panel);
        snapshot('install');
    }

    document.addEventListener('click', function (event) {
        if (event.target && event.target.closest && event.target.closest('.h18-builder-canvas')) { window.setTimeout(function () { snapshot('canvas-click'); }, 0); }
    }, true);
    document.addEventListener('pointerdown', function (event) {
        if (event.target && event.target.closest && event.target.closest('.h18-builder-canvas')) { window.setTimeout(function () { snapshot('pointerdown'); }, 0); }
    }, true);

    if (window.jQuery) {
        const $ = window.jQuery;
        $('#h18-page-sections-sortable').on('sortstart.h18Diag0873', function () { window.setTimeout(function () { snapshot('sortstart'); }, 30); });
        $('#h18-page-sections-sortable').on('sort.h18Diag0873', function () { snapshot('sort'); });
        $('#h18-page-sections-sortable').on('sortstop.h18Diag0873', function () { window.setTimeout(function () { snapshot('sortstop'); }, 30); });
    }

    if (window.MutationObserver) {
        const root = document.querySelector('.h18-builder-canvas') || document.body;
        if (root) {
            let frame = 0;
            new MutationObserver(function () {
                if (frame) { return; }
                frame = window.requestAnimationFrame(function () { frame = 0; snapshot('mutation'); });
            }).observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'data-h18-v0871-target-box', 'data-h18-v0871-inside-kasse'] });
        }
    }

    window.setInterval(function () { snapshot('tick'); }, 250);
    if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', installPanel, { once: true }); }
    else { installPanel(); }

    document.documentElement.setAttribute('data-h18-lego-diagnostics', VERSION);
    window.__h18LegoDiagnosticsV0873 = { version: VERSION, report: report, snapshot: snapshot };
}());
