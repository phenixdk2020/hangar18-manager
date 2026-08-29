(function () {
    'use strict';

    var WIDTHS = { desktop: 1920, laptop: 1180, mobile: 390 };
    var MIN_SCALE = 0.15;
    var root = null;
    var column = null;
    var stage = null;
    var currentScale = 1;
    var currentWidth = WIDTHS.desktop;
    var scheduled = false;
    var rootObserver = null;
    var columnObserver = null;
    var bodyObserver = null;

    function clamp(value, min, max) { return Math.max(min, Math.min(max, value)); }
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
    function ensureStage() {
        root = document.getElementById('h18-clean-canvas');
        if (!root) { return false; }
        column = root.closest('.h18-clean-canvas-column') || root.parentElement;
        if (!column) { return false; }
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
    function ensureStatus() {
        var toolbar = document.querySelector('.h18-clean-toolbar');
        if (!toolbar) { return null; }
        var status = document.getElementById('h18-vd-viewport-status');
        if (status) { return status; }
        status = document.createElement('span');
        status.id = 'h18-vd-viewport-status';
        status.className = 'h18-vd-viewport-status';
        var gridLabel = toolbar.querySelector('.h18-clean-grid-label');
        if (gridLabel) { gridLabel.insertAdjacentElement('afterend', status); }
        else { toolbar.appendChild(status); }
        return status;
    }
    function syncStageHeight() {
        if (!root || !stage) { return; }
        var height = Math.max(1, root.offsetHeight || root.scrollHeight || 1);
        stage.style.height = Math.ceil(height * currentScale) + 'px';
    }
    function applyFit() {
        if (!ensureStage()) { return; }
        var device = activeDevice();
        currentWidth = WIDTHS[device] || WIDTHS.desktop;
        currentScale = clamp(Math.min(1, availableWidth() / currentWidth), MIN_SCALE, 1);

        root.setAttribute('data-h18-viewport-width', String(currentWidth));
        root.setAttribute('data-h18-viewport-scale', String(currentScale));
        root.style.width = currentWidth + 'px';
        root.style.maxWidth = 'none';
        root.style.transformOrigin = '0 0';
        root.style.transform = 'scale(' + currentScale + ')';

        stage.style.width = Math.ceil(currentWidth * currentScale) + 'px';
        syncStageHeight();

        var status = ensureStatus();
        if (status) {
            var label = ({ desktop: 'Desktop', laptop: 'Laptop', mobile: 'Mobil' })[device] || device;
            status.textContent = label + ' · ' + currentWidth + ' px · Fit ' + Math.round(currentScale * 100) + '%';
            status.title = 'Virtuel frontendbredde. Fit ændrer kun editor-zoom, aldrig layoutgeometri.';
        }
        window.dispatchEvent(new CustomEvent('h18-vd-viewport-fit', { detail: { device: device, width: currentWidth, scale: currentScale } }));
    }
    function schedule() {
        if (scheduled) { return; }
        scheduled = true;
        window.requestAnimationFrame(function () {
            scheduled = false;
            applyFit();
        });
    }
    function installObservers() {
        if (window.ResizeObserver && column && !columnObserver) {
            columnObserver = new ResizeObserver(schedule);
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
                if (relevant) { schedule(); }
            });
            bodyObserver.observe(document.body, { attributes: true, attributeFilter: ['data-h18-clean-device', 'class'] });
        }
        window.addEventListener('resize', schedule, { passive: true });
        document.addEventListener('click', function (event) {
            if (event.target && event.target.closest && event.target.closest('.h18-clean-device-button,#h18-clean-wide-canvas,.h18-clean-panel-toggle')) {
                window.requestAnimationFrame(schedule);
            }
        }, true);
    }
    function install() {
        if (!ensureStage()) { return; }
        applyFit();
        installObservers();
    }

    window.H18VDViewport = {
        scale: function () { return currentScale || 1; },
        virtualWidth: function () { return currentWidth || WIDTHS.desktop; },
        unscalePx: function (pixels) { return Number(pixels || 0) / Math.max(MIN_SCALE, currentScale || 1); },
        scaledRowPx: function (rowPx) { return Number(rowPx || 0) * Math.max(MIN_SCALE, currentScale || 1); },
        refresh: schedule,
        widths: Object.assign({}, WIDTHS)
    };

    // Admin scripts are printed after the Designer markup. Prime immediately so
    // editor-v018-core measures text at the virtual frontend width on first render.
    if (document.getElementById('h18-clean-canvas')) { install(); }
    else if (document.readyState === 'loading') { document.addEventListener('DOMContentLoaded', install, { once: true }); }
    else { install(); }
}());
