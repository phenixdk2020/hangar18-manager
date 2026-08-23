(function () {
    'use strict';

    if (window.__h18LegoDiagnosticsV0873) { return; }

    const VERSION = '0.8.74';
    const ACTION_LIMIT = 28;
    const MUTATION_LIMIT = 6;
    const actions = [];
    const mutations = [];
    let panel = null;
    let pre = null;
    let mutationFrame = 0;
    let dragFrame = 0;
    let dragActive = false;
    let lastDrag = null;

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

    function isVisible(node) {
        if (!node || !window.getComputedStyle) { return false; }
        const r = node.getBoundingClientRect();
        const s = window.getComputedStyle(node);
        return r.width > 0 && r.height > 0 && s.display !== 'none' && s.visibility !== 'hidden' && Number(s.opacity || 1) > 0;
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
        if (matching[0] && window.getComputedStyle) {
            const style = window.getComputedStyle(matching[0]);
            outline = [style.outlineStyle, style.outlineWidth, style.outlineColor].join(' ');
        }
        return {
            key: key,
            mode: mode,
            matching: matching.length,
            visibleMatching: matching.filter(isVisible).length,
            selectedTotal: selected.length,
            selectedMatching: selectedMatching.length,
            nativeRowKey: keyOfRow(selectedRow),
            outline: outline,
            runtime: esc(document.documentElement.getAttribute('data-h18-lego-selection-marker')),
            apiVersion: api ? esc(api.version) : '',
            observer: api && typeof api.observerActive === 'function' ? (api.observerActive() ? 'active' : 'inactive') : 'no-api'
        };
    }

    function dropState() {
        const api = window.__h18LegoDropZonesV0838;
        const source = api && typeof api.activeSource === 'function' ? api.activeSource() : {};
        const overlays = Array.from(document.querySelectorAll('.h18-v0838-drop-overlay'));
        const boxOverlays = overlays.filter(function (node) { return node.getAttribute('data-h18-v0871-target-box') === '1'; });
        const inside = Array.from(document.querySelectorAll('.h18-v0838-drop-zone.is-inside'));
        const insideVisible = inside.filter(isVisible);
        const active = document.querySelector('.h18-v0838-drop-zone.is-active');
        const activeText = active ? esc(active.getAttribute('data-h18-v0838-position')) + ':' + esc(active.getAttribute('data-h18-v0838-target')) : '';
        return {
            sourceKey: esc(source && (source.Key || source.key)),
            sourceType: esc(source && (source.Type || source.type)),
            sourceMode: esc(source && (source.Mode || source.mode)),
            overlays: overlays.length,
            boxOverlays: boxOverlays.length,
            inside: inside.length,
            insideVisible: insideVisible.length,
            active: activeText,
            runtime: esc(document.documentElement.getAttribute('data-h18-lego-inside-kasse-zone')),
            dropApi: api ? esc(api.capabilityVersion || api.version) : '',
            lastResult: esc(document.documentElement.getAttribute('data-h18-v0870-last-inside-result') || document.documentElement.getAttribute('data-h18-v0871-last-inside-result') || document.documentElement.getAttribute('data-h18-v0872-last-inside-result'))
        };
    }

    function line(reason, s, d) {
        return now() + ' [' + reason + '] SEL rt=' + (s.runtime || '-') + '/' + (s.apiVersion || '-') + ' obs=' + s.observer + ' key=' + (s.key || '-') + ' mode=' + (s.mode || '-') + ' match=' + s.matching + '/' + s.visibleMatching + ' red=' + s.selectedMatching + ' allRed=' + s.selectedTotal + ' row=' + (s.nativeRowKey || '-') + ' outline=' + (s.outline || '-') + ' | DROP rt=' + (d.runtime || '-') + '/' + (d.dropApi || '-') + ' src=' + (d.sourceKey || '-') + '/' + (d.sourceType || '-') + '/' + (d.sourceMode || '-') + ' overlays=' + d.overlays + ' box=' + d.boxOverlays + ' inside=' + d.inside + '/' + d.insideVisible + ' active=' + (d.active || '-') + ' result=' + (d.lastResult || '-');
    }

    function updateLastDrag(reason, d) {
        if (!dragActive && reason !== 'sortstop') { return; }
        if (!lastDrag) {
            lastDrag = {
                started: now(), sourceKey: d.sourceKey, sourceType: d.sourceType,
                peakOverlays: 0, peakBoxOverlays: 0, peakInside: 0, peakVisibleInside: 0,
                activeSeen: [], stop: '', result: ''
            };
        }
        if (!lastDrag.sourceKey && d.sourceKey) { lastDrag.sourceKey = d.sourceKey; }
        if (!lastDrag.sourceType && d.sourceType) { lastDrag.sourceType = d.sourceType; }
        lastDrag.peakOverlays = Math.max(lastDrag.peakOverlays, d.overlays);
        lastDrag.peakBoxOverlays = Math.max(lastDrag.peakBoxOverlays, d.boxOverlays);
        lastDrag.peakInside = Math.max(lastDrag.peakInside, d.inside);
        lastDrag.peakVisibleInside = Math.max(lastDrag.peakVisibleInside, d.insideVisible);
        if (d.active && lastDrag.activeSeen.indexOf(d.active) === -1) { lastDrag.activeSeen.push(d.active); }
        if (reason === 'sortstop') {
            lastDrag.stop = now();
            lastDrag.result = d.lastResult;
        }
    }

    function snapshot(reason, kind) {
        const s = selectionState();
        const d = dropState();
        updateLastDrag(reason, d);
        const entry = line(reason, s, d);
        const target = kind === 'mutation' ? mutations : actions;
        target.push(entry);
        const limit = kind === 'mutation' ? MUTATION_LIMIT : ACTION_LIMIT;
        while (target.length > limit) { target.shift(); }
        render();
        return { selection: s, drop: d };
    }

    function dragSummary() {
        if (!lastDrag) { return 'last-drag: ingen registreret drag endnu'; }
        return 'last-drag: source=' + (lastDrag.sourceKey || '-') + '/' + (lastDrag.sourceType || '-') + ' peakOverlays=' + lastDrag.peakOverlays + ' peakBox=' + lastDrag.peakBoxOverlays + ' peakInside=' + lastDrag.peakInside + '/' + lastDrag.peakVisibleInside + ' activeSeen=' + (lastDrag.activeSeen.length ? lastDrag.activeSeen.join(',') : '-') + ' result=' + (lastDrag.result || '-');
    }

    function report() {
        const s = selectionState();
        const d = dropState();
        return [
            'Hangar18 LEGO diagnose ' + VERSION,
            'selection-runtime=' + (s.runtime || '-') + ' api=' + (s.apiVersion || '-') + ' observer=' + s.observer,
            'inside-runtime=' + (d.runtime || '-') + ' drop-api=' + (d.dropApi || '-'),
            'selection: key=' + (s.key || '-') + ' mode=' + (s.mode || '-') + ' matching=' + s.matching + ' visible=' + s.visibleMatching + ' selectedMatching=' + s.selectedMatching + ' selectedTotal=' + s.selectedTotal + ' nativeRow=' + (s.nativeRowKey || '-') + ' outline=' + (s.outline || '-'),
            'drop-now: source=' + (d.sourceKey || '-') + ' type=' + (d.sourceType || '-') + ' mode=' + (d.sourceMode || '-') + ' overlays=' + d.overlays + ' boxOverlays=' + d.boxOverlays + ' inside=' + d.inside + ' visibleInside=' + d.insideVisible + ' active=' + (d.active || '-') + ' lastResult=' + (d.lastResult || '-'),
            dragSummary(),
            '',
            'Handlinger:',
            actions.join('\n'),
            '',
            'Seneste mutationer (begrænset):',
            mutations.join('\n')
        ].join('\n');
    }

    function render() {
        if (pre) { pre.textContent = report(); }
    }

    function installPanel() {
        if (panel || !document.body) { return; }
        panel = document.createElement('aside');
        panel.id = 'h18-lego-diagnostics-v0873';
        panel.style.cssText = 'position:fixed;right:16px;bottom:16px;z-index:2147483000;width:min(680px,calc(100vw - 32px));max-height:48vh;overflow:auto;background:#fff;border:2px solid #1d2327;border-radius:8px;box-shadow:0 8px 28px rgba(0,0,0,.28);padding:10px;font:12px/1.35 Consolas,Monaco,monospace;color:#1d2327;';
        const head = document.createElement('div');
        head.style.cssText = 'display:flex;align-items:center;gap:8px;margin-bottom:8px;position:sticky;top:0;background:#fff;padding-bottom:6px;';
        const title = document.createElement('strong');
        title.textContent = 'LEGO diagnose v0.8.74';
        title.style.marginRight = 'auto';
        const copy = document.createElement('button');
        copy.type = 'button'; copy.className = 'button button-small'; copy.textContent = 'Kopiér diagnose';
        copy.addEventListener('click', function () {
            const text = report();
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(text).then(function () { copy.textContent = 'Kopieret'; window.setTimeout(function () { copy.textContent = 'Kopiér diagnose'; }, 1200); });
            } else { window.prompt('Kopiér diagnosen:', text); }
        });
        const clear = document.createElement('button');
        clear.type = 'button'; clear.className = 'button button-small'; clear.textContent = 'Nulstil log';
        clear.addEventListener('click', function () { actions.length = 0; mutations.length = 0; lastDrag = null; snapshot('reset', 'action'); });
        const close = document.createElement('button');
        close.type = 'button'; close.className = 'button button-small'; close.textContent = 'Skjul';
        close.addEventListener('click', function () { panel.style.display = 'none'; });
        pre = document.createElement('pre');
        pre.style.cssText = 'white-space:pre-wrap;margin:0;user-select:text;';
        head.append(title, copy, clear, close);
        panel.append(head, pre);
        document.body.appendChild(panel);
        snapshot('install', 'action');
    }

    document.addEventListener('click', function (event) {
        if (event.target && event.target.closest && event.target.closest('.h18-builder-canvas')) {
            window.setTimeout(function () { snapshot('canvas-click', 'action'); }, 0);
        }
    }, true);
    document.addEventListener('pointerdown', function (event) {
        if (event.target && event.target.closest && event.target.closest('.h18-builder-canvas')) {
            window.setTimeout(function () { snapshot('pointerdown', 'action'); }, 0);
        }
    }, true);

    function installSortableDiagnostics() {
        if (!window.jQuery) { return; }
        const $ = window.jQuery;
        $(document).off('.h18Diag0874');
        $(document).on('sortstart.h18Diag0874', '#h18-page-sections-sortable', function () {
            dragActive = true; lastDrag = null;
            window.setTimeout(function () { snapshot('sortstart', 'action'); }, 0);
        });
        $(document).on('sort.h18Diag0874', '#h18-page-sections-sortable', function () {
            if (dragFrame) { return; }
            dragFrame = window.requestAnimationFrame(function () { dragFrame = 0; snapshot('sort', 'action'); });
        });
        $(document).on('sortstop.h18Diag0874', '#h18-page-sections-sortable', function () {
            snapshot('sortstop', 'action');
            dragActive = false;
            window.setTimeout(function () { snapshot('after-sortstop', 'action'); }, 25);
        });
        $(document).on('sortcancel.h18Diag0874', '#h18-page-sections-sortable', function () {
            snapshot('sortcancel', 'action'); dragActive = false;
        });
    }

    function installMutationDiagnostics() {
        if (!window.MutationObserver || !document.body) { return; }
        const root = document.querySelector('.h18-builder-canvas') || document.body;
        new MutationObserver(function () {
            if (mutationFrame) { return; }
            mutationFrame = window.requestAnimationFrame(function () {
                mutationFrame = 0;
                snapshot('mutation', 'mutation');
            });
        }).observe(root, { childList: true, subtree: true, attributes: true, attributeFilter: ['class', 'data-h18-v0871-target-box', 'data-h18-v0871-inside-kasse'] });
    }

    function install() {
        installPanel();
        installSortableDiagnostics();
        installMutationDiagnostics();
        window.setInterval(function () { render(); }, 300);
    }

    if (document.body) { install(); }
    else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { window.setTimeout(install, 0); }

    document.documentElement.setAttribute('data-h18-lego-diagnostics', VERSION);
    window.__h18LegoDiagnosticsV0873 = { version: VERSION, report: report, snapshot: snapshot };
}());
