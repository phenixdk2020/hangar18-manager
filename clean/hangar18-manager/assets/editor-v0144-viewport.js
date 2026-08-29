(function () {
    'use strict';

    var WIDTHS = { desktop: 1920, laptop: 1180, mobile: 390 };
    var MIN_FIT_SCALE = 0.15;
    var MIN_MANUAL_SCALE = 0.25;
    var MAX_MANUAL_SCALE = 2.0;
    var STEP = 0.10;
    var root = null;
    var column = null;
    var stage = null;
    var currentScale = 1;
    var currentWidth = WIDTHS.desktop;
    var mode = 'fit';
    var scheduled = false;
    var rootObserver = null;
    var columnObserver = null;
    var bodyObserver = null;

    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
    function roundScale(value) { return Math.round(Number(value || 1) * 100) / 100; }
    function activeDevice() {
        if (window.H18CleanResponsive && typeof window.H18CleanResponsive.device === 'function') {
            var responsiveDevice = String(window.H18CleanResponsive.device() || '');
            if (WIDTHS[responsiveDevice]) { return responsiveDevice; }
        }
        var bodyDevice = document.body ? String(document.body.getAttribute('data-h18-clean-device') || '') : '';
        if (WIDTHS[bodyDevice]) { return bodyDevice; }
        var rootDevice = root ? String(root.getAttribute('data-h18-device') || '') : '';
        return WIDTHS[rootDevice] ? rootDevice : 'desktop';
    }
    function availableWidth() {
        if (!column) { return currentWidth; }
        var style = window.getComputedStyle(column);
        var left = parseFloat(style.paddingLeft || '0') || 0;
        var right = parseFloat(style.paddingRight || '0') || 0;
        return Math.max(80, column.clientWidth - left - right - 2);
    }
    function fitScale() {
        return clamp(Math.min(1, availableWidth() / Math.max(1, currentWidth)), MIN_FIT_SCALE, 1);
    }
    function ensureStage() {
        root = document.getElementById('h18-clean-canvas');
        if (!root) { return false; }
        column = root.closest('.h18-clean-canvas-column') || root.parentElement;
        if (!column) { return false; }
        column.classList.add('h18-vd-zoom-scroll-host');
        if (root.parentElement && root.parentElement.classList.contains('h18-vd-viewport-stage')) {
            stage = root.parentElement;
            return true;
        }
        stage = document.createElement('div');
        stage.className = 'h18-vd-viewport-stage';
        column.insertBefore(stage, root);
        stage.appendChild(root);
        return true;
    }
    function syncStageHeight() {
        if (!root || !stage) { return; }
        var height = Math.max(1, root.offsetHeight || root.scrollHeight || 1);
        stage.style.height = Math.ceil(height * currentScale) + 'px';
    }
    function statusText() {
        var device = activeDevice();
        var label = ({ desktop: 'Desktop', laptop: 'Laptop', mobile: 'Mobil' })[device] || device;
        return label + ' · ' + currentWidth + ' px · ' + (mode === 'fit' ? 'Fit ' : 'Zoom ') + Math.round(currentScale * 100) + '%';
    }
    function ensureControls() {
        var toolbar = document.querySelector('.h18-clean-toolbar');
        if (!toolbar) { return null; }
        var controls = document.getElementById('h18-vd-zoom-controls');
        if (controls) { return controls; }
        controls = document.createElement('span');
        controls.id = 'h18-vd-zoom-controls';
        controls.className = 'h18-vd-zoom-controls';
        controls.innerHTML = '<span id="h18-vd-viewport-status" class="h18-vd-viewport-status"></span>' +
            '<button type="button" class="button button-small" data-vd-zoom="out" title="Zoom ud">−</button>' +
            '<button type="button" class="button button-small" data-vd-zoom="fit" title="Tilpas automatisk til den ledige canvasbredde">Fit</button>' +
            '<button type="button" class="button button-small" data-vd-zoom="100" title="Vis 100 procent">100%</button>' +
            '<button type="button" class="button button-small" data-vd-zoom="in" title="Zoom ind">+</button>';
        var gridLabel = toolbar.querySelector('.h18-clean-grid-label');
        if (gridLabel) { gridLabel.insertAdjacentElement('afterend', controls); }
        else { toolbar.appendChild(controls); }
        controls.addEventListener('click', function (event) {
            var button = event.target && event.target.closest ? event.target.closest('[data-vd-zoom]') : null;
            if (!button) { return; }
            var action = String(button.getAttribute('data-vd-zoom') || '');
            if (action === 'fit') { setFit(); }
            else if (action === '100') { setManual(1, null); }
            else if (action === 'in') { setManual(currentScale + STEP, null); }
            else if (action === 'out') { setManual(currentScale - STEP, null); }
        });
        return controls;
    }
    function updateStatus() {
        ensureControls();
        var status = document.getElementById('h18-vd-viewport-status');
        if (status) {
            status.textContent = statusText();
            status.title = mode === 'fit'
                ? 'Virtuel frontendbredde. Fit følger automatisk den ledige editorbredde.'
                : 'Manuel canvas-zoom. Layoutets virtuelle geometri er uændret.';
        }
    }
    function applyScale(nextScale, nextMode) {
        if (!ensureStage()) { return; }
        currentWidth = WIDTHS[activeDevice()] || WIDTHS.desktop;
        currentScale = roundScale(clamp(nextScale, nextMode === 'fit' ? MIN_FIT_SCALE : MIN_MANUAL_SCALE, nextMode === 'fit' ? 1 : MAX_MANUAL_SCALE));
        mode = nextMode;
        root.setAttribute('data-h18-viewport-width', String(currentWidth));
        root.setAttribute('data-h18-viewport-scale', String(currentScale));
        root.setAttribute('data-h18-viewport-mode', mode);
        root.style.width = currentWidth + 'px';
        root.style.maxWidth = 'none';
        root.style.transformOrigin = '0 0';
        root.style.transform = 'scale(' + currentScale + ')';
        stage.style.width = Math.ceil(currentWidth * currentScale) + 'px';
        syncStageHeight();
        updateStatus();
        window.dispatchEvent(new CustomEvent('h18-vd-viewport-fit', { detail: { device: activeDevice(), width: currentWidth, scale: currentScale, mode: mode } }));
    }
    function setFit() {
        mode = 'fit';
        currentWidth = WIDTHS[activeDevice()] || WIDTHS.desktop;
        applyScale(fitScale(), 'fit');
        if (column) { column.scrollLeft = 0; }
    }
    function pointerAnchor(clientX, clientY) {
        if (!root || !column || clientX == null || clientY == null) { return null; }
        var rootRect = root.getBoundingClientRect();
        return {
            clientX: Number(clientX), clientY: Number(clientY),
            virtualX: (Number(clientX) - rootRect.left) / Math.max(0.01, currentScale),
            virtualY: (Number(clientY) - rootRect.top) / Math.max(0.01, currentScale)
        };
    }
    function restoreAnchor(anchor) {
        if (!anchor || !root || !column) { return; }
        window.requestAnimationFrame(function () {
            var rootRect = root.getBoundingClientRect();
            var dx = rootRect.left + anchor.virtualX * currentScale - anchor.clientX;
            var dy = rootRect.top + anchor.virtualY * currentScale - anchor.clientY;
            column.scrollLeft += dx;
            column.scrollTop += dy;
        });
    }
    function setManual(value, anchor) {
        var next = roundScale(clamp(value, MIN_MANUAL_SCALE, MAX_MANUAL_SCALE));
        applyScale(next, 'manual');
        restoreAnchor(anchor);
    }
    function refresh() {
        if (!ensureStage()) { return; }
        currentWidth = WIDTHS[activeDevice()] || WIDTHS.desktop;
        if (mode === 'fit') { applyScale(fitScale(), 'fit'); }
        else { applyScale(currentScale, 'manual'); }
    }
    function schedule() {
        if (scheduled) { return; }
        scheduled = true;
        window.requestAnimationFrame(function () { scheduled = false; refresh(); });
    }
    function installWheel() {
        if (!column || column.getAttribute('data-vd-wheel-zoom') === '1') { return; }
        column.setAttribute('data-vd-wheel-zoom', '1');
        column.addEventListener('wheel', function (event) {
            if (!stage || !event.target || !(event.target === stage || stage.contains(event.target))) { return; }
            event.preventDefault();
            var anchor = pointerAnchor(event.clientX, event.clientY);
            var direction = event.deltaY < 0 ? 1 : -1;
            setManual(currentScale + direction * STEP, anchor);
        }, { passive: false });
    }
    function installObservers() {
        if (window.ResizeObserver && column && !columnObserver) {
            columnObserver = new ResizeObserver(function () { if (mode === 'fit') { schedule(); } else { syncStageHeight(); updateStatus(); } });
            columnObserver.observe(column);
        }
        if (window.ResizeObserver && root && !rootObserver) {
            rootObserver = new ResizeObserver(function () { syncStageHeight(); });
            rootObserver.observe(root);
        }
        if (window.MutationObserver && document.body && !bodyObserver) {
            bodyObserver = new MutationObserver(function (records) {
                var relevant = records.some(function (record) {
                    return record.type === 'attributes' && (record.attributeName === 'data-h18-clean-device' || record.attributeName === 'class');
                });
                if (relevant && mode === 'fit') { schedule(); }
            });
            bodyObserver.observe(document.body, { attributes: true, attributeFilter: ['data-h18-clean-device', 'class'] });
        }
        window.addEventListener('resize', function () { if (mode === 'fit') { schedule(); } }, { passive: true });
        document.addEventListener('click', function (event) {
            if (!event.target || !event.target.closest) { return; }
            if (event.target.closest('.h18-clean-device-button')) {
                mode = 'fit';
                window.requestAnimationFrame(schedule);
                return;
            }
            if (event.target.closest('#h18-clean-wide-canvas,.h18-clean-panel-toggle') && mode === 'fit') {
                window.requestAnimationFrame(schedule);
            }
        }, true);
    }
    function install() {
        if (!ensureStage()) { return; }
        setFit();
        installWheel();
        installObservers();
    }

    window.H18VDViewport = {
        scale: function () { return currentScale || 1; },
        virtualWidth: function () { return currentWidth || WIDTHS.desktop; },
        unscalePx: function (pixels) { return Number(pixels || 0) / Math.max(MIN_FIT_SCALE, currentScale || 1); },
        scaledRowPx: function (rowPx) { return Number(rowPx || 0) * Math.max(MIN_FIT_SCALE, currentScale || 1); },
        refresh: schedule,
        fit: setFit,
        setZoom: function (value) { setManual(Number(value || 1), null); },
        mode: function () { return mode; },
        widths: Object.assign({}, WIDTHS)
    };

    if (document.getElementById('h18-clean-canvas')) { install(); }
    else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
